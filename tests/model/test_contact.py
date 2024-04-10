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
