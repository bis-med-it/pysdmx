from typing import Any, Dict, Optional
from pysdmx.io.format import Format
from pysdmx.io.xml.sdmx21.writer.generic import write as generic_writer
from pysdmx.io.xml.sdmx21.writer.structure import write as structure_writer
from pysdmx.io.xml.sdmx21.writer.structure_specific import write as structure_specific_writer
from pysdmx.io.xml.sdmx21.writer.error import write as error_writer
from pysdmx.io.xml.sdmx21.writer.protocol import Writer
from pysdmx.model.message import Header

WRITERS: Dict[Format, Writer] = {
    Format.DATA_SDMX_ML_2_1_GEN: generic_writer,
    Format.STRUCTURE_SDMX_ML_2_1: structure_writer,
    Format.DATA_SDMX_ML_2_1_STR: structure_specific_writer,
    Format.ERROR_SDMX_ML_2_1: error_writer,
}

def write_sdmx(
    content: Any,
    _format: Format,
    output_path: str = "",
    prettyprint: bool = True,
    header: Optional[Header] = None,
    dimension_at_observation: Optional[Dict[str, str]] = None
) -> Optional[str]:
    """General writer function to route to the appropriate writer.

    Args:
        content: The SDMX document to write.
        _format: The desired output format.
        output_path: The path to save the file.
        prettyprint: Whether to prettyprint the output.
        header: The header to be used (generated if None).
        dimension_at_observation: The mapping between the dataset and the dimension at observation.

    Returns:
        The XML string if output_path is empty, None otherwise.

    Raises:
        ValueError: If no writer is found for the given format.
    """

    writer = WRITERS.get(_format)
    if writer is None:
        raise ValueError(f"No writer found for format: {_format}")

    # Prepare the required arguments for the writer
    args = {
        "content": content,
        "output_path": output_path,
        "prettyprint": prettyprint,
        "header": header,
    } if _format != Format.ERROR_SDMX_ML_2_1 else {}

    if _format in {Format.DATA_SDMX_ML_2_1_GEN, Format.DATA_SDMX_ML_2_1_STR}:
        args["dimension_at_observation"] = dimension_at_observation

    return writer(**args)
