from datetime import datetime as dt, timezone as tz

import httpx
import pytest

from pysdmx.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model.map import ValueMap


def check_code_mapping_core(mock, fmr: RegistryClient, query, body):
    """get_code_mappings() should return a dict with mapped codes."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mapping = fmr.get_code_map("BIS", "ISO3166-A3_2_CTY", "1.0")

    assert len(mapping) == 3
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
