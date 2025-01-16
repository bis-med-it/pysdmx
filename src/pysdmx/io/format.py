"""Lists of supported formats."""

from enum import Enum

_BASE = "application/vnd.sdmx."


class Format(Enum):
    """The SDMX Structure formats."""

    STRUCTURE_SDMX_ML_2_1 = f"{_BASE}structure+xml;version=2.1"
    STRUCTURE_SDMX_ML_3_0 = f"{_BASE}structure+xml;version=3.0.0"
    STRUCTURE_SDMX_JSON_1_0_0 = f"{_BASE}structure+json;version=1.0.0"
    STRUCTURE_SDMX_JSON_2_0_0 = f"{_BASE}structure+json;version=2.0.0"


class StructureFormat(Enum):
    """The SDMX Structure formats."""

    SDMX_ML_2_1 = Format.STRUCTURE_SDMX_ML_2_1.value
    SDMX_ML_3_0 = Format.STRUCTURE_SDMX_ML_3_0.value
    SDMX_JSON_1_0_0 = Format.STRUCTURE_SDMX_JSON_1_0_0.value
    SDMX_JSON_2_0_0 = Format.STRUCTURE_SDMX_JSON_2_0_0.value
