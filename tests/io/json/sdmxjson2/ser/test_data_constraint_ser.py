import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.constraint import JsonDataConstraint
from pysdmx.model import ConstraintAttachment, DataConstraint


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


def test_constraint_no_name(constraint_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonDataConstraint.from_model(constraint_no_name)


def test_constraint_no_attachment(constraint_no_attachment):
    with pytest.raises(
        errors.Invalid, match="must have a constraint attachment"
    ):
        JsonDataConstraint.from_model(constraint_no_attachment)
