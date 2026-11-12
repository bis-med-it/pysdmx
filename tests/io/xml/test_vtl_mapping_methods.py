from pathlib import Path

import pytest

from pysdmx.io import read_sdmx, write_sdmx
from pysdmx.io.format import Format
from pysdmx.model import FromVtlMapping, ToVtlMapping

SAMPLES = Path(__file__).parent / "sdmx31" / "reader" / "samples"
STRUCTURE_FORMATS = [
    Format.STRUCTURE_SDMX_ML_2_1,
    Format.STRUCTURE_SDMX_ML_3_0,
    Format.STRUCTURE_SDMX_ML_3_1,
]


def test_mapping_methods_without_content_are_read():
    scheme = read_sdmx(
        SAMPLES / "vtlmapping_no_method.xml"
    ).get_vtl_mapping_schemes()[0]

    mapping = scheme.items[0]

    assert mapping.to_vtl_mapping_method == ToVtlMapping()
    assert mapping.from_vtl_mapping_method == FromVtlMapping()


@pytest.mark.parametrize("fmt", STRUCTURE_FORMATS)
@pytest.mark.parametrize(
    "sample",
    [
        # Methods with a sub space and no method
        "VTL_Sample_3.xml",
        # Methods with neither a sub space nor a method
        "vtlmapping_no_method.xml",
    ],
)
def test_mapping_methods_without_method_are_written_without_method(
    fmt, sample
):
    scheme = read_sdmx(SAMPLES / sample).get_vtl_mapping_schemes()[0]

    out = write_sdmx([scheme], fmt)

    assert "method=" not in out
    back = read_sdmx(out).get_vtl_mapping_schemes()[0]
    assert [m.to_vtl_mapping_method for m in back.items] == [
        m.to_vtl_mapping_method for m in scheme.items
    ]
    assert [m.from_vtl_mapping_method for m in back.items] == [
        m.from_vtl_mapping_method for m in scheme.items
    ]
