"""Publish structures to an FMR and read them back.

This script shows how pysdmx can write structures to a Fusion Metadata
Registry (FMR) and read them back, using real ECB exchange-rate
structures. The notebook fmr_practice.ipynb has the same steps as an
exercise.
"""

from io import BytesIO

from helpers import (
    AGENCY,
    ECB_STRUCTURES,
    FMR_ENDPOINT,
    FMR_PASSWORD,
    FMR_TOKEN,
    FMR_USER,
    PREFIX,
    TYPES,
    build_structures,
    fmr_service,
)

from pysdmx.api.fmr.maintenance import (
    RegistryMaintenanceClient,
    StructureAction,
)
from pysdmx.api.qb import (
    StructureDetail,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.errors import Invalid, NotFound
from pysdmx.io import read_sdmx

# Step 1: Read the ECB exchange-rate structures.
ecb = read_sdmx(ECB_STRUCTURES, validate=False)
print([s.short_urn for s in ecb.structures])

# Step 2: Inspect the structures.
# Note: Notice the 11 codelists, the concept scheme, the DSD, the dataflow and
# the agency scheme.

# Step 3: Prepare the structures to publish.
# Note: build_structures moves the ECB codelists and concepts to our agency,
# adds PREFIX to their ids, and builds two dataflows on top of them: EXR (in
# keep) and EXR_OLD (in legacy). The ECB DSD itself is left out: a pysdmx bug
# breaks its facets in SDMX-JSON, the only format of the FMR upload.
keep, legacy = build_structures(ecb)
print("keep:  ", [s.short_urn for s in keep])
print("legacy:", [s.short_urn for s in legacy])

# Step 4: Connect to the FMR with write access.
# Note: The client accepts a bearer token or a user and password.
if FMR_TOKEN:
    client = RegistryMaintenanceClient(FMR_ENDPOINT, access_token=FMR_TOKEN)
else:
    client = RegistryMaintenanceClient(
        FMR_ENDPOINT, user=FMR_USER, password=FMR_PASSWORD
    )

# Step 5: Upload the structures to keep.
# Note: Replace overwrites existing structures, so the script can be run again.
# Note: legacy is not uploaded: it stands for a structure retired in the FMR.
client.put_structures(keep, action=StructureAction.Replace)

# Step 6: Download the EXR dataflow with all its references.
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

# Step 7: Inspect the download.
# Note: Notice the dataflow comes with its DSD, the concept scheme, the
# codelists and the SDMX:AGENCIES agency scheme.

# Step 8: List your structures in the FMR.
# Note: Some services reject queries for all types at once, so we ask for one
# type at a time, and only for stubs (ids and versions).
urns = set()
for stype in TYPES:
    query = StructureQuery(
        artefact_type=stype,
        agency_id=AGENCY,
        detail=StructureDetail.ALL_STUBS,
    )
    try:
        msg = read_sdmx(
            BytesIO(fmr_service().structure(query)), validate=False
        )
    except (Invalid, NotFound):
        continue
    urns |= {s.short_urn for s in msg.structures if s.id.startswith(PREFIX)}
print(sorted(urns))

# Step 9: Inspect the list.
# Note: It holds exactly the structures in keep.
