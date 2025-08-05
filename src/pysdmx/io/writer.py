"""pysdmx.io.writer.

Common data and structure writer for SDMX objects.
"""

from typing import Any, Optional, Sequence

from pysdmx.errors import Invalid
from pysdmx.io.format import Format
from pysdmx.model.dataset import Dataset

WRITERS = {
    Format.DATA_SDMX_CSV_1_0_0: "pysdmx.io.csv.sdmx10.writer",
    Format.DATA_SDMX_CSV_2_0_0: "pysdmx.io.csv.sdmx20.writer",
    Format.DATA_SDMX_ML_2_1_GEN: "pysdmx.io.xml.sdmx21.writer.generic",
    Format.DATA_SDMX_ML_2_1_STR: "pysdmx.io.xml.sdmx21.writer."
    "structure_specific",
    Format.STRUCTURE_SDMX_ML_2_1: "pysdmx.io.xml.sdmx21.writer.structure",
    Format.DATA_SDMX_ML_3_0: "pysdmx.io.xml.sdmx30.writer."
    "structure_specific",
    Format.STRUCTURE_SDMX_ML_3_0: "pysdmx.io.xml.sdmx30.writer.structure",
}

STRUCTURE_WRITERS = (
    Format.STRUCTURE_SDMX_ML_2_1,
    Format.STRUCTURE_SDMX_ML_3_0,
)


def write_sdmx(
    sdmx_objects: Any,
    sdmx_format: Format,
    output_path: str = "",
    **kwargs: Any,
) -> Optional[str]:
    """Writes any SDMX object (or list of them) to any supported SDMX format.

    See the :ref:`formats available <io-writer-formats-supported>`

    .. important::
        To use the pysdmx.io data functionalities, you need to
        install the `pysdmx[data]` extra.

        For SDMX-ML support, you also need to install the `pysdmx[xml]` extra.

        Check the :ref:`installation guide <installation>`
        for more information.

    .. important::
        To write SDMX-ML Generic or Series messages, the PandasDataset
        requires to have its structure defined as a
        :class:`Schema <pysdmx.model.dataflow.Schema>`.

    Args:
        sdmx_objects: Model objects to write, including PandasDataset,
            DataStructure, Dataflow, ConceptScheme, etc.
        sdmx_format: The pysdmx.io.Format to write to, e.g.,
            Format.DATA_SDMX_ML_3_0.
        output_path: The path to save the file. If empty, returns a string.
        **kwargs: Additional keyword arguments (see below).

    Keyword Args:
        prettyprint: Whether to pretty-print the output (default: True)
          (only for SDMX-ML).
        header: Custom :class:`Header <pysdmx.model.message.Header>` to
          include in the SDMX Message (only for SDMX-ML)
        dimension_at_observation: Mapping for dimension at observation
          (only for SDMX-ML Data formats). This is a dictionary where
          the keys are short URNs and the values are the dimension IDs
          that should be used as the dimension at observation for that
          structure in the output. For example,
          ``{"Dataflow=MD:TEST_MD(1.0)": "TIME_PERIOD"}``.
          Overrides the header.structure
          (if a custom header is provided).

    Returns:
        A serialised string if output_path is an empty string, otherwise None.

    Raises:
        Invalid: If the file is empty or the format is not supported.
    """
    if sdmx_format not in WRITERS:
        raise Invalid(
            f"No writer found for format: {sdmx_format}. "
            f"Check the docs for supported formats."
        )

    sdmx_objects = (
        sdmx_objects if isinstance(sdmx_objects, Sequence) else [sdmx_objects]
    )

    module = __import__(WRITERS[sdmx_format], fromlist=["write"])
    writer = module.write

    is_structure = sdmx_format in STRUCTURE_WRITERS
    is_xml = "xml" in WRITERS[sdmx_format]
    key = "structures" if is_structure else "datasets"
    value = sdmx_objects if isinstance(sdmx_objects, list) else [sdmx_objects]

    if is_structure and any(isinstance(x, Dataset) for x in value):
        raise Invalid(
            "Datasets cannot be written to structure formats. "
            "Use data formats instead."
        )
    elif not is_structure and not all(isinstance(x, Dataset) for x in value):
        raise Invalid(
            "Only Datasets can be written to data formats. "
            "Use structure formats for other SDMX objects."
        )

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
