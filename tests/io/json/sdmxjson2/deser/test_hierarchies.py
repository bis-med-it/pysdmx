import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonHierarchiesMessage
from pysdmx.model import Hierarchy


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/hier/hier.json", "rb"
    ) as f:
        return f.read()


def test_hierarchies_deser(body):
    res = msgspec.json.Decoder(JsonHierarchiesMessage).decode(body)
    hierarchies = res.to_model()

    assert len(hierarchies) == 2
    for h in hierarchies:
        assert isinstance(h, Hierarchy)
        assert h.version in ["1.0", "1.42"]


def test_hierarchical_code_relative_validity_keeps_its_timezone():
    from datetime import datetime, timedelta, timezone

    from pysdmx.io.json.sdmxjson2.messages.code import JsonHierarchicalCode

    cet = timezone(timedelta(hours=1))
    hc = JsonHierarchicalCode(
        id="A",
        code="urn:sdmx:org.sdmx.infomodel.codelist.Code=BIS:CL_FREQ(1.0).A",
        validFrom=datetime(2021, 1, 1, tzinfo=cet),
        validTo=datetime(2021, 12, 31),
    )

    out = hc.to_model([])

    assert out.rel_valid_from.isoformat() == "2021-01-01T00:00:00+01:00"
    assert out.rel_valid_to == datetime(2021, 12, 31, tzinfo=timezone.utc)
