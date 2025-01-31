import httpx
import pytest

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import Organisation


def check_orgs(mock, fmr: RegistryClient, query, body):
    """get_providers() should return a collection of organizations."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    prvs = fmr.get_providers("BIS")

    assert len(prvs) == 2
    for prv in prvs:
        assert isinstance(prv, Organisation)


async def check_org_core_info(mock, fmr: AsyncRegistryClient, query, body):
    """Providers must contain core information such as ID, name, etc."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    prvs = await fmr.get_providers("BIS")

    for prv in prvs:
        if prv.id == "CH2":
            assert prv.name == "Swiss National Bank"
        elif prv.id == "TST":
            assert prv.name == "Test data provider"
        else:
            pytest.fail(f"Unexepcted provider: {prv.id}")


def check_org_details(mock, fmr: RegistryClient, query, body):
    """Providers may have contact information."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    prvs = fmr.get_providers("BIS")

    for prv in prvs:
        if prv.id == "CH2":
            assert prv.description is None
            assert not prv.contacts
        elif prv.id == "TST":
            assert prv.description == "Description for the test provider."
            assert len(prv.contacts) == 1
            c = prv.contacts[0]
            assert c.id is None
            assert c.name == "Support"
            assert c.department == "Client Support"
            assert c.role == "Head of Support"
            assert len(c.emails) == 1
            assert c.emails[0] == "support@test.com"
            assert len(c.telephones) == 1
            assert c.telephones[0] == "+42.(0)42.4242.4242"
            assert not c.faxes
            assert not c.uris
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

    prvs = fmr.get_providers("BIS", True)

    for prv in prvs:
        if prv.id == "TEST":
            assert len(prv.dataflows) == 2
            for df in prv.dataflows:
                assert df.id in ["DF1", "DF2"]
        elif prv.id == "TEST2":
            assert len(prv.dataflows) == 0
        else:
            pytest.fail(f"Unexepcted provider: {prv.id}")


def check_empty(mock, fmr: RegistryClient, query, body):
    """Can handle empty messages."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    agencies = fmr.get_providers("BIS")

    assert len(agencies) == 0
