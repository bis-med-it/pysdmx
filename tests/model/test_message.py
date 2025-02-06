import pytest

from pysdmx.errors import Invalid, NotFound
from pysdmx.model import AgencyScheme
from pysdmx.model.code import Codelist
from pysdmx.model.concept import ConceptScheme
from pysdmx.model.dataflow import Components, Dataflow, DataStructureDefinition
from pysdmx.model.dataset import Dataset
from pysdmx.model.message import Message


def test_initialization():
    message = Message({}, {})
    assert message.structures == {}
    assert message.data == {}


def test_get_agency_scheme():
    org1 = AgencyScheme(id="orgs1", agency="org1")
    message = Message([org1])
    assert message.get_agency_schemes() == [org1]

    assert (
        message.get_organisation_scheme("AgencyScheme=org1:orgs1(1.0)") == org1
    )


def test_get_codelists():
    cl1 = Codelist(id="cl1", agency="cl1")
    message = Message([cl1])
    assert message.get_codelists() == [cl1]

    assert message.get_codelist("Codelist=cl1:cl1(1.0)") == cl1


def test_get_concepts():
    cs1 = ConceptScheme(id="cs1", agency="cs1")
    message = Message([cs1])
    assert message.get_concept_schemes() == [cs1]

    assert message.get_concept_scheme("ConceptScheme=cs1:cs1(1.0)") == cs1


def test_get_data_structure_definitions():
    dsd1 = DataStructureDefinition(
        id="dsd1", agency="dsd1", components=Components([])
    )

    message = Message([dsd1])
    assert message.get_data_structure_definitions() == [dsd1]
    assert (
        message.get_data_structure_definition("DataStructure=dsd1:dsd1(1.0)")
        == dsd1
    )


def test_get_dataflows():
    df1 = Dataflow(id="df1", agency="df1")

    message = Message([df1])
    assert message.get_dataflows() == [df1]

    assert message.get_dataflow("Dataflow=df1:df1(1.0)") == df1


def test_get_datasets():
    ds = Dataset(structure="DataStructure=ds1:ds1(1.0)")
    message = Message(None, [ds])

    assert message.get_datasets() == [ds]
    assert message.get_dataset("DataStructure=ds1:ds1(1.0)") == ds


def test_wrong_initialization_data_message():
    exc_message = "Invalid data type: str"
    with pytest.raises(Invalid) as exc_info:
        Message({}, {"DataStructure=ds1:ds1(1.0)": "invalid"})
    assert exc_message in str(exc_info.value.title)


def test_cannot_get_datasets():
    message = Message({})
    with pytest.raises(NotFound):
        message.get_datasets()

    with pytest.raises(NotFound):
        message.get_dataset("DataStructure=ds1:ds1(1.0)")


def test_cannot_get_dataset():
    message = Message(data=[Dataset(structure="DataStructure=ds1:ds1(1.0)")])
    with pytest.raises(NotFound):
        message.get_dataset("DataStructure=ds2:ds2(1.0)")


def test_empty_get_elements():
    message = Message()
    with pytest.raises(NotFound) as exc_info:
        message.get_agency_schemes()

    assert "No AgencyScheme found" in str(exc_info.value.title)

    with pytest.raises(NotFound) as exc_info:
        message.get_codelists()

    assert "No Codelist found" in str(exc_info.value.title)

    with pytest.raises(NotFound) as exc_info:
        message.get_concept_schemes()

    assert "No ConceptScheme found" in str(exc_info.value.title)


def test_empty_get_element_by_short_urn():
    message = Message([])
    with pytest.raises(NotFound) as exc_info:
        message.get_organisation_scheme("AgencyScheme=org1:orgs1(1.0)")

    assert "No AgencyScheme with Short URN" in str(exc_info.value.title)

    with pytest.raises(NotFound) as exc_info:
        message.get_codelist("Codelist=cl1:cl1(1.0)")

    assert "No Codelist with Short URN" in str(exc_info.value.title)

    with pytest.raises(NotFound) as exc_info:
        message.get_concept_scheme("ConceptScheme=cs1:cs1(1.0)")

    assert "No ConceptScheme with Short URN" in str(exc_info.value.title)


def test_none_get_element_by_short_urn():
    message = Message()
    with pytest.raises(NotFound) as exc_info:
        message.get_organisation_scheme("AgencyScheme=org1:orgs1(1.0)")

    assert "No AgencyScheme found" in str(exc_info.value.title)


def test_invalid_get_element_by_short_urn():
    message = Message([])

    e_m = "No AgencyScheme with Short URN"

    with pytest.raises(NotFound) as exc_info:
        message.get_organisation_scheme("AgencyScheme=org12:orgs1(1.0)")
    assert e_m in str(exc_info.value.title)


def test_invalid_initialization_content_key():
    exc_message = "Invalid structure: Dataset"
    with pytest.raises(Invalid) as exc_info:
        Message([Dataset(structure="DataStructure=ds1:ds1(1.0)")])
    assert exc_message in str(exc_info.value.title)


def test_tostr_data():
    message = Message(data=[Dataset(structure="DataStructure=ds1:ds1(1.0)")])
    s = str(message)

    assert s == "Message(1 Dataset)"


def test_tostr_structure():
    message = Message(
        [
            AgencyScheme(id="orgs1", agency="org1"),
            Codelist(id="cl1", agency="cl1"),
        ]
    )
    s = str(message)

    assert s == "Message(1 AgencyScheme, 1 Codelist)"


def test_tostr_empty():
    message = Message()
    s = str(message)

    assert s == "Message()"
