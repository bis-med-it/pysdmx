import httpx
import pytest

from pysdmx.api.qb import ApiVersion, DataFormat, StructureFormat
from pysdmx.api.stat import StatConnector, StatEndpoints
from pysdmx.errors import NotFound
from pysdmx.model import Dataflow


@pytest.fixture
def host():
    return "https://test.stat"


@pytest.fixture
def client(host):
    return StatConnector(host)


def test_init_defaults_to_oecd():
    conn = StatConnector()
    assert conn._svc._api_endpoint == StatEndpoints.OECD.value


def test_init_configures_rest_service(client):
    svc = client._svc
    assert svc._api_endpoint == "https://test.stat"
    assert svc._api_version == ApiVersion.V2_0_0
    assert svc._data_format == DataFormat.SDMX_CSV_1_0_0
    assert svc._structure_format == StructureFormat.SDMX_ML_2_1


def test_init_accepts_endpoint_enum():
    conn = StatConnector(StatEndpoints.OECD)
    assert conn._svc._api_endpoint == StatEndpoints.OECD.value


@pytest.fixture
def structure_xml():
    with open("tests/io/samples/dataflow_structure_children.xml", "rb") as f:
        return f.read()


@pytest.fixture
def structure_no_flow_xml():
    with open("tests/io/samples/datastructure.xml", "rb") as f:
        return f.read()


@pytest.fixture
def struct_url(host):
    return f"{host}/structure/dataflow/BIS/WEBSTATS_DER_DATAFLOW/1.0"


def test_dataflow(respx_mock, client, struct_url, structure_xml):
    respx_mock.get(url__startswith=struct_url).mock(
        return_value=httpx.Response(200, content=structure_xml)
    )

    flow = client.dataflow("BIS", "WEBSTATS_DER_DATAFLOW", "1.0")

    assert isinstance(flow, Dataflow)
    assert flow.short_urn == "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)"
    # The DSD must be grafted on so `.components` is populated, not None.
    assert flow.components is not None
    assert len(flow.components) == 26
    assert [m.id for m in flow.components.measures] == ["OBS_VALUE"]


def test_dataflow_not_found(respx_mock, client, structure_no_flow_xml):
    respx_mock.get(
        url__startswith=f"{client._svc._api_endpoint}/structure/dataflow/"
    ).mock(return_value=httpx.Response(200, content=structure_no_flow_xml))

    with pytest.raises(NotFound, match="Dataflow not found"):
        client.dataflow("BIS", "BIS_DER", "1.0")


def test_find_dsd_missing(client):
    from pysdmx.model import Dataflow
    from pysdmx.model.message import Message

    msg = Message(structures=[Dataflow("DF", agency="BIS", version="1.0")])

    with pytest.raises(NotFound, match="Data structure not found"):
        client._find_dsd(msg)


def test_stat_endpoints_are_v2_bases():
    assert len(StatEndpoints) >= 4
    for endpoint in StatEndpoints:
        assert endpoint.value.startswith("https://")
        assert endpoint.value.endswith("/rest/v2")
