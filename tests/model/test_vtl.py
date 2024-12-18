import pytest

from pysdmx.model.vtl import (
    Ruleset,
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
)


@pytest.fixture
def vtl_version():
    return "2.0"


@pytest.fixture
def invalid_vtl_version():
    return "2.4"


def test_instantiation_ts(vtl_version):
    transformation = TransformationScheme(
        id="id",
        name="name",
        description="description",
        vtl_version=vtl_version,
    )

    assert transformation.id == "id"
    assert transformation.name == "name"
    assert transformation.description == "description"
    assert transformation.vtl_version == vtl_version


def test_instantiation_ts_invalid_vtl_version(invalid_vtl_version):
    try:
        TransformationScheme(
            id="id",
            name="name",
            description="description",
            vtl_version=invalid_vtl_version,
        )
    except Exception as e:
        assert type(e).__name__ == "Invalid"
        assert str(e) == f"Invalid VTL version: {invalid_vtl_version}"


def test_instantiation_t(vtl_version):
    transformation = Transformation(
        id="id",
        name="name",
        description="description",
        expression="DS_1 + 1",
        result="DS_r",
        is_persistent=True,
    )

    assert transformation.id == "id"
    assert transformation.name == "name"
    assert transformation.description == "description"
    assert transformation.expression == "DS_1 + 1"
    assert transformation.result == "DS_r"
    assert transformation.is_persistent
    assert transformation.full_expression == "DS_r <- DS_1 + 1;"


def test_instantiation_t_not_persistent(vtl_version):
    transformation = Transformation(
        id="id",
        name="name",
        description="description",
        expression="DS_1 + 1",
        result="DS_r",
        is_persistent=False,
    )

    assert transformation.id == "id"
    assert transformation.name == "name"
    assert transformation.description == "description"
    assert transformation.expression == "DS_1 + 1"
    assert transformation.result == "DS_r"
    assert not transformation.is_persistent
    assert transformation.full_expression == "DS_r := DS_1 + 1;"


def test_instantiation_udo():
    udo = UserDefinedOperator(
        id="id", name="name", description="description", operator_definition=""
    )

    assert udo.id == "id"
    assert udo.name == "name"
    assert udo.description == "description"


def test_instantiation_udo_scheme(vtl_version):
    udo_scheme = UserDefinedOperatorScheme(
        id="id",
        name="name",
        description="description",
        vtl_version=vtl_version,
    )

    assert udo_scheme.id == "id"
    assert udo_scheme.name == "name"
    assert udo_scheme.description == "description"
    assert udo_scheme.vtl_version == "2.0"


def test_instantiation_udo_scheme_invalid_vtl_version(invalid_vtl_version):
    try:
        UserDefinedOperatorScheme(
            id="id",
            name="name",
            description="description",
            vtl_version=invalid_vtl_version,
        )
    except Exception as e:
        assert type(e).__name__ == "Invalid"
        assert str(e) == f"Invalid VTL version: {invalid_vtl_version}"


def test_instantiation_ruleset_scheme(vtl_version):
    ruleset_scheme = RulesetScheme(
        id="id",
        name="name",
        description="description",
        vtl_version=vtl_version,
    )

    assert ruleset_scheme.id == "id"
    assert ruleset_scheme.name == "name"
    assert ruleset_scheme.description == "description"
    assert ruleset_scheme.vtl_version == vtl_version


def test_instantiation_ruleset_scheme_invalid_vtl_version(invalid_vtl_version):
    try:
        RulesetScheme(
            id="id",
            name="name",
            description="description",
            vtl_version=invalid_vtl_version,
        )
    except Exception as e:
        assert type(e).__name__ == "Invalid"
        assert str(e) == f"Invalid VTL version: {invalid_vtl_version}"


def test_instantiation_ruleset():
    ruleset = Ruleset(
        id="id",
        name="name",
        description="description",
        ruleset_type="datapoint",
        ruleset_definition="",
        ruleset_scope="",
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
            ruleset_type="invalid",
            ruleset_definition="",
            ruleset_scope="",
        )
    except Exception as e:
        assert type(e).__name__ == "Invalid"
        assert str(e) == "Invalid VTL Ruleset type: invalid"
