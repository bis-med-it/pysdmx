import httpx

from pysdmx.api.fmr import AsyncRegistryClient, DataflowDetails, RegistryClient
from pysdmx.model import Component, Components, DataflowInfo, Organisation


def check_dataflow_info(
    mock,
    fmr: RegistryClient,
    schema_query,
    schema_body,
    dataflow_query,
    dataflow_body,
    hca_query,
    hca_body,
):
    """get_schema() should return a schema."""
    route1 = mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    route2 = mock.get(dataflow_query).mock(
        return_value=httpx.Response(200, content=dataflow_body)
    )
    route3 = mock.get(schema_query).mock(
        return_value=httpx.Response(200, content=schema_body)
    )

    dsi = fmr.get_dataflow_details("BIS.CBS", "CBS", "1.0")

    assert route1.called
    assert route2.called
    assert route3.called
    __check_dsi(dsi)


def check_dataflow_info_no_version(
    mock,
    fmr: RegistryClient,
    schema_query,
    schema_body,
    dataflow_query_no_version,
    dataflow_body,
    hca_query,
    hca_body,
):
    """get_schema() should return a schema."""
    route1 = mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    route2 = mock.get(schema_query).mock(
        return_value=httpx.Response(200, content=schema_body)
    )
    route3 = mock.get(dataflow_query_no_version).mock(
        return_value=httpx.Response(200, content=dataflow_body)
    )

    dsi = fmr.get_dataflow_details("BIS.CBS", "CBS")

    assert route1.called
    assert route2.called
    assert route3.called
    __check_dsi(dsi)


def check_core_dataflow_info(
    mock,
    fmr: RegistryClient,
    dataflow_query,
    dataflow_body,
):
    """get_schema() should return a schema."""
    route = mock.get(dataflow_query).mock(
        return_value=httpx.Response(200, content=dataflow_body)
    )

    dsi = fmr.get_dataflow_details(
        "BIS.CBS", "CBS", "1.0", DataflowDetails.CORE
    )

    assert route.called
    __check_core_dsi(dsi)


def check_dataflow_info_with_provs(
    mock,
    fmr: RegistryClient,
    dataflow_query,
    dataflow_body,
):
    """get_schema() should return a schema."""
    route = mock.get(dataflow_query).mock(
        return_value=httpx.Response(200, content=dataflow_body)
    )

    dsi = fmr.get_dataflow_details(
        "BIS.CBS", "CBS", "1.0", DataflowDetails.PROVIDERS
    )

    assert route.called
    __check_dsi_and_providers(dsi)


def check_dataflow_info_with_schema(
    mock,
    fmr: RegistryClient,
    schema_query,
    schema_body,
    dataflow_query,
    dataflow_body,
    hca_query,
    hca_body,
):
    """get_schema() should return a schema."""
    route1 = mock.get(schema_query).mock(
        return_value=httpx.Response(200, content=schema_body)
    )
    route2 = mock.get(dataflow_query).mock(
        return_value=httpx.Response(200, content=dataflow_body)
    )
    route3 = mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )

    dsi = fmr.get_dataflow_details(
        "BIS.CBS", "CBS", "1.0", DataflowDetails.SCHEMA
    )

    assert route1.called
    assert route2.called
    assert route3.called
    __check_dsi_and_schema(dsi)


async def check_async_dataflow_info(
    mock,
    fmr: AsyncRegistryClient,
    schema_query,
    schema_body,
    dataflow_query,
    dataflow_body,
    hca_query,
    hca_body,
):
    """get_schema() should return a schema."""
    route1 = mock.get(hca_query).mock(
        return_value=httpx.Response(200, content=hca_body)
    )
    route2 = mock.get(dataflow_query).mock(
        return_value=httpx.Response(200, content=dataflow_body)
    )
    route3 = mock.get(schema_query).mock(
        return_value=httpx.Response(200, content=schema_body)
    )

    dsi = await fmr.get_dataflow_details("BIS.CBS", "CBS", "1.0")

    assert route1.called
    assert route2.called
    assert route3.called
    __check_dsi(dsi)


async def check_async_core_dataflow_info(
    mock,
    fmr: AsyncRegistryClient,
    dataflow_query,
    dataflow_body,
):
    """get_schema() should return a schema."""
    route = mock.get(dataflow_query).mock(
        return_value=httpx.Response(200, content=dataflow_body)
    )

    dsi = await fmr.get_dataflow_details(
        "BIS.CBS", "CBS", "1.0", DataflowDetails.CORE
    )

    assert route.called
    __check_core_dsi(dsi)


def __check_dsi(dsi):
    assert isinstance(dsi, DataflowInfo)
    assert isinstance(dsi.agency, Organisation)
    assert dsi.agency.id == "BIS.CBS"
    assert dsi.id == "CBS"
    assert dsi.name == "Consolidated Banking Statistics"
    assert dsi.description == "This dataflow is associated to the BIS_CBS DSD."
    assert dsi.version == "1.0"
    assert len(dsi.providers) == 33
    for p in dsi.providers:
        assert isinstance(p, Organisation)
        assert p.id is not None
        assert p.name is not None
    assert dsi.end_period is None
    assert dsi.start_period is None
    assert dsi.obs_count is None
    assert dsi.series_count is None
    assert dsi.last_updated is None

    assert isinstance(dsi.components, Components)
    assert len(dsi.components) == 24
    for comp in dsi.components:
        assert isinstance(comp, Component)
        assert comp.id is not None
        assert comp.name is not None


def __check_core_dsi(dsi):
    assert isinstance(dsi, DataflowInfo)
    assert isinstance(dsi.agency, Organisation)
    assert dsi.agency.id == "BIS.CBS"
    assert dsi.id == "CBS"
    assert dsi.name == "Consolidated Banking Statistics"
    assert dsi.description == "This dataflow is associated to the BIS_CBS DSD."
    assert dsi.dsd_ref == (
        "urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure="
        "BIS:BIS_CBS(1.0)"
    )
    assert dsi.version == "1.0"
    assert len(dsi.providers) == 0
    assert dsi.end_period is None
    assert dsi.start_period is None
    assert dsi.obs_count is None
    assert dsi.series_count is None
    assert dsi.last_updated is None
    assert dsi.components is None


def __check_dsi_and_providers(dsi):
    assert isinstance(dsi, DataflowInfo)
    assert isinstance(dsi.agency, Organisation)
    assert dsi.agency.id == "BIS.CBS"
    assert dsi.id == "CBS"
    assert dsi.name == "Consolidated Banking Statistics"
    assert dsi.description == "This dataflow is associated to the BIS_CBS DSD."
    assert dsi.version == "1.0"
    assert len(dsi.providers) == 33
    for p in dsi.providers:
        assert isinstance(p, Organisation)
        assert p.id is not None
        assert p.name is not None
    assert dsi.end_period is None
    assert dsi.start_period is None
    assert dsi.obs_count is None
    assert dsi.series_count is None
    assert dsi.last_updated is None
    assert dsi.components is None


def __check_dsi_and_schema(dsi):
    assert isinstance(dsi, DataflowInfo)
    assert isinstance(dsi.agency, Organisation)
    assert dsi.agency.id == "BIS.CBS"
    assert dsi.id == "CBS"
    assert dsi.name == "Consolidated Banking Statistics"
    assert dsi.description == "This dataflow is associated to the BIS_CBS DSD."
    assert dsi.version == "1.0"
    assert len(dsi.providers) == 0
    assert dsi.end_period is None
    assert dsi.start_period is None
    assert dsi.obs_count is None
    assert dsi.series_count is None
    assert dsi.last_updated is None

    assert isinstance(dsi.components, Components)
    assert len(dsi.components) == 24
    for comp in dsi.components:
        assert isinstance(comp, Component)
        assert comp.id is not None
        assert comp.name is not None
