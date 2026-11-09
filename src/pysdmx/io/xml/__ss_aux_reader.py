"""SDMX XML StructureSpecificData reader aux module."""

from typing import Any, Dict, Iterable, List, Optional, Tuple

from lxml import etree

from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__data_stream import (
    Columns,
    Names,
    Row,
    merge_groups,
    read_data,
)
from pysdmx.io.xml.__tokens import ATTS, EXCLUDED_ATTRIBUTES
from pysdmx.model.dataset import ActionType


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
            df = merge_groups(df, groups)
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
