from datetime import datetime, timezone
from typing import Iterable, Sized

import msgspec
import pytest

from pysdmx.model.code import Code, Codelist


@pytest.fixture
def id():
    return "id"


@pytest.fixture
def name():
    return "name"


@pytest.fixture
def agency():
    return "5B0"


@pytest.fixture
def sdmx_type():
    return "valuelist"


@pytest.fixture
def desc():
    return "description"


@pytest.fixture
def version():
    return "1.42.0"


@pytest.fixture
def valid_from():
    return datetime(2020, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def valid_to():
    return datetime(2024, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def codes():
    return [
        Code(id="child1", name="Child 1"),
        Code(id="child2", name="Child 2"),
    ]


def test_defaults(id, name, agency):
    cl = Codelist(id=id, name=name, agency=agency)

    assert cl.id == id
    assert cl.name == name
    assert cl.agency == agency
    assert cl.description is None
    assert cl.version == "1.0"
    assert cl.codes is not None
    assert len(cl.codes) == 0
    assert cl.sdmx_type == "codelist"


def test_full_initialization(
    id, name, agency, sdmx_type, desc, version, codes
):
    cl = Codelist(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        items=codes,
        sdmx_type=sdmx_type,
    )

    assert cl.id == id
    assert cl.name == name
    assert cl.agency == agency
    assert cl.description == desc
    assert cl.version == version
    assert cl.codes == codes
    assert len(cl) == 2
    assert len(cl) == len(cl.codes)
    assert cl.sdmx_type == sdmx_type


def test_immutable(id, name, agency):
    cl = Codelist(id=id, name=name, agency=agency)
    with pytest.raises(AttributeError):
        cl.description = "Description"


def test_iterable(id, name, agency):
    codes = [
        Code(id="child1", name="Child 1"),
        Code(id="child2", name="Child 2"),
    ]
    cl = Codelist(id=id, name=name, agency=agency, items=codes)

    assert isinstance(cl, Iterable)
    out = [c.id for c in cl]
    assert len(out) == 2
    assert out == ["child1", "child2"]


def test_sized(id, name, agency):
    cl = Codelist(id=id, name=name, agency=agency)

    assert isinstance(cl, Sized)


def test_get_code(id, name, agency, codes):
    cl = Codelist(id=id, name=name, agency=agency, items=codes)

    resp1 = cl[codes[0].id]
    resp2 = cl["NOT_IN_THE_CODELIST"]

    assert resp1 == codes[0]
    assert codes[0].id in cl
    assert resp2 is None


def test_serialization(
    id, name, agency, sdmx_type, desc, version, codes, valid_from, valid_to
):
    cl = Codelist(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        items=codes,
        sdmx_type=sdmx_type,
        is_partial=True,
        valid_from=valid_from,
        valid_to=valid_to,
    )

    ser = msgspec.msgpack.Encoder().encode(cl)

    out = msgspec.msgpack.Decoder(Codelist).decode(ser)

    assert out == cl


def test_short_urn(id, name, agency, version, codes):
    cl = Codelist(
        id=id, name=name, agency=agency, items=codes, version=version
    )

    assert cl.short_urn == f"Codelist={agency}:{id}({version})"


def test_tostr(id, name, agency, version, codes):
    cl = Codelist(
        id=id, name=name, agency=agency, items=codes, version=version
    )

    s = str(cl)

    assert s == (
        "Codelist(id='id', name='name', version='1.42.0', agency='5B0', "
        "sdmx_type='codelist', items=[2 Codes])"
    )
