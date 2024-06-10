Asynchronous client
===================

This is the client to be used for retrieving metadata from an SDMX Registry or
SDMX service in an asynchronous (i.e. non-blocking fashion).

>>> import asyncio
>>> from pysdmx.api.fmr import AsyncRegistryClient
>>> async def main():
>>>     gr = AsyncRegistryClient("https://registry.sdmx.org/sdmx/v2/")
>>>     mapping = await gr.get_schema("dataflow", "UIS", "EDUCAT_CLASS_A", "1.0")
>>>     print(mapping)
>>> asyncio.run(main())

.. autoclass:: pysdmx.fmr.AsyncRegistryClient
    :members: