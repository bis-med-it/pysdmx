from pathlib import Path

import pandas as pd
import pytest

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__write_data_aux import writing_validation
from pysdmx.io.xml.sdmx21.writer.structure import write
from pysdmx.model import Component, Components, Concept, Role, Schema, DataStructureDefinition

@pytest.fixture
def samples_folder():
    return Path(__file__).parent / "samples"

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
    writing_validation(dataset)


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
                        required=True,
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
    with pytest.raises(Invalid):
        writing_validation(dataset)


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
        structure="urn:sdmx:org.sdmx.infomodel.datastructure."
        "DataStructure=BIS:BIS_DER(1.0)",
    )
    with pytest.raises(Invalid, match="Dataset Structure is not a Schema."):
        writing_validation(dataset)


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
        writing_validation(dataset)


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
        writing_validation(dataset)


def test_match_columns():
    dataset = PandasDataset(
        data=pd.DataFrame(
            {
                "DIMX": [1, 2, 3],
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
    with pytest.raises(Invalid, match="Data columns must match components."):
        writing_validation(dataset)

def test_attribute_relationship_roundtrip(samples_folder):
    # Read the SDMX-ML file with None attribute relationships
    file_path = samples_folder / "datastructure_att_rel_21.xml"
    message = read_sdmx(file_path.read_text(), validate=True)

    # Check we have it set to "D" (Dataflow)
    structure_one: DataStructureDefinition = message.structures[0]
    attribute_one = structure_one.components.attributes[0]
    assert attribute_one.attachment_level == "D"

    # Write it back to SDMX-ML format
    result = write(
        structures=message.structures,
        prettyprint=True,
    )
    # Check if a str:None is present in the output
    assert "<str:None/>" in result

    # Read the written content back
    read_message = read_sdmx(result, validate=True)

    structure_two: DataStructureDefinition = read_message.structures[0]
    attribute_two = structure_two.components.attributes[0]
    # Check if the attribute relationships are Dataflow
    assert attribute_two.attachment_level == "D"

    assert attribute_one == attribute_two
