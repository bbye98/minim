from abc import abstractmethod
from datetime import datetime
import time
from typing import TYPE_CHECKING, Any
import warnings

from .._shared import APIClient, OAuth2APIClient, TTLCache
from ._api.albums import AlbumsAPI
from ._api.artists import ArtistsAPI
from ._api.artworks import ArtworksAPI
from ._api.playlists import PlaylistsAPI
from ._api.providers import ProvidersAPI
from ._api.search import SearchAPI
from ._api.tracks import TracksAPI
from ._api.users import UsersAPI
from ._api.videos import VideosAPI
from ._private_api.albums import PrivateAlbumsAPI
from ._private_api.artists import PrivateArtistsAPI
from ._private_api.feed import PrivateFeedAPI
from ._private_api.mixes import PrivateMixesAPI
from ._private_api.pages import PrivatePagesAPI
from ._private_api.playlists import PrivatePlaylistsAPI
from ._private_api.search import PrivateSearchAPI
from ._private_api.tracks import PrivateTracksAPI
from ._private_api.users import PrivateUsersAPI
from ._private_api.videos import PrivateVideosAPI

if TYPE_CHECKING:
    import httpx


class _BaseTIDALAPI(OAuth2APIClient):
    """
    Base class for TIDAL API clients.
    """

    _ALLOWED_AUTH_FLOWS: set[str]
    _ALLOWED_SCOPES: set[str]
    _ENV_VAR_PREFIX: str
    _QUAL_NAME: str
    _VERSION: str
    AUTH_URL: str
    BASE_URL: str

    _PROVIDER = "TIDAL"
    AUTH_URL = "https://login.tidal.com/authorize"
    TOKEN_URL = "https://auth.tidal.com/v1/oauth2/token"

    @classmethod
    def resolve_scopes(
        cls, matches: str | list[str] | None = None
    ) -> set[str]:
        """
        Resolve one or more scope categories or substrings into a set of
        scopes.

        Parameters
        ----------
        matches : str or list[str]; optional
            Substrings to match in the available scopes. If not
            specified, all available scopes are returned.

        Returns
        -------
        scopes : set[str]
            Authorization scopes.
        """
        # Return all scopes if no matches are provided
        if matches is None:
            return cls._ALLOWED_SCOPES.copy()

        # Return scopes containing a substring
        if isinstance(matches, str):
            return {scope for scope in cls._ALLOWED_SCOPES if matches in scope}

        # Recursively gather scopes for multiple
        # categories/substrings
        return {
            scope for match in matches for scope in cls.resolve_scopes(match)
        }

    @staticmethod
    def _validate_tidal_ids(
        tidal_ids: int | str | list[int | str], /, *, _recursive: bool = True
    ) -> None:
        """
        Validate one or more TIDAL IDs.

        Parameters
        ----------
        tidal_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs.
        """
        if not isinstance(tidal_ids, int) and not tidal_ids:
            raise ValueError("At least one TIDAL ID must be specified.")

        if isinstance(tidal_ids, str):
            if not tidal_ids.isdecimal():
                raise ValueError(f"Invalid TIDAL ID {tidal_ids!r}.")
        elif not isinstance(tidal_ids, int):
            if _recursive:
                if not isinstance(tidal_ids, tuple | list | str):
                    raise ValueError("TIDAL IDs must be integers or strings.")
                for tidal_id in tidal_ids:
                    TIDALAPI._validate_tidal_ids(tidal_id, _recursive=False)
            else:
                raise ValueError(f"Invalid TIDAL ID {tidal_ids!r}.")

    @property
    @abstractmethod
    def _my_country_code(self) -> str:
        """
        Current user's country code.
        """
        ...

    @property
    @abstractmethod
    def _my_profile(self) -> dict[str, Any]:
        """
        Current user's profile.
        """
        ...

    @abstractmethod
    def _resolve_user_identifier(self) -> str:
        """
        Return the TIDAL user ID as the user identifier for the
        current account.
        """
        ...

    @abstractmethod
    def _request(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        retry: bool = True,
        **kwargs: dict[str, Any],
    ) -> "httpx.Response":
        """
        Make an HTTP request to a TIDAL API endpoint.

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

        endpoint : str; positional-only
            TIDAL API endpoint.

        retry : bool; keyword-only; default: :code:`True`
            Whether to retry the request if the first attempt returns a
            :code:`401 Unauthorized` or :code:`429 Too Many Requests`.

        **kwargs : dict[str, Any]
            Keyword parameters to pass to :meth:`httpx.Client.request`.

        Returns
        -------
        response : httpx.Response
            HTTP response.
        """
        ...

    def _resolve_country_code(
        self, country_code: str | None, /, params: dict[str, Any]
    ) -> None:
        """
        Resolve or validate the country code for a TIDAL API request.

        Parameters
        ----------
        country_code : str; positional-only
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.
        """
        if country_code is None:
            params["countryCode"] = self._my_country_code
        else:
            self._validate_country_code(country_code)
            params["countryCode"] = country_code


class TIDALAPI(_BaseTIDALAPI):
    """
    TIDAL API client.
    """

    _ALLOWED_AUTH_FLOWS = {"pkce", "client_credentials"}
    _ALLOWED_SCOPES = {
        "collection.read",
        "collection.write",
        "playlists.read",
        "playlists.write",
        "playback",
        "user.read",
        "recommendations.read",
        "entitlements.read",
        "search.read",
        "search.write",
    }
    _ENV_VAR_PREFIX = "TIDAL_API"
    _QUAL_NAME = f"minim.api.{_BaseTIDALAPI._PROVIDER.lower()}.{__qualname__}"
    _VERSION = "1.0.30"
    BASE_URL = "https://openapi.tidal.com/v2"

    def __init__(
        self,
        *,
        authorization_flow: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        scopes: str | set[str] = "",
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
        authorization_flow : str; keyword-only
            Authorization flow.

            .. container::

               **Valid values**:

               * :code:`"pkce"` – Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` – Client Credentials Flow.

        client_id : str; keyword-only; optional
            Client ID. Required unless set as system environment
            variable :code:`TIDAL_API_CLIENT_ID` or stored in the local
            token storage.

        client_secret : str; keyword-only; optional
            Client secret. Required for the Client Credentials flow
            unless set as system environment variable
            :code:`TIDAL_API_CLIENT_SECRET` or stored in the local token
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
            new token is obtained and stored using the TIDAL user ID
            acquired from a successful authorization.

            Prefixing the identifier with a tilde (:code:`~`) bypasses
            token retrieval, forces reauthorization, and stores the new
            token under the suffix.

        redirect_uri : str; keyword-only; optional
            Redirect URI. Required for the Authorization Code with PKCE
            flow.

        scopes : str or set[str]; keyword-only; optional
            Authorization scopes requested by the client to access user
            resources.

            .. seealso::

               :meth:`resolve_scopes` – Resolve scope categories and/or
                substrings into a set of scopes.

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

            .. container::

               **Valid values**:

               * :code:`None` – Manually paste the redirect URL into
                 the terminal.
               * :code:`"http.server"` – Run a simple HTTP server.
               * :code:`"playwright"` – Open a Playwright Firefox
                 browser.

        open_browser : bool; keyword-only; default: :code:`False`
            Whether to automatically open the authorization URL in the
            default web browser for the Authorization Code with PKCE
            flow. If :code:`False`, the URL is printed to the terminal.

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

               :meth:`remove_tokens` – Remove specific or all stored
               access tokens for this client.
        """
        # Initialize subclasses for endpoint groups
        #: Albums API endpoints for the TIDAL API.
        self.albums: AlbumsAPI = AlbumsAPI(self)
        #: Artists and Artist Roles API endpoints for the TIDAL API.
        self.artists: ArtistsAPI = ArtistsAPI(self)
        #: Artworks API endpoints for the TIDAL API.
        self.artworks: ArtworksAPI = ArtworksAPI(self)
        #: Playlists API endpoints for the TIDAL API.
        self.playlists: PlaylistsAPI = PlaylistsAPI(self)
        #: Providers API endpoints for the TIDAL API.
        self.providers: ProvidersAPI = ProvidersAPI(self)
        #: Search Results and Search Suggestions API endpoints for the TIDAL API.
        self.search: SearchAPI = SearchAPI(self)
        #: Tracks API endpoints for the TIDAL API.
        self.tracks: TracksAPI = TracksAPI(self)
        #: User Collections, User Entitlements, User Recommendations,
        #: and Users API endpoints for the TIDAL API.
        self.users: UsersAPI = UsersAPI(self)
        #: Videos API endpoints for the TIDAL API.
        self.videos: VideosAPI = VideosAPI(self)

        super().__init__(
            authorization_flow=authorization_flow,
            client_id=client_id,
            client_secret=client_secret,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            scopes=scopes,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            redirect_handler=redirect_handler,
            open_browser=open_browser,
            enable_cache=enable_cache,
            store_tokens=store_tokens,
        )

    @property
    def _my_country_code(self) -> str:
        """
        Current user's country code.

        .. note::

           Accessing this property may call
           :meth:`~minim.api.tidal.UsersAPI.get_my_profile` and
           make a request to the TIDAL API.
        """
        country_code = self._my_profile.get("attributes", {}).get("country")
        if country_code is None:
            raise RuntimeError(
                "Unable to determine the country associated with the "
                "current user account. A ISO 3166-1 alpha-2 country "
                "code must be provided explicitly via the "
                "`country_code` parameter."
            )
        return country_code

    @property
    def _my_profile(self) -> dict[str, Any]:
        """
        Current user's profile.

        .. note::

           Accessing this property may call
           :meth:`~minim.api.tidal.UsersAPI.get_my_profile` and
           make a request to the TIDAL API.
        """
        return (
            {}
            if self._auth_flow == "client_credentials"
            else self.users.get_my_profile()["data"]
        )

    def _resolve_user_identifier(self) -> str | None:
        """
        Return the TIDAL user ID as the user identifier for the
        current account.

        .. note::

           Invoking this method may call
           :meth:`~minim.api.tidal.UsersAPI.get_my_profile` and
           make a request to the TIDAL API.
        """
        return self._my_profile.get("id")

    def _request(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        retry: bool = True,
        **kwargs: dict[str, Any],
    ) -> "httpx.Response":
        """
        Make an HTTP request to a TIDAL API endpoint.

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

        endpoint : str; positional-only
            TIDAL API endpoint.

        retry : bool; keyword-only; default: :code:`True`
            Whether to retry the request if the first attempt returns a
            :code:`401 Unauthorized` or :code:`429 Too Many Requests`.

        **kwargs : dict[str, Any]
            Keyword parameters to pass to :meth:`httpx.Client.request`.

        Returns
        -------
        response : httpx.Response
            HTTP response.
        """
        if self._expires_at and datetime.now() > self._expires_at:
            self._refresh_access_token()

        resp = self._client.request(method, endpoint, **kwargs)
        status = resp.status_code
        if 200 <= status < 300:
            return resp

        if status == 401 and not self._expires_at and retry:
            self._refresh_access_token()
            return self._request(method, endpoint, retry=False, **kwargs)
        if status == 429 and retry:
            try:
                retry_after = float(resp.headers["Retry-After"]) + 1.0
            except (KeyError, ValueError):
                retry_after = 1.0
            warnings.warn(
                f"Rate limit exceeded. Retrying after {retry_after:.3f} second(s)."
            )
            time.sleep(retry_after)
            return self._request(method, endpoint, retry=False, **kwargs)
        error = resp.json()["errors"][0]
        raise RuntimeError(
            f"{status} {resp.reason_phrase} ({error['code']}) – {error['detail']}"
        )


class PrivateTIDALAPI(_BaseTIDALAPI):
    """
    Private TIDAL API client.
    """

    _ALLOWED_AUTH_FLOWS = {None, "pkce", "device"}
    _ALLOWED_SCOPES = {"r_usr", "w_usr", "w_sub"}
    _DEVICE_TYPES = {"BROWSER", "DESKTOP", "PHONE", "TV"}
    _ENV_VAR_PREFIX = "PRIVATE_TIDAL_API"
    _IMAGE_SIZES = {
        "album": {
            "1280x1280",
            "1080x1080",
            "750x750",
            "640x640",
            "320x320",
            "160x160",
            "80x80",
        },
        "artist": {"750x750", "480x480", "320x320", "160x160"},
        "playlist": {"1280x1280", "480x480", "320x320", "160x160"},
        "video": {"1280x720", "800x450", "640x360", "320x180", "160x90"},
    }
    _IMAGE_TYPES = {
        "album": "cover art",
        "artist": "profile art",
        "playlist": "cover art",
        "video": "thumbnail",
    }
    _IS_TRUSTED_DEVICE = True
    _OPTIONAL_AUTH = True
    _QUAL_NAME = f"minim.api.{_BaseTIDALAPI._PROVIDER.lower()}.{__qualname__}"
    _REDIRECT_HANDLERS = {}
    _REDIRECT_URIS = {"tidal://login/auth", "https://tidal.com/login/auth"}
    _VERSION = "2025.12.18"
    BASE_URL = "https://api.tidal.com"
    DEVICE_AUTH_URL = "https://auth.tidal.com/v1/oauth2/device_authorization"
    #: URL for image resources.
    RESOURCE_URL = "https://resources.tidal.com"

    def __init__(
        self,
        *,
        authorization_flow: str | None,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        scopes: str | set[str] = "",
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
            Authorization flow.

            .. container::

               **Valid values**:

               * :code:`None` – No authentication.
               * :code:`"pkce"` – Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"device"` – Device Authorization Flow.

        client_id : str; keyword-only; optional
            Client ID. Required unless set as system environment
            variable :code:`PRIVATE_TIDAL_API_CLIENT_ID` or stored in
            the local token storage.

        client_secret : str; keyword-only; optional
            Client secret. Required for the Client Credentials flow
            unless set as system environment variable
            :code:`PRIVATE_TIDAL_API_CLIENT_SECRET` or stored in the
            local token storage.

        user_identifier : str; keyword-only; optional
            Identifier for the user account. Used when
            :code:`store_tokens=True` to distinguish between multiple
            accounts for the same client ID and authorization flow.

            If provided, it is used with the client ID and authorization
            flow to locate a matching stored token. If none is found, a
            new token is obtained and stored under this identifier.

            If not provided, the most recently accessed token for the
            client ID and authorization flow is used. If none exists, a
            new token is obtained and stored using the TIDAL user ID
            acquired from a successful authorization.

            Prefixing the identifier with a tilde (:code:`~`) bypasses
            token retrieval, forces reauthorization, and stores the new
            token under the suffix.

        redirect_uri : str; keyword-only; optional
            Redirect URI. Required for the Authorization Code with PKCE
            flow.

            **Valid values**: :code:`"tidal://login/auth"`,
            :code:`"https://tidal.com/login/auth"`.

        scopes : str or set[str]; keyword-only; optional
            Authorization scopes requested by the client to access user
            resources.

            .. seealso::

               :meth:`resolve_scopes` – Resolve scope categories and/or
                substrings into a set of scopes.

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

        redirect_handler : None; keyword-only; optional
            Backend for handling redirects during the authorization
            flow. Redirect handling is only available for hosts
            :code:`localhost`, :code:`127.0.0.1`, or :code:`::1`.

            **Valid value**: :code:`None` – Manually paste the redirect
            URL into the terminal.

        open_browser : bool; keyword-only; default: :code:`False`
            Whether to automatically open the authorization URL in the
            default web browser for the Authorization Code with PKCE
            flow. If :code:`False`, the URL is printed to the terminal.

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

               :meth:`remove_tokens` – Remove specific or all stored
               access tokens for this client.
        """
        # Initialize subclasses for endpoint groups
        #: Albums API endpoints for the private TIDAL API.
        self.albums: PrivateAlbumsAPI = PrivateAlbumsAPI(self)
        #: Artists API endpoints for the private TIDAL API.
        self.artists: PrivateArtistsAPI = PrivateArtistsAPI(self)
        #: Feed API endpoints for the private TIDAL API.
        self.feed: PrivateFeedAPI = PrivateFeedAPI(self)
        #: Mixes API endpoints for the private TIDAL API.
        self.mixes: PrivateMixesAPI = PrivateMixesAPI(self)
        #: Pages API endpoints for the private TIDAL API.
        self.pages: PrivatePagesAPI = PrivatePagesAPI(self)
        #: Playlists API endpoints for the private TIDAL API.
        self.playlists: PrivatePlaylistsAPI = PrivatePlaylistsAPI(self)
        #: Search API endpoints for the private TIDAL API.
        self.search: PrivateSearchAPI = PrivateSearchAPI(self)
        #: Tracks API endpoints for the private TIDAL API.
        self.tracks: PrivateTracksAPI = PrivateTracksAPI(self)
        #: Users API endpoints for the private TIDAL API.
        self.users: PrivateUsersAPI = PrivateUsersAPI(self)
        #: Videos API endpoint for the private TIDAL API.
        self.videos: PrivateVideosAPI = PrivateVideosAPI(self)

        super().__init__(
            authorization_flow=authorization_flow,
            client_id=client_id,
            client_secret=client_secret,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            scopes=scopes,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            redirect_handler=redirect_handler,
            open_browser=open_browser,
            enable_cache=enable_cache,
            store_tokens=store_tokens,
        )
        self._client.headers["x-tidal-client-version"] = self._VERSION

    @classmethod
    def build_artwork_url(
        cls,
        artwork_uuid: str,
        /,
        resource_type: str | None = None,
        *,
        animated: bool = False,
        dimensions: int | str | tuple[int | str, int | str] | None = None,
    ) -> str:
        """
        Build the URL for a TIDAL artwork.

        Parameters
        ----------
        artwork_uuid : str; positional-only
            TIDAL artwork UUID.

        resource_type : str; positional-only; optional
            Type of resource the artwork belongs to. If provided, the
            specified dimensions are validated against the allowed 
            dimensions for the item type.

            **Valid values**: :code:`"artist"`, :code:`"album"`,
            :code:`"playlist"`, :code:`"userProfile"`, :code:`"video"`.

        animated : bool; keyword-only; default: :code:`False`
            Whether the artwork is animated.

        dimensions : int, str, or tuple[int | str, int | str]; \
        keyword-only; optional
            Dimensions of the artwork. Use :code:`"origin"` or leave
            blank to get artwork in its original dimensions.

            **Examples**: :code:`"origin"`, :code:`1_280`, 
            :code:`"1280"`, :code:`"1280x1280"`, :code:`(640, 360)`,
            :code:`("640", "360")`.
        """
        if animated:
            extension = ".mp4"
            media_type = "videos"
        else:
            extension = ".jpg"
            media_type = "images"
        if dimensions is None:
            dimensions = "origin"
        elif isinstance(dimensions, int):
            dimensions = f"{dimensions}x{dimensions}"
        elif isinstance(dimensions, str):
            if "x" in dimensions:
                if len(
                    split_dimensions := dimensions.split("x", maxsplit=1)
                ) != 2 or any(not dim.isdecimal() for dim in split_dimensions):
                    raise ValueError(f"Invalid dimensions {dimensions!r}.")
            elif dimensions.isdecimal():
                dimensions = f"{dimensions}x{dimensions}"
            else:
                raise ValueError(f"Invalid dimensions {dimensions!r}.")
        elif isinstance(dimensions, tuple | list) and len(dimensions) == 2:
            for ax, dim in zip(("width", "height"), dimensions):
                if isinstance(dim, str):
                    if not dim.isdecimal():
                        raise ValueError(f"Invalid {ax} {dim!r}.")
                elif not isinstance(dim, int):
                    raise ValueError(f"Invalid {ax} {dim!r}.")
            dimensions = f"{dimensions[0]}x{dimensions[1]}"
        else:
            raise ValueError(f"Invalid dimensions {dimensions!r}.")
        if resource_type is not None:
            if resource_type[-1] == "s":
                resource_type = resource_type[:-1]
            if resource_type not in cls._IMAGE_SIZES:
                resource_types_str = "', '".join(cls._IMAGE_SIZES)
                raise ValueError(
                    f"Invalid resource type {resource_type!r}. "
                    f"Valid values: '{resource_types_str}'."
                )
            if dimensions not in (sizes := cls._IMAGE_SIZES[resource_type]):
                _sizes = "', '".join(sorted(sizes))
                raise ValueError(
                    f"Invalid dimensions {dimensions!r} for a(n) "
                    f"{resource_type} {cls._IMAGE_TYPES[resource_type]}. "
                    f"Valid values: '{_sizes}'."
                )
        return (
            f"{PrivateTIDALAPI.RESOURCE_URL}/{media_type}"
            f"/{artwork_uuid.replace('-', '/')}/{dimensions}{extension}"
        )

    @staticmethod
    def _prepare_tidal_ids(
        tidal_ids: str | list[str], /, *, limit: int = 500
    ) -> str:
        """
        Normalize, validate, and serialize TIDAL IDs.

        Parameters
        ----------
        tidal_ids : int, str, or list[str]; positional-only
            Comma-separated string or list of TIDAL IDs.

        limit : int; keyword-only, default: :code:`500`
            Maximum number of TIDAL IDs that can be sent in the
            request.

        Returns
        -------
        tidal_ids : str
            Comma-separated string of TIDAL IDs.
        """
        if not tidal_ids:
            raise ValueError("At least one TIDAL ID must be specified.")

        if isinstance(tidal_ids, int):
            return str(tidal_ids)

        if isinstance(tidal_ids, str):
            return PrivateTIDALAPI._prepare_tidal_ids(
                tidal_ids.split(","), limit=limit
            )

        num_ids = len(tidal_ids)
        if num_ids > limit:
            raise ValueError(
                f"A maximum of {limit} TIDAL IDs can be sent in a request."
            )
        for idx, id_ in enumerate(tidal_ids):
            if isinstance(id_, int):
                tidal_ids[idx] = str(id_)
            elif isinstance(id_, str):
                tidal_ids[idx] = id_ = id_.strip()
                if not id_.isdecimal():
                    raise ValueError(f"Invalid TIDAL ID {id_!r}.")
            else:
                raise ValueError(f"Invalid TIDAL ID {id_!r}.")
        return ",".join(tidal_ids)

    @staticmethod
    def _prepare_uuids(
        resource_type: str,
        resource_uuids: str | list[str],
        /,
        *,
        has_prefix: bool = False,
    ) -> str:
        """
        Normalize, validate, and serialize UUIDs.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"folder"`, :code:`"playlist"`.

        resource_uuids : str or list[str]; positional-only
            UUIDs of playlists or playlist folders.

        has_prefix : bool; keyword-only; default: :code:`False`
            Whether UUIDs are prefixed with :code:`trn:{type}:`.

        Returns
        -------
        resource_uuids : str
            Comma-separated string containing UUIDs of playlists or
            playlist folders.
        """
        if not resource_uuids:
            raise ValueError(
                f"At least one {resource_type} UUID must be specified."
            )

        if isinstance(resource_uuids, str):
            return PrivateTIDALAPI._prepare_uuids(resource_uuids.split(","))
        elif isinstance(resource_uuids, tuple | list):
            for idx, uuid in enumerate(resource_uuids):
                if has_prefix:
                    if uuid.startswith(f"trn:{resource_type}:"):
                        uuid = uuid[13:]
                    else:
                        resource_uuids[idx] = f"trn:{resource_type}:{uuid}"
                APIClient._validate_uuid(uuid)
        else:
            raise TypeError(
                f"`{resource_type}_uuids` must be a comma-separated string or "
                "a list of strings."
            )

        return ",".join(resource_uuids)

    @property
    def _my_country_code(self) -> str:
        """
        Current user's country code.

        .. note::

           Accessing this property may call :meth:`get_country_code` or
           :meth:`~minim.api.tidal.PrivateUsersAPI.get_my_profile` and
           make requests to the private TIDAL API.
        """
        if self._auth_flow is None:
            return self.get_country_code()["countryCode"]
        return self._my_profile.get(
            "countryCode", self.get_country_code()["countryCode"]
        )

    @property
    def _my_profile(self) -> dict[str, Any] | None:
        """
        Current user's profile.

        .. note::

           Accessing this property may call
           :meth:`~minim.api.tidal.PrivateUsersAPI.get_my_profile` and
           make a request to the private TIDAL API.
        """
        if self._auth_flow is not None:
            return self.users.get_my_profile()

    @TTLCache.cached_method(ttl="catalog")
    def get_country_code(self) -> dict[str, str]:
        """
        Get the country code associated with the current user account.

        Returns
        -------
        country_code : dict[str, str]
            Country code.

            **Sample response**: :code:`{"countryCode": "US"}`.
        """
        return self._request("GET", "v1/country").json()

    def set_flow(
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
        Set or update the authorization flow and related information.

        .. warning::

           Calling this method replaces all existing values with the
           specified parameters. Parameters not specified explicitly
           will be overwritten by their default values.

        Parameters
        ----------
        authorization_flow : str or None; keyword-only
            OAuth 2.0 authorization flow.

            .. container::

               **Valid values**:

               * :code:`None` – No authentication.
               * :code:`"pkce"` – Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"device"` – Device Authorization Flow.

        client_id : str; keyword-only; optional
            Client ID. Required unless set as system environment
            variable :code:`PRIVATE_TIDAL_API_CLIENT_ID` or stored in
            the local token storage.

        client_secret : str; keyword-only; optional
            Client secret. Required for the Client Credentials flow
            unless set as system environment variable
            :code:`PRIVATE_TIDAL_API_CLIENT_SECRET` or stored in the
            local token storage.

        user_identifier : str; keyword-only; optional
            Identifier for the user account. Used when
            :code:`store_tokens=True` to distinguish between multiple
            accounts for the same client ID and authorization flow.

            If provided, it is used with the client ID and authorization
            flow to locate a matching stored token. If none is found, a
            new token is obtained and stored under this identifier.

            If not provided, the most recently accessed token for the
            client ID and authorization flow is used. If none exists, a
            new token is obtained and stored using the TIDAL user ID
            acquired from a successful authorization.

            Prefixing the identifier with a tilde (:code:`~`) bypasses
            token retrieval, forces reauthorization, and stores the new
            token under the suffix.

        redirect_uri : str; keyword-only; optional
            Redirect URI. Required for the Authorization Code with PKCE
            flow.

            **Valid values**: :code:`"tidal://login/auth"`,
            :code:`"https://tidal.com/login/auth"`.

        scopes : str or set[str]; keyword-only; optional
            Authorization scopes requested by the client to access user
            resources.

            .. seealso::

               :meth:`resolve_scopes` – Resolve scope categories and/or
                substrings into a set of scopes.

        redirect_handler : None; keyword-only; optional
            Backend for handling redirects during the authorization
            flow. Redirect handling is only available for hosts
            :code:`localhost`, :code:`127.0.0.1`, or :code:`::1`.

            **Valid value**: :code:`None` – Manually paste the redirect
            URL into the terminal.

        open_browser : bool; keyword-only; default: :code:`False`
            Whether to automatically open the authorization URL in the
            default web browser for the Authorization Code with PKCE
            flow. If :code:`False`, the URL is printed to the terminal.

        store_tokens : bool; keyword-only; default: :code:`True`
            Whether to enable the local token storage for this client.
            If :code:`True`, existing access tokens are retrieved when
            found in local storage, and newly acquired tokens and their
            metadata are stored for future retrieval. If :code:`False`,
            the client neither retrieves nor stores access tokens.

            .. seealso::

               :meth:`remove_tokens` – Remove specific or all stored
               access tokens for this client.

        authenticate : bool; keyword-only; default: :code:`True`
            Whether to immediately initiate the authorization
            flow to acquire an access token.

            .. important::

               Unless :meth:`set_access_token` is called immediately
               after, this should be left as :code:`True` to ensure the
               client's existing access token is compatible with the new
               authorization flow and/or scopes.
        """
        if authorization_flow is None:
            self._client.headers["x-tidal-token"] = client_id
            if "Authorization" in self._client.headers:
                del self._client.headers["Authorization"]
            self._expires_at = datetime.max
        else:
            if "x-tidal-token" in self._client.headers:
                del self._client.headers["x-tidal-token"]

        super().set_flow(
            authorization_flow,
            client_id=client_id,
            client_secret=client_secret,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            scopes=scopes,
            redirect_handler=redirect_handler,
            open_browser=open_browser,
            store_tokens=store_tokens,
            authenticate=authenticate and authorization_flow is not None,
        )

    def _resolve_user_identifier(self) -> str | None:
        """
        Return the TIDAL user ID as the user identifier for the
        current account.

        .. note::

           Invoking this method may call
           :meth:`~minim.api.tidal.PrivateUsersAPI.get_my_profile` and
           make a request to the private TIDAL API.
        """
        if self._auth_flow is not None:
            return self._token_extras.get(
                "user_id", self._my_profile["userId"]
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        retry: bool = True,
        **kwargs: dict[str, Any],
    ) -> "httpx.Response":
        """
        Make an HTTP request to a private TIDAL API endpoint.

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

        endpoint : str; positional-only
            Private TIDAL API endpoint.

        retry : bool; keyword-only; default: :code:`True`
            Whether to retry the request if the first attempt returns a
            :code:`401 Unauthorized`.

        **kwargs : dict[str, Any]
            Keyword parameters to pass to :meth:`httpx.Client.request`.

        Returns
        -------
        response : httpx.Response
            HTTP response.
        """
        if self._expires_at and datetime.now() > self._expires_at:
            self._refresh_access_token()

        if self._auth_flow == "device" and "r_usr" not in self._scopes:
            raise RuntimeError(
                "The 'r_usr' scope is required when using the private "
                "TIDAL API with the Device Authorization Flow."
            )

        resp = self._client.request(method, endpoint, **kwargs)
        status = resp.status_code
        if 200 <= status < 300:
            return resp

        if status == 401 and not self._expires_at and retry:
            self._refresh_access_token()
            return self._request(method, endpoint, retry=False, **kwargs)
        error = resp.json()
        if isinstance(error, str):
            raise RuntimeError(f"{resp.status_code} {error}")
        if "status" in error:
            if "subStatus" in error:
                raise RuntimeError(
                    f"{error['status']}.{error['subStatus']} – {error['userMessage']}"
                )
            if "path" in error:
                raise RuntimeError(
                    f"{error['status']} {error['error']} – {error['path']}"
                )
            raise RuntimeError(
                f"{error['status']} {error['title']} – {error['detail']}"
            )
        raise RuntimeError(
            f"{error['httpStatus']}.{error['subStatus']} {error['error']} – {error['description']}"
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
                f"{self._QUAL_NAME}.{endpoint_method}() requires "
                f"user authentication via an OAuth 2.0 authorization "
                "flow."
            )

    def _require_subscription(self, endpoint_method: str, /) -> None:
        """ """
        if not self.users.get_user_subscription().get("premiumAccess", False):
            raise RuntimeError(
                f"{self._QUAL_NAME}.{endpoint_method}() requires "
                "an active TIDAL streaming plan."
            )
