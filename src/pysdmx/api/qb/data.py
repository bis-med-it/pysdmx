"""Build SDMX-REST data queries."""

from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, List, Optional, Sequence, Union

import msgspec

from pysdmx.api.dc.query import (
    LogicalOperator,
    MultiFilter,
    NumberFilter,
    Operator,
    TextFilter,
)
from pysdmx.api.qb.util import (
    ApiVersion,
    check_multiple_data_context,
    REST_ALL,
)
from pysdmx.errors import ClientError
from pysdmx.model.types import NC_NAME_ID_TYPE


class DataContext(Enum):
    """The context of the data query."""

    DATA_STRUCTURE = "datastructure"
    DATAFLOW = "dataflow"
    PROVISION_AGREEMENT = "provisionagreement"
    ALL = REST_ALL


class DataFormat(Enum):
    """The response formats."""

    SDMX_JSON_1_0_0 = "application/vnd.sdmx.data+json;version=1.0.0"
    SDMX_JSON_2_0_0 = "application/vnd.sdmx.data+json;version=2.0.0"
    SDMX_CSV_1_0_0 = "application/vnd.sdmx.data+csv;version=1.0.0"
    SDMX_CSV_2_0_0 = "application/vnd.sdmx.data+csv;version=2.0.0"
    SDMX_ML_2_1_GEN = "application/vnd.sdmx.genericdata+xml;version=2.1"
    SDMX_ML_2_1_STR = (
        "application/vnd.sdmx.structurespecificdata+xml;version=2.1"
    )
    SDMX_ML_2_1_GENTS = (
        "application/vnd.sdmx.generictimeseriesdata+xml;version=2.1"
    )
    SDMX_ML_2_1_STRTS = (
        "application/vnd.sdmx.structurespecifictimeseriesdata+xml;version=2.1"
    )
    SDMX_ML_3_0 = "application/vnd.sdmx.data+xml;version=3.0.0"


class DataQuery(msgspec.Struct, frozen=True, omit_defaults=True):
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
    """

    context: DataContext = DataContext.ALL
    agency_id: Union[str, Sequence[str]] = REST_ALL
    resource_id: Union[str, Sequence[str]] = REST_ALL
    version: Union[str, Sequence[str]] = REST_ALL
    key: Union[str, Sequence[str]] = REST_ALL
    components: Union[MultiFilter, NumberFilter, TextFilter] = None
    updated_after: Optional[datetime] = None
    first_n_obs: Optional[Annotated[int, msgspec.Meta(gt=0)]] = None
    last_n_obs: Optional[Annotated[int, msgspec.Meta(gt=0)]] = None
    obs_dimension: Optional[NC_NAME_ID_TYPE] = None
    attributes: Union[
        NC_NAME_ID_TYPE,
        Sequence[NC_NAME_ID_TYPE],
    ] = "dsd"
    measures: Union[
        NC_NAME_ID_TYPE,
        Sequence[NC_NAME_ID_TYPE],
    ] = "all"
    include_history: bool = False

    def validate(self) -> None:
        """Validate the query."""
        try:
            decoder.decode(encoder.encode(self))
        except msgspec.DecodeError as err:
            raise ClientError(422, "Invalid Schema Query", str(err)) from err

    def get_url(self, version: ApiVersion, omit_defaults: bool = False) -> str:
        """The URL for the query in the selected SDMX-REST API version."""
        self.__validate_query(version)
        if omit_defaults:
            return self.__create_short_query(version)
        else:
            return self.__create_full_query(version)

    def __validate_context(self, version: ApiVersion) -> None:
        if version < ApiVersion.V2_0_0 and self.context in [
            DataContext.DATA_STRUCTURE,
            DataContext.PROVISION_AGREEMENT,
        ]:
            raise ClientError(
                422,
                "Validation Error",
                f"{self.context} is not valid for SDMX-REST {version.value}.",
            )

    def __check_multiple_contexts(self, version: ApiVersion) -> None:
        check_multiple_data_context("agency", self.agency_id, version)
        check_multiple_data_context("resource", self.resource_id, version)
        check_multiple_data_context("version", self.version, version)
        check_multiple_data_context("key", self.key, version)

    def __check_resource_id(self, version: ApiVersion) -> None:
        if version < ApiVersion.V2_0_0 and self.resource_id == REST_ALL:
            raise ClientError(
                422,
                "Validation Error",
                f"A dataflow must be provided in SDMX-REST {version.value}.",
            )

    def __check_component(self, version: ApiVersion) -> None:
        if version < ApiVersion.V2_0_0 and self.components:
            raise ClientError(
                422,
                "Validation Error",
                (
                    "Components filter is not supported in "
                    f"SDMX-REST {version.value}."
                ),
            )

    def __validate_query(self, version: ApiVersion) -> None:
        self.validate()
        self.__validate_context(version)
        self.__check_multiple_contexts(version)
        self.__check_resource_id(version)
        self.__check_component(version)

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
        return ",".join(mapped)

    def __get_v2_context_id(self, ver: ApiVersion) -> str:
        o = f"/{self.context.value}"
        a = self.__to_kws(self.agency_id, ver)
        r = self.__to_kws(self.resource_id, ver)
        v = self.__to_kws(self.version, ver)
        o += f"/{a}/{r}/{v}"
        return o

    def __get_v1_context_id(self, ver: ApiVersion) -> str:
        a = self.__to_kw(self.agency_id, ver)
        r = self.__to_kw(self.resource_id, ver)
        v = (
            self.__to_kw(self.version, ver)
            if self.version != REST_ALL
            else "latest"
        )
        return f"/{a},{r},{v}"

    def __get_short_v2_path(self, ver: ApiVersion) -> str:
        k = f"/{self.__to_kws(self.key, ver)}" if self.key != REST_ALL else ""
        v = (
            f"/{self.__to_kws(self.version, ver)}{k}"
            if k or self.version != REST_ALL
            else ""
        )
        r = (
            f"/{self.__to_kws(self.resource_id, ver)}{v}"
            if v or self.resource_id != REST_ALL
            else ""
        )
        a = (
            f"/{self.__to_kws(self.agency_id, ver)}{r}"
            if r or self.agency_id != REST_ALL
            else ""
        )
        c = (
            f"/{self.context.value}{a}"
            if a or self.context != DataContext.ALL
            else ""
        )
        return f"/data{c}"

    def __get_short_v2_qs(self, ver: ApiVersion) -> str:
        qs = ""
        if self.updated_after:
            qs = self.__append_qs_param(
                qs,
                self.updated_after,
                "updatedAfter",
                self.updated_after.isoformat("T", "seconds"),
            )
        qs = self.__append_qs_param(qs, self.first_n_obs, "firstNObservations")
        qs = self.__append_qs_param(qs, self.last_n_obs, "lastNObservations")
        qs = self.__append_qs_param(
            qs, self.obs_dimension, "dimensionAtObservation"
        )
        if self.attributes != "dsd":
            qs = self.__append_qs_param(
                qs, self.__to_kws(self.attributes, ver), "attributes"
            )
        if self.measures != "all":
            qs = self.__append_qs_param(
                qs, self.__to_kws(self.measures, ver), "measures"
            )
        qs = self.__append_qs_param(
            qs,
            self.include_history,
            "includeHistory",
            str(self.include_history).lower(),
        )
        return f"?{qs}" if qs else qs

    def __append_qs_param(
        self, qs: str, value: Any, field: str, disp_value: Any = None
    ) -> str:
        if value:
            if qs:
                qs += "&"
            qs += f"{field}={disp_value if disp_value else value}"
        return qs

    def __get_short_v1_qs(self, ver: ApiVersion) -> str:
        qs = ""
        if self.updated_after:
            qs = self.__append_qs_param(
                qs,
                self.updated_after,
                "updatedAfter",
                self.updated_after.isoformat("T", "seconds"),
            )
        qs = self.__append_qs_param(qs, self.first_n_obs, "firstNObservations")
        qs = self.__append_qs_param(qs, self.last_n_obs, "lastNObservations")
        qs = self.__append_qs_param(
            qs, self.obs_dimension, "dimensionAtObservation"
        )
        detail = self.__get_v1_detail(ver)
        if detail != "full":
            qs = self.__append_qs_param(qs, detail, "detail")
        qs = self.__append_qs_param(
            qs,
            self.include_history,
            "includeHistory",
            str(self.include_history).lower(),
        )
        return f"?{qs}" if qs else qs

    def __get_short_v1_path(self, ver: ApiVersion) -> str:
        v = (
            f",{self.__to_kw(self.version, ver)}"
            if self.version != REST_ALL
            else ""
        )
        r = (
            f"{self.__to_kw(self.resource_id, ver)}{v}"
            if v or self.resource_id != REST_ALL
            else ""
        )
        if self.agency_id != REST_ALL or self.version != REST_ALL:
            a = f"{self.__to_kw(self.agency_id, ver)},{r}"
        else:
            a = f"{r}"
        k = f"/{self.key}" if self.key != REST_ALL else ""
        if a:
            return f"/data/{a}{k}"
        elif k and not a:
            return f"/data/all,all,latest{k}"
        else:
            return ""

    def __get_v1_detail(self, ver: ApiVersion) -> str:
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
            raise ClientError(
                422,
                "Validation Error",
                (
                    f"{self.attributes} and {self.measures} is not a valid "
                    "combination for the detail attribute in SDMX-REST "
                    f"{ver.value}.",
                ),
            )

    def __create_component_filters(self) -> str:
        if isinstance(self.components, MultiFilter):
            if self.components.operator == LogicalOperator.OR:
                raise ClientError(
                    422,
                    "Validation Error",
                    "OR operator is not supported for MultiFilter.",
                )
            flts_by_comp = defaultdict(list)
            for f in self.components.filters:
                flts_by_comp[f.field].append(f)
            flts = []
            for k, v in flts_by_comp.items():
                if isinstance(v, List):
                    flts.append(_create_component_mult_filter(k, v))
                else:
                    flts.append(_create_component_filter(f))
            return "&".join(flts)
        else:
            return _create_component_filter(self.components)

    def __create_full_query(self, ver: ApiVersion) -> str:
        o = "/data"
        if ver >= ApiVersion.V2_0_0:
            c = self.__get_v2_context_id(ver)
        else:
            c = self.__get_v1_context_id(ver)
        o += f"{c}/{self.__to_kws(self.key, ver)}"
        o += "?"
        qs = ""
        if self.components:
            qs += self.__create_component_filters()
        if self.updated_after:
            if qs:
                qs += "&"
            qs += (
                f"updatedAfter={self.updated_after.isoformat('T', 'seconds')}"
            )
        if self.first_n_obs:
            if qs:
                qs += "&"
            qs += f"firstNObservations={self.first_n_obs}"
        if self.last_n_obs:
            if qs:
                qs += "&"
            qs += f"lastNObservations={self.last_n_obs}"
        if self.obs_dimension:
            if qs:
                qs += "&"
            qs += f"dimensionAtObservation={self.obs_dimension}"
        if ver >= ApiVersion.V2_0_0:
            if qs:
                qs += "&"
            qs += (
                f"attributes={self.__to_kws(self.attributes, ver)}"
                f"&measures={self.__to_kws(self.measures, ver)}"
            )
        else:
            if qs:
                qs += "&"
            qs += f"detail={self.__get_v1_detail(ver)}"
        o += f"{qs}&includeHistory={str(self.include_history).lower()}"
        return o

    def __create_short_query(self, ver: ApiVersion) -> str:
        if ver >= ApiVersion.V2_0_0:
            p = self.__get_short_v2_path(ver)
            q = self.__get_short_v2_qs(ver)
            o = f"{p}{q}"
        else:
            p = self.__get_short_v1_path(ver)
            q = self.__get_short_v1_qs(ver)
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
            raise ClientError(
                422,
                "Validation Error",
                (
                    f"The supplied value ({value}) is not correct "
                    "for the LIKE operator."
                ),
            )
        return out
    else:
        raise ClientError(
            422,
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
    if flt.operator in [Operator.LIKE, Operator.NOT_LIKE]:
        op = __map_operator(flt.operator, flt.value)
        val = str(flt.value).replace("%", "")
        return f"c[{flt.field}]={op}:{val}"
    elif flt.operator == Operator.IN:
        return f"c[{flt.field}]={','.join(flt.value)}"
    elif flt.operator == Operator.BETWEEN:
        return f"c[{flt.field}]=ge:{flt.value[0]}+le:{flt.value[1]}"
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
        op = __map_operator(flt.operator, flt.value)
        if op:
            op += ":"
        return f"c[{flt.field}]={op}{flt.value}"
    else:
        raise ClientError(
            422,
            "Validation Error",
            (f"The operator ({flt.operator}) is not supported."),
        )


def _create_component_mult_filter(
    comp: str, flts: Sequence[Union[NumberFilter, TextFilter]]
) -> str:
    cstr = [_create_component_filter(f) for f in flts]
    fstr = [s.replace(f"c[{comp}]=", "") for s in cstr]
    return f"c[{comp}]={'+'.join(fstr)}"


decoder = msgspec.json.Decoder(DataQuery)
encoder = msgspec.json.Encoder()
