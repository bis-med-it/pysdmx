import pytest

from pysdmx.errors import Invalid, NotFound
from pysdmx.model.__base import ItemScheme
from pysdmx.model.code import Codelist
from pysdmx.model.concept import ConceptScheme
from pysdmx.model.dataflow import Components, Dataflow, DataStructureDefinition
from pysdmx.model.dataset import Dataset
from pysdmx.model.message import Message


def test_initialization():
    message = Message({}, {})
    assert message.structures == {}
    assert message.data == {}


def test_get_organisation():
    org1 = ItemScheme(id="orgs1", agency="org1")
    message = Message(
        {
            "OrganisationSchemes": {
                "AgencyScheme=org1:orgs1(1.0)": org1,
            }
        }
    )
    assert message.get_organisation_schemes() == {
        "AgencyScheme=org1:orgs1(1.0)": org1,
    }

    assert (
        message.get_organisation_scheme("AgencyScheme=org1:orgs1(1.0)") == org1
    )


def test_get_codelists():
    cl1 = Codelist(id="cl1", agency="cl1")
    message = Message(
        {
            "Codelists": {
                "Codelist=cl1:cl1(1.0)": cl1,
            }
        }
    )
    assert message.get_codelists() == {
        "Codelist=cl1:cl1(1.0)": cl1,
    }

    assert message.get_codelist("Codelist=cl1:cl1(1.0)") == cl1


def test_get_concepts():
    cs1 = ConceptScheme(id="cs1", agency="cs1")
    message = Message(
        {
            "Concepts": {
                "ConceptScheme=cs1:cs1(1.0)": cs1,
            }
        }
    )
    assert message.get_concept_schemes() == {
        "ConceptScheme=cs1:cs1(1.0)": cs1,
    }

    assert message.get_concept_scheme("ConceptScheme=cs1:cs1(1.0)") == cs1


def test_get_data_structure_definitions():
    dsd1 = DataStructureDefinition(
        id="dsd1", agency="dsd1", components=Components([])
    )

    message = Message(
        {
            "DataStructures": {
                "DataStructureDefinition=dsd1:dsd1(1.0)": dsd1,
            }
        }
    )
    assert message.get_data_structure_definitions() == {
        "DataStructureDefinition=dsd1:dsd1(1.0)": dsd1,
    }
    assert (
        message.get_data_structure_definition(
            "DataStructureDefinition" "=dsd1:dsd1(1.0)"
        )
        == dsd1
    )


def test_get_dataflows():
    df1 = Dataflow(id="df1", agency="df1")

    message = Message(
        {
            "Dataflows": {
                "Dataflow=dsd1:dsd1(1.0)": df1,
            }
        }
    )
    assert message.get_dataflows() == {
        "Dataflow=dsd1:dsd1(1.0)": df1,
    }

    assert message.get_dataflow("Dataflow=dsd1:dsd1(1.0)") == df1


def test_get_datasets():
    ds = Dataset(structure="DataStructure=ds1:ds1(1.0)")
    message = Message(None, {"DataStructure=ds1:ds1(1.0)": ds})

    assert message.get_datasets() == {
        "DataStructure=ds1:ds1(1.0)": ds,
    }

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


def test_empty_get_elements():
    message = Message({})
    with pytest.raises(NotFound) as exc_info:
        message.get_organisation_schemes()

    assert "No OrganisationSchemes found" in str(exc_info.value.title)

    with pytest.raises(NotFound) as exc_info:
        message.get_codelists()

    assert "No Codelists found" in str(exc_info.value.title)

    with pytest.raises(NotFound) as exc_info:
        message.get_concept_schemes()

    assert "No Concepts found" in str(exc_info.value.title)


def test_empty_get_element_by_short_urn():
    message = Message({})
    with pytest.raises(NotFound) as exc_info:
        message.get_organisation_scheme("AgencyScheme=org1:orgs1(1.0)")

    assert "No OrganisationSchemes found" in str(exc_info.value.title)

    with pytest.raises(NotFound) as exc_info:
        message.get_codelist("Codelist=cl1:cl1(1.0)")

    assert "No Codelists found" in str(exc_info.value.title)

    with pytest.raises(NotFound) as exc_info:
        message.get_concept_scheme("ConceptScheme=cs1:cs1(1.0)")

    assert "No Concepts found" in str(exc_info.value.title)


def test_invalid_get_element_by_short_urn():
    message = Message({"OrganisationSchemes": {}})

    e_m = "No OrganisationSchemes with Short URN"

    with pytest.raises(NotFound) as exc_info:
        message.get_organisation_scheme("AgencyScheme=org12:orgs1(1.0)")
    assert e_m in str(exc_info.value.title)


def test_invalid_initialization_content_key():
    exc_message = "Invalid content type: Invalid"
    with pytest.raises(Invalid) as exc_info:
        Message({"Invalid": {}})
    assert exc_message in str(exc_info.value.title)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("OrganisationSchemes", {"AgencyScheme=org1:orgs1(1.0)": "invalid"}),
        ("Codelists", {"Codelist=cl1:cl1(1.0)": "invalid"}),
        ("Concepts", {"ConceptScheme=cs1:cs1(1.0)": "invalid"}),
    ],
)
def test_invalid_initialization_content_value(key, value):
    exc_message = f"Invalid content value type: str for {key}"
    with pytest.raises(Invalid) as exc_info:
        Message({key: value})
    assert exc_message in str(exc_info.value.title)
