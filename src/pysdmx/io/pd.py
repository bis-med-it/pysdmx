"""Pandas SDMX Dataset."""

from datetime import datetime, timezone
from typing import Any, Dict

from pysdmx.__extras_check import __check_data_extra
from pysdmx.model.dataset import Dataset

__check_data_extra()

# E402 is needed here to ensure a clear message is used on missing import
import pandas as pd  # noqa: E402
import pyarrow as pa  # noqa: E402
from pandas.api.types import is_datetime64_any_dtype  # noqa: E402

from pysdmx.errors import Invalid  # noqa: E402
from pysdmx.model import Schema  # noqa: E402
from pysdmx.toolkit.pd import to_pyarrow_schema  # noqa: E402


def format_value(value: Any) -> str:
    """Give the text of a value as SDMX represents it.

    This is the one place that decides how the data writers write a typed
    value. Booleans are written as ``true`` or ``false``. Date times are
    written in UTC, in the ISO 8601 form ``2025-12-19T14:30:00Z``, with
    fractional seconds only when the value has them; a date time without
    a time zone is taken as UTC. Any other value is written as ``str``
    gives it.

    Args:
        value: The value to write. It must not be null.

    Returns:
        The text to write for the value.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        text = value.isoformat()
        if "." in text:
            text = text.rstrip("0")
        return f"{text}Z"
    return str(value)


def stringify_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Convert all DataFrame columns to strings with nulls as empty strings.

    Casts all columns to ``string[pyarrow]`` so that null values become
    ``pd.NA``, fills nulls with empty strings, and converts to plain
    Python strings. Date times are first given the text that
    :func:`format_value` gives them, as the cast gives another one.

    Args:
        df: The DataFrame to convert.

    Returns:
        A new DataFrame with all string columns and no null values.
    """
    if len(df.columns) == 0:
        return df
    str_dtype = pd.ArrowDtype(pa.string())
    conversion = dict.fromkeys(df.columns, str_dtype)
    date_times = {
        col: df[col].astype(object).map(format_value, na_action="ignore")
        for col in df.columns
        if is_datetime64_any_dtype(df[col].dtype)
    }
    return df.assign(**date_times).astype(conversion).fillna("").astype(str)


def _prepare_columns(
    data: pd.DataFrame,
    conversion: Dict[str, pd.ArrowDtype],
    str_dtype: pd.ArrowDtype,
) -> None:
    """Prepare DataFrame columns for PyArrow type conversion.

    For non-string target dtypes, replaces empty strings with None
    so that the conversion succeeds. For timestamp target dtypes,
    converts the values to UTC, taking those without a time zone as
    UTC, because PyArrow accepts neither a mix of both nor, for a
    time zone aware type, a value without an offset. For string target
    dtypes with mixed-type object columns, converts values to Python
    str first because PyArrow cannot infer the string type from a
    column containing both integers and strings.

    Args:
        data: The DataFrame to modify in place.
        conversion: Mapping of column names to target ArrowDtype.
        str_dtype: The PyArrow string dtype for comparison.

    Raises:
        ValueError: If a value of a timestamp column is not a date time.
    """
    for col, dtype in conversion.items():
        if dtype != str_dtype:
            data[col] = data[col].replace("", None)
            if pa.types.is_timestamp(dtype.pyarrow_dtype):
                data[col] = pd.to_datetime(
                    data[col], utc=True, format="ISO8601"
                )
        elif data[col].dtype == object:
            mask = data[col].notna()
            data.loc[mask, col] = data.loc[mask, col].astype(str)


class PandasDataset(Dataset, frozen=False, kw_only=True):
    """A Dataset that is backed by a Pandas DataFrame.

    When a ``Schema`` is provided as the structure, the DataFrame
    columns are automatically cast to PyArrow-backed dtypes based
    on the component data types. When the structure is a URN string,
    all columns are cast to ``string[pyarrow]``.

    ``DATE_TIME`` components are cast to ``timestamp[ns, tz=UTC]``: a
    value with ``Z`` or an offset is converted to UTC and a value without
    a time zone is taken as UTC.

    Args:
        data: Pandas Dataframe to contain SDMX data.
    """

    data: pd.DataFrame

    def __post_init__(self) -> None:
        """Apply PyArrow dtypes after construction."""
        self._apply_dtypes()

    def __setattr__(self, name: str, value: Any) -> None:
        """Re-apply dtypes when structure is reassigned."""
        super().__setattr__(name, value)
        if name == "structure":
            self._apply_dtypes()

    def _apply_dtypes(self) -> None:
        """Cast DataFrame columns to PyArrow-backed dtypes."""
        if (
            not hasattr(self, "data")
            or self.data is None  # type: ignore[redundant-expr]
            or len(self.data.columns) == 0
        ):
            return

        str_dtype = pd.ArrowDtype(pa.string())

        if isinstance(self.structure, Schema):
            schema_dtypes = to_pyarrow_schema(self.structure.components)
            conversion = {
                col: schema_dtypes.get(col, str_dtype)
                for col in self.data.columns
            }
            try:
                _prepare_columns(self.data, conversion, str_dtype)
                self.data = self.data.astype(conversion)
            except (ValueError, TypeError, pa.ArrowInvalid) as e:
                raise Invalid(
                    "Type conversion failed",
                    f"Cannot convert DataFrame columns to PyArrow dtypes: {e}",
                ) from e
        else:
            conversion = dict.fromkeys(self.data.columns, str_dtype)
            _prepare_columns(self.data, conversion, str_dtype)
            self.data = self.data.astype(conversion)
