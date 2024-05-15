from datetime import datetime
from pathlib import Path

import pytest

from pysdmx.errors import ClientError
from pysdmx.model import Agency, Code, Codelist, Concept, ConceptScheme
from pysdmx.model.__base import Annotation
from pysdmx.model.message import MessageType
from pysdmx.writers.write import Header, writer

TEST_CS_URN = (
    "urn:sdmx:org.sdmx.infomodel.conceptscheme."
    "ConceptScheme=BIS:CS_FREQ(1.0)"
)


@pytest.fixture()
def codelist_sample():
    base_path = Path(__file__).parent / "samples" / "codelist.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture()
def concept_sample():
    base_path = Path(__file__).parent / "samples" / "concept.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture()
def empty_sample():
    base_path = Path(__file__).parent / "samples" / "empty.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture()
def header():
    return Header(
        id="ID",
        sender="Unknown",
        receiver="Not_Supplied",
        source="PySDMX",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
    )


def test_codelist(codelist_sample, header):
    codelist = Codelist(
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

    result = writer(
        {"Codelists": {"CL_FREQ": codelist}},
        MessageType.Metadata,
        header=header,
    )

    assert result == codelist_sample


def test_concept(concept_sample, header):
    concept = ConceptScheme(
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

    result = writer(
        {"Concepts": {"FREQ": concept}},
        MessageType.Metadata,
        header=header,
    )

    assert result == concept_sample


def test_header_exception():
    with pytest.raises(
        ClientError, match="The Test value must be either 'true' or 'false'"
    ):
        Header(
            id="ID",
            sender="Unknown",
            receiver="Not_Supplied",
            source="PySDMX",
            prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
            test="WRONG TEST VALUE",
        )


def test_writer_empty(empty_sample):
    result = writer({}, MessageType.Metadata, prettyprint=True)
    assert result == empty_sample


def test_writing_not_supported():
    with pytest.raises(
        NotImplementedError, match="Only Metadata messages are supported"
    ):
        writer({}, MessageType.Error, prettyprint=True)


def test_write_to_file(empty_sample, tmpdir):
    file = tmpdir.join("output.txt")
    result = writer(
        {}, MessageType.Metadata, path=file.strpath, prettyprint=True
    )  # or use str(file)
    assert file.read() == empty_sample
    assert result is None
