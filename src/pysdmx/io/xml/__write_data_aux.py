from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__write_aux import ALL_DIM
from pysdmx.model import Role, Schema


def check_content_dataset(content: Sequence[PandasDataset]) -> None:
    """Checks if the Message content is a dataset."""
    if not all(isinstance(dataset, PandasDataset) for dataset in content):
        raise Invalid("Message Content must only contain a Dataset sequence.")


def check_dimension_at_observation(
    datasets: Dict[str, PandasDataset],
    dimension_at_observation: Optional[Dict[str, str]],
) -> Dict[str, str]:
    """This function checks if the dimension at observation is valid."""
    # If dimension_at_observation is None, set it to ALL_DIM
    if dimension_at_observation is None:
        dimension_at_observation = dict.fromkeys(datasets, ALL_DIM)
        return dimension_at_observation

    # Check the datasets and their dimensions are present
    for key, value in dimension_at_observation.items():
        if key not in datasets:
            raise Invalid(f"Dataset {key} not found in Message content.")
        writing_validation(datasets[key])
        dataset = datasets[key]
        components = dataset.structure.components  # type: ignore[union-attr]

        dimension_codes = [dim.id for dim in components.dimensions]
        if value not in dimension_codes:
            raise Invalid(
                f"Dimension at observation {value} "
                f"not found in dataset {key}."
            )
    # Add the missing datasets on mapping with ALL_DIM
    for key in datasets:
        if key not in dimension_at_observation:
            dimension_at_observation[key] = ALL_DIM
    return dimension_at_observation


def writing_validation(dataset: PandasDataset) -> None:
    """Structural validation of the dataset."""
    if not isinstance(dataset.structure, Schema):
        raise Invalid(
            "Dataset Structure is not a Schema. Cannot perform operation."
        )
    required_components = [
        comp.id
        for comp in dataset.structure.components
        if comp.role in (Role.DIMENSION, Role.MEASURE)
    ]
    for att in dataset.structure.components.attributes:
        if (
            att.required
            and att.attachment_level is not None
            and att.attachment_level != "D"
        ):
            required_components.append(att.id)
    non_required = [
        comp.id
        for comp in dataset.structure.components
        if comp.id not in required_components
    ]
    # Columns match components
    columns = dataset.data.columns
    all_components = required_components + non_required
    difference = [col for col in columns if col not in all_components]

    for comp in required_components:
        difference.append(comp) if comp not in columns else None
    if difference:
        raise Invalid(
            f"Data columns must match components. "
            f"Difference: {', '.join(difference)}"
        )
    # Check if the dataset has at least one dimension and one measure
    if not dataset.structure.components.dimensions:
        raise Invalid(
            "The dataset structure must have at least one dimension."
        )
    if not dataset.structure.components.measures:
        raise Invalid("The dataset structure must have at least one measure.")


def get_codes(
    dimension_code: str, structure: Schema, data: pd.DataFrame
) -> Tuple[List[str], List[str]]:
    """This function divides the components in Series and Obs."""
    series_codes = []
    obs_codes = [dimension_code, structure.components.measures[0].id]

    # Getting the series and obs codes
    for dim in structure.components.dimensions:
        if dim.id != dimension_code:
            series_codes.append(dim.id)

    # Adding the attributes based on the attachment level
    for att in structure.components.attributes:
        if att.attachment_level == "O" and att.id in data.columns:
            obs_codes.append(att.id)
        elif (
            att.attachment_level is not None
            and att.attachment_level != "D"
            and att.id in data.columns
        ):
            series_codes.append(att.id)

    return series_codes, obs_codes
