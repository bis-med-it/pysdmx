from pysdmx.io.json.sdmxjson2.messages.map import JsonComponentMap
from pysdmx.model import (
    ComponentMap,
    ImplicitComponentMap,
    MultiComponentMap,
    MultiRepresentationMap,
    MultiValueMap,
    RepresentationMap,
    ValueMap,
)


def test_icm():
    icm = ImplicitComponentMap("OBS_CONF", "CONF_STATUS")

    sjson = JsonComponentMap.from_model(icm)

    assert sjson.source == ["OBS_CONF"]
    assert sjson.target == ["CONF_STATUS"]
    assert sjson.representationMap is None


def test_cm():
    vm = ValueMap(source="056", target="BEL")
    rm = RepresentationMap(
        "RM",
        agency="BIS",
        version="1.42",
        source="urn:sdmx:org.sdmx.infomodel.codelist.ValueList=ZZ:AREA(1.0)",
        target="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:AREA(1.0)",
        maps=[vm],
    )
    icm = ComponentMap("OBS_CONF", "CONF_STATUS", rm)

    sjson = JsonComponentMap.from_model(icm)

    assert sjson.source == ["OBS_CONF"]
    assert sjson.target == ["CONF_STATUS"]
    assert sjson.representationMap == (
        "urn:sdmx:org.sdmx.infomodel.structuremapping.RepresentationMap="
        "BIS:RM(1.42)"
    )


def test_mcm():
    mvm = MultiValueMap(source=["056", "BEL"], target=["BE"])
    mrm = MultiRepresentationMap(
        "MRM",
        name="Some map",
        agency="BIS",
        version="1.7",
        source=["String", "String"],
        target=["urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:AREA(1.0)"],
        maps=[mvm],
    )
    icm = ComponentMap("OBS_CONF", "CONF_STATUS", mrm)

    sjson = JsonComponentMap.from_model(icm)

    assert sjson.source == ["OBS_CONF"]
    assert sjson.target == ["CONF_STATUS"]
    assert sjson.representationMap == (
        "urn:sdmx:org.sdmx.infomodel.structuremapping.RepresentationMap="
        "BIS:MRM(1.7)"
    )
