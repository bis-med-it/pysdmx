from io import BytesIO
from pathlib import Path

import httpx
import pytest

from pysdmx.api.dc.rest import SdmxConnector
from pysdmx.api.qb import ApiVersion, DataFormat, StructureFormat
from pysdmx.api.stat import StatConnector, StatEndpoints
from pysdmx.errors import Invalid, NotFound
from pysdmx.errors import NotImplemented as NotImpl
from pysdmx.io import read_sdmx
from pysdmx.io.pd import PandasDataset
from pysdmx.model import Dataflow, Schema
from pysdmx.model.message import Message

# --- Sample fixture files ----------------------------------------------------
_IO_SAMPLES = Path(__file__).parent.parent.parent / "io" / "samples"
_SAMPLES = Path(__file__).parent / "samples"

BIS_STRUCTURE = _IO_SAMPLES / "dataflow_structure_children.xml"
BIS_DSD_ONLY = _IO_SAMPLES / "datastructure.xml"
BIS_DATA = _IO_SAMPLES / "data_v1.csv"
OECD_STRUCTURE = _SAMPLES / "oecd_g20_prices_structure.xml"
OECD_DATA = _SAMPLES / "oecd_g20_prices_data.csv"

# --- Reference dataflows -----------------------------------------------------
HOST = "https://test.stat"
BIS_FLOW = ("BIS", "WEBSTATS_DER_DATAFLOW", "1.0")
BIS_URN = "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)"
OECD_FLOW = ("OECD.SDD.TPS", "DSD_G20_PRICES@DF_G20_PRICES", "1.0")
OECD_URN = "Dataflow=OECD.SDD.TPS:DSD_G20_PRICES@DF_G20_PRICES(1.0)"


def _mock(respx_mock, url, content):
    """Mock an SDMX-REST GET (matched by URL prefix) with raw bytes."""
    return respx_mock.get(url__startswith=url).mock(
        return_value=httpx.Response(200, content=content)
    )


@pytest.fixture
def client():
    return StatConnector(HOST)


@pytest.fixture
def structure_xml():
    return BIS_STRUCTURE.read_bytes()


@pytest.fixture
def structure_no_flow_xml():
    return BIS_DSD_ONLY.read_bytes()


@pytest.fixture
def data_csv():
    return BIS_DATA.read_bytes()


@pytest.fixture
def struct_url():
    return f"{HOST}/structure/dataflow/BIS/WEBSTATS_DER_DATAFLOW/1.0"


@pytest.fixture
def data_url():
    return f"{HOST}/data/dataflow/BIS/WEBSTATS_DER_DATAFLOW/1.0"


def test_init_defaults_to_oecd():
    conn = StatConnector()
    assert conn._svc._api_endpoint == StatEndpoints.OECD.value


def test_init_configures_rest_service(client):
    svc = client._svc
    assert svc._api_endpoint == HOST
    assert svc._api_version == ApiVersion.V2_0_0
    assert svc._data_format == DataFormat.SDMX_CSV_1_0_0
    assert svc._structure_format == StructureFormat.SDMX_ML_2_1


def test_init_accepts_endpoint_enum():
    conn = StatConnector(StatEndpoints.OECD)
    assert conn._svc._api_endpoint == StatEndpoints.OECD.value


def test_is_a_sdmx_connector(client):
    assert isinstance(client, SdmxConnector)


def test_inherited_json_methods_disabled(client):
    with pytest.raises(NotImpl, match="fetch_"):
        client.dataflow("x")
    with pytest.raises(NotImpl, match="fetch_"):
        client.dataflows()
    with pytest.raises(NotImpl, match="fetch_"):
        client.data("x")


def test_stat_endpoints_are_v2_bases():
    assert len(StatEndpoints) >= 4
    for endpoint in StatEndpoints:
        assert endpoint.value.startswith("https://")
        assert endpoint.value.endswith("/rest/v2")


def test_fetch_dataflow(respx_mock, client, struct_url, structure_xml):
    _mock(respx_mock, struct_url, structure_xml)

    flow = client.fetch_dataflow(*BIS_FLOW)

    assert isinstance(flow, Dataflow)
    assert flow.short_urn == BIS_URN
    # The DSD must be grafted on so `.components` is populated, not None.
    assert flow.components is not None
    assert len(flow.components) == 26
    assert [m.id for m in flow.components.measures] == ["OBS_VALUE"]


def test_fetch_dataflow_not_found(respx_mock, client, structure_no_flow_xml):
    _mock(
        respx_mock,
        f"{client._svc._api_endpoint}/structure/dataflow/",
        structure_no_flow_xml,
    )

    with pytest.raises(NotFound, match="Dataflow not found"):
        client.fetch_dataflow("BIS", "BIS_DER", "1.0")


def test_find_dsd_missing(client):
    msg = Message(structures=[Dataflow("DF", agency="BIS", version="1.0")])

    with pytest.raises(NotFound, match="Data structure not found"):
        client._find_dsd(msg)


def test_fetch_schema(respx_mock, client, struct_url, structure_xml):
    _mock(respx_mock, struct_url, structure_xml)

    schema = client.fetch_schema(*BIS_FLOW)

    assert isinstance(schema, Schema)
    assert schema.short_urn == BIS_URN
    assert len(schema.components) == 26


def test_fetch_dataset(
    respx_mock, client, struct_url, data_url, structure_xml, data_csv
):
    _mock(respx_mock, struct_url, structure_xml)
    _mock(respx_mock, data_url, data_csv)

    ds = client.fetch_dataset(*BIS_FLOW)

    assert isinstance(ds, PandasDataset)
    assert isinstance(ds.structure, Schema)
    assert ds.structure.short_urn == BIS_URN
    assert len(ds.data) == 1000
    assert "DECIMALS" in ds.attributes


def test_fetch_dataset_structure_matches_schema(
    respx_mock, client, struct_url, data_url, structure_xml, data_csv
):
    _mock(respx_mock, struct_url, structure_xml)
    _mock(respx_mock, data_url, data_csv)

    schema = client.fetch_schema(*BIS_FLOW)
    ds = client.fetch_dataset(*BIS_FLOW)

    assert ds.structure.short_urn == schema.short_urn
    assert [c.id for c in ds.structure.components] == [
        c.id for c in schema.components
    ]


def test_fetch_dataset_with_key(
    respx_mock, client, struct_url, data_url, structure_xml, data_csv
):
    _mock(respx_mock, struct_url, structure_xml)
    route = _mock(respx_mock, data_url, data_csv)

    client.fetch_dataset(*BIS_FLOW, key="A.U.A.B.5J")

    url = str(route.calls.last.request.url)
    assert "/WEBSTATS_DER_DATAFLOW/1.0/A.U.A.B.5J" in url
    assert "dimensionAtObservation=AllDimensions" in url


def test_accept_headers(
    respx_mock, client, struct_url, data_url, structure_xml, data_csv
):
    s = _mock(respx_mock, struct_url, structure_xml)
    d = _mock(respx_mock, data_url, data_csv)

    client.fetch_dataset(*BIS_FLOW)

    assert (
        s.calls.last.request.headers["Accept"]
        == "application/vnd.sdmx.structure+xml;version=2.1"
    )
    assert (
        d.calls.last.request.headers["Accept"]
        == "application/vnd.sdmx.data+csv;version=1.0.0"
    )


def test_fetch_dataflow_builds_oecd_url(respx_mock, client, structure_xml):
    route = _mock(
        respx_mock,
        f"{client._svc._api_endpoint}/structure/dataflow/",
        structure_xml,
    )

    with pytest.raises(NotFound, match="Dataflow not found"):
        client.fetch_dataflow(*OECD_FLOW)

    url = str(route.calls.last.request.url)
    assert "/structure/dataflow/OECD.SDD.TPS/" in url
    assert "DSD_G20_PRICES" in url
    assert "DF_G20_PRICES" in url
    assert "references=descendants" in url


def test_fetch_dataset_with_filters(
    respx_mock, client, struct_url, data_url, structure_xml, data_csv
):
    _mock(respx_mock, struct_url, structure_xml)
    route = _mock(respx_mock, data_url, data_csv)

    client.fetch_dataset(*BIS_FLOW, filters={"FREQ": "A"})

    url = str(route.calls.last.request.url)
    assert "c%5B" not in url  # not the (OECD-ignored) c[] component filter
    assert "/WEBSTATS_DER_DATAFLOW/1.0/A." in url  # FREQ=A is key position 1


def test_fetch_dataset_key_and_filters_conflict(client):
    with pytest.raises(Invalid, match="not both"):
        client.fetch_dataset(*BIS_FLOW, key="A", filters={"FREQ": "A"})


def test_build_key(client, structure_xml):
    msg = read_sdmx(BytesIO(structure_xml), validate=False)
    dsd = client._find_dsd(msg)

    key = client._build_key(dsd, {"FREQ": "A", "DER_REP_CTY": "CH"})

    parts = key.split(".")
    assert parts[0] == "A"  # FREQ is the first dimension
    assert "CH" in parts  # DER_REP_CTY filtered
    assert set(parts) <= {"A", "CH", "*"}


def test_build_key_unknown_dimension(client, structure_xml):
    msg = read_sdmx(BytesIO(structure_xml), validate=False)
    dsd = client._find_dsd(msg)

    with pytest.raises(Invalid, match="Unknown dimension"):
        client._build_key(dsd, {"NOT_A_DIM": "X"})


@pytest.fixture
def oecd_client():
    return StatConnector(StatEndpoints.OECD)


@pytest.fixture
def oecd_structure():
    return OECD_STRUCTURE.read_bytes()


@pytest.fixture
def oecd_data():
    return OECD_DATA.read_bytes()


def test_oecd_real_dataflow(respx_mock, oecd_client, oecd_structure):
    ep = oecd_client._svc._api_endpoint
    _mock(respx_mock, f"{ep}/structure/dataflow/OECD.SDD.TPS", oecd_structure)

    flow = oecd_client.fetch_dataflow(*OECD_FLOW)

    assert flow.short_urn == OECD_URN
    assert flow.components is not None
    assert "REF_AREA" in [d.id for d in flow.components.dimensions]


def test_oecd_real_schema(respx_mock, oecd_client, oecd_structure):
    ep = oecd_client._svc._api_endpoint
    _mock(respx_mock, f"{ep}/structure/dataflow/OECD.SDD.TPS", oecd_structure)

    schema = oecd_client.fetch_schema(*OECD_FLOW)

    assert schema.short_urn == OECD_URN
    assert len(schema.components) == 15


def test_oecd_real_dataset(respx_mock, oecd_client, oecd_structure, oecd_data):
    ep = oecd_client._svc._api_endpoint
    _mock(respx_mock, f"{ep}/structure/dataflow/OECD.SDD.TPS", oecd_structure)
    _mock(respx_mock, f"{ep}/data/dataflow/OECD.SDD.TPS", oecd_data)

    ds = oecd_client.fetch_dataset(*OECD_FLOW, key="CHN.A.N.CPI.PA._T.N.GY")

    assert isinstance(ds.structure, Schema)
    assert len(ds.data) == 41
    assert sorted(ds.data["REF_AREA"].unique()) == ["CHN"]


def test_authenticated_read_sends_bearer(
    respx_mock, struct_url, structure_xml
):
    bearer = "TKN"
    conn = StatConnector(HOST, token=bearer)
    route = _mock(respx_mock, struct_url, structure_xml)

    conn.fetch_dataflow(*BIS_FLOW)

    assert (
        route.calls.last.request.headers["Authorization"] == f"Bearer {bearer}"
    )


def test_anonymous_read_has_no_bearer(
    respx_mock, client, struct_url, structure_xml
):
    route = _mock(respx_mock, struct_url, structure_xml)

    client.fetch_dataflow(*BIS_FLOW)

    assert "Authorization" not in route.calls.last.request.headers
