"""Configuration and helpers for the FMR and .Stat Suite tutorial.

They are shared by the course notebook (fmr_stat_sync.ipynb), the exercise
(fmr_stat_sync_practice.ipynb) and its answer (fmr_stat_sync_practice.py).
The settings are read from environment variables when this module is
imported.
"""

import base64
import os
from functools import lru_cache
from io import BytesIO

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

# The SDMX Lab instance of the participant (the first part of its address,
# <id>.sdmx.solutions), its user and its password.
SDMX_LAB = os.environ.get("SDMX_LAB", "")
LAB_USER = os.environ.get("SDMX_LAB_USER", "")
LAB_PASSWORD = os.environ.get("SDMX_LAB_PASSWORD", "")

# The addresses of the services are derived from the instance.
DOTSTAT = f"https://{SDMX_LAB}-dotstat-dlm.sdmx.solutions/dotstat"
# The FMR: its web service.
FMR_ENDPOINT = os.environ.get(
    "FMR_ENDPOINT", f"https://{SDMX_LAB}.sdmx.solutions/fmr/sdmx/v2"
)
# .Stat Suite: the dataspace, its NSI web service and the Transfer service.
SPACE = os.environ.get("SPACE", "demo-design")
NSI = os.environ.get("NSI", f"{DOTSTAT}/nsi-design")
TRANSFER = os.environ.get("TRANSFER", f"{DOTSTAT}/transfer/1.2")
# The Keycloak realm and client that issue the .Stat tokens.
KEYCLOAK = os.environ.get(
    "KEYCLOAK", f"https://{SDMX_LAB}-dotstat-aai.sdmx.solutions/realms/demo"
)
STAT_CLIENT_ID = os.environ.get("STAT_CLIENT_ID", "stat-suite")
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
    """Return a reader of the FMR, with HTTP Basic authentication."""
    svc = sdmx_service(FMR_ENDPOINT)
    pair = f"{LAB_USER}:{LAB_PASSWORD}".encode()
    # RestService only sends bearer tokens, so set the header directly.
    svc._headers["Authorization"] = f"Basic {base64.b64encode(pair).decode()}"
    return svc


def fmr_client():
    """Return a client of the FMR with write access."""
    return RegistryMaintenanceClient(
        FMR_ENDPOINT, user=LAB_USER, password=LAB_PASSWORD
    )


@lru_cache(maxsize=1)
def keycloak():
    """Return the Keycloak authentication of the user of the instance."""
    return KeycloakAuthentication(
        KEYCLOAK,
        user=LAB_USER,
        password=LAB_PASSWORD,
        client_id=STAT_CLIENT_ID,
    )


def stat_token():
    """Return a .Stat bearer token, renewed when it expires.

    Raises:
        RuntimeError: If Keycloak does not issue a token.
    """
    token = keycloak().get_token()
    if not token:
        raise RuntimeError(f"No .Stat token. {keycloak().init_status}")
    return token


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
    """Print whether a service answers a read-only query."""
    roster = StructureQuery(StructureType.AGENCY_SCHEME, "SDMX", "AGENCIES")
    try:
        msg = read_sdmx(BytesIO(service().structure(roster)), validate=False)
        agencies = {agency.id for agency in msg.structures[0].items}
    except NotFound:
        print(f"{name}: connected. It has no agency scheme.")
        return
    except Exception as error:
        print(
            f"{name}: FAILED. Check the instance, the user and the password "
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
