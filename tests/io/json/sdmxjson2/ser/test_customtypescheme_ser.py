from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.vtl import JsonCustomTypeScheme
from pysdmx.model import Agency, Annotation, CustomType, CustomTypeScheme


@pytest.fixture
def cts():
    c = CustomType(
        "RATING", name="Rating", vtl_scalar_type="test", data_type="string"
    )
    return CustomTypeScheme(
        "CTS",
        name="CTS Scheme",
        agency="BIS",
        description="Just testing",
        version="1.42",
        items=[c],
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        is_partial=True,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        vtl_version="1.0",
    )


@pytest.fixture
def cts_org():
    c = CustomType(
        "RATING", name="Rating", vtl_scalar_type="test", data_type="string"
    )
    return CustomTypeScheme(
        "CTS",
        name="CTS testing",
        agency=Agency("BIS"),
        items=[c],
        vtl_version="1.0",
    )


@pytest.fixture
def cts_no_name():
    c = CustomType(
        "RATING", name="Rating", vtl_scalar_type="test", data_type="string"
    )
    return CustomTypeScheme(
        "CTS", agency=Agency("BIS"), items=[c], vtl_version="1.0"
    )


def test_cts(cts: CustomTypeScheme):
    sjson = JsonCustomTypeScheme.from_model(cts)

    assert sjson.id == cts.id
    assert sjson.name == cts.name
    assert sjson.agency == cts.agency
    assert sjson.description == cts.description
    assert sjson.version == cts.version
    assert len(sjson.customTypes) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == cts.valid_from
    assert sjson.validTo == cts.valid_to
    assert sjson.vtlVersion == cts.vtl_version


def test_cts_org(cts_org: CustomTypeScheme):
    sjson = JsonCustomTypeScheme.from_model(cts_org)

    assert sjson.agency == cts_org.agency.id


def test_cts_no_name(cts_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonCustomTypeScheme.from_model(cts_no_name)
