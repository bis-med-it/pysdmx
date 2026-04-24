import httpx
import pandas as pd
import pytest

from pysdmx.api.dc.pd import PandasConnector
from pysdmx.model import Dataflow, Reference


@pytest.fixture
def host():
    return "https://test.org"


@pytest.fixture
def client(host):
    return PandasConnector(host)


@pytest.fixture
def mock_dataflows(mocker):
    return mocker.patch("pysdmx.api.dc.rest.SdmxConnector.dataflows")


@pytest.fixture
def mock_dataflow(mocker):
    return mocker.patch("pysdmx.api.dc.rest.SdmxConnector.dataflow")


@pytest.fixture
def dataflows():
    df1 = Dataflow("CBS", agency="BIS")
    df2 = Dataflow("LBS", agency="BIS")
    return df1, df2


@pytest.fixture
def dataflow():
    return Dataflow(
        "LBS",
        agency="BIS",
        name="LBS test",
        version="1.42",
        structure="DSD_URN",
    )


@pytest.fixture
def csv_data():
    with open("tests/io/csv/sdmx20/reader/samples/data_v2.csv", "rb") as f:
        return f.read()


@pytest.fixture
def json_availability():
    with open("tests/io/samples/bis_der.json", "rb") as f:
        return f.read()


@pytest.fixture
def query_data(host):
    return (
        f"{host}/data/dataflow/BIS/BIS_DER/1.0"
        "?dimensionAtObservation=AllDimensions"
    )


@pytest.fixture
def query_availability(host):
    return f"{host}/availability/dataflow/BIS/BIS_DER/1.0?references=all"


def test_dataflows(client, mock_dataflows, dataflows):
    mock_dataflows.return_value = dataflows

    flows = client.dataflows()

    assert mock_dataflows.call_count == 1
    assert len(mock_dataflows.call_args.args) == 1
    assert mock_dataflows.call_args.args[0] is None
    assert not mock_dataflows.call_args.kwargs
    assert flows == dataflows


def test_dataflows_search_filter(client, mock_dataflows, dataflows):
    mock_dataflows.return_value = dataflows

    flows = client.dataflows("BS")

    assert mock_dataflows.call_count == 1
    assert len(mock_dataflows.call_args.args) == 1
    assert mock_dataflows.call_args.args[0] == "BS"
    assert not mock_dataflows.call_args.kwargs
    assert flows == dataflows


def test_dataflow(client, mock_dataflow, dataflow):
    mock_dataflow.return_value = dataflow
    ref = Reference("Dataflow", "BIS", "CBS", "1.0")

    flow = client.dataflow(ref)

    assert flow == dataflow


def test_data_query(
    respx_mock,
    client,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(dfref)

    assert isinstance(data, pd.DataFrame)
    assert len(data) == 20  # 20 observations
    assert "STRUCTURE" not in data.columns
    assert "STRUCTURE_ID" not in data.columns
    assert "ACTION" not in data.columns


def test_data_query_no_schema(
    respx_mock,
    client,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(dfref, apply_schema=False)

    assert data["DER_CURR_LEG1"].dtype == "object"


def test_data_query_with_schema(
    respx_mock,
    client,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(dfref)

    assert data["DER_CURR_LEG1"].dtype == "category"


def test_data_query_with_columns_and_index(
    respx_mock,
    client,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(dfref, columns=["OBS_STATUS", "OBS_VALUE"])

    assert len(data.columns) == 4
    assert "OBS_STATUS" in data.columns  # Requested
    assert "OBS_VALUE" in data.columns  # Requested
    assert "SERIES_KEY" in data.columns  # Part of the index
    assert "TIME_PERIOD" in data.columns  # Part of the index


def test_data_query_with_columns_and_skey(
    respx_mock,
    client,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(
        dfref, infer_index=False, columns=["OBS_STATUS", "OBS_VALUE"]
    )

    assert len(data.columns) == 3
    assert "OBS_STATUS" in data.columns  # Requested
    assert "OBS_VALUE" in data.columns  # Requested
    assert "SERIES_KEY" in data.columns  # Inferred series keys


def test_data_query_with_only_requested_columns(
    respx_mock,
    client,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(
        dfref,
        infer_index=False,
        infer_series_keys=False,
        columns=["OBS_STATUS", "OBS_VALUE"],
    )

    assert len(data.columns) == 2
    assert "OBS_STATUS" in data.columns  # Requested
    assert "OBS_VALUE" in data.columns  # Requested


def test_data_query_default_labels(
    respx_mock,
    client,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(dfref)

    assert (data["FREQ"] == "A").all()


def test_data_query_name_labels(
    respx_mock,
    client,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(dfref, labels="name")

    assert (data["FREQ"] == "Annual").all()


def test_data_query_both_labels(
    respx_mock,
    client,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(dfref, labels="both")

    assert (data["FREQ"] == "A: Annual").all()


def test_data_query_with_skeys(
    respx_mock,
    client,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(dfref, infer_index=False)

    assert "SERIES_KEY" in data.columns
    found_keys = sorted(data["SERIES_KEY"].unique())
    assert found_keys == [
        "A.U.A.B.5J.A.1E.A.HKD.TO1.A.A.3.C",
        "A.U.A.B.5J.A.1E.A.HKD.USD.A.A.3.C",
    ]


def test_data_query_no_skeys(
    respx_mock,
    client,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(dfref, infer_index=False, infer_series_keys=False)

    assert "SERIES_KEY" not in data.columns


def test_data_query_with_index(
    respx_mock,
    client,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(dfref)

    expected_indexes = ["SERIES_KEY", "TIME_PERIOD"]
    assert list(data.index.names) == expected_indexes


def test_data_query_no_index(
    respx_mock,
    client,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(dfref, infer_index=False)

    assert data.index.names == [None]


def test_data_query_no_schema_query(respx_mock, client, query_data, csv_data):
    # This test would fail in case we fetch the dataflow as there is no mock
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = Reference("Dataflow", "BIS", "BIS_DER", "1.0")

    data = client.data(
        dfref, infer_index=False, infer_series_keys=False, apply_schema=False
    )

    assert len(data) == 20  # 20 observations
