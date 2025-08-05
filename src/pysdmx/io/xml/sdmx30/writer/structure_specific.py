# mypy: disable-error-code="union-attr"
"""Module for writing SDMX-ML 3.0 Structure Specific data messages."""

from pathlib import Path
from typing import Dict, Optional, Sequence, Union

from pysdmx.io.format import Format
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__tokens import (
    DSD_LOW,
    PROV_AGREEMENT,
    REGISTRY_LOW,
)
from pysdmx.io.xml.__write_aux import (
    __write_header,
    create_namespaces,
    get_end_message,
)
from pysdmx.io.xml.__write_data_aux import (
    check_content_dataset,
    check_dimension_at_observation,
)
from pysdmx.io.xml.__write_structure_specific_aux import (
    __write_data_structure_specific,
)
from pysdmx.model.message import Header
from pysdmx.util import parse_short_urn


def write(
    datasets: Sequence[PandasDataset],
    output_path: Optional[Union[str, Path]] = None,
    prettyprint: bool = True,
    header: Optional[Header] = None,
    dimension_at_observation: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    """Write data to SDMX-ML 3.0 Structure Specific format.

    Args:
        datasets: The datasets to be written.
        output_path: The path to save the file.
        prettyprint: Prettyprint or not.
        header: The header to be used (generated if None).
        dimension_at_observation:
          The mapping between the dataset and the dimension at observation.

    Returns:
        The XML string if path is empty, None otherwise.
    """
    ss_namespaces = ""
    type_ = Format.DATA_SDMX_ML_3_0

    # Checking if we have datasets,
    # we need to ensure we can write them correctly
    check_content_dataset(datasets)
    content = {dataset.short_urn: dataset for dataset in datasets}

    if header is None:
        header = Header()

    # Checking the dimension at observation mapping
    dim_mapping = check_dimension_at_observation(
        content, dimension_at_observation
    )
    header.structure = dim_mapping
    add_namespace_structure = True
    for i, (short_urn, dimension) in enumerate(header.structure.items()):
        reference = parse_short_urn(short_urn)
        pre_urn = (
            REGISTRY_LOW if reference.sdmx_type == PROV_AGREEMENT else DSD_LOW
        )
        ss_namespaces += (
            f'xmlns:ns{i + 1}="urn:sdmx:org.sdmx'
            f".infomodel.{pre_urn}.{short_urn}"
            f':ObsLevelDim:{dimension}" '
        )

    # Generating the initial tag with namespaces
    outfile = create_namespaces(type_, ss_namespaces, prettyprint)
    # Generating the header
    outfile += __write_header(
        header,
        prettyprint,
        add_namespace_structure,
        data_message=True,
        references_30=True,
    )
    # Writing the content
    outfile += __write_data_structure_specific(
        datasets=content,
        dim_mapping=dim_mapping,
        prettyprint=prettyprint,
        references_30=True,
    )

    outfile += get_end_message(type_, prettyprint)

    output_path = (
        str(output_path) if isinstance(output_path, Path) else output_path
    )

    if output_path is None or output_path == "":
        return outfile

    with open(output_path, "w", encoding="UTF-8", errors="replace") as f:
        f.write(outfile)

    return None
