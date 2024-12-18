from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from pysdmx.errors import Invalid
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.enums import MessageType
from pysdmx.io.xml.sdmx21.reader import read_xml
from pysdmx.io.xml.sdmx21.writer import writer
import pysdmx.io.xml.sdmx21.writer.config
from pysdmx.model import (
    Code,
    Codelist,
    Component,
    Components,
    Concept,
    Role,
    Schema,
)
from pysdmx.model.message import Header


@pytest.fixture()
def header():
    return Header(
        id="ID",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
    )


@pytest.fixture()
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
            context="DataStructure",
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
        (MessageType.GenericDataSet, "gen_all.xml", {}),
        (MessageType.StructureSpecificDataSet, "str_all.xml", None),
        (
            MessageType.StructureSpecificDataSet,
            "str_ser.xml",
            {"DataStructure=MD:TEST(1.0)": "DIM1"},
        ),
        (
            MessageType.GenericDataSet,
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
    result = writer(
        content,
        type_=message_type,
        header=header,
        dimension_at_observation=dimension_at_observation,
    )
    # Read the result to check for formal errors
    result_msg = read_xml(result, validate=True)
    assert "DataStructure=MD:TEST(1.0)" in result_msg
    # Read the reference to compare with the result
    infile, _ = process_string_to_read(samples_folder_path / filename)
    reference_msg = read_xml(infile, validate=True)
    result_data = result_msg["DataStructure=MD:TEST(1.0)"].data
    reference_data = reference_msg["DataStructure=MD:TEST(1.0)"].data

    assert result_data.shape == (3, 5)

    pd.testing.assert_frame_equal(
        result_data.fillna("").replace("nan", ""),
        reference_data.replace("nan", ""),
        check_like=True,
    )


@pytest.mark.parametrize(
    ("message_type", "dimension_at_observation"),
    [
        (MessageType.GenericDataSet, {}),
        (MessageType.StructureSpecificDataSet, None),
        (
            MessageType.StructureSpecificDataSet,
            {"DataStructure=MD:TEST(1.0)": "DIM1"},
        ),
        (
            MessageType.GenericDataSet,
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
    content["DataStructure=MD:TEST(1.0)"] = ds

    result = writer(
        content,
        type_=message_type,
        header=header,
        dimension_at_observation=dimension_at_observation,
    )
    # Read the result to check for formal errors
    result_msg = read_xml(result, validate=True)
    assert "DataStructure=MD:TEST(1.0)" in result_msg
    result_data = result_msg["DataStructure=MD:TEST(1.0)"].data

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
        Invalid, match="Message Content must contain only Datasets."
    ):
        writer(content, type_=MessageType.StructureSpecificDataSet)


def test_invalid_dimension(content):
    dim_mapping = {"DataStructure=MD:TEST(1.0)": "DIM3"}
    with pytest.raises(Invalid):
        writer(
            content,
            type_=MessageType.StructureSpecificDataSet,
            dimension_at_observation=dim_mapping,
        )


def test_invalid_dimension_key(content):

    dim_mapping = {"DataStructure=AAA:TEST(1.0)": "DIM1"}
    with pytest.raises(Invalid):
        writer(
            content,
            type_=MessageType.StructureSpecificDataSet,
            dimension_at_observation=dim_mapping,
        )
