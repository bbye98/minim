from abc import ABC, abstractmethod
import base64
from collections import OrderedDict
from collections.abc import Collection
from datetime import datetime, timedelta, timezone
from functools import wraps
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import ipaddress
import os
import secrets
import ssl
from textwrap import dedent
import threading
import time
from typing import Any, Callable
from urllib.parse import parse_qsl, urlencode, urlparse
import warnings
import webbrowser

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import httpx
import yaml

from .. import FOUND, MINIM_DIR, CONFIG_FILE, config
from . import api_config

if FOUND["playwright"]:
    from playwright.sync_api import sync_playwright


def _copy_docstring(
    source: Callable[..., Any],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Copy the docstring from a function to another function.

    Parameters
    ----------
    source : Callable[..., Any]
        Source function.

    Returns
    -------
    decorator : Callable[[Callable[..., Any]], Callable[..., Any]]
        Decorator that replaces the docstring of the decorated function
        with that of `source`.
    """

    def decorator(destination: Callable[..., Any]) -> Callable[..., Any]:
        destination.__doc__ = source.__doc__
        return destination

    return decorator


class TTLCache:
    """
    Time-to-live (TTL) + least recently used (LRU) cache.
    """

    def __init__(self, max_size: int = 1_024) -> None:
        """ """
        self._store = OrderedDict()
        self._max_size = max_size

    @staticmethod
    def _make_hashable(obj: Any) -> Any:
        """ """
        if isinstance(obj, list):
            return tuple(TTLCache._make_hashable(x) for x in obj)
        if isinstance(obj, dict):
            return tuple(
                sorted((k, TTLCache._make_hashable(v)) for k, v in obj.items())
            )
        if isinstance(obj, set):
            return tuple(sorted(TTLCache._make_hashable(x) for x in obj))
        return obj

    @staticmethod
    def cached_method(
        *, ttl: float
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """ """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapped(
                self: ResourceAPI,
                *args: tuple[Any, ...],
                **kwargs: dict[str, Any],
            ) -> Any:
                cache = getattr(self._client, "_cache")
                if cache is None:
                    return func(self, *args, **kwargs)
                return cache.wrapper(ttl=ttl)(func)(self, *args, **kwargs)

            return wrapped

        return decorator

    def clear(self, func: Callable[..., Any] | None = None, /) -> None:
        """ """
        if func is None:
            self._store.clear()
        else:
            if not callable(func):
                raise ValueError(
                    "`func` must be a method from an API client class."
                )
            func = func.__qualname__
            for key in [k for k in self._store if k[0] == func]:
                del self._store[key]

    def wrapper(
        self, *, ttl: float
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """ """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapped(
                *args: tuple[Any, ...], **kwargs: dict[str, Any]
            ) -> Any:
                key = (
                    func.__qualname__,
                    tuple(self._make_hashable(a) for a in args[1:]),
                    frozenset(kwargs.items()),
                )
                now = time.time()

                if (entry := self._store.get(key)) is not None:
                    value, expiry = entry
                    if expiry is None or expiry > now:
                        self._store.move_to_end(key)
                        return value
                    else:
                        del self._store[key]

                value = func(*args, **kwargs)
                self._store[key] = value, now + ttl
                self._store.move_to_end(key)

                while len(self._store) > self._max_size:
                    self._store.popitem(last=False)

                return value

            return wrapped

        return decorator


class OAuth2RedirectHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for OAuth 2.0 redirect URIs.
    """

    def do_GET(self) -> None:
        """
        Handle a GET request to the redirect URI.
        """
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
            self.wfile.write(
                dedent("""\\
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
                """).encode()
            )

    def log_message(
        self, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> None:
        """
        Silence the HTTP server logging output.

        Parameters
        ----------
        *args : tuple[Any, ...], optional
            Positional arguments to pass to
            :meth:`http.server.BaseHTTPRequestHandler.log_message`.

        **kwargs : dict[str, Any], optional
            Keyword arguments to pass to
            :meth:`http.server.BaseHTTPRequestHandler.log_message`.
        """
        pass


class APIClient(ABC):
    """
    Abstract base class for API clients.
    """

    _API_NAME: str = ...
    _PROVIDER: str = ...
    _QUAL_NAME: str = ...
    #: Base URL for API endpoints.
    BASE_URL: str = ...

    def __init__(self, *, cache: bool = True) -> None:
        self._cache = TTLCache() if cache else None

    @abstractmethod
    def _request(
        self, method: str, endpoint: str, /, **kwargs: dict[str, Any]
    ) -> httpx.Response:
        """
        Make an HTTP request to an API endpoint.

        Parameters
        ----------
        method : str, positional-only
            HTTP method.

        endpoint : str, positional-only
            API endpoint.

        **kwargs : dict[str, Any]
            Keyword arguments to pass to :meth:`httpx.Client.request`.

        Returns
        -------
        response : httpx.Response
            HTTP response.
        """
        ...

    @staticmethod
    def _validate_number(
        name: str,
        value: int,
        data_type: type,
        lower_bound: int | None = None,
        upper_bound: int | None = None,
    ) -> None:
        """
        Validate an integer value.

        Parameters
        ----------
        name : str
            Variable name.

        value : int
            Integer value.

        data_type : type
            Data type.

        lower_bound : int, optional
            Lower bound, inclusive.

        upper_bound : int, optional
            Upper bound, inclusive.
        """
        if lower_bound is None:
            if upper_bound is None:
                emsg_suffix = ""
            else:
                emsg_suffix = f" less than {upper_bound}, inclusive"
        else:
            if upper_bound is None:
                emsg_suffix = f" greater than {lower_bound}, inclusive"
            else:
                emsg_suffix = (
                    f" between {lower_bound} and {upper_bound}, inclusive"
                )
        if not (
            isinstance(value, data_type)
            and (lower_bound is None or value >= lower_bound)
            and (upper_bound is None or value <= upper_bound)
        ):
            raise ValueError(f"`{name}` must be an int{emsg_suffix}.")

    @staticmethod
    def _validate_type(name: str, value: Any, data_type: type) -> None:
        """
        Validate the data type of a variable.

        Parameters
        ----------
        name : str
            Variable name.

        value : Any
            Variable value.

        data_type : type
            Allowed data type.
        """
        if not isinstance(value, data_type):
            raise ValueError(
                f"`{name}` must be {data_type.__name__}, not "
                f"{type(value).__name__}."
            )


class OAuth2APIClient(APIClient):
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
    _ENV_VAR_PREFIX: str = ...
    _SCOPES: Any = ...
    #: Authorization endpoint.
    AUTH_URL: str = ...
    #: Token endpoint.
    TOKEN_URL: str = ...

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
        cache: bool = True,
        store: bool = True,
        user_identifier: str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        flow : str, keyword-only
            OAuth 2.0 authorization flow.

            .. container::

               **Valid values**:

               * :code:`"auth_code"` – Authorization Code Flow.
               * :code:`"pkce"` – Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` – Client Credentials Flow.
               * :code:`"implicit"` – Implicit Grant Flow.

        client_id : str, keyword-only, optional
            Client ID. Must be provided unless it is set as a system
            environment variable or stored in Minim's local token
            storage.

        client_secret : str, keyword-only, optional
            Client secret. Required for the Authorization Code, Client
            Credentials, and Resource Owner Password Credential flows.
            Must be provided unless it is set as a system environment
            variable or stored in Minim's local token storage.

        redirect_uri : str, keyword-only, optional
            Redirect URI. Required for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            the host is not :code:`localhost`, :code:`127.0.0.1`, or
            :code:`::1`, redirect handling is not available.

        scopes : str or Collection[str], keyword-only, optional
            Authorization scopes the client requests to access user
            resources.

            .. seealso::

               :meth:`get_scopes` – Get a set of scopes to request.

        access_token : str, keyword-only, optional
            Access token. If provided or found in Minim's local token
            storage, the authorization process is bypassed. If provided,
            all other relevant keyword arguments should also be
            specified to enable automatic token refresh upon expiration.

        token_type : str, keyword-only, default: :code:`"Bearer"`
            Type of the access token.

        refresh_token : str, keyword-only, optional
            Refresh token accompanying the access token in
            `access_token`. If not provided, the user will be
            reauthorized via the authorization flow in `flow` when the
            access token expires.

        expiry : str or datetime.datetime, keyword-only, optional
            Expiry of the access token in `access_token`. If provided as
            a string, it must be in ISO 8601 format
            (:code:`%Y-%m-%dT%H:%M:%SZ`).

        backend : str, keyword-only, optional
            Backend to handle redirects during the authorization flow.

            .. container::

               **Valid values**:

               * :code:`None` – Manually paste the redirect URL into
                 the terminal.
               * :code:`"http.server"` – Simple HTTP server.
               * :code:`"playwright"` – Playwright Firefox browser.

        browser : bool, keyword-only, default: :code:`False`
            Whether to automatically open the authorization
            URL in the default web browser for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            :code:`False`, the authorization URL is printed to the
            terminal.

        cache : bool, keyword-only, default: :code:`True`
            ...

        store : bool, keyword-only, default: :code:`True`
            Whether to enable Minim's local token storage for
            this client. If :code:`True`, newly acquired access tokens
            and related information are stored. If :code:`False`, the
            client will not retrieve or store access tokens.

        user_identifier : str, keyword-only, optional
            Unique identifier for the user account to log into for all
            authorization flows but the Client Credentials flow. Used
            when :code:`store=True` to distinguish between multiple
            user accounts for the same client ID and authorization flow.

            If provided, it is used to locate existing access tokens or
            store new tokens in Minim's local token storage, where the
            key is a SHA-256 hash of the client ID, authorization flow,
            and the identifier.

            If not provided, the last accessed account for the specified
            authorization flow in `flow` is selected if it exists in
            local storage. Otherwise, a new entry is created using a
            hash of the client ID, authorization flow, and an available
            user identifier (e.g., user ID) after successful
            authorization.

            Prepending the identifier with a tilde (`"~"`) skips token
            retrieval from local storage and forces a reauthorization.
        """
        super().__init__(cache=cache)
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

        # Assign unique account identifier
        self._resolve_account_identifier(flow, client_id, user_identifier)

        # If an access token is not provided, try to retrieve it from
        # local token storage
        if (
            not access_token
            and store
            and (accounts := api_config.get(self._API_NAME))
            and (account := accounts.get(self._account_identifier))
        ):
            # If a stored access token is found and the client ID
            # matches, assume all other pertinent information was
            # written correctly by Minim and is also available
            if (
                _access_token := account.get("access_token")
            ) and client_id == account.get("client_id"):
                access_token = _access_token
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
            authorize=False,
            store=store,
            user_identifier=user_identifier,
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

    @classmethod
    @abstractmethod
    def get_scopes(
        cls, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> set[str]:
        """
        Retrieve a set of authorization scopes.

        Parameters
        ----------
        *args : tuple[Any, ...]
            Positional arguments to be defined by subclasses.

        **kwargs : dict[str, Any]
            Keyword arguments to be defined by subclasses.

        Returns
        -------
        scopes : set[str]
            Authorization scopes.
        """
        ...

    @abstractmethod
    def _get_user_identifier(self) -> str:
        """
        Resolve and assign a user identifier for the current account.
        """
        ...

    @classmethod
    def clear_token_storage(cls) -> None:
        """
        Clear all stored access tokens and related information for
        this API client from Minim's local token storage.
        """
        if (api_name := f"{cls.__module__}.{cls.__qualname__}") in api_config:
            del api_config[api_name]
            with CONFIG_FILE.open("w") as f:
                yaml.safe_dump(config, f)

    @classmethod
    def remove_account_token(
        cls, flow: str, client_id: str, user_identifier: str | None = None
    ) -> None:
        """
        Remove a stored access token and related information for a
        specific account from this API client's local token storage.

        Parameters
        ----------
        flow : str
            Authorization flow.

        client_id : str
            Client ID.

        user_identifier : str, optional
            Unique identifier for the user account to log into for all
            authorization flows but the Client Credentials flow. If not
            provided, the last accessed account for the specified
            authorization flow in `flow` and client ID in `client_id` is
            removed.
        """
        changed = False
        if (api_name := f"{cls.__module__}.{cls.__qualname__}") in config:
            accounts = api_config[api_name]
            last_flow_str = f"last_{flow}"
            if user_identifier or flow == "client_credentials":
                if (
                    account_identifier := cls._generate_account_identifier(
                        flow, client_id, user_identifier
                    )
                ) in accounts:
                    # Reassign or delete last accessed account for this
                    # flow if it is the one being removed
                    if id(accounts[account_identifier]) == id(
                        accounts[last_flow_str]
                    ):
                        flow_accounts = [
                            (acct_ident, acct_info["added"])
                            for acct_ident, acct_info in accounts.items()
                            if acct_info["flow"] == flow
                        ]
                        flow_accounts.sort(key=lambda a: a[1], reverse=True)
                        if flow_accounts:
                            accounts[last_flow_str] = next(
                                acct_ident
                                for acct_ident, _ in flow_accounts
                                if acct_ident != account_identifier
                            )
                        else:
                            del accounts[last_flow_str]

                    del accounts[account_identifier]
                    changed = True
            else:
                # Reassign or delete last accessed account for this flow
                # if it has the same client ID
                if accounts[last_flow_str]["client_id"] == client_id:
                    acct_added_next = ""
                    acct_id_last = id(accounts[last_flow_str])
                    acct_ident_delete = acct_ident_next = None
                    for acct_ident, acct_info in accounts.items():
                        if acct_ident.startswith("l"):
                            continue
                        if id(acct_info) == acct_id_last:
                            acct_ident_delete = acct_ident
                        elif (
                            acct_info["flow"] == flow
                            and (acct_added := acct_info["added"])
                            > acct_added_next
                        ):
                            acct_added_next = acct_added
                            acct_ident_next = acct_ident
                    if acct_ident_next:
                        accounts[last_flow_str] = acct_ident_next
                    else:
                        del accounts[last_flow_str]
                    del accounts[acct_ident_delete]
                    changed = True

                # Find and delete the last accessed account for this
                # flow and client ID, if it exists
                else:
                    acct_added_last = ""
                    acct_ident_last = None
                    for acct_ident, acct_info in accounts.items():
                        if acct_ident.startswith("l"):
                            continue
                        if (
                            acct_info["client_id"] == client_id
                            and (acct_info["flow"] == flow)
                            and (acct_added := acct_info["added"])
                            > acct_added_last
                        ):
                            acct_added_last = acct_added
                            acct_ident_last = acct_ident

                    if acct_ident_last:
                        del accounts[acct_ident_last]
                        changed = True

        if changed:
            with CONFIG_FILE.open("w") as f:
                yaml.safe_dump(config, f)

    @staticmethod
    def _generate_account_identifier(
        flow: str, client_id: str, user_identifier: str | None = None
    ) -> str | None:
        """
        Generate a unique account identifier using a SHA-256 hash of the
        client ID, authorization flow, and user identifier.

        Parameters
        ----------
        flow : str
            Authorization flow.

        client_id : str
            Client ID.

        user_identifier : str, optional
            Unique identifier for the user account to log into for all
            authorization flows but the Client Credentials flow.

        Returns
        -------
        account_identifier : str
            Account identifier.
        """
        if flow == "client_credentials":
            return hashlib.sha256(f"{client_id}:{flow}".encode()).hexdigest()
        if user_identifier:
            return hashlib.sha256(
                f"{client_id}:{flow}:{user_identifier}".encode()
            ).hexdigest()
        return f"last_{flow}"

    @staticmethod
    def _generate_self_signed_certificate() -> None:
        """
        Generate a self-signed certificate to handle HTTPS redirects.
        """
        subject = x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, "127.0.0.1"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Minim"),
            ]
        )
        key = rsa.generate_private_key(public_exponent=65_537, key_size=2_048)
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(subject)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc) - timedelta(days=1))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("localhost"),
                        x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
                        x509.IPAddress(ipaddress.ip_address("::1")),
                    ]
                ),
                critical=False,
            )
            .sign(key, hashes.SHA256())
        )

        with open(MINIM_DIR / "key.pem", "wb") as f:
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        with open(MINIM_DIR / "cert.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

    def clear_cache(self, func: Callable[..., Any] | None = None) -> None:
        """ """
        if self._cache is not None:
            self._cache.clear(func)

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

        .. warning::

           Calling this method replaces all existing values with the
           provided arguments. Parameters not specified explicitly will
           be overwritten by their default values.

        Parameters
        ----------
        access_token : str, positional-only
            Access token.

            .. important::

               If the access token was acquired via a different
               authorization flow or client, call :meth:`set_flow` first
               to ensure that all other relevant authorization
               parameters are set correctly.

        token_type : str, default: :code:`"Bearer"`
            Type of the access token.

        refresh_token : str, keyword-only, optional
            Refresh token accompanying the access token in
            `access_token`. If not provided, the user will be
            reauthorized when the access token expires.

        expiry : str or datetime.datetime, keyword-only, optional
            Expiry of the access token in `access_token`. If provided
            as a string, it must be in ISO 8601 format
            (:code:`%Y-%m-%dT%H:%M:%SZ`).
        """
        self._client.headers["Authorization"] = f"{token_type} {access_token}"
        if refresh_token and self._flow in {"client_credentials", "implicit"}:
            raise ValueError(
                f"The {self._OAUTH_FLOWS_NAMES[self._flow]} does not "
                "support refresh tokens, but one was provided via the "
                "`refresh_token` argument."
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
        authorize: bool = True,
        store: bool = True,
        user_identifier: str | None = None,
    ) -> None:
        """
        Set or update the authorization flow and related information.

        .. warning::

           Calling this method replaces all existing values with the
           provided arguments. Parameters not specified explicitly will
           be overwritten by their default values.

        Parameters
        ----------
        flow : str, keyword-only
            OAuth 2.0 authorization flow.

            .. container::

               **Valid values**:

               * :code:`"auth_code"` – Authorization Code Flow.
               * :code:`"pkce"` – Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` – Client Credentials Flow.
               * :code:`"implicit"` – Implicit Grant Flow.

        client_id : str, keyword-only, optional
            Client ID. Must be provided unless it is set as a system
            environment variable or stored in Minim's local token
            storage.

        client_secret : str, keyword-only, optional
            Client secret. Required for the Authorization Code, Client
            Credentials, and Resource Owner Password Credential flows.
            Must be provided unless it is set as a system environment
            variable or stored in Minim's local token storage.

        redirect_uri : str, keyword-only, optional
            Redirect URI. Required for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            the host is not :code:`localhost`, :code:`127.0.0.1`, or
            :code:`::1`, redirect handling is not available.

        scopes : str or Collection[str], keyword-only, optional
            Authorization scopes the client requests to access user
            resources.

            .. seealso::

               :meth:`get_scopes` – Get a set of scopes to request.

        backend : str, keyword-only, optional
            Backend to handle redirects during the authorization flow.

            .. container::

               **Valid values**:

               * :code:`None` – Manually paste the redirect URL into
                 the terminal.
               * :code:`"http.server"` – Simple HTTP server.
               * :code:`"playwright"` – Playwright Firefox browser.

        browser : bool, keyword-only, default: :code:`False`
            Whether to automatically open the authorization
            URL in the default web browser for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            :code:`False`, the authorization URL is printed to the
            terminal.

        authorize : bool, keyword-only, default: :code:`True`
            Whether to immediately initiate the authorization
            flow to acquire an access token.

            .. important::

               Unless :meth:`set_access_token` is immediately called
               afterwards, this should be left as :code:`True` to ensure
               that the client's existing access token is compatible
               with the new authorization flow and/or scopes.

        store : bool, keyword-only, default: :code:`True`
            Whether to enable Minim's local token storage for
            this client. If :code:`True`, newly acquired access tokens
            and related information are stored. If :code:`False`, the
            client will not retrieve or store access tokens.

        user_identifier : str, keyword-only, optional
            Unique identifier for the user account to log into for all
            authorization flows but the Client Credentials flow. Used
            when :code:`store=True` to distinguish between multiple
            user accounts for the same client ID and authorization flow.

            If provided, it is used to locate existing access tokens or
            store new tokens in Minim's local token storage, where the
            key is a SHA-256 hash of the client ID, authorization flow,
            and the identifier.

            If not provided, the last accessed account for the specified
            authorization flow in `flow` is selected if it exists in
            local storage. Otherwise, a new entry is created using a
            hash of the client ID, authorization flow, and an available
            user identifier (e.g., user ID) after successful
            authorization.

            Prepending the identifier with a tilde (`"~"`) skips token
            retrieval from local storage and forces a reauthorization.
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
                f"The {self._OAUTH_FLOWS_NAMES[flow]} requires a "
                "a client secret to be provided via the "
                "`client_secret` argument."
            )
        self._client_secret = client_secret
        if flow in {"auth_code", "pkce", "implicit"} and not redirect_uri:
            raise ValueError(
                f"The {self._OAUTH_FLOWS_NAMES[flow]} requires a "
                "redirect URI to be provided via the `redirect_uri` "
                "argument."
            )
        parsed = urlparse(redirect_uri)
        self._port = (
            port
            if (port := parsed.port)
            else 80
            if parsed.scheme == "http"
            else 443
            if parsed.scheme == "https"
            else None
        )
        self._redirect_uri = redirect_uri
        if backend:
            if backend not in self._BACKENDS:
                _backends = "', '".join(self._BACKENDS)
                raise ValueError(
                    f"Invalid backend {backend!r}. Valid values: '{_backends}'."
                )
            if (hostname := parsed.hostname) not in {
                "localhost",
                "127.0.0.1",
                "::1",
            }:
                backend = None
                warnings.warn(
                    f"Redirect handling is not available for host {hostname!r}."
                )
        self._backend = backend
        self._browser = browser
        self._store = store
        if user_identifier:
            self._resolve_account_identifier(flow, client_id, user_identifier)

        if authorize:
            self._obtain_access_token()

    def _get_authorization_code(self, code_challenge: str | None = None) -> str:
        """
        Get the authorization code for the Authorization Code and
        Authorization Code with PKCE flows.

        Parameters
        ----------
        code_challenge : str, optional
            Code challenge derived from the code verifier for the
            Authorization Code with PKCE flow.

        Returns
        -------
        code : str
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
        auth_url : str
            Authorization URL to visit.

        part : str
            Part of the redirect URL to extract the authorization
            response from.

            **Valid values**: :code:`"query"`, :code:`"fragment"`.

        Returns
        -------
        queries : dict[str, int | str]
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
                httpd = HTTPServer(
                    (urlparse(self._redirect_uri).hostname, self._port),
                    OAuth2RedirectHandler,
                )
                if urlparse(self._redirect_uri).scheme == "https":
                    certfile = MINIM_DIR / "cert.pem"
                    keyfile = MINIM_DIR / "key.pem"
                    if not certfile.exists() or not keyfile.exists():
                        self._generate_self_signed_certificate()
                    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                    context.load_cert_chain(
                        certfile=certfile,
                        keyfile=keyfile,
                    )
                    httpd.socket = context.wrap_socket(
                        httpd.socket, server_side=True
                    )
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
        flow : str, optional
            Authorization flow. If not provided, the current
            authorization flow in :attr:`_flow` is used.

            .. container::

               **Valid values**:

               * :code:`"auth_code"` – Authorization Code Flow.
               * :code:`"pkce"` – Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` – Client Credentials Flow.
               * :code:`"implicit"` – Implicit Grant Flow.
               * :code:`"refresh_token"` – Refresh Token Flow.
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
                if error := resp_json.get("error"):
                    warnings.warn(
                        f"Encountered {error!r} error – "
                        f"{resp_json['error_description']}. "
                        "Reauthorizing via the "
                        f"{self._OAUTH_FLOWS_NAMES[self._flow]}.",
                    )
                    return self._obtain_access_token(self._flow)
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
        if self._store:
            accounts = api_config.get(self._API_NAME)
            if not isinstance(accounts, dict):
                api_config[self._API_NAME] = accounts = {}
            self._resolve_account_identifier(
                self._flow,
                self._client_id,
                getattr(self, "_user_identifier")
                or (
                    None
                    if self._flow == "client_credentials"
                    else self._get_user_identifier()
                ),
            )
            accounts[self._account_identifier] = accounts[
                f"last_{self._flow}"
            ] = {
                "added": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
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

    def _require_scopes(
        self, endpoint_method: str, scopes: str | Collection[str]
    ) -> None:
        """
        Ensure that the required authorization scopes for an endpoint
        method are granted.

        Parameters
        ----------
        endpoint_method : str
            Name of the endpoint method.

        scopes : str or Collection[str]
            Required authorization scopes.
        """
        if isinstance(scopes, str):
            if scopes not in self._scopes:
                raise RuntimeError(
                    f"{self._QUAL_NAME}.{endpoint_method}() requires "
                    f"the '{scopes}' scope."
                )
        else:
            for scope in scopes:
                self._require_scopes(endpoint_method, scope)

    def _resolve_account_identifier(
        self,
        flow: str | None = None,
        client_id: str | None = None,
        user_identifier: str | None = None,
    ) -> None:
        """
        Assign unique account identifier based on client ID,
        authorization flow, and optionally, a user identifier.

        Parameters
        ----------
        flow : str, optional
            Authorization flow. If not provided, the current
            authorization flow in :attr:`_flow` is used.

        client_id : str, optional
            Client ID. If not provided, the current client ID in
            :attr:`_client_id` is used.

        user_identifier : str, optional
            Unique identifier for the user account to log into for all
            authorization flows but the Client Credentials flow. If not
            provided, the current user identifier in
            :attr:`_user_identifier` is used.
        """
        if not flow:
            flow = self._flow
        if not client_id:
            client_id = self._client_id
        if not user_identifier:
            user_identifier = getattr(self, "_user_identifier", None)

        if user_identifier and user_identifier.startswith("~"):
            self._account_identifier = None
            self._user_identifier = user_identifier[1:]
        else:
            self._account_identifier = self._generate_account_identifier(
                flow, client_id, user_identifier
            )
            self._user_identifier = user_identifier


class ResourceAPI(ABC):
    """
    Abstract base class for API resource endpoint groups.
    """

    def __init__(self, client: APIClient, /) -> None:
        """
        Parameters
        ----------
        client : minim.api._shared.APIClient
            API client instance used to make HTTP requests.
        """
        self._client = client
