from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io.csv.sdmx20.reader import read


@pytest.fixture()
def data_path():
    base_path = Path(__file__).parent / "samples" / "data_v2.csv"
    return str(base_path)


def test_reading_data_v2(data_path):
    with open(data_path, 'r') as content:
        data = str(pd.read_csv(content))
    reading = read(data)
    return reading
