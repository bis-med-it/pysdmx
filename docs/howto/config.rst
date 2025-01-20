.. _config:

Configure your processes
========================

The previous tutorials illustrated how ``pysdmx`` can facilitate specific
steps (e.g., validation, mapping, etc.) in our statistical processes in a
fully metadata-driven fashion. However, configuring these steps themselves—
tweaking them to suit our needs—remains a crucial aspect. This tutorial
addresses the question of how we can achieve this using ``pysdmx`` and SDMX
reference metadata.

For example, the :ref:`tutorial about validation<validate>` shows how SDMX
metadata can be used to validate input data. But what should we do in case
some data are reported as invalid? Should we quarantine the entire input?
Or should we quarantine only the subset of invalid data and proceed to the 
next step with the subset of valid data? 

The purpose of this tutorial is to show how we can provide such configuration
details, using ``pysdmx`` and SDMX reference metadata.

Required metadata
-----------------

For a scenario where we need to configure steps in our statistical processes,
the following metadata in our SDMX Registry is essential:

- **Metadataflows**: A set of metadata attributes about "something" and
  related artifacts (concept schemes, codelists, and metadata structure)
  are required.

- **Metadatasets**: A metadata report provides values for the metadata
  attributes relevant to the target to which the report refers (e.g., a
  dataflow).

- **Dataflows**: A set of data about a statistical domain and related
  artifacts (concept schemes, codelists, and data structure) are required.

For additional information about the various types of SDMX artifacts, please
refer to the `SDMX documentation <https://sdmx.org/>`_.

Step-by-step solution
---------------------

Defining the metadata
^^^^^^^^^^^^^^^^^^^^^

In a scenario where we receive a data submission for validation, mapping, and
integration, each step can be configured differently. Configuration options
may depend on the ingested data or business unit practices. For instance,
considering validation:

- The data received might include only what has changed compared to the
  previous submission. Alternatively, it could be a complete dataset,
  requiring different validation approaches.

- In case of validation problems, businesses may choose to quarantine only
  the invalid data, proceeding to the next step with the subset of valid data.
  Others may prefer quarantining the entire submission.

These configuration options can be captured using SDMX reference metadata. To
do this:

- Create a Metadata Structure Definition with the configuration options using
  concepts and coded concepts.

- Define the type(s) of attachment targets (e.g., a dataflow, a provision
  agreement).

- Define a metadataflow (e.g., with the ID ``DCO`` for Dataflow Configuration
  Options) for which metadata reports will be provided.

- Provide metadata reports (metadatasets) attached to the desired targets,
  defining their different configuration options.

For example, for the ``BIS_MACRO`` dataflow maintained by ``BIS``, options
could include:

- ``partial_update`` set to the boolean value ``true`` (indicating acceptance
  of only new or updated data).

- ``on_validation_error`` set to code ``F`` (Fail),
  signifying that the entire submission must be quarantined in case of
  validation issues.

- ``structure_map`` set to the URN of the structure map to be used for
  mapping data from the ``BIS_MACRO`` dataflow structure to its target
  structure.

- ``on_mapping_error`` set to code ``I`` (Ignore), as only a
  subset of data is mapped.


Connecting to a Registry
^^^^^^^^^^^^^^^^^^^^^^^^

``pysdmx`` allows retrieving metadata from an SDMX Registry in either a
synchronous (via ``pysdmx.api.fmr.RegistryClient``) or asynchronous fashion
(via ``pysdmx.api.fmr.AsyncRegistryClient``). The choice depends on your use
case. The asynchronous client is often preferred as it is non-blocking.

To connect to your target Registry, instantiate the client by passing the
SDMX-REST endpoint. If using the
`FMR <https://www.bis.org/innovation/bis_open_tech_sdmx.htm>`_,
the endpoint is the URL at which the FMR is available, followed by
``/sdmx/v2/``.

.. code-block:: python

    from pysdmx.api.fmr import AsyncRegistryClient

    client = AsyncRegistryClient("[endpoint_comes_here]")

Retrieving configuration details
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As mentioned earlier, we aim to retrieve configuration details for the
``BIS_MACRO`` dataflow. The metadata report for the ``DCO_BIS_MACRO`` ID
can be obtained using the get_report method:

.. code-block:: python

    report = await client.get_report("BIS", "DCO_BIS_MACRO", "1.0")

Iterate over the report to print configuration options:

.. code-block:: python

    for attribute in report:
        print(attribute)

In practice, instead of printing, these attributes can be used to drive
process steps. For example, a validation step can check the value of
``partial_update`` to determine whether mandatory attributes need validation.

.. code-block:: python

    check_mandatory = report["partial_update"]

Summary
-------

This tutorial demonstrated how to create a client to retrieve metadata from
our Registry. Using the ``get_report method``, we retrieved configuration
options for the ``BIS_MACRO`` dataflow. This information can now be
utilized to customize the behavior of statistical processes.