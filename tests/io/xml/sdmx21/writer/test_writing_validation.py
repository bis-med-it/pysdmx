from pathlib import Path

import pandas as pd
import pytest

from pysdmx.errors import Invalid
from pysdmx.io import get_datasets, read_sdmx
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__write_data_aux import writing_validation
from pysdmx.io.xml.sdmx21.writer.structure import write
from pysdmx.io.xml.sdmx21.writer.structure_specific import (
    write as write_str_spec,
)
from pysdmx.model import (
    Component,
    Components,
    Concept,
    DataStructureDefinition,
    DataType,
    Role,
    Schema,
)


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


def test_data_write_nullable_nulltypes():
    # Local import on numpy to avoid possible problems with C extensions
    # on windows when using pysdmx
    import numpy as np

    from pysdmx.io.xml.sdmx21.writer.generic import write as write_gen

    # Create dataframe with various null types and data types
    data = pd.DataFrame(
        data={
            "DIM1": [1, 2, 3, 4],  # Required dimension (always has values)
            "MEASURE_REQ": [
                np.nan,
                1,
                None,
                pd.NA,
            ],  # Required numeric measure
            "MEASURE_OPT": [
                np.nan,
                2,
                None,
                pd.NA,
            ],  # Optional numeric measure
            "ATTR_REQ": [None, "value", np.nan, ""],  # Required string attr
            "ATTR_OPT": [None, "value", np.nan, ""],  # Optional string attr
        }
    )
    data["MEASURE_REQ"] = data["MEASURE_REQ"].astype("Int64")
    data["MEASURE_OPT"] = data["MEASURE_OPT"].astype("Int64")

    structure_schema = Schema(
        context="datastructure",
        agency="Short",
        id="Urn",
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
                    id="MEASURE_REQ",
                    role=Role.MEASURE,
                    concept=Concept(id="MEASURE_REQ"),
                    required=True,
                    local_dtype=DataType.INTEGER,
                ),
                Component(
                    id="MEASURE_OPT",
                    role=Role.MEASURE,
                    concept=Concept(id="MEASURE_OPT"),
                    required=False,
                    local_dtype=DataType.INTEGER,
                ),
                Component(
                    id="ATTR_REQ",
                    role=Role.ATTRIBUTE,
                    concept=Concept(id="ATTR_REQ"),
                    required=True,
                    attachment_level="O",
                ),
                Component(
                    id="ATTR_OPT",
                    role=Role.ATTRIBUTE,
                    concept=Concept(id="ATTR_OPT"),
                    required=False,
                    attachment_level="O",
                ),
            ]
        ),
    )

    # The backend is numpy_nullable by default,
    # this line should just make clear
    # that this is not pyarrow related
    data = data.convert_dtypes(dtype_backend="numpy_nullable")
    dataset = PandasDataset(data=data, structure=structure_schema)

    result = write_str_spec([dataset])
    datasets = get_datasets(result)
    assert len(datasets) == 1
    data = datasets[0].data

    # Required: null values (np.nan, None, pd.NA) written as "NaN"/"#N/A"
    # Optional: null values are skipped (read back as "")
    # Empty strings: written for required, skipped for optional
    assert data["MEASURE_REQ"].values.tolist() == ["NaN", "1", "NaN", "NaN"]
    assert data["MEASURE_OPT"].values.tolist() == ["", "2", "", ""]
    # String attributes: required null values written, optional skipped
    assert data["ATTR_REQ"].values.tolist() == [
        "#N/A",
        "value",
        "#N/A",
        "#N/A",
    ]
    # Optional: null values and empty strings are both skipped
    assert data["ATTR_OPT"].values.tolist() == ["", "value", "", ""]

    # GENERIC
    result_gen = write_gen([dataset])
    datasets_gen = get_datasets(result_gen)
    assert len(datasets_gen) == 1
    data_gen = datasets_gen[0].data

    # The generic writer represents single measure values as 'OBS_VALUE'
    # and does not include separate measure-named columns.
    assert "MEASURE_REQ" not in data_gen.columns
    assert "MEASURE_OPT" not in data_gen.columns
    assert (
        data_gen["OBS_VALUE"].values.tolist()
        == data["MEASURE_REQ"].values.tolist()
    )
    assert (
        data_gen["ATTR_REQ"].values.tolist()
        == data["ATTR_REQ"].values.tolist()
    )
    assert (
        data_gen["ATTR_OPT"].values.tolist()
        == data["ATTR_OPT"].values.tolist()
    )
