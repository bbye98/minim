from collections.abc import Collection
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import TIDALAPI


class AlbumsAPI(ResourceAPI):
    """
    Albums API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _client: "TIDALAPI"

    def get_albums(
        self,
        album_ids: Collection[int | str] | None = None,
        barcode_ids: Collection[int | str] | None = None,
        user_ids: Collection[int | str] | None = None,
        country_code: str | None = None,
        page: int | str | None = None,
        include: Collection[str] | None = None,
    ) -> dict[str, Any]:
        pass
