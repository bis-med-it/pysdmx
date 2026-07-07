.. warning::

    The connectors are experimental and subject to change without
    prior notice. They are not covered by semantic versioning
    guarantees, and backward incompatible modifications to these
    classes will not result in a major version increment. Use them
    with caution in production environments or critical processes.

.Stat Suite connector
=====================

Many statistical organisations disseminate SDMX data through the
**.Stat Suite** platform (OECD, ILO, ABS, the Pacific Data Hub and
others). These deployments expose the SDMX-REST v2 API, serving
structural metadata as SDMX-ML 2.1 and data as SDMX-CSV.

The :class:`pysdmx.api.stat.StatConnector` is tuned to that profile.
For a given dataflow it retrieves three artefacts: the ``Dataflow``
(with its components), the ``Schema``, and the data as a typed
``PandasDataset``.

.. important::
    To use the ``StatConnector``, install the ``pysdmx[data,xml]``
    extras.

    Check the :ref:`installation guide <installation>` for more
    information.

Setup
-----

``StatConnector`` defaults to the OECD public service. Known .Stat
Suite deployments are available via the ``StatEndpoints`` enum:

.. code-block:: python

    from pysdmx.api.stat import StatConnector, StatEndpoints

    conn = StatConnector()                    # OECD (default)
    # conn = StatConnector(StatEndpoints.ILO) # or another deployment

You can find the ``agency``, ``id`` and ``version`` of a dataflow in
the `OECD Data Explorer <https://data-explorer.oecd.org>`_ via its
"Developer API" button.

Retrieving the artefacts
------------------------

.. code-block:: python

    agency = "OECD.SDD.TPS"
    flow_id = "DSD_G20_PRICES@DF_G20_PRICES"
    version = "1.0"

    # The dataflow, with components resolved from its data structure
    flow = conn.fetch_dataflow(agency, flow_id, version)

    # The schema: components, data types and allowed values
    schema = conn.fetch_schema(agency, flow_id, version)

    # The data as a typed PandasDataset, with its schema attached
    dataset = conn.fetch_dataset(
        agency, flow_id, version, filters={"REF_AREA": "CHN"}
    )
    print(dataset.data.head())

Filter by dimension with ``filters`` (a mapping of dimension ID to a
single value, resolved to a positional key) or pass a raw positional
``key`` directly. .Stat services key on one value per dimension.

Uploading
---------

Submitting structures and data requires a **writable** .Stat Suite
instance and an OAuth2 / Keycloak bearer token. .Stat splits submission
across two services: structures go to the NSI web service, while data is
uploaded to the Transfer service, scoped to a **data space** and
processed asynchronously.

.. code-block:: python

    from pysdmx.api.stat import StatUploader

    # Obtain a token. `fetch_token` uses the Keycloak password grant,
    # which requires the client to have "Direct Access Grants" enabled
    # and to authenticate a *local* Keycloak account:
    token = StatUploader.fetch_token(
        "https://my.stat/auth/realms/<realm>/protocol/openid-connect/token",
        client_id="my-client",
        username="user",
        password="secret",
    )

    uploader = StatUploader(
        nsi_endpoint="https://my.stat/nsi/rest",
        # The Transfer endpoint includes the API-version segment:
        transfer_endpoint="https://my.stat/transfer/3",
        dataspace="design",          # the target .Stat data space
        token=token,
    )

    # Structure first, then data (data submission is asynchronous)
    response = uploader.submit(dataflow, dataset)

    # `submit`/`submit_data` return the Transfer OperationResult, which
    # carries the integer transaction id (reported as `requestId`). Poll
    # the ImportSummary until its executionStatus is "Completed", then
    # check its "outcome" to confirm success.
    request_id = ...  # the requestId read from `response`
    print(uploader.submission_status(request_id))

The ``dataset`` passed to ``submit``/``submit_data`` must be
Schema-backed — for example one returned by
:meth:`~pysdmx.api.stat.StatConnector.fetch_dataset` or by
:func:`pysdmx.io.get_datasets`. The SDMX *action*
(Append/Replace/Merge/Delete) is carried inside the file (the SDMX-CSV
2.0 ``ACTION`` column, or the SDMX-ML dataset action), not as a request
parameter.

.. note::
    Deployments that authenticate through a federated identity provider
    (e.g. GitHub, ADFS) cannot use the password grant. Obtain a bearer
    token through the browser flow (for example the Transfer service's
    Swagger "Authorize" button) and pass it as ``token=``.

.. note::
    Structure submission can report a per-artefact failure inside the
    ``SubmitStructureResponse`` body even on an HTTP 200; a partial
    failure (HTTP 207) is raised as :class:`~pysdmx.errors.Invalid`.

.. note::
    Submitted (and deleted) content must use an **agency you are
    authorized to maintain**. On the SIS-CC demo that agency is ``MD``;
    everything under other agency IDs is read-only. The agency is taken
    from the artefacts and datasets you pass, so build them under your
    writable agency.

Deleting
--------

Deletion mirrors submission and needs the same bearer token. Delete
observations by uploading them with the SDMX *Delete* action, and delete
structures with :meth:`~pysdmx.api.stat.StatUploader.delete_structure`.

.. code-block:: python

    # Delete observations (SDMX-CSV ACTION=D under the hood)
    uploader.delete_data(dataset)

    # Delete structures. A data import auto-creates an actual content
    # constraint (CR_A_<dataflow>); tear down in dependency order:
    uploader.delete_structure([
        "DataConstraint=MD:CR_A_DF_EXAMPLE(1.0)",
        "Dataflow=MD:DF_EXAMPLE(1.0)",
        "DataStructure=MD:DSD_EXAMPLE(1.0)",
        "ConceptScheme=MD:CS_EXAMPLE(1.0)",
    ])

``delete_structure`` accepts maintainable artefacts or short-URN strings,
and deletes them in the order given — pass dependents first, or a
still-referenced artefact yields :class:`~pysdmx.errors.Invalid` (HTTP
409).

Reading access-controlled dataspaces
-------------------------------------

``StatConnector`` reads anonymously by default. For deployments that
require authentication, pass a bearer ``token``:

.. code-block:: python

    conn = StatConnector(StatEndpoints.OECD, token=my_token)
    flow = conn.fetch_dataflow(agency, flow_id, version)
