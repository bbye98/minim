from ._core import MusixmatchLyricsAPIClient
from ._lyrics_api.albums import AlbumsAPI
from ._lyrics_api.artists import ArtistsAPI
from ._lyrics_api.charts import ChartsAPI
from ._lyrics_api.enterprise import EnterpriseAPI
from ._lyrics_api.matcher import MatcherAPI
from ._lyrics_api.search import SearchAPI
from ._lyrics_api.tracks import TracksAPI

__all__ = [
    "MusixmatchLyricsAPIClient",
    "AlbumsAPI",
    "ArtistsAPI",
    "ChartsAPI",
    "EnterpriseAPI",
    "MatcherAPI",
    "SearchAPI",
    "TracksAPI",
]
