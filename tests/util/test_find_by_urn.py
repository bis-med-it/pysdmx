import pytest

from pysdmx.errors import NotFound
from pysdmx.io.json.sdmxjson2.messages.code import JsonCodelist
from pysdmx.util import find_by_urn


@pytest.fixture
def codelists():
    cl1 = JsonCodelist("CL_FREQ", "Freq", "BIS")
    cl2 = JsonCodelist("CL_AREA", "Area", "BIS")
    return [cl1, cl2]


def test_no_match(codelists):
    bad = "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=SDMX:CL_FREQ(1.0)"
    with pytest.raises(NotFound):
        find_by_urn(codelists, bad)


def test_match(codelists):
    good = "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:CL_FREQ(1.0)"

    m = find_by_urn(codelists, good)

    assert isinstance(m, JsonCodelist)
    assert m.agency == "BIS"
    assert m.id == "CL_FREQ"
    assert m.version == "1.0"
