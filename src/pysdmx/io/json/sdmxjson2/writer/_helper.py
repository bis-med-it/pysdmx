"""Writer interface for SDMX-JSON 2.0.0 Reference Metadata messages."""

from pathlib import Path
from typing import Literal, Optional, Sequence, Union

import msgspec

from pysdmx.io.json.sdmxjson2.messages import (
    JsonMetadataMessage,
    JsonStructureMessage,
)
from pysdmx.model import MetadataReport, encoders
from pysdmx.model.__base import MaintainableArtefact
from pysdmx.model.message import Header, MetadataMessage, StructureMessage


def write_metadata_msg(
    reports: Sequence[MetadataReport],
    output_path: Optional[Union[str, Path]] = None,
    prettyprint: bool = True,
    header: Optional[Header] = None,
    msg_version: Literal["2.0.0", "2.1"] = "2.0.0",
) -> Optional[str]:
    """Write metadata reports in requested SDMX-JSON version.

    Args:
        reports: The reference metadata reports to be serialized.
        output_path: The path to save the JSON file. If None or empty, the
            serialized content is returned as a string instead.
        prettyprint: Whether to format the JSON output with indentation (True)
            or output compact JSON without extra whitespace (False).
        header: The header to be used in the SDMX-JSON message
            (will be generated if no header is supplied).
        msg_version: The desired version of SDMX-JSON. Defaults to 2.0.0.

    Returns:
        The JSON string if output_path is None or empty, None otherwise.
    """
    if not header:
        header = Header()
    sm = MetadataMessage(header, reports)
    jsm = JsonMetadataMessage.from_model(sm, msg_version)

    encoder = msgspec.json.Encoder(enc_hook=encoders)
    serialized_data = encoder.encode(jsm)

    # Apply pretty-printing if requested
    if prettyprint:
        serialized_data = msgspec.json.format(serialized_data, indent=4)

    # If output_path is provided, write to file
    if output_path:
        # Convert to Path object if string
        if isinstance(output_path, str):
            output_path = Path(output_path)

        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(output_path, "wb") as f:
            f.write(serialized_data)
        return None
    else:
        # Return as string
        return serialized_data.decode("utf-8")


def write_structure_msg(
    structures: Sequence[MaintainableArtefact],
    output_path: Optional[Union[str, Path]] = None,
    prettyprint: bool = True,
    header: Optional[Header] = None,
    msg_version: Literal["2.0.0", "2.1"] = "2.0.0",
) -> Optional[str]:
    """Write maintainable SDMX artefacts in SDMX-JSON 2.0.0.

    Args:
        structures: The maintainable SDMX artefacts to be serialized.
        output_path: The path to save the JSON file. If None or empty, the
            serialized content is returned as a string instead.
        prettyprint: Whether to format the JSON output with indentation (True)
            or output compact JSON without extra whitespace (False).
        header: The header to be used in the SDMX-JSON message
            (will be generated if no header is supplied).
        msg_version: The desired version of SDMX-JSON. Defaults to 2.0.0.

    Returns:
        The JSON string if output_path is None or empty, None otherwise.
    """
    if not header:
        header = Header()
    sm = StructureMessage(header, structures)
    jsm = JsonStructureMessage.from_model(sm, msg_version)

    encoder = msgspec.json.Encoder(enc_hook=encoders)
    serialized_data = encoder.encode(jsm)

    # Apply pretty-printing if requested
    if prettyprint:
        serialized_data = msgspec.json.format(serialized_data, indent=4)

    # If output_path is provided, write to file
    if output_path:
        # Convert to Path object if string
        if isinstance(output_path, str):
            output_path = Path(output_path)

        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(output_path, "wb") as f:
            f.write(serialized_data)
        return None
    else:
        # Return as string
        return serialized_data.decode("utf-8")
