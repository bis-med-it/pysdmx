Asynchronous client
===================

This is the client to be used for retrieving the GDS information
in an asynchronous (i.e. non-blocking) fashion.

>>> import asyncio
>>> from pysdmx.api.gds import AsyncGdsClient
>>> async def main():
>>>     gr = AsyncGdsClient()
>>>     gds_agencies = await gr.get_agencies("BIS")
>>>     print(gds_agencies)
>>> asyncio.run(main())

.. autoclass:: pysdmx.api.gds.AsyncGdsClient
    :members: