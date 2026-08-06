from collections import Counter
from typing import Any, Dict, List, Literal, Sequence, Tuple

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.model.dataflow import Component, Schema

_LABELS_NAME_FIXED_COLUMNS = frozenset(
    (
        "STRUCTURE",
        "STRUCTURE_ID",
        "STRUCTURE_NAME",
        "ACTION",
        "SERIES_KEY",
        "OBS_KEY",
        "DATAFLOW",
    )
)


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
            if "name" a column with the localised name of the component
              is inserted right after each component column.
            if "both" a string id: name is written.
        components: The components of the data structure definition.

    Raises:
        Invalid: If "name" is used and two columns would end up with
            the same name (e.g. a concept name equal to a component id,
            or two concepts sharing the same name).
    """
    if labels == "name":
        names = {
            c.id: c.concept.name  # type: ignore[union-attr]
            for c in components
        }
        final_columns: List[Any] = []
        for col in df.columns:
            final_columns.append(col)
            if col in names:
                final_columns.append(names[col])
        duplicated = sorted(
            str(col)
            for col, count in Counter(final_columns).items()
            if count > 1
        )
        if duplicated:
            raise Invalid(
                "Duplicated column names",
                "Writing with labels='name' would produce more than one "
                f"column with the same name ({', '.join(duplicated)}). "
                "Concept names must be unique and different from the "
                "component ids.",
            )
        # Insert from the right so pending positions are not shifted.
        for position in range(len(df.columns) - 1, -1, -1):
            col = df.columns[position]
            if col in names:
                df.insert(position + 1, names[col], df[col])
    elif labels == "both":
        for k in df.columns:
            v = df[k]
            for component in components:
                if component.id == k:
                    df[f"{k}: {component.concept.name}"] = v.apply(  # type: ignore[union-attr]
                        lambda x: f"{x}: {x}"
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


def drop_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Drops the SDMX-CSV labels from a DataFrame, keeping only the ids.

    Both labelled SDMX-CSV representations are supported:

    - labels=both: labelled columns are detected by a ': '
      (colon-space) separator in their header. Headers and cells are
      reduced to the id part before the separator. Ids never contain
      spaces, so values with a bare ':' (e.g. full datetimes) are
      preserved.
    - labels=name (SDMX-CSV 2.x): detected by the presence of the
      STRUCTURE_NAME column. Each component column is directly followed
      by a column with its localised name; those name columns and
      STRUCTURE_NAME are dropped, keeping only the id columns.

    A DataFrame without labels is returned unchanged.

    Args:
        df: The DataFrame to drop the labels from.

    Returns:
        The DataFrame with the labels removed.

    Raises:
        Invalid: If the labels=name format is detected and the number
            of component columns is odd, meaning the id/name column
            pairing is broken.
    """
    if any(": " in col for col in df.columns):
        for x in [col for col in df.columns if ": " in col]:
            df[x.split(": ")[0]] = df[x].map(
                lambda x: x.split(": ", 2)[0], na_action="ignore"
            )
            del df[x]
    elif "STRUCTURE_NAME" in df.columns:
        component_columns = [
            c for c in df.columns if c not in _LABELS_NAME_FIXED_COLUMNS
        ]
        if len(component_columns) % 2 != 0:
            raise Invalid(
                "Invalid SDMX-CSV file with labels=name",
                "Expected an id column followed by a name column per "
                "component, but found an odd number of component "
                "columns.",
            )
        df = df.drop(columns=["STRUCTURE_NAME", *component_columns[1::2]])
    return df


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
