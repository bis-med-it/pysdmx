"""Build SDMX-REST schema queries."""

from enum import Enum
from typing import Optional

import msgspec

from pysdmx.api.qb.structure import _V2_0_ADDED, StructureType
from pysdmx.api.qb.util import ApiVersion, REST_ALL, REST_LATEST
from pysdmx.errors import Invalid


class SchemaContext(Enum):
    """The context for which a schema must be generated."""

    DATA_STRUCTURE = "datastructure"
    METADATA_STRUCTURE = "metadatastructure"
    DATAFLOW = "dataflow"
    METADATA_FLOW = "metadataflow"
    PROVISION_AGREEMENT = "provisionagreement"
    METADATA_PROVISION_AGREEMENT = "metadataprovisionagreement"


class SchemaFormat(Enum):
    """The response formats."""

    SDMX_JSON_1_0_0_SCHEMA = "application/vnd.sdmx.schema+json;version=1.0.0"
    SDMX_JSON_2_0_0_SCHEMA = "application/vnd.sdmx.schema+json;version=2.0.0"
    SDMX_JSON_1_0_0_STRUCTURE = (
        "application/vnd.sdmx.structure+json;version=1.0.0"
    )
    SDMX_JSON_2_0_0_STRUCTURE = (
        "application/vnd.sdmx.structure+json;version=2.0.0"
    )
    SDMX_ML_2_1_SCHEMA = "application/vnd.sdmx.schema+xml;version=2.1"
    SDMX_ML_3_0_SCHEMA = "application/vnd.sdmx.schema+xml;version=3.0.0"
    SDMX_ML_2_1_STRUCTURE = "application/vnd.sdmx.structure+xml;version=2.1"
    SDMX_ML_3_0_STRUCTURE = "application/vnd.sdmx.structure+xml;version=3.0.0"


class SchemaQuery(msgspec.Struct, frozen=True, omit_defaults=True):
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
    """

    context: SchemaContext
    agency_id: str
    resource_id: str
    version: str = REST_LATEST
    obs_dimension: Optional[str] = None
    explicit: bool = False

    def validate(self) -> None:
        """Validate the query."""
        try:
            decoder.decode(encoder.encode(self))
        except msgspec.DecodeError as err:
            raise Invalid("Invalid Schema Query", str(err)) from err

    def get_url(self, version: ApiVersion, omit_defaults: bool = False) -> str:
        """The URL for the query in the selected SDMX-REST API version."""
        self.__validate_query(version)
        if omit_defaults:
            return self.__create_short_query(version)
        else:
            return self.__create_full_query(version)

    def __to_kw(self, val: str, ver: ApiVersion) -> str:
        if val == "~" and ver < ApiVersion.V2_0_0:
            val = "latest"
        return val

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

    def __validate_query(self, version: ApiVersion) -> None:
        self.validate()
        self.__check_context(version)
        self.__check_version()
        self.__check_explicit(version)

    def __create_full_query(self, ver: ApiVersion) -> str:
        u = (
            f"/schema/{self.context.value}/"
            f"{self.agency_id}/{self.resource_id}"
        )
        u += f"/{self.__to_kw(self.version, ver)}"
        if self.obs_dimension or ver < ApiVersion.V2_0_0:
            u += "?"
        if self.obs_dimension:
            u += f"dimensionAtObservation={self.obs_dimension}"
        if ver < ApiVersion.V2_0_0:
            if self.obs_dimension:
                u += "&"
            u += f"explicit={str(self.explicit).lower()}"
        return u

    def __create_short_query(self, ver: ApiVersion) -> str:
        u = (
            f"/schema/{self.context.value}/"
            f"{self.agency_id}/{self.resource_id}"
        )
        if self.version != REST_LATEST:
            u += f"/{self.__to_kw(self.version, ver)}"
        if self.obs_dimension or self.explicit:
            u += "?"
        if self.obs_dimension:
            u += f"dimensionAtObservation={self.obs_dimension}"
        if self.explicit:
            if self.obs_dimension:
                u += "&"
            u += f"explicit={str(self.explicit).lower()}"
        return u


decoder = msgspec.json.Decoder(SchemaQuery)
encoder = msgspec.json.Encoder()


__all__ = ["SchemaContext", "SchemaFormat", "SchemaQuery"]
