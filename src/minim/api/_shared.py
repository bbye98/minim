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
    """
    Abstract base class for OAuth 2.0-based API clients.
    """

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
    _ENV_VAR_PREFIX: str = ...
    AUTH_URL: str = ...
    BASE_URL: str = ...
    TOKEN_URL: str = ...
    SCOPES: Any = ...

    def __init__(
        self,
        *,
        flow: str,
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
        user_identifier: str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        flow : `str`, keyword-only
            OAuth 2.0 authorization flow.

            .. container::

               **Valid values**:

               * :code:`"auth_code"` — Authorization Code Flow.
               * :code:`"pkce"` — Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` — Client Credentials Flow.
               * :code:`"implicit"` — Implicit Grant Flow.

        client_id : `str`, keyword-only, optional
            Client ID. Must be provided unless it is set as a system
            environment variable or stored in Minim's local token
            storage.

        client_secret : `str`, keyword-only, optional
            Client secret. Required for the Authorization Code, Client
            Credentials, and Resource Owner Password Credential flows.
            Must be provided unless it is set as a system environment
            variable or stored in Minim's local token storage.

        redirect_uri : `str`, keyword-only, optional
            Redirect URI. Required for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            the host is not :code:`127.0.0.1` or :code:`localhost`,
            redirect handling is not available.

        scopes : `str` or `Collection[str]`, keyword-only, optional
            Authorization scopes the client requests to access user
            resources.

            .. seealso::

               :meth:`get_scopes` — Get a set of scopes to request.

        access_token : `str`, keyword-only, optional
            Access token. If provided or found in Minim's local token
            storage, the authorization process is bypassed. If provided,
            all other relevant keyword arguments should also be
            specified to enable automatic token refresh upon expiration.

        token_type : `str`, keyword-only, default: :code:`"Bearer"`
            Type of the access token.

        refresh_token : `str`, keyword-only, optional
            Refresh token accompanying the access token in
            `access_token`. If not provided, the user will be
            reauthorized via the authorization flow in `flow` when the
            access token expires.

        expiry : `datetime.datetime` or `str`, keyword-only, optional
            Expiry of the access token in `access_token`. If provided as
            a `str`, it must be in ISO 8601 format
            (:code:`%Y-%m-%dT%H:%M:%SZ`).

        backend : `str`, keyword-only, optional
            Backend to handle redirects during the authorization flow.

            .. container::

               **Valid values**:

               * :code:`None` — Manually paste the redirect URL into
                 the terminal.
               * :code:`"http.server"` — Simple HTTP server.
               * :code:`"playwright"` — Playwright Firefox browser.

        browser : `bool`, keyword-only, default: :code:`False`
            Specifies whether to automatically open the authorization
            URL in the default web browser for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            :code:`False`, the authorization URL is printed to the
            terminal.

        persist : `bool`, keyword-only, default: :code:`True`
            Specifies whether to enable Minim's local token storage for
            this client. If :code:`True`, newly acquired access tokens
            and related information are stored. If :code:`False`, the
            client will not retrieve or store access tokens.

        user_identifier : `str`, keyword-only, optional
            Unique identifier for the user account to log into for all
            authorization flows but the Client Credentials flow. Used
            when :code:`persist=True` to distinguish between multiple
            user accounts for the same client ID and authorization flow.

            If provided, it is used to locate existing access tokens in
            Minim's local token storage, where the key is a SHA-256 hash
            of the client ID, authorization flow, and user identifier.
            For newly acquired tokens, the user identifier is
            incorporated into the storage key.

            If not provided, the last accessed account for the specified
            authorization flow in `flow` is selected if it exists in
            local storage. Otherwise, a new entry is created using a
            hash of the client ID, authorization flow, and an available
            user identifier (e.g., user ID).

            The keyword :code:`"new"` is reserved and cannot be used as
            an identifier, but may be specified to authorize an
            additional account for the same client ID and authorization
            flow.
        """
        self._client = httpx.Client(base_url=self.BASE_URL)

        # If a client ID is not provided, try to retrieve it and its
        # corresponding client secret from environment variables
        if client_id is None:
            client_id = os.environ.get(f"{self._ENV_VAR_PREFIX}_CLIENT_ID")
            client_secret = os.environ.get(
                f"{self._ENV_VAR_PREFIX}_CLIENT_SECRET"
            )

        # Ensure `flow` and `client_id` are not empty/null
        if not (flow and client_id):
            raise ValueError(
                "At a minimum, a client ID and an authorization flow "
                "must be provided via the `client_id` and `flow` "
                "arguments, respectively."
            )

        # Assign unique account identifier based on client ID,
        # authorization flow, and optionally, a user identifier
        if flow == "client_credentials":
            self._account_identifier = hashlib.sha256(
                f"{client_id}:{flow}".encode()
            ).hexdigest()
        elif user_identifier:
            if user_identifier == "new":
                user_identifier = None
                self._account_identifier = None
            else:
                self._account_identifier = hashlib.sha256(
                    f"{client_id}:{flow}:{user_identifier}".encode()
                ).hexdigest()
        else:
            self._account_identifier = f"last_{flow}"
        self._user_identifier = user_identifier

        # If an access token is not provided, try to retrieve it from
        # local token storage
        if (
            not access_token
            and persist
            and (accounts := config.get(self._API_NAME))
            and (account := accounts.get(self._account_identifier))
        ):
            access_token = account.get("access_token")

            # If a stored access token is found, assume all other
            # pertinent information was written correctly by Minim and
            # is also available
            if access_token:
                client_id = account.get("client_id")
                client_secret = account.get("client_secret")
                scopes = account.get("scopes", set())
                redirect_uri = account.get("redirect_uri")
                token_type = account.get("token_type")
                refresh_token = account.get("refresh_token")
                expiry = account.get("expiry")

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
            self._obtain_access_token()

    @property
    def _API_NAME(self) -> str:
        """
        Fully qualified name of the API client class.
        """
        return f"{(cls := self.__class__).__module__}.{cls.__qualname__}"

    @classmethod
    @abstractmethod
    def get_scopes(cls, *args, **kwargs) -> set[str]:
        """
        Retrieve a set of authorization scopes.

        Parameters
        ----------
        *args : `tuple[Any]`
            Positional arguments to be defined by subclasses.

        **kwargs : `dict[str, Any]`
            Keyword arguments to be defined by subclasses.

        Returns
        -------
        scopes : `set[str]`
            Authorization scopes.
        """
        ...

    def close(self) -> None:
        """
        Terminate the HTTP client session.
        """
        self._client.close()

    def set_access_token(
        self,
        access_token: str,
        /,
        token_type: str = "Bearer",
        *,
        refresh_token: str | None = None,
        expiry: str | datetime | None = None,
    ) -> None:
        """
        Set or update the access token and related information.

        .. note::

           Calling this method replaces all existing values with the
           provided arguments. Parameters not provided explicitly will
           be overwritten by their default values.

        .. important::

           If the access token was acquired via a different
           authorization flow or client, call :meth:`set_flow` first to
           ensure that all other relevant parameters are set correctly.

        Parameters
        ----------
        access_token : `str`, positional-only
            Access token.

        token_type : `str`, default: :code:`"Bearer"`
            Type of the access token.

        refresh_token : `str`, keyword-only, optional
            Refresh token accompanying the access token in
            `access_token`. If not provided, the user will be
            reauthorized when the access token expires.

        expiry : `datetime.datetime` or `str`, keyword-only, optional
            Expiry of the access token in `access_token`. If provided
            as a `str`, it must be in ISO 8601 format
            (:code:`%Y-%m-%dT%H:%M:%SZ`).
        """
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
        """
        Set or update the authorization flow and related parameters.

        .. note::

           Calling this method replaces all existing values with the
           provided arguments. Parameters not provided explicitly will
           be overwritten by their default values.

        Parameters
        ----------
        flow : `str`, keyword-only
            OAuth 2.0 authorization flow.

            .. container::

               **Valid values**:

               * :code:`"auth_code"` — Authorization Code Flow.
               * :code:`"pkce"` — Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` — Client Credentials Flow.
               * :code:`"implicit"` — Implicit Grant Flow.

        client_id : `str`, keyword-only, optional
            Client ID. Must be provided unless it is set as a system
            environment variable or stored in Minim's local token
            storage.

        client_secret : `str`, keyword-only, optional
            Client secret. Required for the Authorization Code, Client
            Credentials, and Resource Owner Password Credential flows.
            Must be provided unless it is set as a system environment
            variable or stored in Minim's local token storage.

        redirect_uri : `str`, keyword-only, optional
            Redirect URI. Required for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            the host is not :code:`127.0.0.1` or :code:`localhost`,
            redirect handling is not available.

        scopes : `str` or `Collection[str]`, keyword-only, optional
            Authorization scopes the client requests to access user
            resources.

            .. seealso::

               :meth:`get_scopes` — Get a set of scopes to request.

        backend : `str`, keyword-only, optional
            Backend to handle redirects during the authorization flow.

            .. container::

               **Valid values**:

               * :code:`None` — Manually paste the redirect URL into
                 the terminal.
               * :code:`"http.server"` — Simple HTTP server.
               * :code:`"playwright"` — Playwright Firefox browser.

        browser : `bool`, keyword-only, default: :code:`False`
            Specifies whether to automatically open the authorization
            URL in the default web browser for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            :code:`False`, the authorization URL is printed to the
            terminal.

        persist : `bool`, keyword-only, default: :code:`True`
            Specifies whether to enable Minim's local token storage for
            this client. If :code:`True`, newly acquired access tokens
            and related information are stored. If :code:`False`, the
            client will not retrieve or store access tokens.

        """
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
        if (
            flow in {"auth_code", "client_credentials", "password"}
            and not client_secret
        ):
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

    def _get_authorization_code(self, code_challenge: str | None = None) -> str:
        """
        Get the authorization code for the Authorization Code and
        Authorization Code with PKCE flows.

        Parameters
        ----------
        code_challenge : `str`, optional
            Code challenge derived from the code verifier for the
            Authorization Code with PKCE flow.

        Returns
        -------
        code : `str`
            Authorization code.
        """
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
        """
        Handle redirects during the authorization flow.

        Parameters
        ----------
        auth_url : `str`
            Authorization URL to visit.

        part : `str`
            Part of the redirect URL to extract the authorization
            response from.

            **Valid values**: :code:`"query"` or :code:`"fragment"`.

        Returns
        -------
        queries : `dict[str, int or str]`
            Parsed key-value pairs from the specified part of the
            redirect URL.
        """
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
                while True:
                    redirect_url = page.evaluate("window.location.href")
                    if redirect_url.startswith(self._redirect_uri):
                        break
                    time.sleep(0.1)
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

    def _obtain_access_token(self, flow: str | None = None) -> None:
        """
        Get and set a new access token via the specified or current
        authorization flow.

        Parameters
        ----------
        flow : `str`, optional
            Authorization flow. If not provided, the current
            authorization flow in :attr:`_flow` is used.

            .. container::

               **Valid values**:

               * :code:`"auth_code"` — Authorization Code Flow.
               * :code:`"pkce"` — Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` — Client Credentials Flow.
               * :code:`"implicit"` — Implicit Grant Flow.
               * :code:`"refresh_token"` — Refresh Token Flow.
        """
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
                    "scope": " ".join(self._scopes),
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
            data = {
                "grant_type": "authorization_code",
                "redirect_uri": self._redirect_uri,
            }
            if flow == "pkce":
                data["client_id"] = self._client_id
                data["code_verifier"] = code_verifier = secrets.token_urlsafe(
                    96
                )
                data["code"] = self._get_authorization_code(
                    base64.urlsafe_b64encode(
                        hashlib.sha256(code_verifier.encode()).digest()
                    )
                    .decode()
                    .rstrip("=")
                )
            else:
                data["code"] = self._get_authorization_code()
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
                resp_json = httpx.post(self.TOKEN_URL, data=data).json()

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
            accounts = config.get(self._API_NAME)
            if not isinstance(accounts, dict):
                config[self._API_NAME] = accounts = {}
            if flow != "client_credentials":
                if not self._user_identifier:
                    self._resolve_user_identifier()
                self._account_identifier = hashlib.sha256(
                    f"{self._client_id}:{flow}:{self._user_identifier}".encode()
                ).hexdigest()
            accounts[self._account_identifier] = accounts[
                f"last_{self._flow}"
            ] = {
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

    def _refresh_access_token(self) -> None:
        """
        Refresh the access token.
        """
        self._obtain_access_token(
            "refresh_token" if self._refresh_token else self._flow
        )

    def _require_scope(
        self, endpoint_method: str, scopes: str | Collection[str]
    ) -> None:
        """
        Ensure that the required authorization scopes for an endpoint
        method are granted.

        Parameters
        ----------
        endpoint_method : `str`
            Name of the endpoint method.

        scopes : `str` or `Collection[str]`
            Required authorization scopes.
        """
        if isinstance(scopes, str):
            if scopes not in self._scopes:
                raise RuntimeError(
                    f"{self._API_NAME}.{endpoint_method}() requires the "
                    f"'{scopes}' scope."
                )
        else:
            for scope in scopes:
                self._require_scope(endpoint_method, scope)

    @abstractmethod
    def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """
        Make an HTTP request to an API endpoint.

        Parameters
        ----------
        method : `str`
            HTTP method.

        endpoint : `str`
            API endpoint.

        **kwargs : `dict[str, Any]`
            Additional arguments to pass to
            :meth:`httpx.Client.request`.

        Returns
        -------
        response : `httpx.Response`
            HTTP response.
        """
        ...

    @abstractmethod
    def _resolve_user_identifier(self) -> None:
        """
        Resolve and assign a user identifier for the current account.
        """
        ...
