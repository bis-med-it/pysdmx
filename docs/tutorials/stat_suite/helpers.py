"""Configuration and helpers for the .Stat Suite practice exercise."""

import base64
import os
import re
from pathlib import Path

from msgspec.structs import replace

from pysdmx.api.qb import (
    ApiVersion,
    RestService,
    StructureFormat,
    StructureType,
)
from pysdmx.io.format import Format
from pysdmx.model import (
    Codelist,
    Component,
    Components,
    ConceptScheme,
    Dataflow,
    DataStructureDefinition,
    Role,
)
from pysdmx.model.__base import DataType

FMR_ENDPOINT = os.environ.get(
    "FMR_ENDPOINT", "https://sdmxexpwsfa3.sdmx.solutions/fmr/sdmx/v2"
)
FMR_TOKEN = os.environ.get("FMR_TOKEN")
FMR_USER = os.environ.get("FMR_USER")
FMR_PASSWORD = os.environ.get("FMR_PASSWORD")
AGENCY = os.environ.get("AGENCY", "BIS")
# Use your own prefix (e.g. your initials) so that your structures do not
# clash with those of other participants.
PREFIX = os.environ.get("PREFIX", "PX_PRACTICE")

ECB_STRUCTURES = (
    "https://data-api.ecb.europa.eu/service/"
    "dataflow/ECB/EXR/latest?references=descendants"
)
TYPES = (
    StructureType.CODELIST,
    StructureType.CONCEPT_SCHEME,
    StructureType.DATA_STRUCTURE,
    StructureType.DATAFLOW,
    StructureType.DATA_CONSTRAINT,
)

NSI = os.environ.get("NSI", "https://nsi-demo-stable.siscc.org")
TRANSFER = os.environ.get("TRANSFER", "https://transfer-demo.siscc.org/3")
SPACE = os.environ.get("SPACE", "staging:SIS-CC-stable")
DOTSTAT_TOKEN_FILE = os.environ.get("DOTSTAT_TOKEN_FILE", "dotstat.token")
STAT_FORMAT = Format.STRUCTURE_SDMX_ML_2_1


def sdmx_service(base, token=None):
    """Return an SDMX-REST v2 reader for ``base``, in SDMX-ML 2.1."""
    return RestService(
        api_endpoint=base,
        api_version=ApiVersion.V2_0_0,
        structure_format=StructureFormat.SDMX_ML_2_1,
        token=token,
        timeout=120,
    )


def fmr_service():
    """Return an FMR reader, with HTTP Basic when FMR_USER is set."""
    svc = sdmx_service(FMR_ENDPOINT, FMR_TOKEN)
    if FMR_USER and not FMR_TOKEN:
        pair = f"{FMR_USER}:{FMR_PASSWORD}".encode()
        # RestService only sends bearer tokens, so set the header directly.
        svc._headers["Authorization"] = (
            f"Basic {base64.b64encode(pair).decode()}"
        )
    return svc


def dotstat_token():
    """Read the .Stat bearer token afresh (it expires after 10 minutes)."""
    raw = Path(DOTSTAT_TOKEN_FILE).read_text()
    return re.sub(r"[^A-Za-z0-9._-]", "", raw)


URN = "urn:sdmx:org.sdmx.infomodel"
COMPONENTS = {
    # id: (role, codelist, data type, attachment level)
    "FREQ": (Role.DIMENSION, "CL_FREQ", DataType.STRING, None),
    "CURRENCY": (Role.DIMENSION, "CL_CURRENCY", DataType.STRING, None),
    "CURRENCY_DENOM": (Role.DIMENSION, "CL_CURRENCY", DataType.STRING, None),
    "EXR_TYPE": (Role.DIMENSION, "CL_EXR_TYPE", DataType.STRING, None),
    "EXR_SUFFIX": (Role.DIMENSION, "CL_EXR_SUFFIX", DataType.STRING, None),
    "TIME_PERIOD": (Role.DIMENSION, None, DataType.PERIOD, None),
    "OBS_VALUE": (Role.MEASURE, None, DataType.DOUBLE, None),
    "OBS_STATUS": (Role.ATTRIBUTE, "CL_OBS_STATUS", DataType.STRING, "O"),
    "UNIT": (Role.ATTRIBUTE, "CL_UNIT", DataType.STRING, "O"),
}
EXR = [
    "FREQ",
    "CURRENCY",
    "CURRENCY_DENOM",
    "EXR_TYPE",
    "EXR_SUFFIX",
    "TIME_PERIOD",
    "OBS_VALUE",
    "OBS_STATUS",
]


def restamp(scheme):
    """Copy an item scheme to AGENCY, with PREFIX added to its id."""
    new_id = f"{PREFIX}_{scheme.id}"
    old = f"={scheme.agency}:{scheme.id}({scheme.version})"
    new = f"={AGENCY}:{new_id}({scheme.version})"
    items = [
        replace(item, urn=item.urn.replace(old, new) if item.urn else None)
        for item in scheme.items
    ]
    return replace(scheme, agency=AGENCY, id=new_id, urn=None, items=items)


def build_flow(name, component_ids, concepts, codelists):
    """Build a DSD and its dataflow on top of the re-stamped schemes."""
    concept = {c.id: c for c in concepts.concepts}
    components = []
    for cid in component_ids:
        role, codelist, dtype, attachment = COMPONENTS[cid]
        codes = codelists[codelist] if codelist else None
        components.append(
            Component(
                id=cid,
                required=role != Role.ATTRIBUTE,
                role=role,
                concept=concept[cid],
                local_dtype=dtype,
                local_codes=codes,
                local_enum_ref=(
                    f"{URN}.codelist.{codes.short_urn}" if codes else None
                ),
                attachment_level=attachment,
            )
        )
    dsd = DataStructureDefinition(
        id=f"{PREFIX}_DSD_{name}",
        agency=AGENCY,
        version="1.0",
        name=f"Exchange rates ({name})",
        components=Components(components),
    )
    flow = Dataflow(
        id=f"{PREFIX}_DF_{name}",
        agency=AGENCY,
        version="1.0",
        name=f"Exchange rates ({name})",
        structure=f"{URN}.datastructure.{dsd.short_urn}",
    )
    return [dsd, flow]


def build_structures(ecb):
    """Return the ``keep`` and ``legacy`` structures built from ``ecb``."""
    concepts = restamp(
        next(s for s in ecb.structures if isinstance(s, ConceptScheme))
    )
    codelists = {
        s.id: restamp(s) for s in ecb.structures if isinstance(s, Codelist)
    }
    shared = ["CL_FREQ", "CL_CURRENCY", "CL_EXR_TYPE", "CL_EXR_SUFFIX"]
    keep = [
        concepts,
        *(codelists[c] for c in [*shared, "CL_OBS_STATUS"]),
        *build_flow("EXR", EXR, concepts, codelists),
    ]
    legacy = [
        codelists["CL_UNIT"],
        *build_flow("EXR_OLD", [*EXR, "UNIT"], concepts, codelists),
    ]
    return keep, legacy
