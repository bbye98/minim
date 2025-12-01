from abc import abstractmethod
from datetime import datetime
import time
from typing import TYPE_CHECKING, Any
import warnings

from .._shared import OAuth2APIClient, TTLCache
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
from ._private_api.mixes import PrivateMixesAPI
from ._private_api.users import PrivateUsersAPI

if TYPE_CHECKING:
    import httpx


class _BaseTIDALAPI(OAuth2APIClient):
    """
    Base class for TIDAL API clients.
    """

    _ENV_VAR_PREFIX: str
    _FLOWS: set[str]
    _QUAL_NAME: str
    _SCOPES: set[str]
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
            return cls._SCOPES.copy()

        # Return scopes containing a substring
        if isinstance(matches, str):
            return {scope for scope in cls._SCOPES if matches in scope}

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
            One or more TIDAL IDs, provided as an integer, a string, or
            a list of integers and/or strings.
        """
        if not isinstance(tidal_ids, int) and not tidal_ids:
            raise ValueError("At least one TIDAL ID must be specified.")

        if isinstance(tidal_ids, str):
            if not tidal_ids.isdigit():
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
    def _get_user_identifier(self) -> str:
        """
        Assign the TIDAL user ID as the user identifier for the current
        account.
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
        Resolve or validate a country code for a TIDAL API request.

        Parameters
        ----------
        country_code : str; positional-only
            ISO 3166-1 alpha-2 country code. If :code:`None`, the country
            associated with the current user account is used.
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

    _ENV_VAR_PREFIX = "TIDAL_API"
    _FLOWS = {"pkce", "client_credentials"}
    _QUAL_NAME = f"minim.api.{_BaseTIDALAPI._PROVIDER.lower()}.{__qualname__}"
    _SCOPES = {
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
    _VERSION = "1.0.5"
    BASE_URL = "https://openapi.tidal.com/v2"

    def __init__(
        self,
        *,
        flow: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        scopes: str | set[str] = "",
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
        flow : str; keyword-only
            Authorization flow.

            .. container::

               **Valid values**:

               * :code:`"pkce"` – Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` – Client Credentials Flow.

        client_id : str; keyword-only; optional
            Client ID. Must be provided unless it is set as system
            environment variable :code:`TIDAL_API_CLIENT_ID` or stored
            in Minim's local token storage.

        client_secret : str; keyword-only; optional
            Client secret. Required for the Client Credentials flow and
            must be provided unless it is set as system environment
            variable :code:`TIDAL_API_CLIENT_SECRET` or stored in
            Minim's local token storage.

        user_identifier : str; keyword-only; optional
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

        redirect_uri : str; keyword-only; optional
            Redirect URI. Required for the Authorization Code and
            Authorization Code with PKCE flows. If the host is not
            :code:`localhost` or :code:`127.0.0.1`, redirect handling is
            not available.

        scopes : str or set[str]; keyword-only; optional
            Authorization scopes the client requests to access user
            resources.

            .. seealso::

               :meth:`resolve_scopes` – Get a set of scopes to request,
               filtered by substrings.

        access_token : str; keyword-only; optional
            Access token. If provided or found in Minim's local token
            storage, the authorization process is bypassed. If provided,
            all other relevant keyword parameters should also be
            specified to enable automatic token refresh upon expiration.

        refresh_token : str; keyword-only; optional
            Refresh token accompanying the access token in
            `access_token`. If not provided, the user will be
            reauthorized via the authorization flow in `flow` when the
            access token expires.

        expiry : str or datetime.datetime; keyword-only; optional
            Expiry of the access token in `access_token`. If provided as
            a string, it must be in ISO 8601 format
            (:code:`%Y-%m-%dT%H:%M:%SZ`).

        backend : str; keyword-only; optional
            Backend to handle redirects during the authorization flow.

            .. container::

               **Valid values**:

               * :code:`None` – Manually paste the redirect URL into
                 the terminal.
               * :code:`"http.server"` – Simple HTTP server.
               * :code:`"playwright"` – Playwright Firefox browser.

        browser : bool; keyword-only; default: :code:`False`
            Whether to automatically open the authorization URL in the
            default web browser for the Authorization Code with PKCE
            flow. If :code:`False`, the authorization URL is printed to
            the terminal.

        cache : bool; keyword-only; default: :code:`True`
            Whether to enable an in-memory time-to-live (TTL) cache with
            a least recently used (LRU) eviction policy for this client.
            If :code:`True`, responses from semi-static endpoints are
            cached for between 10 minutes and 1 day, depending on their
            expected update frequency.

            .. seealso::

               :meth:`clear_cache` – Clear specific or all cache
               entries for this API client.

        store : bool; keyword-only; default: :code:`True`
            Whether to enable Minim's local token storage for
            this client. If :code:`True`, newly acquired access tokens
            and related information are stored. If :code:`False`, the
            client will not retrieve or store access tokens.

            .. seealso::

               :meth:`remove_tokens` – Remove specific or all stored
               access tokens for this API client.
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
            flow=flow,
            client_id=client_id,
            client_secret=client_secret,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            scopes=scopes,
            access_token=access_token,
            refresh_token=refresh_token,
            expiry=expiry,
            backend=backend,
            browser=browser,
            cache=cache,
            store=store,
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
            if self._flow == "client_credentials"
            else self.users.get_my_profile()["data"]
        )

    def _get_user_identifier(self) -> str:
        """
        Assign the TIDAL user ID as the user identifier for the current
        account.

        .. note::

           Invoking this method may call
           :meth:`~minim.api.tidal.UsersAPI.get_my_profile` and
           make a request to the TIDAL API.
        """
        return self.users.get_my_profile()["data"]["id"]

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
        if self._expiry and datetime.now() > self._expiry:
            self._refresh_access_token()

        resp = self._client.request(method, endpoint, **kwargs)
        status = resp.status_code
        if 200 <= status < 300:
            return resp

        if status == 401 and not self._expiry and retry:
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

    _ENV_VAR_PREFIX = "PRIVATE_TIDAL_API"
    _FLOWS = {"pkce", "device"}
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
    _QUAL_NAME = f"minim.api.{_BaseTIDALAPI._PROVIDER.lower()}.{__qualname__}"
    _REDIRECT_URIS = {"tidal://login/auth", "https://tidal.com/login/auth"}
    _SCOPES = {"r_usr", "w_usr", "w_sub"}
    _TRUSTED_DEVICE = True
    _VERSION = "2025.11.19"
    DEVICE_AUTH_URL = "https://auth.tidal.com/v1/oauth2/device_authorization"
    BASE_URL = "https://api.tidal.com"
    RESOURCE_URL = "https://resources.tidal.com"

    def __init__(
        self,
        *,
        flow: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str = "tidal://login/auth",
        scopes: str | set[str] = "",
        access_token: str | None = None,
        refresh_token: str | None = None,
        expiry: str | datetime | None = None,
        backend: str | None = None,
        browser: bool = False,
        cache: bool = True,
        store: bool = True,
    ) -> None:
        """ """
        # Initialize subclasses for endpoint groups
        #: Albums API endpoints for the private TIDAL API.
        self.albums: PrivateAlbumsAPI = PrivateAlbumsAPI(self)
        #: Artists API endpoints for the private TIDAL API.
        self.artists: PrivateArtistsAPI = PrivateArtistsAPI(self)
        #: Mixes API endpoints for the private TIDAL API.
        self.mixes: PrivateMixesAPI = PrivateMixesAPI(self)
        #: Users API endpoints for the private TIDAL API.
        self.users: PrivateUsersAPI = PrivateUsersAPI(self)

        super().__init__(
            flow=flow,
            client_id=client_id,
            client_secret=client_secret,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            scopes=scopes,
            access_token=access_token,
            refresh_token=refresh_token,
            expiry=expiry,
            backend=backend,
            browser=browser,
            cache=cache,
            store=store,
        )
        self._client.headers["x-tidal-client-version"] = self._VERSION

    @classmethod
    def build_artwork_url(
        cls,
        uuid: str,
        /,
        item_type: str | None = None,
        *,
        animated: bool = False,
        dimensions: int | str | tuple[int | str, int | str] | None = None,
    ) -> str:
        """
        Build the URL for a TIDAL artwork.

        Parameters
        ----------
        uuid : str; positional-only
            TIDAL artwork UUID.

        item_type : str; positional-only; optional
            Type of item the artwork belongs to. If provided, the
            desired dimensions specified in `dimensions` are validated
            against the allowed dimensions for the item type.

            **Valid values**: :code:`"artist"`, :code:`"album"`,
            :code:`"playlist"`, :code:`"userProfile"`, :code:`"video"`.

        animated : bool; keyword-only; default: :code:`False`
            Whether the artwork is animated.

        dimensions : int, str, or tuple[int | str, int | str]; \
        keyword-only; optional
            Dimensions of the artwork. If not specified, the original
            dimensions (:code:`"origin"`) are used.

            **Examples**: :code:`1280`, :code:`"1280"`,
            :code:`"1280x1280"`, :code:`(640, 360)`,
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
                ) != 2 or any(not dim.isdigit() for dim in split_dimensions):
                    raise ValueError(f"Invalid dimensions {dimensions!r}.")
            elif dimensions.isdigit():
                dimensions = f"{dimensions}x{dimensions}"
            else:
                raise ValueError(f"Invalid dimensions {dimensions!r}.")
        elif isinstance(dimensions, tuple | list) and len(dimensions) == 2:
            for ax, dim in zip(("width", "height"), dimensions):
                if isinstance(dim, str):
                    if not dim.isdigit():
                        raise ValueError(f"Invalid {ax} {dim!r}.")
                elif not isinstance(dim, int):
                    raise ValueError(f"Invalid {ax} {dim!r}.")
            dimensions = f"{dimensions[0]}x{dimensions[1]}"
        else:
            raise ValueError(f"Invalid dimensions {dimensions!r}.")
        if item_type is not None:
            if item_type[-1] == "s":
                item_type = item_type[:-1]
            if item_type not in cls._IMAGE_SIZES:
                raise ValueError(f"Invalid item type {item_type!r}.")
            if dimensions not in (sizes := cls._IMAGE_SIZES[item_type]):
                _sizes = "', '".join(sorted(sizes))
                raise ValueError(
                    f"Invalid dimensions {dimensions!r} for a(n) "
                    f"{item_type} {cls._IMAGE_TYPES[item_type]}. "
                    f"Valid values: '{_sizes}'."
                )
        return (
            f"{PrivateTIDALAPI.RESOURCE_URL}/{media_type}"
            f"/{uuid.replace('-', '/')}/{dimensions}{extension}"
        )

    @staticmethod
    def _prepare_tidal_ids(
        tidal_ids: str | list[str], /, *, limit: int = 500
    ) -> str:
        """
        Stringify a list of TIDAL IDs into a comma-delimited string.

        Parameters
        ----------
        tidal_ids : int, str, or list[str]; positional-only
            Comma-delimited string or list containing TIDAL IDs.

        limit : int; keyword-only, default: :code:`500`
            Maximum number of TIDAL IDs that can be sent in the
            request.

        Returns
        -------
        tidal_ids : str
            Comma-delimited string containing TIDAL IDs.
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
                if not id_.isdigit():
                    raise ValueError(f"Invalid TIDAL ID {id_!r}.")
            else:
                raise ValueError(f"Invalid TIDAL ID {id_!r}.")
        return ",".join(tidal_ids)

    @property
    def _my_country_code(self) -> str:
        """
        Current user's country code.

        .. note::

           Accessing this property may call :meth:`get_country_code` or
           :meth:`~minim.api.tidal.PrivateUsersAPI.get_my_profile` and
           make requests to the private TIDAL API.
        """
        country_code = self._my_profile.get(
            "countryCode", self.get_country_code()["countryCode"]
        )
        if not country_code:
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
           :meth:`~minim.api.tidal.PrivateUsersAPI.get_my_profile` and
           make a request to the private TIDAL API.
        """
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

    def _get_user_identifier(self):
        """
        Assign the TIDAL user ID as the user identifier for the current
        account.

        .. note::

           Invoking this method may call
           :meth:`~minim.api.tidal.PrivateUsersAPI.get_my_profile` and
           make a request to the private TIDAL API.
        """
        return self._token_extras.get("user_id", self._my_profile["userId"])

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
        if self._expiry and datetime.now() > self._expiry:
            self._refresh_access_token()

        resp = self._client.request(method, endpoint, **kwargs)
        status = resp.status_code
        if 200 <= status < 300:
            return resp

        if status == 401 and not self._expiry and retry:
            self._refresh_access_token()
            return self._request(method, endpoint, retry=False, **kwargs)
        error = resp.json()
        raise RuntimeError(
            f"{error['status']}.{error['subStatus']} – {error['userMessage']}"
        )
