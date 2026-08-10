"""Writer for SDMX-ML 3.1 reference metadata (GenericMetadata)."""

from pathlib import Path
from typing import Optional, Sequence, Union

from pysdmx.io.format import Format
from pysdmx.io.xml.__metadata_aux_writer import write_metadata
from pysdmx.model.message import Header
from pysdmx.model.metadata import MetadataReport


def write(
    reports: Sequence[MetadataReport],
    output_path: Optional[Union[str, Path]] = None,
    prettyprint: bool = True,
    header: Optional[Header] = None,
) -> Optional[str]:
    """Writes reference metadata reports as SDMX-ML 3.1 GenericMetadata.

    Args:
        reports: The reference metadata reports to write.
        output_path: The path to save the file (returns a string if empty).
        prettyprint: Prettyprint or not.
        header: The header to use (synthesized if None).

    Returns:
        The XML string if output_path is empty, None otherwise.
    """
    outfile = write_metadata(
        reports, Format.REFMETA_SDMX_ML_3_1, prettyprint, header
    )

    output_path = (
        str(output_path) if isinstance(output_path, Path) else output_path
    )
    if output_path is None or output_path == "":
        return outfile

    with open(output_path, "w", encoding="UTF-8", errors="replace") as f:
        f.write(outfile)
    return None
