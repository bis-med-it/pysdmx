# mypy: disable-error-code="union-attr"
"""Module for writing SDMX-ML 3.0 Structure Specific auxiliary functions."""

from typing import Any, Dict, Iterable, List

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io._pd_utils import validate_schema_exists
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__write_aux import (
    ABBR_MSG,
    ALL_DIM,
    __escape_xml_attribute,
    get_structure,
)
from pysdmx.io.xml.__write_data_aux import (
    _should_skip_xml_value,
    _single_non_empty_or_raise,
    get_data_set_attributes,
    group_rows,
    stringify_dataset,
    writing_validation,
)
from pysdmx.io.xml.config import CHUNKSIZE
from pysdmx.model import Schema
from pysdmx.toolkit.pd._data_utils import get_codes, get_group_codes
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
    reference = parse_short_urn(get_structure(dataset))
    # Remove null values from DataFrame
    stringify_dataset(dataset)

    nl = "\n" if prettyprint else ""
    child1 = "\t" if prettyprint else ""
    child2 = "\t\t" if prettyprint else ""

    attributes = "".join(
        f'{k}="{__escape_xml_attribute(str(v))}" '
        for k, v in get_data_set_attributes(dataset).items()
    )
    if references_30:
        # SDMX-ML 3.x gives the data set attributes in an Atts element
        # without a key, as the DataSet has no attributes from the DSD
        data_set_attributes = ""
        datascope = ""
        atts = f"{child2}<Atts {attributes}/>{nl}" if attributes else ""
    else:
        data_set_attributes = attributes
        datascope = f'ss:dataScope="{reference.sdmx_type}" '
        atts = ""
    # Datasets
    outfile += (
        f"{nl}{child1}<{ABBR_MSG}:DataSet {data_set_attributes}"
        f'ss:structureRef="{reference.id}" '
        f'xsi:type="ns{count}:DataSetType" '
        f"{datascope}"
        f'ss:action="{dataset.action.value}">{nl}'
        f"{atts}"
    )
    data = ""
    if dim == ALL_DIM:
        __validate_all_dimensions_data(dataset)
        data += __all_dimensions_processing(
            dataset, prettyprint, count, references_30
        )
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
        if references_30:
            # An Obs of SDMX-ML 3.x has the attributes of the observation
            # only: those of the dimension at observation go to Atts
            schema = validate_schema_exists(dataset)
            keyed = __dimension_attributes(schema, obs_att_codes)
            obs_att_codes = [x for x in obs_att_codes if x not in keyed]
            data += __atts_processing(dataset.data, schema, keyed, prettyprint)
        if group_codes:
            data += __group_processing(
                data=dataset.data,
                group_codes=group_codes,
                prettyprint=prettyprint,
                count=count,
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

    return outfile


def __dimension_attributes(
    schema: Schema, attributes: Iterable[str]
) -> List[str]:
    """Returns the attributes attached to dimensions only, in schema order."""
    dimensions = {dimension.id for dimension in schema.components.dimensions}
    names = set(attributes)
    return [
        att.id
        for att in schema.components.attributes
        if att.id in names
        and att.attachment_level is not None
        and set(att.attachment_level.split(",")) <= dimensions
    ]


def __atts_processing(
    data: pd.DataFrame,
    schema: Schema,
    attributes: List[str],
    prettyprint: bool,
) -> str:
    """Writes the attributes in Atts with the values of their dimensions.

    An Atts of SDMX-ML 3.x gives the values of attributes for a key, the
    values of some dimensions: the attributes attached to the same
    dimensions share their Atts.
    """
    child2 = "\t\t" if prettyprint else ""
    nl = "\n" if prettyprint else ""
    codes: Dict[str, Dict[str, Any]] = {}
    for att in schema.components.attributes:
        if att.id in attributes:
            level = str(att.attachment_level)
            codes.setdefault(
                level, {"dimensions": level.split(","), "attributes": []}
            )["attributes"].append(att.id)
    out_list: List[str] = []
    for code in codes.values():
        for key, values in group_rows(data, code):
            content = "".join(
                f'{k}="{__escape_xml_attribute(v)}" '
                for k, v in {**key, **values}.items()
            )
            out_list.append(f"{child2}<Atts {content}/>{nl}")
    return "".join(out_list)


def __all_dimensions_processing(
    dataset: PandasDataset, prettyprint: bool, count: int, references_30: bool
) -> str:
    """Writes the Groups and the observations of AllDimensions data.

    The attributes of a group go to its Groups, and the data set
    attributes to the data set, as an Obs only has the attributes of
    an observation or of any dimension. In SDMX-ML 3.x, an Obs only has
    the attributes of the observation, and those of the dimensions go to
    Atts with the values of their dimensions.
    """
    schema = validate_schema_exists(dataset)
    group_codes = get_group_codes(schema, dataset.data)
    excluded = {att for group in group_codes for att in group["attributes"]}
    excluded.update(
        att.id
        for att in schema.components.attributes
        if att.attachment_level == "D"
    )
    atts = ""
    if references_30:
        keyed = __dimension_attributes(
            schema,
            (c for c in dataset.data.columns if c not in excluded),
        )
        excluded.update(keyed)
        atts = __atts_processing(dataset.data, schema, keyed, prettyprint)
    columns = [c for c in dataset.data.columns if c not in excluded]
    return (
        atts
        + __group_processing(dataset.data, group_codes, prettyprint, count)
        + __memory_optimization_writing(dataset.data[columns], prettyprint)
    )


def __group_processing(
    data: pd.DataFrame,
    group_codes: List[Dict[str, Any]],
    prettyprint: bool = True,
    count: int = 1,
) -> str:
    """Writes one Group per key of each group type, with its attributes."""
    child2 = "\t\t" if prettyprint else ""
    nl = "\n" if prettyprint else ""
    out_list: List[str] = []
    for group in group_codes:
        for key, attributes in group_rows(data, group):
            values = "".join(
                f'{k}="{__escape_xml_attribute(v)}" '
                for k, v in {**key, **attributes}.items()
            )
            out_list.append(
                f'{child2}<Group xsi:type="ns{count}:{group["group_id"]}" '
                f"{values}/>{nl}"
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
                out += f'{k}="{__escape_xml_attribute(v)}" '

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
            out_element += f'{k}="{__escape_xml_attribute(v)}" '

    # Series with no observations
    if not data_info.get("Obs"):
        return out_element + f"/>{nl}"

    out_element += f">{nl}"

    for obs in data_info["Obs"]:
        out_element += f"{child3}<Obs "

        for k, v in obs.items():
            if not _should_skip_xml_value(v):
                out_element += f'{k}="{__escape_xml_attribute(v)}" '

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
