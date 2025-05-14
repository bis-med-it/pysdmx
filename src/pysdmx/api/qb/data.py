"""Build SDMX-REST data queries."""

from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Optional, Sequence, Union

import msgspec

from pysdmx.api.dc.query import (
    LogicalOperator,
    MultiFilter,
    NumberFilter,
    Operator,
    SortBy,
    TextFilter,
)
from pysdmx.api.qb.util import (
    REST_ALL,
    ApiVersion,
    CoreQuery,
    check_multiple_data_context,
)
from pysdmx.errors import Invalid
from pysdmx.io.format import DataFormat


class DataContext(Enum):
    """The context of the data query."""

    DATA_STRUCTURE = "datastructure"
    DATAFLOW = "dataflow"
    PROVISION_AGREEMENT = "provisionagreement"
    ALL = REST_ALL


class _CoreDataQuery(CoreQuery, frozen=True, omit_defaults=True):
    def _validate_context(
        self, context: DataContext, api_version: ApiVersion
    ) -> None:
        if api_version < ApiVersion.V2_0_0 and context in [
            DataContext.DATA_STRUCTURE,
            DataContext.PROVISION_AGREEMENT,
        ]:
            raise Invalid(
                "Validation Error",
                f"{context} is not valid for SDMX-REST {api_version.value}.",
            )

    def _check_multiple_contexts(
        self,
        agency_id: Union[str, Sequence[str]],
        resource_id: Union[str, Sequence[str]],
        version: Union[str, Sequence[str]],
        key: Union[str, Sequence[str]],
        api_version: ApiVersion,
    ) -> None:
        check_multiple_data_context("agency", agency_id, api_version)
        check_multiple_data_context("resource", resource_id, api_version)
        check_multiple_data_context("version", version, api_version)
        check_multiple_data_context("key", key, api_version)

    def _check_resource_id(
        self, resource_id: Union[str, Sequence[str]], api_version: ApiVersion
    ) -> None:
        if api_version < ApiVersion.V2_0_0 and resource_id == REST_ALL:
            raise Invalid(
                "Validation Error",
                (
                    f"A dataflow must be provided in SDMX-REST "
                    f"{api_version.value}."
                ),
            )

    def _check_version(
        self,
        field: str,
        value: Any,
        api_version: ApiVersion,
        allowed_version: ApiVersion,
    ) -> None:
        if value and api_version < allowed_version:
            raise Invalid(
                "Validation Error",
                (
                    f"{field} is not supported in "
                    f"SDMX-REST {api_version.value}."
                ),
            )

    def _get_v2_context_id(
        self,
        context: DataContext,
        agency_id: Union[str, Sequence[str]],
        resource_id: Union[str, Sequence[str]],
        version: Union[str, Sequence[str]],
        api_version: ApiVersion,
    ) -> str:
        o = f"/{context.value}"
        a = self._to_kws(agency_id, api_version)
        r = self._to_kws(resource_id, api_version)
        v = self._to_kws(version, api_version)
        o += f"/{a}/{r}/{v}"
        return o

    def _get_v1_context_id(
        self,
        agency_id: str,
        resource_id: str,
        version: str,
        api_version: ApiVersion,
    ) -> str:
        a = self._to_kw(agency_id, api_version)
        r = self._to_kw(resource_id, api_version)
        v = (
            self._to_kw(version, api_version)
            if version != REST_ALL
            else "latest"
        )
        return f"/{a},{r},{v}"

    def _get_short_v2_path(
        self,
        resource: str,
        context: DataContext,
        agency_id: Union[str, Sequence[str]],
        resource_id: Union[str, Sequence[str]],
        version: Union[str, Sequence[str]],
        key: Union[str, Sequence[str]],
        api_version: ApiVersion,
        component_id: Union[str, Sequence[str], None] = None,
    ) -> str:
        d = (
            f"/{self._to_kws(component_id, api_version)}"
            if component_id and component_id != REST_ALL
            else ""
        )
        k = (
            f"/{self._to_kws(key, api_version)}{d}"
            if d or key != REST_ALL
            else ""
        )
        v = (
            f"/{self._to_kws(version, api_version)}{k}"
            if k or version != REST_ALL
            else ""
        )
        r = (
            f"/{self._to_kws(resource_id, api_version)}{v}"
            if v or resource_id != REST_ALL
            else ""
        )
        a = (
            f"/{self._to_kws(agency_id, api_version)}{r}"
            if r or agency_id != REST_ALL
            else ""
        )
        c = f"/{context.value}{a}" if a or context != DataContext.ALL else ""
        return f"/{resource}{c}"

    def _get_short_v1_path(
        self,
        resource: str,
        agency_id: str,
        resource_id: str,
        version: str,
        key: Union[str, Sequence[str]],
        api_version: ApiVersion,
    ) -> str:
        v = (
            f",{self._to_kw(version, api_version)}"
            if version != REST_ALL
            else ""
        )
        kr = self._to_kw(resource_id, api_version)
        r = f"{kr}{v}"
        if agency_id != REST_ALL or version != REST_ALL:
            ka = self._to_kw(agency_id, api_version)
            a = f"{ka},{r}"
        else:
            a = f"{r}"
        k = f"/{key}" if key != REST_ALL else ""
        return f"/{resource}/{a}{k}"

    def _create_component_filters(
        self, components: Union[MultiFilter, NumberFilter, TextFilter]
    ) -> str:
        if isinstance(components, MultiFilter):
            if components.operator == LogicalOperator.OR:
                raise Invalid(
                    "Validation Error",
                    "OR operator is not supported for MultiFilter.",
                )
            flts_by_comp = defaultdict(list)
            for f in components.filters:
                if isinstance(f, (NumberFilter, TextFilter)):
                    flts_by_comp[f.field].append(f)
                else:
                    raise Invalid(
                        "Validation Error",
                        f"Unsupported filter type: {f}.",
                    )
            flts = []
            for k, v in flts_by_comp.items():
                if len(v) > 1:
                    flts.append(_create_component_mult_filter(k, v))
                else:
                    flts.append(_create_component_filter(v[0]))
            return "&".join(flts)
        else:
            return _create_component_filter(components)


class DataQuery(_CoreDataQuery, frozen=True, omit_defaults=True):
    """A data query.

    Data queries allow retrieving statistical data.

    Attributes:
        context: The context for which data must be retrieved.
        agency_id: The agency maintaining the context to be considered.
        resource_id: The id of the context to be considered.
        version: The version of the context to be considered.
        key: The combination of dimension values identifying the slice
            of the cube for which data should be returned. Wildcarding
            is supported via the * operator.
        components: The component values to be used for data filtering.
        updated_after: The last time the query was performed by the client.
        first_n_obs: The maximum number of observations to be returned for
            each of the matching series, starting from the first observation.
        last_n_obs: The maximum number of observations to be returned for
            each of the matching series, counting back from the most recent
            observation.
        obs_dim: The ID of the dimension to be attached at the observation
            level.
        attributes: The attributes to be returned. Possible options are:
            `dsd` (all the attributes defined in the DSD), `msd` (all the
            reference metadata attributes), `dataset` (all the attributes
            attached to the dataset-level), `series` (all the attributes
            attached to the series-level), `obs` (all the attributes
            attached to the observation-level), `all` (all attributes),
            `none` (no attributes), {attribute_id}: The ID of the one or
            more attributes to be returned.
        measures: The measures to be returned. Possible options are:
            `all` (all measures), `none` (no measure), {measure_id}:
            The ID of the one or more measures to be returned.
        include_history: Retrieve previous versions of the data, as they
            were disseminated in the past.
        offset: The number of observations (or series) to skip before
            beginning to return observation (or series).
        limit: The maximum number of observations to be returned.
        sort: The order in which the returned data should be sorted.
            It contains either one or more components, by which the data
            should be sorted, or the * operator, which represents all
            dimensions as positioned in the DSD, or the keyword series_key,
            which represents all dimensions not presented at the observational
            level and as positioned in the DSD. In addition, each component,
            or the set of components (through the operator or keyword) can be
            sorted in ascending or descending order.
        as_of: Retrieve the data as they were at the specified point
            in time (aka time travel).
        reporting_year_start_day: The start day of a reporting year, when
            the year is not a Gregorian calendar year, for example when
            the year represents a fiscal year.
    """

    context: DataContext = DataContext.ALL
    agency_id: Union[str, Sequence[str]] = REST_ALL
    resource_id: Union[str, Sequence[str]] = REST_ALL
    version: Union[str, Sequence[str]] = REST_ALL
    key: Union[str, Sequence[str]] = REST_ALL
    components: Union[MultiFilter, None, NumberFilter, TextFilter] = None
    updated_after: Optional[datetime] = None
    first_n_obs: Optional[Annotated[int, msgspec.Meta(gt=0)]] = None
    last_n_obs: Optional[Annotated[int, msgspec.Meta(gt=0)]] = None
    obs_dimension: Optional[str] = None
    attributes: Union[
        str,
        Sequence[str],
    ] = "dsd"
    measures: Union[
        str,
        Sequence[str],
    ] = "all"
    include_history: bool = False
    offset: int = 0
    limit: Optional[int] = None
    sort: Sequence[SortBy] = []
    as_of: Optional[datetime] = None
    reporting_year_start_day: Optional[str] = None

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
        super()._check_version(
            "components", self.components, api_version, ApiVersion.V2_0_0
        )
        super()._check_version(
            "as_of", self.as_of, api_version, ApiVersion.V2_2_0
        )
        super()._check_version(
            "reporting_year_start_day",
            self.reporting_year_start_day,
            api_version,
            ApiVersion.V2_2_0,
        )
        super()._check_version(
            "offset", self.offset, api_version, ApiVersion.V2_2_0
        )
        super()._check_version(
            "limit", self.limit, api_version, ApiVersion.V2_2_0
        )
        super()._check_version(
            "sort", self.sort, api_version, ApiVersion.V2_2_0
        )
        self.__check_pos_int("offset", self.offset)
        self.__check_pos_int("limit", self.limit)

    def _get_decoder(self) -> msgspec.json.Decoder:  # type: ignore[type-arg]
        return _data_decoder

    def __get_short_v2_qs(self, api_version: ApiVersion) -> str:
        qs = ""
        if self.updated_after:
            qs = super()._append_qs_param(
                qs,
                self.updated_after,
                "updatedAfter",
                self.updated_after.isoformat("T", "seconds"),
            )
        qs = super()._append_qs_param(
            qs, self.first_n_obs, "firstNObservations"
        )
        qs = super()._append_qs_param(qs, self.last_n_obs, "lastNObservations")
        qs = super()._append_qs_param(
            qs, self.obs_dimension, "dimensionAtObservation"
        )
        if self.attributes != "dsd":
            qs = super()._append_qs_param(
                qs, super()._to_kws(self.attributes, api_version), "attributes"
            )
        if self.measures != "all":
            qs = super()._append_qs_param(
                qs, super()._to_kws(self.measures, api_version), "measures"
            )
        qs = super()._append_qs_param(
            qs,
            self.include_history,
            "includeHistory",
            str(self.include_history).lower(),
        )
        if api_version >= ApiVersion.V2_2_0 and self.offset != 0:
            qs = super()._append_qs_param(qs, self.offset, "offset")
        qs = super()._append_qs_param(qs, self.limit, "limit")
        qs = super()._append_qs_param(
            qs, self.sort, "sort", self.__get_sort(self.sort)
        )
        qs = super()._append_qs_param(
            qs,
            self.as_of,
            "asOf",
            self.as_of.isoformat("T", "seconds") if self.as_of else None,
        )
        qs = super()._append_qs_param(
            qs, self.reporting_year_start_day, "reportingYearStartDay"
        )
        return f"?{qs}" if qs else qs

    def __get_short_v1_qs(self, api_version: ApiVersion) -> str:
        qs = ""
        if self.updated_after:
            qs = super()._append_qs_param(
                qs,
                self.updated_after,
                "updatedAfter",
                self.updated_after.isoformat("T", "seconds"),
            )
        qs = super()._append_qs_param(
            qs, self.first_n_obs, "firstNObservations"
        )
        qs = super()._append_qs_param(qs, self.last_n_obs, "lastNObservations")
        qs = super()._append_qs_param(
            qs, self.obs_dimension, "dimensionAtObservation"
        )
        detail = self.__get_v1_detail(api_version)
        if detail != "full":
            qs = super()._append_qs_param(qs, detail, "detail")
        qs = super()._append_qs_param(
            qs,
            self.include_history,
            "includeHistory",
            str(self.include_history).lower(),
        )
        return f"?{qs}" if qs else qs

    def __get_v1_detail(self, api_version: ApiVersion) -> str:
        if self.measures in ["OBS_VALUE", "all"] and self.attributes == "dsd":
            return "full"
        elif (
            self.measures in ["OBS_VALUE", "all"] and self.attributes == "none"
        ):
            return "dataonly"
        if self.measures == "none" and self.attributes == "series":
            return "serieskeysonly"
        if self.measures == "none" and self.attributes == "dsd":
            return "nodata"
        else:
            raise Invalid(
                "Validation Error",
                (
                    f"{self.attributes} and {self.measures} is not a valid "
                    "combination for the detail attribute in SDMX-REST "
                    f"{api_version.value}."
                ),
            )

    def __check_pos_int(self, field: str, value: Optional[int]) -> None:
        if value and value < 0:
            raise Invalid(
                "Validation Error",
                f"{field} is must be a positive integer.",
            )

    def _create_full_query(self, api_version: ApiVersion) -> str:
        o = "/data"
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
        qs = super()._append_qs_param(
            qs, self.first_n_obs, "firstNObservations"
        )
        qs = super()._append_qs_param(qs, self.last_n_obs, "lastNObservations")
        qs = super()._append_qs_param(
            qs, self.obs_dimension, "dimensionAtObservation"
        )
        if api_version >= ApiVersion.V2_0_0:
            qs = super()._append_qs_param(
                qs,
                self.attributes,
                "attributes",
                super()._to_kws(self.attributes, api_version),
            )
            qs = super()._append_qs_param(
                qs,
                self.measures,
                "measures",
                super()._to_kws(self.measures, api_version),
            )
        else:
            qs = super()._append_qs_param(
                qs, self.__get_v1_detail(api_version), "detail"
            )
        qs = super()._append_qs_param(
            qs, str(self.include_history).lower(), "includeHistory"
        )
        if api_version >= ApiVersion.V2_2_0:
            qs = super()._append_qs_param(qs, self.offset, "offset")
        qs = super()._append_qs_param(qs, self.limit, "limit")
        qs = super()._append_qs_param(
            qs, self.sort, "sort", self.__get_sort(self.sort)
        )
        qs = super()._append_qs_param(
            qs,
            self.as_of,
            "asOf",
            self.as_of.isoformat("T", "seconds") if self.as_of else None,
        )
        qs = super()._append_qs_param(
            qs, self.reporting_year_start_day, "reportingYearStartDay"
        )
        return f"{o}?{qs}"

    def __get_sort(self, sort: Sequence[SortBy]) -> str:
        return "+".join([f"{s.component}:{s.order}" for s in sort])

    def _create_short_query(self, api_version: ApiVersion) -> str:
        if api_version >= ApiVersion.V2_0_0:
            p = super()._get_short_v2_path(
                "data",
                self.context,
                self.agency_id,
                self.resource_id,
                self.version,
                self.key,
                api_version,
            )
            q = self.__get_short_v2_qs(api_version)
            o = f"{p}{q}"
        else:
            p = super()._get_short_v1_path(
                "data",
                self.agency_id,  # type: ignore[arg-type]
                self.resource_id,  # type: ignore[arg-type]
                self.version,  # type: ignore[arg-type]
                self.key,
                api_version,
            )
            q = self.__get_short_v1_qs(api_version)
            o = f"{p}{q}"
        return o


def __map_like_operator(value: Any) -> str:
    if isinstance(value, str):
        if value.startswith("%") and value.endswith("%"):
            out = "co"
        elif value.startswith("%"):
            out = "ew"
        elif value.endswith("%"):
            out = "sw"
        else:
            raise Invalid(
                "Validation Error",
                (
                    f"The supplied value ({value}) is not correct "
                    "for the LIKE operator."
                ),
            )
        return out
    else:
        raise Invalid(
            "Validation Error",
            (
                f"The supplied value ({value}) for the LIKE operator "
                "should be a string."
            ),
        )


def __map_operator(op: Operator, value: Any) -> str:
    out = ""
    if op == Operator.NOT_EQUALS:
        out = "ne"
    elif op == Operator.LESS_THAN:
        out = "lt"
    elif op == Operator.LESS_THAN_OR_EQUAL:
        out = "le"
    elif op == Operator.GREATER_THAN:
        out = "gt"
    elif op == Operator.GREATER_THAN_OR_EQUAL:
        out = "ge"
    elif op == Operator.LIKE:
        out = __map_like_operator(value)
    elif op == Operator.NOT_LIKE:
        out = "nc"
    return out


def _create_component_filter(flt: Union[NumberFilter, TextFilter]) -> str:
    fld = flt.field
    val = flt.value
    if flt.operator in [Operator.LIKE, Operator.NOT_LIKE]:
        op = __map_operator(flt.operator, val)
        val = str(val).replace("%", "")
        return f"c[{fld}]={op}:{val}"
    elif flt.operator == Operator.IN:
        return f"c[{fld}]={','.join(val)}"  # type: ignore[arg-type]
    elif flt.operator == Operator.BETWEEN:
        return f"c[{fld}]=ge:{val[0]}+le:{val[1]}"  # type: ignore[index]
    elif flt.operator in [
        Operator.EQUALS,
        Operator.NOT_EQUALS,
        Operator.LIKE,
        Operator.NOT_LIKE,
        Operator.LESS_THAN,
        Operator.LESS_THAN_OR_EQUAL,
        Operator.GREATER_THAN,
        Operator.GREATER_THAN_OR_EQUAL,
    ]:
        op = __map_operator(flt.operator, val)
        if op:
            op += ":"
        return f"c[{fld}]={op}{val}"
    else:
        raise Invalid(
            "Validation Error",
            (f"The operator ({flt.operator}) is not supported."),
        )


def _create_component_mult_filter(
    comp: str, flts: Sequence[Union[NumberFilter, TextFilter]]
) -> str:
    cstr = [_create_component_filter(f) for f in flts]
    fstr = [s.replace(f"c[{comp}]=", "") for s in cstr]
    return f"c[{comp}]={'+'.join(fstr)}"


_data_decoder = msgspec.json.Decoder(DataQuery)

__all__ = [
    "ApiVersion",
    "DataContext",
    "DataFormat",
    "DataQuery",
]
