"""Pandas SDMX Dataset."""

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.model import Schema
from pysdmx.model.dataset import Dataset


class PandasDataset(Dataset, frozen=False, kw_only=True):
    """Class related to Dataset, using Pandas Dataframe.

    It is based on SDMX Dataset and has Pandas Dataframe compatibility to
    withhold data.

    Args:
        attributes: Attributes at dataset level-
        data: Dataframe.
        structure:
        URN or Schema related to this Dataset
        (DSD, Dataflow, ProvisionAgreement)
    """

    data: pd.DataFrame

    def writing_validation(self) -> None:
        """Structural validation of the dataset."""
        if not isinstance(self.structure, Schema):
            raise Invalid(
                "Dataset Structure is not a Schema. "
                "Cannot perform operation."
            )
        if len(self.data.columns) != len(self.structure.components):
            raise Invalid("Data columns length must match components length.")
        columns = set(self.data.columns)
        components = {comp.id for comp in self.structure.components}
        if columns != components:
            difference = columns.symmetric_difference(components)
            raise Invalid(
                f"Data columns must match components. "
                f"Difference: {', '.join(difference)}"
            )

        if not self.structure.components.dimensions:
            raise Invalid(
                "The dataset structure must have at least one dimension."
            )
        if not self.structure.components.measures:
            raise Invalid(
                "The dataset structure must have at least one measure."
            )
