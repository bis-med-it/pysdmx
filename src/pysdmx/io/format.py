"""Lists of supported formats."""

from enum import Enum

_BASE = "application/vnd.sdmx."


class Format(Enum):
    """The list of SDMX formats since version 2.1."""

    DATA_SDMX_CSV_1_0_0 = f"{_BASE}data+csv;version=1.0.0"
    DATA_SDMX_CSV_2_0_0 = f"{_BASE}data+csv;version=2.0.0"
    DATA_SDMX_JSON_1_0_0 = f"{_BASE}data+json;version=1.0.0"
    DATA_SDMX_JSON_2_0_0 = f"{_BASE}data+json;version=2.0.0"
    DATA_SDMX_ML_2_1_GEN = f"{_BASE}genericdata+xml;version=2.1"
    DATA_SDMX_ML_2_1_STR = f"{_BASE}structurespecificdata+xml;version=2.1"
    DATA_SDMX_ML_2_1_GENTS = f"{_BASE}generictimeseriesdata+xml;version=2.1"
    DATA_SDMX_ML_2_1_STRTS = (
        f"{_BASE}structurespecifictimeseriesdata+xml;version=2.1"
    )
    DATA_SDMX_ML_3_0 = f"{_BASE}data+xml;version=3.0.0"
    GDS_JSON = "application/json"
    REFMETA_SDMX_CSV_2_0_0 = f"{_BASE}metadata+csv;version=2.0.0"
    REFMETA_SDMX_JSON_2_0_0 = f"{_BASE}metadata+json;version=2.0.0"
    REFMETA_SDMX_ML_3_0 = f"{_BASE}metadata+xml;version=3.0.0"
    REGISTRY_SDMX_ML_2_1 = f"{_BASE}registry+xml;version=2.1"
    REGISTRY_SDMX_ML_3_0 = f"{_BASE}registry+xml;version=3.0"
    SCHEMA_SDMX_JSON_1_0_0 = f"{_BASE}schema+json;version=1.0.0"
    SCHEMA_SDMX_JSON_2_0_0 = f"{_BASE}schema+json;version=2.0.0"
    SCHEMA_SDMX_ML_2_1 = f"{_BASE}schema+xml;version=2.1"
    SCHEMA_SDMX_ML_3_0 = f"{_BASE}schema+xml;version=3.0.0"
    STRUCTURE_SDMX_JSON_1_0_0 = f"{_BASE}structure+json;version=1.0.0"
    STRUCTURE_SDMX_JSON_2_0_0 = f"{_BASE}structure+json;version=2.0.0"
    STRUCTURE_SDMX_ML_2_1 = f"{_BASE}structure+xml;version=2.1"
    STRUCTURE_SDMX_ML_3_0 = f"{_BASE}structure+xml;version=3.0.0"
    ERROR_SDMX_ML_2_1 = "application/error.xml"
    FUSION_JSON = "application/vnd.fusion.json"


class AvailabilityFormat(Enum):
    """The SDMX Availability formats."""

    SDMX_JSON_1_0_0 = Format.STRUCTURE_SDMX_JSON_1_0_0.value
    SDMX_JSON_2_0_0 = Format.STRUCTURE_SDMX_JSON_2_0_0.value
    SDMX_ML_2_1 = Format.STRUCTURE_SDMX_ML_2_1.value
    SDMX_ML_3_0 = Format.STRUCTURE_SDMX_ML_3_0.value


class DataFormat(Enum):
    """The SDMX Data formats."""

    SDMX_CSV_1_0_0 = Format.DATA_SDMX_CSV_1_0_0.value
    SDMX_CSV_2_0_0 = Format.DATA_SDMX_CSV_2_0_0.value
    SDMX_JSON_1_0_0 = Format.DATA_SDMX_JSON_1_0_0.value
    SDMX_JSON_2_0_0 = Format.DATA_SDMX_JSON_2_0_0.value
    SDMX_ML_2_1_GEN = Format.DATA_SDMX_ML_2_1_GEN.value
    SDMX_ML_2_1_GENTS = Format.DATA_SDMX_ML_2_1_GENTS.value
    SDMX_ML_2_1_STR = Format.DATA_SDMX_ML_2_1_STR.value
    SDMX_ML_2_1_STRTS = Format.DATA_SDMX_ML_2_1_STRTS.value
    SDMX_ML_3_0 = Format.DATA_SDMX_ML_3_0.value


class RefMetaFormat(Enum):
    """The SDMX Reference Metadata formats."""

    SDMX_CSV_2_0_0 = Format.REFMETA_SDMX_CSV_2_0_0.value
    SDMX_JSON_2_0_0 = Format.REFMETA_SDMX_JSON_2_0_0.value
    SDMX_ML_3_0 = Format.REFMETA_SDMX_ML_3_0.value
    FUSION_JSON = Format.FUSION_JSON.value


class SchemaFormat(Enum):
    """The SDMX Schema formats."""

    SDMX_JSON_1_0_0_SCHEMA = Format.SCHEMA_SDMX_JSON_1_0_0.value
    SDMX_JSON_2_0_0_SCHEMA = Format.SCHEMA_SDMX_JSON_2_0_0.value
    SDMX_JSON_1_0_0_STRUCTURE = Format.STRUCTURE_SDMX_JSON_1_0_0.value
    SDMX_JSON_2_0_0_STRUCTURE = Format.STRUCTURE_SDMX_JSON_2_0_0.value
    SDMX_ML_2_1_SCHEMA = Format.SCHEMA_SDMX_ML_2_1.value
    SDMX_ML_3_0_SCHEMA = Format.SCHEMA_SDMX_ML_3_0.value
    SDMX_ML_2_1_STRUCTURE = Format.STRUCTURE_SDMX_ML_2_1.value
    SDMX_ML_3_0_STRUCTURE = Format.STRUCTURE_SDMX_ML_3_0.value
    FUSION_JSON = Format.FUSION_JSON.value


class StructureFormat(Enum):
    """The SDMX Structure formats."""

    SDMX_JSON_1_0_0 = Format.STRUCTURE_SDMX_JSON_1_0_0.value
    SDMX_JSON_2_0_0 = Format.STRUCTURE_SDMX_JSON_2_0_0.value
    SDMX_ML_2_1 = Format.STRUCTURE_SDMX_ML_2_1.value
    SDMX_ML_3_0 = Format.STRUCTURE_SDMX_ML_3_0.value
    FUSION_JSON = Format.FUSION_JSON.value


class RegistryFormat(Enum):
    """The SDMX Registry formats."""

    SDMX_ML_2_1 = Format.REGISTRY_SDMX_ML_2_1.value
    SDMX_ML_3_0 = Format.REGISTRY_SDMX_ML_3_0.value
    FUSION_JSON = Format.FUSION_JSON.value


GDS_FORMAT = Format.GDS_JSON.value
