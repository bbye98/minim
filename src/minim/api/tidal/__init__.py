from ._core import TIDALAPI, PrivateTIDALAPI
from ._api.albums import AlbumsAPI
from ._api.artists import ArtistsAPI
from ._api.artworks import ArtworksAPI
from ._api.playlists import PlaylistsAPI
from ._api.providers import ProvidersAPI
from ._api.search import SearchAPI
from ._api.tracks import TracksAPI
from ._api.users import UsersAPI
from ._api.videos import VideosAPI
from ._private_api.albums import AlbumsAPI as PrivateAlbumsAPI

# from ._private_api.artists import ArtistsAPI as PrivateArtistsAPI
# from ._private_api.mixes import MixesAPI as PrivateMixesAPI
# from ._private_api.pages import PagesAPI as PrivatePagesAPI
# from ._private_api.playlists import PlaylistsAPI as PrivatePlaylistsAPI
# from ._private_api.tracks import TracksAPI as PrivateTracksAPI
from ._private_api.users import UsersAPI as PrivateUsersAPI
# from ._private_api.videos import VideosAPI as PrivateVideosAPI

__all__ = [
    "TIDALAPI",
    "PrivateTIDALAPI",
    "AlbumsAPI",
    "ArtistsAPI",
    "ArtworksAPI",
    "PlaylistsAPI",
    "ProvidersAPI",
    "SearchAPI",
    "TracksAPI",
    "UsersAPI",
    "VideosAPI",
    "PrivateAlbumsAPI",
    # "PrivateArtistsAPI",
    # "PrivateMixesAPI",
    # "PrivatePagesAPI",
    # "PrivatePlaylistsAPI",
    # "PrivateTracksAPI",
    "PrivateUsersAPI",
    # "PrivateVideosAPI",
]
