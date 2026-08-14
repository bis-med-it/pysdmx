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

The :class:`pysdmx.api.stat.StatConnector` **inherits the Fusion
Metadata Registry client** (:class:`~pysdmx.api.fmr.RegistryClient`),
so its ``get_*`` methods return the same model objects --
``get_dataflows`` returns ``Dataflow`` objects, ``get_codes`` a
``Codelist``, and so on. It reads .Stat's SDMX-ML and parses it with
:func:`~pysdmx.io.read_sdmx`. Endpoints .Stat does not serve (e.g.
``get_schema`` -- there is no ``/schema`` endpoint -- or reference
metadata) raise :class:`~pysdmx.errors.Invalid`. On top, it adds data
retrieval the registry client does not offer: ``fetch_data`` (raw
SDMX-CSV) and ``fetch_dataset`` (a typed ``PandasDataset``).

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

Retrieving structures and data
------------------------------

.. code-block:: python

    agency = "OECD.SDD.TPS"
    flow_id = "DSD_G20_PRICES@DF_G20_PRICES"
    version = "1.0"

    # Structures as model objects (the inherited FMR get_* methods)
    flows = conn.get_dataflows(agency, flow_id, version)  # [Dataflow]
    dsds = conn.get_data_structures(agency, "DSD_G20_PRICES", version)
    freq = conn.get_codes("SDMX", "CL_FREQ")              # a Codelist

    # The raw SDMX-CSV data (optionally keyed)
    data = conn.fetch_data(agency, flow_id, version, key="CHN.A.N.CPI.PA")

    # ...or the data as a typed PandasDataset -- structure + data
    # combined through pysdmx's native get_datasets, schema attached:
    dataset = conn.fetch_dataset(
        agency, flow_id, version, key="CHN.A.N.CPI.PA"
    )
    print(dataset.data.head())

The ``get_*`` methods return the same model objects as
:class:`~pysdmx.api.fmr.RegistryClient`. ``fetch_data`` returns the
**raw** SDMX-CSV bytes; ``fetch_dataset`` composes structure + data via
:func:`~pysdmx.io.get_datasets`. Select data with a positional ``key``
(dimensions in data-structure order, ``.``-separated; ``*`` wildcards a
dimension; defaults to the whole dataflow). .Stat services key on one
value per dimension; for multiple values issue separate requests.

Asynchronous access
-------------------

:class:`pysdmx.api.stat.AsyncStatConnector` is the ``async`` counterpart
(inheriting :class:`~pysdmx.api.fmr.AsyncRegistryClient`); its ``get_*``,
``fetch_data`` and ``fetch_dataset`` methods are coroutines:

.. code-block:: python

    from pysdmx.api.stat import AsyncStatConnector

    conn = AsyncStatConnector()
    flows = await conn.get_dataflows(agency, flow_id, version)
    dataset = await conn.fetch_dataset(agency, flow_id, version)

Uploading
---------

Submitting structures and data requires a **writable** .Stat Suite
instance and an OAuth2 / Keycloak bearer token. .Stat splits submission
across two services: structures go to the NSI web service, while data is
uploaded to the Transfer service, scoped to a **data space** and
processed asynchronously.

.. code-block:: python

    from pysdmx.api.stat import StatUploader
    from pysdmx.api.stat.authentication import (
        ClientCredentialsAuthentication,
        KeycloakAuthentication,
        KeycloakDeviceAuthentication,
    )

    authority = "https://keycloak.example/realms/<realm>"

    # Pick ONE of the three flows; each exposes get_token():

    # 1. Interactive device flow (browser sign-in) -- the only option for
    #    federated logins such as GitHub or ADFS. Prints a URL + short
    #    code and waits for the sign-in to finish.
    auth = KeycloakDeviceAuthentication(authority, client_id="app")

    # 2. Machine-to-machine (confidential client + service account):
    # auth = ClientCredentialsAuthentication(
    #     authority, client_id="my-client", client_secret="...",
    # )

    # 3. Resource-owner password grant (local Keycloak accounts only):
    # auth = KeycloakAuthentication(
    #     authority, user="alice", password="...", client_id="app",
    # )

    uploader = StatUploader(
        nsi_endpoint="https://my.stat/nsi",
        # The Transfer endpoint includes the API-version segment:
        transfer_endpoint="https://my.stat/transfer/3",
        dataspace="<data-space>",   # the target .Stat data space
        token=auth.get_token(),     # or any bearer token you already have
    )

    # Structure first, then data (data submission is asynchronous)
    result = uploader.submit(structures=dataflow, dataset=dataset)

    # Poll to completion, then check the outcome
    final = uploader.submission_status(result.request_id, wait=True)
    print(final.execution_status, final.outcome)

``submit``/``submit_data`` return a ``SubmissionResult`` whose
``request_id`` identifies the asynchronous transaction; feed it to
``submission_status`` to obtain the final ``execution_status`` and
``outcome``. Pass ``wait=True`` to poll until the transaction reaches a
terminal state (tune the loop with ``interval`` and ``attempts``).

The ``dataset`` passed to ``submit``/``submit_data`` must be
Schema-backed — for example one returned by
:meth:`~pysdmx.api.stat.StatConnector.fetch_dataset` or by
:func:`pysdmx.io.get_datasets`. The SDMX *action*
(Append/Replace/Merge/Delete) is carried inside the file (the SDMX-CSV
2.0 ``ACTION`` column, or the SDMX-ML dataset action), not as a request
parameter.

.. note::
    :mod:`pysdmx.api.stat.authentication` offers one class per OAuth2
    flow, each taking the realm (authority) URL and exposing
    ``get_token()`` (which re-runs the flow when the token has expired):
    :class:`~pysdmx.api.stat.authentication.KeycloakDeviceAuthentication`
    (interactive device flow — the only option for federated logins such
    as GitHub or ADFS),
    :class:`~pysdmx.api.stat.authentication.ClientCredentialsAuthentication`
    (machine-to-machine, with a client id, secret and service account),
    and :class:`~pysdmx.api.stat.authentication.KeycloakAuthentication`
    (resource-owner password grant, for local Keycloak accounts only).
    Alternatively, pass any bearer token obtained elsewhere (for example
    the Transfer service's Swagger "Authorize" button) directly as
    ``token=``.

.. note::
    ``submit_structure`` reports failures **two** ways, so check both. A
    per-artefact rejection carried in the ``SubmitStructureResponse``
    body (even on an HTTP 2xx response) surfaces as
    ``StructureSubmissionResult.success = False`` (with ``.messages``),
    not as an exception. But the NSI can also reject a submission with an
    HTTP error -- notably **422 Unprocessable Entity** with an SDMX error
    document -- which is raised as :class:`~pysdmx.errors.Invalid`.
    ``submit`` is the convenience wrapper that submits the structures and
    then the data; it raises :class:`~pysdmx.errors.Invalid` if the
    structure step does not succeed.

.. note::
    ``submit_structure`` serializes to **SDMX-JSON 2.0 by default** --
    the only format whose writer covers every SDMX artefact type (the
    SDMX-ML writers do not support the metadata artefacts and have
    narrower type coverage). Override with ``structure_format=`` for a
    deployment that requires SDMX-ML; a type that cannot be written in
    the chosen format raises a clear :class:`~pysdmx.errors.Invalid`.

.. note::
    Submitted (and deleted) content must use an **agency you are
    authorized to maintain** on the target instance (the agency must
    exist in the ``SDMX:AGENCIES`` scheme). The agency is taken from the
    artefacts and datasets you pass, so build them under your writable
    agency.

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
409). It returns one ``StructureSubmissionResult`` per artefact (check
each ``.success``). Like ``submit_structure``, both report a logical
(in-body) failure through ``.success`` / ``.messages`` rather than
raising.

Endpoints
---------

The connectors take different URL forms:

- ``StatConnector(api_endpoint=…)`` — the SDMX-REST **v2** base, e.g.
  ``https://my.stat/rest/v2``.
- ``StatUploader(nsi_endpoint=…, transfer_endpoint=…)`` — the NSI host
  (structures are posted to ``{nsi}/rest/structure``) and the Transfer
  service **including its API-version segment**, e.g.
  ``https://my.stat/transfer/3``.

The ``StatEndpoints`` enum lists ready-made **read** bases for known
public deployments; it does not apply to ``StatUploader``, which takes
raw URLs (writable hosts are deployment-specific). When round-tripping,
the ``StatConnector`` read base is usually the NSI host with ``/rest/v2``
appended, e.g. ``StatConnector(f"{nsi}/rest/v2")`` (reads are anonymous).
