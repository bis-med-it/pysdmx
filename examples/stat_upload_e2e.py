"""End-to-end .Stat Suite upload example using pysdmx StatUploader.

Authors a minimal structure (ConceptScheme + DSD + Dataflow), submits it
to the NSI web service, uploads a tiny dataset to the Transfer service,
and polls the request to completion -- all through pysdmx.

This talks to a **live, writable** .Stat Suite instance, so it needs a
bearer token. On deployments with a federated identity provider (e.g.
GitHub), obtain the token through the browser (the Transfer service's
Swagger "Authorize" button) and export it. This is a runnable example,
not a CI test.

Run::

    export DOTSTAT_TOKEN="eyJ..."          # a fresh bearer token
    poetry run python examples/stat_upload_e2e.py

Defaults target the SIS-CC public demo; override with the env vars
``DOTSTAT_NSI``, ``DOTSTAT_TRANSFER``, ``DOTSTAT_SPACE`` and
``DOTSTAT_AGENCY`` (the agency you are allowed to write).
"""

from __future__ import annotations

import os

import pandas as pd

from pysdmx.api.stat import StatConnector, StatUploader
from pysdmx.io.pd import PandasDataset
from pysdmx.model import (
    Component,
    Components,
    Concept,
    ConceptScheme,
    Dataflow,
    DataStructureDefinition,
    Role,
)
from pysdmx.model.__base import DataType
from pysdmx.model.message import Message
from pysdmx.util import parse_short_urn
from pysdmx.util._model_utils import schema_generator

AGENCY = os.environ.get("DOTSTAT_AGENCY", "MD")
NSI = os.environ.get("DOTSTAT_NSI", "https://nsi-demo-stable.siscc.org")
TRANSFER = os.environ.get(
    "DOTSTAT_TRANSFER", "https://transfer-demo.siscc.org/3"
)
SPACE = os.environ.get("DOTSTAT_SPACE", "staging:SIS-CC-stable")

CS_ID = "CS_PYSDMX_E2E"
DSD_ID = "DSD_PYSDMX_E2E"
DF_ID = "DF_PYSDMX_E2E"
DF_URN = f"Dataflow={AGENCY}:{DF_ID}(1.0)"


def build_structure() -> Message:
    """Author a minimal ConceptScheme + DSD + Dataflow message."""

    def concept(cid: str, name: str, dtype: DataType) -> Concept:
        urn = (
            "urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept="
            f"{AGENCY}:{CS_ID}(1.0).{cid}"
        )
        return Concept(id=cid, name=name, dtype=dtype, urn=urn)

    concepts = [
        concept("REF_AREA", "Reference area", DataType.STRING),
        concept("TIME_PERIOD", "Time period", DataType.PERIOD),
        concept("OBS_VALUE", "Observation value", DataType.DOUBLE),
    ]
    cs = ConceptScheme(
        id=CS_ID,
        agency=AGENCY,
        version="1.0",
        name="pysdmx e2e concepts",
        items=concepts,
    )
    components = Components(
        [
            Component(
                id="REF_AREA",
                required=True,
                role=Role.DIMENSION,
                concept=concepts[0],
                local_dtype=DataType.STRING,
            ),
            Component(
                id="TIME_PERIOD",
                required=True,
                role=Role.DIMENSION,
                concept=concepts[1],
                local_dtype=DataType.PERIOD,
            ),
            Component(
                id="OBS_VALUE",
                required=False,
                role=Role.MEASURE,
                concept=concepts[2],
                local_dtype=DataType.DOUBLE,
            ),
        ]
    )
    dsd = DataStructureDefinition(
        id=DSD_ID,
        agency=AGENCY,
        version="1.0",
        name="pysdmx e2e DSD",
        components=components,
    )
    df = Dataflow(
        id=DF_ID,
        agency=AGENCY,
        version="1.0",
        name="pysdmx e2e dataflow",
        structure=dsd.short_urn,
    )
    return Message(structures=[cs, dsd, df])


def build_dataset(msg: Message) -> PandasDataset:
    """Build a tiny Schema-backed dataset for the authored dataflow."""
    schema = schema_generator(msg, parse_short_urn(DF_URN))
    data = pd.DataFrame(
        {
            "REF_AREA": ["ES", "FR", "DE"],
            "TIME_PERIOD": ["2024", "2024", "2024"],
            "OBS_VALUE": [1.0, 2.0, 3.0],
        }
    )
    return PandasDataset(structure=schema, data=data)


def main() -> None:
    """Run the full author -> submit -> upload -> poll flow."""
    token = os.environ.get("DOTSTAT_TOKEN")
    if not token:
        raise SystemExit("Set DOTSTAT_TOKEN to a fresh bearer token.")

    msg = build_structure()
    dataset = build_dataset(msg)
    uploader = StatUploader(NSI, TRANSFER, dataspace=SPACE, token=token)

    print("1/4 submit_structure ->", f"{NSI}/rest/structure")
    structure = uploader.submit_structure(msg.structures)
    print("  success:", structure.success, "|", "; ".join(structure.messages))

    print("2/4 read the structure back via StatConnector")
    raw = StatConnector(f"{NSI}/rest/v2").fetch_structure(AGENCY, DF_ID, "1.0")
    print("  read back:", len(raw), "bytes of SDMX-ML")

    print("3/4 submit_data -> Transfer /import/sdmxFile")
    result = uploader.submit_data(dataset)
    print("  request id:", result.request_id)

    print("4/4 poll submission_status until terminal")
    final = uploader.submission_status(result.request_id, wait=True)
    print("  ->", final.execution_status, "/", final.outcome)


if __name__ == "__main__":
    main()
