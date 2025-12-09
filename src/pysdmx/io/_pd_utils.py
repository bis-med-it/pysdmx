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
    DataType.INCREMENTAL,
    DataType.INTEGER,
    DataType.LONG,
    DataType.SHORT,
}


def _fill_na_values(data: pd.DataFrame, structure: Schema) -> pd.DataFrame:
    """Fills missing values in the DataFrame based on the component type.

    Numeric components are filled with "NaN".
    Other components are filled with "#N/A".
    Optional components that are missing ("" or NaN) are left as NaN,
    so they can be omitted during writing.
    If the structure does not have components,
    all missing values are filled with "".

    Args:
        data: The DataFrame to fill.
        structure: The structure definition (´Schema´).

    Returns:
        The DataFrame with filled missing values.

    Raises:
        Invalid: If the structure does not have components.
    """
    for component in structure.components:
        # Skip optional components
        if hasattr(component, "required") and not component.required:
            continue

        if component.id in data.columns:
            # Detect missing values
            missing = data[component.id].isna() | (
                data[component.id].astype(str).str.strip() == ""
            )

            if component.dtype in NUMERIC_TYPES:
                data[component.id] = data[component.id].astype(object)
                data.loc[missing, component.id] = "NaN"
            else:
                data[component.id] = data[component.id].astype(object)
                data.loc[missing, component.id] = "#N/A"

    return data


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
