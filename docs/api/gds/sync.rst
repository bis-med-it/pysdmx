Synchronous client
==================

This is the client to be used for retrieving the GDS information
in a synchronous (i.e. blocking) fashion.

>>> from pysdmx.api.gds import GdsClient
>>> gc = GdsClient()
>>> agencies = gc.get_agencies("BIS")

.. autoclass:: pysdmx.api.gds.GdsClient
    :members: