from datetime import datetime, timedelta
import json
import os
import secrets
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse
import warnings

import httpx

from .._shared import TokenDatabase, APIClient, OAuth2APIClient
from ._api.albums import AlbumsAPI
from ._api.artists import ArtistsAPI
from ._api.charts import ChartsAPI
from ._api.editorial import EditorialAPI
from ._api.episodes import EpisodesAPI
from ._api.genres import GenresAPI
from ._api.playlists import PlaylistsAPI
from ._api.podcasts import PodcastsAPI
from ._api.radios import RadiosAPI
from ._api.users import UsersAPI


class DeezerAPI(OAuth2APIClient):
    """
    Deezer API client.
    """

    _ALLOWED_AUTH_FLOWS = {None, "auth_code", "implicit"}
    _ALLOWED_PERMISSIONS = {
        "basic_access",
        "email",
        "offline_access",
        "manage_library",
        "manage_community",
        "delete_library",
        "listening_history",
    }
    _ENV_VAR_PREFIX = "DEEZER_API"
    _OPTIONAL_AUTH = True
    _PROVIDER = "Deezer"
    _QUAL_NAME = f"minim.api.{_PROVIDER.lower()}.{__qualname__}"
    _RATE_LIMIT_PER_SECOND = 10
    AUTH_URL = "https://connect.deezer.com/oauth/auth.php"
    BASE_URL = "https://api.deezer.com"
    TOKEN_URL = "https://connect.deezer.com/oauth/access_token.php"

    def __init__(
        self,
        *,
        authorization_flow: str | None = None,
        app_id: str | None = None,
        app_secret: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        permissions: str | set[str] = "",
        access_token: str | None = None,
        expires_at: str | datetime | None = None,
        redirect_handler: str | None = None,
        open_browser: bool = False,
        enable_cache: bool = True,
        store_tokens: bool = True,
        user_agent: str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        authorization_flow : str; keyword-only
            Authorization flow.

            **Valid values**:

            .. container::

               * :code:`None` – No authentication.
               * :code:`"auth_code"` – Authorization Code Flow.
               * :code:`"implicit"` – Implicit Grant Flow.

        app_id : str; keyword-only; optional
            Application ID. Required unless set as system environment
            variable :code:`DEEZER_API_APP_ID` or stored in the local
            token storage.

        app_secret : str; keyword-only; optional
            Application secret. Required for the Authorization Code flow
            unless set as system environment variable
            :code:`DEEZER_API_APP_SECRET` or stored in the local token
            storage.

        user_identifier : str; keyword-only; optional
            Identifier for the user account. Used when
            :code:`store_tokens=True` to distinguish between multiple
            accounts for the same client ID and authorization flow.

            If provided, it is used with the client ID and authorization
            flow to locate a matching stored token. If none is found, a
            new token is obtained and stored under this identifier.

            If not provided, the most recently accessed token for the
            client ID and authorization flow is used. If none exists, a
            new token is obtained and stored using the Spotify user ID
            acquired from a successful authorization.

            Prefixing the identifier with a tilde (:code:`~`) bypasses
            token retrieval, forces reauthorization, and stores the new
            token under the suffix.

        redirect_uri : str; keyword-only; optional
            Redirect URI. Required for the Authorization Code and
            Authorization Code with PKCE flows.

        permissions : str or set[str]; keyword-only; optional
            Permissions requested by the client to access user
            resources.

            .. seealso::

               :meth:`resolve_permissions` – Resolve substrings into a
               set of permissions.

        access_token : str; keyword-only; optional
            Access token. If provided, the authorization process is
            bypassed.

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
            default web browser for the Authorization Code flow. If
            :code:`False`, the URL is printed to the terminal.

        enable_cache : bool; keyword-only; default: :code:`True`
            Whether to enable an in-memory time-to-live (TTL) cache with
            a least recently used (LRU) eviction policy for this client.
            If :code:`True`, responses from semi-static endpoints are
            cached for 2 minutes to 1 day, depending on their expected
            update frequency.

            .. seealso::

               :meth:`clear_cache` – Clear specific or all cache entries
               for this client.

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

        user_agent : str; keyword-only; optional
            :code:`User-Agent` value to include in the headers of HTTP
            requests.
        """
        APIClient.__init__(
            self, enable_cache=enable_cache, user_agent=user_agent
        )

        # Initialize subclasses for endpoint groups
        #: Albums API endpoints for the Deezer API.
        self.albums: AlbumsAPI = AlbumsAPI(self)
        #: Artists API endpoints for the Deezer API.
        self.artists: ArtistsAPI = ArtistsAPI(self)
        #: Charts API endpoints for the Deezer API.
        self.charts: ChartsAPI = ChartsAPI(self)
        #: Editorial API endpoints for the Deezer API.
        self.editorial: EditorialAPI = EditorialAPI(self)
        #: Episodes API endpoints for the Deezer API.
        self.episodes: EpisodesAPI = EpisodesAPI(self)
        #: Genres API endpoints for the Deezer API.
        self.genres: GenresAPI = GenresAPI(self)
        #: Playlists API endpoints for the Deezer API.
        self.playlists: PlaylistsAPI = PlaylistsAPI(self)
        #: Podcasts API endpoints for the Deezer API.
        self.podcasts: PodcastsAPI = PodcastsAPI(self)
        #: Radios API endpoints for the Deezer API.
        self.radios: RadiosAPI = RadiosAPI(self)
        #: Users API endpoints for the Deezer API.
        self.users: UsersAPI = UsersAPI(self)

        # If an app ID is not provided, try to retrieve it and its
        # corresponding app secret from environment variables
        if app_id is None or app_secret is None:
            app_id = os.environ.get(f"{self._ENV_VAR_PREFIX}_APP_ID")
            app_secret = os.environ.get(f"{self._ENV_VAR_PREFIX}_APP_SECRET")

        if authorization_flow is not None:
            if user_identifier and user_identifier[0] == "~":
                user_identifier = user_identifier[1:]
            elif store_tokens and (
                account := TokenDatabase._get_token(
                    self.__class__.__name__,
                    authorization_flow=authorization_flow,
                    client_id=app_id,
                    user_identifier=user_identifier,
                )
            ):
                # If an access token is not provided, try to retrieve it
                # from local token storage
                access_token = account["access_token"]
                app_secret = account["client_secret"]
                permissions = account["scopes"]
                redirect_uri = account["redirect_uri"]
                expires_at = account["expires_at"]
                self._token_extras = (
                    json.loads(token_extras)
                    if isinstance(token_extras := account["extras"], str)
                    else token_extras
                )

        self.set_authorization_flow(
            authorization_flow,
            app_id=app_id,
            app_secret=app_secret,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            permissions=permissions,
            redirect_handler=redirect_handler,
            open_browser=open_browser,
            store_tokens=store_tokens,
            authenticate=False,
        )
        if authorization_flow is None:
            self._access_token = self._refresh_token = self._expires_at = None
        elif access_token:
            self.set_access_token(access_token, expires_at=expires_at)
        else:
            self._obtain_access_token()

    @classmethod
    def get_tokens(
        cls,
        *,
        authorization_flows: str | list[str] | None = None,
        app_ids: str | list[str] | None = None,
        user_identifiers: str | list[str] | None = None,
    ) -> list[dict[str, Any]] | None:
        """
        Retrieve specific or all access tokens and their metadata for
        this client from local storage.

        Parameters
        ----------
        authorization_flows : str or list[str]; keyword-only; optional
            Authorization flows.

        app_ids : str or list[str]; keyword-only; optional
            Application IDs.

        user_identifiers : str or list[str]; keyword-only; optional
            Identifiers for the user accounts.
        """
        TokenDatabase.get_tokens(
            client_names=cls.__name__,
            authorization_flows=authorization_flows,
            client_ids=app_ids,
            user_identifiers=user_identifiers,
        )

    @classmethod
    def remove_tokens(
        cls,
        *,
        authorization_flows: str | list[str] | None = None,
        app_ids: str | list[str] | None = None,
        user_identifiers: str | list[str] | None = None,
    ) -> None:
        """
        Remove specific or all access tokens and their metadata for this
        client from local storage.

        .. warning::

           If none of `authorization_flows`, `app_ids`, or
           `user_identifiers` are provided, all tokens for this client
           will be removed from local storage.

        Parameters
        ----------
        authorization_flows : str or list[str]; keyword-only; optional
            Authorization flows.

        app_ids : str or list[str]; keyword-only; optional
            Application IDs.

        user_identifiers : str or list[str]; keyword-only; optional
            Identifiers for the user accounts.
        """
        TokenDatabase.remove_tokens(
            client_names=cls.__name__,
            authorization_flows=authorization_flows,
            client_ids=app_ids,
            user_identifiers=user_identifiers,
        )

    @classmethod
    def resolve_permissions(
        cls, matches: str | list[str] | None = None
    ) -> set[str]:
        """
        Resolve one or more substrings into a set of permissions.

        Parameters
        ----------
        matches : str or list[str]; optional
            Substrings to match in the available permissions. If not
            specified, all available permissions are returned.

        Returns
        -------
        permissions : set[str]
            Permissions.
        """
        # Return all permissions if no matches are provided
        if matches is None:
            return cls._ALLOWED_PERMISSIONS.copy()

        # Return permissions containing a substring
        if isinstance(matches, str):
            return {
                permission
                for permission in cls._ALLOWED_PERMISSIONS
                if matches in permission
            }

        # Recursively gather permissions for multiple
        # categories/substrings
        return {
            permission
            for match in matches
            for permission in cls.resolve_permissions(match)
        }

    def _get_authorization_code(self) -> str:
        """
        Get the authorization code for the Authorization Code flow.

        Returns
        -------
        authorization_code : str
            Authorization code.
        """
        params = {
            "app_id": self._app_id,
            "perms": ",".join(self._permissions),
            "redirect_uri": self._redirect_uri,
            "state": secrets.token_urlsafe(),
        }
        queries = self._handle_redirect(
            f"{self.AUTH_URL}?{urlencode(params)}", url_component="query"
        )
        if error := queries.get("error_reason"):
            raise RuntimeError(f"Authorization failed. Error: {error}")
        if params["state"] != queries["state"]:
            raise RuntimeError("Authorization failed due to state mismatch.")
        return queries["code"]

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
               * :code:`"implicit"` – Implicit Grant Flow.
        """
        if not authorization_flow:
            authorization_flow = self._auth_flow

        if authorization_flow is None:
            self.set_access_token(None)

        if authorization_flow == "implicit":
            params = {
                "app_id": self._app_id,
                "redirect_uri": self._redirect_uri,
                "response_type": "token",
                "perms": ",".join(self._permissions),
            }
            resp_json = self._handle_redirect(
                f"{self.AUTH_URL}?{urlencode(params)}",
                url_component="fragment",
            )
            if error := resp_json.get("error"):
                raise RuntimeError(
                    f"Authorization failed. "
                    f"Error: {error} ({resp_json.get('error_reason')})"
                )
        else:  # authorization_flow == "auth_code"
            resp_json = dict(
                parse_qsl(
                    httpx.post(
                        self.TOKEN_URL,
                        data={
                            "app_id": self._app_id,
                            "secret": self._app_secret,
                            "code": self._get_authorization_code(),
                        },
                    ).text
                )
            )

        self.set_access_token(
            resp_json.pop("access_token"),
            expires_at=(datetime.now() + timedelta(seconds=expires))
            if (expires := int(resp_json.pop("expires")))
            else None,
        )
        self._token_extras = resp_json
        if self._user_identifier is None and self._auth_flow is not None:
            self._user_identifier = self._resolve_user_identifier()
        if self._store_tokens:
            TokenDatabase.add_token(
                self.__class__.__name__,
                authorization_flow=self._auth_flow,
                client_id=self._app_id,
                client_secret=self._app_secret,
                user_identifier=self._user_identifier or "",
                redirect_uri=self._redirect_uri,
                scopes=self._permissions or "basic_access",
                token_type=None,
                access_token=self._access_token,
                refresh_token=None,
                expires_at=self._expires_at,
                extras=resp_json,
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        retry: bool = True,
        params: dict[str, Any] | None = None,
        **kwargs: dict[str, Any],
    ) -> "httpx.Response":
        """
        Make an HTTP request to a Deezer API endpoint.

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

        endpoint : str; positional-only
            Deezer API endpoint.

        retry : bool; keyword-only; default: :code:`True`
            Whether to retry the request if the first attempt returns a
            :code:`300 TOKEN_INVALID`.

        **kwargs : dict[str, Any]
            Keyword parameters to pass to :meth:`httpx.Client.request`.

        Returns
        -------
        response : httpx.Response
            HTTP response.
        """
        if self._expires_at and datetime.now() > self._expires_at:
            self._obtain_access_token()

        if self._access_token:
            if params is None:
                params = {}
            params["access_token"] = self._access_token
        resp = self._client.request(method, endpoint, params=params, **kwargs)
        if "error" not in resp.text or not (error := resp.json()["error"]):
            return resp

        error_code = error.get("code")
        if error_code is None:
            raise RuntimeError(f"{error['type']} {error['message']}")
        if error_code == 300 and retry:
            self._obtain_access_token()
            return self._request(
                method, endpoint, retry=False, params=params, **kwargs
            )
        raise RuntimeError(
            f"{error_code} {error['type']} – {error['message']}"
        )

    def _require_permissions(
        self, endpoint_method: str, permissions: str | set[str], /
    ) -> None:
        """
        Ensure that the required permissions for an endpoint method have
        been granted.

        Parameters
        ----------
        endpoint_method : str; positional-only
            Name of the endpoint method.

        scopes : str or set[str]; positional-only
            Required authorization scopes.
        """
        if isinstance(permissions, str):
            if permissions not in self._permissions:
                raise RuntimeError(
                    f"{self._QUAL_NAME}.{endpoint_method}() requires "
                    f"the '{permissions}' permission."
                )
        else:
            for permission in permissions:
                self._require_permissions(endpoint_method, permission)

    def _resolve_user_identifier(self) -> str:
        """
        Return the Deezer user ID as the user identifier for the
        current account.

        .. note::

           Invoking this method may call
           :meth:`~minim.api.deezer.UsersAPI.get_user` and
           make a request to the Deezer API.
        """
        return self.users.get_user()["id"]

    def get_country_info(self) -> dict[str, Any]:
        """
        Get configuration and availability information for the Deezer
        API in the current country.

        Returns
        -------
        info : dict[str, Any]
            Configuration and availability information.

            .. admonition:: Sample response
               :class: dropdown:

               .. code::

                  {
                    "ads": {
                      "audio": {
                        "default": {
                          "interval": <int>,
                          "start": <int>,
                          "unit": <str>
                        }
                      },
                      "big_native_ads_home": {
                        "android": {
                          "enabled": <bool>
                        },
                        "android_tablet": {
                          "enabled": <bool>
                        },
                        "ipad": {
                          "enabled": <bool>
                        },
                        "iphone": {
                          "enabled": <bool>
                        }
                      },
                      "display": {
                        "interstitial": {
                          "interval": <int>,
                          "start": <int>,
                          "unit": <str>
                        }
                      }
                    },
                    "country": <str>,
                    "country_iso": <str>,
                    "has_podcasts": <bool>,
                    "hosts": {
                      "images": <str>,
                      "stream": <str>
                    },
                    "lyrics_available": <bool>,
                    "offers": [],
                    "open": <bool>,
                    "pop": <str>,
                    "upload_token": <str>,
                    "upload_token_lifetime": <int>,
                    "user_token": <str>
                  }
        """
        return self._request("GET", "infos").json()

    def set_access_token(
        self,
        access_token: str | None,
        /,
        *,
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

        expires_at : str or datetime.datetime; keyword-only; optional
            Expiration time of the access token. If a string, it must be
            in ISO 8601 format (:code:`%Y-%m-%dT%H:%M:%SZ`).
        """
        if access_token is None and self._auth_flow is not None:
            raise ValueError(
                "`access_token` cannot be None when using the "
                f"{self._OAUTH_AUTH_FLOWS[self._auth_flow]}."
            )
        self._access_token = access_token
        self._refresh_token = None
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
        app_id: str | None = None,
        app_secret: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        permissions: str | set[str] = "",
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
            Authorization flow.

            **Valid values**:

            .. container::

               * :code:`None` – No authentication.
               * :code:`"auth_code"` – Authorization Code Flow.
               * :code:`"implicit"` – Implicit Grant Flow.

        app_id : str; keyword-only; optional
            Application ID. Required unless set as system environment
            variable :code:`DEEZER_API_APP_ID`.

        app_secret : str; keyword-only; optional
            Application secret. Required for the Authorization Code flow
            unless set as system environment variable
            :code:`DEEZER_API_APP_SECRET`.

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
            Redirect URI. Required for the Authorization Code and
            Implicit Grant flows.

        permissions : str or set[str]; keyword-only; optional
            Permissions requested by the client to access user
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
            default web browser for the Authorization Code  and Implicit
            Grant flows. If :code:`False`, the URL is printed to the
            terminal.

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

        if authorization_flow is None and permissions:
            warnings.warn(
                "Permissions were specified in the `permissions` "
                "parameter, but the unauthenticated client does not"
                "support permissions."
            )
            permissions = ""
        self._permissions = (
            permissions
            if isinstance(permissions, set)
            else set(
                permissions.split()
                if isinstance(permissions, str)
                else permissions
            )
        )

        if app_id is None or app_secret is None:
            app_id = os.environ.get(f"{self._ENV_VAR_PREFIX}_APP_ID")
            app_secret = os.environ.get(f"{self._ENV_VAR_PREFIX}_APP_SECRET")
        if app_id is None and authorization_flow is not None:
            raise ValueError(
                "An application ID must be provided via the `app_id` "
                "parameter for the "
                f"{self._OAUTH_AUTH_FLOWS[authorization_flow]}."
            )
        self._app_id = app_id
        if (
            authorization_flow in {"auth_code", "client_credentials"}
        ) and not app_secret:
            raise ValueError(
                f"The {self._OAUTH_AUTH_FLOWS[authorization_flow]} "
                "requires an application secret to be provided via the "
                "`app_secret` parameter."
            )
        self._app_secret = app_secret
        self._user_identifier = user_identifier

        has_redirect = redirect_uri is not None
        if authorization_flow is not None:
            if not has_redirect:
                raise ValueError(
                    f"The {self._OAUTH_AUTH_FLOWS[authorization_flow]} "
                    "requires a redirect URI to be provided via the "
                    "`redirect_uri` parameter."
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
            if redirect_handler is not None:
                if redirect_handler not in self._REDIRECT_HANDLERS:
                    handlers_str = "', '".join(sorted(self._REDIRECT_HANDLERS))
                    if handlers_str:
                        handlers_str = f", '{handlers_str}'"
                    raise ValueError(
                        f"Invalid redirect handler {redirect_handler!r}. "
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
                    "`redirect_uri` parameter, but the unauthenticated "
                    "client does not use redirects."
                )
            self._redirect_uri = None
            self._redirect_handler = None

        self._open_browser = open_browser
        self._store_tokens = store_tokens

        if authenticate and authorization_flow is not None:
            self._obtain_access_token()
