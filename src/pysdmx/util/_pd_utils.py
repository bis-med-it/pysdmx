from typing import Any

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.model.concept import DataType

NUMERIC_TYPES = {
    DataType.BIG_INTEGER,
    DataType.COUNT,
    DataType.DECIMAL,
    DataType.DOUBLE,
    DataType.FLOAT,
    DataType.INCREMENTAL,
    DataType.INTEGER,
    DataType.LONG,
    DataType.SHORT,
}


def _fill_na_values(data: pd.DataFrame, structure: Any) -> pd.DataFrame:
    """Fills missing values in the DataFrame based on the component type.

    Numeric components are filled with "NaN".
    Other components are filled with "#N/A".
    If the structure does not have components,
    all missing values are filled with "".

    Args:
        data: The DataFrame to fill.
        structure: The structure definition (Schema, Dataflow, etc.).

    Returns:
        The DataFrame with filled missing values.

    Raises:
        Invalid: If the structure does not have components.
    """
    if not hasattr(structure, "components"):
        raise Invalid(
            "Structure must have components defined. "
            "Cannot write data without a proper Schema."
        )

    for component in structure.components:
        if component.id in data.columns:
            if component.dtype in NUMERIC_TYPES:
                data[component.id] = (
                    data[component.id].astype(object).fillna("NaN")
                )
            else:
                data[component.id] = (
                    data[component.id].astype(object).fillna("#N/A")
                )

    return data


def _validate_explicit_null_values(data: pd.DataFrame, structure: Any) -> None:
    """Validates that explicit null values are correct for the component type.

    Numeric components must not contain "#N/A".
    Non-numeric components must not contain "NaN".

    Args:
        data: The DataFrame to validate.
        structure: The structure definition.

    Raises:
        Invalid: If invalid null values are found.
    """
    if not hasattr(structure, "components"):
        return

    for component in structure.components:
        if component.id in data.columns:
            series = data[component.id].astype(str)
            if component.dtype in NUMERIC_TYPES:
                # Numeric: #N/A is invalid
                if series.isin(["#N/A"]).any():
                    raise Invalid(
                        f"Invalid null value '#N/A' in numeric component "
                        f"'{component.id}'."
                    )
            else:
                # Non-numeric: NaN is invalid
                if series.isin(["NaN"]).any():
                    raise Invalid(
                        f"Invalid null value 'NaN' in non-numeric component "
                        f"'{component.id}'."
                    )
