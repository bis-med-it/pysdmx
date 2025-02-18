from typing import Iterable, Sized

import msgspec
import pytest

from pysdmx.model.__base import (
    Agency,
    Annotation,
    Contact,
    DataConsumer,
    DataflowRef,
    DataProvider,
    MetadataProvider,
)
from pysdmx.model.organisation import (
    AgencyScheme,
    DataConsumerScheme,
    DataProviderScheme,
    MetadataProviderScheme,
)

ENCODER = msgspec.msgpack.Encoder()


@pytest.fixture
def contacts():
    return [
        Contact(
            "TEST",
            "Test contact",
            "Test department",
            "Test role",
            emails=["test@testing.org"],
        )
    ]


@pytest.fixture
def dataflows():
    return [DataflowRef("BIS", "CBS", "1.0"), DataflowRef("BIS", "LBS", "1.0")]


@pytest.fixture
def annotations():
    return [
        Annotation(
            "an1",
            "test annotation",
            "text",
            "http://test.org",
            "TEST_ANNOTATION",
        )
    ]


@pytest.fixture
def agencies(contacts, dataflows, annotations):
    a1 = Agency(
        "BIS",
        name="BIS",
        description="Test description",
        contacts=contacts,
        dataflows=dataflows,
        annotations=annotations,
    )
    a2 = Agency("SDMX", name="SDMX")
    return AgencyScheme(agency="TEST", items=[a1, a2])


@pytest.fixture
def data_providers(contacts, dataflows, annotations):
    dp1 = DataProvider(
        "5B0",
        name="BIS",
        description="Test description",
        contacts=contacts,
        dataflows=dataflows,
        annotations=annotations,
    )
    dp2 = DataProvider("4F0", name="ECB")
    return DataProviderScheme(agency="TEST", items=[dp1, dp2])


@pytest.fixture
def data_consumers(contacts, dataflows, annotations):
    dp1 = DataConsumer(
        "5B0",
        name="BIS",
        description="Test description",
        contacts=contacts,
        dataflows=dataflows,
        annotations=annotations,
    )
    dp2 = DataConsumer("ECB", name="ECB")
    return DataConsumerScheme(agency="TEST", items=[dp1, dp2])


@pytest.fixture
def metadata_providers(contacts, dataflows, annotations):
    dp1 = MetadataProvider(
        "5B0",
        name="BIS",
        description="Test description",
        contacts=contacts,
        dataflows=dataflows,
        annotations=annotations,
    )
    dp2 = MetadataProvider("4F0", name="ECB")
    return MetadataProviderScheme(agency="TEST", items=[dp1, dp2])


def test_agency_scheme_serde(agencies):
    ser = ENCODER.encode(agencies)

    deser = msgspec.msgpack.Decoder(AgencyScheme).decode(ser)

    assert deser == agencies


def test_data_provider_scheme_serde(data_providers):
    ser = ENCODER.encode(data_providers)

    deser = msgspec.msgpack.Decoder(DataProviderScheme).decode(ser)

    assert deser == data_providers


def test_data_consumer_scheme_serde(data_consumers):
    ser = ENCODER.encode(data_consumers)

    deser = msgspec.msgpack.Decoder(DataConsumerScheme).decode(ser)

    assert deser == data_consumers


def test_metadata_provider_scheme_serde(metadata_providers):
    ser = ENCODER.encode(metadata_providers)

    deser = msgspec.msgpack.Decoder(MetadataProviderScheme).decode(ser)

    assert deser == metadata_providers


def test_dps_iterable(data_providers):
    assert isinstance(data_providers, Iterable)
    out = list(data_providers)
    assert len(out) == len(data_providers.providers)
    assert out == data_providers.providers


def test_dps_sized(data_providers):
    assert isinstance(data_providers, Sized)


def test_dps_get_provider(data_providers):
    for p in data_providers.items:
        assert data_providers[p.id] == p
        assert p.id in data_providers

    assert data_providers["NOT_IN_THE_SCHEME"] is None
