.. _physical-model:

Create the Physical Data Model
===============================

In this tutorial, we explore how ``pysdmx`` assists in **creating the
physical data model for a dataflow** in a metadata-driven fashion, relying
solely on the metadata stored in an SDMX Registry.

Required Metadata
-----------------

For this scenario, we need the following metadata in our SDMX Registry:

Data Structure
    A data structure describes the expected structure of data, including
    various **components** (dimensions, attributes, or measures) relevant for
    a statistical domain. It also provides component **data types** (string,
    integer, dates, etc.) and specifies whether these components are
    **mandatory**. In short, the data structure contains all the information
    needed to create our physical data model.

Dataflows or provision agreements could also be used to consider additional
constraints, but for this tutorial, we use data structures. 

For additional information about SDMX artifacts, refer to the `SDMX
documentation <https://sdmx.org/>`_.

Step-by-step Solution
---------------------

``pysdmx`` allows retrieving metadata from an SDMX Registry either
synchronously (via ``pysdmx.api.fmr.RegistryClient``) or asynchronously
(via ``pysdmx.api.fmr.AsyncRegistryClient``). The choice depends on the use case
and preference, but we use the asynchronous client by default as it is
non-blocking.

Connecting to a Registry
^^^^^^^^^^^^^^^^^^^^^^^^

First, we need an instance of the client to connect to our target Registry.
When instantiating the client, we pass the SDMX-REST endpoint of our Registry.
If using the `FMR <https://www.bis.org/innovation/bis_open_tech_sdmx.htm>`_,
the reference Implementation of the SDMX Registry specification, the endpoint
is the URL at which the FMR is available, followed by ``/sdmx/v2/``.

For this tutorial, we create the physical data model for the ``CPI``
data structure maintained by Eurostats (``ESTAT``), as published on the
`SDMX Global Registry <https://registry.sdmx.org/>`_ .

.. code-block:: python

    from pysdmx.api.fmr import AsyncRegistryClient
    client = AsyncRegistryClient("https://registry.sdmx.org/sdmx/v2/")

Retrieving the Schema Information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An SDMX-REST ``schema`` query retrieves what is allowed within the context
of a data structure, dataflow, or provision agreement. The SDMX Registry uses
all available information (e.g., constraints) to return a "schema" describing
"data validity rules" for the selected context. We use this to retrieve the
metadata needed to create our physical data model.

As mentioned, we create the physical data model for the ``CPI`` data structure
maintained by Eurostats (``ESTAT``).

.. code-block:: python

    schema = await client.get_schema("datastructure", "ESTAT", "CPI", "1.0")

Creating the Physical Data Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Creating a physical data model depends on the selected technology
(e.g., a SQL database, an AVRO schema, or a document database like MongoDB).
As a minimum, expect an **identifier** for the field (or column), the expected
**data type**, and whether the field **can be null**.

All this information is available in the ``Schema`` object returned by the
``get_schema`` method:

.. code-block:: python

    for component in schema.components:
        print(f"{component.id} ({component.dtype}). Required: {component.required}")

    # Example output:
    # FREQ (String). Required: True
    # SEASONAL_ADJUST (String). Required: True
    # REF_AREA (String). Required: True
    # ...

Mapping SDMX Data Types
^^^^^^^^^^^^^^^^^^^^^^^

Mapping SDMX data types (e.g., ``ObservationalTimePeriod``) to the types
of the selected technology is beyond the scope of this tutorial but is
easily achieved using a mapping table.

Fine-tuning the Physical Data Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The core information for creating the physical data model is covered.
Additional information is available for each component for fine-tuning.

For example, SDMX allows defining **facets** to provide additional
constraints beyond the data type. This information is available via the
``facets`` property.

.. code-block:: python

    print(schema.components["COMMENT_DSET"].facets)
    # Example output:
    # max_length=1050

The **role** a component plays in the data structure (dimension, attribute, or
measure) is available via the ``role`` property. Display the name or value
depending on the use case.

.. code-block:: python

    for component in schema.components:
        print(f"{component.id} has role: {component.role.name}")

This allows, for example, creating a composite primary key out of the
dimension values. Alternatively, get all dimensions (or measures or
attributes) directly using the appropriate property:

.. code-block:: python

    for component in schema.components.dimensions:
        print(f"{component.id}")

Last but not least, SDMX distinguishes between **coded** and **uncoded**
components. If the technology stack supports it, use the list of allowed
codes to define the list of codes a component is allowed to have in
the physical data model. The list of codes is available via the ``codes``
property:

.. code-block:: python

    frequencies = [c.id for c in schema.components["FREQ"].codes]
    print(frequencies)
    # Example output:
    # ['A', 'S', 'Q', 'M', 'W', 'D', 'H', 'B', 'N']

Summary
-------

In this tutorial, we created a client to retrieve metadata from the Registry
and used its ``get_schema`` method to retrieve the structure details for the
``CPI`` dataflow maintained by Eurostat. We saw the type of information
returned by the ``get_schema`` method and now have a good idea of how to use
it to create the physical data model in our technology of choice.
