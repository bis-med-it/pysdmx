import copy
import os
from datetime import datetime
from pathlib import Path

import pytest

from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.xml.sdmx21.__tokens import CON
from pysdmx.io.xml.sdmx21.reader.structure import read
from pysdmx.io.xml.sdmx21.writer.error import write as write_err
from pysdmx.io.xml.sdmx21.writer.structure import write
from pysdmx.model import (
    Agency,
    Code,
    Codelist,
    Concept,
    ConceptScheme,
    Facets,
    Ruleset,
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
)
from pysdmx.model.__base import (
    Annotation,
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
from pysdmx.model.dataset import ActionType
from pysdmx.model.message import Header

TEST_CS_URN = (
    "urn:sdmx:org.sdmx.infomodel.conceptscheme."
    "ConceptScheme=BIS:CS_FREQ(1.0)"
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
            Code(id="W"),
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
                is_persistent="false",
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
                is_persistent="false",
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
        components=[
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
        ],
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
