"""Reader interface for SDMX-JSON 2.0.0 Structure messages."""

import msgspec

from pysdmx import errors
from pysdmx.__extras_check import __check_json_extra
from pysdmx.io.json.sdmxjson2.messages import JsonStructureMessage
from pysdmx.io.json.sdmxjson2.reader.doc_validation import validate_sdmx_json
from pysdmx.model import decoders
from pysdmx.model.message import StructureMessage


def read(input_str: str, validate: bool = True) -> StructureMessage:
    """Read an SDMX-JSON 2.0.0 Structure Message.

    Args:
        input_str: SDMX-JSON structure message to read.
        validate: If True, the JSON data will be validated against the schemas.

    Returns:
        A pysdmx StructureMessage
    """
    if validate:
        __check_json_extra()
        validate_sdmx_json(input_str)

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
