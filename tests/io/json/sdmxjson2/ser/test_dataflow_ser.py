from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
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
        is_external_reference=False,
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
    assert sjson.isExternalReference is False
    assert sjson.validFrom == dataflow.valid_from
    assert sjson.validTo == dataflow.valid_to
    assert sjson.structure == _CBS


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
