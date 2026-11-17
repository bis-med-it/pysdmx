"""Exercise: keep .Stat Suite in sync with an FMR.

Publish real ECB exchange-rate structures to a Fusion Metadata Registry
(FMR) and from the FMR to .Stat Suite, load data into .Stat, then remove
from .Stat the structures that the FMR no longer has. The exercise is a
closed loop on .Stat: it does not touch what was already there, and at the
end it removes the data and the structures that it has published.

This script has the same steps as the notebook
fmr_stat_sync_practice.ipynb. The three uploads (to the FMR, to .Stat and of
the data) are marked "to complete": their code is to be written below their
hint. The other steps are already written. The answer is in the solution
folder, as a script and as a notebook, and fmr_stat_sync.ipynb explains the
steps.

The script asks for the SDMX Lab instance, its user and its password, unless
they are set in the environment (SDMX_LAB, SDMX_LAB_USER and
SDMX_LAB_PASSWORD).
"""

# ruff: noqa: E402, F401, F821

import os
from getpass import getpass

# Every structure of the tutorial starts with this prefix, which tells them
# apart from the other structures of the agency. Only letters, digits and
# underscores are allowed.
os.environ["PREFIX"] = "PX_SYNC"

# The SDMX Lab instance of the participant, its user and its password are
# requested, unless they are already set in the environment. The password
# is not displayed.
if not os.environ.get("SDMX_LAB"):
    os.environ["SDMX_LAB"] = input("SDMX Lab instance (<id>.sdmx.solutions): ")
if not os.environ.get("SDMX_LAB_USER"):
    os.environ["SDMX_LAB_USER"] = input("User: ")
    os.environ["SDMX_LAB_PASSWORD"] = getpass("Password: ")

from contextlib import suppress
from io import BytesIO

from helpers import (
    AGENCY,
    DELETION_ORDER,
    DLM,
    ECB_STRUCTURES,
    PREFIX,
    STAT_FORMAT,
    build_dataset,
    build_structures,
    check_connections,
    fmr_client,
    fmr_service,
    list_urns,
    stat_data,
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
# Note: If a service fails, start again from the beginning (in a notebook,
# restart the kernel first), to enter the instance, the user and the password
# again.
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

# Step 3 (to complete): Upload the structures to keep to the FMR.
# Note: Replace overwrites the existing structures, so the step can be run
# again. legacy is not uploaded.
# Hint: `fmr_client()` returns a `RegistryMaintenanceClient`. Call its
# `put_structures` method with `keep` and `action=StructureAction.Replace`.
# To be completed

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

# Part 2: Publish from the FMR to .Stat and load data

# Step 5: Record what .Stat already has, and find what it does not have yet.
# Note: The SDMX:AGENCIES agency scheme is left out: the agency scheme is not
# maintained by this process.
# Note: before records the structures of the tutorial that .Stat already has:
# they are not published again, and the exercise does not change or delete
# them. On a first run it is empty.
before = list_urns(stat_service())
from_fmr = [s for s in graph.structures if not isinstance(s, AgencyScheme)]
to_stat = [s for s in from_fmr if s.short_urn not in before]
print([s.short_urn for s in to_stat])

# Step 6 (to complete): Publish them to .Stat.
# Note: The result has success, which must be True, and messages: if .Stat
# rejects a structure, the reason is in the messages.
# Hint: If `to_stat` is not empty, call `stat_uploader().submit_structure` with
# `to_stat` and `STAT_FORMAT`, and print the `success` and the `messages` of
# the result.
# To be completed

# Step 7: Build the dataset of the dataflow.
# Note: build_dataset(graph) reads monthly ECB reference exchange rates of four
# currencies and returns them as a dataset of the dataflow.
# Note: The data are loaded only into a dataflow that this exercise has
# published: otherwise dataset is None.
flow = graph.get_dataflows()[0]
dataset = build_dataset(graph) if flow.short_urn not in before else None
print(len(dataset.data) if dataset is not None else 0, "observations to load")

# Step 8 (to complete): Load the data into the dataflow.
# Note: The Transfer service processes the data asynchronously: the submission
# returns the id of the request, and its outcome is requested afterwards.
# Hint: If `dataset` is not None, call `stat_uploader().submit_data(dataset)`:
# the result has a `request_id`. Then call
# `stat_uploader().submission_status(request_id, wait=True)`, and print the
# `outcome` and the `logs` of its result.
# To be completed

# Step 9: Read the data back from .Stat.
# Note: stat_data queries the data of the dataflow on .Stat.
# Note: The dataflow and its data can also be seen in the Data Lifecycle
# Manager of the instance, until the loop is closed in Part 4.
print("Data Lifecycle Manager:", DLM)
if dataset is not None:
    print(stat_data(flow).tail())

# Step 10: Create a difference between the FMR and .Stat.
# Note: legacy is submitted to .Stat only.
retired = [s for s in legacy if s.short_urn not in before]
if retired:
    result = stat_uploader().submit_structure(retired, STAT_FORMAT)
    print(result.success, result.messages)

# Part 3: Bring .Stat back in sync

# Step 11: List the structures on both sides.
# Note: list_urns requests the structures of the agency one type at a time, as
# stubs, and returns the short URNs of those whose id starts with PREFIX.
# Note: The FMR is the reference: without valid credentials its list is empty,
# and every structure on .Stat would then be taken as retired, so the step
# stops in that case.
# Note: The structures that .Stat had before the exercise was run are left out
# of the comparison.
fmr_urns = list_urns(fmr_service())
if not fmr_urns:
    raise RuntimeError("The FMR list is empty: check the user and password.")
stat_urns = list_urns(stat_service()) - before
print("FMR:  ", sorted(fmr_urns))
print(".Stat:", sorted(stat_urns))

# Step 12: Find what .Stat has and the FMR does not.
# Note: The extras must be inspected before anything is deleted: they are the
# EXR_OLD dataflow, its DSD and CL_UNIT. The codelists shared with EXR are
# still in the FMR, so they are not part of the extras.
extras = stat_urns - fmr_urns
print(sorted(extras))

# Step 13: Try to delete the DSD first.
# Note: .Stat refuses (409), because the EXR_OLD dataflow still uses the DSD.
try:
    stat_uploader().delete_structure(
        [u for u in extras if u.startswith("DataStructure=")]
    )
except Invalid as error:
    print(error)

# Step 14: Delete the extras, dependents first.
# Note: delete_structure takes a list of short URNs, deletes them in order and
# stops at the first error. In that case, fix the cause and run it again with
# the remaining structures.
ordered = sorted(extras, key=lambda urn: DELETION_ORDER[urn.split("=")[0]])
for result in stat_uploader().delete_structure(ordered):
    print(result.messages)

# Step 15: Check that .Stat matches the FMR again.
# Note: The printed list must be empty: nothing extra is left on .Stat.
stat_after = list_urns(stat_service()) - before
print(sorted(stat_after - fmr_urns))

# Part 4: Close the loop

# Step 16: Delete the data and the constraint that .Stat created for them.
# Note: The exercise now removes what it has published, so that .Stat is left
# as it was found. The order matters: first the data, then their constraint,
# and then the structures, dependents first. .Stat refuses to delete a dataflow
# while its constraint exists.
# Note: The structures that the exercise has published are those that .Stat has
# now and did not have before. delete_data submits the observations of the
# dataflow with the Delete action.
# Note: After an interrupted run, the structures that it published are part of
# before on the next run, and are therefore not removed. To remove them, set
# before = set() before running the steps of this part: everything with the
# prefix is then removed from .Stat.
published = list_urns(stat_service()) - before
if flow.short_urn in published:
    request = stat_uploader().delete_data(build_dataset(graph))
    status = stat_uploader().submission_status(request.request_id, wait=True)
    print("data deleted:", status.outcome)
    constraint = (
        f"ContentConstraint={flow.agency}:CR_A_{flow.id}({flow.version})"
    )
    with suppress(NotFound):
        for result in stat_uploader().delete_structure(constraint):
            print(result.messages)

# Step 17: Delete the structures that the exercise has published, dependents
# first.
# Note: cleanup_dsd removes what the Transfer service keeps for the DSD.
# Note: The printed list must be empty: .Stat is left as it was found. The
# copies in the FMR remain, because pysdmx cannot delete from the FMR.
ordered = sorted(published, key=lambda urn: DELETION_ORDER[urn.split("=")[0]])
for result in stat_uploader().delete_structure(ordered):
    print(result.messages)
dsd = graph.get_data_structure_definitions()[0]
if dsd.short_urn in published:
    print(stat_uploader().cleanup_dsd(dsd).message)
print(sorted(list_urns(stat_service()) - before))

# Bonus: Create another difference and remove it.
# Note: A codelist that only exists on .Stat is found by the comparison, like
# the structures in legacy.
# Hint: Build a `Codelist` with `agency=AGENCY`, an id that starts with
# `PREFIX` and an underscore, a name and two `Code` items, each with an id and
# a name. Submit it to .Stat only, and repeat the comparison and the deletion.
# To be completed
