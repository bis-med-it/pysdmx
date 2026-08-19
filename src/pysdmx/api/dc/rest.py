"""A connector for SDMX-REST services."""

import csv
import io
from typing import Any, Generator, NoReturn, Optional, Union

import msgspec

from pysdmx import errors
from pysdmx.api.dc import (
    BasicConnector,
    MaintainableIdentification,
)
from pysdmx.api.dc.query import BasicFilter
from pysdmx.api.dc.query.util import parse_query
from pysdmx.api.dc.util import prepare_basic_data_query
from pysdmx.api.qb import (
    ApiVersion,
    AvailabilityFormat,
    AvailabilityMode,
    AvailabilityQuery,
    DataContext,
    DataFormat,
    RestService,
    StructureDetail,
    StructureFormat,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.io import read_sdmx
from pysdmx.io.json.sdmxjson2.messages import JsonDataflowsMessage
from pysdmx.model import Agency, Dataflow, decoders
from pysdmx.util import experimental, parse_flow_urn, parse_urn

_FLOWS_DEC = msgspec.json.Decoder(JsonDataflowsMessage, dec_hook=decoders)


@experimental
class SdmxConnector(BasicConnector):
    """An SDMX-REST connector for data discovery and data retrieval.

    This connector is an implementation of the SDMX "data discovery and
    data retrieval" API for SDMX-REST v2 web services.

    Structural metadata and data are parsed with
    :func:`pysdmx.io.read_sdmx`, which auto-detects the format, so the
    connector works with any SDMX structure/data format pysdmx can read.
    The formats requested from the service default to SDMX-JSON 2.0 for
    structures and SDMX-CSV 2.0 for data; set ``structure_format`` /
    ``data_format`` for a service that serves, e.g., SDMX-ML.
    """

    def __init__(
        self,
        api_endpoint: str,
        pem: Optional[str] = None,
        timeout: Optional[float] = 5.0,
        structure_format: StructureFormat = StructureFormat.SDMX_JSON_2_0_0,
        data_format: DataFormat = DataFormat.SDMX_CSV_2_0_0,
    ):
        """Instantiate a data discovery and retrieval SDMX-REST connector.

        Args:
            api_endpoint: The SDMX-REST v2 base URL.
            pem: Optional PEM file with trusted certificate authorities.
            timeout: Maximum number of seconds to wait per request.
            structure_format: The structural-metadata format to request.
                Defaults to SDMX-JSON 2.0; set an SDMX-ML format for a
                service that does not serve SDMX-JSON (e.g. .Stat/OECD).
            data_format: The data format to request. Defaults to
                SDMX-CSV 2.0.
        """
        self.__client = RestService(
            api_endpoint,
            ApiVersion.V2_0_0,
            data_format=data_format,
            structure_format=structure_format,
            avail_format=AvailabilityFormat.SDMX_JSON_2_0_0,
            pem=pem,
            timeout=timeout,
        )

    def dataflows(
        self, search_term: Optional[str] = None
    ) -> tuple[Dataflow, ...]:
        """Get the list of dataflows available in the connector.

        Args:
            search_term (Optional[str]): A search term. If set, any dataflow
                containing the term in its ID, name, or description will be
                returned.

        Returns:
            tuple[Dataflow]: A sorted and immutable collection of dataflows
                matching the supplied search term, if any. For each dataflow,
                information such as its ID, name and description is returned.
                If a search term is supplied and does not match any dataflow,
                an empty collection will be returned. The collection is sorted
                by agency ID, then dataflow ID and then version number.

        Raises:
            errors.Invalid: In case the targeted service returns a client
                error, i.e. a status between 400 and 499.
            errors.InternalError: In case the targeted service returns a
                server error, i.e. a status between 500 and 599, or in case
                the server response could not be deserialized.
            errors.NotFound: In case the targeted service does not contain
                any dataflow.
            errors.Unavailable: In case the targeted service could not be
                reached.
        """
        q = StructureQuery(
            StructureType.DATAFLOW, detail=StructureDetail.ALL_COMPLETE_STUBS
        )
        try:
            out = self.__client.structure(q)
        except errors.NotFound:
            url = q.get_url(ApiVersion.V2_0_0, True)
            self.__raise_no_dataflows_error(url)

        try:
            msg = read_sdmx(io.BytesIO(out), validate=False)
        except (errors.Invalid, errors.NotImplemented) as e:
            self.__raise_deserialization_error(e, out)
        flows = [s for s in (msg.structures or []) if isinstance(s, Dataflow)]
        if not flows:
            self.__raise_no_flows_in_response_error(out)

        if search_term:
            st = search_term.strip().lower()
            if st:
                flows = [f for f in flows if self.__match_search_term(f, st)]
        return tuple(sorted(flows, key=self.__sort_maintainable))

    def dataflow(
        self,
        dataflow: Union[str, MaintainableIdentification],
        filters: Optional[Union[BasicFilter, str]] = None,
    ) -> Dataflow:
        """Retrieve information about a dataflow.

        This function provides details about a dataflow, including its
        components, to assist in querying data effectively.

        Args:
            dataflow (Union[str, MaintainableIdentification]): Specifies the
                dataflow to retrieve. This can be:
                - A string representing the SDMX URN of the dataflow.
                - An object implementing the `MaintainableIdentification`
                  protocol (e.g., instances of `DataflowRef` or `Dataflow`).
            filters: Filters used to scope the data availability
                information for the selected dataflow. If not supplied,
                information about the full dataflow is returned. If
                supplied, information about the matching subset is
                returned. This can be a string similar to a SQL WHERE
                clause ("AREA='UY' AND FREQ <> 'A'") or a Python expression
                ("REF_AREA=='UY' and FREQ != 'A'") or one of the various
                filters the `pysdmx.api.dc.query` module offers, including
                `MultiFilter`.

        Returns:
            Dataflow: An object containing detailed information about
                the requested dataflow, including:

                - Basic metadata, such as the dataflow's ID and name.
                - Metrics, such as the number of observations or period
                  coverage (if available from the source).
                - The expected data structure (data schema), including
                  components, their types, and other relevant details.

        Raises:
            errors.Invalid: In case the targeted service returns a client
                error, i.e. a status between 400 and 499.
            errors.InternalError: In case the targeted service returns a
                server error, i.e. a status between 500 and 599, or in case
                the server response could not be deserialized.
            errors.NotFound: In case the targeted service does not contain
                the requested dataflow.
            errors.Unavailable: In case the targeted service could not be
                reached.
        """
        if isinstance(dataflow, str):
            try:
                dataflow = parse_urn(dataflow)
            except errors.Invalid:
                dataflow = parse_flow_urn(dataflow)  # type: ignore[arg-type]
        aid = (
            dataflow.agency.id
            if isinstance(dataflow.agency, Agency)
            else dataflow.agency
        )

        if isinstance(filters, str):
            filters = parse_query(filters)  # type: ignore[assignment]

        q = AvailabilityQuery(
            DataContext.DATAFLOW,
            aid,
            dataflow.id,
            dataflow.version,
            components=filters,  # type: ignore[arg-type]
            references=StructureReference.ALL,
            mode=AvailabilityMode.EXACT,
        )
        try:
            out = self.__client.availability(q)
        except errors.NotFound:
            url = q.get_url(ApiVersion.V2_0_0, True)
            self.__raise_dataflow_nf_error(url)
        try:
            dfi = _FLOWS_DEC.decode(out).to_model()
        except msgspec.MsgspecError as e:
            self.__raise_deserialization_error(e, out)

        return dfi[0]

    def data(
        self,
        dataflow: Union[str, MaintainableIdentification],
        filters: Optional[Union[BasicFilter, str]] = None,
    ) -> Generator[dict[str, Any], None, None]:
        """Get data for the selected dataflow, matching the supplied filters.

        Args:
            dataflow (Union[str, MaintainableIdentification]): The dataflow
                from which to retrieve data. Either a string representing the
                SDMX URN of the dataflow or the information necessary to
                uniquely identify it. Classes such as `DataflowRef` or
                `Dataflow` are examples of pysdmx classes that implement the
                `MaintainableIdentification` protocol.
            filters: The data query filters, if any. This can be a string
                similar to a SQL WHERE clause ("AREA='UY' AND FREQ <> 'A'")
                or a Python expression ("REF_AREA=='UY' and FREQ != 'A'") or
                one of the various filters the `pysdmx.api.dc.query` module
                offers, including `MultiFilter`.

        Returns:
            The requested data, if any. Data are returned as a generator of
            observations, the observations being represented as Python
            dictionaries.
        """
        q = prepare_basic_data_query(dataflow, filters)

        try:
            resp = self.__client.data(q)
            csv_string = resp.decode("utf-8")
            csv_file = io.StringIO(csv_string)
            reader = csv.DictReader(csv_file)
            for row in reader:
                yield row
        except errors.NotFound:
            url = q.get_url(ApiVersion.V2_0_0, True)
            self.__raise_data_nf_error(url)

    def __match_search_term(self, df: Dataflow, search_term: str) -> bool:
        return (
            search_term in df.id.lower()  # type: ignore[return-value]
            or (df.name and search_term in df.name.lower())
            or (df.description and search_term in df.description.lower())
        )

    def __sort_maintainable(self, df: Dataflow) -> tuple[str, str, str]:
        aid = df.agency.id if isinstance(df.agency, Agency) else df.agency
        return (aid, df.id, df.version)

    def __raise_deserialization_error(
        self, error: Exception, msg: bytes
    ) -> NoReturn:
        raise errors.InternalError(
            "Unexpected message format",
            (
                "The payload could not be deserialized. This likely "
                "indicates that the service did not respond with a "
                "valid SDMX message."
            ),
            {
                "original_exception": str(error),
                "service_response": msg.decode("utf-8", errors="replace"),
                "endpoint": self.__client._api_endpoint,
            },
        ) from error

    def __raise_no_flows_in_response_error(self, msg: bytes) -> NoReturn:
        raise errors.InternalError(
            "Unexpected response",
            (
                "The service returned a 200 response with no dataflows. "
                "It likely answered the dataflows query with a different "
                "or empty message."
            ),
            {
                "service_response": msg.decode("utf-8", errors="replace"),
                "endpoint": self.__client._api_endpoint,
            },
        )

    def __raise_no_dataflows_error(self, url: str) -> NoReturn:
        raise errors.NotFound(
            "No dataflows found",
            (
                "No dataflows could be found in the targeted service. "
                "This is a violation of the SDMX data discovery and data "
                "retrieval profile, as its purpose is to retrieve data "
                "from dataflows."
            ),
            {
                "url": url,
            },
        )

    def __raise_dataflow_nf_error(self, url: str) -> NoReturn:
        raise errors.NotFound(
            "Requested dataflow not found",
            (
                "The requested dataflow could not be found in the targeted "
                "service. Please use the `dataflows` method of the connector "
                "to see which dataflows are available in the service. If you "
                "have already done so, this indicates that there are no data "
                "for the selected dataflow and, therefore, no availability "
                "information could be found."
            ),
            {
                "url": url,
            },
        )

    def __raise_data_nf_error(self, url: str) -> NoReturn:
        raise errors.NotFound(
            "No data",
            (
                "There are no data for the selected dataflow "
                "matching the supplied filters (if any)."
            ),
            {
                "url": url,
            },
        )
