"""Conversions between pysdmx PandasDataset and vtlengine Dataset."""

from typing import Dict, Optional, Type

from vtlengine.DataTypes import (  # type: ignore[import-untyped]
    Boolean,
    Date,
    Duration,
    Integer,
    Number,
    ScalarType,
    String,
    # Time,
    TimePeriod,
)
from vtlengine.Model import (  # type: ignore[import-untyped]
    Component as VTLComponent,
)
from vtlengine.Model import Dataset as VTLengineDataset
from vtlengine.Model import Role as VTLRole

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.model import Component, Components, Concept, Reference
from pysdmx.model.concept import DataType
from pysdmx.model.dataflow import Role, Schema

SDMX_TO_VTL_TYPE_MAP: Dict[DataType, Type[ScalarType]] = {
    DataType.STRING: String,
    DataType.INTEGER: Integer,
    DataType.DOUBLE: Number,
    DataType.BOOLEAN: Boolean,
    DataType.DATE: Date,         # GregorianDay
    DataType.PERIOD: TimePeriod, # ObservationalTimePeriod
    # DataType.TIME: Time,
    DataType.DURATION: Duration,
}
VTL_TO_SDMX_TYPE_MAP: Dict[Type[ScalarType], DataType] = {
    String: DataType.STRING,
    Integer: DataType.INTEGER,
    Number: DataType.DOUBLE,
    Boolean: DataType.BOOLEAN,
    Date: DataType.DATE,
    TimePeriod: DataType.PERIOD,
    # Time: DataType.TIME,
    Duration: DataType.DURATION,
}

# Role mappings
SDMX_TO_VTL_ROLE_MAP: Dict[Role, VTLRole] = {
    Role.DIMENSION: VTLRole.IDENTIFIER,
    Role.MEASURE: VTLRole.MEASURE,
    Role.ATTRIBUTE: VTLRole.ATTRIBUTE,
}
VTL_TO_SDMX_ROLE_MAP: Dict[VTLRole, Role] = {
    VTLRole.IDENTIFIER: Role.DIMENSION,
    VTLRole.MEASURE: Role.MEASURE,
    VTLRole.ATTRIBUTE: Role.ATTRIBUTE,
}

VALID_SDMX_TYPES = {"DataStructure", "Dataflow", "ProvisionAgreement"}


def convert_dataset_to_vtl(
    dataset: PandasDataset, vtl_dataset_name: str
) -> VTLengineDataset:
    """Convert a PandasDataset to a vtlengine Dataset.

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

    # Get dataframe columns if data is provided
    if pd_dataset is not None:
        pd_dataset_columns = set(pd_dataset.columns)
    else:
        pd_dataset_columns = set()

    # Convert components from SDMX to VTL format
    vtl_components: Dict[str, VTLComponent] = {}
    for component in schema.components:
        component_id = str(component.id)

        # Ensure component column exists in dataframe (if data provided)
        if pd_dataset_columns and component_id not in pd_dataset_columns:
            raise Invalid(
                "Validation Error",
                f"Component '{component_id}' defined in Schema not found "
                "in dataset.data columns",
            )

        # Map the data type
        sdmx_dtype = component.dtype
        if sdmx_dtype not in SDMX_TO_VTL_TYPE_MAP:
            supported = ", ".join(str(t) for t in SDMX_TO_VTL_TYPE_MAP)
            raise Invalid(
                "Validation Error",
                f"SDMX DataType '{sdmx_dtype}' cannot be mapped to a "
                f"VTL type. Supported types are: {supported}",
            )
        vtl_dtype = SDMX_TO_VTL_TYPE_MAP[sdmx_dtype]

        # Map the role
        if component.role not in SDMX_TO_VTL_ROLE_MAP:
            raise Invalid(
                "Validation Error",
                f"SDMX Role '{component.role}' cannot be mapped to a VTL Role",
            )
        vtl_role = SDMX_TO_VTL_ROLE_MAP[component.role]

        # Create VTL component (nullable is the opposite of required)
        vtl_comp = VTLComponent(
            name=component_id,
            data_type=vtl_dtype,
            role=vtl_role,
            nullable=not getattr(component, "required", False),
        )
        vtl_components[component_id] = vtl_comp

    # Create the vtlengine Dataset
    vtl_dataset = VTLengineDataset(
        name=vtl_dataset_name,
        components=vtl_components,
        data=pd_dataset
    )

    return vtl_dataset


def convert_dataset_to_sdmx(
    dataset: VTLengineDataset,
    reference: Optional[Reference] = None,
    schema: Optional[Schema] = None,
) -> PandasDataset:
    """Convert a vtlengine Dataset to a PandasDataset.

    Args:
        dataset: The vtlengine Dataset to convert.
        reference: Optional Reference to the SDMX structure (DataStructure,
            Dataflow, or ProvisionAgreement) used for metadata.
        schema: Optional Schema object. If provided, it will be used for
            validation. If not provided, a Schema will be generated from
            the VTL Dataset components.

    Returns:
        A PandasDataset with the data and structure from the vtlengine Dataset.

    Raises:
        Invalid: If the reference sdmx_type is not valid, if component types
            cannot be mapped, or if validation fails when schema is provided.
    """
    # If schema is provided
    if schema is not None:
        _validate_vtl_dataset_against_schema(dataset, schema)
        pandas_dataset = PandasDataset(
            structure=schema,
            data=dataset.data,
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
        data=dataset.data,
    )

    return pandas_dataset

def _map_vtl_dtype_to_sdmx(vtl_dtype_value: ScalarType) -> DataType:
    """Return the SDMX DataType for a given VTL scalar.

    Args:
        vtl_dtype_value: The VTL scalar type or instance to map.

    Returns:
        The corresponding SDMX DataType.

    Raises:
        Invalid: If the VTL DataType cannot be mapped to an SDMX DataType.
    """
    vtl_dtype_class = (
        vtl_dtype_value if isinstance(vtl_dtype_value, type)
        else type(vtl_dtype_value)
    )
    if vtl_dtype_class not in VTL_TO_SDMX_TYPE_MAP:
        supported = ", ".join(t.__name__ for t in VTL_TO_SDMX_TYPE_MAP)
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

        # Validate data type using helper
        expected_sdmx_dtype = _map_vtl_dtype_to_sdmx(vtl_comp.data_type)
        if component.dtype != expected_sdmx_dtype:
            raise Invalid(
                "Validation Error",
                "Component mismatch between VTL Dataset and Schema. "
                f"Component '{comp_id}' has type {expected_sdmx_dtype} "
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
