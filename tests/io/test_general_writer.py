from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx
from pysdmx.io.format import Format
from pysdmx.io.pd import PandasDataset
from pysdmx.io.writer import write_sdmx
from pysdmx.model import Component, Components, Concept, Role, Schema

CSV_1_0_PATH = Path(__file__).parent / "csv" / "sdmx10" / "reader"
CSV_2_0_PATH = Path(__file__).parent / "csv" / "sdmx20" / "reader"
XML_2_1_PATH = Path(__file__).parent / "xml" / "sdmx21" / "reader"
XML_3_0_PATH = Path(__file__).parent / "xml" / "sdmx30" / "reader"
XML_STR_PATH = Path(__file__).parent
JSN_2_0_PATH = Path(__file__).parent.parent / "api" / "fmr"

DIMENSIONS = [
    "FREQ",
    "DER_TYPE",
    "DER_INSTR",
    "DER_RISK",
    "DER_REP_CTY",
    "DER_SECTOR_CPY",
    "DER_CPC",
    "DER_SECTOR_UDL",
    "DER_CURR_LEG1",
    "DER_CURR_LEG2",
    "DER_ISSUE_MAT",
    "DER_RATING",
    "DER_EX_METHOD",
    "DER_BASIS",
    "TIME_PERIOD",
]

ATTRIBUTES = ["AVAILABILITY", "COLLECTION", "OBS_STATUS", "OBS_CONF"]

MEASURES = ["OBS_VALUE"]

GEN_STRUCTURE = (
    Schema(
        context="datastructure",
        id="TEST",
        agency="MD",
        version="1.0",
        components=Components(
            [
                Component(
                    id=id_,
                    role=(
                        Role.DIMENSION
                        if id_ in DIMENSIONS
                        else (
                            Role.ATTRIBUTE
                            if id_ in ATTRIBUTES
                            else Role.MEASURE
                        )
                    ),
                    concept=Concept(id=id_),
                    required=True,
                    attachment_level="O" if id_ in ATTRIBUTES else None,
                )
                for id_ in DIMENSIONS + ATTRIBUTES + MEASURES
            ]
        ),
    ),
)


@pytest.fixture
def data_path_reference(test_path, reference_file):
    base_path = Path(__file__).parent / test_path / "samples" / reference_file
    return str(base_path)


@pytest.fixture
def reference(data_path_reference):
    return read_sdmx(data_path_reference, validate=False)


@pytest.fixture
def data_path_optional():
    base_path = Path(__file__).parent / "samples" / "df_optional.json"
    return str(base_path)


@pytest.fixture
def dsd_path():
    base_path = Path(__file__).parent / "samples" / "datastructure_for_csv.xml"
    return str(base_path)


@pytest.fixture
def csv_optionals():
    base_path = Path(__file__).parent / "samples" / "csv_optionals.csv"
    return str(base_path)


@pytest.fixture
def extension(format_):
    return (
        "csv"
        if format_ in [Format.DATA_SDMX_CSV_1_0_0, Format.DATA_SDMX_CSV_2_0_0]
        else "xml"
    )


@pytest.fixture
def output_path(extension, tmpdir):
    return tmpdir / f"output.{extension}"


@pytest.mark.parametrize(
    ("format_", "test_path", "reference_file", "params"),
    [
        (Format.DATA_SDMX_CSV_1_0_0, CSV_1_0_PATH, "data_v1.csv", {}),
        (Format.DATA_SDMX_CSV_2_0_0, CSV_2_0_PATH, "data_v2.csv", {}),
        (
            Format.DATA_SDMX_ML_2_1_GEN,
            XML_2_1_PATH,
            "gen_all.xml",
            {"dimension_at_observation": {}},
        ),
        (Format.DATA_SDMX_ML_2_1_STR, XML_2_1_PATH, "str_all.xml", {}),
        (Format.DATA_SDMX_ML_3_0, XML_3_0_PATH, "data_dataflow_3.0.xml", {}),
        (Format.STRUCTURE_SDMX_ML_2_1, XML_STR_PATH, "datastructure.xml", {}),
        (
            Format.STRUCTURE_SDMX_ML_3_0,
            XML_STR_PATH,
            "datastructure3_0.xml",
            {},
        ),
        (Format.STRUCTURE_SDMX_JSON_2_0_0, JSN_2_0_PATH, "code/freq.json", {}),
        (
            Format.REFMETA_SDMX_JSON_2_0_0,
            JSN_2_0_PATH,
            "refmeta/report.json",
            {},
        ),
    ],
)
def test_write_sdmx(
    format_, test_path, reference_file, params, reference, output_path
):
    if reference.reports:
        data = reference.reports
    elif reference.structures:
        data = reference.structures
    else:
        data = reference.data
    if format_ == Format.DATA_SDMX_ML_2_1_GEN:
        data[0].structure = GEN_STRUCTURE[0]
    params["header"] = reference.header

    write_sdmx(data, format_, str(output_path), **params)
    assert output_path.exists(), f"Output file {output_path} was not created."

    written_content = read_sdmx(output_path)

    assert written_content is not None, "Written content should not be None."
    assert written_content.header == reference.header, "Headers do not match."
    if reference.data:
        for actual, ref in zip(written_content.data, reference.data):
            actual.data.equals(ref.data), "Data does not match reference."
    elif reference.reports:
        assert written_content.reports == reference.reports, (
            "Metadata reports do not match reference."
        )
    else:
        assert written_content.structures == reference.structures, (
            "Structures do not match reference."
        )


@pytest.mark.parametrize(
    ("format_", "test_path", "reference_file", "params"),
    [
        (Format.STRUCTURE_SDMX_JSON_2_0_0, JSN_2_0_PATH, "code/freq.json", {}),
        (
            Format.REFMETA_SDMX_JSON_2_0_0,
            JSN_2_0_PATH,
            "refmeta/report.json",
            {},
        ),
    ],
)
def test_write_sdmx_no_header(
    format_, test_path, reference_file, params, reference, output_path
):
    if reference.reports:
        data = reference.reports
    elif reference.structures:
        data = reference.structures
    else:
        data = reference.data
    if format_ == Format.DATA_SDMX_ML_2_1_GEN:
        data[0].structure = GEN_STRUCTURE[0]
    params["header"] = None
    params["prettyprint"] = False

    write_sdmx(data, format_, Path(str(output_path)), **params)
    assert output_path.exists(), f"Output file {output_path} was not created."

    written_content = read_sdmx(output_path)

    assert written_content.header is not None, "The header is missing."
    assert written_content.header.sender.id == "ZZZ", "Unexpected sender."


@pytest.mark.parametrize(
    ("format_", "test_path", "reference_file", "params"),
    [
        (Format.STRUCTURE_SDMX_JSON_2_0_0, JSN_2_0_PATH, "code/freq.json", {}),
        (
            Format.REFMETA_SDMX_JSON_2_0_0,
            JSN_2_0_PATH,
            "refmeta/report.json",
            {},
        ),
    ],
)
def test_write_sdmx_no_output_file(
    format_, test_path, reference_file, params, reference, output_path
):
    if reference.reports:
        data = reference.reports
    elif reference.structures:
        data = reference.structures
    else:
        data = reference.data
    if format_ == Format.DATA_SDMX_ML_2_1_GEN:
        data[0].structure = GEN_STRUCTURE[0]
    params["header"] = None
    params["prettyprint"] = False

    out = write_sdmx(data, format_, **params)

    written_content = read_sdmx(out)

    assert written_content.header is not None, "The header is missing."
    assert written_content.header.sender.id == "ZZZ", "Unexpected sender."
    assert written_content is not None, "Written content should not be None."
    if reference.reports:
        assert written_content.reports == reference.reports, (
            "Metadata reports do not match reference."
        )
    else:
        assert written_content.structures == reference.structures, (
            "Structures do not match reference."
        )


def test_invalid_format(tmpdir):
    with pytest.raises(
        Invalid,
        match="No writer found for format",
    ):
        write_sdmx(
            sdmx_objects=[],
            sdmx_format=Format.ERROR_SDMX_ML_2_1,
            output_path=tmpdir / "output.invalid",
        )


def test_invalid_sdmx_object_data(tmpdir):
    with pytest.raises(
        Invalid,
        match="Only Datasets can be written to data formats",
    ):
        write_sdmx(
            sdmx_objects=GEN_STRUCTURE,
            sdmx_format=Format.DATA_SDMX_CSV_1_0_0,
            output_path=tmpdir / "output.invalid",
        )


def test_invalid_sdmx_object_structure(tmpdir):
    with pytest.raises(
        Invalid,
        match=(
            "Only maintainable artefacts can be written to structure formats."
        ),
    ):
        write_sdmx(
            sdmx_objects=PandasDataset(
                structure="DataStructure=MD:TEST_DSD(1.0)", data=pd.DataFrame()
            ),
            sdmx_format=Format.STRUCTURE_SDMX_ML_2_1,
            output_path=tmpdir / "output.invalid",
        )


def test_write_sdmx_csv_optionals(data_path_optional, dsd_path, csv_optionals):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    schema = dsd.to_schema()
    dataset = PandasDataset(
        attributes={},
        data=pd.read_json(data_path_optional, orient="records"),
        structure=schema,
    )
    result_csv = write_sdmx(
        sdmx_objects=[dataset],
        sdmx_format=Format.DATA_SDMX_CSV_2_1_0,
        labels="both",
        time_format="original",
        keys="both",
    )
    result_df = pd.read_csv(StringIO(result_csv)).astype(str)
    reference_df = pd.read_csv(csv_optionals).astype(str)
    pd.testing.assert_frame_equal(
        result_df.fillna("").replace("nan", ""),
        reference_df.replace("nan", ""),
        check_like=True,
    )


def test_invalid_sdmx_object_refmeta(tmpdir):
    with pytest.raises(
        Invalid,
        match=(
            "Only metadata reports can be written to "
            "reference metadata formats."
        ),
    ):
        write_sdmx(
            sdmx_objects=PandasDataset(
                structure="DataStructure=MD:TEST_DSD(1.0)", data=pd.DataFrame()
            ),
            sdmx_format=Format.REFMETA_SDMX_JSON_2_0_0,
            output_path=tmpdir / "output.invalid",
        )
