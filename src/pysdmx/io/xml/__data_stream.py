"""Single-pass reading of SDMX-ML data messages.

The message is fed in chunks to an lxml pull parser, which validates it
against the XSD in the same pass when asked to. Each Series, Obs and Group
is handed to a DataSet reader as soon as it is parsed, then removed from
the tree, so the memory used does not grow with the size of the message.
"""

import itertools
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    cast,
)

import pandas as pd
import pyarrow as pa
import xmltodict
from lxml import etree

import pysdmx.io.xml.__data_aux as data_aux
from pysdmx.errors import Invalid
from pysdmx.io.input_processor import head_and_rest
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__data_aux import __extract_structure as extract_structure
from pysdmx.io.xml.__parse_xml import (
    NAMESPACES_21,
    NAMESPACES_30,
    NAMESPACES_31,
    XML_OPTIONS_21,
    XML_OPTIONS_30,
    XML_OPTIONS_31,
)
from pysdmx.io.xml.__tokens import (
    DATASET,
    GROUP,
    HEADER,
    OBS,
    SERIES,
    STR_REF,
    STRUCTURE,
)
from pysdmx.io.xml.doc_validation import (
    load_schema,
    sdmx_ml_version,
    severe_errors,
)

# lxml keeps the XSD errors in a log of the last 100 errors of the thread.
# Copying the log after feeding at most 1 KiB keeps every error, even when
# a severe error is followed by many allowed ones.
VALIDATION_FEED_CHARS = 1024
FEED_CHARS = 65536
TAGS = ("{*}Header", "{*}DataSet", "{*}Series", "{*}Obs", "{*}Group")

NAMESPACES = {"2.1": NAMESPACES_21, "3.0": NAMESPACES_30, "3.1": NAMESPACES_31}
XML_OPTIONS: Dict[str, Dict[str, Any]] = {
    "2.1": XML_OPTIONS_21,
    "3.0": XML_OPTIONS_30,
    "3.1": XML_OPTIONS_31,
}


class Names:
    """Names of elements and attributes, as xmltodict gives them."""

    def __init__(self, namespaces: Dict[str, Optional[str]]) -> None:
        """Maps the names with the namespaces of an SDMX-ML version.

        Args:
            namespaces: The prefix of each namespace, None to drop it.
        """
        self.__namespaces = namespaces
        self.__cache: Dict[str, str] = {}

    def __call__(self, clark: str) -> str:
        """Returns the name of an element or attribute.

        Args:
            clark: The name in Clark notation, as lxml gives it.

        Returns:
            The local name, prefixed with the namespace prefix, or with the
            namespace itself when it has no prefix in the map.
        """
        name = self.__cache.get(clark)
        if name is None:
            name = clark
            if clark.startswith("{"):
                uri, local = clark[1:].split("}", 1)
                prefix = self.__namespaces.get(uri, uri)
                name = f"{prefix}:{local}" if prefix else local
            self.__cache[clark] = name
        return name

    def attributes(self, element: etree._Element) -> Dict[str, str]:
        """Returns the attributes of an element, by name."""
        # lxml returns str names and values for a str input
        items = cast(Sequence[Tuple[str, str]], element.items())
        return {self(key): value for key, value in items}


class Columns:
    """Builds string[pyarrow] columns from rows, in batches.

    The columns follow the order in which they first appear in the rows.
    A row without a column gets the fill value, as does every row added
    before the column first appears.
    """

    def __init__(self, fill: Optional[str]) -> None:
        """Starts building columns.

        Args:
            fill: The value of a missing column in a row (None is null).
        """
        self.__fill = fill
        self.__batch = data_aux.READING_CHUNKSIZE
        self.__lists: Dict[str, List[Optional[str]]] = {}
        self.__arrays: Dict[str, List["pa.Array[Any]"]] = {}
        self.__sizes: List[int] = []
        self.__rows = 0

    def add(self, row: Dict[str, Optional[str]]) -> None:
        """Adds a row."""
        rows = self.__rows
        lists = self.__lists
        for name, value in row.items():
            column = lists.get(name)
            if column is None:
                column = lists[name] = [self.__fill] * rows
                self.__arrays[name] = [
                    pa.array([self.__fill] * size, type=pa.string())
                    for size in self.__sizes
                ]
            column.append(value)
        self.__rows = rows + 1
        if len(row) < len(lists):
            for column in lists.values():
                if len(column) == rows:
                    column.append(self.__fill)
        if self.__rows == self.__batch:
            self.__flush()

    def __flush(self) -> None:
        for name, column in self.__lists.items():
            self.__arrays[name].append(pa.array(column, type=pa.string()))
            column.clear()
        self.__sizes.append(self.__rows)
        self.__rows = 0

    def frame(self) -> pd.DataFrame:
        """Returns the DataFrame of the rows added."""
        if self.__rows:
            self.__flush()
        if not self.__arrays:
            # Rows without any column, as pd.DataFrame builds them
            return pd.DataFrame([{}] * sum(self.__sizes))
        return pd.DataFrame(
            {
                name: pd.arrays.ArrowExtensionArray(
                    pa.chunked_array(arrays, type=pa.string())
                )
                for name, arrays in self.__arrays.items()
            }
        )


class DataSetReader(Protocol):
    """Reads the Series, Obs and Group elements of a DataSet."""

    def series_start(self, series: etree._Element) -> None:
        """Starts reading a Series, whose attributes are known."""

    def series_end(self, series: etree._Element) -> None:
        """Ends reading a Series, whose Obs have been removed."""

    def obs(self, obs: etree._Element, in_series: bool) -> None:
        """Reads an Obs, of a Series or of the DataSet."""

    def group(self, group: etree._Element) -> None:
        """Reads a Group."""

    def finish(self, dataset: etree._Element) -> PandasDataset:
        """Returns the dataset read.

        Args:
            dataset: The DataSet, without its Series, Obs and Group.
        """


DataSetReaderFactory = Callable[
    [Dict[str, str], Dict[str, Any], Names], DataSetReader
]


class _MessageReader:
    """Reads the elements of a message as the pull parser gives them."""

    def __init__(
        self,
        names: Names,
        options: Dict[str, Any],
        messages: Tuple[str, ...],
        wrong_message: str,
        reader: DataSetReaderFactory,
    ) -> None:
        self.__names = names
        self.__options = options
        self.__messages = messages
        self.__wrong_message = wrong_message
        self.__reader = reader
        self.__message: Dict[str, Any] = {}
        self.__header: Optional[Dict[str, Any]] = None
        self.__structures: Optional[Dict[str, Any]] = None
        self.__datasets: List[PandasDataset] = []
        self.__current: Optional[DataSetReader] = None
        self.__root_seen = False
        self.__pending: Optional[Exception] = None

    def handle(
        self, events: Iterator[Tuple[str, etree._Element]], defer: bool
    ) -> None:
        """Reads the elements of the events.

        Args:
            events: The events of the pull parser.
            defer: Whether to keep the first error raised by an element and
                raise it in result(), instead of raising it at once.
        """
        if self.__pending is None:
            try:
                for event, element in events:
                    self.__dispatch(event, element)
                return
            except Exception as e:
                if not defer:
                    raise
                # The XSD errors come first, as when validating first
                self.__pending = e
                self.__discard(event, element)
        for event, element in events:
            self.__discard(event, element)

    def result(self) -> Tuple[Optional[Dict[str, Any]], List[PandasDataset]]:
        """Returns the Header and the datasets read.

        Raises:
            Exception: The error kept by handle, if any.
            Invalid: If the message is not of the expected type.
        """
        if self.__pending is not None:
            raise self.__pending
        if not self.__root_seen:
            raise Invalid(self.__wrong_message)
        return self.__header, self.__datasets

    @staticmethod
    def __discard(event: str, element: etree._Element) -> None:
        parent = element.getparent()
        if event == "end" and parent is not None:
            parent.remove(element)

    def __dispatch(self, event: str, element: etree._Element) -> None:
        parent = element.getparent()
        if not self.__root_seen:
            name = self.__names(element.tag)
            if parent is None and name in self.__messages:
                self.__root_seen = True
                return
            raise Invalid(self.__wrong_message)
        if parent is None:
            # The end of the root, as its start was the first event
            self.__structure_info()
        elif parent.getparent() is None:
            self.__root_child(event, element, parent)
        elif self.__current is not None:
            self.__dataset_child(event, element, parent, self.__current)

    def __root_child(
        self, event: str, element: etree._Element, parent: etree._Element
    ) -> None:
        if self.__names(element.tag) == HEADER:
            if event == "end":
                item = self.__to_dict(element)
                self.__message[HEADER] = item
                if element.getprevious() is None:
                    self.__header = item
                parent.remove(element)
        elif element.tag.rpartition("}")[2] == DATASET:
            if event == "start":
                self.__start_dataset(element)
            else:
                current = cast(DataSetReader, self.__current)
                self.__datasets.append(current.finish(element))
                self.__current = None
                parent.remove(element)

    def __dataset_child(
        self,
        event: str,
        element: etree._Element,
        parent: etree._Element,
        current: DataSetReader,
    ) -> None:
        name = self.__names(element.tag)
        if name == SERIES:
            if event == "start":
                current.series_start(element)
            else:
                current.series_end(element)
                parent.remove(element)
        elif name == OBS:
            if event == "end":
                current.obs(element, self.__names(parent.tag) == SERIES)
                parent.remove(element)
        elif name == GROUP and event == "end":
            current.group(element)
            parent.remove(element)

    def __start_dataset(self, element: etree._Element) -> None:
        structures = self.__structure_info()
        attributes = self.__names.attributes(element)
        reference = attributes[STR_REF]
        if reference not in structures:
            raise Invalid(
                f"Dataset Structure Reference {reference} "
                f"not found in the Header"
            )
        self.__current = self.__reader(
            attributes, structures[reference], self.__names
        )

    def __structure_info(self) -> Dict[str, Any]:
        if self.__structures is None:
            # As when reading the whole message: a message without a
            # Header, or with an empty one, fails here
            self.__structures = extract_structure(
                self.__message[HEADER][STRUCTURE]
            )
        return self.__structures

    def __to_dict(self, element: etree._Element) -> Optional[Dict[str, Any]]:
        (item,) = xmltodict.parse(
            etree.tostring(element), **self.__options
        ).values()
        if not isinstance(item, dict):
            return None
        # tostring declares on the element the namespaces it uses, which
        # xmltodict returns under xmlns
        item.pop("xmlns", None)
        return item or None


def _schema_errors(log: Any) -> List[str]:
    return [entry.message for entry in log if entry.domain_name == "SCHEMASV"]


class _WellFormed:
    """A parser target that builds nothing, so the parser only checks XML.

    With the XSD attached, lxml reports a syntax error as the first XSD
    error, with no message at all, or not at all (e.g. a comment not
    terminated after the root), so a second parser checks the syntax.
    Without start and end methods, lxml calls no Python code per element.
    """

    def close(self) -> None:
        """Ends the parse."""


def read_data(
    chunks: Iterable[str],
    validate: bool,
    messages: Tuple[str, ...],
    wrong_message: str,
    reader: DataSetReaderFactory,
) -> Tuple[Optional[Dict[str, Any]], List[PandasDataset]]:
    """Reads an SDMX-ML data message in a single pass.

    Args:
        chunks: The text of the message, in chunks.
        validate: Whether to validate the message against the XSD, in the
            same pass.
        messages: The names of the expected message elements.
        wrong_message: The error when the message is of another type.
        reader: Creates the reader of a DataSet, from its attributes, its
            structure in the Header and the names.

    Returns:
        The Header, as xmltodict parses it, if it is the first element of
        the message, and the datasets.

    Raises:
        Invalid: If the message is not valid, or not of the expected type.
        lxml.etree.XMLSyntaxError: If the message is not well-formed XML.
    """
    head, rest = head_and_rest(iter(chunks))
    version = sdmx_ml_version(head)
    message = _MessageReader(
        Names(NAMESPACES[version]),
        XML_OPTIONS[version],
        messages,
        wrong_message,
        reader,
    )
    # Entities: lxml resolves internal ones only, as in validate_doc
    parser = etree.XMLPullParser(
        events=("start", "end"),
        tag=TAGS + tuple(f"{{*}}{name}" for name in messages),
        schema=load_schema(head) if validate else None,
        remove_comments=True,
        remove_pis=True,
    )
    checker = (
        etree.XMLParser(target=cast("etree.ParserTarget", _WellFormed()))
        if validate
        else None
    )
    feed = VALIDATION_FEED_CHARS if validate else FEED_CHARS
    errors: List[str] = []
    etree.clear_error_log()
    for text in itertools.chain([head], rest):
        for start in range(0, len(text), feed):
            piece = text[start : start + feed]
            if checker is not None:
                checker.feed(piece)
            parser.feed(piece)
            events = cast(
                Iterator[Tuple[str, etree._Element]], parser.read_events()
            )
            message.handle(events, defer=validate)
            if validate:
                errors.extend(_schema_errors(etree.LxmlError("").error_log))
                etree.clear_error_log()
    if checker is not None:
        checker.close()
    try:
        parser.close()
    except etree.XMLSyntaxError as e:
        # The checker has reported any syntax error: with the XSD, the
        # parser reports only XSD errors here
        if not validate:
            raise
        errors.extend(_schema_errors(e.error_log))
    severe = severe_errors(errors)
    if severe:
        raise Invalid("Validation Error", ";\n".join(severe))
    return message.result()
