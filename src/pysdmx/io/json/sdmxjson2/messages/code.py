"""Collection of SDMX-JSON schemas for codes and codelists."""

from datetime import datetime, timezone as tz
from typing import Optional, Sequence, Tuple

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import JsonAnnotation, JsonLink
from pysdmx.model import (
    Code,
    Codelist,
    HierarchicalCode,
    Hierarchy,
    HierarchyAssociation,
)
from pysdmx.util import find_by_urn, parse_item_urn


class JsonCode(Struct, frozen=True):
    """SDMX-JSON payload for codes."""

    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None
    parent: Optional[str] = None

    def __handle_date(self, datestr: str) -> datetime:
        return datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S%z")

    def __get_val(
        self, a: JsonAnnotation
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        vals = a.title.split("/")  # type: ignore[union-attr]
        if a.title.startswith("/"):  # type: ignore[union-attr]
            return (None, self.__handle_date(vals[1]))
        else:
            valid_from = self.__handle_date(vals[0])
            valid_to = self.__handle_date(vals[1]) if vals[1] else None
            return (valid_from, valid_to)

    def to_model(self) -> Code:
        """Converts a JsonCode to a standard code."""
        if self.annotations:
            vp = [
                a for a in self.annotations if a.type == "FR_VALIDITY_PERIOD"
            ]
        else:
            vp = None
        vf, vt = self.__get_val(vp[0]) if vp else (None, None)
        return Code(
            id=self.id,
            name=self.name,
            description=self.description,
            valid_from=vf,
            valid_to=vt,
        )


class JsonCodelist(Struct, frozen=True, rename={"agency": "agencyID"}):
    """SDMX-JSON payload for a codelist."""

    id: str
    name: str
    agency: str
    description: Optional[str] = None
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None
    isPartial: bool = False
    codes: Sequence[JsonCode] = ()

    def to_model(self) -> Codelist:
        """Converts a JsonCodelist to a standard codelist."""
        return Codelist(
            id=self.id,
            name=self.name,
            agency=self.agency,
            description=self.description,
            version=self.version,
            items=[i.to_model() for i in self.codes],
        )


class JsonValuelist(Struct, frozen=True, rename={"agency": "agencyID"}):
    """SDMX-JSON payload for a valuelist."""

    id: str
    name: str
    agency: str
    description: Optional[str] = None
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None
    isPartial: bool = False
    valueItems: Sequence[JsonCode] = ()

    def to_model(self) -> Codelist:
        """Converts a JsonValuelist to a standard codelist."""
        return Codelist(
            id=self.id,
            name=self.name,
            agency=self.agency,
            description=self.description,
            version=self.version,
            items=[i.to_model() for i in self.valueItems],
            sdmx_type="valuelist",
        )


class JsonCodelists(Struct, frozen=True):
    """SDMX-JSON payload for lists of codes."""

    codelists: Sequence[JsonCodelist] = ()
    valuelists: Sequence[JsonValuelist] = ()


class JsonCodelistMessage(Struct, frozen=True):
    """SDMX-JSON payload for /codelist queries."""

    data: JsonCodelists

    def to_model(self) -> Codelist:
        """Returns the requested codelist."""
        if self.data.codelists:
            return self.data.codelists[0].to_model()
        else:
            return self.data.valuelists[0].to_model()


class JsonHierarchicalCode(Struct, frozen=True):
    """Fusion-JSON payload for hierarchical codes."""

    id: str
    code: str
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None
    hierarchicalCodes: Sequence["JsonHierarchicalCode"] = ()

    def __find_code(self, codelists: Sequence[Codelist], urn: str) -> Code:
        r = parse_item_urn(urn)
        f = [
            c
            for c in codelists
            if (
                c.agency == r.agency
                and c.id == r.id
                and c.version == r.version
            )
        ]
        return [c for c in f[0].codes if c.id == r.item_id][0]

    def to_model(self, codelists: Sequence[Codelist]) -> HierarchicalCode:
        """Converts a JsonHierarchicalCode to a hierachical code."""
        code = self.__find_code(codelists, self.code)
        codes = [c.to_model(codelists) for c in self.hierarchicalCodes]
        vf = self.validFrom.replace(tzinfo=tz.utc) if self.validFrom else None
        vt = self.validTo.replace(tzinfo=tz.utc) if self.validTo else None
        return HierarchicalCode(
            code.id,
            code.name,
            code.description,
            code.valid_from,
            code.valid_to,
            vf,
            vt,
            codes,
        )


class JsonHierarchy(Struct, frozen=True, rename={"agency": "agencyID"}):
    """SDMX-JSON payload for a hierarchy."""

    id: str
    name: str
    agency: str
    description: Optional[str] = None
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None
    hierarchicalCodes: Sequence[JsonHierarchicalCode] = ()

    def to_model(self, codelists: Sequence[Codelist]) -> Hierarchy:
        """Converts a JsonHierarchy to a standard hierarchy."""
        return Hierarchy(
            id=self.id,
            name=self.name,
            agency=self.agency,
            description=self.description,
            version=self.version,
            codes=[i.to_model(codelists) for i in self.hierarchicalCodes],
        )


class JsonHierarchies(Struct, frozen=True):
    """SDMX-JSON payload for hierarchies."""

    codelists: Sequence[JsonCodelist] = ()
    hierarchies: Sequence[JsonHierarchy] = ()

    def to_model(self) -> Hierarchy:
        """Returns the requested hierarchy."""
        cls = [cl.to_model() for cl in self.codelists]
        return self.hierarchies[0].to_model(cls)


class JsonHierarchyAssociation(
    Struct, frozen=True, rename={"agency": "agencyID"}
):
    """SDMX-JSON payload for a hierarchy association."""

    id: str
    name: str
    agency: str
    linkedHierarchy: str
    linkedObject: str
    contextObject: str
    links: Sequence[JsonLink] = ()
    description: Optional[str] = None
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None

    def to_model(
        self,
        hierarchies: Sequence[JsonHierarchy],
        codelists: Sequence[JsonCodelist],
    ) -> HierarchyAssociation:
        """Converts a FusionHierarchyAssocation to a standard association."""
        cls = [cl.to_model() for cl in codelists]
        m = find_by_urn(hierarchies, self.linkedHierarchy).to_model(cls)
        lnk = list(
            filter(
                lambda i: hasattr(i, "rel") and i.rel == "UserDefinedOperator",
                self.links,
            )
        )
        return HierarchyAssociation(
            id=self.id,
            name=self.name,
            agency=self.agency,
            hierarchy=m,
            component_ref=self.linkedObject,
            context_ref=self.contextObject,
            description=self.description,
            version=self.version,
            operator=lnk[0].urn if lnk else None,
        )


class JsonHierarchyMessage(Struct, frozen=True):
    """SDMX-JSON payload for /hierarchy queries."""

    data: JsonHierarchies

    def to_model(self) -> Hierarchy:
        """Returns the requested hierarchy."""
        return self.data.to_model()


class JsonHierarchyAssociations(Struct, frozen=True):
    """SDMX-JSON payload for hierarchy associations."""

    codelists: Sequence[JsonCodelist] = ()
    hierarchies: Sequence[JsonHierarchy] = ()
    hierarchyassociations: Sequence[JsonHierarchyAssociation] = ()

    def to_model(self) -> Sequence[HierarchyAssociation]:
        """Returns the requested hierarchy associations."""
        return [
            ha.to_model(self.hierarchies, self.codelists)
            for ha in self.hierarchyassociations
        ]


class JsonHierarchyAssociationMessage(Struct, frozen=True):
    """SDMX-JSON payload for hierarchy associations messages."""

    data: JsonHierarchyAssociations

    def to_model(self) -> Sequence[HierarchyAssociation]:
        """Returns the requested hierarchy associations."""
        return self.data.to_model()
