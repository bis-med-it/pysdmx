import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonAgencyMessage
from pysdmx.model import Agency, AgencyScheme


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/orgs/agencies_flows.json", "rb"
    ) as f:
        return f.read()


def test_agencies_with_flows(body):
    res = msgspec.json.Decoder(JsonAgencyMessage).decode(body)
    schemes = res.to_model()

    assert len(schemes) == 1
    scheme = schemes[0]
    assert isinstance(scheme, AgencyScheme)
    assert len(scheme) == 2
    for agency in scheme:
        assert isinstance(agency, Agency)
        if agency.id == "BIS.DST":
            assert len(agency.dataflows) == 0
        else:
            assert agency.id == "BIS.CMP"
            assert len(agency.dataflows) == 2
            for flow in agency.dataflows:
                assert flow.id in ["TEST_ARRAYS_DF", "TEST_ARRAYS_DF_1"]
