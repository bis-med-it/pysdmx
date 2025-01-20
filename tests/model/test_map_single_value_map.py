import re
from datetime import datetime, timedelta, timezone

import pytest

from pysdmx.model import ValueMap


@pytest.fixture
def source():
    return "UY"


@pytest.fixture
def target():
    return "URY"


def test_default_instantiation(source, target):
    m = ValueMap(source=source, target=target)

    assert m.source == source
    assert m.target == target
    assert m.valid_from is None
    assert m.valid_to is None


def test_full_instantiation(source, target):
    vf = datetime.now(timezone.utc) - timedelta(days=1)
    vt = datetime.now(timezone.utc)
    m = ValueMap(source=source, target=target, valid_from=vf, valid_to=vt)

    assert m.source == source
    assert m.target == target
    assert m.valid_from == vf
    assert m.valid_to == vt


def test_immutable(source, target):
    m = ValueMap(source=source, target=target)
    with pytest.raises(AttributeError):
        m.valid_from = datetime.now(timezone.utc)


def test_equal(source, target):
    m1 = ValueMap(source=source, target=target)
    m2 = ValueMap(source=source, target=target)

    assert m1 == m2


def test_not_equal(source, target):
    m1 = ValueMap(source=source, target=target)
    m2 = ValueMap(
        source=source, target=target, valid_from=datetime.now(timezone.utc)
    )

    assert m1 != m2


def test_regex(target):
    regex = r"regex:^[\d]{1}$"
    vm = ValueMap(source=regex, target=target)
    assert vm.source == regex
    assert vm.typed_source == re.compile(r"^[\d]{1}$")


def test_no_regex(target):
    value = "AR"
    vm = ValueMap(source=value, target=target)
    assert vm.source == value
    assert vm.typed_source == value
