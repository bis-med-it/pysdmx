from datetime import datetime

import httpx

from pysdmx.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import Component, Components, DataType, Role, Schema


def check_schema(mock, fmr: RegistryClient, query, body):
    """get_schema() should return a schema."""
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
    assert len(vc.components) == 24
    for comp in vc.components:
        assert isinstance(comp, Component)
        assert comp.id is not None
        assert comp.name is not None


async def check_coded_components(mock, fmr: AsyncRegistryClient, query, body):
    """Components have the expected number of codes."""
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
            assert len(comp.codes) == exp.get(comp.id)
            count += 1
        else:
            assert not comp.codes
    assert count == len(exp.keys())


def check_unconstrained_coded_components(
    mock, fmr: RegistryClient, no_const_query, no_const_body
):
    """Components have the expected number of codes."""
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
        assert len(comp.codes) == exp.get(comp.id, 0)


def check_core_local_repr(
    mock,
    fmr: RegistryClient,
    no_const_query,
    no_const_body,
):
    """Components have the expected representation (local or core)."""
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

    assert isinstance(freq, Component)
    assert len(freq.codes) == 8
    assert freq.dtype == DataType.STRING
    assert freq.facets.min_length == 1
    assert freq.facets.max_length == 1

    assert isinstance(title, Component)
    assert len(title.codes) == 0
    assert title.dtype == DataType.STRING
    assert title.facets is None


def check_roles(mock, fmr: RegistryClient, query, body):
    """Components have the expected role."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    schema = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0").components

    assert len(schema.dimensions) == 12
    assert len(schema.measures) == 1
    assert len(schema.attributes) == 11

    assert schema["FREQ"] in schema.dimensions
    assert schema["OBS_VALUE"] in schema.measures
    assert schema["DECIMALS"] in schema.attributes


def check_types(mock, fmr: RegistryClient, query, body):
    """Components have the expected type."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    schema = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0").components

    for comp in schema:
        if comp.id == "TIME_PERIOD":
            assert comp.dtype == DataType.PERIOD
        elif comp.id == "DECIMALS":
            assert comp.dtype == DataType.BIG_INTEGER
        else:
            assert comp.dtype == DataType.STRING


def check_facets(mock, fmr: RegistryClient, query, body):
    """Components have the expected facets."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    schema = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0").components

    for comp in schema:
        if comp.id == "TIME_PERIOD":
            assert comp.facets is None
        elif comp.id == "OBS_VALUE":
            assert comp.facets.min_length == 1
            assert comp.facets.max_length == 15
        elif comp.id == "OBS_PRE_BREAK" or comp.id == "OBS_STATUS":
            assert comp.facets is None
        else:
            assert comp.facets is not None
            assert comp.facets.min_length > 0
            assert comp.facets.max_length <= 200


def check_required(mock, fmr: RegistryClient, query, body):
    """Components have the expected required flag."""
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


def check_attachment_level(mock, fmr: RegistryClient, query, body):
    """Components have the expected attachment level."""
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


def check_description(mock, fmr: RegistryClient, query, body):
    """Components may have a description."""
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


def check_array_definition(mock, fmr: RegistryClient, query, body):
    """Array components may have min & max number of items."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    schema = fmr.get_schema("dataflow", "BIS.CBS", "CBS", "1.0").components

    for cmp in schema:
        if cmp.id == "ORG_VISIBILITY":
            assert cmp.array_def is not None
            assert cmp.array_def.min_size == 1
            assert cmp.array_def.max_size == 10
        else:
            assert cmp.array_def is None


def check_no_measure(mock, fmr: RegistryClient, query, body):
    """get_schema() should return a schema, possibly with no measure."""
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


def check_no_attrs(mock, fmr: RegistryClient, query, body):
    """get_schema() should return a schema, possibly with no attributes."""
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
