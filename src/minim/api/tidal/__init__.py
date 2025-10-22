from ._core import TIDALAPI
from ._api.albums import AlbumsAPI
from ._api.artists import ArtistsAPI
from ._api.artworks import ArtworksAPI
from ._api.playlists import PlaylistsAPI
from ._api.providers import ProvidersAPI
from ._api.search import SearchAPI
from ._api.tracks import TracksAPI
from ._api.users import UsersAPI
from ._api.videos import VideosAPI

__all__ = [
    "TIDALAPI",
    "AlbumsAPI",
    "ArtistsAPI",
    "ArtworksAPI",
    "PlaylistsAPI",
    "ProvidersAPI",
    "SearchAPI",
    "TracksAPI",
    "UsersAPI",
    "VideosAPI",
]
