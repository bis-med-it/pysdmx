import pytest

from pysdmx.api.dc.pd import PandasConnector
from pysdmx.model import Dataflow


@pytest.fixture
def host():
    return "https://test.org"


@pytest.fixture
def client(host):
    return PandasConnector(host)


@pytest.fixture
def mock_dataflows(mocker):
    # post_to_medal_inbox is called first to upload the file
    return mocker.patch("pysdmx.api.dc.rest.SdmxConnector.dataflows")


@pytest.fixture
def dataflows():
    df1 = Dataflow("CBS", agency="BIS")
    df2 = Dataflow("LBS", agency="BIS")
    return df1, df2


def test_dataflows(client, mock_dataflows, dataflows):
    mock_dataflows.return_value = dataflows

    flows = client.dataflows()

    assert flows == dataflows
