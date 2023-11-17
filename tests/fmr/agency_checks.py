import httpx
import pytest

from pysdmx.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import Organisation


def check_orgs(mock, fmr: RegistryClient, query, body):
    """get_agencies() should return a collection of organizations."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    agencies = fmr.get_agencies("BIS")

    assert len(agencies) == 2
    for agency in agencies:
        assert isinstance(agency, Organisation)


async def check_org_core_info(mock, fmr: AsyncRegistryClient, query, body):
    """Agencies must contain core information such as ID and name."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    agencies = await fmr.get_agencies("BIS")

    for agency in agencies:
        if agency.id == "BIS.DST":
            assert agency.name == "Data Stewards"
        elif agency.id == "BIS.CMP":
            assert agency.name == "Data Compilation Unit"
        else:
            pytest.fail(f"Unexpected agency: {agency.id}")


def check_org_details(mock, fmr: RegistryClient, query, body):
    """Agencies may have contact information."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    agencies = fmr.get_agencies("BIS")

    for agency in agencies:
        if agency.id == "BIS.DST":
            assert agency.description is None
            assert not agency.contacts
        elif agency.id == "BIS.CMP":
            assert agency.description == "Unit responsible for compilation"
            assert len(agency.contacts) == 2

            c1 = agency.contacts[0]
            assert c1.id is None
            assert c1.name == "Arthur Dent"
            assert c1.role == "Data Owner"
            assert len(c1.emails) == 1
            assert c1.emails[0] == "Arthur.Dent@test.com"
            assert not c1.telephones
            assert not c1.faxes
            assert not c1.uris

            c2 = agency.contacts[1]
            assert c2.id is None
            assert c2.name == "Ford Prefect"
            assert c2.role == "Subject Matter Expert"
            assert len(c2.emails) == 1
            assert c2.emails[0] == "Ford.Prefect@test.com"
            assert not c2.telephones
            assert not c2.faxes
            assert not c2.uris
        else:
            pytest.fail(f"Unexpected agency: {agency.id}")
