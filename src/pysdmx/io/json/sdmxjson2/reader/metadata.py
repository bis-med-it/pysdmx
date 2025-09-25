"""Writer interface for SDMX-JSON 2.0.0 Reference Metadata messages."""

import msgspec

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages import JsonMetadataMessage
from pysdmx.model import decoders
from pysdmx.model.message import MetadataMessage


def read(input_str: str) -> MetadataMessage:
    """Read an SDMX-JSON 2.0.0 Metadata Message.

    Args:
        input_str: SDMX-JSON reference metadata message to read.

    Returns:
        A pysdmx MetadataMessage
    """
    try:
        msg = msgspec.json.Decoder(
            JsonMetadataMessage, dec_hook=decoders
        ).decode(input_str)
        return msg.to_model()
    except msgspec.DecodeError as de:
        raise errors.Invalid(
            "Invalid message",
            (
                "The supplied file could not be read as SDMX-JSON 2.0.0 "
                "reference metadata message."
            ),
        ) from de
