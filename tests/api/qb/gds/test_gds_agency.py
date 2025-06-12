from pysdmx.api.gds import __BaseGdsClient


def test_gds_query_agency():
    """Test the GdsQuery for agency."""
    query = __BaseGdsClient()._agencies_q(agency="ECB")
    assert query.get_url() == "/agency/ECB"
