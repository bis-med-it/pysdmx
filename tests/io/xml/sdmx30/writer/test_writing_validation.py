from pathlib import Path

import pytest

from pysdmx.io import read_sdmx
from pysdmx.io.xml.sdmx30.writer.structure import write


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
