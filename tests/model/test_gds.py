from pathlib import Path

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

BASE_SAMPLES_PATH = Path("tests/model/samples/gds")


def read_expected_str(name):
    """Fixture to load the expected string from the corresponding .txt file."""
    file_name = f"{name}.txt"
    file_path = BASE_SAMPLES_PATH / file_name
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def test_str_gds_agency():
    """Test the __str__ method of GdsAgency."""
    agency = GdsAgency(
        agency_id="BIS",
        name="BIS",
        url="bis.org",
        description="Bank for International Settlements",
    )

    expected_str = read_expected_str("agency")

    assert str(agency) == expected_str


def test_str_gds_catalog():
    """Test the __str__ method of GdsCatalog."""
    catalog = GdsCatalog(
        agency_id="BIS",
        id="BIS_PUBS",
        version="1.0",
        name="BIS Service Ref",
        urn="urn:sdmx:org.sdmx.infomodel.discovery.Catalog=BIS:BIS_PUBS(1.0)",
        endpoints=[
            GdsEndpoint(
                api_version="1.4.0",
                url="https://stats.bis.org/api/v1",
                comments="",
                message_formats=[],
                rest_resources=["structure", "data", "schema", "availability"],
            ),
            GdsEndpoint(
                api_version="2.0.0",
                url="https://stats.bis.org/api/v2",
                comments="",
                message_formats=[],
                rest_resources=["structure"],
            ),
        ],
    )

    expected_str = read_expected_str("catalog")

    assert str(catalog) == expected_str


def test_str_gds_sdmxapi():
    """Test the __str__ method of GdsSdmxApi."""
    sdmxapi = GdsSdmxApi(
        release="1.5.0",
        description="Version 1.5.0 of the SDMX REST API "
        "specification (released: 09/2020) - see the "
        "[release notes](https://github.com/sdmx-twg/"
        "sdmx-rest/releases/tag/v1.5.0) and the [official "
        "documentation](https://github.com/sdmx-twg/"
        "sdmx-rest/tree/v1.5.0/v2_1/ws/rest/docs).",
    )

    expected_str = read_expected_str("sdmxapi")

    assert str(sdmxapi) == expected_str


def test_str_gds_service():
    """Test the __str__ method of GdsService."""
    service = GdsService(
        agency_id="BIS",
        id="BIS_DATA",
        name="BIS Data Portal API",
        urn="urn:sdmx:org.sdmx.infomodel.discovery.Service=BIS:BIS_DATA(1.0)",
        version="1.0",
        base="https://stats.bis.org/api",
        endpoints=[
            GdsEndpoint(
                api_version="1.4.0",
                url="/v1",
                comments="",
                message_formats=[],
                rest_resources=["structure", "data", "schema", "availability"],
            ),
            GdsEndpoint(
                api_version="2.0.0",
                url="/v2",
                comments="",
                message_formats=[],
                rest_resources=[
                    "structure",
                    "data",
                    "schema",
                    "availability",
                    "metadata",
                ],
            ),
        ],
    )

    expected_str = read_expected_str("service")

    assert str(service) == expected_str


def test_str_gds_urn_resolver():
    """Test the __str__ method of GdsUrnResolver."""
    urn_resolution = GdsUrnResolver(
        agency_id="BIS",
        resource_id="BISWEB_CATSCHEME",
        version="1.0",
        sdmx_type="CategoryScheme",
        resolver_results=[
            ResolverResult(
                api_version="1.4.0",
                query="https://stats.bis.org/api/v1/categoryscheme/BIS/BISWEB_CATSCHEME/1.0?detail=allstubs",
                query_response_status_code=200,
            )
        ],
    )

    expected_str = read_expected_str("urn_resolver")

    assert str(urn_resolution) == expected_str


def test_instantiation_gds_agency():
    """Test instantiation of GdsAgency."""
    instance = GdsAgency(agency_id="BIS", name="Bank", url="https://bis.org")
    assert instance.agency_id == "BIS"
    assert instance.name == "Bank"
    assert instance.url == "https://bis.org"
    assert instance.description is None


def test_instantiation_gds_catalog():
    """Test instantiation of GdsCatalog."""
    instance = GdsCatalog(
        agency_id="BIS",
        id="CAT1",
        version="1.0",
        name="Catalog",
        urn="urn:catalog",
    )
    assert instance.agency_id == "BIS"
    assert instance.id == "CAT1"
    assert instance.version == "1.0"
    assert instance.name == "Catalog"
    assert instance.urn == "urn:catalog"
    assert instance.endpoints is None
    assert instance.serviceRefs is None


def test_instantiation_gds_endpoint():
    """Test instantiation of GdsEndpoint."""
    instance = GdsEndpoint(
        api_version="1.0",
        url="https://endpoint",
        comments="Test",
        message_formats=["json"],
        rest_resources=["resource1"],
    )
    assert instance.api_version == "1.0"
    assert instance.url == "https://endpoint"
    assert instance.comments == "Test"
    assert instance.message_formats == ["json"]
    assert instance.rest_resources == ["resource1"]


def test_instantiation_gds_service_reference():
    """Test instantiation of GdsServiceReference."""
    instance = GdsServiceReference(
        id="REF1", name="Reference", urn="urn:ref", service="Service"
    )
    assert instance.id == "REF1"
    assert instance.name == "Reference"
    assert instance.urn == "urn:ref"
    assert instance.service == "Service"
    assert instance.description is None


def test_instantiation_gds_service():
    """Test instantiation of GdsService."""
    instance = GdsService(
        agency_id="BIS",
        id="SERVICE1",
        name="Service",
        urn="urn:service",
        version="1.0",
        base="https://service",
        endpoints=[],
    )
    assert instance.agency_id == "BIS"
    assert instance.id == "SERVICE1"
    assert instance.name == "Service"
    assert instance.urn == "urn:service"
    assert instance.version == "1.0"
    assert instance.base == "https://service"
    assert instance.endpoints == []
    assert instance.authentication is None


def test_instantiation_gds_sdmxapi():
    """Test instantiation of GdsSdmxApi."""
    instance = GdsSdmxApi(release="2.0.0", description="SDMX API")
    assert instance.release == "2.0.0"
    assert instance.description == "SDMX API"


def test_instantiation_resolver_result():
    """Test instantiation of ResolverResult."""
    instance = ResolverResult(
        api_version="1.0",
        query="https://query",
        query_response_status_code=200,
    )
    assert instance.api_version == "1.0"
    assert instance.query == "https://query"
    assert instance.query_response_status_code == 200


def test_instantiation_gds_urn_resolver():
    """Test instantiation of GdsUrnResolver."""
    instance = GdsUrnResolver(
        agency_id="BIS",
        resource_id="RES1",
        version="1.0",
        sdmx_type="CategoryScheme",
        resolver_results=[],
    )
    assert instance.agency_id == "BIS"
    assert instance.resource_id == "RES1"
    assert instance.version == "1.0"
    assert instance.sdmx_type == "CategoryScheme"
    assert instance.resolver_results == []
