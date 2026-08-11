import pytest

from pysdmx.api.dc import Endpoints
from pysdmx.api.dc.pd import PandasConnector
from pysdmx.errors import Invalid
from pysdmx.toolkit.mcp import _services


def test_known_services_reads_the_pysdmx_enum():
    known = _services.known_services()

    assert known == {m.name: m.value for m in Endpoints}
    assert "BIS" in known


def test_notes_for_known_service():
    assert "series_count" in _services.notes_for("BIS")


def test_notes_for_unknown_service():
    assert "No capability notes" in _services.notes_for("NOPE")


def test_resolve_defaults_to_the_single_endpoint():
    resolved = _services.resolve(None)

    assert resolved.name == "BIS"
    assert resolved.base_url == Endpoints.BIS.value
    assert resolved.known is True


@pytest.mark.parametrize("supplied", ["BIS", "bis", " Bis "])
def test_resolve_known_name_is_case_insensitive(supplied):
    resolved = _services.resolve(supplied)

    assert resolved.name == "BIS"
    assert resolved.known is True


@pytest.mark.parametrize(
    ("supplied", "expected"),
    [
        ("https://example.org/api/v2", "https://example.org/api/v2"),
        ("https://example.org/api/v2/", "https://example.org/api/v2"),
        ("http://localhost:8080/sdmx", "http://localhost:8080/sdmx"),
    ],
)
def test_resolve_accepts_custom_base_urls(supplied, expected):
    # Endpoints has a single member, so a supplied URL is a first-class
    # input rather than a fallback.
    resolved = _services.resolve(supplied)

    assert resolved.base_url == expected
    assert resolved.known is False


@pytest.mark.parametrize(
    "supplied", ["", "not a url", "ftp://example.org", "https://", "ECB"]
)
def test_resolve_rejects_anything_else(supplied):
    with pytest.raises(Invalid, match="Unknown service"):
        _services.resolve(supplied)


def test_resolve_error_lists_the_known_names():
    with pytest.raises(Invalid) as exc:
        _services.resolve("ECB")

    assert "BIS" in exc.value.description


def test_connector_targets_the_resolved_url():
    resolved = _services.resolve("https://example.org/api/v2")

    assert isinstance(_services.connector(resolved), PandasConnector)
