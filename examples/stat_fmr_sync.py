"""Reconcile a .Stat Suite instance against an FMR (agency ``MD``).

Lists every ``MD`` structure on both sides, then reports the ones that
exist in .Stat but not in the FMR -- treating the FMR as the source of
truth -- and (with ``--apply``) deletes those extras from .Stat.

Both services expose the SDMX-REST v2 structure API, so a single
``StructureType.ALL`` stub query lists each side. Deletions run in
dependency order (constraints -- including the ``CR_A_*`` ones a data
import auto-creates -- before dataflows, then DSDs, concept schemes and
codelists) so a still-referenced artefact never blocks its dependents.

This is a runnable example -- it needs live FMR and .Stat instances --
not a CI test. It is **safe by default**: without ``--apply`` it only
prints what it would delete.

Run::

    export FMR_ENDPOINT="https://my.fmr/sdmx/v2"  # SDMX-REST v2 base
    export FMR_TOKEN="eyJ..."      # optional, if the FMR needs auth
    export DOTSTAT_TOKEN="eyJ..."  # a fresh .Stat bearer token
    poetry run python examples/stat_fmr_sync.py            # dry run
    poetry run python examples/stat_fmr_sync.py --apply    # delete

.Stat defaults target the SIS-CC public demo; override with the env
vars ``DOTSTAT_NSI``, ``DOTSTAT_TRANSFER`` and ``DOTSTAT_SPACE``.
"""

from __future__ import annotations

import os
import sys
from io import BytesIO

from pysdmx.api.qb import (
    ApiVersion,
    RestService,
    StructureDetail,
    StructureFormat,
    StructureQuery,
    StructureType,
)
from pysdmx.api.stat import StatUploader
from pysdmx.errors import Invalid, NotFound
from pysdmx.io import read_sdmx

AGENCY = os.environ.get("DOTSTAT_AGENCY", "MD")
FMR_ENDPOINT = os.environ.get("FMR_ENDPOINT", "https://my.fmr/sdmx/v2")
NSI = os.environ.get("DOTSTAT_NSI", "https://nsi-demo-stable.siscc.org")
TRANSFER = os.environ.get(
    "DOTSTAT_TRANSFER", "https://transfer-demo.siscc.org/3"
)
SPACE = os.environ.get("DOTSTAT_SPACE", "staging:SIS-CC-stable")

# Delete dependents before the artefacts they reference (lower = first).
_DELETE_ORDER = {
    "DataConstraint": 0,
    "ContentConstraint": 0,
    "ProvisionAgreement": 1,
    "Dataflow": 2,
    "DataStructure": 3,
    "ConceptScheme": 4,
    "Codelist": 5,
    "AgencyScheme": 6,
}


# Not every service supports the all-types 'structure/*/{agency}' form
# (.Stat returns HTTP 422), so list each maintainable type explicitly.
_TYPES = (
    StructureType.CODELIST,
    StructureType.CONCEPT_SCHEME,
    StructureType.DATA_STRUCTURE,
    StructureType.DATAFLOW,
    StructureType.DATA_CONSTRAINT,
)


def list_md_urns(base: str, token: str | None) -> set[str]:
    """Return the short-URNs of every MD structure at an SDMX-REST base."""
    svc = RestService(
        base,
        ApiVersion.V2_0_0,
        structure_format=StructureFormat.SDMX_ML_2_1,
        token=token,
    )
    urns: set[str] = set()
    for stype in _TYPES:
        query = StructureQuery(stype, AGENCY, detail=StructureDetail.ALL_STUBS)
        try:
            msg = read_sdmx(BytesIO(svc.structure(query)), validate=False)
        except (Invalid, NotFound):
            # A type with no artefacts may 404 or return an empty,
            # unparseable body; treat it as "none of that type".
            continue
        urns |= {s.short_urn for s in msg.structures or []}
    return urns


def _delete_rank(urn: str) -> int:
    """Rank a short-URN so dependents are deleted before their targets."""
    return _DELETE_ORDER.get(urn.split("=", 1)[0], 99)


def main() -> None:
    """List MD structures on both sides and prune .Stat's extras."""
    should_apply = "--apply" in sys.argv[1:]
    dotstat_token = os.environ.get("DOTSTAT_TOKEN")
    if not dotstat_token:
        raise SystemExit("Set DOTSTAT_TOKEN to a fresh .Stat bearer token.")

    fmr_urns = list_md_urns(FMR_ENDPOINT, os.environ.get("FMR_TOKEN"))
    stat_urns = list_md_urns(f"{NSI}/rest/v2", dotstat_token)

    extras = sorted(stat_urns - fmr_urns, key=_delete_rank)
    print(f"FMR: {len(fmr_urns)} | .Stat: {len(stat_urns)} MD structures")
    print(f"In .Stat but not in FMR: {len(extras)}")
    for urn in extras:
        print("  -", urn)

    if not extras:
        print("Nothing to prune; .Stat already matches FMR.")
        return
    if not should_apply:
        print("\nDry run. Re-run with --apply to delete the above.")
        return

    uploader = StatUploader(
        NSI, TRANSFER, dataspace=SPACE, token=dotstat_token
    )
    for result in uploader.delete_structure(extras):
        status = "ok" if result.success else "FAILED"
        print(f"  {status}: {'; '.join(result.messages)}")


if __name__ == "__main__":
    main()
