"""A connector for SDMX-REST services."""

import csv
import io
from typing import Generator, NoReturn, Optional, Union

import msgspec

from pysdmx import errors
from pysdmx.api.dc import BasicConnector, MaintainableIdentification
from pysdmx.api.dc.query import MultiFilter, NumberFilter, TextFilter
from pysdmx.api.dc.query.util import parse_query
from pysdmx.api.qb import (
    ApiVersion,
    AvailabilityFormat,
    AvailabilityMode,
    AvailabilityQuery,
    DataContext,
    DataFormat,
    DataQuery,
    RestService,
    StructureDetail,
    StructureFormat,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.io.json.sdmxjson2.messages import JsonDataflowsMessage
from pysdmx.model import Agency, Dataflow, decoders
from pysdmx.util import parse_maintainable_urn

_FLOWS_DEC = msgspec.json.Decoder(JsonDataflowsMessage, dec_hook=decoders)


class SdmxConnector(BasicConnector):
    """An SDMX-REST connector for data discovery and data retrieval.

    This connector is an implementation of the SDMX "data discovery and
    data retrieval" API for SDMX-REST v2 web services.

    In addition to being compliant with the SDMX-REST v2 API, the targeted
    service must be able to return structural metadata in SDMX-JSON v2.0.0 and
    data in SDMX-CSV v2.0.0.
    """

    def __init__(
        self,
        api_endpoint: str,
        pem: Optional[str] = None,
        timeout: Optional[float] = 5.0,
    ):
        """Instantiate a data discovery and retrieval SDMX-REST connector."""
        self.__client = RestService(
            api_endpoint,
            ApiVersion.V2_0_0,
            data_format=DataFormat.SDMX_CSV_2_0_0,
            structure_format=StructureFormat.SDMX_JSON_2_0_0,
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
        out = self.__client.structure(q)
        try:
            flows = _FLOWS_DEC.decode(out).to_model()
        except msgspec.MsgspecError as e:
            self.__raise_deserialization_error(e, out)

        if not flows:
            url = q.get_url(ApiVersion.V2_0_0, True)
            self.__raise_no_dataflows_error(url)

        if search_term:
            st = search_term.strip().lower()
            if st:
                flows = [f for f in flows if self.__match_search_term(f, st)]
        return tuple(sorted(flows, key=self.__sort_maintainable))

    def dataflow(
        self, dataflow: Union[str, MaintainableIdentification]
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
            dataflow = parse_maintainable_urn(dataflow)
        aid = (
            dataflow.agency.id
            if isinstance(dataflow.agency, Agency)
            else dataflow.agency
        )

        q = AvailabilityQuery(
            DataContext.DATAFLOW,
            aid,
            dataflow.id,
            dataflow.version,
            references=StructureReference.ALL,
            mode=AvailabilityMode.EXACT,
        )
        try:
            out = self.__client.availability(q)
        except errors.NotFound:
            url = q.get_url(ApiVersion.V2_0_0, True)
            self.__raise_dataflow_nf_error(url)
        try:
            if out:
                dfi = _FLOWS_DEC.decode(out).to_model()
            else:
                url = q.get_url(ApiVersion.V2_0_0, True)
                self.__raise_dataflow_nf_error(url)
        except msgspec.MsgspecError as e:
            self.__raise_deserialization_error(e, out)

        return dfi[0]

    def data(
        self,
        dataflow: Union[str, MaintainableIdentification],
        filters: Optional[
            Union[MultiFilter, NumberFilter, TextFilter, str]
        ] = None,
    ) -> Generator[dict[str, int], None, None]:
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
        if isinstance(dataflow, str):
            dataflow = parse_maintainable_urn(dataflow)
        aid = (
            dataflow.agency.id
            if isinstance(dataflow.agency, Agency)
            else dataflow.agency
        )

        if isinstance(filters, str):
            filters = parse_query(filters)

        q = DataQuery(
            DataContext.DATAFLOW,
            aid,
            dataflow.id,
            dataflow.version,
            components=filters,
            obs_dimension="AllDimensions",
        )

        try:
            out = self.__client.data(q)
            text_stream = io.TextIOWrapper(io.BytesIO(out), encoding="utf-8")

            # Use the csv.DictReader to parse the CSV data
            reader = csv.DictReader(text_stream)

            # Yield each row as a dictionary
            for row in reader:
                yield row

            # Close the TextIOWrapper to free resources
            text_stream.close()
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
                "valid SDMX-JSON v2.0.0 Structure message containing "
                "dataflows."
            ),
            {
                "original_exception": str(error),
                "service_response": msg.decode("utf-8", errors="replace"),
                "endpoint": self.__client._api_endpoint,
            },
        ) from error

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
