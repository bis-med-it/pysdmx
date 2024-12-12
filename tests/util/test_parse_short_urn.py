import pytest

from pysdmx.errors import Invalid
from pysdmx.util import parse_short_urn, Reference


def test_no_match():
    with pytest.raises(Invalid):
        parse_short_urn("test")


def test_match():
    cl = "Codelist=SDMX:CL_FREQ(1.0)"

    m = parse_short_urn(cl)

    assert isinstance(m, Reference)
    assert m.sdmx_type == "Codelist"
    assert m.agency == "SDMX"
    assert m.id == "CL_FREQ"
    assert m.version == "1.0"