import time

import httpx
import pytest

from pysdmx.api.stat.authentication import (
    SUCCESSFUL_AUTHENTICATION,
    ClientCredentialsAuthentication,
    KeycloakAuthentication,
    KeycloakDeviceAuthentication,
)

AUTHORITY = "https://kc.test/realms/OECD"
TOKEN_URL = f"{AUTHORITY}/protocol/openid-connect/token"
USERINFO_URL = f"{AUTHORITY}/protocol/openid-connect/userinfo"
DEVICE_URL = f"{AUTHORITY}/protocol/openid-connect/auth/device"

ACCESS = "AT"
REFRESH = "RT"

DEVICE_FLOW = {
    "device_code": "DEV",
    "user_code": "UC",
    "verification_uri": "https://kc.test/device",
    "verification_uri_complete": "https://kc.test/device?user_code=UC",
    "interval": 1,
    "expires_in": 600,
}


def _ok(value=ACCESS, expires_in=3600, refresh=None):
    body = {"access_token": value, "expires_in": expires_in}
    if refresh is not None:
        body["refresh_token"] = refresh
    return httpx.Response(200, json=body)


@pytest.fixture
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_: None)


# --- ClientCredentialsAuthentication ---------------------------------------


def test_client_credentials_success(respx_mock):
    route = respx_mock.post(TOKEN_URL).mock(return_value=_ok(refresh=REFRESH))

    auth = ClientCredentialsAuthentication(AUTHORITY, "cid", "secret")

    assert auth.init_status == SUCCESSFUL_AUTHENTICATION
    assert auth.get_token() == "AT"
    assert auth.refresh_token == REFRESH
    # not expired -> get_token returns the cache without re-running the flow
    assert route.call_count == 1
    form = route.calls.last.request.content.decode()
    assert "grant_type=client_credentials" in form
    assert "client_id=cid" in form
    assert "client_secret=secret" in form


def test_client_credentials_error_response(respx_mock):
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(400, text="bad client")
    )

    auth = ClientCredentialsAuthentication(AUTHORITY, "cid", "secret")

    assert auth._access_token is None
    assert "Error code: 400" in auth.init_status
    assert "Bad Request" in auth.init_status
    assert "bad client" in auth.init_status


def test_client_credentials_exception(respx_mock):
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"no": "token"})
    )

    auth = ClientCredentialsAuthentication(AUTHORITY, "cid", "secret")

    assert auth._access_token is None
    assert auth.init_status.startswith("An error occurred: ")


# --- KeycloakAuthentication (password grant) -------------------------------


def test_keycloak_password_success(respx_mock):
    route = respx_mock.post(TOKEN_URL).mock(return_value=_ok())

    auth = KeycloakAuthentication(AUTHORITY, "user", "pw", client_id="app")

    assert auth.init_status == SUCCESSFUL_AUTHENTICATION
    assert auth.get_token() == "AT"
    # no refresh_token in the response -> the property is None
    assert auth.refresh_token is None
    form = route.calls.last.request.content.decode()
    assert "grant_type=password" in form
    assert "username=user" in form
    assert "client_id=app" in form


def test_keycloak_error_unknown_status_has_no_reason_or_body(respx_mock):
    respx_mock.post(TOKEN_URL).mock(return_value=httpx.Response(599))

    auth = KeycloakAuthentication(AUTHORITY, "user", "pw")

    assert auth._access_token is None
    # unknown status -> empty reason phrase and empty body, so neither is
    # appended to the message
    assert auth.init_status == "An error occurred: Error code: 599"


def test_keycloak_password_exception(respx_mock):
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"no": "token"})
    )

    auth = KeycloakAuthentication(AUTHORITY, "user", "pw")

    assert auth._access_token is None
    assert auth.init_status.startswith("An error occurred: ")


# --- KeycloakDeviceAuthentication (device flow) ----------------------------


def test_device_endpoint_error(respx_mock):
    respx_mock.post(DEVICE_URL).mock(
        return_value=httpx.Response(400, text="nope")
    )

    auth = KeycloakDeviceAuthentication(AUTHORITY)

    assert auth._access_token is None
    assert auth.init_status == "An error occurred: 400 nope"


def test_device_success(respx_mock, no_sleep):
    respx_mock.post(DEVICE_URL).mock(
        return_value=httpx.Response(200, json=DEVICE_FLOW)
    )
    respx_mock.post(TOKEN_URL).mock(return_value=_ok(refresh=REFRESH))

    auth = KeycloakDeviceAuthentication(AUTHORITY)

    assert auth.init_status == SUCCESSFUL_AUTHENTICATION
    assert auth.get_token() == "AT"
    assert auth.refresh_token == REFRESH


def test_device_authorization_pending_then_success(respx_mock, no_sleep):
    respx_mock.post(DEVICE_URL).mock(
        return_value=httpx.Response(200, json=DEVICE_FLOW)
    )
    respx_mock.post(TOKEN_URL).mock(
        side_effect=[
            httpx.Response(400, json={"error": "authorization_pending"}),
            _ok(),
        ]
    )

    auth = KeycloakDeviceAuthentication(AUTHORITY)

    assert auth.get_token() == "AT"


def test_device_slow_down_then_success(respx_mock, no_sleep):
    respx_mock.post(DEVICE_URL).mock(
        return_value=httpx.Response(200, json=DEVICE_FLOW)
    )
    respx_mock.post(TOKEN_URL).mock(
        side_effect=[
            httpx.Response(400, json={"error": "slow_down"}),
            _ok(),
        ]
    )

    auth = KeycloakDeviceAuthentication(AUTHORITY)

    assert auth.get_token() == "AT"


def test_device_terminal_error(respx_mock, no_sleep):
    respx_mock.post(DEVICE_URL).mock(
        return_value=httpx.Response(200, json=DEVICE_FLOW)
    )
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(
            400,
            json={"error": "access_denied", "error_description": "Denied"},
        )
    )

    auth = KeycloakDeviceAuthentication(AUTHORITY)

    assert auth._access_token is None
    assert "access_denied" in auth.init_status
    assert "Denied" in auth.init_status


def test_device_expires_before_sign_in(respx_mock, no_sleep):
    flow = {**DEVICE_FLOW, "expires_in": 0}
    respx_mock.post(DEVICE_URL).mock(
        return_value=httpx.Response(200, json=flow)
    )

    auth = KeycloakDeviceAuthentication(AUTHORITY)

    assert auth._access_token is None
    assert auth.init_status.endswith("before the code expired")


def test_device_flow_missing_field_is_caught(respx_mock):
    respx_mock.post(DEVICE_URL).mock(
        return_value=httpx.Response(
            200, json={"user_code": "UC", "device_code": "DEV"}
        )
    )

    auth = KeycloakDeviceAuthentication(AUTHORITY)

    assert auth._access_token is None
    assert auth.init_status.startswith("An error occurred: ")


# --- is_authenticated ------------------------------------------------------


def test_is_authenticated_true(respx_mock):
    respx_mock.post(TOKEN_URL).mock(return_value=_ok())
    respx_mock.get(USERINFO_URL).mock(return_value=httpx.Response(200))

    auth = ClientCredentialsAuthentication(AUTHORITY, "cid", "secret")

    assert auth.is_authenticated() is True


def test_is_authenticated_false_when_rejected(respx_mock):
    respx_mock.post(TOKEN_URL).mock(return_value=_ok())
    respx_mock.get(USERINFO_URL).mock(return_value=httpx.Response(401))

    auth = ClientCredentialsAuthentication(AUTHORITY, "cid", "secret")

    assert auth.is_authenticated() is False


def test_is_authenticated_false_without_token(respx_mock):
    respx_mock.post(TOKEN_URL).mock(return_value=httpx.Response(400))

    auth = ClientCredentialsAuthentication(AUTHORITY, "cid", "secret")

    # no token was ever acquired -> short-circuits without calling userinfo
    assert auth.is_authenticated() is False


def test_is_authenticated_false_on_network_error(respx_mock):
    respx_mock.post(TOKEN_URL).mock(return_value=_ok())
    respx_mock.get(USERINFO_URL).mock(side_effect=httpx.ConnectError("boom"))

    auth = ClientCredentialsAuthentication(AUTHORITY, "cid", "secret")

    assert auth.is_authenticated() is False


# --- get_token expiry handling ---------------------------------------------


def test_get_token_reacquires_when_no_token(respx_mock):
    respx_mock.post(TOKEN_URL).mock(side_effect=[httpx.Response(400), _ok()])

    auth = ClientCredentialsAuthentication(AUTHORITY, "cid", "secret")
    assert auth._access_token is None

    # a missing token forces a fresh acquisition on get_token()
    assert auth.get_token() == "AT"


def test_get_token_reacquires_when_expired(respx_mock):
    respx_mock.post(TOKEN_URL).mock(side_effect=[_ok("AT1"), _ok("AT2")])

    auth = ClientCredentialsAuthentication(AUTHORITY, "cid", "secret")
    assert auth.get_token() == "AT1"

    auth._expiration_time = time.time() - 10  # force the cache to expire

    assert auth.get_token() == "AT2"


def test_get_token_keeps_cache_without_expiry(respx_mock):
    route = respx_mock.post(TOKEN_URL).mock(return_value=_ok())

    auth = ClientCredentialsAuthentication(AUTHORITY, "cid", "secret")
    auth._expiration_time = None  # defensive: never-expiring cached token

    assert auth.get_token() == "AT"
    assert route.call_count == 1
