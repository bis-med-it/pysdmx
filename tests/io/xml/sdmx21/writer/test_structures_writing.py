from datetime import datetime
from pathlib import Path

import pytest

from pysdmx.errors import NotImplemented
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.xml.enums import MessageType
from pysdmx.io.xml.sdmx21.reader import read_xml
from pysdmx.io.xml.sdmx21.writer import Header, writer
from pysdmx.model import Agency, Code, Codelist, Concept, ConceptScheme
from pysdmx.model.__base import Annotation
from pysdmx.model.dataflow import Dataflow, DataStructureDefinition, Components

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
def read_write_sample():
    base_path = Path(__file__).parent / "samples" / "read_write_sample.xml"
    with open(base_path, "r") as f:
        return f.read()


@pytest.fixture()
def header():
    return Header(
        id="ID",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
    )


@pytest.fixture()
def complete_header():
    return Header(
        id="ID",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        sender="ZZZ",
        receiver="Not_Supplied",
        source="PySDMX",
    )


@pytest.fixture()
def read_write_header():
    return Header(
        id="DF1605144905",
        prepared=datetime.strptime("2021-03-05T14:11:16", "%Y-%m-%dT%H:%M:%S"),
        sender="Unknown",
        receiver="Not_Supplied",
    )


@pytest.fixture()
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


@pytest.fixture()
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


@pytest.fixture()
def datastructure():
    return DataStructureDefinition(
        agency="BIS",
        annotations=(),
        id="BIS_DER",
        components=Components([]),
        description="BIS derivates statistics",
        is_external_reference=False,
        is_final=False,
        name="BIS derivates statistics",
        service_url=None,
        structure_url=None,
        uri="http://www.bis.org/statistics/derivatives.html",
        urn="urn:sdmx:org.sdmx.infomodel.datastructure."
        "DataStructure=BIS:BIS_DER(1.0)",
        valid_from=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        valid_to=datetime.strptime("2021-12-31", "%Y-%m-%d"),
        version="1.0",
    )


@pytest.fixture()
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


@pytest.fixture()
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
        structure="Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)",
        structure_url=None,
        uri=None,
        urn="urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)",
        valid_from=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        valid_to=datetime.strptime("2021-12-31", "%Y-%m-%d"),
        version="1.0",
    )


def test_codelist(codelist_sample, complete_header, codelist):
    result = writer(
        {"Codelists": {"CL_FREQ": codelist}},
        MessageType.Structure,
        header=complete_header,
    )

    assert result == codelist_sample


def test_concept(concept_sample, complete_header, concept):
    result = writer(
        {"Concepts": {"FREQ": concept}},
        MessageType.Structure,
        header=complete_header,
    )

    assert result == concept_sample


def test_writer_empty(empty_sample, header):
    result = writer({}, MessageType.Structure, prettyprint=True, header=header)
    assert result == empty_sample


def test_writing_not_supported():
    with pytest.raises(
        NotImplemented, match="Only Metadata messages are supported"
    ):
        writer({}, MessageType.Error, prettyprint=True)


def test_write_to_file(empty_sample, tmpdir, header):
    file = tmpdir.join("output.txt")
    result = writer(
        {},
        MessageType.Structure,
        path=file.strpath,
        prettyprint=True,
        header=header,
    )  # or use str(file)
    assert file.read() == empty_sample
    assert result is None


def test_writer_no_header():
    result: str = writer({}, MessageType.Structure, prettyprint=False)
    assert "<mes:Header>" in result
    assert "<mes:ID>" in result
    assert "<mes:Test>true</mes:Test>" in result
    assert "<mes:Prepared>" in result
    assert '<mes:Sender id="ZZZ"/>' in result


def test_writer_datastructure(complete_header, datastructure):
    result = writer(
        {"DataStructures": {"FREQ": datastructure}},
        MessageType.Structure,
        header=complete_header,
        prettyprint=True,
    )

    assert "DataStructure=BIS:BIS_DER(1.0)" in result


def test_writer_partial_datastructure(complete_header, partial_datastructure):
    result = writer(
        {"DataStructures": {"FREQ": partial_datastructure}},
        MessageType.Structure,
        header=complete_header,
        prettyprint=True,
    )

    assert "DataStructure=BIS:BIS_DER(1.0)" in result


def test_writer_dataflow(complete_header, dataflow):
    result = writer(
        {"Dataflows": {"FREQ": dataflow}},
        MessageType.Structure,
        header=complete_header,
        prettyprint=True,
    )

    assert "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)" in result


def test_read_write(read_write_sample, read_write_header):
    content, filetype = process_string_to_read(read_write_sample)
    assert filetype == "xml"
    read_result = read_xml(content, validate=True)
    write_result = writer(
        read_result,
        MessageType.Structure,
        header=read_write_header,
        prettyprint=True,
    )

    assert write_result == content


def test_write_read(complete_header, datastructure, dataflow):
    content = {
        "DataStructures": {"DataStructure=BIS:BIS_DER(1.0)": datastructure},
        "Dataflows": {"Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)": dataflow},
    }

    write_result = writer(
        content,
        MessageType.Structure,
        header=complete_header,
        prettyprint=True,
    )

    read_result = read_xml(write_result)

    assert content == read_result
