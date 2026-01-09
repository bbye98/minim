from typing import Any

from ..._shared import _copy_docstring
from ._shared import PrivateQobuzResourceAPI
from .users import PrivateUsersAPI


class PrivateDynamicAPI(PrivateQobuzResourceAPI):
    """
    Dynamic Tracks API endpoints for the private Qobuz API.

    .. note::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    @_copy_docstring(PrivateUsersAPI.get_personalized_playlists)
    def get_personalized_playlists(self) -> list[dict[str, Any]]:
        return self._client.users.get_personalized_playlists()

    @_copy_docstring(PrivateUsersAPI.get_personalized_playlist_tracks)
    def get_personalized_playlist_tracks(
        self,
        playlist_type: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_personalized_playlist_tracks(
            playlist_type, limit=limit, offset=offset
        )

    @_copy_docstring(PrivateUsersAPI.get_track_recommendations)
    def get_track_recommendations(
        self,
        seed_track_ids: int | str | list[int | str],
        /,
        exclude_track_ids: int | str | list[int | str] | None = None,
        *,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_track_recommendations(
            seed_track_ids, exclude_track_ids=exclude_track_ids, limit=limit
        )
