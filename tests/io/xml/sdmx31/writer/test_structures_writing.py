import os
from datetime import datetime
from pathlib import Path

import pytest
from msgspec.structs import replace

from pysdmx.errors import Invalid
from pysdmx.io import write_sdmx
from pysdmx.io.format import Format
from pysdmx.io.reader import read_sdmx as read_sdmx
from pysdmx.io.xml.sdmx31.reader.structure import read
from pysdmx.io.xml.sdmx31.writer.structure import write
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
    CubeKeyValue,
    CubeRegion,
    CubeValue,
    DataConstraint,
    DataType,
    Facets,
    FromVtlMapping,
    HierarchicalCode,
    Hierarchy,
    HierarchyAssociation,
    LevelType,
    Ruleset,
    RulesetScheme,
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
from pysdmx.model.message import Header

TEST_CS_URN = (
    "urn:sdmx:org.sdmx.infomodel.conceptscheme.ConceptScheme=BIS:CS_FREQ(1.0)"
)


@pytest.fixture
def samples_folder():
    return Path(__file__).parent / "samples"


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
def agency():
    return AgencyScheme(
        id="AGENCIES",
        uri=None,
        urn="urn:sdmx:org.sdmx.infomodel.base.AgencyScheme=SDMX:AGENCIES(1.0)",
        name="SDMX Agency Scheme",
        description=None,
        version="1.0",
        valid_from=None,
        valid_to=None,
        is_external_reference=False,
        service_url=None,
        structure_url=None,
        agency="SDMX",
        items=[
            Agency(
                id="BIS",
                name="Bank for International Settlements",
                description=None,
            ),
            Agency(id="ECB", name="European Central Bank", description=None),
            Agency(
                id="IMF", name="International Monetary Fund", description=None
            ),
            Agency(id="SDMX", name="SDMX", description=None),
        ],
        is_partial=False,
        annotations=(),
    )


@pytest.fixture
def datastructure():
    return DataStructureDefinition(
        id="DS",
        uri=None,
        urn="urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=MD:DS(1.0)",
        name="DS Test",
        description=None,
        version="1.0",
        valid_from=None,
        valid_to=None,
        is_final=False,
        is_external_reference=False,
        service_url=None,
        structure_url=None,
        agency="MD",
        annotations=(),
        components=Components(
            [
                Component(
                    id="FREQ",
                    required=True,
                    role=Role.DIMENSION,
                    concept=ItemReference(
                        sdmx_type="Concept",
                        agency="MD",
                        id="STANDALONE_CONCEPT_SCHEME",
                        version="1.0",
                        item_id="FREQ",
                    ),
                    local_dtype=DataType.STRING,
                    local_facets=Facets(min_length="1", max_length="1"),
                    name=None,
                    description=None,
                    local_codes=None,
                    attachment_level=None,
                    array_def=None,
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure.Dimension=MD:DM(1.0).FREQ",
                ),
                Component(
                    id="TIME_PERIOD",
                    required=True,
                    role=Role.DIMENSION,
                    concept=ItemReference(
                        sdmx_type="Concept",
                        agency="MD",
                        id="STANDALONE_CONCEPT_SCHEME",
                        version="1.0",
                        item_id="TIME_PERIOD",
                    ),
                    local_dtype=DataType.PERIOD,
                    local_facets=None,
                    name=None,
                    description=None,
                    local_codes=None,
                    attachment_level=None,
                    array_def=None,
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure.TimeDimension=MD:TD(1.0).TIME_PERIOD",
                ),
                Component(
                    id="OBS_VALUE",
                    required=False,
                    role=Role.MEASURE,
                    concept=ItemReference(
                        sdmx_type="Concept",
                        agency="MD",
                        id="STANDALONE_CONCEPT_SCHEME",
                        version="1.0",
                        item_id="OBS_VALUE",
                    ),
                    local_dtype=DataType.STRING,
                    local_facets=Facets(min_length="1", max_length="15"),
                    name=None,
                    description=None,
                    local_codes=None,
                    attachment_level=None,
                    array_def=None,
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure.Measure=MD:M1(1.0).OBS_VALUE",
                ),
                Component(
                    id="OBS_VALUE1",
                    required=False,
                    role=Role.MEASURE,
                    concept=ItemReference(
                        sdmx_type="Concept",
                        agency="MD",
                        id="STANDALONE_CONCEPT_SCHEME",
                        version="1.0",
                        item_id="OBS_VALUE1",
                    ),
                    local_dtype=DataType.STRING,
                    local_facets=Facets(min_length="1", max_length="15"),
                    name=None,
                    description=None,
                    local_codes=None,
                    attachment_level=None,
                    array_def=None,
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure.Measure=MD:M2(1.0).OBS_VALUE1",
                ),
                Component(
                    id="TIME_FORMAT",
                    required=False,
                    role=Role.ATTRIBUTE,
                    concept=ItemReference(
                        sdmx_type="Concept",
                        agency="MD",
                        id="STANDALONE_CONCEPT_SCHEME",
                        version="1.0",
                        item_id="TIME_FORMAT",
                    ),
                    local_dtype=DataType.STRING,
                    local_facets=Facets(min_length="3", max_length="3"),
                    name=None,
                    description=None,
                    local_codes=None,
                    attachment_level="FREQ",
                    array_def=None,
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure.DataAttribute=BIS:ATT1(1.0).TIME_FORMAT",
                ),
                Component(
                    id="OBS_STATUS",
                    required=True,
                    role=Role.ATTRIBUTE,
                    concept=ItemReference(
                        sdmx_type="Concept",
                        agency="MD",
                        id="STANDALONE_CONCEPT_SCHEME",
                        version="1.0",
                        item_id="OBS_STATUS",
                    ),
                    local_dtype=DataType.STRING,
                    local_facets=Facets(min_length="1", max_length="1"),
                    name=None,
                    description=None,
                    local_codes=None,
                    attachment_level="O",
                    array_def=None,
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure.DataAttribute=MD:ATT2(1.0).OBS_STATUS",
                ),
                Component(
                    id="DECIMALS",
                    required=True,
                    role=Role.ATTRIBUTE,
                    concept=ItemReference(
                        sdmx_type="Concept",
                        agency="MD",
                        id="STANDALONE_CONCEPT_SCHEME",
                        version="1.0",
                        item_id="DECIMALS",
                    ),
                    local_dtype=DataType.BIG_INTEGER,
                    local_facets=Facets(min_length="1", max_length="2"),
                    name=None,
                    description=None,
                    local_codes=None,
                    attachment_level="D",
                    array_def=None,
                    urn="urn:sdmx:org.sdmx.infomodel.datastructure.DataAttribute=MD:ATT3(1.0).DECIMALS",
                ),
            ]
        ),
    )


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
        vtl_mapping_scheme=VtlMappingScheme(
            urn="urn:sdmx:org.sdmx.infomodel.transformation.VtlMappingScheme=MD:VMS1(1.0)",
            id="VMS1",
            name="Test VTL Mapping Scheme",
            version="1.0",
            agency="MD",
            items=[
                VtlDataflowMapping(
                    id="VMDataflow",
                    uri=None,
                    urn="urn:sdmx:org.sdmx.infomodel.transformation.VtlDataflowMapping=MD:VMS1(1.0).VMDataflow",
                    name="Test VTL Mapping",
                    description=None,
                    annotations=[],
                    dataflow=DataflowRef(
                        agency="BIS", id="WS_CBS_PUB", version="1.0", name=None
                    ),
                    dataflow_alias="DS_1",
                    to_vtl_mapping_method=ToVtlMapping(
                        to_vtl_sub_space=["FREQ", "L_MEASURE"], method="Basic"
                    ),
                    from_vtl_mapping_method=FromVtlMapping(
                        from_vtl_sub_space=["FREQ", "L_MEASURE", "L_REP_CTY"],
                        method="Basic",
                    ),
                ),
            ],
        ),
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
def dataflow():
    return Dataflow(
        agency="BIS",
        annotations=(),
        id="WEBSTATS_DER_DATAFLOW",
        description="OTC derivatives and FX spot - turnover",
        is_external_reference=False,
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
def partial_datastructure():
    return DataStructureDefinition(
        agency="BIS",
        id="BIS_DER",
        components=Components([]),
        name="BIS derivatives statistics",
        version="1.0",
    )


@pytest.fixture
def dataflow2():
    return Dataflow(
        agency="MD",
        annotations=(),
        id="MD_TEST",
        description="MD_TEST",
        is_external_reference=False,
        name="MD_TEST",
        service_url=None,
        structure="DataStructure=MD:MD_TEST(1.0)",
        structure_url=None,
        uri=None,
        urn="urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=MD:MD_DATAFLOW(1.0)",
        valid_from=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        valid_to=datetime.strptime("2021-12-31", "%Y-%m-%d"),
        version="1.0",
    )


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
def agency_sample():
    base_path = Path(__file__).parent / "samples" / "agency.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def datastructure_sample():
    base_path = Path(__file__).parent / "samples" / "datastructure.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def structures_dataflow_sample():
    base_path = Path(__file__).parent / "samples" / "structure_dataflow.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def structures_dataflow_stub_sample():
    base_path = (
        Path(__file__).parent / "samples" / "structure_dataflow_stub.xml"
    )
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def transformation_scheme_sample():
    base_path = Path(__file__).parent / "samples" / "transformation_scheme.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def ruleset_scheme_sample():
    base_path = Path(__file__).parent / "samples" / "ruleset_scheme.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def udo_scheme_sample():
    base_path = Path(__file__).parent / "samples" / "udo_scheme.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def prov_agreement_sample():
    base_path = Path(__file__).parent / "samples" / "prov_agreement_sample.xml"
    with open(base_path, "r") as f:
        return f.read()


def test_codelist(complete_header, codelist, codelist_sample):
    content = [codelist]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == codelist_sample


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
            HierarchicalCode(
                id="B",
                urn=(
                    "urn:sdmx:org.sdmx.infomodel.codelist."
                    "Code=BIS:CL_FREQ(1.0).Q"
                ),
            ),
        ),
    )


def test_hierarchy(complete_header, hierarchy_with_levels):
    result = write(
        [hierarchy_with_levels], header=complete_header, prettyprint=True
    )
    assert "<str:Hierarchies>" in result
    assert 'hasFormalLevels="true"' in result
    assert '<str:Level id="0">' in result
    assert '<str:Level id="1">' in result
    re_read = read_sdmx(result, validate=True).structures[0]
    assert re_read == hierarchy_with_levels


def test_hierarchy_with_annotations(complete_header):
    hierarchy = Hierarchy(
        id="H1",
        name="Hierarchy 1",
        agency="BIS",
        version="1.0",
        has_formal_levels=True,
        level=LevelType(
            id="0",
            name="Division",
            annotations=(Annotation(id="LA", title="Level annotation"),),
        ),
        codes=(
            HierarchicalCode(
                id="A",
                urn=(
                    "urn:sdmx:org.sdmx.infomodel.codelist."
                    "Code=BIS:CL_FREQ(1.0).A"
                ),
                annotations=(Annotation(id="CA", text="Code annotation"),),
            ),
        ),
    )
    result = write([hierarchy], header=complete_header, prettyprint=True)
    re_read = read_sdmx(result, validate=True).structures[0]
    assert re_read == hierarchy


def test_hierarchy_association(complete_header):
    ha = HierarchyAssociation(
        id="HA1",
        name="Association 1",
        agency="BIS",
        version="1.0",
        hierarchy=Hierarchy(id="H1", name="H", agency="BIS", version="1.0"),
        component_ref=(
            "urn:sdmx:org.sdmx.infomodel.datastructure."
            "Dimension=BIS:DSD(1.0).FREQ"
        ),
        context_ref=(
            "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:DF(1.0)"
        ),
    )
    result = write([ha], header=complete_header, prettyprint=True)
    assert "<str:HierarchyAssociations>" in result
    assert (
        "<str:LinkedHierarchy>"
        "urn:sdmx:org.sdmx.infomodel.codelist.Hierarchy=BIS:H1(1.0)"
        "</str:LinkedHierarchy>" in result
    )
    re_read = read_sdmx(result, validate=True).structures[0]
    assert isinstance(re_read, HierarchyAssociation)
    assert (
        re_read.hierarchy
        == "urn:sdmx:org.sdmx.infomodel.codelist.Hierarchy=BIS:H1(1.0)"
    )


def test_hierarchy_association_no_hierarchy(complete_header):
    ha = HierarchyAssociation(
        id="HA1",
        name="Association 1",
        agency="BIS",
        version="1.0",
        component_ref="urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dimension=BIS:DSD(1.0).FREQ",
    )
    with pytest.raises(Invalid, match="must reference a hierarchy"):
        write([ha], header=complete_header, prettyprint=True)


def test_hierarchy_association_no_component(complete_header):
    ha = HierarchyAssociation(
        id="HA1",
        name="Association 1",
        agency="BIS",
        version="1.0",
        hierarchy="urn:sdmx:org.sdmx.infomodel.codelist.Hierarchy=BIS:H1(1.0)",
    )
    with pytest.raises(Invalid, match="must reference a component"):
        write([ha], header=complete_header, prettyprint=True)


def test_hierarchy_level_no_name(complete_header):
    hierarchy = Hierarchy(
        id="H1",
        name="H",
        agency="BIS",
        version="1.0",
        has_formal_levels=True,
        level=LevelType(id="0"),
    )
    with pytest.raises(Invalid, match="hierarchy levels must have a name"):
        write([hierarchy], header=complete_header, prettyprint=True)


def test_hierarchy_code_no_urn(complete_header):
    hierarchy = Hierarchy(
        id="H1",
        name="H",
        agency="BIS",
        version="1.0",
        codes=[HierarchicalCode(id="A")],
    )
    with pytest.raises(Invalid, match="must reference a code urn"):
        write([hierarchy], header=complete_header, prettyprint=True)


def test_concept(complete_header, concept, concept_sample):
    content = [concept]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == concept_sample


def test_agency(complete_header, agency, agency_sample):
    content = [agency]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == agency_sample


def test_datastructure(complete_header, datastructure, datastructure_sample):
    content = [datastructure]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == datastructure_sample


def test_dataflow(
    complete_header, dataflow, dataflow2, structures_dataflow_sample
):
    content = [dataflow, dataflow2]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == structures_dataflow_sample


def test_dataflow_with_dsd_object(
    complete_header,
    dataflow,
    dataflow2,
    partial_datastructure,
    structures_dataflow_sample,
):
    dataflow_with_dsd = replace(dataflow, structure=partial_datastructure)

    result = write(
        [dataflow_with_dsd, dataflow2],
        header=complete_header,
        prettyprint=True,
    )

    assert result == structures_dataflow_sample


def test_dataflow_without_structure(
    complete_header, dataflow, structures_dataflow_stub_sample
):
    dataflow_stub = replace(dataflow, structure=None)

    result = write(
        [dataflow_stub],
        header=complete_header,
        prettyprint=True,
    )

    assert result == structures_dataflow_stub_sample


def test_dataflow_with_dsd_object_round_trip(
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


def test_dataflow_without_structure_round_trip(complete_header, dataflow):
    dataflow_stub = replace(dataflow, structure=None)

    write_result = write(
        [dataflow_stub],
        header=complete_header,
        prettyprint=False,
    )
    read_result = read(write_result, validate=True)

    assert read_result == [dataflow_stub]


def test_transformation_scheme(
    complete_header,
    transformation_scheme_structure,
    transformation_scheme_sample,
):
    content = [transformation_scheme_structure]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == transformation_scheme_sample


def test_ruleset_scheme(
    complete_header, ruleset_scheme_structure, ruleset_scheme_sample
):
    content = [ruleset_scheme_structure]

    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == ruleset_scheme_sample


def test_writer_udo_scheme_structure(
    complete_header, udo_scheme_structure, udo_scheme_sample
):
    content = [udo_scheme_structure]

    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == udo_scheme_sample


def test_no_header_outpath(concept):
    output_path = str(Path(__file__).parent / "samples" / "test_output.xml")
    content = [concept]
    result = write(
        content,
        prettyprint=True,
        output_path=output_path,
    )
    os.remove(output_path)
    assert result is None


def test_prov_agreement(
    prov_agreement_sample, complete_header, prov_agreement
):
    content = [prov_agreement]
    result = write(
        content,
        header=complete_header,
    )
    read_sdmx(result, validate=True)
    assert result == prov_agreement_sample


def test_write_group_without_urn(datastructure):
    dsd_with_group = datastructure.__replace__(
        groups=[Group(id="Sibling", dimensions=["FREQ"])],
    )
    result = write_sdmx(
        [dsd_with_group],
        sdmx_format=Format.STRUCTURE_SDMX_ML_3_1,
    )
    expected_urn = (
        "urn:sdmx:org.sdmx.infomodel.datastructure"
        ".GroupDimensionDescriptor"
        "=MD:DS(1.0).Sibling"
    )
    assert expected_urn in result
    read_sdmx(result, validate=True)


@pytest.fixture
def category_scheme_nested_31():
    return CategoryScheme(
        id="CS1",
        name="Category Scheme 1",
        description="A scheme",
        agency="BIS",
        version="1.0.0",
        is_final=True,
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


def test_category_scheme_31_round_trip(
    complete_header, category_scheme_nested_31
):
    result = write(
        [category_scheme_nested_31], header=complete_header, prettyprint=True
    )
    assert "<str:CategorySchemes>" in result
    re_read = read_sdmx(result, validate=True).structures[0]
    assert re_read == category_scheme_nested_31


def test_category_scheme_31_name_with_apostrophe(complete_header):
    cs = CategoryScheme(
        id="CS2",
        name="Schemes",
        agency="BIS",
        version="1.0.0",
        is_final=True,
        items=(Category(id="C", name="Côte d'Ivoire"),),
    )
    result = write([cs], header=complete_header, prettyprint=True)
    re_read = read_sdmx(result, validate=True).structures[0]
    assert re_read == cs
    assert re_read.items[0].name == "Côte d'Ivoire"


def test_categorisation_31_round_trip(complete_header):
    # In SDMX-ML 3.1 the Categorisation version attribute is prohibited,
    # so the model default version ("1.0") must round-trip unchanged.
    categorisation = Categorisation(
        id="CAT1",
        name="Categorisation 1",
        agency="BIS",
        source=(
            "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:DF1(1.0.0)"
        ),
        target=(
            "urn:sdmx:org.sdmx.infomodel.categoryscheme."
            "Category=BIS:CS1(1.0.0).TOP.MID.LEAF"
        ),
    )
    result = write([categorisation], header=complete_header, prettyprint=True)
    assert "<str:Categorisations>" in result
    assert (
        "version=" not in result.split("<str:Categorisation ")[1].split(">")[0]
    )
    re_read = read_sdmx(result, validate=True).structures[0]
    # Full URNs round-trip unchanged.
    assert re_read == categorisation


def test_categorisation_31_codelist_source_round_trip(complete_header):
    # A non-Dataflow (Codelist) source must round-trip via the 3.1
    # reference-as-URN form.
    categorisation = Categorisation(
        id="CAT2",
        name="Categorisation 2",
        agency="BIS",
        source=(
            "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:CL_FREQ(1.0.0)"
        ),
        target=(
            "urn:sdmx:org.sdmx.infomodel.categoryscheme."
            "Category=BIS:CS1(1.0.0).OTHER"
        ),
    )
    result = write([categorisation], header=complete_header, prettyprint=True)
    assert "codelist.Codelist=BIS:CL_FREQ(1.0.0)" in result
    re_read = read_sdmx(result, validate=True).structures[0]
    assert re_read == categorisation


def test_category_scheme_31_enrichment_round_trip(complete_header):
    cs = CategoryScheme(
        id="CS1",
        name="Category Scheme 1",
        agency="BIS",
        version="1.0.0",
        is_final=True,
        items=(Category(id="TOP", name="Top"),),
    )
    dataflow = Dataflow(
        id="DF1",
        name="Dataflow 1",
        agency="BIS",
        version="1.0.0",
        structure="DataStructure=BIS:DSD1(1.0.0)",
    )
    categorisation = Categorisation(
        id="CAT1",
        name="Categorisation 1",
        agency="BIS",
        source=(
            "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:DF1(1.0.0)"
        ),
        target=(
            "urn:sdmx:org.sdmx.infomodel.categoryscheme."
            "Category=BIS:CS1(1.0.0).TOP"
        ),
    )
    result = write(
        [cs, dataflow, categorisation],
        header=complete_header,
        prettyprint=True,
    )
    re_read = read_sdmx(result, validate=True).structures
    re_cs = next(s for s in re_read if isinstance(s, CategoryScheme))
    top = re_cs["TOP"]
    assert len(top.dataflows) == 1
    assert isinstance(top.dataflows[0], DataflowRef)
    assert top.dataflows[0].agency == "BIS"
    assert top.dataflows[0].id == "DF1"
    assert top.dataflows[0].version == "1.0.0"
    assert top.dataflows[0].name == "Dataflow 1"


def test_data_constraint_has_no_marker_31():
    # SDMX 3.1 removed the constraint role/type attribute entirely (a
    # DataConstraint is always the allowed values; availability is the
    # separate AvailabilityConstraint element), so a plain DataConstraint
    # must carry no marker attribute at all when written to 3.1.
    dc = DataConstraint(
        id="TEST_31",
        name="Test 3.1 constraint",
        agency="TEST_AGENCY",
        version="1.0",
        constraint_attachment=ConstraintAttachment(
            data_provider=None,
            dataflows=[
                "urn:sdmx:org.sdmx.infomodel.datastructure."
                "Dataflow=TEST_AGENCY:TEST_DF(1.0)"
            ],
        ),
        cube_regions=[
            CubeRegion(
                key_values=[
                    CubeKeyValue(id="FREQ", values=[CubeValue(value="A")])
                ]
            )
        ],
    )
    result = write_sdmx(
        dc, sdmx_format=Format.STRUCTURE_SDMX_ML_3_1, prettyprint=True
    )
    assert 'role="' not in result
    assert 'type="' not in result
    back = read_sdmx(result, validate=True).structures
    assert isinstance(back[0], DataConstraint)


def test_availability_constraint_roundtrip_31(complete_header):
    urn = (
        "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=TEST_AGENCY:DF_TEST(1.0)"
    )
    ac = AvailabilityConstraint(
        constraint_attachment=ConstraintAttachment(
            data_provider=None, dataflows=[urn]
        ),
        cube_region=CubeRegion(
            key_values=[
                CubeKeyValue(id="FREQ", values=(CubeValue(value="M"),))
            ]
        ),
        series_count=3,
        obs_count=42,
    )
    out = write([ac], prettyprint=True, header=complete_header)
    assert "<str:AvailabilityConstraint" in out
    assert 'seriesCount="3"' in out
    assert 'obsCount="42"' in out
    assert "ContentConstraint" not in out
    back = read_sdmx(out, validate=True).structures
    assert back == [ac]


def test_availability_constraint_roundtrip_31_with_annotation(
    complete_header,
):
    urn = (
        "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=TEST_AGENCY:DF_TEST(1.0)"
    )
    ac = AvailabilityConstraint(
        annotations=[Annotation(id="ANN1", title="Note", type="text")],
        constraint_attachment=ConstraintAttachment(
            data_provider=None, dataflows=[urn]
        ),
        cube_region=CubeRegion(
            key_values=[
                CubeKeyValue(id="FREQ", values=(CubeValue(value="M"),))
            ]
        ),
        series_count=3,
        obs_count=42,
    )
    out = write([ac], prettyprint=True, header=complete_header)
    assert "<str:AvailabilityConstraint" in out
    assert '<com:Annotation id="ANN1">' in out
    # Per the 3.1 AnnotableType extension order: Annotations first,
    # then ConstraintAttachment, then CubeRegion.
    ann_pos = out.index("<com:Annotations>")
    attachment_pos = out.index("<str:ConstraintAttachment>")
    region_pos = out.index("<str:CubeRegion")
    assert ann_pos < attachment_pos < region_pos
    back = read_sdmx(out, validate=True).structures
    assert back == [ac]


def test_availability_constraint_31_duplicate_is_invalid(complete_header):
    urn = (
        "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=TEST_AGENCY:DF_TEST(1.0)"
    )
    attachment = ConstraintAttachment(data_provider=None, dataflows=[urn])
    ac1 = AvailabilityConstraint(
        constraint_attachment=attachment,
        cube_region=CubeRegion(key_values=[]),
        series_count=3,
    )
    ac2 = AvailabilityConstraint(
        constraint_attachment=attachment,
        cube_region=CubeRegion(key_values=[]),
        series_count=5,
    )
    with pytest.raises(
        Invalid, match="Two availability constraints for the same"
    ):
        write([ac1, ac2], header=complete_header, prettyprint=True)


def test_availability_constraint_31_without_counts(complete_header):
    ac = AvailabilityConstraint(
        constraint_attachment=ConstraintAttachment(
            data_provider=None,
            dataflows=[
                "urn:sdmx:org.sdmx.infomodel.datastructure."
                "Dataflow=TEST_AGENCY:DF_TEST(1.0)"
            ],
        ),
        cube_region=CubeRegion(key_values=[]),
    )
    out = write([ac], prettyprint=True, header=complete_header)
    assert "seriesCount" not in out
    assert read_sdmx(out, validate=True).structures == [ac]
