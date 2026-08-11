"""Structured outputs returned by the MCP tools.

Every result carries a ``next_step`` field. Telling an agent what to do
next measurably reduces flailing between tools, and it is where the
non-obvious SDMX rules (availability is not validity, AND but never OR,
stop at inspection for availability-only questions) are surfaced at the
moment they matter.

Results also echo the resolved dataflow reference and the filter string
actually sent, so a caller can verify what was queried rather than what
it believed it asked for.
"""

# ruff: noqa: E402
from typing import Any, Dict, List, Optional

from pysdmx.__extras_check import __check_mcp_extra

__check_mcp_extra()

from pydantic import BaseModel, Field


class ServiceInfo(BaseModel):
    """A single SDMX-REST v2 service known to the server."""

    name: str = Field(description="Short identifier, such as 'BIS'.")
    base_url: str = Field(description="SDMX-REST v2 base URL.")
    source: str = Field(
        description=(
            "Where the entry came from: 'pysdmx' for a member of "
            "pysdmx.api.dc.Endpoints, 'custom' for a supplied URL."
        )
    )
    verified: bool = Field(
        description=(
            "True only for services confirmed to meet the connector's "
            "requirements (SDMX-REST v2, SDMX-JSON 2.0.0 structures, "
            "SDMX-CSV data). Unverified services may fail at any step."
        )
    )
    notes: str = Field(description="Capability caveats worth knowing.")


class ServiceList(BaseModel):
    """Result of the ``list_services`` tool."""

    services: List[ServiceInfo]
    custom_endpoints_supported: bool = Field(
        default=True,
        description=(
            "Every tool accepts a 'service' argument holding either a "
            "known name or an arbitrary SDMX-REST v2 base URL."
        ),
    )
    next_step: str


class DataflowSummary(BaseModel):
    """One dataflow, as returned by discovery."""

    ref: str = Field(
        description=(
            "Canonical reference in agency:id(version) form. Pass this "
            "verbatim to inspect_dataflow and get_data."
        )
    )
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    agency: str
    version: str
    matched_on: Optional[str] = Field(
        default=None,
        description=(
            "Which field the search term matched: 'id', 'name' or "
            "'description'. Null when no search term was supplied."
        ),
    )


class DataflowSearchResult(BaseModel):
    """Result of the ``search_dataflows`` tool."""

    service: str
    search_terms: List[str]
    total_dataflows_on_service: int
    match_count: int
    dataflows: List[DataflowSummary]
    next_step: str


class CodeInfo(BaseModel):
    """A single available code within a component."""

    id: str
    name: Optional[str] = None


class ComponentInfo(BaseModel):
    """A dimension, measure or attribute of a dataflow."""

    id: str
    name: Optional[str] = None
    role: str = Field(description="'dimension', 'measure' or 'attribute'.")
    required: bool
    code_count: int = Field(description="Number of codes currently available.")
    codes: List[CodeInfo] = Field(
        description=(
            "Available codes, truncated when numerous. These are "
            "availability-backed: a code absent here may still be valid "
            "in the full codelist."
        )
    )
    codes_truncated: bool


class CodeLocation(BaseModel):
    """Where a code value was found, and in what role."""

    component_id: str
    component_name: Optional[str] = None
    role_hint: str = Field(
        description=(
            "The role this component plays, inferred from its metadata, "
            "such as 'reporting country' or 'counterparty country'. "
            "Disambiguates phrases like 'in Switzerland'."
        )
    )
    code_id: str
    code_name: Optional[str] = None


class DataflowDetail(BaseModel):
    """Result of the ``inspect_dataflow`` tool."""

    service: str
    ref: str = Field(description="The resolved dataflow reference.")
    name: Optional[str] = None
    description: Optional[str] = None
    filter_applied: Optional[str] = Field(
        default=None,
        description=(
            "The filter used to scope availability, echoed verbatim. "
            "Null means availability covers the whole dataflow."
        ),
    )
    series_count: Optional[int] = None
    obs_count: Optional[int] = Field(
        default=None,
        description=(
            "Observation count. Frequently null - BIS does not report "
            "it. Use series_count as the size signal when null."
        ),
    )
    size_warning: Optional[str] = Field(
        default=None,
        description=(
            "Present when the scope is large enough that get_data would "
            "truncate. Narrow the filter first."
        ),
    )
    dimensions: List[ComponentInfo]
    measures: List[ComponentInfo]
    attributes: List[ComponentInfo]
    code_locations: List[CodeLocation] = Field(
        default_factory=list,
        description=(
            "Populated when find_code was supplied: every component "
            "whose available codes contain that value, with the role "
            "each plays. More than one entry means the value is "
            "ambiguous - on BIS consolidated banking 'CH' appears as "
            "reporting country, counterparty country and bank type - so "
            "choose the intended role before filtering."
        ),
    )
    availability_note: str
    next_step: str


class DataResult(BaseModel):
    """Result of the ``get_data`` tool - the observations themselves."""

    service: str
    ref: str = Field(description="The resolved dataflow reference.")
    filter_applied: Optional[str] = Field(
        description=(
            "The filter actually sent to the service, echoed so the "
            "caller can verify what was queried."
        )
    )
    filter_fallback: Optional[str] = Field(
        default=None,
        description=(
            "Set when server-side time pushdown failed and the time "
            "constraint was applied locally instead. Names the filter "
            "that was sent and the cutoff applied with pandas."
        ),
    )
    columns: List[str]
    row_count: int = Field(description="Rows actually returned.")
    total_rows_available: int = Field(
        description="Rows matching the filter before the cap was applied."
    )
    truncated: bool = Field(
        description=(
            "True when total_rows_available exceeded the cap. The "
            "returned rows are the first row_count in service order and "
            "are NOT a representative sample - narrow the filter for a "
            "complete answer."
        )
    )
    records: List[Dict[str, Any]]
    next_step: str
