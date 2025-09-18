import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.vtl import JsonUserDefinedOperator
from pysdmx.model.vtl import UserDefinedOperator


@pytest.fixture
def udo():
    return UserDefinedOperator(
        "UDO1",
        name="User Defined Operator",
        description="Description",
        operator_definition="operator definition",
    )


@pytest.fixture
def udo_no_name():
    return UserDefinedOperator(
        "UDO1",
        operator_definition="operator definition",
    )


def test_user_defined_operator(udo: UserDefinedOperator):
    sjson = JsonUserDefinedOperator.from_model(udo)

    assert sjson.id == udo.id
    assert sjson.name == udo.name
    assert sjson.description == udo.description
    assert len(sjson.annotations) == 0
    assert sjson.operatorDefinition == udo.operator_definition


def test_udo_no_name(udo_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonUserDefinedOperator.from_model(udo_no_name)
