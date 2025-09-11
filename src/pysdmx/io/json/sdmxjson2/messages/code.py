"""Collection of SDMX-JSON schemas for codes and codelists."""

from datetime import datetime
from datetime import timezone as tz
from typing import Optional, Sequence, Tuple

from msgspec import Struct

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.core import (
    ItemSchemeType,
    JsonAnnotation,
    JsonLink,
    MaintainableType,
    NameableType,
)
from pysdmx.model import (
    Agency,
    Annotation,
    Code,
    Codelist,
    HierarchicalCode,
    Hierarchy,
    HierarchyAssociation,
)
from pysdmx.util import find_by_urn, parse_item_urn

_VAL_FMT = "%Y-%m-%dT%H:%M:%S%z"


class JsonCode(NameableType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for codes."""

    parent: Optional[str] = None

    def __handle_date(self, datestr: str) -> datetime:
        return datetime.strptime(datestr, _VAL_FMT)

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

    def to_model(self, scheme: Optional[str] = None) -> Code:
        """Converts a JsonCode to a standard code."""
        if self.annotations:
            vp = [
                a for a in self.annotations if a.type == "FR_VALIDITY_PERIOD"
            ]
        else:
            vp = None
        vf, vt = self.__get_val(vp[0]) if vp else (None, None)
        if scheme:
            urn = f"{scheme}.{self.id}"
        else:
            urn = None
        return Code(
            id=self.id,
            name=self.name,
            description=self.description,
            valid_from=vf,
            valid_to=vt,
            annotations=[a.to_model() for a in self.annotations],
            urn=urn,
        )

    @classmethod
    def from_model(self, code: Code) -> "JsonCode":
        """Converts a pysdmx code to an SDMX-JSON one."""
        if not code.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON codes must have a name",
                {"code": code.id},
            )

        annotations = [JsonAnnotation.from_model(a) for a in code.annotations]
        if code.valid_from and code.valid_to:
            vp = (
                f"{datetime.strftime(code.valid_from, _VAL_FMT)}/"
                f"{datetime.strftime(code.valid_to, _VAL_FMT)}"
            )
        elif code.valid_from:
            vp = f"{datetime.strftime(code.valid_from, _VAL_FMT)}/"
        elif code.valid_to:
            vp = f"/{datetime.strftime(code.valid_to, _VAL_FMT)}"
        else:
            vp = ""
        if vp:
            annotations.append(
                JsonAnnotation(title=vp, type="FR_VALIDITY_PERIOD")
            )

        return JsonCode(
            id=code.id,
            name=code.name,
            description=code.description,
            annotations=tuple(annotations),
        )


class JsonCodelist(ItemSchemeType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a codelist."""

    codes: Sequence[JsonCode] = ()

    def to_model(self, extract_urns: bool = False) -> Codelist:
        """Converts a JsonCodelist to a standard codelist."""
        if extract_urns:
            scheme = (
                "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=",
                f"{self.agency}:{self.id}({self.version})",
            )
        else:
            scheme = None
        return Codelist(
            id=self.id,
            name=self.name,
            agency=self.agency,
            description=self.description,
            version=self.version,
            items=[i.to_model(scheme) for i in self.codes],
            annotations=[a.to_model() for a in self.annotations],
            is_external_reference=self.isExternalReference,
            is_partial=self.isPartial,
            valid_from=self.validFrom,
            valid_to=self.validTo,
        )

    @classmethod
    def from_model(self, cl: Codelist) -> "JsonCodelist":
        """Converts a pysdmx codelist to an SDMX-JSON one."""
        if not cl.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON codelists must have a name",
                {"codelist": cl.id},
            )
        return JsonCodelist(
            id=cl.id,
            name=cl.name,
            agency=(
                cl.agency.id if isinstance(cl.agency, Agency) else cl.agency
            ),
            description=cl.description,
            version=cl.version,
            codes=tuple([JsonCode.from_model(i) for i in cl.items]),
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in cl.annotations]
            ),
            isExternalReference=cl.is_external_reference,
            isPartial=cl.is_partial,
            validFrom=cl.valid_from,
            validTo=cl.valid_to,
        )


class JsonValuelist(ItemSchemeType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a valuelist."""

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
            annotations=[a.to_model() for a in self.annotations],
            is_external_reference=self.isExternalReference,
            is_partial=self.isPartial,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            sdmx_type="valuelist",
        )

    @classmethod
    def from_model(self, cl: Codelist) -> "JsonValuelist":
        """Converts a pysdmx codelist to an SDMX-JSON valuelist."""
        if not cl.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON valuelists must have a name",
                {"valuelist": cl.id},
            )
        return JsonValuelist(
            id=cl.id,
            name=cl.name,
            agency=(
                cl.agency.id if isinstance(cl.agency, Agency) else cl.agency
            ),
            description=cl.description,
            version=cl.version,
            valueItems=tuple([JsonCode.from_model(i) for i in cl.items]),
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in cl.annotations]
            ),
            isExternalReference=cl.is_external_reference,
            isPartial=cl.is_partial,
            validFrom=cl.valid_from,
            validTo=cl.valid_to,
        )


class JsonCodelists(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for lists of codes."""

    codelists: Sequence[JsonCodelist] = ()
    valuelists: Sequence[JsonValuelist] = ()


class JsonCodelistMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /codelist queries."""

    data: JsonCodelists

    def to_model(self) -> Codelist:
        """Returns the requested codelist."""
        if self.data.codelists:
            return self.data.codelists[0].to_model()
        else:
            return self.data.valuelists[0].to_model()


class JsonHierarchicalCode(Struct, frozen=True, omit_defaults=True):
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
        if codelists:
            code = self.__find_code(codelists, self.code)
            name = code.name
            description = code.description
        else:
            r = parse_item_urn(self.code)
            code = Code(r.item_id)
            name = None
            description = None
        codes = [c.to_model(codelists) for c in self.hierarchicalCodes]
        vf = self.validFrom.replace(tzinfo=tz.utc) if self.validFrom else None
        vt = self.validTo.replace(tzinfo=tz.utc) if self.validTo else None
        if self.id != code.id:
            a = Annotation(id="hcode", type="pysdmx", text=self.id)
            annotations = [a]
        else:
            annotations = []
        return HierarchicalCode(
            code.id,
            name,
            description,
            code.valid_from,
            code.valid_to,
            vf,
            vt,
            codes,
            tuple(annotations),
            code.urn,
        )

    @classmethod
    def from_model(self, code: HierarchicalCode) -> "JsonHierarchicalCode":
        """Converts a pysdmx hierarchical code to an SDMX-JSON one."""
        if not code.urn:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON hierarchical codes must have the code urn.",
                {"code": code.id},
            )

        annotations = [
            JsonAnnotation.from_model(a)
            for a in code.annotations
            if a.type != "pysdmx"
        ]
        id_ano = [
            a
            for a in code.annotations
            if a.type == "pysdmx" and a.id == "hcode"
        ]
        hid = id_ano[0].value if len(id_ano) > 0 else code.id

        return JsonHierarchicalCode(
            id=hid,
            code=code.urn,
            validFrom=code.rel_valid_from,
            validTo=code.rel_valid_to,
            annotations=tuple(annotations),
            hierarchicalCodes=[
                JsonHierarchicalCode.from_model(c) for c in code.codes
            ],
        )


class JsonHierarchy(ItemSchemeType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a hierarchy."""

    hierarchicalCodes: Sequence[JsonHierarchicalCode] = ()

    def to_model(self, codelists: Sequence[JsonCodelist]) -> Hierarchy:
        """Converts a JsonHierarchy to a standard hierarchy."""
        cls = [cl.to_model(True) for cl in codelists]
        return Hierarchy(
            id=self.id,
            name=self.name,
            agency=self.agency,
            description=self.description,
            version=self.version,
            annotations=[a.to_model() for a in self.annotations],
            is_external_reference=self.isExternalReference,
            is_partial=self.isPartial,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            codes=[i.to_model(cls) for i in self.hierarchicalCodes],
        )

    @classmethod
    def from_model(self, h: Hierarchy) -> "JsonHierarchy":
        """Converts a pysdmx hierarchy to an SDMX-JSON one."""
        if not h.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON hierarchy must have a name",
                {"hierarchy": h.id},
            )
        return JsonHierarchy(
            id=h.id,
            name=h.name,
            agency=(h.agency.id if isinstance(h.agency, Agency) else h.agency),
            description=h.description,
            version=h.version,
            hierarchicalCodes=tuple(
                [JsonHierarchicalCode.from_model(i) for i in h.codes]
            ),
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in h.annotations]
            ),
            isExternalReference=h.is_external_reference,
            isPartial=h.is_partial,
            validFrom=h.valid_from,
            validTo=h.valid_to,
        )


class JsonHierarchies(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for hierarchies."""

    codelists: Sequence[JsonCodelist] = ()
    hierarchies: Sequence[JsonHierarchy] = ()

    def to_model(self) -> Sequence[Hierarchy]:
        """Returns the requested hierarchy."""
        return [h.to_model(self.codelists) for h in self.hierarchies]


class JsonHierarchyAssociation(
    MaintainableType, frozen=True, omit_defaults=True
):
    """SDMX-JSON payload for a hierarchy association."""

    linkedHierarchy: str = ""
    linkedObject: str = ""
    contextObject: str = ""
    links: Sequence[JsonLink] = ()

    def to_model(
        self,
        hierarchies: Sequence[JsonHierarchy],
        codelists: Sequence[JsonCodelist],
    ) -> HierarchyAssociation:
        """Converts a JsonHierarchyAssocation to a standard association."""
        if hierarchies:
            m = find_by_urn(hierarchies, self.linkedHierarchy).to_model(
                codelists
            )
        else:
            m = self.linkedHierarchy
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
            annotations=[a.to_model() for a in self.annotations],
            is_external_reference=self.isExternalReference,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            operator=lnk[0].urn if lnk else None,
        )

    @classmethod
    def from_model(
        self, ha: HierarchyAssociation
    ) -> "JsonHierarchyAssociation":
        """Converts a pysdmx hierarchy association to an SDMX-JSON one."""
        if not ha.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON hierarchy associations must have a name",
                {"hierarchy_association": ha.id},
            )
        if ha.hierarchy is None:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON hierarchy associations must reference a hierarchy",
                {"hierarchy_association": ha.id},
            )
        if not ha.component_ref:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON hierarchy associations must reference a component",
                {"hierarchy_association": ha.id},
            )
        if isinstance(ha.hierarchy, Hierarchy):
            base = "urn:sdmx:org.sdmx.infomodel.codelist."
            href = f"{base}{ha.hierarchy.short_urn}"
        else:
            href = ha.hierarchy
        if not ha.context_ref:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON hierarchy associations must reference a context",
                {"hierarchy_association": ha.id},
            )
        return JsonHierarchyAssociation(
            agency=(
                ha.agency.id if isinstance(ha.agency, Agency) else ha.agency
            ),
            id=ha.id,
            name=ha.name,
            version=ha.version,
            isExternalReference=ha.is_external_reference,
            validFrom=ha.valid_from,
            validTo=ha.valid_to,
            description=ha.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in ha.annotations]
            ),
            linkedHierarchy=href,
            linkedObject=ha.component_ref,
            contextObject=ha.context_ref,
        )


class JsonHierarchyMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /hierarchy queries."""

    data: JsonHierarchies

    def to_model(self) -> Hierarchy:
        """Returns the requested hierarchy."""
        return self.data.to_model()[0]


class JsonHierarchiesMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /hierarchy queries."""

    data: JsonHierarchies

    def to_model(self) -> Sequence[Hierarchy]:
        """Returns the requested hierarchy."""
        return self.data.to_model()


class JsonHierarchyAssociations(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for hierarchy associations."""

    codelists: Sequence[JsonCodelist] = ()
    hierarchies: Sequence[JsonHierarchy] = ()
    hierarchyAssociations: Sequence[JsonHierarchyAssociation] = ()

    def to_model(self) -> Sequence[HierarchyAssociation]:
        """Returns the requested hierarchy associations."""
        return [
            ha.to_model(self.hierarchies, self.codelists)
            for ha in self.hierarchyAssociations
        ]


class JsonHierarchyAssociationMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for hierarchy associations messages."""

    data: JsonHierarchyAssociations

    def to_model(self) -> Sequence[HierarchyAssociation]:
        """Returns the requested hierarchy associations."""
        return self.data.to_model()
