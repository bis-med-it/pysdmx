"""Build SDMX-REST registration queries."""

from abc import abstractmethod
from datetime import datetime
from typing import Optional, Sequence, Union

import msgspec
from msgspec.json import Decoder

from pysdmx.api.qb.data import DataContext
from pysdmx.api.qb.util import REST_ALL, ApiVersion
from pysdmx.errors import Invalid
from pysdmx.io.format import RegistryFormat


class _CoreRegistrationQuery(
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
        if version < ApiVersion.V2_1_0:
            raise Invalid(
                "Invalid Request",
                (
                    "Registration are not supported"
                    f"in SDMX-REST {version.value}."
                ),
            )

    def _check_updated_consistency(
        self,
        updated_before: Optional[datetime],
        updated_after: Optional[datetime],
    ) -> None:
        if updated_before and updated_after and updated_before < updated_after:
            raise Invalid(
                "Inconsistent updated timestamps",
                (
                    "The updated_after timestamp should be before "
                    "the updated_before timestamp."
                ),
                csi={
                    "updated_after": str(updated_after),
                    "updated_before": str(updated_before),
                },
            )

    def _join_mult(self, vals: Union[str, Sequence[str]]) -> str:
        return vals if isinstance(vals, str) else ",".join(vals)

    def _create_qs(
        self,
        updated_before: Optional[datetime],
        updated_after: Optional[datetime],
    ) -> str:
        qs = ""
        if updated_before:
            qs += (
                "updatedBefore=" f'{updated_before.isoformat("T", "seconds")}'
            )
        if updated_after:
            if qs:
                qs += "&"
            qs += "updatedAfter=" f'{updated_after.isoformat("T", "seconds")}'
        if qs:
            qs = f"?{qs}"
        return qs

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


class RegistrationByIdQuery(
    _CoreRegistrationQuery,
    frozen=True,
    omit_defaults=True,
):
    """A query for registration, using the registraton ID.

    Attributes:
        registration_id: The registration id(s).
    """

    registration_id: str

    def _validate_query(self, version: ApiVersion) -> None:
        super().validate()
        super()._check_version(version)

    def _get_decoder(self) -> Decoder:  # type: ignore[type-arg]
        return _by_id_decoder

    def _create_full_query(self) -> str:
        return f"/registration/id/{self.registration_id}"

    def _create_short_query(self) -> str:
        return self._create_full_query()


class RegistrationByProviderQuery(
    _CoreRegistrationQuery,
    frozen=True,
    omit_defaults=True,
):
    """A query for registrations by provider.

    Attributes:
        provider_agency_id: The ID of the agency maintaining the data
            provider scheme.
        provider_id: The provider of the registered data.
        updated_before: Returns only registrations updated or created before
            the supplied timestamp.
        updated_after: Returns only registrations updated or created after
            the supplied timestamp.
    """

    provider_agency_id: Union[str, Sequence[str]] = REST_ALL
    provider_id: Union[str, Sequence[str]] = REST_ALL
    updated_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None

    def _validate_query(self, version: ApiVersion) -> None:
        super().validate()
        super()._check_version(version)
        super()._check_updated_consistency(
            self.updated_before, self.updated_after
        )

    def _get_decoder(self) -> Decoder:  # type: ignore[type-arg]
        return _by_prov_decoder

    def _create_full_query(self) -> str:
        a = super()._join_mult(self.provider_agency_id)
        p = super()._join_mult(self.provider_id)
        q = super()._create_qs(self.updated_before, self.updated_after)
        return f"/registration/provider/{a}/{p}{q}"

    def _create_short_query(self) -> str:
        q = super()._create_qs(self.updated_before, self.updated_after)
        p = (
            f"/{super()._join_mult(self.provider_id)}"
            if self.provider_id != REST_ALL
            else ""
        )
        a = (
            f"/{super()._join_mult(self.provider_agency_id)}"
            if self.provider_agency_id != REST_ALL
            else ""
        )
        return f"/registration/provider{a}{p}{q}"


class RegistrationByContextQuery(
    _CoreRegistrationQuery,
    frozen=True,
    omit_defaults=True,
):
    """A query for registrations by context.

    Attributes:
        provider_agency_id: The ID of the agency maintaining the data
            provider scheme.
        provider_id: The provider of the registered data.
        updated_before: Returns only registrations updated or created before
            the supplied timestamp.
        updated_after: Returns only registrations updated or created after
            the supplied timestamp.
    """

    context: DataContext = DataContext.ALL
    agency_id: Union[str, Sequence[str]] = REST_ALL
    resource_id: Union[str, Sequence[str]] = REST_ALL
    version: Union[str, Sequence[str]] = REST_ALL
    updated_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None

    def _validate_query(self, version: ApiVersion) -> None:
        super().validate()
        super()._check_version(version)
        super()._check_updated_consistency(
            self.updated_before, self.updated_after
        )

    def _get_decoder(self) -> Decoder:  # type: ignore[type-arg]
        return _by_ctx_decoder

    def _create_full_query(self) -> str:
        o = f"/{self.context.value}"
        a = super()._join_mult(self.agency_id)
        r = super()._join_mult(self.resource_id)
        v = super()._join_mult(self.version)
        o += f"/{a}/{r}/{v}"
        q = super()._create_qs(self.updated_before, self.updated_after)
        return f"/registration{o}{q}"

    def _create_short_query(self) -> str:
        v = (
            f"/{super()._join_mult(self.version)}"
            if self.version != REST_ALL
            else ""
        )
        r = (
            f"/{super()._join_mult(self.resource_id)}{v}"
            if v or self.resource_id != REST_ALL
            else ""
        )
        a = (
            f"/{super()._join_mult(self.agency_id)}{r}"
            if r or self.agency_id != REST_ALL
            else ""
        )
        c = (
            f"/{self.context.value}{a}"
            if a or self.context != DataContext.ALL
            else ""
        )
        q = super()._create_qs(self.updated_before, self.updated_after)
        return f"/registration{c}{q}"


_by_id_decoder = msgspec.json.Decoder(RegistrationByIdQuery)
_by_ctx_decoder = msgspec.json.Decoder(RegistrationByContextQuery)
_by_prov_decoder = msgspec.json.Decoder(RegistrationByProviderQuery)
_encoder = msgspec.json.Encoder()


__all__ = [
    "RegistrationByIdQuery",
    "RegistrationByProviderQuery",
    "RegistrationByContextQuery",
    "RegistryFormat",
]
