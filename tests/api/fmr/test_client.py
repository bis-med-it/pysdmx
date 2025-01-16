import pytest

from pysdmx.api.fmr import Format, RegistryClient
from pysdmx.errors import NotImplemented


def test_unsupported_format():
    with pytest.raises(NotImplemented) as ni:
        RegistryClient(
            "https://registry.sdmx.org/sdmx/v2",
            Format.SDMX_JSON_1_0_0,
        )
    assert ni.value.title is not None
    assert ni.value.description is not None
    assert "requested_format" in ni.value.csi
    assert ni.value.csi["requested_format"] == Format.SDMX_JSON_1_0_0.value
