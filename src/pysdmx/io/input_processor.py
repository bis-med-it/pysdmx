"""Processes the input that comes into read_sdmx function."""

import csv
import os.path
from io import BytesIO, StringIO, TextIOWrapper
from json import JSONDecodeError, loads
from os import PathLike
from pathlib import Path
from typing import Tuple, Union

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io.enums import SDMXFormat


def __remove_bom(input_string: str) -> str:
    return input_string.replace("\ufeff", "")


def __check_xml(infile: str) -> bool:
    return infile[:5] == "<?xml"


def __check_csv(infile: str) -> bool:
    try:
        pd.read_csv(StringIO(infile), nrows=2)
        if (
            len(infile.splitlines()) > 1
            or infile.splitlines()[0].count(",") > 1
        ):
            return True
    except Exception:
        return False
    return False


def __check_json(infile: str) -> bool:
    try:
        loads(infile)
        return True
    except JSONDecodeError:
        return False


def __get_sdmx_ml_flavour(infile: str) -> Tuple[str, SDMXFormat]:
    flavour_check = infile[:1000].lower()
    if ":generic" in flavour_check:
        return infile, SDMXFormat.SDMX_ML_2_1_DATA_GENERIC
    if ":structurespecificdata" in flavour_check:
        return infile, SDMXFormat.SDMX_ML_2_1_DATA_STRUCTURE_SPECIFIC
    if ":structure" in flavour_check:
        return infile, SDMXFormat.SDMX_ML_2_1_STRUCTURE
    if ":registryinterface" in flavour_check:
        return infile, SDMXFormat.SDMX_ML_2_1_SUBMISSION
    if ":error" in flavour_check:
        return infile, SDMXFormat.SDMX_ML_2_1_ERROR
    raise Invalid("Validation Error", "Cannot parse input as SDMX.")


def __get_sdmx_csv_flavour(infile: str) -> Tuple[str, SDMXFormat]:
    headers = csv.reader(StringIO(infile)).__next__()
    if "DATAFLOW" in headers:
        return infile, SDMXFormat.SDMX_CSV_1_0
    elif "STRUCTURE" in headers and "STRUCTURE_ID" in headers:
        return infile, SDMXFormat.SDMX_CSV_2_0
    raise Invalid("Validation Error", "Cannot parse input as SDMX.")


def process_string_to_read(
    infile: Union[str, Path, BytesIO],
) -> Tuple[str, SDMXFormat]:
    """Processes the input that comes into read_sdmx function.

    Args:
        infile: Path to file, URL, or string.

    Returns:
        tuple: Tuple containing the parsed input and the format of the input.

    Raises:
        Invalid: If the input cannot be parsed as SDMX.
    """
    if isinstance(infile, str) and os.path.exists(infile):
        infile = Path(infile)
    # Read file as string
    if isinstance(infile, (Path, PathLike)):
        with open(infile, "r", encoding="utf-8-sig", errors="replace") as f:
            out_str = f.read()

    # Read from BytesIO
    elif isinstance(infile, BytesIO):
        text_wrap = TextIOWrapper(infile, encoding="utf-8", errors="replace")
        out_str = text_wrap.read()

    elif isinstance(infile, str):
        out_str = infile
    else:
        raise Invalid(
            "Validation Error", f"Cannot parse input of type {type(infile)}."
        )

    out_str = __remove_bom(out_str)

    # Check if string is a valid JSON
    if __check_json(out_str):
        return out_str, SDMXFormat.SDMX_JSON_2

    # Check if string is a valid XML
    if __check_xml(out_str):
        return __get_sdmx_ml_flavour(out_str)

    # Check if string is a valid CSV
    if __check_csv(out_str):
        return __get_sdmx_csv_flavour(out_str)

    raise Invalid(
        "Validation Error", f"Cannot parse input as SDMX. Found {infile}"
    )
