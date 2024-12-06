from datetime import datetime as dt, timezone as tz
from typing import Pattern

import httpx
import pytest

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model.concept import DataType
from pysdmx.model.map import (
    MultiRepresentationMap,
    MultiValueMap,
    RepresentationMap,
    ValueMap,
)


def check_code_mapping_core(mock, fmr: RegistryClient, query, body):
    """get_code_mappings() should return a dict with mapped codes."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mapping = fmr.get_code_map("BIS", "ISO3166-A3_2_CTY", "1.0")

    assert isinstance(mapping, RepresentationMap)
    assert len(mapping) == 3
    assert mapping.id == "ISO3166-A3_2_CTY"
    assert mapping.agency == "BIS"
    assert mapping.version == "1.0"
    assert mapping.name == "Representation Map from ISO 3166-A3 Codes to DD"
    assert "Codelist=ISO:CL_3166-A3(1.0)" in mapping.source
    assert "Codelist=BIS:CL_COUNTRY(1.0)" in mapping.target
    assert mapping.description is None
    for v in mapping:
        assert isinstance(v, ValueMap)


async def check_code_mapping_details(
    mock,
    fmr: AsyncRegistryClient,
    query,
    body,
):
    """Attributes contain the expected information."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mapping = await fmr.get_code_map("BIS", "ISO3166-A3_2_CTY", "1.0")

    for v in mapping:
        if v.source == "ARG":
            assert v.target == "AR"
            assert v.valid_from is None
            assert v.valid_to is None
        elif v.source == "URY":
            assert v.target == "UY"
            assert v.valid_from is None
            assert v.valid_to is None
        elif v.source == "SCG":
            assert v.target == "CS"
            assert v.valid_from == dt(2003, 7, 23, tzinfo=tz.utc)
            assert v.valid_to == dt(2006, 6, 1, tzinfo=tz.utc)
        else:
            pytest.fail(f"Unexpected mapping: {v}")


def check_multi_code_mapping_core(mock, fmr: RegistryClient, query, body):
    """get_code_mappings() should return a dict with mapped codes (multi)."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mapping = fmr.get_code_map("BIS", "CONSOLIDATE_ADDRESS_FIELDS", "1.42")

    assert isinstance(mapping, MultiRepresentationMap)
    assert mapping.id == "CONSOLIDATE_ADDRESS_FIELDS"
    assert mapping.agency == "BIS"
    assert mapping.version == "1.42"
    assert mapping.name == "Consolidates many address fields to one"
    assert mapping.description == "description"
    assert len(mapping.source) == 4
    assert len(mapping.target) == 1
    for s in mapping.source:
        assert s == DataType.STRING
    assert "ValueList=ISO:CL_3166-A3(1.0)" in mapping.target[0]
    for v in mapping:
        assert isinstance(v, MultiValueMap)


async def check_multi_code_mapping_details(
    mock,
    fmr: AsyncRegistryClient,
    query,
    body,
):
    """Attributes contain the expected information."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mapping = await fmr.get_code_map(
        "BIS", "CONSOLIDATE_ADDRESS_FIELDS", "1.42"
    )

    assert isinstance(mapping, MultiRepresentationMap)
    assert len(mapping) == 1
    m = mapping.maps[0]

    assert len(m.source) == 4
    assert len(m.target) == 1
    for s in m.source:
        assert s.startswith("regex:")
    t = m.target[0]
    assert t == "address"
