"""Collection of SDMX-JSON schemas for provision agreements."""

from msgspec import Struct


class JsonProvisionAgreement(Struct, frozen=True):
    """SDMX-JSON payload for a provision agreement."""

    structureUsage: str
    dataProvider: str
