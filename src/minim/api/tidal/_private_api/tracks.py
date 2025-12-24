from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI, _copy_docstring
from .users import PrivateUsersAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class PrivateTracksAPI(ResourceAPI):
    """
    Tracks API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _client: "PrivateTIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_track(
        self, track_id: int | str, /, country_code: str = None
    ) -> dict[str, Any]:
        """ """
        return
