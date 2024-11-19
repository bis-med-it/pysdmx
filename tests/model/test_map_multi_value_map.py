from datetime import datetime, timedelta, timezone

import pytest

from pysdmx.model import MultiValueMap


@pytest.fixture()
def source():
    return ["CH", "LC"]


@pytest.fixture()
def target():
    return ["CHF"]


def test_default_instantiation(source, target):
    m = MultiValueMap(source, target)

    assert m.source == source
    assert m.target == target
    assert m.valid_from is None
    assert m.valid_to is None


def test_full_instantiation(source, target):
    vf = datetime.now(timezone.utc) - timedelta(days=1)
    vt = datetime.now(timezone.utc)
    m = MultiValueMap(source, target, vf, vt)

    assert m.source == source
    assert m.target == target
    assert m.valid_from == vf
    assert m.valid_to == vt


def test_immutable(source, target):
    m = MultiValueMap(source, target)
    with pytest.raises(AttributeError):
        m.valid_from = datetime.now(timezone.utc)


def test_equal(source, target):
    m1 = MultiValueMap(source, target)
    m2 = MultiValueMap(source, target)

    assert m1 == m2


def test_not_equal(source, target):
    m1 = MultiValueMap(source, target)
    m2 = MultiValueMap(source, target, datetime.now(timezone.utc))

    assert m1 != m2
