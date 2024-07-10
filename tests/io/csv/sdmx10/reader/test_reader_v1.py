from pathlib import Path

import pytest

from pysdmx.io.csv.sdmx10.reader import read


@pytest.fixture()
def data_path():
    return Path(__file__).parent / "samples" / "data_v1.csv"


def test_reading_data_v1(data_path):
    reading = read(data_path)
    return reading
