"""Conversions between pysdmx SDMX objects and vtlengine VTL objects."""

import re
from typing import (
    Callable,
    Dict,
    FrozenSet,
    Optional,
    Sequence,
    Type,
    Union,
)

import pandas as pd
from vtlengine.API import (  # type: ignore[attr-defined]
    load_datasets,
    to_vtl_json,
)
from vtlengine.DataTypes import (
    SCALAR_TYPES_CLASS_REVERSE,
    Boolean,
    Date,
    Duration,
    Integer,
    Number,
    ScalarType,
    String,
    TimeInterval,
    TimePeriod,
)
from vtlengine.Model import Dataset as VTLengineDataset
from vtlengine.Model import Role as VTLRole
from vtlengine.Model import ValueDomain

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.model import (
    Code,
    Codelist,
    Component,
    Components,
    Concept,
    DataType,
    Reference,
)
from pysdmx.model.dataflow import Role, Schema

# See "Mapping SDMX data types to VTL basic scalar types" and "Mapping VTL
# basic scalar types to SDMX data types" in the SDMX technical notes.

# VTL type of each SDMX data type
SDMX_TO_VTL_TYPE_MAP: Dict[DataType, Type[ScalarType]] = {
    DataType.STRING: String,
    DataType.ALPHA: String,
    DataType.ALPHA_NUM: String,
    DataType.NUMERIC: String,
    DataType.URI: String,
    DataType.MONTH: String,
    DataType.MONTH_DAY: String,
    DataType.DAY: String,
    DataType.TIME: String,
    DataType.INTEGER: Integer,
    DataType.LONG: Integer,
    DataType.SHORT: Integer,
    DataType.COUNT: Integer,
    DataType.BIG_INTEGER: Integer,
    DataType.DOUBLE: Number,
    DataType.DECIMAL: Number,
    DataType.FLOAT: Number,
    DataType.INC_VAL_RANGE: Number,
    DataType.EXC_VAL_RANGE: Number,
    DataType.INCREMENTAL: Number,
    DataType.BOOLEAN: Boolean,
    DataType.DATE: Date,
    DataType.DATE_TIME: Date,
    DataType.YEAR: TimePeriod,
    DataType.YEAR_MONTH: TimePeriod,
    DataType.GREGORIAN_TIME_PERIOD: TimePeriod,
    DataType.BASIC_TIME_PERIOD: TimePeriod,
    DataType.REP_TIME_PERIOD: TimePeriod,
    DataType.REP_YEAR: TimePeriod,
    DataType.REP_SEMESTER: TimePeriod,
    DataType.REP_TRIMESTER: TimePeriod,
    DataType.REP_QUARTER: TimePeriod,
    DataType.REP_MONTH: TimePeriod,
    DataType.REP_WEEK: TimePeriod,
    DataType.REP_DAY: TimePeriod,
    DataType.STD_TIME_PERIOD: TimePeriod,
    DataType.PERIOD: TimePeriod,
    DataType.TIME_RANGE: TimeInterval,
    DataType.DURATION: Duration,
}

# Default SDMX data type of each VTL type
VTL_TO_SDMX_TYPE_MAP: Dict[Type[ScalarType], DataType] = {
    String: DataType.STRING,
    Integer: DataType.INTEGER,
    Number: DataType.DOUBLE,
    Boolean: DataType.BOOLEAN,
    Date: DataType.DATE_TIME,
    TimePeriod: DataType.REP_TIME_PERIOD,
    TimeInterval: DataType.TIME_RANGE,
    Duration: DataType.DURATION,
}

# SDMX data types compatible with each VTL type
SDMX_TYPES_BY_VTL_TYPE: Dict[Type[ScalarType], FrozenSet[DataType]] = {
    String: frozenset(
        {
            DataType.STRING,
            DataType.ALPHA,
            DataType.ALPHA_NUM,
            DataType.NUMERIC,
            DataType.URI,
            DataType.MONTH_DAY,
            DataType.DAY,
            DataType.TIME,
        }
    ),
    Integer: frozenset(
        {
            DataType.INTEGER,
            DataType.LONG,
            DataType.SHORT,
            DataType.COUNT,
            DataType.BIG_INTEGER,
        }
    ),
    Number: frozenset(
        {
            DataType.DOUBLE,
            DataType.DECIMAL,
            DataType.FLOAT,
            DataType.INC_VAL_RANGE,
            DataType.EXC_VAL_RANGE,
            DataType.INCREMENTAL,
        }
    ),
    Boolean: frozenset({DataType.BOOLEAN}),
    Date: frozenset(
        {
            DataType.DATE,
            DataType.DATE_TIME,
            DataType.BASIC_TIME_PERIOD,
            DataType.GREGORIAN_TIME_PERIOD,
            DataType.STD_TIME_PERIOD,
            DataType.PERIOD,
        }
    ),
    TimePeriod: frozenset(
        {
            DataType.REP_TIME_PERIOD,
            DataType.REP_YEAR,
            DataType.REP_SEMESTER,
            DataType.REP_TRIMESTER,
            DataType.REP_QUARTER,
            DataType.REP_MONTH,
            DataType.REP_WEEK,
            DataType.REP_DAY,
            DataType.YEAR,
            DataType.YEAR_MONTH,
            DataType.GREGORIAN_TIME_PERIOD,
            DataType.BASIC_TIME_PERIOD,
            DataType.STD_TIME_PERIOD,
            DataType.PERIOD,
        }
    ),
    TimeInterval: frozenset({DataType.TIME_RANGE, DataType.PERIOD}),
    Duration: frozenset({DataType.DURATION}),
}

# Role mapping
# ViralAttribute is not yet supported as a separate role in VTL 1.2.2,
# so it is mapped to Attribute following vtlengine's behavior
VTL_TO_SDMX_ROLE_MAP: Dict[VTLRole, Role] = {
    VTLRole.IDENTIFIER: Role.DIMENSION,
    VTLRole.MEASURE: Role.MEASURE,
    VTLRole.ATTRIBUTE: Role.ATTRIBUTE,
    "ViralAttribute": Role.ATTRIBUTE,  # type: ignore[dict-item]
}

VALID_SDMX_TYPES = {"DataStructure", "Dataflow", "ProvisionAgreement"}

# An SDMX TimeRange that a VTL time can hold: a date and a duration in days
_TIME_RANGE = re.compile(
    r"(\d{4}-\d{2}-\d{2})"
    r"/P(?=\d)(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?"
)
# A date with a time
_DATE_TIME = r"\d{4}-\d{2}-\d{2}T[^/]*$"
# The SDMX data types with values that VTL holds in another way
_TIMES_TO_CONVERT = frozenset(
    {
        DataType.TIME_RANGE,
        DataType.BASIC_TIME_PERIOD,
        DataType.STD_TIME_PERIOD,
        DataType.PERIOD,
    }
)
# A VTL time, as vtlengine holds it: the first and the last day
_VTL_TIME = re.compile(r"(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})")
_ONE_DAY = pd.Timedelta(days=1)


def convert_dataset_to_vtl(
    dataset: PandasDataset, vtl_dataset_name: str
) -> VTLengineDataset:
    """Convert a PandasDataset to a vtlengine Dataset.

    This function converts a PandasDataset, which contains both data and
    structure (Schema), into a vtlengine Dataset. It uses vtlengine's
    conversion functions to handle the Schema to VTL structure mapping, with
    the VTL type that `SDMX_TO_VTL_TYPE_MAP` gives to each SDMX data type.

    The values of the `TimeRange` components, which are a start and a
    duration (`2025-01-01/P1Y`), are given as VTL times, which are the first
    and the last day (`2025-01-01/2025-12-31`).

    A date with a time in a `BasicTimePeriod`, `StandardTimePeriod` or
    `ObservationalTimePeriod` component, which are VTL time periods, is given
    as its day: the time and the time zone are dropped.

    It raises an Invalid exception if the dataset structure is not a
    Schema object, or if a `TimeRange` has a time of day.

    Args:
        dataset: The PandasDataset to convert.
        vtl_dataset_name: The name for the vtlengine Dataset.

    Returns:
        A vtlengine Dataset with the data and structure from the
        PandasDataset.

    Raises:
        Invalid: If the dataset structure is not a Schema object or if
            component types cannot be mapped.
    """
    if not isinstance(dataset.structure, Schema):
        raise Invalid(
            "Validation Error",
            "Dataset structure must be a Schema object for conversion to VTL",
        )

    schema = dataset.structure
    pd_dataset = dataset.data
    times = {
        c.id: _vtl_times(pd_dataset[c.id], c.dtype)
        for c in schema.components
        if c.dtype in _TIMES_TO_CONVERT and c.id in pd_dataset.columns
    }
    if times:
        pd_dataset = pd_dataset.assign(**times)

    # Use vtlengine's built-in conversion function to convert Schema to VTL,
    # with the VTL types of SDMX_TO_VTL_TYPE_MAP
    vtl_json = to_vtl_json(schema, vtl_dataset_name)
    for component in vtl_json["datasets"][0]["DataStructure"]:
        vtl_type = SDMX_TO_VTL_TYPE_MAP[
            schema.components[component["name"]].dtype
        ]
        component["type"] = SCALAR_TYPES_CLASS_REVERSE[vtl_type]

    # Load the dataset structure using vtlengine's API
    datasets, scalars = load_datasets(vtl_json)
    vtl_dataset = datasets[vtl_dataset_name]

    # Assign the pandas DataFrame to the VTL dataset
    vtl_dataset.data = pd_dataset

    return vtl_dataset


def _convert_values(
    values: pd.Series, convert: Callable[[str], str]
) -> pd.Series:
    """Converts the values of a column, each distinct value once."""
    converted = {value: convert(value) for value in values.dropna().unique()}
    return values.map(converted).astype(values.dtype)


def _dates(texts: Sequence[str]) -> pd.DatetimeIndex:
    """Gives the dates of some texts, with a null if a text is not a date."""
    return pd.to_datetime(list(texts), format="%Y-%m-%d", errors="coerce")


def _vtl_times(values: pd.Series, dtype: DataType) -> pd.Series:
    """Gives the values of an SDMX time component as VTL holds them.

    A TimeRange is given as a VTL time. In the time periods, a date with a
    time is given as its day, without the time and the time zone, as a VTL
    time period has none.
    """
    if dtype == DataType.TIME_RANGE:
        return _convert_values(values, _time_range_to_vtl_time)
    date_times = values.str.match(_DATE_TIME, na=False)
    return values.where(~date_times, values.str.slice(0, 10))


def _time_range_to_vtl_time(value: str) -> str:
    """Gives an SDMX TimeRange as a VTL time.

    A TimeRange is a start and a duration (`2025-01-01/P1Y`). A VTL time is
    the first and the last day (`2025-01-01/2025-12-31`).

    Args:
        value: The TimeRange.

    Returns:
        The VTL time.

    Raises:
        Invalid: If the TimeRange is not a date and a duration in years,
            months, weeks or days, which is all that a VTL time can hold.
    """
    match = _TIME_RANGE.fullmatch(value)
    dates = _dates(match.groups()[:1] if match else ())
    if match is None or dates.hasnans:
        raise Invalid(
            "Validation Error",
            f"The TimeRange '{value}' cannot be converted to a VTL time: it "
            "must be a date and a duration in years, months, weeks or days.",
        )
    start = dates[0]
    years, months, weeks, days = (int(n or 0) for n in match.groups()[1:])
    duration = pd.DateOffset(years=years, months=months, days=7 * weeks + days)
    return f"{match[1]}/{(start + duration - _ONE_DAY).date()}"


def _vtl_time_to_time_range(value: str) -> str:
    """Gives a VTL time as an SDMX TimeRange.

    A VTL time is the first and the last day (`2025-01-01/2025-12-31`). A
    TimeRange is a start and a duration (`2025-01-01/P1Y`), given here in
    years, months and days.

    Args:
        value: The VTL time.

    Returns:
        The TimeRange.

    Raises:
        Invalid: If the value is not a VTL time.
    """
    match = _VTL_TIME.fullmatch(value)
    dates = _dates(match.groups() if match else ())
    if match is None or dates.hasnans:
        raise Invalid(
            "Validation Error",
            f"'{value}' is not a VTL time (YYYY-MM-DD/YYYY-MM-DD).",
        )
    first, last = dates
    end = last + _ONE_DAY
    months = (end.year - first.year) * 12 + end.month - first.month
    months -= end.day < first.day
    days = (end - (first + pd.DateOffset(months=months))).days
    parts = zip((months // 12, months % 12, days), "YMD")
    return f"{match[1]}/P{''.join(f'{n}{unit}' for n, unit in parts if n)}"


def _data(dataset: VTLengineDataset) -> pd.DataFrame:
    """Returns the data of a VTL dataset, as SDMX holds them.

    The data have no rows if the dataset has no data, and the VTL times are
    given as SDMX TimeRanges.
    """
    if dataset.data is None:
        return pd.DataFrame(columns=list(dataset.components))
    times = [
        name
        for name, component in dataset.components.items()
        if _vtl_dtype_class(component.data_type) is TimeInterval
    ]
    if not times:
        return dataset.data
    return dataset.data.assign(
        **{
            name: _convert_values(dataset.data[name], _vtl_time_to_time_range)
            for name in times
        }
    )


def convert_dataset_to_sdmx(
    dataset: VTLengineDataset,
    reference: Optional[Reference] = None,
    schema: Optional[Schema] = None,
) -> PandasDataset:
    """Convert a VTLengine Dataset to a PandasDataset.

    This function converts a `vtlengine.Model.Dataset` into
    a `PandasDataset` by:

    * Using a provided `Schema` for direct validation and conversion.
    * Generating a new SDMX-compatible `Schema` from the dataset components,
      using metadata from a provided `Reference`.

    When a `schema` is supplied, the dataset is first validated against it and,
    if validation passes, the data is wrapped in a `PandasDataset` with that
    schema. If no `schema` is provided, a `reference` must be given so a new
    SDMX structure (with components, roles, and data types mapped from the
    VTL dataset) can be created.

    The data types follow the mappings between SDMX data types and VTL basic
    scalar types of the SDMX technical notes. A `schema` may give a component
    any SDMX data type that can hold the values of its VTL type (e.g.
    `Double`, `Decimal` or `Float` for a VTL number). A generated schema uses
    the default SDMX data type of each VTL type (e.g. `DateTime` for a VTL
    date), except for a VTL number, which is a `Double`, and a VTL time,
    which is a `TimeRange`.

    The values of the VTL times, which are the first and the last day
    (`2025-01-01/2025-12-31`), are given as SDMX `TimeRange` values, which
    are a start and a duration (`2025-01-01/P1Y`).

    A dataset without data (e.g. a result of the semantic analysis of
    vtlengine, which only has the components) is converted too: the
    `PandasDataset` then has an empty DataFrame, with a column for each
    component.

    Invalid is raised in the following cases:
        * If neither `schema` nor `reference` is provided.
        * If the `reference` has an unsupported `sdmx_type`.
        * If component types or roles cannot be mapped to SDMX equivalents.
        * If validation fails when a `schema` is provided.

    Args:
        dataset: The VTLengine dataset to convert.
            Must include components, and may have no data.
        reference: Optional reference to the SDMX structure
            (DataStructure, Dataflow, or ProvisionAgreement).
            Required only when no `schema` is provided.
            Used to build a schema and supply contextual identifiers.
        schema: Optional schema describing the SDMX structure.
            If provided, the dataset is validated against it
            and the same schema is used directly in the output.

    Returns:
        A `PandasDataset` containing the converted data and the associated SDMX
        structure (either the provided schema or a generated one).

    Raises:
        Invalid: If the reference sdmx_type is not valid, if component types
            cannot be mapped, or if validation fails when schema is provided.
    """
    # If schema is provided
    if schema is not None:
        _validate_vtl_dataset_against_schema(dataset, schema)

        pandas_dataset = PandasDataset(
            structure=schema,
            data=_data(dataset),
        )
        return pandas_dataset

    # If schema is not provided, reference must be provided
    if reference is None:
        raise Invalid(
            "Validation Error",
            "Either schema or reference must be provided",
        )

    # Validate reference.sdmx_type
    if reference.sdmx_type not in VALID_SDMX_TYPES:
        raise Invalid(
            "Validation Error",
            f"Reference sdmx_type must be one of {VALID_SDMX_TYPES}, "
            f"but got '{reference.sdmx_type}'",
        )

    # Generate a new Schema from VTL Dataset components
    sdmx_components = []

    for comp_name, vtl_comp in dataset.components.items():
        # Map VTL data type to SDMX data type
        sdmx_dtype = _map_vtl_dtype_to_sdmx(vtl_comp.data_type)

        # Map VTL role to SDMX role
        sdmx_role = _map_vtl_role_to_sdmx(vtl_comp.role)

        # Determine attachment_level for attributes
        attachment_level = "O" if sdmx_role == Role.ATTRIBUTE else None

        # Create SDMX Component
        sdmx_comp = Component(
            id=comp_name,
            required=not vtl_comp.nullable,
            role=sdmx_role,
            concept=Concept(comp_name, dtype=sdmx_dtype),
            attachment_level=attachment_level,
        )
        sdmx_components.append(sdmx_comp)

    # Create Schema using reference information
    generated_schema = Schema(
        context=reference.sdmx_type.lower(),  # type: ignore[arg-type]
        agency=reference.agency,
        id=reference.id,
        version=reference.version,
        components=Components(sdmx_components),
    )

    pandas_dataset = PandasDataset(
        structure=generated_schema,
        data=_data(dataset),
    )
    return pandas_dataset


def _vtl_dtype_class(
    vtl_dtype_value: Union[ScalarType, Type[ScalarType]],
) -> Type[ScalarType]:
    """Return the class of a VTL scalar type, given as a class or instance."""
    if isinstance(vtl_dtype_value, type):
        return vtl_dtype_value
    return type(vtl_dtype_value)


def _map_vtl_dtype_to_sdmx(
    vtl_dtype_value: Union[ScalarType, Type[ScalarType]],
) -> DataType:
    """Return the SDMX DataType for a given VTL scalar.

    Args:
        vtl_dtype_value: The VTL scalar type or instance to map.

    Returns:
        The corresponding SDMX DataType.

    Raises:
        Invalid: If the VTL DataType cannot be mapped to an SDMX DataType.
    """
    vtl_dtype_class = _vtl_dtype_class(vtl_dtype_value)

    if vtl_dtype_class not in VTL_TO_SDMX_TYPE_MAP:
        supported = ", ".join(str(t.__name__) for t in VTL_TO_SDMX_TYPE_MAP)
        raise Invalid(
            "Validation Error",
            f"VTL DataType '{vtl_dtype_class.__name__}' cannot be "
            f"mapped to an SDMX type. Supported types are: {supported}",
        )

    return VTL_TO_SDMX_TYPE_MAP[vtl_dtype_class]


def _map_vtl_role_to_sdmx(vtl_role: VTLRole) -> Role:
    """Return the SDMX Role for a given VTL Role.

    Args:
        vtl_role: The VTLRole to map.

    Returns:
        The corresponding SDMX Role.

    Raises:
        Invalid: If the VTL Role cannot be mapped to an SDMX Role.
    """
    if vtl_role not in VTL_TO_SDMX_ROLE_MAP:
        raise Invalid(
            "Validation Error",
            f"VTL Role '{vtl_role}' cannot be mapped to an SDMX Role",
        )
    return VTL_TO_SDMX_ROLE_MAP[vtl_role]


def _validate_vtl_dataset_against_schema(
    dataset: VTLengineDataset,
    schema: Schema,
) -> None:
    """Validate VTLengine Dataset against SDMX Schema.

    Args:
        dataset: The VTLengineDataset instance whose components, roles, and
            data types will be validated.
        schema: The SDMX Schema that defines the expected components,
            SDMX data types, and SDMX roles for validation.

    Raises:
        Invalid: If component names differ, if types or roles cannot be mapped,
                 or if any mismatch is detected between the Dataset and Schema.
    """
    # Validate that schema components match VTL dataset components
    vtl_component_names = set(dataset.components.keys())
    schema_component_names = {comp.id for comp in schema.components}

    if vtl_component_names != schema_component_names:
        missing_in_schema = vtl_component_names - schema_component_names
        missing_in_vtl = schema_component_names - vtl_component_names
        error_parts = []
        if missing_in_schema:
            error_parts.append(
                f"VTL components not in Schema: {missing_in_schema}"
            )
        if missing_in_vtl:
            error_parts.append(
                f"Schema components not in VTL: {missing_in_vtl}"
            )
        raise Invalid(
            "Validation Error",
            "Component mismatch between VTL Dataset and Schema. "
            f"{'; '.join(error_parts)}",
        )

    # Validate that component types and roles match
    for component in schema.components:
        comp_id = str(component.id)
        vtl_comp = dataset.components[comp_id]

        # Validate the data type: the VTL type must be supported, and the
        # SDMX type of the schema must be one mapped to it
        _map_vtl_dtype_to_sdmx(vtl_comp.data_type)
        vtl_dtype_class = _vtl_dtype_class(vtl_comp.data_type)
        if component.dtype not in SDMX_TYPES_BY_VTL_TYPE[vtl_dtype_class]:
            raise Invalid(
                "Validation Error",
                "Component mismatch between VTL Dataset and Schema. "
                f"Component '{comp_id}' has type {vtl_dtype_class.__name__} "
                f"in VTL but {component.dtype} in Schema",
            )

        # Validate role using helper
        expected_sdmx_role = _map_vtl_role_to_sdmx(vtl_comp.role)
        if component.role != expected_sdmx_role:
            raise Invalid(
                "Validation Error",
                "Component mismatch between VTL Dataset and Schema. "
                f"Component '{comp_id}' has role {expected_sdmx_role} "
                f"in VTL but {component.role} in Schema",
            )


def convert_codelist_to_vtl(
    codelist: Codelist, vtl_value_domain_name: str
) -> ValueDomain:
    """Convert a codelist to a vtlengine Value Domain.

    The values of the Value Domain are the ids of the codes, as strings.

    Args:
        codelist: The codelist (or value list) to convert.
        vtl_value_domain_name: The name for the vtlengine Value Domain,
            e.g. the alias of the VTL mapping of the codelist.

    Returns:
        A vtlengine Value Domain of type String with the ids of the codes.
    """
    return ValueDomain(
        name=vtl_value_domain_name,
        type=String,
        setlist=[code.id for code in codelist.codes],
    )


def convert_value_domain_to_sdmx(
    value_domain: ValueDomain, reference: Reference
) -> Codelist:
    """Convert a vtlengine Value Domain to a codelist.

    The codelist has a code for each value of the Value Domain, whose id
    and name are the value, and the name of the Value Domain.

    Args:
        value_domain: The vtlengine Value Domain to convert.
        reference: The reference to the codelist to create (Codelist), or
            to the value list (ValueList) if the values are not valid ids
            of codes.

    Returns:
        The codelist, or value list, with the values of the Value Domain.

    Raises:
        Invalid: If the reference is not to a Codelist or ValueList.
    """
    if reference.sdmx_type not in ("Codelist", "ValueList"):
        raise Invalid(
            "Validation Error",
            "Reference sdmx_type must be Codelist or ValueList, "
            f"but got '{reference.sdmx_type}'",
        )
    return Codelist(
        id=reference.id,
        agency=reference.agency,
        version=reference.version,
        name=value_domain.name,
        items=[
            Code(id=str(value), name=str(value))
            for value in value_domain.setlist
        ],
        sdmx_type=(
            "valuelist" if reference.sdmx_type == "ValueList" else "codelist"
        ),
    )
