"""SDMX 2.1 XML Generic Data reader module."""

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, cast

import pandas as pd
from lxml import etree

from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__data_stream import Columns, Names, read_data
from pysdmx.io.xml.__tokens import (
    ATTRIBUTES,
    DIM_OBS,
    GENERIC,
    GENERIC_TS,
    GROUP_KEY,
    OBS_DIM,
    OBS_KEY,
    OBS_VALUE_ID,
    OBS_VALUE_XML_TAG,
    SERIES_KEY,
    VALUE,
)
from pysdmx.model.dataset import ActionType

Row = Dict[str, Optional[str]]


# The children are typed Any: lxml returns str attribute values for a str
# input, while its stubs type them as str or bytes
def _children(element: etree._Element, names: Names) -> Dict[str, Any]:
    return {names(child.tag): child for child in element}


def _values(element: Any, names: Names, row: Row) -> None:
    """Adds the id and value of the Value children of an element."""
    for child in element:
        if names(child.tag) == VALUE:
            row[child.attrib["id"]] = child.attrib[VALUE.lower()]


class _GenericDataSet:
    """Reads the elements of a Generic DataSet."""

    def __init__(
        self,
        attributes: Dict[str, str],
        structure: Dict[str, Any],
        names: Names,
    ) -> None:
        self.__attributes = attributes
        self.__structure = structure
        self.__names = names
        self.__series = Columns("")
        self.__observations = Columns("")
        self.__groups = Columns("")
        self.__has_series = False
        self.__has_groups = False
        self.__keys: Optional[Row] = None
        self.__series_has_obs = False

    def series_start(self, series: etree._Element) -> None:
        self.__has_series = True
        self.__keys = None
        self.__series_has_obs = False

    def series_end(self, series: etree._Element) -> None:
        if not self.__series_has_obs:
            self.__series.add(self.__series_keys(series))

    def obs(self, obs: etree._Element, in_series: bool) -> None:
        children = _children(obs, self.__names)
        if in_series:
            if self.__keys is None:
                series = cast(etree._Element, obs.getparent())
                self.__keys = self.__series_keys(series)
            row = dict(self.__keys)
            row[OBS_DIM] = children[OBS_DIM].attrib[VALUE.lower()]
        else:
            row = {}
            _values(children[OBS_KEY], self.__names, row)
        row[OBS_VALUE_ID] = (
            children[OBS_VALUE_XML_TAG].attrib[VALUE.lower()]
            if OBS_VALUE_XML_TAG in children
            else ""
        )
        if ATTRIBUTES in children:
            _values(children[ATTRIBUTES], self.__names, row)
        if in_series:
            self.__series_has_obs = True
            self.__series.add(row)
        else:
            self.__observations.add(row)

    def group(self, group: etree._Element) -> None:
        children = _children(group, self.__names)
        row: Row = {}
        _values(children[GROUP_KEY], self.__names, row)
        _values(children[ATTRIBUTES], self.__names, row)
        self.__has_groups = True
        self.__groups.add(row)

    def finish(self, dataset: etree._Element) -> PandasDataset:
        attributes: Row = {}
        children = _children(dataset, self.__names)
        if ATTRIBUTES in children:
            _values(children[ATTRIBUTES], self.__names, attributes)
        if self.__has_series:
            df = self.__series.frame()
            if self.__has_groups:
                df_group = self.__groups.frame()
                common_columns = list(
                    set(df.columns).intersection(set(df_group.columns))
                )
                df = pd.merge(df, df_group, on=common_columns, how="left")
            dim_at_obs = self.__structure[DIM_OBS]
            # In case there are observations defined, we need to replace the
            # OBS_DIM column with the dimension at observation
            if OBS_DIM in df.columns:
                df[dim_at_obs] = df[OBS_DIM]
                del df[OBS_DIM]
        else:
            df = self.__observations.frame()
        action = ActionType(self.__attributes.get("action", "Information"))
        structure_type = self.__structure["structure_type"]
        urn = f"{structure_type}={self.__structure['unique_id']}"
        return PandasDataset(
            structure=urn, attributes=attributes, data=df, action=action
        )

    def __series_keys(self, series: etree._Element) -> Row:
        children = _children(series, self.__names)
        keys: Row = {}
        _values(children[SERIES_KEY], self.__names, keys)
        if ATTRIBUTES in children:
            _values(children[ATTRIBUTES], self.__names, keys)
        return keys


def read_stream(
    chunks: Iterable[str], validate: bool = True
) -> Tuple[Optional[Dict[str, Any]], List[PandasDataset]]:
    """Reads an SDMX-ML 2.1 Generic data message given in text chunks.

    The message is read in a single pass, which also validates it.

    Args:
        chunks: The text of the message, in chunks.
        validate: If True, the XML data will be validated against the XSD.

    Returns:
        The Header of the message, as xmltodict parses it, and the
        datasets.

    Raises:
        Invalid: If the message is not valid SDMX-ML 2.1 Generic data.
    """
    return read_data(
        chunks,
        validate,
        (GENERIC, GENERIC_TS),
        "This SDMX document is not SDMX-ML 2.1 Generic.",
        _GenericDataSet,
    )


def read(input_str: str, validate: bool = True) -> Sequence[PandasDataset]:
    """Reads an SDMX-ML 2.1 Generic data and returns a Sequence of Datasets.

    The message is read in a single pass, which also validates it.

    Args:
        input_str: SDMX-ML data to read.
        validate: If True, the XML data will be validated against the XSD.
    """
    return read_stream([input_str], validate)[1]
