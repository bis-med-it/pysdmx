# mypy: disable-error-code="union-attr"
"""Module for writing SDMX-ML 2.1 Generic data messages."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import pandas as pd

from pysdmx.io._pd_utils import (
    transform_dataframe_for_writing,
    validate_schema_exists,
)
from pysdmx.io.format import Format
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__write_aux import (
    ABBR_GEN,
    ABBR_MSG,
    ALL_DIM,
    __escape_xml,
    __write_header,
    create_namespaces,
    get_end_message,
    get_structure,
)
from pysdmx.io.xml.__write_data_aux import (
    check_content_dataset,
    check_dimension_at_observation,
    writing_validation,
)
from pysdmx.io.xml.config import CHUNKSIZE
from pysdmx.model.message import Header
from pysdmx.toolkit.pd._data_utils import get_codes
from pysdmx.util import parse_short_urn


def __value(id: str, value: str) -> str:
    """Write a value tag."""
    return f"<{ABBR_GEN}:Value id={id!r} value={__escape_xml(str(value))!r}/>"


def __generate_obs_structure(
    dataset: PandasDataset,
) -> Tuple[List[str], str, List[str]]:
    """Generate the structure of the observations.

    First element is a list of
    the codes for Key, second element is the code for the value, and the third
    element is a list of the codes for the attributes.

    Args:
        dataset: PandasDataset. The dataset to generate the structure from.

    Returns:
        The structure of the observations
    """
    obs_structure: Tuple[List[str], str, List[str]] = (
        [],
        dataset.structure.components.measures[0].id,
        [],
    )
    for dim in dataset.structure.components.dimensions:
        obs_structure[0].append(dim.id)

    cols = dataset.data.columns

    for att in dataset.structure.components.attributes:
        if att.attachment_level == "O" and att.id in cols:
            obs_structure[2].append(att.id)
        elif (
            att.attachment_level is not None
            and att.attachment_level != "D"
            and att.id in cols
        ):
            obs_structure[0].append(att.id)

    return obs_structure


def __memory_optimization_writing(
    data: pd.DataFrame,
    obs_structure: Tuple[List[str], str, List[str]],
    prettyprint: bool,
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
            outfile += __obs_processing(
                data.iloc[previous:next_], obs_structure, prettyprint
            )
            previous = next_
            next_ += CHUNKSIZE

            if next_ >= length_:
                outfile += __obs_processing(
                    data.iloc[previous:], obs_structure, prettyprint
                )
                previous = next_
    else:
        outfile += __obs_processing(data, obs_structure, prettyprint)

    return outfile


def __write_data_generic(
    datasets: Dict[str, PandasDataset],
    dim_mapping: Dict[str, str],
    prettyprint: bool = True,
) -> str:
    """Write data to SDMX-ML 2.1 Generic format.

    Args:
        datasets: dict. Datasets to be written.
        dim_mapping: dict. URN-DimensionAtObservation mapping.
        prettyprint: bool. Prettyprint or not.

    Returns:
        The data in SDMX-ML 2.1 Generic format, as string.
    """
    outfile = ""

    for short_urn, dataset in datasets.items():
        writing_validation(dataset)
        outfile += __write_data_single_dataset(
            dataset=dataset,
            prettyprint=prettyprint,
            dim=dim_mapping[short_urn],
        )

    return outfile


def __write_data_single_dataset(
    dataset: PandasDataset,
    prettyprint: bool = True,
    dim: str = ALL_DIM,
) -> str:
    """Write data to SDMX-ML 2.1 Generic format.

    Args:
        dataset: PandasDataset. Dataset to be written.
        prettyprint: bool. Prettyprint or not.
        dim: str. Dimension to be written.

    Returns:
        The data in SDMX-ML 2.1 Generic format, as string.
    """
    outfile = ""
    structure_urn = get_structure(dataset)
    id_structure = parse_short_urn(structure_urn).id

    nl = "\n" if prettyprint else ""
    child1 = "\t" if prettyprint else ""
    child2 = "\t\t" if prettyprint else ""
    child3 = "\t\t\t" if prettyprint else ""

    # Datasets
    outfile += (
        f"{nl}{child1}<{ABBR_MSG}:DataSet "
        f"structureRef={id_structure!r} "
        f"action={dataset.action.value!r}>{nl}"
    )
    data = ""
    # Write attached attributes
    attached_attributes_str = []
    for k, v in dataset.attributes.items():
        attached_attributes_str.append(__value(k, v))

    if len(attached_attributes_str) > 0:
        data += f"{child2}<{ABBR_GEN}:Attributes>{nl}"
        for att in attached_attributes_str:
            data += f"{child3}{att}{nl}"
        data += f"{child2}</{ABBR_GEN}:Attributes>{nl}"

    # Transform DataFrame for null value handling
    schema = validate_schema_exists(dataset)
    transformed_data = transform_dataframe_for_writing(dataset.data, schema)

    if dim == ALL_DIM:
        obs_structure = __generate_obs_structure(dataset)
        data += __memory_optimization_writing(
            data=transformed_data,
            obs_structure=obs_structure,
            prettyprint=prettyprint,
        )
    else:
        series_codes, obs_codes, group_codes = get_codes(
            dimension_code=dim,
            structure=dataset.structure,  # type: ignore[arg-type]
            data=transformed_data,
        )
        att_codes = [att.id for att in dataset.structure.components.attributes]
        series_att_codes = [x for x in series_codes if x in att_codes]
        obs_att_codes = [x for x in obs_codes if x in att_codes]

        series_codes = [x for x in series_codes if x not in series_att_codes]
        obs_codes = [x for x in obs_codes if x not in obs_att_codes]

        if group_codes:
            data += __group_processing(
                data=transformed_data,
                group_codes=group_codes,
                prettyprint=prettyprint,
            )

        data += __series_processing(
            data=transformed_data,
            series_codes=series_codes,
            series_att_codes=series_att_codes,
            obs_codes=obs_codes,
            obs_att_codes=obs_att_codes,
            prettyprint=prettyprint,
        )

    # Add to outfile
    outfile += data

    outfile += f"{child1}</{ABBR_MSG}:DataSet>"

    return outfile.replace("'", '"')


def __obs_processing(
    data: pd.DataFrame,
    obs_structure: Tuple[List[str], str, List[str]],
    prettyprint: bool = True,
) -> str:
    def __format_obs_str(element: Dict[str, Any]) -> str:
        child2 = "\t\t" if prettyprint else ""
        child3 = "\t\t\t" if prettyprint else ""
        child4 = "\t\t\t\t" if prettyprint else ""
        nl = "\n" if prettyprint else ""

        out = f"{child2}<{ABBR_GEN}:Obs>{nl}"
        # Obs Key writing
        out += f"{child3}<{ABBR_GEN}:ObsKey>{nl}"
        for k, v in element.items():
            if k in obs_structure[0] and v is not None:
                out += f"{child4}{__value(k, v)}{nl}"
        out += f"{child3}</{ABBR_GEN}:ObsKey>{nl}"

        # Obs Value writing (already transformed)
        obs_value_id = obs_structure[1]
        obs_value = element.get(obs_value_id)
        if obs_value is not None:
            out += (
                f"{child3}<{ABBR_GEN}:ObsValue value={str(obs_value)!r}/>{nl}"
            )

        if len(obs_structure[2]) > 0:
            # Obs Attributes writing
            obs_att_content = ""
            for k, v in element.items():
                if k in obs_structure[2] and v is not None:
                    obs_att_content += f"{child4}{__value(k, v)}{nl}"
            if obs_att_content:
                out += f"{child3}<{ABBR_GEN}:Attributes>{nl}"
                out += obs_att_content
                out += f"{child3}</{ABBR_GEN}:Attributes>{nl}"

        out += f"{child2}</{ABBR_GEN}:Obs>{nl}"

        return out

    parser = lambda x: __format_obs_str(x)  # noqa: E731

    iterator = map(parser, data.to_dict(orient="records"))

    return "".join(iterator)


def __group_processing(
    data: pd.DataFrame,
    group_codes: List[Dict[str, Any]],
    prettyprint: bool = True,
) -> str:
    def __format_group_str(
        data_info: Dict[Any, Any],
        group_id: str,
        dimensions: List[str],
        attribute: str,
    ) -> str:
        """Formats a generic SDMX group using __value()."""
        child2 = "\t\t" if prettyprint else ""
        nl = "\n" if prettyprint else ""

        out_element = f'{child2}<{ABBR_GEN}:Group type="{group_id}">{nl}'

        # GroupKey block
        out_element += f"{child2}\t<{ABBR_GEN}:GroupKey>{nl}"
        for dim in dimensions:
            dim_val = data_info.get(dim)
            if dim_val is not None:
                out_element += f"{child2}\t\t{__value(dim, dim_val)}{nl}"
        out_element += f"{child2}\t</{ABBR_GEN}:GroupKey>{nl}"

        # Attributes block (value already transformed)
        attr_value = data_info.get(attribute)
        if attr_value is not None:
            out_element += f"{child2}\t<{ABBR_GEN}:Attributes>{nl}"
            out_element += f"{child2}\t\t{__value(attribute, attr_value)}{nl}"
            out_element += f"{child2}\t</{ABBR_GEN}:Attributes>{nl}"

        out_element += f"{child2}</{ABBR_GEN}:Group>{nl}"
        return out_element

    out_list: List[str] = []

    for group in group_codes:
        group_id = group["group_id"]
        dimensions = group["dimensions"]
        attribute = group["attribute"]
        group_keys = dimensions + [attribute]

        grouped_data = (
            data[group_keys]
            .drop_duplicates()
            .reset_index(drop=True)
            .to_dict(orient="records")
        )

        out_list.extend(
            [
                __format_group_str(record, group_id, dimensions, attribute)
                for record in grouped_data
            ]
        )

    return "".join(out_list)


def __series_processing(
    data: pd.DataFrame,
    series_codes: List[str],
    series_att_codes: List[str],
    obs_codes: List[str],
    obs_att_codes: List[str],
    prettyprint: bool = True,
) -> str:
    def __generate_series_str() -> str:
        out_list: List[str] = []
        data.groupby(by=series_codes + series_att_codes, dropna=False)[
            data.columns
        ].apply(lambda x: __format_dict_ser(out_list, x))

        return "".join(out_list)

    def __format_dict_ser(
        output_list: List[str],
        group_data: Any,
    ) -> Any:
        obs_data = group_data[obs_codes + obs_att_codes].copy()
        data_dict["Series"][0]["Obs"] = obs_data.to_dict(orient="records")
        data_dict["Series"][0].update(
            {
                k: v
                for k, v in group_data[series_att_codes].iloc[0].items()
                if k in series_att_codes
            }
        )
        output_list.append(
            __format_ser_str(
                data_info=data_dict["Series"][0],
                series_codes=series_codes,
                series_att_codes=series_att_codes,
                obs_codes=obs_codes,
                obs_att_codes=obs_att_codes,
                prettyprint=prettyprint,
            )
        )
        del data_dict["Series"][0]

    # Getting each datapoint from data and creating dict
    data = data.sort_values(series_codes, axis=0)
    data_dict = {
        "Series": data[series_codes]
        .drop_duplicates()
        .reset_index(drop=True)
        .to_dict(orient="records")
    }

    out = __generate_series_str()

    return out


def __format_ser_str(
    data_info: Dict[Any, Any],
    series_codes: List[str],
    series_att_codes: List[str],
    obs_codes: List[str],
    obs_att_codes: List[str],
    prettyprint: bool,
) -> str:
    child2 = "\t\t" if prettyprint else ""
    child3 = "\t\t\t" if prettyprint else ""
    child4 = "\t\t\t\t" if prettyprint else ""
    child5 = "\t\t\t\t\t" if prettyprint else ""
    nl = "\n" if prettyprint else ""

    out_element = f"{child2}<{ABBR_GEN}:Series>{nl}"

    # Series Key writing
    out_element += f"{child3}<{ABBR_GEN}:SeriesKey>{nl}"
    for k, v in data_info.items():
        if k in series_codes and v is not None:
            out_element += f"{child4}{__value(k, v)}{nl}"
    out_element += f"{child3}</{ABBR_GEN}:SeriesKey>{nl}"

    # Series Attributes writing (values already transformed)
    if len(series_att_codes) > 0:
        att_content = ""
        for k, v in data_info.items():
            if k in series_att_codes and v is not None:
                att_content += f"{child4}{__value(k, v)}{nl}"
        if att_content:
            out_element += f"{child3}<{ABBR_GEN}:Attributes>{nl}"
            out_element += att_content
            out_element += f"{child3}</{ABBR_GEN}:Attributes>{nl}"

    # Obs writing
    for obs in data_info["Obs"]:
        out_element += f"{child3}<{ABBR_GEN}:Obs>{nl}"

        # Obs Dimension writing
        obs_dim_val = obs.get(obs_codes[0])
        if obs_dim_val is not None:
            out_element += (
                f"{child4}<{ABBR_GEN}:ObsDimension "
                f"value={str(obs_dim_val)!r}/>{nl}"
            )
        # Obs Value writing (already transformed)
        obs_value_id = obs_codes[1]
        obs_val = obs.get(obs_value_id)
        if obs_val is not None:
            out_element += (
                f"{child4}<{ABBR_GEN}:ObsValue value={str(obs_val)!r}/>{nl}"
            )

        # Obs Attributes writing
        out_element += __format_obs_attributes(
            obs, obs_att_codes, child4, child5, nl
        )
        out_element += f"{child3}</{ABBR_GEN}:Obs>{nl}"

    out_element += f"{child2}</{ABBR_GEN}:Series>{nl}"

    return out_element


def __format_obs_attributes(
    obs: Dict[str, Any],
    obs_att_codes: List[str],
    child4: str,
    child5: str,
    nl: str,
) -> str:
    if len(obs_att_codes) == 0:
        return ""

    obs_att_content = ""
    for k, v in obs.items():
        if k in obs_att_codes and v is not None:
            obs_att_content += f"{child5}{__value(k, v)}{nl}"

    if not obs_att_content:
        return ""

    return (
        f"{child4}<{ABBR_GEN}:Attributes>{nl}"
        f"{obs_att_content}"
        f"{child4}</{ABBR_GEN}:Attributes>{nl}"
    )


def write(
    datasets: Sequence[PandasDataset],
    output_path: Optional[Union[str, Path]] = None,
    prettyprint: bool = True,
    header: Optional[Header] = None,
    dimension_at_observation: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    """Write data to SDMX-ML 2.1 Generic format.

    Args:
        datasets: The datasets to be written.
        output_path: The path to save the file.
        prettyprint: Prettyprint or not.
        header: The header to be used (generated if None).
        dimension_at_observation:
          The mapping between the dataset and the dimension at observation.

    Returns:
        The XML string if path is empty, None otherwise.
    """
    type_ = Format.DATA_SDMX_ML_2_1_GEN

    # Checking if we have datasets,
    # we need to ensure we can write them correctly
    check_content_dataset(datasets)
    content = {dataset.short_urn: dataset for dataset in datasets}

    if header is None:
        header = Header()

    # Checking the dimension at observation mapping
    dim_mapping = check_dimension_at_observation(
        datasets=content, dimension_at_observation=dimension_at_observation
    )
    header.structure = dim_mapping
    # Generating the initial tag with namespaces
    outfile = create_namespaces(type_, prettyprint=prettyprint)
    # Generating the header
    outfile += __write_header(header, prettyprint, data_message=True)
    # Writing the content
    outfile += __write_data_generic(content, dim_mapping, prettyprint)

    outfile += get_end_message(type_, prettyprint)

    output_path = (
        str(output_path) if isinstance(output_path, Path) else output_path
    )

    if output_path is None or output_path == "":
        return outfile

    with open(output_path, "w", encoding="UTF-8", errors="replace") as f:
        f.write(outfile)

    return None
