import pytest

from pysdmx.model import DataflowRef, Organisation


@pytest.fixture()
def id():
    return "5B0"


@pytest.fixture()
def name():
    return "BIS"


@pytest.fixture()
def desc():
    return "Bank for International Settlements"


@pytest.fixture()
def contact():
    return "support@email.address"


@pytest.fixture()
def dataflows():
    df1 = DataflowRef("DF1", "TEST")
    df2 = DataflowRef("DF2", "Also TEST")
    return [df1, df2]


def test_defaults(id):
    org = Organisation(id)

    assert org.id == id
    assert org.name is None
    assert org.description is None
    assert org.contacts is not None
    assert len(org.contacts) == 0
    assert org.dataflows is not None
    assert len(org.dataflows) == 0


def test_full_instantiation(id, name, desc, contact, dataflows):
    org = Organisation(id, name, desc, contact, dataflows)

    assert org.id == id
    assert org.name == name
    assert org.description == desc
    assert org.contacts == contact
    assert org.dataflows == dataflows


def test_immutable(id):
    org = Organisation(id)
    with pytest.raises(AttributeError):
        org.name = "Not allowed"


def test_equal(id, name, desc, contact):
    org1 = Organisation(id, name, desc, contact)
    org2 = Organisation(id, name, desc, contact)

    assert org1 == org2


def test_not_equal(id, name, desc, contact):
    org1 = Organisation(id, name, desc, contact)
    org2 = Organisation(id, f"{id}_{name}", desc, contact)

    assert org1 != org2


def test_tostr_id(id):
    o = Organisation(id)

    s = str(o)

    assert s == id


def test_tostr_name(id, name):
    o = Organisation(id, name)

    s = str(o)

    assert s == f"{id} ({name})"


def test_equal_has_same_hash(id):
    org1 = Organisation(id)
    org2 = Organisation(id)

    assert org1.__hash__() == org2.__hash__()


def test_not_equal_has_different_hash(id):
    org1 = Organisation(id)
    org2 = Organisation(f"{id}42")

    assert org1.__hash__() != org2.__hash__()
