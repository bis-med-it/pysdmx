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


def test_missing_required_attribute_passes_validation():
    """Required attributes missing from data should not fail.

    SDMX structure-specific format supports partial updates.
    """
    dataset = PandasDataset(
        data=pd.DataFrame({"DIM1": [1, 2, 3], "M1": [10, 11, 12]}),
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
                        id="ATT_REQ",
                        role=Role.ATTRIBUTE,
                        concept=Concept(id="ATT_REQ"),
                        required=True,
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
    # Create dataframe with null values
    data = pd.DataFrame(
        data={
            "DIM1": ["X", "Y", "Z", "W"],
            "OBS_VALUE": [None, 1, None, pd.NA],
        }
    )
    data["OBS_VALUE"] = data["OBS_VALUE"].astype("Int64")
    schema = Schema(
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
                    id="OBS_VALUE",
                    role=Role.MEASURE,
                    concept=Concept(id="OBS_VALUE"),
                    required=True,
                    local_dtype=DataType.INTEGER,
                ),
            ]
        ),
    )
    dataset = PandasDataset(data=data, structure=schema)
    result = write_str_spec([dataset])
    datasets = get_datasets(result)
    assert len(datasets) == 1
    data = datasets[0].data
    assert data["OBS_VALUE"].values.tolist() == ["", "1", "", ""]


def test_data_write_csv_sentinel_values():
    """CSV sentinels: optional attrs omitted, required get sentinel."""
    from pysdmx.io.format import Format
    from pysdmx.io.writer import write_sdmx

    data = pd.DataFrame(
        data={
            "DIM1": ["A", "B"],
            "OBS_VALUE": ["#N/A", "42"],
            "ATTR1": ["NaN", "hello"],
        }
    )
    schema = Schema(
        context="datastructure",
        agency="TEST",
        id="TEST_DS",
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
                    id="OBS_VALUE",
                    role=Role.MEASURE,
                    concept=Concept(id="OBS_VALUE"),
                    required=True,
                ),
                Component(
                    id="ATTR1",
                    role=Role.ATTRIBUTE,
                    concept=Concept(id="ATTR1"),
                    required=False,
                    attachment_level="O",
                ),
            ]
        ),
    )
    dataset = PandasDataset(data=data, structure=schema)

    # Test structure-specific writer (SDMX-ML 2.1)
    result_ss = write_sdmx([dataset], sdmx_format=Format.DATA_SDMX_ML_2_1_STR)
    # Sentinel values from CSV are cleaned out
    assert "#N/A" not in result_ss
    assert 'ATTR1="NaN"' not in result_ss
    # Valid values are preserved
    assert 'OBS_VALUE="42"' in result_ss
    assert 'ATTR1="hello"' in result_ss

    # Test generic writer (SDMX-ML 2.1)
    result_gen = write_sdmx([dataset], sdmx_format=Format.DATA_SDMX_ML_2_1_GEN)
    # Sentinel values from CSV are cleaned out
    assert "#N/A" not in result_gen
    assert 'value="NaN"' not in result_gen
    # Valid values are preserved
    assert '<gen:ObsValue value="42"/>' in result_gen
    assert '<gen:Value id="ATTR1" value="hello"/>' in result_gen


def test_data_write_csv_sentinel_empty_obs_value():
    """Empty obs value omitted from generic XML output."""
    from pysdmx.io.format import Format
    from pysdmx.io.writer import write_sdmx

    data = pd.DataFrame(
        data={
            "DIM1": ["A", "A", "A"],
            "DIM2": ["", "X", "Y"],
            "OBS_VALUE": ["", "", "42"],
            "S_ATT": ["s1", "s1", "s1"],
        }
    )
    schema = Schema(
        context="datastructure",
        agency="TEST",
        id="TEST_DS",
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
                    id="DIM2",
                    role=Role.DIMENSION,
                    concept=Concept(id="DIM2"),
                    required=True,
                ),
                Component(
                    id="OBS_VALUE",
                    role=Role.MEASURE,
                    concept=Concept(id="OBS_VALUE"),
                    required=False,
                ),
                Component(
                    id="S_ATT",
                    role=Role.ATTRIBUTE,
                    concept=Concept(id="S_ATT"),
                    required=False,
                    attachment_level="D",
                ),
            ]
        ),
    )
    dataset = PandasDataset(data=data, structure=schema)

    # AllDimensions mode — covers empty obs value skip
    result = write_sdmx([dataset], sdmx_format=Format.DATA_SDMX_ML_2_1_GEN)
    assert '<gen:ObsValue value="42"/>' in result

    # Series mode — covers empty obs value skip
    dim_at_obs = {dataset.structure.short_urn: "DIM2"}
    result_ser = write_sdmx(
        [dataset],
        sdmx_format=Format.DATA_SDMX_ML_2_1_GEN,
        dimension_at_observation=dim_at_obs,
    )
    assert '<gen:ObsValue value="42"/>' in result_ser
