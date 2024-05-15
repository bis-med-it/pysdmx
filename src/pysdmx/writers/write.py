"""Writing SDMX-ML files from Message content."""

from datetime import datetime
from typing import Any, Dict, Optional

from msgspec import Struct

from pysdmx.errors import ClientError
from pysdmx.model.message import MessageType
from pysdmx.writers.__write_aux import (
    ABBR_MSG,
    create_namespaces,
    generate_new_header,
    generate_structures,
    get_end_message,
)


class Header(Struct, frozen=True, kw_only=True):
    """Header for the SDMX-ML file."""

    id: str
    test: str = "true"
    prepared: datetime = datetime.strptime("2021-01-01", "%Y-%m-%d")
    sender: str
    receiver: str
    source: str

    def __post_init__(self) -> None:
        """Additional validation checks for Headers."""
        if self.test not in {"true", "false"}:
            raise ClientError(
                422,
                "Invalid value for 'Test' in Header",
                "The Test value must be either 'true' or 'false'",
            )

    @staticmethod
    def __value(element: str, value: str, prettyprint: bool) -> str:
        """Generates a value element for the XML file.

        A Value element is an XML tag with a value.

        Args:
            element: ID, Test, Prepared, Sender, Receiver, Source
            value: The value to be written
            prettyprint: Prettyprint or not

        Returns:
            A string with the value element
        """
        nl = "\n" if prettyprint else ""
        child2 = "\t\t" if prettyprint else ""
        return (
            f"{nl}{child2}<{ABBR_MSG}:{element}>"
            f"{value}"
            f"</{ABBR_MSG}:{element}>"
        )

    @staticmethod
    def __item(element: str, id_: str, prettyprint: bool) -> str:
        """Generates an item element for the XML file.

        An Item element is an XML tag with an id attribute.

        Args:
            element: Sender, Receiver
            id_: The ID to be written
            prettyprint: Prettyprint or not

        Returns:
            A string with the item element
        """
        nl = "\n" if prettyprint else ""
        child2 = "\t\t" if prettyprint else ""
        return f"{nl}{child2}<{ABBR_MSG}:{element} id={id_!r}/>"

    def to_xml(self, prettyprint: bool = True) -> str:
        """Converts the Header to an XML string.

        Args:
            prettyprint: Prettyprint or not

        Returns:
            The XML string
        """
        nl = "\n" if prettyprint else ""
        child1 = "\t" if prettyprint else ""
        prepared = self.prepared.strftime("%Y-%m-%dT%H:%M:%S")

        return (
            f"{nl}{child1}<{ABBR_MSG}:Header>"
            f"{self.__value('ID', self.id, prettyprint)}"
            f"{self.__value('Test', self.test, prettyprint)}"
            f"{self.__value('Prepared', prepared, prettyprint)}"
            f"{self.__item('Sender', self.sender, prettyprint)}"
            f"{self.__item('Receiver', self.receiver, prettyprint)}"
            f"{self.__value('Source', self.source, prettyprint)}"
            f"{nl}{child1}</{ABBR_MSG}:Header>"
        )


def writer(
    content: Dict[str, Any],
    type_: MessageType,
    path: str = "",
    prettyprint: bool = True,
    header: Optional[Header] = None,
) -> Optional[str]:
    """This function writes a SDMX-ML file from the Message Content.

    Args:
        content: The content to be written
        type_: The type of message to be written
        path: The path to save the file
        prettyprint: Prettyprint or not
        header: The header to be used (generated if None)

    Returns:
        The XML string if path is empty, None otherwise

    Raises:
        NotImplementedError: If the MessageType is not Metadata
    """
    if type_ != MessageType.Metadata:
        raise NotImplementedError("Only Metadata messages are supported")
    outfile = create_namespaces(type_, content, prettyprint)

    if header is None:
        outfile += generate_new_header(type_, content, prettyprint)
    else:
        outfile += header.to_xml(prettyprint)

    outfile += generate_structures(content, prettyprint)

    outfile += get_end_message(type_, prettyprint)

    if path == "":
        return outfile

    with open(path, "w", encoding="UTF-8", errors="replace") as f:
        f.write(outfile)

    return None
