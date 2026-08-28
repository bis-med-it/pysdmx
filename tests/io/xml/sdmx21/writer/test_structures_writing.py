import copy
import os
from datetime import datetime
from pathlib import Path

import pytest
from msgspec.structs import replace

from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io import read_sdmx, write_sdmx
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.xml.__tokens import CON
from pysdmx.io.xml.sdmx21.reader.structure import read
from pysdmx.io.xml.sdmx21.writer.error import write as write_err
from pysdmx.io.xml.sdmx21.writer.structure import write
from pysdmx.model import (
    Agency,
    AgencyScheme,
    AvailabilityConstraint,
    Categorisation,
    Category,
    CategoryScheme,
    Code,
    Codelist,
    Concept,
    ConceptScheme,
    ConstraintAttachment,
    Contact,
    CubeKeyValue,
    CubeRegion,
    CubeTimeRange,
    CubeValue,
    CustomTypeScheme,
    DataConstraint,
    DataConsumer,
    DataConsumerScheme,
    DataKey,
    DataKeyValue,
    DataProvider,
    DataProviderScheme,
    Facets,
    FromVtlMapping,
    HierarchicalCode,
    Hierarchy,
    KeySet,
    LevelType,
    Metadataflow,
    MetadataProvider,
    MetadataProviderScheme,
    MetadataProvisionAgreement,
    MetadataStructure,
    NamePersonalisationScheme,
    Ruleset,
    RulesetScheme,
    TimePeriodBoundary,
    ToVtlMapping,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
    VtlDataflowMapping,
    VtlMappingScheme,
)
from pysdmx.model.__base import (
    Annotation,
    DataflowRef,
    ItemReference,
    Organisation,
    Reference,
)
from pysdmx.model.dataflow import (
    Component,
    Components,
    Dataflow,
    DataStructureDefinition,
    Group,
    ProvisionAgreement,
    Role,
)
from pysdmx.model.dataset import ActionType
from pysdmx.model.message import Header

TEST_CS_URN = (
    "urn:sdmx:org.sdmx.infomodel.conceptscheme.ConceptScheme=BIS:CS_FREQ(1.0)"
)


@pytest.fixture
def codelist_sample():
    base_path = Path(__file__).parent / "samples" / "codelist.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def concept_sample():
    base_path = Path(__file__).parent / "samples" / "concept.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def empty_sample():
    base_path = Path(__file__).parent / "samples" / "empty.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def read_write_sample():
    base_path = Path(__file__).parent / "samples" / "read_write_sample.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def vtl_complete():
    base_path = Path(__file__).parent / "samples" / "vtl_complete.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def datastructure_group_read():
    base_path = (
        Path(__file__).parent / "samples" / "read_datastructure_group.xml"
    )
    with open(base_path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def datastructure_group_write():
    base_path = (
        Path(__file__).parent / "samples" / "write_datastructure_group.xml"
    )
    with open(base_path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def bis_sample():
    base_path = Path(__file__).parent / "samples" / "bis_der.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def estat_sample():
    base_path = Path(__file__).parent / "samples" / "estat_sample.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def groups_sample():
    base_path = Path(__file__).parent / "samples" / "del_groups.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def header():
    return Header(
        id="ID",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
    )


@pytest.fixture
def complete_header():
    return Header(
        id="ID",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        sender=Organisation(
            id="ZZZ",
        ),
        receiver=Organisation(
            id="Not_Supplied",
        ),
        source="PySDMX",
    )


@pytest.fixture
def hierarchy_with_levels():
    return Hierarchy(
        id="H1",
        name="Hierarchy 1",
        agency="BIS",
        version="1.0",
        has_formal_levels=True,
        level=LevelType(
            id="0",
            name="Division",
            level=LevelType(id="1", name="Group"),
        ),
        codes=(
            HierarchicalCode(
                id="A",
                urn=(
                    "urn:sdmx:org.sdmx.infomodel.codelist."
                    "Code=BIS:CL_FREQ(1.0).A"
                ),
                level="1",
                codes=(
                    HierarchicalCode(
                        id="A1",
                        urn=(
                            "urn:sdmx:org.sdmx.infomodel.codelist."
                            "Code=BIS:CL_FREQ(1.0).M"
                        ),
                    ),
                ),
            ),
        ),
    )


def test_hierarchy_21_round_trip(complete_header, hierarchy_with_levels):
    result = write(
        [hierarchy_with_levels], header=complete_header, prettyprint=True
    )
    assert "<str:HierarchicalCodelists>" in result
    assert "<str:HierarchicalCodelist " in result
    assert 'leveled="true"' in result
    re_read = read_sdmx(result, validate=True).structures[0]
    assert re_read == hierarchy_with_levels


def test_org_schemes_21_round_trip(complete_header):
    agency_scheme = AgencyScheme(
        agency="SDMX",
        items=[Agency(id="SDMX", name="SDMX")],
    )
    provider_scheme = DataProviderScheme(
        agency="BIS",
        items=[DataProvider(id="5B0", name="BIS")],
    )
    consumer_scheme = DataConsumerScheme(
        agency="SDMX",
        items=[DataConsumer(id="ECB", name="European Central Bank")],
    )
    content = [agency_scheme, provider_scheme, consumer_scheme]
    result = write(content, header=complete_header, prettyprint=True)
    # In SDMX-ML 2.1 all organisation schemes share a single container.
    assert result.count("<str:OrganisationSchemes>") == 1
    assert "<str:DataProviderScheme " in result
    assert "<str:DataConsumerScheme " in result
    re_read = read_sdmx(result, validate=True).structures
    by_type = {type(s): s for s in re_read}
    assert by_type[AgencyScheme] == agency_scheme
    assert by_type[DataProviderScheme] == provider_scheme
    assert by_type[DataConsumerScheme] == consumer_scheme


def test_provider_scheme_contacts_21_round_trip(complete_header):
    provider_scheme = DataProviderScheme(
        agency="BIS",
        items=[
            DataProvider(
                id="5B0",
                name="BIS",
                contacts=[
                    Contact(
                        name="Stats",
                        department="STATS",
                        role="Provider",
                        emails=["stats@bis.org"],
                        uris=["http://www.bis.org"],
                    )
                ],
            )
        ],
    )
    result = write([provider_scheme], header=complete_header, prettyprint=True)
    assert "<str:Contact>" in result
    re_read = read_sdmx(result, validate=True).structures[0]
    assert re_read == provider_scheme


def test_provider_scheme_enrichment_21_round_trip(complete_header):
    provider_scheme = DataProviderScheme(
        agency="BIS",
        items=[
            DataProvider(
                id="TEST",
                name="Test Organisation",
                dataflows=[DataflowRef(id="DF1", agency="BIS", version="1.0")],
            )
        ],
    )
    # An AgencyScheme shares the OrganisationSchemes wrapper but must be
    # left untouched by the dataflow enrichment.
    agency_scheme = AgencyScheme(
        agency="SDMX",
        items=[Agency(id="SDMX", name="SDMX")],
    )
    provision_agreement = ProvisionAgreement(
        id="PA1",
        name="PA1",
        agency="BIS",
        version="1.0",
        dataflow="Dataflow=BIS:DF1(1.0)",
        provider="DataProvider=BIS:DATA_PROVIDERS(1.0).TEST",
    )
    content = [agency_scheme, provider_scheme, provision_agreement]
    result = write(content, header=complete_header, prettyprint=True)
    re_read = read_sdmx(result, validate=True).structures
    scheme = next(s for s in re_read if isinstance(s, DataProviderScheme))
    # The dataflows are re-derived from the provision agreement on read.
    assert scheme.items[0].dataflows == [
        DataflowRef(id="DF1", agency="BIS", version="1.0")
    ]
    assert scheme == provider_scheme
    # The agency scheme is preserved unchanged.
    re_agency = next(s for s in re_read if isinstance(s, AgencyScheme))
    assert re_agency == agency_scheme


def test_unsupported_type_raises_invalid(header):
    # MetadataProviderScheme has no SDMX-ML 2.1 representation.
    mps = MetadataProviderScheme(
        agency="MD",
        name="MD Metadata Provider Scheme",
        items=[MetadataProvider(id="MP1", name="Metadata Provider 1")],
    )
    with pytest.raises(Invalid, match="MetadataProviderScheme"):
        write([mps], header=header, prettyprint=True)


def test_hierarchy_21_no_levels(complete_header):
    hierarchy = Hierarchy(
        id="H3",
        name="Flat hierarchy",
        agency="BIS",
        version="1.0",
        codes=(
            HierarchicalCode(
                id="A",
                urn=(
                    "urn:sdmx:org.sdmx.infomodel.codelist."
                    "Code=BIS:CL_FREQ(1.0).A"
                ),
            ),
        ),
    )
    result = write([hierarchy], header=complete_header, prettyprint=True)
    assert 'leveled="false"' in result
    re_read = read_sdmx(result, validate=True).structures[0]
    assert re_read == hierarchy


def test_hierarchy_21_metadata_round_trip(complete_header):
    hierarchy = Hierarchy(
        id="H1",
        name="Hierarchy 1",
        description="My description",
        agency="BIS",
        version="1.0",
        valid_from=datetime(2021, 1, 1),
        valid_to=datetime(2021, 12, 31),
        annotations=(Annotation(id="AN1", title="anno"),),
        codes=(
            HierarchicalCode(
                id="A",
                urn=(
                    "urn:sdmx:org.sdmx.infomodel.codelist."
                    "Code=BIS:CL_FREQ(1.0).A"
                ),
            ),
        ),
    )
    result = write([hierarchy], header=complete_header, prettyprint=True)
    re_read = read_sdmx(result, validate=True).structures[0]
    assert re_read == hierarchy


def test_hierarchy_21_name_with_apostrophe(complete_header):
    hierarchy = Hierarchy(
        id="H4",
        name="Côte d'Ivoire groups",
        agency="BIS",
        version="1.0",
        codes=[
            HierarchicalCode(
                id="A",
                urn=(
                    "urn:sdmx:org.sdmx.infomodel.codelist."
                    "Code=BIS:CL_FREQ(1.0).A"
                ),
            ),
        ],
    )
    result = write([hierarchy], header=complete_header, prettyprint=True)
    re_read = read_sdmx(result, validate=True).structures[0]
    assert re_read.name == "Côte d'Ivoire groups"


@pytest.fixture
def category_scheme_nested():
    return CategoryScheme(
        id="CS1",
        name="Category Scheme 1",
        description="A scheme",
        agency="BIS",
        version="1.0",
        items=(
            Category(
                id="TOP",
                name="Top",
                categories=(
                    Category(
                        id="MID",
                        name="Middle",
                        categories=(Category(id="LEAF", name="Leaf"),),
                    ),
                ),
            ),
            Category(id="OTHER", name="Other"),
        ),
    )


def test_category_scheme_21_round_trip(
    complete_header, category_scheme_nested
):
    result = write(
        [category_scheme_nested], header=complete_header, prettyprint=True
    )
    assert "<str:CategorySchemes>" in result
    assert "<str:CategoryScheme " in result
    assert "<str:Category " in result
    re_read = read_sdmx(result, validate=True).structures[0]
    assert re_read == category_scheme_nested


def test_category_scheme_21_name_with_apostrophe(complete_header):
    cs = CategoryScheme(
        id="CS2",
        name="Schemes",
        agency="BIS",
        version="1.0",
        items=(Category(id="C", name="Côte d'Ivoire"),),
    )
    result = write([cs], header=complete_header, prettyprint=True)
    re_read = read_sdmx(result, validate=True).structures[0]
    assert re_read == cs
    assert re_read.items[0].name == "Côte d'Ivoire"


def test_categorisation_21_round_trip(complete_header):
    categorisation = Categorisation(
        id="CAT1",
        name="Categorisation 1",
        agency="BIS",
        version="1.0",
        source=(
            "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:DF1(1.0)"
        ),
        target=(
            "urn:sdmx:org.sdmx.infomodel.categoryscheme."
            "Category=BIS:CS1(1.0).TOP.MID.LEAF"
        ),
    )
    result = write([categorisation], header=complete_header, prettyprint=True)
    assert "<str:Categorisations>" in result
    assert "<str:Categorisation " in result
    assert "<str:Source>" in result
    assert "<str:Target>" in result
    assert "isPartial" not in result
    re_read = read_sdmx(result, validate=True).structures[0]
    # Full URNs round-trip unchanged.
    assert re_read == categorisation


def test_category_scheme_21_enrichment_round_trip(complete_header):
    cs = CategoryScheme(
        id="CS1",
        name="Category Scheme 1",
        agency="BIS",
        version="1.0",
        items=[Category(id="TOP", name="Top")],
    )
    dataflow = Dataflow(
        id="DF1",
        name="Dataflow 1",
        agency="BIS",
        version="1.0",
        structure="DataStructure=BIS:DSD1(1.0)",
    )
    categorisation = Categorisation(
        id="CAT1",
        name="Categorisation 1",
        agency="BIS",
        version="1.0",
        source=(
            "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:DF1(1.0)"
        ),
        target=(
            "urn:sdmx:org.sdmx.infomodel.categoryscheme."
            "Category=BIS:CS1(1.0).TOP"
        ),
    )
    result = write(
        [cs, dataflow, categorisation],
        header=complete_header,
        prettyprint=True,
    )
    # The dataflow must NOT be inlined inside the category scheme: it is
    # re-derived from the Categorisation on read.
    re_read = read_sdmx(result, validate=True).structures
    re_cs = next(s for s in re_read if isinstance(s, CategoryScheme))
    top = re_cs["TOP"]
    assert len(top.dataflows) == 1
    assert isinstance(top.dataflows[0], DataflowRef)
    assert top.dataflows[0].agency == "BIS"
    assert top.dataflows[0].id == "DF1"
    assert top.dataflows[0].version == "1.0"
    assert top.dataflows[0].name == "Dataflow 1"


def test_category_annotations_21_round_trip(complete_header):
    # Annotations on both a top-level and a nested category must survive
    # a write/read cycle, including when the category is enriched.
    cs = CategoryScheme(
        id="CS1",
        name="Category Scheme 1",
        agency="BIS",
        version="1.0",
        items=(
            Category(
                id="TOP",
                name="Top",
                annotations=(Annotation(id="A_TOP", title="top anno"),),
                categories=(
                    Category(
                        id="LEAF",
                        name="Leaf",
                        annotations=(
                            Annotation(id="A_LEAF", title="leaf anno"),
                        ),
                    ),
                ),
            ),
        ),
    )
    categorisation = Categorisation(
        id="CAT1",
        name="Categorisation 1",
        agency="BIS",
        version="1.0",
        source=(
            "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:CL_FREQ(1.0)"
        ),
        target=(
            "urn:sdmx:org.sdmx.infomodel.categoryscheme."
            "Category=BIS:CS1(1.0).TOP.LEAF"
        ),
    )
    result = write(
        [cs, categorisation], header=complete_header, prettyprint=True
    )
    re_read = read_sdmx(result, validate=True).structures
    re_cs = next(s for s in re_read if isinstance(s, CategoryScheme))
    top = re_cs["TOP"]
    assert top.annotations == (Annotation(id="A_TOP", title="top anno"),)
    leaf = re_cs["TOP.LEAF"]
    assert leaf.annotations == (Annotation(id="A_LEAF", title="leaf anno"),)


def test_category_multiple_categorisations_same_category_21(complete_header):
    # Two categorisations targeting the SAME category must accumulate
    # both dataflows in that category's dataflows.
    cs = CategoryScheme(
        id="CS1",
        name="Category Scheme 1",
        agency="BIS",
        version="1.0",
        items=(Category(id="TOP", name="Top"),),
    )
    df1 = Dataflow(
        id="DF1",
        name="Dataflow 1",
        agency="BIS",
        version="1.0",
        structure="DataStructure=BIS:DSD1(1.0)",
    )
    df2 = Dataflow(
        id="DF2",
        name="Dataflow 2",
        agency="BIS",
        version="1.0",
        structure="DataStructure=BIS:DSD1(1.0)",
    )
    cat1 = Categorisation(
        id="CAT1",
        name="Categorisation 1",
        agency="BIS",
        version="1.0",
        source=(
            "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:DF1(1.0)"
        ),
        target=(
            "urn:sdmx:org.sdmx.infomodel.categoryscheme."
            "Category=BIS:CS1(1.0).TOP"
        ),
    )
    cat2 = Categorisation(
        id="CAT2",
        name="Categorisation 2",
        agency="BIS",
        version="1.0",
        source=(
            "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:DF2(1.0)"
        ),
        target=(
            "urn:sdmx:org.sdmx.infomodel.categoryscheme."
            "Category=BIS:CS1(1.0).TOP"
        ),
    )
    result = write(
        [cs, df1, df2, cat1, cat2],
        header=complete_header,
        prettyprint=True,
    )
    re_read = read_sdmx(result, validate=True).structures
    re_cs = next(s for s in re_read if isinstance(s, CategoryScheme))
    top = re_cs["TOP"]
    assert len(top.dataflows) == 2
    assert all(isinstance(d, DataflowRef) for d in top.dataflows)
    assert {d.id for d in top.dataflows} == {"DF1", "DF2"}


@pytest.fixture
def read_write_header():
    return Header(
        id="DF1605144905",
        prepared=datetime.strptime("2021-03-05T14:11:16", "%Y-%m-%dT%H:%M:%S"),
        sender=Organisation(
            id="Unknown",
        ),
        receiver=Organisation(
            id="Not_Supplied",
        ),
    )


@pytest.fixture
def bis_header():
    return Header(
        id="test",
        prepared=datetime.strptime("2021-04-20T10:29:14", "%Y-%m-%dT%H:%M:%S"),
        sender=Organisation(
            id="Unknown",
        ),
        receiver=Organisation(
            id="Not_supplied",
        ),
    )


@pytest.fixture
def codelist():
    return Codelist(
        annotations=[
            Annotation(
                id="FREQ_ANOT",
                title="Frequency",
                text="Frequency",
                type="text",
            ),
            Annotation(
                text="Frequency",
                type="text",
            ),
            Annotation(
                id="FREQ_ANOT2",
                title="Frequency",
            ),
        ],
        id="CL_FREQ",
        name="Frequency",
        items=[
            Code(id="A", name="Annual"),
            Code(id="M", name="Monthly"),
            Code(id="Q", name="Quarterly"),
            Code(id="W", name="Weekly"),
        ],
        agency="BIS",
        version="1.0",
        valid_from=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        valid_to=datetime.strptime("2021-12-31", "%Y-%m-%d"),
    )


@pytest.fixture
def noname_codelist():
    return Codelist(
        id="Test_Cod",
        items=[
            Code(id="A", name="Annual"),
            Code(id="M", name="Monthly"),
            Code(id="Q", name="Quarterly"),
            Code(id="W", name="Weekly"),
        ],
        agency="MD",
        version="1.0",
        valid_from=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        valid_to=datetime.strptime("2021-12-31", "%Y-%m-%d"),
    )


@pytest.fixture
def concept():
    return ConceptScheme(
        id="FREQ",
        name="Frequency",
        agency=Agency(id="BIS"),
        version="1.0",
        uri=TEST_CS_URN,
        urn=TEST_CS_URN,
        is_external_reference=False,
        is_partial=False,
        is_final=False,
        items=[
            Concept(
                id="A",
                name="Annual",
                description="Annual",
            ),
            Concept(
                id="M",
                name="Monthly",
                description="Monthly",
            ),
            Concept(
                id="Q",
                name="Quarterly",
                description="Quarterly",
            ),
        ],
    )


@pytest.fixture
def concept_quotes():
    return ConceptScheme(
        id='"Quote"',
        name='Concept with "Quotes"',
        description='concept with "Quotes"',
        agency=Agency(id="MD"),
        version="1.0",
        uri=TEST_CS_URN,
        urn=TEST_CS_URN,
        is_external_reference=False,
        is_partial=False,
        is_final=False,
        items=[],
    )


@pytest.fixture
def concept_ds():
    return ConceptScheme(
        urn="urn:sdmx:org.sdmx.infomodel.conceptscheme."
        "ConceptScheme=BIS:CS_FREQ(1.0)",
        uri="urn:sdmx:org.sdmx.infomodel.conceptscheme."
        "ConceptScheme=BIS:CS_FREQ(1.0)",
        id="CS_FREQ",
        name="Frequency",
        version="1.0",
        agency="BIS",
        items=[
            Concept(
                id="freq",
                urn="urn:sdmx:org.sdmx.infomodel.conceptscheme."
                "Concept=BIS:CS_FREQ(1.0).freq",
                name="Time frequency",
                annotations=(),
            ),
            Concept(
                id="OBS_VALUE",
                urn="urn:sdmx:org.sdmx.infomodel.conceptscheme."
                "Concept=BIS:CS_FREQ(1.0).OBS_VALUE",
                name="Observation value",
                annotations=(),
            ),
        ],
    )


@pytest.fixture
def full_structure_sample():
    base_path = Path(__file__).parent / "samples" / "full_scheme_structure.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def transformation_sample():
    base_path = Path(__file__).parent / "samples" / "transformation_scheme.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def transformation_scheme_structure():
    return TransformationScheme(
        id="TEST_TS",
        uri=None,
        urn="urn:sdmx:org.sdmx.infomodel.transformation.TransformationScheme=MD:TEST_TS(1.0)",
        name="Testing TS",
        description=None,
        version="1.0",
        valid_from=None,
        valid_to=None,
        is_final=False,
        is_external_reference=False,
        service_url=None,
        structure_url=None,
        agency="MD",
        items=[
            Transformation(
                id="TEST_Tr",
                uri=None,
                urn="urn:sdmx:org.sdmx.infomodel.transformation.Transformation=MD:TEST_TS(1.0).TEST_Tr",
                name="Testing Transformation",
                description=None,
                expression="sum(             BIS_LOC_STATS"
                "              group by REP_COUNTRY,"
                "COUNT_SECTOR,REF_DATE)",
                is_persistent=False,
                result="aggr.agg1",
                annotations=(),
            )
        ],
        is_partial=False,
        vtl_version="2.0",
        vtl_mapping_scheme=None,
        name_personalisation_scheme=None,
        custom_type_scheme=None,
        ruleset_schemes=Reference(
            sdmx_type="RulesetScheme",
            agency="MD",
            id="TEST_RULESET_SCHEME",
            version="1.0",
        ),
        user_defined_operator_schemes=Reference(
            sdmx_type="UserDefinedOperatorScheme",
            agency="MD",
            id="TEST_UDO_SCHEME",
            version="1.0",
        ),
        annotations=(),
    )


@pytest.fixture
def transformation_scheme_structure_with_object(udo_scheme_structure):
    return TransformationScheme(
        id="TEST_TS",
        uri=None,
        urn="urn:sdmx:org.sdmx.infomodel.transformation.TransformationScheme=MD:TEST_TS(1.0)",
        name="Testing TS",
        description=None,
        version="1.0",
        valid_from=None,
        valid_to=None,
        is_final=False,
        is_external_reference=False,
        service_url=None,
        structure_url=None,
        agency="MD",
        items=[
            Transformation(
                id="TEST_Tr",
                uri=None,
                urn="urn:sdmx:org.sdmx.infomodel.transformation.Transformation=MD:TEST_TS(1.0).TEST_Tr",
                name="Testing Transformation",
                description=None,
                expression="sum(             BIS_LOC_STATS"
                "              group by REP_COUNTRY,"
                "COUNT_SECTOR,REF_DATE)",
                is_persistent=False,
                result="aggr.agg1",
                annotations=(),
            )
        ],
        is_partial=False,
        vtl_version="2.0",
        vtl_mapping_scheme=None,
        name_personalisation_scheme=None,
        custom_type_scheme=None,
        ruleset_schemes=Reference(
            sdmx_type="RulesetScheme",
            agency="MD",
            id="TEST_RULESET_SCHEME",
            version="1.0",
        ),
        user_defined_operator_schemes=[udo_scheme_structure],
        annotations=(),
    )


@pytest.fixture
def ruleset_sample():
    base_path = Path(__file__).parent / "samples" / "ruleset_scheme.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def ruleset_scheme_structure():
    return RulesetScheme(
        id="TEST_RULESET_SCHEME",
        uri=None,
        urn="urn:sdmx:org.sdmx.infomodel.transformation.RulesetScheme=MD:TEST_RULESET_SCHEME(1.0)",
        name="Testing Ruleset Scheme",
        description=None,
        version="1.0",
        valid_from=None,
        valid_to=None,
        is_final=False,
        is_external_reference=False,
        service_url=None,
        structure_url=None,
        agency="MD",
        items=[
            Ruleset(
                id="TEST_DATAPOINT_RULESET",
                uri=None,
                urn="urn:sdmx:org.sdmx.infomodel.transformation.Ruleset=MD:"
                "TEST_RULESET_SCHEME(1.0).TEST_DATAPOINT_RULESET",
                name="Testing Datapoint Ruleset",
                description=None,
                ruleset_definition="define datapoint ruleset signValidation "
                "(variable ACCOUNTING_ENTRY as AE, "
                "INT_ACC_ITEM as IAI,                 "
                "FUNCTIONAL_CAT as FC, INSTR_ASSET as IA,"
                " OBS_VALUE as O) is      "
                'sign1c: when AE = "C" and IAI = "G" then O > 0 '
                'errorcode "sign1c" errorlevel 1;     '
                "end datapoint ruleset;",
                ruleset_scope="variable",
                ruleset_type="datapoint",
                annotations=(),
            )
        ],
        is_partial=False,
        vtl_version="2.0",
        vtl_mapping_scheme=None,
        annotations=(),
    )


@pytest.fixture
def udo_sample():
    base_path = Path(__file__).parent / "samples" / "udo_scheme.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def udo_scheme_structure():
    return UserDefinedOperatorScheme(
        id="TEST_UDO_SCHEME",
        uri=None,
        urn="urn:sdmx:org.sdmx.infomodel.transformation.UserDefinedOperatorScheme=MD:TEST_UDO_SCHEME(1.0)",
        name="Testing UDO Scheme",
        description=None,
        version="1.0",
        valid_from=None,
        valid_to=None,
        is_final=False,
        is_external_reference=False,
        service_url=None,
        structure_url=None,
        agency="MD",
        items=[
            UserDefinedOperator(
                id="TEST_UDO",
                uri=None,
                urn="urn:sdmx:org.sdmx.infomodel.transformation.UserDefinedOperator=MD:TEST_UDO_SCHEME(1.0).TEST_UDO",
                name="UDO Testing",
                description=None,
                operator_definition="define operator filter_ds"
                " (ds1 dataset, great_cons "
                'string default "1",'
                " less_cons number default 4.0)"
                "   returns dataset is"
                "     ds1[filter Me_1 > great_cons"
                " and Me_2 < less_cons]"
                " end operator;",
                annotations=(),
            )
        ],
        is_partial=False,
        vtl_version="2.0",
        vtl_mapping_scheme=None,
        ruleset_schemes=[
            Reference(
                sdmx_type="RulesetScheme",
                agency="MD",
                id="TEST_RULESET_SCHEME",
                version="1.0",
            ),
            Reference(
                sdmx_type="RulesetScheme",
                agency="MD",
                id="TEST_RULESET_SCHEME",
                version="1.0",
            ),
        ],
        annotations=(),
    )


@pytest.fixture
def datastructure(concept_ds):
    return DataStructureDefinition(
        annotations=[
            Annotation(title="OBS_FLAG", type="DISSEMINATION_FLAG_SETTINGS"),
            Annotation(title="time", type="DISSEMINATION_TIME_DIMENSION_CODE"),
        ],
        urn="urn:sdmx:org.sdmx.infomodel.datastructure."
        "DataStructure=ESTAT:HLTH_RS_PRSHP1(7.0)",
        id="HLTH_RS_PRSHP1",
        name="HLTH_RS_PRSHP1",
        version="7.0",
        agency="ESTAT",
        is_final=True,
        components=Components(
            [
                Component(
                    id="freq_dim",
                    required=True,
                    role=Role.DIMENSION,
                    concept=concept_ds.concepts[0],
                    local_facets=Facets(min_length="1", max_length="1"),
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure."
                    "TimeDimension=ESTAT:HLTH_RS_PRSHP1(7.0).FREQ",
                ),
                Component(
                    id="DIM2",
                    required=True,
                    role=Role.DIMENSION,
                    # Missing Concept Scheme
                    concept=ItemReference(
                        id="CS_FREQ2",
                        sdmx_type=CON,
                        agency="BIS",
                        version="1.0",
                        item_id="DIM2",
                    ),
                    local_facets=Facets(min_length="1", max_length="1"),
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure."
                    "TimeDimension=ESTAT:HLTH_RS_PRSHP1(7.0).DIM2",
                ),
                Component(
                    id="DIM3",
                    required=True,
                    role=Role.DIMENSION,
                    # Missing Concept in Concept Identity
                    concept=ItemReference(
                        id="CS_FREQ",
                        sdmx_type=CON,
                        agency="BIS",
                        version="1.0",
                        item_id="DIM3",
                    ),
                    local_facets=Facets(min_length="1", max_length="1"),
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure."
                    "TimeDimension=ESTAT:HLTH_RS_PRSHP1(7.0).DIM2",
                ),
                Component(
                    id="OBS_VALUE",
                    required=True,
                    role=Role.MEASURE,
                    concept=concept_ds.concepts[1],
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure."
                    "PrimaryMeasure=ESTAT:HLTH_RS_PRSHP1(7.0).OBS_VALUE",
                ),
            ]
        ),
        description="Healthcare resource partnership statistics",
    )


@pytest.fixture
def datastructure_two_measures(concept_ds):
    return DataStructureDefinition(
        annotations=[
            Annotation(title="OBS_FLAG", type="DISSEMINATION_FLAG_SETTINGS"),
            Annotation(title="time", type="DISSEMINATION_TIME_DIMENSION_CODE"),
        ],
        urn="urn:sdmx:org.sdmx.infomodel.datastructure."
        "DataStructure=ESTAT:HLTH_RS_PRSHP1(7.0)",
        id="HLTH_RS_PRSHP1",
        name="HLTH_RS_PRSHP1",
        version="7.0",
        agency="ESTAT",
        is_final=True,
        components=Components(
            [
                Component(
                    id="freq_dim",
                    required=True,
                    role=Role.DIMENSION,
                    concept=concept_ds.concepts[0],
                    local_facets=Facets(min_length="1", max_length="1"),
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure."
                    "TimeDimension=ESTAT:HLTH_RS_PRSHP1(7.0).FREQ",
                ),
                Component(
                    id="OBS_VALUE_1",
                    required=True,
                    role=Role.MEASURE,
                    concept=concept_ds.concepts[1],
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure."
                    "PrimaryMeasure=ESTAT:HLTH_RS_PRSHP1(7.0).OBS_VALUE_1",
                ),
                Component(
                    id="OBS_VALUE_2",
                    required=True,
                    role=Role.MEASURE,
                    concept=concept_ds.concepts[1],
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure."
                    "PrimaryMeasure=ESTAT:HLTH_RS_PRSHP1(7.0).OBS_VALUE_2",
                ),
            ]
        ),
        description="Healthcare resource partnership statistics",
    )


@pytest.fixture
def partial_datastructure():
    return DataStructureDefinition(
        agency="BIS",
        annotations=(),
        id="BIS_DER",
        components=Components([]),
        description="BIS derivates statistics",
        name="BIS derivates statistics",
        urn="urn:sdmx:org.sdmx.infomodel.datastructure."
        "DataStructure=BIS:BIS_DER(1.0)",
        version="1.0",
    )


@pytest.fixture
def dataflow():
    return Dataflow(
        agency="BIS",
        annotations=(),
        id="WEBSTATS_DER_DATAFLOW",
        description="OTC derivatives and FX spot - turnover",
        is_external_reference=True,
        is_final=True,
        name="OTC derivatives turnover",
        service_url=None,
        structure="DataStructure=BIS:BIS_DER(1.0)",
        structure_url=None,
        uri=None,
        urn="urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)",
        valid_from=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        valid_to=datetime.strptime("2021-12-31", "%Y-%m-%d"),
        version="1.0",
    )


@pytest.fixture
def vtlmapping_scheme():
    return VtlMappingScheme(
        id="VTLMS1",
        uri=None,
        urn="urn:sdmx:org.sdmx.infomodel.transformation.VtlMappingScheme=FR1:VTLMS1(1.0)",
        name="VTL Mapping Scheme #1",
        description=None,
        version="1.0",
        valid_from=None,
        valid_to=None,
        is_final=False,
        is_external_reference=False,
        service_url=None,
        structure_url=None,
        agency="FR1",
        items=[
            VtlDataflowMapping(
                id="VTLM1",
                uri=None,
                urn="urn:sdmx:org.sdmx.infomodel.transformation.VtlDataflowMapping=FR1:VTLMS1(1.0).VTLM1",
                name="VTL Mapping #1",
                description=None,
                annotations=(),
                dataflow=DataflowRef(
                    agency="FR1",
                    id="BPE_DETAIL",
                    version="1.0",
                    name="Dataflow",
                ),
                dataflow_alias="BPE_DETAIL_VTL",
                to_vtl_mapping_method=None,
                from_vtl_mapping_method=None,
            ),
            VtlDataflowMapping(
                id="VTLM2",
                uri=None,
                urn="urn:sdmx:org.sdmx.infomodel.transformation.VtlDataflowMapping=FR1:VTLMS1(1.0).VTLM2",
                name="VTL Mapping #2",
                description=None,
                annotations=(),
                dataflow=DataflowRef(
                    agency="FR1",
                    id="LEGAL_POP_CUBE",
                    version="1.0",
                    name="Dataflow",
                ),
                dataflow_alias="LEGAL_POP",
                to_vtl_mapping_method=None,
                from_vtl_mapping_method=None,
            ),
        ],
        is_partial=False,
        annotations=(),
    )


@pytest.fixture
def vtlmapping_sample():
    base_path = Path(__file__).parent / "samples" / "vtl_mapping_scheme.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def enum_format():
    base_path = Path(__file__).parent / "samples" / "enum_format.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def prov_agreement():
    return ProvisionAgreement(
        id="TEST",
        agency="MD",
        version="1.0",
        name="Test Provision Agreement",
        description=None,
        dataflow="Dataflow=MD:TEST(1.0)",
        provider="DataProvider=MD:DATA_PROVIDERS(1.0).MD",
    )


@pytest.fixture
def prov_agreement_sample():
    base_path = Path(__file__).parent / "samples" / "prov_agreement_sample.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def constraint_with_cube():
    return DataConstraint(
        id="TEST_CONSTRAINT_CUBE",
        name="Test Constraint with Cube Region",
        agency="TEST_AGENCY",
        version="1.0",
        description="A test constraint with cube region",
        constraint_attachment=ConstraintAttachment(
            data_provider=None,
            dataflows=[
                "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow="
                "TEST_AGENCY:TEST_DF(1.0)"
            ],
            data_structures=None,
            provision_agreements=None,
        ),
        cube_regions=[
            CubeRegion(
                key_values=[
                    CubeKeyValue(
                        id="FREQ",
                        values=[
                            CubeValue(value="M"),
                            CubeValue(value="Q"),
                        ],
                    ),
                    CubeKeyValue(
                        id="REF_AREA",
                        values=[
                            CubeValue(value="US"),
                            CubeValue(value="UK"),
                        ],
                    ),
                ],
                is_included=True,
            ),
            CubeRegion(
                key_values=[],
                is_included=True,
            ),
        ],
        key_sets=[],
    )


@pytest.fixture
def constraint_with_keyset():
    return DataConstraint(
        id="TEST_CONSTRAINT_KEYSET",
        name="Test Constraint with Key Set",
        agency="TEST_AGENCY",
        version="1.0",
        description="A test constraint with key set",
        constraint_attachment=ConstraintAttachment(
            data_provider=None,
            dataflows=[
                "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow="
                "TEST_AGENCY:TEST_DF(1.0)"
            ],
            data_structures=None,
            provision_agreements=None,
        ),
        cube_regions=[],
        key_sets=[
            KeySet(
                keys=[
                    DataKey(
                        keys_values=[
                            DataKeyValue(id="FREQ", value="M"),
                            DataKeyValue(id="REF_AREA", value="US"),
                        ],
                        valid_from=None,
                        valid_to=None,
                    ),
                    DataKey(
                        keys_values=[
                            DataKeyValue(id="FREQ", value="Q"),
                            DataKeyValue(id="REF_AREA", value="UK"),
                        ],
                        valid_from=None,
                        valid_to=None,
                    ),
                ],
                is_included=True,
            ),
        ],
    )


@pytest.fixture
def constraint_cube_sample():
    base_path = Path(__file__).parent / "samples" / "constraint_cube.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def constraint_keyset_sample():
    base_path = Path(__file__).parent / "samples" / "constraint_keyset.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def constraint_with_data_structure():
    return DataConstraint(
        id="TEST_CONSTRAINT_DSD",
        name="Test Constraint with Data Structure",
        agency="TEST_AGENCY",
        version="1.0",
        description="A test constraint attached to a data structure",
        constraint_attachment=ConstraintAttachment(
            data_provider=None,
            dataflows=None,
            data_structures=[
                "urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure="
                "TEST_AGENCY:TEST_DSD(1.0)"
            ],
            provision_agreements=None,
        ),
        cube_regions=[
            CubeRegion(
                key_values=[
                    CubeKeyValue(
                        id="FREQ",
                        values=[CubeValue(value="A")],
                    ),
                ],
                is_included=True,
            ),
        ],
        key_sets=[],
    )


@pytest.fixture
def constraint_with_provider():
    return DataConstraint(
        id="TEST_CONSTRAINT_PROV",
        name="Test Constraint with Provider",
        agency="TEST_AGENCY",
        version="1.0",
        description="A test constraint attached to a provider",
        constraint_attachment=ConstraintAttachment(
            data_provider="DataProvider=TEST_AGENCY:DATA_PROVIDERS(1.0).PROVIDER_ID",
            dataflows=None,
            data_structures=None,
            provision_agreements=None,
        ),
        cube_regions=[
            CubeRegion(
                key_values=[
                    CubeKeyValue(
                        id="FREQ",
                        values=[CubeValue(value="M")],
                    ),
                ],
                is_included=True,
            ),
        ],
        key_sets=[],
    )


@pytest.fixture
def constraint_datastructure_sample():
    base_path = (
        Path(__file__).parent / "samples" / "constraint_datastructure.xml"
    )
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def constraint_provider_sample():
    base_path = Path(__file__).parent / "samples" / "constraint_provider.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def constraint_with_provision_agreement():
    return DataConstraint(
        id="TEST_CONSTRAINT_PA",
        name="Test Constraint with Provision Agreement",
        agency="TEST_AGENCY",
        version="1.0",
        description="A test constraint attached to a provision agreement",
        constraint_attachment=ConstraintAttachment(
            data_provider=None,
            dataflows=None,
            data_structures=None,
            provision_agreements=[
                "urn:sdmx:org.sdmx.infomodel.registry.ProvisionAgreement="
                "TEST_AGENCY:TEST_PA(1.0)"
            ],
        ),
        cube_regions=[
            CubeRegion(
                key_values=[
                    CubeKeyValue(
                        id="FREQ",
                        values=[CubeValue(value="A")],
                    ),
                ],
                is_included=True,
            ),
        ],
        key_sets=[],
    )


@pytest.fixture
def constraint_provision_agreement_sample():
    base_path = (
        Path(__file__).parent
        / "samples"
        / "constraint_provision_agreement.xml"
    )
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def constraint_without_attachment():
    return DataConstraint(
        id="TEST_CONSTRAINT_NO_ATTACH",
        name="Test Constraint without Attachment",
        agency="TEST_AGENCY",
        version="1.0",
        description="A test constraint without constraint attachment",
        constraint_attachment=None,
        cube_regions=[
            CubeRegion(
                key_values=[
                    CubeKeyValue(
                        id="FREQ",
                        values=[CubeValue(value="Q")],
                    ),
                ],
                is_included=True,
            ),
        ],
        key_sets=[],
    )


@pytest.fixture
def constraint_no_attachment_sample():
    base_path = (
        Path(__file__).parent / "samples" / "constraint_no_attachment.xml"
    )
    with open(base_path, "r") as f:
        return f.read()


def test_codelist(codelist_sample, complete_header, codelist):
    content = [codelist]
    result = write(
        content,
        header=complete_header,
    )
    read(result, validate=False)

    assert result == codelist_sample


def test_concept(concept_sample, complete_header, concept):
    content = [concept]
    result = write(
        content,
        header=complete_header,
    )

    assert result == concept_sample


def test_file_writing(concept_sample, complete_header, concept):
    content = [concept]
    output_path = str(Path(__file__).parent / "samples" / "test_output.xml")
    write(
        content,
        output_path=output_path,
        header=complete_header,
    )

    with open(output_path, "r") as f:
        assert f.read() == concept_sample
    os.remove(output_path)


def test_writer_empty(empty_sample, header):
    result = write([], prettyprint=True, header=header)
    assert result == empty_sample


def test_writing_not_supported():
    with pytest.raises(NotImplemented):
        write_err()


def test_write_to_file(empty_sample, tmpdir, header):
    file = tmpdir.join("output.txt")
    result = write(
        [],
        output_path=file.strpath,
        prettyprint=True,
        header=header,
    )  # or use str(file)
    assert file.read() == empty_sample
    assert result is None


def test_writer_no_header():
    result: str = write({}, prettyprint=False)
    assert "<mes:Header>" in result
    assert "<mes:ID>" in result
    assert "<mes:Test>false</mes:Test>" in result
    assert "<mes:Prepared>" in result
    assert '<mes:Sender id="ZZZ"/>' in result


def test_writer_datastructure(complete_header, datastructure):
    content = [datastructure]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )

    assert "DataStructures" in result


def test_writer_partial_datastructure(complete_header, partial_datastructure):
    content = [partial_datastructure]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )

    assert "DataStructure=BIS:BIS_DER(1.0)" in result


def test_writer_dataflow(complete_header, dataflow):
    content = [dataflow]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )

    assert "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)" in result


def test_writer_dataflow_with_dsd_object(
    complete_header, dataflow, partial_datastructure
):
    dataflow_with_dsd = replace(dataflow, structure=partial_datastructure)

    result = write(
        [dataflow_with_dsd],
        header=complete_header,
        prettyprint=False,
    )

    assert (
        "<str:Structure>"
        '<Ref package="datastructure" agencyID="BIS" '
        'id="BIS_DER" version="1.0" class="DataStructure"/>'
        "</str:Structure>" in result.replace("\t", "")
    )
    assert result == write(
        [dataflow],
        header=complete_header,
        prettyprint=False,
    )


def test_writer_dataflow_without_structure(complete_header, dataflow):
    dataflow_stub = replace(dataflow, structure=None)

    result = write(
        [dataflow_stub],
        header=complete_header,
        prettyprint=False,
    )

    assert (
        "<str:Dataflow "
        'id="WEBSTATS_DER_DATAFLOW" '
        'urn="urn:sdmx:org.sdmx.infomodel.datastructure.'
        'Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)" '
        'version="1.0" '
        'validFrom="2021-01-01T00:00:00" '
        'validTo="2021-12-31T00:00:00" '
        'isExternalReference="true" '
        'isFinal="true" '
        'agencyID="BIS">'
        '<com:Name xml:lang="en">OTC derivatives turnover</com:Name>'
        '<com:Description xml:lang="en">'
        "OTC derivatives and FX spot - turnover</com:Description>"
        "</str:Dataflow>" in result.replace("\t", "")
    )


def test_write_read_dataflow_with_dsd_object(
    complete_header, dataflow, partial_datastructure
):
    dataflow_with_dsd = replace(dataflow, structure=partial_datastructure)

    write_result = write(
        [dataflow_with_dsd],
        header=complete_header,
        prettyprint=False,
    )
    read_result = read(write_result, validate=True)

    # The DSD object is read back as its short URN reference.
    assert read_result == [dataflow]


def test_write_read_dataflow_without_structure(complete_header, dataflow):
    dataflow_stub = replace(dataflow, structure=None)

    write_result = write(
        [dataflow_stub],
        header=complete_header,
        prettyprint=False,
    )
    read_result = read(write_result, validate=True)

    assert read_result == [dataflow_stub]


def test_read_write(read_write_sample, read_write_header):
    content, read_format = process_string_to_read(read_write_sample)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    read_result = read(content, validate=True)

    write_result = write(
        read_result,
        header=read_write_header,
        prettyprint=True,
    )

    assert write_result == content


def test_write_read(complete_header, datastructure, dataflow, concept_ds):
    content = [concept_ds, datastructure, dataflow]

    write_result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )

    read_result = read(write_result)

    assert content == read_result


def test_bis_der(bis_sample, bis_header):
    content, _ = process_string_to_read(bis_sample)
    read_result = read(bis_sample, validate=True)
    write_result = write(
        read_result,
        header=bis_header,
        prettyprint=True,
    )
    assert write_result == content


def test_group_deletion(groups_sample, header):
    content, read_format = process_string_to_read(groups_sample)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    read_result = read(content, validate=True)
    write_result = write(
        read_result,
        header=header,
        prettyprint=True,
    )
    assert "Groups" not in write_result
    assert any("BIS:BIS_DER(1.0)" in e.short_urn for e in read_result)


def test_check_escape(estat_sample):
    structures = read(estat_sample, validate=True)
    result = write(structures, prettyprint=True)
    assert result.count("&lt;") == 10
    assert result.count("&gt;") == 10
    assert result.count("&amp;") == 4

    structures_after_loop = read(result, validate=True)
    assert structures == structures_after_loop


def test_invalid_structure_header(header):
    header_da = copy.deepcopy(header)
    header_did = copy.deepcopy(header)
    header_structures = copy.deepcopy(header)
    header_da.dataset_action = ActionType.Append
    with pytest.raises(Invalid):
        write([], header=header_da)
    header_did.dataset_id = "ID"
    with pytest.raises(Invalid):
        write([], header=header_did)
    header_structures.structure = {"BIS_DER": "DataStructure=BIS:BIS_DER(1.0)"}
    with pytest.raises(Invalid):
        write([], header=header_structures)


def test_writer_transformation_scheme_structure(
    complete_header, transformation_scheme_structure, transformation_sample
):
    content = [transformation_scheme_structure]
    structure = write(
        content,
        header=complete_header,
        prettyprint=True,
    )

    assert structure == transformation_sample


def test_writer_transformation_single_quoted_identifier(complete_header):
    # Reserved VTL keywords used as identifiers must stay single-quoted
    # (e.g. 'errorlevel'); the writer must not turn that escape into a
    # "errorlevel" string literal (issue #615).
    expression = (
        "check_datapoint(ds, dp_ruleset) [calc errorcode := errorcode, "
        "'errorlevel' := errorlevel]"
    )
    scheme = TransformationScheme(
        id="TEST_TS",
        urn="urn:sdmx:org.sdmx.infomodel.transformation."
        "TransformationScheme=MD:TEST_TS(1.0)",
        name="Testing TS",
        version="1.0",
        agency="MD",
        items=[
            Transformation(
                id="TEST_Tr",
                urn="urn:sdmx:org.sdmx.infomodel.transformation."
                "Transformation=MD:TEST_TS(1.0).TEST_Tr",
                name="Validation",
                expression=expression,
                is_persistent=False,
                result="validation_result",
            )
        ],
        is_partial=False,
        vtl_version="2.0",
    )

    structure = write([scheme], header=complete_header, prettyprint=True)

    assert "&apos;errorlevel&apos;" in structure
    assert '"errorlevel"' not in structure

    # The single-quoted identifier must round-trip back unchanged.
    read_result = read(structure, validate=True)
    assert read_result[0].items[0].expression == expression


def test_writer_ruleset_udo_single_quoted_identifier(complete_header):
    # The same escaping applies to ruleset and operator definitions.
    ruleset_definition = (
        "define datapoint ruleset r1 (variable 'errorlevel' as E) is "
        "myrule: when E > 0 then E > 0 end datapoint ruleset;"
    )
    operator_definition = (
        "define operator op1 (ds dataset) returns dataset is "
        "ds['errorlevel' = 1] end operator;"
    )
    ruleset_scheme = RulesetScheme(
        id="TEST_RS",
        urn="urn:sdmx:org.sdmx.infomodel.transformation."
        "RulesetScheme=MD:TEST_RS(1.0)",
        name="RS",
        version="1.0",
        agency="MD",
        items=[
            Ruleset(
                id="R1",
                urn="urn:sdmx:org.sdmx.infomodel.transformation."
                "Ruleset=MD:TEST_RS(1.0).R1",
                name="R1",
                ruleset_definition=ruleset_definition,
                ruleset_scope="variable",
                ruleset_type="datapoint",
            )
        ],
        is_partial=False,
        vtl_version="2.0",
    )
    udo_scheme = UserDefinedOperatorScheme(
        id="TEST_UDO",
        urn="urn:sdmx:org.sdmx.infomodel.transformation."
        "UserDefinedOperatorScheme=MD:TEST_UDO(1.0)",
        name="UDO",
        version="1.0",
        agency="MD",
        items=[
            UserDefinedOperator(
                id="OP1",
                urn="urn:sdmx:org.sdmx.infomodel.transformation."
                "UserDefinedOperator=MD:TEST_UDO(1.0).OP1",
                name="OP1",
                operator_definition=operator_definition,
            )
        ],
        is_partial=False,
        vtl_version="2.0",
    )

    structure = write(
        [ruleset_scheme, udo_scheme],
        header=complete_header,
        prettyprint=True,
    )

    assert structure.count("&apos;errorlevel&apos;") == 2
    assert '"errorlevel"' not in structure


def test_writer_ruleset_scheme_structure(
    complete_header, ruleset_scheme_structure, ruleset_sample
):
    content = [ruleset_scheme_structure]

    structure = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert structure == ruleset_sample


def test_writer_udo_scheme_structure(
    complete_header, udo_scheme_structure, udo_sample
):
    content = [udo_scheme_structure]

    structure = write(
        content,
        header=complete_header,
        prettyprint=True,
    )

    assert structure == udo_sample


def test_writer_full_scheme_structure(
    complete_header,
    transformation_scheme_structure,
    ruleset_scheme_structure,
    udo_scheme_structure,
    full_structure_sample,
):
    content = [
        ruleset_scheme_structure,
        transformation_scheme_structure,
        udo_scheme_structure,
    ]
    structure = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert structure == full_structure_sample


def test_writer_full_scheme_structure_with_object(
    complete_header,
    transformation_scheme_structure_with_object,
    ruleset_scheme_structure,
    udo_scheme_structure,
    full_structure_sample,
):
    content = [
        ruleset_scheme_structure,
        transformation_scheme_structure_with_object,
        udo_scheme_structure,
    ]
    structure = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert structure == full_structure_sample


def test_writer_vtlmapping_scheme(
    complete_header,
    vtlmapping_scheme,
    vtlmapping_sample,
):
    content = [vtlmapping_scheme]
    structure = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert structure == vtlmapping_sample


def test_writer_raise_nameable_error(noname_codelist, complete_header):
    content = [noname_codelist]
    with pytest.raises(Invalid, match="Name is required for NameableArtefact"):
        write(
            content,
            header=complete_header,
        )


def test_read_write_vtl_complete(vtl_complete):
    msg = read_sdmx(vtl_complete, validate=True)
    ts = msg.get_transformation_schemes()[0]
    result = write(
        [
            ts,
            ts.user_defined_operator_schemes[0],
            ts.ruleset_schemes[0],
            ts.vtl_mapping_scheme,
            ts.custom_type_scheme,
            ts.name_personalisation_scheme,
        ],
        prettyprint=True,
    )
    msg_2 = read_sdmx(result, validate=True)
    assert len(msg_2.get_transformation_schemes()) == 1
    ts_2 = msg_2.get_transformation_schemes()[0]
    assert ts_2.ruleset_schemes[0] == ts.ruleset_schemes[0]
    assert (
        ts_2.user_defined_operator_schemes[0]
        == ts.user_defined_operator_schemes[0]
    )
    assert isinstance(ts_2.vtl_mapping_scheme, VtlMappingScheme)
    assert ts_2.vtl_mapping_scheme == ts.vtl_mapping_scheme
    dataflow_mapping = ts_2.vtl_mapping_scheme.items[0]
    assert isinstance(dataflow_mapping, VtlDataflowMapping)
    from_vtl = dataflow_mapping.from_vtl_mapping_method
    assert isinstance(from_vtl, FromVtlMapping)
    assert len(from_vtl.from_vtl_sub_space) == 3
    assert from_vtl.from_vtl_sub_space[0] == "FREQ"
    to_vtl = dataflow_mapping.to_vtl_mapping_method
    assert isinstance(to_vtl, ToVtlMapping)
    assert len(to_vtl.to_vtl_sub_space) == 2
    assert to_vtl.to_vtl_sub_space[0] == "FREQ"
    assert isinstance(ts_2.custom_type_scheme, CustomTypeScheme)
    assert ts_2.custom_type_scheme == ts.custom_type_scheme
    assert isinstance(
        ts_2.name_personalisation_scheme, NamePersonalisationScheme
    )
    assert ts_2.name_personalisation_scheme == ts.name_personalisation_scheme


def test_read_write_enum_format(enum_format):
    structure = read_sdmx(enum_format, validate=True).structures
    # Read the structure and write it back
    result = write(
        structure,
        prettyprint=True,
    )
    # Read the result back to ensure it is valid
    read_sdmx(result, validate=True)


def test_writing_more_than_one_measure(datastructure_two_measures):
    content = [datastructure_two_measures]
    with pytest.raises(
        Invalid, match="SDMX-ML 2.1 does not support multiple measures"
    ):
        write(
            content,
            prettyprint=True,
        )


def test_read_write_datastructure_group(
    datastructure_group_read, datastructure_group_write
):
    message = read_sdmx(datastructure_group_read, validate=True)

    result = write(
        structures=message.structures,
        header=message.header,
        prettyprint=True,
    )
    assert result == datastructure_group_write


def test_write_dataflow_with_quote(concept_quotes):
    content = [concept_quotes]
    result = write(
        content,
        prettyprint=True,
    )
    assert 'id=""Quote""' in result
    assert 'Name xml:lang="en">Concept with "Quotes"' in result
    assert 'Description xml:lang="en">concept with "Quotes"' in result


def test_prov_agreement(
    prov_agreement_sample, complete_header, prov_agreement
):
    content = [prov_agreement]
    result = write(
        content,
        header=complete_header,
    )
    read(result, validate=True)
    assert result == prov_agreement_sample


def test_concept_identity_without_urn():
    concept = Concept(id="test_concept", name="Test Concept", urn=None)
    component = Component(
        id="test_comp",
        required=True,
        role=Role.DIMENSION,
        concept=concept,
    )
    dsd = DataStructureDefinition(
        id="test_dsd",
        name="Test DSD",
        version="1.0",
        agency="TEST",
        components=Components([component]),
    )
    with pytest.raises(
        Invalid, match="Cannot select concept identity without URN"
    ):
        write([dsd])


def test_constraint_with_cube_region(
    complete_header, constraint_with_cube, constraint_cube_sample
):
    content = [constraint_with_cube]
    result = write(
        content,
        header=complete_header,
    )
    read(result, validate=True)
    assert result == constraint_cube_sample


def test_constraint_with_keyset(
    complete_header, constraint_with_keyset, constraint_keyset_sample
):
    content = [constraint_with_keyset]
    result = write(
        content,
        header=complete_header,
    )
    read(result, validate=True)
    assert result == constraint_keyset_sample


def test_constraint_with_data_structure(
    complete_header,
    constraint_with_data_structure,
    constraint_datastructure_sample,
):
    content = [constraint_with_data_structure]
    result = write(
        content,
        header=complete_header,
    )
    read(result, validate=True)
    assert result == constraint_datastructure_sample


def test_constraint_with_provider(
    complete_header, constraint_with_provider, constraint_provider_sample
):
    content = [constraint_with_provider]
    result = write(
        content,
        header=complete_header,
    )
    read(result, validate=True)
    assert result == constraint_provider_sample


def test_constraint_with_provision_agreement(
    complete_header,
    constraint_with_provision_agreement,
    constraint_provision_agreement_sample,
):
    content = [constraint_with_provision_agreement]
    result = write(
        content,
        header=complete_header,
    )
    read(result, validate=True)
    assert result == constraint_provision_agreement_sample


def test_constraint_without_attachment(
    complete_header,
    constraint_without_attachment,
    constraint_no_attachment_sample,
):
    content = [constraint_without_attachment]
    result = write(
        content,
        header=complete_header,
    )
    read(result, validate=True)
    assert result == constraint_no_attachment_sample


def test_availability_constraint_roundtrip_21(complete_header):
    urn = (
        "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=TEST_AGENCY:DF_TEST(1.0)"
    )
    ac = AvailabilityConstraint(
        constraint_attachment=ConstraintAttachment(
            data_provider=None, dataflows=[urn]
        ),
        cube_region=CubeRegion(
            key_values=[CubeKeyValue(id="FREQ", values=[CubeValue(value="M")])]
        ),
        series_count=3,
        obs_count=42,
    )
    out = write([ac], prettyprint=True, header=complete_header)
    assert 'type="Actual"' in out
    assert 'id="DF_TEST"' in out
    assert 'agencyID="TEST_AGENCY"' in out
    assert "Availability for DF_TEST" in out
    # The counts have no dedicated element in SDMX-ML 2.1, so they are
    # carried as FMR-style sdmx_metrics annotations.
    assert '<com:Annotation id="series_count">' in out
    assert "<com:AnnotationType>sdmx_metrics</com:AnnotationType>" in out
    assert "<com:AnnotationTitle>3</com:AnnotationTitle>" in out
    assert '<com:Annotation id="obs_count">' in out
    assert "<com:AnnotationTitle>42</com:AnnotationTitle>" in out
    back = read_sdmx(out, validate=True).structures
    assert len(back) == 1
    assert isinstance(back[0], AvailabilityConstraint)
    assert back[0].constraint_attachment == ac.constraint_attachment
    kv = back[0].cube_region.key_values[0]
    assert kv.id == "FREQ"
    assert [v.value for v in kv.values] == ["M"]
    # The counts now survive the legacy round trip via the annotations,
    # which are lifted back and excluded from back[0].annotations.
    assert back[0].series_count == 3
    assert back[0].obs_count == 42
    assert back[0].annotations == ()


def test_availability_constraint_21_ignores_bad_metric_title(
    complete_header,
):
    urn = (
        "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=TEST_AGENCY:DF_TEST(1.0)"
    )
    ac = AvailabilityConstraint(
        constraint_attachment=ConstraintAttachment(
            data_provider=None, dataflows=[urn]
        ),
        cube_region=CubeRegion(
            key_values=[CubeKeyValue(id="FREQ", values=[CubeValue(value="M")])]
        ),
        series_count=3,
    )
    out = write([ac], prettyprint=True, header=complete_header)
    # Corrupt the emitted count so it can no longer be parsed as an
    # int: a non-numeric title cannot be a genuine count, so the
    # annotation must be kept as-is instead of being lifted (and no
    # exception raised for it).
    corrupted = out.replace(
        "<com:AnnotationTitle>3</com:AnnotationTitle>",
        "<com:AnnotationTitle>not-a-number</com:AnnotationTitle>",
    )
    back = read_sdmx(corrupted, validate=True).structures
    assert back[0].series_count is None
    assert len(back[0].annotations) == 1
    assert back[0].annotations[0].id == "series_count"
    assert back[0].annotations[0].title == "not-a-number"


def test_availability_constraint_21_ignores_unicode_digit_title(
    complete_header,
):
    # str.isdigit() returns True for characters such as the
    # superscript two ("²") that int() still cannot parse; the guard
    # must not crash on those either.
    urn = (
        "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=TEST_AGENCY:DF_TEST(1.0)"
    )
    ac = AvailabilityConstraint(
        constraint_attachment=ConstraintAttachment(
            data_provider=None, dataflows=[urn]
        ),
        cube_region=CubeRegion(
            key_values=[CubeKeyValue(id="FREQ", values=[CubeValue(value="M")])]
        ),
        series_count=3,
    )
    out = write([ac], prettyprint=True, header=complete_header)
    corrupted = out.replace(
        "<com:AnnotationTitle>3</com:AnnotationTitle>",
        "<com:AnnotationTitle>²</com:AnnotationTitle>",
    )
    back = read_sdmx(corrupted, validate=True).structures
    assert back[0].series_count is None
    assert back[0].annotations[0].title == "²"


def test_availability_constraint_21_no_counts_writes_no_metrics(
    complete_header,
):
    urn = (
        "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=TEST_AGENCY:DF_TEST(1.0)"
    )
    ac = AvailabilityConstraint(
        constraint_attachment=ConstraintAttachment(
            data_provider=None, dataflows=[urn]
        ),
        cube_region=CubeRegion(key_values=[]),
    )
    out = write([ac], prettyprint=True, header=complete_header)
    # Neither count is set: no sdmx_metrics annotation (and no
    # Annotations element at all) should be emitted.
    assert "sdmx_metrics" not in out
    assert "<com:Annotations>" not in out
    back = read_sdmx(out, validate=True).structures
    assert back[0].series_count is None
    assert back[0].obs_count is None
    assert back[0].annotations == ()


def test_constraint_time_range_roundtrip_21():
    dc = DataConstraint(
        id="TR",
        name="tr",
        agency="AG",
        version="1.0",
        cube_regions=[
            CubeRegion(
                key_values=[
                    CubeKeyValue(
                        id="TIME_PERIOD",
                        time_range=CubeTimeRange(
                            start_period=TimePeriodBoundary("2020", True),
                            end_period=TimePeriodBoundary("2024", False),
                        ),
                    )
                ]
            )
        ],
    )
    out = write_sdmx(dc, Format.STRUCTURE_SDMX_ML_2_1, prettyprint=True)
    assert "<com:TimeRange>" in out
    assert "<com:StartPeriod " in out
    kv = read_sdmx(out).get_data_constraints()[0].cube_regions[0].key_values[0]
    assert kv.time_range.start_period.period == "2020"
    assert kv.time_range.start_period.is_inclusive is True
    assert kv.time_range.end_period.is_inclusive is False


def test_constraint_keyvalue_validity_omitted_21():
    dc = DataConstraint(
        id="KV",
        name="kv",
        agency="AG",
        version="1.0",
        cube_regions=[
            CubeRegion(
                key_values=[
                    CubeKeyValue(
                        id="FREQ",
                        values=[CubeValue(value="A")],
                        valid_from=datetime(2020, 1, 1),
                        valid_to=datetime(2021, 1, 1),
                    )
                ]
            )
        ],
    )
    out = write_sdmx(dc, Format.STRUCTURE_SDMX_ML_2_1, prettyprint=True)
    assert "validFrom" not in out
    assert "validTo" not in out
    kv = read_sdmx(out).get_data_constraints()[0].cube_regions[0].key_values[0]
    assert kv.valid_from is None
    assert kv.valid_to is None


def test_write_group_without_urn(complete_header, datastructure):
    dsd_with_group = datastructure.__replace__(
        groups=[Group(id="Sibling", dimensions=["FREQ"])],
    )
    content = [dsd_with_group]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    expected_urn = (
        "urn:sdmx:org.sdmx.infomodel.datastructure"
        ".GroupDimensionDescriptor"
        "=ESTAT:HLTH_RS_PRSHP1(7.0).Sibling"
    )
    assert expected_urn in result
    read(result, validate=True)


@pytest.mark.xml
def test_metadataflow_21_round_trip(complete_header):
    metadataflow = Metadataflow(
        id="MDF_TEST",
        name="Test Metadataflow",
        agency="BIS",
        version="1.0",
        structure=(
            "urn:sdmx:org.sdmx.infomodel.metadatastructure."
            "MetadataStructure=BIS:MSD_TEST(1.0)"
        ),
        targets=(),
    )
    result = write([metadataflow], header=complete_header, prettyprint=True)
    assert "<str:Metadataflows>" in result
    # SDMX-ML 2.1 uses a <Ref> element with class MetadataStructure
    assert 'class="MetadataStructure"' in result
    assert 'package="metadatastructure"' in result
    # No targets in SDMX-ML 2.1
    assert "<str:Target>" not in result
    re_read = read_sdmx(result, validate=True).structures[0]
    assert isinstance(re_read, Metadataflow)
    assert re_read == metadataflow


@pytest.mark.xml
def test_metadata_structure_21_raises(complete_header):
    msd = MetadataStructure(
        id="MSD_TEST", name="Test MSD", agency="BIS", version="1.0"
    )
    with pytest.raises(Invalid, match="not supported in SDMX-ML 2.1"):
        write([msd], header=complete_header, prettyprint=True)


@pytest.mark.xml
def test_metadata_provision_agreement_21_raises(complete_header):
    mpa = MetadataProvisionAgreement(
        id="MPA_TEST",
        name="Test MPA",
        agency="BIS",
        version="1.0",
        metadataflow="Metadataflow=BIS:MDF_TEST(1.0)",
        metadata_provider=(
            "MetadataProvider=BIS:METADATA_PROVIDERS(1.0).PROV1"
        ),
    )
    with pytest.raises(Invalid, match="not supported in SDMX-ML 2.1"):
        write([mpa], header=complete_header, prettyprint=True)
