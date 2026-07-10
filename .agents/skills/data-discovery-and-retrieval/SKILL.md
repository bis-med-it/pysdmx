---
name: data-discovery-and-retrieval
description: Use when the user wants to find datasets, identify the right dataflow, inspect dimensions or codes, map natural-language requests to SDMX filters, or download data as a pandas DataFrame from SDMX-REST services.
---
# SDMX Data Discovery and Retrieval

## Goal

Use `pysdmx` connectors implementing the SDMX-REST data discovery and
retrieval profile to:

1. Discover available dataflows (datasets).
2. Inspect a selected dataflow to build effective queries.
3. Retrieve filtered data as a pandas DataFrame.

## Prerequisites

- Install extra dependencies: `pysdmx[data]`

## Setup

Use the DataFrame-oriented connector, `pysdmx.api.dc.pd.PandasConnector`.

Minimal setup:

```python
from pysdmx.api.dc import Endpoints
from pysdmx.api.dc.pd import PandasConnector

conn = PandasConnector(Endpoints.BIS)
```

If the requested service is not present in `Endpoints`, initialize the
connector with a SDMX-REST v2 base URL string directly.

## Discovery Strategy

Prefer this order:

1. Call `dataflows()` once for the selected service.
2. Match the user terms locally against each dataflow's `id`, `name`, and
   `description`.
3. Call `dataflow(...)` only for the directly matched candidates.
4. Only if that direct pass fails, inspect broader candidate dataflows and
   search component and code metadata.

### If the user asks for a statistical domain but not for a specific service

When the caller asks a general discovery question such as "Where can I find
data about exchange rates?", do not assume a single service.

Instead:

1. Iterate over every member of `pysdmx.api.dc.Endpoints`.
2. For each endpoint, construct a `PandasConnector`.
3. Call `dataflows()` once on that connector.
4. Match the user terms locally against the returned dataflows.
5. Return every matching dataflow across all services.

Only skip this cross-service iteration when the user explicitly names a
specific provider or service, or when they supply a concrete SDMX-REST base
URL.

## Workflow

### Step 1: Discover candidate dataflows

Use one unfiltered `dataflows()` call when the service is already known:

```python
flows = conn.dataflows()
terms = ["exchange rate", "swiss franc", "dollar"]
matches = []

for flow in flows:
    text = " ".join(
        [
            flow.id,
            str(flow.name or ""),
            str(flow.description or ""),
        ]
    ).lower()
    if any(term in text for term in terms):
        matches.append(flow)
```

Do not stop here. Some concepts are represented only by component or code
labels inside broader dataflows.

### Step 2: Inspect candidate dataflows

`dataflow(...)` accepts:

- A discovered object from `conn.dataflows()`.
- A short string form like `"BIS:CBS(1.0)"`.
- A URN string.
- Any object exposing `id`, `agency`, and `version`.

Inspect the candidate:

```python
cbs = conn.dataflow(flows[0])
print(f"Name: {cbs.name}")
print(f"Number of observations: {cbs.obs_count}")
print(f"Number of series: {cbs.series_count}")
```

Use `obs_count` and `series_count` (when available) as early size signals.
If either metric is large, tighten filters before pulling data.

Inspect dimensions and available values:

```python
for d in cbs.components.dimensions:
    dv = [c.id for c in (d.enumeration or []) if c is not None]
    print(f"{d.id}: {','.join(dv)}.")
```

Translate user intent by searching component and code `id`, `name`, and
`description` fields.

Matching policy for agents:

1. Match target component by exact `id` first, else partial match on
   `name`/`description` (case-insensitive).
2. Inside that component, match code by exact `id` first, else partial
   match on code `name`/`description`.
3. If multiple code matches remain in the same component, keep all of
   them and build a multi-value filter for that component.
4. For phrases such as "in Switzerland", inspect every dimension whose
   available codes contain the target country code (for example `CH`), not
   only common country dimension names. Report whether the match is a
   reporting country, counterparty country, reference area, currency, or
   another role when the component metadata makes this clear.
5. Ask a disambiguation question only when the target component itself
   is ambiguous.
6. If no match is found, report which concept could not be mapped.

Availability rule:

- `dataflow(...)` returns availability-backed values, that is, values for
  which data actually exist in the current scope.
- A code may still be valid in the full codelist even when it is absent
  from `dataflow(...).components[...].enumeration`.
- If a user asks about a specific label or code and it is missing from
  availability, verify against structural metadata before concluding that it
  does not exist.

Scope availability when needed:

When a dataflow is large, inspect availability for a targeted subset first.
`dataflow` accepts a `filters` parameter that scopes the returned
availability information:

- `filters=None` (default): return availability for the full dataflow.
- `filters` set: return availability for the matching subset only
  (that is, values that remain available after applying filters).

Example:

```python
cbs_subset = conn.dataflow(cbs, "L_POSITION = 'D' AND L_REP_CTY = 'CH'")
print(cbs_subset.series_count)
```

If the user asks only whether data are available, stop at `dataflow(...)`
once availability for the requested subset has been established. Do not call
`data(...)` unless the user also asks to retrieve observations or unless
additional validation is necessary.

The same filter formats accepted by `data(...)` work here as well:

- query filter objects from `pysdmx.api.dc.query`
- SQL-style strings
- Python boolean expressions

### Step 3: Retrieve data

The `data` method requires `dataflow` and returns a DataFrame when using
`PandasConnector`.

Translate natural language intent into `component_id = code_id` filters
using Step 2 metadata.

Example:

```python
query = "FREQ = 'D' AND EXR_TYPE = 'SP00' AND CUR = 'CHF'"
df = conn.data(cbs, query)
```

If a phrase matches multiple codes in one component (for example,
multiple currencies), include all matched codes using `IN`.

Important parser note:

- Query strings currently support conjunctions (`AND`) between clauses.
- Do not generate `OR` in query strings.
- For multiple values of the same component, use `IN (...)` instead.

Date cutoff note:

- Prefer pushing date/time filters such as `TIME_PERIOD >= '2020-Q1'`
  down to the service first, both for `dataflow(...)` and `data(...)`,
  when the targeted service is known or expected to support them.
- Date/datetime comparisons in string queries may not be supported for
  all datasets/connectors.
- If the service rejects the query, ignores the date constraint, or returns
  inconsistent results, fall back to retrieving the narrowest safe subset
  first (for example by non-time dimensions) and then apply time filtering
  in pandas.

```python
query = "FREQ = 'M' AND REF_AREA = 'RU' AND TIME_PERIOD >= '2018-01'"

try:
    df = conn.data(cbs, query)
except Exception:
    df = conn.data(cbs, "FREQ = 'M' AND REF_AREA = 'RU'")

df = df[df["TIME_PERIOD"] >= "2018-01"]
```

Default behavior:

- `infer_index=True` (index inferred from series key and time period)
- `infer_series_keys=True` (series keys generated)

Disable either when needed:

```python
df = conn.data(
    cbs,
    "L_POSITION = 'D' AND L_REP_CTY = 'CH'",
    infer_index=False,
    infer_series_keys=False,
)
```

By default, dtypes are applied from the DSD schema (`apply_schema=True`).
Disable if needed:

```python
df = conn.data(cbs, "L_POSITION = 'D' AND L_REP_CTY = 'CH'", apply_schema=False)
print(df.dtypes)
```

Coded components are represented as categorical data by default.

Use `labels` to control rendered category values:

- `id` (default): code IDs only.
- `name`: replace IDs with names.
- `both`: `ID: Name`.

Use `columns` to reduce output size and focus on required fields:

```python
df = conn.data(
    cbs,
    "L_POSITION = 'D' AND L_REP_CTY = 'CH'",
    columns=["OBS_VALUE", "OBS_STATUS"],
)
```

If `columns` is omitted, all DSD-defined components are included.

## Agent-Optimized Execution Guidance

When an agent is asked to discover and retrieve data, use this sequence:

1. Initialize `PandasConnector` from `Endpoints`.
2. Call `dataflows()` once for the selected service.
3. Match the user's terms locally against each returned dataflow's `id`,
  `name`, and `description`.
4. Call `dataflow(...)` for the directly matched candidates.
5. If the question is availability-only, use `dataflow(..., filters=...)`
  to answer it and stop there.
6. Only if no direct candidate works, inspect broader domain candidates and
  search component and code `id`, `name`, and `description` fields for
   the user's concepts.
7. If needed, call `dataflow(..., filters=...)` to scope availability to
   the subset implied by user intent.
8. Inspect dimensions and propose valid filter values.
9. When retrieving observations, push down time filters first if the
  service is known or expected to support them.
10. Retrieve a constrained sample with `data(...)`.
11. If time-filter pushdown fails or behaves incorrectly, retry with the
  narrowest non-time subset and apply the time cutoff locally.
12. Only then expand scope (more columns, broader filters, or full pull).

### Safety and efficiency defaults for agents

- Start with targeted filters to avoid huge DataFrames.
- Prefer one `dataflows()` request per service and local term matching over
  repeated `dataflows(search_term)` requests for synonyms.
- Search component and code labels in candidate dataflows before concluding
  that no data exist for a topic.
- Use `dataflow(..., filters=...)` to validate remaining available values
  before broad retrieval.
- For availability-only questions, answer from `dataflow(...)` and avoid
  `data(...)` unless observation retrieval is explicitly requested.
- Compare `obs_count` and `series_count` between full and filtered
  availability to decide whether additional narrowing is needed.
- Prefer server-side time-filter pushdown when supported, but fall back to
  local pandas filtering if the service does not support date comparisons
  correctly.
- Request only needed columns via `columns` when possible.
- Keep `labels="id"` unless human-readable output is explicitly required.
- Prefer schema-applied dtypes unless downstream logic needs raw strings.
- If no matching dataflows are found, refine search terms before broad pulls.
- If `Endpoints` has no match for the service, switch to a caller-provided
  base URL.

### Minimal end-to-end template

```python
from pysdmx.api.dc import Endpoints
from pysdmx.api.dc.pd import PandasConnector

conn = PandasConnector(Endpoints.BIS)

flows = conn.dataflows()
target = next(f for f in flows if "banking" in str(f.name).lower())
detail = conn.dataflow(target)

subset = conn.dataflow(
    detail,
    "L_POSITION = 'D' AND L_REP_CTY = 'CH'",
)

df = conn.data(
    detail,
    "L_POSITION = 'D' AND L_REP_CTY = 'CH'",
    columns=["OBS_VALUE", "OBS_STATUS"],
)
```

