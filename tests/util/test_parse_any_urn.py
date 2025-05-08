import pytest

from pysdmx.errors import Invalid
from pysdmx.model import ItemReference, Reference
from pysdmx.util import parse_urn


def test_no_match():
    with pytest.raises(Invalid):
        parse_urn("test")


def test_match_maintainable():
    cl = "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=SDMX:CL_FREQ(1.0)"

    m = parse_urn(cl)

    assert isinstance(m, Reference)
    assert m.sdmx_type == "Codelist"
    assert m.agency == "SDMX"
    assert m.id == "CL_FREQ"
    assert m.version == "1.0"


def test_match_item():
    cl = "urn:sdmx:org.sdmx.infomodel.codelist.Code=SDMX:CL_FREQ(1.0).A"

    m = parse_urn(cl)

    assert isinstance(m, ItemReference)
    assert m.sdmx_type == "Code"
    assert m.agency == "SDMX"
    assert m.id == "CL_FREQ"
    assert m.version == "1.0"
    assert m.item_id == "A"


def test_match_short_maintainable():
    cl = "Codelist=SDMX:CL_FREQ(1.0)"

    m = parse_urn(cl)

    assert isinstance(m, Reference)
    assert m.sdmx_type == "Codelist"
    assert m.agency == "SDMX"
    assert m.id == "CL_FREQ"
    assert m.version == "1.0"


def test_match_short_item():
    cl = "Code=SDMX:CL_FREQ(1.0).A"

    m = parse_urn(cl)

    assert isinstance(m, ItemReference)
    assert m.sdmx_type == "Code"
    assert m.agency == "SDMX"
    assert m.id == "CL_FREQ"
    assert m.version == "1.0"
    assert m.item_id == "A"
