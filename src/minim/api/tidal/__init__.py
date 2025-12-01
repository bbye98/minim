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
from ._private_api.albums import PrivateAlbumsAPI
from ._private_api.artists import PrivateArtistsAPI
from ._private_api.mixes import PrivateMixesAPI

# from ._private_api.pages import PrivatePagesAPI
# from ._private_api.playlists import PrivatePlaylistsAPI
# from ._private_api.tracks import PrivateTracksAPI
from ._private_api.users import PrivateUsersAPI
# from ._private_api.videos import PrivateVideosAPI

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
    "PrivateArtistsAPI",
    "PrivateMixesAPI",
    # "PrivatePagesAPI",
    # "PrivatePlaylistsAPI",
    # "PrivateTracksAPI",
    "PrivateUsersAPI",
    # "PrivateVideosAPI",
]
