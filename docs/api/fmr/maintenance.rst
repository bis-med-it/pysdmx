FMR clients
===========

.. important::

    These clients are still **EXPERIMENTAL** and their API is subject to change without warnings.

FMR Transactions client
-----------------------

Use this client to browse and retrieve transactions in an FMR. Each
transaction records a change to structural or reference metadata. The target
FMR instance must be version 12.4.0 or later.

>>> from datetime import UTC, datetime
>>> from pysdmx.api.fmr.maintenance import RegistryTransactionsClient
>>> client = RegistryTransactionsClient("https://your-fmr.org")
>>> txs = client.list_transactions(datetime(2026, 10, 1, 0, 0, 0, 0, UTC))
>>> print(f"{len(txs)} transactions")
>>> tx = txs[0]
>>> print(f"Transaction ID: {tx.meta.transaction_id}")
>>> transaction = client.get_transaction(tx.meta.transaction_id)
>>> print(transaction)

.. autoclass:: pysdmx.api.fmr.maintenance.RegistryTransactionsClient
    :members:

FMR Maintenance client
----------------------

This is the client to be used for maintaining metadata in an SDMX Registry.
This client inherits from RegistryTransactionsClient and can therefore also
be used to browse and retrieve transactions.

>>> from pysdmx.api.fmr.maintenance import RegistryMaintenanceClient
>>> cd = Code("A", name="Code A")
>>> cl = Codelist("CL_TEST", agency="TEST", name="Test CL", items=[cd])
>>> target = "https://registry.sdmx.org"
>>> client = RegistryMaintenanceClient(target, "user", "password")
>>> client.put_structures([cl])

.. autoclass:: pysdmx.api.fmr.maintenance.RegistryMaintenanceClient
    :members: