"""IO Enumerations for SDMX files."""

from enum import Enum


class ReadFormat(Enum):
    """Enumeration of supported SDMX read formats."""

    SDMX_ML_2_1_STRUCTURE = "SDMX-ML 2.1 Structure"
    SDMX_ML_2_1_DATA_STRUCTURE_SPECIFIC = "SDMX-ML 2.1 StructureSpecific"
    SDMX_ML_2_1_DATA_GENERIC = "SDMX-ML 2.1 Generic"
    SDMX_JSON_2 = "SDMX-JSON 2.0.0"
    FUSION_JSON = "FusionJSON"
    SDMX_CSV_1_0 = "SDMX-CSV 1.0"
    SDMX_CSV_2_0 = "SDMX-CSV 2.0"

    def __str__(self) -> str:
        """Return the string representation of the format."""
        return self.value
