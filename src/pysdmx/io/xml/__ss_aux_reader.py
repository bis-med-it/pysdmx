"""SDMX XML StructureSpecificData reader aux module."""

from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
from lxml import etree

from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__data_stream import Columns, Names, read_data
from pysdmx.io.xml.__tokens import EXCLUDED_ATTRIBUTES
from pysdmx.model.dataset import ActionType

Row = Dict[str, Optional[str]]


def _merge_groups(
    df: pd.DataFrame, group_dfs: List[pd.DataFrame]
) -> pd.DataFrame:
    """Merges the attributes of the groups into the series."""
    original_columns = df.columns.tolist()
    for group_df in group_dfs:
        # Find non-NaN columns in this group
        non_nan_cols = [
            col for col in group_df.columns if not group_df[col].isna().all()
        ]

        # Merge keys are intersection of original and non-NaN cols
        merge_cols = list(
            set(original_columns).intersection(set(non_nan_cols))
        )

        group_df = group_df.drop_duplicates(merge_cols, keep="first")
        df = pd.merge(
            df,
            group_df,
            on=merge_cols,
            how="left",
            suffixes=("", "_drop"),
        )
        for col in list(df.columns):
            if col.endswith("_drop"):
                original = col[:-5]
                df[original] = df[original].fillna(df[col])
                df.drop(col, axis=1, inplace=True)
    return df


def _group_frame(group: Row) -> pd.DataFrame:
    """Returns the single-row frame of a group, without the :type columns."""
    columns = Columns(None)
    columns.add({k: v for k, v in group.items() if ":type" not in k})
    return columns.frame()


class _StructureSpecificDataSet:
    """Reads the elements of a StructureSpecific DataSet."""

    def __init__(
        self,
        attributes: Dict[str, str],
        structure: Dict[str, Any],
        names: Names,
    ) -> None:
        self.__attributes = attributes
        self.__structure = structure
        self.__names = names
        self.__series = Columns(None)
        self.__observations = Columns("")
        self.__groups: List[Row] = []
        self.__has_series = False
        self.__keys: Row = {}
        self.__series_has_obs = False

    def series_start(self, series: etree._Element) -> None:
        self.__has_series = True
        self.__keys = dict(self.__names.attributes(series))
        self.__series_has_obs = False

    def series_end(self, series: etree._Element) -> None:
        if not self.__series_has_obs:
            self.__series.add(self.__keys)

    def obs(self, obs: etree._Element, in_series: bool) -> None:
        if in_series:
            self.__series_has_obs = True
            self.__series.add({**self.__keys, **self.__names.attributes(obs)})
        else:
            self.__observations.add(dict(self.__names.attributes(obs)))

    def group(self, group: etree._Element) -> None:
        self.__groups.append(dict(self.__names.attributes(group)))

    def finish(self, dataset: etree._Element) -> PandasDataset:
        if self.__has_series:
            # Structure Specific Series
            df = self.__series.frame()
            if self.__groups:
                group_dfs = [_group_frame(group) for group in self.__groups]
                df = _merge_groups(df, group_dfs)
        else:
            # Structure Specific All dimensions
            df = self.__observations.frame()
        attached_attributes = {
            k: v
            for k, v in self.__attributes.items()
            if k not in EXCLUDED_ATTRIBUTES
        }
        action = ActionType(self.__attributes.get("action", "Information"))
        structure_type = self.__structure["structure_type"]
        urn = f"{structure_type}={self.__structure['unique_id']}"
        return PandasDataset(
            structure=urn,
            attributes=attached_attributes,
            data=df,
            action=action,
        )


def read_structure_specific(
    chunks: Iterable[str], validate: bool, messages: Tuple[str, ...]
) -> Tuple[Optional[Dict[str, Any]], List[PandasDataset]]:
    """Reads an SDMX-ML StructureSpecific data message in a single pass.

    Args:
        chunks: The text of the message, in chunks.
        validate: If True, the XML data will be validated against the XSD.
        messages: The names of the expected message elements.

    Returns:
        The Header of the message, as xmltodict parses it, and the
        datasets.

    Raises:
        Invalid: If the message is not valid SDMX-ML StructureSpecific
            data.
    """
    return read_data(
        chunks,
        validate,
        messages,
        "This SDMX document is not an SDMX-ML StructureSpecificData.",
        _StructureSpecificDataSet,
    )
