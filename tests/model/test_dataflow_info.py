from datetime import datetime, timezone

import msgspec
import pytest

from pysdmx.model import (
    Agency,
    ArrayBoundaries,
    Component,
    Components,
    Concept,
    DataflowInfo,
    DataProvider,
    DataType,
    decoders,
    encoders,
    Facets,
    Role,
)


@pytest.fixture()
def id():
    return "EXR"


@pytest.fixture()
def comps():
    f1 = Component(
        "FREQ",
        True,
        Role.DIMENSION,
        Concept("FREQ", dtype=DataType.STRING),
        DataType.ALPHA,
        Facets(min_length=1, max_length=3),
    )
    f2 = Component(
        "INDICATOR", True, Role.DIMENSION, Concept("IND"), DataType.STRING
    )
    f3 = Component(
        "PERIOD", True, Role.DIMENSION, Concept("PERIOD"), DataType.PERIOD
    )
    f4 = Component(
        "VALUE", False, Role.MEASURE, Concept("VALUE"), DataType.INTEGER
    )
    f5 = Component(
        "CONF",
        True,
        Role.ATTRIBUTE,
        Concept("CONF"),
        DataType.STRING,
        attachment_level="O",
        array_def=ArrayBoundaries(1, 3),
    )
    return Components([f1, f2, f3, f4, f5])


@pytest.fixture()
def name():
    return "EXR name"


@pytest.fixture()
def desc():
    return "EXR desc"


@pytest.fixture()
def agency():
    return Agency("BIS")


@pytest.fixture()
def version():
    return "1.42"


@pytest.fixture()
def providers():
    return [DataProvider("5B0"), DataProvider("4F0")]


@pytest.fixture()
def series():
    return 42_000


@pytest.fixture()
def obs():
    return 20_110_617


@pytest.fixture()
def start():
    return "2000"


@pytest.fixture()
def end():
    return "2042"


@pytest.fixture()
def upd():
    return datetime.now(timezone.utc)


@pytest.fixture()
def dsd():
    return (
        "urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure="
        "BIS:BIS_CBS(1.0)"
    )


def test_basic_instantiation(id, comps, agency):
    ds = DataflowInfo(id, comps, agency)

    assert ds.id == id
    assert ds.components == comps
    assert ds.agency == agency
    assert ds.name is None
    assert ds.description is None
    assert ds.version == "1.0"
    assert len(ds.providers) == 0
    assert ds.series_count is None
    assert ds.obs_count is None
    assert ds.start_period is None
    assert ds.end_period is None
    assert ds.last_updated is None
    assert ds.dsd_ref is None


def test_full_instantiation(
    id,
    comps,
    name,
    desc,
    agency,
    version,
    providers,
    series,
    obs,
    start,
    end,
    upd,
    dsd,
):
    ds = DataflowInfo(
        id,
        comps,
        agency,
        name,
        desc,
        version,
        providers,
        series,
        obs,
        start,
        end,
        upd,
        dsd,
    )

    assert ds.id == id
    assert ds.components == comps
    assert ds.name == name
    assert ds.description == desc
    assert ds.agency == agency
    assert ds.version == version
    assert ds.providers == providers
    assert ds.series_count == series
    assert ds.obs_count == obs
    assert ds.start_period == start
    assert ds.end_period == end
    assert ds.last_updated == upd
    assert ds.dsd_ref == dsd


def test_immutable(id, comps, agency):
    ds = DataflowInfo(id, comps, agency)
    with pytest.raises(AttributeError):
        ds.name = "Not allowed"


def test_equal(id, comps, name, agency):
    ds1 = DataflowInfo(id, comps, agency, name=name)
    ds2 = DataflowInfo(id, comps, agency, name=name)

    assert ds1 == ds2


def test_not_equal(id, comps, name, agency, upd):
    ds1 = DataflowInfo(id, comps, agency, name=name)
    ds2 = DataflowInfo(
        id,
        comps,
        agency,
        name=name,
        last_updated=upd,
    )

    assert ds1 != ds2


def test_tostr_basic(id, comps, agency):
    ds = DataflowInfo(id, comps, agency)

    s = str(ds)

    assert s == f"id={id}, components={comps}, agency={agency}, version=1.0"


def test_tostr_more(
    id,
    comps,
    name,
    agency,
    providers,
    obs,
    start,
    end,
    upd,
):
    ds = DataflowInfo(
        id,
        comps,
        agency,
        name=name,
        providers=providers,
        obs_count=obs,
        start_period=start,
        end_period=end,
        last_updated=upd,
    )

    s = str(ds)

    assert s == (
        f"id={id}, components={comps}, agency={agency}, "
        f"name={name}, version=1.0, providers={providers}, obs_count={obs}, "
        f"start_period={start}, end_period={end}, last_updated={upd}"
    )


def test_serialization(
    id,
    comps,
    name,
    desc,
    agency,
    version,
    providers,
    series,
    obs,
    start,
    end,
    upd,
    dsd,
):
    ds = DataflowInfo(
        id,
        comps,
        agency,
        name,
        desc,
        version,
        providers,
        series,
        obs,
        start,
        end,
        upd,
        dsd,
    )

    ser = msgspec.msgpack.Encoder(enc_hook=encoders).encode(ds)
    out = msgspec.msgpack.Decoder(DataflowInfo, dec_hook=decoders).decode(ser)
    assert out == ds
