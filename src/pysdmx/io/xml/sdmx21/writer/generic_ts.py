# mypy: disable-error-code="union-attr"
"""Module for writing SDMX-ML 2.1 Generic Time Series data messages."""

from pathlib import Path
from typing import Dict, Optional, Sequence, Union

from pysdmx.io.format import Format
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.sdmx21.writer.generic import write as _base_write
from pysdmx.model.message import Header


def write(
    datasets: Sequence[PandasDataset],
    output_path: Optional[Union[str, Path]] = None,
    prettyprint: bool = True,
    header: Optional[Header] = None,
    dimension_at_observation: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    """Write data to SDMX-ML 2.1 Generic Time Series format.

    This is a thin wrapper around the generic writer that defaults
    ``dimension_at_observation`` to ``TIME_PERIOD`` for all datasets
    and uses the Generic Time Series message type.

    Args:
        datasets: The datasets to be written.
        output_path: The path to save the file.
        prettyprint: Prettyprint or not.
        header: The header to be used (generated if None).
        dimension_at_observation:
          The mapping between the dataset and the dimension at observation.
          Defaults to TIME_PERIOD for all datasets.

    Returns:
        The XML string if path is empty, None otherwise.
    """
    if dimension_at_observation is None:
        dimension_at_observation = {
            ds.short_urn: "TIME_PERIOD" for ds in datasets
        }

    return _base_write(
        datasets=datasets,
        output_path=output_path,
        prettyprint=prettyprint,
        header=header,
        dimension_at_observation=dimension_at_observation,
        sdmx_format=Format.DATA_SDMX_ML_2_1_GENTS,
    )
