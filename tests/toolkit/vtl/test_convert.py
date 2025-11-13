"""Tests for VTL conversion functions."""

import pandas as pd
import pytest
from vtlengine.DataTypes import (  # type: ignore[import-untyped]
    Boolean,
    Date,
    Duration,
    Integer,
    Number,
    String,
    TimePeriod,
)
from vtlengine.Model import Role as VTLRole  # type: ignore[import-untyped]

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.model import Component, Components, Concept, DataType, Role, Schema
from pysdmx.toolkit.vtl import convert_dataset_to_vtl


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


def test_convert_basic_dataset(
    basic_schema: Schema,
    basic_dataframe: pd.DataFrame
) -> None:
    """Test conversion of a basic PandasDataset to VTL Dataset."""
    dataset = PandasDataset(structure=basic_schema, data=basic_dataframe)

    vtl_dataset = convert_dataset_to_vtl(dataset, "test_dataset")

    assert vtl_dataset.name == "test_dataset"
    assert len(vtl_dataset.components) == 4
    assert vtl_dataset.data is not None
    assert len(vtl_dataset.data) == 3


def test_convert_component_names(
    basic_schema: Schema,
    basic_dataframe: pd.DataFrame
) -> None:
    """Test that component names are correctly mapped."""
    dataset = PandasDataset(structure=basic_schema, data=basic_dataframe)

    vtl_dataset = convert_dataset_to_vtl(dataset, "test_dataset")

    assert "FREQ" in vtl_dataset.components
    assert "REF_AREA" in vtl_dataset.components
    assert "OBS_VALUE" in vtl_dataset.components
    assert "OBS_STATUS" in vtl_dataset.components


def test_convert_component_types(
    all_types_schema: Schema,
    all_types_dataframe: pd.DataFrame
) -> None:
    """Test that all SDMX data types are correctly mapped to VTL types."""
    dataset = PandasDataset(
        structure=all_types_schema, data=all_types_dataframe
    )

    vtl_dataset = convert_dataset_to_vtl(dataset, "test_dataset")

    # Check type mappings
    assert isinstance(
        vtl_dataset.components["STRING_DIM"].data_type, type(String)
    )
    assert isinstance(
        vtl_dataset.components["INTEGER_MEASURE"].data_type, type(Integer)
    )
    assert isinstance(
        vtl_dataset.components["DOUBLE_MEASURE"].data_type, type(Number)
    )
    assert isinstance(
        vtl_dataset.components["BOOLEAN_ATTR"].data_type, type(Boolean)
    )
    assert isinstance(
        vtl_dataset.components["DATE_ATTR"].data_type, type(Date)
    )
    assert isinstance(
        vtl_dataset.components["PERIOD_DIM"].data_type, type(TimePeriod)
    )
    assert isinstance(
        vtl_dataset.components["DURATION_ATTR"].data_type, type(Duration)
    )


def test_convert_component_roles(
    basic_schema: Schema,
    basic_dataframe: pd.DataFrame
) -> None:
    """Test that SDMX roles are correctly mapped to VTL roles."""
    dataset = PandasDataset(structure=basic_schema, data=basic_dataframe)

    vtl_dataset = convert_dataset_to_vtl(dataset, "test_dataset")

    # DIMENSION -> IDENTIFIER
    assert vtl_dataset.components["FREQ"].role == VTLRole.IDENTIFIER
    assert vtl_dataset.components["REF_AREA"].role == VTLRole.IDENTIFIER

    # MEASURE -> MEASURE
    assert vtl_dataset.components["OBS_VALUE"].role == VTLRole.MEASURE

    # ATTRIBUTE -> ATTRIBUTE
    assert vtl_dataset.components["OBS_STATUS"].role == VTLRole.ATTRIBUTE


def test_convert_dataset_without_data(basic_schema: Schema) -> None:
    """Test conversion of a dataset without data (None DataFrame)."""
    dataset = PandasDataset(structure=basic_schema, data=None)  # type: ignore[arg-type]

    vtl_dataset = convert_dataset_to_vtl(dataset, "empty_dataset")

    assert vtl_dataset.name == "empty_dataset"
    assert len(vtl_dataset.components) == 4
    assert vtl_dataset.data is None


def test_convert_dataset_with_string_structure() -> None:
    """Test that conversion fails when structure is a string."""
    dataset = PandasDataset(
        structure="DataStructure=BIS:BIS_DER(1.0)", data=pd.DataFrame()
    )

    with pytest.raises(Invalid, match="Dataset structure must be a Schema"):
        convert_dataset_to_vtl(dataset, "test_dataset")


def test_convert_missing_column_in_dataframe(basic_schema: Schema) -> None:
    """Test that conversion fails when DataFrame is missing a column."""
    incomplete_df = pd.DataFrame(
        {
            "FREQ": ["A", "M"],
            "REF_AREA": ["US", "EU"],
            # Missing OBS_VALUE and OBS_STATUS
        }
    )
    dataset = PandasDataset(structure=basic_schema, data=incomplete_df)

    # Should fail on the first missing column (OBS_VALUE)
    with pytest.raises(
        Invalid,
        match="Component 'OBS_VALUE' defined in Schema not found in "
        "dataset.data columns",
    ):
        convert_dataset_to_vtl(dataset, "test_dataset")


def test_convert_unsupported_data_type() -> None:
    """Test that conversion fails with unsupported data types."""
    schema = Schema(
        context="datastructure",
        agency="TEST",
        id="TEST_DSD",
        version="1.0",
        components=Components(
            [
                Component(
                    id="UNSUPPORTED",
                    required=True,
                    role=Role.DIMENSION,
                    concept=Concept("UNSUPPORTED", dtype=DataType.XHTML),
                )
            ]
        ),
    )
    df = pd.DataFrame({"UNSUPPORTED": ["<p>test</p>"]})
    dataset = PandasDataset(structure=schema, data=df)

    with pytest.raises(
        Invalid,
        match="SDMX DataType 'XHTML' cannot be mapped to a VTL type",
    ):
        convert_dataset_to_vtl(dataset, "test_dataset")


def test_convert_with_local_dtype() -> None:
    """Test conversion when component uses local_dtype.

    Instead of concept dtype.
    """
    schema = Schema(
        context="datastructure",
        agency="TEST",
        id="TEST_DSD",
        version="1.0",
        components=Components(
            [
                Component(
                    id="VALUE",
                    required=True,
                    role=Role.MEASURE,
                    concept=Concept("VALUE"),  # No dtype in concept
                    local_dtype=DataType.INTEGER,  # Local override
                )
            ]
        ),
    )
    df = pd.DataFrame({"VALUE": [1, 2, 3]})
    dataset = PandasDataset(structure=schema, data=df)

    vtl_dataset = convert_dataset_to_vtl(dataset, "test_dataset")

    # Should use local_dtype (INTEGER -> Integer)
    assert isinstance(
        vtl_dataset.components["VALUE"].data_type, type(Integer)
    )
