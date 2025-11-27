import pytest

from pysdmx.errors import Invalid
from pysdmx.model.code import Code, Codelist


@pytest.fixture
def scheme():
    codes = [
        Code(id="A", name="Annual frequency"),
        Code(
            id="M",
            name="Monthly frequency",
            description="Another useful frequency",
        ),
    ]
    return Codelist(
        "CL_FREQ", name="Frequency codelist", agency="BIS", items=codes
    )


def test_invalid(scheme):
    with pytest.raises(Invalid):
        scheme.search("")


def test_partial_match_zero(scheme):
    m = scheme.search("weekly")

    assert len(m) == 0


def test_partial_match_one(scheme):
    m = scheme.search("annual")

    assert len(m) == 1

    assert m[0].id == "A"


def test_partial_match_two(scheme):
    m = scheme.search("frequency")

    assert len(m) == 2

    for i in m:
        assert i.id in ["A", "M"]


def test_partial_match_desc(scheme):
    m = scheme.search("useful")

    assert len(m) == 1

    assert m[0].id == "M"


def test_regex_case_sensitive(scheme):
    m = scheme.search("annual", use_regex=True)

    assert len(m) == 0

    m = scheme.search("Annual", use_regex=True)

    assert len(m) == 1


def test_regex_exact_match(scheme):
    m = scheme.search("^Annual$", use_regex=True)

    assert len(m) == 0

    m = scheme.search("^Annual frequency$", use_regex=True)

    assert len(m) == 1


def test_included_field(scheme):
    m = scheme.search("useful", fields="name")

    assert len(m) == 0

    m = scheme.search("useful", fields="description")

    assert len(m) == 1
