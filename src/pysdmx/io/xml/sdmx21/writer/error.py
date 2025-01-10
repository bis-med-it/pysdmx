"""Module for writing SDMX-ML 2.1 Error messages."""

from typing import Dict, Optional, Sequence

from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.enums import MessageType
from pysdmx.io.xml.sdmx21.writer.__write_aux import __namespaces_from_type
from pysdmx.model.message import Header


def write(
    datasets: Sequence[PandasDataset],
    output_path: str = "",
    prettyprint: bool = True,
    header: Optional[Header] = None,
    dimension_at_observation: Optional[Dict[str, str]] = None,
) -> None:
    """Write data to SDMX-ML 2.1 Generic format.

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
    __namespaces_from_type(MessageType.Error)
