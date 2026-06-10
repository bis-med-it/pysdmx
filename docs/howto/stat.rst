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
