from typing import Any

import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.io.format import Format
from pysdmx.model import (
    CustomType,
    DataType,
    NamePersonalisation,
    Ruleset,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    VtlCodelistMapping,
    VtlConceptMapping,
    VtlDataflowMapping,
)


def check_transformation_scheme(
    mock, fmr: RegistryClient, query, body, is_fusion: bool = False
):
    """get_vtl_transformation_scheme() returns a transformation scheme."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    ts = fmr.get_vtl_transformation_scheme("TEST", "TEST_TS", "1.0")

    assert len(mock.calls) == 1
    if is_fusion:
        assert (
            mock.calls[0].request.headers["Accept"] == Format.FUSION_JSON.value
        )
    else:
        assert (
            mock.calls[0].request.headers["Accept"]
            == Format.STRUCTURE_SDMX_JSON_2_0_0.value
        )

    __check_response(ts)


async def check_transformation_scheme_async(
    mock, fmr: AsyncRegistryClient, query, body
):
    """get_vtl_transformation_scheme() returns a transformation scheme."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    ts = await fmr.get_vtl_transformation_scheme("TEST", "TEST_TS", "1.0")

    __check_response(ts)


def check_cl_mapping(mock, fmr: RegistryClient, query, body):
    """get_vtl_transformation_scheme() can map a codelist."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    ts = fmr.get_vtl_transformation_scheme("TEST", "TEST_TS", "1.0")

    assert ts.vtl_mapping_scheme is not None
    assert len(ts.vtl_mapping_scheme.items) == 1
    for vm in ts.vtl_mapping_scheme.items:
        assert isinstance(vm, VtlCodelistMapping)
        assert vm.id == "VTLM1"
        assert vm.name == "VTL Mapping #1"
        assert "Codelist=SDMX:CL_FREQ(1.0)" in vm.codelist
        assert vm.codelist_alias == "TEST_DETAIL_VTL"


def check_concept_mapping(mock, fmr: RegistryClient, query, body):
    """get_vtl_transformation_scheme() can map a concept."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    ts = fmr.get_vtl_transformation_scheme("TEST", "TEST_TS", "1.0")

    assert ts.vtl_mapping_scheme is not None
    assert len(ts.vtl_mapping_scheme.items) == 1
    for vm in ts.vtl_mapping_scheme.items:
        assert isinstance(vm, VtlConceptMapping)
        assert vm.id == "VTLM1"
        assert vm.name == "VTL Mapping #1"
        assert "Concept=SDMX:CONCEPTS(1.0).CONF_STATUS" in vm.concept
        assert vm.concept_alias == "OBS_CONF"


def __check_response(resp: Any):
    assert isinstance(resp, TransformationScheme)
    __check_transformations(resp)
    __check_user_defined_operator_scheme(resp)
    __check_name_personalisation_scheme(resp)
    __check_custom_type_scheme(resp)
    __check_ruleset_scheme(resp)
    __check_vtl_mapping_scheme(resp)


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
            assert (
                udo.operator_definition
                == "define operator filter_ds (ds1 dataset, "
                'great_cons string default "1", '
                "less_cons number default 4.0) "
                "returns dataset is ds1[filter Me_1 > "
                "great_cons and Me_2 < less_cons] end operator;"
            )

        else:
            assert udo.id == "AVG"
            assert udo.name == "Average"
            assert (
                udo.operator_definition
                == "define operator filter_ds (ds1 dataset, "
                'great_cons string default "1", '
                "less_cons number default 4.0) "
                "returns dataset is ds1[filter Me_1 > "
                "great_cons and Me_2 < less_cons] end operator;"
            )


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


def __check_ruleset_scheme(ts: TransformationScheme):
    assert len(ts.ruleset_schemes) == 1
    rs = ts.ruleset_schemes[0]
    assert rs.agency == "TEST"
    assert rs.id == "RS1"
    assert rs.name == "Ruleset Scheme #1"
    assert rs.description is None
    assert rs.version == "1.0"
    assert rs.vtl_version == "2.0"
    assert len(rs.items) == 1
    for rule in rs.items:
        assert isinstance(rule, Ruleset)
        assert rule.id == "UNIQUE_SOMETHING"
        assert rule.name == "Datapoint Ruleset UNIQUE_SOMETHING"
        assert (
            rule.ruleset_definition
            == "define datapoint ruleset signValidation "
            "(variable ACCOUNTING_ENTRY as AE, "
            "INT_ACC_ITEM as IAI,FUNCTIONAL_CAT as FC,"
            " INSTR_ASSET as IA, OBS_VALUE as O) "
            'is sign1c: when AE = "C" and IAI = "G" '
            'then O > 0 errorcode "sign1c" errorlevel 1 '
            "end datapoint ruleset;"
        )
        assert rule.ruleset_scope == "variable"
        assert rule.ruleset_type == "datapoint"


def __check_vtl_mapping_scheme(ts: TransformationScheme):
    assert ts.vtl_mapping_scheme is not None
    assert ts.vtl_mapping_scheme.agency == "TEST"
    assert ts.vtl_mapping_scheme.id == "TEST_DETAIL"
    assert ts.vtl_mapping_scheme.name == "VTL Mapping Scheme #1"
    assert ts.vtl_mapping_scheme.description is None
    assert ts.vtl_mapping_scheme.version == "1.0"
    assert len(ts.vtl_mapping_scheme.items) == 1
    for vm in ts.vtl_mapping_scheme.items:
        assert isinstance(vm, VtlDataflowMapping)
        assert vm.id == "VTLM1"
        assert vm.name == "VTL Mapping #1"
        assert vm.dataflow.agency == "TEST"
        assert vm.dataflow.id == "TEST_DETAIL"
        assert vm.dataflow.version == "1.0"
        assert vm.dataflow_alias == "TEST_DETAIL_VTL"
        assert vm.to_vtl_mapping_method is not None
        assert vm.to_vtl_mapping_method.method == "to_test"
        assert vm.to_vtl_mapping_method.to_vtl_sub_space == ["ID"]
        assert vm.from_vtl_mapping_method is not None
        assert vm.from_vtl_mapping_method.method == "from_test"
        assert vm.from_vtl_mapping_method.from_vtl_sub_space == ["ID1", "ID2"]
