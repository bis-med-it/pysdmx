"""Shared reader for SDMX-ML reference metadata (GenericMetadata)."""

from typing import Any, Dict, List, Sequence

from pysdmx.errors import Invalid
from pysdmx.io.xml.__parse_xml import parse_xml
from pysdmx.io.xml.__structure_aux_reader import _extract_text
from pysdmx.io.xml.__tokens import (
    ACTION,
    AGENCY_ID,
    ATT,
    GENERIC_METADATA,
    ID,
    METADATA_SET,
    METADATAFLOW,
    MPA,
    NAME,
    PUBLICATION_PERIOD,
    PUBLICATION_YEAR,
    REPORTING_BEGIN_DATE,
    REPORTING_END_DATE,
    TARGET,
    VALUE,
    VERSION,
)
from pysdmx.io.xml.utils import add_list
from pysdmx.model.dataset import ActionType
from pysdmx.model.metadata import (
    MetadataAttribute,
    MetadataReport,
    merge_attributes,
)

# In a GenericMetadata document the metadata/generic namespace prefix is
# stripped by parse_xml, so the elements use their local names: the
# reported attribute is <Attribute> (token ATT), the value <Value>
# (token VALUE), etc.
ATTRIBUTE = ATT


def __format_attribute(att_elem: Dict[str, Any]) -> MetadataAttribute:
    """Recursively formats a metadata attribute.

    A reported attribute either holds one or more ``<Value>`` (a scalar or a
    list of scalars) or contains nested ``<Attribute>`` children.
    """
    value = None
    if VALUE in att_elem:
        raw = att_elem[VALUE]
        value = (
            [_extract_text(v) for v in raw]
            if isinstance(raw, list)
            else _extract_text(raw)
        )
    children = (
        [__format_attribute(child) for child in add_list(att_elem[ATTRIBUTE])]
        if ATTRIBUTE in att_elem
        else []
    )
    return MetadataAttribute(
        id=att_elem[ID],
        value=value,
        attributes=tuple(merge_attributes(children)),
    )


def __format_report(metadata_set: Dict[str, Any]) -> MetadataReport:
    """Formats a single ``<mes:MetadataSet>`` into a MetadataReport.

    Note the discrepancies handled here: the XML element is ``MetadataSet``
    (not ``MetadataReport``), and the XML set attributes
    ``reportingBeginDate`` / ``reportingEndDate`` map to the model fields
    ``reportingBegin`` / ``reportingEnd``.
    """
    name = _extract_text(metadata_set[NAME]) if NAME in metadata_set else None
    metadataflow = (
        _extract_text(metadata_set[METADATAFLOW])
        if METADATAFLOW in metadata_set
        else ""
    )
    mpa = _extract_text(metadata_set[MPA]) if MPA in metadata_set else None
    targets = (
        tuple(_extract_text(t) for t in add_list(metadata_set[TARGET]))
        if TARGET in metadata_set
        else ()
    )
    raw_attrs = (
        [__format_attribute(att) for att in add_list(metadata_set[ATTRIBUTE])]
        if ATTRIBUTE in metadata_set
        else []
    )
    action = (
        ActionType(metadata_set[ACTION]) if ACTION in metadata_set else None
    )
    return MetadataReport(
        id=metadata_set[ID],
        name=name,
        agency=metadata_set[AGENCY_ID],
        version=metadata_set.get(VERSION, "1.0"),
        metadataflow=metadataflow,
        metadataProvisionAgreement=mpa,
        targets=targets,
        attributes=tuple(merge_attributes(raw_attrs)),
        action=action,
        publicationYear=metadata_set.get(PUBLICATION_YEAR),
        publicationPeriod=metadata_set.get(PUBLICATION_PERIOD),
        reportingBegin=metadata_set.get(REPORTING_BEGIN_DATE),
        reportingEnd=metadata_set.get(REPORTING_END_DATE),
    )


def read_metadata(
    input_str: str, validate: bool = True
) -> Sequence[MetadataReport]:
    """Reads an SDMX-ML GenericMetadata message into MetadataReports.

    Args:
        input_str: The SDMX-ML GenericMetadata message to read.
        validate: If True, the XML data is validated against the XSD.

    Returns:
        The sequence of reference metadata reports.

    Raises:
        Invalid: If the document is not an SDMX-ML GenericMetadata message.
    """
    dict_info = parse_xml(input_str, validate)
    if GENERIC_METADATA not in dict_info:
        raise Invalid("This SDMX document is not SDMX-ML GenericMetadata.")
    reports: List[MetadataReport] = []
    sets = dict_info[GENERIC_METADATA].get(METADATA_SET)
    if sets is not None:
        reports = [
            __format_report(metadata_set) for metadata_set in add_list(sets)
        ]
    return reports
