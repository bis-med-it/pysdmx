Asynchronous client
=======================

This is the client to be used for retrieving the GDS information
in an asynchronous (i.e. non-blocking) fashion.

>>> import asyncio
>>> from pysdmx.api.gds import AsyncGdsClient
>>> async def main():
>>>     gr = AsyncGdsClient()
>>>     gds_agencies = await gr.get_agencies("BIS")
>>>     print(gds_agencies)
>>> asyncio.run(main())

.. important::
    This client is designed to be used with Python's `asyncio` library.
    Ensure you have an event loop running when using this client.

.. note::
    For more details over the connectors, check the :ref:`GDS Synchronous client <gds-sync>` documentation. The async client
    supports the same parameters and methods as the synchronous client, but operates asynchronously.

.. autoclass:: pysdmx.api.gds.AsyncGdsClient
    :members: