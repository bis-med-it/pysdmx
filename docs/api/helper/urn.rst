URN handling
============

Overview
--------

SDMX allows identifying any artefact in a non-ambiguous and stable fashion
using URNs. For example, version ``2.1`` of the ``CL_FREQ`` codelist
maintained by ``SDMX`` will have the following unique URN:
``urn:sdmx:org.sdmx.infomodel.codelist.Codelist=SDMX:CL_FREQ(2.1)``.

``pysdmx`` offers helper methods to:

- Parse URNs of maintainable artefacts (``parse_urn``).
- Parse URNs of items (``parse_item_urn``).
- Find the artefact identified by the supplied URN in a collection of
  artefacts (``find_by_urn``).

Functions
---------

.. autofunction:: pysdmx.util.parse_urn

.. autofunction:: pysdmx.util.parse_item_urn

.. autofunction:: pysdmx.util.find_by_urn


Responses
---------

.. autoclass:: pysdmx.util.Reference
    :members:

.. autoclass:: pysdmx.util.ItemReference
    :members: