import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonHierarchyAssociationMessage
from pysdmx.model import HierarchyAssociation


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/hassoc/assoc.json", "rb"
    ) as f:
        return f.read()


def test_ha_deser(body):
    exp = (
        "urn:sdmx:org.sdmx.infomodel.codelist.Hierarchy=BIS:H_OPTION_TYPE(1.0)"
    )

    res = msgspec.json.Decoder(JsonHierarchyAssociationMessage).decode(body)
    has = res.to_model()

    assert len(has) == 1
    ha = has[0]
    assert isinstance(ha, HierarchyAssociation)
    assert isinstance(ha.hierarchy, str)
    assert ha.hierarchy == exp
