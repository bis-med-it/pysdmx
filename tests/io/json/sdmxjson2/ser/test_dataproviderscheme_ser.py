from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx.io.json.sdmxjson2.messages.provider import JsonDataProviderScheme
from pysdmx.model import Agency, Annotation, DataProvider, DataProviderScheme


@pytest.fixture
def dps():
    c = DataProvider("5B0", name="BIS")
    return DataProviderScheme(
        agency="BIS",
        description="BIS providers",
        items=[c],
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        is_partial=True,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
    )


@pytest.fixture
def dps_org():
    c = DataProvider("5B0", name="BIS")
    return DataProviderScheme(
        agency=Agency("BIS"), description="FREQ cl", items=[c]
    )


def test_provider_scheme(dps: DataProviderScheme):
    sjson = JsonDataProviderScheme.from_model(dps)

    assert sjson.id == "DATA_PROVIDERS"
    assert sjson.name == "DATA_PROVIDERS"
    assert sjson.agency == dps.agency
    assert sjson.description == dps.description
    assert sjson.version == "1.0"
    assert len(sjson.dataProviders) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == dps.valid_from
    assert sjson.validTo == dps.valid_to


def test_provider_scheme_org(dps_org: DataProviderScheme):
    sjson = JsonDataProviderScheme.from_model(dps_org)

    assert sjson.agency == dps_org.agency.id
