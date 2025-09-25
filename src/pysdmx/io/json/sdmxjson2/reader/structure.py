"""Reader interface for SDMX-JSON 2.0.0 Structure messages."""

import msgspec

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages import JsonStructureMessage
from pysdmx.model import decoders
from pysdmx.model.message import StructureMessage


def read(input_str: str) -> StructureMessage:
    """Read an SDMX-JSON 2.0.0 Stucture Message.

    Args:
        input_str: SDMX-JSON structure message to read.

    Returns:
        A pysdmx StructureMessage
    """
    try:
        msg = msgspec.json.Decoder(
            JsonStructureMessage, dec_hook=decoders
        ).decode(input_str)
        return msg.to_model()
    except msgspec.DecodeError as de:
        raise errors.Invalid(
            "Invalid message",
            (
                "The supplied file could not be read as SDMX-JSON 2.0.0 "
                "structure message."
            ),
        ) from de
