from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io.csv.sdmx10.writer import write
from pysdmx.io.pd import PandasDataset
from pysdmx.io.reader import read_sdmx


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
def schema(dsd_path):
    """Load the Schema from the datastructure file."""
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    return result[0].to_schema()


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


@pytest.mark.data
def test_to_sdmx_csv_writing(data_path, data_path_reference, schema_manual):
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path, orient="records"),
        structure=schema_manual,
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


@pytest.mark.data
def test_to_sdmx_csv_writing_to_file(
    data_path, data_path_reference, schema_manual, tmpdir
):
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path, orient="records"),
        structure=schema_manual,
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
    data_path, data_path_reference_atch_atts, schema_manual
):
    dataset = PandasDataset(
        attributes={"DECIMALS": 3},
        data=pd.read_json(data_path, orient="records"),
        structure=schema_manual,
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
