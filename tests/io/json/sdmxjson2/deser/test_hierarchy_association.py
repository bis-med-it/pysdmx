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


@pytest.fixture
def body_stub():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/hassoc/assoc_stubs.json", "rb"
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


def test_ha_deser_stub(body_stub):
    res = msgspec.json.Decoder(JsonHierarchyAssociationMessage).decode(
        body_stub
    )

    has = res.to_model()

    assert len(has) == 1
    ha = has[0]
    assert isinstance(ha, HierarchyAssociation)
    assert ha.agency == "BIS.TEST"
    assert ha.id == "HA_TEST"
    assert ha.version == "1.0"
    assert ha.name == "Test Hierarchy Association for MEDAL 2.0"
    assert ha.description is None
    assert ha.is_external_reference is True
    assert ha.hierarchy is None
    assert ha.context_ref is None
    assert ha.component_ref is None
