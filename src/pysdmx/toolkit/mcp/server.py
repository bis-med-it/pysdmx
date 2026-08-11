"""An MCP server exposing SDMX data discovery and retrieval.

Four tools, in the order they are meant to be called:

1. :func:`list_services` - what can I talk to?
2. :func:`search_dataflows` - which dataset holds this?
3. :func:`inspect_dataflow` - what can I filter on, and how big is it?
4. :func:`get_data` - give me the numbers.

The last one is the point. Comparable SDMX MCP servers navigate metadata
and then hand back a URL; this one returns observations.

Run it over STDIO with ``python -m pysdmx.toolkit.mcp``.
"""

# ruff: noqa: E402
from typing import Any, Dict, List, Optional, Tuple

from pysdmx.__extras_check import __check_data_extra, __check_mcp_extra

__check_mcp_extra()
__check_data_extra()

import pandas as pd
from fastmcp import FastMCP
from pydantic import Field
from typing_extensions import Annotated

from pysdmx.toolkit.mcp import _matching, _safety, _services
from pysdmx.toolkit.mcp._errors import as_tool_error
from pysdmx.toolkit.mcp._models import (
    CodeInfo,
    CodeLocation,
    ComponentInfo,
    DataflowDetail,
    DataflowSearchResult,
    DataflowSummary,
    DataResult,
    ServiceInfo,
    ServiceList,
)

_INSTRUCTIONS = (
    "Discover and retrieve official statistics from SDMX-REST v2 "
    "services.\n\n"
    "Call the tools in order: list_services -> search_dataflows -> "
    "inspect_dataflow -> get_data.\n\n"
    "Rules that prevent wrong answers:\n"
    "- Filter syntax supports AND only. NEVER emit OR. For several "
    "values of one component use IN ('A', 'B').\n"
    "- Availability is not validity. inspect_dataflow returns codes for "
    "which data currently exist; a code absent from that list may still "
    "be valid in the full codelist, so never report that something "
    "'does not exist' on that basis alone.\n"
    "- A country code may appear in several dimensions with different "
    "meanings. Pass find_code to inspect_dataflow to see every "
    "component carrying a value, and state which role you used.\n"
    "- If the question is only whether data exist, stop at "
    "inspect_dataflow. Do not call get_data unless observations were "
    "actually requested.\n"
    "- Check size before retrieving. When get_data reports "
    "truncated=true the rows are the first N and NOT a sample, so do "
    "not aggregate them - narrow the filter instead."
)

mcp: FastMCP[Any] = FastMCP(
    name="pysdmx-sdmx-data", instructions=_INSTRUCTIONS
)

#: Cap on codes listed per component, so that inspecting a dataflow with
#: a 259-code country dimension does not flood the response.
_CODE_PREVIEW_LIMIT = 60

_AVAILABILITY_NOTE = (
    "These codes are availability-backed: values for which data "
    "currently exist in this scope. A code missing here may still be "
    "valid in the full codelist - verify against structural metadata "
    "before concluding that it does not exist."
)


@mcp.tool
def list_services() -> ServiceList:
    """List the SDMX services this server can query.

    Any SDMX-REST v2 base URL also works: pass it as the service
    argument to any other tool. The service must return structural
    metadata as SDMX-JSON 2.0.0 and data as SDMX-CSV.

    Returns:
        The known services, with capability notes for each.
    """
    entries = [
        ServiceInfo(
            name=name,
            base_url=url,
            source="pysdmx",
            verified=name == "BIS",
            notes=_services.notes_for(name),
        )
        for name, url in _services.known_services().items()
    ]
    return ServiceList(
        services=entries,
        next_step=(
            "Call search_dataflows with a topic to find a dataset. "
            "pysdmx currently ships one endpoint, so for any other "
            "provider (ECB, OECD, IMF, Eurostat, ILO) pass its "
            "SDMX-REST v2 base URL as the service argument - it is a "
            "first-class input, not a fallback."
        ),
    )


@mcp.tool
def search_dataflows(
    query: Annotated[
        str,
        Field(
            description=(
                "Topic to search for, such as 'banking' or 'policy "
                "rates'. Space-separated words are treated as "
                "alternatives and matched case-insensitively against "
                "each dataflow's id, name and description. Pass an "
                "empty string to list every dataflow."
            )
        ),
    ] = "",
    service: Annotated[
        Optional[str],
        Field(
            description=(
                "Service name from list_services, or an SDMX-REST v2 "
                "base URL. Defaults to the pysdmx endpoint."
            )
        ),
    ] = None,
    limit: Annotated[
        int,
        Field(description="Maximum dataflows to return.", ge=1, le=200),
    ] = 50,
) -> DataflowSearchResult:
    """Find dataflows (datasets) matching a topic.

    Issues exactly one request to the service and matches the terms
    locally, so searching for synonyms costs nothing extra: put them all
    in one query rather than calling this repeatedly.

    Returns:
        Matching dataflows, each with a ref to pass to the next tool.

    Raises:
        ToolError: If the service is unknown or the request fails. The
            message carries a [kind] discriminator and a retry hint.
    """
    resolved = _resolve(service)
    conn = _services.connector(resolved)

    try:
        flows = conn.dataflows()
    except Exception as exc:
        raise as_tool_error(exc) from exc

    terms = [t for t in query.lower().split() if t]
    matches: List[DataflowSummary] = []
    for flow in flows:
        matched_on = _matching.match_dataflow(flow, terms)
        if terms and matched_on is None:
            continue
        agency = getattr(flow, "agency", "")
        matches.append(
            DataflowSummary(
                ref=_matching.dataflow_ref(flow),
                id=flow.id,
                name=_text(getattr(flow, "name", None)),
                description=_text(getattr(flow, "description", None)),
                agency=str(getattr(agency, "id", agency)),
                version=str(flow.version),
                matched_on=matched_on,
            )
        )

    return DataflowSearchResult(
        service=resolved.name,
        search_terms=terms,
        total_dataflows_on_service=len(flows),
        match_count=len(matches),
        dataflows=matches[:limit],
        next_step=_search_next_step(matches, len(flows)),
    )


@mcp.tool
def inspect_dataflow(
    ref: Annotated[
        str,
        Field(
            description=(
                "Dataflow reference in agency:id(version) form, such as "
                "'BIS:WS_CBS_PUB(1.0)'. Take this from the ref field of "
                "search_dataflows. A full SDMX URN also works."
            )
        ),
    ],
    filters: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional filter scoping availability to a subset, such "
                "as \"L_REP_CTY = 'CH' AND FREQ = 'Q'\". AND only, "
                "never OR; use IN ('A', 'B') for several values of one "
                "component. Supplying this narrows the reported codes "
                "and counts to what remains available."
            )
        ),
    ] = None,
    find_code: Annotated[
        Optional[str],
        Field(
            description=(
                "Optional code value such as 'CH'. Reports every "
                "component whose available codes contain it, and the "
                "role each plays. Use this before filtering on a "
                "country: the same code often appears in several "
                "dimensions with different meanings."
            )
        ),
    ] = None,
    service: Annotated[
        Optional[str],
        Field(description="Service name or SDMX-REST v2 base URL."),
    ] = None,
) -> DataflowDetail:
    """Inspect a dataflow's components, available codes and size.

    Call this before get_data. It answers three questions: what can I
    filter on, which codes actually have data, and is this small enough
    to retrieve?

    If you only need to know whether data exist for some subset, pass
    filters and stop here rather than going on to get_data.

    Returns:
        Components grouped by role, availability-backed codes, and size
        signals with a warning when retrieval would truncate.

    Raises:
        ToolError: If the dataflow is not found or the request fails.
    """
    resolved = _resolve(service)
    conn = _services.connector(resolved)

    try:
        flow = conn.dataflow(ref, filters)
    except Exception as exc:
        raise as_tool_error(exc) from exc

    components = getattr(flow, "components", None)
    locations = (
        _locate_code(components, find_code)
        if find_code and components is not None
        else []
    )

    series_count = getattr(flow, "series_count", None)
    obs_count = getattr(flow, "obs_count", None)
    warning = _safety.size_warning(series_count, obs_count)

    return DataflowDetail(
        service=resolved.name,
        ref=ref,
        name=_text(getattr(flow, "name", None)),
        description=_text(getattr(flow, "description", None)),
        filter_applied=filters,
        series_count=series_count,
        obs_count=obs_count,
        size_warning=warning,
        dimensions=_describe(components, "dimensions"),
        measures=_describe(components, "measures"),
        attributes=_describe(components, "attributes"),
        code_locations=locations,
        availability_note=_AVAILABILITY_NOTE,
        next_step=_inspect_next_step(warning, locations, filters),
    )


@mcp.tool
def get_data(
    ref: Annotated[
        str,
        Field(
            description=(
                "Dataflow reference in agency:id(version) form, such as "
                "'BIS:WS_CBS_PUB(1.0)'."
            )
        ),
    ],
    filters: Annotated[
        Optional[str],
        Field(
            description=(
                "Filter selecting the data, such as \"L_MEASURE = 'S' "
                "AND L_REP_CTY = 'CH' AND TIME_PERIOD >= '2020-Q1'\". "
                "AND only, never OR; use IN ('A', 'B') for several "
                "values of one component. Omitting this pulls the whole "
                "dataflow and will almost certainly truncate."
            )
        ),
    ] = None,
    columns: Annotated[
        Optional[List[str]],
        Field(
            description=(
                "Components to return, such as ['OBS_VALUE']. Omit for "
                "all. TIME_PERIOD and SERIES_KEY are added "
                "automatically by pysdmx."
            )
        ),
    ] = None,
    limit: Annotated[
        Optional[int],
        Field(
            description=(
                "Maximum rows to return. Defaults to 1000, hard ceiling 10000."
            )
        ),
    ] = None,
    labels: Annotated[
        str,
        Field(
            description=(
                "'id' returns code IDs (default, and far more compact). "
                "'name' substitutes human-readable names. 'both' gives "
                "'ID: Name'. Leave as 'id' unless names were requested."
            ),
            pattern="^(id|name|both)$",
        ),
    ] = "id",
    service: Annotated[
        Optional[str],
        Field(description="Service name or SDMX-REST v2 base URL."),
    ] = None,
) -> DataResult:
    """Retrieve observations as records. This returns the actual numbers.

    Call inspect_dataflow first to confirm component and code IDs and to
    check the size of what you are about to pull.

    If a TIME_PERIOD clause is rejected by the service, it is retried
    without that clause and the cutoff is applied locally; the response
    says so in filter_fallback.

    Returns:
        The observations, the filter actually sent, and a truncated
        flag. When truncated, the rows are the first N in service order
        and are NOT a representative sample.

    Raises:
        ToolError: If retrieval fails. The message carries a [kind]
            discriminator and a retry hint.
    """
    resolved = _resolve(service)
    conn = _services.connector(resolved)
    row_limit = _safety.clamp_limit(limit)

    df, applied, fallback = _fetch(conn, ref, filters, columns, labels)

    if list(df.index.names) != [None]:
        df = df.reset_index()
    total = int(len(df))
    capped = df.head(row_limit)

    return DataResult(
        service=resolved.name,
        ref=ref,
        filter_applied=applied,
        filter_fallback=fallback,
        columns=[str(c) for c in capped.columns],
        row_count=int(len(capped)),
        total_rows_available=total,
        truncated=total > row_limit,
        records=_records(capped),
        next_step=_data_next_step(total, row_limit, fallback),
    )


def _fetch(
    conn: Any,
    ref: str,
    filters: Optional[str],
    columns: Optional[List[str]],
    labels: str,
) -> Tuple["pd.DataFrame", Optional[str], Optional[str]]:
    """Retrieve data, falling back to local time filtering if needed.

    Args:
        conn: The connector.
        ref: Dataflow reference.
        filters: The requested filter.
        columns: Requested columns.
        labels: Label mode.

    Returns:
        A tuple of the frame, the filter actually sent, and a note
        describing the fallback when one was used.

    Raises:
        ToolError: If retrieval fails and no fallback applies.
    """
    kwargs: Dict[str, Any] = {"labels": labels}
    if columns:
        kwargs["columns"] = columns

    try:
        return conn.data(ref, filters, **kwargs), filters, None
    except Exception as exc:
        split = _safety.split_time_filter(filters)
        if not (_safety.is_pushdown_failure(exc) and split.has_time):
            raise as_tool_error(exc) from exc

        # The service rejected a query carrying a time clause. Retry
        # without it, then re-apply the cutoff with pandas.
        try:
            df = conn.data(ref, split.without_time, **kwargs)
        except Exception as retry_exc:
            raise as_tool_error(retry_exc) from retry_exc

        conditions = ", ".join(
            f"TIME_PERIOD {op} '{value}'" for op, value in split.constraints
        )
        note = (
            f"The service rejected server-side time filtering, so "
            f"{split.without_time!r} was sent instead and {conditions} "
            f"was applied locally with pandas."
        )
        filtered = _safety.apply_time_locally(df, split.constraints)
        return filtered, split.without_time, note


def _resolve(service: Optional[str]) -> "_services.ResolvedService":
    """Resolve a service argument, converting failure into a ToolError.

    Args:
        service: The service name or URL.

    Returns:
        The resolved service.

    Raises:
        ToolError: If the service cannot be resolved.
    """
    try:
        return _services.resolve(service)
    except Exception as exc:
        raise as_tool_error(exc) from exc


def _describe(components: Any, group: str) -> List[ComponentInfo]:
    """Render one group of components for the response.

    Args:
        components: The dataflow's components, possibly ``None``.
        group: ``dimensions``, ``measures`` or ``attributes``.

    Returns:
        The described components, or an empty list when the service
        returned no component metadata.
    """
    if components is None:
        return []

    described: List[ComponentInfo] = []
    for comp in getattr(components, group, []):
        codes = _matching.codes_of(comp)
        preview = codes[:_CODE_PREVIEW_LIMIT]
        described.append(
            ComponentInfo(
                id=comp.id,
                name=_text(getattr(comp, "name", None)),
                role=group[:-1],
                required=bool(getattr(comp, "required", False)),
                code_count=len(codes),
                codes=[
                    CodeInfo(id=c.id, name=_text(getattr(c, "name", None)))
                    for c in preview
                ],
                codes_truncated=len(codes) > len(preview),
            )
        )
    return described


def _locate_code(components: Any, value: str) -> List[CodeLocation]:
    """Find every component whose available codes contain a value.

    Args:
        components: The dataflow's components.
        value: The code to look for, matched case-insensitively.

    Returns:
        One entry per component carrying the code.
    """
    wanted = value.strip().upper()
    found: List[CodeLocation] = []
    for comp in components:
        for code in _matching.codes_of(comp):
            if str(code.id).upper() == wanted:
                found.append(
                    CodeLocation(
                        component_id=comp.id,
                        component_name=_text(getattr(comp, "name", None)),
                        role_hint=_matching.role_hint(comp),
                        code_id=code.id,
                        code_name=_text(getattr(code, "name", None)),
                    )
                )
                break
    return found


def _records(df: "pd.DataFrame") -> List[Dict[str, Any]]:
    """Convert a data frame to JSON-safe records.

    Categorical dtypes and numpy scalars do not serialise cleanly and
    NaN is not valid JSON, so values are normalised to ``None`` or
    Python primitives.

    Args:
        df: The frame to convert.

    Returns:
        One dictionary per row.
    """
    safe = df.astype(object).where(pd.notna(df), None)
    return [
        {str(k): _scalar(v) for k, v in row.items()}
        for row in safe.to_dict(orient="records")
    ]


def _scalar(value: Any) -> Any:
    """Coerce a numpy or pandas scalar to a JSON-safe Python value.

    Args:
        value: The value to coerce.

    Returns:
        A Python primitive, or ``None``.
    """
    if value is None:
        return None
    item = getattr(value, "item", None)
    if callable(item):
        return item()
    return value


def _text(value: Any) -> Optional[str]:
    """Normalise an optional metadata field to a string or ``None``.

    Args:
        value: The raw metadata value.

    Returns:
        The stripped string, or ``None`` when empty or absent.
    """
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _search_next_step(matches: List[DataflowSummary], total: int) -> str:
    """Compose the hint returned by search_dataflows.

    Args:
        matches: The matching dataflows.
        total: How many dataflows the service holds.

    Returns:
        The hint.
    """
    if not matches:
        return (
            f"Nothing matched. The service has {total} dataflows - call "
            f"this again with an empty query to see them all, or try "
            f"broader terms. Some concepts appear only in component or "
            f"code labels, so also consider inspect_dataflow on a "
            f"plausible dataflow before concluding no data exist."
        )
    if len(matches) == 1:
        return (
            f"Call inspect_dataflow with ref='{matches[0].ref}' to see "
            f"its dimensions, available codes and size."
        )
    return (
        f"{len(matches)} dataflows matched. Call inspect_dataflow on the "
        f"most promising ref to see its dimensions and size before "
        f"retrieving anything."
    )


def _inspect_next_step(
    warning: Optional[str],
    locations: List[CodeLocation],
    filters: Optional[str],
) -> str:
    """Compose the hint returned by inspect_dataflow.

    Args:
        warning: The size warning, if any.
        locations: Components carrying a searched-for code.
        filters: The filter that scoped availability, if any.

    Returns:
        The hint.
    """
    if len(locations) > 1:
        roles = "; ".join(
            f"{loc.component_id} ({loc.role_hint})" for loc in locations
        )
        return (
            f"That code is ambiguous - it appears in {len(locations)} "
            f"components: {roles}. Decide which role the question "
            f"means, filter on that component, and state which one you "
            f"used."
        )
    if warning:
        return (
            "This scope is large. Add filters and call inspect_dataflow "
            "again to confirm the subset shrinks, then call get_data. "
            "If the question was only whether data exist, you already "
            "have the answer - stop here."
        )
    if filters:
        return (
            "Availability for this subset is confirmed. If observations "
            "were requested, call get_data with the same filter. If the "
            "question was only whether data exist, stop here."
        )
    return (
        "Choose dimensions to filter on from the codes above, then call "
        "get_data. Filtering first is strongly preferred - unfiltered "
        "pulls truncate."
    )


def _data_next_step(
    total: int, row_limit: int, fallback: Optional[str]
) -> str:
    """Compose the hint returned by get_data.

    Args:
        total: Rows matching before the cap.
        row_limit: The cap applied.
        fallback: The fallback note, if the time filter ran locally.

    Returns:
        The hint.
    """
    if total > row_limit:
        hint = (
            f"Truncated: {total:,} rows matched but only {row_limit:,} "
            f"were returned. These are the first rows in service order, "
            f"not a sample - do not compute totals or averages from "
            f"them. Narrow the filter (add a TIME_PERIOD bound or more "
            f"dimensions) and call again."
        )
    else:
        hint = (
            f"Complete: all {total:,} matching rows were returned. Safe "
            f"to aggregate."
        )
    if fallback:
        hint += (
            " Time filtering happened locally, so rows outside the "
            "requested period were fetched and discarded. The counts "
            "above are post-filter."
        )
    return hint
