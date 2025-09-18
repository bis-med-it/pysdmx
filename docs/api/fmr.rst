Metadata API
============

Overview
--------

One of the core features of the library is to allow retrieving metadata
that can be used to **power statistical processes**.

.. note::
    Discover the range of statistical processes enabled by the SDMX metadata
    through the metadata API in the following tutorials:

    - :ref:`fs`.
    - :ref:`physical-model`.
    - :ref:`validate`.
    - :ref:`map`.
    - :ref:`maintenance`.

These metadata are typically stored in an **SDMX Registry**, such as the
`FMR <https://www.bis.org/innovation/bis_open_tech_sdmx.htm>`_. However,
retrieval is not limited to specific registries; any service compliant with
the `SDMX-REST 2.0.0 specification <https://github.com/sdmx-twg/sdmx-rest>`_,
allowing metadata retrieval in `SDMX-JSON 2.0.0 
<https://github.com/sdmx-twg/sdmx-json>`_, can be used.

To retrieve metadata, a ``pysdmx`` client is necessary. Two types of clients
are available: one for **synchronous** (blocking) retrieval and another for
asynchronous (non-blocking) **retrieval**. At a minimum, the registry endpoint
must be provided during client instantiation to specify where the metadata will
be fetched from.

Once the client instance is obtained, various methods can be utilized to
retrieve the desired metadata.

Examples:
    Let's illustrate the process with an example. Assume we wish to retrieve 
    information from the SDMX Global Registry for data validation of the
    ``EDUCAT_CLASS_A`` dataflow maintained by the UNESCO Institute for
    Statistics (``UIS``). The following code demonstrates this:

        >>> from pysdmx.api.fmr import RegistryClient
        >>> gr = RegistryClient("https://registry.sdmx.org/sdmx/v2/")
        >>> schema = gr.get_schema("dataflow", "UIS", "EDUCAT_CLASS_A", "1.0")

API Reference
-------------

Two clients are available for metadata retrieval, both exposing the same API.
The only distinction is that one client operates synchronously
(``RegistryClient``), while the other operates asynchronously
(``AsyncRegistryClient``).

In addition, an **experimental** client is now also available to support
metadata maintenance operations.

.. toctree::
   :maxdepth: 1

   fmr/sync
   fmr/async
   fmr/maintenance
