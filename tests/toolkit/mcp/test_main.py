import pytest

from pysdmx.toolkit.mcp import __main__


@pytest.fixture
def run_calls(mocker):
    return mocker.patch("pysdmx.toolkit.mcp.__main__.mcp.run")


def test_defaults_to_stdio(run_calls):
    __main__.main([])

    run_calls.assert_called_once_with()


def test_stdio_can_be_requested_explicitly(run_calls):
    __main__.main(["--transport", "stdio"])

    run_calls.assert_called_once_with()


def test_http_transport(run_calls):
    __main__.main(["--transport", "http", "--host", "10.0.0.1", "--port", "9"])

    run_calls.assert_called_once_with(
        transport="http", host="10.0.0.1", port=9
    )


def test_http_transport_defaults(run_calls):
    __main__.main(["--transport", "http"])

    run_calls.assert_called_once_with(
        transport="http", host="127.0.0.1", port=8000
    )


def test_rejects_unknown_transport(run_calls):
    with pytest.raises(SystemExit):
        __main__.main(["--transport", "carrier-pigeon"])

    run_calls.assert_not_called()
