"""Message module.

This module contains the enumeration for the different types of messages that
can be written.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from msgspec import Struct


class ActionType(Enum):
    """ActionType enumeration.

    Enumeration that withholds the Action type for writing purposes.
    """

    Append = "append"
    Replace = "replace"
    Delete = "delete"
    Information = "information"


class Header(Struct, frozen=True, kw_only=True):
    """Header for the SDMX messages."""

    id: str = "test"
    test: bool = True
    prepared: datetime = datetime.strptime("2021-01-01", "%Y-%m-%d")
    sender: str = "ZZZ"
    receiver: Optional[str] = None
    source: Optional[str] = None
    dataset_action: Optional[ActionType] = None
