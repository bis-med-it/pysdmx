"""Upload metadata to an FMR instance."""

import warnings
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, Sequence, Union

import httpx
import msgspec

from pysdmx.errors import InternalError, Invalid, NotImplemented, Unauthorized
from pysdmx.io.json.sdmxjson2.writer import serializers
from pysdmx.model import AvailabilityConstraint, MetadataReport
from pysdmx.model.__base import MaintainableArtefact
from pysdmx.model.message import (
    Header,
    MetadataMessage,
    StructureMessage,
)
from pysdmx.util import experimental
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


class RegistryTxHeader(
    msgspec.Struct,
    frozen=True,
    rename={"transaction_id": "txId", "transaction_time": "txTs"},
):
    """Metainformation for a Registry transaction.

    Contains metadata about a transaction, such as its unique identifier.

    Attributes:
        transaction_id: The unique identifier for the transaction.

    Properties:
        transaction_time: The time at which the transaction occurred, in UTC.
    """

    transaction_id: str
    txTs: int

    @property
    def transaction_time(self) -> datetime:
        """Return the transaction time as a UTC datetime."""
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        return epoch + timedelta(milliseconds=self.txTs)


class RegistryTxPayload(
    msgspec.Struct,
    frozen=True,
    rename={"inserted": "ins", "updated": "upd", "deleted": "del"},
):
    """Payload content for a Registry transaction.

    Contains lists of URNs for artefacts that were inserted, updated, or
    deleted in the Registry as part of a transaction.

    Attributes:
        inserted: Sequence of URNs for newly inserted artefacts
        updated: Sequence of URNs for modified artefacts
        deleted: Sequence of URNs for removed artefacts
    """

    inserted: Sequence[str] = ()
    updated: Sequence[str] = ()
    deleted: Sequence[str] = ()


class RegistryTx(msgspec.Struct, frozen=True):
    """Registry transaction structure.

    Attributes:
        meta: Metainformation about the transaction
        data: Payload containing the URNs of affected artefacts
    """

    meta: RegistryTxHeader
    data: RegistryTxPayload


@experimental
class RegistryTransactionsClient:
    """EXPERIMENTAL: Client for accessing FMR registry transactions.

    Args:
        api_endpoint: The endpoint of the target FMR service.
        pem: A PEM file for an otherwise untrusted certificate authority.
        timeout: The maximum number of seconds to wait for a request. Defaults
            to 60 seconds.
    """

    def __init__(
        self,
        api_endpoint: str,
        pem: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        """Instantiate a registry transactions client."""
        self._api_endpoint = self._sanitize_endpoint(api_endpoint)
        self._timeout = timeout
        self._ssl_context = (
            httpx.create_ssl_context(
                verify=pem,
            )
            if pem
            else httpx.create_ssl_context()
        )

    def _sanitize_endpoint(self, endpoint: str) -> str:
        if endpoint.endswith("/"):
            endpoint = endpoint[0:-1]
        endpoint = endpoint.replace("/ws/secure/sdmx/v2/metadata", "")
        endpoint = endpoint.replace("/sdmx/v2", "")
        endpoint = endpoint.replace("/ws/secure/sdmxapi/rest", "")
        return endpoint

    def __get(self, endpoint: str) -> bytes:
        with httpx.Client(verify=self._ssl_context) as client:
            try:
                response = client.get(endpoint, timeout=self._timeout)
                response.raise_for_status()
            except (httpx.RequestError, httpx.HTTPStatusError) as error:
                map_httpx_errors(error)
            return response.content

    def list_transactions(
        self, updated_after: Optional[datetime] = None
    ) -> Sequence[RegistryTx]:
        """List transactions that occurred after an optional point in time.

        Args:
            updated_after: Return only transactions updated after this time.
                If not provided, return all transactions. A timezone-naive
                datetime is interpreted as UTC.

        Returns:
            The transactions returned by the FMR.
        """
        endpoint = f"{self._api_endpoint}/ws/registry/transactions"
        if updated_after is not None:
            if updated_after.tzinfo is None:
                updated_after = updated_after.replace(tzinfo=timezone.utc)
            timestamp = int(updated_after.timestamp() * 1000)
            endpoint = f"{endpoint}?updatedAfter={timestamp}"
        return msgspec.json.decode(self.__get(endpoint), type=list[RegistryTx])

    def get_transaction(
        self, transaction_id: str
    ) -> Union[StructureMessage, MetadataMessage]:
        """Retrieve the content of a registry transaction.

        Args:
            transaction_id: The identifier of the transaction to retrieve.

        Returns:
            The SDMX structure or reference metadata message contained in the
            transaction.

        Raises:
            InternalError: If the transaction content cannot be read as an
                SDMX structure or reference metadata message.
        """
        from pysdmx.io.reader import read_sdmx

        endpoint = (
            f"{self._api_endpoint}/ws/registry/transactions/{transaction_id}"
        )
        content = self.__get(endpoint).decode("utf-8", errors="replace")
        try:
            message = read_sdmx(content, validate=False)
        except (Invalid, NotImplemented) as error:
            raise InternalError(
                "Unexpected transaction format",
                (
                    "The transaction content could not be read as an "
                    "SDMX message."
                ),
                {
                    "read_error": str(error),
                    "endpoint": endpoint,
                },
            ) from error

        if message.structures is not None:
            return StructureMessage(message.header, message.structures)
        if message.reports is not None:
            return MetadataMessage(message.header, message.reports)

        raise InternalError(
            "Unexpected transaction format",
            (
                "The transaction content is neither an SDMX structure nor "
                "reference metadata message."
            ),
            {"endpoint": endpoint},
        )


class RegistryMaintenanceClient(RegistryTransactionsClient):
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
        super().__init__(api_endpoint, pem, timeout)
        self._user = user
        self._password = password
        self._access_token = access_token

        if self._access_token is None and not (self._user and self._password):
            raise Unauthorized(
                "Missing authentication",
                (
                    "Authentication requires either access_token or both "
                    "user and password, but none were provided."
                ),
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
                Availability constraints are not maintainable artefacts
                and are skipped with a warning if present (e.g. when
                passing the ``structures`` of a message returned by an
                availability query).
            header: Optional SDMX Header to include in the message. If not
                supplied, pysdmx will generate one for you.
            action: How to apply the changes in case of already existing
                structures.

        Warns:
            UserWarning: If ``artefacts`` contains availability constraints.
                They are not maintainable artefacts and, therefore, they
                are not meant to be stored in the FMR, so they are skipped.
        """
        if not header:
            header = Header()
        # The contract admits maintainable artefacts only, but callers may
        # pass the ``structures`` of a message read from an availability
        # query, which can also hold availability constraints. Widen the
        # element type so the runtime filter is a genuine check for mypy.
        candidates: Sequence[
            Union[MaintainableArtefact, AvailabilityConstraint]
        ] = artefacts
        structures = [
            a for a in candidates if not isinstance(a, AvailabilityConstraint)
        ]
        if len(structures) != len(artefacts):
            warnings.warn(
                "Availability constraints are not maintainable artefacts "
                "and, therefore, they are not meant to be stored in the FMR: "
                f"{len(artefacts) - len(structures)} skipped.",
                UserWarning,
                stacklevel=2,
            )
        message = StructureMessage(header=header, structures=structures)
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
