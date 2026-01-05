from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io import read_sdmx
from pysdmx.io.csv.sdmx21.writer import write
from pysdmx.io.pd import PandasDataset
from pysdmx.model.dataset import ActionType


@pytest.fixture
def data_path():
    base_path = Path(__file__).parent / "samples" / "df.json"
    return str(base_path)


@pytest.fixture
def schema(dsd_path):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    return dsd.to_schema()


@pytest.fixture
def schema_provision_agreement(schema):
    from pysdmx.model import Schema

    return Schema(
        context="provisionagreement",
        agency=schema.agency,
        id=schema.id,
        version=schema.version,
        components=schema.components,
        name=schema.name,
    )


@pytest.fixture
def data_path_optional():
    base_path = Path(__file__).parent / "samples" / "df_optional.json"
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


@pytest.fixture
def data_path_reference_append_action():
    base_path = (
        Path(__file__).parent / "samples" / "reference_with_append_action.csv"
    )
    return base_path


@pytest.fixture
def dsd_path():
    base_path = Path(__file__).parent / "samples" / "datastructure.xml"
    return str(base_path)


@pytest.fixture
def csv_labels_id():
    base_path = Path(__file__).parent / "samples" / "csv_labels_id.csv"
    return str(base_path)


@pytest.fixture
def csv_labels_name():
    base_path = Path(__file__).parent / "samples" / "csv_labels_name.csv"
    return str(base_path)


@pytest.fixture
def csv_labels_both():
    base_path = Path(__file__).parent / "samples" / "csv_labels_both.csv"
    return str(base_path)


@pytest.fixture
def csv_keys_obs():
    base_path = Path(__file__).parent / "samples" / "csv_keys_obs.csv"
    return str(base_path)


@pytest.fixture
def csv_keys_series():
    base_path = Path(__file__).parent / "samples" / "csv_keys_series.csv"
    return str(base_path)


@pytest.fixture
def csv_keys_both():
    base_path = Path(__file__).parent / "samples" / "csv_keys_both.csv"
    return str(base_path)


@pytest.fixture
def csv_time_format_original():
    base_path = (
        Path(__file__).parent / "samples" / "csv_time_format_original.csv"
    )
    return str(base_path)


@pytest.mark.data
def test_to_sdmx_csv_writing(
    data_path, data_path_reference, schema_provision_agreement
):
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path, orient="records"),
        structure=schema_provision_agreement,
    )
    dataset.data = dataset.data.astype("str")
    result_sdmx = write([dataset])
    result_df = pd.read_csv(StringIO(result_sdmx)).astype(str)
    reference_df = pd.read_csv(data_path_reference).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


@pytest.mark.data
def test_to_sdmx_csv_writing_to_file(
    data_path, data_path_reference, schema_provision_agreement, tmpdir
):
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path, orient="records"),
        structure=schema_provision_agreement,
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


@pytest.mark.data
def test_writer_attached_attrs(
    data_path, data_path_reference_attch_atts, schema
):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure=schema,
    )
    dataset.data = dataset.data.astype(str)
    result_sdmx = write([dataset])
    result_df = pd.read_csv(StringIO(result_sdmx)).astype(str)
    reference_df = pd.read_csv(data_path_reference_attch_atts).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


@pytest.mark.data
def test_writer_with_action(data_path, data_path_reference_action, schema):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure=schema,
        action=ActionType.Replace,
    )
    dataset.data = dataset.data.astype(str)
    result_sdmx = write([dataset])
    result_df = pd.read_csv(StringIO(result_sdmx)).astype(str)
    reference_df = pd.read_csv(data_path_reference_action).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


@pytest.mark.data
def test_writer_with_append_action(
    data_path, data_path_reference_append_action, schema
):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure=schema,
        action=ActionType.Append,
    )
    dataset.data = dataset.data.astype(str)
    result_sdmx = write([dataset])
    result_df = pd.read_csv(StringIO(result_sdmx)).astype(str)
    reference_df = pd.read_csv(data_path_reference_append_action).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_writer_labels_id(data_path_optional, schema, csv_labels_id):
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


def test_writer_labels_name(data_path_optional, schema, csv_labels_name):
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path_optional, orient="records"),
        structure=schema,
    )
    dataset.data = dataset.data.astype("str")
    result_sdmx_csv = write([dataset], labels="name")
    result_df = pd.read_csv(StringIO(result_sdmx_csv)).astype(str)
    reference_df = pd.read_csv(csv_labels_name).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_writer_labels_both(data_path_optional, schema, csv_labels_both):
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


def test_writer_keys_obs(data_path_optional, schema, csv_keys_obs):
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path_optional, orient="records"),
        structure=schema,
    )
    dataset.data = dataset.data.astype("str")
    result_sdmx_csv = write([dataset], keys="obs")
    result_df = pd.read_csv(StringIO(result_sdmx_csv)).astype(str)
    reference_df = pd.read_csv(csv_keys_obs).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_writer_keys_series(data_path_optional, schema, csv_keys_series):
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path_optional, orient="records"),
        structure=schema,
    )
    dataset.data = dataset.data.astype("str")
    result_sdmx_csv = write([dataset], keys="series")
    result_df = pd.read_csv(StringIO(result_sdmx_csv)).astype(str)
    reference_df = pd.read_csv(csv_keys_series).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_writer_keys_both(data_path_optional, schema, csv_keys_both):
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path_optional, orient="records"),
        structure=schema,
    )
    dataset.data = dataset.data.astype("str")
    result_sdmx_csv = write([dataset], keys="both")
    result_df = pd.read_csv(StringIO(result_sdmx_csv)).astype(str)
    reference_df = pd.read_csv(csv_keys_both).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_writer_time_format_original(
    data_path_optional, schema, csv_time_format_original
):
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


def test_writer_time_format_normalized(data_path_optional, schema):
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
