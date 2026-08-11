import pandas as pd
import pytest

from pysdmx import errors
from pysdmx.toolkit.mcp import _safety


@pytest.mark.parametrize(
    ("supplied", "expected"),
    [
        (None, _safety.DEFAULT_ROW_LIMIT),
        (0, 1),
        (-5, 1),
        (10, 10),
        (_safety.MAX_ROW_LIMIT + 1, _safety.MAX_ROW_LIMIT),
        (10**9, _safety.MAX_ROW_LIMIT),
    ],
)
def test_clamp_limit(supplied, expected):
    assert _safety.clamp_limit(supplied) == expected


@pytest.mark.parametrize(
    ("filters", "without_time", "constraints"),
    [
        (None, None, ()),
        ("", "", ()),
        ("FREQ = 'M'", "FREQ = 'M'", ()),
        (
            "FREQ = 'M' AND TIME_PERIOD >= '2018-01'",
            "FREQ = 'M'",
            ((">=", "2018-01"),),
        ),
        (
            "TIME_PERIOD >= '2018-01' AND FREQ = 'M'",
            "FREQ = 'M'",
            ((">=", "2018-01"),),
        ),
        (
            "A = '1' AND TIME_PERIOD >= '2018-01' AND B = '2'",
            "A = '1' AND B = '2'",
            ((">=", "2018-01"),),
        ),
        ("TIME_PERIOD >= '2018-01'", None, ((">=", "2018-01"),)),
        (
            "TIME_PERIOD >= '2018-01' AND TIME_PERIOD <= '2020-12'",
            None,
            ((">=", "2018-01"), ("<=", "2020-12")),
        ),
        ('TIME_PERIOD = "2020"', None, (("=", "2020"),)),
        ("TIME_PERIOD = 2020", None, (("=", "2020"),)),
        ("time_period >= '2018'", None, ((">=", "2018"),)),
    ],
)
def test_split_time_filter(filters, without_time, constraints):
    split = _safety.split_time_filter(filters)

    assert split.without_time == without_time
    assert split.constraints == constraints
    assert split.has_time is bool(constraints)


def test_split_time_filter_leaves_similarly_named_component():
    # A component whose name merely contains TIME_PERIOD as a substring
    # must not be mistaken for the time dimension.
    split = _safety.split_time_filter("MY_TIME_PERIODICITY = 'A'")

    assert split.without_time == "MY_TIME_PERIODICITY = 'A'"
    assert split.constraints == ()


@pytest.fixture
def frame():
    return pd.DataFrame(
        {
            "TIME_PERIOD": ["2018-Q1", "2019-Q1", "2020-Q1", "2021-Q1"],
            "OBS_VALUE": [1.0, 2.0, 3.0, 4.0],
        }
    )


@pytest.mark.parametrize(
    ("op", "value", "expected"),
    [
        (">=", "2020-Q1", ["2020-Q1", "2021-Q1"]),
        (">", "2020-Q1", ["2021-Q1"]),
        ("<=", "2019-Q1", ["2018-Q1", "2019-Q1"]),
        ("<", "2019-Q1", ["2018-Q1"]),
        ("=", "2019-Q1", ["2019-Q1"]),
        ("==", "2019-Q1", ["2019-Q1"]),
        ("<>", "2019-Q1", ["2018-Q1", "2020-Q1", "2021-Q1"]),
        ("!=", "2019-Q1", ["2018-Q1", "2020-Q1", "2021-Q1"]),
    ],
)
def test_apply_time_locally_operators(frame, op, value, expected):
    out = _safety.apply_time_locally(frame, ((op, value),))

    assert list(out["TIME_PERIOD"]) == expected


def test_apply_time_locally_combines_constraints(frame):
    out = _safety.apply_time_locally(
        frame, ((">=", "2019-Q1"), ("<=", "2020-Q1"))
    )

    assert list(out["TIME_PERIOD"]) == ["2019-Q1", "2020-Q1"]


def test_apply_time_locally_without_constraints(frame):
    assert _safety.apply_time_locally(frame, ()) is frame


def test_apply_time_locally_without_time_column():
    df = pd.DataFrame({"OBS_VALUE": [1.0]})

    assert _safety.apply_time_locally(df, ((">=", "2020"),)) is df


def test_size_warning_flags_large_obs_count():
    warning = _safety.size_warning(None, 5_000, row_limit=1_000)

    assert warning is not None
    assert "5,000 observations" in warning


def test_size_warning_flags_large_series_count():
    warning = _safety.size_warning(_safety.LARGE_SERIES_THRESHOLD + 1, None)

    assert warning is not None
    assert "series" in warning


def test_size_warning_flags_unknown_size():
    # BIS reports neither for some scopes; silence would read as "small".
    warning = _safety.size_warning(None, None)

    assert warning is not None
    assert "unknown" in warning


@pytest.mark.parametrize(
    ("series_count", "obs_count"),
    [(10, None), (None, 10), (10, 10), (0, 0)],
)
def test_size_warning_silent_when_small(series_count, obs_count):
    assert _safety.size_warning(series_count, obs_count) is None


def test_size_warning_prefers_obs_count_when_both_present():
    # obs_count is the more direct signal, so it wins when available.
    warning = _safety.size_warning(1, 9_999, row_limit=10)

    assert "9,999 observations" in warning


@pytest.mark.parametrize(
    ("exc", "expected"),
    [
        (errors.Invalid("nope"), True),
        (errors.NotImplemented("nope"), True),
        (errors.NotFound("nope"), False),
        (errors.Unavailable("nope"), False),
        (errors.InternalError("nope"), False),
        (ValueError("nope"), False),
    ],
)
def test_is_pushdown_failure(exc, expected):
    assert _safety.is_pushdown_failure(exc) is expected
