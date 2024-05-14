"""Message module.

This module contains the enumeration for the different types of messages that
can be written.
"""

from enum import Enum


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
