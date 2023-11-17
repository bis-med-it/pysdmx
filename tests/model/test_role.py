from pysdmx.model import Role


def test_expected_role_for_attribute():
    r = Role.ATTRIBUTE

    assert r == "A"


def test_expected_role_for_dimension():
    r = Role.DIMENSION

    assert r == "D"


def test_expected_role_for_measure():
    r = Role.MEASURE

    assert r == "M"
