"""Message module.

This module contains the enumeration for the different types of messages that
can be written.
"""

from datetime import datetime
from enum import Enum

from msgspec import Struct

from pysdmx.errors import ClientError


class MessageType(Enum):
    """MessageType enumeration.

    Enumeration that withholds the Message type for writing purposes.
    """

    GenericDataSet = 1
    StructureSpecificDataSet = 2
    Metadata = 3
    Error = 4
    Submission = 5


class ActionType(Enum):
    """ActionType enumeration.

    Enumeration that withholds the Action type for writing purposes.
    """

    Append = "append"
    Replace = "replace"
    Delete = "delete"
    Information = "information"


class Header(Struct, frozen=True, kw_only=True):
    """Header for the SDMX-ML file."""

    id: str = "test"
    test: str = "true"
    prepared: datetime = datetime.strptime("2021-01-01", "%Y-%m-%d")
    sender: str = "Unknown"
    receiver: str = "Not_Supplied"
    source: str = "PySDMX"
    dataset_action: str = ActionType.Information.value

    def __post_init__(self) -> None:
        """Additional validation checks for Headers."""
        if self.test not in {"true", "false"}:
            raise ClientError(
                422,
                "Invalid value for 'Test' in Header",
                "The Test value must be either 'true' or 'false'",
            )
