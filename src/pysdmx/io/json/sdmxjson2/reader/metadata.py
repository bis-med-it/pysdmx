"""Reader interface for SDMX-JSON 2.0.0 and 2.1.0 Reference Metadata."""

import msgspec

from pysdmx import errors
from pysdmx.__extras_check import __check_json_extra
from pysdmx.io.json.sdmxjson2.messages import JsonMetadataMessage
from pysdmx.io.json.sdmxjson2.reader.doc_validation import validate_sdmx_json
from pysdmx.model import decoders
from pysdmx.model.message import MetadataMessage


def read(input_str: str, validate: bool = True) -> MetadataMessage:
    """Read SDMX-JSON 2.0.0 and 2.1.0 Metadata messages.

    Args:
        input_str: SDMX-JSON reference metadata message to read.
        validate: If True, the JSON data will be validated against the schemas.

    Returns:
        A pysdmx MetadataMessage
    """
    if validate:
        __check_json_extra()
        validate_sdmx_json(input_str)

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
                "or SDMX-JSON 2.1.0 reference metadata message."
            ),
        ) from de
