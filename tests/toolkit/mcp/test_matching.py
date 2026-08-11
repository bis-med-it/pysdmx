import pytest

from pysdmx.model import Agency, Code, Dataflow
from pysdmx.toolkit.mcp import _matching


class FakeComponent:
    """Duck-typed stand-in for a pysdmx Component."""

    def __init__(self, id, name=None, description=None, enumeration=None):
        """Instantiate a fake component."""
        self.id = id
        self.name = name
        self.description = description
        self.enumeration = enumeration


def test_dataflow_ref_from_agency_object():
    flow = Dataflow("CBS", agency=Agency("BIS"), version="1.0")

    assert _matching.dataflow_ref(flow) == "BIS:CBS(1.0)"


def test_dataflow_ref_from_agency_string():
    flow = Dataflow("CBS", agency="BIS", version="1.0")

    assert _matching.dataflow_ref(flow) == "BIS:CBS(1.0)"


@pytest.mark.parametrize(
    ("terms", "expected"),
    [
        ([], None),
        (["cbs"], "id"),
        (["banking"], "name"),
        (["positions"], "description"),
        (["nothing"], None),
    ],
)
def test_match_dataflow(terms, expected):
    flow = Dataflow(
        "CBS",
        agency="BIS",
        name="Consolidated banking",
        description="Cross-border positions",
    )

    assert _matching.match_dataflow(flow, terms) == expected


def test_match_dataflow_reports_id_first():
    # A term hitting several fields should be reported against the most
    # precise one, so the caller can judge match quality.
    flow = Dataflow("CBS", agency="BIS", name="CBS banking", description="CBS")

    assert _matching.match_dataflow(flow, ["cbs"]) == "id"


def test_match_dataflow_tolerates_missing_optional_fields():
    flow = Dataflow("CBS", agency="BIS")

    assert _matching.match_dataflow(flow, ["cbs"]) == "id"
    assert _matching.match_dataflow(flow, ["missing"]) is None


@pytest.mark.parametrize(
    ("comp_id", "name", "expected"),
    [
        ("L_REP_CTY", "Reporting country", "reporting country"),
        ("L_CP_COUNTRY", "Counterparty country", "counterparty country"),
        ("REF_AREA", "Reference area", "reference area"),
        ("CURRENCY", "Currency", "currency"),
        ("ISSUER", "Issuer", "issuer"),
        ("RESIDENCE", "Country of residence", "country of residence"),
        ("NATIONALITY", "Nationality", "nationality"),
        ("BORROWER", "Borrower", "borrower country"),
        (
            "CBS_BANK_TYPE",
            "CBS bank type",
            "bank type (shares a country codelist)",
        ),
    ],
)
def test_role_hint_recognises_country_roles(comp_id, name, expected):
    # The point of this: 'in Switzerland' must not silently resolve to
    # the wrong dimension.
    assert _matching.role_hint(FakeComponent(comp_id, name)) == expected


def test_role_hint_falls_back_to_name():
    comp = FakeComponent("WEIRD_DIM", "Some other thing")

    assert _matching.role_hint(comp) == "Some other thing"


def test_role_hint_falls_back_to_id():
    assert _matching.role_hint(FakeComponent("WEIRD_DIM")) == "WEIRD_DIM"


def test_role_hint_matches_on_description():
    comp = FakeComponent("X", "Y", description="The reporting country")

    assert _matching.role_hint(comp) == "reporting country"


def test_codes_of_returns_codes():
    comp = FakeComponent("F", enumeration=[Code("A"), Code("B")])

    assert [c.id for c in _matching.codes_of(comp)] == ["A", "B"]


@pytest.mark.parametrize("enumeration", [None, []])
def test_codes_of_tolerates_uncoded_components(enumeration):
    assert (
        _matching.codes_of(FakeComponent("F", enumeration=enumeration)) == []
    )


def test_codes_of_drops_none_entries():
    comp = FakeComponent("F", enumeration=[Code("A"), None])

    assert [c.id for c in _matching.codes_of(comp)] == ["A"]
