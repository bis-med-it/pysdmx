"""Build SDMX-REST structure queries."""

from enum import Enum
from typing import Sequence, Union, Optional

import msgspec

from pysdmx.api.qb.util import (
    REST_ALL,
    REST_LATEST,
    ApiVersion,
    check_multiple_items,
)
from pysdmx.errors import Invalid


class GdsType(Enum):
    """The type of GDS metadata to be returned."""

    GDS_AGENCY = "agency"
    GDS_CATALOG = "catalog"
    GDS_SERVICE = "service"
    ALL = REST_ALL
    LATEST = REST_LATEST

_V2_0_RESOURCES = {
    GdsType.GDS_AGENCY,
    GdsType.GDS_CATALOG,
    GdsType.GDS_SERVICE,
}

_API_RESOURCES = {
    "V2.0.0": _V2_0_RESOURCES,
    "V2.1.0": _V2_0_RESOURCES,
    "LATEST": _V2_0_RESOURCES,
}


class GdsQuery(msgspec.Struct, frozen=True, omit_defaults=True):
    """A query for base GDS metadata.

    Attributes:
        artefact_type: The type of GDS metadata to be returned.
        agency_id: The agency (or agencies) maintaining the artefact(s)
            to be returned.
        resource_id: The id(s) of the artefact(s) to be returned.
        version: The version(s) of the artefact(s) to be returned.
    """

    artefact_type: GdsType
    agency_id: Union[str, Sequence[str]] = REST_ALL
    resource_id: Union[str, Sequence[str]] = REST_ALL
    version: Union[str, Sequence[str]] = REST_LATEST
    resource_type: Optional[str] = None
    message_format: Optional[str] = None
    api_version: Optional[str] = None
    detail: Optional[str] = None
    references: Optional[str] = None

    def validate(self) -> None:
        """Validate the query."""
        try:
            decoder.decode(encoder.encode(self))
        except msgspec.DecodeError as err:
            raise Invalid("Invalid Structure Query", str(err)) from err

    def _get_base_url(self, version: ApiVersion, omit_defaults: bool = False) -> str:
        """The URL for the query in the selected SDMX-REST API version."""
        self.__validate_query(version)
        if omit_defaults:
            return self.__create_short_query(version)
        else:
            return self.__create_full_query(version)

    def get_url(self, version: ApiVersion, omit_defaults: bool = False) -> str:
        """The URL for the query in the selected SDMX-REST API version."""
        base_url = self._get_base_url(version, omit_defaults)
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

    def __validate_query(self, version: ApiVersion) -> None:
        self.validate()
        self.__check_multiple_items(version)
        self.__check_artefact_type(self.artefact_type, version)

    def __check_multiple_items(self, version: ApiVersion) -> None:
        check_multiple_items(self.agency_id, version)
        check_multiple_items(self.resource_id, version)
        check_multiple_items(self.version, version)

    def __check_artefact_type(
        self, atyp: GdsType, version: ApiVersion
    ) -> None:
        if atyp not in _API_RESOURCES[version.name.replace("_", ".")]:
            raise Invalid(
                "Validation Error",
                f"{atyp} is not valid for SDMX-REST {version.name}.",
            )

    def __to_type_kw(self, val: GdsType, ver: ApiVersion) -> str:
        if val == GdsType.ALL and ver < ApiVersion.V2_0_0:
            out = ""
        else:
            out = val.value
        return out

    def __to_kw(self, val: str, ver: ApiVersion) -> str:
        if val == "*" and ver < ApiVersion.V2_0_0:
            val = "all"
        elif val == "~" and ver < ApiVersion.V2_0_0:
            val = "latest"
        return val

    def __to_kws(
        self, vals: Union[str, Sequence[str]], ver: ApiVersion
    ) -> str:
        vals = [vals] if isinstance(vals, str) else vals
        mapped = [self.__to_kw(v, ver) for v in vals]
        sep = "+" if ver < ApiVersion.V2_0_0 else ","
        return sep.join(mapped)

    def __create_full_query(self, ver: ApiVersion) -> str:
        t = self.__to_type_kw(self.artefact_type, ver)
        a = self.__to_kws(self.agency_id, ver)
        r = self.__to_kws(self.resource_id, ver)
        v = self.__to_kws(self.version, ver)
        return f"{t}/{a}/{r}/{v}"

    def __create_short_query(self, ver: ApiVersion) -> str:
        t = self.__to_type_kw(self.artefact_type, ver)
        a = self.__to_kws(self.agency_id, ver)
        r = self.__to_kws(self.resource_id, ver)
        v = self.__to_kws(self.version, ver)

        vu = f"/{v}" if self.version != REST_LATEST else ""
        ru = f"/{r}{vu}" if vu or self.resource_id != REST_ALL else ""
        au = f"/{a}{ru}" if ru or self.agency_id != REST_ALL else ""

        return f"/{t}{au}"


decoder = msgspec.json.Decoder(GdsQuery)
encoder = msgspec.json.Encoder()


__all__ = [
    "ApiVersion",
    "GdsQuery",
]
