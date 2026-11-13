import json
from pathlib import Path

import msgspec
import pytest

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx, write_sdmx
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.json.sdmxjson2.messages.vtl import (
    JsonVtlDatasetMapping,
    JsonVtlExecution,
)
from pysdmx.io.json.sdmxjson2.writer.v2_2.structure import write
from pysdmx.model import (
    QueryExtraction,
    QueryParameter,
    RulesetScheme,
    TransformationScheme,
    UrlExtraction,
    VtlCodelistMapping,
    VtlDataflowMapping,
    VtlDatasetMapping,
    VtlExecution,
    VtlMappingScheme,
)

SAMPLES = Path(__file__).parent / "deser" / "samples" / "vtl"
BASE = "urn:sdmx:org.sdmx.infomodel."
DS_A = f"{BASE}transformation.VtlDatasetMapping=EXAMPLE:VTL_MAP(1.0).DS_A"
DS_B = f"{BASE}transformation.VtlDatasetMapping=EXAMPLE:VTL_MAP(1.0).DS_B"
SCHEMA_2_2 = "https://json.sdmx.org/2.2/sdmx-json-structure-schema.json"
VTL_ARTEFACTS = (
    RulesetScheme,
    TransformationScheme,
    VtlExecution,
    VtlMappingScheme,
)


@pytest.fixture
def mapping_scheme():
    return VtlMappingScheme(
        id="VMS",
        agency="AG",
        name="Mappings",
        items=(
            VtlDatasetMapping(
                id="DS_A",
                name="Input A",
                vtl_alias="ds_a",
                is_input=True,
                sdmx_artefact=f"{BASE}datastructure.DataStructure=AG:DSD(1.0)",
            ),
            VtlDatasetMapping(
                id="DS_R",
                name="Result",
                vtl_alias="ds_r",
                is_input=False,
                sdmx_artefact=f"{BASE}registry.ProvisionAgreement=AG:PA(1.0)",
            ),
            VtlCodelistMapping(
                id="CL_AREA",
                name="Areas",
                vtl_alias="cl_area",
                codelist=f"{BASE}codelist.Codelist=AG:CL_AREA(1.0)",
            ),
        ),
    )


@pytest.fixture
def execution():
    return VtlExecution(
        id="EXEC",
        agency="AG",
        name="Execution",
        transformation_scheme=(
            f"{BASE}transformation.TransformationScheme=AG:TS(1.0)"
        ),
        extractions=(
            UrlExtraction(
                dataset_mapping=(
                    f"{BASE}transformation.VtlDatasetMapping=AG:VMS(1.0).DS_A"
                ),
                url_template="https://example.org/data",
            ),
        ),
    )


def test_sdmx_json_2_2_structure_is_detected():
    _, read_format = process_string_to_read(SAMPLES / "vtl-sample-4.json")

    assert read_format == Format.STRUCTURE_SDMX_JSON_2_2_0


def test_dataset_mappings_and_execution():
    msg = read_sdmx(SAMPLES / "vtl-sample-4.json")

    mappings = msg.get_vtl_mapping_schemes()[0].items
    assert [type(m) for m in mappings] == [VtlDatasetMapping] * 3
    assert [m.vtl_alias for m in mappings] == ["ds_a", "ds_b", "ds_diff"]
    assert [m.is_input for m in mappings] == [True, True, False]
    assert mappings[0].name == "Trade in goods - source A"
    assert mappings[0].sdmx_artefact == (
        f"{BASE}datastructure.Dataflow=EXAMPLE:DF_A(1.0)"
    )
    execution = msg.get_vtl_executions()[0]
    assert execution.short_urn == "VtlExecution=EXAMPLE:EXEC_DIFF(1.0)"
    assert execution.transformation_scheme == (
        f"{BASE}transformation.TransformationScheme=EXAMPLE:TS_DIFF(1.0)"
    )
    assert execution.extractions == (
        QueryExtraction(
            dataset_mapping=DS_A,
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
            dataset_mapping=DS_B,
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


def test_context_of_query_extractions():
    sample = json.loads((SAMPLES / "vtl-sample-5.json").read_text())

    sdmx_exec, example_exec = [
        msgspec.convert(e, JsonVtlExecution).to_model()
        for e in sample["data"]["vtlExecutions"]
    ]

    assert [e.context for e in sdmx_exec.extractions] == [None, None]
    assert [e.context for e in example_exec.extractions] == [
        f"{BASE}datastructure.Dataflow=EXAMPLE:DF_POP(1.0)"
    ] * 2


def test_codelist_mapping_and_viral_propagation():
    msg = read_sdmx(SAMPLES / "vtl-sample-6.json")

    mappings = msg.get_vtl_mapping_schemes()[0].items
    assert [type(m) for m in mappings] == [VtlDatasetMapping] * 4 + [
        VtlCodelistMapping
    ]
    assert mappings[-1].vtl_alias == "cl_area"
    assert mappings[-1].codelist_alias == "cl_area"
    assert mappings[-1].sdmx_urn == (
        f"{BASE}codelist.Codelist=SDMX:CL_AREA(2.0)"
    )
    assert msg.get_ruleset_schemes()[0].items[0].ruleset_type == "viral"


def test_deprecated_mappings():
    msg = read_sdmx(SAMPLES / "deprecated-vtl-sample-3.json")

    mappings = msg.get_vtl_mapping_schemes()[0].items
    assert [type(m) for m in mappings] == [VtlDataflowMapping] * 2
    assert [m.vtl_alias for m in mappings] == ["DF3R1", "DF31"]


@pytest.mark.parametrize("sample", ["vtl-sample-4.json", "vtl-sample-6.json"])
def test_vtl_artefacts_of_samples_are_written_as_read(sample):
    msg = read_sdmx(SAMPLES / sample)
    structures = [s for s in msg.structures if isinstance(s, VTL_ARTEFACTS)]

    written = write_sdmx(structures, Format.STRUCTURE_SDMX_JSON_2_2_0)

    assert json.loads(written)["meta"]["schema"] == SCHEMA_2_2
    _, read_format = process_string_to_read(written)
    assert read_format == Format.STRUCTURE_SDMX_JSON_2_2_0
    assert list(read_sdmx(written).structures) == structures


def test_mappings_and_execution_are_written(mapping_scheme, execution):
    written = json.loads(write([mapping_scheme, execution]))

    scheme = written["data"]["vtlMappingSchemes"][0]
    assert "vtlMappings" not in scheme
    assert scheme["vtlDatasetMappings"] == [
        {
            "id": "DS_A",
            "name": "Input A",
            "vtlAlias": "ds_a",
            "isInput": True,
            "dataStructure": f"{BASE}datastructure.DataStructure=AG:DSD(1.0)",
        },
        {
            "id": "DS_R",
            "name": "Result",
            "vtlAlias": "ds_r",
            "isInput": False,
            "provisionAgreement": (
                f"{BASE}registry.ProvisionAgreement=AG:PA(1.0)"
            ),
        },
    ]
    assert scheme["vtlCodelistMappings"] == [
        {
            "id": "CL_AREA",
            "name": "Areas",
            "vtlAlias": "cl_area",
            "codelist": f"{BASE}codelist.Codelist=AG:CL_AREA(1.0)",
        }
    ]
    assert written["data"]["vtlExecutions"] == [
        {
            "agencyID": "AG",
            "id": "EXEC",
            "name": "Execution",
            "version": "1.0",
            "transformationScheme": (
                f"{BASE}transformation.TransformationScheme=AG:TS(1.0)"
            ),
            "urlExtractions": [
                {
                    "datasetMapping": (
                        f"{BASE}transformation.VtlDatasetMapping="
                        "AG:VMS(1.0).DS_A"
                    ),
                    "urlTemplate": "https://example.org/data",
                }
            ],
        }
    ]


def test_codelist_mapping_in_sdmx_json_2_1(mapping_scheme):
    cl_area = mapping_scheme.items[-1]
    scheme = VtlMappingScheme(
        id="VMS", agency="AG", name="Mappings", items=[cl_area]
    )

    written = write_sdmx([scheme], Format.STRUCTURE_SDMX_JSON_2_1_0)

    mappings = json.loads(written)["data"]["vtlMappingSchemes"][0]
    assert mappings["vtlMappings"][0]["alias"] == "cl_area"
    assert "vtlCodelistMappings" not in mappings


def test_dataset_mapping_needs_sdmx_json_2_2(mapping_scheme):
    with pytest.raises(Invalid, match="Unsupported VTL mapping type"):
        write_sdmx([mapping_scheme], Format.STRUCTURE_SDMX_JSON_2_1_0)


def test_execution_needs_sdmx_json_2_2(execution):
    with pytest.raises(Invalid, match="VtlExecution cannot be written"):
        write_sdmx([execution], Format.STRUCTURE_SDMX_JSON_2_1_0)


def test_vtl_version_is_mandatory():
    scheme = TransformationScheme(id="TS", agency="AG", name="Program")

    with pytest.raises(Invalid, match="must have a VTL version"):
        write([scheme])


def test_mapping_needs_a_name():
    mapping = VtlDatasetMapping(
        id="DS",
        vtl_alias="ds",
        is_input=True,
        sdmx_artefact=f"{BASE}datastructure.Dataflow=AG:DF(1.0)",
    )
    scheme = VtlMappingScheme(
        id="VMS", agency="AG", name="Mappings", items=[mapping]
    )

    with pytest.raises(Invalid, match="must have a name"):
        write([scheme])


def test_codelist_mapping_needs_a_codelist():
    mapping = VtlCodelistMapping(id="CL", name="Codelist", vtl_alias="cl")
    scheme = VtlMappingScheme(
        id="VMS", agency="AG", name="Mappings", items=[mapping]
    )

    with pytest.raises(Invalid, match="must reference a codelist"):
        write([scheme])


def test_dataset_mapping_without_artefact_is_rejected():
    mapping = JsonVtlDatasetMapping(
        id="DS", name="Dataset", vtlAlias="ds", isInput=True
    )

    with pytest.raises(Invalid, match="Data Structure Definition, Dataflow"):
        mapping.to_model()


def test_stub_of_an_execution():
    stub = VtlExecution(
        id="EXEC", agency="AG", name="Stub", is_external_reference=True
    )

    written = write([stub])

    assert "transformationScheme" not in written
    read_stub = read_sdmx(written, validate=False).get_vtl_executions()[0]
    assert read_stub.is_external_reference is True
    assert read_stub.transformation_scheme is None
    assert read_stub.extractions == ()
