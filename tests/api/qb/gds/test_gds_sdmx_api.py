from pysdmx.api.qb.gds import GdsQuery, GdsType


def test_gds_query_sdmx_api():
    query = GdsQuery(artefact_type=GdsType.GDS_SDMX_API, resource_id="2.1")
    assert query.get_url() == "/sdmxapi/2.1"
