from datetime import datetime

import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.io.format import Format
from pysdmx.model import (
    Codelist,
    Component,
    Components,
    DataType,
    Hierarchy,
    Role,
    Schema,
)


def check_schema(
    mock,
    fmr: RegistryClient,
    query,
    hca_query,
    body,
    hca_body,
    is_fusion: bool = False,
):
    """get_schema() should return a schema."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    vc = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0")

    assert len(mock.calls) == 2  # We fetch hierarchies too in this case
    if is_fusion:
        assert (
            mock.calls[0].request.headers["Accept"] == Format.FUSION_JSON.value
        )
    else:
        assert (
            mock.calls[0].request.headers["Accept"]
            == Format.STRUCTURE_SDMX_JSON_2_0_0.value
        )

    assert isinstance(vc, Schema)
    assert vc.agency == "BIS.CBS"
    assert vc.id == "CBS"
    assert vc.version == "1.0"
    assert vc.context == "dataflow"
    assert len(vc.artefacts) == 24
    assert isinstance(vc.generated, datetime)
    assert isinstance(vc.components, Components)
    assert len(vc.components) == 24
    for comp in vc.components:
        assert isinstance(comp, Component)
        assert comp.id is not None
        assert comp.name is not None
        assert comp.concept is not None
        assert comp.concept.id is not None
        assert comp.id == comp.concept.id
        assert comp.required is not None
        assert comp.role is not None
        assert comp.dtype is not None
    assert vc.groups is not None
    assert len(vc.groups) == 1
    grp = vc.groups[0]
    assert grp.id == "Sibling"
    assert grp.dimensions == [
        "L_MEASURE",
        "L_REP_CTY",
        "CBS_BANK_TYPE",
        "CBS_BASIS",
        "L_POSITION",
        "L_INSTR",
        "REM_MATURITY",
        "CURR_TYPE_BOOK",
        "L_CP_SECTOR",
        "L_CP_COUNTRY",
    ]


def check_no_td(mock, fmr: RegistryClient, query, hca_query, body, hca_body):
    """Not having a time dimension works fine."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    vc = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0")

    assert isinstance(vc, Schema)
    assert vc.agency == "BIS.CBS"
    assert vc.id == "CBS"
    assert vc.version == "1.0"
    assert vc.context == "dataflow"
    assert len(vc.components) == 23
    for comp in vc.components:
        assert comp.id != "TIME_PERIOD"


def check_schema_from_pra(
    mock, fmr: RegistryClient, query, hca_query, body, hca_body
):
    """get_schema() using PA should return a schema."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    vc = fmr.get_schema("provisionagreement", "BIS.CBS", "CBS_BIS_GR2", "1.0")

    assert isinstance(vc, Schema)
    assert vc.agency == "BIS.CBS"
    assert vc.id == "CBS_BIS_GR2"
    assert vc.version == "1.0"
    assert vc.context == "provisionagreement"
    assert len(vc.artefacts) == 27
    assert isinstance(vc.generated, datetime)
    assert isinstance(vc.components, Components)
    assert len(vc.components) == 24
    for comp in vc.components:
        assert isinstance(comp, Component)
        assert comp.id is not None
        assert comp.name is not None


async def check_coded_components(
    mock, fmr: AsyncRegistryClient, query, hca_query, body, hca_body
):
    """Components have the expected number of codes."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))
    exp = {
        "FREQ": 1,
        "L_MEASURE": 1,
        "L_REP_CTY": 32,
        "CBS_BANK_TYPE": 35,
        "CBS_BASIS": 5,
        "L_POSITION": 10,
        "L_INSTR": 12,
        "REM_MATURITY": 6,
        "CURR_TYPE_BOOK": 3,
        "L_CP_SECTOR": 10,
        "L_CP_COUNTRY": 245,
        "DECIMALS": 1,
        "UNIT_MEASURE": 1,
        "UNIT_MULT": 1,
        "TIME_FORMAT": 19,
        "COLLECTION": 1,
        "ORG_VISIBILITY": 5,
        "OBS_STATUS": 13,
        "OBS_CONF": 3,
        "AVAILABILITY": 20,
    }

    vc = await fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0")

    count = 0
    for comp in vc.components:
        if comp.id in exp:
            assert len(comp.enumeration) == exp.get(comp.id)
            assert comp.enumeration.id is not None
            assert comp.enumeration.agency == "BIS"
            assert comp.enumeration.version == "1.0"
            assert comp.enumeration.name is not None
            assert (
                comp.enumeration.sdmx_type == "valuelist"
                if comp.id == "AVAILABILITY"
                else "codelist"
            )
            assert comp.enum_ref is not None
            assert ".codelist." in comp.enum_ref
            count += 1
        else:
            assert not comp.enumeration
    assert count == len(exp.keys())


async def check_coded_pra_components(
    mock, fmr: AsyncRegistryClient, query, hca_query, body, hca_body
):
    """Components have the expected number of codes."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))
    exp = {
        "FREQ": 1,
        "L_MEASURE": 1,
        "L_REP_CTY": 1,
        "CBS_BANK_TYPE": 35,
        "CBS_BASIS": 5,
        "L_POSITION": 10,
        "L_INSTR": 12,
        "REM_MATURITY": 6,
        "CURR_TYPE_BOOK": 3,
        "L_CP_SECTOR": 10,
        "L_CP_COUNTRY": 245,
        "DECIMALS": 1,
        "UNIT_MEASURE": 1,
        "UNIT_MULT": 1,
        "TIME_FORMAT": 19,
        "COLLECTION": 1,
        "ORG_VISIBILITY": 5,
        "OBS_STATUS": 16,
        "OBS_CONF": 3,
        "AVAILABILITY": 20,
    }

    vc = await fmr.get_schema(
        "provisionagreement", "BIS.CBS", "CBS_BIS_GR2", "1.0"
    )

    count = 0
    for comp in vc.components:
        print(comp.id)
        if comp.id in exp:
            assert len(comp.enumeration) == exp.get(comp.id)
            assert comp.enumeration.id is not None
            assert comp.enumeration.agency == "BIS"
            assert comp.enumeration.version == "1.0"
            assert comp.enumeration.name is not None
            assert comp.enumeration.sdmx_type == "codelist"
            count += 1
        else:
            assert not comp.enumeration
    assert count == len(exp.keys())


def check_unconstrained_coded_components(
    mock,
    fmr: RegistryClient,
    no_const_query,
    hca_query,
    no_const_body,
    hca_body,
):
    """Components have the expected number of codes."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(no_const_query).mock(
        return_value=httpx.Response(200, content=no_const_body)
    )

    exp = {
        "FREQ": 8,
        "L_MEASURE": 5,
        "L_REP_CTY": 426,
        "CBS_BANK_TYPE": 426,
        "CBS_BASIS": 7,
        "L_POSITION": 16,
        "L_INSTR": 19,
        "REM_MATURITY": 28,
        "CURR_TYPE_BOOK": 324,
        "L_CP_SECTOR": 20,
        "L_CP_COUNTRY": 426,
        "DECIMALS": 17,
        "UNIT_MEASURE": 324,
        "UNIT_MULT": 10,
        "TIME_FORMAT": 19,
        "COLLECTION": 10,
        "ORG_VISIBILITY": 5,
        "OBS_STATUS": 13,
        "OBS_CONF": 5,
        "AVAILABILITY": 20,
    }
    vc = fmr.get_schema("datastructure", "BIS", "BIS_CBS", "1.0")

    for comp in vc.components:
        if comp.id in exp:
            assert len(comp.enumeration) == exp[comp.id]
        else:
            assert comp.enumeration is None


async def check_core_local_repr_async(
    mock,
    fmr: AsyncRegistryClient,
    no_const_query,
    hca_query,
    no_const_body,
    hca_body,
):
    """Components have the expected representation (local or core)."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(no_const_query).mock(
        return_value=httpx.Response(200, content=no_const_body)
    )

    schema = await fmr.get_schema(
        "datastructure",
        "BIS",
        "BIS_CBS",
        "1.0",
    )

    freq = schema.components["FREQ"]

    assert isinstance(freq, Component)
    assert len(freq.enumeration) == 8
    assert freq.dtype == DataType.STRING


def check_core_local_repr(
    mock,
    fmr: RegistryClient,
    no_const_query,
    hca_query,
    no_const_body,
    hca_body,
):
    """Components have the expected representation (local or core)."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(no_const_query).mock(
        return_value=httpx.Response(200, content=no_const_body)
    )

    schema = fmr.get_schema(
        "datastructure",
        "BIS",
        "BIS_CBS",
        "1.0",
    ).components
    freq = schema["FREQ"]
    title = schema["TITLE_GRP"]
    unit_mult = schema["UNIT_MULT"]
    obs_value = schema["OBS_VALUE"]

    assert isinstance(freq, Component)
    assert len(freq.enumeration) == 8
    assert freq.dtype == DataType.STRING
    assert freq.facets.min_length == 1
    assert freq.facets.max_length == 1

    assert isinstance(title, Component)
    assert not title.enumeration
    assert title.dtype == DataType.STRING
    assert title.facets is None

    assert isinstance(unit_mult, Component)
    assert unit_mult.dtype == DataType.INTEGER
    assert len(unit_mult.enumeration) == 10
    assert unit_mult.facets.min_length == 1
    assert unit_mult.facets.max_length == 2
    assert unit_mult.facets.min_value == -15
    assert unit_mult.facets.max_value == 15

    assert isinstance(obs_value, Component)
    assert obs_value.dtype == DataType.DOUBLE
    assert obs_value.enumeration is None
    assert obs_value.facets.start_value == 0.0
    assert obs_value.facets.end_value == 42.99


def check_roles(mock, fmr: RegistryClient, query, hca_query, body, hca_body):
    """Components have the expected role."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    schema = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0").components

    assert len(schema.dimensions) == 12
    assert len(schema.measures) == 1
    assert len(schema.attributes) == 11

    assert schema["FREQ"] in schema.dimensions
    assert schema["OBS_VALUE"] in schema.measures
    assert schema["DECIMALS"] in schema.attributes


def check_types(mock, fmr: RegistryClient, query, hca_query, body, hca_body):
    """Components have the expected type."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    schema = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0").components

    for comp in schema:
        if comp.id == "TIME_PERIOD":
            assert comp.dtype == DataType.PERIOD
        elif comp.id == "DECIMALS":
            assert comp.dtype == DataType.BIG_INTEGER
        elif comp.id == "UNIT_MULT":
            assert comp.dtype == DataType.INTEGER
        else:
            assert comp.dtype == DataType.STRING


def check_facets(mock, fmr: RegistryClient, query, hca_query, body, hca_body):
    """Components have the expected facets."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    schema = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0").components

    for comp in schema:
        if comp.id in ["TIME_PERIOD", "OBS_PRE_BREAK", "OBS_STATUS"]:
            assert comp.facets is None
        elif comp.id == "OBS_VALUE":
            assert comp.facets.min_length == 1
            assert comp.facets.max_length == 15
        elif comp.id == "DOUBLE":
            assert comp.facets.min_length == 1
            assert comp.facets.max_length == 2
            assert comp.facets.min_value == -15
            assert comp.facets.max_value == 15
        else:
            assert comp.facets is not None
            assert comp.facets.min_length > 0
            assert comp.facets.max_length <= 200


def check_required(
    mock, fmr: RegistryClient, query, hca_query, body, hca_body
):
    """Components have the expected required flag."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    schema = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0").components

    for comp in schema:
        if comp.id in [
            "ORG_VISIBILITY",
            "OBS_CONF",
            "OBS_PRE_BREAK",
            "TITLE_GRP",
        ]:
            assert comp.required is False
        else:
            assert comp.required is True


def check_attachment_level(
    mock, fmr: RegistryClient, query, hca_query, body, hca_body
):
    """Components have the expected attachment level."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    schema = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0").components

    for comp in schema:
        if comp.id in ["OBS_CONF", "OBS_PRE_BREAK", "OBS_STATUS"]:
            assert comp.attachment_level == "O"
        elif comp.id in ["DECIMALS", "UNIT_MEASURE", "UNIT_MULT"]:
            assert comp.attachment_level == "D"
        elif comp.role == Role.ATTRIBUTE:
            assert comp.attachment_level is not None
            assert len(comp.attachment_level.split(",")) in [10, 11]
        else:
            assert comp.attachment_level is None


def check_description(
    mock, fmr: RegistryClient, query, hca_query, body, hca_body
):
    """Components may have a description."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    schema = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0").components

    for comp in schema:
        if comp.id == "OBS_VALUE":
            assert comp.description == "Description for a measure"
        elif comp.id == "TIME_PERIOD":
            assert comp.description == "Description for a dimension"
        elif comp.id == "UNIT_MEASURE":
            assert comp.description == "Description for an attribute"
        else:
            assert comp.description is None


def check_array_definition(
    mock, fmr: RegistryClient, query, hca_query, body, hca_body
):
    """Array components may have min & max number of items."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    schema = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0").components

    for cmp in schema:
        if cmp.id == "ORG_VISIBILITY":
            assert cmp.array_def is not None
            assert cmp.array_def.min_size == 1
            assert cmp.array_def.max_size == 10
        else:
            assert cmp.array_def is None


def check_no_measure(
    mock, fmr: RegistryClient, query, hca_query, body, hca_body
):
    """get_schema() should return a schema, possibly with no measure."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    vc = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0")

    assert isinstance(vc, Schema)
    assert vc.agency == "BIS.CBS"
    assert vc.id == "CBS"
    assert vc.version == "1.0"
    assert vc.context == "dataflow"
    assert len(vc.artefacts) == 24
    assert isinstance(vc.generated, datetime)
    assert isinstance(vc.components, Components)
    assert len(vc.components) == 20
    assert len(vc.components.measures) == 0


def check_no_attrs(
    mock, fmr: RegistryClient, query, hca_query, body, hca_body
):
    """get_schema() should return a schema, possibly with no attributes."""
    mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    vc = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0")

    assert isinstance(vc, Schema)
    assert vc.agency == "BIS.CBS"
    assert vc.id == "CBS"
    assert vc.version == "1.0"
    assert vc.context == "dataflow"
    assert len(vc.artefacts) == 24
    assert isinstance(vc.generated, datetime)
    assert isinstance(vc.components, Components)
    assert len(vc.components) == 13
    assert len(vc.components.attributes) == 0


def check_hierarchy(
    mock, fmr: RegistryClient, query, query_hca, body, body_hca
):
    """Some components may reference a hierarchy."""
    mock.get(query_hca).mock(
        return_value=httpx.Response(200, content=body_hca)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    vc = fmr.get_schema("dataflow", "BIS", "TEST_DF", "1.0")

    assert isinstance(vc, Schema)
    assert vc.agency == "BIS"
    assert vc.id == "TEST_DF"
    assert vc.version == "1.0"
    assert vc.context == "dataflow"
    assert len(vc.artefacts) == 8
    assert isinstance(vc.generated, datetime)
    assert isinstance(vc.components, Components)
    assert len(vc.components) == 5
    assert len(vc.components.attributes) == 0
    for d in vc.components.dimensions:
        if d.id in ["CONTRACT", "TIME_PERIOD"]:
            assert d.enumeration is None
        elif d.id == "OPTION_TYPE":
            assert isinstance(d.enumeration, Hierarchy)
            assert len(d.enumeration) == 3
            assert d.enumeration.id == "H_OPTION_TYPE"
            assert d.enumeration.operator == (
                "urn:sdmx:org.sdmx.infomodel.transformation."
                "UserDefinedOperator=SDMX:OPS(1.0).SUM"
            )
        else:
            assert isinstance(d.enumeration, Codelist)


def check_hierarchy_pra(
    mock, fmr: RegistryClient, query, query_hca, body, body_hca
):
    """Some components may reference a hierarchy."""
    mock.get(query_hca).mock(
        return_value=httpx.Response(200, content=body_hca)
    )
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    vc = fmr.get_schema("provisionagreement", "BIS.CBS", "CBS_BIS_TEST", "1.0")

    assert isinstance(vc, Schema)
    assert vc.agency == "BIS.CBS"
    assert vc.id == "CBS_BIS_TEST"
    assert vc.version == "1.0"
    assert vc.context == "provisionagreement"
    assert len(vc.artefacts) == 27
    assert isinstance(vc.generated, datetime)
    assert isinstance(vc.components, Components)
    assert len(vc.components) == 24
    assert len(vc.components.attributes) == 11
    for d in vc.components.dimensions:
        if d.id == "TIME_PERIOD":
            assert d.enumeration is None
        elif d.id == "L_CP_COUNTRY":
            assert isinstance(d.enumeration, Hierarchy)
            assert len(d.enumeration) == 251
            assert (
                d.enumeration.id
                == "CBS_CLIENT_HIERARCHIES@COUNTERPARTYCOUNTRY"
            )
            assert d.enumeration.operator == (
                "urn:sdmx:org.sdmx.infomodel.transformation."
                "UserDefinedOperator=SDMX:OPS(1.0).SUM"
            )
        else:
            assert isinstance(d.enumeration, Codelist)
