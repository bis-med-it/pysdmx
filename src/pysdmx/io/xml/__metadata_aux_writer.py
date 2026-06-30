"""Shared writer for SDMX-ML reference metadata (GenericMetadata)."""

from typing import Optional, Sequence

from pysdmx.errors import Invalid
from pysdmx.io.format import Format
from pysdmx.io.xml.__tokens import (
    ATT,
    METADATAFLOW,
    MPA,
    TARGET,
    VALUE,
)
from pysdmx.io.xml.__write_aux import (
    ABBR_COM,
    ABBR_MSG,
    __escape_xml,
    add_indent,
    create_namespaces,
    get_end_message,
)
from pysdmx.model.__base import Agency
from pysdmx.model.message import Header
from pysdmx.model.metadata import (
    MetadataAttribute,
    MetadataReport,
    unmerge_attributes,
)
from pysdmx.util import parse_urn

# The reported attributes live in the metadata/generic namespace.
ABBR_META = "metadata"


def __write_attribute(attr: MetadataAttribute, indent: str) -> str:
    """Recursively writes a ``<metadata:Attribute>`` element.

    A scalar value is written as a single ``<metadata:Value>``; the caller is
    expected to have already expanded list values into separate attributes
    via :func:`unmerge_attributes`.
    """
    label = f"{ABBR_META}:{ATT}"
    outfile = f"{indent}<{label} id={attr.id!r}>".replace("'", '"')
    if attr.value is not None:
        value = __escape_xml(str(attr.value))
        outfile += (
            f"{add_indent(indent)}<{ABBR_META}:{VALUE}>"
            f"{value}</{ABBR_META}:{VALUE}>"
        )
    for child in attr.attributes:
        outfile += __write_attribute(child, add_indent(indent))
    outfile += f"{indent}</{label}>"
    return outfile


def __metadata_set_attrs(report: MetadataReport) -> str:
    """Builds the ``<mes:MetadataSet>`` attribute string.

    The XML set attributes ``reportingBeginDate`` / ``reportingEndDate`` map
    to the model fields ``reportingBegin`` / ``reportingEnd``.
    """
    agency = (
        report.agency.id
        if isinstance(report.agency, Agency)
        else report.agency
    )
    attrs = f" agencyID={agency!r} id={report.id!r} version={report.version!r}"
    optional = {
        "action": report.action.value if report.action else None,
        "publicationYear": report.publicationYear,
        "publicationPeriod": report.publicationPeriod,
        "reportingBeginDate": report.reportingBegin,
        "reportingEndDate": report.reportingEnd,
    }
    for key, value in optional.items():
        if value is not None:
            attrs += f" {key}={value!r}"
    return attrs.replace("'", '"')


def __write_metadata_set(report: MetadataReport, indent: str) -> str:
    """Writes a single ``<mes:MetadataSet>`` from a MetadataReport.

    Handles the name discrepancy explicitly: the XML element is
    ``MetadataSet`` (not ``MetadataReport``).
    """
    if not report.name:
        raise Invalid(
            "Invalid input",
            "SDMX-ML metadata reports must have a name",
            {"metadata_report": report.id},
        )
    attrs = __metadata_set_attrs(report)

    child = add_indent(indent)
    outfile = f"{indent}<{ABBR_MSG}:MetadataSet{attrs}>"
    name = __escape_xml(str(report.name))
    outfile += (
        f'{child}<{ABBR_COM}:Name xml:lang="en">{name}</{ABBR_COM}:Name>'
    )

    # The XSD requires a choice between MetadataProvisionAgreement and
    # Metadataflow.
    if report.metadataProvisionAgreement:
        outfile += (
            f"{child}<{ABBR_META}:{MPA}>"
            f"{report.metadataProvisionAgreement}</{ABBR_META}:{MPA}>"
        )
    elif report.metadataflow:
        outfile += (
            f"{child}<{ABBR_META}:{METADATAFLOW}>"
            f"{report.metadataflow}</{ABBR_META}:{METADATAFLOW}>"
        )
    else:
        raise Invalid(
            "Invalid input",
            "SDMX-ML metadata reports must reference either a metadataflow "
            "or a metadata provision agreement.",
            {"metadata_report": report.id},
        )

    for target in report.targets:
        outfile += (
            f"{child}<{ABBR_META}:{TARGET}>{target}</{ABBR_META}:{TARGET}>"
        )

    for attr in unmerge_attributes(report.attributes):
        outfile += __write_attribute(attr, child)

    outfile += f"{indent}</{ABBR_MSG}:MetadataSet>"
    return outfile


def __header_structure_ref(
    header: Optional[Header], reports: Sequence[MetadataReport]
) -> str:
    """Builds the structure short URN required by the GenericMetadata header.

    The GenericMetadata XSD requires the header to carry a ``<mes:Structure>``
    referencing a metadataflow or metadata structure definition. It is taken
    from the supplied header (if any) or synthesized from the first report's
    metadataflow.
    """
    if header is not None and header.structure:
        return next(iter(header.structure))
    for report in reports:
        if report.metadataflow:
            return str(parse_urn(report.metadataflow))
    raise Invalid(
        "Invalid input",
        "Cannot write SDMX-ML reference metadata without a metadataflow "
        "reference: it is required to build the message header.",
    )


def __write_metadata_header(
    header: Optional[Header],
    structure_urn: str,
    prettyprint: bool,
) -> str:
    """Writes the ``<mes:Header>`` of a GenericMetadata message.

    The header requires a ``<mes:Structure>`` referencing the metadataflow
    (or MSD). Unlike a data header, ``dimensionAtObservation`` is prohibited.
    """
    nl = "\n" if prettyprint else ""
    child1 = "\t" if prettyprint else ""
    child2 = "\t\t" if prettyprint else ""
    child3 = "\t\t\t" if prettyprint else ""

    header = header if header is not None else Header()
    prepared = header.prepared.isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )
    sender = header.sender.id

    ref = parse_urn(structure_urn)
    if ref.sdmx_type == "MetadataStructure":
        struct_tag = "Structure"
        urn = (
            f"urn:sdmx:org.sdmx.infomodel.metadatastructure."
            f"MetadataStructure={ref.agency}:{ref.id}({ref.version})"
        )
    else:
        struct_tag = "StructureUsage"
        urn = (
            f"urn:sdmx:org.sdmx.infomodel.metadatastructure."
            f"Metadataflow={ref.agency}:{ref.id}({ref.version})"
        )

    outfile = f"{nl}{child1}<{ABBR_MSG}:Header>"
    outfile += f"{nl}{child2}<{ABBR_MSG}:ID>{header.id}</{ABBR_MSG}:ID>"
    outfile += (
        f"{nl}{child2}<{ABBR_MSG}:Test>"
        f"{str(header.test).lower()}</{ABBR_MSG}:Test>"
    )
    outfile += (
        f"{nl}{child2}<{ABBR_MSG}:Prepared>{prepared}</{ABBR_MSG}:Prepared>"
    )
    outfile += f"{nl}{child2}<{ABBR_MSG}:Sender id={sender!r}/>".replace(
        "'", '"'
    )
    outfile += (
        f"{nl}{child2}<{ABBR_MSG}:Structure structureID={ref.id!r}>".replace(
            "'", '"'
        )
    )
    outfile += (
        f"{nl}{child3}<{ABBR_COM}:{struct_tag}>{urn}</{ABBR_COM}:{struct_tag}>"
    )
    outfile += f"{nl}{child2}</{ABBR_MSG}:Structure>"
    outfile += f"{nl}{child1}</{ABBR_MSG}:Header>"
    return outfile


def write_metadata(
    reports: Sequence[MetadataReport],
    type_: Format,
    prettyprint: bool = True,
    header: Optional[Header] = None,
) -> str:
    """Writes reference metadata reports as an SDMX-ML GenericMetadata message.

    Args:
        reports: The reference metadata reports to serialize.
        type_: The reference metadata SDMX-ML format (3.0 or 3.1).
        prettyprint: Whether to pretty-print the output.
        header: The header to use (synthesized if None).

    Returns:
        The SDMX-ML GenericMetadata message as a string.
    """
    nl = "\n" if prettyprint else ""
    child1 = "\t" if prettyprint else ""

    structure_urn = __header_structure_ref(header, reports)

    outfile = create_namespaces(type_, prettyprint=prettyprint)
    outfile += __write_metadata_header(header, structure_urn, prettyprint)
    for report in reports:
        outfile += __write_metadata_set(report, f"{nl}{child1}")
    outfile += get_end_message(type_, prettyprint)
    return outfile
