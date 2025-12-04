from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI, _copy_docstring
from .pages import PrivatePagesAPI
from .users import PrivateUsersAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class PrivateVideosAPI(ResourceAPI):
    """
    Videos API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _client: "PrivateTIDALAPI"

    @_copy_docstring(PrivatePagesAPI.get_video_page)
    def get_video_page(
        self,
        video_id: int | str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
        locale: str | None = None,
    ) -> dict[str, Any]:
        return self._client.pages.get_video_page(
            video_id, country_code, device_type=device_type, locale=locale
        )
