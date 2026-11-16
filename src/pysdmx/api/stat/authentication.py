"""OIDC token acquisition for the .Stat Suite APIs.

One class per flow:

- ClientCredentialsAuthentication: non-interactive client-credentials flow,
  for confidential clients (client id + secret with a service account) --
  machine-to-machine, no user involved.
- KeycloakAuthentication: non-interactive resource-owner password grant, for
  users with a local Keycloak password.
- KeycloakDeviceAuthentication: interactive device-code flow (RFC 8628) with
  PKCE; the sign-in happens in any browser, so federated logins (e.g. GitHub)
  work.

All flows take the authority (realm) URL and derive the OIDC endpoints from
it using Keycloak's URL layout ({authority}/protocol/openid-connect/...), so
they work against Keycloak or any provider with the same layout.
"""

import base64
import hashlib
import secrets
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import httpx

SUCCESSFUL_AUTHENTICATION = "Successful authentication"
ERROR_OCCURRED = "An error occurred: "

# Every flow requests these scopes: openid marks the request as OIDC, which
# is what makes the token acceptable to the userinfo endpoint that
# is_authenticated() uses as the live check.
OIDC_SCOPES = "openid profile email"


class Authentication(ABC):
    """Base class for the token-acquisition flows.

    Holds what every flow shares -- the authority (realm) URL, the token
    endpoint derived from it using Keycloak's URL layout, the proxy, the
    token state and the expiry handling; the credentials live in the
    subclasses. Each subclass implements _initialize_token() with one
    specific OAuth flow and sets its own attributes before calling this
    constructor, which runs the flow once; get_token() re-runs it when the
    token is missing or expired.

    After construction, init_status explains how the attempt went;
    is_authenticated() asks the provider whether the token really works.
    """

    def __init__(
        self, authority_url: str, proxy: Optional[str] = None
    ) -> None:
        """Store the realm URL, derive the token endpoint, run the flow."""
        self._authority_url = authority_url.rstrip("/")
        self._token_url = (
            f"{self._authority_url}/protocol/openid-connect/token"
        )
        self._proxy = proxy

        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._creation_time: Optional[float] = None
        self._expiration_time: Optional[float] = None
        self.init_status: Optional[str] = None

        self._initialize_token()

    @abstractmethod
    def _initialize_token(self) -> None:
        """Run the OAuth flow once.

        Implementations must call _store_token() on success, or set
        init_status to an ERROR_OCCURRED message explaining the failure.
        """

    def is_authenticated(self) -> bool:
        """Ask the provider whether the current access token is active.

        Sends the token to the OIDC userinfo endpoint under the authority
        URL, and only an HTTP 200 counts. False when the flow never
        produced a token, the provider rejects it (expired, revoked,
        missing openid scope), or the endpoint cannot be reached.
        """
        if self._access_token is None:
            return False
        userinfo_url = (
            f"{self._authority_url}/protocol/openid-connect/userinfo"
        )
        try:
            response = httpx.get(
                userinfo_url,
                headers={"Authorization": f"Bearer {self._access_token}"},
                proxy=self._proxy,
                timeout=30,
            )
            return response.status_code == 200
        except Exception:
            return False

    @property
    def refresh_token(self) -> Optional[str]:
        """Refresh token from the last flow (None if none was issued)."""
        return self._refresh_token

    def get_token(self) -> Optional[str]:
        """Return a valid access token, or None if acquisition failed.

        Re-runs the flow when the cached token is missing or expired; for
        the interactive device flow that means a new browser sign-in.
        """
        if self._access_token is None or (
            self._expiration_time is not None
            and time.time() >= self._expiration_time
        ):
            self._initialize_token()

        return self._access_token

    def _reset(self) -> None:
        """Clear the token state before a new acquisition attempt."""
        self._access_token = None
        self._refresh_token = None
        self._creation_time = None
        self._expiration_time = None
        self.init_status = None

    def _store_token(
        self,
        access_token: str,
        expires_in: int,
        refresh_token: Optional[str] = None,
    ) -> None:
        """Record a successful acquisition and schedule its expiry."""
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._creation_time = time.time()
        # renew one minute early to never hand out an almost-expired token
        self._expiration_time = time.time() + int(expires_in) - 60
        self.init_status = SUCCESSFUL_AUTHENTICATION

    @staticmethod
    def _error_from_response(response: httpx.Response) -> str:
        """Build a readable init_status message from an error response."""
        message = f"{ERROR_OCCURRED}Error code: {response.status_code}"
        if response.reason_phrase:
            message += f"\nReason: {response.reason_phrase}"
        if response.text:
            message += f"\n{response.text}"
        return message


class ClientCredentialsAuthentication(Authentication):
    """Non-interactive client-credentials flow (machine-to-machine).

    The application authenticates as itself -- no user involved. Requires a
    confidential client: its id, its secret, and a service account holding
    the permissions the API calls will need.
    """

    def __init__(
        self,
        authority_url: str,
        client_id: str,
        client_secret: str,
        proxy: Optional[str] = None,
    ) -> None:
        """Build the flow from the realm URL and the client credentials."""
        self._client_id = client_id
        self._client_secret = client_secret
        super().__init__(authority_url, proxy)

    def _initialize_token(self) -> None:
        self._reset()
        try:
            payload = {
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": OIDC_SCOPES,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = httpx.post(
                self._token_url,
                proxy=self._proxy,
                headers=headers,
                data=payload,
                timeout=30,
            )
            if response.status_code not in {200, 201}:
                self.init_status = self._error_from_response(response)
            else:
                results_json = response.json()
                self._store_token(
                    results_json["access_token"],
                    results_json["expires_in"],
                    results_json.get("refresh_token"),
                )
        except Exception as err:
            self.init_status = f"{ERROR_OCCURRED}{err}"


class KeycloakAuthentication(Authentication):
    """Non-interactive resource-owner password grant.

    Sends a username and password directly to the token endpoint. The user
    needs a local Keycloak password (federated accounts, e.g. GitHub, have
    none) and the client must allow direct access grants. This is a legacy
    grant -- prefer the device or client-credentials flow when possible.
    """

    def __init__(
        self,
        authority_url: str,
        user: str,
        password: str,
        client_id: str = "app",
        client_secret: str = "",
        proxy: Optional[str] = None,
    ) -> None:
        """Build the flow from the realm URL and the user's credentials.

        client_secret stays empty for public clients such as the demo "app".
        """
        self._user = user
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret
        super().__init__(authority_url, proxy)

    def _initialize_token(self) -> None:
        self._reset()
        try:
            payload = {
                "grant_type": "password",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "username": self._user,
                "password": self._password,
                "scope": OIDC_SCOPES,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = httpx.post(
                self._token_url,
                proxy=self._proxy,
                headers=headers,
                data=payload,
                timeout=30,
            )
            if response.status_code not in {200, 201}:
                self.init_status = self._error_from_response(response)
            else:
                results_json = response.json()
                self._store_token(
                    results_json["access_token"],
                    results_json["expires_in"],
                    results_json.get("refresh_token"),
                )
        except Exception as err:
            self.init_status = f"{ERROR_OCCURRED}{err}"


class KeycloakDeviceAuthentication(Authentication):
    """Interactive device-code flow (RFC 8628) with PKCE.

    Prints a verification URL plus a short code, then polls the token
    endpoint until the user finishes signing in from any browser. No
    redirect URI is involved, so it works with federated logins (e.g.
    GitHub) and public clients out of the box.
    """

    def __init__(
        self,
        authority_url: str,
        client_id: str = "app",
        proxy: Optional[str] = None,
    ) -> None:
        """Build the flow from the realm URL."""
        self._client_id = client_id
        super().__init__(authority_url, proxy)

    def _initialize_token(self) -> None:
        self._reset()
        try:
            # Keycloak clients may enforce PKCE, also on the device grant.
            verifier = (
                base64.urlsafe_b64encode(secrets.token_bytes(32))
                .rstrip(b"=")
                .decode()
            )
            challenge = (
                base64.urlsafe_b64encode(
                    hashlib.sha256(verifier.encode()).digest()
                )
                .rstrip(b"=")
                .decode()
            )

            response = httpx.post(
                f"{self._authority_url}/protocol/openid-connect/auth/device",
                data={
                    "client_id": self._client_id,
                    "scope": OIDC_SCOPES,
                    "code_challenge": challenge,
                    "code_challenge_method": "S256",
                },
                proxy=self._proxy,
                timeout=30,
            )
            if response.status_code != 200:
                self.init_status = (
                    f"{ERROR_OCCURRED}{response.status_code} {response.text}"
                )
                return
            flow = response.json()

            uri = flow.get(
                "verification_uri_complete", flow["verification_uri"]
            )
            print(f"\nOpen {uri}", flush=True)
            print(f"and confirm the code {flow['user_code']}.", flush=True)
            print(
                "Waiting for the sign-in to finish in the browser...",
                flush=True,
            )

            self.__poll_for_token(flow, verifier)
        except Exception as err:
            self.init_status = f"{ERROR_OCCURRED}{err}"

    def __poll_for_token(self, flow: Dict[str, Any], verifier: str) -> None:
        """Poll the token endpoint until the sign-in resolves.

        Stops when the sign-in completes, the code expires, or the server
        reports a terminal error.
        """
        interval = int(flow.get("interval", 5))
        deadline = time.time() + int(flow.get("expires_in", 600))
        while time.time() < deadline:
            time.sleep(interval)
            response = httpx.post(
                self._token_url,
                data={
                    "grant_type": (
                        "urn:ietf:params:oauth:grant-type:device_code"
                    ),
                    "device_code": flow["device_code"],
                    "client_id": self._client_id,
                    "code_verifier": verifier,
                },
                proxy=self._proxy,
                timeout=30,
            )
            results_json = response.json()
            if response.status_code in {200, 201}:
                self._store_token(
                    results_json["access_token"],
                    results_json["expires_in"],
                    results_json.get("refresh_token"),
                )
                return
            error = results_json.get("error")
            if error == "slow_down":
                # the server asked to back off (RFC 8628); widen the interval
                interval += 5
            elif error != "authorization_pending":
                self.init_status = (
                    f"{ERROR_OCCURRED}{error} Error description: "
                    f"{results_json.get('error_description')}"
                )
                return
        self.init_status = (
            f"{ERROR_OCCURRED}sign-in not completed before the code expired"
        )
