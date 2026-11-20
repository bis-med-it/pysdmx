"""Pandas SDMX Dataset."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Collection, Dict, cast

from pysdmx.__extras_check import __check_data_extra
from pysdmx.model.dataset import Dataset

__check_data_extra()

# E402 is needed here to ensure a clear message is used on missing import
import pandas as pd  # noqa: E402
import pyarrow as pa  # noqa: E402
import pyarrow.compute as pc  # noqa: E402
from pandas.api.types import (  # noqa: E402
    is_datetime64_any_dtype,
    is_float_dtype,
)

from pysdmx.errors import Invalid  # noqa: E402
from pysdmx.model import DataType, Schema  # noqa: E402
from pysdmx.toolkit.pd import to_pyarrow_schema  # noqa: E402


def format_value(value: Any) -> str:
    """Give the text of a value as SDMX represents it.

    This is the one place that decides how the data writers write a typed
    value. Booleans are written as ``true`` or ``false``. Date times are
    written in UTC, in the ISO 8601 form ``2025-12-19T14:30:00Z``, with
    fractional seconds only when the value has them; a date time without
    a time zone is taken as UTC. Decimals are written without an
    exponent and without trailing zeros (``0.1``, ``100``). Any other
    value is written as ``str`` gives it.

    Args:
        value: The value to write. It must not be null.

    Returns:
        The text to write for the value.
    """
    if isinstance(value, str):
        # Most values are text already
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        text = value.isoformat()
        if "." in text:
            text = text.rstrip("0")
        return f"{text}Z"
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    return str(value)


def is_decimal(dtype: Any) -> bool:
    """Whether a dtype is a PyArrow decimal."""
    return isinstance(dtype, pd.ArrowDtype) and pa.types.is_decimal(
        dtype.pyarrow_dtype
    )


def stringify_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Convert all DataFrame columns to strings with nulls as empty strings.

    Casts all columns to ``string[pyarrow]`` so that null values become
    ``pd.NA``, fills nulls with empty strings, and converts to plain
    Python strings. Date times and decimals are first given the text
    that :func:`format_value` gives them, as the cast gives another one.

    Args:
        df: The DataFrame to convert.

    Returns:
        A new DataFrame with all string columns and no null values.
    """
    if len(df.columns) == 0:
        return df
    str_dtype = pd.ArrowDtype(pa.string())
    conversion = dict.fromkeys(df.columns, str_dtype)
    formatted = {
        col: df[col].astype(object).map(format_value, na_action="ignore")
        for col in df.columns
        if is_datetime64_any_dtype(df[col].dtype) or is_decimal(df[col].dtype)
    }
    return df.assign(**formatted).astype(conversion).fillna("").astype(str)


# A date time with a time zone: Z or an offset after the time
_ZONED = r"[T ].*[Z+-]"
_UTC = pd.DatetimeTZDtype("ns", "UTC")


def _to_utc(values: pd.Series) -> pd.Series:
    """Convert date times to UTC, taking those without a time zone as UTC.

    The values with a time zone are read apart from those without one:
    when they are read together, pandas 2 gives a value without a time
    zone the offset of the value before it.

    Args:
        values: The date times, as ISO 8601 text or as date times.

    Returns:
        The date times in UTC.

    Raises:
        ValueError: If a value is not a date time.
    """
    values = values.infer_objects()
    if is_datetime64_any_dtype(values.dtype):
        return pd.to_datetime(values, utc=True)
    text = values.astype(pd.ArrowDtype(pa.string()))
    # pandas takes words such as now, today or nan as date times
    words = text[text.str.match(r"\D", na=False).to_numpy(dtype=bool)]
    if len(words) > 0:
        raise ValueError(f"'{words.iloc[0]}' is not an ISO 8601 date time")
    zoned = text.str.contains(_ZONED, na=False).to_numpy(dtype=bool)
    with_zone, without_zone = (
        pd.to_datetime(part, utc=True, format="ISO8601").astype(_UTC)
        for part in (text.where(zoned), text.where(~zoned))
    )
    return with_zone.fillna(without_zone)


# A decimal number without an exponent
_PLAIN = r"^[+-]?(\d+\.?\d*|\.\d+)$"
# The text before the fractional digits of a number, and its trailing zeros
_NOT_FRACTION = r"^[^.]*\.?|0+$"
# float64 holds any number of up to these digits, so any text this short
_FLOAT64_DIGITS = 15
_DECIMAL_PRECISION = 38


def _to_decimal(values: pd.Series) -> pd.Series:
    """Convert to decimals the numbers that float64 cannot hold.

    float64 holds a number when the shortest text of its float64 is the
    same number, as for ``0.10``, ``1.5`` or ``1234.5``. When it holds
    all the numbers, they are returned as text, to be cast to float64.
    When it alters at least one of them (``1234567890.123456789``), they
    are returned as ``decimal128(38, scale)``, the scale being the
    largest number of fractional digits of a number, trailing zeros
    apart.

    NaN, the infinities and the numbers with an exponent are not looked
    at to choose the type: float64 keeps having them. A decimal column
    has no NaN, and has a number with an exponent only if it fits the
    scale.

    Args:
        values: The numbers, as text or as numbers of any type.

    Returns:
        The numbers as they were given if they are floats, as text if
        float64 holds them and as decimals if it does not.

    Raises:
        ArrowInvalid: If a value is not a number that a decimal of 38
            digits holds, when decimals are needed.
    """
    if is_float_dtype(values.dtype):
        return values
    if is_decimal(values.dtype) or values.dtype == object:
        # Numbers that are not text yet, such as Decimal objects
        values = values.astype(object).map(format_value, na_action="ignore")
    values = values.astype(pd.ArrowDtype(pa.string()))
    text: Any = pa.array(values)
    if (pc.max(pc.utf8_length(text)).as_py() or 0) <= _FLOAT64_DIGITS:
        return values
    plain = pc.if_else(
        pc.match_substring_regex(text, _PLAIN),
        text,
        pa.scalar(None, pa.string()),
    )
    fraction = pc.replace_substring_regex(plain, _NOT_FRACTION, "")
    scale = pc.max(pc.utf8_length(fraction)).as_py() or 0
    decimal = pa.decimal128(_DECIMAL_PRECISION, scale)
    shortest = plain.cast(pa.float64()).cast(pa.string())
    held = pc.equal(plain.cast(decimal), shortest.cast(decimal))
    if pc.all(held, min_count=0).as_py():
        return values
    return pd.Series(
        pd.arrays.ArrowExtensionArray(text.cast(decimal)), index=values.index
    )


def _prepare_columns(
    data: pd.DataFrame,
    conversion: Dict[str, pd.ArrowDtype],
    str_dtype: pd.ArrowDtype,
    decimals: Collection[str] = (),
) -> None:
    """Prepare DataFrame columns for PyArrow type conversion.

    For non-string target dtypes, replaces empty strings with None
    so that the conversion succeeds. For timestamp target dtypes,
    converts the values to UTC first, because PyArrow accepts neither
    a mix of values with and without a time zone nor, for a time zone
    aware type, a value without one. For decimal columns, converts the
    values to decimals when float64 cannot hold them, and the target
    dtype becomes theirs. For string target
    dtypes with mixed-type object columns, converts values to Python
    str first because PyArrow cannot infer the string type from a
    column containing both integers and strings.

    Args:
        data: The DataFrame to modify in place.
        conversion: Mapping of column names to target ArrowDtype, which
            gets the dtype of the columns converted to decimals.
        str_dtype: The PyArrow string dtype for comparison.
        decimals: The columns of DECIMAL components.

    Raises:
        ValueError: If a value of a timestamp column is not a date time,
            or a value of a decimal column is not a number.
    """
    for col, dtype in conversion.items():
        if dtype != str_dtype:
            data[col] = data[col].replace("", None)
            if pa.types.is_timestamp(dtype.pyarrow_dtype):
                data[col] = _to_utc(data[col])
            elif col in decimals:
                data[col] = _to_decimal(data[col])
                if is_decimal(data[col].dtype):
                    conversion[col] = cast("pd.ArrowDtype", data[col].dtype)
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

    ``DECIMAL`` components are cast to ``double`` when float64 holds all
    their values as they are given (``0.10``, ``1.5``, ``1234.5``). If
    it would alter one of them (``1234567890.123456789``), the column is
    cast to ``decimal128(38, scale)`` instead, the scale being the
    largest number of fractional digits of its values.

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
            decimals = {
                component.id
                for component in self.structure.components
                if component.dtype == DataType.DECIMAL
            }
            try:
                _prepare_columns(self.data, conversion, str_dtype, decimals)
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
