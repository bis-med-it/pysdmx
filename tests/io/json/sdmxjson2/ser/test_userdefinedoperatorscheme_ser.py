from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.vtl import JsonUserDefinedOperatorScheme
from pysdmx.model import Agency, Annotation
from pysdmx.model.vtl import UserDefinedOperator, UserDefinedOperatorScheme


@pytest.fixture
def udos():
    udo = UserDefinedOperator(
        "UDO1",
        name="User Defined Operator",
        operator_definition="operator definition",
    )
    return UserDefinedOperatorScheme(
        "UDOS",
        name="UDOS Scheme",
        agency="BIS",
        description="Just testing",
        version="1.42",
        items=[udo],
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        is_partial=True,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        vtl_version="1.0",
        vtl_mapping_scheme="VTL_MAPPING",
        ruleset_schemes=["RULESET1", "RULESET2"],
    )


@pytest.fixture
def udos_org():
    udo = UserDefinedOperator(
        "UDO1",
        name="User Defined Operator",
        operator_definition="operator definition",
    )
    return UserDefinedOperatorScheme(
        "UDOS",
        name="UDOS testing",
        agency=Agency("BIS"),
        items=[udo],
        vtl_version="1.0",
    )


@pytest.fixture
def udos_no_name():
    udo = UserDefinedOperator(
        "UDO1",
        name="User Defined Operator",
        operator_definition="operator definition",
    )
    return UserDefinedOperatorScheme(
        "UDOS", agency=Agency("BIS"), items=[udo], vtl_version="1.0"
    )


def test_udos(udos: UserDefinedOperatorScheme):
    sjson = JsonUserDefinedOperatorScheme.from_model(udos)

    assert sjson.id == udos.id
    assert sjson.name == udos.name
    assert sjson.agency == udos.agency
    assert sjson.description == udos.description
    assert sjson.version == udos.version
    assert len(sjson.userDefinedOperators) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == udos.valid_from
    assert sjson.validTo == udos.valid_to
    assert sjson.vtlVersion == udos.vtl_version
    assert sjson.vtlMappingScheme == udos.vtl_mapping_scheme
    assert sjson.rulesetSchemes == udos.ruleset_schemes


def test_udos_org(udos_org: UserDefinedOperatorScheme):
    sjson = JsonUserDefinedOperatorScheme.from_model(udos_org)

    assert sjson.agency == udos_org.agency.id


def test_udos_no_name(udos_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonUserDefinedOperatorScheme.from_model(udos_no_name)
