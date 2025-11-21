from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.msd import JsonMetadataStructure
from pysdmx.model import (
    Annotation,
    ArrayBoundaries,
    Code,
    Codelist,
    Concept,
    DataType,
    Facets,
    MetadataComponent,
    MetadataStructure,
)

_BASE = "urn:sdmx:org.sdmx.infomodel."


@pytest.fixture
def msd():
    f1 = Code("A")
    f2 = Code("M")
    cl = Codelist("CL_FREQ", agency="BIS", version="1.0", items=[f1, f2])
    c1 = MetadataComponent(
        "FREQ",
        concept=Concept(
            "FREQ",
            urn=f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).FREQ",
        ),
        local_dtype=DataType.ALPHA,
        local_facets=Facets(min_length=1, max_length=1),
        local_codes=cl,
        local_enum_ref=f"{_BASE}codelist.Codelist=BIS:CL_FREQ(1.0)",
    )
    c2 = MetadataComponent(
        "C2",
        concept=Concept(
            "C2",
            urn=f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).C2",
        ),
        local_dtype=DataType.INTEGER,
        array_def=ArrayBoundaries(1, 42),
    )
    return MetadataStructure(
        "EXR",
        name="Exchange rates",
        description="Test DSD for EXR",
        version="1.7",
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        is_external_reference=False,
        agency="BIS",
        annotations=[Annotation(type="test")],
        components=[c1, c2],
    )


@pytest.fixture
def msd_no_name():
    c1 = MetadataComponent(
        "FREQ",
        concept=Concept(
            "FREQ",
            urn=f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).FREQ",
        ),
        local_dtype=DataType.ALPHA,
        local_facets=Facets(min_length=1, max_length=1),
    )
    return MetadataStructure("EXR", agency="BIS", components=[c1])


def test_msd(msd: MetadataStructure):
    sjson = JsonMetadataStructure.from_model(msd)

    # Check the DSD properties
    assert sjson.agency == "BIS"
    assert sjson.id == msd.id
    assert sjson.name == msd.name
    assert sjson.version == "1.7"
    assert sjson.isExternalReference is False
    assert isinstance(sjson.validFrom, datetime)
    assert isinstance(sjson.validTo, datetime)
    assert sjson.description == msd.description
    assert len(sjson.annotations) == 1

    # Check the components
    msc = sjson.metadataStructureComponents
    assert msc is not None
    assert msc.metadataAttributeList is not None
    assert len(msc.metadataAttributeList.metadataAttributes) == 2

    cmp1 = msc.metadataAttributeList.metadataAttributes[0]
    assert cmp1.id == "FREQ"
    assert (
        cmp1.conceptIdentity == f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).FREQ"
    )
    assert (
        cmp1.localRepresentation.enumerationFormat.dataType
        == DataType.ALPHA.value
    )
    assert cmp1.localRepresentation.enumerationFormat.minLength == 1
    assert cmp1.localRepresentation.enumerationFormat.maxLength == 1
    assert (
        cmp1.localRepresentation.enumeration
        == f"{_BASE}codelist.Codelist=BIS:CL_FREQ(1.0)"
    )
    assert cmp1.isPresentational is False
    assert cmp1.minOccurs == 0
    assert cmp1.maxOccurs == 1

    cmp2 = msc.metadataAttributeList.metadataAttributes[1]
    assert cmp2.id == "C2"
    assert cmp2.conceptIdentity == f"{_BASE}conceptscheme.Concept=Z:ZZ(1.0).C2"
    assert cmp2.localRepresentation.format.dataType == DataType.INTEGER.value
    assert cmp2.localRepresentation.enumerationFormat is None
    assert cmp2.localRepresentation.enumeration is None
    assert cmp2.isPresentational is False
    assert cmp2.minOccurs == 1
    assert cmp2.maxOccurs == 42


def test_msd_no_name(msd_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonMetadataStructure.from_model(msd_no_name)
