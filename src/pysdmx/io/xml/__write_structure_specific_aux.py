# mypy: disable-error-code="union-attr"
"""Module for writing SDMX-ML 3.0 Structure Specific auxiliary functions."""

from typing import Any, Dict, List

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__write_aux import (
    ABBR_MSG,
    ALL_DIM,
    __escape_xml,
    get_structure,
)
from pysdmx.io.xml.__write_data_aux import (
    _should_skip_xml_value,
    _single_non_empty_or_raise,
    stringify_dataset,
    writing_validation,
)
from pysdmx.io.xml.config import CHUNKSIZE
from pysdmx.toolkit.pd._data_utils import get_codes
from pysdmx.util import parse_short_urn


def __validate_all_dimensions_data(dataset: PandasDataset) -> None:
    dim_cols = [d.id for d in dataset.structure.components.dimensions]
    for col in dim_cols:
        if col not in dataset.data.columns:
            continue
        empty_rows = dataset.data[col] == ""
        if empty_rows.any():
            raise Invalid(
                f"AllDimensions requires all dimensions to have values. "
                f"Dimension '{col}' has empty values."
            )


def __memory_optimization_writing(
    data: pd.DataFrame, prettyprint: bool
) -> str:
    """Memory optimization for writing data."""
    outfile = ""
    length_ = len(data)
    if length_ > CHUNKSIZE:
        previous = 0
        next_ = CHUNKSIZE
        while previous <= length_:
            # Sliding a window for efficient access to the data
            # and avoid memory issues
            outfile += __obs_processing(data.iloc[previous:next_], prettyprint)
            previous = next_
            next_ += CHUNKSIZE

            if next_ >= length_:
                outfile += __obs_processing(data.iloc[previous:], prettyprint)
                previous = next_
    else:
        outfile += __obs_processing(data, prettyprint)

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
        stringify_dataset(dataset)
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
    outfile = ""
    structure_urn = get_structure(dataset)
    id_structure = parse_short_urn(structure_urn).id
    sdmx_type = parse_short_urn(structure_urn).id
    # Remove null values from DataFrame
    stringify_dataset(dataset)

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
        __validate_all_dimensions_data(dataset)
        data += __memory_optimization_writing(dataset.data, prettyprint)
    else:
        writing_validation(dataset)
        series_codes, obs_codes, group_codes = get_codes(
            dimension_code=dim,
            structure=dataset.structure,  # type: ignore[arg-type]
            data=dataset.data,
        )
        att_codes = [att.id for att in dataset.structure.components.attributes]
        series_att_codes = [x for x in series_codes if x in att_codes]
        obs_att_codes = [x for x in obs_codes if x in att_codes]
        series_codes = [x for x in series_codes if x not in series_att_codes]
        obs_codes = [x for x in obs_codes if x not in obs_att_codes]
        if group_codes:
            data += __group_processing(
                data=dataset.data,
                group_codes=group_codes,
                prettyprint=prettyprint,
            )
        data += __series_processing(
            data=dataset.data,
            series_codes=series_codes,
            series_att_codes=series_att_codes,
            obs_codes=obs_codes,
            obs_att_codes=obs_att_codes,
            prettyprint=prettyprint,
        )

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
            out_element += f"{k}={__escape_xml(v)!r} "
        out_element += f"/>{nl}"

        return out_element

    out_list: List[str] = []

    for group in group_codes:
        attribute = group["attribute"]
        dimensions = group["dimensions"]
        # Aggregate by group dimensions only; take the unique non-empty
        # attribute value per group so that rows where the attribute was
        # left empty do not collide with rows carrying the real value.
        # Conflicting non-empty values raise ``Invalid``.
        aggregated = data.groupby(by=dimensions, dropna=False, as_index=False)[
            attribute
        ].agg(
            lambda s, _att=attribute: _single_non_empty_or_raise(
                s, _att, "group"
            )
        )

        out_list.extend(
            __format_group_str(record, group["group_id"])
            for record in aggregated.to_dict(orient="records")
            if not _should_skip_xml_value(record.get(attribute))
        )

    return "".join(out_list)


def __obs_processing(data: pd.DataFrame, prettyprint: bool = True) -> str:
    def __format_obs_str(element: Dict[str, Any]) -> str:
        """Formats the observation as key=value pairs."""
        nl = "\n" if prettyprint else ""
        child2 = "\t\t" if prettyprint else ""

        out = f"{child2}<Obs "

        for k, v in element.items():
            if not _should_skip_xml_value(v):
                out += f"{k}={__escape_xml(v)!r} "

        out += f"/>{nl}"

        return out

    parser = lambda x: __format_obs_str(x)  # noqa: E731

    iterator = map(parser, data.to_dict(orient="records"))

    return "".join(iterator)


def __format_ser_str(data_info: Dict[Any, Any], prettyprint: bool) -> str:
    """Formats the series as key=value pairs."""
    child2 = "\t\t" if prettyprint else ""
    child3 = "\t\t\t" if prettyprint else ""
    nl = "\n" if prettyprint else ""

    out_element = f"{child2}<Series "

    for k, v in data_info.items():
        if k != "Obs" and not _should_skip_xml_value(v):
            out_element += f"{k}={__escape_xml(v)!r} "

    # Series with no observations
    if not data_info.get("Obs"):
        return out_element + f"/>{nl}"

    out_element += f">{nl}"

    for obs in data_info["Obs"]:
        out_element += f"{child3}<Obs "

        for k, v in obs.items():
            if not _should_skip_xml_value(v):
                out_element += f"{k}={__escape_xml(v)!r} "

        out_element += f"/>{nl}"

    out_element += f"{child2}</Series>{nl}"

    return out_element


def __series_processing(
    data: pd.DataFrame,
    series_codes: List[str],
    series_att_codes: List[str],
    obs_codes: List[str],
    obs_att_codes: List[str],
    prettyprint: bool = True,
) -> str:
    """Format one <Series> per dimension key, deriving series attributes.

    Group by dimensions only so that rows where a series-attached
    attribute was left empty do not split the series into multiple
    <Series> elements. Each attribute is set to the unique non-empty
    value found across the group's rows; conflicting non-empty values
    raise ``Invalid``. Rows whose observation dimension is empty
    (series-attribute-only rows) are excluded from the obs list.
    """
    obs_dim = obs_codes[0]
    out_list: List[str] = []
    for keys, group_data in data.groupby(by=series_codes, dropna=False):
        record: Dict[str, Any] = dict(zip(series_codes, keys))
        for att in series_att_codes:
            record[att] = _single_non_empty_or_raise(
                group_data[att], att, "series"
            )
        obs_rows = group_data[~group_data[obs_dim].map(_should_skip_xml_value)]
        record["Obs"] = obs_rows[obs_codes + obs_att_codes].to_dict(
            orient="records"
        )
        out_list.append(__format_ser_str(record, prettyprint))
    return "".join(out_list)
