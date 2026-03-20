"""A connector for SDMX-REST services."""

from typing import NoReturn, Optional

import msgspec

from pysdmx import errors
from pysdmx.api.dc import BasicConnector
from pysdmx.api.qb import (
    ApiVersion,
    RestService,
    StructureDetail,
    StructureFormat,
    StructureQuery,
    StructureType,
)
from pysdmx.io.json.sdmxjson2.messages import JsonDataflowsMessage
from pysdmx.model import Agency, Dataflow, decoders

_FLOW_DEC = msgspec.json.Decoder(JsonDataflowsMessage, dec_hook=decoders)


class SdmxConnector(BasicConnector):
    """An SDMX-REST connector for data discovery and data retrieval.

    This connector is an implementation of the SDMX "data discovery and
    data retrieval" API for SDMX-REST v2 web services.
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
            structure_format=StructureFormat.SDMX_JSON_2_0_0,
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
                matching the supplied search term, if any. If a search term
                is supplied and does not match any dataflow, an empty
                collection will be returned. The collection is sorted by
                agency ID, then dataflow ID and then version number.

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
            flows = _FLOW_DEC.decode(out).to_model()
        except msgspec.MsgspecError as e:
            self.__raise_deserialization_error(e, out)

        if not flows:
            self.__raise_no_dataflow_error(out)

        if search_term:
            st = search_term.strip().lower()
            if st:
                flows = [f for f in flows if self.__match_search_term(f, st)]
        return tuple(sorted(flows, key=self.__sort_maintainable))

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

    def __raise_no_dataflow_error(self, msg: bytes) -> NoReturn:
        raise errors.NotFound(
            "No dataflows found.",
            (
                "No dataflows could be found in the targeted service. "
                "This is a violation of the SDMX data discovery and data "
                "retrieval profile, as its purpose is to retrieve data "
                "from dataflows."
            ),
            {
                "service_response": msg.decode("utf-8", errors="replace"),
                "endpoint": self.__client._api_endpoint,
            },
        )
