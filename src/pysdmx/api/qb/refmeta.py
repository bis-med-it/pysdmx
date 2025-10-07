"""Build SDMX-REST reference metadata queries."""

from datetime import datetime
from enum import Enum
from typing import Optional, Sequence, Union

import msgspec
from msgspec.json import Decoder

from pysdmx.api.qb.structure import _API_RESOURCES, StructureType
from pysdmx.api.qb.util import REST_ALL, REST_LATEST, ApiVersion, CoreQuery
from pysdmx.errors import Invalid
from pysdmx.io.format import RefMetaFormat
from pysdmx.model import Reference
from pysdmx.util import parse_urn


class RefMetaDetail(Enum):
    """The desired amount of information to be returned."""

    FULL = "full"
    ALL_STUBS = "allstubs"


class _RefMetaCoreQuery(CoreQuery, frozen=True, omit_defaults=True):
    def _check_version(self, version: ApiVersion) -> None:
        if version < ApiVersion.V2_0_0:
            raise Invalid(
                "Invalid Request",
                (
                    "Queries for reference metadata are not supported"
                    f"in SDMX-REST {version.value}."
                ),
            )

    def _check_as_of(
        self, as_of: Optional[datetime], version: ApiVersion
    ) -> None:
        if as_of and version < ApiVersion.V2_2_0:
            raise Invalid(
                "Validation Error",
                f"as_of not supported in {version.value}.",
            )

    def _get_as_of_value(self, as_of: Optional[datetime]) -> str:
        return f'&asOf={as_of.isoformat("T", "seconds")}' if as_of else ""

    def _get_short_qs(
        self, detail: RefMetaDetail, as_of: Optional[datetime]
    ) -> str:
        qs = ""
        if detail != RefMetaDetail.FULL:
            qs = super()._append_qs_param(qs, detail.value, "detail")
        qs = super()._append_qs_param(
            qs,
            as_of,
            "asOf",
            as_of.isoformat("T", "seconds") if as_of else None,
        )
        if qs:
            qs = f"?{qs}"
        return qs


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
        as_of: Retrieve the metadata as they were at the specified point
            in time (aka time travel).
    """

    provider_id: Union[str, Sequence[str]] = REST_ALL
    metadataset_id: Union[str, Sequence[str]] = REST_ALL
    version: Union[str, Sequence[str]] = REST_LATEST
    detail: RefMetaDetail = RefMetaDetail.FULL
    as_of: Optional[datetime] = None

    @staticmethod
    def from_ref(ref: Union[Reference, str]) -> "RefMetaByMetadatasetQuery":
        """Create a RefMetaByMetadatasetQuery out of the supplied reference.

        Args:
            ref: Either a reference object or an SDMX urn.

        Returns:
            A RefMetaByMetadatasetQuery to retrieve the supplied reference.

        Raises:
            Invalid: If reference is a string and it is not an SDMX urn,
                or if the artefact type is not MetadataSet.
        """
        if isinstance(ref, str):
            ref = parse_urn(ref)  # type: ignore[assignment]
        if ref.sdmx_type != "MetadataSet":  # type: ignore[union-attr]
            raise Invalid(
                "Unexpected artefact type",
                (
                    "Only references of type MetadataSet can be converted"
                    "into a RefMetaByMetadatasetQuery"
                ),
                {"received_type": ref.sdmx_type},  # type: ignore[union-attr]
            )
        return RefMetaByMetadatasetQuery(
            ref.agency,  # type: ignore[union-attr]
            ref.id,  # type: ignore[union-attr]
            ref.version,  # type: ignore[union-attr]
        )

    def _validate_query(self, version: ApiVersion) -> None:
        super().validate()
        super()._check_version(version)
        super()._check_as_of(self.as_of, version)

    def _get_decoder(self) -> Decoder:  # type: ignore[type-arg]
        return _by_mds_decoder

    def _create_full_query(self, ver: ApiVersion) -> str:
        p = super()._join_mult(self.provider_id)
        i = super()._join_mult(self.metadataset_id)
        v = super()._join_mult(self.version)
        ao = super()._get_as_of_value(self.as_of)
        return (
            f"/metadata/metadataset/{p}/{i}/{v}?detail={self.detail.value}{ao}"
        )

    def _create_short_query(self, ver: ApiVersion) -> str:
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
        q = super()._get_short_qs(self.detail, self.as_of)
        return f"/metadata/metadataset{p}{q}"


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
        as_of: Retrieve the metadata as they were at the specified point
            in time (aka time travel).
    """

    artefact_type: StructureType = StructureType.ALL
    agency_id: Union[str, Sequence[str]] = REST_ALL
    resource_id: Union[str, Sequence[str]] = REST_ALL
    version: Union[str, Sequence[str]] = REST_LATEST
    detail: RefMetaDetail = RefMetaDetail.FULL
    as_of: Optional[datetime] = None

    def _validate_query(self, version: ApiVersion) -> None:
        super().validate()
        super()._check_version(version)
        super()._check_as_of(self.as_of, version)
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

    def _create_full_query(self, ver: ApiVersion) -> str:
        a = super()._join_mult(self.agency_id)
        r = super()._join_mult(self.resource_id)
        v = super()._join_mult(self.version)
        ao = super()._get_as_of_value(self.as_of)
        return (
            f"/metadata/structure/{self.artefact_type.value}/{a}/{r}/{v}"
            f"?detail={self.detail.value}{ao}"
        )

    def _create_short_query(self, ver: ApiVersion) -> str:
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
        q = super()._get_short_qs(self.detail, self.as_of)
        return f"/metadata/structure{t}{q}"


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
        as_of: Retrieve the metadata as they were at the specified point
            in time (aka time travel).
    """

    agency_id: Union[str, Sequence[str]] = REST_ALL
    resource_id: Union[str, Sequence[str]] = REST_ALL
    version: Union[str, Sequence[str]] = REST_LATEST
    provider_id: Union[str, Sequence[str]] = REST_ALL
    detail: RefMetaDetail = RefMetaDetail.FULL
    as_of: Optional[datetime] = None

    def _validate_query(self, version: ApiVersion) -> None:
        super().validate()
        super()._check_version(version)
        super()._check_as_of(self.as_of, version)

    def _get_decoder(self) -> Decoder:  # type: ignore[type-arg]
        return _by_flow_decoder

    def _create_full_query(self, ver: ApiVersion) -> str:
        a = super()._join_mult(self.agency_id)
        r = super()._join_mult(self.resource_id)
        v = super()._join_mult(self.version)
        p = super()._join_mult(self.provider_id)
        ao = super()._get_as_of_value(self.as_of)
        return (
            f"/metadata/metadataflow/{a}/{r}/{v}/{p}"
            f"?detail={self.detail.value}{ao}"
        )

    def _create_short_query(self, ver: ApiVersion) -> str:
        p = f"/{self.provider_id}" if self.provider_id != REST_ALL else ""
        v = f"/{self.version}{p}" if p or self.version != REST_LATEST else ""
        r = (
            f"/{self.resource_id}{v}"
            if v or self.resource_id != REST_ALL
            else ""
        )
        a = f"/{self.agency_id}{r}" if r or self.agency_id != REST_ALL else ""
        q = super()._get_short_qs(self.detail, self.as_of)
        return f"/metadata/metadataflow{a}{q}"


_by_mds_decoder = msgspec.json.Decoder(RefMetaByMetadatasetQuery)
_by_struct_decoder = msgspec.json.Decoder(RefMetaByStructureQuery)
_by_flow_decoder = msgspec.json.Decoder(RefMetaByMetadataflowQuery)


__all__ = [
    "RefMetaDetail",
    "RefMetaFormat",
    "RefMetaByMetadataflowQuery",
    "RefMetaByMetadatasetQuery",
    "RefMetaByStructureQuery",
]
