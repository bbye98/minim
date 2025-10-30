from collections.abc import Collection
from datetime import datetime
import time
from typing import TYPE_CHECKING, Any
import warnings

from .._shared import OAuth2APIClient
from ._api.albums import AlbumsAPI
from ._api.artists import ArtistsAPI
from ._api.artworks import ArtworksAPI
from ._api.playlists import PlaylistsAPI
from ._api.providers import ProvidersAPI
from ._api.search import SearchAPI
from ._api.tracks import TracksAPI
from ._api.users import UsersAPI
from ._api.videos import VideosAPI

if TYPE_CHECKING:
    import httpx


class TIDALAPI(OAuth2APIClient):
    """
    TIDAL API client.
    """

    _ENV_VAR_PREFIX = "TIDAL_API"
    _FLOWS = {"pkce", "client_credentials"}
    _PROVIDER = "TIDAL"
    _QUAL_NAME = f"minim.api.{_PROVIDER.lower()}.{__qualname__}"
    AUTH_URL = "https://login.tidal.com/authorize"
    BASE_URL = "https://openapi.tidal.com/v2"
    TOKEN_URL = "https://auth.tidal.com/v1/oauth2/token"

    def __init__(
        self,
        *,
        flow: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        access_token: str | None = None,
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
            Authorization flow.

            .. container::

               **Valid values**:

               * :code:`"pkce"` – Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` – Client Credentials Flow.

        client_id : str, keyword-only, optional
            Client ID. Must be provided unless it is set as system
            environment variable :code:`TIDAL_API_CLIENT_ID` or stored
            in Minim's local token storage.

        client_secret : str, keyword-only, optional
            Client secret. Required for the Client Credentials flow and
            must be provided unless it is set as system environment
            variable :code:`TIDAL_API_CLIENT_SECRET` or stored in
            Minim's local token storage.

        redirect_uri : str, keyword-only, optional
            Redirect URI. Required for the Authorization Code and
            Authorization Code with PKCE flows. If the host is not
            :code:`localhost` or :code:`127.0.0.1`, redirect handling is
            not available.

        access_token : str, keyword-only, optional
            Access token. If provided or found in Minim's local token
            storage, the authorization process is bypassed. If provided,
            all other relevant keyword arguments should also be
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
            Whether to automatically open the authorization URL in the
            default web browser for the Authorization Code with PKCE
            flow. If :code:`False`, the authorization URL is printed to
            the terminal.

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

               :meth:`remove_token` – Remove a specific stored access
               token for this API client.

               :meth:`remove_all_tokens` – Remove all stored access
               tokens for this API client.

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
            hash of the client ID, authorization flow, and the Spotify
            user ID.

            Prepending the identifier with a tilde (:code:`~`) skips
            token retrieval from local storage and forces a
            reauthorization.
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
            redirect_uri=redirect_uri,
            access_token=access_token,
            refresh_token=refresh_token,
            expiry=expiry,
            backend=backend,
            browser=browser,
            cache=cache,
            store=store,
            user_identifier=user_identifier,
        )

    @staticmethod
    def _validate_tidal_ids(
        tidal_ids: int | str | Collection[int | str],
        /,
        *,
        _recursive: bool = True,
    ) -> None:
        """
        Validate one or more TIDAL IDs.

        Parameters
        ----------
        tidal_ids : int, str, or Collection[int | str], positional-only
            One or more TIDAL IDs, provided as an integer, a string, or
            a collection of integers and/or strings.
        """
        if not isinstance(tidal_ids, int) and not tidal_ids:
            raise ValueError("At least one TIDAL ID must be specified.")

        if isinstance(tidal_ids, str):
            if not tidal_ids.isdigit():
                raise ValueError(f"Invalid TIDAL ID {tidal_ids!r}.")
        elif not isinstance(tidal_ids, int):
            if _recursive:
                if not isinstance(tidal_ids, Collection):
                    raise ValueError("TIDAL IDs must be integers or strings.")
                for tidal_id in tidal_ids:
                    TIDALAPI._validate_tidal_ids(tidal_id, _recursive=False)
            else:
                raise ValueError(f"Invalid TIDAL ID {tidal_ids!r}.")

    @property
    def _my_country_code(self) -> str:
        """
        Current user's country code.

        .. note::

           Accessing this property may call
           :meth:`~minim.api.tidal.UsersAPI.get_my_profile` and
           make a request to the TIDAL API.
        """
        country_code = (
            None
            if self._flow == "client_credentials"
            else (
                self.users.get_my_profile()["data"]
                .get("attributes", {})
                .get("country")
            )
        )
        if country_code is None:
            raise RuntimeError(
                "Unable to determine the country associated with the "
                "current user account. A ISO 3166-1 alpha-2 country "
                "code must be provided explicitly."
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
        method : str, positional-only
            HTTP method.

        endpoint : str, positional-only
            TIDAL API endpoint.

        retry : bool, keyword-only, default: :code:`True`
            Whether to retry the request if the first attempt returns a
            :code:`401 Unauthorized` or :code:`429 Too Many Requests`.

        **kwargs : dict[str, Any]
            Keyword arguments to pass to :meth:`httpx.Client.request`.

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

    def _resolve_country_code(
        self, country_code: str | None, /, params: dict[str, Any]
    ) -> None:
        """
        Resolve or validate a country code for a TIDAL API request.

        Parameters
        ----------
        country_code : str, positional-only
            ISO 3166-1 alpha-2 country code. If :code:`None`, the country
            associated with the current user account is used.
        """
        if country_code is None:
            params["countryCode"] = self._my_country_code
        else:
            if (
                not isinstance(country_code, str)
                or len(country_code) != 2
                or not country_code.isalpha()
            ):
                raise ValueError(
                    f"{country_code!r} is not a valid ISO 3166-1 "
                    "alpha-2 country code."
                )
            params["countryCode"] = country_code
