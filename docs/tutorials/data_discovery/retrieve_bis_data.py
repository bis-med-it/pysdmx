"""Discover and retrieve data using data connectors."""

from pysdmx.api.dc import Endpoints
from pysdmx.api.dc.pd import PandasConnector

# Step 1: Connect to an SDMX-RESTv2 service which supports the SDMX
# data discovery and retrieval profile.
conn = PandasConnector(Endpoints.BIS)

# Step 2: List all dataflows provided by the service
flows = conn.dataflows()
print(f"Found {len(flows)} dataflows.")
for f in flows:
    print(f.short_urn)

# Step 3: Let's filter the dataflows by providing a search term.
flows = conn.dataflows("banking")
print(f"Found {len(flows)} dataflows.")
for f in flows:
    print(f.short_urn)

# Step 4: After identifying a dataflow of interest, the next step is to
# gather detailed information about it to learn how to query it effectively
cbs = conn.dataflow(flows[0])

# You can print details about the dataflow, such as its name and availability
# metrics, if provided by the source:
print(f"Name: {cbs.name}")
print(f"Number of observations: {cbs.obs_count}")
print(f"Number of series: {cbs.series_count}")

# To query data effectively, examine the dimensions.
for d in cbs.components.dimensions:
    dv = [c.id for c in d.enumeration]
    print(f"{d.id}: {','.join(dv)}.")

# Step 5: Once you know how to query the data, the next step is to download it.
# Here, we will add some filters. This can be done in different ways, for
# example, using a SQL-like string
df = conn.data(cbs, "L_POSITION = 'D' AND L_REP_CTY = 'CH'")

# Notice that you get a Pandas DataFrame back and the types are optimized based
# on the data structure, i.e. coded components are defined as categorical data,
# making them efficient for analysis.
print(df.dtypes)

# The `columns` parameter allows you to specify which columns should be
# included in the resulting DataFrame. This is useful when you are only
# interested in a subset of the components, as it can reduce the size of the
# DataFrame and make the output more focused.

df = conn.data(
    cbs,
    "L_POSITION = 'D' AND L_REP_CTY = 'CH'",
    columns=["OBS_VALUE", "OBS_STATUS"],
)
print(df)
