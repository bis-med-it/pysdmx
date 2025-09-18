"""Collection of SDMX-JSON schemas for organisations."""

from collections import defaultdict
from typing import Dict, Sequence, Set

import msgspec

from pysdmx.io.json.sdmxjson2.messages.core import (
    ItemSchemeType,
    JsonAnnotation,
)
from pysdmx.io.json.sdmxjson2.messages.dataflow import JsonDataflow
from pysdmx.model import Agency, AgencyScheme, DataflowRef


def _sanitize_agency(agency: Agency, is_sdmx_scheme: bool) -> Agency:
    if is_sdmx_scheme:
        nid = agency.id
    else:
        nid = agency.id[agency.id.rindex(".") + 1 :]
    return msgspec.structs.replace(agency, id=nid, dataflows=())


class JsonAgencyScheme(ItemSchemeType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for an agency scheme."""

    agencies: Sequence[Agency] = ()

    def __add_owner(
        self, owner: str, a: Agency, dfowners: Dict[str, Set[DataflowRef]]
    ) -> Agency:
        oid = f"{owner}.{a.id}" if owner != "SDMX" else a.id
        flows = list(dfowners[oid]) if dfowners else []
        return Agency(
            id=oid,
            name=a.name,
            description=a.description,
            contacts=a.contacts,
            dataflows=flows,
            annotations=tuple([a.to_model() for a in self.annotations]),
        )

    def to_model(self, dataflows: Sequence[JsonDataflow]) -> AgencyScheme:
        """Returns the requested list of agencies."""
        dfowners: Dict[str, Set[DataflowRef]] = defaultdict(set)
        if dataflows:
            for df in dataflows:
                dfref = DataflowRef(df.agency, df.id, df.version, df.name)
                dfowners[df.agency].add(dfref)
        agencies = [
            self.__add_owner(self.agency, a, dfowners) for a in self.agencies
        ]
        return AgencyScheme(
            description=self.description,
            agency=self.agency,
            items=agencies,
            annotations=tuple([a.to_model() for a in self.annotations]),
            is_external_reference=self.isExternalReference,
            is_partial=self.isPartial,
            valid_from=self.validFrom,
            valid_to=self.validTo,
        )

    @classmethod
    def from_model(self, asc: AgencyScheme) -> "JsonAgencyScheme":
        """Converts a pysdmx agency scheme to an SDMX-JSON one."""
        agency = (
            asc.agency.id if isinstance(asc.agency, Agency) else asc.agency
        )
        is_sdmx_scheme = agency == "SDMX"
        children = [_sanitize_agency(a, is_sdmx_scheme) for a in asc.items]

        return JsonAgencyScheme(
            id="AGENCIES",
            name="AGENCIES",
            agency=agency,
            description=asc.description,
            version="1.0",
            agencies=children,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in asc.annotations]
            ),
            isExternalReference=asc.is_external_reference,
            isPartial=asc.is_partial,
            validFrom=asc.valid_from,
            validTo=asc.valid_to,
        )


class JsonAgencySchemes(msgspec.Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of agency schemes."""

    agencySchemes: Sequence[JsonAgencyScheme]
    dataflows: Sequence[JsonDataflow] = ()

    def to_model(self) -> Sequence[AgencyScheme]:
        """Returns the requested agency schemes."""
        return [a.to_model(self.dataflows) for a in self.agencySchemes]


class JsonAgencyMessage(msgspec.Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /agencyscheme queries."""

    data: JsonAgencySchemes

    def to_model(self) -> Sequence[AgencyScheme]:
        """Returns the requested agency schemes."""
        return self.data.to_model()
