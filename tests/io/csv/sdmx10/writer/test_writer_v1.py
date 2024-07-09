from pathlib import Path

import pandas as pd

from pysdmx.io.csv.sdmx10.reader import read
from pysdmx.io.csv.sdmx10.writer import writer
from pytest import fixture


from pysdmx.model.dataset import Dataset


@fixture
def data_path():
    base_path = Path(__file__).parent / 'samples' / 'df.json'
    return str(base_path)


def test_to_sdmx_csv_writing(data_path):
    dataset = Dataset(attached_attributes={}, data=pd.read_json(data_path, orient='records'),
                      unique_id='MD:DS1(1.0)', structure_type='dataflow')
    dataset.data = dataset.data.astype('str')
    result_sdmx_csv = writer(dataset)
    dataset_read = read(result_sdmx_csv)
    dataset_sdmx_csv = dataset_read['MD:DS1(1.0)']
    pd.testing.assert_frame_equal(
        dataset_sdmx_csv.data.fillna('').replace('nan', ''),
        dataset.data.replace('nan', ''),
        check_like=True)
