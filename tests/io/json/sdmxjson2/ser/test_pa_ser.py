from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.pa import JsonProvisionAgreement
from pysdmx.model import Agency, Annotation, ProvisionAgreement


@pytest.fixture
def pa():
    return ProvisionAgreement(
        "PA",
        name="PA BIS_MACRO 5B0",
        agency="BIS",
        description="My PA desc",
        version="1.42",
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        dataflow="BIS_MACRO",
        provider="5B0",
    )


@pytest.fixture
def pa_org():
    return ProvisionAgreement(
        "PA",
        name="PA BIS_MACRO 5B0",
        agency=Agency("BIS"),
        dataflow="BIS_MACRO",
        provider="5B0",
    )


@pytest.fixture
def pa_no_name():
    return ProvisionAgreement(
        "PA",
        agency=Agency("BIS"),
        dataflow="BIS_MACRO",
        provider="5B0",
    )


def test_pa(pa: ProvisionAgreement):
    sjson = JsonProvisionAgreement.from_model(pa)

    assert sjson.id == pa.id
    assert sjson.name == pa.name
    assert sjson.agency == pa.agency
    assert sjson.description == pa.description
    assert sjson.version == pa.version
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.validFrom == pa.valid_from
    assert sjson.validTo == pa.valid_to
    assert sjson.dataflow == pa.dataflow
    assert sjson.dataProvider == pa.provider


def test_pa_org(pa_org: ProvisionAgreement):
    sjson = JsonProvisionAgreement.from_model(pa_org)

    assert sjson.agency == pa_org.agency.id


def test_pa_no_name(pa_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonProvisionAgreement.from_model(pa_no_name)
