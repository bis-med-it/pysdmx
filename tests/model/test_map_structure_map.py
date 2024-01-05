import pytest

from pysdmx.model import ImplicitComponentMap, StructureMap


@pytest.fixture()
def mappings():
    m1 = ImplicitComponentMap("OBS_CONF", "CONF_STATUS")
    m2 = ImplicitComponentMap("OBS_STATUS", "OBS_STATUS")
    return [m1, m2]


def test_full_initialization(mappings):
    sm = StructureMap(implicit_maps=mappings)

    assert len(sm.implicit_maps) == 2
    assert sm.implicit_maps == mappings
    assert not sm.component_maps
    assert not sm.date_maps
    assert not sm.fixed_value_maps
    assert not sm.multiple_component_maps


def test_immutable(mappings):
    sm = StructureMap(mappings)
    with pytest.raises(AttributeError):
        sm.fixed_value_maps = []
