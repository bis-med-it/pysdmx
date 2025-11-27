import pytest

from pysdmx.io.json.sdmxjson2.messages.vtl import JsonToVtlMapping
from pysdmx.model.vtl import ToVtlMapping


@pytest.fixture
def to_vtl_mapping():
    return ToVtlMapping(
        to_vtl_sub_space=["sub1", "sub2"],
        method="test_type",
    )


@pytest.fixture
def to_vtl_mapping_no_type():
    return ToVtlMapping(to_vtl_sub_space=["sub1", "sub2"])


def test_to_vtl_mapping(to_vtl_mapping: ToVtlMapping):
    sjson = JsonToVtlMapping.from_model(to_vtl_mapping)

    assert sjson.toVtlSubSpace == {"keys": to_vtl_mapping.to_vtl_sub_space}
    assert sjson.method == to_vtl_mapping.method


def test_to_vtl_mapping_no_type(to_vtl_mapping_no_type: ToVtlMapping):
    sjson = JsonToVtlMapping.from_model(to_vtl_mapping_no_type)

    assert sjson.toVtlSubSpace == {
        "keys": to_vtl_mapping_no_type.to_vtl_sub_space
    }
    assert sjson.method is None
