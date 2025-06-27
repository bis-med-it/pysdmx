import os
from datetime import datetime
from pathlib import Path

import pytest

from pysdmx.io.reader import read_sdmx as read_sdmx
from pysdmx.io.xml.sdmx30.writer.structure import write
from pysdmx.model import (
    Agency,
    AgencyScheme,
    Code,
    Codelist,
    Concept,
    ConceptScheme,
    CustomType,
    CustomTypeScheme,
    DataType,
    Facets,
    FromVtlMapping,
    NamePersonalisation,
    NamePersonalisationScheme,
    Ruleset,
    RulesetScheme,
    ToVtlMapping,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
    VtlCodelistMapping,
    VtlConceptMapping,
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
def valuelist():
    return Codelist(
        id="VL_CURRENCY_SYMBOL",
        name="Currency Symbol",
        description="Enumerated list of currencies identified by symbol",
        agency="EXAMPLE",
        version="1.0",
        urn="urn:sdmx:org.sdmx.infomodel.codelist.ValueList=SDMX:VL_CURRENCY_SYMBOL(1.0)",
        sdmx_type="valuelist",
        items=[
            Code(id="$", name="USD", description="US Dollar"),
            Code(id="£", name="GBP", description="UK Pound"),
            Code(id="€", name="EUR", description="Euro"),
            Code(id="¥", name="CNY", description="China Yuan Renminbi"),
            Code(id="﷼", name="IRR", description="Iran Rial"),
            Code(id="¥", name="JPY", description="Japan Yen"),
        ],
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
            VtlCodelistMapping(
                urn="urn:sdmx:org.sdmx.infomodel.transformation.VtlCodelistMapping=MD:VMS1(1.0).VMCodelist",
                id="VMCodelist",
                name="Test VTL Mapping Codelist",
                codelist_alias="CL1",
                codelist=Reference(
                    sdmx_type="Codelist",
                    agency="BIS",
                    id="CL_FREQ",
                    version="1.0",
                ),
            ),
            VtlConceptMapping(
                urn="urn:sdmx:org.sdmx.infomodel.transformation.VtlConceptMapping=MD:VMS1(1.0).VMConcept",
                id="VMConcept",
                name="Test VTL Mapping Concept",
                concept_alias="C1",
                concept=ItemReference(
                    sdmx_type="Concept",
                    agency="BIS",
                    id="STANDALONE_CONCEPT_SCHEME",
                    version="1.0",
                    item_id="FREQ",
                ),
            ),
        ],
        is_partial=False,
        annotations=(),
    )


@pytest.fixture
def name_personalisation_scheme():
    return NamePersonalisationScheme(
        urn="urn:sdmx:org.sdmx.infomodel.transformation.NamePersonalisationScheme=MD:NPS1(1.0)",
        id="NPS1",
        name="Test Name Personalisation Scheme",
        version="1.0",
        agency="MD",
        vtl_version="2.0",
        items=[
            NamePersonalisation(
                id="NP1",
                uri=None,
                urn="urn:sdmx:org.sdmx.infomodel.transformation.NamePersonalisation=MD:NPS1(1.0).NP1",
                name="Test Name Personalisation",
                description=None,
                personalised_name="TEST_PERSONALISED",
                vtl_artefact="TEST_VTL_ARTEFACT",
                vtl_default_name="TEST_DEFAULT",
                annotations=[],
            )
        ],
    )


@pytest.fixture
def custom_type_scheme():
    return CustomTypeScheme(
        urn="urn:sdmx:org.sdmx.infomodel.transformation.CustomTypeScheme=MD:CTS1(1.0)",
        id="CTS1",
        name="Test Custom Type Scheme",
        version="1.0",
        agency="MD",
        vtl_version="2.0",
        items=[
            CustomType(
                id="CT1",
                uri=None,
                urn="urn:sdmx:org.sdmx.infomodel.transformation.CustomType=MD:CTS1(1.0).CT1",
                name="Test Custom Type",
                description=None,
                data_type="Test_data_type",
                null_value="Test_literal_format",
                output_format="Test_null_value",
                vtl_literal_format="Test_output_format",
                vtl_scalar_type="Test_scalar_type",
                annotations=[],
            )
        ],
    )


@pytest.fixture
def codelist_sample():
    base_path = Path(__file__).parent / "samples" / "codelist.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def valuelist_sample():
    base_path = Path(__file__).parent / "samples" / "valuelist.xml"
    with open(base_path, "r", encoding="utf-8") as f:
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
def vtl_mapping_scheme_sample():
    base_path = Path(__file__).parent / "samples" / "vtlmapping_scheme.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def name_personalisation_scheme_sample():
    base_path = (
        Path(__file__).parent / "samples" / "name_personalisation_scheme.xml"
    )
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def custom_type_scheme_sample():
    base_path = Path(__file__).parent / "samples" / "custom_type_scheme.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def full_datastructure_sample():
    base_path = (
        Path(__file__).parent / "samples" / "read_datastructure_sample.xml"
    )
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def write_datastructure_sample():
    base_path = (
        Path(__file__).parent / "samples" / "write_datastructure_sample.xml"
    )
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def datastructure_group_read():
    base_path = (
        Path(__file__).parent / "samples" / "read_datastructure_group.xml"
    )
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture
def datastructure_group_write():
    base_path = (
        Path(__file__).parent / "samples" / "write_datastructure_group.xml"
    )
    with open(base_path, "r", encoding="utf-8") as f:
        return f.read()


def test_codelist(complete_header, codelist, codelist_sample):
    content = [codelist]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == codelist_sample


def test_valuelist(complete_header, valuelist, valuelist_sample):
    content = [valuelist]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == valuelist_sample


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


def test_dataflow(complete_header, dataflow, structures_dataflow_sample):
    content = [dataflow]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == structures_dataflow_sample


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


def test_writer_vtlmapping_scheme(
    complete_header, vtlmapping_scheme, vtl_mapping_scheme_sample
):
    content = [vtlmapping_scheme]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == vtl_mapping_scheme_sample


def test_write_name_personalisation_scheme(
    complete_header,
    name_personalisation_scheme,
    name_personalisation_scheme_sample,
):
    content = [name_personalisation_scheme]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == name_personalisation_scheme_sample


def test_write_custom_type_scheme(
    complete_header, custom_type_scheme, custom_type_scheme_sample
):
    content = [custom_type_scheme]
    result = write(
        content,
        header=complete_header,
        prettyprint=True,
    )
    assert result == custom_type_scheme_sample


def test_datastructure_read_write(
    complete_header, full_datastructure_sample, write_datastructure_sample
):
    message = read_sdmx(full_datastructure_sample, validate=True)
    result = write(
        structures=message.structures,
        header=complete_header,
        prettyprint=True,
    )
    assert result == write_datastructure_sample


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
