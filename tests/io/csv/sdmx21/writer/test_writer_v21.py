from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io.csv.sdmx21.writer import write
from pysdmx.io.pd import PandasDataset
from pysdmx.model import Component, Components, Concept, DataType, Role, Schema
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
def data_path_reference_append_action():
    base_path = (
        Path(__file__).parent / "samples" / "reference_with_append_action.csv"
    )
    return base_path


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


@pytest.fixture
def schema():
    return Schema(
        context="datastructure",
        agency="MD",
        id="MD_TEST",
        version="1.0",
        name="MD TEST",
        components=Components(
            [
                Component(
                    id="DIM1",
                    concept=Concept(
                        id="DIM1", name="DIMENSION 1", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DIM2",
                    concept=Concept(
                        id="DIM2", name="DIMENSION 2", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="TIME_PERIOD",
                    concept=Concept(
                        id="TIME_PERIOD",
                        name="TIME PERIOD",
                        dtype=DataType.TIME,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="ATT1",
                    concept=Concept(
                        id="ATT1", name="ATTRIBUTE 1", dtype=DataType.STRING
                    ),
                    role=Role.ATTRIBUTE,
                    required=False,
                    attachment_level="S",
                ),
                Component(
                    id="ATT2",
                    concept=Concept(
                        id="ATT2", name="ATTRIBUTE 2", dtype=DataType.STRING
                    ),
                    role=Role.ATTRIBUTE,
                    required=False,
                    attachment_level="O",
                ),
                Component(
                    id="OBS_VALUE",
                    concept=Concept(
                        id="OBS_VALUE", name="OBS_VALUE", dtype=DataType.STRING
                    ),
                    role=Role.MEASURE,
                    required=False,
                ),
            ]
        ),
    )


@pytest.fixture
def schema_provision_agreement():
    return Schema(
        context="provisionagreement",
        agency="MD",
        id="PA1",
        version="1.0",
        name="MD TEST",
        components=Components(
            [
                Component(
                    id="FREQ",
                    concept=Concept(
                        id="FREQ", name="FREQ", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_TYPE",
                    concept=Concept(
                        id="DER_TYPE", name="DER_TYPE", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_INSTR",
                    concept=Concept(
                        id="DER_INSTR", name="DER_INSTR", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_RISK",
                    concept=Concept(
                        id="DER_RISK", name="DER_RISK", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_REP_CTY",
                    concept=Concept(
                        id="DER_REP_CTY",
                        name="DER_REP_CTY",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_SECTOR_CPY",
                    concept=Concept(
                        id="DER_SECTOR_CPY",
                        name="DER_SECTOR_CPY",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_CPC",
                    concept=Concept(
                        id="DER_CPC", name="DER_CPC", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_SECTOR_UDL",
                    concept=Concept(
                        id="DER_SECTOR_UDL",
                        name="DER_SECTOR_UDL",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_CURR_LEG1",
                    concept=Concept(
                        id="DER_CURR_LEG1",
                        name="DER_CURR_LEG1",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_CURR_LEG2",
                    concept=Concept(
                        id="DER_CURR_LEG2",
                        name="DER_CURR_LEG2",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_ISSUE_MAT",
                    concept=Concept(
                        id="DER_ISSUE_MAT",
                        name="DER_ISSUE_MAT",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_RATING",
                    concept=Concept(
                        id="DER_RATING",
                        name="DER_RATING",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_EX_METHOD",
                    concept=Concept(
                        id="DER_EX_METHOD",
                        name="DER_EX_METHOD",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_BASIS",
                    concept=Concept(
                        id="DER_BASIS", name="DER_BASIS", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="TIME_PERIOD",
                    concept=Concept(
                        id="TIME_PERIOD",
                        name="TIME PERIOD",
                        dtype=DataType.TIME,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="OBS_VALUE",
                    concept=Concept(
                        id="OBS_VALUE", name="OBS_VALUE", dtype=DataType.STRING
                    ),
                    role=Role.MEASURE,
                    required=False,
                ),
                Component(
                    id="AVAILABILITY",
                    concept=Concept(
                        id="AVAILABILITY",
                        name="AVAILABILITY",
                        dtype=DataType.STRING,
                    ),
                    role=Role.ATTRIBUTE,
                    required=False,
                    attachment_level="O",
                ),
                Component(
                    id="COLLECTION",
                    concept=Concept(
                        id="COLLECTION",
                        name="COLLECTION",
                        dtype=DataType.STRING,
                    ),
                    role=Role.ATTRIBUTE,
                    required=False,
                    attachment_level="O",
                ),
                Component(
                    id="OBS_STATUS",
                    concept=Concept(
                        id="OBS_STATUS",
                        name="OBS_STATUS",
                        dtype=DataType.STRING,
                    ),
                    role=Role.ATTRIBUTE,
                    required=False,
                    attachment_level="O",
                ),
                Component(
                    id="OBS_CONF",
                    concept=Concept(
                        id="OBS_CONF", name="OBS_CONF", dtype=DataType.STRING
                    ),
                    role=Role.ATTRIBUTE,
                    required=False,
                    attachment_level="O",
                ),
            ]
        ),
    )


@pytest.fixture
def schema_alter_ID():
    return Schema(
        context="datastructure",
        agency="MD",
        id="DS1",
        version="2.0",
        name="MD TEST",
        components=Components(
            [
                Component(
                    id="FREQ",
                    concept=Concept(
                        id="FREQ", name="FREQ", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_TYPE",
                    concept=Concept(
                        id="DER_TYPE", name="DER_TYPE", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_INSTR",
                    concept=Concept(
                        id="DER_INSTR", name="DER_INSTR", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_RISK",
                    concept=Concept(
                        id="DER_RISK", name="DER_RISK", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_REP_CTY",
                    concept=Concept(
                        id="DER_REP_CTY",
                        name="DER_REP_CTY",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_SECTOR_CPY",
                    concept=Concept(
                        id="DER_SECTOR_CPY",
                        name="DER_SECTOR_CPY",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_CPC",
                    concept=Concept(
                        id="DER_CPC", name="DER_CPC", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_SECTOR_UDL",
                    concept=Concept(
                        id="DER_SECTOR_UDL",
                        name="DER_SECTOR_UDL",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_CURR_LEG1",
                    concept=Concept(
                        id="DER_CURR_LEG1",
                        name="DER_CURR_LEG1",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_CURR_LEG2",
                    concept=Concept(
                        id="DER_CURR_LEG2",
                        name="DER_CURR_LEG2",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_ISSUE_MAT",
                    concept=Concept(
                        id="DER_ISSUE_MAT",
                        name="DER_ISSUE_MAT",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_RATING",
                    concept=Concept(
                        id="DER_RATING",
                        name="DER_RATING",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_EX_METHOD",
                    concept=Concept(
                        id="DER_EX_METHOD",
                        name="DER_EX_METHOD",
                        dtype=DataType.STRING,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="DER_BASIS",
                    concept=Concept(
                        id="DER_BASIS", name="DER_BASIS", dtype=DataType.STRING
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="TIME_PERIOD",
                    concept=Concept(
                        id="TIME_PERIOD",
                        name="TIME PERIOD",
                        dtype=DataType.TIME,
                    ),
                    role=Role.DIMENSION,
                    required=True,
                ),
                Component(
                    id="OBS_VALUE",
                    concept=Concept(
                        id="OBS_VALUE", name="OBS_VALUE", dtype=DataType.STRING
                    ),
                    role=Role.MEASURE,
                    required=False,
                ),
                Component(
                    id="AVAILABILITY",
                    concept=Concept(
                        id="AVAILABILITY",
                        name="AVAILABILITY",
                        dtype=DataType.STRING,
                    ),
                    role=Role.ATTRIBUTE,
                    required=False,
                    attachment_level="O",
                ),
                Component(
                    id="COLLECTION",
                    concept=Concept(
                        id="COLLECTION",
                        name="COLLECTION",
                        dtype=DataType.STRING,
                    ),
                    role=Role.ATTRIBUTE,
                    required=False,
                    attachment_level="O",
                ),
                Component(
                    id="OBS_STATUS",
                    concept=Concept(
                        id="OBS_STATUS",
                        name="OBS_STATUS",
                        dtype=DataType.STRING,
                    ),
                    role=Role.ATTRIBUTE,
                    required=False,
                    attachment_level="O",
                ),
                Component(
                    id="OBS_CONF",
                    concept=Concept(
                        id="OBS_CONF", name="OBS_CONF", dtype=DataType.STRING
                    ),
                    role=Role.ATTRIBUTE,
                    required=False,
                    attachment_level="O",
                ),
            ]
        ),
    )


@pytest.mark.data
def test_to_sdmx_csv_writing(
    schema_provision_agreement, data_path, data_path_reference
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
    schema_provision_agreement, data_path, data_path_reference, tmpdir
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
    schema_alter_ID, data_path, data_path_reference_attch_atts
):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure=schema_alter_ID,
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
    schema_alter_ID, data_path, data_path_reference_action
):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure=schema_alter_ID,
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
    schema_alter_ID, data_path, data_path_reference_append_action
):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure=schema_alter_ID,
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


def test_writer_time_format_original(
    data_path_optional, csv_time_format_original, schema
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
