from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.vtl import JsonNamePersonalisationScheme
from pysdmx.model import Agency, Annotation
from pysdmx.model.vtl import NamePersonalisation, NamePersonalisationScheme


@pytest.fixture
def nps():
    np = NamePersonalisation(
        "NP1",
        name="Name Personalisation",
        vtl_default_name="default_name",
        personalised_name="personalised_name",
        vtl_artefact="artefact",
    )
    return NamePersonalisationScheme(
        "NPS",
        name="NPS Scheme",
        agency="BIS",
        description="Just testing",
        version="1.42",
        items=[np],
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        is_partial=True,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        vtl_version="1.0",
    )


@pytest.fixture
def nps_org():
    np = NamePersonalisation(
        "NP1",
        name="Name Personalisation",
        vtl_default_name="default_name",
        personalised_name="personalised_name",
        vtl_artefact="artefact",
    )
    return NamePersonalisationScheme(
        "NPS",
        name="NPS testing",
        agency=Agency("BIS"),
        items=[np],
        vtl_version="1.0",
    )


@pytest.fixture
def nps_no_name():
    np = NamePersonalisation(
        "NP1",
        name="Name Personalisation",
        vtl_default_name="default_name",
        personalised_name="personalised_name",
        vtl_artefact="artefact",
    )
    return NamePersonalisationScheme(
        "NPS", agency=Agency("BIS"), items=[np], vtl_version="1.0"
    )


def test_nps(nps: NamePersonalisationScheme):
    sjson = JsonNamePersonalisationScheme.from_model(nps)

    assert sjson.id == nps.id
    assert sjson.name == nps.name
    assert sjson.agency == nps.agency
    assert sjson.description == nps.description
    assert sjson.version == nps.version
    assert len(sjson.namePersonalisations) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == nps.valid_from
    assert sjson.validTo == nps.valid_to
    assert sjson.vtlVersion == nps.vtl_version


def test_nps_org(nps_org: NamePersonalisationScheme):
    sjson = JsonNamePersonalisationScheme.from_model(nps_org)

    assert sjson.agency == nps_org.agency.id


def test_nps_no_name(nps_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonNamePersonalisationScheme.from_model(nps_no_name)
