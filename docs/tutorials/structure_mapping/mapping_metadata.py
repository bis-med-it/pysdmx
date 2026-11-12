"""Retrieve metadata for a mapping process.

This script shows how pysdmx can be used to retrieve the structures required
to map data from one structure to another.
"""

from pathlib import Path

from pysdmx.api.fmr import RegistryClient
from pysdmx.io import read_sdmx

# Step 1: Connect to the service that contains the required structures.
client = RegistryClient("https://registry.sdmx.org/sdmx/v2")
# Note: The client can connect to any compatible SDMX-RESTv2 service.

# Step 2: Retrieve the required mapping definition.
representation_map = client.get_code_map("SDMX", "CL_AREA_ISO_M49", "1.0")
print(representation_map)

# Step 3: Inspect the mapping definition. This is a very simple mapping between
# two-letter ISO country codes and their corresponding M49 codes.

# Step 4: Load a data file.
# Note: The CSV file was generated automatically, i.e. there is
# no guarantee the data are meaningful.
file_path = Path(__file__).parent.parent / "samples" / "bpm6_bop_m.csv"
submission = read_sdmx(file_path)

# Step 5: Inspect the data.
# The data are represented as Pandas DataFrames.

# Step 6: Map the REF_AREA and COUNTERPART_AREA columns
# Note: This should be done in a more subtle way, i.e. getting the DSD and
# inferring the components that can be mapped. For this demonstration,
# explicitly selecting the columns is sufficient to demonstrate how mapping
# works.
# Note: pysdmx will soon offer a map() function!
mapping_candidates = ["REF_AREA", "COUNTERPART_AREA"]
code_map = {vm.source: vm.target for vm in representation_map}

for ds in submission.data:
    df = ds.data
    for component in mapping_candidates:
        df[component] = df[component].replace(code_map)

# Step 7: Inspect the object and check that AR (Argentina) and UY (Uruguay)
# have been mapped to 032 and 858 respectively. R1 (Belgo-Luxembourg Economic
# Union) remains unchanged, as it is not mapped in the representation map.
