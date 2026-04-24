Data discovery and retrieval
============================

One of the core use cases of SDMX is enabling data consumers to
**discover and retrieve available datasets from a source**. This
functionality is formalized in the SDMX-REST "Data Discovery and
Retrieval" profile, implemented by the pysdmx connector. Below,
we describe the features supported by this connector.

.. warning::

    The connectors are experimental and subject to change without
    prior notice. They are not covered by semantic versioning
    guarantees, and backward incompatible modifications to these
    classes will not result in a major version increment. Use them
    with caution in production environments or critical processes.

Setup: Initializing the pysdmx Connector
----------------------------------------

``pysdmx`` offers two connectors compliant with the SDMX-REST
"Data Discovery and Retrieval" profile:

- ``pysdmx.api.dc.rest.SdmxConnector``: A basic connector for
  SDMX-REST services.

- ``pysdmx.api.dc.pd.PandasConnector``: A connector, based on the
  one above, that returns data as a Pandas DataFrame.

For this demo, we will use the **Pandas Connector**, which can be
initialized as follows:

.. code-block:: python

    from pysdmx.api.dc import Endpoints
    from pysdmx.api.dc.pd import PandasConnector

    conn = PandasConnector(Endpoints.BIS)

The connector requires the service's entry point URL to retrieve data 
and metadata, and we can easily get it using the ``Endpoints`` enum.
Now that the connector is set up, let's explore its capabilities!

Data Discovery, step 1: Discover Available Datasets
---------------------------------------------------

To begin, we need to **list available datasets** in the source to
**identify those of interest**. This can be achieved using the 
``dataflows`` method provided by the connector:

.. code-block:: python

    flows = conn.dataflows()
    print(f"Found {len(flows)} dataflows.")
    for f in flows:
        print(f.short_urn)

    # Output:
    # Found 32 dataflows.
    # Dataflow=BIS:BIS_REL_CAL(1.0)
    # Dataflow=BIS:WS_CBPOL(1.0)
    # Dataflow=BIS:WS_CBS_PUB(1.0)
    # Dataflow=BIS:WS_CBTA(1.0)
    # Dataflow=BIS:WS_CPMI_CASHLESS(1.0)
    # ... more lines

You can also filter datasets by providing a search term.
The method will return dataflows where the term matches the
ID, name, or description:

.. code-block:: python

    flows = conn.dataflows("banking")
    print(f"Found {len(flows)} dataflows.")
    for f in flows:
        print(f.short_urn)

    # Output:
    # Found 5 dataflows.
    # Dataflow=BIS:WS_CBS_PUB(1.0)
    # Dataflow=BIS:WS_LBS_D_PUB(1.0)
    # Dataflow=BIS.CBS:CBS(1.0)
    # Dataflow=BIS.LBS:LBSN(1.0)
    # Dataflow=BIS.LBS:LBSR(1.0)

Data Discovery, step 2: Gather Information about a Dataset
----------------------------------------------------------

After identifying a dataflow of interest, the next step is to
gather detailed **information about it** to learn how to
**query it effectively**. This can be achieved using the 
``dataflow`` method provided by the connector:

.. code-block:: python
    
    # Fetch information about the WS_CBS_PUB dataflow
    cbs = conn.dataflow(flows[0])

Basic information
^^^^^^^^^^^^^^^^^

You can print details about the dataflow, such as its name
and the number of series it contains:

.. code-block:: python

    print(f"Name: {cbs.name}")
    print(f"Number of series: {cbs.series_count}")

    # Output:
    # Name: Consolidated banking
    # Number of series: 227004

Querying dimensions
^^^^^^^^^^^^^^^^^^^

To query data effectively, examine the dimensions and their possible
values:

.. code-block:: python

    for d in cbs.components.dimensions:
        dv = [c.id for c in d.enumeration]
        print(f"{d.id}: {','.join(dv)}.")

    # Output:
    # FREQ: Q.
    # L_MEASURE: S,B.
    # ...  more lines

Rather than returning all theoretically possible values from the codelist
for each dimension, the connector only provides values for which data
actually exist, reducing the risk of executing queries that yield no results.

Data Retrieval: Download Data
-----------------------------

Once you know how to query the data, the next step is to **download it**
as a **Pandas Data Frame**. This can be achieved using the ``data`` method
provided by the connector. The ``data`` method has one mandatory parameter,
``dataflow``.

Specifying the Dataflow
^^^^^^^^^^^^^^^^^^^^^^^

The `dataflow` parameter specifies the dataflow from which to retrieve data.
It can accept the following types of input:

- **String**: A string representation of the dataflow, which can be an **SDMX URN**
  (e.g. ``urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:CBS(1.0)``) or 
  a short notation for the dataflow, such as ``BIS:CBS(1.0)``.

- **Python Object**: A Python object that has the following three properties:

    - ``id``: The unique identifier of the dataflow.
    - ``agency``: The agency responsible for the dataflow.
    - ``version``: The version of the dataflow.

  These three properties (``id``, ``agency``, and ``version``) are the standard attributes
  used in SDMX to uniquely identify artefacts of a certain type, such as a Dataflow.
  Examples of Python objects that can be passed include ``pysdmx.Dataflow``,
  ``pysdmx.DataflowInfo``, or ``pysdmx.Reference``.

Applying Query Filters
^^^^^^^^^^^^^^^^^^^^^^

To filter the data, you can use `pysdmx` query filters. For example, to retrieve
cross-border claims (`L_POSITION=D`) for Switzerland (`L_REP_CTY=CH`):

.. code-block:: python

    from pysdmx.api.dc.query import MultiFilter, Operator, TextFilter

    f1 = TextFilter("L_POSITION", Operator.EQUALS, "D")
    f2 = TextFilter("L_REP_CTY", Operator.EQUALS, "CH")
    mf = MultiFilter([f1, f2])

    df = conn.data(cbs, mf)

    print(df)

    # Output:
    #                                         FREQ      L_MEASURE
    # SERIES_KEY                 TIME_PERIOD                                             
    # Q.S.CH.4R.U.D.A.A.TO1.A.5J 2005-Q2      Q         S   
    #                            2005-Q3      Q         S   
    #                            2005-Q4      Q         S   
    #                            2006-Q1      Q         S   
    #                            2006-Q2      Q         S   
    # ... more lines
    # [164 rows x 24 columns]

By default, the connector infers the index using the series keys and the time period. 
This behavior can be disabled by setting ``infer_index=False``. Similarly, the
generation of series keys is enabled by default and can be turned off by setting 
``infer_series_keys=False``.

Alternative Query Formats
^^^^^^^^^^^^^^^^^^^^^^^^^

The same query can also be expressed as:

- **SQL string**: "L_POSITION = 'D' AND L_REP_CTY = 'CH'"
- **Python boolean expression**: "L_POSITION == 'D' and L_REP_CTY == 'CH'"

.. code-block:: python

    df = conn.data(cbs, "L_POSITION = 'D' AND L_REP_CTY = 'CH'")

Data Types in the Pandas DataFrame
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, the Pandas DataFrame applies data types based on the Data Structure
Definition (DSD). You can disable this feature by setting ``apply_schema=False``
when calling the ``data`` method.

.. code-block:: python
    
    print(df.dtypes)

    # Output:
    # DATAFLOW               str
    # FREQ              category
    # L_MEASURE         category
    # L_REP_CTY         category
    # CBS_BANK_TYPE     category
    # CBS_BASIS         category
    # L_POSITION        category
    # L_INSTR           category
    # REM_MATURITY      category
    # CURR_TYPE_BOOK    category
    # L_CP_SECTOR       category
    # L_CP_COUNTRY      category
    # OBS_VALUE          Float64
    # DECIMALS          category
    # UNIT_MEASURE      category
    # UNIT_MULT         category
    # TIME_FORMAT       category
    # COLLECTION        category
    # ORG_VISIBILITY    category
    # AVAILABILITY      category
    # TITLE_GRP           string
    # OBS_STATUS        category
    # OBS_CONF          category
    # OBS_PRE_BREAK      Float64
    # dtype: object

Coded components will be defined as categorical data, making them efficient for analysis.

Label Options for Category Fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``labels`` parameter allows you to control how category fields are represented in the
DataFrame. You can choose from the following options:

- **id** (Default): The DataFrame will include only the code IDs for category fields.
  This is the most compact representation.

- **name**:  The code IDs are replaced with their corresponding names, as defined in
  the codelists.
- **both**:  Both the code IDs and their names are included in the category fields,
  formatted as ``ID: Name``.

You can specify the ``labels`` parameter when calling the connector:

.. code-block:: python

    df = conn.data(cbs, "L_POSITION = 'D' AND L_REP_CTY = 'CH'", labels="name")

    print(df)

    # Output:
    #                                         FREQ          L_MEASURE
    # SERIES_KEY                 TIME_PERIOD                                       
    # Q.S.CH.4R.U.D.A.A.TO1.A.5J 2005-Q2      Quarterly     Amounts outstanding / Stocks   
    #                            2005-Q3      Quarterly     Amounts outstanding / Stocks   
    #                            2005-Q4      Quarterly     Amounts outstanding / Stocks   
    #                            2006-Q1      Quarterly     Amounts outstanding / Stocks   
    #                            2006-Q2      Quarterly     Amounts outstanding / Stocks   
    # ... more lines
    # [164 rows x 24 columns]

Selecting Specific Columns
^^^^^^^^^^^^^^^^^^^^^^^^^^

The `columns` parameter allows you to specify which columns should be included in the resulting
DataFrame. This is useful when you are only interested in a subset of the components, as it can
reduce the size of the DataFrame and make the output more focused.

.. code-block:: python

    df = conn.data(cbs, "L_POSITION = 'D' AND L_REP_CTY = 'CH'", columns=["OBS_VALUE", "OBS_STATUS"])

    print(df)

    # Output:
    #                                         OBS_STATUS   OBS_VALUE
    # SERIES_KEY                 TIME_PERIOD                       
    # Q.S.CH.4R.U.D.A.A.TO1.A.5J 2005-Q2      A            805455.0
    #                            2005-Q3      A            847949.0
    #                            2005-Q4      A            794753.0
    #                            2006-Q1      A            919947.0
    #                            2006-Q2      A            989307.0
    # [164 rows x 2 columns]

If the `columns` parameter is not specified, all components defined in the Data Structure
Definition (DSD) are included in the DataFrame.

We hope this demo has provided a helpful introduction to the capabilities of the pysdmx
connectors.