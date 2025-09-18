from datetime import datetime

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.code import JsonHierarchicalCode
from pysdmx.model import Annotation, HierarchicalCode


@pytest.fixture
def code():
    rel_vf = datetime(2001, 1, 1)
    rel_vt = datetime(2027, 12, 31)
    nested = HierarchicalCode(
        "A1",
        "Another HCode",
        urn="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=TEST:Z(1.0).P",
    )
    return HierarchicalCode(
        "A",
        "An HCode",
        rel_valid_from=rel_vf,
        rel_valid_to=rel_vt,
        urn="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=TEST:Z(1.0).V",
        codes=[nested],
    )


@pytest.fixture
def code_no_urn():
    return HierarchicalCode("A")


@pytest.fixture
def code_diff_ids():
    ano = Annotation(id="hcode", type="pysdmx", text="Z")
    return HierarchicalCode(
        "A",
        urn="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=TEST:Z(1.0).V",
        annotations=[ano],
    )


def test_code(code: HierarchicalCode):
    sjson = JsonHierarchicalCode.from_model(code)

    assert sjson.id == code.id
    assert sjson.code == code.urn
    assert sjson.validFrom == code.rel_valid_from
    assert sjson.validTo == code.rel_valid_to
    assert len(sjson.annotations) == 0
    assert len(sjson.hierarchicalCodes) == 1
    assert isinstance(sjson.hierarchicalCodes[0], JsonHierarchicalCode)
    assert sjson.hierarchicalCodes[0].id == "A1"


def test_code_diff_ids(code_diff_ids: HierarchicalCode):
    sjson = JsonHierarchicalCode.from_model(code_diff_ids)

    assert sjson.id == "Z"
    assert sjson.code == code_diff_ids.urn
    assert sjson.validFrom is None
    assert sjson.validTo is None
    assert len(sjson.annotations) == 0
    assert len(sjson.hierarchicalCodes) == 0


def test_code_no_urn(code_no_urn):
    with pytest.raises(errors.Invalid, match="must have the code urn"):
        JsonHierarchicalCode.from_model(code_no_urn)
