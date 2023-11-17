from datetime import datetime as dt, timezone as tz
import re

import httpx
import pytest

from pysdmx.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model.map import (
    ComponentMapper,
    DateMapper,
    ImplicitMapper,
    MappingDefinition,
    ValueSetter,
)


def check_mapping(mock, fmr: RegistryClient, query, body):
    """get_mapping() should return a mapping definition report."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mapping = fmr.get_mapping("BIS", "SRC_2_MDD", "1.0")

    assert isinstance(mapping, MappingDefinition)
    count = (
        len(mapping.component_maps)
        + len(mapping.date_maps)
        + len(mapping.fixed_value_maps)
        + len(mapping.implicit_maps)
        + len(mapping.multiple_component_maps)
    )
    assert count == 9


def check_multi_mapping(mock, fmr: RegistryClient, query, body):
    """get_mapping() should return a mapping definition report."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mapping = fmr.get_mapping("BIS", "FXS_2_MDD", "1.0")

    assert isinstance(mapping, MappingDefinition)
    count = (
        len(mapping.component_maps)
        + len(mapping.date_maps)
        + len(mapping.fixed_value_maps)
        + len(mapping.implicit_maps)
        + len(mapping.multiple_component_maps)
    )
    assert count == 2
    assert len(mapping.multiple_component_maps) == 1
    assert len(mapping.implicit_maps) == 1


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
    assert len(mapping.date_maps) == 1
    assert len(mapping.fixed_value_maps) == 3
    assert len(mapping.implicit_maps) == 4
    assert len(mapping.multiple_component_maps) == 0

    for m in mapping.component_maps:
        __check_component(m)
    for m in mapping.date_maps:
        __check_date(m)
    for m in mapping.fixed_value_maps:
        __check_fixed(m)
    for m in mapping.implicit_maps:
        __check_implicit(m)


def __check_component(m: ComponentMapper):
    assert m.source == "CONTRACT"
    assert m.target == "CONTRACT"
    assert len(m.values) == 2
    for v in m.values:
        if v.source == "PROD TYPE":
            assert v.target == "_T"
            assert v.valid_from == dt(2008, 1, 1, 0, 0, 0, 0, tz.utc)
            assert v.valid_to == dt(2011, 1, 1, 10, 0, 42, 0, tz.utc)
        else:
            assert v.source == re.compile("^([A-Z0-9]+)$")
            assert v.target == "\\1"
            assert v.valid_from is None
            assert v.valid_to is None


def __check_date(m: DateMapper):
    assert m.source == "ACTIVITY_DATE"
    assert m.target == "TIME_PERIOD"
    assert m.frequency == "M"
    assert m.pattern == "MM/dd/yyyy"


def __check_implicit(m: ImplicitMapper):
    if m.source in ["OPTION_TYPE", "OI"]:
        assert m.target == m.source
    elif m.source == "VOL_MTD":
        assert m.target == "TO"
    elif m.source == "VOL_YTD":
        assert m.target == "TO_YTD"
    else:
        pytest.fail(f"Unexpected implicit value: {m}")


def __check_fixed(m: ValueSetter):
    if m.target == "OBS_STATUS":
        assert m.value == "A"
    elif m.target == "FREQ":
        assert m.value == "M"
    elif m.target == "CONF_STATUS":
        assert m.value == "C"
    else:
        pytest.fail(f"Unexpected fixed value: {m}")
