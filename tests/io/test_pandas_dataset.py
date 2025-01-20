import pandas as pd

from pysdmx.io.pd import PandasDataset
from pysdmx.model import Schema


def test_short_urn_schema():
    dataset = PandasDataset(
        data=pd.DataFrame(),
        structure=Schema(
            context="datastructure",
            agency="BIS",
            id="BIS_DER",
            version="1.0",
            components=[],
        ),
    )

    short_urn = dataset.short_urn
    structure_ref, unique_id = short_urn.split("=", maxsplit=1)
    assert structure_ref == "datastructure"
    assert unique_id == "BIS:BIS_DER(1.0)"
