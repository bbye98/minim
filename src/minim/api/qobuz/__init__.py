from ._core import PrivateQobuzAPI
from ._private_api.genres import PrivateGenresAPI
from ._private_api.playlists import PrivatePlaylistsAPI
from ._private_api.purchases import PrivatePurchasesAPI
from ._private_api.search import PrivateSearchEndpoints
from ._private_api.tracks import PrivateTracksAPI
from ._private_api.users import PrivateUsersAPI

__all__ = [
    "PrivateQobuzAPI",
    "PrivateGenresAPI",
    "PrivatePlaylistsAPI",
    "PrivatePurchasesAPI",
    "PrivateSearchEndpoints",
    "PrivateTracksAPI",
    "PrivateUsersAPI",
]
