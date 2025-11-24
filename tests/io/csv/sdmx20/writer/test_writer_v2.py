from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io.csv.sdmx20.writer import write
from pysdmx.io.pd import PandasDataset
from pysdmx.model import Schema
from pysdmx.model.dataset import ActionType


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
def dsd_path():
    base_path = Path(__file__).parent / "samples" / "datastructure.xml"
    return str(base_path)


@pytest.fixture
def dsd_path_alt_id_and_version():
    base_path = (
        Path(__file__).parent
        / "samples"
        / "datastructure_alt_id_and_version.xml"
    )
    return str(base_path)


@pytest.fixture
def dsd_path_provision_agreement():
    base_path = (
        Path(__file__).parent
        / "samples"
        / "datastructure_provision_agreement.xml"
    )
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
def schema(dsd_path):
    from pysdmx.io import read_sdmx

    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    return dsd.to_schema()


@pytest.fixture
def schema_alt_id_and_version(dsd_path_alt_id_and_version):
    from pysdmx.io import read_sdmx

    result = read_sdmx(
        dsd_path_alt_id_and_version
    ).get_data_structure_definitions()
    dsd = result[0]
    return dsd.to_schema()


@pytest.fixture
def schema_provision_agreement(dsd_path_provision_agreement):
    from pysdmx.io import read_sdmx

    result = read_sdmx(
        dsd_path_provision_agreement
    ).get_data_structure_definitions()
    dsd = result[0]

    base_schema = dsd.to_schema()

    # Build a Schema with provisionagreement context
    return Schema(
        context="provisionagreement",
        agency=base_schema.agency,
        id=base_schema.id,
        version=base_schema.version,
        components=base_schema.components,
        artefacts=base_schema.artefacts,
        generated=base_schema.generated,
        name=base_schema.name,
        groups=base_schema.groups,
    )


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
    data_path, data_path_reference, tmpdir, schema_provision_agreement
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
    data_path, data_path_reference_attch_atts, schema_alt_id_and_version
):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure=schema_alt_id_and_version,
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
def test_writer_with_action(
    data_path, data_path_reference_action, schema_alt_id_and_version
):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure=schema_alt_id_and_version,
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


def test_writer_labels_id(data_path_optional, csv_labels_id, schema):
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


def test_writer_labels_name(data_path_optional, csv_labels_name, schema):
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


def test_writer_labels_both(data_path_optional, csv_labels_both, schema):
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


def test_writer_keys_obs(data_path_optional, csv_keys_obs, schema):
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


def test_writer_keys_series(data_path_optional, csv_keys_series, schema):
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


def test_writer_keys_both(data_path_optional, csv_keys_both, schema):
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
