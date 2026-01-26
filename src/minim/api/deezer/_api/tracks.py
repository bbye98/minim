from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import DeezerResourceAPI
from .charts import ChartsAPI
from .users import UsersAPI


class TracksAPI(DeezerResourceAPI):
    """
    Tracks API endpoints for the Deezer API.

    .. note::

       This class is managed by :class:`minim.api.deezer.DeezerAPIClient` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="popularity")
    def get_track(self, track_id: int | str, /) -> dict[str, Any]:
        """
        `Track <https://developers.deezer.com/api/track>`__: Get Deezer
        catalog information for a track.

        Parameters
        ----------
        track_id : int or str; positional-only
            Deezer ID of the track.

            **Examples**: :code:`101602968`, :code:`"3541756661"`.

        Returns
        -------
        track : dict[str, Any]
            Deezer content metadata for the track.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "album": {
                      "cover": <str>,
                      "cover_big": <str>,
                      "cover_medium": <str>,
                      "cover_small": <str>,
                      "cover_xl": <str>,
                      "id": <int>,
                      "link": <str>,
                      "md5_image": <str>,
                      "release_date": <str>,
                      "title": <str>,
                      "tracklist": <str>,
                      "type": "album"
                    },
                    "artist": {
                      "id": <int>,
                      "link": <str>,
                      "name": <str>,
                      "picture": <str>,
                      "picture_big": <str>,
                      "picture_medium": <str>,
                      "picture_small": <str>,
                      "picture_xl": <str>,
                      "radio": <bool>,
                      "share": <str>,
                      "tracklist": <str>,
                      "type": "artist"
                    },
                    "available_countries": <list[str]>,
                    "bpm": <int>,
                    "contributors": [
                      {
                        "id": <int>,
                        "link": <str>,
                        "name": <str>,
                        "picture": <str>,
                        "picture_big": <str>,
                        "picture_medium": <str>,
                        "picture_small": <str>,
                        "picture_xl": <str>,
                        "radio": <bool>,
                        "role": <str>,
                        "share": <str>,
                        "tracklist": <str>,
                        "type": "artist"
                      }
                    ],
                    "disk_number": <int>,
                    "duration": <int>,
                    "explicit_content_cover": <int>,
                    "explicit_content_lyrics": <int>,
                    "explicit_lyrics": <bool>,
                    "gain": <float>,
                    "id": <int>,
                    "isrc": <str>,
                    "link": <str>,
                    "md5_image": <str>,
                    "preview": <str>,
                    "rank": <int>,
                    "readable": true,
                    "release_date": <str>,
                    "share": <str>,
                    "title": <str>,
                    "title_short": <str>,
                    "title_version": <str>,
                    "track_position": <int>,
                    "track_token": <str>,
                    "type": "track"
                  }
        """
        return self._request_resource_relationship("GET", "track", track_id)

    @_copy_docstring(ChartsAPI.get_top_tracks)
    def get_top_tracks(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        return self._client.charts.get_top_tracks(limit=limit, offset=offset)

    @_copy_docstring(UsersAPI.get_user_tracks)
    def get_user_tracks(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_user_tracks(
            user_id, limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.update_user_track_details)
    def update_user_track_details(
        self,
        track_id: int | str,
        /,
        *,
        album: str | None = None,
        artist: str | None = None,
        title: str | None = None,
    ) -> bool:
        return self._client.users.update_user_track_details(
            track_id, album=album, artist=artist, title=title
        )

    @_copy_docstring(UsersAPI.delete_user_track)
    def delete_user_track(self, track_id: int | str, /) -> bool:
        return self._client.users.delete_user_track(track_id)

    @_copy_docstring(UsersAPI.get_saved_tracks)
    def get_saved_tracks(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        self._client.users.get_saved_tracks(
            user_id, limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.save_tracks)
    def save_tracks(
        self,
        track_ids: int | str | list[int | str],
        /,
        *,
        user_id: int | str = "me",
    ) -> bool:
        return self._client.users.save_tracks(track_ids, user_id=user_id)

    @_copy_docstring(UsersAPI.remove_saved_track)
    def remove_saved_track(
        self, track_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        return self._client.users.remove_saved_track(track_id, user_id=user_id)

    @_copy_docstring(UsersAPI.get_user_top_tracks)
    def get_user_top_tracks(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_user_top_tracks(
            user_id, limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.get_track_recommendations)
    def get_track_recommendations(
        self, user_id: int | str = "me", /
    ) -> dict[str, Any]:
        return self._client.users.get_track_recommendations(user_id)
