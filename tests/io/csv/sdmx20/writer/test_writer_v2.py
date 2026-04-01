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
def schema(dsd_path):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    return dsd.to_schema()


@pytest.fixture
def schema_manual():
    """Schema manually built without using read_sdmx for @pytest.mark.data."""
    from pysdmx.model import Component, Components, Concept, Role, Schema

    dim1_concept = Concept("DIM1", name="DIMENSION 1")
    dim2_concept = Concept("DIM2", name="DIMENSION 2")
    time_period_concept = Concept("TIME_PERIOD", name="TIME PERIOD")
    att1_concept = Concept("ATT1", name="ATTRIBUTE 1")
    att2_concept = Concept("ATT2", name="ATTRIBUTE 2")
    obs_value_concept = Concept("OBS_VALUE", name="OBS_VALUE")

    components = Components(
        [
            Component(
                "DIM1",
                required=True,
                role=Role.DIMENSION,
                concept=dim1_concept,
            ),
            Component(
                "DIM2",
                required=True,
                role=Role.DIMENSION,
                concept=dim2_concept,
            ),
            Component(
                "TIME_PERIOD",
                required=True,
                role=Role.DIMENSION,
                concept=time_period_concept,
            ),
            Component(
                "ATT1",
                required=False,
                role=Role.ATTRIBUTE,
                concept=att1_concept,
                attachment_level="DIM1,DIM2",
            ),
            Component(
                "ATT2",
                required=False,
                role=Role.ATTRIBUTE,
                concept=att2_concept,
                attachment_level="OBS_VALUE",
            ),
            Component(
                "OBS_VALUE",
                required=True,
                role=Role.MEASURE,
                concept=obs_value_concept,
            ),
        ]
    )

    return Schema(
        context="datastructure",
        agency="MD",
        id="MD_TEST",
        version="1.0",
        components=components,
        name="MD TEST",
    )


@pytest.fixture
def schema_provision_agreement(schema_manual):
    from pysdmx.model import Schema

    return Schema(
        context="provisionagreement",
        agency=schema_manual.agency,
        id=schema_manual.id,
        version=schema_manual.version,
        components=schema_manual.components,
        name=schema_manual.name,
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
def data_path_reference_partial_keys():
    base_path = (
        Path(__file__).parent / "samples" / "reference_partial_keys.csv"
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
    data_path, data_path_reference_attch_atts, schema_manual
):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure=schema_manual,
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
    data_path, data_path_reference_action, schema_manual
):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure=schema_manual,
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


def test_writer_partial_keys(
    partial_keys_data, partial_keys_schema, data_path_reference_partial_keys
):
    dataset = PandasDataset(
        attributes={},
        data=partial_keys_data,
        structure=partial_keys_schema,
    )
    dataset.data = dataset.data.astype("str")
    result_sdmx_csv = write([dataset], partial_keys=True)
    result_df = pd.read_csv(StringIO(result_sdmx_csv)).astype(str)
    reference_df = pd.read_csv(data_path_reference_partial_keys).astype(str)
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
    df_with = pd.read_csv(StringIO(result_with))
    df_without = pd.read_csv(StringIO(result_without))
    pd.testing.assert_frame_equal(df_with, df_without, check_like=True)


def test_writer_partial_keys_empty_attr(partial_keys_schema):
    """Partial key rows with null-like attribute values are skipped."""
    import numpy as np

    data = pd.DataFrame(
        [
            {
                "DIM1": "A",
                "DIM2": "B",
                "ATT1": np.nan,
                "ATT2": "D",
                "OBS_VALUE": "1",
                "TIME_PERIOD": "2020",
            },
            {
                "DIM1": "A",
                "DIM2": "D",
                "ATT1": "X",
                "ATT2": "F",
                "OBS_VALUE": "3",
                "TIME_PERIOD": "2022",
            },
        ]
    )
    dataset = PandasDataset(
        attributes={},
        data=data,
        structure=partial_keys_schema,
    )
    result_csv = write([dataset], partial_keys=True)
    result_df = pd.read_csv(
        StringIO(result_csv), keep_default_na=False, na_values=[]
    )
    # 2 obs rows + 1 partial key for ATT1=X (NaN skipped)
    assert len(result_df) == 3


@pytest.mark.data
def test_writer_partial_keys_no_schema(partial_keys_data):
    dataset = PandasDataset(
        attributes={},
        data=partial_keys_data,
        structure="DataStructure=MD:DS1(2.0)",
    )
    dataset.data = dataset.data.astype("str")
    with pytest.raises(Invalid, match="not a Schema"):
        write([dataset], partial_keys=True)
