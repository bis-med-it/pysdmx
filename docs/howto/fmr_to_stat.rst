.. warning::

    The FMR maintenance client and the .Stat connectors are
    experimental and subject to change without prior notice.

Publishing structures from FMR to .Stat
=======================================

This tutorial moves structural metadata from a **Fusion Metadata
Registry (FMR)** to a **.Stat Suite** instance, end to end, using
pysdmx. The full runnable script is
`examples/fmr_to_stat.py <https://github.com/bis-med-it/pysdmx/blob/main/examples/fmr_to_stat.py>`_.

The pipeline, under the mock agency ``MD``:

1. author a minimal structure graph (ConceptScheme + DSD + Dataflow);
2. upload it to the FMR;
3. download it back from the FMR **with all its references**;
4. submit the downloaded structures and a tiny dataset to .Stat.

Downloading with ``references=all`` is deliberate: it returns the whole
dependency graph and exercises the SDMX-ML readers on it, and it is
exactly what is forwarded to .Stat.

.. important::
    Requires the ``pysdmx[data,xml]`` extras, a **writable** FMR, and a
    **writable** .Stat Suite instance. Everything is created under the
    agency you are authorised to maintain (``MD`` on the SIS-CC demo).

.. note::
    The FMR rejects structures whose maintenance agency is unknown, so
    the target agency must already exist in the ``SDMX:AGENCIES`` scheme.
    Register it once (e.g. submit an
    :class:`~pysdmx.model.organisation.AgencyScheme` containing an
    :class:`~pysdmx.model.Agency` with ``StructureAction.Merge``) before
    running this tutorial. The SIS-CC demo already has ``MD``.

Authentication
--------------

The FMR maintenance client takes either a bearer ``access_token`` or
HTTP Basic ``user``/``password``; .Stat takes a bearer ``token``. The
script reads them from the environment:

.. code-block:: bash

    export FMR_ENDPOINT="https://my.fmr/sdmx/v2"  # SDMX-REST v2 base
    export FMR_TOKEN="eyJ..."      # or FMR_USER + FMR_PASSWORD
    export DOTSTAT_TOKEN="eyJ..."  # a fresh .Stat bearer token

Upload to the FMR
-----------------

:class:`~pysdmx.api.fmr.maintenance.RegistryMaintenanceClient` posts the
artefacts to the FMR. ``Replace`` adds new artefacts and overwrites
existing ones:

.. code-block:: python

    from pysdmx.api.fmr.maintenance import (
        RegistryMaintenanceClient,
        StructureAction,
    )

    client = RegistryMaintenanceClient(FMR_ENDPOINT, access_token=token)
    client.put_structures(structures, action=StructureAction.Replace)

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

    svc = RestService(
        FMR_ENDPOINT,
        ApiVersion.V2_0_0,
        structure_format=StructureFormat.SDMX_ML_2_1,
        token=token,
    )
    query = StructureQuery(
        StructureType.DATAFLOW,
        "MD",
        "DF_PYSDMX_FMR",
        "1.0",
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

    uploader = StatUploader(NSI, TRANSFER, dataspace=SPACE, token=token)
    uploader.submit_structure(graph.structures)

    imported = uploader.submit_data(dataset)
    final = uploader.submission_status(imported.request_id, wait=True)
    print(final.execution_status, final.outcome)

See the :doc:`.Stat connector guide <stat>` for the .Stat submission
details, and :doc:`reconciling .Stat against FMR <stat_fmr_sync>` for
the reverse clean-up direction.
