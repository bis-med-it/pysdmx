import pytest

from pysdmx.model.vtl import (
    Ruleset,
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
)


@pytest.fixture()
def vtlVersion():
    return "2.0"


@pytest.fixture()
def invalidVtlVersion():
    return "2.4"


def test_instantiation_ts(vtlVersion):
    transformation = TransformationScheme(
        id="id", name="name", description="description", vtlVersion=vtlVersion
    )

    assert transformation.id == "id"
    assert transformation.name == "name"
    assert transformation.description == "description"
    assert transformation.vtlVersion == vtlVersion


def test_instantiation_ts_invalid_vtl_version(invalidVtlVersion):
    try:
        TransformationScheme(
            id="id",
            name="name",
            description="description",
            vtlVersion=invalidVtlVersion,
        )
    except Exception as e:
        assert type(e).__name__ == "Invalid"
        assert str(e) == f"Invalid VTL version: {invalidVtlVersion}"


def test_instantiation_t(vtlVersion):
    transformation = Transformation(
        id="id",
        name="name",
        description="description",
        Expression="DS_1 + 1",
        Result="DS_r",
        isPersistent=True,
    )

    assert transformation.id == "id"
    assert transformation.name == "name"
    assert transformation.description == "description"
    assert transformation.Expression == "DS_1 + 1"
    assert transformation.Result == "DS_r"
    assert transformation.isPersistent
    assert transformation.full_expression == "DS_r <- DS_1 + 1;"


def test_instantiation_t_not_persistent(vtlVersion):
    transformation = Transformation(
        id="id",
        name="name",
        description="description",
        Expression="DS_1 + 1",
        Result="DS_r",
        isPersistent=False,
    )

    assert transformation.id == "id"
    assert transformation.name == "name"
    assert transformation.description == "description"
    assert transformation.Expression == "DS_1 + 1"
    assert transformation.Result == "DS_r"
    assert not transformation.isPersistent
    assert transformation.full_expression == "DS_r := DS_1 + 1;"


def test_instantiation_udo():
    udo = UserDefinedOperator(
        id="id", name="name", description="description", operatorDefinition=""
    )

    assert udo.id == "id"
    assert udo.name == "name"
    assert udo.description == "description"


def test_instantiation_udo_scheme(vtlVersion):
    udo_scheme = UserDefinedOperatorScheme(
        id="id", name="name", description="description", vtlVersion=vtlVersion
    )

    assert udo_scheme.id == "id"
    assert udo_scheme.name == "name"
    assert udo_scheme.description == "description"
    assert udo_scheme.vtlVersion == "2.0"


def test_instantiation_udo_scheme_invalid_vtl_version(invalidVtlVersion):
    try:
        UserDefinedOperatorScheme(
            id="id",
            name="name",
            description="description",
            vtlVersion=invalidVtlVersion,
        )
    except Exception as e:
        assert type(e).__name__ == "Invalid"
        assert str(e) == f"Invalid VTL version: {invalidVtlVersion}"


def test_instantiation_ruleset_scheme(vtlVersion):
    ruleset_scheme = RulesetScheme(
        id="id", name="name", description="description", vtlVersion=vtlVersion
    )

    assert ruleset_scheme.id == "id"
    assert ruleset_scheme.name == "name"
    assert ruleset_scheme.description == "description"
    assert ruleset_scheme.vtlVersion == vtlVersion


def test_instantiation_ruleset_scheme_invalid_vtl_version(invalidVtlVersion):
    try:
        RulesetScheme(
            id="id",
            name="name",
            description="description",
            vtlVersion=invalidVtlVersion,
        )
    except Exception as e:
        assert type(e).__name__ == "Invalid"
        assert str(e) == f"Invalid VTL version: {invalidVtlVersion}"


def test_instantiation_ruleset():
    ruleset = Ruleset(
        id="id",
        name="name",
        description="description",
        rulesetType="datapoint",
        rulesetDefinition="",
        rulesetScope="",
    )

    assert ruleset.id == "id"
    assert ruleset.name == "name"
    assert ruleset.description == "description"


def test_instantiation_ruleset_invalid_type():
    try:
        Ruleset(
            id="id",
            name="name",
            description="description",
            rulesetType="invalid",
            rulesetDefinition="",
            rulesetScope="",
        )
    except Exception as e:
        assert type(e).__name__ == "Invalid"
        assert str(e) == "Invalid VTL Ruleset type: invalid"
