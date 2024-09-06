"""Build SDMX-REST data queries."""

from datetime import datetime
from enum import Enum
from typing import Optional, Sequence, Union

import msgspec

from pysdmx.api.dc.query import (
    MultiFilter,
    NumberFilter,
    TextFilter,
)
from pysdmx.api.qb.data import _CoreDataQuery, DataContext
from pysdmx.api.qb.structure import StructureReference
from pysdmx.api.qb.util import (
    ApiVersion,
    check_multiple_data_context,
    REST_ALL,
)
from pysdmx.errors import Invalid


class AvailabilityMode(str, Enum):
    """The mode of a data availability query."""

    AVAILABLE = "available"
    EXACT = "exact"


class AvailabilityFormat(Enum):
    """The response formats for availabillity queries."""

    SDMX_ML_2_1_STRUCTURE = "application/vnd.sdmx.structure+xml;version=2.1"
    SDMX_ML_3_0_STRUCTURE = "application/vnd.sdmx.structure+xml;version=3.0.0"
    SDMX_JSON_1_0_0 = "application/vnd.sdmx.structure+json;version=1.0.0"
    SDMX_JSON_2_0_0 = "application/vnd.sdmx.structure+json;version=2.0.0"


REFERENCES_V1 = [
    StructureReference.ALL,
    StructureReference.NONE,
    StructureReference.CODELIST,
    StructureReference.CONCEPT_SCHEME,
    StructureReference.DATAFLOW,
    StructureReference.DATA_PROVIDER_SCHEME,
    StructureReference.DATA_STRUCTURE,
]

REFERENCES_V2 = [
    StructureReference.ALL,
    StructureReference.NONE,
    StructureReference.CODELIST,
    StructureReference.CONCEPT_SCHEME,
    StructureReference.DATAFLOW,
    StructureReference.DATA_PROVIDER_SCHEME,
    StructureReference.DATA_STRUCTURE,
    StructureReference.VALUE_LIST,
]


class AvailabilityQuery(_CoreDataQuery, frozen=True, omit_defaults=True):
    """A data availability query.

    Availability queries allow to see what data are available for a
    specific context (data structure, dataflow or provision agreement).

    Attributes:
        context: The context for which data must be retrieved.
        agency_id: The agency maintaining the context to be considered.
        resource_id: The id of the context to be considered.
        version: The version of the context to be considered.
        key: The combination of dimension values identifying the slice
            of the cube for which data should be returned. Wildcarding
            is supported via the * operator.
        component_id: The id of the dimension for which to obtain availability
            information about. In the case where this information is
            not provided, data availability will be provided for all
            dimensions.
        components: The component values to be used for data filtering.
        updated_after: The last time the query was performed by the client.
        references: This attribute instructs the web service to return (or not)
            the artefacts referenced by the DataConstraint to be returned.
        mode: Return a Cube Region containing values which will be returned
            by executing the query (mode="exact") vs a Cube Region showing
            what values remain valid selections that could be added to the
            data query (mode="available").
    """

    context: DataContext = DataContext.ALL
    agency_id: Union[str, Sequence[str]] = REST_ALL
    resource_id: Union[str, Sequence[str]] = REST_ALL
    version: Union[str, Sequence[str]] = REST_ALL
    key: Union[str, Sequence[str]] = REST_ALL
    component_id: Union[str, Sequence[str]] = REST_ALL
    components: Union[MultiFilter, None, NumberFilter, TextFilter] = None
    updated_after: Optional[datetime] = None
    references: Union[StructureReference, Sequence[StructureReference]] = (
        StructureReference.NONE
    )
    mode: AvailabilityMode = AvailabilityMode.EXACT

    def _validate_query(self, api_version: ApiVersion) -> None:
        self.validate()
        super()._validate_context(self.context, api_version)
        super()._check_multiple_contexts(
            self.agency_id,
            self.resource_id,
            self.version,
            self.key,
            api_version,
        )
        super()._check_resource_id(self.resource_id, api_version)
        super()._check_components(self.components, api_version)
        self.__validate_references(api_version)
        self.__validate_component_id(api_version)

    def __validate_reference(
        self, ref: StructureReference, api_version: ApiVersion
    ) -> None:
        if (api_version >= ApiVersion.V2_0_0 and ref not in REFERENCES_V2) or (
            api_version < ApiVersion.V2_0_0 and ref not in REFERENCES_V1
        ):
            raise Invalid(
                "Validation Error",
                f"{ref} is not allowed for SDMX-REST {api_version.value}.",
            )

    def __validate_references(self, api_version: ApiVersion) -> None:
        if isinstance(self.references, StructureReference):
            self.__validate_reference(self.references, api_version)
        else:
            refs = [r.value for r in self.references]
            check_multiple_data_context("references", refs, api_version)
            for ref in self.references:
                self.__validate_reference(ref, api_version)

    def __validate_component_id(self, api_version: ApiVersion) -> None:
        if (
            isinstance(self.component_id, (list, tuple))
            and api_version < ApiVersion.V2_0_0
        ):
            raise Invalid(
                "Validation Error",
                (
                    f"Only one component ID is allowed in SDMX-REST "
                    f"{api_version.value}."
                ),
            )

    def _get_decoder(self) -> msgspec.json.Decoder:  # type: ignore[type-arg]
        return _availability_decoder

    def __get_short_v2_qs(self) -> str:
        qs = ""
        if self.updated_after:
            qs = super()._append_qs_param(
                qs,
                self.updated_after,
                "updatedAfter",
                self.updated_after.isoformat("T", "seconds"),
            )
        if self.references != StructureReference.NONE:
            if isinstance(self.references, StructureReference):
                r = self.references.value
            else:
                refs = [ref.value for ref in self.references]
                r = ",".join(refs)
            qs = super()._append_qs_param(qs, r, "references")
        if self.mode != AvailabilityMode.EXACT:
            qs = super()._append_qs_param(qs, self.mode.value, "mode")
        return f"?{qs}" if qs else qs

    def __get_short_v1_qs(self) -> str:
        qs = ""
        if self.updated_after:
            qs = super()._append_qs_param(
                qs,
                self.updated_after,
                "updatedAfter",
                self.updated_after.isoformat("T", "seconds"),
            )
        if self.references != StructureReference.NONE:
            qs = super()._append_qs_param(
                qs,
                self.references.value,  # type: ignore[union-attr]
                "references",
            )
        if self.mode != AvailabilityMode.EXACT:
            qs = super()._append_qs_param(qs, self.mode.value, "mode")
        return f"?{qs}" if qs else qs

    def _create_full_query(self, api_version: ApiVersion) -> str:
        o = (
            "/availability"
            if api_version >= ApiVersion.V2_0_0
            else "/availableconstraint"
        )
        if api_version >= ApiVersion.V2_0_0:
            c = super()._get_v2_context_id(
                self.context,
                self.agency_id,
                self.resource_id,
                self.version,
                api_version,
            )
        else:
            c = super()._get_v1_context_id(
                self.agency_id,  # type: ignore[arg-type]
                self.resource_id,  # type: ignore[arg-type]
                self.version,  # type: ignore[arg-type]
                api_version,
            )
        o += f"{c}/{super()._to_kws(self.key, api_version)}"
        o += f"/{super()._to_kws(self.component_id, api_version)}"
        qs = ""
        if self.components:
            qs += self._create_component_filters(self.components)
        if self.updated_after:
            qs = super()._append_qs_param(
                qs,
                self.updated_after,
                "updatedAfter",
                self.updated_after.isoformat("T", "seconds"),
            )
        if isinstance(self.references, StructureReference):
            r = self.references.value
        else:
            refs = [ref.value for ref in self.references]
            r = ",".join(refs)
        qs = super()._append_qs_param(qs, r, "references")
        qs = super()._append_qs_param(qs, self.mode.value, "mode")
        return f"{o}?{qs}"

    def _create_short_query(self, api_version: ApiVersion) -> str:
        if api_version >= ApiVersion.V2_0_0:
            p = super()._get_short_v2_path(
                "availability",
                self.context,
                self.agency_id,
                self.resource_id,
                self.version,
                self.key,
                api_version,
                self.component_id,
            )
            q = self.__get_short_v2_qs()
            o = f"{p}{q}"
        else:
            p = super()._get_short_v1_path(
                "availableconstraint",
                self.agency_id,  # type: ignore[arg-type]
                self.resource_id,  # type: ignore[arg-type]
                self.version,  # type: ignore[arg-type]
                self.key,
                api_version,
            )
            q = self.__get_short_v1_qs()
            o = f"{p}{q}"
        return o


_availability_decoder = msgspec.json.Decoder(AvailabilityQuery)
