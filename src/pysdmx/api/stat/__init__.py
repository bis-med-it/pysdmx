"""Download and submission connectors for SDMX .Stat Suite services."""

from __future__ import annotations

import json
import re
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
from msgspec import Struct, structs

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
from pysdmx.model.__base import DataType, MaintainableArtefact
from pysdmx.model.dataset import ActionType, Dataset
from pysdmx.model.message import Message
from pysdmx.util import experimental, parse_short_urn
from pysdmx.util._model_utils import schema_generator
from pysdmx.util._net_utils import BearerAuth, map_httpx_errors

if TYPE_CHECKING:  # pragma: no cover
    from pysdmx.io.pd import PandasDataset

# SDMX time-period data types, used to detect the time dimension (which
# is excluded from a positional series key) without hard-coding its id.
_TIME_DTYPES = frozenset(
    {
        DataType.PERIOD,
        DataType.TIME,
        DataType.TIME_RANGE,
        DataType.STD_TIME_PERIOD,
        DataType.BASIC_TIME_PERIOD,
        DataType.GREGORIAN_TIME_PERIOD,
        DataType.REP_TIME_PERIOD,
    }
)


class SubmissionResult(Struct, frozen=True, repr_omit_defaults=True):
    """Outcome of a .Stat data submission or status poll.

    Attributes:
        success: Whether the operation succeeded.
        message: The service message (or raw body when not JSON).
        request_id: The async transaction id, when known.
        execution_status: The status poll's execution status, if any.
        outcome: The status poll's outcome, if any.
        logs: Any log lines returned by a status poll.
    """

    success: bool
    message: str = ""
    request_id: Optional[int] = None
    execution_status: Optional[str] = None
    outcome: Optional[str] = None
    logs: tuple[str, ...] = ()


class StructureSubmissionResult(Struct, frozen=True, repr_omit_defaults=True):
    """Outcome of a .Stat structure submission or deletion.

    Attributes:
        success: True when every reported artefact code is 200/201.
        messages: The per-artefact messages the service returned.
    """

    success: bool
    messages: tuple[str, ...] = ()


def _submission_from_import(text: str) -> SubmissionResult:
    """Parse a Transfer ``OperationResult`` (import/delete ack)."""
    try:
        payload = json.loads(text)
    except ValueError:
        return SubmissionResult(success=False, message=text.strip())
    data = payload if isinstance(payload, dict) else {}
    lower = {k.lower(): v for k, v in data.items()}
    message = str(lower.get("message") or "")
    rid = re.search(r"ID\s+(\d+)", message)
    return SubmissionResult(
        success=bool(lower.get("success", True)),
        message=message,
        request_id=int(rid.group(1)) if rid else None,
    )


def _submission_from_status(text: str) -> SubmissionResult:
    """Parse a Transfer ``ImportSummary`` (status poll)."""
    try:
        payload = json.loads(text)
    except ValueError:
        return SubmissionResult(success=False, message=text.strip())
    if not isinstance(payload, dict):
        return SubmissionResult(success=False, message=text.strip())
    lower = {k.lower(): v for k, v in payload.items()}
    outcome = lower.get("outcome")
    logs = tuple(
        str(e.get("message") or e) if isinstance(e, dict) else str(e)
        for e in (lower.get("logs") or [])
    )
    return SubmissionResult(
        success=outcome == "Success",
        message=str(outcome or lower.get("executionstatus") or ""),
        request_id=lower.get("requestid"),
        execution_status=lower.get("executionstatus"),
        outcome=outcome,
        logs=logs,
    )


def _structure_result(text: str) -> StructureSubmissionResult:
    """Parse an NSIWS ``SubmitStructureResponse`` error envelope."""
    pairs = re.findall(
        r'code="(\d+)"[^>]*>\s*<[^>]*Text[^>]*>(.*?)</', text, re.DOTALL
    )
    return StructureSubmissionResult(
        success=all(c in {"200", "201"} for c, _ in pairs),
        messages=tuple(t.strip() for _, t in pairs),
    )


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
        token: Optional[str] = None,
    ) -> None:
        """Instantiate a .Stat Suite download connector.

        Args:
            api_endpoint: The SDMX-REST v2 entry point. Defaults to the
                OECD public service.
            pem: Optional PEM file with trusted certificate authorities,
                for services using a self-signed certificate.
            timeout: Maximum number of seconds to wait per request.
            token: An optional OAuth2 bearer token, for reading
                access-controlled dataspaces. Anonymous when omitted.
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
        if token:
            self._svc._headers["Authorization"] = f"Bearer {token}"

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
        """Return the requested Dataflow from a structure message.

        Matches on agency and id; the version is treated leniently, so a
        service that normalises the version (e.g. ``1.0`` -> ``1.0.0``)
        or a wildcard request (``~``, ``+``) still resolves to the sole
        returned dataflow.
        """
        prefix = f"Dataflow={agency}:{id}("
        matches = [
            a
            for a in msg.structures or []
            if isinstance(a, Dataflow) and a.short_urn.startswith(prefix)
        ]
        for artefact in matches:
            if artefact.short_urn == f"{prefix}{version})":
                return artefact
        if len(matches) == 1:
            return matches[0]
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
        dims = [
            d
            for d in dsd.components.dimensions
            if d.id != "TIME_PERIOD" and d.local_dtype not in _TIME_DTYPES
        ]
        unknown = sorted(f for f in filters if f not in {d.id for d in dims})
        if unknown:
            valid = sorted(d.id for d in dims)
            raise errors.Invalid(
                "Invalid filter",
                f"Unknown dimension(s): {unknown}. Valid: {valid}.",
            )
        for dim, value in filters.items():
            if any(c in value for c in ".+*"):
                raise errors.Invalid(
                    "Invalid filter value",
                    f"Value {value!r} for dimension {dim!r} contains a "
                    "reserved key character ('.', '+' or '*'). Pass one "
                    "plain code value per dimension.",
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
# The Transfer /import/sdmxFile file part must declare a plain file
# content-type from the service's whitelist (it auto-detects the SDMX
# format from the bytes); the SDMX-CSV media type is rejected there.
_DATA_FILE_CT = "text/csv"


@experimental
class StatUploader:
    """Submit structures and data to a .Stat Suite service.

    .Stat Suite splits submission across two services. Structural
    metadata goes to the **NSI web service**
    (``POST {nsi}/rest/structure``, SDMX-ML 2.1). Data goes to the
    **Transfer service** as a ``multipart/form-data`` upload
    (``POST {transfer}/import/sdmxFile``, file field ``file``) scoped to
    a **data space**; it is asynchronous and returns a transaction id
    polled via ``POST {transfer}/status/request``. Both services require
    an OAuth2 / Keycloak bearer token. Payloads are built with pysdmx's
    :func:`pysdmx.io.write_sdmx`.

    The SDMX action (Append/Replace/Merge/Delete) is carried inside the
    submitted file (the SDMX-CSV 2.0 ``ACTION`` column, or the SDMX-ML
    dataset action), not as a request parameter. A dataflow's structure
    must exist before its data is loaded, so use :meth:`submit`
    (structure first, then data) for a new dataflow.

    This class is standalone (it does not inherit
    :class:`pysdmx.api.dc.rest.SdmxConnector`): submission needs
    authenticated ``POST`` requests, whereas the connector's
    ``RestService`` only performs anonymous ``GET`` requests.
    """

    def __init__(
        self,
        nsi_endpoint: str,
        transfer_endpoint: str,
        dataspace: Optional[str] = None,
        token: Optional[str] = None,
        pem: Optional[str] = None,
        timeout: Optional[float] = 60.0,
    ) -> None:
        """Instantiate a .Stat Suite submission connector.

        Args:
            nsi_endpoint: The NSI web service entry point used for
                structure submission (host of ``/rest/structure``).
            transfer_endpoint: The Transfer service entry point,
                INCLUDING the API-version segment, e.g.
                ``https://transfer-demo.siscc.org/3`` (the service
                versions its routes: ``/3/import/sdmxFile``,
                ``/3/status/request``).
            dataspace: The default .Stat data space that data submission
                and status polling target (e.g. ``"design"``). May be
                overridden per call; one of the two is required by those
                operations.
            token: An OAuth2 bearer token. Required for every submission
                and status call; obtain one with :meth:`fetch_token`.
            pem: Optional PEM file with trusted certificate authorities,
                for services using a self-signed certificate.
            timeout: Maximum number of seconds to wait per request.
        """
        self._nsi = nsi_endpoint.rstrip("/")
        self._transfer = transfer_endpoint.rstrip("/")
        self._dataspace = dataspace
        self._token = token
        self._ssl = (
            httpx.create_ssl_context(verify=pem)
            if pem
            else httpx.create_ssl_context()
        )
        self._timeout = timeout

    def _resolve_dataspace(self, dataspace: Optional[str]) -> str:
        """Return the per-call or default data space, or raise."""
        space = dataspace if dataspace is not None else self._dataspace
        if space is None:
            raise errors.Invalid(
                "Missing data space",
                "A data space is required for .Stat data submission and "
                "status polling. Pass dataspace=... to the method or the "
                "constructor.",
            )
        return space

    def _send(
        self,
        method: str,
        url: str,
        *,
        content: Optional[str] = None,
        content_type: Optional[str] = None,
        data: Optional[Mapping[str, str]] = None,
        files: Optional[Mapping[str, Any]] = None,
    ) -> httpx.Response:
        """Send an authenticated request; return the response.

        Each call uses one body style: a raw ``content`` body (with
        ``content_type``), or form ``data`` optionally combined with
        multipart ``files`` (the client sets the content type itself).

        Args:
            method: The HTTP method (``POST`` or ``GET``).
            url: The absolute request URL.
            content: An optional raw request body.
            content_type: The ``Content-Type`` for a raw ``content``
                body. Omit for form/multipart requests so the client can
                set it (with the multipart boundary).
            data: Optional form fields (URL-encoded, or multipart when
                combined with ``files``).
            files: Optional multipart file parts.

        Returns:
            The successful HTTP response.

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
                    data=data,
                    files=files,
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
                return r
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
            The NSI ``SubmitStructureResponse`` body (SDMX-ML). Inspect
            it for the per-artefact outcome: the service can report a
            failure inside the body even on an HTTP 200 response.

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If the service returns a client error, or
                reports a partial failure (HTTP 207 Multi-Status).
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        body = write_sdmx(structures, Format.STRUCTURE_SDMX_ML_2_1)
        r = self._send(
            "POST",
            f"{self._nsi}/rest/structure",
            content=body,
            content_type=_STRUCTURE_CT,
        )
        if r.status_code == 207:
            raise errors.Invalid(
                "Partial structure submission",
                "The service reported a partial failure (HTTP 207). "
                f"Response: {r.text}",
            )
        return r.text

    def _import_data(
        self,
        dataset: Union[Dataset, Sequence[Dataset]],
        dataspace: Optional[str],
    ) -> str:
        """Upload a dataset to the Transfer service (shared transport).

        Serializes to SDMX-CSV 2.0 and posts it as a multipart file to
        ``{transfer}/import/sdmxFile``. The per-row action (I/M/R/D) is
        taken from the dataset's ``action``.
        """
        space = self._resolve_dataspace(dataspace)
        body = write_sdmx(dataset, Format.DATA_SDMX_CSV_2_0_0) or ""
        r = self._send(
            "POST",
            f"{self._transfer}/import/sdmxFile",
            data={"dataspace": space},
            files={"file": ("data.csv", body, _DATA_FILE_CT)},
        )
        return r.text

    def submit_data(
        self,
        dataset: Union[Dataset, Sequence[Dataset]],
        dataspace: Optional[str] = None,
    ) -> str:
        """Submit data to the Transfer service.

        The dataset is serialized to SDMX-CSV 2.0 with :func:`write_sdmx`
        and uploaded as a ``multipart/form-data`` request (file field
        ``file``, plus the required ``dataspace`` field) to
        ``{transfer}/import/sdmxFile``. The dataset must be Schema-backed
        (e.g. produced by ``StatConnector.fetch_dataset`` or
        ``pysdmx.io.get_datasets``); a dataset whose structure is a bare
        URN cannot be written as SDMX-CSV 2.0. The per-row action is
        taken from the SDMX-CSV 2.0 ``ACTION`` column.

        Submission is asynchronous: the response is the Transfer
        ``OperationResult`` (JSON), whose transaction id (an integer,
        reported as ``requestId``) is passed to
        :meth:`submission_status`.

        Args:
            dataset: A Schema-backed dataset, or a sequence of them.
            dataspace: The target data space; defaults to the one set on
                the connector.

        Returns:
            The raw ``OperationResult`` response body.

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If no data space is set, or the service
                returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        return self._import_data(dataset, dataspace)

    def delete_data(
        self, dataset: Dataset, dataspace: Optional[str] = None
    ) -> str:
        """Delete data by submitting it with the SDMX Delete action.

        The dataset's observations are uploaded to the Transfer service
        as SDMX-CSV 2.0 with ``ACTION=D`` per row, which deletes the
        matching observations. Asynchronous, like :meth:`submit_data`.

        Args:
            dataset: A Schema-backed dataset whose observations (keys)
                should be deleted.
            dataspace: The target data space; defaults to the one set on
                the connector.

        Returns:
            The raw ``OperationResult`` response body (with the request
            id), pollable with :meth:`submission_status`.

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If no data space is set, or the service
                returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        return self._import_data(
            structs.replace(dataset, action=ActionType.Delete), dataspace
        )

    def delete_structure(
        self,
        artefacts: Union[
            MaintainableArtefact,
            str,
            Sequence[Union[MaintainableArtefact, str]],
        ],
    ) -> list[str]:
        """Delete structural artefact(s) from the NSI web service.

        Each artefact is deleted with
        ``DELETE {nsi}/rest/{type}/{agency}/{id}/{version}`` (the type
        segment is the lower-cased SDMX type). Accepts a maintainable
        artefact, a short-URN string (e.g.
        ``"DataConstraint=MD:CR_A_DF(1.0)"``), or a sequence of either;
        a sequence is deleted **in order**, so pass dependents first.

        .Stat dependencies: a data import auto-creates an actual content
        constraint ``CR_A_<dataflow>``. To remove a dataflow, first
        :meth:`delete_data`, then delete that constraint, then the
        dataflow, its DSD and concept scheme (a wrong order yields a
        ``409``/:class:`~pysdmx.errors.Invalid`).

        Args:
            artefacts: The artefact(s) or short URN(s) to delete.

        Deletion is fail-fast: on the first error the exception is
        raised and an indeterminate prefix of the sequence may already
        have been deleted (re-run with the remaining artefacts). The NSI
        signals a delete failure with an HTTP status (mapped above)
        rather than an in-body error, but callers may still inspect the
        returned bodies.

        Returns:
            The service response bodies, one per artefact, in order.

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If the service returns a client error (e.g.
                a ``409`` because a dependent artefact still references
                it).
            errors.NotFound: If an artefact does not exist.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        items = (
            [artefacts]
            if isinstance(artefacts, (str, MaintainableArtefact))
            else list(artefacts)
        )
        responses = []
        for item in items:
            urn = item if isinstance(item, str) else item.short_urn
            try:
                ref = parse_short_urn(urn)
            except errors.Invalid as exc:
                raise errors.Invalid(
                    "Invalid artefact reference",
                    "Expected a short URN like 'Dataflow=MD:DF(1.0)'; "
                    f"got {urn!r}.",
                ) from exc
            url = (
                f"{self._nsi}/rest/{ref.sdmx_type.lower()}"
                f"/{ref.agency}/{ref.id}/{ref.version}"
            )
            responses.append(self._send("DELETE", url).text)
        return responses

    def submit(
        self,
        structures: Union[MaintainableArtefact, Sequence[Any]],
        dataset: Union[Dataset, Sequence[Dataset]],
        dataspace: Optional[str] = None,
    ) -> str:
        """Submit the structure(s) first, then the data.

        .Stat Suite requires a dataflow's structure to exist before its
        data can be loaded, so the structure is submitted synchronously
        and only then is the (asynchronous) data submission started.

        Args:
            structures: The structural metadata to submit first.
            dataset: The data to submit once the structure is in place.
            dataspace: The target data space for the data; defaults to
                the one set on the connector.

        Returns:
            The raw data-submission ``OperationResult`` response body.

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If no data space is set, or the service
                returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        self.submit_structure(structures)
        return self.submit_data(dataset, dataspace=dataspace)

    def submission_status(
        self, request_id: str, dataspace: Optional[str] = None
    ) -> str:
        """Poll the status of an asynchronous data submission.

        Issues ``POST {transfer}/status/request`` with the ``dataspace``
        and ``id`` form fields.

        Args:
            request_id: The transaction id returned by
                :meth:`submit_data` or :meth:`submit`.
            dataspace: The data space the request was submitted to;
                defaults to the one set on the connector.

        Returns:
            The raw Transfer ``ImportSummary`` response body (JSON). Read
            its ``executionStatus`` (Queued/InProgress/Completed/...) and
            ``outcome`` (Success/Warning/Error/None) fields: a
            ``Completed`` status still requires checking ``outcome`` to
            confirm the submission actually succeeded.

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If no data space is set, or the service
                returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        space = self._resolve_dataspace(dataspace)
        r = self._send(
            "POST",
            f"{self._transfer}/status/request",
            data={"dataspace": space, "id": request_id},
        )
        return r.text

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


__all__ = [
    "StatConnector",
    "StatEndpoints",
    "StatUploader",
    "StructureSubmissionResult",
    "SubmissionResult",
]
