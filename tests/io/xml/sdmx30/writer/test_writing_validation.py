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
    DataStructureDefinition,
    Schema,
    Components,
    Component,
    Concept,
    Role
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
    # Local import on numpy to avoid possible problems with C extensions
    # on windows when using pysdmx
    import numpy as np

    # Create dataframe with nan value
    data = pd.DataFrame(data={"A": [np.nan, 1, None, pd.NA],"DIM1": [1, 2, 3, 4]})
    data["A"] = data["A"].astype("Int64")  # Use nullable integer type
    structure_schema = Schema(
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
                    id="A",
                    role=Role.MEASURE,
                    concept=Concept(id="A"),
                    required=False,
                ),
            ]
        ),
    )

    # The backend is numpy_nullable by default,
    # this line should just make clear
    # that this is not pyarrow related
    data = data.convert_dtypes(dtype_backend="numpy_nullable")

    dataset = PandasDataset(data=data, structure=structure_schema)
    result = write_str_spec([dataset])
    datasets = get_datasets(result)
    assert len(datasets) == 1
    data = datasets[0].data
    assert data["A"].values.tolist() == ["#N/A", "1", "#N/A", "#N/A"]
