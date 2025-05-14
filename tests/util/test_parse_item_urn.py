import pytest

from pysdmx.errors import Invalid
from pysdmx.model import ItemReference
from pysdmx.util import parse_item_urn


def test_no_match():
    with pytest.raises(Invalid):
        parse_item_urn("test")


def test_match():
    cl = "urn:sdmx:org.sdmx.infomodel.codelist.Code=SDMX:CL_FREQ(1.0).A"

    m = parse_item_urn(cl)

    assert isinstance(m, ItemReference)
    assert m.sdmx_type == "Code"
    assert m.agency == "SDMX"
    assert m.id == "CL_FREQ"
    assert m.version == "1.0"
    assert m.item_id == "A"


def test_match_nested():
    cl = (
        "urn:sdmx:org.sdmx.infomodel.categoryscheme.Category="
        "TEST:TESTCS(1.42).TOP.SUB"
    )

    m = parse_item_urn(cl)

    assert isinstance(m, ItemReference)
    assert m.sdmx_type == "Category"
    assert m.agency == "TEST"
    assert m.id == "TESTCS"
    assert m.version == "1.42"
    assert m.item_id == "TOP.SUB"
