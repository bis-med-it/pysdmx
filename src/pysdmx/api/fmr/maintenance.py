"""Upload metadata to an FMR instance."""

from enum import Enum
from typing import Optional, Sequence, Union

import httpx
import msgspec

from pysdmx.errors import Unauthorized
from pysdmx.io.json.sdmxjson2.writer import serializers
from pysdmx.model import MetadataReport
from pysdmx.model.__base import MaintainableArtefact
from pysdmx.model.message import (
    Header,
    MetadataMessage,
    StructureMessage,
)
from pysdmx.util._net_utils import BearerAuth, map_httpx_errors


class StructureAction(Enum):
    """Enumeration that defines the action when updating metadata in the FMR.

    Arguments:
        Append: Metadata uploaded with action 'Append' may only add new
            metadata and may not overwrite any existing metadata, i.e. any
            attempt to update existing metadata will be rejected.
        Merge: Metadata uploaded with action 'Merge' may add new metadata and
            replace existing metadata. However, for Item Schemes (codelists,
            concept schemes, etc.), the items submitted will be added to the
            existing scheme. For example, if a codelist exists with codes A, B,
            and C, and the same codelist is submitted with codes B and X, then
            the resulting codelist will have codes A, B, C, X, i.e. code B has
            been replaced while code X has been added.
        Replace: Metadata uploaded with action 'Replace' may add new metadata,
            and can also replace existing metadata with new ones. This is the
            default.
    """

    Append = "Append"
    Merge = "Merge"
    Replace = "Replace"


class RegistryMaintenanceClient:
    """EXPERIMENTAL: A client to update metadata in the FMR.

    The client supports two authentication modes:

    - Bearer token authentication via ``access_token``
    - HTTP Basic authentication via ``user`` and ``password``

    If ``access_token`` is provided, it takes precedence over ``user`` and
    ``password``.

    The client does not obtain or refresh OIDC/OAuth2 tokens itself. It is the
    responsibility of the caller to acquire a valid access token from their
    authentication provider and pass it to this client.
    """

    def __init__(
        self,
        api_endpoint: str,
        user: Optional[str] = None,
        password: Optional[str] = None,
        access_token: Optional[str] = None,
        pem: Optional[str] = None,
        timeout: float = 60.0,
    ):
        """Instantiate a new client to update metadata in the target endpoint.

        Args:
            api_endpoint: The endpoint of the targeted service.
            user: Username for HTTP Basic authentication. Optional if
                ``access_token`` is provided.
            password: Password for HTTP Basic authentication. Optional if
                ``access_token`` is provided.
            access_token: Bearer access token to use for authentication. If
                provided, it takes precedence over ``user`` and ``password``.
                The caller is responsible for obtaining this token.
            pem: In case the service exposed a certificate created by an
                unknown certificate authority, you can pass a pem file for
                this authority using this parameter.
            timeout: The maximum number of seconds to wait before considering
                that a request timed out. Defaults to 60 seconds.

        Raises:
            Unauthorized: If neither ``access_token`` nor both ``user`` and
                ``password`` are provided.
        """
        self._api_endpoint = self.__sanitize_endpoint(api_endpoint)
        self._user = user
        self._password = password
        self._access_token = access_token
        self._timeout = timeout

        if self._access_token is None and not (self._user and self._password):
            raise Unauthorized(
                "Missing authentication",
                (
                    "Authentication requires either access_token or both "
                    "user and password, but none were provided."
                ),
            )

        self._ssl_context = (
            httpx.create_ssl_context(
                verify=pem,
            )
            if pem
            else httpx.create_ssl_context()
        )
        self._encoder = msgspec.json.Encoder()

    def __build_auth(self) -> httpx.Auth:
        """Build the authentication strategy for outgoing requests.

        Returns:
            An ``httpx.Auth`` instance.

        Notes:
            If ``access_token`` is set, bearer-token authentication is used
            and takes precedence over ``user`` and ``password``.
        """
        if self._access_token is not None:
            return BearerAuth(self._access_token)

        return httpx.BasicAuth(self._user, self._password)  # type: ignore[arg-type]

    def __post(
        self,
        message: Union[MetadataMessage, StructureMessage],
        action: StructureAction,
        endpoint: str,
    ) -> None:
        with httpx.Client(verify=self._ssl_context) as client:
            try:
                auth = self.__build_auth()
                headers = {
                    "Content-Type": "application/text",
                    "Action": action.value,
                }
                if isinstance(message, MetadataMessage):
                    serializer = serializers.metadata_message
                else:
                    serializer = serializers.structure_message
                bodyjs = self._encoder.encode(serializer.from_model(message))
                r = client.post(
                    endpoint,
                    headers=headers,
                    content=bodyjs,
                    timeout=self._timeout,
                    auth=auth,
                )
                r.raise_for_status()
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                map_httpx_errors(e)

    def put_structures(
        self,
        artefacts: Sequence[MaintainableArtefact],
        header: Optional[Header] = None,
        action: StructureAction = StructureAction.Replace,
    ) -> None:
        """EXPERIMENTAL: Upload SDMX structures to the FMR.

        This method is experimental and its interface or behavior may change
        without notice.

        Args:
            artefacts: The sequence of SDMX maintainable artefacts to upload.
            header: Optional SDMX Header to include in the message. If not
                supplied, pysdmx will generate one for you.
            action: How to apply the changes in case of already existing
                structures.
        """
        if not header:
            header = Header()
        message = StructureMessage(header=header, structures=artefacts)
        endpoint = f"{self._api_endpoint}/ws/secure/sdmxapi/rest"
        return self.__post(message, action, endpoint)

    def put_metadata_reports(
        self,
        reports: Sequence[MetadataReport],
        header: Optional[Header] = None,
        action: StructureAction = StructureAction.Replace,
    ) -> None:
        """EXPERIMENTAL: Upload SDMX metadata reports to the FMR.

        This method is experimental and its interface or behavior may change
        without notice.

        Args:
            reports: A sequence of metadata reports to upload.
            header: Optional SDMX Header to include in the message. If not
                supplied, pysdmx will generate one for you.
            action: How to apply the changes in case of already existing
                structures.
        """
        if not header:
            header = Header()
        message = MetadataMessage(header=header, reports=reports)
        endpoint = f"{self._api_endpoint}/ws/secure/sdmx/v2/metadata"
        return self.__post(message, action, endpoint)

    def __sanitize_endpoint(self, endpoint: str) -> str:
        if endpoint.endswith("/"):
            endpoint = endpoint[0:-1]
        endpoint = endpoint.replace("/ws/secure/sdmx/v2/metadata", "")
        endpoint = endpoint.replace("/sdmx/v2", "")
        endpoint = endpoint.replace("/ws/secure/sdmxapi/rest", "")
        return endpoint
