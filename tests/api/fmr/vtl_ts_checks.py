from typing import Any

import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import (
    CustomType,
    DataType,
    NamePersonalisation,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
)


def check_transformation_scheme(mock, fmr: RegistryClient, query, body):
    """get_vtl_transformation_scheme() returns a transformation scheme."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    ts = fmr.get_vtl_transformation_scheme("TEST", "TEST_TS", "1.0")

    __check_response(ts)


async def check_transformation_scheme_async(
    mock, fmr: AsyncRegistryClient, query, body
):
    """get_vtl_transformation_scheme() returns a transformation scheme."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    ts = await fmr.get_vtl_transformation_scheme("TEST", "TEST_TS", "1.0")

    __check_response(ts)


def __check_response(resp: Any):
    assert isinstance(resp, TransformationScheme)
    __check_transformations(resp)
    __check_user_defined_operator_scheme(resp)
    __check_name_personalisation_scheme(resp)
    __check_custom_type_scheme(resp)


def __check_transformations(ts: TransformationScheme):
    assert ts.agency == "TEST"
    assert ts.id == "TEST_TS"
    assert ts.version == "1.0"
    assert ts.vtl_version == "2.0"
    assert len(ts.items) == 1
    tr = ts.items[0]
    assert isinstance(tr, Transformation)
    assert tr.id == "STEP_1"
    assert tr.name == "Step 1"
    assert tr.description == "Validation of something in input file"
    assert (
        tr.expression
        == "check_datapoint(TEST_DETAIL_VTL, UNIQUE_SOMETHING invalid)"
    )
    assert tr.result == "CHECK_SOMETHING"
    assert tr.is_persistent is False


def __check_user_defined_operator_scheme(ts: TransformationScheme):
    assert len(ts.user_defined_operator_schemes) == 1
    dos = ts.user_defined_operator_schemes[0]
    assert dos.agency == "SDMX"
    assert dos.id == "OPS"
    assert dos.name == "Operators"
    assert dos.version == "1.0"
    assert dos.vtl_version == "2.0"
    assert "VtlMappingScheme=TEST:TEST_DETAIL(1.0)" in dos.vtl_mapping_scheme
    assert len(dos.ruleset_schemes) == 1
    assert "RulesetScheme=TEST:RS1(1.0)" in dos.ruleset_schemes[0]
    assert len(dos.items) == 2
    for udo in dos.items:
        assert isinstance(udo, UserDefinedOperator)
        if udo.id == "SUM":
            assert udo.name == "Sum"
            assert udo.operator_definition == "sum"
        else:
            assert udo.id == "AVG"
            assert udo.name == "Average"
            assert udo.operator_definition == "avg"


def __check_name_personalisation_scheme(ts: TransformationScheme):
    assert ts.name_personalisation_scheme is not None
    assert ts.name_personalisation_scheme.agency == "BIS.TEST"
    assert ts.name_personalisation_scheme.id == "TEST_NPS"
    assert (
        ts.name_personalisation_scheme.name == "Test for name personalisations"
    )
    assert ts.name_personalisation_scheme.description is None
    assert ts.name_personalisation_scheme.version == "1.0"
    assert ts.name_personalisation_scheme.vtl_version == "2.1"
    assert len(ts.name_personalisation_scheme.items) == 1
    for np in ts.name_personalisation_scheme.items:
        assert isinstance(np, NamePersonalisation)
        assert np.id == "ALDF"
        assert np.name == "Alias for Dataflow"
        assert np.vtl_artefact == "Dataflow"
        assert np.vtl_default_name == "Dataflow"
        assert np.personalised_name == "Dataset"


def __check_custom_type_scheme(ts: TransformationScheme):
    assert ts.custom_type_scheme is not None
    assert ts.custom_type_scheme.agency == "TEST"
    assert ts.custom_type_scheme.id == "TS_CTS"
    assert ts.custom_type_scheme.name == "Test Custom Types"
    assert ts.custom_type_scheme.description is None
    assert ts.custom_type_scheme.version == "1.0"
    assert ts.custom_type_scheme.vtl_version == "2.1"
    assert len(ts.custom_type_scheme.items) == 1
    for ct in ts.custom_type_scheme.items:
        assert isinstance(ct, CustomType)
        assert ct.id == "TITLE"
        assert ct.name == "Title"
        assert ct.vtl_scalar_type == "String"
        assert ct.data_type == DataType.STRING
        assert ct.null_value == "null"
