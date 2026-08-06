from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx.io.json.sdmxjson2.messages.consumer import JsonDataConsumerScheme
from pysdmx.model import Agency, Annotation, DataConsumer, DataConsumerScheme


@pytest.fixture
def dps():
    c = DataConsumer("5B0", name="BIS")
    return DataConsumerScheme(
        agency="BIS",
        description="BIS consumers",
        items=[c],
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        is_partial=True,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
    )


@pytest.fixture
def dps_org():
    c = DataConsumer("5B0", name="BIS")
    return DataConsumerScheme(
        agency=Agency("BIS"), description="FREQ cl", items=[c]
    )


def test_consumer_scheme(dps: DataConsumerScheme):
    sjson = JsonDataConsumerScheme.from_model(dps)

    assert sjson.id == "DATA_CONSUMERS"
    assert sjson.name == "DATA_CONSUMERS"
    assert sjson.agency == dps.agency
    assert sjson.description == dps.description
    assert sjson.version == "1.0"
    assert len(sjson.dataConsumers) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == dps.valid_from
    assert sjson.validTo == dps.valid_to


def test_consumer_scheme_org(dps_org: DataConsumerScheme):
    sjson = JsonDataConsumerScheme.from_model(dps_org)

    assert sjson.agency == dps_org.agency.id
