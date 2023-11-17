from datetime import datetime, timezone

import httpx

from pysdmx.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import Code, Codelist


def check_codelist(mock, fmr: RegistryClient, query, body):
    """get_codes() should return a codelist with the expected codes."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    codelist = fmr.get_codes("SDMX", "CL_FREQ", "2.0")

    assert isinstance(codelist, Codelist)
    assert len(codelist) == 9
    assert codelist.id == "CL_FREQ"
    assert codelist.name == "Frequency"
    assert codelist.agency == "SDMX"
    assert codelist.description == "The frequency of the data"
    assert codelist.version == "2.0"
    for code in codelist:
        assert isinstance(code, Code)


async def check_code_core_info(mock, fmr: AsyncRegistryClient, query, body):
    """Codes must contain core information such as ID and name."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    codelist = await fmr.get_codes("SDMX", "CL_FREQ", "2.0")

    for code in codelist:
        assert code.id in ["A", "S", "Q", "M", "W", "D", "H", "B", "N"]
        assert code.name is not None


def check_code_details(mock, fmr: RegistryClient, query, body):
    """Codes may have extended information."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    codelist = fmr.get_codes("SDMX", "CL_FREQ", "2.0")

    for code in codelist:
        if code.id == "A":
            assert code.description is None
            assert code.valid_from is None
            assert code.valid_to == datetime.fromisoformat(
                "1987-06-01T00:00:00"
            ).replace(tzinfo=timezone.utc)
        elif code.id == "S":
            assert code.description is not None
            assert code.valid_from == datetime.fromisoformat(
                "1989-06-01T00:00:00"
            ).replace(tzinfo=timezone.utc)
            assert code.valid_to is None
        elif code.id == "Q":
            assert code.description is not None
            assert code.valid_from == datetime.fromisoformat(
                "1987-06-01T00:00:00"
            ).replace(tzinfo=timezone.utc)
            assert code.valid_to == datetime.fromisoformat(
                "1989-06-01T00:00:00"
            ).replace(tzinfo=timezone.utc)
        else:
            assert code.id in ["M", "W", "D", "H", "B", "N"]
            assert code.description is not None
            assert code.valid_from is None
            assert code.valid_to is None
