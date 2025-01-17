import pytest

from pysdmx.api.fmr import RegistryClient, StructureFormat
from pysdmx.errors import NotImplemented


@pytest.mark.parametrize(
    "fmt",
    (
        f
        for f in StructureFormat
        if f
        not in [StructureFormat.FUSION_JSON, StructureFormat.SDMX_JSON_2_0_0]
    ),
)
def test_unsupported_format(fmt):
    with pytest.raises(NotImplemented) as ni:
        RegistryClient("https://registry.sdmx.org/sdmx/v2", fmt)
    assert ni.value.title is not None
    assert ni.value.description is not None
    assert "requested_format" in ni.value.csi
    assert ni.value.csi["requested_format"] == fmt.value
