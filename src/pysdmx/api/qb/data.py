"""Build SDMX-REST data queries."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import msgspec

from pysdmx.api.qb.util import ApiVersion, REST_ALL, REST_LATEST
from pysdmx.errors import ClientError


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
    agency_id: str = REST_ALL
    resource_id: str = REST_ALL
    version: str = REST_ALL
    key: str = REST_ALL
    components: Dict[str, Any] = None
    updated_after: Optional[datetime] = None
    first_n_obs: Optional[int] = None
    last_n_obs: Optional[int] = None
    obs_dimension: Optional[str] = None
    attributes: str = "dsd"
    measures: str = "all"
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

    def __validate_query(self, version: ApiVersion) -> None:
        self.validate()

    def __create_full_query(self, ver: ApiVersion) -> str:
        return "/data"

    def __create_short_query(self, ver: ApiVersion) -> str:
        return "/data"


decoder = msgspec.json.Decoder(DataQuery)
encoder = msgspec.json.Encoder()
