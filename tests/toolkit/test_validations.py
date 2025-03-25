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
from pysdmx.toolkit.vtl._validations import (
    _ruleset_scheme_validations,
    _ruleset_validation,
    _transformation_scheme_validations,
    _transformation_validations,
    _user_defined_operator_scheme_validations,
    _user_defined_operator_validation,
)
from pysdmx.util import Reference


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


@pytest.fixture
def valid_udo_scheme_reference():
    return Reference(
        sdmx_type="UserDefinedOperatorScheme",
        agency="ECB",
        id="id",
        version="2.0",
    )


@pytest.fixture
def valid_ruleset_scheme_reference():
    return Reference(
        sdmx_type="RulesetScheme", agency="ECB", id="id", version="2.0"
    )


@pytest.fixture
def valid_ts_with_reference(
    valid_udo,
    valid_ruleset,
    valid_transformation,
    valid_ruleset_scheme,
    valid_udo_scheme,
    valid_ruleset_scheme_reference,
    valid_udo_scheme_reference,
):
    return TransformationScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        ruleset_schemes=[valid_ruleset_scheme, valid_ruleset_scheme_reference],
        user_defined_operator_schemes=[
            valid_udo_scheme,
            valid_udo_scheme_reference,
        ],
        items=[valid_transformation],
    )


@pytest.fixture
def invalid_ts_with_wrong_ruleset_scheme_reference(
    valid_udo,
    valid_ruleset,
    valid_transformation,
    valid_ruleset_scheme,
    valid_udo_scheme_reference,
):
    return TransformationScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        ruleset_schemes=[valid_udo_scheme_reference],
        items=[valid_transformation],
    )


@pytest.fixture
def invalid_ts_with_wrong_udo_scheme_reference(
    valid_udo,
    valid_ruleset,
    valid_transformation,
    valid_udo_scheme,
    valid_ruleset_scheme_reference,
):
    return TransformationScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        user_defined_operator_schemes=[valid_ruleset_scheme_reference],
        items=[valid_transformation],
    )


def test_ruleset_validation(valid_ruleset):
    _ruleset_validation(valid_ruleset)


def test_invalid_ruleset_definition():
    ruleset = Ruleset(
        id="id",
        name="name",
        description="description",
        ruleset_type="datapoint",
        ruleset_definition="""define datapoint ruleset signValidation
                (variable ACCOUNTING_ENTRY as AE, INT_ACC_ITEM as IAI,
                FUNCTIONAL_CAT as FC, INSTR_ASSET as IA, OBS_VALUE as O)
                is """,
        ruleset_scope="variable",
    )
    with pytest.raises(
        Invalid, match="Invalid ruleset definition: Not valid VTL Syntax"
    ):
        _ruleset_validation(ruleset)


def test_ruleset_invalid_children_number():
    ruleset = Ruleset(
        id="id",
        name="name",
        description="description",
        ruleset_type="datapoint",
        ruleset_definition="""define datapoint ruleset signValidation
                    (variable ACCOUNTING_ENTRY as AE, INT_ACC_ITEM as IAI,
                        FUNCTIONAL_CAT as FC,
                        INSTR_ASSET as IA, OBS_VALUE as O) is
                        sign1c: when AE = "C"
                        and IAI = "G" then O > 0 errorcode
                        "sign1c" errorlevel 1
                        end datapoint ruleset;
                        define datapoint ruleset signValidation
                    (variable ACCOUNTING_ENTRY as AE, INT_ACC_ITEM as IAI,
                        FUNCTIONAL_CAT as FC,
                        INSTR_ASSET as IA, OBS_VALUE as O) is
                        sign1c: when AE = "C"
                        and IAI = "G" then O > 0 errorcode
                        "sign1c" errorlevel 1
                        end datapoint ruleset;""",
        ruleset_scope="variable",
    )
    with pytest.raises(
        Invalid, match="A single RulesetDefinition is valid in a Ruleset"
    ):
        _ruleset_validation(ruleset)


def test_invalid_ruleset_type():
    ruleset = Ruleset(
        id="id",
        name="name",
        description="description",
        ruleset_type="hierarchical",
        ruleset_definition="""define datapoint ruleset signValidation
                (variable ACCOUNTING_ENTRY as AE, INT_ACC_ITEM as IAI,
                FUNCTIONAL_CAT as FC, INSTR_ASSET as IA, OBS_VALUE as O)
                is
                sign1c: when AE = "C" and IAI = "G" then O > 0 errorcode
                "sign1c" errorlevel 1
                end datapoint ruleset;""",
        ruleset_scope="variable",
    )
    with pytest.raises(
        Invalid, match="Ruleset type does not match the definition"
    ):
        _ruleset_validation(ruleset)


def test_invalid_ruleset_type2():
    ruleset = Ruleset(
        id="id",
        name="name",
        description="description",
        ruleset_type="datapoint",
        ruleset_definition="""define hierarchical ruleset accountingEntry
                (variable rule ACCOUNTING_ENTRY) is
                B = C - D errorcode "Balance(credit-debit)" errorlevel 4;
                N = A - L errorcode "Net(assets-liabilities)" errorlevel 4
                end hierarchical ruleset;""",
        ruleset_scope="variable",
    )
    with pytest.raises(
        Invalid, match="Ruleset type does not match the definition"
    ):
        _ruleset_validation(ruleset)


def test_invalid_ruleset_scope():
    ruleset = Ruleset(
        id="id",
        name="name",
        description="description",
        ruleset_type="datapoint",
        ruleset_definition="""define datapoint ruleset signValidation
                (variable ACCOUNTING_ENTRY as AE,INT_ACC_ITEM as IAI,
                FUNCTIONAL_CAT as FC,
                  INSTR_ASSET as IA, OBS_VALUE as O)
                is
                sign1c: when AE = "C" and IAI = "G" then O > 0 errorcode
                "sign1c" errorlevel 1
                end datapoint ruleset;""",
        ruleset_scope="valuedomain",
    )
    with pytest.raises(
        Invalid, match="Ruleset scope does not match the definition"
    ):
        _ruleset_validation(ruleset)


def test_invalid_ruleset_scope2():
    ruleset = Ruleset(
        id="id",
        name="name",
        description="description",
        ruleset_type="datapoint",
        ruleset_definition="""define datapoint ruleset signValidation
               (valuedomain ACCOUNTING_ENTRY as AE, INT_ACC_ITEM as IAI,
               FUNCTIONAL_CAT as FC, INSTR_ASSET as IA, OBS_VALUE as O)
               is
               sign1c: when AE = "C" and IAI = "G" then O > 0 errorcode
               "sign1c" errorlevel 1
               end datapoint ruleset;""",
        ruleset_scope="variable",
    )
    with pytest.raises(
        Invalid, match="Ruleset scope does not match the definition"
    ):
        _ruleset_validation(ruleset)


def test_ruleset_scheme_validation(valid_ruleset_scheme):
    _ruleset_scheme_validations(valid_ruleset_scheme)


def test_invalid_empty_items_ruleset_scheme():
    ruleset_scheme = RulesetScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        items=[],
    )
    with pytest.raises(
        Invalid, match="RulesetScheme must contain at least one Ruleset"
    ):
        _ruleset_scheme_validations(ruleset_scheme)


def test_invalid_item_ruleset_scheme():
    ruleset_scheme = RulesetScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        items=["invalid"],
    )
    with pytest.raises(
        Invalid, match="RulesetScheme must contain Ruleset items"
    ):
        _ruleset_scheme_validations(ruleset_scheme)


def test_instantiation_udo(valid_udo):
    _user_defined_operator_validation(valid_udo)


def test_invalid_udo_definition():
    udo = UserDefinedOperator(
        id="id",
        name="name",
        description="description",
        operator_definition="""define operator filter_ds
                (ds1 dataset, great_cons string default "1",
                 less_cons number default 4.0)
                returns dataset is ds1
                [filter Me_1 > great_cons and Me_2 < less_cons]
                end operator""",
    )
    with pytest.raises(
        Invalid, match="Invalid operator definition: Not valid VTL Syntax"
    ):
        _user_defined_operator_validation(udo)


def test_udo_invalid_children_number():
    udo = UserDefinedOperator(
        id="id",
        name="name",
        description="description",
        operator_definition="""define operator filter_ds
                           (ds1 dataset, great_cons string default "1",
                            less_cons number default 4.0)
                           returns dataset
                           is ds1[filter Me_1 >
                           great_cons and Me_2 < less_cons]
                           end operator;
                           define operator filter_ds
                           (ds1 dataset, great_cons string default "1",
                            less_cons number default 4.0)
                           returns dataset
                           is ds1[filter Me_1 >
                           great_cons and Me_2 < less_cons]
                           end operator;""",
    )
    with pytest.raises(
        Invalid,
        match="A single OperatorDefinition is valid in "
        "a UserDefinedOperator",
    ):
        _user_defined_operator_validation(udo)


def test_invalid_udo_type():
    udo = UserDefinedOperator(
        id="id",
        name="name",
        description="description",
        operator_definition="""define datapoint ruleset signValidation
                (variable ACCOUNTING_ENTRY as AE, INT_ACC_ITEM as IAI,
                FUNCTIONAL_CAT as FC, INSTR_ASSET as IA, OBS_VALUE as O)
                is
                sign1c: when AE = "C" and IAI = "G" then O > 0 errorcode
                "sign1c" errorlevel 1
                end datapoint ruleset;""",
    )
    with pytest.raises(
        Invalid,
        match="User defined operator type does not match the definition",
    ):
        _user_defined_operator_validation(udo)


def test_user_defined_operator_scheme_validation(valid_udo_scheme):
    _user_defined_operator_scheme_validations(valid_udo_scheme)


def test_invalid_empty_items_udo_scheme():
    udo_scheme = UserDefinedOperatorScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        items=[],
    )
    with pytest.raises(
        Invalid,
        match="UserDefinedOperatorScheme must contain at least "
        "one UserDefinedOperator",
    ):
        _user_defined_operator_scheme_validations(udo_scheme)


def test_invalid_item_udo_scheme():
    udo_scheme = UserDefinedOperatorScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        items=["invalid"],
    )
    with pytest.raises(
        Invalid,
        match="UserDefinedOperatorScheme must contain "
        "UserDefinedOperator items",
    ):
        _user_defined_operator_scheme_validations(udo_scheme)


def test_instantiation_t(valid_transformation):
    _transformation_validations(valid_transformation)


def test_invalid_transformation_expression():
    transformation = Transformation(
        id="id",
        name="name",
        description="description",
        expression="DS_1 @ 1",
        result="DS_r",
        is_persistent=True,
    )
    with pytest.raises(
        Invalid,
        match="Invalid transformation definition: Not valid VTL Syntax",
    ):
        _transformation_validations(transformation)


def test_transformation_invalid_children_number():
    transformation = Transformation(
        id="id",
        name="name",
        description="description",
        expression="DS_1 + 1;DS_r := DS_2 + 1",
        result="DS_r",
        is_persistent=True,
    )
    with pytest.raises(
        Invalid, match="A single Assignment is valid in a Transformation"
    ):
        _transformation_validations(transformation)


def test_transformation_scheme_validation(valid_ts):
    _transformation_scheme_validations(valid_ts)


def test_transformation_scheme_validation_with_reference(
    valid_ts_with_reference,
):
    _transformation_scheme_validations(valid_ts_with_reference)


def test_invalid_ts_with_wrong_ruleset_scheme_reference(
    invalid_ts_with_wrong_ruleset_scheme_reference,
):
    with pytest.raises(
        Invalid,
        match="Reference in Ruleset Schemes must point "
        "to a Ruleset Scheme, got UserDefinedOperatorScheme",
    ):
        _transformation_scheme_validations(
            invalid_ts_with_wrong_ruleset_scheme_reference
        )


def test_invalid_ts_with_wrong_udo_scheme_reference(
    invalid_ts_with_wrong_udo_scheme_reference,
):
    with pytest.raises(
        Invalid,
        match="Reference in User Defined Operator Schemes must "
        "point to a Defined Operator Scheme, got RulesetScheme",
    ):
        _transformation_scheme_validations(
            invalid_ts_with_wrong_udo_scheme_reference
        )


def test_empty_items_transformation_scheme(
    valid_udo_scheme, valid_ruleset_scheme
):
    ts = TransformationScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        ruleset_schemes=[valid_ruleset_scheme],
        user_defined_operator_schemes=[valid_udo_scheme],
        items=[],
    )
    with pytest.raises(
        Invalid,
        match="TransformationScheme must contain at least "
        "one Transformation",
    ):
        _transformation_scheme_validations(ts)


def test_invalid_item_transformation_scheme(
    valid_udo_scheme, valid_ruleset_scheme
):
    ts = TransformationScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        ruleset_schemes=[valid_ruleset_scheme],
        user_defined_operator_schemes=[valid_udo_scheme],
        items=["invalid"],
    )
    with pytest.raises(
        Invalid,
        match="TransformationScheme must contain Transformation items",
    ):
        _transformation_scheme_validations(ts)
