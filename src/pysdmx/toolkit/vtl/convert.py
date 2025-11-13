"""Conversions between pysdmx PandasDataset and vtlengine Dataset."""

from typing import Dict, Type

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

# Role mappings
SDMX_TO_VTL_ROLE_MAP: Dict[Role, VTLRole] = {
    Role.DIMENSION: VTLRole.IDENTIFIER,
    Role.MEASURE: VTLRole.MEASURE,
    Role.ATTRIBUTE: VTLRole.ATTRIBUTE,
}



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
