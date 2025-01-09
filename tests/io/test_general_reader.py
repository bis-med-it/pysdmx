from pathlib import Path

import pytest

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx
from pysdmx.io.enums import ReadFormat


@pytest.fixture
def empty_message():
    file_path = Path(__file__).parent / "samples" / "empty_message.xml"
    with open(file_path, "r") as f:
        text = f.read()
    return text


def test_read_sdmx_invalid_extension():
    with pytest.raises(Invalid, match="Cannot parse input as SDMX."):
        read_sdmx(",,,,")


def test_read_format_str():
    assert str(ReadFormat.SDMX_ML_2_1_STRUCTURE) == "SDMX-ML 2.1 Structure"
    assert str(ReadFormat.SDMX_ML_2_1_DATA_GENERIC) == "SDMX-ML 2.1 Generic"
    assert (
        str(ReadFormat.SDMX_ML_2_1_DATA_STRUCTURE_SPECIFIC)
        == "SDMX-ML 2.1 StructureSpecific"
    )
    assert str(ReadFormat.SDMX_CSV_1_0) == "SDMX-CSV 1.0"
    assert str(ReadFormat.SDMX_CSV_2_0) == "SDMX-CSV 2.0"


def test_empty_result(empty_message):
    with pytest.raises(Invalid, match="Empty SDMX Message"):
        read_sdmx(empty_message, validate=False)
