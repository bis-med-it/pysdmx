Maintenance client
==================

.. important::

    The maintenance client is still **EXPERIMENTAL** and its API is subject
    to change without warnings.

This is the client to be used for maintaining metadata in an SDMX Registry.

>>> from pysdmx.api.fmr.maintenance import RegistryMaintenanceClient
>>> cd = Code("A", name="Code A")
>>> cl = Codelist("CL_TEST", agency="TEST", name="Test CL", items=[cd])
>>> target = "https://registry.sdmx.org"
>>> client = RegistryMaintenanceClient(target, "user", "password")
>>> client.put_structures([cl])

.. autoclass:: pysdmx.api.fmr.maintenance.RegistryMaintenanceClient
    :members: