.. warning::

    The .Stat connectors are experimental and subject to change without
    prior notice.

Reconciling .Stat against FMR
=============================

This tutorial treats the **FMR** as the source of truth and prunes a
**.Stat Suite** instance to match it: for a chosen agency it lists every
structure on both sides and deletes from .Stat the ones that no longer
exist in the FMR.

.. important::
    Requires a **writable** .Stat Suite instance (the FMR is only read).
    Structures are exchanged as SDMX-JSON, so the base ``pysdmx`` package
    is enough -- no extras needed. Compute the difference first and
    inspect it before running the deletion loop.

List both sides
---------------

Both services expose the SDMX-REST v2 structure API. Not every service
accepts the all-types ``structure/*/{agency}`` form (``.Stat`` returns
HTTP 422), so the helper queries each maintainable type in turn and
collects comparable short-URNs via :func:`~pysdmx.io.read_sdmx`:

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
    from pysdmx.errors import Invalid, NotFound
    from pysdmx.io import read_sdmx

    agency_id = "<your-agency>"

    TYPES = (
        StructureType.CODELIST, StructureType.CONCEPT_SCHEME,
        StructureType.DATA_STRUCTURE, StructureType.DATAFLOW,
        StructureType.DATA_CONSTRAINT,
    )

    def list_urns(base, token):
        svc = RestService(
            api_endpoint=base,
            api_version=ApiVersion.V2_0_0,
            structure_format=StructureFormat.SDMX_JSON_2_0_0,
            token=token,
        )
        urns = set()
        for stype in TYPES:
            q = StructureQuery(
                artefact_type=stype,
                agency_id=agency_id,
                detail=StructureDetail.ALL_STUBS,
            )
            try:
                msg = read_sdmx(BytesIO(svc.structure(q)), validate=False)
            except (Invalid, NotFound):
                continue  # no artefacts of this type
            urns |= {s.short_urn for s in msg.structures or []}
        return urns

    fmr_urns = list_urns(FMR_ENDPOINT, fmr_token)
    stat_urns = list_urns(f"{NSI}/rest/v2", dotstat_token)
    extras = stat_urns - fmr_urns  # present in .Stat, absent in FMR

.. warning::
    Deleting ``extras`` removes from ``.Stat`` everything for that agency
    that is not in the FMR, so the FMR must be the **complete** source of
    truth for it. Pointing at a partial FMR would delete legitimate
    structures. Always inspect ``extras`` first.

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
    ordered = sorted(
        extras, key=lambda u: ORDER.get(u.split("=", 1)[0], 99)
    )

    uploader = StatUploader(
        nsi_endpoint=NSI,
        transfer_endpoint=TRANSFER,
        dataspace=SPACE,
        token=dotstat_token,
    )
    try:
        for result in uploader.delete_structure(ordered):
            print("ok", "; ".join(result.messages))
    except (Invalid, NotFound) as err:
        # delete_structure is fail-fast: the first artefact the NSI
        # rejects raises here and stops the sequence (an earlier prefix
        # may already be deleted -- re-run with the remainder).
        print("FAILED", err)

``delete_structure`` deletes in order and is **fail-fast**: it returns one
:class:`~pysdmx.api.stat.StructureSubmissionResult` per artefact it
deletes, but the first the NSI rejects raises
:class:`~pysdmx.errors.Invalid` and stops the loop — so wrap it in
``try``/``except`` as above.

Configuration
-------------

The snippets read the FMR and .Stat endpoints and bearer tokens from the
environment:

.. code-block:: bash

    export FMR_ENDPOINT="https://my.fmr/sdmx/v2"
    export DOTSTAT_TOKEN="eyJ..."  # a fresh .Stat bearer token

See :doc:`publishing structures from FMR to .Stat <fmr_to_stat>` for the
forward direction.
