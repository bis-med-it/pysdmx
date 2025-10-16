import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import Component, Components, DataStructureDefinition


def check_dsd(mock, fmr: RegistryClient, query, body):
    """get_data_structures() should return a DSD."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    dsds = fmr.get_data_structures("BIS", "BIS_CBS", "1.0")

    assert len(mock.calls) == 1


async def check_dsd_async(mock, fmr: AsyncRegistryClient, query, body):
    """get_data_structures() should return a DSD (async)."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    dsds = await fmr.get_data_structures("BIS", "BIS_CBS", "1.0")

    assert len(mock.calls) == 1

    __check_content(dsds)


def __check_content(dsds):
    assert len(dsds) == 1
    dsd = dsds[0]
    assert isinstance(dsd, DataStructureDefinition)
    assert dsd.agency == "BIS"
    assert dsd.id == "BIS_CBS"
    assert dsd.version == "1.0"
    assert isinstance(dsd.components, Components)
    assert len(dsd.components) == 24
    for comp in dsd.components:
        assert isinstance(comp, Component)
        assert comp.id is not None
        assert comp.name is not None
        assert comp.concept is not None
        assert comp.concept.id is not None
        assert comp.id == comp.concept.id
        assert comp.required is not None
        assert comp.role is not None
        assert comp.dtype is not None
    assert dsd.groups is not None
    assert len(dsd.groups) == 1
    grp = dsd.groups[0]
    assert grp.id == "Sibling"
    assert grp.dimensions == [
        "L_MEASURE",
        "L_REP_CTY",
        "CBS_BANK_TYPE",
        "CBS_BASIS",
        "L_POSITION",
        "L_INSTR",
        "REM_MATURITY",
        "CURR_TYPE_BOOK",
        "L_CP_SECTOR",
        "L_CP_COUNTRY",
    ]
