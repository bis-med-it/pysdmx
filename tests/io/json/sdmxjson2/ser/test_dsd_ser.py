from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.dsd import JsonDataStructure
from pysdmx.model import (
    Annotation,
    Code,
    Codelist,
    Component,
    Components,
    Concept,
    DataStructureDefinition,
    DataType,
    Facets,
    ItemReference,
    Role,
)

_BASE = "urn:sdmx:org.sdmx.infomodel."


@pytest.fixture
def dsd():
    f1 = Code("A")
    f2 = Code("M")
    cl = Codelist("CL_FREQ", agency="BIS", version="1.0", items=[f1, f2])
    c1 = Component(
        "FREQ",
        True,
        Role.DIMENSION,
        Concept(
            "FREQ",
            urn=f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).FREQ",
        ),
        DataType.ALPHA,
        Facets(min_length=1, max_length=1),
        local_codes=cl,
    )
    c2 = Component(
        "CUR1",
        True,
        Role.DIMENSION,
        Concept(
            "CUR1",
            urn=f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).CUR1",
        ),
        DataType.ALPHA,
        Facets(min_length=3, max_length=3),
    )
    c3 = Component(
        "CUR2",
        True,
        Role.DIMENSION,
        Concept(
            "CUR2",
            urn=f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).CUR2",
        ),
        DataType.ALPHA,
        Facets(min_length=3, max_length=3),
    )
    c4 = Component(
        "TIME_PERIOD",
        True,
        Role.DIMENSION,
        Concept(
            "TIME_PERIOD",
            urn=f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).TIME_PERIOD",
        ),
        DataType.PERIOD,
    )
    c5 = Component(
        "OBS_VALUE",
        False,
        Role.MEASURE,
        ItemReference("Concept", "Z", "ZZ", "1.0", "OBS_VALUE"),
        DataType.FLOAT,
    )
    c6 = Component(
        "OBS_STATUS",
        True,
        Role.ATTRIBUTE,
        ItemReference("Concept", "Z", "ZZ", "1.0", "OBS_STATUS"),
        DataType.ALPHA,
        Facets(min_length=1, max_length=1),
        attachment_level="O",
    )
    c7 = Component(
        "UNIT",
        True,
        Role.ATTRIBUTE,
        ItemReference("Concept", "Z", "ZZ", "1.0", "UNIT"),
        DataType.ALPHA,
        Facets(min_length=3, max_length=3),
        attachment_level="FREQ,CUR1,CUR2",
    )
    c8 = Component(
        "TITLE",
        False,
        Role.ATTRIBUTE,
        ItemReference("Concept", "Z", "ZZ", "1.0", "TITLE"),
        DataType.STRING,
        Facets(min_length=1, max_length=400),
        attachment_level="FREQ,CUR1,CUR2",
    )
    c9 = Component(
        "UNIT_MULT",
        True,
        Role.ATTRIBUTE,
        ItemReference("Concept", "Z", "ZZ", "1.0", "UNIT_MULT"),
        DataType.SHORT,
        Facets(min_value=0, max_value=9),
        attachment_level="D",
    )
    comps = Components([c1, c2, c3, c4, c5, c6, c7, c8, c9])
    return DataStructureDefinition(
        "EXR",
        name="Exchange rates",
        description="Test DSD for EXR",
        version="1.7",
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        is_external_reference=False,
        agency="BIS",
        annotations=[Annotation(type="test")],
        components=comps,
        evolving_structure=False,
    )


@pytest.fixture
def dsd_no_name():
    c1 = Component(
        "FREQ",
        True,
        Role.DIMENSION,
        Concept(
            "FREQ",
            urn=f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).FREQ",
        ),
        DataType.ALPHA,
        Facets(min_length=1, max_length=1),
    )
    c2 = Component(
        "CUR1",
        True,
        Role.DIMENSION,
        Concept(
            "FREQ",
            urn=f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).CUR1",
        ),
        DataType.ALPHA,
        Facets(min_length=3, max_length=3),
    )
    comps = Components([c1, c2])
    return DataStructureDefinition(
        "EXR",
        agency="BIS",
        components=comps,
    )


def test_dsd(dsd: DataStructureDefinition):
    sjson = JsonDataStructure.from_model(dsd)

    # Check the DSD properties
    assert sjson.agency == "BIS"
    assert sjson.id == dsd.id
    assert sjson.name == dsd.name
    assert sjson.version == "1.7"
    assert sjson.isExternalReference is False
    assert isinstance(sjson.validFrom, datetime)
    assert isinstance(sjson.validTo, datetime)
    assert sjson.description == dsd.description
    assert len(sjson.annotations) == 1
    assert sjson.dataStructureComponents is not None
    assert sjson.evolvingStructure is False

    # Check the dimensions
    assert sjson.dataStructureComponents.dimensionList is not None
    assert len(sjson.dataStructureComponents.dimensionList.dimensions) == 3
    assert (
        sjson.dataStructureComponents.dimensionList.timeDimension is not None
    )
    dim1 = sjson.dataStructureComponents.dimensionList.dimensions[0]
    dim2 = sjson.dataStructureComponents.dimensionList.dimensions[1]
    time = sjson.dataStructureComponents.dimensionList.timeDimension
    assert dim1.id == "FREQ"
    assert (
        dim1.conceptIdentity == f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).FREQ"
    )
    assert dim1.conceptRoles is None
    assert dim1.position is None
    assert (
        dim1.localRepresentation.enumerationFormat.dataType
        == DataType.ALPHA.value
    )
    assert dim1.localRepresentation.enumerationFormat.minLength == 1
    assert dim1.localRepresentation.enumerationFormat.maxLength == 1
    assert (
        dim1.localRepresentation.enumeration
        == f"{_BASE}codelist.Codelist=BIS:CL_FREQ(1.0)"
    )
    assert dim2.id == "CUR1"
    assert (
        dim2.conceptIdentity == f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).CUR1"
    )
    assert dim2.conceptRoles is None
    assert dim2.position is None
    assert dim2.localRepresentation.format.dataType == DataType.ALPHA.value
    assert dim2.localRepresentation.format.minLength == 3
    assert dim2.localRepresentation.format.maxLength == 3
    assert time.id == "TIME_PERIOD"
    assert (
        time.conceptIdentity
        == f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).TIME_PERIOD"
    )
    assert time.conceptRoles is None
    assert time.position is None
    assert time.localRepresentation.format.dataType == DataType.PERIOD.value

    # Check the attributes
    assert sjson.dataStructureComponents.attributeList is not None
    assert len(sjson.dataStructureComponents.attributeList.attributes) == 4
    attr1 = sjson.dataStructureComponents.attributeList.attributes[0]
    attr2 = sjson.dataStructureComponents.attributeList.attributes[2]
    attr3 = sjson.dataStructureComponents.attributeList.attributes[3]
    assert attr1.id == "OBS_STATUS"
    assert (
        attr1.conceptIdentity
        == f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).OBS_STATUS"
    )
    assert attr1.conceptRoles is None
    assert attr1.usage == "mandatory"
    assert attr1.localRepresentation.format.dataType == DataType.ALPHA.value
    assert attr1.localRepresentation.format.minLength == 1
    assert attr1.localRepresentation.format.maxLength == 1
    assert attr1.attributeRelationship.observation == {}
    assert attr2.id == "TITLE"
    assert (
        attr2.conceptIdentity
        == f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).TITLE"
    )
    assert attr2.conceptRoles is None
    assert attr2.usage == "optional"
    assert attr2.localRepresentation.format.dataType == DataType.STRING.value
    assert attr2.localRepresentation.format.minLength == 1
    assert attr2.localRepresentation.format.maxLength == 400
    assert attr2.attributeRelationship.dimensions == ["FREQ", "CUR1", "CUR2"]
    assert attr3.id == "UNIT_MULT"
    assert (
        attr3.conceptIdentity
        == f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).UNIT_MULT"
    )
    assert attr3.conceptRoles is None
    assert attr3.usage == "mandatory"
    assert attr3.localRepresentation.format.dataType == DataType.SHORT.value
    assert attr3.localRepresentation.format.minValue == 0
    assert attr3.localRepresentation.format.maxValue == 9
    assert attr3.attributeRelationship.dataflow == {}

    # Check the measures
    assert sjson.dataStructureComponents.measureList is not None
    assert len(sjson.dataStructureComponents.measureList.measures) == 1
    measure = sjson.dataStructureComponents.measureList.measures[0]
    assert measure.id == "OBS_VALUE"
    assert (
        measure.conceptIdentity
        == f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).OBS_VALUE"
    )
    assert measure.conceptRoles is None
    assert measure.usage == "optional"
    assert measure.localRepresentation.format.dataType == DataType.FLOAT.value


def test_dsd_no_name(dsd_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonDataStructure.from_model(dsd_no_name)
