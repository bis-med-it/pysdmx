import pytest

from pysdmx.errors import Invalid
from pysdmx.util import ItemReference, parse_item_urn


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
