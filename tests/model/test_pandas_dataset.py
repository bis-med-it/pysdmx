import pandas as pd

from pysdmx.model import Schema
from pysdmx.model.dataset import PandasDataset


def test_short_urn_using_full_urn():
    urn = (
        "urn:sdmx:org.sdmx.infomodel.datastructure."
        "DataStructure=BIS:BIS_DER(1.0)"
    )
    dataset = PandasDataset(
        data=pd.DataFrame(),
        structure=urn,
    )

    short_urn = dataset.short_urn
    structure_ref, unique_id = short_urn.split("=", maxsplit=1)
    assert structure_ref == "DataStructure"
    assert unique_id == "BIS:BIS_DER(1.0)"


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
