from datetime import datetime, timezone

import pytest

from pysdmx.model import SeriesInfo


@pytest.fixture
def id():
    return "A.B.42"


@pytest.fixture
def name():
    return "AB42"


@pytest.fixture
def obs():
    return 4242


@pytest.fixture
def start():
    return "2000"


@pytest.fixture
def end():
    return "2042"


@pytest.fixture
def upd():
    return datetime.now(timezone.utc)


@pytest.fixture
def active():
    return True


def test_basic_instantiation(id):
    i = SeriesInfo(id)

    assert i.id == id
    assert i.name is None
    assert i.obs_count is None
    assert i.start_period is None
    assert i.end_period is None
    assert i.last_updated is None
    assert i.is_active is True


def test_full_instantiation(id, name, obs, start, end, upd, active):
    i = SeriesInfo(id, name, obs, start, end, upd, active)

    assert i.id == id
    assert i.name == name
    assert i.obs_count == obs
    assert i.start_period == start
    assert i.end_period == end
    assert i.last_updated == upd
    assert i.is_active == active


def test_immutable(id):
    i = SeriesInfo(id)
    with pytest.raises(AttributeError):
        i.name = "Not allowed"


def test_equal(id, name, obs, start, end, upd, active):
    i1 = SeriesInfo(id, name, obs, start, end, upd, active)
    i2 = SeriesInfo(id, name, obs, start, end, upd, active)

    assert i1 == i2


def test_not_equal(id, name, obs, start, end, upd, active):
    i1 = SeriesInfo(id, name, obs, start, end, upd, active)
    i2 = SeriesInfo(id, name, obs, start, end, upd, not active)

    assert i1 != i2


def test_tostr_id(id):
    i = SeriesInfo(id)

    s = str(i)

    assert s == f"id={id}, is_active=True"


def test_tostr(id, name, obs, start):
    i = SeriesInfo(id, name, obs, start)

    s = str(i)

    assert s == (
        f"id={id}, name={name}, obs_count={obs}, "
        f"start_period={start}, is_active=True"
    )
