import contextlib
import importlib.util
import os
from pathlib import Path
from types import ModuleType

import pytest

from pysdmx.api.stat import StatConnector, StatUploader
from pysdmx.errors import Invalid, NotFound

pytestmark = pytest.mark.skipif(
    not os.environ.get("DOTSTAT_TOKEN"),
    reason="live .Stat round trip; set DOTSTAT_TOKEN to run",
)

_EXAMPLE = (
    Path(__file__).resolve().parents[3] / "examples" / "stat_upload_e2e.py"
)

_EXPECTED = {
    ("ES", "2024"): 1.0,
    ("FR", "2024"): 2.0,
    ("DE", "2024"): 3.0,
}


def _load_example() -> ModuleType:
    spec = importlib.util.spec_from_file_location("stat_e2e_example", _EXAMPLE)
    assert spec
    assert spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_stat_round_trip():
    """Live upload -> download -> delete round trip (agency MD)."""
    ex = _load_example()
    token = os.environ["DOTSTAT_TOKEN"]
    up = StatUploader(ex.NSI, ex.TRANSFER, dataspace=ex.SPACE, token=token)
    conn = StatConnector(f"{ex.NSI}/rest/v2")  # reads are anonymous
    msg = ex.build_structure()
    ds = ex.build_dataset(msg)
    ag, df, dsd, cs = ex.AGENCY, ex.DF_ID, ex.DSD_ID, ex.CS_ID

    # Create the structure and load the data.
    assert up.submit_structure(msg.structures).success
    imported = up.submit_data(ds)
    final = up.submission_status(imported.request_id, wait=True)
    assert final.outcome == "Success"

    # Download it back and confirm it matches what was uploaded.
    data = conn.fetch_dataset(ag, df, "1.0").data
    downloaded = {
        (str(r.REF_AREA), str(r.TIME_PERIOD)): float(r.OBS_VALUE)
        for r in data.itertuples()
    }
    assert downloaded == _EXPECTED

    # Tear down: data, then constraint, then dataflow -> DSD -> CS.
    up.submission_status(up.delete_data(ds).request_id, wait=True)
    with contextlib.suppress(NotFound):
        up.delete_structure(f"DataConstraint={ag}:CR_A_{df}(1.0)")
    up.delete_structure(
        [
            f"Dataflow={ag}:{df}(1.0)",
            f"DataStructure={ag}:{dsd}(1.0)",
            f"ConceptScheme={ag}:{cs}(1.0)",
        ]
    )
    with pytest.raises((NotFound, Invalid)):
        conn.fetch_structure(ag, df, "1.0")
