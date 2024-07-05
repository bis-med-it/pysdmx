"""Build SDMX-REST structure queries."""

from enum import Enum
from typing import Sequence, Union

import msgspec

from pysdmx.api.qb.structure import _API_RESOURCES, StructureType
from pysdmx.api.qb.util import (
    ApiVersion,
    check_multiple_items,
    REST_ALL,
    REST_LATEST,
)
from pysdmx.errors import ClientError


class RefMetaDetail(Enum):
    """The desired amount of information to be returned."""

    FULL = "full"
    ALL_STUBS = "allstubs"


class RefMetaFormat(Enum):
    """The response formats."""

    SDMX_ML_3_0_STRUCTURE = "application/vnd.sdmx.metadata+xml;version=3.0.0"
    SDMX_JSON_2_0_0 = "application/vnd.sdmx.metadata+json;version=2.0.0"
    SDMX_CSV_2_0_0 = "application/vnd.sdmx.metadata+csv;version=2.0.0"


class RefMetaByStructureQuery(
    msgspec.Struct,
    frozen=True,
    omit_defaults=True,
):
    """A query for reference metadata reported against one or more structures.

    Attributes:
        artefact_type: The type of structural metadata to which the
            reference metadata to be returned are attached.
        agency_id: The agency (or agencies) maintaining the artefact(s)
            to which the reference metadata to be returned are attached.
        resource_id: The id(s) of the artefact(s) to which the reference
            metadata to be returned are attached.
        version: The version(s) of the artefact(s) to which the reference
            metadata to be returned are attached.
        detail: The desired amount of information to be returned.
    """

    artefact_type: StructureType = StructureType.ALL
    agency_id: Union[str, Sequence[str]] = REST_ALL
    resource_id: Union[str, Sequence[str]] = REST_ALL
    version: Union[str, Sequence[str]] = REST_LATEST
    detail: RefMetaDetail = RefMetaDetail.FULL

    def validate(self) -> None:
        """Validate the query."""
        try:
            decoder.decode(encoder.encode(self))
        except msgspec.DecodeError as err:
            raise ClientError(
                422, "Invalid Reference Metadata Query", str(err)
            ) from err

    def get_url(self, version: ApiVersion, omit_defaults: bool = False) -> str:
        """The URL for the query in the selected SDMX-REST API version."""
        self.__validate_query(version)
        if omit_defaults:
            return self.__create_short_query()
        else:
            return self.__create_full_query()

    def __validate_query(self, version: ApiVersion) -> None:
        self.validate()
        self.__check_version(version)
        self.__check_multiple_items(version)
        self.__check_artefact_type(self.artefact_type, version)

    def __check_multiple_items(self, version: ApiVersion) -> None:
        check_multiple_items(self.agency_id, version)
        check_multiple_items(self.resource_id, version)
        check_multiple_items(self.version, version)

    def __check_artefact_type(
        self, atyp: StructureType, version: ApiVersion
    ) -> None:
        if atyp not in _API_RESOURCES[version.value.label]:
            raise ClientError(
                422,
                "Validation Error",
                f"{atyp} is not valid for SDMX-REST {version.value}.",
            )

    def __check_version(self, version: ApiVersion) -> None:
        if version < ApiVersion.V2_0_0:
            raise ClientError(
                422,
                "Invalid Request",
                (
                    "Queries for reference metadata are not supported"
                    f"in SDMX-REST {version.value}."
                ),
            )

    def __join_mult(self, vals: Union[str, Sequence[str]]) -> str:
        return vals if isinstance(vals, str) else ",".join(vals)

    def __create_full_query(self) -> str:
        a = self.__join_mult(self.agency_id)
        r = self.__join_mult(self.resource_id)
        v = self.__join_mult(self.version)
        return (
            f"/metadata/structure/{self.artefact_type.value}/{a}/{r}/{v}"
            f"?detail={self.detail.value}"
        )

    def __create_short_query(self) -> str:
        v = f"/{self.version}" if self.version != REST_LATEST else ""
        r = (
            f"/{self.resource_id}{v}"
            if v or self.resource_id != REST_ALL
            else ""
        )
        a = f"/{self.agency_id}{r}" if r or self.agency_id != REST_ALL else ""
        t = (
            f"/{self.artefact_type.value}{a}"
            if a or self.artefact_type != StructureType.ALL
            else ""
        )
        d = f"?{self.detail}" if self.detail != RefMetaDetail.FULL else ""
        return f"/metadata/structure{t}{d}"


decoder = msgspec.json.Decoder(RefMetaByStructureQuery)
encoder = msgspec.json.Encoder()


__all__ = [
    "RefMetaDetail",
    "RefMetaFormat",
    "RefMetaByStructureQuery",
]
