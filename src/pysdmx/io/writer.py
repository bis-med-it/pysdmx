"""pysdmx.io.writer.

Common data and structure writer for SDMX objects.
"""

from typing import Any, Optional, Sequence

from pysdmx.io.format import Format

WRITERS = {
    Format.DATA_SDMX_CSV_1_0_0: "pysdmx.io.csv.sdmx10.writer",
    Format.DATA_SDMX_CSV_2_0_0: "pysdmx.io.csv.sdmx20.writer",
    Format.DATA_SDMX_ML_2_1_GEN: "pysdmx.io.xml.sdmx21.writer.generic",
    Format.DATA_SDMX_ML_2_1_STR: "pysdmx.io.xml.sdmx21.writer."
    "structure_specific",
    Format.STRUCTURE_SDMX_ML_2_1: "pysdmx.io.xml.sdmx21.writer.structure",
}


def write(
    sdmx_objects: Any, output_path: str, format_: Format, **kwargs: Any
) -> Optional[str]:
    """Write SDMX objects to a file in the specified format."""
    if format_ not in WRITERS:
        raise ValueError(f"No data writer for format: {format_}")

    sdmx_objects = (
        sdmx_objects if isinstance(sdmx_objects, Sequence) else [sdmx_objects]
    )

    module = __import__(WRITERS[format_], fromlist=["write"])
    writer = module.write

    is_structure = format_ == Format.STRUCTURE_SDMX_ML_2_1
    is_xml = "xml" in WRITERS[format_]
    key = "structures" if is_structure else "datasets"
    value = sdmx_objects if isinstance(sdmx_objects, list) else [sdmx_objects]

    args = {
        key: value,
        "output_path": output_path,
        **(
            {
                "prettyprint": kwargs.get("prettyprint"),
                "header": kwargs.get("header"),
            }
            if is_xml
            else {}
        ),
        **(
            {
                "dimension_at_observation": kwargs.get(
                    "dimension_at_observation"
                )
            }
            if is_xml and not is_structure
            else {}
        ),
    }
    args = {k: v for k, v in args.items() if v is not None}

    return writer(**args)
