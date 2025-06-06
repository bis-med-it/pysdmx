"""Infer the Pandas data type for a component."""

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
    elif dt == DataType.MONTH:
        return "int8" if required else "Int8"
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


def to_pandas(comp: Component) -> str:
    """Get the Pandas data type of the supplied component."""
    if comp.enumeration:
        return "category"
    else:
        return __get_pd_type(comp.dtype, comp.required)
