"""Configuration and helpers for the FMR and .Stat Suite tutorial.

They are shared by the course notebook (fmr_stat_sync.ipynb), the exercise
(fmr_stat_sync_practice.ipynb) and its answer (fmr_stat_sync_practice.py).
The settings are read from environment variables when this module is
imported.
"""

import base64
import json
import os
import re
import time
from contextlib import suppress
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from msgspec.structs import replace
from pysdmx.api.stat.authentication import KeycloakAuthentication

from pysdmx.api.fmr.maintenance import RegistryMaintenanceClient
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

# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------

# The identifier of the SDMX Lab instance of the participant.
SDMX_LAB = os.environ.get("SDMX_LAB", "")

# The FMR: its web service, and a user and a password, or a bearer token.
FMR_ENDPOINT = os.environ.get(
    "FMR_ENDPOINT", f"https://{SDMX_LAB}.sdmx.solutions/fmr/sdmx/v2"
)
FMR_USER = os.environ.get("FMR_USER")
FMR_PASSWORD = os.environ.get("FMR_PASSWORD")
FMR_TOKEN = os.environ.get("FMR_TOKEN")

# .Stat Suite: the NSI web service, the Transfer service and the dataspace.
NSI = os.environ.get("NSI", "https://nsi-demo-stable.siscc.org")
TRANSFER = os.environ.get("TRANSFER", "https://transfer-demo.siscc.org/3")
SPACE = os.environ.get("SPACE", "staging:SIS-CC-stable")
# The .Stat token is requested from Keycloak with a user and a password or,
# without them, read from a file.
KEYCLOAK = os.environ.get("KEYCLOAK", "https://keycloak.siscc.org/realms/OECD")
STAT_USER = os.environ.get("STAT_USER")
STAT_PASSWORD = os.environ.get("STAT_PASSWORD")
STAT_CLIENT_ID = os.environ.get("STAT_CLIENT_ID", "app")
DOTSTAT_TOKEN_FILE = os.environ.get("DOTSTAT_TOKEN_FILE", "dotstat.token")
# Structures are read and submitted to .Stat as SDMX-ML 2.1.
STAT_FORMAT = Format.STRUCTURE_SDMX_ML_2_1

AGENCY = os.environ.get("AGENCY", "BIS")
# Every structure of the tutorial starts with this prefix, which tells them
# apart from the other structures of the agency.
PREFIX = os.environ.get("PREFIX", "PX_SYNC")

ECB_STRUCTURES = (
    "https://data-api.ecb.europa.eu/service/"
    "dataflow/ECB/EXR/latest?references=descendants"
)
# The types of the structures that are compared between the FMR and .Stat.
TYPES = (
    StructureType.CODELIST,
    StructureType.CONCEPT_SCHEME,
    StructureType.DATA_STRUCTURE,
    StructureType.DATAFLOW,
    StructureType.DATA_CONSTRAINT,
)
# The position of each type in a deletion: the dependents come first.
DELETION_ORDER = {
    "DataConstraint": 0,
    "ContentConstraint": 0,
    "Dataflow": 1,
    "DataStructure": 2,
    "ConceptScheme": 3,
    "Codelist": 4,
}

# --------------------------------------------------------------------------
# Connections
# --------------------------------------------------------------------------


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
    """Return a reader of the FMR, with HTTP Basic when FMR_USER is set."""
    svc = sdmx_service(FMR_ENDPOINT, FMR_TOKEN)
    if FMR_USER and not FMR_TOKEN:
        pair = f"{FMR_USER}:{FMR_PASSWORD}".encode()
        # RestService only sends bearer tokens, so set the header directly.
        svc._headers["Authorization"] = (
            f"Basic {base64.b64encode(pair).decode()}"
        )
    return svc


def fmr_client():
    """Return a client of the FMR with write access."""
    if FMR_TOKEN:
        return RegistryMaintenanceClient(FMR_ENDPOINT, access_token=FMR_TOKEN)
    return RegistryMaintenanceClient(
        FMR_ENDPOINT, user=FMR_USER, password=FMR_PASSWORD
    )


@lru_cache(maxsize=1)
def _keycloak():
    """Return the Keycloak authentication of the .Stat user."""
    return KeycloakAuthentication(
        KEYCLOAK,
        user=STAT_USER,
        password=STAT_PASSWORD,
        client_id=STAT_CLIENT_ID,
    )


def stat_token():
    """Return a .Stat bearer token.

    With STAT_USER and STAT_PASSWORD, the token is requested from Keycloak
    and renewed when it expires. Otherwise, it is read from the
    DOTSTAT_TOKEN_FILE file.

    Raises:
        RuntimeError: If there is no token.
    """
    if STAT_USER:
        token = _keycloak().get_token()
        if not token:
            raise RuntimeError(f"No .Stat token. {_keycloak().init_status}")
        return token
    if not Path(DOTSTAT_TOKEN_FILE).exists():
        raise RuntimeError(
            "No .Stat token: set STAT_USER and STAT_PASSWORD, or save a "
            f"token to the file {DOTSTAT_TOKEN_FILE!r}."
        )
    raw = Path(DOTSTAT_TOKEN_FILE).read_text()
    return re.sub(r"[^A-Za-z0-9._-]", "", raw)


def minutes_left(token):
    """Return the minutes until a token expires (no checks are made)."""
    payload = token.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    claims = json.loads(base64.urlsafe_b64decode(payload))
    return (claims["exp"] - time.time()) / 60


def stat_service():
    """Return a reader of .Stat, with the current token."""
    return sdmx_service(f"{NSI}/rest/v2", stat_token())


def stat_uploader():
    """Return a client of .Stat with write access, with the current token."""
    return StatUploader(
        nsi_endpoint=NSI,
        transfer_endpoint=TRANSFER,
        dataspace=SPACE,
        token=stat_token(),
    )


def _check(name, service):
    """Print whether a service answers and has AGENCY in its agencies."""
    roster = StructureQuery(StructureType.AGENCY_SCHEME, "SDMX", "AGENCIES")
    try:
        msg = read_sdmx(BytesIO(service().structure(roster)), validate=False)
        agencies = {agency.id for agency in msg.structures[0].items}
    except Exception as error:
        print(
            f"{name}: FAILED. Check its address and its credentials "
            f"({type(error).__name__}: {error})"
        )
        return
    registered = "is" if AGENCY in agencies else "IS NOT"
    print(f"{name}: connected. The agency {AGENCY} {registered} registered.")


def check_connections():
    """Test the connections with read-only queries and print the outcome."""
    print(f"Agency {AGENCY}, prefix {PREFIX}")
    _check(f"FMR   ({FMR_ENDPOINT})", fmr_service)
    _check(f".Stat ({NSI})", stat_service)
    with suppress(Exception):
        print(f".Stat token valid for {minutes_left(stat_token()):.1f} min")


# --------------------------------------------------------------------------
# Structures
# --------------------------------------------------------------------------


def list_urns(service):
    """Return the short URNs of the structures of the tutorial on a service.

    The structures of AGENCY are requested one type at a time, because
    .Stat rejects the queries for all types, and as stubs (ids and versions
    only). Only the ids that start with PREFIX and an underscore are kept.

    Raises:
        Invalid: If the service rejects the credentials (401 or 403).
    """
    urns = set()
    for stype in TYPES:
        query = StructureQuery(
            artefact_type=stype,
            agency_id=AGENCY,
            detail=StructureDetail.ALL_STUBS,
        )
        try:
            msg = read_sdmx(BytesIO(service.structure(query)), validate=False)
        except NotFound:
            continue  # there are no structures of this type
        except Invalid as error:
            if error.title in ("Client error 401", "Client error 403"):
                raise  # the credentials are rejected
            continue  # there are no structures of this type
        urns |= {
            s.short_urn
            for s in msg.structures or []
            if s.id.startswith(f"{PREFIX}_")
        }
    return urns


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
                # The writers link the codelist through its full URN.
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
    """Return the ``keep`` and ``legacy`` structures built from ``ecb``.

    The ECB concept scheme and codelists are copied to AGENCY, with PREFIX
    added to their ids, and two dataflows are built on top of them: EXR
    (in ``keep``) and EXR_OLD, which also has a UNIT attribute (in
    ``legacy``). Each list ends with its DSD and its dataflow, so
    reversing it gives the dependents first.
    """
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
