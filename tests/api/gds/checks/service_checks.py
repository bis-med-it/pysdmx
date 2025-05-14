import httpx

from pysdmx.api.gds import GdsClient
from pysdmx.api.qb.util import REST_ALL
from pysdmx.io.format import Format
from pysdmx.model.gds import GdsService


def check(
        mock,
        gds: GdsClient,
        query, body,
        value,
        resource: str = REST_ALL,
        version: str = REST_ALL
):
    """get_services() should return a collection of services."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    result = gds.get_services(value, resource, version)

    assert len(mock.calls) == 1

    assert (
        mock.calls[0].request.headers["Accept"] == Format.GDS_JSON.value
    )

    assert len(result) == 1
    for agency in result:
        assert isinstance(agency, GdsService)
