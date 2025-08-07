from typing import Literal

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.model.dataflow import Schema


def write_labels(
    df: PandasDataset,
    labels: Literal["name", "both"],
) -> None:
    """Writes the labels to the DataFrame.

    Args:
        df: The DataFrame to write the labels to.
        labels: The label type to write.
            if "name" the name of the data is written.
            if "both" a string id:name is written.
    """
    schema = df.structure
    if not isinstance(schema, Schema):
        raise Invalid(
            "Labels can only be written if the dataset has a Schema."
        )
    components_data = schema.components.data

    if labels == "name":
        for k in df.data.columns:
            for component in components_data:
                if component.id == k:
                    df.data.rename(
                        columns={k: component.concept.name},  # type: ignore[union-attr]
                        inplace=True,
                    )
    elif labels == "both":
        for k in df.data.columns:
            v = df.data[k]
            for component in components_data:
                if component.id == k:
                    df.data[f"{k}:{component.concept.name}"] = v.apply(  # type: ignore[union-attr]
                        lambda x: f"{x}:{x}"
                    )
                    df.data.drop(columns=[k], inplace=True)
