"""Writer interface for SDMX-JSON 2.1.0 Reference Metadata messages."""

from pathlib import Path
from typing import Optional, Sequence, Union

from pysdmx.io.json.sdmxjson2.writer._helper import write_metadata_msg
from pysdmx.model import MetadataReport
from pysdmx.model.message import Header


def write(
    reports: Sequence[MetadataReport],
    output_path: Optional[Union[str, Path]] = None,
    prettyprint: bool = True,
    header: Optional[Header] = None,
) -> Optional[str]:
    """Write metadata reports in SDMX-JSON 2.1.0.

    Args:
        reports: The reference metadata reports to be serialized.
        output_path: The path to save the JSON file. If None or empty, the
            serialized content is returned as a string instead.
        prettyprint: Whether to format the JSON output with indentation (True)
            or output compact JSON without extra whitespace (False).
        header: The header to be used in the SDMX-JSON message
            (will be generated if no header is supplied).

    Returns:
        The JSON string if output_path is None or empty, None otherwise.
    """
    return write_metadata_msg(reports, output_path, prettyprint, header, "2.1")
