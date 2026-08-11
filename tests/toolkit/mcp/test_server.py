import numpy as np
import pandas as pd
import pytest
from fastmcp.exceptions import ToolError

from pysdmx import errors
from pysdmx.model import Code, Dataflow
from pysdmx.toolkit.mcp import _safety, _services, server


class FakeComponent:
    """Duck-typed stand-in for a pysdmx Component.

    The server reads components through getattr, so a light fake keeps
    these tests focused on server behaviour rather than on constructing
    a full DSD.
    """

    def __init__(self, id, name=None, enumeration=None, required=True):
        """Instantiate a fake component."""
        self.id = id
        self.name = name
        self.enumeration = enumeration
        self.required = required


class FakeComponents:
    """Duck-typed stand-in for a pysdmx Components collection."""

    def __init__(self, dimensions=(), measures=(), attributes=()):
        """Instantiate a fake components collection."""
        self.dimensions = list(dimensions)
        self.measures = list(measures)
        self.attributes = list(attributes)

    def __iter__(self):
        """Iterate over every component, whatever its role."""
        return iter(self.dimensions + self.measures + self.attributes)


class FakeFlow:
    """Duck-typed stand-in for a pysdmx Dataflow with availability."""

    def __init__(
        self,
        name="Consolidated banking",
        description=None,
        components=None,
        series_count=None,
        obs_count=None,
    ):
        """Instantiate a fake dataflow."""
        self.name = name
        self.description = description
        self.components = components
        self.series_count = series_count
        self.obs_count = obs_count


class FakeConnector:
    """Records calls so tests can assert what was actually sent."""

    def __init__(self, flows=(), flow=None, data=None, raises=None):
        """Instantiate a fake connector."""
        self._flows = tuple(flows)
        self._flow = flow
        self._data = data
        self._raises = raises
        self.data_calls = []
        self.dataflow_calls = []

    def dataflows(self, search_term=None):
        """Return the canned dataflows, or raise the canned error."""
        if isinstance(self._raises, Exception):
            raise self._raises
        return self._flows

    def dataflow(self, ref, filters=None):
        """Return the canned dataflow, recording the call."""
        self.dataflow_calls.append((ref, filters))
        if isinstance(self._raises, Exception):
            raise self._raises
        return self._flow

    def data(self, ref, filters=None, **kwargs):
        """Return canned data, or delegate to a responder callable."""
        self.data_calls.append((ref, filters, kwargs))
        result = self._data
        if callable(result):
            return result(ref, filters, **kwargs)
        return result


@pytest.fixture
def use_connector(monkeypatch):
    """Install a fake connector for every tool call."""

    def _install(connector):
        monkeypatch.setattr(
            _services, "connector", lambda resolved, **kw: connector
        )
        return connector

    return _install


# --------------------------------------------------------------------
# list_services
# --------------------------------------------------------------------


def test_list_services_reports_the_pysdmx_endpoint():
    result = server.list_services()

    assert [s.name for s in result.services] == ["BIS"]
    assert result.services[0].verified is True
    assert result.custom_endpoints_supported is True
    assert "base URL" in result.next_step


# --------------------------------------------------------------------
# search_dataflows
# --------------------------------------------------------------------


@pytest.fixture
def flows():
    return (
        Dataflow(
            "WS_CBS_PUB",
            agency="BIS",
            version="1.0",
            name="Consolidated banking",
        ),
        Dataflow(
            "WS_CBPOL",
            agency="BIS",
            version="1.0",
            name="Central bank policy rates",
        ),
    )


def test_search_dataflows_matches_locally(use_connector, flows):
    use_connector(FakeConnector(flows=flows))

    result = server.search_dataflows("banking")

    assert result.match_count == 1
    assert result.dataflows[0].ref == "BIS:WS_CBS_PUB(1.0)"
    assert result.dataflows[0].matched_on == "name"
    assert result.total_dataflows_on_service == 2
    assert "inspect_dataflow" in result.next_step


def test_search_dataflows_treats_words_as_alternatives(use_connector, flows):
    # One call, many synonyms - the documented way to avoid repeated
    # round trips for each candidate term.
    use_connector(FakeConnector(flows=flows))

    result = server.search_dataflows("banking policy")

    assert result.match_count == 2
    assert result.search_terms == ["banking", "policy"]


def test_search_dataflows_empty_query_returns_everything(use_connector, flows):
    use_connector(FakeConnector(flows=flows))

    result = server.search_dataflows("")

    assert result.match_count == 2
    assert result.dataflows[0].matched_on is None


def test_search_dataflows_no_match_suggests_recovery(use_connector, flows):
    use_connector(FakeConnector(flows=flows))

    result = server.search_dataflows("cryptocurrency")

    assert result.match_count == 0
    assert result.dataflows == []
    assert "component or code labels" in result.next_step


def test_search_dataflows_single_match_names_the_ref(use_connector, flows):
    use_connector(FakeConnector(flows=flows))

    result = server.search_dataflows("banking")

    assert "BIS:WS_CBS_PUB(1.0)" in result.next_step


def test_search_dataflows_applies_limit(use_connector, flows):
    use_connector(FakeConnector(flows=flows))

    result = server.search_dataflows("", limit=1)

    assert result.match_count == 2
    assert len(result.dataflows) == 1


def test_search_dataflows_maps_errors(use_connector):
    use_connector(FakeConnector(raises=errors.Unavailable("Service down")))

    with pytest.raises(ToolError, match=r"\[unavailable\]"):
        server.search_dataflows("banking")


def test_search_dataflows_rejects_unknown_service():
    with pytest.raises(ToolError, match=r"\[invalid_request\]"):
        server.search_dataflows("banking", service="ECB")


# --------------------------------------------------------------------
# inspect_dataflow
# --------------------------------------------------------------------


@pytest.fixture
def banking_components():
    # 'CH' deliberately appears in three components, mirroring BIS
    # consolidated banking, where it is a reporting country, a
    # counterparty country and a bank type.
    return FakeComponents(
        dimensions=[
            FakeComponent("FREQ", "Frequency", [Code("Q", name="Quarterly")]),
            FakeComponent(
                "L_REP_CTY",
                "Reporting country",
                [Code("CH", name="Switzerland"), Code("DE")],
            ),
            FakeComponent(
                "CBS_BANK_TYPE", "CBS bank type", [Code("CH"), Code("4R")]
            ),
            FakeComponent(
                "L_CP_COUNTRY", "Counterparty country", [Code("CH")]
            ),
        ],
        measures=[FakeComponent("OBS_VALUE", "Observation value")],
        attributes=[FakeComponent("OBS_STATUS", "Status", required=False)],
    )


def test_inspect_dataflow_groups_components(use_connector, banking_components):
    use_connector(
        FakeConnector(
            flow=FakeFlow(components=banking_components, series_count=10)
        )
    )

    result = server.inspect_dataflow("BIS:WS_CBS_PUB(1.0)")

    assert [d.id for d in result.dimensions] == [
        "FREQ",
        "L_REP_CTY",
        "CBS_BANK_TYPE",
        "L_CP_COUNTRY",
    ]
    assert result.dimensions[0].role == "dimension"
    assert result.measures[0].role == "measure"
    assert result.attributes[0].role == "attribute"
    assert result.attributes[0].required is False


def test_inspect_dataflow_reports_availability_not_validity(
    use_connector, banking_components
):
    use_connector(
        FakeConnector(
            flow=FakeFlow(components=banking_components, series_count=10)
        )
    )

    result = server.inspect_dataflow("BIS:WS_CBS_PUB(1.0)")

    assert "may still be valid in the full codelist" in (
        result.availability_note
    )


def test_inspect_dataflow_echoes_the_filter(use_connector, banking_components):
    conn = use_connector(
        FakeConnector(
            flow=FakeFlow(components=banking_components, series_count=10)
        )
    )
    flt = "L_REP_CTY = 'CH'"

    result = server.inspect_dataflow("BIS:WS_CBS_PUB(1.0)", filters=flt)

    assert result.filter_applied == flt
    assert conn.dataflow_calls == [("BIS:WS_CBS_PUB(1.0)", flt)]
    assert "get_data with the same filter" in result.next_step


def test_inspect_dataflow_finds_a_code_in_every_role(
    use_connector, banking_components
):
    use_connector(
        FakeConnector(
            flow=FakeFlow(components=banking_components, series_count=10)
        )
    )

    result = server.inspect_dataflow("BIS:WS_CBS_PUB(1.0)", find_code="ch")

    assert [loc.component_id for loc in result.code_locations] == [
        "L_REP_CTY",
        "CBS_BANK_TYPE",
        "L_CP_COUNTRY",
    ]
    assert result.code_locations[0].role_hint == "reporting country"
    assert result.code_locations[0].code_name == "Switzerland"
    assert "ambiguous" in result.next_step


def test_inspect_dataflow_unambiguous_code(use_connector):
    components = FakeComponents(
        dimensions=[FakeComponent("FREQ", "Frequency", [Code("Q")])]
    )
    use_connector(
        FakeConnector(flow=FakeFlow(components=components, series_count=1))
    )

    result = server.inspect_dataflow("BIS:X(1.0)", find_code="Q")

    assert len(result.code_locations) == 1
    assert "ambiguous" not in result.next_step


def test_inspect_dataflow_code_not_found(use_connector, banking_components):
    use_connector(
        FakeConnector(
            flow=FakeFlow(components=banking_components, series_count=1)
        )
    )

    result = server.inspect_dataflow("BIS:X(1.0)", find_code="ZZ")

    assert result.code_locations == []


def test_inspect_dataflow_warns_when_large(use_connector, banking_components):
    use_connector(
        FakeConnector(
            flow=FakeFlow(
                components=banking_components,
                series_count=_safety.LARGE_SERIES_THRESHOLD + 1,
            )
        )
    )

    result = server.inspect_dataflow("BIS:WS_CBS_PUB(1.0)")

    assert result.size_warning is not None
    assert "Add filters" in result.next_step


def test_inspect_dataflow_survives_missing_obs_count(
    use_connector, banking_components
):
    # BIS returns None for obs_count; depending on it would break
    # against the only endpoint pysdmx ships.
    use_connector(
        FakeConnector(
            flow=FakeFlow(components=banking_components, series_count=100)
        )
    )

    result = server.inspect_dataflow("BIS:WS_CBS_PUB(1.0)")

    assert result.obs_count is None
    assert result.series_count == 100
    assert result.size_warning is None


def test_inspect_dataflow_without_components(use_connector):
    use_connector(FakeConnector(flow=FakeFlow(components=None)))

    result = server.inspect_dataflow("BIS:X(1.0)")

    assert result.dimensions == []
    assert result.measures == []
    assert result.attributes == []
    assert result.code_locations == []


def test_inspect_dataflow_truncates_long_code_lists(use_connector):
    codes = [Code(f"C{i}") for i in range(server._CODE_PREVIEW_LIMIT + 5)]
    components = FakeComponents(
        dimensions=[FakeComponent("BIG", "Big", codes)]
    )
    use_connector(
        FakeConnector(flow=FakeFlow(components=components, series_count=1))
    )

    result = server.inspect_dataflow("BIS:X(1.0)")

    assert result.dimensions[0].code_count == len(codes)
    assert len(result.dimensions[0].codes) == server._CODE_PREVIEW_LIMIT
    assert result.dimensions[0].codes_truncated is True


def test_inspect_dataflow_maps_errors(use_connector):
    use_connector(FakeConnector(raises=errors.NotFound("No such flow")))

    with pytest.raises(ToolError, match=r"\[not_found\]"):
        server.inspect_dataflow("BIS:NOPE(1.0)")


# --------------------------------------------------------------------
# get_data
# --------------------------------------------------------------------


@pytest.fixture
def observations():
    return pd.DataFrame(
        {
            "TIME_PERIOD": ["2018-Q1", "2019-Q1", "2020-Q1"],
            "OBS_VALUE": [1.0, 2.0, 3.0],
        }
    )


def test_get_data_returns_observations(use_connector, observations):
    conn = use_connector(FakeConnector(data=observations))

    result = server.get_data("BIS:X(1.0)", "FREQ = 'Q'")

    assert result.row_count == 3
    assert result.total_rows_available == 3
    assert result.truncated is False
    assert result.records[0]["OBS_VALUE"] == 1.0
    assert result.filter_applied == "FREQ = 'Q'"
    assert result.filter_fallback is None
    assert "Complete" in result.next_step
    assert conn.data_calls[0][1] == "FREQ = 'Q'"


def test_get_data_truncates_and_says_so(use_connector):
    df = pd.DataFrame({"OBS_VALUE": range(50)})
    use_connector(FakeConnector(data=df))

    result = server.get_data("BIS:X(1.0)", limit=10)

    assert result.row_count == 10
    assert result.total_rows_available == 50
    assert result.truncated is True
    assert "not a sample" in result.next_step


def test_get_data_clamps_the_limit(use_connector):
    df = pd.DataFrame({"OBS_VALUE": range(3)})
    use_connector(FakeConnector(data=df))

    result = server.get_data("BIS:X(1.0)", limit=10**9)

    assert result.row_count == 3


def test_get_data_flattens_an_index(use_connector, observations):
    indexed = observations.set_index("TIME_PERIOD")
    use_connector(FakeConnector(data=indexed))

    result = server.get_data("BIS:X(1.0)")

    assert "TIME_PERIOD" in result.columns
    assert result.records[0]["TIME_PERIOD"] == "2018-Q1"


def test_get_data_passes_columns_through(use_connector, observations):
    conn = use_connector(FakeConnector(data=observations))

    server.get_data("BIS:X(1.0)", columns=["OBS_VALUE"])

    assert conn.data_calls[0][2]["columns"] == ["OBS_VALUE"]


def test_get_data_omits_columns_when_not_requested(
    use_connector, observations
):
    conn = use_connector(FakeConnector(data=observations))

    server.get_data("BIS:X(1.0)")

    assert "columns" not in conn.data_calls[0][2]


def test_get_data_passes_labels_through(use_connector, observations):
    conn = use_connector(FakeConnector(data=observations))

    server.get_data("BIS:X(1.0)", labels="both")

    assert conn.data_calls[0][2]["labels"] == "both"


def test_get_data_serialises_awkward_values(use_connector):
    df = pd.DataFrame(
        {
            "OBS_VALUE": [np.float64(1.5), np.nan],
            "OBS_STATUS": pd.Categorical(["A", "B"]),
        }
    )
    use_connector(FakeConnector(data=df))

    result = server.get_data("BIS:X(1.0)")

    assert result.records[0]["OBS_VALUE"] == 1.5
    assert result.records[1]["OBS_VALUE"] is None
    assert result.records[0]["OBS_STATUS"] == "A"


# --------------------------------------------------------------------
# get_data: time-filter fallback
# --------------------------------------------------------------------


def test_get_data_falls_back_when_pushdown_rejected(use_connector):
    df = pd.DataFrame(
        {
            "TIME_PERIOD": ["2018-Q1", "2020-Q1", "2021-Q1"],
            "OBS_VALUE": [1.0, 2.0, 3.0],
        }
    )
    calls = []

    def responder(ref, filters, **kwargs):
        calls.append(filters)
        if filters and "TIME_PERIOD" in filters:
            raise errors.Invalid("Bad query", "Dates are not supported.")
        return df

    use_connector(FakeConnector(data=responder))

    result = server.get_data(
        "BIS:X(1.0)", "FREQ = 'Q' AND TIME_PERIOD >= '2020-Q1'"
    )

    assert calls == ["FREQ = 'Q' AND TIME_PERIOD >= '2020-Q1'", "FREQ = 'Q'"]
    assert result.filter_applied == "FREQ = 'Q'"
    assert result.filter_fallback is not None
    assert "applied locally" in result.filter_fallback
    assert result.row_count == 2
    assert [r["TIME_PERIOD"] for r in result.records] == [
        "2020-Q1",
        "2021-Q1",
    ]
    assert "Time filtering happened locally" in result.next_step


def test_get_data_fallback_with_a_time_only_filter(use_connector):
    df = pd.DataFrame(
        {"TIME_PERIOD": ["2018-Q1", "2020-Q1"], "OBS_VALUE": [1.0, 2.0]}
    )
    seen = []

    def responder(ref, filters, **kwargs):
        seen.append(filters)
        if filters is not None:
            raise errors.NotImplemented("Unsupported")
        return df

    use_connector(FakeConnector(data=responder))

    result = server.get_data("BIS:X(1.0)", "TIME_PERIOD >= '2020-Q1'")

    assert seen == ["TIME_PERIOD >= '2020-Q1'", None]
    assert result.filter_applied is None
    assert result.row_count == 1


def test_get_data_does_not_fall_back_without_a_time_clause(use_connector):
    def responder(ref, filters, **kwargs):
        raise errors.Invalid("Bad query")

    use_connector(FakeConnector(data=responder))

    with pytest.raises(ToolError, match=r"\[invalid_request\]"):
        server.get_data("BIS:X(1.0)", "FREQ = 'Q'")


@pytest.mark.parametrize(
    "exc",
    [
        errors.NotFound("Gone"),
        errors.Unavailable("Down"),
        errors.InternalError("Boom"),
    ],
)
def test_get_data_does_not_fall_back_on_unrelated_errors(use_connector, exc):
    # Dropping a clause cannot fix a wrong reference or an unreachable
    # service; retrying would waste a round trip and obscure the error.
    calls = []

    def responder(ref, filters, **kwargs):
        calls.append(filters)
        raise exc

    use_connector(FakeConnector(data=responder))

    with pytest.raises(ToolError):
        server.get_data("BIS:X(1.0)", "FREQ = 'Q' AND TIME_PERIOD >= '2020'")

    assert len(calls) == 1


def test_get_data_reports_a_failing_retry(use_connector):
    def responder(ref, filters, **kwargs):
        if filters and "TIME_PERIOD" in filters:
            raise errors.Invalid("Dates unsupported")
        raise errors.Unavailable("Service died")

    use_connector(FakeConnector(data=responder))

    with pytest.raises(ToolError, match=r"\[unavailable\]"):
        server.get_data("BIS:X(1.0)", "FREQ = 'Q' AND TIME_PERIOD >= '2020'")


def test_get_data_rejects_unknown_service():
    with pytest.raises(ToolError, match=r"\[invalid_request\]"):
        server.get_data("BIS:X(1.0)", service="not a url")


# --------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [(None, None), ("", None), ("   ", None), (" x ", "x"), (5, "5")],
)
def test_text_normalisation(value, expected):
    assert server._text(value) == expected


def test_scalar_passes_through_plain_values():
    assert server._scalar("a") == "a"
    assert server._scalar(None) is None


@pytest.mark.parametrize(
    ("value", "expected", "expected_type"),
    [
        (np.float64(1.5), 1.5, float),
        (np.int64(3), 3, int),
        (np.bool_(True), True, bool),
    ],
)
def test_scalar_unwraps_numpy_values(value, expected, expected_type):
    # numpy scalars are not JSON-serialisable; unwrapping them keeps the
    # records payload valid regardless of the dtypes pysdmx applies.
    result = server._scalar(value)

    assert result == expected
    assert type(result) is expected_type
