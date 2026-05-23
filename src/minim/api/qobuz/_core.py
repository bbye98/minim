from __future__ import annotations
import base64
from datetime import datetime
import getpass
import hashlib
import json
import os
import re
from typing import TYPE_CHECKING
from urllib.parse import urlencode, urlparse
import warnings

import httpx

from ... import FOUND
from ..._utility import join_values
from .._shared import OAuthAPIClient, TokenDatabase
from ._private_api.albums import PrivateAlbumsAPI
from ._private_api.artists import PrivateArtistsAPI
from ._private_api.catalog import PrivateCatalogAPI
from ._private_api.dynamic import PrivateDynamicAPI
from ._private_api.favorites import PrivateFavoritesAPI
from ._private_api.labels import PrivateLabelsAPI
from ._private_api.genres import PrivateGenresAPI
from ._private_api.playlists import PrivatePlaylistsAPI
from ._private_api.purchases import PrivatePurchasesAPI
from ._private_api.search import PrivateSearchAPI
from ._private_api.tracks import PrivateTracksAPI
from ._private_api.users import PrivateUsersAPI

if FOUND["playwright"]:
    from playwright.sync_api import sync_playwright

if TYPE_CHECKING:
    from typing import Any

    from ..._types import Collection


class PrivateQobuzAPIClient(OAuthAPIClient):
    """
    Private Qobuz API client.

    .. admonition:: attention

       As the private Qobuz API is not designed to be publicly
       accessible, this client may break without warning if Qobuz makes
       internal changes or be disabled and removed at any time to ensure
       compliance with the `Qobuz API Terms of Use
       <https://static.qobuz.com/apps/api/QobuzAPI-TermsofUse.pdf>`_.
    """

    _APP_RE = re.compile(r"/resources/.*/bundle.js")
    _ID_KEY_RE = re.compile(
        r'production:\{api:\{appId:"([^"]+)",appSecret.*?privateKey:\s*"([^"]+)"'
    )
    _SEED_RE = re.compile(
        r'[a-z]\.initialSeed\("([^"]+)",window\.utimezone\.([^)]+)\)'
    )

    _ALLOWED_AUTH_FLOWS = _AUTH_FLOWS = {
        None: "unauthenticated client",
        "ext_auth_code": "Qobuz authorization code flow",
        "password": "Qobuz Web Player login flow",
    }
    _ENV_VAR_PREFIX = "PRIVATE_QOBUZ_API"
    _OPTIONAL_AUTH = True
    _PROVIDER = "Qobuz"
    _REDIRECT_FLOWS = {"ext_auth_code"}
    _QUAL_NAME = f"minim.api.{_PROVIDER.lower()}.{__qualname__}"
    _VERSION = "1.17"

    AUTH_URL = "https://www.qobuz.com/signin/oauth"
    BASE_URL = "https://www.qobuz.com/api.json/0.2"
    TOKEN_URL = f"{BASE_URL}/oauth/callback"
    #: Web Player URL.
    WEB_PLAYER_URL = "https://play.qobuz.com"

    __slots__ = (
        "_app_id",
        "_app_secret",
        "_auth_key",
        "_credential_handler",
        "_token_extras",
        "albums",
        "artists",
        "catalog",
        "dynamic",
        "favorites",
        "labels",
        "genres",
        "playlists",
        "purchases",
        "search",
        "tracks",
        "users",
    )

    def __init__(
        self,
        *,
        auth_flow: str | None = None,
        app_id: str | None = None,
        app_secret: str | None = None,
        auth_key: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        user_auth_token: str | None = None,
        credential_handler: str | None = None,
        redirect_handler: str | None = None,
        open_browser: bool = False,
        enable_cache: bool = True,
        store_tokens: bool = True,
        user_agent: str | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Parameters
        ----------
        auth_flow : str or None; keyword-only; optional
            Authorization flow.

            **Valid values**:

            * :code:`None` – No authentication.
            * :code:`"ext_auth_code"` – Qobuz authorization code flow.
            * :code:`"password"` – Qobuz Web Player login flow.

        app_id : str; keyword-only; optional
            Application ID. If not provided, it is loaded from the
            system environment variable :code:`PRIVATE_QOBUZ_API_APP_ID`
            or from the local token storage if available, or retrieved
            from the Qobuz Web Player login page otherwise.

        app_secret : str; keyword-only; optional
            Application secret. If not provided, it is loaded from the
            system environment variable
            :code:`PRIVATE_QOBUZ_API_APP_SECRET` or from the local token
            storage if available, or retrieved from the Qobuz Web Player
            login page otherwise.

        auth_key : str; keyword-only; optional
            Authorization key used in the Authorization Code flow. If
            not provided, it is loaded from the system environment
            variable :code:`PRIVATE_QOBUZ_API_AUTH_KEY` if available, or
            retrieved from the Qobuz Web Player login page otherwise.

        user_identifier : str; keyword-only; optional
            Identifier for the user account. Used when
            :code:`store_tokens=True` to distinguish between multiple
            accounts for the same client ID and authorization flow.

            If specified, it is used with the client ID and authorization
            flow to locate a matching stored token. If none is found, a
            new token is obtained and stored under this identifier.

            If not specified, the most recently accessed token for the
            client ID and authorization flow is used. If none exists, a
            new token is obtained and stored using a user identifier
            (e.g., user ID) acquired from a successful authorization.

            Prefixing the identifier with a tilde (:code:`~`) bypasses
            token retrieval, forces reauthorization, and stores the new
            token under the suffix.

        redirect_uri : str; keyword-only; optional
            Redirect URI. Required for the Authorization Code flow.

        user_auth_token : str; keyword-only; optional
            User authentication token. If provided, the authorization
            process is bypassed.

        credential_handler : str; keyword-only; optional
            Backend for handling user credentials during the Qobuz Web
            Player login flow. If not specified, the client first looks
            for credentials in `kwargs` and falls back to prompting for
            them in an echo-free terminal.

            **Valid values**:

            * :code:`"kwargs"` – User credentials (email or username and
              password or its MD5 hash) provided directly via the
              `username` and `password` keyword arguments, respectively.
            * :code:`"getpass"` – Prompt for credentials in an echo-free
              terminal.
            * :code:`"playwright"` – Open the Qobuz Web Player login
              page in a Playwright Firefox browser.

        redirect_handler : str or None; keyword-only; optional
            Backend for handling redirects during the Authorization Code
            flow. Redirect handling is only available for hosts
            :code:`localhost`, :code:`127.0.0.1`, or :code:`::1`.

            **Valid values**:

            * :code:`None` – Show authorization URL in and have the user
              manually paste the redirect URL into the terminal.
            * :code:`"http.server"` – Run a HTTP server to intercept the
              redirect after user authorization in any local browser.
            * :code:`"playwright"` – Use a Playwright Firefox browser to
              complete the user authorization.

        open_browser : bool; keyword-only; default: :code:`False`
            Whether to automatically open the authorization URL in the
            default web browser for the Authorization Code flow. If
            :code:`False`, the URL is printed to the terminal.

        enable_cache : bool; keyword-only; default: :code:`True`
            Whether to enable an in-memory time-to-live (TTL) cache with
            a least recently used (LRU) eviction policy for this client.
            If :code:`True`, responses from semi-static endpoints are
            cached for one minute to one day, depending on their
            expected update frequency.

            .. seealso::

               :meth:`clear_cache` – Clear specific or all cache entries
               for this client.

        store_tokens : bool; keyword-only; default: :code:`True`
            Whether to enable the local token storage for this client.
            If :code:`True`, existing user authentication tokens are
            retrieved when found in local storage, and newly acquired
            tokens and their metadata are stored for future retrieval.
            If :code:`False`, the client neither retrieves nor stores
            tokens.

            .. seealso::

               :meth:`get_tokens` – Retrieve specific or all stored
               tokens for this client.

               :meth:`remove_tokens` – Remove specific or all stored
               tokens for this client.

        user_agent : str; keyword-only; optional
            :code:`User-Agent` value to include in the headers of HTTP
            requests.

        **kwargs : dict[str, Any]
            Keyword arguments to pass to
            :meth:`~minim.api.qobuz.PrivateUsersAPI.login`.
        """
        super().__init__(enable_cache=enable_cache, user_agent=user_agent)

        # Initialize subclasses for endpoint groups
        #: Albums API endpoints for the private Qobuz API.
        self.albums: PrivateAlbumsAPI = PrivateAlbumsAPI(self)
        #: Artists API endpoints for the private Qobuz API.
        self.artists: PrivateArtistsAPI = PrivateArtistsAPI(self)
        #: Catalog API endpoints for the private Qobuz API.
        self.catalog: PrivateCatalogAPI = PrivateCatalogAPI(self)
        #: Dynamic Tracks API endpoints for the private Qobuz API.
        self.dynamic: PrivateDynamicAPI = PrivateDynamicAPI(self)
        #: Favorites API endpoints for the private Qobuz API.
        self.favorites: PrivateFavoritesAPI = PrivateFavoritesAPI(self)
        #: Labels API endpoints for the private Qobuz API.
        self.labels: PrivateLabelsAPI = PrivateLabelsAPI(self)
        #: Genres API endpoints for the private Qobuz API.
        self.genres: PrivateGenresAPI = PrivateGenresAPI(self)
        #: Playlists API endpoints for the private Qobuz API.
        self.playlists: PrivatePlaylistsAPI = PrivatePlaylistsAPI(self)
        #: Purchases API endpoints for the private Qobuz API.
        self.purchases: PrivatePurchasesAPI = PrivatePurchasesAPI(self)
        #: Search-related endpoints for the private Qobuz API.
        self.search: PrivateSearchAPI = PrivateSearchAPI(self)
        #: Tracks API endpoints for the private Qobuz API.
        self.tracks: PrivateTracksAPI = PrivateTracksAPI(self)
        #: Users API endpoints for the private Qobuz API.
        self.users: PrivateUsersAPI = PrivateUsersAPI(self)

        # If an app ID is not provided, try to retrieve it and its
        # corresponding app secret from environment variables
        if app_id is None or app_secret is None:
            app_id = os.environ.get(f"{self._ENV_VAR_PREFIX}_APP_ID")
            app_secret = os.environ.get(f"{self._ENV_VAR_PREFIX}_APP_SECRET")

        # If the authorization key for the Authorization Code Flow is
        # not provided, try to retrieve it from environment variables
        if auth_flow == "auth_code" and auth_key is None:
            auth_key = os.environ.get(f"{self._ENV_VAR_PREFIX}_AUTH_KEY")

        # If the app ID or authorization key is still missing, get it
        # from Qobuz
        if app_id is None or auth_flow == "auth_code" and auth_key is None:
            app_id, auth_key, app_secret = self._resolve_app_credentials()

        if auth_flow is not None:
            if user_identifier and user_identifier[0] == "~":
                user_identifier = user_identifier[1:]
            elif store_tokens and (
                account := TokenDatabase._get_token(
                    self.__class__.__name__,
                    auth_flow=auth_flow,
                    client_id=app_id,
                    user_identifier=user_identifier,
                )
            ):
                # If a user authentication token is not provided, try
                # to retrieve it from local token storage
                user_auth_token = account["access_token"]
                app_secret = account["client_secret"]
                redirect_uri = account["redirect_uri"]
                self._token_extras = (
                    json.loads(token_extras)
                    if isinstance(token_extras := account["extras"], str)
                    else token_extras
                )

        self.set_auth_flow(
            auth_flow,
            app_id=app_id,
            app_secret=app_secret,
            auth_key=auth_key,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            credential_handler=credential_handler,
            redirect_handler=redirect_handler,
            open_browser=open_browser,
            store_tokens=store_tokens,
            authenticate=False,
        )
        if auth_flow is None:
            self._determine_app_secret()
        elif user_auth_token:
            self.set_user_auth_token(user_auth_token)
        else:
            self._obtain_user_auth_token(**kwargs)

    @classmethod
    def get_tokens(
        cls,
        *,
        auth_flows: str | Collection[str] | None = None,
        app_ids: str | Collection[str] | None = None,
        user_identifiers: str | Collection[str] | None = None,
    ) -> list[dict[str, Any]] | None:
        """
        Retrieve specific or all user authentication tokens and their
        metadata for this client from local storage.

        Parameters
        ----------
        auth_flows : str or Collection[str]; keyword-only; optional
            Authorization flows.

        app_ids : str or Collection[str]; keyword-only; optional
            Application IDs.

        user_identifiers : str or Collection[str]; keyword-only; \
        optional
            Identifiers for the user accounts.
        """
        TokenDatabase.get_tokens(
            client_names=cls.__name__,
            auth_flows=auth_flows,
            client_ids=app_ids,
            user_identifiers=user_identifiers,
        )

    @classmethod
    def remove_tokens(
        cls,
        *,
        auth_flows: str | Collection[str] | None = None,
        app_ids: str | Collection[str] | None = None,
        user_identifiers: str | Collection[str] | None = None,
    ) -> None:
        """
        Remove specific or all user authentication tokens and their
        metadata for this client from local storage.

        .. warning::

           If none of `auth_flows`, `app_ids`, or
           `user_identifiers` are provided, all tokens for this client
           will be removed from local storage.

        Parameters
        ----------
        auth_flows : str or Collection[str]; keyword-only; optional
            Authorization flows.

        app_ids : str or Collection[str]; keyword-only; optional
            Application IDs.

        user_identifiers : str or Collection[str]; keyword-only; \
        optional
            Identifiers for the user accounts.
        """
        TokenDatabase.remove_tokens(
            client_names=cls.__name__,
            auth_flows=auth_flows,
            client_ids=app_ids,
            user_identifiers=user_identifiers,
        )

    @classmethod
    def _resolve_app_credentials(cls) -> tuple[str, list[str], str]:
        """
        Resolve the application ID and secret using the Qobuz Web Player
        login page.

        Returns
        -------
        app_id : str
            Application ID.

        auth_key : str
            Authorization key used in the Authorization Code flow.

        app_secrets : list[str]
            Possible application secrets.
        """
        with httpx.Client(
            base_url=cls.WEB_PLAYER_URL, follow_redirects=True
        ) as client:
            m = cls._APP_RE.search(client.get("login").text)
            if m is None:
                raise RuntimeError("'bundle.js' was not found.")

            # /resources/8.1.0-b019/bundle.js
            bundle = client.get(m.group(0)).text

        return (
            *cls._ID_KEY_RE.search(bundle).groups(),
            [
                base64.b64decode(
                    "".join((secret, *match.groups()))[:-44]
                ).decode()
                for secret, match in (
                    (
                        secret,
                        re.search(
                            f'(?:{city.capitalize()}",info:")(.*?)(?:",extras:")'
                            '(.*?)(?:"},{offset)',
                            bundle,
                        ),
                    )
                    for secret, city in cls._SEED_RE.findall(bundle)
                )
                if match
            ],
        )

    def _determine_app_secret(self) -> None:
        """
        Determine the working application secret from the possible
        values.
        """
        if isinstance(self._app_secret, list):
            for app_secret in self._app_secret:
                try:
                    self._app_secret = app_secret
                    self.tracks.get_track_media_info(344521217, format_id=5)
                    break
                except RuntimeError:
                    continue
            else:
                raise RuntimeError(
                    "No valid application secret was found in 'bundle.js'."
                )

    def _get_ext_auth_code(self) -> str:
        """
        Get the authorization code for the Qobuz authorization code
        flow.

        Returns
        -------
        auth_code : str
            Authorization code.
        """
        params = {
            "ext_app_id": self._app_id,
            "redirect_url": self._redirect_uri,
        }
        auth_code = self._handle_redirect(
            f"{self.AUTH_URL}?{urlencode(params)}", url_component="query"
        ).get("code_autorisation")
        if not auth_code:
            raise RuntimeError("Authorization failed.")

        return auth_code

    def _login(
        self,
        username: str | None = None,
        password: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Perform the Qobuz Web Player login flow.

        Parameters
        ----------
        username : str; optional
            Email or username.

        password : str; optional
            Password or its MD5 hash.

        **kwargs : dict[str, Any]
            Keyword arguments to pass to
            :meth:`~minim.api.qobuz.PrivateUsersAPI.login`.

        Returns
        -------
        token : dict[str, Any]
            User authentication token and profile information.
        """
        if self._credential_handler == "playwright":
            if not FOUND["playwright"]:
                raise RuntimeError(
                    "The Qobuz Web Player login flow uses the "
                    "`playwright` library, but it could not be found "
                    "or imported."
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
                with page.expect_request(
                    f"{self.BASE_URL}/oauth/callback*", timeout=0
                ) as callback:
                    page.goto(f"{self.WEB_PLAYER_URL}/login")
                resp_json = callback.value.response().json()
                context.close()
                browser.close()
            return resp_json

        if self._credential_handler in {None, "kwargs"}:
            if username is None or password is None:
                if self._credential_handler == "kwargs":
                    raise ValueError(
                        "`username` and `password` must be provided for "
                        "the Qobuz Web Player login flow."
                    )
            else:
                return self.users.login(username, password, **kwargs)

        # self._credential_handler in {None, "getpass"}
        print(
            f"To grant Minim access to {self._PROVIDER} data "
            "and features, log in below:\n"
        )
        return self.users.login(
            input("Username: "),
            hashlib.md5(getpass.getpass().encode()).hexdigest(),
            **kwargs,
        )

    def _obtain_access_token(self):
        pass  # Implemented as _obtain_user_auth_token()

    def _obtain_user_auth_token(
        self, auth_flow: str | None = None, **kwargs: dict[str, Any]
    ) -> None:
        """
        Get and set a new user authentication token via the provided or
        current authorization flow.

        Parameters
        ----------
        auth_flow : str; optional
            Authorization flow. If not provided, the current
            authorization flow in :attr:`_auth_flow` is used.

            **Valid values**:

            * :code:`None` – No authentication.
            * :code:`"password"` – Qobuz Web Player login flow.

        **kwargs : dict[str, Any]
            Keyword arguments to pass to
            :meth:`~minim.api.qobuz.PrivateUsersAPI.login`.
        """
        if not auth_flow:
            auth_flow = self._auth_flow

        match auth_flow:
            case None:
                self.set_user_auth_token(None)
                return

            case "ext_auth_code":
                resp_json = self._client.get(
                    self.TOKEN_URL,
                    params={
                        "code": self._get_ext_auth_code(),
                        "private_key": self._auth_key,
                    },
                ).json()

            case "password":
                resp_json = self._login(**kwargs)

        user_auth_token = resp_json.pop(
            "token" if "token" in resp_json else "user_auth_token"
        )
        self.set_user_auth_token(user_auth_token)
        self._token_extras = resp_json
        if not self._user_identifier and self._auth_flow is not None:
            self._user_identifier = self._resolve_user_identifier()

        # Figure out the working application secret from the possible
        # values
        self._determine_app_secret()

        if self._store_tokens:
            TokenDatabase.add_token(
                self.__class__.__name__,
                auth_flow=self._auth_flow,
                client_id=self._app_id,
                client_secret=self._app_secret,
                user_identifier=self._user_identifier,
                redirect_uri=self._redirect_uri,
                token_type=None,
                access_token=user_auth_token,
                refresh_token=None,
                expires_at=None,
                extras=resp_json,
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        signed: bool = False,
        sig_params: dict[str, Any] | None = None,
        **kwargs: dict[str, Any],
    ) -> "httpx.Response":
        """
        Make an HTTP request to a private Qobuz API endpoint.

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

        endpoint : str; positional-only
            Private Qobuz API endpoint.

        signed : bool; keyword-only; default: :code:`False`
            Whether to sign the request.

        sig_params : dict[str, Any]; keyword-only; optional
            Query parameters to include in the signature.

        **kwargs : dict[str, Any]
            Keyword parameters to pass to :meth:`httpx.Client.request`.

        Returns
        -------
        response : httpx.Response
            HTTP response.
        """
        if signed:
            timestamp = datetime.now().timestamp()
            signature = "".join(
                f"{k}{str(v).lower() if isinstance(v, bool) else v}"
                for k, v in sorted(sig_params.items())
            )
            if "params" not in kwargs:
                kwargs["params"] = {}
            kwargs["params"] |= {
                "request_ts": timestamp,
                "request_sig": hashlib.md5(
                    (
                        f"{endpoint.replace('/', '')}{signature}"
                        f"{timestamp}{self._app_secret}"
                    ).encode()
                ).hexdigest(),
            }
        resp = self._client.request(method, endpoint, **kwargs)
        status = resp.status_code
        if 200 <= status < 300:
            return resp

        raise RuntimeError(
            f"{status} {resp.reason_phrase} – {resp.json()['message']}"
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
                "authentication."
            )

    def _resolve_user_identifier(self) -> str:
        """
        Return the Qobuz user ID as the user identifier for the
        current account.

        .. note::

           Invoking this method may call
           :meth:`~minim.api.qobuz.UsersAPI.get_me` and make a request
           to the private Qobuz API.
        """
        return (
            self._token_extras.get("user_id")
            or self._token_extras.get("user", {}).get("id")
            or self.users.get_me()
        )

    def set_auth_flow(
        self,
        auth_flow: str | None,
        /,
        *,
        app_id: str | None = None,
        app_secret: str | None = None,
        auth_key: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        credential_handler: str | None = None,
        redirect_handler: str | None = None,
        open_browser: bool = False,
        store_tokens: bool = True,
        authenticate: bool = True,
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Set or update the authorization flow and related parameters.

        .. warning::

           Calling this method replaces all existing values with the
           provided parameters. Parameters not provided explicitly
           will be overwritten by their default values.

        Parameters
        ----------
        auth_flow : str or None; keyword-only
            Authorization flow.

            **Valid values**:

            * :code:`None` – No authentication.
            * :code:`"ext_auth_code"` – Qobuz authorization code flow.
            * :code:`"password"` – Qobuz Web Player login flow.

        app_id : str; keyword-only; optional
            Application ID. If not provided, it is loaded from the
            system environment variable
            :code:`PRIVATE_QOBUZ_API_APP_ID`.

        app_secret : str; keyword-only; optional
            Application secret. If not provided, it is loaded from the
            system environment variable
            :code:`PRIVATE_QOBUZ_API_APP_SECRET`.

        auth_key : str; keyword-only; optional
            Authorization key used in the Authorization Code flow. If
            not provided, it is loaded from the system environment
            variable :code:`PRIVATE_QOBUZ_API_AUTH_KEY`.

        user_identifier : str; keyword-only; optional
            Identifier for the user account. Used when
            :code:`store_tokens=True` to distinguish between multiple
            accounts for the same client ID and authorization flow.

            If specified, it is used with the client ID and authorization
            flow to locate a matching stored token. If none is found, a
            new token is obtained and stored under this identifier.

            If not specified, the most recently accessed token for the
            client ID and authorization flow is used. If none exists, a
            new token is obtained and stored using a user identifier
            (e.g., user ID) acquired from a successful authorization.

            Prefixing the identifier with a tilde (:code:`~`) bypasses
            token retrieval, forces reauthorization, and stores the new
            token under the suffix.

        redirect_uri : str; keyword-only; optional
            Redirect URI. Required for the Authorization Code flow.

        credential_handler : str; keyword-only; optional
            Backend for handling user credentials during the Qobuz Web
            Player login flow. If not specified, the client first looks
            for credentials in `kwargs` and falls back to prompting for
            them in an echo-free terminal.

            **Valid values**:

            * :code:`"kwargs"` – Use credentials provided directly via
              the `username` and `password` keyword arguments.
            * :code:`"getpass"` – Prompt for credentials in an echo-free
              terminal.
            * :code:`"playwright"` – Open the Qobuz Web Player login
              page in a Playwright Firefox browser.

        redirect_handler : str or None; keyword-only; optional
            Backend for handling redirects during the Authorization Code
            flow. Redirect handling is only available for hosts
            :code:`localhost`, :code:`127.0.0.1`, or :code:`::1`.

            **Valid values**:

            * :code:`None` – Show authorization URL in and have the
              user manually paste the redirect URL into the terminal.
            * :code:`"http.server"` – Run a HTTP server to intercept
              the redirect after user authorization in any local
              browser.
            * :code:`"playwright"` – Use a Playwright Firefox
              browser to complete the user authorization.

        open_browser : bool; keyword-only; default: :code:`False`
            Whether to automatically open the authorization URL in the
            default web browser for the Authorization Code flow. If
            :code:`False`, the URL is printed to the terminal.

        store_tokens : bool; keyword-only; default: :code:`True`
            Whether to enable the local token storage for this client.
            If :code:`True`, existing user authentication tokens are
            retrieved when found in local storage, and newly acquired
            tokens and their metadata are stored for future retrieval.
            If :code:`False`, the client neither retrieves nor stores
            tokens.

            .. seealso::

               :meth:`get_tokens` – Retrieve specific or all stored
               tokens for this client.

               :meth:`remove_tokens` – Remove specific or all stored
               tokens for this client.

        authenticate : bool; keyword-only; default: :code:`True`
            Whether to immediately initiate the authorization
            flow to acquire a user authentication token.

            .. important::

               Unless :meth:`set_user_auth_token` is called immediately
               after, this should be left as :code:`True` to ensure the
               client's existing token is compatible with the new
               authorization flow.

        **kwargs : dict[str, Any]
            Keyword arguments to pass to
            :meth:`~minim.api.qobuz.PrivateUsersAPI.login`.
        """
        if auth_flow == "auth_code" and auth_key is None:
            auth_key = os.environ.get(f"f{self._ENV_VAR_PREFIX}_AUTH_KEY")
            if auth_key is None:
                raise ValueError(
                    "The authorization key must be provided via the "
                    "`auth_key` parameter."
                )

        if app_id is None or app_secret is None:
            app_id = os.environ.get(f"{self._ENV_VAR_PREFIX}_APP_ID")
            if app_id is None:
                raise ValueError(
                    "An application ID must be provided via the `app_id` "
                    "parameter."
                )

            app_secret = os.environ.get(f"{self._ENV_VAR_PREFIX}_APP_SECRET")
            if app_secret is None:
                raise ValueError(
                    "An application secret must be provided via the "
                    "`app_secret` parameter."
                )

        if auth_flow not in self._AUTH_FLOWS:
            raise ValueError(
                f"Invalid authorization flow {auth_flow!r}. "
                f"Valid values: {self._join_values(self._AUTH_FLOWS)}."
            )

        self._client.headers["x-app-id"] = self._app_id = app_id
        self._app_secret = app_secret
        self._auth_key = auth_key
        self._credential_handler = credential_handler

        super().set_auth_flow(
            auth_flow=auth_flow,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            redirect_handler=redirect_handler,
            open_browser=open_browser,
            store_tokens=store_tokens,
            authenticate=False,
        )

        if authenticate and auth_flow is not None:
            self._obtain_user_auth_token(**kwargs)

    def set_access_token(self) -> None:
        """
        Not implemented for this API client; use
        :meth:`set_user_auth_token` instead.
        """
        raise NotImplementedError

    def set_user_auth_token(self, user_auth_token: str | None, /) -> None:
        """
        Set or update the user authentication token.

        Parameters
        ----------
        user_auth_token : str or None; positional-only
            User authentication token.
        """
        if user_auth_token is None:
            if self._auth_flow is not None:
                raise ValueError(
                    "`user_auth_token` cannot be None when using the "
                    f"{self._AUTH_FLOWS[self._auth_flow]}."
                )
            if "x-user-auth-token" in self._client.headers:
                del self._client.headers["x-user-auth-token"]
            return
        elif isinstance(user_auth_token, str):
            self._client.headers["x-user-auth-token"] = user_auth_token
        else:
            raise TypeError("`user_auth_token` must be a string.")
