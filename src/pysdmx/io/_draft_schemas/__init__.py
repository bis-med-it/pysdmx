"""Draft schemas of SDMX-ML 3.2 and SDMX-JSON 2.2.

They are bundled with pysdmx until the ``sdmxschemas`` package provides
them. See the README of this package for their origin.
"""

from pathlib import Path

_ROOT = Path(__file__).parent

SDMX_ML_32_MESSAGE_PATH = _ROOT / "sdmx_ml_3_2" / "SDMXMessage.xsd"
SDMX_JSON_22_STRUCTURE_PATH = (
    _ROOT / "sdmx_json_2_2" / "sdmx-json-structure-schema.json"
)
