# mypy: disable-error-code="union-attr"
"""Module for writing SDMX-ML 3.0 Structure Specific auxiliary functions."""

from typing import Any, Dict, List, Tuple

import pandas as pd

from pysdmx.io._pd_utils import _validate_schema_exists
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__tokens import OBS, SERIES
from pysdmx.io.xml.__write_aux import (
    ABBR_MSG,
    ALL_DIM,
    __escape_xml,
    get_structure,
)
from pysdmx.io.xml.config import CHUNKSIZE
from pysdmx.model import Schema
from pysdmx.toolkit.pd._data_utils import get_codes
from pysdmx.util import parse_short_urn


def __memory_optimization_writing(
    dataset: PandasDataset, prettyprint: bool
) -> str:
    """Memory optimization for writing data."""
    outfile = ""
    length_ = len(dataset.data)

    schema = _validate_schema_exists(dataset)

    if len(dataset.data) > CHUNKSIZE:
        previous = 0
        next_ = CHUNKSIZE
        while previous <= length_:
            # Sliding a window for efficient access to the data
            # and avoid memory issues
            outfile += __obs_processing(
                dataset.data.iloc[previous:next_],
                schema,
                prettyprint,
            )
            previous = next_
            next_ += CHUNKSIZE

            if next_ >= length_:
                outfile += __obs_processing(
                    dataset.data.iloc[previous:],
                    schema,
                    prettyprint,
                )
                previous = next_
    else:
        outfile += __obs_processing(
            dataset.data,
            schema,
            prettyprint,
        )

    return outfile


def __write_data_structure_specific(
    datasets: Dict[str, PandasDataset],
    dim_mapping: Dict[str, str],
    prettyprint: bool = True,
    references_30: bool = False,
) -> str:
    """Write data to SDMX-ML Structure-Specific format.

    Args:
        datasets: dict. Datasets to be written.
        dim_mapping: dict. URN-DimensionAtObservation mapping.
        prettyprint: bool. Prettyprint or not.
        references_30: bool. Whether to use SDMX 3.0 references.

    Returns:
        The data in SDMX-ML Structure-Specific format, as string.
    """
    outfile = ""

    for i, (short_urn, dataset) in enumerate(datasets.items()):
        outfile += __write_data_single_dataset(
            dataset=dataset,
            prettyprint=prettyprint,
            count=i + 1,
            dim=dim_mapping[short_urn],
            references_30=references_30,
        )

    return outfile


def __write_data_single_dataset(
    dataset: PandasDataset,
    prettyprint: bool = True,
    count: int = 1,
    dim: str = ALL_DIM,
    references_30: bool = False,
) -> str:
    """Write data to SDMX-ML Structure-Specific format.

    Args:
        dataset: PandasDataset. Dataset to be written.
        prettyprint: bool. Prettyprint or not.
        count: int. Count for namespace.
        dim: str. Dimension to be written.
        references_30: bool. Whether to use SDMX 3.0 references.

    Returns:
        The data in SDMX-ML Structure-Specific format, as string.
    """

    def __remove_optional_attributes_empty_data(str_to_check: str) -> str:
        """This function removes data when optional attributes are found."""
        for att in dataset.structure.components.attributes:
            if not att.required:
                str_to_check = str_to_check.replace(f"{att.id}='' ", "")
                str_to_check = str_to_check.replace(f'{att.id}="" ', "")
        return str_to_check

    outfile = ""
    structure_urn = get_structure(dataset)
    id_structure = parse_short_urn(structure_urn).id
    sdmx_type = parse_short_urn(structure_urn).id

    nl = "\n" if prettyprint else ""
    child1 = "\t" if prettyprint else ""

    attached_attributes_str = ""
    for k, v in dataset.attributes.items():
        attached_attributes_str += f"{k}={str(v)!r} "
    datascope = ""
    if not references_30:
        datascope = f'ss:dataScope="{sdmx_type}" '
    # Datasets
    outfile += (
        f"{nl}{child1}<{ABBR_MSG}:DataSet {attached_attributes_str}"
        f"ss:structureRef={id_structure!r} "
        f'xsi:type="ns{count}:DataSetType" '
        f"{datascope}"
        f'action="{dataset.action.value}">{nl}'
    )
    data = ""
    if dim == ALL_DIM:
        data += __memory_optimization_writing(dataset, prettyprint)
    else:
        series_codes, obs_codes, group_codes = get_codes(
            dimension_code=dim,
            structure=dataset.structure,  # type: ignore[arg-type]
            data=dataset.data,
        )
        if group_codes:
            data += __group_processing(
                data=dataset.data,
                group_codes=group_codes,
                prettyprint=prettyprint,
            )
        data += __series_processing(
            data=dataset.data,
            series_codes=series_codes,
            obs_codes=obs_codes,
            prettyprint=prettyprint,
        )

        # Remove optional attributes empty data
        data = __remove_optional_attributes_empty_data(data)

    # Adding to outfile
    outfile += data

    outfile += f"{child1}</{ABBR_MSG}:DataSet>"

    return outfile.replace("'", '"')


def __group_processing(
    data: pd.DataFrame,
    group_codes: list[Dict[str, Any]],
    prettyprint: bool = True,
) -> str:
    def __format_group_str(data_info: Dict[Any, Any], group_id: str) -> str:
        """Formats the series as key=value pairs."""
        child2 = "\t\t" if prettyprint else ""
        nl = "\n" if prettyprint else ""

        out_element = f"{child2}<Group xsi:type='ns1:{group_id}' "
        for k, v in data_info.items():
            out_element += f"{k}={__escape_xml(str(v))!r} "
        out_element += f"/>{nl}"

        return out_element

    out_list: List[str] = []

    for group in group_codes:
        group_keys = group["dimensions"] + [group["attribute"]]

        grouped_data = (
            data[group_keys]
            .drop_duplicates()
            .reset_index(drop=True)
            .to_dict(orient="records")
        )

        out_list.extend(
            [
                __format_group_str(record, group["group_id"])
                for record in grouped_data
            ]
        )

    return "".join(out_list)


def __obs_processing(
    data: pd.DataFrame,
    structure: Schema,
    prettyprint: bool = True,
) -> str:
    all_comp_ids = [comp.id for comp in structure.components]

    def __format_obs_str(element: Dict[str, Any]) -> str:
        """Formats the observation as key=value pairs."""
        nl = "\n" if prettyprint else ""
        child2 = "\t\t" if prettyprint else ""

        out = f"{child2}<{OBS} "

        # Use shared function to filter attributes
        attr_lines = _format_observation_attributes(element, all_comp_ids)

        for k, v in attr_lines:
            out += f"{k}={__escape_xml(str(v))!r} "

        out += f"/>{nl}"

        return out

    def parser(x: Dict[Any, Any]) -> str:
        return __format_obs_str(x)

    iterator = map(parser, data.to_dict(orient="records"))

    return "".join(iterator)


def __format_ser_str(
    data_info: Dict[Any, Any], prettyprint: bool = True
) -> str:
    """Formats the series as key=value pairs."""
    child2 = "\t\t" if prettyprint else ""
    child3 = "\t\t\t" if prettyprint else ""
    nl = "\n" if prettyprint else ""

    out_element = f"{child2}<{SERIES} "

    attr_parts: List[str] = []
    for k, v in data_info.items():
        if k != OBS:
            # Skip empty series attributes
            is_empty = pd.isna(v) or (isinstance(v, str) and v.strip() == "")
            if is_empty:
                continue
            attr_parts.append(f"{k}={__escape_xml(str(v))!r}")

    if attr_parts:
        out_element += " ".join(attr_parts) + " "

    # If there are no observations self-closing tag
    obs_list = data_info.get(OBS, [])
    if not obs_list:
        out_element += f"/>{nl}"
        return out_element

    out_element += f">{nl}"

    for obs in obs_list:
        out_element += f"{child3}<{OBS} "

        for k, v in obs.items():
            # Null
            if pd.isna(v):
                continue

            # Empty string
            if isinstance(v, str) and v.strip() == "":
                out_element += f'{k}="" '
                continue

            # Normal value
            out_element += f"{k}={__escape_xml(str(v))!r} "

        out_element += f"/>{nl}"

    out_element += f"{child2}</{SERIES}>{nl}"

    return out_element


def __process_series_observations(
    data: pd.DataFrame,
    series_codes: List[str],
    obs_codes: List[str],
    prettyprint: bool = True,
) -> str:
    """Process series and their observations into XML string."""
    out_list: List[str] = []

    if series_codes:
        # Series without observations
        for _, series_group in data.groupby(
            by=series_codes, sort=False, dropna=False
        ):
            series_attrs = series_group[series_codes].iloc[0].to_dict()
            obs_rows = series_group[obs_codes].to_dict(orient="records")

            processed = []
            for obs in obs_rows:
                has_non_empty = any(
                    not (pd.isna(v) or str(v).strip() == "")
                    for v in obs.values()
                )
                if not has_non_empty:
                    continue
                processed.append(obs)
                continue

            obs_rows = processed
            series_dict = {**series_attrs, OBS: obs_rows}

            result = __format_ser_str(series_dict, prettyprint)
            out_list.append(result)
    else:
        # No series codes
        series_attrs = {}
        obs_rows = data[obs_codes].to_dict(orient="records")

        processed = []
        for obs in obs_rows:
            has_non_empty = any(
                not (pd.isna(v) or str(v).strip() == "") for v in obs.values()
            )
            processed.append(obs)

        obs_rows = processed
        series_dict = {OBS: obs_rows}
        result = __format_ser_str(series_dict, prettyprint)
        out_list.append(result)

    return "".join(out_list)


def __series_processing(
    data: pd.DataFrame,
    series_codes: List[str],
    obs_codes: List[str],
    prettyprint: bool = True,
) -> str:
    """Write series to SDMX-ML Structure-Specific format."""
    data = data.sort_values(series_codes, axis=0)
    return __process_series_observations(
        data, series_codes, obs_codes, prettyprint
    )


def _format_observation_attributes(
    element: Dict[str, Any],
    attribute_ids: list[str],
) -> List[Tuple[str, Any]]:
    """Format observation attributes filtering empty optional ones.

    Args:
        element: Dictionary containing the observation data
        attribute_ids: List of attribute IDs to process

    Returns:
        List of (attribute_id, value) tuples (empty if no attributes to write)
    """
    attr_lines = []
    for k, v in element.items():
        if k in attribute_ids:
            is_empty = pd.isna(v)

            if isinstance(v, str) and v.strip() == "":
                is_empty = True

            if not is_empty:
                attr_lines.append((k, v))

    return attr_lines
