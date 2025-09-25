import pytest

from pysdmx.errors import Invalid
from pysdmx.model import (
    Ruleset,
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
)
from pysdmx.toolkit.vtl.validation import model_validations


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


@pytest.fixture
def valid_ruleset_scheme(valid_ruleset):
    return RulesetScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        items=[valid_ruleset],
    )


@pytest.fixture
def valid_udo_scheme(valid_udo):
    return UserDefinedOperatorScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        items=[valid_udo],
    )


@pytest.fixture
def valid_ts(
    valid_udo,
    valid_ruleset,
    valid_transformation,
    valid_ruleset_scheme,
    valid_udo_scheme,
):
    return TransformationScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        ruleset_schemes=[valid_ruleset_scheme],
        user_defined_operator_schemes=[valid_udo_scheme],
        items=[valid_transformation],
    )


def test_valid_model_object_ruleset(valid_ruleset):
    model_validations(valid_ruleset)


def test_valid_model_object_udo(valid_udo):
    model_validations(valid_udo)


def test_valid_model_object_transformation(valid_transformation):
    model_validations(valid_transformation)


def test_valid_model_object_ruleset_scheme(valid_ruleset_scheme):
    model_validations(valid_ruleset_scheme)


def test_valid_model_object_udo_scheme(valid_udo_scheme):
    model_validations(valid_udo_scheme)


def test_valid_model_object_ts(valid_ts):
    model_validations(valid_ts)


def test_invalid_model_object():
    with pytest.raises(Invalid, match="Invalid model object"):
        model_validations("invalid")
