import gzip

import httpx
import pytest

from pysdmx.api.fmr import (
    AsyncRegistryClient,
    RegistryClient,
    StructureFormat,
)
from pysdmx.errors import NotImplemented


@pytest.mark.parametrize(
    "fmt",
    (
        f
        for f in StructureFormat
        if f
        not in [StructureFormat.FUSION_JSON, StructureFormat.SDMX_JSON_2_0_0]
    ),
)
def test_unsupported_format(fmt):
    with pytest.raises(NotImplemented) as ni:
        RegistryClient("https://registry.sdmx.org/sdmx/v2", fmt)
    assert ni.value.title is not None
    assert ni.value.description is not None
    assert "requested_format" in ni.value.csi
    assert ni.value.csi["requested_format"] == fmt.value


@pytest.fixture
def endpoint():
    return "https://registry.sdmx.org/sdmx/v2"


@pytest.fixture
def gzip_agencies(respx_mock, endpoint):
    # The agencies are compressed with gzip, but sent without a
    # Content-Encoding header, as some services (e.g. Eurostat) do
    with open("tests/api/fmr/samples/orgs/agencies.json", "rb") as f:
        body = gzip.compress(f.read())
    return respx_mock.get(f"{endpoint}/structure/agencyscheme/BIS/").mock(
        return_value=httpx.Response(200, content=body)
    )


def test_lenient(endpoint, gzip_agencies):
    client = RegistryClient(endpoint, lenient=True)

    assert len(client.get_agencies("BIS")) == 2


@pytest.mark.asyncio
async def test_lenient_async(endpoint, gzip_agencies):
    client = AsyncRegistryClient(endpoint, lenient=True)

    assert len(await client.get_agencies("BIS")) == 2
