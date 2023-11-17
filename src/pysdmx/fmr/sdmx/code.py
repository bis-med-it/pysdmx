"""Collection of SDMX-JSON schemas for codes and codelists."""

from datetime import datetime, timezone as tz
from typing import Optional, Sequence, Tuple

from msgspec import Struct

from pysdmx.fmr.sdmx.core import JsonAnnotation
from pysdmx.model import Code, Codelist, HierarchicalCode, Hierarchy
from pysdmx.util import parse_item_urn


class JsonCode(Struct, frozen=True):
    """SDMX-JSON payload for codes."""

    id: str
    annotations: Sequence[JsonAnnotation] = ()
    name: Optional[str] = None
    description: Optional[str] = None

    def __handle_date(self, datestr: str) -> datetime:
        return datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S%z")

    def __get_val(
        self, a: JsonAnnotation
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        vals = a.title.split("/")
        if a.title.startswith("/"):
            return (None, self.__handle_date(vals[1]))
        else:
            valid_from = self.__handle_date(vals[0])
            valid_to = self.__handle_date(vals[1]) if vals[1] else None
            return (valid_from, valid_to)

    def to_model(self) -> Code:
        """Converts a JsonCode to a standard code."""
        vp = [a for a in self.annotations if a.type == "FR_VALIDITY_PERIOD"]
        vf, vt = self.__get_val(vp[0]) if vp else (None, None)
        return Code(self.id, self.name, self.description, vf, vt)


class JsonCodelist(Struct, frozen=True, rename={"agency": "agencyID"}):
    """SDMX-JSON payload for a codelist."""

    id: str
    name: str
    agency: str
    description: Optional[str] = None
    version: str = "1.0"
    codes: Sequence[JsonCode] = ()

    def to_model(self) -> Codelist:
        """Converts a JsonCodelist to a standard codelist."""
        return Codelist(
            self.id,
            self.name,
            self.agency,
            self.description,
            self.version,
            [i.to_model() for i in self.codes],
        )


class JsonValuelist(Struct, frozen=True, rename={"agency": "agencyID"}):
    """SDMX-JSON payload for a valuelist."""

    id: str
    name: str
    agency: str
    description: Optional[str] = None
    version: str = "1.0"
    valueItems: Sequence[JsonCode] = ()

    def to_model(self) -> Codelist:
        """Converts a JsonValuelist to a standard codelist."""
        return Codelist(
            self.id,
            self.name,
            self.agency,
            self.description,
            self.version,
            [i.to_model() for i in self.valueItems],
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

    code: str
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
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
    hierarchicalCodes: Sequence[JsonHierarchicalCode] = ()

    def to_model(self, codelists: Sequence[Codelist]) -> Hierarchy:
        """Converts a JsonHierarchy to a standard hierarchy."""
        return Hierarchy(
            self.id,
            self.name,
            self.agency,
            self.description,
            self.version,
            [i.to_model(codelists) for i in self.hierarchicalCodes],
        )


class JsonHierarchies(Struct, frozen=True):
    """SDMX-JSON payload for hierarchies."""

    codelists: Sequence[JsonCodelist] = ()
    hierarchies: Sequence[JsonHierarchy] = ()

    def to_model(self) -> Hierarchy:
        """Returns the requested hierarchy."""
        cls = [cl.to_model() for cl in self.codelists]
        return self.hierarchies[0].to_model(cls)


class JsonHierarchyMessage(Struct, frozen=True):
    """SDMX-JSON payload for /hierarchy queries."""

    data: JsonHierarchies

    def to_model(self) -> Hierarchy:
        """Returns the requested hierarchy."""
        return self.data.to_model()
