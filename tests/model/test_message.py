import pytest

from pysdmx.model import Codelist, ConceptScheme
from pysdmx.model.__base import ItemScheme
from pysdmx.model.message import Message


def test_initialization():
    message = Message({})
    assert message.content == {}


def test_get_organisation():
    org1 = ItemScheme(id="orgs1", agency="org1")
    message = Message(
        {
            "OrganisationSchemes": {
                "org1:orgs1(1.0)": org1,
            }
        }
    )
    assert message.get_organisation_schemes() == {
        "org1:orgs1(1.0)": org1,
    }

    assert message.get_organisation_scheme_by_uid("org1:orgs1(1.0)") == org1


def test_get_codelists():
    cl1 = Codelist(id="cl1", agency="cl1")
    message = Message(
        {
            "Codelists": {
                "cl1:cl1(1.0)": cl1,
            }
        }
    )
    assert message.get_codelists() == {
        "cl1:cl1(1.0)": cl1,
    }

    assert message.get_codelist_by_uid("cl1:cl1(1.0)") == cl1


def test_get_concepts():
    cs1 = ConceptScheme(id="cs1", agency="cs1")
    message = Message(
        {
            "ConceptSchemes": {
                "cs1:cs1(1.0)": cs1,
            }
        }
    )
    assert message.get_concept_schemes() == {
        "cs1:cs1(1.0)": cs1,
    }

    assert message.get_concept_scheme_by_uid("cs1:cs1(1.0)") == cs1


def test_empty_get_elements():
    message = Message({})
    with pytest.raises(ValueError, match="No OrganisationSchemes found"):
        message.get_organisation_schemes()

    with pytest.raises(ValueError, match="No Codelists found"):
        message.get_codelists()

    with pytest.raises(ValueError, match="No ConceptSchemes found"):
        message.get_concept_schemes()


def test_empty_get_element_by_uid():
    message = Message({})
    with pytest.raises(ValueError, match="No OrganisationSchemes found"):
        message.get_organisation_scheme_by_uid("org1:orgs1(1.0)")

    with pytest.raises(ValueError, match="No Codelists found"):
        message.get_codelist_by_uid("cl1:cl1(1.0)")

    with pytest.raises(ValueError, match="No ConceptSchemes found"):
        message.get_concept_scheme_by_uid("cs1:cs1(1.0)")


def test_invalid_get_element_by_uid():
    message = Message({"OrganisationSchemes": {}})

    e_m = "No OrganisationSchemes with id"

    with pytest.raises(ValueError, match=e_m):
        message.get_organisation_scheme_by_uid("org12:orgs1(1.0)")


def test_invalid_initialization_content_key():
    exc_message = "Invalid content type: Invalid"
    with pytest.raises(ValueError, match=exc_message):
        Message({"Invalid": {}})


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("OrganisationSchemes", {"org1:orgs1(1.0)": "invalid"}),
        ("Codelists", {"cl1:cl1(1.0)": "invalid"}),
        ("ConceptSchemes", {"cs1:cs1(1.0)": "invalid"}),
    ],
)
def test_invalid_initialization_content_value(key, value):
    exc_message = f"Invalid content value type: str for {key}"
    with pytest.raises(ValueError, match=exc_message):
        Message({key: value})
