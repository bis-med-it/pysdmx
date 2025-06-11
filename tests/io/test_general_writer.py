import os
from pathlib import Path

import pytest

from pysdmx.io import read_sdmx
from pysdmx.io.format import Format
from pysdmx.model import Component, Components, Concept, Role, Schema
from src.pysdmx.io.writer import write

CSV_1_0_PATH = Path("csv") / "sdmx10" / "reader"
CSV_2_0_PATH = Path("csv") / "sdmx20" / "reader"
XML_2_1_PATH = Path("xml") / "sdmx21" / "reader"

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
                    role=Role.DIMENSION
                    if id_ in DIMENSIONS
                    else Role.ATTRIBUTE
                    if id_ in ATTRIBUTES
                    else Role.MEASURE,
                    concept=Concept(id=id_),
                    required=True,
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
    return read_sdmx(data_path_reference)


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
    ],
)
def test_write(
    format_, test_path, reference_file, params, reference, output_path
):
    data = reference.data if reference.data else reference.structures
    if format_ == Format.DATA_SDMX_ML_2_1_GEN:
        data[0].structure = GEN_STRUCTURE[0]
    params["header"] = reference.header

    write(data, output_path=str(output_path), format_=format_, **params)
    assert output_path.exists(), f"Output file {output_path} was not created."

    written_content = read_sdmx(output_path)
    os.remove(output_path)

    assert written_content is not None, "Written content should not be None."
    assert written_content.header == reference.header, "Headers do not match."
    for actual, ref in zip(written_content.data, reference.data):
        actual.data.equals(ref.data), "Data does not match reference."
