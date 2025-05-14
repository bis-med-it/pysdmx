import httpx

from pysdmx.api.gds import GdsClient
from pysdmx.io.format import Format
from pysdmx.model.gds import GdsSdmxApi


def check(
    mock, gds: GdsClient, query, body, value
):
    """get_sdmxapi() should return a collection of sdmx api objects."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    result = gds.get_sdmx_api(value)

    assert len(mock.calls) == 1

    assert (
        mock.calls[0].request.headers["Accept"] == Format.GDS_JSON.value
    )

    assert len(result) == 1
    for agency in result:
        assert isinstance(agency, GdsSdmxApi)
