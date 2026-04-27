from pysdmx.model import Reference
from pysdmx.util import parse_flow_urn


def test_match_short_dataflow():
    df = "BIS:CBS(1.0)"

    m = parse_flow_urn(df)

    assert isinstance(m, Reference)
    assert m.sdmx_type == "Dataflow"
    assert m.agency == "BIS"
    assert m.id == "CBS"
    assert m.version == "1.0"
