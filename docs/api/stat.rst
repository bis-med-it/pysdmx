.Stat Connector
===============

Overview
--------
The ``StatConnector`` retrieves dataflows, schemas and data (as Pandas
datasets) from SDMX .Stat Suite services such as the OECD dotStatSuite.

**This connector is experimental and subject to change without prior
notice.** It is not covered by semantic versioning guarantees. Use it
with caution in production environments or critical processes.

API Reference
-------------

.. autoclass:: pysdmx.api.stat.StatConnector
    :members:

.. autoclass:: pysdmx.api.stat.StatAsyncConnector
    :members:

.. autoclass:: pysdmx.api.stat.StatUploader
    :members:

.. autoclass:: pysdmx.api.stat.StatEndpoints
    :members:

Authentication
--------------
Token-acquisition flows for the .Stat Suite APIs. Each class takes the
realm (authority) URL, runs its OAuth2 flow, and exposes ``get_token()``.

.. autoclass:: pysdmx.api.stat.authentication.KeycloakDeviceAuthentication
    :members: get_token, is_authenticated, refresh_token

.. autoclass:: pysdmx.api.stat.authentication.ClientCredentialsAuthentication
    :members: get_token, is_authenticated, refresh_token

.. autoclass:: pysdmx.api.stat.authentication.KeycloakAuthentication
    :members: get_token, is_authenticated, refresh_token
