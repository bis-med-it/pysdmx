# mypy: disable-error-code="union-attr"
"""Module for writing SDMX-ML 3.0 Structure Specific auxiliary functions."""

from typing import Any, Dict, Hashable, List, Tuple

import pandas as pd

from pysdmx.io._pd_utils import _fill_na_values, _validate_schema_exists
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__write_aux import (
    ABBR_MSG,
    ALL_DIM,
    __escape_xml,
    get_structure,
)
from pysdmx.io.xml.__write_data_aux import (
    writing_validation,
)
from pysdmx.io.xml.config import CHUNKSIZE
from pysdmx.model import Role, Schema
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

    # Validate structure before writing
    schema = writing_validation(dataset)

    # Remove nan values from DataFrame
    dataset.data = _fill_na_values(dataset.data, schema)

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
    comp_required = {comp.id: comp.required for comp in structure.components}
    all_comp_ids = [comp.id for comp in structure.components]

    def __format_obs_str(element: Dict[str, Any]) -> str:
        """Formats the observation as key=value pairs."""
        nl = "\n" if prettyprint else ""
        child2 = "\t\t" if prettyprint else ""

        out = f"{child2}<Obs "

        # Use shared function to filter attributes
        attr_lines = _format_observation_attributes(
            element, all_comp_ids, comp_required
        )

        for k, v in attr_lines:
            out += f"{k}={__escape_xml(str(v))!r} "

        out += f"/>{nl}"

        return out

    def parser(x: Dict[Any, Any]) -> str:
        if _should_skip_obs(x, structure):
            return ""
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

    out_element = f"{child2}<Series "

    for k, v in data_info.items():
        if k != "Obs":
            out_element += f"{k}={__escape_xml(str(v))!r} "

    out_element += f">{nl}"

    for obs in data_info["Obs"]:
        out_element += f"{child3}<Obs "

        for k, v in obs.items():
            out_element += f"{k}={__escape_xml(str(v))!r} "

        out_element += f"/>{nl}"

    out_element += f"{child2}</Series>{nl}"

    return out_element


def __build_series_dict(
    data: pd.DataFrame, series_codes: List[str]
) -> Dict[str, List[Dict[Hashable, Any]]]:
    """Build series dictionary from data."""
    if not series_codes:
        return {"Series": [{}] if not data.empty else []}
    return {
        "Series": data[series_codes]
        .drop_duplicates()
        .reset_index(drop=True)
        .to_dict(orient="records")
    }


def __process_series_observations(
    data: pd.DataFrame,
    series_codes: List[str],
    obs_codes: List[str],
    data_dict: Dict[str, List[Dict[Hashable, Any]]],
    prettyprint: bool = True,
) -> str:
    """Process series and their observations into XML string."""
    out_list: List[str] = []

    def append_series_with_obs(obs: Any) -> str:
        """Append series with observations to output list."""
        data_dict["Series"][0]["Obs"] = obs.to_dict(orient="records")
        result = __format_ser_str(data_dict["Series"][0], prettyprint)
        out_list.append(result)
        del data_dict["Series"][0]
        return result

    if not series_codes:
        if not data.empty:
            append_series_with_obs(data[obs_codes])
    else:
        data.groupby(by=series_codes)[obs_codes].apply(append_series_with_obs)

    return "".join(out_list)


def __series_processing(
    data: pd.DataFrame,
    series_codes: List[str],
    obs_codes: List[str],
    prettyprint: bool = True,
) -> str:
    """Write series to SDMX-ML Structure-Specific format."""
    data = data.sort_values(series_codes, axis=0)
    data_dict = __build_series_dict(data, series_codes)
    return __process_series_observations(
        data, series_codes, obs_codes, data_dict, prettyprint
    )


def _should_skip_obs(element: Dict[str, Any], structure: Schema) -> bool:
    """Check if observation should be skipped.

    Skip if any required dimension has no value.

    Args:
        element: Dictionary representing one observation row
        structure: Schema containing component definitions

    Returns:
        True if observation should be skipped, False otherwise
    """
    for comp in structure.components:
        if comp.role == Role.DIMENSION and comp.required:
            val = element[comp.id]
            # If dimension value is empty or nan, skip this obs
            if pd.isna(val) or str(val) in ("", "#N/A", "NaN"):
                return True
    return False


def _format_observation_attributes(
    element: Dict[str, Any],
    attribute_ids: list[str],
    attr_required: Dict[str, bool],
) -> List[Tuple[str, Any]]:
    """Format observation attributes filtering empty optional ones.

    Args:
        element: Dictionary containing the observation data
        attribute_ids: List of attribute IDs to process
        attr_required: Dictionary mapping attribute IDs to required status

    Returns:
        List of (attribute_id, value) tuples (empty if no attributes to write)
    """
    attr_lines = []
    for k, v in element.items():
        if k in attribute_ids:
            is_required = attr_required.get(k, False)
            is_empty = pd.isna(v) or str(v) == ""

            # Write if: required (even if empty) OR has a value
            if is_required or not is_empty:
                attr_lines.append((k, v))

    return attr_lines
