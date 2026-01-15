"""Writer interface for SDMX-JSON 2.1.0 Structure messages."""

from pathlib import Path
from typing import Optional, Sequence, Union

from pysdmx.io.json.sdmxjson2.writer._helper import write_structure_msg
from pysdmx.model.__base import MaintainableArtefact
from pysdmx.model.message import Header


def write(
    structures: Sequence[MaintainableArtefact],
    output_path: Optional[Union[str, Path]] = None,
    prettyprint: bool = True,
    header: Optional[Header] = None,
) -> Optional[str]:
    """Write maintainable SDMX artefacts in SDMX-JSON 2.1.0.

    Args:
        structures: The maintainable SDMX artefacts to be serialized.
        output_path: The path to save the JSON file. If None or empty, the
            serialized content is returned as a string instead.
        prettyprint: Whether to format the JSON output with indentation (True)
            or output compact JSON without extra whitespace (False).
        header: The header to be used in the SDMX-JSON message
            (will be generated if no header is supplied).

    Returns:
        The JSON string if output_path is None or empty, None otherwise.
    """
    return write_structure_msg(
        structures, output_path, prettyprint, header, "2.1.0"
    )
