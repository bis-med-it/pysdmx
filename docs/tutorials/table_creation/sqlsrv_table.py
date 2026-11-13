"""Retrieve structural metadata and create a SQL Server table.

This script demonstrates how pysdmx can use structural metadata
to generate a SQL Server CREATE TABLE statement.
"""

from pysdmx.api.fmr import RegistryClient
from pysdmx.toolkit.sqlsrv import create_table

# Step 1: Connect to an SDMX-RESTv2 service containing the required structures.
client = RegistryClient("https://registry.sdmx.org/sdmx/v2")

# Step 2: Retrieve the required schema
schema = client.get_schema("datastructure", "IMF", "BOP", "2.6.0")

# Step 3: Inspect the schema.
# Notice the list of components, data type, facets, role and required fields.

# Step 4: Generate a SQL Server CREATE TABLE statement from the DSD.
# By default, the dimension values form the primary key and an index is created
# for each dimension. Facets determine column sizes  and each component's
# `required` property determines whether the corresponding column is nullable.
# Names are used as documentation.
create_stmt = create_table(schema)
print(create_stmt)
