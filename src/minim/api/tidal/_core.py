from collections.abc import Collection
from datetime import datetime
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


class TIDALAPI(OAuth2APIClient):
    """
    TIDAL API client.
    """

    _ENV_VAR_PREFIX = "TIDAL_API"
    _FLOWS = {"pkce", "client_credentials"}
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
