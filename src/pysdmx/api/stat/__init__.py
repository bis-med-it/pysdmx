"""Download and submission connectors for SDMX .Stat Suite services."""

from __future__ import annotations

from enum import Enum
from io import BytesIO
from typing import (
    TYPE_CHECKING,
    Any,
    Mapping,
    NoReturn,
    Optional,
    Sequence,
    Union,
)

import httpx
from msgspec import structs

from pysdmx import errors
from pysdmx.api.dc.rest import SdmxConnector
from pysdmx.api.qb import (
    ApiVersion,
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
from pysdmx.io import get_datasets, read_sdmx
from pysdmx.io.format import Format
from pysdmx.io.writer import write_sdmx
from pysdmx.model import Dataflow, DataStructureDefinition, Schema
from pysdmx.model.__base import MaintainableArtefact
from pysdmx.model.dataset import Dataset
from pysdmx.model.message import Message
from pysdmx.util import experimental, parse_short_urn
from pysdmx.util._model_utils import schema_generator
from pysdmx.util._net_utils import BearerAuth, map_httpx_errors

if TYPE_CHECKING:  # pragma: no cover
    from pysdmx.io.pd import PandasDataset


class StatEndpoints(str, Enum):
    """Public .Stat Suite SDMX-REST v2 entry points.

    Each entry is verified to serve structural metadata as SDMX-ML 2.1
    over the SDMX-REST v2 API. Other .Stat deployments can be used by
    passing their entry-point URL directly.
    """

    OECD = "https://sdmx.oecd.org/public/rest/v2"
    ILO = "https://sdmx.ilo.org/rest/v2"
    ABS = "https://data.api.abs.gov.au/rest/v2"
    PACIFIC = "https://stats-sdmx-disseminate.pacificdata.org/rest/v2"
    STATEC = "https://lustat.statec.lu/rest/v2"


@experimental
class StatConnector(SdmxConnector):
    """Download connector for .Stat Suite SDMX-REST v2 services.

    .Stat Suite deployments (e.g. OECD dotStatSuite) serve structural
    metadata as SDMX-ML 2.1 and data as SDMX-CSV, and do not expose the
    SDMX-REST ``/schema`` endpoint. The ``fetch_*`` methods retrieve a
    single SDMX-ML 2.1 structure message (with descendants) plus
    SDMX-CSV 1.0.0 data, and rely on pysdmx's native readers to produce
    a ``Dataflow``, a ``Schema`` and a ``PandasDataset``.

    This connector inherits :class:`pysdmx.api.dc.rest.SdmxConnector`.
    Its inherited ``dataflow``/``dataflows``/``data`` methods assume
    SDMX-JSON and are disabled here; use ``fetch_dataflow``/
    ``fetch_schema``/``fetch_dataset`` instead.

    Obtain the ``agency``, ``id`` and ``version`` of a dataflow from the
    OECD Data Explorer (https://data-explorer.oecd.org) via its
    "Developer API" button.
    """

    def __init__(
        self,
        api_endpoint: str = StatEndpoints.OECD,
        pem: Optional[str] = None,
        timeout: Optional[float] = 20.0,
    ) -> None:
        """Instantiate a .Stat Suite download connector.

        Args:
            api_endpoint: The SDMX-REST v2 entry point. Defaults to the
                OECD public service.
            pem: Optional PEM file with trusted certificate authorities,
                for services using a self-signed certificate.
            timeout: Maximum number of seconds to wait per request.
        """
        super().__init__(api_endpoint, pem=pem, timeout=timeout)
        self._svc = RestService(
            api_endpoint,
            ApiVersion.V2_0_0,
            data_format=DataFormat.SDMX_CSV_1_0_0,
            structure_format=StructureFormat.SDMX_ML_2_1,
            timeout=timeout,
            pem=pem,
        )

    def _structure_query(
        self, agency: str, id: str, version: str
    ) -> StructureQuery:
        """Build the structure query for a dataflow (with descendants)."""
        return StructureQuery(
            StructureType.DATAFLOW,
            agency,
            id,
            version,
            detail=StructureDetail.FULL,
            references=StructureReference.DESCENDANTS,
        )

    def _fetch_structure(self, agency: str, id: str, version: str) -> Message:
        """Fetch and parse the SDMX-ML 2.1 structure (with descendants)."""
        q = self._structure_query(agency, id, version)
        raw = self._svc.structure(q)
        return read_sdmx(BytesIO(raw), validate=False)

    def _find_dataflow(
        self, msg: Message, agency: str, id: str, version: str
    ) -> Dataflow:
        """Return the requested Dataflow from a structure message."""
        target = f"Dataflow={agency}:{id}({version})"
        for artefact in msg.structures or []:
            if isinstance(artefact, Dataflow) and artefact.short_urn == target:
                return artefact
        raise errors.NotFound(
            "Dataflow not found",
            (
                f"No dataflow {agency}:{id}({version}) was returned by "
                "the service. Verify the agency, id and version."
            ),
        )

    def _find_dsd(self, msg: Message) -> DataStructureDefinition:
        """Return the data structure definition in a structure message."""
        for artefact in msg.structures or []:
            if isinstance(artefact, DataStructureDefinition):
                return artefact
        raise errors.NotFound(
            "Data structure not found",
            "The structure message did not include a data structure "
            "definition. Re-run the structure query with references.",
        )

    def _build_key(
        self, dsd: DataStructureDefinition, filters: Mapping[str, str]
    ) -> str:
        """Build a positional series key from dimension filters."""
        dims = [d for d in dsd.components.dimensions if d.id != "TIME_PERIOD"]
        unknown = sorted(f for f in filters if f not in {d.id for d in dims})
        if unknown:
            valid = sorted(d.id for d in dims)
            raise errors.Invalid(
                "Invalid filter",
                f"Unknown dimension(s): {unknown}. Valid: {valid}.",
            )
        return ".".join(filters.get(d.id, "*") for d in dims)

    def fetch_dataflow(self, agency: str, id: str, version: str) -> Dataflow:
        """Get the dataflow matching the supplied identification.

        The dataflow's data structure definition is grafted onto the
        returned object so that ``Dataflow.components`` is populated; a
        plain parse leaves ``structure`` as a URN and ``components`` None.

        Args:
            agency: The agency maintaining the dataflow.
            id: The dataflow ID.
            version: The dataflow version.

        Returns:
            The dataflow, including its components (from the DSD).

        Raises:
            errors.NotFound: If the dataflow or its DSD is not returned.
            errors.Invalid: If the service returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        msg = self._fetch_structure(agency, id, version)
        flow = self._find_dataflow(msg, agency, id, version)
        dsd = self._find_dsd(msg)
        return structs.replace(flow, structure=dsd)

    def fetch_schema(self, agency: str, id: str, version: str) -> Schema:
        """Get the data validity schema for a dataflow.

        The schema is derived from the dataflow's data structure
        definition, as .Stat Suite services do not expose the
        SDMX-REST ``/schema`` endpoint.

        Args:
            agency: The agency maintaining the dataflow.
            id: The dataflow ID.
            version: The dataflow version.

        Returns:
            The dataflow-context schema (components and their types).

        Raises:
            errors.NotFound: If the dataflow is not returned.
            errors.Invalid: If the service returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        msg = self._fetch_structure(agency, id, version)
        flow = self._find_dataflow(msg, agency, id, version)
        return schema_generator(msg, parse_short_urn(flow.short_urn))

    def fetch_dataset(
        self,
        agency: str,
        id: str,
        version: str,
        key: Optional[str] = None,
        filters: Optional[Mapping[str, str]] = None,
    ) -> "PandasDataset":
        """Get data for a dataflow as a typed Pandas dataset.

        Filter the data either with ``filters`` (a mapping of dimension
        ID to a single value, resolved to a positional series key using
        the data structure) or with a raw positional ``key``. .Stat
        services key on one value per dimension; for multiple values
        issue separate requests.

        Args:
            agency: The agency maintaining the dataflow.
            id: The dataflow ID.
            version: The dataflow version.
            key: A raw positional series key (dimensions in DSD order,
                ``.``-separated, ``*`` to wildcard a dimension).
            filters: A mapping of dimension ID to a single value, e.g.
                ``{"REF_AREA": "CHN", "FREQ": "M"}``.

        Returns:
            The requested data as a ``PandasDataset`` with its schema.

        Raises:
            errors.Invalid: If both ``key`` and ``filters`` are supplied,
                or a filter targets an unknown dimension.
            errors.NotFound: If no data or dataflow is returned.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        if key is not None and filters is not None:
            raise errors.Invalid(
                "Invalid query",
                "Provide either 'key' or 'filters', not both.",
            )
        q = self._structure_query(agency, id, version)
        raw = self._svc.structure(q)
        if filters is not None:
            dsd = self._find_dsd(read_sdmx(BytesIO(raw), validate=False))
            key = self._build_key(dsd, filters)
        dq = DataQuery(
            DataContext.DATAFLOW,
            agency,
            id,
            version,
            key=key or "*",
            obs_dimension="AllDimensions",
        )
        data = self._svc.data(dq)
        return get_datasets(BytesIO(data), BytesIO(raw), validate=False)[0]

    def _unsupported(self, *args: object, **kwargs: object) -> NoReturn:
        """Reject an inherited SDMX-JSON method (use ``fetch_*``)."""
        raise errors.NotImplemented(
            "Not supported by .Stat",
            "The inherited SDMX-JSON methods do not work against .Stat "
            "services. Use fetch_dataflow / fetch_schema / fetch_dataset.",
        )

    # The inherited SDMX-JSON methods do not work against .Stat services.
    dataflow = dataflows = data = _unsupported


_STRUCTURE_CT = "application/vnd.sdmx.structure+xml;version=2.1"
_DATA_CT = "application/vnd.sdmx.data+csv;version=2.0.0"


@experimental
class StatUploader:
    """Submit structures and data to a .Stat Suite service.

    .Stat Suite splits submission across two services: structural
    metadata goes to the NSI web service (``POST /rest/structure``,
    SDMX-ML 2.1) and data goes to the Transfer service
    (``POST /import/sdmxFile``, SDMX-CSV 2.0, asynchronous). Both require
    an OAuth2 / Keycloak bearer token. Payloads are built with pysdmx's
    :func:`pysdmx.io.write_sdmx`.

    Data submission is asynchronous: it returns a request id that can be
    polled with :meth:`submission_status`. The targeted dataflow's
    structure must already exist before its data is loaded, so use
    :meth:`submit` (structure first, then data) for a new dataflow.

    This class is standalone (it does not inherit
    :class:`pysdmx.api.dc.rest.SdmxConnector`): submission needs
    authenticated ``POST`` requests, whereas the connector's
    ``RestService`` only performs anonymous ``GET`` requests.
    """

    def __init__(
        self,
        nsi_endpoint: str,
        transfer_endpoint: str,
        token: Optional[str] = None,
        pem: Optional[str] = None,
        timeout: Optional[float] = 60.0,
    ) -> None:
        """Instantiate a .Stat Suite submission connector.

        Args:
            nsi_endpoint: The NSI web service entry point used for
                structure submission (host of ``/rest/structure``).
            transfer_endpoint: The Transfer service entry point used for
                data submission (host of ``/import/sdmxFile``).
            token: An OAuth2 bearer token. Required for every submission
                and status call; obtain one with :meth:`fetch_token`.
            pem: Optional PEM file with trusted certificate authorities,
                for services using a self-signed certificate.
            timeout: Maximum number of seconds to wait per request.
        """
        self._nsi = nsi_endpoint.rstrip("/")
        self._transfer = transfer_endpoint.rstrip("/")
        self._token = token
        self._ssl = (
            httpx.create_ssl_context(verify=pem)
            if pem
            else httpx.create_ssl_context()
        )
        self._timeout = timeout

    def _request(
        self,
        method: str,
        url: str,
        content: Optional[str] = None,
        content_type: Optional[str] = None,
        params: Optional[Mapping[str, str]] = None,
    ) -> str:
        """Send an authenticated request; return the response text.

        Args:
            method: The HTTP method (``POST`` or ``GET``).
            url: The absolute request URL.
            content: An optional request body.
            content_type: The optional ``Content-Type`` header value.
            params: Optional query-string parameters (URL-encoded by
                the client).

        Returns:
            The response body as text.

        Raises:
            errors.Unauthorized: If no token was configured, or the
                service rejected it (HTTP 401/403).
            errors.Invalid: If the service returned another client error.
            errors.InternalError: If the service returned a server error.
            errors.Unavailable: If the service could not be reached.
        """
        if self._token is None:
            raise errors.Unauthorized(
                "Missing token",
                "A bearer token is required for .Stat submission "
                "operations. Pass token=... or use fetch_token().",
            )
        headers = {"Content-Type": content_type} if content_type else {}
        try:
            with httpx.Client(
                verify=self._ssl, follow_redirects=True
            ) as client:
                r = client.request(
                    method,
                    url,
                    content=content,
                    params=params,
                    headers=headers,
                    auth=BearerAuth(self._token),
                    timeout=self._timeout,
                )
                if r.status_code in (401, 403):
                    raise errors.Unauthorized(
                        "Unauthorized",
                        f"The service rejected the token "
                        f"({r.status_code}). The request was `{url}`.",
                    )
                r.raise_for_status()
                return r.text
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            map_httpx_errors(e)

    def submit_structure(
        self, structures: Union[MaintainableArtefact, Sequence[Any]]
    ) -> str:
        """Submit structural metadata to the NSI web service.

        The artefact(s) are serialized to SDMX-ML 2.1 with
        :func:`write_sdmx` and posted to ``{nsi}/rest/structure``.

        Args:
            structures: A maintainable artefact (e.g. a ``Codelist`` or
                ``Dataflow``) or a sequence of maintainable artefacts.

        Returns:
            The service response body as text.

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If the service returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        body = write_sdmx(structures, Format.STRUCTURE_SDMX_ML_2_1)
        return self._request(
            "POST", f"{self._nsi}/rest/structure", body, _STRUCTURE_CT
        )

    def submit_data(self, dataset: Union[Dataset, Sequence[Dataset]]) -> str:
        """Submit data to the Transfer service.

        The dataset is serialized to SDMX-CSV 2.0 with :func:`write_sdmx`
        and posted to ``{transfer}/import/sdmxFile``. The dataset must be
        Schema-backed (e.g. produced by ``StatConnector.fetch_dataset``
        or ``pysdmx.io.get_datasets``); a dataset whose structure is a
        bare URN cannot be written as SDMX-CSV 2.0.

        Submission is asynchronous: the returned request id can be polled
        with :meth:`submission_status`.

        Args:
            dataset: A Schema-backed dataset, or a sequence of them.

        Returns:
            The async submission request id (the service response text).

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If the service returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        body = write_sdmx(dataset, Format.DATA_SDMX_CSV_2_0_0)
        return self._request(
            "POST", f"{self._transfer}/import/sdmxFile", body, _DATA_CT
        )

    def submit(
        self,
        structures: Union[MaintainableArtefact, Sequence[Any]],
        dataset: Union[Dataset, Sequence[Dataset]],
    ) -> str:
        """Submit the structure(s) first, then the data.

        .Stat Suite requires a dataflow's structure to exist before its
        data can be loaded, so the structure is submitted synchronously
        and only then is the (asynchronous) data submission started.

        Args:
            structures: The structural metadata to submit first.
            dataset: The data to submit once the structure is in place.

        Returns:
            The async data submission request id.

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If the service returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        self.submit_structure(structures)
        return self.submit_data(dataset)

    def submission_status(self, request_id: str) -> str:
        """Poll the status of an asynchronous data submission.

        Args:
            request_id: The request id returned by :meth:`submit_data`
                or :meth:`submit`.

        Returns:
            The Transfer service status response as text.

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If the service returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        url = f"{self._transfer}/status/request"
        return self._request("GET", url, params={"id": request_id})

    @staticmethod
    def fetch_token(
        token_url: str, client_id: str, username: str, password: str
    ) -> str:
        """Obtain a bearer token via the Keycloak password grant.

        Performs the OAuth2 resource-owner password-credentials grant
        against the instance's Keycloak token endpoint. The instance must
        have "Direct Access Grants" enabled for the client.

        Args:
            token_url: The Keycloak token endpoint
                (``.../protocol/openid-connect/token``).
            client_id: The OAuth2 client id.
            username: The account user name.
            password: The account password.

        Returns:
            The access token.

        Raises:
            errors.Invalid: If the token endpoint rejects the request
                (e.g. bad credentials) or returns another client error.
            errors.InternalError: If the token endpoint returns a server
                error.
            errors.Unavailable: If the token endpoint cannot be reached.
        """
        try:
            with httpx.Client() as client:
                r = client.post(
                    token_url,
                    data={
                        "grant_type": "password",
                        "client_id": client_id,
                        "username": username,
                        "password": password,
                    },
                    timeout=60.0,
                )
                r.raise_for_status()
                data = r.json()
                token: str = data["access_token"]
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            # A rejected grant (e.g. 401 bad credentials) maps to a
            # client Invalid here, unlike _request where a rejected token
            # raises Unauthorized.
            map_httpx_errors(e)
        except (KeyError, TypeError, ValueError) as e:
            raise errors.Invalid(
                "Invalid token response",
                "The token endpoint did not return a valid "
                f"'access_token'. The query was `{token_url}`.",
            ) from e
        return token


__all__ = ["StatConnector", "StatEndpoints", "StatUploader"]
