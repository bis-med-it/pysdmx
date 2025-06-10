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


def test_str_gds_agency():
    """Test the __str__ method of GdsAgency."""
    agency = GdsAgency(
        id="BIS",
        name="BIS",
        url="bis.org",
        description="Bank for International Settlements",
    )

    expected_str = (
        "id: BIS, "
        "name: BIS, "
        "url: bis.org, "
        "description: Bank for International Settlements"
    )

    assert str(agency) == expected_str


def test_str_gds_catalog():
    """Test the __str__ method of GdsCatalog."""
    catalog = GdsCatalog(
        agency="BIS",
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

    expected_str = (
        "id: BIS_PUBS, urn: "
        "urn:sdmx:org.sdmx.infomodel.discovery.Catalog=BIS:BIS_PUBS(1.0), "
        "name: BIS "
        "Service Ref, version: 1.0, agency: BIS, endpoints: 2 gdsendpoints"
    )

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

    expected_str = (
        "release: 1.5.0, "
        "description: Version 1.5.0 of the SDMX REST API "
        "specification (released: 09/2020) - see the "
        "[release notes](https://github.com/sdmx-twg"
        "/sdmx-rest/releases/tag/v1.5.0) and the "
        "[official documentation]"
        "(https://github.com/sdmx-twg/sdmx-rest"
        "/tree/v1.5.0/v2_1/ws/rest/docs)."
    )

    assert str(sdmxapi) == expected_str


def test_str_gds_service():
    """Test the __str__ method of GdsService."""
    service = GdsService(
        agency="BIS",
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

    expected_str = (
        "id: BIS_DATA, urn: "
        "urn:sdmx:org.sdmx.infomodel.discovery.Service=BIS:BIS_DATA(1.0), "
        "name: BIS "
        "Data Portal API, version: 1.0, agency: BIS, "
        "base: https://stats.bis.org/api, "
        "endpoints: 2 gdsendpoints"
    )

    assert str(service) == expected_str


def test_str_gds_urn_resolver():
    """Test the __str__ method of GdsUrnResolver."""
    urn_resolution = GdsUrnResolver(
        agency="BIS",
        resource_id="BISWEB_CATSCHEME",
        version="1.0",
        sdmx_type="CategoryScheme",
        resolver_results=[
            ResolverResult(
                api_version="1.4.0",
                query="https://stats.bis.org/api/v1/categoryscheme/BIS/BISWEB_CATSCHEME/1.0?detail=allstubs",
                status_code=200,
            )
        ],
    )

    expected_str = (
        "agency: BIS, "
        "resource_id: BISWEB_CATSCHEME, "
        "version: 1.0, sdmx_type: CategoryScheme, "
        "resolver_results: 1 resolverresults"
    )

    assert str(urn_resolution) == expected_str


def test_str_gds_catalog_empty_endpoints():
    """Test the __str__ method of GdsCatalog with empty endpoints."""
    catalog = GdsCatalog(
        agency="BIS",
        id="CAT1",
        version="1.0",
        name="Catalog",
        urn="urn",
        endpoints=[],  # Empty list
    )

    expected_str = (
        "id: CAT1, urn: urn, name: Catalog, version: 1.0, agency: BIS"
    )

    assert str(catalog) == expected_str


def test_repr_gds_agency():
    """Test the __repr__ method of GdsAgency."""
    agency = GdsAgency(
        id="BIS",
        name="BIS",
        url="bis.org",
        description="Bank for International Settlements",
    )

    expected_repr = (
        "GdsAgency(id='BIS', name='BIS', url='bis.org', "
        "description='Bank for International Settlements')"
    )

    assert repr(agency) == expected_repr


def test_repr_gds_catalog():
    """Test the __repr__ method of GdsCatalog."""
    catalog = GdsCatalog(
        agency="BIS",
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

    expected_repr = (
        "GdsCatalog(id='BIS_PUBS', "
        "urn='urn:sdmx:org.sdmx.infomodel.discovery."
        "Catalog=BIS:BIS_PUBS(1.0)', "
        "name='BIS Service Ref', version='1.0', agency='BIS', "
        "endpoints=[GdsEndpoint(api_version='1.4.0', "
        "url='https://stats.bis.org/api/v1', comments='', "
        "rest_resources=['structure', 'data', 'schema', 'availability']), "
        "GdsEndpoint(api_version='2.0.0', url='https://stats.bis.org/api/v2', "
        "comments='', rest_resources=['structure'])])"
    )

    assert repr(catalog) == expected_repr


def test_repr_gds_service():
    """Test the __repr__ method of GdsService."""
    service = GdsService(
        agency="BIS",
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

    expected_repr = (
        "GdsService(id='BIS_DATA', "
        "urn='urn:sdmx:org.sdmx.infomodel.discovery."
        "Service=BIS:BIS_DATA(1.0)', "
        "name='BIS Data Portal API', version='1.0', agency='BIS', "
        "base='https://stats.bis.org/api', "
        "endpoints=[GdsEndpoint(api_version='1.4.0', url='/v1', comments='', "
        "rest_resources=['structure', 'data', 'schema', 'availability']), "
        "GdsEndpoint(api_version='2.0.0', url='/v2', comments='', "
        "rest_resources=['structure', 'data', 'schema', 'availability', "
        "'metadata'])])"
    )

    assert repr(service) == expected_repr


def test_repr_gds_sdmxapi():
    """Test the __repr__ method of GdsSdmxApi."""
    sdmxapi = GdsSdmxApi(
        release="1.5.0",
        description="Version 1.5.0 of the SDMX REST API "
        "specification (released: 09/2020) - see the "
        "[release notes](https://github.com/sdmx-twg/"
        "sdmx-rest/releases/tag/v1.5.0) and the [official "
        "documentation](https://github.com/sdmx-twg/"
        "sdmx-rest/tree/v1.5.0/v2_1/ws/rest/docs).",
    )

    expected_repr = (
        "GdsSdmxApi(release='1.5.0', "
        "description='Version 1.5.0 of the SDMX REST API "
        "specification (released: 09/2020) - see the ["
        "release notes](https://github.com/sdmx-twg/"
        "sdmx-rest/releases/tag/v1.5.0) and the ["
        "official documentation](https://github.com/sdmx-twg/"
        "sdmx-rest/tree/v1.5.0/v2_1/ws/rest/docs).')"
    )

    assert repr(sdmxapi) == expected_repr


def test_repr_gds_urn_resolver():
    """Test the __repr__ method of GdsUrnResolver."""
    urn_resolution = GdsUrnResolver(
        agency="BIS",
        resource_id="BISWEB_CATSCHEME",
        version="1.0",
        sdmx_type="CategoryScheme",
        resolver_results=[
            ResolverResult(
                api_version="1.4.0",
                query="https://stats.bis.org/api/v1/categoryscheme/BIS"
                "/BISWEB_CATSCHEME/1.0?detail=allstubs",
                status_code=200,
            )
        ],
    )

    expected_repr = (
        "GdsUrnResolver(agency='BIS', "
        "resource_id='BISWEB_CATSCHEME', version='1.0', "
        "sdmx_type='CategoryScheme', resolver_results=["
        "ResolverResult(api_version='1.4.0', "
        "query='https://stats.bis.org/api/v1/categoryscheme/"
        "BIS/BISWEB_CATSCHEME/1.0?detail=allstubs', "
        "status_code=200)])"
    )

    assert repr(urn_resolution) == expected_repr


def test_instantiation_gds_agency():
    """Test instantiation of GdsAgency."""
    instance = GdsAgency(id="BIS", name="Bank", url="https://bis.org")
    assert instance.id == "BIS"
    assert instance.name == "Bank"
    assert instance.url == "https://bis.org"
    assert instance.description is None


def test_instantiation_gds_catalog():
    """Test instantiation of GdsCatalog."""
    instance = GdsCatalog(
        agency="BIS",
        id="CAT1",
        version="1.0",
        name="Catalog",
        urn="urn:catalog",
    )
    assert instance.agency == "BIS"
    assert instance.id == "CAT1"
    assert instance.version == "1.0"
    assert instance.name == "Catalog"
    assert instance.urn == "urn:catalog"
    assert instance.endpoints is None
    assert instance.services is None


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
        agency="BIS",
        id="SERVICE1",
        name="Service",
        urn="urn:service",
        version="1.0",
        base="https://service",
        endpoints=[],
    )
    assert instance.agency == "BIS"
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
        status_code=200,
    )
    assert instance.api_version == "1.0"
    assert instance.query == "https://query"
    assert instance.status_code == 200


def test_instantiation_gds_urn_resolver():
    """Test instantiation of GdsUrnResolver."""
    instance = GdsUrnResolver(
        agency="BIS",
        resource_id="RES1",
        version="1.0",
        sdmx_type="CategoryScheme",
        resolver_results=[],
    )
    assert instance.agency == "BIS"
    assert instance.resource_id == "RES1"
    assert instance.version == "1.0"
    assert instance.sdmx_type == "CategoryScheme"
    assert instance.resolver_results == []
