"""IO module for SDMX data."""

from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Union, Dict, Any

from pysdmx.errors import Invalid
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.model.dataset import Dataset


class ReadFormat(Enum):
    """Enumeration of supported SDMX read formats."""

    SDMX_ML_2_1 = "SDMX-ML 2.1"
    # SDMX_JSON_2 = "SDMX-JSON 2.0.0"
    # FUSION_JSON = "FusionJSON"
    SDMX_CSV_1_0 = "SDMX-CSV 1.0"
    SDMX_CSV_2_0 = "SDMX-CSV 2.0"

    def check_extension(self, extension: str) -> bool:
        if self == ReadFormat.SDMX_ML_2_1 and extension == "xml":
            return True
        # if self == ReadFormat.SDMX_JSON_2 and extension == "json":
        #     return True
        # if self == ReadFormat.FUSION_JSON and extension == "json":
        #     return True
        if self == ReadFormat.SDMX_CSV_1_0 and extension == "csv":
            return True
        if self == ReadFormat.SDMX_CSV_2_0 and extension == "csv":
            return True
        return False

    def __str__(self):
        return self.value


def read_sdmx(
        infile: Union[str, Path, BytesIO], format: ReadFormat
) -> Dict[str, Any]:
    """
    Reads any sdmx file and returns a dictionary.

    Supported metadata formats are:
    - SDMX-ML 2.1

    Supported data formats are:
    - SDMX-ML 2.1
    - SDMX-CSV 1.0
    - SDMX-CSV 2.0

    Args:
        infile: Path to file (pathlib.Path), URL, or string.

    Returns:
        A dictionary containing the parsed SDMX data or metadata.
    """

    input_str, ext = process_string_to_read(infile)
    if not format.check_extension(ext):
        raise Invalid(f"Invalid format {format} for extension {ext}.")

    elif format == ReadFormat.SDMX_ML_2_1:
        from pysdmx.io.xml.sdmx21.reader import read_xml
        result = read_xml(input_str, validate=True)
    elif format == ReadFormat.SDMX_CSV_1_0:
        from pysdmx.io.csv.sdmx10.reader import read
        result = read(input_str)
    elif format == ReadFormat.SDMX_CSV_2_0:
        from pysdmx.io.csv.sdmx20.reader import read
        result = read(input_str)
    else:
        raise Invalid("Invalid format", f"Format {format} is not supported.")

    # Additional processing for all formats will be placed here

    # TODO: Add message class?

    return result