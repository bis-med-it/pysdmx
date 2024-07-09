.. _validate:

Validate your data
==================

In this tutorial, we'll explore how ``pysdmx`` facilitates **data
validation** in a metadata-driven approach, relying solely on the metadata
stored in an SDMX Registry.

There are various types of validation, and we'll focus on **structural
validation** in this scenario. Structural validation ensures that the
structure of data meets the expectations.

Required metadata
-----------------

For this scenario, the necessary metadata depends on the desired
thoroughness of validation. At a minimum, we need the **data structure**
information. However, for more comprehensive validation, we may consider
additional constraints from the **dataflow** or **provision agreement**.

Data Structure
^^^^^^^^^^^^^^

A data structure describes the expected structure of data, including component
types, data types, and whether components are mandatory. If components are
**coded**, the allowed values are also specified. This is the minimum
required for structural validation.

Dataflows
^^^^^^^^^

Dataflows allow defining one or more set of data sharing the same data
structure. For example, if we have a data structure about locational banking
statistics, we might want to define a dataflow representing the locational
banking statistics by country (residence) and another dataflow representing
the locational banking statistics by nationality. If we have a data structure 
representing bilateral foreign exchange reference rates, we might want to
create a dataflow for the subset of exchange rates published on a website on
a daily basis.

Expanding on this last example, we could define this subset of data using
constraints, i.e. setting the frequency dimension to “daily” and the currency
codes to the subset of codes that are published on a daily basis (e.g. CHF,
CNY, EUR, JPY, USD, etc.) and we would “attach” these constraints to the
dataflow. Taking these additional constraints into account makes the
validation more strict.

Provisioning metadata
^^^^^^^^^^^^^^^^^^^^^

Provision agreements and data providers indicate which providers supply data
for a dataflow. Constraints, such as expecting a provider to supply data only
for its own country, can be applied.

In summary, the following SDMX artifacts need to be in the SDMX Registry:
**AgencyScheme**, **Codelist**, **ConceptScheme**, and **Data Structure**.
For more thorough validation, additional metadata like **Data Constraint**,
**Dataflow**, **DataProviderScheme**, **DataStructure**, and
**ProvisionAgreement** is needed.

For additional information about the various types of SDMX artifacts, please
refer to the `SDMX documentation <https://sdmx.org/>`_.

Step-by-step solution
---------------------

``pysdmx`` allows retrieving metadata from an SDMX Registry in either a
synchronous (via ``pymedal.fmr.RegistryClient``) or asynchronous fashion
(via ``pymedal.fmr.AsyncRegistryClient``). Which one to use depends on the
use case (and taste), but we tend to use the asynchronous client by default,
as it is non-blocking.

Connecting to a Registry
^^^^^^^^^^^^^^^^^^^^^^^^

First, we will need an instance of the client, so that we can connect to our
target Registry. When instantiating the client, we need to pass the SDMX-REST
endpoint of the Registry. If we use the
`FMR <https://www.bis.org/innovation/bis_open_tech_sdmx.htm>`_, i.e. the
reference Implementation of the SDMX Registry specification, the endpoint
will be the URL at which the FMR is available, followed by ``/sdmx/v2/``.

.. code-block:: python

    from pysdmx.api.fmr import AsyncRegistryClient
    gr = AsyncRegistryClient("https://registry.sdmx.org/sdmx/v2/")

Retrieving the schema information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For this tutorial, we want to validate data received for the ``EDUCAT_CLASS_A``
dataflow maintained by UNESCO Institute for Statistics (``UIS``), as published
on the `SDMX Global Registry <https://registry.sdmx.org/>`_.

This dataflow is based on the ``UOE_NON_FINANCE`` data structure. If we view
the data structure using the Global Registry user interface, we will see that
many values are allowed for most coded components. For example, at the time
of writing, more than 80 codes are allowed for the ``AGE`` component. However,
if we look at the dataflow, we will see that only one value is allowed (``_T``).
This is because constraints (``CR_EDUCAT_ALL`` and ``CR_EDUCAT_CLASS_A`` in
this particular case) have been applied to the dataflow.

An SDMX-REST ``schema`` query can be used to retrieve what is allowed within
the context of a data structure, a dataflow, or a provision agreement. The
SDMX Registry then uses all available information (e.g., constraints) to return
a "schema" describing the "data validity rules" for the selected context. We
will use this to retrieve the metadata we need to validate our data.

As we want to make the validation as strict as possible, we want to consider
all available constraints. No information about data providers or provision
agreements is available for the selected dataflow in the Global Registry at the
time of writing, and so we will use the next available context, i.e. **dataflow**.

.. code-block:: python

    schema = await gr.get_schema("dataflow", "UIS", "EDUCAT_CLASS_A", "1.0")

Validating data
^^^^^^^^^^^^^^^

Many different types of checks can be implemented, and covering them all goes
beyond the scope of this tutorial. However, some common validation checks are
described below. For this tutorial, we will assume that the data was provided
in SDMX-CSV, and that the data file was read using Python CSV ``DictReader``.
That means, it is possible to iterate over the content of the file one row at
a time, and every row is represented as a dictionary, with the column header as
key and the cell content as value.

For example, to get the value for the AGE dimension:

.. code-block:: python

    for row in reader:
        age = row["AGE"]
        print(age)

Validating the components
"""""""""""""""""""""""""

The first thing we might want to do is to check whether we find the expected
columns in SDMX-CSV. Each column in the SDMX-CSV input should be either the
ID of a component defined in the data structure or one of the special SDMX-CSV
columns (``STRUCTURE``, ``STRUCTURE_ID``, or ``ACTION``).

.. code-block:: python

    sdmx_cols = ["STRUCTURE", "STRUCTURE_ID", "ACTION"]
    components = [c.id for c in schema.components]
    for col in reader.fieldnames:
        if col not in sdmx_cols and col not in components:
            raise ValueError(f"Found unexpected column: {col}")

Validating the data type
""""""""""""""""""""""""

``pysdmx`` returns the expected data type for each of the components in a data
structure. CSV treats everything as a string but the information provided by
``pysdmx`` may be used to attempt a type casting (or similar checks) and check
for errors reported in the process.

The exact code will depend on the library used. While the Python interpreter
only supports a few generic types, other Python libraries (like numpy, pandas,
or pyarrow) offer more options. Covering them all goes beyond the scope
of this tutorial, but the code below should be sufficient to give an idea.

.. code-block:: python

    from pysdmx.model import DataType
    for row in reader:
        for comp, value in row.items():
            data_type = schema.components[comp].dtype
            if data_type in [DataType.DOUBLE, DataType.FLOAT]:
                try:
                    float(value)
                except ValueError:
                    raise TypeError(f"{value} for component {comp} is not a valid {data_type}")

Validating with facets
""""""""""""""""""""""

SDMX allows defining so-called **facets**, to provide additional
constraints in addition to the data type. For example, we can say that a
component is a string, with a minimum length of 3 characters and a maximum
length of 10. This information is available via the ``facets`` property.

.. code-block:: python

    print(schema.components["COMMENT_DSET"].facets)
    max_length=1050

This information can of course be used for validation purposes:

.. code-block:: python

    for row in reader:
        for comp, value in row.items():
            facets = schema.components[comp].facets
            if facets and facets.max_length:
                if len(value) > facets.max_length:
                    raise ValueError(f"The value for {comp} is longer than {facets.max_length} characters")

Validating coded components
""""""""""""""""""""""""""""

SDMX distinguishes between **coded** and **uncoded** components. The list of
codes (defined either in a codelist or a valuelist) is available via the
``codes`` property:

.. code-block:: python

    coded_comp = {
        comp.id: [code.id for code in comp.codes]
        for comp in schema.components
        if comp.codes
    }
    
    for row in reader:
        for comp, value in row.items():
            if comp in coded_comp and value not in coded_comp[comp]:
                raise ValueError(f"{value} is not one of the expected codes for {comp}")

Validating mandatory components
""""""""""""""""""""""""""""""""

The data structure indicates whether a component is required. However, this
check also requires taking the message action into account. After all, if the
message only contains updates and revisions to previously provided data, and
if the value of a mandatory component hasn't changed, then, in principle, the
value does not need to be sent again. However, assuming the check for
mandatory components needs to run, the ``required`` property can be used:

.. code-block:: python

    for row in reader:
        for comp, value in row.items():
            if schema.components[comp].required and value is None:
                raise ValueError(f"Value is missing for {comp}")

Summary
-------

In this tutorial, we created a client to retrieve metadata from the SDMX
Global Registry. We used the ``get_schema`` method to obtain the metadata
necessary to validate data for the "EDUCAT_CLASS_A" dataflow by the UNESCO
Institute for Statistics.

While this tutorial covers fundamental validation checks, there are many more
aspects to consider when validating SDMX messages. Nonetheless, it provides
a solid foundation for using ``pysdmx`` to write Python validation code for
SDMX messages.
