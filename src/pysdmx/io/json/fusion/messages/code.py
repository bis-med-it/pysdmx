"""Collection of Fusion-JSON schemas for codes and codelists."""

from datetime import datetime, timedelta, timezone as tz
from typing import Optional, Sequence, Tuple

from msgspec import Struct

from pysdmx.io.json.fusion.messages.core import (
    FusionAnnotation,
    FusionLink,
    FusionString,
)
from pysdmx.model import (
    Code,
    Codelist as CL,
    HierarchicalCode,
    Hierarchy as HCL,
    HierarchyAssociation as HA,
)
from pysdmx.util import find_by_urn, parse_item_urn


class FusionCode(Struct, frozen=True):
    """Fusion-JSON payload for codes."""

    id: str
    annotations: Sequence[FusionAnnotation] = ()
    names: Sequence[FusionString] = ()
    descriptions: Sequence[FusionString] = ()

    def __handle_date(self, datestr: str) -> datetime:
        return datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S%z")

    def __get_val(
        self, a: FusionAnnotation
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        vals = a.title.split("/")
        if a.title.startswith("/"):
            return (None, self.__handle_date(vals[1]))
        else:
            valid_from = self.__handle_date(vals[0])
            valid_to = self.__handle_date(vals[1]) if vals[1] else None
            return (valid_from, valid_to)

    def to_model(self) -> Code:
        """Converts a FusionCode to a standard code."""
        vp = [a for a in self.annotations if a.type == "FR_VALIDITY_PERIOD"]
        vf, vt = self.__get_val(vp[0]) if vp else (None, None)
        return Code(
            id=self.id,
            name=self.names[0].value,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            valid_from=vf,
            valid_to=vt,
        )


class FusionCodelist(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a codelist."""

    id: str
    urn: str
    names: Sequence[FusionString]
    agency: str
    descriptions: Sequence[FusionString] = ()
    version: str = "1.0"
    items: Sequence[FusionCode] = ()

    def to_model(self) -> CL:
        """Converts a JsonCodelist to a standard codelist."""
        t = "codelist" if "Codelist" in self.urn else "valuelist"
        return CL(
            id=self.id,
            name=self.names[0].value,
            agency=self.agency,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            version=self.version,
            items=[i.to_model() for i in self.items],
            sdmx_type=t,  # type: ignore[arg-type]
        )


class FusionCodelistMessage(Struct, frozen=True):
    """Fusion-JSON payload for /codelist queries."""

    Codelist: Sequence[FusionCodelist] = ()
    ValueList: Sequence[FusionCodelist] = ()

    def to_model(self) -> CL:
        """Returns the requested codelist."""
        if self.Codelist:
            return self.Codelist[0].to_model()
        else:
            return self.ValueList[0].to_model()


class FusionHierarchicalCode(Struct, frozen=True):
    """Fusion-JSON payload for hierarchical codes."""

    code: str
    validFrom: Optional[int] = None
    validTo: Optional[int] = None
    codes: Sequence["FusionHierarchicalCode"] = ()

    def __find_code(self, codelists: Sequence[CL], urn: str) -> Code:
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

    def __convert_epoch(self, epoch: int) -> datetime:
        if epoch < 0:
            return datetime(1970, 1, 1, tzinfo=tz.utc) + timedelta(
                milliseconds=epoch
            )
        else:
            return datetime.fromtimestamp(epoch / 1000, tz.utc)

    def to_model(self, codelists: Sequence[CL]) -> HierarchicalCode:
        """Converts a FusionHierarchicalCode to a hierachical code."""
        code = self.__find_code(codelists, self.code)
        rvf = self.__convert_epoch(self.validFrom) if self.validFrom else None
        rvt = self.__convert_epoch(self.validTo) if self.validTo else None
        codes = [c.to_model(codelists) for c in self.codes]
        return HierarchicalCode(
            code.id,
            code.name,
            code.description,
            code.valid_from,
            code.valid_to,
            rvf,
            rvt,
            codes,
        )


class FusionHierarchy(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a hierarchy."""

    id: str
    names: Sequence[FusionString]
    agency: str
    descriptions: Sequence[FusionString] = ()
    version: str = "1.0"
    codes: Sequence[FusionHierarchicalCode] = ()

    def to_model(self, codelists: Sequence[CL]) -> HCL:
        """Converts a FusionHierarchy to a standard hierarchy."""
        return HCL(
            id=self.id,
            name=self.names[0].value,
            agency=self.agency,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            version=self.version,
            codes=[i.to_model(codelists) for i in self.codes],
        )


class FusionHierarchyAssociation(
    Struct, frozen=True, rename={"agency": "agencyId"}
):
    """Fusion-JSON payload for a hierarchy association."""

    id: str
    names: Sequence[FusionString]
    agency: str
    hierarchyRef: str
    linkedStructureRef: str
    contextRef: str
    links: Sequence[FusionLink] = ()
    descriptions: Sequence[FusionString] = ()
    version: str = "1.0"

    def to_model(
        self,
        hierarchies: Sequence[FusionHierarchy],
        codelists: Sequence[FusionCodelist],
    ) -> HA:
        """Converts a FusionHierarchyAssocation to a standard association."""
        cls = [cl.to_model() for cl in codelists]
        m = find_by_urn(hierarchies, self.hierarchyRef).to_model(cls)
        return HA(
            id=self.id,
            name=self.names[0].value,
            agency=self.agency,
            hierarchy=m,
            component_ref=self.linkedStructureRef,
            context_ref=self.contextRef,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            version=self.version,
            operator=self.links[0].urn if self.links else None,
        )


class FusionHierarchyMessage(Struct, frozen=True):
    """Fusion-JSON payload for /hierarchy queries."""

    Codelist: Sequence[FusionCodelist] = ()
    Hierarchy: Sequence[FusionHierarchy] = ()

    def to_model(self) -> HCL:
        """Returns the requested hierarchy."""
        cls = [cl.to_model() for cl in self.Codelist]
        return self.Hierarchy[0].to_model(cls)


class FusionHierarchyAssociationMessage(Struct, frozen=True):
    """Fusion-JSON payload for hierarchy associations."""

    Codelist: Sequence[FusionCodelist] = ()
    Hierarchy: Sequence[FusionHierarchy] = ()
    HierarchyAssociation: Sequence[FusionHierarchyAssociation] = ()

    def to_model(self) -> Sequence[HA]:
        """Returns the requested hierarchy associations."""
        return [
            ha.to_model(self.Hierarchy, self.Codelist)
            for ha in self.HierarchyAssociation
        ]
