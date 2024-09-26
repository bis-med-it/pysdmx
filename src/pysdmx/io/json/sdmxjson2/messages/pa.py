"""Collection of SDMX-JSON schemas for provision agreements."""

from datetime import datetime
from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import JsonAnnotation


class JsonProvisionAgreement(Struct, frozen=True):
    """SDMX-JSON payload for a provision agreement."""

    id: str
    name: str
    agency: str
    structureUsage: str
    dataProvider: str
    description: Optional[str] = None
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None
