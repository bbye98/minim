from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import APIClient


class TracksAPI(ResourceAPI):
    """
    Tracks API endpoints for the private Qobuz API.

    .. important::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    _client: "APIClient"

    def get_track_playback_info(
        self, track_id: int | str, /, *, format_id: int | str = 27
    ) -> dict[str, Any]:
        """ """
        return self._client._request(
            "GET",
            "track/getFileUrl",
            params={"track_id": track_id, "format_id": format_id},
            signed=True,
        )
