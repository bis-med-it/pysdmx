import httpx

from pysdmx.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import Code, Codelist


def check_vl_codelist(mock, fmr: RegistryClient, q1, q2, body):
    """get_codes() should return a codelist with the expected codes."""
    mock.get(q1).mock(return_value=httpx.Response(404))
    mock.get(q2).mock(return_value=httpx.Response(200, content=body))

    codelist = fmr.get_codes("TEST", "CTYPES", "1.0")

    assert isinstance(codelist, Codelist)
    assert len(codelist) == 4
    assert codelist.id == "CTYPES"
    assert codelist.name == "Contract Types"
    assert codelist.agency == "TEST"
    assert codelist.description is None
    assert codelist.version == "1.0"
    assert codelist.sdmx_type == "valuelist"
    for code in codelist:
        assert isinstance(code, Code)


async def check_vl_code_expected_info(
    mock,
    fmr: AsyncRegistryClient,
    q1,
    q2,
    body,
):
    """Codes must contain core information such as ID and name."""
    mock.get(q1).mock(return_value=httpx.Response(404))
    mock.get(q2).mock(return_value=httpx.Response(200, content=body))

    codelist = await fmr.get_codes("TEST", "CTYPES", "1.0")

    for code in codelist:
        assert code.id in ["A", "B", "C", "E"]
        assert code.name is not None
        assert code.description is None
        assert code.valid_from is None
        assert code.valid_to is None
