from pathlib import Path

import httpx
import pytest
from msgspec._core import DecodeError
from msgspec.json import decode

from pysdmx.api.gds import GDS_BASE_ENDPOINT, AsyncGdsClient, GdsClient
from pysdmx.api.qb import StructureType
from pysdmx.api.qb.gds import GdsQuery, GdsType
from pysdmx.api.qb.util import REST_ALL, REST_LATEST, ApiVersion
from pysdmx.errors import Invalid
from pysdmx.io.format import Format
from pysdmx.io.json.gds.reader import deserializers as gds_readers
from pysdmx.model.gds import (
    GdsAgency,
    GdsCatalog,
    GdsSdmxApi,
    GdsService,
    GdsUrnResolver,
)

# Mapping of endpoints to their expected classes
ENDPOINTS = {
    "agency": GdsAgency,
    "catalog": GdsCatalog,
    "sdmxapi": GdsSdmxApi,
    "service": GdsService,
    "urn_resolver": GdsUrnResolver,
}

REFERENCES = {
    GdsAgency: "agency",
    GdsCatalog: "catalog",
    GdsSdmxApi: "api_version",
    GdsService: "service",
    GdsUrnResolver: "urn",
}

DECODERS = {
    GdsAgency: gds_readers.agencies,
    GdsCatalog: gds_readers.catalogs,
    GdsSdmxApi: gds_readers.sdmx_api,
    GdsService: gds_readers.services,
    GdsUrnResolver: gds_readers.urn_resolver,
}

METHOD_MAP = {
    GdsAgency: GdsClient.get_agencies,
    GdsCatalog: GdsClient.get_catalogs,
    GdsSdmxApi: GdsClient.get_sdmx_api,
    GdsService: GdsClient.get_services,
    GdsUrnResolver: GdsClient.get_urn_resolver,
}

ASYNC_METHOD_MAP = {
    GdsAgency: AsyncGdsClient.get_agencies,
    GdsCatalog: AsyncGdsClient.get_catalogs,
    GdsSdmxApi: AsyncGdsClient.get_sdmx_api,
    GdsService: AsyncGdsClient.get_services,
    GdsUrnResolver: AsyncGdsClient.get_urn_resolver,
}

BASE_SAMPLES_PATH = Path("tests/api/gds/samples")


@pytest.fixture
def gds() -> GdsClient:
    return GdsClient(GDS_BASE_ENDPOINT)


@pytest.fixture
def async_gds_client() -> AsyncGdsClient:
    return AsyncGdsClient(GDS_BASE_ENDPOINT)


@pytest.fixture
def gds_without_slash() -> GdsClient:
    return GdsClient(str(GDS_BASE_ENDPOINT)[:-1])


@pytest.fixture
def gds_1_4_0() -> GdsClient:
    return GdsClient(str(GDS_BASE_ENDPOINT), ApiVersion.V1_4_0)


@pytest.fixture
def body(endpoint, request):
    """Fixture to load the body content for a specific test case."""
    file_name = request.param
    file_path = BASE_SAMPLES_PATH / endpoint / file_name
    with open(file_path, "rb") as f:
        return f.read()


@pytest.fixture
def expected_class(endpoint):
    """Fixture to map the endpoint to its expected class."""
    return ENDPOINTS[endpoint]


@pytest.fixture
def references(body, expected_class):
    """Fixture to decode the body content to the expected objects."""
    decoder = DECODERS[expected_class]
    schemes = decode(body, type=decoder).to_model()
    return schemes


@pytest.fixture
def query(gds: GdsClient, endpoint, value, params, resource):
    """Construct a query URL similar to the GDS query logic."""
    r = f"/{resource}" if resource and resource != REST_ALL else ""
    a = f"/{value}{r}" if r or value and value != REST_ALL else ""
    base_query = f"{gds.api_endpoint}/{endpoint}{a}"

    # Add query parameters for catalog endpoint
    if endpoint == "catalog":
        query_params = "&".join(
            f"{key}={value}" for key, value in params.items()
        )
        return f"{base_query}/?{query_params}" if query_params else base_query

    return base_query


def generic_test(
    mock,
    gds,
    query,
    body,
    value,
    resource,
    params,
    expected_class,
    references,
):
    """Generic function to test endpoints."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    get_params = {REFERENCES.get(expected_class): value}
    if resource:
        get_params["resource"] = resource
    get_params = {**get_params, **params}

    # Get and execute the get_{class} method
    method = METHOD_MAP.get(expected_class)
    result = method(gds, **get_params)

    # Common validations
    assert len(mock.calls) == 1

    assert mock.calls[0].request.headers["Accept"] == Format.GDS_JSON.value

    if expected_class == GdsUrnResolver:
        assert isinstance(result, expected_class)
    else:
        for item in result:
            assert isinstance(item, expected_class)

    assert result == references


async def generic_async_test(
    mock,
    gds,
    query,
    body,
    value,
    resource,
    params,
    expected_class,
    references,
):
    """Generic function to test async endpoints."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    get_params = {REFERENCES.get(expected_class): value}
    if resource:
        get_params["resource"] = resource
    get_params = {**get_params, **params}

    # Get and execute the get_{class} method
    method = ASYNC_METHOD_MAP.get(expected_class)
    result = await method(gds, **get_params)

    # Common validations
    assert len(mock.calls) == 1

    assert mock.calls[0].request.headers["Accept"] == Format.GDS_JSON.value

    if expected_class == GdsUrnResolver:
        assert isinstance(result, expected_class)
    else:
        for item in result:
            assert isinstance(item, expected_class)

    assert result == references


GENERIC_PARAMS = [
        ("agency", "BIS", {}, None, "agency_bis.json"),
        ("agency", "ESTAT", {}, None, "agency_estat.json"),
        (
            "agency",
            "BIS_ESTAT",
            {},
            None,
            "comma_separated_agencies.json",
        ),
        ("agency", REST_ALL, {}, None, "agency_all.json"),
        (
            "catalog",
            "BIS",
            {
                "resource_type": "data",
                "message_format": "json",
                "api_version": "2.0.0",
                "detail": "full",
                "references": "none",
            },
            REST_ALL,
            "catalog_bis_full.json",
        ),
        (
            "catalog",
            "BIS",
            {
                "detail": "raw",
                "references": "children",
            },
            REST_ALL,
            "catalog_bis_raw.json",
        ),
        (
            "catalog",
            "BIS",
            {},
            REST_ALL,
            "catalog_bis_latest_no_params.json",
        ),
        (
            "catalog",
            REST_ALL,
            {},
            REST_ALL,
            "catalog_all_no_params.json",
        ),
        ("sdmxapi", "1.4.0", {}, None, "sdmxapi_1.4.0.json"),
        ("sdmxapi", "2.0.0", {}, None, "sdmxapi_2.0.0.json"),
        ("sdmxapi", REST_ALL, {}, None, "sdmxapi_all.json"),
        ("service", "BIS", {}, REST_ALL, "service_bis.json"),
        (
            "service",
            "BIS",
            {},
            REST_ALL,
            "service_bis_latest.json",
        ),
        (
            "urn_resolver",
            "urn:sdmx:org.sdmx.infomodel.categoryscheme.CategoryScheme=BIS:BISWEB_CATSCHEME(1.0)",
            {},
            None,
            "urn_resolver.json",
        ),
    ]

@pytest.mark.parametrize(
    ("endpoint", "value", "params", "resource", "body"),
    GENERIC_PARAMS,
    indirect=["body"],
)
def test_generic(
    respx_mock,
    gds,
    query,
    body,
    endpoint,
    value,
    params,
    resource,
    expected_class,
    references,
):
    """Generic test for all endpoints."""
    generic_test(
        respx_mock,
        gds,
        query,
        body,
        value,
        resource,
        params,
        expected_class,
        references,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("endpoint", "value", "params", "resource", "body"),
    GENERIC_PARAMS,
    indirect=["body"],
)
async def test_async_generic(
    respx_mock,
    async_gds_client,
    query,
    body,
    endpoint,
    value,
    params,
    resource,
    expected_class,
    references,
):
    """Generic test for all endpoints using async client."""
    await generic_async_test(
        respx_mock,
        async_gds_client,
        query,
        body,
        value,
        resource,
        params,
        expected_class,
        references,
    )


@pytest.mark.parametrize(
    ("endpoint", "value", "params", "resource", "body"),
    [
        ("agency", "BIS", {}, None, "agency_bis.json"),
    ],
    indirect=["body"],
)
def test_gds_without_slash(
    respx_mock,
    gds_without_slash,
    query,
    body,
    endpoint,
    value,
    params,
    resource,
    expected_class,
    references,
):
    generic_test(
        respx_mock,
        gds_without_slash,
        query,
        body,
        value,
        resource,
        params,
        expected_class,
        references,
    )


@pytest.mark.parametrize(
    ("endpoint", "value", "params", "resource", "body"),
    [
        ("agency", "BIS", {}, None, "agency_bis.json"),
    ],
    indirect=["body"],
)
def test_gds_downgraded_version(
    respx_mock,
    gds_1_4_0,
    query,
    body,
    endpoint,
    value,
    params,
    resource,
    expected_class,
    references,
):
    generic_test(
        respx_mock,
        gds_1_4_0,
        query,
        body,
        value,
        resource,
        params,
        expected_class,
        references,
    )


@pytest.mark.parametrize(
    ("endpoint", "value", "params", "resource", "body"),
    [
        (
            "agency",
            "non_existing_agency",
            {},
            None,
            "non_existing_agency.json",
        )
    ],
    indirect=["body"],
)
def test_non_existing_entty(
    respx_mock,
    gds,
    query,
    body,
    endpoint,
    value,
    params,
    resource,
    expected_class,
):
    with pytest.raises(DecodeError):
        generic_test(
            respx_mock,
            gds,
            query,
            body,
            value,
            resource,
            params,
            expected_class,
            None,
        )


def test_invalid_query():
    query = GdsQuery(artefact_type=StructureType.AGENCY_SCHEME)
    with pytest.raises(Invalid):
        query._get_base_url()


def test_invalid_artefact_type():
    query = GdsQuery(artefact_type=GdsType.GDS_AGENCY)
    # Using name mangling to internally change the
    # hidden method name and access to test it
    with pytest.raises(Invalid):
        query._GdsQuery__check_artefact_type(
            atyp=StructureType.AGENCY_SCHEME
        )
