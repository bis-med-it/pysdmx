.. _pandas_toolkit:

Pandas Toolkit
==============

The Pandas Toolkit provides functions to help leveraging the SDMX information model 
in Pandas data frames.

Getting the schema of a Pandas Data Frame
-----------------------------------------

The :meth:`pysdmx.toolkit.pd.to_pandas_schema` function infers the schema of a Pandas
Data Frame from a collection of SDMX components. The schema is a dictionary mapping
component IDs to their corresponding Pandas data types. The dictionary can be used
as input to the Pandas `astype` method to cast DataFrame columns to the desired types.

.. code-block:: python

    from pysdmx.api.fmr import RegistryClient
    from pysdmx.toolkit.pd import to_pandas_schema

    fmr = RegistryClient("https://registry.sdmx.io/sdmx/v2/")

    df = fmr.get_dataflow_details("BIS.CBS", "CBS", "1.0")

    schema = to_pandas_schema(df.components)

    print(schema)

    # The schema can then be used with a Pandas Data Frame, 
    # via the astype method, e.g.: df.astype(schema)

If you prefer to retrieve the type for each column individually, you can use the
:meth:`pysdmx.toolkit.pd.to_pandas_type` instead.