# mypy: disable-error-code="union-attr"
"""Module for writing SDMX-ML 3.0 Structure Specific auxiliary functions."""

from typing import Any, Dict, List

import pandas as pd

from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__write_aux import (
    ABBR_MSG,
    ALL_DIM,
    __escape_xml,
    get_structure,
)
from pysdmx.io.xml.__write_data_aux import (
    get_codes,
    writing_validation,
)
from pysdmx.io.xml.config import CHUNKSIZE
from pysdmx.util import parse_short_urn


def __memory_optimization_writing(
    dataset: PandasDataset, prettyprint: bool
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
                dataset.data.iloc[previous:next_], prettyprint
            )
            previous = next_
            next_ += CHUNKSIZE

            if next_ >= length_:
                outfile += __obs_processing(
                    dataset.data.iloc[previous:], prettyprint
                )
                previous = next_
    else:
        outfile += __obs_processing(dataset.data, prettyprint)

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
        dataset.data = dataset.data.astype(str).replace(
            {"nan": "", "<NA>": ""}
        )
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
    # Remove nan values from DataFrame
    dataset.data = dataset.data.fillna("").astype(str).replace("nan", "")

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
        writing_validation(dataset)
        series_codes, obs_codes = get_codes(
            dimension_code=dim,
            structure=dataset.structure,  # type: ignore[arg-type]
            data=dataset.data,
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


def __obs_processing(data: pd.DataFrame, prettyprint: bool = True) -> str:
    def __format_obs_str(element: Dict[str, Any]) -> str:
        """Formats the observation as key=value pairs."""
        nl = "\n" if prettyprint else ""
        child2 = "\t\t" if prettyprint else ""

        out = f"{child2}<Obs "

        for k, v in element.items():
            out += f"{k}={__escape_xml(str(v))!r} "

        out += f"/>{nl}"

        return out

    parser = lambda x: __format_obs_str(x)  # noqa: E731

    iterator = map(parser, data.to_dict(orient="records"))

    return "".join(iterator)


def __series_processing(
    data: pd.DataFrame,
    series_codes: List[str],
    obs_codes: List[str],
    prettyprint: bool = True,
) -> str:
    def __generate_series_str() -> str:
        """Generates the series item with its observations."""
        out_list: List[str] = []
        data.groupby(by=series_codes)[obs_codes].apply(
            lambda x: __format_dict_ser(out_list, x)
        )

        return "".join(out_list)

    def __format_dict_ser(
        output_list: List[str],
        obs: Any,
    ) -> Any:
        """Formats the series as key=value pairs."""
        # Creating the observation dict,
        # we always get the first element on Series
        # as we are grouping by it
        data_dict["Series"][0]["Obs"] = obs.to_dict(orient="records")
        output_list.append(__format_ser_str(data_dict["Series"][0]))
        # We remove the data for series as it is no longer necessary
        del data_dict["Series"][0]

    def __format_ser_str(data_info: Dict[Any, Any]) -> str:
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
