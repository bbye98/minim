from ._core import WebAPI
from ._web_api.albums import WebAPIAlbumEndpoints
from ._web_api.artists import WebAPIArtistEndpoints
from ._web_api.audiobooks import WebAPIAudiobookEndpoints
from ._web_api.categories import WebAPICategoryEndpoints
from ._web_api.chapters import WebAPIChapterEndpoints
from ._web_api.episodes import WebAPIEpisodeEndpoints
from ._web_api.genres import WebAPIGenreEndpoints
from ._web_api.markets import WebAPIMarketEndpoints

# from ._web_api.player import WebAPIPlayerEndpoints
# from ._web_api.playlists import WebAPIPlaylistEndpoints
# from ._web_api.search import WebAPISearchEndpoints
# from ._web_api.shows import WebAPIShowEndpoints
from ._web_api.tracks import WebAPITrackEndpoints
from ._web_api.users import WebAPIUserEndpoints

__all__ = [
    "WebAPI",
    "WebAPIAlbumEndpoints",
    "WebAPIArtistEndpoints",
    "WebAPIAudiobookEndpoints",
    "WebAPICategoryEndpoints",
    "WebAPIChapterEndpoints",
    "WebAPIEpisodeEndpoints",
    "WebAPIGenreEndpoints",
    "WebAPIMarketEndpoints",
    # "WebAPIPlayerEndpoints",
    # "WebAPIPlaylistEndpoints",
    # "WebAPISearchEndpoints",
    # "WebAPIShowEndpoints",
    "WebAPITrackEndpoints",
    "WebAPIUserEndpoints",
]
