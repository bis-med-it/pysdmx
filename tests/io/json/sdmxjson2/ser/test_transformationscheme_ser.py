from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.vtl import JsonTransformationScheme
from pysdmx.model import Agency, Annotation
from pysdmx.model.vtl import (
    CustomTypeScheme,
    NamePersonalisationScheme,
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UserDefinedOperatorScheme,
    VtlMappingScheme,
)


@pytest.fixture
def ts():
    transformation = Transformation(
        "TRANS1",
        name="Test Transformation",
        expression='DS_1 := DS_r[filter Id_1 = "A"];',
        is_persistent=True,
        result="DS_1",
    )

    # Create referenced schemes
    vtl_mapping_scheme = VtlMappingScheme(
        "VMS", name="VTL Mapping Scheme", agency="BIS", version="1.0"
    )
    custom_type_scheme = CustomTypeScheme(
        "CTS",
        name="Custom Type Scheme",
        agency="BIS",
        version="1.0",
        vtl_version="2.0",
    )
    name_personalisation_scheme = NamePersonalisationScheme(
        "NPS",
        name="Name Personalisation Scheme",
        agency="BIS",
        version="1.0",
        vtl_version="2.0",
    )
    ruleset_scheme = RulesetScheme(
        "RSS",
        name="Ruleset Scheme",
        agency="BIS",
        version="1.0",
        vtl_version="2.0",
    )
    user_defined_operator_scheme = UserDefinedOperatorScheme(
        "UDOS",
        name="User Defined Operator Scheme",
        agency="BIS",
        version="1.0",
        vtl_version="2.0",
    )

    return TransformationScheme(
        "TS",
        name="TS Scheme",
        agency="BIS",
        description="Just testing",
        version="1.42",
        items=[transformation],
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        is_partial=True,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        vtl_version="1.0",
        vtl_mapping_scheme=vtl_mapping_scheme,
        custom_type_scheme=custom_type_scheme,
        name_personalisation_scheme=name_personalisation_scheme,
        ruleset_schemes=[ruleset_scheme],
        user_defined_operator_schemes=[user_defined_operator_scheme],
    )


@pytest.fixture
def ts_org():
    transformation = Transformation(
        "TRANS1",
        name="Test Transformation",
        expression='DS_1 := DS_r[filter Id_1 = "A"];',
        is_persistent=True,
        result="DS_1",
    )
    return TransformationScheme(
        "TS",
        name="TS testing",
        agency=Agency("BIS"),
        items=[transformation],
        vtl_version="1.0",
    )


@pytest.fixture
def ts_no_name():
    transformation = Transformation(
        "TRANS1",
        name="Test Transformation",
        expression='DS_1 := DS_r[filter Id_1 = "A"];',
        is_persistent=True,
        result="DS_1",
    )
    return TransformationScheme(
        "TS", agency=Agency("BIS"), items=[transformation], vtl_version="1.0"
    )


def test_ts(ts: TransformationScheme):
    sjson = JsonTransformationScheme.from_model(ts)

    assert sjson.id == ts.id
    assert sjson.name == ts.name
    assert sjson.agency == ts.agency
    assert sjson.description == ts.description
    assert sjson.version == ts.version
    assert len(sjson.transformations) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == ts.valid_from
    assert sjson.validTo == ts.valid_to
    assert sjson.vtlVersion == ts.vtl_version
    assert (
        sjson.vtlMappingScheme
        == "urn:sdmx:org.sdmx.infomodel.vtl.VtlMappingScheme=BIS:VMS(1.0)"
    )
    assert (
        sjson.customTypeScheme
        == "urn:sdmx:org.sdmx.infomodel.vtl.CustomTypeScheme=BIS:CTS(1.0)"
    )
    assert (
        sjson.namePersonalisationScheme
        == "urn:sdmx:org.sdmx.infomodel.vtl.NamePersonalisationScheme=BIS:NPS(1.0)"
    )
    assert len(sjson.rulesetSchemes) == 1
    assert (
        sjson.rulesetSchemes[0]
        == "urn:sdmx:org.sdmx.infomodel.vtl.RulesetScheme=BIS:RSS(1.0)"
    )
    assert len(sjson.userDefinedOperatorSchemes) == 1
    assert (
        sjson.userDefinedOperatorSchemes[0]
        == "urn:sdmx:org.sdmx.infomodel.vtl.UserDefinedOperatorScheme=BIS:UDOS(1.0)"
    )


def test_ts_org(ts_org: TransformationScheme):
    sjson = JsonTransformationScheme.from_model(ts_org)

    assert sjson.agency == ts_org.agency.id


def test_ts_no_name(ts_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonTransformationScheme.from_model(ts_no_name)
