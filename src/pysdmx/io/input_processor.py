"""Processes the input that comes into read_sdmx function."""

from io import BytesIO, TextIOWrapper
from json import JSONDecodeError, loads
from os import PathLike
from pathlib import Path
from typing import Tuple, Union

from pysdmx.errors import Invalid


def __remove_bom(input_string: str) -> str:
    return input_string.replace("\ufeff", "")


def __check_xml(infile: str) -> bool:
    if infile[:5] == "<?xml":
        return True

    return False


def process_string_to_read(
    infile: Union[str, Path, BytesIO]
) -> Tuple[str, str]:
    """Processes the input that comes into read_sdmx function.

    Args:
        infile: Path to file, URL, or string.

    Returns:
        tuple: Tuple containing the parsed input and the format of the input.

    Raises:
        Invalid: If the input cannot be parsed as SDMX.
    """
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
    try:
        loads(out_str)
        return out_str, "json"
    except JSONDecodeError:
        pass

    # Check if string is a valid XML
    if __check_xml(out_str):
        return out_str, "xml"

    raise Invalid(
        "Validation Error", f"Cannot parse input as SDMX. Found {infile}"
    )
