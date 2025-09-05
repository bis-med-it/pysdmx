from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io.csv.sdmx10.writer import write
from pysdmx.io.pd import PandasDataset
from pysdmx.io.reader import read_sdmx as read_sdmx


@pytest.fixture
def data_path():
    base_path = Path(__file__).parent / "samples" / "df.json"
    return str(base_path)


@pytest.fixture
def data_path_optional():
    base_path = Path(__file__).parent / "samples" / "df_optional.json"
    return str(base_path)


@pytest.fixture
def data_path_reference():
    base_path = Path(__file__).parent / "samples" / "reference.csv"
    return str(base_path)


@pytest.fixture
def data_path_reference_atch_atts():
    base_path = Path(__file__).parent / "samples" / "reference_attch_atts.csv"
    return str(base_path)


@pytest.fixture
def dsd_path():
    base_path = Path(__file__).parent / "samples" / "datastructure.xml"
    return str(base_path)


@pytest.fixture
def csv_labels_id():
    base_path = Path(__file__).parent / "samples" / "csv_labels_id.csv"
    return str(base_path)


@pytest.fixture
def csv_labels_both():
    base_path = Path(__file__).parent / "samples" / "csv_labels_both.csv"
    return str(base_path)


@pytest.fixture
def csv_time_format_original():
    base_path = (
        Path(__file__).parent / "samples" / "csv_time_format_original.csv"
    )
    return str(base_path)


def test_to_sdmx_csv_writing(data_path, data_path_reference):
    urn = "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=MD:DS1(1.0)"
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path, orient="records"),
        structure=urn,
    )
    dataset.data = dataset.data.astype("str")
    result_sdmx_csv = write([dataset])
    result_df = pd.read_csv(StringIO(result_sdmx_csv)).astype(str)
    reference_df = pd.read_csv(data_path_reference).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_to_sdmx_csv_writing_to_file(data_path, data_path_reference, tmpdir):
    urn = "urn:sdmx:org.sdmx.infomodel.datastructure.DataFlow=MD:DS1(1.0)"

    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path, orient="records"),
        structure=urn,
    )
    dataset.data = dataset.data.astype("str")
    write([dataset], output_path=tmpdir / "output.csv")
    result_df = pd.read_csv(tmpdir / "output.csv").astype(str)
    reference_df = pd.read_csv(data_path_reference).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_writer_attached_attrs(data_path, data_path_reference_atch_atts):
    urn = "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=MD:DS1(1.0)"
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure=urn,
    )
    dataset.data = dataset.data.astype("str")
    result_sdmx_csv = write([dataset])
    result_df = pd.read_csv(StringIO(result_sdmx_csv)).astype(str)
    reference_df = pd.read_csv(data_path_reference_atch_atts).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_writer_labels_id(data_path_optional, dsd_path, csv_labels_id):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    schema = dsd.to_schema()
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path_optional, orient="records"),
        structure=schema,
    )
    dataset.data = dataset.data.astype("str")
    result_sdmx_csv = write([dataset], labels="id")
    result_df = pd.read_csv(StringIO(result_sdmx_csv)).astype(str)
    reference_df = pd.read_csv(csv_labels_id).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_writer_labels_both(data_path_optional, dsd_path, csv_labels_both):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    schema = dsd.to_schema()
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path_optional, orient="records"),
        structure=schema,
    )
    dataset.data = dataset.data.astype("str")
    result_sdmx_csv = write([dataset], labels="both")
    result_df = pd.read_csv(StringIO(result_sdmx_csv)).astype(str)
    reference_df = pd.read_csv(csv_labels_both).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_writer_time_format_original(
    data_path_optional, dsd_path, csv_time_format_original
):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    schema = dsd.to_schema()
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path_optional, orient="records"),
        structure=schema,
    )
    dataset.data = dataset.data.astype("str")
    result_sdmx_csv = write([dataset], time_format="original")
    result_df = pd.read_csv(StringIO(result_sdmx_csv)).astype(str)
    reference_df = pd.read_csv(csv_time_format_original).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_writer_time_format_normalized(data_path_optional, dsd_path):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    schema = dsd.to_schema()
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path_optional, orient="records"),
        structure=schema,
    )
    dataset.data = dataset.data.astype("str")
    with pytest.raises(
        NotImplementedError,
        match="Normalized time format is not implemented yet.",
    ):
        write([dataset], time_format="normalized")
