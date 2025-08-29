from datetime import datetime
from datetime import timezone as tz

from pysdmx.io.json.sdmxjson2.messages.map import (
    JsonComponentMap,
    JsonDatePatternMap,
    JsonFixedValueMap,
    JsonStructureMap,
)
from pysdmx.model import (
    Annotation,
    ComponentMap,
    DatePatternMap,
    FixedValueMap,
    ImplicitComponentMap,
    MultiComponentMap,
    MultiRepresentationMap,
    MultiValueMap,
    RepresentationMap,
    StructureMap,
    ValueMap,
)


def test_sm():
    icm = ImplicitComponentMap("OBS_CONF", "CONF_STATUS")
    vm = ValueMap(source="056", target="BEL")
    rm = RepresentationMap(
        "RM",
        agency="BIS",
        version="1.42",
        source="urn:sdmx:org.sdmx.infomodel.codelist.ValueList=ZZ:AREA(1.0)",
        target="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:AREA(1.0)",
        maps=[vm],
    )
    cm = ComponentMap("COUNTRY", "REF_AREA", rm)
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
    mcm = MultiComponentMap(["COUNTRY", "C2"], ["REF_AREA"], mrm)
    dpm = DatePatternMap(
        source="ACTIVITY_DATE",
        target="TIME_PERIOD",
        pattern="MM/dd/yyyy",
        frequency="M",
        id="DPM_1",
        locale="en",
        pattern_type="fixed",
    )
    fvm = FixedValueMap(target="OBS_CONF", value="R", located_in="source")
    sm = StructureMap(
        "SM",
        name="Some structure map",
        agency="BIS",
        description="A test one",
        version="42.0",
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        source="urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=Z:O(1.0)",
        target="urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=Z:O(2.0)",
        maps=[icm, cm, mcm, dpm, fvm],
    )

    sjson = JsonStructureMap.from_model(sm)

    assert sjson.agency == sm.agency
    assert sjson.id == sm.id
    assert sjson.name == sm.name
    assert sjson.version == sm.version
    assert sjson.isExternalReference == sm.is_external_reference
    assert sjson.validFrom == sm.valid_from
    assert sjson.validTo == sm.valid_to
    assert sjson.description == sm.description
    assert len(sjson.annotations) == 1
    assert sjson.source == sm.source
    assert sjson.target == sm.target
    assert len(sjson.fixedValueMaps) == 1
    assert isinstance(sjson.fixedValueMaps[0], JsonFixedValueMap)
    assert len(sjson.datePatternMaps) == 1
    assert isinstance(sjson.datePatternMaps[0], JsonDatePatternMap)
    assert len(sjson.componentMaps) == 3
    for i in sjson.componentMaps:
        assert isinstance(i, JsonComponentMap)
