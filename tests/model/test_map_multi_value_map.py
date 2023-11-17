from datetime import datetime, timedelta

import pytest

from pysdmx.model import MultipleValueMap


@pytest.fixture()
def source():
    return ["CH", "LC"]


@pytest.fixture()
def target():
    return ["CHF"]


def test_default_instantiation(source, target):
    m = MultipleValueMap(source, target)

    assert m.source == source
    assert m.target == target
    assert m.valid_from is None
    assert m.valid_to is None


def test_full_instantiation(source, target):
    vf = datetime.utcnow() - timedelta(days=1)
    vt = datetime.utcnow()
    m = MultipleValueMap(source, target, vf, vt)

    assert m.source == source
    assert m.target == target
    assert m.valid_from == vf
    assert m.valid_to == vt


def test_immutable(source, target):
    m = MultipleValueMap(source, target)
    with pytest.raises(AttributeError):
        m.valid_from = datetime.utcnow()


def test_equal(source, target):
    m1 = MultipleValueMap(source, target)
    m2 = MultipleValueMap(source, target)

    assert m1 == m2


def test_not_equal(source, target):
    m1 = MultipleValueMap(source, target)
    m2 = MultipleValueMap(source, target, datetime.utcnow())

    assert m1 != m2
