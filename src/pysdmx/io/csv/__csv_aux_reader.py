from pysdmx.errors import Invalid
import pandas as pd

from pysdmx.io.pd import PandasDataset
from pysdmx.model.dataset import ActionType

ACTION_SDMX_CSV_MAPPER_READING = {
    "A": ActionType.Append,
    "D": ActionType.Delete,
    "R": ActionType.Replace,
    "I": ActionType.Information,
}


def __generate_dataset_from_sdmx_csv(data: pd.DataFrame) -> PandasDataset:
    if "DATAFLOW" in data.columns:
        # For SDMX-CSV version 1, use 'DATAFLOW' column as the structure id
        structure_id = data["DATAFLOW"].iloc[0]
        # Drop 'DATAFLOW' column from DataFrame
        df_csv = data.drop(["DATAFLOW"], axis=1)
        urn = f"Dataflow={structure_id}"

        # Return a Dataset object with the extracted information
        return PandasDataset(
            structure=urn,
            data=df_csv,
        )
    elif {"STRUCTURE", "STRUCTURE_ID"}.issubset(data.columns):
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
                        "Check the docs for the proper values on ACTION column.",
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
        # For SDMX-CSV version 2, use 'STRUCTURE_ID'
        # column as the structure id and 'STRUCTURE' as the structure type
        structure_id = data["STRUCTURE_ID"].iloc[0]
        structure_type = data["STRUCTURE"].iloc[0]
        # Drop 'STRUCTURE' and 'STRUCTURE_ID' columns from DataFrame
        df_csv = data.drop(["STRUCTURE", "STRUCTURE_ID"], axis=1)

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

        # Return a Dataset object with the extracted information
        return PandasDataset(
            structure=urn,
            data=df_csv,
            action=action,
        )
    else:
        raise Invalid(
            "Invalid SDMX-CSV file",
            "Invalid SDMX-CSV file. "
            "Check the docs for the proper structure on content.",
        )