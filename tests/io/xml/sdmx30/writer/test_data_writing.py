import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
import xmltodict

import pysdmx
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.sdmx30.writer.structure_specific import (
    write as write_str_spec,
)
from pysdmx.model import (
    Component,
    Components,
    Concept,
    Organisation,
    Role,
    Schema,
)
from pysdmx.model.dataflow import GroupDimension
from pysdmx.model.message import Header

SCHEMA_ROOT = "http://www.sdmx.org/resources/sdmxml/schemas/v3_0/"
NAMESPACES_30 = {
    SCHEMA_ROOT + "message": None,
    SCHEMA_ROOT + "common": None,
    SCHEMA_ROOT + "structure": None,
    "http://www.w3.org/2001/XMLSchema-instance": "xsi",
    "http://www.w3.org/XML/1998/namespace": None,
    SCHEMA_ROOT + "data/structurespecific": None,
    SCHEMA_ROOT + "registry": None,
    "http://schemas.xmlsoap.org/soap/envelope/": None,
}

XML_OPTIONS = {
    "process_namespaces": True,
    "namespaces": NAMESPACES_30,
    "dict_constructor": dict,
    "attr_prefix": "",
}


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
def prov_agree():
    ds = PandasDataset(
        data=pd.DataFrame(
            {
                "DIM1": [1, 2, 3],
                "M1": [10, 11, 12],
            }
        ),
        structure=Schema(
            context="provisionagreement",
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
                        id="ds_att1",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ds_att1"),
                        required=True,
                    ),
                    Component(
                        id="ds_att2",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ds_att2"),
                        required=True,
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
    return ds


@pytest.fixture
def data_flow():
    ds = PandasDataset(
        data=pd.DataFrame(
            {
                "DIM1": [1, 2, 3],
                "M1": [10, 11, 12],
            }
        ),
        structure=Schema(
            context="dataflow",
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
                        id="ds_att1",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ds_att1"),
                        required=True,
                    ),
                    Component(
                        id="ds_att2",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ds_att2"),
                        required=True,
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
    return ds


@pytest.fixture
def data_structure():
    ds = PandasDataset(
        data=pd.DataFrame(
            {
                "DIM1": [1, 2, 3],
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
                        id="M1",
                        role=Role.MEASURE,
                        concept=Concept(id="M1"),
                        required=True,
                    ),
                ]
            ),
        ),
    )
    return ds


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
            groups=[GroupDimension(id="ATT3", dimensions=["DIM2"])],
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
        attributes={"ds_att1": "value1", "ds_att2": "10"},
    )
    return {ds.structure.short_urn: ds}


def test_data_write_prov_agree_30(
    header,
    prov_agree,
):
    base_path = (
        Path(__file__).parent / "samples" / "data_write_30_prov_agree.xml"
    )
    result = write_str_spec(
        datasets=[prov_agree],
        header=header,
        prettyprint=True,
    )
    with open(base_path, "r") as f:
        expected = f.read()

    assert result == expected


def test_data_write_data_flow_30(
    header,
    data_flow,
):
    base_path = (
        Path(__file__).parent / "samples" / "data_write_30_data_flow.xml"
    )
    result = write_str_spec(
        datasets=[data_flow],
        header=header,
        prettyprint=True,
    )
    with open(base_path, "r") as f:
        expected = f.read()

    assert result == expected


def test_data_write_data_structure_30(
    header,
    data_structure,
):
    base_path = (
        Path(__file__).parent / "samples" / "data_write_30_data_structure.xml"
    )
    result = write_str_spec(
        datasets=[data_structure],
        header=header,
        prettyprint=True,
    )
    with open(base_path, "r") as f:
        expected = f.read()

    assert result == expected


def test_data_write_30_path(
    header,
    data_structure,
):
    output_path = str(Path(__file__).parent / "samples" / "test_output.xml")
    write_str_spec(
        datasets=[data_structure],
        header=header,
        prettyprint=True,
        output_path=output_path,
    )
    os.remove(output_path)


def test_data_write_data_structure_30_no_header(
    data_structure,
):
    result = write_str_spec(
        datasets=[data_structure],
        prettyprint=True,
    )
    assert result is not None

    dict_info = xmltodict.parse(
        result,
        **XML_OPTIONS,
    )
    header = dict_info.get("StructureSpecificData").get("Header")

    assert header is not None
    assert header.get("Test") == "false"
    assert header.get("Sender").get("id") == "ZZZ"
    assert header.get("Structure") == {
        "Structure": "urn:sdmx:org.sdmx.infomodel."
        "datastructure.DataStructure=MD:TEST(1.0)",
        "dimensionAtObservation": "AllDimensions",
        "namespace": "urn:sdmx:org.sdmx.infomodel."
        "datastructure.DataStructure=MD:TEST(1.0)",
        "structureID": "TEST",
    }


def test_data_write_30_chunksize(
    header,
    data_structure,
):
    pysdmx.io.xml.__write_structure_specific_aux.CHUNKSIZE = 1
    write_str_spec(
        header=header,
        datasets=[data_structure],
        prettyprint=True,
    )


def test_write_data_with_groups(header, ds_with_group):
    base_path = (
        Path(__file__).parent / "samples" / "test_dataset_with_groups.xml"
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
