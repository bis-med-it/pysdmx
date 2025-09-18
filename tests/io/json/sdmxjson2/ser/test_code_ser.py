from datetime import datetime, timedelta
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.code import JsonCode
from pysdmx.model import Code


@pytest.fixture
def code():
    return Code("A", name="Annual", description="Description")


@pytest.fixture
def code_vf():
    return Code("A", name="Annual", valid_from=datetime.now(tz.utc))


@pytest.fixture
def code_vt():
    return Code("A", name="Annual", valid_to=datetime.now(tz.utc))


@pytest.fixture
def code_vf_vt():
    vf = datetime.now(tz.utc)
    vt = vf + timedelta(hours=1)
    return Code("A", name="Annual", valid_from=vf, valid_to=vt)


@pytest.fixture
def code_no_name():
    return Code("A")


def test_code(code: Code):
    sjson = JsonCode.from_model(code)

    assert sjson.id == code.id
    assert sjson.name == code.name
    assert sjson.description == code.description
    assert sjson.parent is None
    assert len(sjson.annotations) == 0


def test_code_vf(code_vf: Code):
    sjson = JsonCode.from_model(code_vf)

    assert sjson.id == code_vf.id
    assert sjson.name == code_vf.name
    assert sjson.description is None
    assert sjson.parent is None
    assert len(sjson.annotations) == 1
    a = sjson.annotations[0]
    assert a.type == "FR_VALIDITY_PERIOD"
    vf = datetime.strftime(code_vf.valid_from, "%Y-%m-%dT%H:%M:%S%z")
    assert a.title == f"{vf}/"


def test_code_vt(code_vt: Code):
    sjson = JsonCode.from_model(code_vt)

    assert sjson.id == code_vt.id
    assert sjson.name == code_vt.name
    assert sjson.description is None
    assert sjson.parent is None
    assert len(sjson.annotations) == 1
    a = sjson.annotations[0]
    assert a.type == "FR_VALIDITY_PERIOD"
    vt = datetime.strftime(code_vt.valid_to, "%Y-%m-%dT%H:%M:%S%z")
    assert a.title == f"/{vt}"


def test_code_vf_vt(code_vf_vt: Code):
    sjson = JsonCode.from_model(code_vf_vt)

    assert sjson.id == code_vf_vt.id
    assert sjson.name == code_vf_vt.name
    assert sjson.description is None
    assert sjson.parent is None
    assert len(sjson.annotations) == 1
    a = sjson.annotations[0]
    assert a.type == "FR_VALIDITY_PERIOD"
    vf = datetime.strftime(code_vf_vt.valid_from, "%Y-%m-%dT%H:%M:%S%z")
    vt = datetime.strftime(code_vf_vt.valid_to, "%Y-%m-%dT%H:%M:%S%z")
    assert a.title == f"{vf}/{vt}"


def test_code_no_name(code_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonCode.from_model(code_no_name)
