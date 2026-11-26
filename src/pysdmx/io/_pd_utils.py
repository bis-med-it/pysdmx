from copy import copy
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd
import pyarrow as pa
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
)

from pysdmx.errors import Invalid
from pysdmx.io.pd import (
    PandasDataset,
    format_value,
    is_decimal,
    stringify_dataframe,
)
from pysdmx.model import DataType
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
    DataType.INC_VAL_RANGE,
    DataType.EXC_VAL_RANGE,
}


def validate_schema_exists(dataset: PandasDataset) -> Schema:
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


def values_to_write(values: pd.Series) -> pd.Series:
    """Give the values of a column as ``format_value`` can take them.

    pandas hands the values of some columns in another type, in which
    their text is not the one to write:

    - An integer column with a null is handed as floats (``1.0``, and
      ``9007199254740992.0`` for 9007199254740993), so integers are
      given as text, as booleans are (``true``).
    - A float32 value is handed as a float, with the digits of its
      float64 (``0.10000000149011612`` for 0.1), so it is given as its
      shortest text. float64 values are left as they are.
    - Date times and decimals are given as objects.

    Args:
        values: The values of a column.

    Returns:
        The values, with the nulls as nulls.
    """
    dtype = values.dtype
    if is_float_dtype(dtype):
        if getattr(dtype, "itemsize", 8) != 4:
            return values
        floats = values.to_numpy(dtype=np.float32, na_value=np.nan)
        text = pd.Series(floats.astype(str), index=values.index, dtype=object)
        return text.where(~np.isnan(floats), None)
    if is_integer_dtype(dtype) or is_bool_dtype(dtype):
        return values.astype(pd.ArrowDtype(pa.string()))
    if is_datetime64_any_dtype(dtype) or is_decimal(dtype):
        return values.astype(object)
    return values


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

    Args:
        value: The value to process.
        required: Whether the component is required.
        dtype: The data type of the component.

    Returns:
        The string value to write, or None if the value should be skipped.
    """
    if _is_null_value(value) or value == "":
        return _get_null_representation(dtype) if required else None
    return format_value(value)


def typed_values(values: Dict[str, Any], schema: Schema) -> pd.DataFrame:
    """Give values the types of their components, as one row of data.

    The values get their types as the columns of a dataset do, for them
    to be the same wherever they come from: the data set attributes of
    SDMX-ML are given apart from the data, and those of SDMX-CSV in its
    columns.

    Args:
        values: The values, by the id of their component.
        schema: The schema with the components.

    Returns:
        The row, with a column for each value.

    Raises:
        Invalid: If a value does not fit the type of its component.
    """
    data = pd.DataFrame({name: [value] for name, value in values.items()})
    return PandasDataset(structure=schema, data=data).data


def attribute_text(value: Any) -> Optional[str]:
    """Give the text of the value of a data set attribute.

    NaN is a value, the marker of a number that is not one: only a null
    or an empty string is no value.

    Args:
        value: The value of the attribute.

    Returns:
        The text of the value, as ``format_value`` gives it, ``NaN`` for
        NaN and None if the attribute has no value.
    """
    if isinstance(value, (float, np.floating)) and np.isnan(value):
        return "NaN"
    return _get_value_to_write(value, required=False)


def sdmx_csv_text(values: pd.Series) -> Optional[str]:
    """Give the text that the SDMX-CSV writers write for a value.

    Args:
        values: A column with the value.

    Returns:
        The text of the value, or None if it is null or empty.
    """
    value = values_to_write(values).iloc[0]
    return _get_value_to_write(value, required=False)


def sdmx_ml_text(values: pd.Series) -> Optional[str]:
    """Give the text that the SDMX-ML writers write for a value.

    Args:
        values: A column with the value.

    Returns:
        The text of the value, or None if it is null or empty.
    """
    text = str(stringify_dataframe(values.to_frame()).iloc[0, 0])
    return text or None


def first_value_to_write(
    values: pd.Series,
    to_text: Callable[[pd.Series], Optional[str]] = sdmx_csv_text,
) -> Optional[str]:
    """Give the text to write of the first value of a column.

    The text is the one that a writer gives a value of the column, so
    that a float is ``100.0`` or ``1e-07`` for the SDMX-CSV writers and
    ``100`` or ``1e-7`` for the SDMX-ML ones. NaN is ``NaN`` for both:
    it is a value, unlike a null.

    Args:
        values: The values of a column, with at least one.
        to_text: The text that the writer gives the value of a column.

    Returns:
        The text of the value, or None if it is null or empty.
    """
    first = values.iloc[:1]
    value = first.iloc[0]
    if isinstance(value, float) and np.isnan(value):
        return "NaN"
    return to_text(first)


def data_set_attribute_ids(schema: Schema) -> List[str]:
    """Give the ids of the data set attributes of a schema."""
    return [
        attribute.id
        for attribute in schema.components.attributes
        if attribute.attachment_level == "D"
    ]


def data_set_attributes(
    dataset: PandasDataset,
    to_text: Callable[[pd.Series], Optional[str]] = sdmx_csv_text,
) -> Dict[str, Optional[str]]:
    """Give the data set attributes of a dataset as the text to write.

    A data set attribute of the schema gets the text that the writer
    gives a value of the type of its component in a column, for a value
    to read the same at every level of a message. The other attributes
    get the text of ``format_value``.

    Args:
        dataset: The dataset.
        to_text: The text that the writer gives the value of a column.

    Returns:
        The text of the value of each attribute, or None if the
        attribute has no value.

    Raises:
        Invalid: If a data set attribute does not fit the type of its
            component.
    """
    schema = validate_schema_exists(dataset)
    given = {
        name: attribute_text(value)
        for name, value in dataset.attributes.items()
    }
    names = data_set_attribute_ids(schema)
    typed = typed_values(
        {name: given[name] for name in names if name in given}, schema
    )
    return {
        name: first_value_to_write(typed[name], to_text)
        if name in typed.columns
        else text
        for name, text in given.items()
    }


def text_dataset(dataset: PandasDataset) -> PandasDataset:
    """Give a copy of a dataset with its values as the text to write.

    The data are converted to strings, with the nulls as empty strings,
    and the data set attributes to the text of their values, without
    those that have no value. The dataset given is left as it is: only
    the copy gets the new data and attributes.

    Args:
        dataset: The dataset to write.

    Returns:
        The copy of the dataset.
    """
    result = copy(dataset)
    result.data = stringify_dataframe(dataset.data)
    result.attributes = {
        name: value
        for name, value in data_set_attributes(dataset, sdmx_ml_text).items()
        if value is not None
    }
    return result


def transform_dataframe_for_writing(
    df: pd.DataFrame,
    schema: Schema,
) -> pd.DataFrame:
    """Transform DataFrame values for SDMX output.

    Applies null value representations based on component types:
    - Null values (None/np.nan/pd.NA) -> "NaN" (numeric) or "#N/A" (string)
    - Empty strings for required components -> "NaN" or "#N/A"
    - Empty strings for optional components -> None (to be skipped)

    Any other value is given the text that ``format_value`` gives it.

    Args:
        df: The DataFrame to transform.
        schema: The Schema containing component definitions.

    Returns:
        A new DataFrame with transformed values.
    """
    df = df.copy()
    for component in schema.components:
        if component.id in df.columns:

            def transform_value(
                v: Any,
                req: bool = component.required,
                dt: Optional[DataType] = component.dtype,
            ) -> Optional[str]:
                return _get_value_to_write(v, req, dt)

            df[component.id] = values_to_write(df[component.id]).apply(
                transform_value
            )
    return df
