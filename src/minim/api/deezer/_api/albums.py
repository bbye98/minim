from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import DeezerResourceAPI
from .users import UsersAPI


class AlbumsAPI(DeezerResourceAPI):
    """
    Albums API endpoints for the Deezer API.

    .. note::

       This class is managed by :class:`minim.api.deezer.DeezerAPI` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="popularity")
    def get_album(
        self,
        album_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Album <https://developers.deezer.com/api/album>`_: Get Deezer
        catalog information for an album.

        Parameters
        ----------
        album_id : int or str; positional-only
            Deezer ID of the album.

            **Examples**: :code:`10546890`, :code:`"816455081"`.

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
        album : dict[str, Any]
            Deezer content metadata for the album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "artist": {
                      "id": <int>,
                      "name": <str>,
                      "picture": <str>,
                      "picture_big": <str>,
                      "picture_medium": <str>,
                      "picture_small": <str>,
                      "picture_xl": <str>,
                      "tracklist": <str>,
                      "type": "artist"
                    },
                    "available": <bool>,
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
                    "cover": <str>,
                    "cover_big": <str>,
                    "cover_medium": <str>,
                    "cover_small": <str>,
                    "cover_xl": <str>,
                    "duration": <int>,
                    "explicit_content_cover": <int>,
                    "explicit_content_lyrics": <int>,
                    "explicit_lyrics": <bool>,
                    "fans": <int>,
                    "genre_id": <int>,
                    "genres": {
                      "data": [
                        {
                          "id": <int>,
                          "name": <str>,
                          "picture": <str>,
                          "type": "genre"
                        }
                      ]
                    },
                    "id": <int>,
                    "label": <str>,
                    "link": <str>,
                    "md5_image": <str>,
                    "nb_tracks": <int>,
                    "record_type": <str>,
                    "release_date": <str>,
                    "share": <str>,
                    "title": <str>,
                    "tracklist": <str>,
                    "tracks": {
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
                            "type": "album"
                          },
                          "artist": {
                            "id": <int>,
                            "name": <str>,
                            "tracklist": <str>,
                            "type": "artist"
                          },
                          "duration": <int>,
                          "explicit_content_cover": <int>,
                          "explicit_content_lyrics": <int>,
                          "explicit_lyrics": <bool>,
                          "id": <int>,
                          "link": <str>,
                          "md5_image": <str>,
                          "preview": <str>,
                          "rank": <int>,
                          "readable": <bool>,
                          "title": <str>,
                          "title_short": <str>,
                          "title_version": <str>,
                          "type": "track"
                        }
                      ]
                    },
                    "type": "album",
                    "upc": <str>
                  }
        """
        return self._request_resource_relationship(
            "GET", "album", album_id, limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_album_fans(
        self,
        album_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Album > Fans <https://developers.deezer.com/api/album/fans>`_:
        Get Deezer catalog information for an album's fans.

        Parameters
        ----------
        album_id : int or str; positional-only
            Deezer ID of the album.

            **Examples**: :code:`10546890`, :code:`"816455081"`.

        limit : int or None; keyword-only; optional
            Maximum number of users to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first user to return. Use with `limit` to get
            the next batch of users.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        users : dict[str, Any]
            Page of Deezer content metadata for the album's fans.

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
            "GET", "album", album_id, "fans", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_album_tracks(
        self,
        album_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Album > Tracks <https://developers.deezer.com/api/album
        /tracks>`_: Get Deezer catalog information for tracks in an
        album.

        Parameters
        ----------
        album_id : int or str; positional-only
            Deezer ID of the album.

            **Examples**: :code:`10546890`, :code:`"816455081"`.

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
        tracks : dict[str, Any]
            Page of Deezer content metadata for the tracks in the album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "artist": {
                          "id": <int>,
                          "name": <str>,
                          "tracklist": <str>,
                          "type": "artist"
                        },
                        "disk_number": <int>,
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
                        "title": <str>,
                        "title_short": <str>,
                        "title_version": <str>,
                        "track_position": <int>,
                        "type": "track"
                      }
                    ],
                    "next": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET", "album", album_id, "tracks", limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.save_albums)
    def save_albums(
        self,
        album_ids: int | str | list[int | str],
        /,
        *,
        user_id: int | str = "me",
    ) -> bool:
        return self._client.users.save_albums(album_ids, user_id=user_id)

    @_copy_docstring(UsersAPI.remove_saved_album)
    def remove_saved_album(
        self, album_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        return self._client.users.remove_saved_album(album_id, user_id=user_id)
