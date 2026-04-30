"""Pandas SDMX Dataset."""

from typing import Any, Dict

from pysdmx.__extras_check import __check_data_extra
from pysdmx.model.dataset import Dataset

__check_data_extra()

# E402 is needed here to ensure a clear message is used on missing import
import pandas as pd  # noqa: E402
import pyarrow as pa  # noqa: E402

from pysdmx.errors import Invalid  # noqa: E402
from pysdmx.model import Schema  # noqa: E402
from pysdmx.toolkit.pd import to_pyarrow_schema  # noqa: E402


def stringify_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Convert all DataFrame columns to strings with nulls as empty strings.

    Casts all columns to ``string[pyarrow]`` so that null values become
    ``pd.NA``, fills nulls with empty strings, and converts to plain
    Python strings.

    Args:
        df: The DataFrame to convert.

    Returns:
        A new DataFrame with all string columns and no null values.
    """
    if len(df.columns) == 0:
        return df
    str_dtype = pd.ArrowDtype(pa.string())
    conversion = dict.fromkeys(df.columns, str_dtype)
    return df.astype(conversion).fillna("").astype(str)


def _prepare_columns(
    data: pd.DataFrame,
    conversion: Dict[str, pd.ArrowDtype],
    str_dtype: pd.ArrowDtype,
) -> None:
    """Prepare DataFrame columns for PyArrow type conversion.

    For non-string target dtypes, replaces empty strings with None
    so that the conversion succeeds. For string target dtypes with
    mixed-type object columns, converts values to Python str first
    because PyArrow cannot infer the string type from a column
    containing both integers and strings.

    Args:
        data: The DataFrame to modify in place.
        conversion: Mapping of column names to target ArrowDtype.
        str_dtype: The PyArrow string dtype for comparison.
    """
    for col, dtype in conversion.items():
        if dtype != str_dtype:
            data[col] = data[col].replace("", None)
        elif data[col].dtype == object:
            mask = data[col].notna()
            data.loc[mask, col] = data.loc[mask, col].astype(str)


class PandasDataset(Dataset, frozen=False, kw_only=True):
    """A Dataset that is backed by a Pandas DataFrame.

    When a ``Schema`` is provided as the structure, the DataFrame
    columns are automatically cast to PyArrow-backed dtypes based
    on the component data types. When the structure is a URN string,
    all columns are cast to ``string[pyarrow]``.

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
            _prepare_columns(self.data, conversion, str_dtype)
            try:
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
