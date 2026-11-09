import io
import sys
from typing import Iterable, Optional

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.model.dataset import ActionType

ACTION_SDMX_CSV_MAPPER_READING = {
    "A": ActionType.Append,
    "D": ActionType.Delete,
    "R": ActionType.Replace,
    "I": ActionType.Information,
}


class _TextChunks(io.TextIOBase):
    """A read-only text stream over chunks of text, for pandas.

    read(size) returns size characters unless the text ends, as a StringIO
    does, so pandas parses the text as it would from a StringIO. A chunk is
    not copied to be read: each read takes a slice of it.
    """

    def __init__(self, chunks: Iterable[str]) -> None:
        """Streams the given chunks."""
        super().__init__()
        self.__chunks = iter(chunks)
        self.__text = ""
        self.__position = 0

    @property
    def mode(self) -> str:
        """Returns "r": the stream is read as text."""
        return "r"

    def read(self, size: Optional[int] = -1) -> str:
        """Reads size characters, or the rest of the text."""
        size = sys.maxsize if size is None or size < 0 else size
        end = self.__position + size
        if end > len(self.__text):
            rest = self.__text[self.__position :]
            parts = [rest] if rest else []
            length = len(rest)
            while length < size:
                chunk = next(self.__chunks, None)
                if chunk is None:
                    break
                parts.append(chunk)
                length += len(chunk)
            self.__text = "".join(parts)
            self.__position = 0
            end = size
        text = self.__text[self.__position : end]
        self.__position = end
        return text


def read_csv_chunks(chunks: Iterable[str]) -> pd.DataFrame:
    """Reads SDMX-CSV text, given in chunks, into a DataFrame.

    pandas reads the text as it needs it, as from a file.

    Args:
        chunks: The text, in chunks.

    Returns:
        The DataFrame, with the types pandas infers.
    """
    return pd.read_csv(
        _TextChunks(chunks), keep_default_na=False, na_values=[]
    )


def __generate_dataset_from_sdmx_csv(  # noqa: C901
    data: pd.DataFrame,
    references_21: bool = False,
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
                if action_value == "M":
                    if not references_21:
                        raise Invalid(
                            "Invalid value on ACTION column",
                            "Value 'M' is only allowed for"
                            " SDMX-CSV 2.1 files.",
                        )
                    action = ActionType.Append
                elif action_value in ACTION_SDMX_CSV_MAPPER_READING:
                    action = ACTION_SDMX_CSV_MAPPER_READING[action_value]
                else:
                    raise Invalid(
                        "Invalid value on ACTION column",
                        "Invalid SDMX-CSV file. "
                        "Check the docs for the proper values "
                        "on ACTION column.",
                    )

                del data["ACTION"]  # Remove ACTION column from DataFrame
            else:
                raise Invalid(
                    "Invalid value on ACTION column",
                    "Invalid SDMX-CSV file. "
                    "Cannot have more than one value on ACTION column, "
                    "or 2 if D is present",
                )
        data = data.drop(columns=["SERIES_KEY", "OBS_KEY"], errors="ignore")

        # For SDMX-CSV version 2, use 'STRUCTURE_ID'
        # column as the structure id and 'STRUCTURE' as the structure type
        structure_id = data["STRUCTURE_ID"].iloc[0]
        # The specification writes the structure types in lowercase, but
        # other tools may use different casings, so match case-insensitively
        structure_type = data["STRUCTURE"].iloc[0].lower()
        # Drop 'STRUCTURE' and 'STRUCTURE_ID' columns from DataFrame
        df_csv = data.drop(["STRUCTURE", "STRUCTURE_ID"], axis=1)
        # Strip the label (name) from the structure id, if present. Labels
        # use a ': ' separator and codes never contain spaces.
        if structure_id.count(": ") == 1:
            structure_id = structure_id.split(": ")[0]
        if structure_type == "datastructure":
            urn = f"DataStructure={structure_id}"
        elif structure_type == "dataflow":
            urn = f"Dataflow={structure_id}"
        elif structure_type == "dataprovision":
            urn = f"ProvisionAgreement={structure_id}"
        else:
            raise Invalid(
                "Invalid value on STRUCTURE column",
                "Invalid SDMX-CSV file. "
                "Check the docs for the proper values on STRUCTURE column.",
            )
    else:
        # For SDMX-CSV version 1, use 'DATAFLOW' column as the structure id
        structure_id = data["DATAFLOW"].iloc[0]
        # Strip the label (name) from the structure id, if present. Labels
        # use a ': ' separator and codes never contain spaces.
        if structure_id.count(": ") == 1:
            structure_id = structure_id.split(": ")[0]
        # Drop 'DATAFLOW' column from DataFrame
        df_csv = data.drop(["DATAFLOW"], axis=1)

        urn = f"Dataflow={structure_id}"
    return PandasDataset(
        structure=urn,
        data=df_csv,
        action=action if action is not None else ActionType.Information,
    )
