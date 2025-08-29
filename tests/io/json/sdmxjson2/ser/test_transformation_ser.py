import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.vtl import JsonTransformation
from pysdmx.model.vtl import Transformation


@pytest.fixture
def transformation():
    return Transformation(
        "TRANS1",
        name="Test Transformation",
        description="Description",
        expression='DS_1 := DS_r[filter Id_1 = "A"];',
        is_persistent=True,
        result="DS_1",
    )


@pytest.fixture
def transformation_no_name():
    return Transformation(
        "TRANS1",
        expression='DS_1 := DS_r[filter Id_1 = "A"];',
        is_persistent=False,
        result="DS_1",
    )


def test_transformation(transformation: Transformation):
    sjson = JsonTransformation.from_model(transformation)

    assert sjson.id == transformation.id
    assert sjson.name == transformation.name
    assert sjson.description == transformation.description
    assert len(sjson.annotations) == 0
    assert sjson.expression == transformation.expression
    assert sjson.isPersistent == transformation.is_persistent
    assert sjson.result == transformation.result


def test_transformation_no_name(transformation_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonTransformation.from_model(transformation_no_name)
