Pandas Toolkit
==============

The Pandas Toolkit provides functions to help leveraging the SDMX information model 
in Pandas data frames.

.. code-block:: python

    from pysdmx.api.fmr import RegistryClient
    from pysdmx.toolkit.pd import to_pandas_schema

    fmr = RegistryClient("https://registry.sdmx.io/sdmx/v2/")

    df = fmr.get_dataflow_details("BIS.CBS", "CBS", "1.0")

    schema = to_pandas_schema(df.components)

    print(schema)

    # The schema can then be used with a Pandas Data Frame, 
    # via the astype method, e.g.: df.astype(schema)

Mapping SDMX data types to Pandas
---------------------------------

.. autofunction:: pysdmx.toolkit.pd.to_pandas_type

.. autofunction:: pysdmx.toolkit.pd.to_pandas_schema
