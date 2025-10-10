from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.mpa import (
    JsonMetadataProvisionAgreement,
)
from pysdmx.model import Agency, Annotation, MetadataProvisionAgreement


@pytest.fixture
def pa():
    return MetadataProvisionAgreement(
        "PA",
        name="PA BIS_MACRO 5B0",
        agency="BIS",
        description="My PA desc",
        version="1.42",
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        metadataflow="BIS_MACRO",
        metadata_provider="5B0",
    )


@pytest.fixture
def pa_org():
    return MetadataProvisionAgreement(
        "PA",
        name="PA BIS_MACRO 5B0",
        agency=Agency("BIS"),
        metadataflow="BIS_MACRO",
        metadata_provider="5B0",
    )


@pytest.fixture
def pa_no_name():
    return MetadataProvisionAgreement(
        "PA",
        agency=Agency("BIS"),
        metadataflow="BIS_MACRO",
        metadata_provider="5B0",
    )


def test_mpa(pa: MetadataProvisionAgreement):
    sjson = JsonMetadataProvisionAgreement.from_model(pa)

    assert sjson.id == pa.id
    assert sjson.name == pa.name
    assert sjson.agency == pa.agency
    assert sjson.description == pa.description
    assert sjson.version == pa.version
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.validFrom == pa.valid_from
    assert sjson.validTo == pa.valid_to
    assert sjson.metadataflow == pa.metadataflow
    assert sjson.metadataProvider == pa.metadata_provider


def test_mpa_org(pa_org: MetadataProvisionAgreement):
    sjson = JsonMetadataProvisionAgreement.from_model(pa_org)

    assert sjson.agency == pa_org.agency.id


def test_mpa_no_name(pa_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonMetadataProvisionAgreement.from_model(pa_no_name)
