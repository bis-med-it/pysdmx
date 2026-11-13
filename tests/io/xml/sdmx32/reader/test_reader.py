from pathlib import Path

import pytest

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.xml.sdmx32.reader.structure import read
from pysdmx.model import (
    Codelist,
    Dataflow,
    DataStructureDefinition,
    ItemReference,
    QueryExtraction,
    QueryParameter,
    Reference,
    TransformationScheme,
    UrlExtraction,
    VtlCodelistMapping,
    VtlDataflowMapping,
    VtlDatasetMapping,
)

SAMPLES = Path(__file__).parent / "samples"
BASE = "urn:sdmx:org.sdmx.infomodel."


def mapping_ref(agency, scheme, version, item):
    return ItemReference("VtlDatasetMapping", agency, scheme, version, item)


def test_sdmx_ml_3_2_structure_is_detected():
    _, read_format = process_string_to_read(SAMPLES / "VTL_Sample_4.xml")

    assert read_format == Format.STRUCTURE_SDMX_ML_3_2


def test_dataset_mappings():
    msg = read_sdmx(SAMPLES / "VTL_Sample_4.xml")

    scheme = msg.get_vtl_mapping_schemes()[0]
    assert scheme.short_urn == "VtlMappingScheme=EXAMPLE:VTL_MAP(1.0)"
    assert [type(m) for m in scheme.items] == [VtlDatasetMapping] * 3
    assert [m.id for m in scheme.items] == ["DS_A", "DS_B", "DIFF"]
    assert [m.vtl_alias for m in scheme.items] == ["ds_a", "ds_b", "ds_diff"]
    assert [m.is_input for m in scheme.items] == [True, True, False]
    ds_a = scheme.items[0]
    assert ds_a.name == "Trade in goods - source A"
    assert isinstance(ds_a.sdmx_artefact, Dataflow)
    assert ds_a.sdmx_artefact == msg.get_dataflow("Dataflow=EXAMPLE:DF_A(1.0)")
    assert ds_a.sdmx_urn == f"{BASE}datastructure.Dataflow=EXAMPLE:DF_A(1.0)"


def test_execution_with_query_and_url_extractions():
    msg = read_sdmx(SAMPLES / "VTL_Sample_4.xml")

    executions = msg.get_vtl_executions()
    assert len(executions) == 1
    execution = executions[0]
    assert execution.short_urn == "VtlExecution=EXAMPLE:EXEC_DIFF(1.0)"
    assert execution.name == "Execution of TS_DIFF"
    assert isinstance(execution.transformation_scheme, TransformationScheme)
    assert (
        execution.transformation_scheme
        == (msg.get_transformation_schemes()[0])
    )
    assert execution.extractions == (
        QueryExtraction(
            dataset_mapping=mapping_ref("EXAMPLE", "VTL_MAP", "1.0", "DS_A"),
            entry_point="https://sdmx.example.org/rest",
            sdmx_api_version="1.5",
            parameters=(
                QueryParameter(name="key", value="A.USA.", is_fixed=True),
                QueryParameter(
                    name="startPeriod", value="2015", is_fixed=False
                ),
                QueryParameter(name="endPeriod", is_fixed=False),
            ),
        ),
        UrlExtraction(
            dataset_mapping=mapping_ref("EXAMPLE", "VTL_MAP", "1.0", "DS_B"),
            url_template=(
                "https://sdmx.example.org/rest/data/EXAMPLE,DF_B,1.0/A.USA."
                "?startPeriod={startPeriod}&endPeriod={endPeriod}"
            ),
            parameters=(
                QueryParameter(
                    name="startPeriod", value="2015", is_fixed=False
                ),
                QueryParameter(name="endPeriod", is_fixed=False),
            ),
        ),
    )


def test_mapping_to_data_structure_and_context():
    msg = read_sdmx(SAMPLES / "VTL_Sample_5.xml")

    pop_m = msg.get_vtl_mapping_schemes()[0].items[0]
    assert isinstance(pop_m.sdmx_artefact, DataStructureDefinition)
    assert pop_m.sdmx_artefact.short_urn == "DataStructure=SDMX:POP(1.0.0)"
    assert pop_m.sdmx_urn == (
        f"{BASE}datastructure.DataStructure=SDMX:POP(1.0.0)"
    )
    sdmx_exec, example_exec = msg.get_vtl_executions()
    assert sdmx_exec.short_urn == "VtlExecution=SDMX:EXEC_POPRATIO(1.0.0)"
    assert example_exec.short_urn == "VtlExecution=EXAMPLE:EXEC_POPRATIO(1.0)"
    assert [e.context for e in sdmx_exec.extractions] == [None, None]
    context = example_exec.extractions[0].context
    assert context == msg.get_dataflow("Dataflow=EXAMPLE:DF_POP(1.0)")
    assert example_exec.extractions[0].context_urn == (
        f"{BASE}datastructure.Dataflow=EXAMPLE:DF_POP(1.0)"
    )


def test_codelist_mapping_and_viral_propagation():
    msg = read_sdmx(SAMPLES / "VTL_Sample_6.xml")

    mappings = msg.get_vtl_mapping_schemes()[0].items
    assert [type(m) for m in mappings] == [VtlDatasetMapping] * 4 + [
        VtlCodelistMapping
    ]
    cl_area = mappings[-1]
    assert cl_area.id == "CL_AREA"
    assert cl_area.vtl_alias == "cl_area"
    assert cl_area.codelist_alias == "cl_area"
    assert isinstance(cl_area.codelist, Codelist)
    assert cl_area.sdmx_urn == f"{BASE}codelist.Codelist=SDMX:CL_AREA(2.0)"
    ruleset = msg.get_ruleset_schemes()[0].items[0]
    assert ruleset.ruleset_type == "viral"
    assert ruleset.ruleset_scope == "variable"
    assert msg.get_transformation_schemes()[0].vtl_version == "2.2"


def test_deprecated_mappings():
    msg = read_sdmx(SAMPLES / "deprecated-VTL_Sample_3.xml")

    mappings = msg.get_vtl_mapping_schemes()[0].items
    assert [type(m) for m in mappings] == [VtlDataflowMapping] * 2
    assert [m.vtl_alias for m in mappings] == ["DF3R1", "DF31"]
    assert [m.dataflow_alias for m in mappings] == ["DF3R1", "DF31"]
    assert mappings[1].to_vtl_mapping_method.to_vtl_sub_space == (
        "INDICATOR",
        "COUNTRY",
    )


def test_references_to_artefacts_not_in_the_message():
    text = (SAMPLES / "VTL_Sample_5.xml").read_text()
    start = text.index("<str:VtlMappingSchemes>")
    end = text.index("<str:TransformationSchemes>")
    end_ts = text.index("<str:VtlExecutions>")
    head = text[: text.index("<str:AgencySchemes>")]
    only_vtl = head + text[start:end] + text[end_ts:]

    structures = read(only_vtl)

    scheme, sdmx_exec, example_exec = structures
    assert scheme.items[0].sdmx_artefact == Reference(
        "DataStructure", "SDMX", "POP", "1.0.0"
    )
    assert sdmx_exec.transformation_scheme == Reference(
        "TransformationScheme", "SDMX", "TS_POPRATIO", "1.0.0"
    )
    assert example_exec.extractions[0].context == Reference(
        "Dataflow", "EXAMPLE", "DF_POP", "1.0"
    )


def test_invalid_message_is_rejected():
    text = (SAMPLES / "VTL_Sample_4.xml").read_text()
    invalid = text.replace(' isInput="true"', "", 1)

    with pytest.raises(Invalid, match="isInput"):
        read_sdmx(invalid)


def test_not_a_structure_message():
    text = (SAMPLES / "VTL_Sample_4.xml").read_text()
    not_structure = text.replace("mes:Structure ", "mes:Other ", 1).replace(
        "</mes:Structure>", "</mes:Other>"
    )

    with pytest.raises(Invalid, match="not SDMX-ML 3.2 Structure"):
        read(not_structure, validate=False)
