from ._core import PrivateQobuzAPIClient
from ._private_api.albums import PrivateAlbumsAPI
from ._private_api.artists import PrivateArtistsAPI
from ._private_api.catalog import PrivateCatalogAPI
from ._private_api.dynamic import PrivateDynamicAPI
from ._private_api.favorites import PrivateFavoritesAPI
from ._private_api.labels import PrivateLabelsAPI
from ._private_api.genres import PrivateGenresAPI
from ._private_api.playlists import PrivatePlaylistsAPI
from ._private_api.purchases import PrivatePurchasesAPI
from ._private_api.search import PrivateSearchAPI
from ._private_api.tracks import PrivateTracksAPI
from ._private_api.users import PrivateUsersAPI

__all__ = [
    "PrivateQobuzAPIClient",
    "PrivateAlbumsAPI",
    "PrivateArtistsAPI",
    "PrivateCatalogAPI",
    "PrivateDynamicAPI",
    "PrivateFavoritesAPI",
    "PrivateLabelsAPI",
    "PrivateGenresAPI",
    "PrivatePlaylistsAPI",
    "PrivatePurchasesAPI",
    "PrivateSearchAPI",
    "PrivateTracksAPI",
    "PrivateUsersAPI",
]
