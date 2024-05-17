"""Enumeration for the XML message types."""

from enum import Enum


class MessageType(Enum):
    """MessageType enumeration.

    Enumeration that withholds the Message type for writing purposes.
    """

    GenericDataSet = 1
    StructureSpecificDataSet = 2
    Structure = 3
    Error = 4
    Submission = 5
