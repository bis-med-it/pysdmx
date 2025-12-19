from typing import Any

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.model.dataflow import Schema


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
    """Check if a value is a null/missing value."""
    if value is None:
        return True
    if isinstance(value, str):
        # Empty strings are not considered null
        return False

    return pd.isna(value)


def _should_write_value(value: Any) -> bool:
    """Check if a value should be written to the output.

    A value should be written if it is not null and not an empty string.
    """
    is_empty = _is_null_value(value) or (
        isinstance(value, str) and value == ""
    )
    return not is_empty
