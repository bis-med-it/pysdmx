"""Processes the input that comes into read_sdmx function."""

import csv
import os.path
from io import BytesIO, StringIO, TextIOWrapper
from json import JSONDecodeError, loads
from os import PathLike
from pathlib import Path
from typing import Tuple, Union

from httpx import get as httpx_get

from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io.format import Format


def __remove_bom(input_string: str) -> str:
    return input_string.replace("\ufeff", "")


def __check_xml(input_str: str) -> bool:
    return input_str[:5] == "<?xml"


def __check_csv(input_str: str) -> bool:
    try:
        max_length = len(input_str) if len(input_str) < 2048 else 2048
        dialect = csv.Sniffer().sniff(input_str[:max_length])
        control_csv_format = (
            dialect.delimiter == "," and dialect.quotechar == '"'
        )
        # Check we can access the data and it is not empty
        if (
            len(input_str.splitlines()) > 1
            or input_str.splitlines()[0].count(",") > 1
        ) and control_csv_format:
            return True
    except Exception:
        return False
    return False


def __check_json(input_str: str) -> bool:
    try:
        loads(input_str)
        return True
    except JSONDecodeError:
        return False


def __get_sdmx_ml_flavour(input_str: str) -> Tuple[str, Format]:
    flavour_check = input_str[:1000].lower()
    if ":generic" in flavour_check:
        return input_str, Format.DATA_SDMX_ML_2_1_GEN
    # Local import to ensure xml extra is checked at the latest moment
    from pysdmx.io.xml.__parse_xml import SCHEMA_ROOT_30

    if ":structurespecificdata" in flavour_check:
        if SCHEMA_ROOT_30 in flavour_check:
            return input_str, Format.DATA_SDMX_ML_3_0
        else:
            return input_str, Format.DATA_SDMX_ML_2_1_STR
    if ":structure" in flavour_check:
        if SCHEMA_ROOT_30 in flavour_check:
            return input_str, Format.STRUCTURE_SDMX_ML_3_0
        else:
            return input_str, Format.STRUCTURE_SDMX_ML_2_1
    if ":registryinterface" in flavour_check:
        return input_str, Format.REGISTRY_SDMX_ML_2_1
    if ":error" in flavour_check:
        return input_str, Format.ERROR_SDMX_ML_2_1
    raise Invalid("Validation Error", "Cannot parse input as SDMX-ML.")


def __get_sdmx_csv_flavour(input_str: str) -> Tuple[str, Format]:
    headers = csv.reader(StringIO(input_str)).__next__()
    if "DATAFLOW" in headers:
        return input_str, Format.DATA_SDMX_CSV_1_0_0
    elif "STRUCTURE" in headers and "STRUCTURE_ID" in headers:
        return input_str, Format.DATA_SDMX_CSV_2_0_0
    raise Invalid("Validation Error", "Cannot parse input as SDMX-CSV.")


def __check_sdmx_str(input_str: str) -> Tuple[str, Format]:
    """Attempts to infer the SDMX format of the input string."""
    if __check_xml(input_str):
        return __get_sdmx_ml_flavour(input_str)
    if __check_csv(input_str):
        return __get_sdmx_csv_flavour(input_str)
    if __check_json(input_str):
        raise NotImplemented("JSON formats reading are not supported yet")
    raise Invalid("Validation Error", "Cannot parse input as SDMX.")


def process_string_to_read(
    sdmx_document: Union[str, Path, BytesIO],
) -> Tuple[str, Format]:
    """Processes the input that comes into read_sdmx function.

    Automatically detects the format of the input. The input can be a file,
    URL, or string.

    Args:
        sdmx_document: Path to file, URL, or string.

    Returns:
        tuple: Tuple containing the parsed input and the format of the input.

    Raises:
        Invalid: If the input cannot be parsed as SDMX.
    """
    if isinstance(sdmx_document, str) and os.path.exists(sdmx_document):
        sdmx_document = Path(sdmx_document)
    # Read file as string
    if isinstance(sdmx_document, (Path, PathLike)):
        with open(
            sdmx_document, "r", encoding="utf-8-sig", errors="replace"
        ) as f:
            out_str = f.read()

    # Read from BytesIO
    elif isinstance(sdmx_document, BytesIO):
        text_wrap = TextIOWrapper(
            sdmx_document, encoding="utf-8", errors="replace"
        )
        out_str = text_wrap.read()

    elif isinstance(sdmx_document, str):
        if sdmx_document.startswith("http"):
            try:
                response = httpx_get(sdmx_document, timeout=60)
                if (
                    response.status_code != 200
                    and "<?xml" not in response.text
                ):
                    raise Exception("Invalid URL, no SDMX Error found")
                out_str = response.text
            except Exception:
                raise Invalid(
                    "Validation Error",
                    f"Cannot retrieve a SDMX Message "
                    f"from URL: {sdmx_document}.",
                ) from None
        else:
            out_str = sdmx_document
    else:
        raise Invalid(
            "Validation Error",
            f"Cannot parse input of type {type(sdmx_document)}.",
        )

    out_str = __remove_bom(out_str)

    return __check_sdmx_str(out_str)
