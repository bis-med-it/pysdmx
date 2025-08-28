from datetime import datetime, timezone as tz

from pysdmx.io.json.sdmxjson2.messages.map import (
    JsonAnnotation,
    JsonRepresentationMap,
)
from pysdmx.model import (
    Annotation,
    MultiValueMap,
    MultiRepresentationMap,
    RepresentationMap,
    ValueMap,
)


def test_rm():
    vm = ValueMap(source="056", target="BEL")
    rm = RepresentationMap(
        "RM",
        name="Some map",
        agency="BIS",
        description="A test one",
        version="1.42",
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        source="urn:sdmx:org.sdmx.infomodel.codelist.ValueList=ZZ:AREA(1.0)",
        target="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:AREA(1.0)",
        maps=[vm],
    )

    sjson = JsonRepresentationMap.from_model(rm)

    assert sjson.agency == rm.agency
    assert sjson.id == rm.id
    assert sjson.name == rm.name
    assert sjson.version == rm.version
    assert sjson.isExternalReference == rm.is_external_reference
    assert sjson.validFrom == rm.valid_from
    assert sjson.validTo == rm.valid_to
    assert sjson.description == rm.description
    assert len(sjson.annotations) == 1
    assert sjson.source == [{"valuelist": rm.source}]
    assert sjson.target == [{"codelist": rm.target}]
    assert len(sjson.representationMappings) == 1


def test_mrm():
    mvm = MultiValueMap(source=["056", "BEL"], target=["BE"])
    mrm = MultiRepresentationMap(
        "MRM",
        name="Some map",
        agency="BIS",
        description="A test one",
        version="1.42",
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        source=["String", "String"],
        target=["urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:AREA(1.0)"],
        maps=[mvm],
    )

    sjson = JsonRepresentationMap.from_model(mrm)

    assert sjson.source == [{"dataType": "String"}, {"dataType": "String"}]
    assert sjson.target == [{"codelist": mrm.target[0]}]
    assert len(sjson.representationMappings) == 1
