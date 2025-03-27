"""Build SDMX-REST schema queries."""

from datetime import datetime
from enum import Enum
from typing import Optional

import msgspec
from msgspec.json import Decoder

from pysdmx.api.qb.structure import _V2_0_ADDED, StructureType
from pysdmx.api.qb.util import REST_ALL, REST_LATEST, ApiVersion, CoreQuery
from pysdmx.errors import Invalid
from pysdmx.io.format import SchemaFormat


class SchemaContext(Enum):
    """The context for which a schema must be generated."""

    DATA_STRUCTURE = "datastructure"
    METADATA_STRUCTURE = "metadatastructure"
    DATAFLOW = "dataflow"
    METADATA_FLOW = "metadataflow"
    PROVISION_AGREEMENT = "provisionagreement"
    METADATA_PROVISION_AGREEMENT = "metadataprovisionagreement"


class SchemaQuery(CoreQuery, frozen=True, omit_defaults=True):
    """A schema query.

    Schema queries allow retrieving the definition of data validity for a
    certain context. The service must take into account the constraints
    that apply within that context (e.g. dataflow).

    Attributes:
        context: The context for which a schema must be generated. This
            determines the constraints that will be taken into
            consideration.
        agency_id: The agency maintaining the context to be considered.
        resource_id: The id of the context to be considered.
        version: The version of the context to be considered.
        obs_dimension: The ID of the dimension at the observation level.
        explicit: For cross-sectional data validation, indicates whether
            observations are strongly typed.
        deletion: Whether the schema will be used to validate deletion
            messages.
        as_of: Retrieve the schema as it was at the specified point
            in time (aka time travel).
    """

    context: SchemaContext
    agency_id: str
    resource_id: str
    version: str = REST_LATEST
    obs_dimension: Optional[str] = None
    explicit: bool = False
    deletion: bool = False
    as_of: Optional[datetime] = None

    def __check_context(self, version: ApiVersion) -> None:
        ct = StructureType(self.context.value)
        if version < ApiVersion.V2_0_0 and ct in _V2_0_ADDED:
            raise Invalid(
                "Validation Error",
                f"{self.context} not allowed in {version.value}.",
            )

    def __check_version(self) -> None:
        if self.version == REST_ALL:
            raise Invalid(
                "Validation Error",
                "Retrieving schemas for all versions is not allowed.",
            )

    def __check_explicit(self, version: ApiVersion) -> None:
        if self.explicit and version >= ApiVersion.V2_0_0:
            raise Invalid(
                "Validation Error",
                f"Explicit parameter is not supported in {version.value}.",
            )

    def __check_as_of(self, version: ApiVersion) -> None:
        if self.as_of and version < ApiVersion.V2_2_0:
            raise Invalid(
                "Validation Error",
                f"as_of not supported in {version.value}.",
            )

    def __check_deletion(self, version: ApiVersion) -> None:
        if self.deletion and version < ApiVersion.V2_2_0:
            raise Invalid(
                "Validation Error",
                f"deletion parameter is not supported in {version.value}.",
            )

    def _validate_query(self, version: ApiVersion) -> None:
        self.validate()
        self.__check_context(version)
        self.__check_version()
        self.__check_explicit(version)
        self.__check_as_of(version)
        self.__check_deletion(version)

    def _create_full_query(self, ver: ApiVersion) -> str:
        u = (
            f"/schema/{self.context.value}/"
            f"{self.agency_id}/{self.resource_id}"
        )
        u += f"/{self._to_kw(self.version, ver)}"
        if (
            self.obs_dimension
            or self.as_of
            or ver < ApiVersion.V2_0_0
            or ver >= ApiVersion.V2_2_0
        ):
            u += "?"
        if self.obs_dimension:
            u += f"dimensionAtObservation={self.obs_dimension}"
        if ver < ApiVersion.V2_0_0:
            if self.obs_dimension:
                u += "&"
            u += f"explicit={str(self.explicit).lower()}"
        if self.as_of:
            if self.obs_dimension:
                u += "&"
            u += f'asOf={self.as_of.isoformat("T", "seconds")}'
        if ver >= ApiVersion.V2_2_0:
            if self.obs_dimension or self.as_of:
                u += "&"
            u += f"deletion={str(self.deletion).lower()}"
        return u

    def _create_short_query(self, ver: ApiVersion) -> str:
        u = (
            f"/schema/{self.context.value}/"
            f"{self.agency_id}/{self.resource_id}"
        )
        if self.version != REST_LATEST:
            u += f"/{self._to_kw(self.version, ver)}"
        if self.obs_dimension or self.explicit or self.as_of or self.deletion:
            u += "?"
        if self.obs_dimension:
            u += f"dimensionAtObservation={self.obs_dimension}"
        if self.explicit:
            if self.obs_dimension:
                u += "&"
            u += f"explicit={str(self.explicit).lower()}"
        if self.as_of:
            if self.obs_dimension:
                u += "&"
            u += f'asOf={self.as_of.isoformat("T", "seconds")}'
        if self.deletion:
            if self.obs_dimension or self.as_of:
                u += "&"
            u += f"deletion={str(self.deletion).lower()}"
        return u

    def _get_decoder(self) -> Decoder:  # type: ignore[type-arg]
        return _decoder


_decoder = msgspec.json.Decoder(SchemaQuery)

__all__ = ["SchemaContext", "SchemaFormat", "SchemaQuery"]
