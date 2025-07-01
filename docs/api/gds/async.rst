Asynchronous client
=======================

This is the client to be used for retrieving the GDS information
in an asynchronous (i.e. non-blocking) fashion.

.. code-block:: python
    import asyncio
    from pysdmx.api.gds import AsyncGdsClient

    async def main():
        gr = AsyncGdsClient()
        gds_agencies = await gr.get_agencies("BIS")
        print(gds_agencies)
    asyncio.run(main())

.. important::
    This client is designed to be used with Python's `asyncio` library.
    Ensure you have an event loop running when using this client.

The asynchronous client is recommended for asynchronous workflows based on `fastapi` or similar frameworks.

.. code-block:: python
    from fastapi import FastAPI
    from pysdmx.api.gds import AsyncGdsClient

    app = FastAPI()

    @app.get("/agencies/{agency_id}")
    async def get_agencies(agency_id: str):
        client = AsyncGdsClient()
        agencies = await client.get_agencies(agency_id)
        return {"agencies": agencies}


.. note::
    For more details over the connectors, check the :ref:`GDS Synchronous client <gds-sync>` documentation. The async client
    supports the same parameters and methods as the synchronous client, but operates asynchronously.

.. autoclass:: pysdmx.api.gds.AsyncGdsClient
    :members: