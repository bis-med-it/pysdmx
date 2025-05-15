from pathlib import Path

import httpx
import pytest
from msgspec._core import DecodeError
from msgspec.json import decode

from pysdmx.api.gds import GDS_BASE_ENDPOINT, GdsClient
from pysdmx.api.qb import StructureType
from pysdmx.api.qb.gds import GdsQuery, GdsType
from pysdmx.api.qb.util import REST_ALL, REST_LATEST, ApiVersion
from pysdmx.errors import Invalid
from pysdmx.io.format import Format
from pysdmx.io.json.gds.reader import deserializers as gds_readers
from pysdmx.model.gds import (
    GdsAgency,
    GdsCatalog,
    GdsEndpoint,
    GdsSdmxApi,
    GdsService,
    GdsServiceReference,
    GdsUrnResolver,
    ResolverResult,
)

# Mapping of endpoints to their expected classes
ENDPOINTS = {
    "agency": GdsAgency,
    "catalog": GdsCatalog,
    "sdmxapi": GdsSdmxApi,
    "service": GdsService,
    "urn_resolver": GdsUrnResolver,
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

BASE_SAMPLES_PATH = Path("tests/api/gds/samples")


@pytest.fixture
def gds() -> GdsClient:
    return GdsClient(GDS_BASE_ENDPOINT)


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
def query(gds: GdsClient, endpoint, value, params, resource, version):
    """Construct a query URL similar to the GDS query logic."""
    v = f"/{version}" if version and version != REST_LATEST else ""
    r = f"/{resource}{v}" if v or resource and resource != REST_ALL else ""
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
    version,
    params,
    expected_class,
    references,
):
    """Generic function to test endpoints."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    get_params = {"ref": value}
    if resource:
        get_params["resource"] = resource
    if version:
        get_params["version"] = version
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


def repr_test(
    mock,
    gds,
    query,
    body,
    value,
    params,
    resource,
    version,
    expected_class,
    references,
):
    """Generic function to test GDS model __str__ method."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    get_params = {"ref": value}
    if resource:
        get_params["resource"] = resource
    if version:
        get_params["version"] = version
    get_params = {**get_params, **params}

    # Get and execute the get_{class} method
    method = METHOD_MAP.get(expected_class)
    result = method(gds, **get_params)

    # Common validations
    assert len(mock.calls) == 1

    if expected_class == GdsUrnResolver:
        assert result.__str__() == references.__str__()
    else:
        for i, item in enumerate(result):
            assert item.__str__() == references[i].__str__()


@pytest.mark.parametrize(
    ("endpoint", "value", "params", "resource", "version", "body"),
    [
        ("agency", "BIS", {}, None, None, "agency_bis.json"),
        ("agency", "ESTAT", {}, None, None, "agency_estat.json"),
        (
            "agency",
            "BIS_ESTAT",
            {},
            None,
            None,
            "comma_separated_agencies.json",
        ),
        ("agency", REST_ALL, {}, None, None, "agency_all.json"),
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
            REST_ALL,
            "catalog_bis_raw.json",
        ),
        (
            "catalog",
            "BIS",
            {},
            REST_ALL,
            REST_ALL,
            "catalog_bis_latest_no_params.json",
        ),
        (
            "catalog",
            REST_ALL,
            {},
            REST_ALL,
            REST_ALL,
            "catalog_all_no_params.json",
        ),
        ("sdmxapi", "1.4.0", {}, None, None, "sdmxapi_1.4.0.json"),
        ("sdmxapi", "2.0.0", {}, None, None, "sdmxapi_2.0.0.json"),
        ("sdmxapi", REST_ALL, {}, None, None, "sdmxapi_all.json"),
        ("service", "BIS", {}, REST_ALL, REST_ALL, "service_bis.json"),
        (
            "service",
            "BIS",
            {},
            REST_ALL,
            REST_LATEST,
            "service_bis_latest.json",
        ),
        (
            "urn_resolver",
            "urn:sdmx:org.sdmx.infomodel.categoryscheme.CategoryScheme=BIS:BISWEB_CATSCHEME(1.0)",
            {},
            None,
            None,
            "urn_resolver.json",
        ),
    ],
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
    version,
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
        version,
        params,
        expected_class,
        references,
    )


@pytest.mark.parametrize(
    ("endpoint", "value", "params", "resource", "version", "body"),
    [
        ("agency", REST_ALL, {}, None, None, "agency_all.json"),
        (
            "catalog",
            REST_ALL,
            {},
            REST_ALL,
            REST_ALL,
            "catalog_all_no_params.json",
        ),
        ("sdmxapi", REST_ALL, {}, None, None, "sdmxapi_all.json"),
        ("service", "BIS", {}, REST_ALL, REST_ALL, "service_bis.json"),
        (
            "urn_resolver",
            "urn:sdmx:org.sdmx.infomodel.categoryscheme.CategoryScheme=BIS:BISWEB_CATSCHEME(1.0)",
            {},
            None,
            None,
            "urn_resolver.json",
        ),
    ],
    indirect=["body"],
)
def test_string_repr(
    respx_mock,
    gds,
    query,
    body,
    endpoint,
    value,
    params,
    resource,
    version,
    expected_class,
    references,
):
    """String repr test for all GDS models."""
    repr_test(
        respx_mock,
        gds,
        query,
        body,
        value,
        params,
        resource,
        version,
        expected_class,
        references,
    )


@pytest.mark.parametrize(
    ("cls", "kwargs", "expected"),
    [
        (
            GdsAgency,
            {"agency_id": "BIS", "name": "Bank", "url": "https://bis.org"},
            {"description": None},
        ),
        (
            GdsCatalog,
            {
                "agency_id": "BIS",
                "id": "CAT1",
                "version": "1.0",
                "name": "Catalog",
                "urn": "urn:catalog",
            },
            {"endpoints": None, "serviceRefs": None},
        ),
        (
            GdsEndpoint,
            {
                "api_version": "1.0",
                "url": "https://endpoint",
                "comments": "Test",
                "message_formats": ["json"],
                "rest_resources": ["resource1"],
            },
            {},
        ),
        (
            GdsServiceReference,
            {
                "id": "REF1",
                "name": "Reference",
                "urn": "urn:ref",
                "service": "Service",
            },
            {"description": None},
        ),
        (
            GdsService,
            {
                "agency_id": "BIS",
                "id": "SERVICE1",
                "name": "Service",
                "urn": "urn:service",
                "version": "1.0",
                "base": "https://service",
                "endpoints": [],
            },
            {"authentication": None},
        ),
        (GdsSdmxApi, {"release": "2.0.0", "description": "SDMX API"}, {}),
        (
            ResolverResult,
            {
                "api_version": "1.0",
                "query": "https://query",
                "query_response_status_code": 200,
            },
            {},
        ),
        (
            GdsUrnResolver,
            {
                "agency_id": "BIS",
                "resource_id": "RES1",
                "version": "1.0",
                "sdmx_type": "CategoryScheme",
                "resolver_results": [],
            },
            {},
        ),
    ],
)
def test_instantiation(cls, kwargs, expected):
    """Test instantiation of Gds model classes."""
    instance = cls(**kwargs)
    for key, value in kwargs.items():
        assert getattr(instance, key) == value
    for key, value in expected.items():
        assert getattr(instance, key) == value


@pytest.mark.parametrize(
    ("endpoint", "value", "params", "resource", "version", "body"),
    [
        ("agency", "BIS", {}, None, None, "agency_bis.json"),
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
    version,
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
        version,
        params,
        expected_class,
        references,
    )


@pytest.mark.parametrize(
    ("endpoint", "value", "params", "resource", "version", "body"),
    [
        ("agency", "BIS", {}, None, None, "agency_bis.json"),
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
    version,
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
        version,
        params,
        expected_class,
        references,
    )


@pytest.mark.parametrize(
    ("endpoint", "value", "params", "resource", "version", "body"),
    [
        (
            "agency",
            "non_existing_agency",
            {},
            None,
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
    version,
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
            version,
            params,
            expected_class,
            None,
        )


def test_invalid_query():
    query = GdsQuery(artefact_type=StructureType.AGENCY_SCHEME)
    with pytest.raises(Invalid):
        query._get_base_url(version=REST_LATEST)


def test_invalid_artefact_type():
    query = GdsQuery(artefact_type=GdsType.GDS_AGENCY)
    # Using name mangling to internally change the
    # hidden method name and access to test it
    with pytest.raises(Invalid):
        query._GdsQuery__check_artefact_type(
            atyp=StructureType.AGENCY_SCHEME, version=ApiVersion.V2_0_0
        )
