from datetime import datetime, timezone

import pytest

from pysdmx.errors import Invalid, NotFound
from pysdmx.model import (
    AgencyScheme,
    Organisation,
    RulesetScheme,
    TransformationScheme,
    UserDefinedOperatorScheme,
)
from pysdmx.model.code import Codelist
from pysdmx.model.concept import ConceptScheme
from pysdmx.model.dataflow import Components, Dataflow, DataStructureDefinition
from pysdmx.model.dataset import Dataset
from pysdmx.model.message import Header, Message


def test_initialization():
    message = Message({}, {}, {})
    assert message.structures == {}
    assert message.data == {}


def test_get_agency_scheme():
    org1 = AgencyScheme(id="orgs1", agency="org1")
    message = Message(structures=[org1])
    assert message.get_agency_schemes() == [org1]

    assert (
        message.get_organisation_scheme("AgencyScheme=org1:orgs1(1.0)") == org1
    )


def test_get_codelists():
    cl1 = Codelist(id="cl1", agency="cl1")
    message = Message(structures=[cl1])
    assert message.get_codelists() == [cl1]

    assert message.get_codelist("Codelist=cl1:cl1(1.0)") == cl1


def test_get_concepts():
    cs1 = ConceptScheme(id="cs1", agency="cs1")
    message = Message(structures=[cs1])
    assert message.get_concept_schemes() == [cs1]

    assert message.get_concept_scheme("ConceptScheme=cs1:cs1(1.0)") == cs1


def test_get_data_structure_definitions():
    dsd1 = DataStructureDefinition(
        id="dsd1", agency="dsd1", components=Components([])
    )

    message = Message(structures=[dsd1])
    assert message.get_data_structure_definitions() == [dsd1]
    assert (
        message.get_data_structure_definition("DataStructure=dsd1:dsd1(1.0)")
        == dsd1
    )


def test_get_dataflows():
    df1 = Dataflow(id="df1", agency="df1")

    message = Message(structures=[df1])
    assert message.get_dataflows() == [df1]

    assert message.get_dataflow("Dataflow=df1:df1(1.0)") == df1


def test_get_datasets():
    ds = Dataset(structure="DataStructure=ds1:ds1(1.0)")
    message = Message(None, None, [ds])

    assert message.get_datasets() == [ds]
    assert message.get_dataset("DataStructure=ds1:ds1(1.0)") == ds
    assert (
        str(message.get_dataset("DataStructure=ds1:ds1(1.0)"))
        == "structure: DataStructure=ds1:ds1(1.0)"
    )
    assert (
        repr(message.get_dataset("DataStructure=ds1:ds1(1.0)"))
        == "Dataset(structure='DataStructure=ds1:ds1(1.0)')"
    )


def test_wrong_initialization_data_message():
    exc_message = "Invalid data type: str"
    with pytest.raises(Invalid) as exc_info:
        Message(data={"DataStructure=ds1:ds1(1.0)": "invalid"})
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
    message = Message(structures=[])
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
    message = Message(structures=[])

    e_m = "No AgencyScheme with Short URN"

    with pytest.raises(NotFound) as exc_info:
        message.get_organisation_scheme("AgencyScheme=org12:orgs1(1.0)")
    assert e_m in str(exc_info.value.title)


def test_invalid_initialization_content_key():
    exc_message = "Invalid structure: Dataset"
    with pytest.raises(Invalid) as exc_info:
        Message({}, [Dataset(structure="DataStructure=ds1:ds1(1.0)")])
    assert exc_message in str(exc_info.value.title)


def test_get_transformation_scheme():
    transformation = TransformationScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
    )
    message = Message(structures=[transformation])
    assert message.get_transformation_schemes() == [transformation]


def test_get_udo_scheme():
    udo_scheme = UserDefinedOperatorScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
    )
    message = Message(structures=[udo_scheme])
    assert message.get_user_defined_operator_schemes() == [udo_scheme]


def test_get_ruleset_scheme():
    ruleset_scheme = RulesetScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
    )
    message = Message(structures=[ruleset_scheme])
    assert message.get_ruleset_schemes() == [ruleset_scheme]


def test_message_str_with_structures():
    agency_scheme = AgencyScheme(id="agency1", agency="agency1")
    codelist = Codelist(id="codelist1", agency="agency1")
    message = Message(structures=[agency_scheme, codelist])

    s = str(message)
    expected_str = "structures: 1 agencyscheme, 1 codelist"

    assert s == expected_str


def test_message_str_with_data():
    dataset = Dataset(structure="DataStructure=ds1:ds1(1.0)")
    message = Message(data=[dataset])

    s = str(message)
    expected_str = "data: 1 dataset"

    assert s == expected_str


def test_message_str_without_data():
    message = Message()

    s = str(message)
    expected_str = ""

    assert s == expected_str


def test_message_str():
    agency_scheme = AgencyScheme(id="agency1", agency="agency1")
    codelist = Codelist(id="codelist1", agency="agency1")
    message = Message(structures=[agency_scheme, codelist], data=[])

    s = str(message)
    expected_str = "structures: 1 agencyscheme, 1 codelist"

    assert s == expected_str


def test_message_repr():
    agency_scheme = AgencyScheme(id="agency1", agency="agency1")
    codelist = Codelist(id="codelist1", agency="agency1")
    message = Message(structures=[agency_scheme, codelist], data=[])

    r = repr(message)
    expected_repr = (
        "Message(structures=[AgencyScheme(id='agency1', agency='agency1'), "
        "Codelist(id='codelist1', agency='agency1')])"
    )
    assert r == expected_repr


def test_header_str():
    h = Header(
        id="12345",
        test=True,
        prepared=datetime(2023, 1, 1, tzinfo=timezone.utc),
        sender=Organisation(id="TEST"),
        receiver=None,
        source="Test Source",
    )

    s = str(h)
    expected_str = (
        "id: 12345, test: True, prepared: 2023-01-01 00:00:00+00:00, "
        "sender: id: TEST, source: Test Source"
    )
    assert s == expected_str


def test_header_repr():
    h = Header(
        id="12345",
        test=True,
        prepared=datetime(2023, 1, 1, tzinfo=timezone.utc),
        sender=Organisation(id="TEST"),
        receiver=None,
        source="Test Source",
    )

    r = repr(h)
    expected_repr = (
        "Header(id='12345', test=True, "
        "prepared=datetime.datetime(2023, 1, 1, 0, 0, "
        "tzinfo=datetime.timezone.utc), "
        "sender=Organisation(id='TEST'), source='Test Source')"
    )
    assert r == expected_repr
