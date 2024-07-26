"""Model for SDMX Reference Metadata.

Reference metadata are quite generic (and therefore powerful) in SDMX.
Though they are typically used to provide additional information about
statistical data, such as information about the general methodological
and quality aspects of the statistical production process, they can also
be used to drive process steps such as validation or mapping, for
example by providing configuration details in a metadata report.
"""

from collections import defaultdict
from typing import Any, Dict, Iterator, List, Optional, Sequence

from msgspec import Struct


class MetadataAttribute(Struct, frozen=True, omit_defaults=True):
    """An entry in a metadata report.

    An attribute is iterable, as it may contain other attributes.

    Attributes:
        id: The identifier of the attribute (e.g. "License").
        value: The attribute value (e.g. "BSD-2-Clause").
        attributes: The list of "children" attributes (i.e. attributes
            can be nested).
    """

    id: str
    value: Optional[Any] = None
    attributes: Sequence["MetadataAttribute"] = ()

    def __iter__(self) -> Iterator["MetadataAttribute"]:
        """Return an iterator over the list of attributes."""
        yield from self.attributes

    def __str__(self) -> str:
        """Returns a human-friendly description."""
        return f"{self.id}: {self.value}"


class MetadataReport(Struct, frozen=True, omit_defaults=True):
    """An organized collection of metadata.

    A metadata report is iterable and it is also possible to directly
    retrieve an attribute using its ID.

    Attributes:
        id: The identifier of the report (e.g. DTI_MACRO).
        name: The name of the report (e.g. "Configuration metadata for
            the MACRO dataflow").
        metadataflow: The URN of the dataflow for which the report
            belongs.
        targets: The URN(s) of SDMX artefact(s) to which the report relates.
        attributes: The list of metadata attributes included in the report.
            Attributes may contain other attributes.
    """

    id: str
    name: str
    metadataflow: str
    targets: Sequence[str]
    attributes: Sequence[MetadataAttribute]

    def __iter__(self) -> Iterator[MetadataAttribute]:
        """Return an iterator over the list of report attributes."""
        yield from self.attributes

    def __len__(self) -> int:
        """Return the number of attributes in the report."""
        return self.__get_count(self.attributes)

    def __getitem__(self, id_: str) -> Optional[MetadataAttribute]:
        """Return the attribute identified by the given ID."""
        return self.__extract_attr(self.attributes, id_)

    def __get_count(self, attributes: Sequence[MetadataAttribute]) -> int:
        """Return the number of attributes at all levels."""
        count = len(attributes)
        for attr in attributes:
            if attr.attributes:
                count += self.__get_count(attr.attributes)
        return count

    def __extract_attr(
        self, attributes: Sequence[MetadataAttribute], id_: str
    ) -> Optional[MetadataAttribute]:
        if "." in id_:
            ids = id_.split(".")
            out = list(filter(lambda attr: attr.id == ids[0], attributes))
            if out:
                pkey = ".".join(ids[1:])
                return self.__extract_attr(out[0].attributes, pkey)
        else:
            out = list(filter(lambda attr: attr.id == id_, attributes))
            if out:
                return out[0]
        return None


def merge_attributes(
    attrs: Sequence[MetadataAttribute],
) -> Sequence[MetadataAttribute]:
    """Groups together the values of attributes with the same ID.

    The function assumes that an attribute will either have a
    value or will act as a container for other attributes. In
    case the attribute contains other attributes AND has a value,
    this function will NOT work as expected.

    Args:
        attrs: The list of attributes to be merged

    Returns:
        The list of (possibly merged) attributes
    """
    by_id: Dict[str, List[Any]] = defaultdict(list)
    sub_id = []

    for attr in attrs:
        if attr.attributes:
            sub_id.append(
                MetadataAttribute(
                    attr.id,
                    attr.value,
                    merge_attributes(attr.attributes),
                )
            )
        else:
            by_id[attr.id].append(attr.value)

    out = []
    out.extend(sub_id)
    for k, v in by_id.items():
        val = v if len(v) > 1 else v[0]
        out.append(MetadataAttribute(k, val))
    return out
