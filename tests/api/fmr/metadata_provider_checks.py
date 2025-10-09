import httpx
import pytest

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import MetadataProvider


def check_orgs(mock, fmr: RegistryClient, query, body):
    """get_metadata_providers() should return metadata providers."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    prvs = fmr.get_metadata_providers("BIS")

    assert len(mock.calls) == 1

    assert len(prvs) == 2
    for prv in prvs:
        assert isinstance(prv, MetadataProvider)


async def check_org_core_info(mock, fmr: AsyncRegistryClient, query, body):
    """Metadata providers contain core information such as ID, name, etc."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    prvs = await fmr.get_metadata_providers("BIS")

    for prv in prvs:
        if prv.id == "MD":
            assert prv.name == "Top-level metadata provider"
        elif prv.id == "MD_PROVIDER":
            assert prv.name == "Metadata Provider (test)"
        else:
            pytest.fail(f"Unexepcted provider: {prv.id}")


def check_with_flows(mock, fmr, query, body):
    """Providers may have flows attached."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    prvs = fmr.get_metadata_providers("BIS", True)

    for prv in prvs:
        if prv.id == "MD":
            assert len(prv.dataflows) == 1
            for df in prv.dataflows:
                assert df.id == "DF_CNF"
        elif prv.id == "MD_PROVIDER":
            assert len(prv.dataflows) == 0
        else:
            pytest.fail(f"Unexepcted provider: {prv.id}")
