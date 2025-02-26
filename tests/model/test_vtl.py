import pytest

from pysdmx.errors import Invalid
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


@pytest.fixture
def valid_ruleset():
    return Ruleset(
        id="id",
        name="name",
        description="description",
        ruleset_type="datapoint",
        ruleset_definition="""define datapoint ruleset signValidation
            (variable ACCOUNTING_ENTRY as AE, INT_ACC_ITEM as IAI,
                FUNCTIONAL_CAT as FC, INSTR_ASSET as IA, OBS_VALUE as O)
                is
                sign1c: when AE = "C" and IAI = "G" then O > 0 errorcode
                "sign1c" errorlevel 1
                end datapoint ruleset;""",
        ruleset_scope="variable",
    )


@pytest.fixture
def valid_udo():
    return UserDefinedOperator(
        id="id",
        name="name",
        description="description",
        operator_definition="""define operator filter_ds
            (ds1 dataset, great_cons string default "1",
             less_cons number default 4.0)
            returns dataset
            is ds1[filter Me_1 > great_cons and Me_2 < less_cons]
            end operator;""",
    )


@pytest.fixture
def valid_transformation():
    return Transformation(
        id="id",
        name="name",
        description="description",
        expression="DS_1 + 1",
        result="DS_r",
        is_persistent=True,
    )


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
    with pytest.raises(
        Invalid, match=f"Invalid VTL version: {invalid_vtl_version}"
    ):
        TransformationScheme(
            id="id",
            name="name",
            description="description",
            vtl_version=invalid_vtl_version,
        )


def test_instantiation_t(vtl_version, valid_transformation):
    transformation = valid_transformation

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


def test_instantiation_udo(valid_udo):
    udo = valid_udo

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
    with pytest.raises(
        Invalid, match=f"Invalid VTL version: {invalid_vtl_version}"
    ):
        UserDefinedOperatorScheme(
            id="id",
            name="name",
            description="description",
            vtl_version=invalid_vtl_version,
        )


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
    with pytest.raises(
        Invalid, match=f"Invalid VTL version: {invalid_vtl_version}"
    ):
        RulesetScheme(
            id="id",
            name="name",
            description="description",
            vtl_version=invalid_vtl_version,
        )


def test_instantiation_ruleset(valid_ruleset):
    ruleset = valid_ruleset

    assert ruleset.id == "id"
    assert ruleset.name == "name"
    assert ruleset.description == "description"
    assert ruleset.ruleset_type == "datapoint"
    assert ruleset.ruleset_scope == "variable"
