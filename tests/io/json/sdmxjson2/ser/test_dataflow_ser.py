from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.core import JsonLink
from pysdmx.io.json.sdmxjson2.messages.dataflow import JsonDataflow
from pysdmx.model import (
    Agency,
    Annotation,
    Component,
    Components,
    Concept,
    Dataflow,
    DataStructureDefinition,
    DataType,
    Role,
)

_CBS = (
    "urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=BIS:BIS_CBS(1.0)"
)


@pytest.fixture
def dataflow():
    return Dataflow(
        "CL_FREQ",
        name="Frequency",
        agency="BIS",
        description="FREQ cl",
        version="1.42",
        annotations=[Annotation(type="test")],
        is_external_reference=True,
        structure_url="https://example.test/dataflow/BIS/CL_FREQ/1.42",
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        structure=_CBS,
    )


@pytest.fixture
def dataflow_org():
    return Dataflow(
        "CL_FREQ",
        name="Frequency",
        agency=Agency("BIS"),
        structure=_CBS,
    )


@pytest.fixture
def dataflow_dsd():
    return Dataflow(
        "CL_FREQ",
        name="Frequency",
        agency=Agency("BIS"),
        structure=DataStructureDefinition(
            "BIS_CBS",
            agency="BIS",
            version="1.0",
            components=Components(
                [
                    Component(
                        "DIM",
                        True,
                        Role.DIMENSION,
                        Concept("DIM"),
                        DataType.STRING,
                    )
                ]
            ),
        ),
    )


@pytest.fixture
def dataflow_no_name():
    return Dataflow(
        "CL_FREQ",
        agency=Agency("BIS"),
        structure=_CBS,
    )


@pytest.fixture
def dataflow_no_structure():
    return Dataflow(
        "CL_FREQ",
        agency=Agency("BIS"),
        name="Frequency",
    )


def test_dataflow(dataflow: Dataflow):
    sjson = JsonDataflow.from_model(dataflow)

    assert sjson.id == dataflow.id
    assert sjson.name == dataflow.name
    assert sjson.agency == dataflow.agency
    assert sjson.description == dataflow.description
    assert sjson.version == dataflow.version
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is True
    assert sjson.links[0].rel == "self"
    assert sjson.links[0].href == dataflow.structure_url
    assert sjson.validFrom == dataflow.valid_from
    assert sjson.validTo == dataflow.valid_to
    assert sjson.structure == _CBS
    assert sjson.to_model().is_external_reference is True


def test_dataflow_uses_first_self_link_with_href():
    sjson = JsonDataflow(
        agency="BIS",
        id="CL_FREQ",
        name="Frequency",
        structure=_CBS,
        isExternalReference=True,
        links=(
            JsonLink(rel="self"),
            JsonLink(rel="alternate", href="https://example.test/alternate"),
            JsonLink(rel="self", href="https://example.test/dataflow"),
            JsonLink(rel="self", href="https://example.test/ignored"),
        ),
    )

    model = sjson.to_model()

    assert model.structure_url == "https://example.test/dataflow"
    assert JsonDataflow.from_model(model).isExternalReference is True


def test_dataflow_org(dataflow_org: Dataflow):
    sjson = JsonDataflow.from_model(dataflow_org)

    assert sjson.agency == dataflow_org.agency.id


def test_dataflow_dsd(dataflow_dsd: Dataflow):
    sjson = JsonDataflow.from_model(dataflow_dsd)

    assert sjson.structure == _CBS


def test_dataflow_no_name(dataflow_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonDataflow.from_model(dataflow_no_name)


def test_dataflow_no_structure(dataflow_no_structure):
    with pytest.raises(errors.Invalid, match="must reference a DSD"):
        JsonDataflow.from_model(dataflow_no_structure)
