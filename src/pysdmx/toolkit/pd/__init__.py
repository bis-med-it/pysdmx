"""Utility functions to leverage the SDMX information model in Pandas."""

from typing import Dict, Iterable

import pandas as pd
import pyarrow as pa

from pysdmx.model import Component, DataType


def __get_pd_type(dt: DataType, required: bool) -> str:  # noqa: C901
    if dt == DataType.SHORT:
        return "int16" if required else "Int16"
    elif dt == DataType.INTEGER:
        return "int32" if required else "Int32"
    elif dt == DataType.LONG or dt == DataType.COUNT:
        return "int64" if required else "Int64"
    elif dt == DataType.BIG_INTEGER or dt == DataType.DECIMAL:
        return "object"
    elif dt == DataType.FLOAT:
        return "float32" if required else "Float32"
    elif dt == DataType.DOUBLE:
        return "float64" if required else "Float64"
    elif dt == DataType.BOOLEAN:
        return "bool" if required else "boolean"
    elif dt == DataType.GREGORIAN_TIME_PERIOD:
        return "object"
    elif dt == DataType.DATE_TIME:
        return "datetime64[ns]"
    elif dt == DataType.YEAR:
        return "datetime64[Y]"
    elif dt == DataType.YEAR_MONTH:
        return "datetime64[M]"
    elif dt == DataType.DATE:
        return "datetime64[D]"
    else:
        return "string"


def to_pandas_type(comp: Component) -> str:
    """Determine the appropriate Pandas data type for the given component.

    For enumerated components, returns 'category' as the Pandas data type.
    For non-enumerated components, maps the SDMX data type to the corresponding
    Pandas data type, taking into account whether the component is required.

    Args:
        comp (Component):
            The SDMX component for which to determine the Pandas data type.

    Returns:
        The string representation of the corresponding Pandas data type.
        Possible return values include:

        - 'category' (for enumerated components)
        - Numeric types ('int16', 'Int16', 'float32', 'Float32', etc.)
        - 'object' (for complex numeric types and time periods)
        - Datetime types ('datetime64[ns]', 'datetime64[Y]', etc.)
        - 'string' (default for unhandled types)
        - 'bool' or 'boolean' (for boolean values)
    """
    if comp.enumeration:
        return "category"
    elif comp.dtype == DataType.INCREMENTAL:
        if comp.facets and isinstance(comp.facets.interval, float):
            return "float32" if comp.required else "Float32"
        else:
            return "int32" if comp.required else "Int32"
    else:
        return __get_pd_type(comp.dtype, comp.required)


def to_pandas_schema(components: Iterable[Component]) -> Dict[str, str]:
    """Infer the schema of a Pandas Data Frame from a list of components.

    This function generates a dictionary mapping component IDs to their
    corresponding Pandas data types. The resulting dictionary can be used
    as input to the Pandas `astype` method to cast DataFrame columns
    to the desired types.

    Args:
        components (Iterable[Component]):
            A collection of SDMX components from which the schema for
            the Pandas DataFrame will be inferred.

    Returns:
        Dict[str, str]:
            A dictionary where keys are the component IDs (field names)
            and values are their corresponding Pandas data types.
    """
    return {c.id: to_pandas_type(c) for c in components}


def __get_pa_type(dt: DataType) -> pa.DataType:  # noqa: C901
    """Map an SDMX DataType to a PyArrow type."""
    if dt == DataType.SHORT:
        return pa.int16()
    elif dt == DataType.INTEGER:
        return pa.int32()
    elif dt == DataType.LONG or dt == DataType.COUNT:
        return pa.int64()
    elif dt == DataType.FLOAT:
        return pa.float32()
    elif dt == DataType.DOUBLE or dt == DataType.DECIMAL:
        return pa.float64()
    elif dt == DataType.BOOLEAN:
        return pa.bool_()
    elif dt == DataType.MONTH:
        return pa.int8()
    elif dt == DataType.DATE:
        return pa.date32()
    elif dt == DataType.DATE_TIME:
        return pa.timestamp("ns")
    else:
        return pa.string()


def to_pyarrow_type(comp: Component) -> pd.ArrowDtype:
    """Determine the appropriate PyArrow-backed Pandas dtype for a component.

    For enumerated components, returns ``ArrowDtype(pa.string())``.
    For non-enumerated components, maps the SDMX data type to the
    corresponding PyArrow type. All types are nullable by default.

    Args:
        comp: The SDMX component for which to determine the dtype.

    Returns:
        The ``pd.ArrowDtype`` wrapping the corresponding PyArrow type.
    """
    if comp.enumeration:
        return pd.ArrowDtype(pa.string())
    elif comp.dtype == DataType.INCREMENTAL:
        if comp.facets and isinstance(comp.facets.interval, float):
            return pd.ArrowDtype(pa.float32())
        else:
            return pd.ArrowDtype(pa.int32())
    else:
        return pd.ArrowDtype(__get_pa_type(comp.dtype))


def to_pyarrow_schema(
    components: Iterable[Component],
) -> Dict[str, pd.ArrowDtype]:
    """Infer a PyArrow-backed schema from a list of components.

    This function generates a dictionary mapping component IDs to their
    corresponding ``pd.ArrowDtype`` values. The resulting dictionary can
    be used as input to the Pandas ``astype`` method.

    Args:
        components: A collection of SDMX components.

    Returns:
        A dictionary where keys are component IDs and values are
        ``pd.ArrowDtype`` instances.
    """
    return {c.id: to_pyarrow_type(c) for c in components}
