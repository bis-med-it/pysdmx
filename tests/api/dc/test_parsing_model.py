from datetime import datetime

from pysdmx.api.dc.query._model import Operator
from pysdmx.api.dc.query._parsing_model import (
    _Boolean,
    _DateTime,
    _Field,
    _Filter,
    _Number,
    _String,
)


def test_field():
    name = "REF_AREA"

    fld = _Field(name)

    assert fld.name == name


def test_number_int():
    v = 42

    n = _Number(v)

    assert n.value == v


def test_number_float():
    v = 42.42

    n = _Number(v)

    assert n.value == v


def test_string():
    v = "A"

    s = _String(v)

    assert s.value == v


def test_boolean():
    v = True

    s = _Boolean(v)

    assert s.value == v


def test_datetime():
    v = datetime.now()

    s = _DateTime(v)

    assert s.value == v


def test_filter():
    fld = "REF_AREA"
    op = Operator.EQUALS
    val = "UY"

    flt = _Filter(fld, op, val)

    assert flt.field == fld
    assert flt.operator == op
    assert flt.value == val
