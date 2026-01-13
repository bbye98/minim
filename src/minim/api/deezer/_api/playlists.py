from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import DeezerResourceAPI
from .users import UsersAPI


class PlaylistsAPI(DeezerResourceAPI):
    """
    Playlists API endpoints for the Deezer API.

    .. note::

       This class is managed by :class:`minim.api.deezer.DeezerAPI` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="user")
    def get_playlist(
        self,
        playlist_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Playlist <https://developers.deezer.com/api/playlist>`__: Get
        Deezer catalog information for a playlist.

        Parameters
        ----------
        playlist_id : int or str; positional-only
            Deezer ID of the playlist.

            **Examples**: :code:`13651021241`, :code:`"1495242491"`.

        limit : int or None; keyword-only; optional
            Maximum number of tracks to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlist : dict[str, Any]
            Deezer content metadata for the playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "add_date": <str>,
                    "checksum": <str>,
                    "collaborative": <bool>,
                    "creation_date": <str>,
                    "creator": {
                      "id": <int>,
                      "name": <str>,
                      "tracklist": <str>,
                      "type": "user"
                    },
                    "description": <str>,
                    "duration": <int>,
                    "fans": <int>,
                    "id": <int>,
                    "is_loved_track": <bool>,
                    "link": <str>,
                    "md5_image": <str>,
                    "mod_date": <str>,
                    "nb_tracks": <int>,
                    "picture": <str>,
                    "picture_big": <str>,
                    "picture_medium": <str>,
                    "picture_small": <str>,
                    "picture_type": <str>,
                    "picture_xl": <str>,
                    "public": <bool>,
                    "share": <str>,
                    "title": <str>,
                    "tracklist": <str>,
                    "tracks": {
                      "checksum": <str>,
                      "data": [
                        {
                          "album": {
                            "cover": <str>,
                            "cover_big": <str>,
                            "cover_medium": <str>,
                            "cover_small": <str>,
                            "cover_xl": <str>,
                            "id": <int>,
                            "md5_image": <str>,
                            "title": <str>,
                            "tracklist": <str>,
                            "type": "album",
                            "upc": <str>
                          },
                          "artist": {
                            "id": <int>,
                            "link": <str>,
                            "name": <str>,
                            "tracklist": <str>,
                            "type": "artist"
                          },
                          "duration": <int>,
                          "explicit_content_cover": <int>,
                          "explicit_content_lyrics": <int>,
                          "explicit_lyrics": <bool>,
                          "id": <int>,
                          "isrc": <str>,
                          "link": <str>,
                          "md5_image": <str>,
                          "preview": <str>,
                          "rank": <int>,
                          "readable": <bool>,
                          "time_add": <int>,
                          "title": "<str>,
                          "title_short": <str>,
                          "title_version": <str>,
                          "type": "track"
                        }
                      ]
                    },
                    "type": "playlist"
                  }
        """
        return self._request_resource_relationship(
            "GET", "playlist", playlist_id, limit=limit, offset=offset
        )

    def mark_playlist_seen(self, playlist_id: int | str, /) -> bool:
        """
        `Playlist > Seen <https://developers.deezer.com/api/playlist
        /seen>`_: Mark a playlist as seen.

        Parameters
        ----------
        playlist_id : int or str; positional-only
            Deezer ID of the playlist.

            **Examples**: :code:`13651021241`, :code:`"1495242491"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        return self._request_resource_relationship(
            "POST", "playlist", playlist_id, "seen"
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_playlist_fans(
        self,
        playlist_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Playlist > Fans <https://developers.deezer.com/api/playlist
        /fans>`_: Get Deezer catalog information for a playlist's fans.

        Parameters
        ----------
        playlist_id : int or str; positional-only
            Deezer ID of the playlist.

            **Examples**: :code:`13651021241`, :code:`"1495242491"`.

        limit : int; keyword-only; optional
            Maximum number of users to return.

            **Minimum value**: :code:`1`.

        offset : int; keyword-only; optional
            Index of the first user to return. Use with `limit` to get
            the next batch of users.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        users : dict[str, Any]
            Page of Deezer content metadata for the playlist's fans.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <int>,
                        "name": <str>,
                        "picture": <str>,
                        "picture_big": <str>,
                        "picture_medium": <str>,
                        "picture_small": <str>,
                        "picture_xl": <str>,
                        "tracklist": <str>,
                        "type": "user"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET", "playlist", playlist_id, "fans", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="user")
    def get_playlist_tracks(
        self,
        playlist_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Playlist > Tracks <https://developers.deezer.com/api/playlist
        /tracks>`__: Get Deezer catalog information for the tracks in a
        playlist.

        Parameters
        ----------
        playlist_id : int or str; positional-only
            Deezer ID of the playlist.

            **Examples**: :code:`13651021241`, :code:`"1495242491"`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of Deezer content metadata for the artist's top tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "checksum": <str>,
                    "data": [
                      {
                        "album": {
                          "cover": <str>,
                          "cover_big": <str>,
                          "cover_medium": <str>,
                          "cover_small": <str>,
                          "cover_xl": <str>,
                          "id": <int>,
                          "md5_image": <str>,
                          "title": <str>,
                          "tracklist": <str>,
                          "type": "album",
                          "upc": <str>,
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
                          "tracklist": <str>,
                          "type": "artist"
                        },
                        "duration": <int>,
                        "explicit_content_cover": <int>,
                        "explicit_content_lyrics": <int>,
                        "explicit_lyrics": <bool>,
                        "id": <int>,
                        "isrc": <str>,
                        "link": <str>,
                        "md5_image": <str>,
                        "preview": <str>,
                        "rank": <int>,
                        "readable": <bool>,
                        "time_add": <int>,
                        "title": <str>,
                        "title_short": <str>,
                        "title_version": <str>,
                        "type": "track"
                      }
                    ],
                    "prev": <str>,
                    "next": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET",
            "playlist",
            playlist_id,
            "tracks",
            limit=limit,
            offset=offset,
        )

    def get_playlist_radio_tracks(
        self,
        playlist_id: int | str,
        /,
    ) -> dict[str, Any]:
        """
        `Playlist > Radio <https://developers.deezer.com/api/playlist
        /radio>`_: Get Deezer catalog information for algorithmically
        selected tracks in a playlist's radio.

        Parameters
        ----------
        playlist_id : int or str; positional-only
            Deezer ID of the playlist.

            **Examples**: :code:`13651021241`, :code:`"1495242491"`.

        Returns
        -------
        tracks : dict[str, Any]
            Deezer content metadata for the tracks in the playlist's
            radio.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "album": {
                          "id": <int>,
                          "md5_image": <str>,
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
                          "tracklist": <str>,
                          "type": "artist"
                        },
                        "duration": <int>,
                        "explicit_content_cover": <int>,
                        "explicit_content_lyrics": <int>,
                        "explicit_lyrics": <bool>,
                        "id": <int>,
                        "isrc": <str>,
                        "link": <str>,
                        "md5_image": <str>,
                        "preview": <str>,
                        "rank": <int>,
                        "title": <str>,
                        "title_short": <str>,
                        "title_version": <str>,
                        "type": "track"
                      }
                    ]
                  }
        """
        return self._request_resource_relationship(
            "GET", "playlist", playlist_id, "radio"
        )

    @_copy_docstring(UsersAPI.create_playlist)
    def create_playlist(self, name: str) -> dict[str, int]:
        return self._client.users.create_playlist(name)

    @_copy_docstring(UsersAPI.update_playlist_details)
    def update_playlist_details(
        self,
        playlist_id: int | str,
        /,
        *,
        name: str | None = None,
        description: str | None = None,
        public: bool | None = None,
        collaborative: bool | None = None,
    ) -> bool:
        return self._client.users.update_playlist_details(
            playlist_id,
            name=name,
            description=description,
            public=public,
            collaborative=collaborative,
        )

    @_copy_docstring(UsersAPI.delete_playlist)
    def delete_playlist(self, playlist_id: int | str, /) -> bool:
        return self._client.users.delete_playlist(playlist_id)

    @_copy_docstring(UsersAPI.add_playlist_tracks)
    def add_playlist_tracks(
        self, playlist_id: int | str, /, track_ids: int | str | list[int | str]
    ) -> bool:
        return self._client.users.add_playlist_tracks(
            playlist_id, track_ids=track_ids
        )

    @_copy_docstring(UsersAPI.reorder_playlist_tracks)
    def reorder_playlist_tracks(
        self, playlist_id: int | str, /, track_ids: int | str | list[int | str]
    ) -> Any:
        return self._client.users.reorder_playlist_tracks(
            playlist_id, track_ids=track_ids
        )

    @_copy_docstring(UsersAPI.follow_playlists)
    def follow_playlists(
        self,
        playlist_ids: int | str | list[int | str],
        /,
        *,
        user_id: int | str = "me",
    ) -> bool:
        return self._client.users.follow_playlists(
            playlist_ids, user_id=user_id
        )

    @_copy_docstring(UsersAPI.unfollow_playlist)
    def unfollow_playlist(
        self,
        playlist_id: int | str,
        /,
        *,
        user_id: int | str = "me",
    ) -> bool:
        return self._client.users.unfollow_playlist(
            playlist_id, user_id=user_id
        )
