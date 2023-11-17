Synchronous client
==================

This is the client to be used for retrieving metadata from an SDMX Registry or
SDMX service in a synchronous (i.e. blocking fashion).

>>> from pysdmx.fmr import RegistryClient
>>> gr = RegistryClient("https://registry.sdmx.org/sdmx/v2/")
>>> schema = gr.get_schema("dataflow", "UIS", "EDUCAT_CLASS_A", "1.0")

.. autoclass:: pysdmx.fmr.RegistryClient
    :members: