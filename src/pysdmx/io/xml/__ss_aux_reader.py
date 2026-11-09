"""SDMX XML StructureSpecificData reader aux module."""

from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
import pyarrow as pa
from lxml import etree

from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__data_stream import Columns, Names, read_data
from pysdmx.io.xml.__tokens import ATTS, EXCLUDED_ATTRIBUTES
from pysdmx.model.dataset import ActionType

Row = Dict[str, Optional[str]]
Batch = Dict[Tuple[Optional[str], ...], Row]


def _batches(
    groups: List[Row], columns: List[str]
) -> Dict[Tuple[str, ...], Batch]:
    """Splits the groups into batches that can be merged at once.

    The key columns of a group are its columns that the data have, and
    its other columns are its attributes. A batch has the groups with the
    same key columns, as one row per key: the values of the key columns,
    and each attribute from the first of these groups that has it. The
    batches follow the order in which their key columns first appear. A
    group without key columns matches no row, so it is in no batch.
    """
    batches: Dict[Tuple[str, ...], Batch] = {}
    for group in groups:
        keys = tuple(column for column in columns if column in group)
        if not keys:
            continue
        values = tuple(group[key] for key in keys)
        row = batches.setdefault(keys, {}).setdefault(values, {})
        for name, value in group.items():
            row.setdefault(name, value)
    return batches


def _merge_groups(df: pd.DataFrame, groups: List[Row]) -> pd.DataFrame:
    """Merges the attributes of the groups into the rows of their key.

    A group has the values of a Group, or of an Atts with a key: those of
    its key columns, which the data have, and those of its attributes.
    The batches of groups are merged in their order, and a row keeps the
    first value it gets for an attribute. A group without key columns
    matches no row. The attributes follow the columns of the data, in the
    order they first appear in the groups.

    Args:
        df: The rows of the series, or the observations.
        groups: The values of each group, in the order they were read.

    Returns:
        The rows, with the attributes of the groups.
    """
    columns = df.columns.tolist()
    for keys, rows in _batches(groups, columns).items():
        frame = Columns(None)
        for row in rows.values():
            frame.add(row)
        batch = frame.frame()
        # A row keeps the attributes that an earlier batch has set
        filled = [
            name
            for name in batch.columns
            if name in df.columns and name not in keys
        ]
        df = pd.merge(
            df, batch, on=list(keys), how="left", suffixes=("", "_drop")
        )
        for name in filled:
            df[name] = df[name].fillna(df.pop(f"{name}_drop"))
    data = set(columns)
    attributes = dict.fromkeys(
        name for group in groups for name in group if name not in data
    )
    # Attributes set only by groups without key columns
    nulls = {
        name: pd.arrays.ArrowExtensionArray(pa.nulls(len(df), pa.string()))
        for name in attributes
        if name not in df.columns
    }
    return df.assign(**nulls)[columns + list(attributes)]


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
        self.__groups.append(
            {
                name: value
                for name, value in self.__names.attributes(group).items()
                if ":type" not in name
            }
        )

    def finish(self, dataset: etree._Element) -> PandasDataset:
        if self.__has_series:
            # Structure Specific Series
            df = self.__series.frame()
        else:
            # Structure Specific All dimensions
            df = self.__observations.frame()
        data_set_atts, atts = self.__atts(dataset, df.columns)
        # The Atts with a key are merged after the Groups
        groups = self.__groups + atts
        if groups:
            df = _merge_groups(df, groups)
        attributes = {**self.__attributes, **data_set_atts}
        attached_attributes = {
            k: v for k, v in attributes.items() if k not in EXCLUDED_ATTRIBUTES
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

    def __atts(
        self, dataset: etree._Element, columns: Iterable[str]
    ) -> Tuple[Dict[str, str], List[Row]]:
        """Returns the attributes given in Atts elements.

        In SDMX-ML 3.x, an Atts without a key gives data set attributes.
        An Atts with a column of the data has a key, and its attributes go
        to the rows of that key, as those of a Group.

        Returns:
            The data set attributes, and the values of the Atts with a key.
        """
        keys = set(columns)
        attributes: Dict[str, str] = {}
        atts: List[Row] = []
        for child in dataset:
            if self.__names[child.tag] == ATTS:
                values = self.__names.attributes(child)
                if keys.isdisjoint(values):
                    attributes.update(values)
                else:
                    atts.append(dict(values))
        return attributes, atts


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
