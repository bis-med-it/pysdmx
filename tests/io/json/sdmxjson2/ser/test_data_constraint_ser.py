import msgspec
import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.constraint import JsonDataConstraint
from pysdmx.model import ConstraintAttachment, ConstraintRole, DataConstraint


@pytest.fixture
def constraint_no_name():
    return DataConstraint(
        "TEST",
        agency="BIS",
        constraint_attachment=ConstraintAttachment(data_provider="5B0"),
    )


@pytest.fixture
def constraint_no_attachment():
    return DataConstraint("TEST", agency="BIS", name="Test")


@pytest.fixture
def constraint_role_actual():
    return DataConstraint(
        "TEST",
        agency="BIS",
        name="Test",
        role=ConstraintRole.ACTUAL,
        constraint_attachment=ConstraintAttachment(data_provider="5B0"),
    )


def test_constraint_no_name(constraint_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonDataConstraint.from_model(constraint_no_name)


def test_constraint_no_attachment(constraint_no_attachment):
    with pytest.raises(
        errors.Invalid, match="must have a constraint attachment"
    ):
        JsonDataConstraint.from_model(constraint_no_attachment)


def test_constraint_role_actual(constraint_role_actual):
    sjson = JsonDataConstraint.from_model(constraint_role_actual)

    assert sjson.role == "Actual"
    assert b'"role":"Actual"' in msgspec.json.encode(sjson)
