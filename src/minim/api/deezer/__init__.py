from ._core import DeezerAPI
from ._api.albums import AlbumsAPI
from ._api.artists import ArtistsAPI
from ._api.charts import ChartsAPI
from ._api.editorial import EditorialAPI
from ._api.episodes import EpisodesAPI
from ._api.genres import GenresAPI
from ._api.playlists import PlaylistsAPI
from ._api.podcasts import PodcastsAPI
from ._api.radios import RadiosAPI
from ._api.search import SearchAPI
from ._api.tracks import TracksAPI
from ._api.users import UsersAPI

__all__ = [
    "DeezerAPI",
    "AlbumsAPI",
    "ArtistsAPI",
    "ChartsAPI",
    "EditorialAPI",
    "EpisodesAPI",
    "GenresAPI",
    "PlaylistsAPI",
    "PodcastsAPI",
    "RadiosAPI",
    "SearchAPI",
    "TracksAPI",
    "UsersAPI",
]
