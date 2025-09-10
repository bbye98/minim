from ._core import WebAPI
from ._web_api.albums import WebAPIAlbumEndpoints
from ._web_api.artists import WebAPIArtistEndpoints
from ._web_api.users import WebAPIUserEndpoints

__all__ = [
    "WebAPI",
    "WebAPIAlbumEndpoints",
    "WebAPIArtistEndpoints",
    "WebAPIUserEndpoints",
]
