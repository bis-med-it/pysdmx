"""Submission (upload) connector for SDMX .Stat Suite services."""

from __future__ import annotations

from typing import Any, Optional, Sequence, Union

import httpx

from pysdmx import errors
from pysdmx.io.format import Format
from pysdmx.io.writer import write_sdmx
from pysdmx.model.__base import MaintainableArtefact
from pysdmx.model.dataset import Dataset
from pysdmx.util import experimental
from pysdmx.util._net_utils import BearerAuth, map_httpx_errors

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
    ) -> str:
        """Send an authenticated request; return the response text.

        Args:
            method: The HTTP method (``POST`` or ``GET``).
            url: The absolute request URL.
            content: An optional request body.
            content_type: The optional ``Content-Type`` header value.

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
        url = f"{self._transfer}/status/request?id={request_id}"
        return self._request("GET", url)

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
                token: str = r.json()["access_token"]
                return token
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            map_httpx_errors(e)
