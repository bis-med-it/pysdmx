import pytest

from pysdmx.api.fmr import Format, RegistryClient
from pysdmx.errors import NotImplemented


@pytest.mark.parametrize(
    "fmt",
    (
        f
        for f in Format
        if f not in [Format.FUSION_JSON, Format.SDMX_JSON_2_0_0]
    ),
)
def test_unsupported_format(fmt):
    with pytest.raises(NotImplemented) as ni:
        RegistryClient("https://registry.sdmx.org/sdmx/v2", fmt)
    assert ni.value.title is not None
    assert ni.value.description is not None
    assert "requested_format" in ni.value.csi
    assert ni.value.csi["requested_format"] == fmt.value
