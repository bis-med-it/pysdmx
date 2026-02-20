import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

import pysdmx.io.xml.config
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
from pysdmx.model.dataflow import Group
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
                        attachment_level="D",
                    ),
                    Component(
                        id="ds_att2",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ds_att2"),
                        required=False,
                        attachment_level="D",
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


@pytest.fixture
def ds_with_group():
    ds = PandasDataset(
        data=pd.DataFrame(
            {
                "DIM1": [1, 2, 3],
                "DIM2": [4, 5, 6],
                "ATT1": ["A", "B", "C"],
                "ATT2": [7, 8, 9],
                "ATT3": ["H", "I", "J"],
                "M1": [10, 11, 12],
            }
        ),
        structure=Schema(
            context="datastructure",
            id="TEST",
            agency="MD",
            version="1.0",
            groups=[Group(id="Group", dimensions=["DIM2"])],
            components=Components(
                [
                    Component(
                        id="DIM1",
                        role=Role.DIMENSION,
                        concept=Concept(id="DIM1"),
                        required=True,
                        attachment_level=None,
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
                        id="ATT3",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT3"),
                        required=True,
                        attachment_level="DIM2",
                    ),
                    Component(
                        id="ds_att1",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ds_att1"),
                        required=True,
                        attachment_level="D",
                    ),
                    Component(
                        id="ds_att2",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ds_att2"),
                        required=False,
                        attachment_level="D",
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
        attributes={"ds_att1": "value1", "ds_att2": "10"},
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
        (
            Format.DATA_SDMX_ML_2_1_STR,
            "str_all.xml",
            {"DataStructure=MD:TEST(1.0)": "AllDimensions"},
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


def test_write_structure_specific_with_groups(header, ds_with_group):
    base_path = (
        Path(__file__).parent
        / "samples"
        / "test_structure_specific_with_groups.xml"
    )
    with open(base_path, "r") as f:
        sample = f.read()

    ds_with_group = list(ds_with_group.values())
    result = write_str_spec(
        ds_with_group,
        header=header,
        prettyprint=True,
        dimension_at_observation={"DataStructure=MD:TEST(1.0)": "DIM1"},
    )

    assert result == sample


def test_write_generic_with_groups(header, ds_with_group):
    base_path = (
        Path(__file__).parent / "samples" / "test_generic_with_groups.xml"
    )
    with open(base_path, "r") as f:
        sample = f.read()
    ds_with_group = list(ds_with_group.values())
    result = write_gen(
        ds_with_group,
        header=header,
        prettyprint=True,
        dimension_at_observation={"DataStructure=MD:TEST(1.0)": "DIM1"},
    )

    assert result == sample


def test_data_scape_quote(content):
    # Create dataframe with quotation mark in string
    data = pd.DataFrame({"A": 'quote="'}, index=pd.DatetimeIndex(["2000-1-1"]))
    dataset: PandasDataset = content["DataStructure=MD:TEST(1.0)"]
    dataset.data = data

    result = write_str_spec([dataset])
    assert result is not None
    assert 'A="quote=&quot;"' in result


def test_generic_writer_varying_attributes(header, content):
    dataset = list(content.values())[0]
    urn = dataset.structure.short_urn
    df_test = pd.DataFrame(
        {
            "DIM1": [1, 1],
            "DIM2": [4, 5],
            "ATT1": ["A", "B"],  # Varying attribute
            "ATT2": [7, 8],
            "M1": [10, 11],
        }
    )
    dataset.data = df_test

    result = write_gen(
        [dataset],
        header=header,
        dimension_at_observation={urn: "DIM2"},
    )

    assert result is not None
    assert "gen:Series" in result
    assert "gen:Obs" in result
    assert result.count("<gen:Series>") == 2
    assert "A" in result
    assert "B" in result


@pytest.fixture
def ds_optional_attributes():
    df = pd.DataFrame(
        {
            "DIM1": ["A", "B", "C", "D", "E"],
            "DIM2": ["X", "Y", "Z", "W", "V"],
            "OBS": [1, 2, 3, 4, 5],
            "G_ATT": ["G1", "", "G3", None, ""],
            "S_ATT": ["S1", "S1", "", None, ""],
            "O_ATT": ["", "", "", "VAL", ""],
        }
    )

    structure = Schema(
        id="TEST_COV",
        context="datastructure",
        agency="MD",
        version="1.0",
        groups=[Group(id="Group", dimensions=["DIM1"])],
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
                    id="OBS",
                    role=Role.MEASURE,
                    concept=Concept(id="OBS"),
                    required=True,
                ),
                Component(
                    id="G_ATT",
                    role=Role.ATTRIBUTE,
                    concept=Concept(id="G_ATT"),
                    attachment_level="DIM1",
                    required=False,
                ),
                Component(
                    id="S_ATT",
                    role=Role.ATTRIBUTE,
                    concept=Concept(id="S_ATT"),
                    attachment_level="DIM1",
                    required=False,
                ),
                Component(
                    id="O_ATT",
                    role=Role.ATTRIBUTE,
                    concept=Concept(id="O_ATT"),
                    attachment_level="O",
                    required=False,
                ),
            ]
        ),
    )
    ds = PandasDataset(data=df, structure=structure)
    return {ds.structure.short_urn: ds}


def test_write_generic_optional_attributes_with_groups(ds_optional_attributes):
    ds = list(ds_optional_attributes.values())[0]
    dim_at_obs = {ds.structure.short_urn: "DIM2"}

    result = write_gen(
        [ds],
        dimension_at_observation=dim_at_obs,
    )

    # Groups with present values and #N/A for None
    assert '<gen:Value id="G_ATT" value="G1"/>' in result
    assert '<gen:Value id="G_ATT" value="G3"/>' in result
    assert '<gen:Value id="G_ATT" value="#N/A"/>' in result
    assert '<gen:Value id="S_ATT" value="S1"/>' in result

    # Roundtrip validation
    read_msg = read_sdmx(result, validate=True)
    result_data = read_msg.data[0].data

    # G_ATT should contain G1, G3 and '#N/A'
    g_att_values = result_data["G_ATT"].astype(str).tolist()
    assert "G1" in g_att_values
    assert "G3" in g_att_values
    assert g_att_values.count("#N/A") == 1


def test_write_generic_all_dimensions(ds_optional_attributes):
    """Missing optional attributes are written as "None" text in this mode."""
    ds = list(ds_optional_attributes.values())[0]
    dim_at_obs = {ds.structure.short_urn: "AllDimensions"}

    result = write_gen(
        [ds],
        dimension_at_observation=dim_at_obs,
    )

    assert 'gen:Value id="G_ATT" value="None"' in result
    assert 'gen:Value id="S_ATT" value="None"' in result

    # Roundtrip validation
    read_msg = read_sdmx(result, validate=True)
    result_data = read_msg.data[0].data

    # Verify O_ATT value "VAL" persists for DIM1="D"
    filter = result_data["DIM1"] == "D"
    row_d = result_data[filter]
    assert not row_d.empty
    assert row_d["O_ATT"].values[0] == "VAL"


def test_write_structure_specific_optional_attributes(ds_optional_attributes):
    ds = list(ds_optional_attributes.values())[0]
    dim_at_obs = {ds.structure.short_urn: "DIM2"}

    result = write_str_spec(
        [ds],
        dimension_at_observation=dim_at_obs,
    )

    assert 'O_ATT="VAL"' in result

    # Roundtrip validation
    read_msg = read_sdmx(result, validate=True)
    result_data = read_msg.data[0].data

    # Verify O_ATT value "VAL" persists
    filter = result_data["DIM1"] == "D"
    row_d = result_data[filter]
    assert not row_d.empty
    assert row_d["O_ATT"].values[0] == "VAL"


def test_write_generic_no_groups_series_attributes(ds_optional_attributes):
    ds = list(ds_optional_attributes.values())[0]

    new_structure = Schema(
        id=ds.structure.id,
        agency=ds.structure.agency,
        version=ds.structure.version,
        context=ds.structure.context,
        components=ds.structure.components,
        groups=[],  # Explicitly empty groups
    )
    ds_no_groups = PandasDataset(data=ds.data, structure=new_structure)

    dim_at_obs = {ds_no_groups.structure.short_urn: "DIM2"}

    result = write_gen(
        [ds_no_groups],
        dimension_at_observation=dim_at_obs,
    )

    assert '<gen:Value id="S_ATT" value="S1"/>' in result

    # Roundtrip validation
    read_msg = read_sdmx(result, validate=True)
    result_data = read_msg.data[0].data

    s_att_count = result_data["S_ATT"].astype(str).tolist()
    assert s_att_count.count("S1") == 2


def test_all_dimensions_with_series_only_row(header):
    # Dataset with empty DIM2
    ds = PandasDataset(
        data=pd.DataFrame(
            {
                "DIM1": ["A", "B", "C"],
                "DIM2": ["X", "", "Z"],  # Empty dimension
                "ATT1": ["a1", "a2", "a3"],
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
                        required=False,
                        attachment_level="DIM1",
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
    )

    with pytest.raises(
        Invalid,
        match="AllDimensions requires all dimensions to have values. "
        "Dimension 'DIM2' has empty values",
    ):
        write_str_spec(
            [ds],
            header=header,
            dimension_at_observation={ds.structure.short_urn: "AllDimensions"},
        )


def test_series_format_with_series_no_obs(header):
    ds = PandasDataset(
        data=pd.DataFrame(
            {
                "DIM1": ["A", "A", "B"],
                "DIM2": ["X", "Y", ""],  # B series has no obs (empty DIM2)
                "ATT1": ["a1", "a1", "b1"],
                "M1": [10, 11, ""],  # B series has no measure
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
                        required=False,
                        attachment_level="DIM1",
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
    )

    result = write_str_spec(
        [ds],
        header=header,
        prettyprint=True,
        dimension_at_observation={ds.structure.short_urn: "DIM2"},
    )

    assert result is not None
    # Series A should have observations
    assert "<Series " in result
    assert "<Obs " in result
    # Series B should be "selfclosed" (no observations)
    assert '<Series DIM1="B" ATT1="b1" />' in result
