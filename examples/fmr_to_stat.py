"""Publish MD structures from an FMR to a .Stat Suite instance.

Tutorial pipeline, end to end, under the mock agency ``MD``:

1. author a minimal structure graph (ConceptScheme + DSD + Dataflow);
2. upload it to an FMR with :class:`RegistryMaintenanceClient`;
3. download it back from the FMR with ``references=all`` -- the full
   graph, which also exercises the SDMX-ML readers;
4. submit the downloaded structures and a tiny dataset to .Stat.

Only the download step's output is sent on to .Stat, so what reaches
.Stat is exactly what the FMR round-trip produced.

This is a runnable example -- it needs live, writable FMR and .Stat
instances -- not a CI test.

Run::

    export FMR_ENDPOINT="https://my.fmr/sdmx/v2"  # SDMX-REST v2 base
    export FMR_TOKEN="eyJ..."      # or FMR_USER + FMR_PASSWORD
    export DOTSTAT_TOKEN="eyJ..."  # a fresh .Stat bearer token
    poetry run python examples/fmr_to_stat.py

.Stat defaults target the SIS-CC public demo; override with the env
vars ``DOTSTAT_NSI``, ``DOTSTAT_TRANSFER`` and ``DOTSTAT_SPACE``.
"""

from __future__ import annotations

import os
from io import BytesIO

import pandas as pd

from pysdmx.api.fmr.maintenance import (
    RegistryMaintenanceClient,
    StructureAction,
)
from pysdmx.api.qb import (
    ApiVersion,
    RestService,
    StructureDetail,
    StructureFormat,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.api.stat import StatUploader
from pysdmx.io import read_sdmx
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
FMR_ENDPOINT = os.environ.get("FMR_ENDPOINT", "https://my.fmr/sdmx/v2")
NSI = os.environ.get("DOTSTAT_NSI", "https://nsi-demo-stable.siscc.org")
TRANSFER = os.environ.get(
    "DOTSTAT_TRANSFER", "https://transfer-demo.siscc.org/3"
)
SPACE = os.environ.get("DOTSTAT_SPACE", "staging:SIS-CC-stable")

CS_ID = "CS_PYSDMX_FMR"
DSD_ID = "DSD_PYSDMX_FMR"
DF_ID = "DF_PYSDMX_FMR"
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
        name="pysdmx FMR concepts",
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
        name="pysdmx FMR DSD",
        components=components,
    )
    df = Dataflow(
        id=DF_ID,
        agency=AGENCY,
        version="1.0",
        name="pysdmx FMR dataflow",
        structure=dsd,
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


def upload_to_fmr(msg: Message) -> None:
    """Upload the seed structures to the FMR (bearer or basic auth)."""
    client = RegistryMaintenanceClient(
        FMR_ENDPOINT,
        user=os.environ.get("FMR_USER"),
        password=os.environ.get("FMR_PASSWORD"),
        access_token=os.environ.get("FMR_TOKEN"),
    )
    client.put_structures(
        list(msg.structures or []), action=StructureAction.Replace
    )


def download_from_fmr() -> Message:
    """Download the dataflow graph from the FMR with references=all."""
    svc = RestService(
        FMR_ENDPOINT,
        ApiVersion.V2_0_0,
        structure_format=StructureFormat.SDMX_ML_2_1,
        token=os.environ.get("FMR_TOKEN"),
    )
    query = StructureQuery(
        StructureType.DATAFLOW,
        AGENCY,
        DF_ID,
        "1.0",
        detail=StructureDetail.FULL,
        references=StructureReference.ALL,
    )
    raw = svc.structure(query)
    return read_sdmx(BytesIO(raw), validate=False)


def main() -> None:
    """Run the FMR upload -> download -> .Stat submission pipeline."""
    if not os.environ.get("DOTSTAT_TOKEN"):
        raise SystemExit("Set DOTSTAT_TOKEN to a fresh .Stat bearer token.")

    seed = build_structure()

    print("1/4 upload seed structures to FMR ->", FMR_ENDPOINT)
    upload_to_fmr(seed)

    print("2/4 download the graph back from FMR (references=all)")
    graph = download_from_fmr()
    structures = list(graph.structures or [])
    print("  downloaded:", [s.short_urn for s in structures])

    print("3/4 submit the downloaded structures to .Stat")
    uploader = StatUploader(
        NSI, TRANSFER, dataspace=SPACE, token=os.environ["DOTSTAT_TOKEN"]
    )
    result = uploader.submit_structure(structures)
    print("  success:", result.success, "|", "; ".join(result.messages))

    print("4/4 upload data and poll to completion")
    imported = uploader.submit_data(build_dataset(seed))
    final = uploader.submission_status(imported.request_id, wait=True)
    print("  ->", final.execution_status, "/", final.outcome)


if __name__ == "__main__":
    main()
