"""Collection of Fusion-JSON schemas for codes and codelists."""

from datetime import datetime, timezone
from typing import Optional, Sequence, Tuple

from msgspec import Struct

from pysdmx.fmr.fusion.core import FusionAnnotation, FusionString
from pysdmx.model import (
    Code,
    Codelist as CL,
    HierarchicalCode,
    Hierarchy as HCL,
)
from pysdmx.util import parse_item_urn


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
            self.id,
            self.names[0].value,
            self.descriptions[0].value if self.descriptions else None,
            vf,
            vt,
        )


class FusionCodelist(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a codelist."""

    id: str
    names: Sequence[FusionString]
    agency: str
    descriptions: Sequence[FusionString] = ()
    version: str = "1.0"
    items: Sequence[FusionCode] = ()

    def to_model(self) -> CL:
        """Converts a JsonCodelist to a standard codelist."""
        return CL(
            self.id,
            self.names[0].value,
            self.agency,
            self.descriptions[0].value if self.descriptions else None,
            self.version,
            [i.to_model() for i in self.items],
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

    def to_model(self, codelists: Sequence[CL]) -> HierarchicalCode:
        """Converts a FusionHierarchicalCode to a hierachical code."""
        code = self.__find_code(codelists, self.code)
        if self.validFrom:
            rvf = datetime.fromtimestamp(self.validFrom / 1000, timezone.utc)
        else:
            rvf = None
        if self.validTo:
            rvt = datetime.fromtimestamp(self.validTo / 1000, timezone.utc)
        else:
            rvt = None
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
            self.id,
            self.names[0].value,
            self.agency,
            self.descriptions[0].value if self.descriptions else None,
            self.version,
            [i.to_model(codelists) for i in self.codes],
        )


class FusionHierarchyMessage(Struct, frozen=True):
    """Fusion-JSON payload for /hierarchy queries."""

    Codelist: Sequence[FusionCodelist] = ()
    Hierarchy: Sequence[FusionHierarchy] = ()

    def to_model(self) -> HCL:
        """Returns the requested hierarchy."""
        cls = [cl.to_model() for cl in self.Codelist]
        return self.Hierarchy[0].to_model(cls)
