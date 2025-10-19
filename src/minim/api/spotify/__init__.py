from ._core import SpotifyWebAPI
from ._web_api.albums import AlbumsAPI
from ._web_api.artists import ArtistsAPI
from ._web_api.audiobooks import AudiobooksAPI
from ._web_api.categories import CategoriesAPI
from ._web_api.chapters import ChaptersAPI
from ._web_api.episodes import EpisodesAPI
from ._web_api.genres import GenresAPI
from ._web_api.markets import MarketsAPI
from ._web_api.player import PlayerAPI
from ._web_api.playlists import PlaylistsAPI
from ._web_api.search import SearchAPI
from ._web_api.shows import ShowsAPI
from ._web_api.tracks import TracksAPI
from ._web_api.users import UsersAPI

__all__ = [
    "SpotifyWebAPI",
    "AlbumsAPI",
    "ArtistsAPI",
    "AudiobooksAPI",
    "CategoriesAPI",
    "ChaptersAPI",
    "EpisodesAPI",
    "GenresAPI",
    "MarketsAPI",
    "PlayerAPI",
    "PlaylistsAPI",
    "SearchAPI",
    "ShowsAPI",
    "TracksAPI",
    "UsersAPI",
]
