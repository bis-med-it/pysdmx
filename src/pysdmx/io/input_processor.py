"""Processes the input that comes into read_sdmx function."""

import contextlib
import csv
import os.path
from io import BytesIO, StringIO, TextIOWrapper
from os import PathLike
from pathlib import Path
from typing import Generator, Iterator, List, Optional, TextIO, Tuple, Union

import msgspec
from httpx import Client as httpx_Client
from httpx import HTTPStatusError, create_ssl_context

from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io.format import Format
from pysdmx.util import map_httpx_errors

SCHEMA_ROOT_31 = "http://www.sdmx.org/resources/sdmxml/schemas/v3_1/"
SCHEMA_ROOT_30 = "http://www.sdmx.org/resources/sdmxml/schemas/v3_0/"
# Characters read at a time from a file or a BytesIO
READ_CHUNK_CHARS = 65536


def __remove_bom(input_string: str) -> str:
    return input_string.replace("\ufeff", "")


def __check_xml(input_str: str) -> bool:
    return input_str[:5] == "<?xml"


def __check_csv(input_str: str) -> bool:
    # JSON ({ or [) and XML (<) documents are never SDMX-CSV, but a
    # one-line document has enough commas and quotes to fool the sniffer.
    if input_str[:100].lstrip().startswith(("{", "[", "<")):
        return False
    try:
        lines = input_str.splitlines()

        # Use the first N complete lines
        # (1 should be enough)
        max_lines = 1
        sample = "\n".join(lines[:max_lines])

        dialect = csv.Sniffer().sniff(sample)
        control_csv_format = (
            dialect.delimiter == "," and dialect.quotechar == '"'
        )
        # Check we can access the data and it is not empty
        if (len(lines) > 1 or lines[0].count(",") > 1) and control_csv_format:
            return True
    except Exception:
        return False
    return False


def __check_json(input_str: str) -> bool:
    try:
        msgspec.json.decode(input_str)
        return True
    except msgspec.DecodeError:
        return False


def __get_sdmx_ml_version(
    flavour_check: str,
    v21: Format,
    v30: Format,
    v31: Format,
) -> Format:
    if SCHEMA_ROOT_30 in flavour_check:
        return v30
    elif SCHEMA_ROOT_31 in flavour_check:
        return v31
    return v21


def __get_generic_metadata_flavour(flavour_check: str) -> Format:
    """Resolves the version of a GenericMetadata (reference metadata) doc.

    There is no SDMX-ML 2.1 reference metadata format in pysdmx, so a 2.1
    GenericMetadata document raises NotImplemented.
    """
    if SCHEMA_ROOT_30 in flavour_check:
        return Format.REFMETA_SDMX_ML_3_0
    if SCHEMA_ROOT_31 in flavour_check:
        return Format.REFMETA_SDMX_ML_3_1
    raise NotImplemented(
        "Unsupported format",
        "SDMX-ML 2.1 reference metadata (GenericMetadata) is not supported.",
    )


def __get_sdmx_ml_flavour(input_str: str) -> Tuple[str, Format]:
    flavour_check = input_str[:1000].lower()
    # Root-element tokens are checked first: looser substrings such as
    # ":structure" also match content of registry and error messages
    # (e.g. <str:Structures> in a SubmitStructureRequest).
    if ":registryinterface" in flavour_check:
        return input_str, Format.REGISTRY_SDMX_ML_2_1
    if ":error" in flavour_check:
        return input_str, Format.ERROR_SDMX_ML_2_1
    if ":generictimeseriesdata" in flavour_check:
        return input_str, Format.DATA_SDMX_ML_2_1_GENTS
    # GenericMetadata must be checked before the ":generic" data check,
    # otherwise a reference metadata message is misrouted to generic data.
    if ":genericmetadata" in flavour_check:
        return input_str, __get_generic_metadata_flavour(flavour_check)
    if ":generic" in flavour_check:
        return input_str, Format.DATA_SDMX_ML_2_1_GEN

    if ":structurespecifictimeseriesdata" in flavour_check:
        return input_str, Format.DATA_SDMX_ML_2_1_STRTS
    if ":structurespecificdata" in flavour_check:
        return input_str, __get_sdmx_ml_version(
            flavour_check,
            Format.DATA_SDMX_ML_2_1_STR,
            Format.DATA_SDMX_ML_3_0,
            Format.DATA_SDMX_ML_3_1,
        )
    if ":structure" in flavour_check:
        return input_str, __get_sdmx_ml_version(
            flavour_check,
            Format.STRUCTURE_SDMX_ML_2_1,
            Format.STRUCTURE_SDMX_ML_3_0,
            Format.STRUCTURE_SDMX_ML_3_1,
        )
    raise Invalid("Validation Error", "Cannot parse input as SDMX-ML.")


def __get_sdmx_csv_flavour(input_str: str) -> Tuple[str, Format]:
    headers = csv.reader(StringIO(input_str)).__next__()
    if "DATAFLOW" in headers:
        return input_str, Format.DATA_SDMX_CSV_1_0_0
    elif "STRUCTURE" in headers and "STRUCTURE_ID" in headers:
        return input_str, Format.DATA_SDMX_CSV_2_1_0
    raise Invalid("Validation Error", "Cannot parse input as SDMX-CSV.")


def __get_sdmx_json_flavour(input_str: str) -> Tuple[str, Format]:
    flavour_check = input_str[:350].lower()
    if "2.0.0/sdmx-json-metadata-schema.json" in flavour_check:
        return input_str, Format.REFMETA_SDMX_JSON_2_0_0
    elif (
        "2.1/sdmx-json-metadata-schema.json" in flavour_check
        or "2.1.0/sdmx-json-metadata-schema.json" in flavour_check
    ):
        return input_str, Format.REFMETA_SDMX_JSON_2_1_0
    elif "2.0.0/sdmx-json-structure-schema.json" in flavour_check:
        return input_str, Format.STRUCTURE_SDMX_JSON_2_0_0
    elif "2.1/sdmx-json-structure-schema.json" in flavour_check:
        return input_str, Format.STRUCTURE_SDMX_JSON_2_1_0
    elif "sdmx-json" in flavour_check:
        raise NotImplemented(
            "Unsupported format", "This flavour of SDMX-JSON is not supported."
        )
    else:
        raise Invalid("Validation Error", "Cannot parse input as SDMX-JSON.")


def __check_sdmx_str(input_str: str) -> Tuple[str, Format]:
    """Attempts to infer the SDMX format of the input string."""
    if __check_xml(input_str):
        return __get_sdmx_ml_flavour(input_str)
    if __check_csv(input_str):
        return __get_sdmx_csv_flavour(input_str)
    if __check_json(input_str):
        return __get_sdmx_json_flavour(input_str)
    raise Invalid("Validation Error", "Cannot parse input as SDMX.")


def __read_text(text: TextIO) -> Generator[str, None, None]:
    while chunk := text.read(READ_CHUNK_CHARS):
        yield __remove_bom(chunk)


def __file_chunks(path: Path) -> Generator[str, None, None]:
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        yield from __read_text(f)


def __bytes_chunks(data: BytesIO) -> Generator[str, None, None]:
    yield from __read_text(
        TextIOWrapper(data, encoding="utf-8", errors="replace")
    )


def __string_chunks(text: str) -> Generator[str, None, None]:
    yield __remove_bom(text)


def __url_chunks(
    url: str, pem: Optional[Union[str, Path]]
) -> Generator[str, None, None]:
    if pem is not None and isinstance(pem, Path):
        pem = str(pem)
    if pem is not None and pem and not os.path.exists(pem):
        raise Invalid(
            "Validation Error",
            f"PEM file {pem} does not exist.",
        )
    ssl_context = (
        create_ssl_context(verify=pem) if pem else create_ssl_context()
    )
    try:
        with (
            httpx_Client(verify=ssl_context) as client,
            client.stream("GET", url, timeout=60) as response,
        ):
            try:
                response.raise_for_status()
            except HTTPStatusError as e:
                # The body of an error is read whole: it is small, and
                # map_httpx_errors needs it
                response.read()
                if "<?xml" in response.text:
                    yield __remove_bom(response.text)
                    return
                map_httpx_errors(e)
            for chunk in response.iter_text():
                yield __remove_bom(chunk)
    except Exception as e:
        raise Invalid(
            "Validation Error",
            f"Cannot retrieve a SDMX Message "
            f"from URL: {url}. Error message: {e}",
        ) from None


def __text_chunks(
    sdmx_document: Union[str, Path, BytesIO],
    pem: Optional[Union[str, Path]],
) -> Generator[str, None, None]:
    """Reads the input as decoded text chunks, without any BOM."""
    if isinstance(sdmx_document, str) and os.path.exists(sdmx_document):
        sdmx_document = Path(sdmx_document)
    if isinstance(sdmx_document, (Path, PathLike)):
        return __file_chunks(sdmx_document)
    if isinstance(sdmx_document, BytesIO):
        return __bytes_chunks(sdmx_document)
    if isinstance(sdmx_document, str):
        if sdmx_document.startswith("http"):
            return __url_chunks(sdmx_document, pem)
        return __string_chunks(sdmx_document)
    raise Invalid(
        "Validation Error",
        f"Cannot parse input of type {type(sdmx_document)}.",
    )


def __chain(
    head: str, rest: Generator[str, None, None]
) -> Generator[str, None, None]:
    try:
        yield head
        yield from rest
    finally:
        rest.close()


def __lines(text: str) -> Iterator[str]:
    """Yields the lines of a text as a StringIO does, without copying it."""
    start = 0
    while start < len(text):
        end = text.find("\n", start) + 1 or len(text)
        yield text[start:end]
        start = end


def __first_record_lines(text: str) -> int:
    """Returns the number of lines the first CSV record of a text uses."""
    reader = csv.reader(__lines(text))
    with contextlib.suppress(csv.Error):
        next(reader, None)
    return reader.line_num


def __csv_head(head: str, chunks: Iterator[str]) -> Tuple[str, str]:
    """Reads on until the head holds the first CSV record and one more line.

    Returns the head, and its start up to that line, with 100 characters at
    least. The CSV checks read only that start, so they give the same result
    on it as on the whole text. A head that ends within a quoted value ends
    the record as well, so the record is only known to be complete when the
    head holds a line more.
    """
    parts = [head]
    newlines = head.count("\n")
    record_lines = 1
    while True:
        if newlines > record_lines:
            head = "".join(parts)
            parts = [head]
            record_lines = __first_record_lines(head)
            if newlines > record_lines:
                end = 0
                for _ in range(record_lines + 1):
                    end = head.index("\n", end) + 1
                return head, head[: max(end, 100)]
        chunk = next(chunks, None)
        if chunk is None:
            head = "".join(parts)
            return head, head
        parts.append(chunk)
        newlines += chunk.count("\n")


def head_and_rest(
    chunks: Iterator[str], size: int = 1000
) -> Tuple[str, Iterator[str]]:
    """Reads the first characters of a text given as chunks.

    Args:
        chunks: The chunks of the text.
        size: The number of characters to read, at least.

    Returns:
        The first chunks joined, with at least ``size`` characters unless
        the text is shorter, and the iterator over the remaining chunks.
    """
    head: List[str] = []
    length = 0
    for chunk in chunks:
        head.append(chunk)
        length += len(chunk)
        if length >= size:
            break
    return "".join(head), chunks


def process_string_to_read(
    sdmx_document: Union[str, Path, BytesIO],
    pem: Optional[Union[str, Path]] = None,
) -> Tuple[str, Format]:
    """Processes the input that comes into read_sdmx function.

    Automatically detects the format of the input. The input can be a file,
    URL, or string.

    Args:
        sdmx_document: Path to file, URL, or string.
        pem: Path to a PEM file for SSL verification when reading from a URL.

    Returns:
        tuple: Tuple containing the parsed input and the format of the input.

    Raises:
        Invalid: If the input cannot be parsed as SDMX.
    """
    return __check_sdmx_str("".join(__text_chunks(sdmx_document, pem)))


def stream_sdmx(
    sdmx_document: Union[str, Path, BytesIO],
    pem: Optional[Union[str, Path]] = None,
) -> Tuple[Generator[str, None, None], Format]:
    """Processes the input that comes into read_sdmx, as a stream of text.

    The text is decoded as in process_string_to_read. The format of an
    SDMX-ML or SDMX-CSV message is detected from its first characters or
    lines, without reading the rest of it; any other input is read whole to
    detect its format.

    Args:
        sdmx_document: Path to file, URL, or string.
        pem: Path to a PEM file for SSL verification when reading from a URL.

    Returns:
        The text of the input as a generator of chunks, and the format of
        the input. Closing the generator closes the file or the HTTP
        response it reads.

    Raises:
        Invalid: If the input cannot be parsed as SDMX.
    """
    chunks = __text_chunks(sdmx_document, pem)
    try:
        head, _ = head_and_rest(chunks)
        if __check_xml(head):
            _, read_format = __get_sdmx_ml_flavour(head)
        else:
            head, sample = __csv_head(head, chunks)
            if __check_csv(sample):
                _, read_format = __get_sdmx_csv_flavour(sample)
            else:
                head, read_format = __check_sdmx_str(head + "".join(chunks))
    except BaseException:
        chunks.close()
        raise
    return __chain(head, chunks), read_format
