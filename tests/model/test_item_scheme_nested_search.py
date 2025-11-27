import pytest

from pysdmx.errors import Invalid
from pysdmx.model.category import Category, CategoryScheme


@pytest.fixture
def scheme():
    cat1 = Category(id="PA", name="Panama")
    cat2 = Category(id="AR", name="Argentina")
    cat3 = Category(id="UY", name="Uruguay")
    cat4 = Category(id="G212", name="Central America", categories=[cat1])
    cat5 = Category(
        id="G213",
        name="South America",
        description="The southern subregion of the Americas",
        categories=[cat2, cat3],
    )
    cats = [cat4, cat5]
    return CategoryScheme(
        "CS", name="Test category scheme", agency="SDMX", items=cats
    )


def test_invalid(scheme):
    with pytest.raises(Invalid):
        scheme.search("")


def test_partial_match_zero(scheme):
    m = scheme.search("North")

    assert len(m) == 0


def test_partial_match_one(scheme):
    m = scheme.search("central")

    assert len(m) == 1

    assert m[0].id == "G212"


def test_partial_match_two(scheme):
    m = scheme.search("America")

    assert len(m) == 2

    for i in m:
        assert i.id in ["G212", "G213"]


def test_partial_match_desc(scheme):
    m = scheme.search("subregion")

    assert len(m) == 1

    assert m[0].id == "G213"


def test_regex_case_sensitive(scheme):
    m = scheme.search("south america", use_regex=True)

    assert len(m) == 0

    m = scheme.search("South America", use_regex=True)

    assert len(m) == 1


def test_regex_exact_match(scheme):
    m = scheme.search("^South$", use_regex=True)

    assert len(m) == 0

    m = scheme.search("^South America$", use_regex=True)

    assert len(m) == 1


def test_included_field(scheme):
    m = scheme.search("subregion", fields="name")

    assert len(m) == 0

    m = scheme.search("subregion", fields="description")

    assert len(m) == 1


def test_nested(scheme):
    m = scheme.search("Argentina")

    assert len(m) == 1

    assert m[0].id == "AR"
