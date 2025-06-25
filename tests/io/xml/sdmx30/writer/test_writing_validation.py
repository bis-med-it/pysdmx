from pathlib import Path

import pytest

from pysdmx.io import read_sdmx
from pysdmx.io.xml.sdmx30.writer.structure import write
from pysdmx.model import DataStructureDefinition

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
