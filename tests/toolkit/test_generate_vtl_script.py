from pathlib import Path

import pytest

from pysdmx.errors import Invalid
from pysdmx.model import (
    Reference,
    Ruleset,
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
)
from pysdmx.toolkit.vtl import generate_vtl_script


@pytest.fixture
def generate_vtl_script_sample():
    with open(
        Path(__file__).parent
        / "samples/generate_vtl_script_sample_objects.vtl",
        "r",
        encoding="utf-8",
    ) as f:
        return f.read()


@pytest.fixture
def generate_vtl_script_sample_with_reference():
    with open(
        Path(__file__).parent
        / "samples/generate_vtl_script_sample_references.vtl",
        "r",
        encoding="utf-8",
    ) as f:
        return f.read()


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
def valid_ts_with_only_references(
    valid_udo,
    valid_ruleset,
    valid_transformation,
    valid_ruleset_scheme_reference,
    valid_udo_scheme_reference,
):
    return TransformationScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        ruleset_schemes=[valid_ruleset_scheme_reference],
        user_defined_operator_schemes=[valid_udo_scheme_reference],
        items=[valid_transformation],
    )


@pytest.fixture
def valid_ts_with_several_references(
    valid_udo,
    valid_ruleset,
    valid_transformation,
    valid_ruleset_scheme_reference,
    valid_udo_scheme_reference,
):
    return TransformationScheme(
        id="id",
        name="name",
        description="description",
        vtl_version="2.0",
        ruleset_schemes=[
            valid_ruleset_scheme_reference,
            valid_ruleset_scheme_reference,
        ],
        user_defined_operator_schemes=[
            valid_udo_scheme_reference,
            valid_udo_scheme_reference,
        ],
        items=[valid_transformation],
    )


def test_generate_vtl_script_model_validation(
    valid_ts, generate_vtl_script_sample
):
    vtl_script = generate_vtl_script(valid_ts)
    assert vtl_script.strip() == generate_vtl_script_sample.strip()


def test_generate_vtl_script_with_reference(
    valid_ts_with_reference, generate_vtl_script_sample
):
    vtl_script = generate_vtl_script(
        valid_ts_with_reference, model_validation=True
    )
    assert vtl_script.strip() == generate_vtl_script_sample.strip()


def test_generate_invalid_vtl():
    ts = TransformationScheme(
        agency="MD",
        id="TS1",
        version="1.0",
        items=[
            Transformation(
                id="id",
                name="name",
                description="description",
                expression="DS_1 @ 1",
                result="DS_r",
                is_persistent=True,
            )
        ],
        vtl_version="2.1",
    )
    with pytest.raises(
        Invalid,
        match="Invalid transformation definition: Not valid VTL Syntax",
    ):
        generate_vtl_script(ts, model_validation=True)


def test_generate_vtl_script_prettify():
    ts = TransformationScheme(
        id="TS1",
        agency="MD",
        version="1.0",
        vtl_version="2.1",
        items=[
            Transformation(
                id="T1",
                result="DS_r",
                is_persistent=True,
                expression="DS_1 + 1",
            )
        ],
    )
    vtl_script = generate_vtl_script(ts, prettyprint=True)
    reference = "DS_r <-\n\tDS_1 + 1;\n"
    assert vtl_script == reference


def test_generate_vtl_script_with_only_reference(
    valid_ts_with_only_references,
    generate_vtl_script_sample_with_reference,
):
    vtl_script = generate_vtl_script(
        valid_ts_with_only_references, model_validation=True
    )
    assert (
        vtl_script.strip() == generate_vtl_script_sample_with_reference.strip()
    )


def test_generate_vtl_script_with_several_references(
    valid_ts_with_several_references,
    generate_vtl_script_sample_with_reference,
):
    vtl_script = generate_vtl_script(valid_ts_with_several_references)
    assert (
        vtl_script.strip() == generate_vtl_script_sample_with_reference.strip()
    )


def test_generate_vtl_script_no_model_validation(
    valid_ts, generate_vtl_script_sample
):
    vtl_script = generate_vtl_script(valid_ts, False)
    assert vtl_script.strip() == generate_vtl_script_sample.strip()
