import pytest

from pysdmx.io.json.sdmxjson2.messages.vtl import JsonFromVtlMapping
from pysdmx.model.vtl import FromVtlMapping


@pytest.fixture
def from_vtl_mapping():
    return FromVtlMapping(
        from_vtl_sub_space=["super1", "super2"],
        method="test_type",
    )


@pytest.fixture
def from_vtl_mapping_no_type():
    return FromVtlMapping(from_vtl_sub_space=["super1", "super2"])


def test_from_vtl_mapping(from_vtl_mapping: FromVtlMapping):
    sjson = JsonFromVtlMapping.from_model(from_vtl_mapping)

    assert sjson.fromVtlSuperSpace == {
        "keys": from_vtl_mapping.from_vtl_sub_space
    }
    assert sjson.method == from_vtl_mapping.method


def test_from_vtl_mapping_no_type(from_vtl_mapping_no_type: FromVtlMapping):
    sjson = JsonFromVtlMapping.from_model(from_vtl_mapping_no_type)

    assert sjson.fromVtlSuperSpace == {
        "keys": from_vtl_mapping_no_type.from_vtl_sub_space
    }
    assert sjson.method is None
