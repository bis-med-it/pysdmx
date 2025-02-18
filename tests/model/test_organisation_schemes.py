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


def test_as_serde(agencies):
    ser = ENCODER.encode(agencies)

    deser = msgspec.msgpack.Decoder(AgencyScheme).decode(ser)

    assert deser == agencies


def test_dps_serde(data_providers):
    ser = ENCODER.encode(data_providers)

    deser = msgspec.msgpack.Decoder(DataProviderScheme).decode(ser)

    assert deser == data_providers


def test_dcs_serde(data_consumers):
    ser = ENCODER.encode(data_consumers)

    deser = msgspec.msgpack.Decoder(DataConsumerScheme).decode(ser)

    assert deser == data_consumers


def test_mps_serde(metadata_providers):
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


def test_mps_iterable(metadata_providers):
    assert isinstance(metadata_providers, Iterable)
    out = list(metadata_providers)
    assert len(out) == len(metadata_providers.providers)
    assert out == metadata_providers.providers


def test_mps_sized(metadata_providers):
    assert isinstance(metadata_providers, Sized)


def test_mps_get_provider(metadata_providers):
    for p in metadata_providers.items:
        assert metadata_providers[p.id] == p
        assert p.id in metadata_providers

    assert metadata_providers["NOT_IN_THE_SCHEME"] is None


def test_dcs_iterable(data_consumers):
    assert isinstance(data_consumers, Iterable)
    out = list(data_consumers)
    assert len(out) == len(data_consumers.consumers)
    assert out == data_consumers.consumers


def test_dcs_sized(data_consumers):
    assert isinstance(data_consumers, Sized)


def test_dcs_get_consumer(data_consumers):
    for p in data_consumers.items:
        assert data_consumers[p.id] == p
        assert p.id in data_consumers

    assert data_consumers["NOT_IN_THE_SCHEME"] is None


def test_as_iterable(agencies):
    assert isinstance(agencies, Iterable)
    out = list(agencies)
    assert len(out) == len(agencies.agencies)
    assert out == agencies.agencies


def test_as_sized(agencies):
    assert isinstance(agencies, Sized)


def test_as_get_agency(agencies):
    for p in agencies.items:
        assert agencies[p.id] == p
        assert p.id in agencies

    assert agencies["NOT_IN_THE_SCHEME"] is None
