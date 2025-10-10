from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.metadataflow import JsonMetadataflow
from pysdmx.model import (
    Agency,
    Annotation,
    Concept,
    MetadataComponent,
    Metadataflow,
    MetadataStructure,
    DataType,
)

_CBS = (
    "urn:sdmx:org.sdmx.infomodel.metadatastructure.MetadataStructure="
    "BIS:BIS_CBS(1.0)"
)


@pytest.fixture
def md():
    return Metadataflow(
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
        targets=["urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=*:*(*)"],
    )


@pytest.fixture
def md_org():
    return Metadataflow(
        "CL_FREQ",
        name="Frequency",
        agency=Agency("BIS"),
        structure=_CBS,
        targets=["urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=*:*(*)"],
    )


@pytest.fixture
def md_msd():
    return Metadataflow(
        "CL_FREQ",
        name="Frequency",
        agency=Agency("BIS"),
        structure=MetadataStructure(
            "BIS_CBS",
            agency="BIS",
            version="1.0",
            components=[
                MetadataComponent(
                    "DIM",
                    concept=Concept("DIM"),
                    local_dtype=DataType.INTEGER,
                )
            ],
        ),
        targets=["urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=*:*(*)"],
    )


@pytest.fixture
def md_no_name():
    return Metadataflow(
        "CL_FREQ",
        agency=Agency("BIS"),
        structure=_CBS,
        targets=["urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=*:*(*)"],
    )


def test_metadataflow(md: Metadataflow):
    sjson = JsonMetadataflow.from_model(md)

    assert sjson.id == md.id
    assert sjson.name == md.name
    assert sjson.agency == md.agency
    assert sjson.description == md.description
    assert sjson.version == md.version
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.validFrom == md.valid_from
    assert sjson.validTo == md.valid_to
    assert sjson.structure == _CBS


def test_metadataflow_org(md_org: Metadataflow):
    sjson = JsonMetadataflow.from_model(md_org)

    assert sjson.agency == md_org.agency.id


def test_metadataflow_dsd(md_msd: Metadataflow):
    sjson = JsonMetadataflow.from_model(md_msd)

    assert sjson.structure == _CBS


def test_metadataflow_no_name(md_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonMetadataflow.from_model(md_no_name)
