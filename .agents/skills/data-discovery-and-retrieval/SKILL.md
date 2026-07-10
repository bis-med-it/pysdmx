---
name: data-discovery-and-retrieval
description: Discover and retrieve SDMX datasets from a service. Use this skill when the user wants to find available datasets, learn more about a dataset (e.g. inspect dimensions and codes), map natural-language requests to valid data filters, and download results as a pandas DataFrame, even if they do not explicitly mention SDMX.
---
# SDMX Data Discovery and Retrieval

## Goal

Use `pysdmx` connectors implementing the SDMX-REST **Data Discovery and
Retrieval** profile to:

1. Discover available dataflows (datasets).
2. Inspect a selected dataflow to build effective queries.
3. Retrieve filtered data as a pandas DataFrame.

## Prerequisites

- Install extra dependencies: `pysdmx[data]`

## Connector Setup

`pysdmx` provides a DataFrame-oriented connector, `pysdmx.api.dc.pd.PandasConnector`. 

Example setup:

```python
from pysdmx.api.dc import Endpoints
from pysdmx.api.dc.pd import PandasConnector

conn = PandasConnector(Endpoints.BIS)
```

The connector requires a service entry point URL for data and metadata.
Use `Endpoints` whenever possible.

### If the user asks for a statistical domain but not for a specific service

When the caller asks a general discovery question such as "Where can I find
data about exchange rates?", do not assume a single service.

Instead:

1. Iterate over every member of `pysdmx.api.dc.Endpoints`.
2. For each endpoint, construct a `PandasConnector`.
3. Call `dataflows(search_term)` on that connector.
4. Return every matching dataflow across all services.

The search term should be matched using the connector's built-in
`dataflows(search_term)` behavior, which checks whether the term appears in a
dataflow's `id`, `name`, or `description`.

Example:

```python
from pysdmx.api.dc import Endpoints
from pysdmx.api.dc.pd import PandasConnector

search_term = "exchange rates"
matches = []

for endpoint in Endpoints:
  conn = PandasConnector(endpoint)
  flows = conn.dataflows(search_term)
  matches.extend((endpoint.name, flow) for flow in flows)

for service_name, flow in matches:
  print(service_name, flow.id, flow.name)
```

Only skip this cross-service iteration when the user explicitly names a
specific provider or service, or when they supply a concrete SDMX-REST base
URL.

### If `Endpoints` does not contain the requested service

When the caller requests a service that is not present in `Endpoints`:

1. Ask for the SDMX-REST v2 API base URL (for example,
  `https://example.org/api/v2`).
2. Initialize `PandasConnector` with that URL string directly.

Example fallback setup:

```python
from pysdmx.api.dc.pd import PandasConnector

service_url = "https://example.org/api/v2"
conn = PandasConnector(service_url)

flows = conn.dataflows()
```

## Workflow

### Step 1: Discover available datasets (`dataflows`)

List all available dataflows:

```python
flows = conn.dataflows()
print(f"Found {len(flows)} dataflows.")
for f in flows:
    print(f.short_urn)
```

Filter by a term (matches ID, name, or description):

```python
flows = conn.dataflows("banking")
print(f"Found {len(flows)} dataflows.")
for f in flows:
    print(f.short_urn)
```

If the user is exploring a topic rather than a known service, repeat this
search for every endpoint in `Endpoints` and aggregate the results before
presenting candidate datasets.

### Step 2: Inspect one dataset (`dataflow`)

Fetch details for a selected dataflow. `flows[0]` is only one convenient way
to choose a candidate from discovery results.

`dataflow(...)` accepts any valid maintainable identification, such as:

- A discovered object (for example, one item from `conn.dataflows()`).
- A short string form like `"BIS:CBS(1.0)"`.
- A URN string.
- Any object exposing `id`, `agency`, and `version`.

Examples:

```python
cbs = conn.dataflow(flows[0])

cbs2 = conn.dataflow("BIS:CBS(1.0)")
```

Inspect basic metadata:

```python
print(f"Name: {cbs.name}")
print(f"Number of series: {cbs.series_count}")
```

Inspect queryable dimensions and available values:

```python
for d in cbs.components.dimensions:
    dv = [c.id for c in d.enumeration]
    print(f"{d.id}: {','.join(dv)}.")
```

Build a semantic lookup from components and codes before filtering.
In SDMX, both components and codes can carry `id`, `name`, and
`description`, so agents should use these fields to translate user intent.

```python
dimension_catalog = []
for dim in cbs.components.dimensions:
    codes = [
        {
            "id": code.id,
            "name": (code.name or ""),
            "description": (code.description or ""),
        }
        for code in (dim.enumeration or [])
    ]
    dimension_catalog.append(
        {
            "id": dim.id,
            "name": (dim.name or ""),
            "description": (dim.description or ""),
            "codes": codes,
        }
    )
```

Matching policy for agents:

1. Match target component by exact `id` first, else partial match on
   `name`/`description` (case-insensitive).
2. Inside that component, match code by exact `id` first, else partial
   match on code `name`/`description`.
3. If multiple code matches remain in the same component, keep all of
   them and build a multi-value filter for that component.
4. Ask a disambiguation question only when the target component itself
   is ambiguous.
5. If no match is found, report which concept could not be mapped.

The connector returns values for which data actually exist (not every
theoretical codelist value), which helps avoid empty queries.

#### Filter availability information with `dataflow(..., filters=...)`

When a dataflow is large, inspect availability for a targeted subset first.
`dataflow` accepts a `filters` parameter that scopes the returned
availability information:

- `filters=None` (default): return availability for the full dataflow.
- `filters` set: return availability for the matching subset only
  (that is, values that remain available after applying filters).

Use this to narrow candidate codes before constructing the final
`data(...)` query.

Example with filter objects:

```python
from pysdmx.api.dc.query import MultiFilter, Operator, TextFilter

f1 = TextFilter("L_POSITION", Operator.EQUALS, "D")
f2 = TextFilter("L_REP_CTY", Operator.EQUALS, "CH")
mf = MultiFilter([f1, f2])

cbs_subset = conn.dataflow(cbs, mf)

for d in cbs_subset.components.dimensions:
    print(d.id, [c.id for c in (d.enumeration or [])])
```

`filters` follows the same syntax accepted by `data(...)` queries:

- query filter objects from `pysdmx.api.dc.query` (for example `MultiFilter`)
- SQL-style strings (for example `"L_POSITION = 'D' AND L_REP_CTY = 'CH'"`)
- Python boolean expressions (for example
  `"L_POSITION == 'D' and L_REP_CTY == 'CH'"`)

### Step 3: Retrieve data (`data`)

The `data` method requires `dataflow` and returns a DataFrame when using
`PandasConnector`.

#### `dataflow` parameter

Accepted formats:

- String:
  - SDMX URN, e.g.
    `urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:CBS(1.0)`
  - short form, e.g. `BIS:CBS(1.0)`
- Python object exposing:
  - `id`
  - `agency`
  - `version`

Typical accepted objects include `pysdmx.Dataflow`,
`pysdmx.DataflowInfo`, and `pysdmx.Reference`.

#### Translate natural language intent into SDMX filters

Before calling `data(...)`, map user phrasing to concrete
`component_id=code_id` pairs using Step 2 metadata.

Example intent: "daily effective exchange rates for the Swiss franc"

- `daily` -> component `FREQ`, code `D`
- `effective exchange rate` -> component `EXR_TYPE`, code `SP00`
- `Swiss franc` -> component `CUR`, code `CHF`

Resulting query:

```python
query = "FREQ = 'D' AND EXR_TYPE = 'SP00' AND CUR = 'CHF'"
df = conn.data(cbs, query)
```

If a phrase matches multiple codes in one component (for example,
multiple currencies), include all matched codes using `IN`.
For example: `CUR IN ('CHF','EUR')`.

Important parser note:

- Query strings currently support conjunctions (`AND`) between clauses.
- Do not generate `OR` in query strings.
- For multiple values of the same component, use `IN (...)` instead.

Example:

```python
query = "FREQ = 'D' AND REF_AREA IN ('CH','XM')"
df = conn.data(cbs, query)
```

Date cutoff note:

- Date/datetime comparisons in string queries may not be supported for
  all datasets/connectors.
- When unsupported, retrieve constrained data first (for example by
  dimensions) and then apply time filtering in pandas.

```python
df = conn.data(cbs, "FREQ = 'M' AND REF_AREA = 'RU'")
df = df[df["TIME_PERIOD"] >= "2018-01"]
```

#### Apply query filters

Example with explicit filter objects:

```python
from pysdmx.api.dc.query import MultiFilter, Operator, TextFilter

f1 = TextFilter("L_POSITION", Operator.EQUALS, "D")
f2 = TextFilter("L_REP_CTY", Operator.EQUALS, "CH")
mf = MultiFilter([f1, f2])

df = conn.data(cbs, mf)
print(df)
```

Default behavior:

- `infer_index=True` (index inferred from series key and time period)
- `infer_series_keys=True` (series keys generated)

Disable either when needed:

```python
df = conn.data(
    cbs,
    mf,
    infer_index=False,
    infer_series_keys=False,
)
```

#### Alternative query formats

The same filter can be passed as:

- SQL-style string: `"L_POSITION = 'D' AND L_REP_CTY = 'CH'"`
- Python-style boolean expression:
  `"L_POSITION == 'D' and L_REP_CTY == 'CH'"`

```python
df = conn.data(cbs, "L_POSITION = 'D' AND L_REP_CTY = 'CH'")
```

#### Data types and schema application

By default, dtypes are applied from the DSD schema (`apply_schema=True`).
Disable if needed:

```python
df = conn.data(cbs, mf, apply_schema=False)
print(df.dtypes)
```

Coded components are represented as categorical data by default.

#### Label representation for coded fields

Use `labels` to control rendered category values:

- `id` (default): code IDs only.
- `name`: replace IDs with names.
- `both`: `ID: Name`.

```python
df = conn.data(cbs, "L_POSITION = 'D' AND L_REP_CTY = 'CH'", labels="name")
```

#### Select specific output columns

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
2. Call `dataflows(search_term)` if user intent includes a topic.
3. Select one candidate dataflow and call `dataflow(...)`.
4. If needed, call `dataflow(..., filters=...)` to scope availability to
  the subset implied by user intent.
5. Inspect dimensions and propose valid filter values.
6. Retrieve a constrained sample with `data(...)`.
7. Only then expand scope (more columns, broader filters, or full pull).

### Safety and efficiency defaults for agents

- Start with targeted filters to avoid huge DataFrames.
- Use `dataflow(..., filters=...)` to validate remaining available values
  before broad retrieval.
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

flows = conn.dataflows("banking")
target = conn.dataflow(flows[0])

subset = conn.dataflow(
    target,
    "L_POSITION = 'D' AND L_REP_CTY = 'CH'",
)

df = conn.data(
    target,
    "L_POSITION = 'D' AND L_REP_CTY = 'CH'",
    columns=["OBS_VALUE", "OBS_STATUS"],
)
```

