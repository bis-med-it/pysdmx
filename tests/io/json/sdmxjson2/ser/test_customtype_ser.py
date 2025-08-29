import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.vtl import JsonCustomType
from pysdmx.model.vtl import CustomType


@pytest.fixture
def ct():
    return CustomType(
        "RATING",
        name="Rating",
        description="Description",
        vtl_scalar_type="test",
        data_type="string",
        vtl_literal_format="fmt",
        output_format="of",
        null_value="NaN",
    )


@pytest.fixture
def ct_no_name():
    return CustomType("RATING", vtl_scalar_type="test", data_type="string")


def test_custom_type(ct: CustomType):
    sjson = JsonCustomType.from_model(ct)

    assert sjson.id == ct.id
    assert sjson.name == ct.name
    assert sjson.description == ct.description
    assert len(sjson.annotations) == 0
    assert sjson.vtlScalarType == ct.vtl_scalar_type
    assert sjson.dataType == ct.data_type
    assert sjson.vtlLiteralFormat == ct.vtl_literal_format
    assert sjson.outputFormat == ct.output_format
    assert sjson.nullValue == ct.null_value


def test_ct_no_name(ct_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonCustomType.from_model(ct_no_name)
