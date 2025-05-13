import httpx

from pysdmx.api.gds import GdsClient
from pysdmx.io.format import Format
from pysdmx.model.gds import GdsUrnResolver


def check(
    mock, gds: GdsClient, query, body, value
):
    """get_urn_resolver() should return the resolution of the urn."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    result = gds.get_urn_resolver(value)

    assert len(mock.calls) == 1

    assert (
        mock.calls[0].request.headers["Accept"] == Format.GDS_JSON_2_0_0.value
    )

    assert isinstance(result, GdsUrnResolver)
