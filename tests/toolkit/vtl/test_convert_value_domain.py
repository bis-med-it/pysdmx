import pytest
from vtlengine.DataTypes import Integer, String
from vtlengine.Model import ValueDomain

from pysdmx.errors import Invalid
from pysdmx.model import Code, Codelist, Reference
from pysdmx.toolkit.vtl import (
    convert_codelist_to_vtl,
    convert_value_domain_to_sdmx,
)


@pytest.fixture
def codelist() -> Codelist:
    return Codelist(
        id="CL_FREQ",
        agency="SDMX",
        version="2.0",
        name="Frequency",
        items=[Code(id="A", name="Annual"), Code(id="M", name="Monthly")],
    )


def test_convert_codelist_to_vtl(codelist: Codelist) -> None:
    value_domain = convert_codelist_to_vtl(codelist, "cl_freq")

    assert value_domain.name == "cl_freq"
    assert value_domain.type is String
    assert value_domain.setlist == ["A", "M"]


@pytest.mark.parametrize(
    ("sdmx_type", "expected"),
    [("Codelist", "codelist"), ("ValueList", "valuelist")],
)
def test_convert_value_domain_to_sdmx(sdmx_type: str, expected: str) -> None:
    value_domain = ValueDomain(name="cl_freq", type=String, setlist=["A", "M"])
    reference = Reference(sdmx_type, "SDMX", "CL_FREQ", "2.0")

    result = convert_value_domain_to_sdmx(value_domain, reference)

    assert result.short_urn == f"{sdmx_type}=SDMX:CL_FREQ(2.0)"
    assert result.sdmx_type == expected
    assert result.name == "cl_freq"
    assert [(c.id, c.name) for c in result.codes] == [("A", "A"), ("M", "M")]


def test_convert_value_domain_of_numbers_to_sdmx() -> None:
    value_domain = ValueDomain(name="levels", type=Integer, setlist=[1, 2])
    reference = Reference("ValueList", "SDMX", "VL_LEVEL", "1.0")

    result = convert_value_domain_to_sdmx(value_domain, reference)

    assert [c.id for c in result.codes] == ["1", "2"]


def test_convert_value_domain_to_sdmx_invalid_reference() -> None:
    value_domain = ValueDomain(name="cl_freq", type=String, setlist=["A"])
    reference = Reference("Dataflow", "SDMX", "DF", "1.0")

    with pytest.raises(Invalid, match="Codelist or ValueList"):
        convert_value_domain_to_sdmx(value_domain, reference)


def test_codelist_roundtrip(codelist: Codelist) -> None:
    value_domain = convert_codelist_to_vtl(codelist, "cl_freq")
    reference = Reference("Codelist", "SDMX", "CL_FREQ", "2.0")

    result = convert_value_domain_to_sdmx(value_domain, reference)

    assert result.short_urn == codelist.short_urn
    assert [c.id for c in result.codes] == [c.id for c in codelist.codes]
