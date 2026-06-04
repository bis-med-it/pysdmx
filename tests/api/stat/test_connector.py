import httpx
import pytest

from pysdmx.api.qb import ApiVersion, DataFormat, StructureFormat
from pysdmx.api.stat import StatConnector, StatEndpoints
from pysdmx.errors import NotFound
from pysdmx.model import Dataflow, Schema


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


def test_schema(respx_mock, client, struct_url, structure_xml):
    respx_mock.get(url__startswith=struct_url).mock(
        return_value=httpx.Response(200, content=structure_xml)
    )

    schema = client.schema("BIS", "WEBSTATS_DER_DATAFLOW", "1.0")

    assert isinstance(schema, Schema)
    assert schema.short_urn == "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)"
    assert len(schema.components) == 26


@pytest.fixture
def data_csv():
    with open("tests/io/samples/data_v1.csv", "rb") as f:
        return f.read()


@pytest.fixture
def data_url(host):
    return f"{host}/data/dataflow/BIS/WEBSTATS_DER_DATAFLOW/1.0"


def test_dataset(
    respx_mock, client, struct_url, data_url, structure_xml, data_csv
):
    from pysdmx.io.pd import PandasDataset

    respx_mock.get(url__startswith=struct_url).mock(
        return_value=httpx.Response(200, content=structure_xml)
    )
    respx_mock.get(url__startswith=data_url).mock(
        return_value=httpx.Response(200, content=data_csv)
    )

    ds = client.dataset("BIS", "WEBSTATS_DER_DATAFLOW", "1.0")

    assert isinstance(ds, PandasDataset)
    assert isinstance(ds.structure, Schema)
    assert ds.structure.short_urn == "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)"
    assert len(ds.data) == 1000
    assert "DECIMALS" in ds.attributes


def test_dataset_structure_matches_schema(
    respx_mock, client, struct_url, data_url, structure_xml, data_csv
):
    respx_mock.get(url__startswith=struct_url).mock(
        return_value=httpx.Response(200, content=structure_xml)
    )
    respx_mock.get(url__startswith=data_url).mock(
        return_value=httpx.Response(200, content=data_csv)
    )

    schema = client.schema("BIS", "WEBSTATS_DER_DATAFLOW", "1.0")
    ds = client.dataset("BIS", "WEBSTATS_DER_DATAFLOW", "1.0")

    assert ds.structure.short_urn == schema.short_urn
    assert [c.id for c in ds.structure.components] == [
        c.id for c in schema.components
    ]


def test_dataset_with_string_filter(
    respx_mock, client, struct_url, data_url, structure_xml, data_csv
):
    respx_mock.get(url__startswith=struct_url).mock(
        return_value=httpx.Response(200, content=structure_xml)
    )
    data_route = respx_mock.get(url__startswith=data_url).mock(
        return_value=httpx.Response(200, content=data_csv)
    )

    client.dataset("BIS", "WEBSTATS_DER_DATAFLOW", "1.0", filters="FREQ = 'A'")

    requested_url = str(data_route.calls.last.request.url)
    assert "c%5BFREQ%5D=A" in requested_url


def test_dataset_with_key(
    respx_mock, client, struct_url, data_url, structure_xml, data_csv
):
    respx_mock.get(url__startswith=struct_url).mock(
        return_value=httpx.Response(200, content=structure_xml)
    )
    data_route = respx_mock.get(url__startswith=data_url).mock(
        return_value=httpx.Response(200, content=data_csv)
    )

    client.dataset("BIS", "WEBSTATS_DER_DATAFLOW", "1.0", key="A.U.A.B.5J")

    requested_url = str(data_route.calls.last.request.url)
    assert "/WEBSTATS_DER_DATAFLOW/1.0/A.U.A.B.5J" in requested_url


def test_accept_headers(
    respx_mock, client, struct_url, data_url, structure_xml, data_csv
):
    s = respx_mock.get(url__startswith=struct_url).mock(
        return_value=httpx.Response(200, content=structure_xml)
    )
    d = respx_mock.get(url__startswith=data_url).mock(
        return_value=httpx.Response(200, content=data_csv)
    )

    client.dataset("BIS", "WEBSTATS_DER_DATAFLOW", "1.0")

    assert (
        s.calls.last.request.headers["Accept"]
        == "application/vnd.sdmx.structure+xml;version=2.1"
    )
    assert (
        d.calls.last.request.headers["Accept"]
        == "application/vnd.sdmx.data+csv;version=1.0.0"
    )


def test_dataset_with_filter_object(
    respx_mock, client, struct_url, data_url, structure_xml, data_csv
):
    from pysdmx.api.dc.query import Operator, TextFilter

    respx_mock.get(url__startswith=struct_url).mock(
        return_value=httpx.Response(200, content=structure_xml)
    )
    data_route = respx_mock.get(url__startswith=data_url).mock(
        return_value=httpx.Response(200, content=data_csv)
    )

    client.dataset(
        "BIS",
        "WEBSTATS_DER_DATAFLOW",
        "1.0",
        filters=TextFilter("FREQ", Operator.EQUALS, "A"),
    )

    assert "c%5BFREQ%5D=A" in str(data_route.calls.last.request.url)


def test_oecd_shaped_query_url():
    from pysdmx.api.qb import (
        StructureDetail,
        StructureQuery,
        StructureReference,
        StructureType,
    )

    q = StructureQuery(
        StructureType.DATAFLOW,
        "OECD.SDD.TPS",
        "DSD_G20_PRICES@DF_G20_PRICES",
        "1.0",
        detail=StructureDetail.FULL,
        references=StructureReference.DESCENDANTS,
    )
    url = q.get_url(ApiVersion.V2_0_0, True)
    assert url == (
        "/structure/dataflow/OECD.SDD.TPS/"
        "DSD_G20_PRICES@DF_G20_PRICES/1.0?references=descendants"
    )
