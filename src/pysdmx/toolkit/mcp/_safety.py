"""Guards that keep retrieval bounded and honest.

Three concerns:

* **Row caps.** A three-clause filter on BIS consolidated banking returns
  well over 400,000 rows. Without a cap, one tool call floods an agent's
  context window.
* **Size checks before retrieval.** ``series_count`` is the usable
  signal. ``obs_count`` is ``None`` on BIS, so logic that depends on it
  fails against the only endpoint pysdmx ships.
* **Time-filter fallback.** Server-side pushdown of ``TIME_PERIOD`` is
  preferred but not universally supported. When a service rejects it,
  retry without the clause and apply the cutoff with pandas.
"""

# ruff: noqa: E402
import re
from typing import Callable, Dict, Optional, Tuple

from pysdmx.__extras_check import __check_data_extra

__check_data_extra()

import pandas as pd

from pysdmx import errors

#: Default cap on rows returned by the ``get_data`` tool.
DEFAULT_ROW_LIMIT = 1000

#: Hard ceiling a caller may request, bounding the response payload.
MAX_ROW_LIMIT = 10_000

#: ``series_count`` above which a scope is flagged as large.
LARGE_SERIES_THRESHOLD = 5_000

#: Matches a ``TIME_PERIOD <op> value`` clause together with the ``AND``
#: joining it to its neighbours, so the clause can be excised cleanly.
#: Only conjunctions need handling: the SDMX query parser rejects ``OR``.
_TIME_CLAUSE = re.compile(
    r"""
    (?:\s+AND\s+)?
    \bTIME_PERIOD\b\s*
    (?:>=|<=|<>|!=|==|=|>|<)\s*
    (?:'[^']*'|"[^"]*"|\S+)
    """,
    re.IGNORECASE | re.VERBOSE,
)

#: Extracts the operator and value of each time clause, so the same
#: constraint can be re-applied locally.
_TIME_PARTS = re.compile(
    r"""\bTIME_PERIOD\b\s*
        (?P<op>>=|<=|<>|!=|==|=|>|<)\s*
        (?P<value>'[^']*'|"[^"]*"|\S+)""",
    re.IGNORECASE | re.VERBOSE,
)

_COMPARATORS: Dict[str, Callable[["pd.Series", str], "pd.Series"]] = {
    ">=": lambda s, v: s >= v,
    "<=": lambda s, v: s <= v,
    ">": lambda s, v: s > v,
    "<": lambda s, v: s < v,
    "=": lambda s, v: s == v,
    "==": lambda s, v: s == v,
    "<>": lambda s, v: s != v,
    "!=": lambda s, v: s != v,
}


class TimeSplit:
    """A filter string split into its time and non-time parts.

    Attributes:
        without_time: The filter with every ``TIME_PERIOD`` clause
            removed, or ``None`` when nothing would remain.
        constraints: The excised ``(operator, value)`` pairs, ready to be
            re-applied with pandas.
    """

    def __init__(
        self,
        without_time: Optional[str],
        constraints: Tuple[Tuple[str, str], ...],
    ):
        """Instantiate a split filter."""
        self.without_time = without_time
        self.constraints = constraints

    @property
    def has_time(self) -> bool:
        """Whether any time constraint was present."""
        return bool(self.constraints)


def clamp_limit(limit: Optional[int]) -> int:
    """Clamp a caller-supplied row limit into the permitted range.

    Args:
        limit: The requested limit, or ``None`` for the default.

    Returns:
        A limit between 1 and ``MAX_ROW_LIMIT``.
    """
    if limit is None:
        return DEFAULT_ROW_LIMIT
    return max(1, min(int(limit), MAX_ROW_LIMIT))


def split_time_filter(filters: Optional[str]) -> TimeSplit:
    """Separate ``TIME_PERIOD`` clauses from the rest of a filter.

    Args:
        filters: A filter string, or ``None``.

    Returns:
        The split. When the filter holds no time clause, ``without_time``
        is the input unchanged and ``constraints`` is empty.
    """
    if not filters:
        return TimeSplit(filters, ())

    constraints = tuple(
        (m.group("op"), _unquote(m.group("value")))
        for m in _TIME_PARTS.finditer(filters)
    )
    if not constraints:
        return TimeSplit(filters, ())

    remainder = _TIME_CLAUSE.sub("", filters).strip()
    # A leading AND survives when the time clause came first.
    remainder = re.sub(r"^\s*AND\s+", "", remainder, flags=re.IGNORECASE)
    remainder = remainder.strip()
    return TimeSplit(remainder or None, constraints)


def apply_time_locally(
    df: "pd.DataFrame",
    constraints: Tuple[Tuple[str, str], ...],
) -> "pd.DataFrame":
    """Apply time constraints to a data frame with pandas.

    SDMX time periods (``2020-Q1``, ``2018-01``, ``2024``) compare
    correctly as strings within a single frequency, which is what the
    fallback needs. No date parsing is attempted, since that would have
    to guess the frequency and would fail on formats such as ``2020-S1``.

    Args:
        df: The retrieved data.
        constraints: ``(operator, value)`` pairs from
            :func:`split_time_filter`.

    Returns:
        The filtered frame, or the frame unchanged when it holds no
        ``TIME_PERIOD`` column and there is nothing to filter on.
    """
    if "TIME_PERIOD" not in df.columns or not constraints:
        return df

    series = df["TIME_PERIOD"].astype(str)
    mask = pd.Series(True, index=df.index)
    for op, value in constraints:
        comparator = _COMPARATORS[op]
        mask &= comparator(series, value)
    return df[mask]


def size_warning(
    series_count: Optional[int],
    obs_count: Optional[int],
    row_limit: int = DEFAULT_ROW_LIMIT,
) -> Optional[str]:
    """Warn when a scope is large enough that retrieval would truncate.

    Args:
        series_count: Series in scope, if the service reported it.
        obs_count: Observations in scope. Frequently ``None`` - BIS does
            not report it - so it is treated as optional corroboration
            rather than the primary signal.
        row_limit: The cap the retrieval tool would apply.

    Returns:
        A warning string, or ``None`` when the scope looks retrievable.
    """
    if obs_count is not None and obs_count > row_limit:
        return (
            f"This scope holds {obs_count:,} observations but get_data "
            f"returns at most {row_limit:,} rows. Narrow the filter "
            f"before retrieving, or the result will be truncated."
        )
    if series_count is not None and series_count > LARGE_SERIES_THRESHOLD:
        return (
            f"This scope holds {series_count:,} series. Each carries "
            f"many observations, so get_data will almost certainly "
            f"truncate at {row_limit:,} rows. Add filters on the "
            f"dimensions above before retrieving."
        )
    if series_count is None and obs_count is None:
        return (
            "This service reported neither series_count nor obs_count, "
            "so the size of this scope is unknown. Filter defensively."
        )
    return None


def is_pushdown_failure(exc: Exception) -> bool:
    """Decide whether an error justifies retrying without the time clause.

    Only client-side rejections are worth retrying this way. A
    ``NotFound`` means the dataflow reference itself is wrong and an
    ``Unavailable`` means the service never answered; neither is fixed by
    dropping a clause, and retrying would waste a round trip and obscure
    the error the caller ultimately sees.

    Args:
        exc: The exception raised by the first retrieval attempt.

    Returns:
        Whether to attempt the fallback.
    """
    return isinstance(exc, (errors.Invalid, errors.NotImplemented))


def _unquote(value: str) -> str:
    """Strip matching surrounding quotes from a filter literal."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value
