from typing import Any, Dict, List, Literal, Sequence, Tuple

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.model.concept import DataType
from pysdmx.model.dataflow import Component, Schema

NUMERIC_TYPES = {
    DataType.BIG_INTEGER,
    DataType.COUNT,
    DataType.DECIMAL,
    DataType.DOUBLE,
    DataType.FLOAT,
    DataType.INCREMENTAL,
    DataType.INTEGER,
    DataType.LONG,
    DataType.SHORT,
}


def format_labels(  # noqa: C901
    df: pd.DataFrame,
    labels: Literal["name", "both", "id"],
    components: Sequence[Component],
) -> None:
    """Writes the labels to the DataFrame.

    Args:
        df: The DataFrame to write the labels to.
        labels: The label type to write.
            if "id" the id of the data is written.
            if "name" the name of the data is written.
            if "both" a string id:name is written.
        components: The components of the data structure definition.

    """
    if labels == "name":
        for k in df.columns:
            for component in components:
                if component.id == k:
                    df.rename(
                        columns={k: component.concept.name},  # type: ignore[union-attr]
                        inplace=True,
                    )
    elif labels == "both":
        for k in df.columns:
            v = df[k]
            for component in components:
                if component.id == k:
                    df[f"{k}:{component.concept.name}"] = v.apply(  # type: ignore[union-attr]
                        lambda x: f"{x}:{x}"
                    )
                    df.drop(columns=[k], inplace=True)

    else:
        for k in df.columns:
            for component in components:
                if component.concept.name == k:  # type: ignore[union-attr]
                    df.rename(
                        columns={k: component.concept.id},
                        inplace=True,
                    )


def get_codes(
    dimension_code: str, structure: Schema, data: pd.DataFrame
) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
    """This function divides the components in Series and Obs."""
    groups = structure.groups
    group_codes = []
    obs_codes = [dimension_code, structure.components.measures[0].id]

    # Getting the series and obs codes
    series_codes = [
        d.id for d in structure.components.dimensions if d.id != dimension_code
    ]

    # Adding the attributes based on the attachment level
    for att in structure.components.attributes:
        matching_group = next(
            (
                group
                for group in groups or []
                if set(group.dimensions)
                == set(att.attachment_level.split(","))  # type: ignore[union-attr]
            ),
            None,
        )

        if (
            att.attachment_level != "D"
            and att.id in data.columns
            and groups is not None
            and matching_group
        ):
            group_codes.append(
                {
                    "group_id": matching_group.id,
                    "attribute": att.id,
                    "dimensions": matching_group.dimensions,
                }
            )
        elif att.attachment_level == "O" and att.id in data.columns:
            obs_codes.append(att.id)
        elif (
            att.attachment_level is not None
            and att.attachment_level != "D"
            and att.id in data.columns
        ):
            series_codes.append(att.id)

    return series_codes, obs_codes, group_codes


def fill_na_values(data: pd.DataFrame, structure: Any) -> pd.DataFrame:
    """Fills missing values in the DataFrame based on the component type.

    Numeric components are filled with "NaN".
    Other components are filled with "#N/A".
    If the structure does not have components,
    all missing values are filled with "".

    Args:
        data: The DataFrame to fill.
        structure: The structure definition (Schema, Dataflow, etc.).

    Returns:
        The DataFrame with filled missing values.

    Raises:
        Invalid: If the structure does not have components.
    """
    if not hasattr(structure, "components"):
        raise Invalid(
            "Structure must have components defined. "
            "Cannot write data without a proper Schema."
        )

    for component in structure.components:
        if component.id in data.columns:
            if component.dtype in NUMERIC_TYPES:
                data[component.id] = (
                    data[component.id].astype(object).fillna("NaN")
                )
            else:
                data[component.id] = (
                    data[component.id].astype(object).fillna("#N/A")
                )

    return data
