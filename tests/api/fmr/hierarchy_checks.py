from datetime import datetime, timezone
from typing import Sequence

import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.io.format import Format
from pysdmx.model import HierarchicalCode, Hierarchy


def check_hierarchy(
    mock, fmr: RegistryClient, query, body, is_fusion: bool = False
):
    """get_hierarchy() should return a hierarchy."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    h = fmr.get_hierarchy("TEST", "HCL_ELEMENT")

    assert len(mock.calls) == 1
    if is_fusion:
        assert (
            mock.calls[0].request.headers["Accept"] == Format.FUSION_JSON.value
        )
    else:
        assert (
            mock.calls[0].request.headers["Accept"]
            == Format.STRUCTURE_SDMX_JSON_2_0_0.value
        )

    assert isinstance(h, Hierarchy)
    assert len(h) == 18
    assert h.id == "HCL_ELEMENT"
    assert h.name == "Main"
    assert h.agency == "TEST"
    assert h.description is None
    assert h.version == "1.0"
    for c in h:
        assert isinstance(c, HierarchicalCode)


async def check_hcode_core_info(
    mock,
    fmr: AsyncRegistryClient,
    query,
    body,
):
    """Hierarchical codes contain core information such as ID and name."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    h = await fmr.get_hierarchy("TEST", "HCL_ELEMENT")

    __check_core_info(h.codes)


def check_hcode_details(mock, fmr: RegistryClient, query, body):
    """Hierarchical codes may have extended information."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    h = fmr.get_hierarchy("TEST", "HCL_ELEMENT")

    for hc in h:
        assert hc.description is None
        if hc.id == "M0":
            assert len(hc.codes) == 6
            for c in hc.codes:
                assert c.id in ["M1", "M2", "M3", "M4", "M5", "M6"]
                assert c.name is not None
                assert c.description is None
                if c.id == "M1":
                    assert len(c.codes) == 6
                    assert c.valid_from == datetime(
                        1970,
                        1,
                        2,
                        tzinfo=timezone.utc,
                    )
                    assert c.rel_valid_from == datetime(
                        1973,
                        1,
                        1,
                        tzinfo=timezone.utc,
                    )
                    for chld in c.codes:
                        if chld.id == "Li":
                            assert chld.rel_valid_from == datetime(
                                1920, 1, 1, tzinfo=timezone.utc
                            )
                            assert chld.rel_valid_to == datetime(
                                2020, 12, 31, 23, 59, 59, tzinfo=timezone.utc
                            )
                            pass
                else:
                    assert not c.codes
        elif hc.id == "D0":
            assert not hc.codes
        elif hc.id == "N0":
            assert len(hc.codes) == 2
            c1 = hc.codes[0]
            c2 = hc.codes[1]
            assert c1.id == "N1"
            assert c1.description is None
            assert not c1.codes
            assert c2.id == "N2"
            assert c2.description is None
            assert not c2.codes
        else:
            assert hc.id == "U0"
            assert not hc.codes


def __check_core_info(codes: Sequence[HierarchicalCode]):
    for code in codes:
        assert code.id is not None
        assert code.name is not None
    if code.codes:
        __check_core_info(code.codes)
