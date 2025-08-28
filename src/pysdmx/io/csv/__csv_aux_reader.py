import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.model.dataset import ActionType

ACTION_SDMX_CSV_MAPPER_READING = {
    "A": ActionType.Append,
    "D": ActionType.Delete,
    "R": ActionType.Replace,
    "I": ActionType.Information,
    "M": ActionType.Merge,
}


def __generate_dataset_from_sdmx_csv(  # noqa: C901
    data: pd.DataFrame,
) -> PandasDataset:
    urn = ""
    df_csv = pd.DataFrame()
    action = None

    if {"STRUCTURE", "STRUCTURE_ID"}.issubset(data.columns):
        action = ActionType.Information
        if "ACTION" in data.columns:
            unique_values = list(data["ACTION"].unique())
            if len(unique_values) > 1 and "D" in unique_values:
                unique_values.remove("D")
                data = data[data["ACTION"] != "D"]
            if len(unique_values) == 1:  # If there is only one value, use it
                action_value = unique_values[0]
                if action_value not in ACTION_SDMX_CSV_MAPPER_READING:
                    raise Invalid(
                        "Invalid value on ACTION column",
                        "Invalid SDMX-CSV 2.0 file. "
                        "Check the docs for the proper values "
                        "on ACTION column.",
                    )
                action = ACTION_SDMX_CSV_MAPPER_READING[action_value]
                del data["ACTION"]  # Remove ACTION column from DataFrame
            else:
                raise Invalid(
                    "Invalid value on ACTION column",
                    "Invalid SDMX-CSV 2.0 file. "
                    "Cannot have more than one value on ACTION column, "
                    "or 2 if D is present",
                )
        # Remove columns that are not needed
        if "STRUCTURE_NAME" in data.columns:
            data = data.drop(columns=["STRUCTURE_NAME"])
        if "SERIES_KEYS" in data.columns:
            data = data.drop(columns=["SERIES_KEYS"])
        if "OBS_KEYS" in data.columns:
            data = data.drop(columns=["OBS_KEYS"])

        # For SDMX-CSV version 2, use 'STRUCTURE_ID'
        # column as the structure id and 'STRUCTURE' as the structure type
        structure_id = data["STRUCTURE_ID"].iloc[0]
        structure_type = data["STRUCTURE"].iloc[0]
        # Drop 'STRUCTURE' and 'STRUCTURE_ID' columns from DataFrame
        df_csv = data.drop(["STRUCTURE", "STRUCTURE_ID"], axis=1)
        if structure_id.count(":") == 2:
            structure_id = ":".join(structure_id.split(":")[:2])
        if structure_type == "DataStructure".lower():
            urn = f"DataStructure={structure_id}"
        elif structure_type == "Dataflow".lower():
            urn = f"Dataflow={structure_id}"
        elif structure_type == "dataprovision":
            urn = f"ProvisionAgreement={structure_id}"
        else:
            raise Invalid(
                "Invalid value on STRUCTURE column",
                "Invalid SDMX-CSV 2.0 file. "
                "Check the docs for the proper values on STRUCTURE column.",
            )
    else:
        # For SDMX-CSV version 1, use 'DATAFLOW' column as the structure id
        structure_id = data["DATAFLOW"].iloc[0]
        if structure_id.count(":") == 2:
            structure_id = ":".join(structure_id.split(":")[:2])
        # Drop 'DATAFLOW' column from DataFrame
        df_csv = data.drop(["DATAFLOW"], axis=1)

        urn = f"Dataflow={structure_id}"
    return PandasDataset(
        structure=urn,
        data=df_csv,
        action=action if action is not None else ActionType.Information,
    )
