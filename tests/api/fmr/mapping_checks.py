from datetime import datetime as dt
from datetime import timezone as tz

import httpx
import pytest

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.io.format import Format
from pysdmx.model.concept import DataType
from pysdmx.model.map import (
    ComponentMap,
    DatePatternMap,
    FixedValueMap,
    ImplicitComponentMap,
    MultiComponentMap,
    MultiRepresentationMap,
    MultiValueMap,
    RepresentationMap,
    StructureMap,
    ValueMap,
)


def check_mapping(
    mock, fmr: RegistryClient, query, body, is_fusion: bool = False
):
    """get_mapping() should return a mapping definition report."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mapping = fmr.get_mapping("BIS", "SRC_2_MDD", "1.0")

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

    assert isinstance(mapping, StructureMap)
    assert mapping.id == "SRC_2_MDD"
    assert mapping.name == "Map SRC data to MDD"
    assert mapping.agency == "BIS"
    assert mapping.version == "1.0"
    assert "BIS:SRC(1.0)" in mapping.source
    assert "BIS:MDD(1.0)" in mapping.target
    assert mapping.description is None
    assert len(mapping.maps) == 10
    assert len(mapping.component_maps) == 1
    assert len(mapping.date_pattern_maps) == 2
    assert len(mapping.fixed_value_maps) == 3
    assert len(mapping.implicit_component_maps) == 4
    assert len(mapping.multi_component_maps) == 0


def check_multi_mapping(mock, fmr: RegistryClient, query, body):
    """get_mapping() should return a mapping definition report."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mapping = fmr.get_mapping("BIS", "FXS_2_MDD", "1.0")

    assert isinstance(mapping, StructureMap)
    count = (
        len(mapping.component_maps)
        + len(mapping.date_pattern_maps)
        + len(mapping.fixed_value_maps)
        + len(mapping.implicit_component_maps)
        + len(mapping.multi_component_maps)
    )
    assert count == 2
    assert len(mapping.multi_component_maps) == 1
    assert len(mapping.implicit_component_maps) == 1
    mm = mapping.multi_component_maps[0]
    assert isinstance(mm, MultiComponentMap)
    assert isinstance(mm.values, MultiRepresentationMap)
    assert mm.values.id == "CONSOLIDATE_ADDRESS_FIELDS"
    assert mm.values.name is not None
    assert mm.values.agency == "BIS"
    assert len(mm.values.source) == 4
    for ms in mm.values.source:
        assert ms == DataType.STRING
    assert len(mm.values.target) == 1
    assert mm.values.target[0] == DataType.STRING
    assert mm.values.description is None
    assert mm.values.version == "1.0"
    assert len(mm.values) == 1
    for v in mm.values:
        assert isinstance(v, MultiValueMap)


async def check_mapping_rules(mock, fmr: AsyncRegistryClient, query, body):
    """Mapping rules contain the expected information."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mapping = await fmr.get_mapping("BIS", "SRC_2_MDD", "1.0")

    assert len(mapping.component_maps) == 1
    assert len(mapping.date_pattern_maps) == 2
    assert len(mapping.fixed_value_maps) == 3
    assert len(mapping.implicit_component_maps) == 4
    assert len(mapping.multi_component_maps) == 0

    for m in mapping.component_maps:
        __check_component(m)
    for m in mapping.date_pattern_maps:
        __check_date(m)
    for m in mapping.fixed_value_maps:
        __check_fixed(m)
    for m in mapping.implicit_component_maps:
        __check_implicit(m)


def __check_component(m: ComponentMap):
    assert m.source == "CONTRACT"
    assert m.target == "CONTRACT"
    assert isinstance(m.values, RepresentationMap)
    assert m.values.id == "CONTRACT"
    assert m.values.name == "Internal map of contract"
    assert m.values.agency == "BIS"
    assert "ValueList=BIS:CONTRACTS(1.0)" in m.values.source
    assert "ValueList=BIS:CONTRACTS(1.0)" in m.values.target
    assert m.values.description is None
    assert m.values.version == "1.0"
    assert len(m.values) == 2
    for v in m.values:
        assert isinstance(v, ValueMap)
        if v.source == "PROD TYPE":
            assert v.target == "_T"
            assert v.valid_from == dt(2008, 1, 1, 0, 0, 0, 0, tz.utc)
            assert v.valid_to == dt(2011, 1, 1, 10, 0, 42, 0, tz.utc)
        else:
            assert v.source == "regex:^([A-Z0-9]+)$"
            assert v.target == "\\1"
            assert v.valid_from is None
            assert v.valid_to is None


def __check_date(m: DatePatternMap):
    if m.id == "my_id":
        assert m.source == "ACTIVITY_DATE"
        assert m.target == "TIME_PERIOD"
        assert m.frequency == "M"
        assert m.pattern == "MM/dd/yyyy"
        assert m.pattern_type == "fixed"
        assert m.locale == "en"
    else:
        assert m.source == "VOLUME_MONTH"
        assert m.target == "TIME_PERIOD"
        assert m.frequency == "CONTRACT_CODE"
        assert m.pattern == "ddMMyy"
        assert m.pattern_type == "variable"
        assert m.locale == "es"
        assert m.id == "your_id"


def __check_implicit(m: ImplicitComponentMap):
    if m.source in ["OPTION_TYPE", "OI"]:
        assert m.target == m.source
    elif m.source == "VOL_MTD":
        assert m.target == "TO"
    elif m.source == "VOL_YTD":
        assert m.target == "TO_YTD"
    else:
        pytest.fail(f"Unexpected implicit value: {m}")


def __check_fixed(m: FixedValueMap):
    if m.target == "OBS_STATUS":
        assert m.value == "A"
        assert m.located_in == "target"
    elif m.target == "FREQ":
        assert m.value == "M"
        assert m.located_in == "target"
    elif m.target == "CONF_STATUS":
        assert m.value == "C"
        assert m.located_in == "source"
    else:
        pytest.fail(f"Unexpected fixed value: {m}")
