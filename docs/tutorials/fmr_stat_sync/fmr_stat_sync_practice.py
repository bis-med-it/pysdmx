"""Keep .Stat Suite in sync with an FMR.

This script shows how pysdmx can publish structures to a Fusion Metadata
Registry (FMR) and from the FMR to .Stat Suite, and then remove from .Stat
the structures the FMR no longer has, using real ECB exchange-rate
structures. The notebook fmr_stat_sync_practice.ipynb is the exercise on
the same steps, and fmr_stat_sync.ipynb explains them.

Before running it, set in the environment the identifier of the SDMX Lab
instance (SDMX_LAB), its user (SDMX_LAB_USER) and its password
(SDMX_LAB_PASSWORD).
"""

from contextlib import suppress
from io import BytesIO

from helpers import (
    AGENCY,
    DELETION_ORDER,
    ECB_STRUCTURES,
    PREFIX,
    STAT_FORMAT,
    build_structures,
    check_connections,
    fmr_client,
    fmr_service,
    list_urns,
    stat_service,
    stat_uploader,
)

from pysdmx.api.fmr.maintenance import StructureAction
from pysdmx.api.qb import (
    StructureDetail,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.errors import Invalid, NotFound
from pysdmx.io import read_sdmx
from pysdmx.model import AgencyScheme, Code, Codelist

# Part 1: Publish to the FMR

# Step 1: Check the connections.
# Note: check_connections tests the FMR and .Stat with read-only queries. Both
# services must be connected before going on.
# Note: If a service fails, restart the kernel and run the cells again, to
# enter the instance, the user and the password again.
check_connections()

# Step 2: Read the ECB exchange-rate structures and prepare the structures to
# publish.
# Note: build_structures copies the ECB codelists and concepts to the agency of
# the participant, adds PREFIX to their ids, and builds two dataflows on top of
# them: EXR (in keep) and EXR_OLD (in legacy).
# Note: legacy stands for structures that have been retired in the FMR but
# remain on .Stat.
ecb = read_sdmx(ECB_STRUCTURES, validate=False)
keep, legacy = build_structures(ecb)
print("keep:  ", [s.short_urn for s in keep])
print("legacy:", [s.short_urn for s in legacy])

# Step 3: Upload the structures to keep to the FMR.
# Note: Replace overwrites the existing structures, so the step can be run
# again. legacy is not uploaded.
fmr_client().put_structures(keep, action=StructureAction.Replace)
print("uploaded to the FMR:", len(keep), "structures")

# Step 4: Download the EXR dataflow with all its references from the FMR.
# Note: The dataflow comes with its DSD, the concept scheme, the codelists and
# the SDMX:AGENCIES agency scheme.
query = StructureQuery(
    artefact_type=StructureType.DATAFLOW,
    agency_id=AGENCY,
    resource_id=f"{PREFIX}_DF_EXR",
    version="1.0",
    detail=StructureDetail.FULL,
    references=StructureReference.ALL,
)
graph = read_sdmx(BytesIO(fmr_service().structure(query)), validate=False)
print([s.short_urn for s in graph.structures])

# Part 2: Publish from the FMR to .Stat

# Step 5: Start from a clean .Stat.
# Note: .Stat rejects a structure that already exists, so the structures left
# by a previous run are removed first. Each list ends with its DSD and its
# dataflow, so reversing it deletes the dependents first.
stat = stat_uploader()
for artefact in [*reversed(legacy), *reversed(keep)]:
    with suppress(Invalid, NotFound):
        stat.delete_structure(artefact)

# Step 6: Publish the download to .Stat.
# Note: The SDMX:AGENCIES agency scheme is left out: the agency scheme is not
# maintained by this process.
# Note: The result has success, which must be True, and messages: if .Stat
# rejects a structure, the reason is in the messages.
# Note: To run the step again, run Step 5 first: .Stat rejects the structures
# that already exist.
to_stat = [s for s in graph.structures if not isinstance(s, AgencyScheme)]
result = stat_uploader().submit_structure(to_stat, STAT_FORMAT)
print(result.success, result.messages)

# Step 7: Create a difference between the FMR and .Stat.
# Note: legacy is submitted to .Stat only.
result = stat_uploader().submit_structure(legacy, STAT_FORMAT)
print(result.success, result.messages)

# Part 3: Bring .Stat back in sync

# Step 8: List the structures on both sides.
# Note: list_urns requests the structures of the agency one type at a time, as
# stubs, and returns the short URNs of those whose id starts with PREFIX.
# Note: The FMR is the reference: without valid credentials its list is empty,
# and every structure on .Stat would then be taken as retired, so the step
# stops in that case.
fmr_urns = list_urns(fmr_service())
if not fmr_urns:
    raise RuntimeError("The FMR list is empty: check the user and password.")
stat_urns = list_urns(stat_service())
print("FMR:  ", sorted(fmr_urns))
print(".Stat:", sorted(stat_urns))

# Step 9: Find what .Stat has and the FMR does not.
# Note: The extras must be inspected before anything is deleted: they are the
# EXR_OLD dataflow, its DSD and CL_UNIT. The codelists shared with EXR are
# still in the FMR, so they are not part of the extras.
extras = stat_urns - fmr_urns
print(sorted(extras))

# Step 10: Try to delete the DSD first.
# Note: .Stat refuses (409), because the EXR_OLD dataflow still uses the DSD.
try:
    stat_uploader().delete_structure(
        [u for u in extras if u.startswith("DataStructure=")]
    )
except Invalid as error:
    print(error)

# Step 11: Delete the extras, dependents first.
# Note: delete_structure takes a list of short URNs, deletes them in order and
# stops at the first error. In that case, fix the cause and run it again with
# the remaining structures.
ordered = sorted(extras, key=lambda urn: DELETION_ORDER[urn.split("=")[0]])
for result in stat_uploader().delete_structure(ordered):
    print(result.messages)

# Step 12: Check that .Stat matches the FMR again, and remove the structures to
# keep from .Stat.
# Note: The printed list must be empty: nothing extra is left on .Stat.
# Note: The structures to keep are removed from .Stat, so that the exercise can
# be run again. The copies in the FMR remain, because pysdmx cannot delete from
# the FMR.
stat_after = list_urns(stat_service())
print(sorted(stat_after - fmr_urns))
stat_uploader().delete_structure(list(reversed(keep)))

# Bonus: Create another difference and remove it.
# Note: A codelist that only exists on .Stat is found by the comparison, like
# the structures in legacy.
extra_codelist = Codelist(
    id=f"{PREFIX}_CL_EXTRA",
    agency=AGENCY,
    version="1.0",
    name="A codelist that is not in the FMR",
    items=[Code(id="A", name="First code"), Code(id="B", name="Second code")],
)
stat_uploader().submit_structure([extra_codelist], STAT_FORMAT)
extras = list_urns(stat_service()) - fmr_urns
print(sorted(extras))
stat_uploader().delete_structure(sorted(extras))
