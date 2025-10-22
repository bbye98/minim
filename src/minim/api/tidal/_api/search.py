from collections.abc import Collection
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import TIDALAPI


class SearchAPI(ResourceAPI):
    """
    Search Results and Search Suggestions API endpoints for the TIDAL
    API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _client: "TIDALAPI"
