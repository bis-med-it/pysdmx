.. warning::

    The .Stat connectors are experimental and subject to change without
    prior notice.

Reconciling .Stat against FMR
=============================

This tutorial treats the **FMR** as the source of truth and prunes a
**.Stat Suite** instance to match it: it lists every ``MD`` structure on
both sides and deletes from .Stat the ones that no longer exist in the
FMR. The full runnable script is
`examples/stat_fmr_sync.py <https://github.com/bis-med-it/pysdmx/blob/main/examples/stat_fmr_sync.py>`_.

.. important::
    Requires the ``pysdmx[data,xml]`` extras and a **writable** .Stat
    Suite instance (the FMR is only read). The script is **safe by
    default** -- without ``--apply`` it just prints what it would delete.

List both sides
---------------

Both services expose the SDMX-REST v2 structure API, so a single
``StructureType.ALL`` stub query lists all the ``MD`` structures on each,
and :func:`~pysdmx.io.read_sdmx` turns the response into comparable
short-URNs:

.. code-block:: python

    from io import BytesIO

    from pysdmx.api.qb import (
        ApiVersion,
        RestService,
        StructureDetail,
        StructureFormat,
        StructureQuery,
        StructureType,
    )
    from pysdmx.io import read_sdmx

    def list_md_urns(base, token):
        svc = RestService(
            base,
            ApiVersion.V2_0_0,
            structure_format=StructureFormat.SDMX_ML_2_1,
            token=token,
        )
        query = StructureQuery(
            StructureType.ALL, "MD", detail=StructureDetail.ALL_STUBS
        )
        msg = read_sdmx(BytesIO(svc.structure(query)), validate=False)
        return {s.short_urn for s in msg.structures or []}

    fmr_urns = list_md_urns(FMR_ENDPOINT, fmr_token)
    stat_urns = list_md_urns(f"{NSI}/rest/v2", dotstat_token)
    extras = stat_urns - fmr_urns  # present in .Stat, absent in FMR

Delete the extras in dependency order
--------------------------------------

Deletions must run **dependents first** or a still-referenced artefact
returns HTTP 409. In particular a data import auto-creates an actual
content constraint (``CR_A_<dataflow>``) that must go before its
dataflow. Rank the short-URNs by type, then hand them to
:meth:`~pysdmx.api.stat.StatUploader.delete_structure`:

.. code-block:: python

    from pysdmx.api.stat import StatUploader

    ORDER = {
        "DataConstraint": 0, "ContentConstraint": 0,
        "Dataflow": 2, "DataStructure": 3,
        "ConceptScheme": 4, "Codelist": 5,
    }
    ordered = sorted(extras, key=lambda u: ORDER.get(u.split("=", 1)[0], 99))

    uploader = StatUploader(NSI, TRANSFER, dataspace=SPACE, token=dotstat_token)
    for result in uploader.delete_structure(ordered):
        print("ok" if result.success else "FAILED", "; ".join(result.messages))

``delete_structure`` returns one
:class:`~pysdmx.api.stat.StructureSubmissionResult` per artefact, so a
logical failure surfaces as ``success=False`` rather than an exception.

Run it
------

.. code-block:: bash

    export FMR_ENDPOINT="https://my.fmr/sdmx/v2"
    export DOTSTAT_TOKEN="eyJ..."
    poetry run python examples/stat_fmr_sync.py           # dry run
    poetry run python examples/stat_fmr_sync.py --apply   # delete

See :doc:`publishing structures from FMR to .Stat <fmr_to_stat>` for the
forward direction.
