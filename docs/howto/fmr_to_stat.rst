.. warning::

    The FMR maintenance client and the .Stat connectors are
    experimental and subject to change without prior notice.

Publishing structures from FMR to .Stat
=======================================

This tutorial moves structural metadata from a **Fusion Metadata
Registry (FMR)** to a **.Stat Suite** instance, end to end, using
pysdmx.

The pipeline, under an agency you are authorised to maintain:

1. author a minimal structure graph (ConceptScheme + DSD + Dataflow);
2. upload it to the FMR;
3. download it back from the FMR **with all its references**;
4. submit the downloaded structures and a tiny dataset to .Stat.

Downloading with ``references=all`` is deliberate: it returns the whole
dependency graph, which is exactly what is forwarded to .Stat.

.. important::
    Requires a **writable** FMR and a **writable** .Stat Suite instance.
    Moving *structures* needs only the base ``pysdmx`` package (they are
    exchanged as SDMX-JSON); the ``data`` extra (``pysdmx[data]``) is
    needed only for the final dataset-upload step. The target agency
    must already exist in the ``SDMX:AGENCIES`` scheme -- the FMR rejects
    structures whose maintenance agency is unknown.

Authentication
--------------

The FMR maintenance client takes either a bearer ``access_token`` or
HTTP Basic ``user``/``password``; .Stat takes a bearer ``token``. Read
them from the environment:

.. code-block:: bash

    export FMR_ENDPOINT="https://my.fmr/sdmx/v2"  # SDMX-REST v2 base
    export FMR_TOKEN="eyJ..."      # or FMR_USER + FMR_PASSWORD
    export DOTSTAT_TOKEN="eyJ..."  # a fresh .Stat bearer token

Upload to the FMR
-----------------

:class:`~pysdmx.api.fmr.maintenance.RegistryMaintenanceClient` posts the
artefacts to the FMR. ``Replace`` adds new artefacts and overwrites
existing ones. Authenticate with a bearer token **or** HTTP Basic
credentials:

.. code-block:: python

    from pysdmx.api.fmr.maintenance import (
        RegistryMaintenanceClient,
        StructureAction,
    )

    # with a bearer token ...
    client = RegistryMaintenanceClient(
        api_endpoint=FMR_ENDPOINT, access_token=FMR_TOKEN
    )
    # ... or with HTTP Basic credentials:
    # client = RegistryMaintenanceClient(
    #     api_endpoint=FMR_ENDPOINT, user=FMR_USER, password=FMR_PASSWORD
    # )

    client.put_structures(
        structures=structures, action=StructureAction.Replace
    )

Download from the FMR (references=all)
--------------------------------------

The same SDMX-REST base serves reads. A ``RestService`` structure query
with ``references=all`` returns the full graph, which
:func:`~pysdmx.io.read_sdmx` parses into a message:

.. code-block:: python

    from io import BytesIO

    from pysdmx.api.qb import (
        ApiVersion,
        RestService,
        StructureDetail,
        StructureFormat,
        StructureQuery,
        StructureReference,
        StructureType,
    )
    from pysdmx.io import read_sdmx

    agency_id = "<your-agency>"

    svc = RestService(
        api_endpoint=FMR_ENDPOINT,
        api_version=ApiVersion.V2_0_0,
        structure_format=StructureFormat.SDMX_JSON_2_0_0,
        token=FMR_TOKEN,
    )
    query = StructureQuery(
        artefact_type=StructureType.DATAFLOW,
        agency_id=agency_id,
        resource_id="DF_PYSDMX_FMR",
        version="1.0",
        detail=StructureDetail.FULL,
        references=StructureReference.ALL,
    )
    graph = read_sdmx(BytesIO(svc.structure(query)), validate=False)

Submit to .Stat
---------------

Finally, submit the downloaded structures, upload a dataset, and poll
the asynchronous import to completion:

.. code-block:: python

    from pysdmx.api.stat import StatUploader

    uploader = StatUploader(
        nsi_endpoint=NSI,
        transfer_endpoint=TRANSFER,
        dataspace=SPACE,
        token=DOTSTAT_TOKEN,
    )
    uploader.submit_structure(structures=graph.structures)

    imported = uploader.submit_data(dataset=dataset)
    final = uploader.submission_status(imported.request_id, wait=True)
    print(final.execution_status, final.outcome)

See the :doc:`.Stat connector guide <stat>` for the .Stat submission
details, and :doc:`reconciling .Stat against FMR <stat_fmr_sync>` for
the reverse clean-up direction.
