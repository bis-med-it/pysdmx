from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx.io.json.sdmxjson2.messages.agency import JsonAgencyScheme
from pysdmx.model import Agency, AgencyScheme, Annotation


@pytest.fixture
def asc():
    c = Agency("BIS", name="BIS")
    return AgencyScheme(
        agency="SDMX",
        description="SDMX agencies",
        items=[c],
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        is_partial=True,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
    )


@pytest.fixture
def asc_org():
    c = Agency("BIS", name="BIS")
    return AgencyScheme(
        agency=Agency("SDMX"), description="FREQ cl", items=[c]
    )


@pytest.fixture
def sub_agencies():
    c = Agency("BIS.TEST", name="BIS")
    return AgencyScheme(agency="BIS", items=[c])


def test_agency_scheme(asc: AgencyScheme):
    sjson = JsonAgencyScheme.from_model(asc)

    assert sjson.id == "AGENCIES"
    assert sjson.name == "AGENCIES"
    assert sjson.agency == asc.agency
    assert sjson.description == asc.description
    assert sjson.version == "1.0"
    assert len(sjson.agencies) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == asc.valid_from
    assert sjson.validTo == asc.valid_to


def test_agency_scheme_org(asc_org: AgencyScheme):
    sjson = JsonAgencyScheme.from_model(asc_org)

    assert sjson.agency == asc_org.agency.id


def test_agency_scheme_sub(sub_agencies: AgencyScheme):
    sjson = JsonAgencyScheme.from_model(sub_agencies)

    assert len(sjson.agencies) == 1
    sub = sjson.agencies[0]
    assert sub.id == "TEST"
