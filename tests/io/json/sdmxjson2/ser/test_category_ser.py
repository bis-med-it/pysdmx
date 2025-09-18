import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.category import JsonCategory
from pysdmx.model import Category


@pytest.fixture
def category():
    child = Category("A1", name="Child A1")
    return Category(
        "A", name="Annual", description="Description", categories=[child]
    )


@pytest.fixture
def category_no_name():
    return Category("A")


def test_category(category: Category):
    sjson = JsonCategory.from_model(category)

    assert sjson.id == category.id
    assert sjson.name == category.name
    assert sjson.description == category.description
    assert len(sjson.annotations) == 0
    assert len(sjson.categories) == 1
    child = sjson.categories[0]
    assert child.id == "A1"
    assert child.name == "Child A1"
    assert child.description is None
    assert len(child.categories) == 0


def test_category_no_name(category_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonCategory.from_model(category_no_name)
