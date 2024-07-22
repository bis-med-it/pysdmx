"""Type aliases for core SDMX types (e.g. IDType)."""

from typing import Annotated

from msgspec import Meta

NC_NAME_ID_TYPE = Annotated[str, Meta(pattern=r"^[A-Za-z][A-Za-z\d_-]*$")]
