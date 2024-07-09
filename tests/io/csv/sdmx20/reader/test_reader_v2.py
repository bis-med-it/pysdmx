from pathlib import Path

from pysdmx.io.csv.sdmx20.reader import read
from pytest import fixture


@fixture
def data_path():
    base_path = Path(__file__).parent / 'samples' / 'data_v2.csv'
    return base_path


def test_reading_data_v2(data_path):
    reading = read(data_path)
    return reading
