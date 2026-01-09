from ._core import PrivateQobuzAPI
from ._private_api.albums import PrivateAlbumsAPI
from ._private_api.artists import PrivateArtistsAPI
from ._private_api.catalog import PrivateCatalogAPI
from ._private_api.dynamic import PrivateDynamicAPI
from ._private_api.favorites import PrivateFavoritesAPI
from ._private_api.labels import PrivateLabelsAPI
from ._private_api.genres import PrivateGenresAPI
from ._private_api.playlists import PrivatePlaylistsAPI
from ._private_api.purchases import PrivatePurchasesAPI
from ._private_api.search import PrivateSearchEndpoints
from ._private_api.tracks import PrivateTracksAPI
from ._private_api.users import PrivateUsersAPI

__all__ = [
    "PrivateQobuzAPI",
    "PrivateAlbumsAPI",
    "PrivateArtistsAPI",
    "PrivateCatalogAPI",
    "PrivateDynamicAPI",
    "PrivateFavoritesAPI",
    "PrivateLabelsAPI",
    "PrivateGenresAPI",
    "PrivatePlaylistsAPI",
    "PrivatePurchasesAPI",
    "PrivateSearchEndpoints",
    "PrivateTracksAPI",
    "PrivateUsersAPI",
]
