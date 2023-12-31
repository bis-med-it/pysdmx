import pytest

from pysdmx.errors import NotFound
from pysdmx.util import parse_urn, Reference


def test_no_match():
    with pytest.raises(NotFound):
        parse_urn("test")


def test_match():
    cl = "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=SDMX:CL_FREQ(1.0)"

    m = parse_urn(cl)

    assert isinstance(m, Reference)
    assert m.sdmx_type == "Codelist"
    assert m.agency == "SDMX"
    assert m.id == "CL_FREQ"
    assert m.version == "1.0"
