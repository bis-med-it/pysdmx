import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.vtl import JsonRuleset
from pysdmx.model.vtl import Ruleset


@pytest.fixture
def ruleset():
    return Ruleset(
        "RULESET1",
        name="Test Ruleset",
        description="Description",
        ruleset_definition="ruleset definition",
        ruleset_type="datapoint",
        ruleset_scope="variable",
    )


@pytest.fixture
def ruleset_no_name():
    return Ruleset(
        "RULESET1",
        ruleset_definition="ruleset definition",
        ruleset_type="datapoint",
        ruleset_scope="variable",
    )


def test_ruleset(ruleset: Ruleset):
    sjson = JsonRuleset.from_model(ruleset)

    assert sjson.id == ruleset.id
    assert sjson.name == ruleset.name
    assert sjson.description == ruleset.description
    assert len(sjson.annotations) == 0
    assert sjson.rulesetDefinition == ruleset.ruleset_definition
    assert sjson.rulesetType == ruleset.ruleset_type
    assert sjson.rulesetScope == ruleset.ruleset_scope


def test_ruleset_no_name(ruleset_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonRuleset.from_model(ruleset_no_name)
