from pysdmx.api.gds import __BaseGdsClient


def test_gds_query_service():
    query = __BaseGdsClient()._services_q(agency="BIS")
    assert query.get_url() == "/service/BIS"


def test_gds_query_service_with_version():
    query = __BaseGdsClient()._services_q(agency="BIS", version="1.0")
    assert query.get_url() == "/service/BIS/*/1.0"


def test_gds_query_service_with_resource_id():
    query = __BaseGdsClient()._services_q(agency="BIS", resource="123")
    assert query.get_url() == "/service/BIS/123"


def test_gds_query_service_with_all():
    query = __BaseGdsClient()._services_q(
        agency="BIS",
        resource="TEST",
        version="1.0",
    )
    assert query.get_url() == "/service/BIS/TEST/1.0"
