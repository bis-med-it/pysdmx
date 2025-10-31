from datetime import datetime
from pathlib import Path

import pytest

from pysdmx.io.xml.__write_aux import (
    __write_header as write_header_aux,
)
from pysdmx.model import Organisation
from pysdmx.model.message import Header


@pytest.fixture
def header():
    return Header(
        id="ID",
        test="true",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        sender=Organisation(
            id="ZZZ",
            name="unknown",
        ),
        receiver=[Organisation(id="AR2"), Organisation(id="UY2")],
        source=None,
        dataset_action=None,
        structure={"DataStructure=MD:TEST(1.0)": "AllDimensions"},
        dataset_id=None,
    )


@pytest.fixture
def header_no_name():
    return Header(
        id="ID",
        test="true",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        sender=Organisation(
            id="ZZZ",
            uri=None,
            urn=None,
            name=None,
            description=None,
            contacts=(),
            dataflows=(),
            annotations=(),
        ),
        receiver=None,
        source=None,
        dataset_action=None,
        structure={"DataStructure=MD:TEST(1.0)": "AllDimensions"},
        dataset_id=None,
    )


@pytest.fixture
def header_warning():
    return Header(
        id="ID",
        test="true",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        sender=Organisation(
            id="ZZZ",
        ),
        receiver=Organisation(
            id="ZZZ",
            name="unknown",
            description="Description",
        ),
        source=None,
        dataset_action=None,
        structure={"DataStructure=MD:TEST(1.0)": "AllDimensions"},
        dataset_id=None,
    )


@pytest.fixture
def header_structure_usage():
    return Header(
        id="ID",
        test="true",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        sender=Organisation(
            id="ZZZ",
        ),
        receiver=Organisation(
            id="ZZZ",
            name="unknown",
        ),
        source=None,
        dataset_action=None,
        structure={"Dataflow=MD:TEST(1.0)": "AllDimensions"},
        dataset_id=None,
    )


@pytest.fixture
def header_provision_agrement():
    return Header(
        id="ID",
        test="true",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        sender=Organisation(
            id="ZZZ",
        ),
        receiver=Organisation(
            id="ZZZ",
            name="unknown",
        ),
        source=None,
        dataset_action=None,
        structure={"ProvisionAgrement=MD:TEST(1.0)": "AllDimensions"},
        dataset_id=None,
    )


@pytest.fixture
def samples_folder():
    return Path(__file__).parent / "samples"


def test_write_header(header, samples_folder):
    file_path = samples_folder / "header.xml"
    header = write_header_aux(header, False, False, True)
    with open(file_path, "r") as f:
        expected = f.read()
    assert header == expected


def test_write_header_no_name(header_no_name, samples_folder):
    file_path = samples_folder / "header_no_name.xml"
    header = write_header_aux(header_no_name, False, False, True)
    with open(file_path, "r") as f:
        expected = f.read()
    assert header == expected


def test_write_header_namespace(header_no_name, samples_folder):
    file_path = samples_folder / "header_namespace.xml"
    header = write_header_aux(header_no_name, False, True, True)
    with open(file_path, "r") as f:
        expected = f.read()
    assert header == expected


def test_write_header_warning(header_warning, samples_folder, recwarn):
    file_path = samples_folder / "header_warning.xml"
    header = write_header_aux(header_warning, False, False, True)
    with open(file_path, "r") as f:
        expected = f.read()
    assert header == expected
    assert len(recwarn) == 1


def test_write_header_structure_usage(header_structure_usage, samples_folder):
    file_path = samples_folder / "header_structure_usage.xml"
    header = write_header_aux(header_structure_usage, True, False, True)
    with open(file_path, "r") as f:
        expected = f.read()
    assert header == expected


def test_write_header_provision_agreement(
    header_provision_agrement, samples_folder
):
    file_path = samples_folder / "header_provision_agrement.xml"
    header = write_header_aux(header_provision_agrement, True, False, True)
    with open(file_path, "r") as f:
        expected = f.read()
    assert header == expected
