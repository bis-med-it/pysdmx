import pandas as pd
import pytest

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.model import Schema, Component, Role, Concept, Components


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


def test_structural_validation():
    dataset = PandasDataset(
        data=pd.DataFrame(
            {
                "DIM1": [1, 2, 3],
                "ATT1": ["A", "B", "C"],
                "ATT2": [7, 8, 9],
                "M1": [10, 11, 12],
            }
        ),
        structure=Schema(
            context="datastructure",
            agency="BIS",
            id="BIS_DER",
            version="1.0",
            components=Components(
                [
                    Component(
                        id="DIM1",
                        role=Role.DIMENSION,
                        concept=Concept(id="DIM1"),
                        required=True,
                    ),
                    Component(
                        id="ATT1",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT1"),
                        required=False,
                        attachment_level="D",
                    ),
                    Component(
                        id="ATT2",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT2"),
                        required=False,
                        attachment_level="O",
                    ),
                    Component(
                        id="M1",
                        role=Role.MEASURE,
                        concept=Concept(id="M1"),
                        required=True,
                    ),
                ]
            ),
        ),
    )
    dataset.writing_validation()


def test_invalid_data_columns():
    dataset = PandasDataset(
        data=pd.DataFrame(
            {"DIM1": [1, 2, 3], "ATT1": ["A", "B", "C"], "ATT2": [7, 8, 9]}
        ),
        structure=Schema(
            context="datastructure",
            agency="BIS",
            id="BIS_DER",
            version="1.0",
            components=Components(
                [
                    Component(
                        id="DIM1",
                        role=Role.DIMENSION,
                        concept=Concept(id="DIM1"),
                        required=True,
                    ),
                    Component(
                        id="ATT1",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT1"),
                        required=False,
                        attachment_level="D",
                    ),
                    Component(
                        id="ATT2",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT2"),
                        required=False,
                        attachment_level="O",
                    ),
                    Component(
                        id="M1",
                        role=Role.MEASURE,
                        concept=Concept(id="M1"),
                        required=True,
                    ),
                ]
            ),
        ),
    )
    with pytest.raises(
        Invalid, match="Data columns length must match components length."
    ):
        dataset.writing_validation()


def test_invalid_structure():
    dataset = PandasDataset(
        data=pd.DataFrame(
            {
                "DIM1": [1, 2, 3],
                "ATT1": ["A", "B", "C"],
                "ATT2": [7, 8, 9],
                "M1": [10, 11, 12],
            }
        ),
        structure="urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=BIS:BIS_DER(1.0)",
    )
    with pytest.raises(Invalid, match="Dataset Structure is not a Schema."):
        dataset.writing_validation()


def test_no_dimensions():
    dataset = PandasDataset(
        data=pd.DataFrame(
            {"ATT1": ["A", "B", "C"], "ATT2": [7, 8, 9], "M1": [10, 11, 12]}
        ),
        structure=Schema(
            context="datastructure",
            agency="BIS",
            id="BIS_DER",
            version="1.0",
            components=Components(
                [
                    Component(
                        id="ATT1",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT1"),
                        required=False,
                        attachment_level="D",
                    ),
                    Component(
                        id="ATT2",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT2"),
                        required=False,
                        attachment_level="O",
                    ),
                    Component(
                        id="M1",
                        role=Role.MEASURE,
                        concept=Concept(id="M1"),
                        required=True,
                    ),
                ]
            ),
        ),
    )
    with pytest.raises(
        Invalid,
        match="The dataset structure must have at least one dimension.",
    ):
        dataset.writing_validation()


def test_no_measures():
    dataset = PandasDataset(
        data=pd.DataFrame(
            {"DIM1": [1, 2, 3], "ATT1": ["A", "B", "C"], "ATT2": [7, 8, 9]}
        ),
        structure=Schema(
            context="datastructure",
            agency="BIS",
            id="BIS_DER",
            version="1.0",
            components=Components(
                [
                    Component(
                        id="DIM1",
                        role=Role.DIMENSION,
                        concept=Concept(id="DIM1"),
                        required=True,
                    ),
                    Component(
                        id="ATT1",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT1"),
                        required=False,
                        attachment_level="D",
                    ),
                    Component(
                        id="ATT2",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT2"),
                        required=False,
                        attachment_level="O",
                    ),
                ]
            ),
        ),
    )
    with pytest.raises(
        Invalid, match="The dataset structure must have at least one measure."
    ):
        dataset.writing_validation()

def test_match_columns():
    dataset = PandasDataset(
        data=pd.DataFrame(
            {"DIMX": [1, 2, 3], "ATT1": ["A", "B", "C"],
             "ATT2": [7, 8, 9], "M1": [10, 11, 12]}
        ),
        structure=Schema(
            context="datastructure",
            agency="BIS",
            id="BIS_DER",
            version="1.0",
            components=Components(
                [
                    Component(
                        id="DIM1",
                        role=Role.DIMENSION,
                        concept=Concept(id="DIM1"),
                        required=True,
                    ),
                    Component(
                        id="ATT1",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT1"),
                        required=False,
                        attachment_level="D",
                    ),
                    Component(
                        id="ATT2",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT2"),
                        required=False,
                        attachment_level="O",
                    ),
                    Component(
                        id="M1",
                        role=Role.MEASURE,
                        concept=Concept(id="M1"),
                        required=True,
                    ),
                ]
            ),
        ),
    )
    with pytest.raises(
        Invalid, match="Data columns must match components."
    ):
        dataset.writing_validation()
