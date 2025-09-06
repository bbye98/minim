from abc import ABC, abstractmethod
import base64
from collections.abc import Collection
from datetime import datetime, timedelta
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import secrets
import threading
import time
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse
import webbrowser

import httpx
import yaml

from .. import FOUND, CONFIG_FILE, config

if FOUND["playwright"]:
    from playwright.sync_api import sync_playwright


class _OAuth2RedirectHandler(BaseHTTPRequestHandler):
    """ """

    def do_GET(self):
        """ """
        parsed = urlparse(self.path)
        if parsed.query:
            self.server.response = dict(parse_qsl(parsed.query))
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            status = "denied" if "error" in self.server.response else "granted"
            self.wfile.write(
                f"Access {status}. You may close this page.".encode()
            )
            threading.Thread(target=self.server.shutdown).start()
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = """
<html>
  <body>
    <script>
      const params = new URLSearchParams(window.location.hash.substring(1));
      const query = Array.from(params.entries())
        .map(e => e.join('='))
        .join('&');
      fetch('/callback?' + query)
        .then(response => response.text())
        .then(text => document.body.innerHTML = text);
    </script>
  </body>
</html>
            """
            self.wfile.write(html.encode())

    def log_message(self, *args, **kwargs) -> None:
        """ """
        pass


class _OAuth2API(ABC):
    """ """

    _BACKENDS = {"http.server", "playwright"}
    _FLOWS: set[str] = ...
    _OAUTH_FLOWS_NAMES = {
        "auth_code": "Authorization Code Flow",
        "pkce": "Authorization Code Flow with Proof Key for Code Exchange (PKCE)",
        "client_credentials": "Client Credentials Flow",
        # "device": "Device Authorization Flow",
        "implicit": "Implicit Grant Flow",
        # "password": "Resource Owner Password Credentials Flow"
    }
    _PROVIDER: str = ...
    AUTH_URL: str = ...
    BASE_URL: str = ...
    TOKEN_URL: str = ...
    SCOPES: Any = ...

    def __init__(
        self,
        *,
        flow: str = "client_credentials",
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        scopes: str | Collection[str] = "",
        access_token: str | None = None,
        token_type: str = "Bearer",
        refresh_token: str | None = None,
        expiry: str | datetime | None = None,
        backend: str | None = None,
        browser: bool = False,
        persist: bool = True,
    ) -> None:
        """ """
        self._client = httpx.Client(base_url=self.BASE_URL)

        # If an access token is not provided, try to retrieve it from
        # local token storage
        if not access_token and persist and self._NAME in config:
            section = config[self._NAME]
            access_token = section.get("access_token")

            # If a stored access token is found, assume all other
            # pertinent information was written correctly by Minim and
            # is also available
            if access_token:
                flow = section.get("flow")
                client_id = section.get("client_id")
                client_secret = section.get("client_secret")
                scopes = section.get("scopes", "")
                redirect_uri = section.get("redirect_uri")
                token_type = section.get("token_type")
                refresh_token = section.get("refresh_token")
                expiry = section.get("expiry")

        # Try to retrieve client ID and secret from environment variables
        if client_id is None:
            provider_upper = self._PROVIDER.upper()
            client_id = os.environ.get(f"{provider_upper}_CLIENT_ID")
            if client_secret is None:
                client_secret = os.environ.get(
                    f"{provider_upper}_CLIENT_SECRET"
                )

        # Ensure `flow` and `client_id` have been provided
        if not (flow and client_id):
            raise ValueError(
                "At a minimum, the authorization flow and a client ID "
                "must be provided via the `flow` and `client_id` "
                "arguments, respectively."
            )

        self.set_flow(
            flow,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scopes=scopes,
            backend=backend,
            browser=browser,
            persist=persist,
        )
        if access_token:
            self.set_access_token(
                access_token,
                token_type,
                refresh_token=refresh_token,
                expiry=expiry,
            )
        else:
            self._get_and_set_access_token()

    def _get_and_set_access_token(self, flow: str | None = None) -> None:
        """ """
        if not flow:
            flow = self._flow

        if flow == "refresh_token":
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
            }
            if self._client_secret:
                client_b64 = base64.urlsafe_b64encode(
                    f"{self._client_id}:{self._client_secret}".encode()
                ).decode()
                resp_json = httpx.post(
                    self.TOKEN_URL,
                    data=data,
                    headers={"Authorization": f"Basic {client_b64}"},
                ).json()
            else:
                data["client_id"] = self._client_id
                resp_json = httpx.post(self.TOKEN_URL, data=data).json()
        elif flow == "client_credentials":
            resp_json = httpx.post(
                self.TOKEN_URL,
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "grant_type": "client_credentials",
                },
            ).json()
        elif flow == "implicit":
            params = {
                "client_id": self._client_id,
                "redirect_uri": self._redirect_uri,
                "response_type": "token",
                "scope": " ".join(self._scopes),
                "state": secrets.token_urlsafe(),
            }
            resp_json = self._handle_redirect(
                f"{self.AUTH_URL}?{urlencode(params)}", "fragment"
            )
            if error := resp_json.get("error"):
                raise RuntimeError(f"Authorization failed. Error: {error}")
            if params.get("state") != resp_json.get("state"):
                raise RuntimeError(
                    "Authorization failed due to state mismatch."
                )
        else:  # "auth_code" or "pkce"
            client_b64 = base64.urlsafe_b64encode(
                f"{self._client_id}:{self._client_secret}".encode()
            ).decode()
            data = {
                "grant_type": "authorization_code",
                "redirect_uri": self._redirect_uri,
            }
            if flow == "pkce":
                data["client_id"] = self._client_id
                data["code_verifier"] = secrets.token_urlsafe(96)
                data["code"] = self._get_authorization_code(
                    base64.urlsafe_b64encode(
                        hashlib.sha256(data["code_verifier"].encode()).digest()
                    )
                    .decode()
                    .rstrip("=")
                )
            else:
                data["code"] = self._get_authorization_code()
            resp_json = httpx.post(
                self.TOKEN_URL,
                data=data,
                headers={"Authorization": f"Basic {client_b64}"},
            ).json()

        access_token = resp_json["access_token"]
        token_type = resp_json["token_type"].capitalize()
        if scopes := resp_json.get("scopes"):
            self._scopes = set(scopes.split())
        self.set_access_token(
            access_token,
            token_type,
            refresh_token=resp_json.get(
                "refresh_token", getattr(self, "_refresh_token", None)
            ),
            expiry=datetime.now()
            + timedelta(seconds=int(resp_json["expires_in"])),
        )
        if self._persist:
            config[self._NAME] = {
                "flow": self._flow,
                "client_id": self._client_id,
                "client_secret": self._client_secret or "",
                "redirect_uri": self._redirect_uri or "",
                "scopes": " ".join(sorted(self._scopes)),
                "access_token": access_token,
                "token_type": token_type,
                "refresh_token": self._refresh_token or "",
                "expiry": expiry.strftime("%Y-%m-%dT%H:%M:%SZ")
                if (expiry := getattr(self, "_expiry"))
                else "",
            }
            with CONFIG_FILE.open("w") as f:
                yaml.safe_dump(config, f)

    def _get_authorization_code(self, code_challenge: str | None = None) -> str:
        """ """
        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "response_type": "code",
            "state": secrets.token_urlsafe(),
        }
        if self._scopes:
            params["scope"] = " ".join(self._scopes)
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        queries = self._handle_redirect(
            f"{self.AUTH_URL}?{urlencode(params)}", "query"
        )
        if error := queries.get("error"):
            raise RuntimeError(f"Authorization failed. Error: {error}")
        if params["state"] != queries["state"]:
            raise RuntimeError("Authorization failed due to state mismatch.")
        return queries["code"]

    def _handle_redirect(
        self, auth_url: str, part: str
    ) -> dict[str, int | str]:
        """ """
        if self._backend == "playwright":
            if not FOUND["playwright"]:
                raise RuntimeError(
                    f"The {self._OAUTH_FLOWS_NAMES[self._flow]} with "
                    f"`backend={self._backend!r}` requires the "
                    "`playwright` library, but it could not be found "
                    "or imported."
                )

            with sync_playwright() as playwright:
                browser = playwright.firefox.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()
                with page.expect_request(f"{self._redirect_uri}*", timeout=0):
                    page.goto(auth_url)
                redirect_url = page.evaluate("window.location.href")
                while not redirect_url.startswith(self._redirect_uri):
                    time.sleep(0.1)
                    redirect_url = page.evaluate("window.location.href")
                queries = dict(
                    parse_qsl(
                        getattr(
                            urlparse(redirect_url),
                            part,
                        )
                    )
                )
                context.close()
                browser.close()
        else:
            if self._browser:
                webbrowser.open(auth_url)
            else:
                print(
                    f"To grant Minim access to {self._PROVIDER} data "
                    "and features, open the following link in your web "
                    f"browser:\n\n{auth_url}\n"
                )

            if self._backend == "http.server":
                httpd = HTTPServer(("", self._port), _OAuth2RedirectHandler)
                httpd.serve_forever()
                queries = httpd.response
            else:
                uri = input(
                    "After authorizing Minim to access "
                    f"{self._PROVIDER} on your behalf, copy and paste "
                    f"the URI beginning with '{self._redirect_uri}' "
                    "below.\n\nURI: "
                )
                queries = dict(parse_qsl(urlparse(uri).query))

        return queries

    def _refresh_access_token(self) -> None:
        """ """
        self._get_and_set_access_token(
            "refresh_token" if self._refresh_token else self._flow
        )

    def _require_scope(self, endpoint: str, scope: str) -> None:
        """ """
        if scope not in self._scopes:
            raise RuntimeError(
                f"{self._NAME}.{endpoint}() requires the '{scope}' scope."
            )

    @property
    def _NAME(self) -> str:
        """ """
        return f"{(cls := self.__class__).__module__}.{cls.__qualname__}"

    @classmethod
    @abstractmethod
    def get_scopes(cls, *args, **kwargs) -> set[str]:
        """ """
        ...

    def set_flow(
        self,
        flow: str,
        /,
        *,
        client_id: str,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        scopes: str | Collection[str] = "",
        backend: str | None = None,
        browser: bool = False,
        persist: bool = True,
    ) -> None:
        """ """
        if flow not in self._FLOWS:
            _flows = "', '".join(self._FLOWS)
            raise ValueError(
                f"Invalid authorization flow {flow!r}. "
                f"Valid values: '{_flows}'."
            )
        self._flow = flow
        self._scopes = (
            scopes
            if isinstance(scopes, set)
            else set(scopes.split() if isinstance(scopes, str) else scopes)
        )
        self._client_id = client_id
        if flow in {"auth_code", "client_credentials"} and not client_secret:
            raise ValueError(
                f"The {self._OAUTH_FLOWS_NAMES[flow]} ({flow=}) requires "
                "a client secret via the `client_secret` argument."
            )
        self._client_secret = client_secret
        if flow in {"auth_code", "pkce", "implicit"} and not redirect_uri:
            raise ValueError(
                f"The {self._OAUTH_FLOWS_NAMES[flow]} ({flow=}) requires "
                "a redirect URI via the `redirect_uri` argument."
            )
        self._port = (
            port
            if (port := (parsed := urlparse(redirect_uri)).port)
            else 80
            if parsed.scheme == "http"
            else 443
            if parsed.scheme == "https"
            else None
        )
        self._redirect_uri = redirect_uri
        if backend and backend not in self._BACKENDS:
            _backends = "', '".join(self._BACKENDS)
            raise ValueError(
                f"Invalid backend {backend!r}. Valid values: '{_backends}'."
            )
        self._backend = backend
        self._browser = browser
        self._persist = persist

    def set_access_token(
        self,
        access_token: str,
        /,
        token_type: str = "Bearer",
        *,
        refresh_token: str | None = None,
        expiry: str | datetime | None = None,
    ) -> None:
        """ """
        self._client.headers["Authorization"] = f"{token_type} {access_token}"
        if refresh_token and self._flow in {"client_credentials", "implicit"}:
            raise ValueError(
                f"The {self._OAUTH_FLOWS_NAMES[self._flow]} "
                f"({self._flow=}) does not support refresh tokens, but "
                "one was provided via the `refresh_token` argument."
            )
        self._refresh_token = refresh_token
        self._expiry = (
            datetime.strptime(expiry, "%Y-%m-%dT%H:%M:%SZ")
            if expiry and isinstance(expiry, str)
            else expiry
        )

    def close(self) -> None:
        """ """
        self._client.close()
