from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.vtl import JsonRulesetScheme
from pysdmx.model import Agency, Annotation
from pysdmx.model.vtl import Ruleset, RulesetScheme


@pytest.fixture
def rss():
    ruleset = Ruleset(
        "RULESET1",
        name="Test Ruleset",
        ruleset_definition="ruleset definition",
        ruleset_type="datapoint",
        ruleset_scope="variable",
    )
    return RulesetScheme(
        "RSS",
        name="RSS Scheme",
        agency="BIS",
        description="Just testing",
        version="1.42",
        items=[ruleset],
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        is_partial=True,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        vtl_version="1.0",
        vtl_mapping_scheme="VTL_MAPPING",
    )


@pytest.fixture
def rss_org():
    ruleset = Ruleset(
        "RULESET1",
        name="Test Ruleset",
        ruleset_definition="ruleset definition",
        ruleset_type="datapoint",
        ruleset_scope="variable",
    )
    return RulesetScheme(
        "RSS",
        name="RSS testing",
        agency=Agency("BIS"),
        items=[ruleset],
        vtl_version="1.0",
    )


@pytest.fixture
def rss_no_name():
    ruleset = Ruleset(
        "RULESET1",
        name="Test Ruleset",
        ruleset_definition="ruleset definition",
        ruleset_type="datapoint",
        ruleset_scope="variable",
    )
    return RulesetScheme(
        "RSS", agency=Agency("BIS"), items=[ruleset], vtl_version="1.0"
    )


def test_rss(rss: RulesetScheme):
    sjson = JsonRulesetScheme.from_model(rss)

    assert sjson.id == rss.id
    assert sjson.name == rss.name
    assert sjson.agency == rss.agency
    assert sjson.description == rss.description
    assert sjson.version == rss.version
    assert len(sjson.rulesets) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == rss.valid_from
    assert sjson.validTo == rss.valid_to
    assert sjson.vtlVersion == rss.vtl_version
    assert sjson.vtlMappingScheme == rss.vtl_mapping_scheme


def test_rss_org(rss_org: RulesetScheme):
    sjson = JsonRulesetScheme.from_model(rss_org)

    assert sjson.agency == rss_org.agency.id


def test_rss_no_name(rss_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonRulesetScheme.from_model(rss_no_name)
