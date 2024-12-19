from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io.csv.sdmx20.writer import writer
from pysdmx.io.pd import PandasDataset
from pysdmx.model.message import ActionType


@pytest.fixture
def data_path():
    base_path = Path(__file__).parent / "samples" / "df.json"
    return str(base_path)


@pytest.fixture
def data_path_reference():
    base_path = Path(__file__).parent / "samples" / "reference.csv"
    return base_path


@pytest.fixture
def data_path_reference_attch_atts():
    base_path = Path(__file__).parent / "samples" / "reference_attch_atts.csv"
    return base_path


@pytest.fixture
def data_path_reference_action():
    base_path = Path(__file__).parent / "samples" / "reference_with_action.csv"
    return base_path


def test_to_sdmx_csv_writing(data_path, data_path_reference):
    urn = (
        "urn:sdmx:org.sdmx.infomodel.registry."
        "ProvisionAgreement=MD:PA1(1.0)"
    )
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path, orient="records"),
        structure=urn,
    )
    dataset.data = dataset.data.astype("str")
    result_sdmx = writer(dataset)
    result_df = pd.read_csv(StringIO(result_sdmx)).astype(str)
    reference_df = pd.read_csv(data_path_reference).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_writer_attached_attrs(data_path, data_path_reference_attch_atts):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure="urn:sdmx:org.sdmx.infomodel.datastructure."
        "DataStructure=MD:DS1(2.0)",
    )
    dataset.data = dataset.data.astype(str)
    result_sdmx = writer(dataset)
    result_df = pd.read_csv(StringIO(result_sdmx)).astype(str)
    reference_df = pd.read_csv(data_path_reference_attch_atts).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_writer_with_action(data_path, data_path_reference_action):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure="urn:sdmx:org.sdmx.infomodel.datastructure."
        "DataStructure=MD:DS1(2.0)",
        action=ActionType.Replace,
    )
    dataset.data = dataset.data.astype(str)
    result_sdmx = writer(dataset)
    result_df = pd.read_csv(StringIO(result_sdmx)).astype(str)
    reference_df = pd.read_csv(data_path_reference_action).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )
