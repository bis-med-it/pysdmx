from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.model.dataflow import Schema


def _validate_schema_exists(dataset: PandasDataset) -> Schema:
    """Validates that the dataset has a Schema defined.

    Args:
        dataset: The dataset to validate.

    Returns:
        The `Schema` from the dataset.

    Raises:
        Invalid: If the structure is not a `Schema`.
    """
    if not isinstance(dataset.structure, Schema):
        raise Invalid(
            "Dataset Structure is not a Schema. Cannot perform operation."
        )
    return dataset.structure
