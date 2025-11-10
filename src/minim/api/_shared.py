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
from pathlib import Path
import secrets
import ssl
from textwrap import dedent
import threading
import time
import types
from typing import Any, Callable
from urllib.parse import parse_qsl, urlencode, urlparse
import uuid
import warnings
import webbrowser

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import httpx

from .. import FOUND, MINIM_DIR
from . import db_connection, db_cursor

if FOUND["playwright"]:
    from playwright.sync_api import sync_playwright


def _copy_docstring(
    source: Callable[..., Any],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Create a decorator that copies the docstring from a function to
    another function.

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


class TokenDatabase:
    """
    Application programming interface (API) for the local token storage.
    """

    @staticmethod
    def get_token(
        client: str,
        *,
        flow: str | None,
        client_id: str,
        user_identifier: str | None,
    ) -> dict[str, Any] | None:
        """
        Retrieves a access token and its related information from the
        local storage.

        Parameters
        ----------
        flow : str or None, keyword-only
            Authorization flow.

        client_id : str, keyword-only
            Client ID.

        user_identifier : str or None, keyword-only
            Unique identifier for the user account to log into.

        Returns
        -------
        token : dict[str, Any]
            Access token and its related information.
        """
        if user_identifier is None:
            clause = "ORDER BY added DESC"
            params = client, flow, client_id
        else:
            clause = "AND user_identifier = ?"
            params = client, flow, client_id, user_identifier
        db_cursor.execute(
            f"""
            SELECT *
            FROM tokens
            WHERE client = ?
            AND flow = ?
            AND client_id = ?
            {clause}
            LIMIT 1
            """,
            params,
        )
        row = db_cursor.fetchone()
        if row is None:
            return None
        return dict(zip((col for col, *_ in db_cursor.description), row))

    @staticmethod
    def add_token(
        client: str,
        *,
        flow: str,
        client_id: str,
        client_secret: str | None,
        user_identifier: str | None,
        redirect_uri: str | None,
        scopes: str | Collection[str],
        token_type: str,
        access_token: str,
        expiry: str | datetime | None,
        refresh_token: str | None,
    ) -> None:
        """
        Adds an access token and its related information to the local
        storage.

        Parameters
        ----------
        flow : str or None, keyword-only
            Authorization flow.

        client_id : str, keyword-only
            Client ID.

        client_secret : str or None, keyword-only
            Client secret.

        user_identifier : str or None, keyword-only
            Unique identifier for the user account to log into.

        redirect_uri : str, keyword-only, optional
            Redirect URI. Required for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            the host is not :code:`localhost`, :code:`127.0.0.1`, or
            :code:`::1`, redirect handling is not available.

        scopes : str or Collection[str], keyword-only
            Authorization scopes the client requests to access user
            resources.

        token_type : str, keyword-only
            Type of the access token in `access_token`.

        access_token : str, keyword-only
            Access token.

        expiry : str, datetime.datetime, or None, keyword-only
            Expiry of the access token in `access_token`.

        refresh_token : str or None, keyword-only
            Refresh token accompanying the access token in
            `access_token`.
        """
        db_cursor.execute(
            """
            INSERT OR REPLACE INTO tokens (
                flow,
                client,
                client_id,
                client_secret,
                user_identifier,
                redirect_uri,
                scopes,
                token_type,
                access_token,
                expiry,
                refresh_token
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                flow,
                client,
                client_id,
                client_secret,
                user_identifier or "",
                redirect_uri,
                scopes
                if isinstance(scopes, str)
                else " ".join(sorted(scopes)),
                token_type,
                access_token,
                expiry
                if isinstance(expiry, str)
                else expiry.strftime("%Y-%m-%dT%H:%M:%SZ"),
                refresh_token,
            ),
        )
        db_connection.commit()

    @staticmethod
    def remove_tokens(
        client: str,
        *,
        flows: str | Collection[str] | None = None,
        client_ids: str | Collection[str] | None = None,
        user_identifiers: str | Collection[str] | None = None,
    ) -> None:
        """
        Remove specific or all access tokens and their related
        information from the local storage.

        .. warning::

           If `flows`, `client_ids`, and `user_identifiers` are all not
           provided, all tokens in the local storage for the specified
           API client are removed.

        Parameters
        ----------
        client : str
            API client.

        flows : str or Collection[str], optional
            Authorization flows for which tokens should be removed.

        client_ids : str or Collection[str], optional
            Client IDs for which tokens should be removed.

        user_identifiers : str or Collection[str], optional
            Unique identifiers for the user accounts for which tokens
            should be removed.
        """
        query = "DELETE FROM tokens WHERE client = ?"
        params = [client]

        def make_filter_clause(
            field: str, values: str | Collection[str]
        ) -> str:
            if isinstance(values, str):
                params.append(values)
                return f" AND {field} = ?"
            else:
                params.extend(values)
                return f" AND {field} IN ({', '.join('?' for _ in values)})"

        if flows is not None:
            query += make_filter_clause("flow", flows)
        if client_ids is not None:
            query += make_filter_clause("client_id", client_ids)
        if user_identifiers is not None:
            query += make_filter_clause("user_identifier", user_identifiers)

        db_cursor.execute(query, params)
        db_connection.commit()


class TTLCache:
    """
    Time-to-live (TTL) cache with least recently used (LRU) eviction
    policy.
    """

    _TTL = {"catalog": 86_400, "featured": 43_200, "top": 3_600, "search": 600}

    def __init__(self, max_size: int = 1_024) -> None:
        """
        Parameters
        ----------
        max_size : int, default: :code:`1_024`
            Maximum number of entries to retain in the cache.
        """
        self._store = OrderedDict()
        self._max_size = max_size

    @staticmethod
    def _make_hashable(obj: Any) -> Any:
        """
        Convert an object into a hashable form for use as a cache key.

        Parameters
        ----------
        obj : Any
            Object to convert.

        Returns
        -------
        obj: Any
            Hashable equivalent of the input object.
        """
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
        *, ttl: int | float | str
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Create a decorator that marks an API endpoint method for
        caching.

        Parameters
        ----------
        ttl : int, float, or str, keyword-only
            Time-to-live (TTL) in seconds (or key referring to a
            predefined TTL) for cached entries.

            **Valid keys**:

            .. container::

               * :code:`"catalog"` – 1 day
               * :code:`"featured"` – 12 hours
               * :code:`"top"` – 1 hour
               * :code:`"search"` – 10 minutes

        Returns
        -------
        decorator : Callable[[Callable[..., Any]], Callable[..., Any]]
            Decorator that enables TTL-based caching for an API endpoint
            method.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapped(
                self: ResourceAPI,
                *args: tuple[Any, ...],
                **kwargs: dict[str, Any],
            ) -> Any:
                cache = getattr(
                    self._client if isinstance(self, ResourceAPI) else self,
                    "_cache",
                )
                if cache is None:
                    return func(self, *args, **kwargs)
                return cache.wrapper(ttl=ttl)(func)(self, *args, **kwargs)

            return wrapped

        return decorator

    def clear(
        self,
        funcs: Callable[..., Any]
        | Collection[Callable[..., Any]]
        | None = None,
        /,
        *,
        _recursive: bool = True,
    ) -> None:
        """
        Clear cached entries.

        .. warning::

           If no parameters are specified, all entries in the cache are
           cleared.

        Parameters
        ----------
        funcs : Callable or Collection[Callable], positional-only, \
        optional
            Functions whose cache entries should be cleared.
        """
        if funcs is None:
            self._store.clear()
        elif callable(funcs):
            funcs = funcs.__qualname__
            for key in [k for k in self._store if k[0] == funcs]:
                del self._store[key]
        elif _recursive and isinstance(funcs, Collection):
            for func in funcs:
                self.clear(func, _recursive=False)
        else:
            raise ValueError(
                "`funcs` must be methods from an API client class."
            )

    def wrapper(
        self, *, ttl: int | float | str
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Create a decorator that applies TTL- and LRU-based caching using
        the current cache instance.

        Parameters
        ----------
        ttl : int, float, or str, keyword-only
            Time-to-live (TTL) in seconds (or key referring to a
            predefined TTL) for cached entries.

            **Valid keys**:

            .. container::

               * :code:`"catalog"` – 1 day
               * :code:`"featured"` – 12 hours
               * :code:`"top"` – 1 hour
               * :code:`"search"` – 10 minutes

        Returns
        -------
        decorator : Callable[[Callable[..., Any]], Callable[..., Any]]
            Decorator that applies TTL-based caching to an API endpoint
            method.
        """
        if isinstance(ttl, str):
            ttl = self._TTL[ttl]

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapped(
                *args: tuple[Any, ...], **kwargs: dict[str, Any]
            ) -> Any:
                key = (
                    func.__qualname__,
                    tuple(self._make_hashable(a) for a in args[1:]),
                    frozenset(
                        (
                            (k, self._make_hashable(v))
                            for k, v in kwargs.items()
                        )
                    ),
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
    Abstract base class for application programming interface (API)
    clients.
    """

    _PROVIDER: str = ...
    _QUAL_NAME: str = ...
    #: Base URL for API endpoints.
    BASE_URL: str = ...

    def __init__(self, *, cache: bool = True) -> None:
        """
        Parameters
        ----------
        cache : bool, keyword-only, default: :code:`True`
            Whether to enable an in-memory time-to-live (TTL) cache with
            a least recently used (LRU) eviction policy for this client.
            If :code:`True`, responses from semi-static endpoints are
            cached for between 10 minutes and 1 day, depending on their
            expected update frequency.

            .. seealso::

               :meth:`clear_cache` – Clear specific or all cache
               entries for this API client.
        """
        self._cache = TTLCache() if cache else None
        self._client = httpx.Client(base_url=self.BASE_URL)

    def __enter__(self) -> "APIClient":
        """
        Enter the runtime context related to this API client.

        Returns
        -------
        client : APIClient
            This API client.
        """
        if self._client is None:
            raise RuntimeError(
                "The HTTP client session has been closed and cannot be used."
            )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """
        Exit the runtime context related to this API client.

        Parameters
        ----------
        exc_type : type, optional
            Exception type.

        exc_value : Exception, optional
            Exception value.

        exc_tb : TracebackType, optional
            Traceback.
        """
        self.close()

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
    def _validate_barcode(barcode: int | str, /) -> None:
        """
        Validate a Universal Product Code (UPC) or European Article
        Number (EAN) barcode.

        Parameters
        ----------
        barcode : int or str, positional-only
            UPC or EAN barcode.
        """
        if not (barcode_ := str(barcode)).isdigit() or len(barcode_) not in {
            12,
            13,
        }:
            raise ValueError(f"{barcode!r} is not a valid UPC or EAN.")

    @staticmethod
    def _validate_country_code(country_code: str, /) -> None:
        """
        Validate a country code.

        Parameters
        ----------
        country_code : str, positional-only
            ISO 3166-1 alpha-2 country code.
        """
        if (
            not isinstance(country_code, str)
            or len(country_code) != 2
            or not country_code.isalpha()
        ):
            raise ValueError(
                f"{country_code!r} is not a valid ISO 3166-1 "
                "alpha-2 country code."
            )

    @staticmethod
    def _validate_locale(locale: str, /) -> None:
        """
        Validate locale identifier.

        Parameters
        ----------
        locale : str, positional-only
            Locale identifier.
        """
        APIClient._validate_type("locale", locale, str)
        if (
            len(locale) != 5
            or not locale[:2].isalpha()
            or locale[2] != "_"
            or not locale[3:].isalpha()
        ):
            raise ValueError(
                f"{locale!r} is not a valid locale consisting of a "
                "an ISO 639-1 language code and an ISO 3166-1 alpha-2 "
                "country code joined by an underscore."
            )

    @staticmethod
    def _validate_isrc(isrc: str, /) -> None:
        """
        Validate an International Standard Recording Code (ISRC).

        Parameters
        ----------
        isrc : str, positional-only
            ISRC.
        """
        APIClient._validate_type("isrc", isrc, str)
        if len(isrc) != 12 or not (
            isrc[:2].isalpha() and isrc[2:5].isalnum() and isrc[5:].isdigit()
        ):
            raise ValueError(f"{isrc!r} is not a valid ISRC.")

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
            raise ValueError(f"`{name}` must be an integer{emsg_suffix}.")

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

    @staticmethod
    def _validate_uuid(uuid_: str, /) -> None:
        """
        Validate a universally unique identifier (UUID).

        Parameters
        ----------
        uuid_ : str, positional-only
            UUID.
        """
        try:
            uuid.UUID(uuid_)
        except (TypeError, ValueError):
            raise ValueError(f"{uuid_!r} is not a valid UUID.")

    def clear_cache(
        self,
        endpoint_methods: Callable[..., Any]
        | Collection[Callable[..., Any]]
        | None = None,
    ) -> None:
        """
        Clear specific or all cache entries for this API client.

        .. warning::

           If `endpoint_methods` is not provided, all cache entries for
           this API client are cleared.

        Parameters
        ----------
        endpoint_methods : Callable or Collection[Callable], \
        positional-only, optional
            Endpoint methods whose cache entries should be cleared.

            **Examples**: :code:`minim.api.spotify.SearchAPI.search`,
            :code:`[minim.api.spotify.SearchAPI.search,
            minim.api.spotify.TracksAPI.get_tracks]`.
        """
        if self._cache is not None:
            self._cache.clear(endpoint_methods)

    def close(self) -> None:
        """
        Terminate the HTTP client session.
        """
        if self._client is not None:
            self._client.close()
            self._client = None

    def set_cache_enabled(self, enable: bool) -> None:
        """
        Enable or disable the in-memory TTL cache for this API client.

        Parameters
        ----------
        enable : bool
            Whether to enable the cache.
        """
        if enable and self._cache is None:
            self._cache = TTLCache()
        elif not enable and self._cache is not None:
            self._cache.clear()
            self._cache = None


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
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        scopes: str | Collection[str] = "",
        token_type: str = "Bearer",
        access_token: str | None = None,
        refresh_token: str | None = None,
        expiry: str | datetime | None = None,
        backend: str | None = None,
        browser: bool = False,
        cache: bool = True,
        store: bool = True,
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
            Credentials, and Resource Owner Password Credential flows,
            and must be provided unless it is set as a system
            environment variable or stored in Minim's local token
            storage.

        user_identifier : str, keyword-only, optional
            Unique identifier for the user account to log into for all
            authorization flows but the Client Credentials flow. Used
            when :code:`store=True` to distinguish between multiple
            user accounts for the same client ID and authorization flow.

            If provided, it is used to locate existing access tokens or
            store new tokens in Minim's local token storage.

            If not provided, the last accessed account for the specified
            authorization flow in `flow` is selected if it exists in
            local storage. Otherwise, a new entry is created using a
            the client ID, authorization flow, and an available user
            identifier (e.g., user ID) after successful authorization.

            Prepending the identifier with a tilde (:code:`~`) skips
            token retrieval from local storage, and the suffix will be
            used as the identifier for storing future tokens.

        redirect_uri : str, keyword-only, optional
            Redirect URI. Required for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            the host is not :code:`localhost`, :code:`127.0.0.1`, or
            :code:`::1`, redirect handling is not available.

        scopes : str or Collection[str], keyword-only, optional
            Authorization scopes the client requests to access user
            resources.

        token_type : str, keyword-only, default: :code:`"Bearer"`
            Type of the access token in `access_token`.

        access_token : str, keyword-only, optional
            Access token. If provided or found in Minim's local token
            storage, the authorization process is bypassed. If provided,
            all other relevant keyword parameters should also be
            specified to enable automatic token refresh upon expiration.

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
            Whether to enable an in-memory time-to-live (TTL) cache with
            a least recently used (LRU) eviction policy for this client.
            If :code:`True`, responses from semi-static endpoints are
            cached for between 10 minutes and 1 day, depending on their
            expected update frequency.

            .. seealso::

               :meth:`clear_cache` – Clear specific or all cache
               entries for this API client.

        store : bool, keyword-only, default: :code:`True`
            Whether to enable Minim's local token storage for
            this client. If :code:`True`, newly acquired access tokens
            and related information are stored. If :code:`False`, the
            client will not retrieve or store access tokens.

            .. seealso::

               :meth:`remove_tokens` – Remove specific or all stored
               access tokens for this API client.
        """
        super().__init__(cache=cache)

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
                "parameters, respectively."
            )

        # If an access token is not provided, try to retrieve it from
        # local token storage
        if user_identifier and user_identifier[0] == "~":
            user_identifier = user_identifier[1:]
        elif account := TokenDatabase.get_token(
            self.__class__.__name__,
            flow=flow,
            client_id=client_id,
            user_identifier=user_identifier,
        ):
            access_token = account["access_token"]
            client_secret = account["client_secret"]
            scopes = account["scopes"]
            redirect_uri = account["redirect_uri"]
            token_type = account["token_type"]
            refresh_token = account["refresh_token"]
            expiry = account["expiry"]

        self.set_flow(
            flow,
            client_id=client_id,
            client_secret=client_secret,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            scopes=scopes,
            backend=backend,
            browser=browser,
            authorize=False,
            store=store,
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

    @abstractmethod
    def _get_user_identifier(self) -> str:
        """
        Resolve and assign a user identifier for the current account.
        """
        ...

    @classmethod
    def remove_tokens(
        cls,
        *,
        flows: str | Collection[str] | None = None,
        client_ids: str | Collection[str] | None = None,
        user_identifiers: str | Collection[str] | None = None,
    ) -> None:
        """
        Remove specific or all access tokens and their related
        information for this API client from the local token storage.

        .. warning::

           If no parameters are specified, all tokens in the local
           storage for this API client are removed.

        Parameters
        ----------
        flows : str or Collection[str], optional
            Authorization flows for which tokens should be removed.

        client_ids : str or Collection[str], optional
            Client IDs for which tokens should be removed.

        user_identifiers : str or Collection[str], optional
            Unique identifiers for the user accounts for which tokens
            should be removed.
        """
        TokenDatabase.remove_tokens(
            cls.__name__,
            flows=flows,
            client_ids=client_ids,
            user_identifiers=user_identifiers,
        )

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
            .not_valid_before(
                (now := datetime.now(timezone.utc)) - timedelta(minutes=5)
            )
            .not_valid_after(now + timedelta(days=365))
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

    @staticmethod
    def _is_certificate_valid(certificate_file: str | Path, /) -> bool:
        """
        Check whether a self-signed certificate is still valid.

        Parameters
        ----------
        certificate_file : str or pathlib.Path, positional-only
            Name of or path to the certificate file.

        Returns
        -------
        is_valid : bool
            Whether the certificate is valid.
        """
        try:
            with open(certificate_file, "rb") as f:
                certificate = x509.load_pem_x509_certificate(
                    f.read(), default_backend()
                )
            return (
                certificate.not_valid_before_utc
                <= datetime.now(timezone.utc)
                <= certificate.not_valid_after_utc
            )
        except Exception:
            return False

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
           specified parameters. Parameters not specified explicitly
           will be overwritten by their default values.

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
            Type of the access token in `access_token`.

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
                "`refresh_token` parameter."
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
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        scopes: str | Collection[str] = "",
        backend: str | None = None,
        browser: bool = False,
        authorize: bool = True,
        store: bool = True,
    ) -> None:
        """
        Set or update the authorization flow and related information.

        .. warning::

           Calling this method replaces all existing values with the
           specified parameters. Parameters not specified explicitly
           will be overwritten by their default values.

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

        user_identifier : str, keyword-only, optional
            Unique identifier for the user account to log into for all
            authorization flows but the Client Credentials flow. Used
            when :code:`store=True` to distinguish between multiple
            user accounts for the same client ID and authorization flow.

            If provided, it is used to locate existing access tokens or
            store new tokens in Minim's local token storage.

            If not provided, the last accessed account for the specified
            authorization flow in `flow` is selected if it exists in
            local storage. Otherwise, a new entry is created using a
            the client ID, authorization flow, and an available user
            identifier (e.g., user ID) after successful authorization.

            Prepending the identifier with a tilde (:code:`~`) skips
            token retrieval from local storage, and the suffix will be
            used as the identifier for storing future tokens.

        redirect_uri : str, keyword-only, optional
            Redirect URI. Required for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            the host is not :code:`localhost`, :code:`127.0.0.1`, or
            :code:`::1`, redirect handling is not available.

        scopes : str or Collection[str], keyword-only, optional
            Authorization scopes the client requests to access user
            resources.

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

            .. seealso::

               :meth:`remove_tokens` – Remove specific or all stored
               access tokens for this API client.
        """
        if flow not in self._FLOWS:
            _flows = "', '".join(self._FLOWS)
            raise ValueError(
                f"Invalid authorization flow {flow!r}. "
                f"Valid values: '{_flows}'."
            )
        self._flow = flow
        if flow == "client_credentials" and scopes:
            warnings.warn(
                "Scopes were specified in the `scopes` parameter, but "
                f"the {self._OAUTH_FLOWS_NAMES['client_credentials']} "
                "does not support scopes."
            )
            scopes = ""
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
                "`client_secret` parameter."
            )
        self._client_secret = client_secret
        has_redirect = flow in {"auth_code", "pkce", "implicit"}
        if has_redirect and not redirect_uri:
            raise ValueError(
                f"The {self._OAUTH_FLOWS_NAMES[flow]} requires a "
                "redirect URI to be provided via the `redirect_uri` "
                "parameter."
            )
        self._user_identifier = user_identifier
        if has_redirect:
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
                    warnings.warn(
                        f"Redirect handling is not available for host {hostname!r}."
                    )
            self._backend = backend
            self._browser = browser
        else:
            warnings.warn(
                "A redirect URI was provided via the `redirect_uri` "
                f"parameter, but the {self._OAUTH_FLOWS_NAMES[flow]} "
                "does not use redirects."
            )
            self._redirect_uri = None
            self._backend = None
            self._browser = None
        self._store = store

        if authorize:
            self._obtain_access_token()

    def _get_authorization_code(
        self, code_challenge: str | None = None
    ) -> str:
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
                    certificate_file = MINIM_DIR / "cert.pem"
                    private_key_file = MINIM_DIR / "key.pem"
                    if (
                        not certificate_file.exists()
                        or not private_key_file.exists()
                        or not self._is_certificate_valid(certificate_file)
                    ):
                        self._generate_self_signed_certificate()
                    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                    context.load_cert_chain(
                        certfile=certificate_file,
                        keyfile=private_key_file,
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
            b64_client_credentials = base64.urlsafe_b64encode(
                f"{self._client_id}:{self._client_secret}".encode()
            ).decode()
            resp_json = httpx.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "scope": " ".join(self._scopes),
                },
                headers={"Authorization": f"Basic {b64_client_credentials}"},
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
            TokenDatabase.add_token(
                self.__class__.__name__,
                flow=self._flow,
                client_id=self._client_id,
                client_secret=self._client_secret,
                user_identifier=getattr(self, "_user_identifier")
                or (
                    None
                    if self._flow == "client_credentials"
                    else self._get_user_identifier()
                ),
                redirect_uri=self._redirect_uri,
                scopes=self._scopes,
                token_type=token_type,
                access_token=access_token,
                refresh_token=getattr(self, "_refresh_token", None),
                expiry=getattr(self, "_expiry", None),
            )

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
