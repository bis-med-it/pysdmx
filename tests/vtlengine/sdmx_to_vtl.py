from pathlib import Path

import pytest
import requests
from vtlengine import run

from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.xml.sdmx21.reader import read_xml


data_path = "data"
input_data_path = Path(__file__).parent / data_path / "input_data"
vtl_data_path = Path(__file__).parent / data_path / "vtl"


def read_sdmx_from_url(url: str):
    response = requests.get(url, timeout=10)
    xml_content = response.content
    xml_str = xml_content.decode("utf-8")

    return xml_str


def read_sample(path: Path):
    with open(path, "r") as f:
        return f.read()


@pytest.fixture()
def bis_metadata_sample():
    url = (
        "https://stats.bis.org/api/v1/dataflow/BIS/WS_CBS_PUB/1.0?"
        "references=descendants&detail=full"
    )
    return read_sdmx_from_url(url)


@pytest.fixture()
def bis_data_sample():
    url = (
        "https://stats.bis.org/api/v1/data/BIS%2CWS_CBS_PUB%2C1.0/all/all?"
        "startPeriod=2024-Q1&detail=full"
    )
    return read_sdmx_from_url(url)


@pytest.fixture()
def bis_script_sample():
    base_path = vtl_data_path / "bis_script.vtl"
    return read_sample(base_path)


def test_sdmx_to_vtl(bis_metadata_sample, bis_data_sample, bis_script_sample):
    meta_content, filetype = process_string_to_read(bis_metadata_sample)
    if filetype != "xml":
        raise ValueError("Invalid file type")
    metadata_result = read_xml(meta_content, validate=True)
    data_structure = metadata_result["DataStructures"][
        "DataStructure=BIS:BIS_CBS(1.0)"
    ]

    data_content, filetype = process_string_to_read(bis_data_sample)
    if filetype != "xml":
        raise ValueError("Invalid file type")
    data_result = read_xml(data_content, validate=True)

    def change_component_type(ds, component_name, new_type):
        for component in ds["datasets"][0]["DataStructure"]:
            if component["name"] == component_name:
                component["type"] = new_type
        return ds

    vtl_data_structure = data_structure.to_vtl_json()
    vtl_data_structure = change_component_type(
        vtl_data_structure, "OBS_VALUE", "Number"
    )
    datapoints = {"BIS_CBS": data_result["DataFlow=BIS:WS_CBS_PUB(1.0)"].data}

    run_result = run(
        script=bis_script_sample,
        data_structures=vtl_data_structure,
        datapoints=datapoints,
        return_only_persistent=True,
    )

    print(run_result)

    # Reference data_sample comparison WIP
    assert True
