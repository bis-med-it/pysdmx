import pytest
from fastmcp.exceptions import ToolError

from pysdmx import errors
from pysdmx.toolkit.mcp._errors import as_tool_error, classify


@pytest.mark.parametrize(
    ("exc", "kind", "retriable"),
    [
        (errors.Unavailable("down"), "unavailable", True),
        (errors.NotFound("gone"), "not_found", False),
        (errors.Unauthorized("nope"), "unauthorized", False),
        (errors.NotImplemented("no"), "not_implemented", False),
        (errors.Invalid("bad"), "invalid_request", False),
        (errors.InternalError("boom"), "internal_error", False),
        (errors.RetriableError("later"), "retriable_error", True),
        (errors.PysdmxError("generic"), "sdmx_error", False),
        (ValueError("bug"), "unexpected_error", False),
    ],
)
def test_classify(exc, kind, retriable):
    info = classify(exc)

    assert info["error"] == kind
    assert info["retriable"] is retriable
    assert info["next_step"]


def test_classify_prefers_most_specific_type():
    # Unavailable subclasses RetriableError, which subclasses
    # PysdmxError. Collapsing them would tell an agent to retry a
    # NotFound, or to give up on a transient outage.
    assert classify(errors.Unavailable("x"))["error"] == "unavailable"
    assert classify(errors.RetriableError("x"))["error"] == "retriable_error"


def test_classify_keeps_not_found_and_unavailable_distinct():
    not_found = classify(errors.NotFound("x"))
    unavailable = classify(errors.Unavailable("x"))

    assert not_found["retriable"] is False
    assert unavailable["retriable"] is True
    assert not_found["next_step"] != unavailable["next_step"]


def test_classify_uses_title_and_description():
    info = classify(errors.NotFound("Flow missing", "Try search_dataflows."))

    assert info["message"] == "Flow missing"
    assert info["detail"] == "Try search_dataflows."


def test_classify_without_description():
    assert classify(errors.NotFound("Flow missing"))["detail"] is None


def test_classify_non_pysdmx_error_reports_type_as_detail():
    info = classify(ValueError("bug"))

    assert info["message"] == "bug"
    assert info["detail"] == "ValueError"
    assert "pysdmx MCP server" in info["next_step"]


def test_classify_falls_back_to_type_name_for_empty_message():
    assert classify(ValueError())["message"] == "ValueError"


def test_as_tool_error_embeds_the_classification():
    err = as_tool_error(errors.NotFound("Flow missing", "Not here."))

    assert isinstance(err, ToolError)
    assert "[not_found]" in str(err)
    assert "Flow missing" in str(err)
    assert "Not here." in str(err)
    assert "retriable=false" in str(err)
    assert "next_step:" in str(err)


def test_as_tool_error_without_detail():
    err = as_tool_error(errors.Unavailable("Service down"))

    assert "[unavailable]" in str(err)
    assert "retriable=true" in str(err)
    assert " - " not in str(err).split("|")[0]
