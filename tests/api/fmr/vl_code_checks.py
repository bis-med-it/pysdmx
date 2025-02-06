import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.io.format import Format
from pysdmx.model import Code, Codelist


def check_vl_codelist(
    mock, fmr: RegistryClient, q1, q2, body, is_fusion: bool = False
):
    """get_codes() should return a codelist with the expected codes."""
    mock.get(q1).mock(return_value=httpx.Response(404))
    mock.get(q2).mock(return_value=httpx.Response(200, content=body))

    codelist = fmr.get_codes("TEST", "CTYPES", "1.0")

    assert len(mock.calls) == 2  # We first fetch a codelist then a valuelist
    if is_fusion:
        assert (
            mock.calls[0].request.headers["Accept"] == Format.FUSION_JSON.value
        )
    else:
        assert (
            mock.calls[0].request.headers["Accept"]
            == Format.STRUCTURE_SDMX_JSON_2_0_0.value
        )

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
