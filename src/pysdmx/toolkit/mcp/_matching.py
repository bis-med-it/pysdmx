"""Local matching of user terms against dataflow and component metadata.

The discovery rule this module exists to support: issue **one**
``dataflows()`` call per service and match locally, rather than firing
repeated ``dataflows(search_term)`` requests for every synonym a user
might have meant.
"""

from typing import Any, Iterable, List, Optional, Tuple

#: Words in a component's metadata that hint at the role a code plays.
#: A phrase such as "in Switzerland" may mean the reporting country, the
#: counterparty country or the reference area, and reporting the wrong
#: one produces a confidently incorrect answer.
_ROLE_HINTS: Tuple[Tuple[Tuple[str, ...], str], ...] = (
    (("reporting", "rep_cty", "reporter"), "reporting country"),
    (
        ("counterparty", "cp_country", "cp_cty", "partner"),
        "counterparty country",
    ),
    (("reference area", "ref_area", "refarea"), "reference area"),
    (("currency", "curr", "denom"), "currency"),
    (("issuer",), "issuer"),
    (("residence", "resident"), "country of residence"),
    (("nationality",), "nationality"),
    (("borrower",), "borrower country"),
    (("bank type", "bank_type"), "bank type (shares a country codelist)"),
)


def dataflow_ref(flow: Any) -> str:
    """Build the canonical ``agency:id(version)`` reference for a flow.

    Args:
        flow: Any object exposing ``agency``, ``id`` and ``version``.

    Returns:
        The shorthand reference pysdmx accepts wherever a dataflow is
        expected.
    """
    agency = getattr(flow, "agency", "")
    agency_id = getattr(agency, "id", agency)
    return f"{agency_id}:{flow.id}({flow.version})"


def match_dataflow(flow: Any, terms: Iterable[str]) -> Optional[str]:
    """Test one dataflow against a set of search terms.

    Args:
        flow: A dataflow returned by ``dataflows()``.
        terms: Lower-cased search terms. An empty iterable matches
            nothing, which callers treat as "no filtering requested".

    Returns:
        The name of the field that matched - ``id``, ``name`` or
        ``description`` - or ``None`` when nothing matched. The ID is
        checked first, so the most precise match is the one reported.
    """
    terms = list(terms)
    if not terms:
        return None

    fields = (
        ("id", flow.id),
        ("name", getattr(flow, "name", None)),
        ("description", getattr(flow, "description", None)),
    )
    for field_name, value in fields:
        if value and any(t in str(value).lower() for t in terms):
            return field_name
    return None


def role_hint(component: Any) -> str:
    """Infer the semantic role a component plays, for disambiguation.

    Args:
        component: A pysdmx ``Component``.

    Returns:
        A short human-readable role such as ``reporting country``. Falls
        back to the component's own name, then to its ID, so the result
        is never empty - callers render it directly.
    """
    haystack = " ".join(
        str(v).lower()
        for v in (
            component.id,
            getattr(component, "name", None),
            getattr(component, "description", None),
        )
        if v
    )
    for needles, hint in _ROLE_HINTS:
        if any(n in haystack for n in needles):
            return hint
    return str(getattr(component, "name", None) or component.id)


def codes_of(component: Any) -> List[Any]:
    """Return a component's available codes, tolerating a missing list.

    Args:
        component: A pysdmx ``Component``.

    Returns:
        The codes currently available. Uncoded components, and coded
        components whose enumeration the service did not return, both
        yield an empty list rather than raising.
    """
    enumeration = getattr(component, "enumeration", None)
    if not enumeration:
        return []
    return [c for c in enumeration if c is not None]
