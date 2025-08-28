from typing import Literal, Sequence

import pandas as pd

from pysdmx.model.dataflow import Component


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
