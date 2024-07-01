import pytest

from pysdmx.errors import ClientError, NotFound
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
            "Concepts": {
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
    with pytest.raises(NotFound) as exc_info:
        message.get_organisation_schemes()

    assert "No OrganisationSchemes found" in str(exc_info.value.title)

    with pytest.raises(NotFound) as exc_info:
        message.get_codelists()

    assert "No Codelists found" in str(exc_info.value.title)

    with pytest.raises(NotFound) as exc_info:
        message.get_concept_schemes()

    assert "No Concepts found" in str(exc_info.value.title)


def test_empty_get_element_by_uid():
    message = Message({})
    with pytest.raises(NotFound) as exc_info:
        message.get_organisation_scheme_by_uid("org1:orgs1(1.0)")

    assert "No OrganisationSchemes found" in str(exc_info.value.title)

    with pytest.raises(NotFound) as exc_info:
        message.get_codelist_by_uid("cl1:cl1(1.0)")

    assert "No Codelists found" in str(exc_info.value.title)

    with pytest.raises(NotFound) as exc_info:
        message.get_concept_scheme_by_uid("cs1:cs1(1.0)")

    assert "No Concepts found" in str(exc_info.value.title)


def test_invalid_get_element_by_uid():
    message = Message({"OrganisationSchemes": {}})

    e_m = "No OrganisationSchemes with id"

    with pytest.raises(NotFound) as exc_info:
        message.get_organisation_scheme_by_uid("org12:orgs1(1.0)")
    assert e_m in str(exc_info.value.title)


def test_invalid_initialization_content_key():
    exc_message = "Invalid content type: Invalid"
    with pytest.raises(ClientError) as exc_info:
        Message({"Invalid": {}})
    assert exc_message in str(exc_info.value.title)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("OrganisationSchemes", {"org1:orgs1(1.0)": "invalid"}),
        ("Codelists", {"cl1:cl1(1.0)": "invalid"}),
        ("Concepts", {"cs1:cs1(1.0)": "invalid"}),
    ],
)
def test_invalid_initialization_content_value(key, value):
    exc_message = f"Invalid content value type: str for {key}"
    with pytest.raises(ClientError) as exc_info:
        Message({key: value})
    assert exc_message in str(exc_info.value.title)
