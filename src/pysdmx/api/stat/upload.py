"""Submission (upload) connector for SDMX .Stat Suite services."""

from __future__ import annotations

from typing import Optional

import httpx

from pysdmx.util import experimental


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
