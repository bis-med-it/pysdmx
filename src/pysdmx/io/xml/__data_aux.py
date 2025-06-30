from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io.xml.__tokens import (
    AGENCY_ID,
    DATASET,
    DIM_OBS,
    HEADER,
    ID,
    PROV_AGREEMENT,
    REF,
    STR_ID,
    STR_REF,
    STR_USAGE,
    STRUCTURE,
    URN,
    VERSION,
)
from pysdmx.io.xml.utils import add_list
from pysdmx.util import parse_urn

READING_CHUNKSIZE = 50000


def __process_df(
    test_list: List[Dict[str, Any]],
    df: Optional[pd.DataFrame],
    is_end: bool = False,
) -> Any:
    if not is_end and len(test_list) <= READING_CHUNKSIZE:
        return test_list, df
    if df is not None:
        df = pd.concat([df, pd.DataFrame(test_list)], ignore_index=True)
    else:
        df = pd.DataFrame(test_list)

    del test_list[:]

    return test_list, df


def __get_ids_from_structure(element: Dict[str, Any]) -> Any:
    """Gets the agency_id, id and version of the structure.

    Args:
        element: The data hold in the structure.

    Returns:
        If the element is REF, agency_id, id and version may be returned.
        If the element is URN, agency_id, id and version would be taken from
        split function.
    """
    if REF in element:
        agency_id = element[REF][AGENCY_ID]
        id_ = element[REF][ID]
        version = element[REF][VERSION]
        return agency_id, id_, version
    elif URN in element:
        urn = parse_urn(element[URN])
        return urn.agency, urn.id, urn.version
    else:
        urn = parse_urn(element)  # type: ignore[arg-type]
        return urn.agency, urn.id, urn.version


def __get_elements_from_structure(structure: Dict[str, Any]) -> Any:
    """Gets elements according to the xml type of file.

    Args:
        structure: It can appear in two ways:
            If structure is 'STRUCTURE', it will get
            the ids related to STRUCTURE.
            If structure is 'STR_USAGE', it will get
            the ids related to STR_USAGE.

    Returns:
        The ids contained in the structure will be returned.

    Raises:
        NotImplemented: For Provision Agreement, as it is not implemented.
    """
    if STRUCTURE in structure:
        structure_type = "DataStructure"
        tuple_ids = __get_ids_from_structure(structure[STRUCTURE])

    elif STR_USAGE in structure:
        structure_type = "Dataflow"
        tuple_ids = __get_ids_from_structure(structure[STR_USAGE])
    elif PROV_AGREEMENT in structure:
        structure_type = "ProvisionAgreement"
        tuple_ids = __get_ids_from_structure(structure[PROV_AGREEMENT])
    else:
        raise NotImplemented(
            "Unsupported", "ProvisionAgrement not implemented"
        )
    return tuple_ids + (structure_type,)


def __extract_structure(structure: Any) -> Any:
    """Extracts elements contained in the structure."""
    structure = add_list(structure)
    str_info = {}
    for str_item in structure:
        (agency_id, id_, version, structure_type) = (
            __get_elements_from_structure(str_item)
        )

        str_id = f"{agency_id}:{id_}({version})"

        str_info[str_item[STR_ID]] = {
            DIM_OBS: str_item[DIM_OBS],
            "unique_id": str_id,
            "structure_type": structure_type,
        }

    return str_info


def get_data_objects(dict_info: Dict[str, Any]) -> Tuple[Any, Any]:
    """Parse dataset.

    Args:
        dict_info: Dict.
          XML dictionary (xmltodict).

    Returns:
        A dictionary of datasets.
    """
    str_info = __extract_structure(dict_info[HEADER][STRUCTURE])
    if DATASET not in dict_info:
        dataset_info = []
        for key in dict_info:
            if DATASET in key:
                dataset_info = add_list(dict_info[key])
    else:
        dataset_info = add_list(dict_info[DATASET])

    for d in dataset_info:
        if d[STR_REF] not in str_info:
            raise Invalid(
                f"Dataset Structure Reference {d[STR_REF]} "
                f"not found in the Header"
            )
    return dataset_info, str_info
