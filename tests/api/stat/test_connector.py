from io import BytesIO
from pathlib import Path

import httpx
import pytest

from pysdmx.api.dc import BasicConnector
from pysdmx.api.qb import ApiVersion, DataFormat, StructureFormat
from pysdmx.api.stat import (
    AsyncStatConnector,
    StatConnector,
    StatEndpoints,
    _df_search_match,
    _df_sort_key,
)
from pysdmx.errors import InternalError, Invalid, NotFound, Unavailable
from pysdmx.io import get_datasets, read_sdmx
from pysdmx.io.format import Format
from pysdmx.io.pd import PandasDataset
from pysdmx.io.writer import write_sdmx
from pysdmx.model import (
    Agency,
    AgencyScheme,
    Categorisation,
    Category,
    CategoryScheme,
    Code,
    Codelist,
    Component,
    Components,
    Concept,
    ConceptScheme,
    Dataflow,
    DataProviderScheme,
    DataStructureDefinition,
    Hierarchy,
    Metadataflow,
    MetadataProviderScheme,
    MetadataProvisionAgreement,
    MetadataStructure,
    MultiRepresentationMap,
    ProvisionAgreement,
    RepresentationMap,
    Role,
    Schema,
    StructureMap,
    TransformationScheme,
)
from pysdmx.model.__base import DataProvider, DataType, MetadataProvider
from pysdmx.model.code import HierarchicalCode
from pysdmx.model.metadata import MetadataComponent

HOST = "https://test.stat"
STRUCT_PREFIX = f"{HOST}/structure"
DATA_PREFIX = f"{HOST}/data/dataflow/OECD.SDD.TPS"

_SAMPLES = Path(__file__).parent / "samples"
OECD_STRUCTURE = _SAMPLES / "oecd_g20_prices_structure.xml"
OECD_DATA = _SAMPLES / "oecd_g20_prices_data.csv"
OECD_FLOW = ("OECD.SDD.TPS", "DSD_G20_PRICES@DF_G20_PRICES", "1.0")
OECD_KEY = "CHN.A.N.CPI.PA._T.N.GY"

_ERROR_CASES = [
    (404, NotFound),
    (400, Invalid),
    (500, InternalError),
    (503, InternalError),
]

_A = "TEST"
_V = "1.0"
_INFO = "urn:sdmx:org.sdmx.infomodel"
_CONCEPT_URN = f"{_INFO}.conceptscheme.Concept=TEST:CS(1.0).OBS_VALUE"
# Full URNs: read_sdmx round-trips these; short URNs would not parse.
_DF_URN = f"{_INFO}.datastructure.Dataflow=TEST:DF(1.0)"
_CAT_URN = f"{_INFO}.categoryscheme.Category=TEST:CATS(1.0).C1"
_DP_URN = f"{_INFO}.base.DataProvider=TEST:DPS(1.0).P1"
_MDF_URN = f"{_INFO}.metadatastructure.Metadataflow=TEST:MDF(1.0)"
_MP_URN = f"{_INFO}.base.MetadataProvider=TEST:MPS(1.0).MP1"
_MSD_URN = f"{_INFO}.metadatastructure.MetadataStructure=TEST:MSD(1.0)"


def _all_structures():
    """One instance of every artefact type StatConnector reads."""
    cu = "urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept=TEST:CS(1.0)."
    concepts = [
        Concept(id="REF_AREA", name="Ref area", urn=cu + "REF_AREA"),
        Concept(id="OBS_VALUE", name="Obs", urn=cu + "OBS_VALUE"),
    ]
    cs = ConceptScheme(
        id="CS", agency=_A, version=_V, name="cs", items=concepts
    )
    cl = Codelist(
        id="CL",
        agency=_A,
        version=_V,
        name="cl",
        items=[Code(id="A", name="A")],
    )
    cat = CategoryScheme(
        id="CATS",
        agency=_A,
        version=_V,
        name="cats",
        items=[Category(id="C1", name="c1")],
    )
    dps = DataProviderScheme(
        id="DPS",
        agency=_A,
        version=_V,
        name="dps",
        items=[DataProvider(id="P1", name="prov")],
    )
    mps = MetadataProviderScheme(
        id="MPS",
        agency=_A,
        version=_V,
        name="mps",
        items=[MetadataProvider(id="MP1", name="mprov")],
    )
    ags = AgencyScheme(
        id="AGENCIES",
        agency=_A,
        version=_V,
        name="ags",
        items=[Agency(id="TEST.SUB", name="Sub agency")],
    )
    components = Components(
        [
            Component(
                id="REF_AREA",
                required=True,
                role=Role.DIMENSION,
                concept=concepts[0],
                local_dtype=DataType.STRING,
            ),
            Component(
                id="OBS_VALUE",
                required=False,
                role=Role.MEASURE,
                concept=concepts[1],
                local_dtype=DataType.DOUBLE,
            ),
        ]
    )
    dsd = DataStructureDefinition(
        id="DSD", agency=_A, version=_V, name="dsd", components=components
    )
    df = Dataflow(id="DF", agency=_A, version=_V, name="df", structure=dsd)
    hier = Hierarchy(
        id="H",
        agency=_A,
        version=_V,
        name="h",
        codes=[
            HierarchicalCode(
                id="A",
                name="A",
                urn="urn:sdmx:org.sdmx.infomodel.codelist.Code=TEST:CL(1.0).A",
            )
        ],
    )
    catn = Categorisation(
        id="CATN",
        agency=_A,
        version=_V,
        name="catn",
        source=_DF_URN,
        target=_CAT_URN,
    )
    pa = ProvisionAgreement(
        id="PA",
        agency=_A,
        version=_V,
        name="pa",
        dataflow=_DF_URN,
        provider=_DP_URN,
    )
    msd = MetadataStructure(
        id="MSD",
        agency=_A,
        version=_V,
        name="msd",
        components=[
            MetadataComponent(id="MC", concept=Concept("MC", urn=_CONCEPT_URN))
        ],
    )
    mdf = Metadataflow(
        id="MDF",
        agency=_A,
        version=_V,
        name="mdf",
        structure=_MSD_URN,
        targets=[_DF_URN],
    )
    mpa = MetadataProvisionAgreement(
        id="MPA",
        agency=_A,
        version=_V,
        name="mpa",
        metadataflow=_MDF_URN,
        metadata_provider=_MP_URN,
    )
    built = [
        cs,
        cl,
        cat,
        dps,
        mps,
        ags,
        dsd,
        df,
        hier,
        catn,
        pa,
        msd,
        mdf,
        mpa,
    ]
    # maps + VTL are impractical to author by hand -> reuse io samples
    io_samples = Path(__file__).parent.parent.parent / "io" / "samples"
    harvested = (
        getattr(read_sdmx(io_samples / "maps.xml"), "structures", []) or []
    )
    vtl = Path(__file__).parent.parent.parent
    vtl = vtl / "io/xml/sdmx21/writer/samples/vtl_complete.xml"
    harvested = list(harvested) + list(
        getattr(read_sdmx(vtl), "structures", []) or []
    )
    return [*built, *harvested]


# Every artefact type shares this one SDMX-JSON structure message.
STRUCT_JSON = write_sdmx(
    _all_structures(), Format.STRUCTURE_SDMX_JSON_2_0_0
).encode()


def _mock(respx_mock, url, content):
    return respx_mock.get(url__startswith=url).mock(
        return_value=httpx.Response(200, content=content)
    )


@pytest.fixture
def client():
    return StatConnector(HOST)


@pytest.fixture
def structs_mock(respx_mock):
    _mock(respx_mock, STRUCT_PREFIX, STRUCT_JSON)
    return respx_mock


# --- Construction ------------------------------------------------------------
def test_init_defaults_to_oecd():
    conn = StatConnector()
    assert conn._svc._api_endpoint == StatEndpoints.OECD.value


def test_init_configures_rest_service(client):
    svc = client._svc
    assert svc._api_endpoint == HOST
    assert svc._api_version == ApiVersion.V2_0_0
    assert svc._data_format == DataFormat.SDMX_CSV_2_0_0
    assert svc._structure_format == StructureFormat.SDMX_ML_2_1


def test_init_accepts_endpoint_enum():
    conn = StatConnector(StatEndpoints.OECD)
    assert conn._svc._api_endpoint == StatEndpoints.OECD.value


def test_is_a_registry_client():
    from pysdmx.api.fmr import RegistryClient

    assert isinstance(StatConnector(HOST), RegistryClient)


def test_stat_endpoints_are_urls():
    assert len(StatEndpoints) >= 6
    for endpoint in StatEndpoints:
        assert endpoint.value.startswith(("http://", "https://"))
    verified = {
        StatEndpoints.OECD,
        StatEndpoints.ILO,
        StatEndpoints.ABS,
        StatEndpoints.PACIFIC,
        StatEndpoints.STATEC,
        StatEndpoints.SIMEL_SV,
    }
    for endpoint in verified:
        assert endpoint.value.endswith("/rest/v2")


# --- Inherited get_* (return FMR model objects) ------------------------------
def test_get_dataflows(client, structs_mock):
    out = client.get_dataflows("TEST")
    assert out
    assert all(isinstance(x, Dataflow) for x in out)


def test_get_data_structures(client, structs_mock):
    out = client.get_data_structures("TEST")
    assert out
    assert all(isinstance(x, DataStructureDefinition) for x in out)


def test_get_codes(client, structs_mock):
    assert isinstance(client.get_codes("TEST", "CL"), Codelist)


def test_get_concepts(client, structs_mock):
    assert isinstance(client.get_concepts("TEST", "CS"), ConceptScheme)


def test_get_categories(client, structs_mock):
    assert isinstance(client.get_categories("TEST", "CATS"), CategoryScheme)


def test_get_categorisation(client, structs_mock):
    assert isinstance(
        client.get_categorisation("TEST", "CATN"), Categorisation
    )


def test_get_provision_agreement(client, structs_mock):
    assert isinstance(
        client.get_provision_agreement("TEST", "PA"), ProvisionAgreement
    )


def test_get_agencies(client, structs_mock):
    assert list(client.get_agencies("TEST"))


def test_get_providers(client, structs_mock):
    assert list(client.get_providers("TEST"))


def test_get_metadata_providers(client, structs_mock):
    assert list(client.get_metadata_providers("TEST"))


def test_get_hierarchy(client, structs_mock):
    assert isinstance(client.get_hierarchy("TEST", "H"), Hierarchy)


def test_get_metadata_structures(client, structs_mock):
    out = client.get_metadata_structures("TEST")
    assert out
    assert all(isinstance(x, MetadataStructure) for x in out)


def test_get_metadataflows(client, structs_mock):
    out = client.get_metadataflows("TEST")
    assert out
    assert all(isinstance(x, Metadataflow) for x in out)


def test_get_metadata_provision_agreement(client, structs_mock):
    assert isinstance(
        client.get_metadata_provision_agreement("TEST", "MPA"),
        MetadataProvisionAgreement,
    )


def test_get_mapping(client, structs_mock):
    assert isinstance(client.get_mapping("TEST", "SM"), StructureMap)


def test_get_code_map(client, structs_mock):
    assert isinstance(
        client.get_code_map("TEST", "RM"),
        (RepresentationMap, MultiRepresentationMap),
    )


def test_get_vtl_transformation_scheme(client, structs_mock):
    assert isinstance(
        client.get_vtl_transformation_scheme("TEST", "TS"),
        TransformationScheme,
    )


def test_get_when_type_absent_raises_not_found(client, respx_mock):
    # a codelist-only message -> get_concepts finds no ConceptScheme
    body = write_sdmx(
        Codelist(
            id="CL",
            agency="A",
            version="1.0",
            name="c",
            items=[Code(id="X", name="x")],
        ),
        Format.STRUCTURE_SDMX_JSON_2_0_0,
    ).encode()
    _mock(respx_mock, STRUCT_PREFIX, body)
    with pytest.raises(NotFound):
        client.get_concepts("A", "MISSING")


def test_get_empty_204_no_content(respx_mock, client):
    # An unknown artefact yields HTTP 204 with an empty body, which is
    # not parseable SDMX: _many returns [] and _one raises NotFound
    # (rather than "Cannot parse input as SDMX").
    respx_mock.get(url__startswith=STRUCT_PREFIX).mock(
        return_value=httpx.Response(204)
    )
    assert client.get_dataflows("TEST") == []
    with pytest.raises(NotFound):
        client.get_codes("TEST", "CL")


# --- Endpoints .Stat does not serve -> Invalid -------------------------------
def test_get_schema_unsupported(client):
    with pytest.raises(Invalid, match="Not available"):
        client.get_schema("dataflow", "A", "DF", "1.0")


def test_get_dataflow_details_unsupported(client):
    with pytest.raises(Invalid, match="Not available"):
        client.get_dataflow_details("A", "DF", "1.0")


def test_get_report_unsupported(client):
    with pytest.raises(Invalid, match="Not available"):
        client.get_report("P", "R", "1.0")


def test_get_reports_unsupported(client):
    with pytest.raises(Invalid, match="Not available"):
        client.get_reports("dataflow", "A", "DF", "1.0")


# --- fetch_data --------------------------------------------------------------
def test_fetch_data_returns_raw_bytes(respx_mock, client):
    data = OECD_DATA.read_bytes()
    route = _mock(respx_mock, DATA_PREFIX, data)
    out = client.fetch_data(*OECD_FLOW)
    assert out == data
    url = str(route.calls.last.request.url)
    assert url.endswith("dimensionAtObservation=AllDimensions")


def test_fetch_data_with_key_in_url(respx_mock, client):
    data = OECD_DATA.read_bytes()
    route = _mock(respx_mock, DATA_PREFIX, data)
    client.fetch_data(*OECD_FLOW, key=OECD_KEY)
    assert f"/1.0/{OECD_KEY}" in str(route.calls.last.request.url)


def test_fetch_data_accept_header(respx_mock, client):
    route = _mock(respx_mock, DATA_PREFIX, OECD_DATA.read_bytes())
    client.fetch_data(*OECD_FLOW)
    assert (
        route.calls.last.request.headers["Accept"]
        == "application/vnd.sdmx.data+csv;version=2.0.0"
    )


# --- fetch_dataset -----------------------------------------------------------
def test_fetch_dataset_returns_pandas_dataset(respx_mock, client):
    structure = OECD_STRUCTURE.read_bytes()
    data = OECD_DATA.read_bytes()
    _mock(respx_mock, STRUCT_PREFIX, structure)
    _mock(respx_mock, DATA_PREFIX, data)
    expected = get_datasets(BytesIO(data), BytesIO(structure), validate=False)[
        0
    ]

    ds = client.fetch_dataset(*OECD_FLOW)

    assert isinstance(ds, PandasDataset)
    assert isinstance(ds.structure, Schema)
    assert ds.data.equals(expected.data)


def test_fetch_dataset_passes_key_to_data(respx_mock, client):
    _mock(respx_mock, STRUCT_PREFIX, OECD_STRUCTURE.read_bytes())
    data_route = _mock(respx_mock, DATA_PREFIX, OECD_DATA.read_bytes())
    client.fetch_dataset(*OECD_FLOW, key=OECD_KEY)
    assert f"/1.0/{OECD_KEY}" in str(data_route.calls.last.request.url)


# --- Error mapping -----------------------------------------------------------
@pytest.mark.parametrize(("status", "error"), _ERROR_CASES)
def test_get_dataflows_error_mapping(respx_mock, client, status, error):
    respx_mock.get(url__startswith=STRUCT_PREFIX).mock(
        return_value=httpx.Response(status, text="boom")
    )
    with pytest.raises(error):
        client.get_dataflows("TEST")


def test_fetch_data_connection_error(respx_mock, client):
    respx_mock.get(url__startswith=DATA_PREFIX).mock(
        side_effect=httpx.ConnectError("boom")
    )
    with pytest.raises(Unavailable):
        client.fetch_data(*OECD_FLOW)


# --- SDMX data-discovery profile (BasicConnector) ----------------------------
def test_dataflows_lists_and_searches(client, structs_mock):
    flows = client.dataflows()
    assert flows
    assert all(isinstance(f, Dataflow) for f in flows)
    assert client.dataflows(search_term=flows[0].id)
    assert client.dataflows(search_term="zzz-no-such-flow") == ()
    # a whitespace-only term is treated as no filter
    assert client.dataflows(search_term="   ") == flows


def test_df_search_match_and_sort():
    df = Dataflow(
        id="DF1",
        agency="A",
        version="1.0",
        name="Prices",
        description="CPI data",
    )
    assert _df_search_match(df, "df1")
    assert _df_search_match(df, "price")
    assert _df_search_match(df, "cpi")
    assert not _df_search_match(df, "zzz")
    bare = Dataflow(id="DF2", agency="A", version="1.0", name="x")
    assert not _df_search_match(bare, "zzz")
    assert _df_sort_key(df) == ("A", "DF1", "1.0")


def test_data_yields_observation_dicts(respx_mock, client):
    _mock(respx_mock, DATA_PREFIX, OECD_DATA.read_bytes())
    df = Dataflow(
        id="DSD_G20_PRICES@DF_G20_PRICES",
        agency="OECD.SDD.TPS",
        version="1.0",
        name="x",
    )
    rows = list(client.data(df))
    assert rows
    assert all(isinstance(r, dict) for r in rows)


def test_dataflow_returns_flow(client, structs_mock):
    obj = Dataflow(id="DF", agency="TEST", version="1.0", name="x")
    assert client.dataflow(obj).id == "DF"
    assert client.dataflow(_DF_URN).id == "DF"
    assert client.dataflow("TEST:DF(1.0)").id == "DF"


def test_dataflow_filters_unsupported(client):
    with pytest.raises(Invalid, match="[Aa]vailability"):
        client.dataflow("TEST:DF(1.0)", filters="FREQ='A'")


def test_is_a_basic_connector(client):
    assert isinstance(client, BasicConnector)


# --- Async connector (AsyncStatConnector) ------------------------------------
@pytest.fixture
def aclient():
    return AsyncStatConnector(HOST)


def test_async_init_is_async_registry_client():
    from pysdmx.api.fmr import AsyncRegistryClient

    conn = AsyncStatConnector(HOST)
    assert isinstance(conn, AsyncRegistryClient)
    assert conn._svc._api_endpoint == HOST


@pytest.mark.asyncio
async def test_async_get_structures(aclient, structs_mock):
    dfs = await aclient.get_dataflows("TEST")
    assert all(isinstance(x, Dataflow) for x in dfs)
    dsds = await aclient.get_data_structures("TEST")
    assert all(isinstance(x, DataStructureDefinition) for x in dsds)
    assert isinstance(await aclient.get_codes("TEST", "CL"), Codelist)
    assert isinstance(await aclient.get_concepts("TEST", "CS"), ConceptScheme)
    assert isinstance(
        await aclient.get_categories("TEST", "CATS"), CategoryScheme
    )
    assert isinstance(
        await aclient.get_categorisation("TEST", "CATN"), Categorisation
    )
    assert isinstance(
        await aclient.get_provision_agreement("TEST", "PA"),
        ProvisionAgreement,
    )
    assert isinstance(await aclient.get_hierarchy("TEST", "H"), Hierarchy)


@pytest.mark.asyncio
async def test_async_get_schemes_and_maps(aclient, structs_mock):
    assert list(await aclient.get_agencies("TEST"))
    assert list(await aclient.get_providers("TEST"))
    assert list(await aclient.get_metadata_providers("TEST"))
    mds = await aclient.get_metadata_structures("TEST")
    assert all(isinstance(x, MetadataStructure) for x in mds)
    mdfs = await aclient.get_metadataflows("TEST")
    assert all(isinstance(x, Metadataflow) for x in mdfs)
    assert isinstance(
        await aclient.get_metadata_provision_agreement("TEST", "MPA"),
        MetadataProvisionAgreement,
    )
    assert isinstance(await aclient.get_mapping("TEST", "SM"), StructureMap)
    assert isinstance(
        await aclient.get_code_map("TEST", "RM"),
        (RepresentationMap, MultiRepresentationMap),
    )
    assert isinstance(
        await aclient.get_vtl_transformation_scheme("TEST", "TS"),
        TransformationScheme,
    )


@pytest.mark.asyncio
async def test_async_get_not_found(aclient, respx_mock):
    body = write_sdmx(
        Codelist(
            id="CL",
            agency="A",
            version="1.0",
            name="c",
            items=[Code(id="X", name="x")],
        ),
        Format.STRUCTURE_SDMX_JSON_2_0_0,
    ).encode()
    _mock(respx_mock, STRUCT_PREFIX, body)
    with pytest.raises(NotFound):
        await aclient.get_concepts("A", "MISSING")


@pytest.mark.asyncio
async def test_async_get_empty_204_no_content(respx_mock, aclient):
    respx_mock.get(url__startswith=STRUCT_PREFIX).mock(
        return_value=httpx.Response(204)
    )
    assert await aclient.get_dataflows("TEST") == []
    with pytest.raises(NotFound):
        await aclient.get_codes("TEST", "CL")


@pytest.mark.parametrize(
    "call",
    [
        lambda c: c.get_schema("dataflow", "A", "DF", "1.0"),
        lambda c: c.get_dataflow_details("A", "DF", "1.0"),
        lambda c: c.get_report("P", "R", "1.0"),
        lambda c: c.get_reports("dataflow", "A", "DF", "1.0"),
    ],
)
@pytest.mark.asyncio
async def test_async_unsupported_raise_invalid(aclient, call):
    with pytest.raises(Invalid, match="Not available"):
        await call(aclient)


@pytest.mark.asyncio
async def test_async_fetch_data(respx_mock, aclient):
    data = OECD_DATA.read_bytes()
    route = _mock(respx_mock, DATA_PREFIX, data)
    out = await aclient.fetch_data(*OECD_FLOW, key=OECD_KEY)
    assert out == data
    assert f"/1.0/{OECD_KEY}" in str(route.calls.last.request.url)


@pytest.mark.asyncio
async def test_async_fetch_dataset(respx_mock, aclient):
    structure = OECD_STRUCTURE.read_bytes()
    data = OECD_DATA.read_bytes()
    _mock(respx_mock, STRUCT_PREFIX, structure)
    _mock(respx_mock, DATA_PREFIX, data)
    ds = await aclient.fetch_dataset(*OECD_FLOW)
    assert isinstance(ds, PandasDataset)
    assert isinstance(ds.structure, Schema)


@pytest.mark.parametrize(("status", "error"), _ERROR_CASES)
@pytest.mark.asyncio
async def test_async_get_dataflows_error_mapping(
    respx_mock, aclient, status, error
):
    respx_mock.get(url__startswith=STRUCT_PREFIX).mock(
        return_value=httpx.Response(status, text="boom")
    )
    with pytest.raises(error):
        await aclient.get_dataflows("TEST")


@pytest.mark.asyncio
async def test_async_fetch_data_connection_error(respx_mock, aclient):
    respx_mock.get(url__startswith=DATA_PREFIX).mock(
        side_effect=httpx.ConnectError("boom")
    )
    with pytest.raises(Unavailable):
        await aclient.fetch_data(*OECD_FLOW)


@pytest.mark.asyncio
async def test_async_dataflows(aclient, structs_mock):
    flows = await aclient.dataflows()
    assert flows
    assert all(isinstance(f, Dataflow) for f in flows)
    assert await aclient.dataflows(search_term=flows[0].id)
    assert await aclient.dataflows(search_term="zzz-no-such-flow") == ()
    assert await aclient.dataflows(search_term="   ") == flows


@pytest.mark.asyncio
async def test_async_data(respx_mock, aclient):
    _mock(respx_mock, DATA_PREFIX, OECD_DATA.read_bytes())
    df = Dataflow(
        id="DSD_G20_PRICES@DF_G20_PRICES",
        agency="OECD.SDD.TPS",
        version="1.0",
        name="x",
    )
    rows = [r async for r in aclient.data(df)]
    assert rows
    assert all(isinstance(r, dict) for r in rows)


@pytest.mark.asyncio
async def test_async_dataflow(aclient, structs_mock):
    obj = Dataflow(id="DF", agency="TEST", version="1.0", name="x")
    assert (await aclient.dataflow(obj)).id == "DF"
    assert (await aclient.dataflow(_DF_URN)).id == "DF"
    assert (await aclient.dataflow("TEST:DF(1.0)")).id == "DF"


@pytest.mark.asyncio
async def test_async_dataflow_filters_unsupported(aclient):
    with pytest.raises(Invalid, match="[Aa]vailability"):
        await aclient.dataflow("TEST:DF(1.0)", filters="FREQ='A'")
