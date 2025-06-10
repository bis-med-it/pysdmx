from pysdmx.api.gds import __BaseGdsClient


def test_gds_query_urn_resolver():
    query = __BaseGdsClient()._urn_resolver_q(
        urn="urn:sdmx:org.sdmx.infomodel."
        "datastructure.DataStructure=MD:TEST(1.0)",
    )
    assert (
        query.get_url() == "/urn_resolver/urn:sdmx:org.sdmx.infomodel."
        "datastructure.DataStructure=MD:TEST(1.0)"
    )
