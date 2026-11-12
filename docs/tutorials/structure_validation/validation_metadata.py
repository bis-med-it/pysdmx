"""Retrieve metadata for validation process."""

from pathlib import Path

from pysdmx.api.fmr import RegistryClient
from pysdmx.io import read_sdmx

# Step 1: Connect to the service that contains the required structures.
client = RegistryClient("https://registry.sdmx.org/sdmx/v2")
# Note: The client can connect to any compatible SDMX-RESTv2 service.

# Step 2: Retrieve the required schema
schema = client.get_schema("dataflow", "ESTAT", "BPM6_BOP_M", "2.6.0")
print(schema)

# Step 3: Inspect the schema.
# Notice the list of components, their data type, enumerations, and facets.
# Notice the list of structures used to generate the schema (`artefacts`).
# Notice the attribute relationships.

# Step 4: Load a data file
# Note: The CSV file was generated automatically, i.e. there is
# no guarantee the data are meaningful.
file_path = Path(__file__).parent.parent / "samples" / "bpm6_bop_m.csv"
submission = read_sdmx(file_path)
print(submission.data[0])

# Step 5: Inspect the data.
# Notice you get a Pandas DataFrame.

# Bonus: Write your own code to validate a data message using the schema.
# Note: pysdmx will soon offer a validate() function!
for ds in submission.data:
    df = ds.data

    # For example, check that values belong to the relevant enumerations.
    for column in df.columns:
        component = schema.components[column]
        if component and component.enumeration:
            allowed_values = {code.id for code in component.enumeration}
            values = {value for value in df[column].dropna() if value != ""}
            unexpected = values - allowed_values
            if unexpected:
                print(f"Found invalid values for {component.id}: {unexpected}")
