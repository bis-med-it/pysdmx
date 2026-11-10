from datetime import datetime, timezone
from pathlib import Path

import pytest

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx, write_sdmx
from pysdmx.io.format import Format
from pysdmx.io.xml.sdmx32.writer.structure import write
from pysdmx.model import (
    DataflowRef,
    ItemReference,
    QueryExtraction,
    QueryParameter,
    Reference,
    TransformationScheme,
    UrlExtraction,
    VtlCodelistMapping,
    VtlDataflowMapping,
    VtlDatasetMapping,
    VtlExecution,
    VtlMappingScheme,
)
from pysdmx.model.message import Header

READER_SAMPLES = Path(__file__).parents[1] / "reader" / "samples"
SAMPLES = Path(__file__).parent / "samples"
BASE = "urn:sdmx:org.sdmx.infomodel."


@pytest.fixture
def header():
    return Header(
        id="ID",
        prepared=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
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
                sdmx_artefact=Reference("DataStructure", "AG", "DSD", "1.0"),
            ),
            VtlDatasetMapping(
                id="DS_B",
                name="Input B",
                description="Mapped to a Dataflow",
                vtl_alias="ds_b",
                is_input=True,
                sdmx_artefact=Reference("Dataflow", "AG", "DF_B", "1.0"),
            ),
            VtlDatasetMapping(
                id="DS_R",
                name="Result",
                vtl_alias="ds_r",
                is_input=False,
                sdmx_artefact=Reference(
                    "ProvisionAgreement", "AG", "PA_R", "1.0"
                ),
            ),
            VtlCodelistMapping(
                id="CL_AREA",
                name="Areas",
                vtl_alias="cl_area",
                codelist=Reference("Codelist", "AG", "CL_AREA", "1.0"),
            ),
            VtlDataflowMapping(
                id="OLD",
                name="Deprecated mapping",
                dataflow_alias="old",
                dataflow=DataflowRef(agency="AG", id="DF_OLD"),
            ),
        ),
    )


@pytest.fixture
def execution():
    return VtlExecution(
        id="EXEC",
        agency="AG",
        name="Execution",
        transformation_scheme=Reference(
            "TransformationScheme", "AG", "TS", "1.0"
        ),
        extractions=(
            QueryExtraction(
                dataset_mapping=ItemReference(
                    "VtlDatasetMapping", "AG", "VMS", "1.0", "DS_A"
                ),
                entry_point="https://sdmx.example.org/rest?a=1&b=2",
                sdmx_api_version="2.1",
                context=Reference("ProvisionAgreement", "AG", "PA_A", "1.0"),
                parameters=(
                    QueryParameter(name="key", value="A.B", is_fixed=True),
                    QueryParameter(
                        name="c[OBS_STATUS]",
                        value="\"A\" & 'B' < C",
                        is_fixed=False,
                    ),
                    QueryParameter(name="updatedAfter", is_fixed=False),
                ),
            ),
            QueryExtraction(
                dataset_mapping=ItemReference(
                    "VtlDatasetMapping", "AG", "VMS", "1.0", "DS_B"
                ),
                entry_point="https://sdmx.example.org/rest",
            ),
            UrlExtraction(
                dataset_mapping=ItemReference(
                    "VtlDatasetMapping", "AG", "VMS", "1.0", "DS_C"
                ),
                url_template="https://example.org/{flow}?from={start}&x=1",
                parameters=(
                    QueryParameter(name="flow", value="DF", is_fixed=True),
                    QueryParameter(name="start", is_fixed=False),
                ),
            ),
        ),
    )


@pytest.mark.parametrize(
    "sample",
    [
        "VTL_Sample_4.xml",
        "VTL_Sample_5.xml",
        "VTL_Sample_6.xml",
    ],
)
def test_samples_are_written_as_read(sample):
    structures = read_sdmx(READER_SAMPLES / sample).structures

    written = write_sdmx(structures, Format.STRUCTURE_SDMX_ML_3_2)

    assert read_sdmx(written).structures == structures


def test_mappings_and_execution(header, mapping_scheme, execution):
    expected = (SAMPLES / "vtl_mappings_and_execution.xml").read_text()

    written = write([mapping_scheme, execution], header=header)

    assert written == expected
    msg = read_sdmx(written)
    assert msg.get_vtl_mapping_schemes()[0].items == mapping_scheme.items
    read_execution = msg.get_vtl_executions()[0]
    assert read_execution.extractions == execution.extractions
    assert read_execution.transformation_scheme == (
        execution.transformation_scheme
    )


def test_references_given_as_urn(header, mapping_scheme, execution):
    ds_a, *others = mapping_scheme.items
    with_urns = [
        VtlMappingScheme(
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
                *others,
            ),
        ),
        VtlExecution(
            id="EXEC",
            agency="AG",
            name="Execution",
            transformation_scheme=(
                f"{BASE}transformation.TransformationScheme=AG:TS(1.0)"
            ),
            extractions=(
                QueryExtraction(
                    dataset_mapping=(
                        f"{BASE}transformation.VtlDatasetMapping=AG:VMS(1.0).DS_A"
                    ),
                    entry_point="https://sdmx.example.org/rest?a=1&b=2",
                    sdmx_api_version="2.1",
                    context=f"{BASE}registry.ProvisionAgreement=AG:PA_A(1.0)",
                    parameters=execution.extractions[0].parameters,
                ),
                *execution.extractions[1:],
            ),
        ),
    ]

    written = write(with_urns, header=header)

    assert written == write([mapping_scheme, execution], header=header)


def test_compact_message(mapping_scheme, execution):
    written = write([mapping_scheme, execution], prettyprint=False)

    assert "\n" not in written
    assert read_sdmx(written).get_vtl_executions()[0].id == "EXEC"


def test_write_to_file(tmp_path, header, execution):
    path = tmp_path / "execution.xml"

    result = write([execution], output_path=path, header=header)

    assert result is None
    assert path.read_text() == write([execution], header=header)


def test_dataset_mapping_needs_sdmx_ml_3_2(mapping_scheme):
    with pytest.raises(Invalid, match="VtlDatasetMapping cannot be written"):
        write_sdmx([mapping_scheme], Format.STRUCTURE_SDMX_ML_3_1)


def test_execution_needs_sdmx_ml_3_2(execution):
    with pytest.raises(Invalid, match="VtlExecution cannot be written"):
        write_sdmx([execution], Format.STRUCTURE_SDMX_ML_3_1)


def test_vtl_version_is_mandatory():
    scheme = TransformationScheme(id="TS", agency="AG", name="Program")

    with pytest.raises(Invalid, match="must have a VTL version"):
        write([scheme])
