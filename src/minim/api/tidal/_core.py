from collections.abc import Collection
from datetime import datetime
from functools import cached_property
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
        """ """
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
        #: User Collections, User Entitlements, User Recommendations, and Users API endpoints for the TIDAL API.
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

    @cached_property
    def my_profile(self) -> dict[str, Any] | None:
        """
        Current user's profile.

        .. note::

           Accessing this property for the first time may call
           :meth:`~minim.api.tidal.UsersAPI.get_my_profile` and
           make a request to the TIDAL API.
        """
        if self._flow != "client_credentials":
            return self.users.get_my_profile()

    def set_access_token(
        self,
        access_token: str,
        /,
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

        refresh_token : str, keyword-only, optional
            Refresh token accompanying the access token in
            `access_token`. If not provided, the user will be
            reauthorized when the access token expires.

        expiry : str or datetime.datetime, keyword-only, optional
            Expiry of the access token in `access_token`. If provided
            as a string, it must be in ISO 8601 format
            (:code:`%Y-%m-%dT%H:%M:%SZ`).
        """
        super().set_access_token(
            access_token, refresh_token=refresh_token, expiry=expiry
        )

    def _get_user_identifier(self) -> str:
        """
        Assign the TIDAL user ID as the user identifier for the current
        account.
        """
        return self.my_profile["data"]["id"]

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

        ...  # TODO
