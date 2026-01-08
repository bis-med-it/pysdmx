from typing import Any, Optional

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.model.concept import DataType
from pysdmx.model.dataflow import Schema

NUMERIC_TYPES = {
    DataType.BIG_INTEGER,
    DataType.COUNT,
    DataType.DECIMAL,
    DataType.DOUBLE,
    DataType.FLOAT,
    DataType.INTEGER,
    DataType.LONG,
    DataType.SHORT,
}


def _validate_schema_exists(dataset: PandasDataset) -> Schema:
    """Validates that the dataset has a Schema defined.

    Args:
        dataset: The dataset to validate.

    Returns:
        The `Schema` from the dataset.

    Raises:
        Invalid: If the structure is not a `Schema`.
    """
    if not isinstance(dataset.structure, Schema):
        raise Invalid(
            "Dataset Structure is not a Schema. Cannot perform operation."
        )
    return dataset.structure


def _is_null_value(value: Any) -> bool:
    """Check if a value is null.

    Empty strings are NOT considered null values.

    Args:
        value: The value to check.

    Returns:
        True if the value is null, False otherwise.
    """
    if isinstance(value, str):
        # Empty strings are not considered null
        return False

    return pd.isna(value) or value is None


def _get_null_representation(dtype: Optional[DataType] = None) -> str:
    """Get the appropriate null value representation based on data type.

    - Numeric types use "NaN"
    - Other types use "#N/A"

    Args:
        dtype: The data type of the component.

    Returns:
        The null value representation ("NaN" for numeric, "#N/A" otherwise).
    """
    if dtype is not None and dtype in NUMERIC_TYPES:
        return "NaN"
    return "#N/A"


def _get_value_to_write(
    value: Any,
    required: bool = True,
    dtype: Optional[DataType] = None,
) -> Optional[str]:
    """Get the value to write to the output, handling null representations.

    - Null value (None/np.nan/pd.NA): return "NaN" or "#N/A" based on dtype
    - Empty string + required: return "NaN" or "#N/A" based on dtype
    - Empty string + optional: return None (skip writing)
    - Any other value: return it's string representation

    Args:
        value: The value to process.
        required: Whether the component is required.
        dtype: The data type of the component.

    Returns:
        The string value to write, or None if the value should be skipped.
    """
    # Null values are always written as their null representation
    if _is_null_value(value):
        return _get_null_representation(dtype)

    # Write required empty strings, skip for optional empty strings
    if isinstance(value, str) and value == "":
        return _get_null_representation(dtype) if required else None

    return str(value)


def _is_nullable_integer_dtype(dtype: Any) -> bool:
    """Check if the dtype is a pandas nullable integer type."""
    return pd.api.types.is_integer_dtype(dtype) and str(dtype).startswith(
        ("Int", "UInt")
    )


def transform_dataframe_for_writing(
    df: pd.DataFrame,
    schema: Schema,
) -> pd.DataFrame:
    """Transform DataFrame values for SDMX output.

    Applies null value representations based on component types:
    - Null values (None/np.nan/pd.NA) -> "NaN" (numeric) or "#N/A" (string)
    - Empty strings for required components -> "NaN" or "#N/A"
    - Empty strings for optional components -> None (to be skipped)

    Args:
        df: The DataFrame to transform.
        schema: The Schema containing component definitions.

    Returns:
        A new DataFrame with transformed values.
    """
    df = df.copy()
    for component in schema.components:
        if component.id in df.columns:
            col_dtype = df[component.id].dtype
            is_nullable_int = _is_nullable_integer_dtype(col_dtype)

            def transform_value(
                v: Any,
                req: bool = component.required,
                dt: Optional[DataType] = component.dtype,
                is_int: bool = is_nullable_int,
            ) -> Optional[str]:
                result = _get_value_to_write(v, req, dt)
                # Format nullable integers without decimal places
                if (
                    is_int
                    and result is not None
                    and result not in ("NaN", "#N/A")
                ):
                    return str(int(float(result)))

                return result

            df[component.id] = df[component.id].apply(transform_value)
    return df
