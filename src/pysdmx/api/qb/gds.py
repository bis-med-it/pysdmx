"""Build GDS-REST structure queries."""

from enum import Enum
from typing import Literal, Optional, Sequence, Union

import msgspec

from pysdmx.api.qb.util import (
    REST_ALL,
    REST_LATEST,
)
from pysdmx.errors import Invalid


class GdsType(Enum):
    """The type of GDS metadata to be returned."""

    GDS_AGENCY = "agency"
    GDS_CATALOG = "catalog"
    GDS_SDMX_API = "sdmxapi"
    GDS_SERVICE = "service"
    GDS_URN_RESOLVER = "urn_resolver"
    ALL = REST_ALL
    LATEST = REST_LATEST


_RESOURCES = {
    GdsType.GDS_AGENCY,
    GdsType.GDS_CATALOG,
    GdsType.GDS_SDMX_API,
    GdsType.GDS_SERVICE,
    GdsType.GDS_URN_RESOLVER,
}


class GdsQuery(msgspec.Struct, frozen=True, omit_defaults=True):
    """A query for base GDS metadata.

    Attributes:
        artefact_type: The type of GDS metadata to be returned.
        agency: The agency (or agencies) maintaining the artefact(s)
            to be returned.
        resource_id: The resource ID(s) to query. Defaults to '*'.
        version: The version(s) of the resource. Defaults to '*'.
        resource_type: Filters the endpoints that support
          the requested resource type (eg, 'data', 'metadata').
        message_format: Filters the endpoints that support any
          of the requested message formats.

        api_version: Filters the endpoints that is in a
          specific SDMX API version.
          Multiple values separated by commas are possible.
          By default (if nothing is sent) it returns everything.

        detail: The amount of information to be returned.
            Option full: All available information for all artefacts
              should be returned.
            Option raw: Any nested service will be referenced.

        references: Instructs the web service to return
          (or not) the artefacts referenced by the
          artefact to be returned.

            Option none: No referenced artefacts will be returned.
            Option children: Returns the artefacts
              referenced by the artefact to be returned.
    """

    artefact_type: GdsType
    agency: Union[str, Sequence[str]] = REST_ALL
    resource_id: Union[str, Sequence[str]] = REST_ALL
    version: Optional[str] = None
    resource_type: Optional[Literal["data", "metadata"]] = None
    message_format: Optional[Literal["json", "csv", "xml"]] = None
    api_version: Optional[str] = None
    detail: Optional[Literal["full", "raw"]] = None
    references: Optional[Literal["none", "children"]] = None

    def validate(self) -> None:
        """Validate the query."""
        try:
            decoder.decode(encoder.encode(self))
        except msgspec.DecodeError as err:
            raise Invalid("Invalid Structure Query", str(err)) from err

    def _get_base_url(self) -> str:
        """The URL for the query in the GDS-REST API."""
        self.__validate_query()
        return self.__create_query()

    def get_url(self) -> str:
        """The URL for the query in the GDS-REST API."""
        base_url = self._get_base_url()
        params = []
        if self.resource_type:
            params.append(f"resource_type={self.resource_type}")
        if self.message_format:
            params.append(f"message_format={self.message_format}")
        if self.api_version:
            params.append(f"api_version={self.api_version}")
        if self.detail:
            params.append(f"detail={self.detail}")
        if self.references:
            params.append(f"references={self.references}")
        query_string = f"/?{'&'.join(params)}" if params else ""
        return f"{base_url}{query_string}"

    def __validate_query(self) -> None:
        self.validate()
        self.__check_artefact_type(self.artefact_type)

    def __check_artefact_type(self, atyp: GdsType) -> None:
        if atyp not in _RESOURCES:
            raise Invalid(
                "Validation Error",
                f"{atyp} is not valid for GDS-REST.",
            )

    def __to_type_kw(self, val: GdsType) -> str:
        return val.value

    def __to_kw(self, val: str) -> str:
        return val

    def __to_kws(self, vals: Union[str, Sequence[str]]) -> str:
        vals = [vals] if isinstance(vals, str) else vals
        mapped = [self.__to_kw(v) for v in vals]
        sep = ","
        return sep.join(mapped)

    def __create_query(self) -> str:
        t = self.__to_type_kw(self.artefact_type)
        a = self.__to_kws(self.agency)
        r = self.__to_kws(self.resource_id)
        v = self.__to_kws(self.version) if self.version else REST_ALL

        if t in ("sdmxapi", "agency", "urn_resolver"):
            return f"/{t}/{r}"

        vu = f"/{v}" if v != REST_ALL else ""
        ru = f"/{r}{vu}" if vu or self.resource_id != REST_ALL else ""
        au = f"/{a}{ru}" if ru or self.agency != REST_ALL else ""

        return f"/{t}{au}"


decoder = msgspec.json.Decoder(GdsQuery)
encoder = msgspec.json.Encoder()


__all__ = [
    "GdsQuery",
]
