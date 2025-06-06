import pytest

from pysdmx.model import Contact


def test_defaults():
    c = Contact()

    assert c.name is None
    assert c.role is None
    assert c.id is None
    assert c.emails is None
    assert c.department is None
    assert c.telephones is None
    assert c.uris is None
    assert c.faxes is None


def test_full_initialization():
    name = "Fname Lname"
    role = "Statistician"
    id = "fl000042"
    email = "Fname.Lname@test.org"
    unit = "Statistics"
    phone = "+42 123 45 67"
    fax = "+42 123 45 68"
    url = "https//test.org"

    c = Contact(
        id=id,
        name=name,
        department=unit,
        role=role,
        emails=[email],
        telephones=[phone],
        faxes=[fax],
        uris=[url],
    )

    assert c.name == name
    assert c.role == role
    assert c.id == id
    assert c.emails[0] == email
    assert c.department == unit
    assert c.telephones[0] == phone
    assert c.uris[0] == url
    assert c.faxes[0] == fax


def test_immutable():
    contact = Contact(name="someone")
    with pytest.raises(AttributeError):
        contact.name = "somebody"


def test_contact_str():
    name = "Fname Lname"
    role = "Statistician"
    id = "fl000042"
    email = "Fname.Lname@test.org"
    unit = "Statistics"
    phone = "+42 123 45 67"
    url = "https://test.org"

    c = Contact(
        id=id,
        name=name,
        department=unit,
        role=role,
        emails=[email],
        telephones=[phone],
        faxes=[],
        uris=[url],
    )

    s = str(c)
    expected_str = (
        "id: fl000042, "
        "name: Fname Lname, "
        "department: Statistics, "
        "role: Statistician, "
        "telephones: 1 strs, "
        "uris: 1 strs, "
        "emails: 1 strs"
    )
    assert s == expected_str


def test_contact_repr():
    name = "Fname Lname"
    role = "Statistician"
    id = "fl000042"
    email = "Fname.Lname@test.org"
    unit = "Statistics"
    phone = "+42 123 45 67"
    url = "https://test.org"

    c = Contact(
        id=id,
        name=name,
        department=unit,
        role=role,
        emails=[email],
        telephones=[phone],
        faxes=[],
        uris=[url],
    )

    r = repr(c)
    expected_repr = (
        "Contact("
        "id='fl000042', "
        "name='Fname Lname', "
        "department='Statistics', "
        "role='Statistician', "
        "telephones=['+42 123 45 67'], "
        "uris=['https://test.org'], "
        "emails=['Fname.Lname@test.org'])"
    )
    assert r == expected_repr
