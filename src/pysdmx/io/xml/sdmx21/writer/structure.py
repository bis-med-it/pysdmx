"""Module for writing metadata to XML files."""

from typing import Dict, Optional, Sequence

from pysdmx.io.format import Format
from pysdmx.io.xml.__structure_aux_writer import (
    STR_DICT_TYPE_LIST_21,
    STR_TYPES,
    __write_structures,
)
from pysdmx.io.xml.__write_aux import (
    __write_header,
    create_namespaces,
    get_end_message,
)
from pysdmx.io.xml.__tokens import (
    AGENCY_ID,
    AGENCY_SCHEME,
    AS_STATUS,
    ATT,
    ATT_REL,
    CL,
    CL_LOW,
    CLASS,
    CON,
    CON_ID,
    CONDITIONAL,
    CORE_REP,
    CS,
    CUSTOM_TYPE,
    CUSTOM_TYPE_SCHEME,
    DEPARTMENT,
    DFW,
    DIM,
    DSD,
    DSD_COMPS,
    EMAIL,
    ENUM,
    ENUM_FORMAT,
    FAX,
    ID,
    LOCAL_REP,
    MANDATORY,
    MEASURE,
    NAME,
    NAME_PER,
    NAME_PER_SCHEME,
    PACKAGE,
    PAR_ID,
    PAR_VER,
    POSITION,
    PRIM_MEASURE,
    REF,
    ROLE,
    RULE,
    RULE_SCHEME,
    TELEPHONE,
    TEXT_FORMAT,
    TEXT_TYPE,
    TIME_DIM,
    TRANS_SCHEME,
    TRANSFORMATION,
    UDO,
    UDO_SCHEME,
    URI,
    URN,
    VERSION,
    VTL_MAPPING_SCHEME,
    VTLMAPPING,
)
from pysdmx.io.xml.__write_aux import (
    ABBR_COM,
    ABBR_MSG,
    ABBR_STR,
    MSG_CONTENT_PKG,
    __escape_xml,
    __to_lower_camel_case,
    __write_header,
    add_indent,
    create_namespaces,
    get_end_message,
)
from pysdmx.model import (
    AgencyScheme,
    Codelist,
    Concept,
    ConceptScheme,
    CustomType,
    CustomTypeScheme,
    DataType,
    Facets,
    Hierarchy,
    NamePersonalisation,
    NamePersonalisationScheme,
    Ruleset,
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
    VtlCodelistMapping,
    VtlConceptMapping,
    VtlDataflowMapping,
    VtlMappingScheme,
    VtlScheme,
)
from pysdmx.model.__base import (
    Agency,
    AnnotableArtefact,
    Contact,
    IdentifiableArtefact,
    Item,
    ItemReference,
    ItemScheme,
    MaintainableArtefact,
    NameableArtefact,
    Reference,
    VersionableArtefact,
)
from pysdmx.model.dataflow import (
    Component,
    Dataflow,
    DataStructureDefinition,
    Role,
)
from pysdmx.model.message import Header


def write(
    structures: Sequence[STR_TYPES],
    output_path: str = "",
    prettyprint: bool = True,
    header: Optional[Header] = None,
) -> Optional[str]:
    """This function writes a SDMX-ML file from the Message Content.

    Args:
        structures: The content to be written
        output_path: The path to save the file
        prettyprint: Prettyprint or not
        header: The header to be used (generated if None)

    Returns:
        The XML string if output_path is empty, None otherwise
    """
    type_ = Format.STRUCTURE_SDMX_ML_2_1
    elements = {structure.short_urn: structure for structure in structures}
    if header is None:
        header = Header()

    content: Dict[str, Dict[str, STR_TYPES]] = {}
    for urn, element in elements.items():
        list_ = STR_DICT_TYPE_LIST_21[type(element)]
        if list_ not in content:
            content[list_] = {}
        content[list_][urn] = element

    # Generating the initial tag with namespaces
    outfile = create_namespaces(type_, prettyprint=prettyprint)
    # Generating the header
    outfile += __write_header(header, prettyprint, data_message=False)
    # Writing the content
    outfile += __write_structures(content, prettyprint)

    outfile += get_end_message(type_, prettyprint)

    if output_path == "":
        return outfile
    with open(output_path, "w", encoding="UTF-8", errors="replace") as f:
        f.write(outfile)
    return None
