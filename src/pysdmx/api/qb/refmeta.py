"""Build SDMX-REST structure queries."""

from abc import abstractmethod
from enum import Enum
from typing import Sequence, Union

import msgspec
from msgspec.json import Decoder

from pysdmx.api.qb.structure import _API_RESOURCES, StructureType
from pysdmx.api.qb.util import (
    ApiVersion,
    REST_ALL,
    REST_LATEST,
)
from pysdmx.errors import Invalid


class RefMetaDetail(Enum):
    """The desired amount of information to be returned."""

    FULL = "full"
    ALL_STUBS = "allstubs"


class RefMetaFormat(Enum):
    """The response formats."""

    SDMX_ML_3_0_STRUCTURE = "application/vnd.sdmx.metadata+xml;version=3.0.0"
    SDMX_JSON_2_0_0 = "application/vnd.sdmx.metadata+json;version=2.0.0"
    SDMX_CSV_2_0_0 = "application/vnd.sdmx.metadata+csv;version=2.0.0"


class _RefMetaCoreQuery(
    msgspec.Struct,
    frozen=True,
    omit_defaults=True,
):
    def get_url(self, version: ApiVersion, omit_defaults: bool = False) -> str:
        """The URL for the query in the selected SDMX-REST API version."""
        self._validate_query(version)
        if omit_defaults:
            return self._create_short_query()
        else:
            return self._create_full_query()

    def validate(self) -> None:
        """Validate the query."""
        try:
            self._get_decoder().decode(_encoder.encode(self))
        except msgspec.DecodeError as err:
            raise Invalid(
                "Invalid Reference Metadata Query", str(err)
            ) from err

    def _check_version(self, version: ApiVersion) -> None:
        if version < ApiVersion.V2_0_0:
            raise Invalid(
                "Invalid Request",
                (
                    "Queries for reference metadata are not supported"
                    f"in SDMX-REST {version.value}."
                ),
            )

    def _join_mult(self, vals: Union[str, Sequence[str]]) -> str:
        return vals if isinstance(vals, str) else ",".join(vals)

    @abstractmethod
    def _get_decoder(self) -> Decoder:  # type: ignore[type-arg]
        """Returns the decoder to be used for validation."""

    @abstractmethod
    def _validate_query(self, version: ApiVersion) -> None:
        """Any additional validation steps to be performed by subclasses."""

    @abstractmethod
    def _create_full_query(self) -> str:
        """Creates a URL, with default values."""

    @abstractmethod
    def _create_short_query(self) -> str:
        """Creates a URL, omitting default values when possible."""


class RefMetaByMetadatasetQuery(
    _RefMetaCoreQuery,
    frozen=True,
    omit_defaults=True,
):
    """A query for reference metadata with metadataset identification details.

    Attributes:
        provider_id: The id(s) of the data provider.
        metadataset_id: The id(s) of the metadataset(s) to be returned.
        version: The version(s) of the metadataset(s) to be returned.
        detail: The desired amount of information to be returned.
    """

    provider_id: Union[str, Sequence[str]] = REST_ALL
    metadataset_id: Union[str, Sequence[str]] = REST_ALL
    version: Union[str, Sequence[str]] = REST_LATEST
    detail: RefMetaDetail = RefMetaDetail.FULL

    def _validate_query(self, version: ApiVersion) -> None:
        super().validate()
        super()._check_version(version)

    def _get_decoder(self) -> Decoder:  # type: ignore[type-arg]
        return _by_mds_decoder

    def _create_full_query(self) -> str:
        p = super()._join_mult(self.provider_id)
        i = super()._join_mult(self.metadataset_id)
        v = super()._join_mult(self.version)
        return f"/metadata/metadataset/{p}/{i}/{v}?detail={self.detail.value}"

    def _create_short_query(self) -> str:
        v = f"/{self.version}" if self.version != REST_LATEST else ""
        i = (
            f"/{self.metadataset_id}{v}"
            if v or self.metadataset_id != REST_ALL
            else ""
        )
        p = (
            f"/{self.provider_id}{i}"
            if i or self.provider_id != REST_ALL
            else ""
        )
        d = f"?{self.detail}" if self.detail != RefMetaDetail.FULL else ""
        return f"/metadata/metadataset{p}{d}"


class RefMetaByStructureQuery(
    _RefMetaCoreQuery,
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

    def _validate_query(self, version: ApiVersion) -> None:
        super().validate()
        super()._check_version(version)
        self.__check_artefact_type(self.artefact_type, version)

    def _get_decoder(self) -> Decoder:  # type: ignore[type-arg]
        return _by_struct_decoder

    def __check_artefact_type(
        self, atyp: StructureType, version: ApiVersion
    ) -> None:
        if atyp not in _API_RESOURCES[version.name.replace("_", ".")]:
            raise Invalid(
                "Validation Error",
                f"{atyp} is not valid for SDMX-REST {version.name}.",
            )

    def _create_full_query(self) -> str:
        a = super()._join_mult(self.agency_id)
        r = super()._join_mult(self.resource_id)
        v = super()._join_mult(self.version)
        return (
            f"/metadata/structure/{self.artefact_type.value}/{a}/{r}/{v}"
            f"?detail={self.detail.value}"
        )

    def _create_short_query(self) -> str:
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


class RefMetaByMetadataflowQuery(
    _RefMetaCoreQuery,
    frozen=True,
    omit_defaults=True,
):
    """A query for reference metadata reported for metadataflows.

    Attributes:
        agency_id: The agency (or agencies) maintaining the metadataflow(s)
            of which reference metadata need to be returned.
        resource_id: The id(s) of the metadataflow(s) of which reference
            metadata need to be returned.
        version: The version(s) of the metadataflows(s) of which reference
            metadata need to be returned.
        provider_id: The id(s) of the providers that provided the reference
            metadata to be returned.
        detail: The desired amount of information to be returned.
    """

    agency_id: Union[str, Sequence[str]] = REST_ALL
    resource_id: Union[str, Sequence[str]] = REST_ALL
    version: Union[str, Sequence[str]] = REST_LATEST
    provider_id: Union[str, Sequence[str]] = REST_ALL
    detail: RefMetaDetail = RefMetaDetail.FULL

    def _validate_query(self, version: ApiVersion) -> None:
        super().validate()
        super()._check_version(version)

    def _get_decoder(self) -> Decoder:  # type: ignore[type-arg]
        return _by_flow_decoder

    def _create_full_query(self) -> str:
        a = super()._join_mult(self.agency_id)
        r = super()._join_mult(self.resource_id)
        v = super()._join_mult(self.version)
        p = super()._join_mult(self.provider_id)
        return (
            f"/metadata/metadataflow/{a}/{r}/{v}/{p}"
            f"?detail={self.detail.value}"
        )

    def _create_short_query(self) -> str:
        p = f"/{self.provider_id}" if self.provider_id != REST_ALL else ""
        v = f"/{self.version}{p}" if p or self.version != REST_LATEST else ""
        r = (
            f"/{self.resource_id}{v}"
            if v or self.resource_id != REST_ALL
            else ""
        )
        a = f"/{self.agency_id}{r}" if r or self.agency_id != REST_ALL else ""
        d = f"?{self.detail}" if self.detail != RefMetaDetail.FULL else ""
        return f"/metadata/metadataflow{a}{d}"


_by_mds_decoder = msgspec.json.Decoder(RefMetaByMetadatasetQuery)
_by_struct_decoder = msgspec.json.Decoder(RefMetaByStructureQuery)
_by_flow_decoder = msgspec.json.Decoder(RefMetaByMetadataflowQuery)
_encoder = msgspec.json.Encoder()


__all__ = [
    "RefMetaDetail",
    "RefMetaFormat",
    "RefMetaByStructureQuery",
]
