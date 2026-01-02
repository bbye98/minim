from abc import ABC, abstractmethod
import base64
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from functools import wraps
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import ipaddress
import json
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
    Return a decorator that copies the docstring from one function to
    another.

    Parameters
    ----------
    source : Callable[..., Any]
        Function whose docstring should be copied.

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
    API for storing and managing access tokens in local storage.
    """

    @staticmethod
    def get_tokens(
        *,
        client_names: str | list[str] | None = None,
        authorization_flows: str | list[str] | None = None,
        client_ids: str | list[str] | None = None,
        user_identifiers: str | list[str] | None = None,
    ) -> list[dict[str, Any]] | None:
        """
        Retrieve specific or all access tokens and their metadata from
        local storage.

        Parameters
        ----------
        client_names : str; keyword-only; optional
            Class names of the clients.

        authorization_flows : str or list[str]; keyword-only; optional
            Authorization flows.

        client_ids : str or list[str]; keyword-only; optional
            Client IDs.

        user_identifiers : str or list[str]; keyword-only; optional
            Identifiers for the user accounts.

        Returns
        -------
        tokens : list[dict[str, Any]] or None
            Access tokens and their metadata. Returns :code:`None` if no
            matching token is found.
        """
        params = []
        query = "SELECT * FROM tokens"
        first_clause = True

        _locals = locals()
        for param in [
            "client_name",
            "authorization_flow",
            "client_id",
            "user_identifier",
        ]:
            value = _locals.get(f"{param}s")
            if value is not None:
                query = TokenDatabase._update_filter_clause(
                    param,
                    value,
                    first_clause=first_clause,
                    query=query,
                    params=params,
                )
                first_clause = False

        db_cursor.execute(query, params)
        cols = tuple(col for col, *_ in db_cursor.description)
        if (rows := db_cursor.fetchall()) is not None:
            return [dict(zip(cols, row)) for row in rows]

    @staticmethod
    def add_token(
        client_name: str,
        *,
        authorization_flow: str,
        client_id: str,
        client_secret: str | None,
        user_identifier: str,
        redirect_uri: str | None,
        scopes: str | set[str] | None,
        token_type: str | None,
        access_token: str,
        expires_at: str | datetime | None,
        refresh_token: str | None,
        extras: dict[str, Any] | None = None,
    ) -> None:
        """
        Add an access token and its metadata to local storage.

        Parameters
        ----------
        client_name : str
            Class name of the client.

        authorization_flow : str; keyword-only
            Authorization flow.

        client_id : str; keyword-only
            Client ID.

        client_secret : str or None; keyword-only
            Client secret.

        user_identifier : str; keyword-only
            Identifier for the user account.

        redirect_uri : str; keyword-only; optional
            Redirect URI.

        scopes : str, set[str], or None; keyword-only
            Authorization scopes.

        token_type : str or None; keyword-only
            Type of the access token.

        access_token : str; keyword-only
            Access token.

        expires_at : str, datetime.datetime, or None; keyword-only
            Expiration time of the access token.

        refresh_token : str or None; keyword-only
            Refresh token for renewing the access token.

        extras : dict[str, Any]; keyword-only; optional
            Optional extra metadata associated with the access token.
        """
        db_cursor.execute(
            """
            INSERT OR REPLACE INTO tokens (
                authorization_flow,
                client_name,
                client_id,
                client_secret,
                user_identifier,
                redirect_uri,
                scopes,
                token_type,
                access_token,
                expires_at,
                refresh_token,
                extras
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                authorization_flow,
                client_name,
                client_id,
                client_secret,
                user_identifier,
                redirect_uri,
                " ".join(sorted(scopes))
                if isinstance(scopes, set)
                else scopes,
                token_type,
                access_token,
                expires_at.strftime("%Y-%m-%dT%H:%M:%SZ")
                if isinstance(expires_at, datetime)
                else expires_at,
                refresh_token,
                json.dumps(extras) if isinstance(extras, dict) else None,
            ),
        )
        db_connection.commit()

    @staticmethod
    def remove_tokens(
        *,
        client_names: str | list[str] | None = None,
        authorization_flows: str | list[str] | None = None,
        client_ids: str | list[str] | None = None,
        user_identifiers: str | list[str] | None = None,
    ) -> None:
        """
        Remove specific or all access tokens and their metadata from
        local storage.

        .. warning::

           If none of `client_names`, `authorization_flows`,
           `client_ids`, or `user_identifiers` are provided, all tokens
           will be removed from local storage.

        Parameters
        ----------
        client_names : str; keyword-only; optional
            Class names of the clients.

        authorization_flows : str or list[str]; keyword-only; optional
            Authorization flows.

        client_ids : str or list[str]; keyword-only; optional
            Client IDs.

        user_identifiers : str or list[str]; keyword-only; optional
            Identifiers for the user accounts.
        """
        params = []
        query = "DELETE FROM tokens"
        first_clause = True

        _locals = locals()
        for param in [
            "client_name",
            "authorization_flow",
            "client_id",
            "user_identifier",
        ]:
            value = _locals.get(f"{param}s")
            if value is not None:
                query = TokenDatabase._update_filter_clause(
                    param,
                    value,
                    first_clause=first_clause,
                    query=query,
                    params=params,
                )
                first_clause = False

        db_cursor.execute(query, params)
        db_connection.commit()

    @staticmethod
    def _get_token(
        client_name: str,
        *,
        authorization_flow: str | None,
        client_id: str,
        user_identifier: str | None,
    ) -> dict[str, Any] | None:
        """
        Retrieve an access token and its metadata from local storage.

        Parameters
        ----------
        client_name : str
            Class name of the client.

        authorization_flow : str or None; keyword-only
            Authorization flow.

        client_id : str; keyword-only
            Client ID.

        user_identifier : str or None; keyword-only
            Identifier for the user account.

        Returns
        -------
        token : dict[str, Any] or None
            Access token and its metadata. Returns :code:`None` if no
            matching token is found.
        """
        if user_identifier is None:
            clause = "ORDER BY added_at DESC"
            params = client_name, authorization_flow, client_id
        else:
            clause = "AND user_identifier = ?"
            params = (
                client_name,
                authorization_flow,
                client_id,
                user_identifier,
            )
        db_cursor.execute(
            f"""
            SELECT *
            FROM tokens
            WHERE client_name = ?
            AND authorization_flow = ?
            AND client_id = ?
            {clause}
            LIMIT 1
            """,
            params,
        )
        if (row := db_cursor.fetchone()) is not None:
            return dict(zip((col for col, *_ in db_cursor.description), row))

    @staticmethod
    def _update_filter_clause(
        field: str,
        values: str | list[str],
        /,
        *,
        first_clause: bool,
        query: str,
        params: list[Any],
    ) -> str:
        """
        Append a filter condition to a SQL :code:`WHERE` clause.

        Parameters
        ----------
        field : str; positional-only
            Name of the database column to filter on.

        values : str, list[str], or None; positional-only
            Values to filter by.

        query : str; keyword-only
            Existing SQL :code:`WHERE` clause.

        params : list[Any]; keyword-only
            SQL parameters corresponding to the :code:`WHERE` clause.

            .. note::

               This `list` is mutated in-place.

        Returns
        -------
        query : str
            Updated SQL :code:`WHERE` clause.
        """
        prefix = f"{query} {'WHERE' if first_clause else 'AND'} {field} "
        if isinstance(values, str):
            params.append(values)
            return f"{prefix}= ?"
        params.extend(values)
        return f"{prefix}IN ({', '.join('?' for _ in values)})"


class TTLCache:
    """
    Time-to-live (TTL) cache with least recently used (LRU) eviction
    policy.
    """

    _PREDEFINED_TTLS = {
        "permanent": float("Inf"),
        "catalog": 86_400,
        "featured": 43_200,
        "top": 3_600,
        "search": 600,
        "user": 120,
    }

    def __init__(self, *, max_size: int = 1_024) -> None:
        """
        Parameters
        ----------
        max_size : int; keyword-only; default: :code:`1_024`
            Maximum number of entries to retain in the cache.
        """
        self._store = OrderedDict()
        self._max_size = max_size

    @staticmethod
    def _make_hashable(obj: Any, /) -> Any:
        """
        Convert an object into a hashable form for use as a cache key.

        Parameters
        ----------
        obj : Any
            Object to convert.

        Returns
        -------
        hashable_obj: Any
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
        Return a decorator that marks a function for caching.

        Parameters
        ----------
        ttl : int, float, or str; keyword-only
            Time-to-live (TTL) (in seconds) or a key referring to a
            predefined TTL for cache entries.

            **Valid keys**:

            .. container::

               * :code:`"permanent"` – Cache indefinitely.
               * :code:`"catalog"` – 1 day.
               * :code:`"featured"` – 12 hours.
               * :code:`"top"` – 1 hour.
               * :code:`"search"` – 10 minutes.
               * :code:`"user"` – 2 minutes.

        Returns
        -------
        decorator : Callable[[Callable[..., Any]], Callable[..., Any]]
            Decorator that enables TTL-based caching for a function.
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
        funcs: Callable[..., Any] | list[Callable[..., Any]] | None = None,
        /,
        *,
        _recursive: bool = True,
    ) -> None:
        """
        Clear specific or all cache entries.

        .. warning::

           If `funcs` is not provided, all cache entries are cleared.

        Parameters
        ----------
        funcs : Callable or list[Callable]; positional-only; optional
            Functions whose cache entries should be cleared.
        """
        if funcs is None:
            self._store.clear()
        elif callable(funcs):
            funcs = funcs.__qualname__
            for key in [k for k in self._store if k[0] == funcs]:
                del self._store[key]
        elif _recursive and isinstance(funcs, tuple | list | set):
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
        ttl : int, float, or str; keyword-only
            Time-to-live (TTL) (in seconds) or a key referring to a
            predefined TTL for cache entries.

            **Valid keys**:

            .. container::

               * :code:`"catalog"` – 1 day.
               * :code:`"featured"` – 12 hours.
               * :code:`"top"` – 1 hour.
               * :code:`"search"` – 10 minutes.

        Returns
        -------
        decorator : Callable[[Callable[..., Any]], Callable[..., Any]]
            Decorator that applies TTL- and LRU-based caching to a
            function.
        """
        if isinstance(ttl, str):
            ttl = self._PREDEFINED_TTLS[ttl]

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
                    value, expires_at = entry
                    if expires_at is None or expires_at > now:
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
        Suppress the HTTP server logging output.

        Parameters
        ----------
        *args : tuple[Any, ...]
            Positional arguments to pass to
            :meth:`http.server.BaseHTTPRequestHandler.log_message`.

        **kwargs : dict[str, Any]
            Keyword arguments to pass to
            :meth:`http.server.BaseHTTPRequestHandler.log_message`.
        """
        pass


class APIClient(ABC):
    """
    Abstract base class for API clients.
    """

    _ALLOWED_AUTH_FLOWS: set[str | None]
    _ENV_VAR_PREFIX: str
    _PROVIDER: str
    _QUAL_NAME: str
    #: Base URL for API endpoints.
    BASE_URL: str

    def __init__(self, *, enable_cache: bool = True) -> None:
        """
        Parameters
        ----------
        enable_cache : bool; keyword-only; default: :code:`True`
            Whether to enable an in-memory time-to-live (TTL) cache with
            a least recently used (LRU) eviction policy for this client.
            If :code:`True`, responses from semi-static endpoints are
            cached for between 10 minutes and 1 day, depending on their
            expected update frequency.

            .. seealso::

               :meth:`clear_cache` – Clear specific or all cache
               entries for this client.
        """
        self._cache = TTLCache() if enable_cache else None
        self._client = httpx.Client(
            base_url=self.BASE_URL,  # follow_redirects=True
        )

    def __enter__(self) -> "APIClient":
        """
        Enter the runtime context related to this client.

        Returns
        -------
        client : APIClient
            This client.
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
        Exit the runtime context related to this client.

        Parameters
        ----------
        exc_type : type; optional
            Exception type.

        exc_value : Exception; optional
            Exception value.

        exc_tb : TracebackType; optional
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
        method : str; positional-only
            HTTP method.

        endpoint : str; positional-only
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
        barcode : int or str; positional-only
            UPC or EAN barcode.
        """
        if not (barcode_ := str(barcode)).isdecimal() or len(barcode_) not in {
            12,
            13,
        }:
            raise ValueError(f"{barcode!r} is not a valid UPC or EAN.")

    @staticmethod
    def _validate_country_code(country_code: str, /) -> None:
        """
        Validate a ISO 3166-1 alpha-2 country code.

        Parameters
        ----------
        country_code : str; positional-only
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
        Validate an Internet Engineering Task Force (IETF) Best Current
        Practice (BCP) 47 language tag, as defined in Request for
        Comments (RFC) 1766.

        Parameters
        ----------
        locale : str; positional-only
            IETF BCP 47 language tag.
        """
        if (
            not isinstance(locale, str)
            or len(locale) != 5
            or not locale[:2].isalpha()
            or locale[2] != "_"
            or not locale[3:].isalpha()
        ):
            raise ValueError(
                f"{locale!r} is not a valid IETF BCP 47 language tag "
                "consisting of an ISO 639-1 language code and an ISO "
                "3166-1 alpha-2 country code joined by an underscore."
            )

    @staticmethod
    def _validate_isrc(isrc: str, /) -> None:
        """
        Validate an International Standard Recording Code (ISRC).

        Parameters
        ----------
        isrc : str; positional-only
            ISRC.
        """
        if (
            not isinstance(isrc, str)
            or len(isrc) != 12
            or not (
                isrc[:2].isalpha()
                and isrc[2:5].isalnum()
                and isrc[5:].isdecimal()
            )
        ):
            raise ValueError(f"{isrc!r} is not a valid ISRC.")

    @staticmethod
    def _validate_number(
        name: str,
        value: int | float,
        data_type: type | types.UnionType,
        /,
        lower_bound: int | float | None = None,
        upper_bound: int | float | None = None,
    ) -> None:
        """
        Validate the value of a variable containing a number.

        Parameters
        ----------
        name : str; positional-only
            Variable name.

        value : int or float; positional-only
            Variable value.

        data_type : type or types.UnionType; positional-only
            Allowed numeric data types.

        lower_bound : int or float; optional
            Lower bound, inclusive.

        upper_bound : int or float; optional
            Upper bound, inclusive.
        """
        has_lower_bound = lower_bound is not None
        has_upper_bound = upper_bound is not None
        if has_lower_bound:
            if has_upper_bound:
                emsg_suffix = (
                    f" between {lower_bound} and {upper_bound}, inclusive"
                )
            else:
                emsg_suffix = f" greater than {lower_bound}, inclusive"
        else:
            if has_upper_bound:
                emsg_suffix = f" less than {upper_bound}, inclusive"
            else:
                emsg_suffix = ""
        if (
            not isinstance(value, data_type)
            or (has_lower_bound and value < lower_bound)
            or (has_upper_bound and value > upper_bound)
        ):
            data_type_str = (
                data_type.__name__
                if isinstance(data_type, type)
                else str(data_type)
            )
            raise ValueError(
                f"`{name}` must be a(n) {data_type_str}{emsg_suffix}."
            )

    @staticmethod
    def _validate_numeric(
        name: str,
        value: int | float | str,
        data_type: type,
        /,
        lower_bound: int | float | None = None,
        upper_bound: int | float | None = None,
    ) -> None:
        """
        Validate the value of a variable containing a numeric value.

        Parameters
        ----------
        name : str; positional-only
            Variable name.

        value : int, float, or str; positional-only
            Variable value.

        data_type : type; positional-only
            Allowed numeric data type.

        lower_bound : int or float; optional
            Lower bound, inclusive.

        upper_bound : int or float; optional
            Upper bound, inclusive.
        """
        try:
            if isinstance(value, str):
                value = data_type(value)
            APIClient._validate_number(
                name, value, data_type, lower_bound, upper_bound
            )
        except ValueError:
            raise ValueError(
                f"`{name}` must be a(n) {data_type.__name__} or its "
                "string representation."
            )

    @staticmethod
    def _validate_type(
        name: str, value: Any, data_type: type | types.UnionType, /
    ) -> None:
        """
        Validate the data type of a variable.

        Parameters
        ----------
        name : str; positional-only
            Variable name.

        value : Any; positional-only
            Variable value.

        data_type : type or types.UnionTypes; positional-only
            Allowed data type.
        """
        if not isinstance(value, data_type):
            data_type_str = (
                data_type.__name__
                if isinstance(data_type, type)
                else str(data_type)
            )
            raise ValueError(
                f"`{name}` must be a(n) {data_type_str}, not a(n) "
                f"{type(value).__name__}."
            )

    @staticmethod
    def _validate_uuid(uuid_: str, /) -> None:
        """
        Validate a universally unique identifier (UUID).

        Parameters
        ----------
        uuid_ : str; positional-only
            UUID.
        """
        try:
            uuid.UUID(uuid_)
        except (TypeError, ValueError):
            raise ValueError(f"{uuid_!r} is not a valid UUID.")

    def clear_cache(
        self,
        endpoint_methods: Callable[..., Any]
        | list[Callable[..., Any]]
        | None = None,
        /,
    ) -> None:
        """
        Clear specific or all cache entries for this client.

        .. warning::

           If `endpoint_methods` is not provided, all cache entries for
           this client are cleared.

        Parameters
        ----------
        endpoint_methods : Callable or list[Callable]; positional-only; \
        optional
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

    def set_cache_enabled(self, enable: bool, /) -> None:
        """
        Enable or disable the in-memory TTL cache for this client.

        Parameters
        ----------
        enable : bool; positional-only
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

    _ALLOWED_SCOPES: Any
    #: Authorization endpoint.
    AUTH_URL: str
    #: Device authorization endpoint.
    DEVICE_AUTH_URL: str
    #: Token endpoint.
    TOKEN_URL: str

    _IS_TRUSTED_DEVICE: bool = False
    _OAUTH_AUTH_FLOWS = {
        None: "unauthenticated client",
        "auth_code": "Authorization Code Flow",
        "pkce": "Authorization Code Flow with Proof Key for Code Exchange (PKCE)",
        "client_credentials": "Client Credentials Flow",
        "device": "Device Authorization Flow",
        "implicit": "Implicit Grant Flow",
        # "password": "Resource Owner Password Credentials Flow"
    }
    _OPTIONAL_AUTH: bool = False
    _REDIRECT_HANDLERS = {"http.server", "playwright"}

    def __init__(
        self,
        *,
        authorization_flow: str | None,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        scopes: str | set[str] = "",
        token_type: str = "Bearer",
        access_token: str | None = None,
        refresh_token: str | None = None,
        expires_at: str | datetime | None = None,
        redirect_handler: str | None = None,
        open_browser: bool = False,
        enable_cache: bool = True,
        store_tokens: bool = True,
    ) -> None:
        """
        Parameters
        ----------
        authorization_flow : str or None; keyword-only
            OAuth 2.0 authorization flow.

            **Valid values**:

            .. container::

               * :code:`None` – No authentication.
               * :code:`"auth_code"` – Authorization Code Flow.
               * :code:`"pkce"` – Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` – Client Credentials Flow.
               * :code:`"device"` – Device Authorization Flow.
               * :code:`"implicit"` – Implicit Grant Flow.

        client_id : str; keyword-only; optional
            Client ID. Required unless set as a system environment
            variable or stored in the local token storage.

        client_secret : str; keyword-only; optional
            Client secret. Required for the Authorization Code,
            Client Credentials, and Resource Owner Password Credential
            flows unless set as a system environment variable or
            stored in the local token storage.

        user_identifier : str; keyword-only; optional
            Identifier for the user account. Used when
            :code:`store_tokens=True` to distinguish between multiple
            accounts for the same client ID and authorization flow.

            If provided, it is used with the client ID and authorization
            flow to locate a matching stored token. If none is found, a
            new token is obtained and stored under this identifier.

            If not provided, the most recently accessed token for the
            client ID and authorization flow is used. If none exists, a
            new token is obtained and stored using a user identifier
            (e.g., user ID) acquired from a successful authorization.

            Prefixing the identifier with a tilde (:code:`~`) bypasses
            token retrieval, forces reauthorization, and stores the new
            token under the suffix.

        redirect_uri : str; keyword-only; optional
            Redirect URI. Required for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows.

        scopes : str or set[str]; keyword-only; optional
            Authorization scopes requested by the client to access user
            resources.

        token_type : str; keyword-only; default: :code:`"Bearer"`
            Type of the access token.

        access_token : str; keyword-only; optional
            Access token. If provided, the authorization process is
            bypassed, and automatic token refresh is enabled when
            relevant metadata (refresh token, expiry, etc.) is also
            supplied.

        refresh_token : str; keyword-only; optional
            Refresh token for renewing the access token. If not
            provided, the user will be reauthorized via the specified
            authorization flow when the access token expires.

        expires_at : str or datetime.datetime; keyword-only; optional
            Expiration time of the access token. If a string, it must be
            in ISO 8601 format (:code:`%Y-%m-%dT%H:%M:%SZ`).

        redirect_handler : str or None; keyword-only; optional
            Backend for handling redirects during the authorization
            flow. Redirect handling is only available for hosts
            :code:`localhost`, :code:`127.0.0.1`, or :code:`::1`.

            **Valid values**:

            .. container::

               * :code:`None` – Show authorization URL in and have the
                 user manually paste the redirect URL into the terminal.
               * :code:`"http.server"` – Run a HTTP server to intercept
                 the redirect after user authorization in any local
                 browser.
               * :code:`"playwright"` – Use a Playwright Firefox
                 browser to complete the user authorization.

        open_browser : bool; keyword-only; default: :code:`False`
            Whether to automatically open the authorization URL in the
            default web browser for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            :code:`False`, the URL is printed to the terminal.

        enable_cache : bool; keyword-only; default: :code:`True`
            Whether to enable an in-memory time-to-live (TTL) cache with
            a least recently used (LRU) eviction policy for this client.
            If :code:`True`, responses from semi-static endpoints are
            cached for 10 minutes to 1 day, depending on their expected
            update frequency.

            .. seealso::

               :meth:`clear_cache` – Clear specific or all cache
               entries for this client.

        store_tokens : bool; keyword-only; default: :code:`True`
            Whether to enable the local token storage for this client.
            If :code:`True`, existing access tokens are retrieved when
            found in local storage, and newly acquired tokens and their
            metadata are stored for future retrieval. If :code:`False`,
            the client neither retrieves nor stores access tokens.

            .. seealso::

               :meth:`get_tokens` – Retrieve specific or all stored
               access tokens for this client.

               :meth:`remove_tokens` – Remove specific or all stored
               access tokens for this client.
        """
        super().__init__(enable_cache=enable_cache)

        # If a client ID is not provided, try to retrieve it and its
        # corresponding client secret from environment variables
        if client_id is None:
            client_id = os.environ.get(f"{self._ENV_VAR_PREFIX}_CLIENT_ID")
            client_secret = os.environ.get(
                f"{self._ENV_VAR_PREFIX}_CLIENT_SECRET"
            )

        # Ensure `client_id` and `authorization_flow` are not empty/null
        if client_id is None:
            raise ValueError(
                "A client ID must be provided via the `client_id` parameter."
            )
        if not self._OPTIONAL_AUTH and authorization_flow is None:
            raise ValueError(
                "An authorization flow must be provided via the "
                "`authorization_flow` parameter."
            )

        if authorization_flow is not None:
            if user_identifier and user_identifier[0] == "~":
                user_identifier = user_identifier[1:]
            elif store_tokens and (
                account := TokenDatabase._get_token(
                    self.__class__.__name__,
                    authorization_flow=authorization_flow,
                    client_id=client_id,
                    user_identifier=user_identifier,
                )
            ):
                # If an access token is not provided, try to retrieve it
                # from local token storage
                access_token = account["access_token"]
                client_secret = account["client_secret"]
                scopes = account["scopes"]
                redirect_uri = account["redirect_uri"]
                token_type = account["token_type"]
                refresh_token = account["refresh_token"]
                expires_at = account["expires_at"]
                self._token_extras = (
                    json.loads(token_extras)
                    if isinstance(token_extras := account["extras"], str)
                    else token_extras
                )

        self.set_authorization_flow(
            authorization_flow,
            client_id=client_id,
            client_secret=client_secret,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            scopes=scopes,
            redirect_handler=redirect_handler,
            open_browser=open_browser,
            store_tokens=store_tokens,
            authenticate=False,
        )
        if authorization_flow is not None:
            if access_token:
                self.set_access_token(
                    access_token,
                    token_type,
                    refresh_token=refresh_token,
                    expires_at=expires_at,
                )
            else:
                self._obtain_access_token()

    @abstractmethod
    def _resolve_user_identifier(self) -> str | None:
        """
        Resolve the best user identifier for the current account.
        """
        ...

    @classmethod
    def get_tokens(
        cls,
        *,
        authorization_flows: str | list[str] | None = None,
        client_ids: str | list[str] | None = None,
        user_identifiers: str | list[str] | None = None,
    ) -> None:
        """
        Retrieve specific or all access tokens and their metadata for
        this client from local storage.

        Parameters
        ----------
        authorization_flows : str or list[str]; keyword-only; optional
            Authorization flows.

        client_ids : str or list[str]; keyword-only; optional
            Client IDs.

        user_identifiers : str or list[str]; keyword-only; optional
            Identifiers for the user accounts.
        """
        return TokenDatabase.get_tokens(
            client_names=cls.__name__,
            authorization_flows=authorization_flows,
            client_ids=client_ids,
            user_identifiers=user_identifiers,
        )

    @classmethod
    def remove_tokens(
        cls,
        *,
        authorization_flows: str | list[str] | None = None,
        client_ids: str | list[str] | None = None,
        user_identifiers: str | list[str] | None = None,
    ) -> None:
        """
        Remove specific or all access tokens and their metadata for this
        client from local storage.

        .. warning::

           If none of `authorization_flows`, `client_ids`, or
           `user_identifiers` are provided, all tokens for this client
           will be removed from local storage.

        Parameters
        ----------
        authorization_flows : str or list[str]; keyword-only; optional
            Authorization flows.

        client_ids : str or list[str]; keyword-only; optional
            Client IDs.

        user_identifiers : str or list[str]; keyword-only; optional
            Identifiers for the user accounts.
        """
        TokenDatabase.remove_tokens(
            client_names=cls.__name__,
            authorization_flows=authorization_flows,
            client_ids=client_ids,
            user_identifiers=user_identifiers,
        )

    @staticmethod
    def _generate_local_https_certificate() -> None:
        """
        Generate a self-signed certificate for handling local HTTPS
        redirects.
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
        certificate_file : str or pathlib.Path; positional-only
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
        access_token: str | None,
        /,
        token_type: str | None = "Bearer",
        *,
        refresh_token: str | None = None,
        expires_at: str | datetime | None = None,
    ) -> None:
        """
        Set or update the access token and its related metadata.

        .. warning::

           Calling this method replaces all existing values with the
           provided parameters. Parameters not provided explicitly
           will be overwritten by their default values.

        Parameters
        ----------
        access_token : str or None; positional-only
            Access token.

            .. important::

               If the access token was acquired via a different
               authorization flow or client, call :meth:`set_flow` first
               to ensure that all other relevant authorization
               parameters are set correctly.

        token_type : str or None; default: :code:`"Bearer"`
            Type of the access token.

        refresh_token : str; keyword-only; optional
            Refresh token for renewing the access token. If not
            provided, the user will be reauthorized via the current
            authorization flow when the access token expires.

        expires_at : str or datetime.datetime; keyword-only; optional
            Expiration time of the access token. If a string, it must be
            in ISO 8601 format (:code:`%Y-%m-%dT%H:%M:%SZ`).
        """
        if access_token is None:
            if self._auth_flow is not None:
                raise ValueError(
                    "`access_token` cannot be None when using the "
                    f"{self._OAUTH_AUTH_FLOWS[self._auth_flow]}."
                )
            if "Authorization" in self._client.headers:
                del self._client.headers["Authorization"]
            self._refresh_token = self._expires_at = None
            return

        self._client.headers["Authorization"] = f"{token_type} {access_token}"
        if refresh_token and self._auth_flow in {
            "client_credentials",
            "implicit",
        }:
            raise ValueError(
                f"The {self._OAUTH_AUTH_FLOWS[self._auth_flow]} does "
                "not support refresh tokens, but one was provided via "
                "the `refresh_token` parameter."
            )
        self._refresh_token = refresh_token
        self._expires_at = (
            datetime.strptime(expires_at, "%Y-%m-%dT%H:%M:%SZ")
            if expires_at and isinstance(expires_at, str)
            else expires_at
        )

    def set_authorization_flow(
        self,
        authorization_flow: str | None,
        /,
        *,
        client_id: str,
        client_secret: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        scopes: str | set[str] = "",
        redirect_handler: str | None = None,
        open_browser: bool = False,
        store_tokens: bool = True,
        authenticate: bool = True,
    ) -> None:
        """
        Set or update the authorization flow and related parameters.

        .. warning::

           Calling this method replaces all existing values with the
           provided parameters. Parameters not provided explicitly
           will be overwritten by their default values.

        Parameters
        ----------
        authorization_flow : str or None; keyword-only
            OAuth 2.0 authorization flow.

            **Valid values**:

            .. container::

               * :code:`None` – No authentication.
               * :code:`"auth_code"` – Authorization Code Flow.
               * :code:`"pkce"` – Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` – Client Credentials Flow.
               * :code:`"device"` – Device Authorization Flow.
               * :code:`"implicit"` – Implicit Grant Flow.

        client_id : str; keyword-only; optional
            Client ID. Required unless set as a system environment
            variable or stored in the local token storage.

        client_secret : str; keyword-only; optional
            Client secret. Required for the Authorization Code,
            Client Credentials, and Resource Owner Password Credential
            flows unless set as a system environment variable or
            stored in the local token storage.

        user_identifier : str; keyword-only; optional
            Identifier for the user account. Used when
            :code:`store_tokens=True` to distinguish between multiple
            accounts for the same client ID and authorization flow.

            If provided, it is used with the client ID and authorization
            flow to locate a matching stored token. If none is found, a
            new token is obtained and stored under this identifier.

            If not provided, the most recently accessed token for the
            client ID and authorization flow is used. If none exists, a
            new token is obtained and stored using a user identifier
            (e.g., user ID) acquired from a successful authorization.

            Prefixing the identifier with a tilde (:code:`~`) bypasses
            token retrieval, forces reauthorization, and stores the new
            token under the suffix.

        redirect_uri : str; keyword-only; optional
            Redirect URI. Required for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows.

        scopes : str or set[str]; keyword-only; optional
            Authorization scopes requested by the client to access user
            resources.

        redirect_handler : str or None; keyword-only; optional
            Backend for handling redirects during the authorization
            flow. Redirect handling is only available for hosts
            :code:`localhost`, :code:`127.0.0.1`, or :code:`::1`.

            **Valid values**:

            .. container::

               * :code:`None` – Show authorization URL in and have the
                 user manually paste the redirect URL into the terminal.
               * :code:`"http.server"` – Run a HTTP server to intercept
                 the redirect after user authorization in any local
                 browser.
               * :code:`"playwright"` – Use a Playwright Firefox
                 browser to complete the user authorization.

        open_browser : bool; keyword-only; default: :code:`False`
            Whether to automatically open the authorization URL in the
            default web browser for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            :code:`False`, the URL is printed to the terminal.

        store_tokens : bool; keyword-only; default: :code:`True`
            Whether to enable the local token storage for this client.
            If :code:`True`, existing access tokens are retrieved when
            found in local storage, and newly acquired tokens and their
            metadata are stored for future retrieval. If :code:`False`,
            the client neither retrieves nor stores access tokens.

            .. seealso::

               :meth:`get_tokens` – Retrieve specific or all stored
               access tokens for this client.

               :meth:`remove_tokens` – Remove specific or all stored
               access tokens for this client.

        authenticate : bool; keyword-only; default: :code:`True`
            Whether to immediately initiate the authorization
            flow to acquire an access token.

            .. important::

               Unless :meth:`set_access_token` is called immediately
               after, this should be left as :code:`True` to ensure the
               client's existing token is compatible with the new
               authorization flow and/or scopes.
        """
        if authorization_flow not in self._ALLOWED_AUTH_FLOWS:
            flows_str = "', '".join(
                sorted(f for f in self._ALLOWED_AUTH_FLOWS if f)
            )
            raise ValueError(
                f"Invalid authorization flow {authorization_flow!r}. "
                f"Valid values: '{flows_str}'."
            )
        self._auth_flow = authorization_flow
        if authorization_flow in {None, "client_credentials"} and scopes:
            warnings.warn(
                "Scopes were specified in the `scopes` parameter, but "
                f"the {self._OAUTH_AUTH_FLOWS[authorization_flow]} "
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
            authorization_flow
            in {"auth_code", "client_credentials", "password"}
            or authorization_flow == "device"
            and self._IS_TRUSTED_DEVICE
        ) and not client_secret:
            raise ValueError(
                f"The {self._OAUTH_AUTH_FLOWS[authorization_flow]} "
                "requires a client secret to be provided via the "
                "`client_secret` parameter."
            )
        self._client_secret = client_secret
        self._user_identifier = user_identifier
        requires_redirect = authorization_flow in {
            "auth_code",
            "pkce",
            "implicit",
        }
        has_redirect = redirect_uri is not None
        if requires_redirect and not has_redirect:
            raise ValueError(
                f"The {self._OAUTH_AUTH_FLOWS[authorization_flow]} "
                "requires a redirect URI to be provided via the "
                "`redirect_uri` parameter."
            )
        if requires_redirect:
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
            if redirect_handler is not None:
                if redirect_handler not in self._REDIRECT_HANDLERS:
                    handlers_str = "', '".join(sorted(self._REDIRECT_HANDLERS))
                    if handlers_str:
                        handlers_str = f", '{handlers_str}'"
                    raise ValueError(
                        f"Invalid backend {redirect_handler!r}. "
                        f"Valid value(s): None{handlers_str}."
                    )
                if (hostname := parsed.hostname) not in {
                    "localhost",
                    "127.0.0.1",
                    "::1",
                }:
                    warnings.warn(
                        "Redirect handling is not available for host "
                        f"{hostname!r}."
                    )
                    redirect_handler = None
            self._redirect_handler = redirect_handler
        else:
            if has_redirect:
                warnings.warn(
                    "A redirect URI was provided via the "
                    "`redirect_uri` parameter, but the "
                    f"{self._OAUTH_AUTH_FLOWS[authorization_flow]} "
                    "does not use redirects."
                )
            self._redirect_uri = None
            self._redirect_handler = None
        self._open_browser = open_browser
        self._store_tokens = store_tokens

        if authenticate and authorization_flow is not None:
            self._obtain_access_token()

    def _get_authorization_code(
        self, code_challenge: str | None = None
    ) -> str:
        """
        Get the authorization code for the Authorization Code and
        Authorization Code with PKCE flows.

        Parameters
        ----------
        code_challenge : str; optional
            Code challenge derived from the code verifier used in the
            Authorization Code with PKCE flow.

        Returns
        -------
        authorization_code : str
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
            f"{self.AUTH_URL}?{urlencode(params)}", url_component="query"
        )
        if error := queries.get("error"):
            raise RuntimeError(f"Authorization failed. Error: {error}")
        if params["state"] != queries["state"]:
            raise RuntimeError("Authorization failed due to state mismatch.")
        return queries["code"]

    def _handle_redirect(
        self, auth_url: str, /, url_component: str
    ) -> dict[str, int | str]:
        """
        Handle the redirect during an authorization flow.

        Parameters
        ----------
        auth_url : str; positional-only
            Authorization URL.

        url_component : str
            Part of the redirect URL to extract parameters from.

            **Valid values**: :code:`"query"`, :code:`"fragment"`.

        Returns
        -------
        queries : dict[str, int | str]
            Key-value pairs parsed from the specified part of the
            redirect URL.
        """
        if self._redirect_handler == "playwright":
            if not FOUND["playwright"]:
                raise RuntimeError(
                    "The redirect in the "
                    f"{self._OAUTH_AUTH_FLOWS[self._auth_flow]} uses "
                    "the `playwright` library, but it could not be "
                    "found or imported."
                )

            with sync_playwright() as playwright:
                browser = playwright.firefox.launch(headless=False)
                context = browser.new_context(
                    color_scheme="dark",
                    locale="en-US",
                    timezone_id="America/Los_Angeles",
                    **playwright.devices["Desktop Firefox HiDPI"],
                )
                page = context.new_page()
                with page.expect_request(f"{self._redirect_uri}*", timeout=0):
                    page.goto(auth_url)
                while True:
                    redirect_url = page.evaluate("window.location.href")
                    if redirect_url.startswith(self._redirect_uri):
                        break
                    time.sleep(0.1)
                queries = dict(
                    parse_qsl(getattr(urlparse(redirect_url), url_component))
                )
                context.close()
                browser.close()
        else:
            if self._open_browser:
                webbrowser.open(auth_url)
            else:
                print(
                    f"To grant Minim access to {self._PROVIDER} data "
                    "and features, open the following link in your web "
                    f"browser:\n\n{auth_url}\n"
                )

            if self._redirect_handler == "http.server":
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
                        self._generate_local_https_certificate()
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

    def _obtain_access_token(
        self, authorization_flow: str | None = None
    ) -> None:
        """
        Get and set a new access token via the provided or current
        authorization flow.

        Parameters
        ----------
        authorization_flow : str; optional
            Authorization flow. If not provided, the current
            authorization flow in :attr:`_auth_flow` is used.

            **Valid values**:

            .. container::

               * :code:`"auth_code"` – Authorization Code Flow.
               * :code:`"pkce"` – Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` – Client Credentials Flow.
               * :code:`"implicit"` – Implicit Grant Flow.
               * :code:`"refresh_token"` – Refresh Token Flow.
        """
        if not authorization_flow:
            authorization_flow = self._auth_flow

        if authorization_flow is None:
            self.set_access_token(None)

        if authorization_flow == "refresh_token":
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
                        f"{self._OAUTH_AUTH_FLOWS[self._auth_flow]}.",
                    )
                    return self._obtain_access_token(self._auth_flow)
            else:
                data["client_id"] = self._client_id
                resp_json = httpx.post(self.TOKEN_URL, data=data).json()
        elif authorization_flow == "client_credentials":
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
        elif authorization_flow == "implicit":
            params = {
                "client_id": self._client_id,
                "redirect_uri": self._redirect_uri,
                "response_type": "token",
                "scope": " ".join(self._scopes),
                "state": secrets.token_urlsafe(),
            }
            resp_json = self._handle_redirect(
                f"{self.AUTH_URL}?{urlencode(params)}",
                url_component="fragment",
            )
            if error := resp_json.get("error"):
                raise RuntimeError(f"Authorization failed. Error: {error}")
            if params.get("state") != resp_json.get("state"):
                raise RuntimeError(
                    "Authorization failed due to state mismatch."
                )
        elif authorization_flow == "device":
            data = {
                "client_id": self._client_id,
                "scope": " ".join(self._scopes),
            }
            resp_json = httpx.post(self.DEVICE_AUTH_URL, data=data).json()
            if error := resp_json.get("error"):
                raise RuntimeError(f"Authorization failed. Error: {error}")
            data["device_code"] = resp_json["deviceCode"]
            data["grant_type"] = "urn:ietf:params:oauth:grant-type:device_code"
            verification_uri = (
                f"https://{resp_json['verificationUriComplete']}"
            )
            if self._open_browser:
                webbrowser.open(verification_uri)
            else:
                print(
                    f"To grant Minim access to {self._PROVIDER} data "
                    "and features, open the following link in your web "
                    f"browser:\n\n{verification_uri}\n"
                )
            polling_interval = resp_json.get("interval", 2)
            while True:
                time.sleep(polling_interval)
                resp_json = httpx.post(
                    self.TOKEN_URL,
                    auth=(self._client_id, self._client_secret)
                    if self._IS_TRUSTED_DEVICE
                    else None,
                    data=data,
                ).json()
                if not (error := resp_json.get("error")):
                    break
                elif error != "authorization_pending":
                    raise RuntimeError(f"Authorization failed. Error: {error}")
        else:  # authorization_flow in {"auth_code", "pkce"}
            data = {
                "grant_type": "authorization_code",
                "redirect_uri": self._redirect_uri,
            }
            if authorization_flow == "pkce":
                data["client_id"] = self._client_id
                data["code_verifier"] = code_verifier = secrets.token_urlsafe(
                    96
                )
                data["code"] = self._get_authorization_code(
                    code_challenge=base64.urlsafe_b64encode(
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

        access_token = resp_json.pop("access_token")
        token_type = resp_json.pop("token_type").capitalize()
        if scopes := resp_json.pop("scope", None):
            self._scopes = set(scopes.split())
        self.set_access_token(
            access_token,
            token_type,
            refresh_token=resp_json.pop(
                "refresh_token", getattr(self, "_refresh_token", None)
            ),
            expires_at=datetime.now()
            + timedelta(seconds=int(resp_json.pop("expires_in"))),
        )
        self._token_extras = resp_json
        if self._user_identifier is None and self._auth_flow not in {
            None,
            "client_credentials",
        }:
            self._user_identifier = self._resolve_user_identifier()

        if self._store_tokens:
            TokenDatabase.add_token(
                self.__class__.__name__,
                authorization_flow=self._auth_flow,
                client_id=self._client_id,
                client_secret=self._client_secret,
                user_identifier=self._user_identifier or "",
                redirect_uri=self._redirect_uri,
                scopes=self._scopes,
                token_type=token_type,
                access_token=access_token,
                refresh_token=getattr(self, "_refresh_token", None),
                expires_at=getattr(self, "_expires_at", None),
                extras=resp_json,
            )

    def _refresh_access_token(self) -> None:
        """
        Refresh the access token.
        """
        self._obtain_access_token(
            "refresh_token" if self._refresh_token else self._auth_flow
        )

    def _require_authentication(self, endpoint_method: str, /) -> None:
        """
        Ensure that the user authentication has been performed for a
        protected endpoint.

        Parameters
        ----------
        endpoint_method : str; positional-only
            Name of the endpoint method.
        """
        if self._auth_flow is None:
            raise RuntimeError(
                f"{self._QUAL_NAME}.{endpoint_method}() requires user "
                "authentication via an OAuth 2.0 authorization flow."
            )

    def _require_scopes(
        self, endpoint_method: str, scopes: str | set[str], /
    ) -> None:
        """
        Ensure that the required authorization scopes for an endpoint
        method have been granted.

        Parameters
        ----------
        endpoint_method : str; positional-only
            Name of the endpoint method.

        scopes : str or set[str]; positional-only
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
