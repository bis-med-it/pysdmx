from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx
from pysdmx.io.csv.sdmx20.writer import write
from pysdmx.io.pd import PandasDataset
from pysdmx.model.concept import Concept
from pysdmx.model.dataflow import Component, Components, Role, Schema
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
def partial_keys_data():
    return pd.DataFrame(
        [
            {
                "DIM1": "A",
                "DIM2": "B",
                "ATT1": "C",
                "ATT2": "D",
                "OBS_VALUE": 1,
                "TIME_PERIOD": "2020",
            },
            {
                "DIM1": "A",
                "DIM2": "B",
                "ATT1": "C",
                "ATT2": "E",
                "OBS_VALUE": 2,
                "TIME_PERIOD": "2021",
            },
        ]
    )


@pytest.fixture
def partial_keys_schema(dsd_path):
    dsd = read_sdmx(dsd_path).get_data_structure_definitions()[0]
    return dsd.to_schema()


@pytest.fixture
def csv_partial_keys():
    base_path = Path(__file__).parent / "samples" / "csv_partial_keys.csv"
    return str(base_path)


@pytest.mark.data
def test_to_sdmx_csv_writing(data_path, data_path_reference):
    urn = "urn:sdmx:org.sdmx.infomodel.registry.ProvisionAgreement=MD:PA1(1.0)"
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path, orient="records"),
        structure=urn,
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
def test_to_sdmx_csv_writing_to_file(data_path, data_path_reference, tmpdir):
    urn = "urn:sdmx:org.sdmx.infomodel.registry.ProvisionAgreement=MD:PA1(1.0)"
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


@pytest.mark.data
def test_writer_attached_attrs(data_path, data_path_reference_attch_atts):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure="DataStructure=MD:DS1(2.0)",
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
def test_writer_with_action(data_path, data_path_reference_action):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure="DataStructure=MD:DS1(2.0)",
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


def test_writer_labels_name(data_path_optional, dsd_path, csv_labels_name):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    schema = dsd.to_schema()
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


def test_writer_keys_obs(data_path_optional, dsd_path, csv_keys_obs):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    schema = dsd.to_schema()
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


def test_writer_keys_series(data_path_optional, dsd_path, csv_keys_series):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    schema = dsd.to_schema()
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


def test_writer_keys_both(data_path_optional, dsd_path, csv_keys_both):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    schema = dsd.to_schema()
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


def test_writer_partial_keys(
    partial_keys_data, partial_keys_schema, csv_partial_keys
):
    dataset = PandasDataset(
        attributes={},
        data=partial_keys_data,
        structure=partial_keys_schema,
    )
    dataset.data = dataset.data.astype("str")
    result_sdmx_csv = write([dataset], partial_keys=True)
    result_df = pd.read_csv(StringIO(result_sdmx_csv)).astype(str)
    reference_df = pd.read_csv(csv_partial_keys).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
    )


def test_writer_partial_keys_all_obs_attrs(dsd_path):
    """When all attributes are obs-level, partial_keys has no effect."""

    def _comp(cid: str, role: Role, **kw: str) -> Component:
        return Component(
            id=cid,
            required=role != Role.ATTRIBUTE,
            role=role,
            concept=Concept(id=cid),
            **kw,
        )

    comps = Components(
        [
            _comp("DIM1", Role.DIMENSION),
            _comp("DIM2", Role.DIMENSION),
            _comp("OBS_VALUE", Role.MEASURE),
            _comp("ATT1", Role.ATTRIBUTE, attachment_level="O"),
            _comp("ATT2", Role.ATTRIBUTE, attachment_level="O"),
            _comp("ATT3", Role.ATTRIBUTE, attachment_level="DIM1"),
        ]
    )
    schema = Schema(
        context="datastructure",
        agency="MD",
        id="MD_TEST",
        components=comps,
    )
    data = pd.DataFrame(
        [
            {
                "DIM1": "A",
                "DIM2": "B",
                "ATT1": "C",
                "ATT2": "D",
                "OBS_VALUE": 1,
            }
        ]
    )
    dataset = PandasDataset(
        attributes={}, data=data.astype("str"), structure=schema
    )
    result_with = write([dataset], partial_keys=True)
    result_without = write([dataset], partial_keys=False)
    assert result_with == result_without


def test_writer_partial_keys_empty_attr(partial_keys_schema):
    """Partial key rows with empty attribute values are skipped."""
    data = pd.DataFrame(
        [
            {
                "DIM1": "A",
                "DIM2": "B",
                "ATT1": "",
                "ATT2": "D",
                "OBS_VALUE": 1,
                "TIME_PERIOD": "2020",
            }
        ]
    )
    dataset = PandasDataset(
        attributes={}, data=data.astype("str"), structure=partial_keys_schema
    )
    result_csv = write([dataset], partial_keys=True)
    result_df = pd.read_csv(StringIO(result_csv))
    assert len(result_df) == 1


@pytest.mark.data
def test_writer_partial_keys_no_schema(partial_keys_data):
    dataset = PandasDataset(
        attributes={},
        data=partial_keys_data,
        structure="DataStructure=MD:DS1(2.0)",
    )
    dataset.data = dataset.data.astype("str")
    with pytest.raises(Invalid, match="requires a Schema"):
        write([dataset], partial_keys=True)
