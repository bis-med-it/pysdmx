import pytest

from pysdmx.errors import Invalid
from pysdmx.model import Reference
from pysdmx.util import parse_maintainable_urn


def test_no_match():
    with pytest.raises(Invalid):
        parse_maintainable_urn("test")


def test_match():
    cl = "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=SDMX:CL_FREQ(1.0)"

    m = parse_maintainable_urn(cl)

    assert isinstance(m, Reference)
    assert m.sdmx_type == "Codelist"
    assert m.agency == "SDMX"
    assert m.id == "CL_FREQ"
    assert m.version == "1.0"
