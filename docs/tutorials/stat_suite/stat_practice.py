"""Publish structures to .Stat Suite and clean it up against an FMR.

This script shows how pysdmx can publish structures from an FMR to .Stat
Suite, and then remove from .Stat the structures the FMR no longer has.
Run fmr_practice.py first, with the same PREFIX. The notebook
stat_practice.ipynb has the same steps as an exercise.
"""

from contextlib import suppress
from io import BytesIO

from helpers import (
    AGENCY,
    ECB_STRUCTURES,
    NSI,
    PREFIX,
    SPACE,
    STAT_FORMAT,
    TRANSFER,
    TYPES,
    build_structures,
    dotstat_token,
    fmr_service,
    sdmx_service,
)

from pysdmx.api.qb import (
    StructureDetail,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.api.stat import StatUploader
from pysdmx.errors import Invalid, NotFound
from pysdmx.io import read_sdmx
from pysdmx.model import AgencyScheme

# Step 1: Build the structures, as in the FMR tutorial.
ecb = read_sdmx(ECB_STRUCTURES, validate=False)
keep, legacy = build_structures(ecb)

# Step 2: Connect to .Stat with write access.
# Note: .Stat tokens expire after 10 minutes: create a new client if a call is
# rejected.
stat = StatUploader(
    nsi_endpoint=NSI,
    transfer_endpoint=TRANSFER,
    dataspace=SPACE,
    token=dotstat_token(),
)

# Step 3: Start from a clean .Stat.
# Note: .Stat rejects a structure that already exists, so we remove what an
# earlier run left behind. Each list ends with its dataflow, so reversing it
# deletes dependents first.
for artefact in [*reversed(legacy), *reversed(keep)]:
    with suppress(Invalid, NotFound):
        stat.delete_structure(artefact)

# Step 4: Download the EXR dataflow with all its references from the FMR.
query = StructureQuery(
    artefact_type=StructureType.DATAFLOW,
    agency_id=AGENCY,
    resource_id=f"{PREFIX}_DF_EXR",
    version="1.0",
    detail=StructureDetail.FULL,
    references=StructureReference.ALL,
)
graph = read_sdmx(BytesIO(fmr_service().structure(query)), validate=False)

# Step 5: Publish it to .Stat.
# Note: The SDMX:AGENCIES agency scheme is left out so that it does not
# overwrite the one on .Stat.
to_stat = [s for s in graph.structures if not isinstance(s, AgencyScheme)]
result = stat.submit_structure(to_stat, STAT_FORMAT)
print(result.success, result.messages)

# Step 6: Inspect the result.
# Note: Notice success is True. If .Stat rejects a structure, the reason is in
# the messages.

# Step 7: Create a difference between the FMR and .Stat.
# Note: legacy stands for structures retired in the FMR but still on .Stat.
stat.submit_structure(legacy, STAT_FORMAT)


# Step 8: List your structures on both sides.
# Note: .Stat rejects queries for all types at once, so we ask for one type at
# a time, and only for stubs.
def list_urns(service):
    """Return the short URNs of our structures on a service."""
    urns = set()
    for stype in TYPES:
        query = StructureQuery(
            artefact_type=stype,
            agency_id=AGENCY,
            detail=StructureDetail.ALL_STUBS,
        )
        try:
            msg = read_sdmx(BytesIO(service.structure(query)), validate=False)
        except (Invalid, NotFound):
            continue
        urns |= {
            s.short_urn for s in msg.structures if s.id.startswith(PREFIX)
        }
    return urns


fmr_urns = list_urns(fmr_service())
stat_urns = list_urns(sdmx_service(f"{NSI}/rest/v2", dotstat_token()))

# Step 9: Find what .Stat has and the FMR does not.
extras = stat_urns - fmr_urns
print(sorted(extras))

# Step 10: Inspect the extras before deleting anything.
# Note: Notice the EXR_OLD dataflow, its DSD and CL_UNIT. The codelists shared
# with EXR are still in the FMR, so they are not here.
# Note: If the FMR list were incomplete, valid structures would appear here
# too.

# Step 11: Try to delete the DSD first.
# Note: .Stat refuses (409) because the EXR_OLD dataflow still uses the DSD.
try:
    stat.delete_structure(
        [u for u in extras if u.startswith("DataStructure=")]
    )
except Invalid as error:
    print(error)

# Step 12: Delete the extras in the right order: dependents first.
# Note: delete_structure stops at the first error. If that happens, fix the
# cause and run it again with what is left.
ORDER = {
    "DataConstraint": 0,
    "Dataflow": 1,
    "DataStructure": 2,
    "ConceptScheme": 3,
    "Codelist": 4,
}
ordered = sorted(extras, key=lambda urn: ORDER.get(urn.split("=")[0], 9))
for result in stat.delete_structure(ordered):
    print(result.messages)

# Step 13: Check that .Stat matches the FMR again.
stat_after = list_urns(sdmx_service(f"{NSI}/rest/v2", dotstat_token()))
print(sorted(stat_after - fmr_urns))

# Step 14: Inspect the check.
# Note: The list is empty: nothing extra is left on .Stat.

# Step 15: Remove the structures to keep from .Stat, so the script can be run
# again.
stat.delete_structure(list(reversed(keep)))
