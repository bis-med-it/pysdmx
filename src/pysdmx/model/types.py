from typing import Annotated

from msgspec import Meta

NC_NAME_ID_TYPE = Annotated[str, Meta(pattern="^[A-Za-z][A-Za-z\d_-]*$")]
