from collections.abc import Collection
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache
from ._shared import TIDALResourceAPI

if TYPE_CHECKING:
    from .. import TIDALAPI

if TYPE_CHECKING:
    from .. import TIDALAPI


class TracksAPI(TIDALResourceAPI):
    """
    Tracks API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _RESOURCES = {
        "albums",
        "artists",
        "owners",
        "providers",
        "radio",
        "similarTracks",
        "sourceFile",
    }
    _client: "TIDALAPI"
