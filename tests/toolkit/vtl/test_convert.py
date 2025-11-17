"""Tests for VTL and SDMX conversion functions."""

import pandas as pd
import pytest
from vtlengine.DataTypes import (
    Boolean,
    Date,
    Duration,
    Integer,
    Number,
    String,
    TimeInterval,
    TimePeriod,
)
from vtlengine.Model import Component as VTLComponent
from vtlengine.Model import Dataset as VTLengineDataset
from vtlengine.Model import Role as VTLRole

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.model import (
    Component,
    Components,
    Concept,
    DataType,
    Reference,
    Role,
    Schema,
)
from pysdmx.toolkit.vtl import convert_dataset_to_sdmx, convert_dataset_to_vtl

# Tests for convert_dataset_to_vtl


@pytest.fixture
def basic_schema() -> Schema:
    """Create a basic schema with common components."""
    return Schema(
        context="datastructure",
        agency="TEST",
        id="TEST_DSD",
        version="1.0",
        components=Components(
            [
                Component(
                    id="FREQ",
                    required=True,
                    role=Role.DIMENSION,
                    concept=Concept("FREQ", dtype=DataType.STRING),
                ),
                Component(
                    id="REF_AREA",
                    required=True,
                    role=Role.DIMENSION,
                    concept=Concept("REF_AREA", dtype=DataType.STRING),
                ),
                Component(
                    id="OBS_VALUE",
                    required=False,
                    role=Role.MEASURE,
                    concept=Concept("OBS_VALUE", dtype=DataType.DOUBLE),
                ),
                Component(
                    id="OBS_STATUS",
                    required=False,
                    role=Role.ATTRIBUTE,
                    concept=Concept("OBS_STATUS", dtype=DataType.STRING),
                    attachment_level="O",
                ),
            ]
        ),
    )


@pytest.fixture
def all_types_schema() -> Schema:
    """Create a schema with all supported data types."""
    return Schema(
        context="datastructure",
        agency="TEST",
        id="ALL_TYPES",
        version="1.0",
        components=Components(
            [
                Component(
                    id="STRING_DIM",
                    required=True,
                    role=Role.DIMENSION,
                    concept=Concept("STRING_DIM", dtype=DataType.STRING),
                ),
                Component(
                    id="INTEGER_MEASURE",
                    required=True,
                    role=Role.MEASURE,
                    concept=Concept("INTEGER_MEASURE", dtype=DataType.INTEGER),
                ),
                Component(
                    id="DOUBLE_MEASURE",
                    required=True,
                    role=Role.MEASURE,
                    concept=Concept("DOUBLE_MEASURE", dtype=DataType.DOUBLE),
                ),
                Component(
                    id="BOOLEAN_ATTR",
                    required=False,
                    role=Role.ATTRIBUTE,
                    concept=Concept("BOOLEAN_ATTR", dtype=DataType.BOOLEAN),
                    attachment_level="O",
                ),
                Component(
                    id="DATE_ATTR",
                    required=False,
                    role=Role.ATTRIBUTE,
                    concept=Concept("DATE_ATTR", dtype=DataType.DATE),
                    attachment_level="O",
                ),
                Component(
                    id="PERIOD_DIM",
                    required=True,
                    role=Role.DIMENSION,
                    concept=Concept("PERIOD_DIM", dtype=DataType.PERIOD),
                ),
                Component(
                    id="DURATION_ATTR",
                    required=False,
                    role=Role.ATTRIBUTE,
                    concept=Concept("DURATION_ATTR", dtype=DataType.DURATION),
                    attachment_level="O",
                ),
                Component(
                    id="TIME_ATTR",
                    required=False,
                    role=Role.ATTRIBUTE,
                    concept=Concept("TIME_ATTR", dtype=DataType.TIME),
                    attachment_level="O",
                ),
            ]
        ),
    )


@pytest.fixture
def basic_dataframe() -> pd.DataFrame:
    """Create a basic DataFrame matching basic_schema."""
    return pd.DataFrame(
        {
            "FREQ": ["A", "M", "Q"],
            "REF_AREA": ["US", "EU", "JP"],
            "OBS_VALUE": [100.5, 200.3, 150.7],
            "OBS_STATUS": ["A", "E", "A"],
        }
    )


@pytest.fixture
def all_types_dataframe() -> pd.DataFrame:
    """Create a DataFrame with all supported types."""
    return pd.DataFrame(
        {
            "STRING_DIM": ["A", "B", "C"],
            "INTEGER_MEASURE": [1, 2, 3],
            "DOUBLE_MEASURE": [1.5, 2.5, 3.5],
            "BOOLEAN_ATTR": [True, False, True],
            "DATE_ATTR": ["2025-01-01", "2025-01-02", "2025-01-03"],
            "PERIOD_DIM": ["2025", "2025-01", "2025-Q1"],
            "DURATION_ATTR": ["P1Y", "P1M", "P1D"],
        }
    )


def test_convert_to_vtl_basic_conversion(
    basic_schema: Schema, basic_dataframe: pd.DataFrame
) -> None:
    """Test basic conversion of a PandasDataset to a VTL Dataset."""
    dataset = PandasDataset(structure=basic_schema, data=basic_dataframe)

    vtl_dataset = convert_dataset_to_vtl(dataset, "test_dataset")

    assert vtl_dataset.name == "test_dataset"
    assert len(vtl_dataset.components) == 4
    assert vtl_dataset.data is not None
    assert len(vtl_dataset.data) == 3

    # Check component roles
    assert vtl_dataset.components["FREQ"].role == VTLRole.IDENTIFIER
    assert vtl_dataset.components["REF_AREA"].role == VTLRole.IDENTIFIER
    assert vtl_dataset.components["OBS_VALUE"].role == VTLRole.MEASURE
    assert vtl_dataset.components["OBS_STATUS"].role == VTLRole.ATTRIBUTE

    # Check a component's type
    assert vtl_dataset.components["OBS_VALUE"].data_type is Number


def test_convert_to_vtl_component_types(
    all_types_schema: Schema, all_types_dataframe: pd.DataFrame
) -> None:
    """Test that all SDMX data types are correctly mapped to VTL types."""
    dataset = PandasDataset(
        structure=all_types_schema, data=all_types_dataframe
    )

    vtl_dataset = convert_dataset_to_vtl(dataset, "test_dataset")

    # Check type mappings
    assert vtl_dataset.components["STRING_DIM"].data_type is String
    assert vtl_dataset.components["INTEGER_MEASURE"].data_type is Integer
    assert vtl_dataset.components["DOUBLE_MEASURE"].data_type is Number
    assert vtl_dataset.components["BOOLEAN_ATTR"].data_type is Boolean
    assert vtl_dataset.components["DATE_ATTR"].data_type is Date
    assert vtl_dataset.components["PERIOD_DIM"].data_type is TimePeriod
    assert vtl_dataset.components["DURATION_ATTR"].data_type is Duration
    # TimeInterval not yet supported by vtlengine
    assert vtl_dataset.components["TIME_ATTR"].data_type is String


def test_convert_to_vtl_nullable_matches_required_flag(
    basic_schema: Schema, basic_dataframe: pd.DataFrame
) -> None:
    """Test that nullable is correctly derived from the required flag."""
    dataset = PandasDataset(structure=basic_schema, data=basic_dataframe)
    vtl_dataset = convert_dataset_to_vtl(dataset, "test_dataset")

    # FREQ, REF_AREA: required=True -> nullable=False
    assert vtl_dataset.components["FREQ"].nullable is False
    assert vtl_dataset.components["REF_AREA"].nullable is False

    # OBS_VALUE, OBS_STATUS: required=False -> nullable=True
    assert vtl_dataset.components["OBS_VALUE"].nullable is True
    assert vtl_dataset.components["OBS_STATUS"].nullable is True


def test_convert_to_vtl_dataset_without_data(basic_schema: Schema) -> None:
    """Test conversion of a dataset without data (None or empty DataFrame)."""
    # Test with None data
    dataset_none = PandasDataset(structure=basic_schema, data=None)  # type: ignore[arg-type]
    vtl_dataset_none = convert_dataset_to_vtl(
        dataset_none, "empty_dataset_none"
    )

    assert vtl_dataset_none.name == "empty_dataset_none"
    assert len(vtl_dataset_none.components) == 4
    assert vtl_dataset_none.data is None

    # Test with empty DataFrame
    empty_df = pd.DataFrame(
        columns=["FREQ", "REF_AREA", "OBS_VALUE", "OBS_STATUS"]
    )
    dataset_empty = PandasDataset(structure=basic_schema, data=empty_df)
    vtl_dataset_empty = convert_dataset_to_vtl(
        dataset_empty, "empty_dataset_df"
    )

    assert vtl_dataset_empty.name == "empty_dataset_df"
    assert len(vtl_dataset_empty.components) == 4
    assert vtl_dataset_empty.data is not None
    assert len(vtl_dataset_empty.data) == 0


def test_convert_to_vtl_dataset_with_string_structure() -> None:
    """Test that conversion fails when structure is a string."""
    dataset = PandasDataset(
        structure="DataStructure=BIS:BIS_DER(1.0)", data=pd.DataFrame()
    )

    with pytest.raises(
        Invalid,
        match="Dataset structure must be a Schema "
        "object for conversion to VTL",
    ):
        convert_dataset_to_vtl(dataset, "test_dataset")


# Tests for convert_dataset_to_sdmx


@pytest.fixture
def vtl_basic_dataset() -> VTLengineDataset:
    """Create a basic VTL Dataset."""
    components = {
        "FREQ": VTLComponent(
            name="FREQ",
            data_type=String(),
            role=VTLRole.IDENTIFIER,
            nullable=False,
        ),
        "REF_AREA": VTLComponent(
            name="REF_AREA",
            data_type=String(),
            role=VTLRole.IDENTIFIER,
            nullable=False,
        ),
        "OBS_VALUE": VTLComponent(
            name="OBS_VALUE",
            data_type=Number(),
            role=VTLRole.MEASURE,
            nullable=True,
        ),
        "OBS_STATUS": VTLComponent(
            name="OBS_STATUS",
            data_type=String(),
            role=VTLRole.ATTRIBUTE,
            nullable=True,
        ),
    }
    data = pd.DataFrame(
        {
            "FREQ": ["A", "M", "Q"],
            "REF_AREA": ["US", "EU", "JP"],
            "OBS_VALUE": [100.5, 200.3, 150.7],
            "OBS_STATUS": ["A", "E", "A"],
        }
    )
    return VTLengineDataset(name="test_vtl", components=components, data=data)


@pytest.fixture
def vtl_all_types_dataset() -> VTLengineDataset:
    """Create a VTL Dataset with all supported types."""
    components = {
        "STRING_DIM": VTLComponent(
            name="STRING_DIM",
            data_type=String(),
            role=VTLRole.IDENTIFIER,
            nullable=False,
        ),
        "INTEGER_MEASURE": VTLComponent(
            name="INTEGER_MEASURE",
            data_type=Integer(),
            role=VTLRole.MEASURE,
            nullable=False,
        ),
        "DOUBLE_MEASURE": VTLComponent(
            name="DOUBLE_MEASURE",
            data_type=Number(),
            role=VTLRole.MEASURE,
            nullable=False,
        ),
        "BOOLEAN_ATTR": VTLComponent(
            name="BOOLEAN_ATTR",
            data_type=Boolean(),
            role=VTLRole.ATTRIBUTE,
            nullable=True,
        ),
        "DATE_ATTR": VTLComponent(
            name="DATE_ATTR",
            data_type=Date(),
            role=VTLRole.ATTRIBUTE,
            nullable=True,
        ),
        "PERIOD_DIM": VTLComponent(
            name="PERIOD_DIM",
            data_type=TimePeriod(),
            role=VTLRole.IDENTIFIER,
            nullable=False,
        ),
        "DURATION_ATTR": VTLComponent(
            name="DURATION_ATTR",
            data_type=Duration(),
            role=VTLRole.ATTRIBUTE,
            nullable=True,
        ),
        "TIME_ATTR": VTLComponent(
            name="TIME_ATTR",
            data_type=TimeInterval(),
            role=VTLRole.ATTRIBUTE,
            nullable=True,
        ),
    }
    data = pd.DataFrame(
        {
            "STRING_DIM": ["A", "B", "C"],
            "INTEGER_MEASURE": [1, 2, 3],
            "DOUBLE_MEASURE": [1.5, 2.5, 3.5],
            "BOOLEAN_ATTR": [True, False, True],
            "DATE_ATTR": ["2025-01-01", "2025-01-02", "2025-01-03"],
            "PERIOD_DIM": ["2025", "2025-01", "2025-Q1"],
            "DURATION_ATTR": ["P1Y", "P1M", "P1D"],
            "TIME_ATTR": ["12:00:00", "13:30:00", "14:45:00"],
        }
    )
    return VTLengineDataset(
        name="test_all_types", components=components, data=data
    )


@pytest.fixture
def basic_reference() -> Reference:
    """Create a basic Reference."""
    return Reference(
        sdmx_type="DataStructure",
        agency="TEST",
        id="TEST_DSD",
        version="1.0",
    )


def test_convert_to_sdmx_with_schema(
    vtl_basic_dataset: VTLengineDataset,
    basic_schema: Schema,
) -> None:
    """Test conversion with provided Schema."""
    pandas_dataset = convert_dataset_to_sdmx(
        vtl_basic_dataset, schema=basic_schema
    )

    assert isinstance(pandas_dataset, PandasDataset)
    assert pandas_dataset.structure == basic_schema
    assert pandas_dataset.data is not None
    assert len(pandas_dataset.data) == 3
    assert list(pandas_dataset.data.columns) == [
        "FREQ",
        "REF_AREA",
        "OBS_VALUE",
        "OBS_STATUS",
    ]


@pytest.mark.parametrize(
    ("sdmx_type", "expected_context", "ref_id", "version"),
    [
        ("DataStructure", "datastructure", "TEST_DSD", "1.0"),
        ("Dataflow", "dataflow", "TEST_DF", "2.0"),
        ("ProvisionAgreement", "provisionagreement", "TEST_PA", "3.0"),
    ],
)
def test_convert_to_sdmx_with_reference(
    vtl_basic_dataset: VTLengineDataset,
    sdmx_type: str,
    expected_context: str,
    ref_id: str,
    version: str,
) -> None:
    """Test conversion with different Reference types (generates Schema)."""
    reference = Reference(
        sdmx_type=sdmx_type,
        agency="TEST",
        id=ref_id,
        version=version,
    )

    pandas_dataset = convert_dataset_to_sdmx(vtl_basic_dataset, reference)

    assert isinstance(pandas_dataset, PandasDataset)
    assert isinstance(pandas_dataset.structure, Schema)

    # Check schema properties
    schema = pandas_dataset.structure
    assert schema.context == expected_context
    assert schema.agency == "TEST"
    assert schema.id == ref_id
    assert schema.version == version
    assert len(schema.components) == 4

    # Check role and required mappings
    components_dict = {comp.id: comp for comp in schema.components}
    assert components_dict["FREQ"].role == Role.DIMENSION
    assert components_dict["FREQ"].required is True
    assert components_dict["REF_AREA"].role == Role.DIMENSION
    assert components_dict["REF_AREA"].required is True
    assert components_dict["OBS_VALUE"].role == Role.MEASURE
    assert components_dict["OBS_VALUE"].required is False
    assert components_dict["OBS_STATUS"].role == Role.ATTRIBUTE
    assert components_dict["OBS_STATUS"].required is False


def test_convert_to_sdmx_type_mappings(
    vtl_all_types_dataset: VTLengineDataset,
    basic_reference: Reference,
) -> None:
    """Test that all VTL types are correctly mapped to SDMX types."""
    pandas_dataset = convert_dataset_to_sdmx(
        vtl_all_types_dataset, basic_reference
    )

    schema = pandas_dataset.structure
    assert isinstance(schema, Schema)
    components_dict = {comp.id: comp for comp in schema.components}

    assert components_dict["STRING_DIM"].dtype == DataType.STRING
    assert components_dict["INTEGER_MEASURE"].dtype == DataType.INTEGER
    assert components_dict["DOUBLE_MEASURE"].dtype == DataType.DOUBLE
    assert components_dict["BOOLEAN_ATTR"].dtype == DataType.BOOLEAN
    assert components_dict["DATE_ATTR"].dtype == DataType.DATE
    assert components_dict["PERIOD_DIM"].dtype == DataType.PERIOD
    assert components_dict["DURATION_ATTR"].dtype == DataType.DURATION
    assert components_dict["TIME_ATTR"].dtype == DataType.TIME

    # Attributes should have attachment_level "O"
    assert components_dict["BOOLEAN_ATTR"].attachment_level == "O"
    assert components_dict["DATE_ATTR"].attachment_level == "O"
    assert components_dict["DURATION_ATTR"].attachment_level == "O"
    assert components_dict["TIME_ATTR"].attachment_level == "O"

    # Non-attributes should not have attachment_level
    assert components_dict["STRING_DIM"].attachment_level is None
    assert components_dict["INTEGER_MEASURE"].attachment_level is None
    assert components_dict["DOUBLE_MEASURE"].attachment_level is None
    assert components_dict["PERIOD_DIM"].attachment_level is None


def test_convert_to_sdmx_without_data(
    basic_reference: Reference,
) -> None:
    """Test conversion of VTL Dataset without data.

    (None or empty DataFrame).
    """
    components = {
        "DIM1": VTLComponent(
            name="DIM1",
            data_type=String(),
            role=VTLRole.IDENTIFIER,
            nullable=False,
        ),
    }

    # Test with None data
    vtl_dataset_none = VTLengineDataset(
        name="empty_none", components=components, data=None
    )
    pandas_dataset_none = convert_dataset_to_sdmx(
        vtl_dataset_none, basic_reference
    )

    assert pandas_dataset_none.data is None
    assert len(pandas_dataset_none.structure.components) == 1

    # Test with empty DataFrame
    empty_df = pd.DataFrame(columns=["DIM1"])
    vtl_dataset_empty = VTLengineDataset(
        name="empty_df", components=components, data=empty_df
    )
    pandas_dataset_empty = convert_dataset_to_sdmx(
        vtl_dataset_empty, basic_reference
    )

    assert pandas_dataset_empty.data is not None
    assert len(pandas_dataset_empty.data) == 0
    assert len(pandas_dataset_empty.structure.components) == 1


def test_convert_to_sdmx_no_schema_no_reference(
    vtl_basic_dataset: VTLengineDataset,
) -> None:
    """Test that conversion fails without schema or reference."""
    with pytest.raises(
        Invalid,
        match="Either schema or reference must be provided",
    ):
        convert_dataset_to_sdmx(vtl_basic_dataset)


def test_convert_to_sdmx_invalid_sdmx_type(
    vtl_basic_dataset: VTLengineDataset,
) -> None:
    """Test that conversion fails with invalid Reference sdmx_type."""
    invalid_reference = Reference(
        sdmx_type="InvalidType",
        agency="TEST",
        id="TEST",
        version="1.0",
    )

    with pytest.raises(
        Invalid,
        match="Reference sdmx_type must be one of",
    ):
        convert_dataset_to_sdmx(vtl_basic_dataset, invalid_reference)


def test_convert_to_sdmx_schema_mismatch_vtl_extra_and_missing(
    basic_schema: Schema,
) -> None:
    """VTL dataset has an extra component missing some from the schema."""
    components = {
        "FREQ": VTLComponent(
            name="FREQ",
            data_type=String(),
            role=VTLRole.IDENTIFIER,
            nullable=False,
        ),
        "REF_AREA": VTLComponent(
            name="REF_AREA",
            data_type=String(),
            role=VTLRole.IDENTIFIER,
            nullable=False,
        ),
        "EXTRA_COMPONENT": VTLComponent(
            name="EXTRA_COMPONENT",
            data_type=String(),
            role=VTLRole.ATTRIBUTE,
            nullable=True,
        ),
        # OBS_VALUE and OBS_STATUS are missing
    }

    vtl_dataset = VTLengineDataset(
        name="test", components=components, data=None
    )

    with pytest.raises(
        Invalid,
        match="Component mismatch between VTL Dataset and Schema",
    ):
        convert_dataset_to_sdmx(vtl_dataset, schema=basic_schema)


def test_convert_to_sdmx_schema_mismatch_schema_missing_components(
    vtl_basic_dataset: VTLengineDataset,
) -> None:
    """Schema is missing components that exist in VTL dataset."""
    schema = Schema(
        context="datastructure",
        agency="TEST",
        id="TEST_DSD",
        version="1.0",
        components=Components(
            [
                Component(
                    id="FREQ",
                    required=True,
                    role=Role.DIMENSION,
                    concept=Concept("FREQ", dtype=DataType.STRING),
                ),
                Component(
                    id="REF_AREA",
                    required=True,
                    role=Role.DIMENSION,
                    concept=Concept("REF_AREA", dtype=DataType.STRING),
                ),
                # Missing OBS_VALUE and OBS_STATUS
                Component(
                    id="EXTRA_COMPONENT",
                    required=False,
                    role=Role.ATTRIBUTE,
                    concept=Concept("EXTRA_COMPONENT", dtype=DataType.STRING),
                    attachment_level="O",
                ),
            ]
        ),
    )

    with pytest.raises(
        Invalid,
        match="Component mismatch between VTL Dataset and Schema",
    ):
        convert_dataset_to_sdmx(vtl_basic_dataset, schema=schema)


def test_convert_to_sdmx_schema_mismatch_wrong_type(
    vtl_basic_dataset: VTLengineDataset,
) -> None:
    """Schema has different type for OBS_VALUE.

    (INTEGER instead of DOUBLE/Number).
    """
    schema = Schema(
        context="datastructure",
        agency="TEST",
        id="TEST_DSD",
        version="1.0",
        components=Components(
            [
                Component(
                    id="FREQ",
                    required=True,
                    role=Role.DIMENSION,
                    concept=Concept("FREQ", dtype=DataType.STRING),
                ),
                Component(
                    id="REF_AREA",
                    required=True,
                    role=Role.DIMENSION,
                    concept=Concept("REF_AREA", dtype=DataType.STRING),
                ),
                Component(
                    id="OBS_VALUE",
                    required=False,
                    role=Role.MEASURE,
                    concept=Concept("OBS_VALUE", dtype=DataType.INTEGER),
                ),
                Component(
                    id="OBS_STATUS",
                    required=False,
                    role=Role.ATTRIBUTE,
                    concept=Concept("OBS_STATUS", dtype=DataType.STRING),
                    attachment_level="O",
                ),
            ]
        ),
    )

    with pytest.raises(
        Invalid,
        match="Component mismatch between VTL Dataset and Schema",
    ):
        convert_dataset_to_sdmx(vtl_basic_dataset, schema=schema)


def test_convert_to_sdmx_schema_mismatch_wrong_role(
    vtl_basic_dataset: VTLengineDataset,
) -> None:
    """Schema has different role for OBS_VALUE.

    (ATTRIBUTE instead of MEASURE).
    """
    schema = Schema(
        context="datastructure",
        agency="TEST",
        id="TEST_DSD",
        version="1.0",
        components=Components(
            [
                Component(
                    id="FREQ",
                    required=True,
                    role=Role.DIMENSION,
                    concept=Concept("FREQ", dtype=DataType.STRING),
                ),
                Component(
                    id="REF_AREA",
                    required=True,
                    role=Role.DIMENSION,
                    concept=Concept("REF_AREA", dtype=DataType.STRING),
                ),
                Component(
                    id="OBS_VALUE",
                    required=False,
                    role=Role.ATTRIBUTE,
                    concept=Concept("OBS_VALUE", dtype=DataType.DOUBLE),
                    attachment_level="O",
                ),
                Component(
                    id="OBS_STATUS",
                    required=False,
                    role=Role.ATTRIBUTE,
                    concept=Concept("OBS_STATUS", dtype=DataType.STRING),
                    attachment_level="O",
                ),
            ]
        ),
    )

    with pytest.raises(
        Invalid,
        match="Component mismatch between VTL Dataset and Schema",
    ):
        convert_dataset_to_sdmx(vtl_basic_dataset, schema=schema)


def test_convert_to_sdmx_schema_mismatch_schema_only_extra_component(
    vtl_basic_dataset: VTLengineDataset,
) -> None:
    """Schema has an extra component that is not present in VTL dataset."""
    schema_with_only_extra = Schema(
        context="datastructure",
        agency="TEST",
        id="TEST_DSD",
        version="1.0",
        components=Components(
            [
                Component(
                    id="FREQ",
                    required=True,
                    role=Role.DIMENSION,
                    concept=Concept("FREQ", dtype=DataType.STRING),
                ),
                Component(
                    id="REF_AREA",
                    required=True,
                    role=Role.DIMENSION,
                    concept=Concept("REF_AREA", dtype=DataType.STRING),
                ),
                Component(
                    id="OBS_VALUE",
                    required=False,
                    role=Role.MEASURE,
                    concept=Concept("OBS_VALUE", dtype=DataType.DOUBLE),
                ),
                Component(
                    id="OBS_STATUS",
                    required=False,
                    role=Role.ATTRIBUTE,
                    concept=Concept("OBS_STATUS", dtype=DataType.STRING),
                    attachment_level="O",
                ),
                Component(
                    id="EXTRA_COMPONENT",
                    required=False,
                    role=Role.ATTRIBUTE,
                    concept=Concept("EXTRA_COMPONENT", dtype=DataType.STRING),
                    attachment_level="O",
                ),
            ]
        ),
    )

    with pytest.raises(
        Invalid,
        match="Component mismatch between VTL Dataset and Schema",
    ):
        convert_dataset_to_sdmx(
            vtl_basic_dataset, schema=schema_with_only_extra
        )


def test_convert_to_sdmx_schema_mismatch_vtl_only_extra_component(
    basic_schema: Schema,
    vtl_basic_dataset: VTLengineDataset,
) -> None:
    """VTL dataset has an extra component missing some from the schema."""
    vtl_components_with_only_extra = dict(vtl_basic_dataset.components)
    vtl_components_with_only_extra["EXTRA_COMPONENT"] = VTLComponent(
        name="EXTRA_COMPONENT",
        data_type=String(),
        role=VTLRole.ATTRIBUTE,
        nullable=True,
    )
    vtl_dataset_with_only_extra = VTLengineDataset(
        name="test_extra_vtl",
        components=vtl_components_with_only_extra,
        data=None,
    )

    with pytest.raises(
        Invalid,
        match="Component mismatch between VTL Dataset and Schema",
    ):
        convert_dataset_to_sdmx(
            vtl_dataset_with_only_extra, schema=basic_schema
        )


def test_roundtrip_conversion(
    basic_schema: Schema,
    basic_dataframe: pd.DataFrame,
) -> None:
    """Test that converting SDMX -> VTL -> SDMX -> VTL preserves data."""
    # SDMX -> VTL
    original_dataset = PandasDataset(
        structure=basic_schema, data=basic_dataframe
    )
    vtl_dataset_1 = convert_dataset_to_vtl(original_dataset, "test_1")

    # VTL -> SDMX
    sdmx_dataset = convert_dataset_to_sdmx(vtl_dataset_1, schema=basic_schema)
    assert sdmx_dataset.structure == original_dataset.structure
    pd.testing.assert_frame_equal(sdmx_dataset.data, original_dataset.data)

    # SDMX -> VTL (second conversion)
    vtl_dataset_2 = convert_dataset_to_vtl(sdmx_dataset, "test_2")

    # Check that components match between the two VTL datasets
    assert len(vtl_dataset_2.components) == len(vtl_dataset_1.components)
    for comp_name in vtl_dataset_1.components:
        assert comp_name in vtl_dataset_2.components
        comp_1 = vtl_dataset_1.components[comp_name]
        comp_2 = vtl_dataset_2.components[comp_name]
        assert type(comp_2.data_type) is type(comp_1.data_type)
        assert comp_2.role == comp_1.role
        assert comp_2.nullable == comp_1.nullable

    # Check that data is preserved
    pd.testing.assert_frame_equal(vtl_dataset_2.data, vtl_dataset_1.data)


def test_convert_to_sdmx_unsupported_vtl_dtype(
    basic_reference: Reference,
) -> None:
    """Test unsupported VTL types raise Invalid via convert_dataset_to_sdmx."""

    class CustomScalar:
        pass

    components = {
        "DIM1": VTLComponent(
            name="DIM1",
            data_type=CustomScalar(),
            role=VTLRole.IDENTIFIER,
            nullable=False,
        ),
    }
    data = pd.DataFrame({"DIM1": ["A"]})
    vtl_dataset = VTLengineDataset(
        name="test_custom_scalar", components=components, data=data
    )

    with pytest.raises(
        Invalid,
        match="VTL DataType 'CustomScalar' cannot be mapped to an SDMX type",
    ):
        convert_dataset_to_sdmx(vtl_dataset, basic_reference)


def test_convert_to_sdmx_unsupported_vtl_role(
    basic_reference: Reference,
) -> None:
    """Test unsupported VTL roles raise Invalid via convert_dataset_to_sdmx."""

    class FakeRole:
        pass

    fake_role = FakeRole()

    components = {
        "DIM1": VTLComponent(
            name="DIM1",
            data_type=String(),
            role=fake_role,  # type: ignore[unused-ignore]
            nullable=False,
        ),
    }
    data = pd.DataFrame({"DIM1": ["A"]})
    vtl_dataset = VTLengineDataset(
        name="test_fake_role", components=components, data=data
    )

    with pytest.raises(
        Invalid,
        match="VTL Role",
    ):
        convert_dataset_to_sdmx(vtl_dataset, basic_reference)
