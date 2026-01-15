import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import Component, Components, DataStructureDefinition


def check_dsd(mock, fmr: RegistryClient, query, body):
    """get_data_structures() should return a DSD."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    dsds = fmr.get_data_structures("BIS", "BIS_CBS", "1.0")

    assert len(mock.calls) == 1

    __check_content(dsds)


def check_dsd_partial_cs(mock, fmr: RegistryClient, query, body):
    """get_data_structures() return a DSD, even if concepts are missing."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    dsds = fmr.get_data_structures("BIS", "BIS_CBS", "1.0")

    assert len(mock.calls) == 1

    __check_content(dsds)


async def check_dsd_async(mock, fmr: AsyncRegistryClient, query, body):
    """get_data_structures() should return a DSD (async)."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    dsds = await fmr.get_data_structures("BIS", "BIS_CBS", "1.0")

    assert len(mock.calls) == 1

    __check_content(dsds)


def check_multi_meas(mock, fmr: RegistryClient, query, body):
    """Multiple measures are extracted, including attachment level."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    dsds = fmr.get_data_structures("TEST", "TEST_MM", "1.0")

    assert len(mock.calls) == 1
    dsd = dsds[0]

    assert len(dsd.components.attributes) == 3
    for a in dsd.components.attributes:
        if a.id == "TO_STATUS":
            assert a.attachment_level == "TO"
        elif a.id == "OI_STATUS":
            assert a.attachment_level == "OI"
        else:
            assert a.id == "OBS_CONF"
            assert a.attachment_level == "OI,TO"


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
