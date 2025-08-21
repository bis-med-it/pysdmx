import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
import xmltodict

from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.sdmx31.writer.structure_specific import (
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
from pysdmx.model.message import Header

SCHEMA_ROOT = "http://www.sdmx.org/resources/sdmxml/schemas/v3_1/"
NAMESPACES_31 = {
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
    "namespaces": NAMESPACES_31,
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
                        attachment_level="D",
                    ),
                    Component(
                        id="ds_att2",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ds_att2"),
                        required=True,
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
                        attachment_level="D",
                    ),
                    Component(
                        id="ds_att2",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ds_att2"),
                        required=True,
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


def test_data_write_prov_agree_31(
    header,
    prov_agree,
):
    base_path = (
        Path(__file__).parent / "samples" / "data_write_31_prov_agree.xml"
    )
    result = write_str_spec(
        datasets=[prov_agree],
        header=header,
        prettyprint=True,
    )
    with open(base_path, "r") as f:
        expected = f.read()

    assert result == expected


def test_data_write_data_flow_31(
    header,
    data_flow,
):
    base_path = (
        Path(__file__).parent / "samples" / "data_write_31_data_flow.xml"
    )
    result = write_str_spec(
        datasets=[data_flow],
        header=header,
        prettyprint=True,
    )
    with open(base_path, "r") as f:
        expected = f.read()

    assert result == expected


def test_data_write_data_structure_31(
    header,
    data_structure,
):
    base_path = (
        Path(__file__).parent / "samples" / "data_write_31_data_structure.xml"
    )
    result = write_str_spec(
        datasets=[data_structure],
        header=header,
        prettyprint=True,
    )
    with open(base_path, "r") as f:
        expected = f.read()

    assert result == expected


def test_data_write_31_path(
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


def test_data_write_data_structure_31_no_header(
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
