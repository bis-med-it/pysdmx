from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io import get_datasets, read_sdmx
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.sdmx30.writer.structure import write
from pysdmx.io.xml.sdmx30.writer.structure_specific import (
    write as write_str_spec,
)
from pysdmx.model import (
    Component,
    Components,
    Concept,
    DataStructureDefinition,
    DataType,
    Role,
    Schema,
)


@pytest.fixture
def samples_folder():
    """Fixture to provide the path to the samples folder."""
    return Path(__file__).parent / "samples"


roundtrip_files = [
    "dataflow_global_registry.xml",
    "dataflow_structure_children_21.xml",
]


@pytest.mark.parametrize("filename", roundtrip_files)
def test_roundtrip(samples_folder, filename, tmp_path):
    file_path = Path(samples_folder) / filename

    msg1 = read_sdmx(file_path, validate=False)

    result = write(msg1.structures)

    msg2 = read_sdmx(result)

    assert len(msg1.structures) == len(msg2.structures)


def test_attribute_relationship_roundtrip(samples_folder):
    # Read the SDMX-ML file with None attribute relationships
    file_path = samples_folder / "datastructure_att_rel_21.xml"
    message = read_sdmx(file_path.read_text(), validate=True)

    # Check we have it set to "D" (Dataflow)
    structure_one: DataStructureDefinition = message.structures[0]
    attribute_one = structure_one.components.attributes[0]
    assert attribute_one.attachment_level == "D"

    # Write it back to SDMX-ML format
    result = write(
        structures=message.structures,
        prettyprint=True,
    )
    # Check if a str:Dataflow is present in the output
    assert "<str:Dataflow/>" in result

    # Read the written content back
    read_message = read_sdmx(result, validate=True)

    structure_two: DataStructureDefinition = read_message.structures[0]
    attribute_two = structure_two.components.attributes[0]
    # Check if the attribute relationships are Dataflow
    assert attribute_two.attachment_level == "D"

    assert attribute_one == attribute_two


def test_data_write_nullable_nulltypes():
    # Create dataframe with null values
    data = pd.DataFrame(
        data={
            "DIM1": ["X", "Y", "Z", "W"],
            "OBS_VALUE": [None, 1, None, pd.NA],
        }
    )
    data["OBS_VALUE"] = data["OBS_VALUE"].astype("Int64")
    schema = Schema(
        context="datastructure",
        agency="Short",
        id="Urn",
        version="1.0",
        components=Components(
            [
                Component(
                    id="DIM1",
                    role=Role.DIMENSION,
                    concept=Concept(id="DIM1"),
                    required=True,
                ),
                Component(
                    id="OBS_VALUE",
                    role=Role.MEASURE,
                    concept=Concept(id="OBS_VALUE"),
                    required=True,
                    local_dtype=DataType.INTEGER,
                ),
            ]
        ),
    )
    dataset = PandasDataset(data=data, structure=schema)
    result = write_str_spec([dataset])
    datasets = get_datasets(result)
    assert len(datasets) == 1
    data = datasets[0].data
    assert data["OBS_VALUE"].values.tolist() == ["", "1", "", ""]


def test_data_write_csv_sentinel_values():
    """CSV sentinels: optional attrs omitted, required get sentinel."""
    from pysdmx.io.writer import write_sdmx

    data = pd.DataFrame(
        data={
            "DIM1": ["A", "B"],
            "OBS_VALUE": ["#N/A", "42"],
            "ATTR1": ["NaN", "hello"],
        }
    )
    schema = Schema(
        context="datastructure",
        agency="TEST",
        id="TEST_DS",
        version="1.0",
        components=Components(
            [
                Component(
                    id="DIM1",
                    role=Role.DIMENSION,
                    concept=Concept(id="DIM1"),
                    required=True,
                ),
                Component(
                    id="OBS_VALUE",
                    role=Role.MEASURE,
                    concept=Concept(id="OBS_VALUE"),
                    required=True,
                ),
                Component(
                    id="ATTR1",
                    role=Role.ATTRIBUTE,
                    concept=Concept(id="ATTR1"),
                    required=False,
                    attachment_level="O",
                ),
            ]
        ),
    )
    from pysdmx.io.format import Format

    dataset = PandasDataset(data=data, structure=schema)
    result = write_sdmx([dataset], sdmx_format=Format.DATA_SDMX_ML_3_0)
    # Sentinel values from CSV are cleaned out
    assert "#N/A" not in result
    assert 'ATTR1="NaN"' not in result
    # Valid values are preserved
    assert 'OBS_VALUE="42"' in result
    assert 'ATTR1="hello"' in result
