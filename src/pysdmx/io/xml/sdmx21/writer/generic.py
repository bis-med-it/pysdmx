"""Module for writing SDMX-ML 2.1 Generic data messages."""

from typing import Any, Dict, List, Tuple

import pandas as pd

from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.sdmx21.writer.__write_aux import (
    ABBR_GEN,
    ABBR_MSG,
    ALL_DIM,
    CHUNKSIZE,
    get_codes,
    get_structure,
)
from pysdmx.model import Schema
from pysdmx.util import parse_urn


def __value(id: str, value: str) -> str:
    return f"<{ABBR_GEN}:Value id={id!r} value={value!r}/>"


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
    obs_structure = ([], dataset.structure.components.measures[0].id, [])
    for dim in dataset.structure.components.dimensions:
        obs_structure[0].append(dim.id)

    for att in dataset.structure.components.attributes:
        if att.attachment_level == "O":
            obs_structure[2].append(att.id)
        elif att.attachment_level == "D":
            obs_structure[0].append(att.id)

    return obs_structure


def __memory_optimization_writing(
    dataset: PandasDataset,
    obs_structure: Tuple[List[str], str, List[str]],
    prettyprint: bool,
) -> str:
    """Memory optimization for writing data."""
    outfile = ""
    length_ = len(dataset.data)
    if len(dataset.data) > CHUNKSIZE:
        previous = 0
        next_ = CHUNKSIZE
        while previous <= length_:
            # Sliding a window for efficient access to the data
            # and avoid memory issues
            outfile += __obs_processing(
                dataset.data.iloc[previous:next_], obs_structure, prettyprint
            )
            previous = next_
            next_ += CHUNKSIZE

            if next_ >= length_:
                outfile += __obs_processing(
                    dataset.data.iloc[previous:], obs_structure, prettyprint
                )
                previous = next_
    else:
        outfile += __obs_processing(dataset.data, obs_structure, prettyprint)

    return outfile


def write_data_generic(
    datasets: Dict[str, PandasDataset], prettyprint: bool = True
) -> str:
    """Write data to SDMX-ML 2.1 Generic format.

    Args:
        datasets: dict. Datasets to be written.
        prettyprint: bool. Prettyprint or not.

    Returns:
        The data in SDMX-ML 2.1 Generic format, as string.
    """
    outfile = ""

    for dataset in datasets.values():
        outfile += __write_data_single_dataset(
            dataset=dataset, prettyprint=prettyprint
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

    def __remove_optional_attributes_empty_data(str_to_check: str) -> str:
        """This function removes data when optional attributes are found."""
        if isinstance(dataset.structure, Schema):
            for att in dataset.structure.components.attributes:
                if not att.required:
                    to_replace = f'<{ABBR_GEN}:Value id={att.id!r} value=""/>'
                    if prettyprint:
                        to_replace = f"{child3}{to_replace}{nl}"
                    str_to_check = str_to_check.replace(to_replace, "")
        return str_to_check

    outfile = ""
    structure_urn = get_structure(dataset)
    id_structure = parse_urn(structure_urn).id

    nl = "\n" if prettyprint else ""
    child1 = "\t" if prettyprint else ""
    child2 = "\t\t" if prettyprint else ""
    child3 = "\t\t\t" if prettyprint else ""

    # Datasets
    outfile += (
        f"{nl}{child1}<{ABBR_MSG}:DataSet "
        f"structureRef={id_structure!r} "
        f'action="Replace">{nl}'
    )

    # Write attached attributes
    attached_attributes_str = []
    for k, v in dataset.attributes.items():
        attached_attributes_str.append(__value(k, v))

    if len(attached_attributes_str) > 0:
        outfile += f"{child2}<{ABBR_GEN}:Attributes>{nl}"
        for att in attached_attributes_str:
            outfile += f"{child3}{att}{nl}"
        outfile += f"{child2}</{ABBR_GEN}:Attributes>{nl}"

    if dim == ALL_DIM:
        obs_structure = __generate_obs_structure(dataset)
        outfile += __memory_optimization_writing(
            dataset=dataset,
            obs_structure=obs_structure,
            prettyprint=prettyprint,
        )
    else:
        series_codes, obs_codes = get_codes(dim, dataset)
        series_att_codes = [
            x
            for x in series_codes
            if x in dataset.structure.components.attributes
        ]
        obs_att_codes = [
            x
            for x in obs_codes
            if x in dataset.structure.components.attributes
        ]

        series_codes = [x for x in series_codes if x not in series_att_codes]
        obs_codes = [x for x in obs_codes if x not in obs_att_codes]

        outfile += __series_processing(
            data=dataset.data,
            series_codes=series_codes,
            series_att_codes=series_att_codes,
            obs_codes=obs_codes,
            obs_att_codes=obs_att_codes,
            prettyprint=prettyprint,
        )

    # Remove optional attributes empty data
    outfile = __remove_optional_attributes_empty_data(outfile)

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
            if k in obs_structure[0]:
                out += f"{child4}{__value(k, v)}{nl}"
        out += f"{child3}</{ABBR_GEN}:ObsKey>{nl}"

        # Obs Value writing
        out += (
            f"{child3}<{ABBR_GEN}:ObsValue "
            f"value={element[obs_structure[1]]!r}/>{nl}"
        )

        # Obs Attributes writing
        out += f"{child3}<{ABBR_GEN}:Attributes>{nl}"
        for k, v in element.items():
            if k in obs_structure[0]:
                out += f"{child4}{__value(k, v)}{nl}"
        out += f"{child3}</{ABBR_GEN}:Attributes>{nl}"

        out += f"{child2}</{ABBR_GEN}:Obs>{nl}"

        return out

    parser = lambda x: __format_obs_str(x)  # noqa: E731

    iterator = map(parser, data.to_dict(orient="records"))

    return "".join(iterator)


def __series_processing(
    data: pd.DataFrame,
    series_codes: List[str],
    series_att_codes: List[str],
    obs_codes: List[str],
    obs_att_codes: List[str],
    prettyprint: bool = True,
) -> str:
    def __generate_series_str() -> str:
        out_list = []
        if all(elem in data.columns for elem in obs_codes):
            data.groupby(by=series_codes)[obs_codes].apply(
                lambda x: __format_dict_ser(out_list, x)
            )

        return "".join(out_list)

    def __format_dict_ser(
        output_list: List[Any],
        obs: pd.DataFrame,
    ) -> None:
        data_dict["Series"][0]["Obs"] = obs.to_dict(orient="records")
        output_list.append(__format_ser_str(data_dict))
        del data_dict["Series"][0]

    def __format_ser_str(data_info: Dict[str, Any]) -> str:
        child2 = "\t\t" if prettyprint else ""
        child3 = "\t\t\t" if prettyprint else ""
        child4 = "\t\t\t\t" if prettyprint else ""
        child5 = "\t\t\t\t\t" if prettyprint else ""
        nl = "\n" if prettyprint else ""

        out_element = f"{child2}<{ABBR_GEN}:Series>"

        # Series Key writing
        out_element += f"{child3}<{ABBR_GEN}:SeriesKey>{nl}"
        for k, v in data_info.items():
            if k in series_codes:
                out_element += f"{child4}{__value(k, v)}{nl}"
        out_element += f"{child3}</{ABBR_GEN}:SeriesKey>{nl}"

        # Series Attributes writing
        if len(series_att_codes) > 0:
            out_element += f"{child3}<{ABBR_GEN}:Attributes>{nl}"
            for k, v in data_info.items():
                if k in series_att_codes:
                    out_element += f"{child4}{__value(k, v)}{nl}"
            out_element += f"{child3}</{ABBR_GEN}:Attributes>{nl}"

        # Obs writing
        for obs in data_info["Obs"]:
            out_element += f"{child3}<{ABBR_GEN}:Obs>{nl}"

            # Obs Dimension writing
            out_element += (
                f"{child4}<{ABBR_GEN}:ObsDimension value={obs_codes[0]!r}>{nl}"
            )
            # Obs Value writing
            out_element += (
                f"{child4}<{ABBR_GEN}:ObsValue value={obs_codes[1]!r}/>{nl}"
            )

            # Obs Attributes writing
            if len(obs_att_codes) > 0:
                out_element += f"{child4}<{ABBR_GEN}:Attributes>{nl}"
                for k, v in obs.items():
                    if k in obs_att_codes:
                        out_element += f"{child5}{__value(k, v)}{nl}"
                out_element += f"{child4}</{ABBR_GEN}:Attributes>{nl}"
            out_element += f"{child3}<{ABBR_GEN}:Obs>"

        out_element += f"{child2}</{ABBR_GEN}:Series>"

        return out_element

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
