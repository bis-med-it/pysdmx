from pathlib import Path

import httpx
import pytest

from pysdmx.api.stat import StatUploader
from pysdmx.errors import (
    InternalError,
    Invalid,
    Unauthorized,
    Unavailable,
)
from pysdmx.io import get_datasets
from pysdmx.model import Code, Codelist

NSI = "https://nsi.test/rest"
TRANSFER = "https://transfer.test"
STRUCT_URL = f"{NSI}/rest/structure"
IMPORT_URL = f"{TRANSFER}/import/sdmxFile"
STATUS_URL = f"{TRANSFER}/status/request"
AUTH_URL = "https://kc.test/protocol/openid-connect/token"

_IO_SAMPLES = Path(__file__).parent.parent.parent / "io" / "samples"
DATA_CSV = _IO_SAMPLES / "data_v1.csv"
STRUCTURE_XML = _IO_SAMPLES / "dataflow_structure_children.xml"


@pytest.fixture
def token():
    return "TKN"


@pytest.fixture
def uploader(token):
    return StatUploader(NSI, TRANSFER, token=token)


@pytest.fixture
def codelist():
    return Codelist(
        id="CL_TEST",
        agency="TEST",
        version="1.0",
        name="Test codelist",
        items=[Code(id="A", name="A")],
    )


@pytest.fixture
def dataset():
    return get_datasets(str(DATA_CSV), str(STRUCTURE_XML), validate=False)[0]


def test_init_stores_endpoints_and_token():
    up = StatUploader("https://nsi.test/rest/", "https://transfer.test/")
    assert up._nsi == "https://nsi.test/rest"  # trailing slash stripped
    assert up._transfer == "https://transfer.test"
    assert up._token is None


def test_submit_structure_posts_sdmx_ml(respx_mock, uploader, codelist):
    route = respx_mock.post(STRUCT_URL).mock(
        return_value=httpx.Response(200, text="structOK")
    )

    result = uploader.submit_structure(codelist)

    assert result == "structOK"
    req = route.calls.last.request
    assert req.headers["Authorization"] == "Bearer TKN"
    assert req.headers["Content-Type"] == (
        "application/vnd.sdmx.structure+xml;version=2.1"
    )
    assert "CL_TEST" in req.content.decode()  # serialized to SDMX-ML


def test_submit_structure_without_token_raises(codelist):
    up = StatUploader(NSI, TRANSFER)  # no token

    with pytest.raises(Unauthorized, match="Missing token"):
        up.submit_structure(codelist)


@pytest.mark.parametrize("status", [401, 403])
def test_submit_structure_rejected_token_raises(
    respx_mock, uploader, codelist, status
):
    respx_mock.post(STRUCT_URL).mock(
        return_value=httpx.Response(status, text="nope")
    )

    with pytest.raises(Unauthorized, match="rejected the token"):
        uploader.submit_structure(codelist)


def test_submit_structure_client_error_raises_invalid(
    respx_mock, uploader, codelist
):
    respx_mock.post(STRUCT_URL).mock(
        return_value=httpx.Response(400, text="bad request")
    )

    with pytest.raises(Invalid):
        uploader.submit_structure(codelist)


def test_submit_structure_server_error_raises_internal(
    respx_mock, uploader, codelist
):
    respx_mock.post(STRUCT_URL).mock(
        return_value=httpx.Response(500, text="boom")
    )

    with pytest.raises(InternalError):
        uploader.submit_structure(codelist)


def test_submit_data_posts_sdmx_csv_and_returns_request_id(
    respx_mock, uploader, dataset
):
    route = respx_mock.post(IMPORT_URL).mock(
        return_value=httpx.Response(200, text="REQ-123")
    )

    request_id = uploader.submit_data(dataset)

    assert request_id == "REQ-123"
    req = route.calls.last.request
    assert req.headers["Authorization"] == "Bearer TKN"
    assert req.headers["Content-Type"] == (
        "application/vnd.sdmx.data+csv;version=2.0.0"
    )
    # SDMX-CSV 2.0 carries the STRUCTURE/STRUCTURE_ID/ACTION columns.
    assert "STRUCTURE" in req.content.decode()


def test_submit_uploads_structure_then_data(
    respx_mock, uploader, codelist, dataset
):
    struct = respx_mock.post(STRUCT_URL).mock(
        return_value=httpx.Response(200, text="structOK")
    )
    data = respx_mock.post(IMPORT_URL).mock(
        return_value=httpx.Response(200, text="REQ-456")
    )

    request_id = uploader.submit(codelist, dataset)

    assert request_id == "REQ-456"  # returns the data request id
    assert struct.called
    assert data.called
    # The structure must be submitted before the data.
    assert [str(c.request.url) for c in respx_mock.calls] == [
        STRUCT_URL,
        IMPORT_URL,
    ]


def test_submission_status_gets_with_auth(respx_mock, uploader):
    route = respx_mock.get(url__startswith=STATUS_URL).mock(
        return_value=httpx.Response(200, text="Completed")
    )

    status = uploader.submission_status("REQ-456")

    assert status == "Completed"
    req = route.calls.last.request
    assert req.headers["Authorization"] == "Bearer TKN"
    assert "id=REQ-456" in str(req.url)


def test_fetch_token_password_grant(respx_mock):
    route = respx_mock.post(AUTH_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "NEW"})
    )

    result = StatUploader.fetch_token(AUTH_URL, "my-client", "user", "secret")

    assert result == "NEW"
    form = route.calls.last.request.content.decode()
    assert "grant_type=password" in form
    assert "client_id=my-client" in form
    assert "username=user" in form


def test_fetch_token_bad_credentials_raises(respx_mock):
    respx_mock.post(AUTH_URL).mock(
        return_value=httpx.Response(401, text="invalid_grant")
    )

    with pytest.raises(Invalid):
        StatUploader.fetch_token(AUTH_URL, "c", "user", "wrong")


def test_submit_structure_unreachable_raises_unavailable(
    respx_mock, uploader, codelist
):
    respx_mock.post(STRUCT_URL).mock(side_effect=httpx.ConnectError("boom"))

    with pytest.raises(Unavailable):
        uploader.submit_structure(codelist)


def test_fetch_token_missing_access_token_raises(respx_mock):
    respx_mock.post(AUTH_URL).mock(
        return_value=httpx.Response(200, json={"error": "invalid_client"})
    )

    with pytest.raises(Invalid, match="token response"):
        StatUploader.fetch_token(AUTH_URL, "c", "user", "pw")


def test_fetch_token_non_json_response_raises(respx_mock):
    respx_mock.post(AUTH_URL).mock(
        return_value=httpx.Response(200, text="<html>oops</html>")
    )

    with pytest.raises(Invalid, match="token response"):
        StatUploader.fetch_token(AUTH_URL, "c", "user", "pw")
