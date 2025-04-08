import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

import pysdmx.io.xml.sdmx21.writer.config
from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.sdmx21.writer.generic import write as write_gen
from pysdmx.io.xml.sdmx21.writer.structure_specific import (
    write as write_str_spec,
)
from pysdmx.model import (
    Code,
    Codelist,
    Component,
    Components,
    Concept,
    Organisation,
    Role,
    Schema,
)
from pysdmx.model.dataset import ActionType
from pysdmx.model.message import Header


@pytest.fixture
def header():
    return Header(
        id="ID",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        sender=Organisation(
            id="SENDER",
        ),
        receiver=Organisation(
            id="RECEIVER",
        ),
        source="PySDMX",
    )


@pytest.fixture
def content():
    ds = PandasDataset(
        data=pd.DataFrame(
            {
                "DIM1": [1, 2, 3],
                "DIM2": [4, 5, 6],
                "ATT1": ["A", "B", "C"],
                "ATT2": [7, 8, 9],
                "M1": [10, 11, 12],
            }
        ),
        structure=Schema(
            context="datastructure",
            id="TEST",
            agency="MD",
            version="1.0",
            components=Components(
                [
                    Component(
                        id="DIM1",
                        role=Role.DIMENSION,
                        concept=Concept(id="DIM1"),
                        required=True,
                    ),
                    Component(
                        id="DIM2",
                        role=Role.DIMENSION,
                        concept=Concept(id="DIM2"),
                        required=True,
                    ),
                    Component(
                        id="ATT1",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT1"),
                        required=True,
                        attachment_level="DIM1",
                    ),
                    Component(
                        id="ATT2",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT2"),
                        required=False,
                        attachment_level="O",
                    ),
                    Component(
                        id="ds_att1",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ds_att1"),
                        required=True,
                    ),
                    Component(
                        id="ds_att2",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ds_att2"),
                        required=False,
                    ),
                    Component(
                        id="M1",
                        role=Role.MEASURE,
                        concept=Concept(id="M1"),
                        required=True,
                    ),
                ]
            ),
        ),
        attributes={"ds_att1": "value1", "ds_att2": 10},
    )
    return {ds.structure.short_urn: ds}


@pytest.mark.parametrize(
    ("message_type", "filename", "dimension_at_observation"),
    [
        (Format.DATA_SDMX_ML_2_1_GEN, "gen_all.xml", {}),
        (Format.DATA_SDMX_ML_2_1_STR, "str_all.xml", None),
        (
            Format.DATA_SDMX_ML_2_1_STR,
            "str_ser.xml",
            {"DataStructure=MD:TEST(1.0)": "DIM1"},
        ),
        (
            Format.DATA_SDMX_ML_2_1_GEN,
            "gen_ser.xml",
            {"DataStructure=MD:TEST(1.0)": "DIM1"},
        ),
    ],
)
def test_data_write_read(
    header, content, message_type, filename, dimension_at_observation
):
    samples_folder_path = Path(__file__).parent / "samples"
    # Write from Dataset
    write = (
        write_str_spec
        if message_type == Format.DATA_SDMX_ML_2_1_STR
        else write_gen
    )
    result = write(
        list(content.values()),
        header=header,
        dimension_at_observation=dimension_at_observation,
    )
    # Read the result to check for formal errors
    result_data = read_sdmx(result, validate=True).data
    assert result_data is not None
    assert len(result_data) == 1
    dataset = result_data[0]
    assert dataset.short_urn == "DataStructure=MD:TEST(1.0)"
    # Read the reference to compare with the result
    infile, _ = process_string_to_read(samples_folder_path / filename)
    reference_msg = read_sdmx(infile, validate=True)
    result_data = dataset.data
    reference_data = reference_msg.get_dataset(
        "DataStructure=MD:TEST(1.0)"
    ).data

    assert result_data.shape == (3, 5)

    pd.testing.assert_frame_equal(
        result_data.fillna("").replace("nan", ""),
        reference_data.replace("nan", ""),
        check_like=True,
    )


@pytest.mark.parametrize(
    ("message_type", "filename", "dimension_at_observation"),
    [
        (Format.DATA_SDMX_ML_2_1_GEN, "gen_all.xml", {}),
        (Format.DATA_SDMX_ML_2_1_STR, "str_all.xml", None),
    ],
)
def test_write_data_file(
    header, content, message_type, filename, dimension_at_observation
):
    output_file = Path(__file__).parent / "test_output_data.xml"
    # Write from Dataset
    write = (
        write_str_spec
        if message_type == Format.DATA_SDMX_ML_2_1_STR
        else write_gen
    )
    write(
        list(content.values()),
        output_path=output_file,
        dimension_at_observation=dimension_at_observation,
    )

    assert output_file.exists()
    os.remove(output_file)


@pytest.mark.parametrize(
    ("message_type", "dimension_at_observation"),
    [
        (Format.DATA_SDMX_ML_2_1_GEN, {}),
        (Format.DATA_SDMX_ML_2_1_STR, None),
        (
            Format.DATA_SDMX_ML_2_1_GEN,
            {"DataStructure=MD:TEST(1.0)": "DIM1"},
        ),
        (
            Format.DATA_SDMX_ML_2_1_STR,
            {"DataStructure=MD:TEST(1.0)": "DIM1"},
        ),
    ],
)
def test_data_write_df(
    header, content, message_type, dimension_at_observation
):
    pysdmx.io.xml.sdmx21.writer.structure_specific.CHUNKSIZE = 20
    pysdmx.io.xml.sdmx21.writer.generic.CHUNKSIZE = 20
    # Write from DataFrame
    df = pd.DataFrame(
        {
            "DIM1": [1, 2, 3, 4, 5] * 10,
            "DIM2": [6, 7, 8, 9, 10] * 10,
            "M1": [10, 11, None, 13, 14] * 10,
        }
    )
    ds: PandasDataset = content["DataStructure=MD:TEST(1.0)"]
    ds.structure.components.remove(ds.structure.components["ATT1"])
    ds.structure.components.remove(ds.structure.components["ATT2"])
    ds.data = df
    ds.attributes = {}
    content = [ds]

    write = (
        write_str_spec
        if message_type == Format.DATA_SDMX_ML_2_1_STR
        else write_gen
    )
    result = write(
        content,
        header=header,
        dimension_at_observation=dimension_at_observation,
    )
    # Read the result to check for formal errors
    result_msg = read_sdmx(result, validate=True).data
    assert result_msg is not None
    assert len(result_msg) == 1
    dataset = result_msg[0]
    assert dataset.short_urn == "DataStructure=MD:TEST(1.0)"
    result_data = dataset.data

    assert result_data.shape == (50, 3)


def test_invalid_content():
    content = {
        "Codelist=MD:TEST(1.0)": Codelist(
            id="ID",
            agency="MD",
            version="1.0",
            items=[Code(id="1", name="Name")],
        )
    }
    with pytest.raises(
        Invalid, match="Message Content must only contain a Dataset sequence."
    ):
        write_str_spec(content)

    with pytest.raises(
        Invalid, match="Message Content must only contain a Dataset sequence."
    ):
        write_gen(content)


def test_invalid_dimension(content):
    dim_mapping = {"DataStructure=MD:TEST(1.0)": "DIM3"}
    content = list(content.values())
    with pytest.raises(Invalid):
        write_str_spec(
            content,
            dimension_at_observation=dim_mapping,
        )


def test_invalid_dimension_key(content):
    dim_mapping = {"DataStructure=AAA:TEST(1.0)": "DIM1"}
    content = list(content.values())
    with pytest.raises(Invalid):
        write_str_spec(
            content,
            dimension_at_observation=dim_mapping,
        )


def test_data_writing_escape(content):
    content = list(content.values())
    content[0].data["ATT1"] = ["<A", ">B", "&C"]
    result_spe = write_str_spec(content)
    assert "&lt;A" in result_spe
    assert "&gt;B" in result_spe
    assert "&amp;C" in result_spe
    result_gen = write_gen(content)
    assert "&lt;A" in result_spe
    assert "&gt;B" in result_spe
    assert "&amp;C" in result_spe

    # Read the result to check for formal errors
    data_spe = read_sdmx(result_spe, validate=True).data[0]
    data_gen = read_sdmx(result_gen, validate=True).data[0]

    assert data_spe.data["ATT1"].tolist() == ["<A", ">B", "&C"]
    assert data_gen.data["ATT1"].tolist() == ["<A", ">B", "&C"]


def test_write_empty_data(header, content):
    content = list(content.values())
    content[0].data = pd.DataFrame(columns=content[0].data.columns)
    content[0].attributes = {}
    result_spe = write_str_spec(
        content,
        header=header,
        prettyprint=True,
    )
    result_gen = write_gen(
        content,
        header=header,
        prettyprint=True,
    )

    # Check the source is present and there are references to the structure
    assert "Source" in result_spe
    assert "Source" in result_gen

    reference = (
        '<Ref agencyID="MD" id="TEST" version="1.0" class="DataStructure"/>'
    )
    assert reference in result_spe
    assert reference in result_gen
    # Checks validation against XSD
    msg_spe = read_sdmx(result_spe, validate=True)
    msg_gen = read_sdmx(result_gen, validate=True)

    assert msg_spe.data[0].data.empty
    assert msg_gen.data[0].data.empty


def test_optional_data_attributes(content):
    content = list(content.values())
    # Removing optional attribute ATT2 only from data
    content[0].data = content[0].data.drop(columns=["ATT2"])

    assert "ATT2" in [c.id for c in content[0].structure.components]
    assert not content[0].structure.components["ATT2"].required

    # Writing with ATT2 removed to check issue #209
    result_spe = write_str_spec(
        content,
        dimension_at_observation={content[0].structure.short_urn: "DIM1"},
    )
    result_spe_all = write_str_spec(content)
    result_gen = write_gen(content)

    # Reading the output to check the shape
    msg_spe = read_sdmx(result_spe, validate=True)
    msg_gen = read_sdmx(result_gen, validate=True)
    msg_spe_all = read_sdmx(result_spe_all, validate=True)
    data_spe = msg_spe.get_dataset(content[0].structure.short_urn).data
    data_gen = msg_gen.get_dataset(content[0].structure.short_urn).data
    data_spe_all = msg_spe_all.get_dataset(content[0].structure.short_urn).data

    assert data_spe.shape == (3, 4)
    assert data_gen.shape == (3, 4)
    assert data_spe_all.shape == (3, 4)


def test_dataset_action_and_header_action_dataset_id(content, header):
    content = list(content.values())
    content[0].action = ActionType.Append

    header.dataset_action = ActionType.Replace
    header.dataset_id = "TEST_ID"

    result_spe = write_str_spec(content, header=header)
    result_gen = write_gen(content, header=header)

    assert "DataSetAction>Replace</" in result_spe
    assert "DataSetAction>Replace</" in result_gen
    assert "DataSetID>TEST_ID</" in result_spe
    assert "DataSetID>TEST_ID</" in result_gen

    # Read the result to check for formal errors
    data_spe = read_sdmx(result_spe, validate=True)
    data_gen = read_sdmx(result_gen, validate=True)
    assert data_spe.data[0].action == ActionType.Append
    assert data_gen.data[0].action == ActionType.Append
