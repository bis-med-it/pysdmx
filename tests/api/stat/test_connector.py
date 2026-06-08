from io import BytesIO

import httpx
import pytest

from pysdmx.api.qb import ApiVersion, DataFormat, StructureFormat
from pysdmx.api.stat import StatConnector, StatEndpoints
from pysdmx.errors import Invalid, NotFound
from pysdmx.io import read_sdmx
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
    assert "dimensionAtObservation=AllDimensions" in requested_url


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


def test_dataflow_builds_oecd_url(respx_mock, client, structure_xml):
    route = respx_mock.get(
        url__startswith=f"{client._svc._api_endpoint}/structure/dataflow/"
    ).mock(return_value=httpx.Response(200, content=structure_xml))

    with pytest.raises(NotFound, match="Dataflow not found"):
        client.dataflow("OECD.SDD.TPS", "DSD_G20_PRICES@DF_G20_PRICES", "1.0")

    url = str(route.calls.last.request.url)
    assert "/structure/dataflow/OECD.SDD.TPS/" in url
    assert "DSD_G20_PRICES" in url
    assert "DF_G20_PRICES" in url
    assert "references=descendants" in url


def test_dataset_with_filters(
    respx_mock, client, struct_url, data_url, structure_xml, data_csv
):
    respx_mock.get(url__startswith=struct_url).mock(
        return_value=httpx.Response(200, content=structure_xml)
    )
    data_route = respx_mock.get(url__startswith=data_url).mock(
        return_value=httpx.Response(200, content=data_csv)
    )

    client.dataset(
        "BIS", "WEBSTATS_DER_DATAFLOW", "1.0", filters={"FREQ": "A"}
    )

    url = str(data_route.calls.last.request.url)
    assert "c%5B" not in url  # not the (OECD-ignored) c[] component filter
    assert "/WEBSTATS_DER_DATAFLOW/1.0/A." in url  # FREQ=A is key position 1


def test_dataset_key_and_filters_conflict(client):
    with pytest.raises(Invalid, match="not both"):
        client.dataset(
            "BIS",
            "WEBSTATS_DER_DATAFLOW",
            "1.0",
            key="A",
            filters={"FREQ": "A"},
        )


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
    path = "tests/api/stat/samples/oecd_g20_prices_structure.xml"
    with open(path, "rb") as f:
        return f.read()


@pytest.fixture
def oecd_data():
    with open("tests/api/stat/samples/oecd_g20_prices_data.csv", "rb") as f:
        return f.read()


def test_oecd_real_dataflow(respx_mock, oecd_client, oecd_structure):
    ep = oecd_client._svc._api_endpoint
    spath = f"{ep}/structure/dataflow/OECD.SDD.TPS/DSD_G20_PRICES"
    respx_mock.get(url__startswith=spath).mock(
        return_value=httpx.Response(200, content=oecd_structure)
    )

    flow = oecd_client.dataflow(
        "OECD.SDD.TPS", "DSD_G20_PRICES@DF_G20_PRICES", "1.0"
    )

    assert flow.short_urn == (
        "Dataflow=OECD.SDD.TPS:DSD_G20_PRICES@DF_G20_PRICES(1.0)"
    )
    assert flow.components is not None
    assert "REF_AREA" in [d.id for d in flow.components.dimensions]


def test_oecd_real_schema(respx_mock, oecd_client, oecd_structure):
    ep = oecd_client._svc._api_endpoint
    spath = f"{ep}/structure/dataflow/OECD.SDD.TPS/DSD_G20_PRICES"
    respx_mock.get(url__startswith=spath).mock(
        return_value=httpx.Response(200, content=oecd_structure)
    )

    schema = oecd_client.schema(
        "OECD.SDD.TPS", "DSD_G20_PRICES@DF_G20_PRICES", "1.0"
    )

    assert schema.short_urn == (
        "Dataflow=OECD.SDD.TPS:DSD_G20_PRICES@DF_G20_PRICES(1.0)"
    )
    assert len(schema.components) == 15


def test_oecd_real_dataset(respx_mock, oecd_client, oecd_structure, oecd_data):
    ep = oecd_client._svc._api_endpoint
    spath = f"{ep}/structure/dataflow/OECD.SDD.TPS/DSD_G20_PRICES"
    dpath = f"{ep}/data/dataflow/OECD.SDD.TPS/DSD_G20_PRICES"
    respx_mock.get(url__startswith=spath).mock(
        return_value=httpx.Response(200, content=oecd_structure)
    )
    respx_mock.get(url__startswith=dpath).mock(
        return_value=httpx.Response(200, content=oecd_data)
    )

    ds = oecd_client.dataset(
        "OECD.SDD.TPS",
        "DSD_G20_PRICES@DF_G20_PRICES",
        "1.0",
        key="CHN.A.N.CPI.PA._T.N.GY",
    )

    assert isinstance(ds.structure, Schema)
    assert len(ds.data) == 41
    assert sorted(ds.data["REF_AREA"].unique()) == ["CHN"]
