from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import DeezerResourceAPI
from .users import UsersAPI


class ArtistsAPI(DeezerResourceAPI):
    """
    Artists API endpoints for the Deezer API.

    .. note::

       This class is managed by :class:`minim.api.deezer.DeezerAPIClient` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="popularity")
    def get_artist(self, artist_id: int | str, /) -> dict[str, Any]:
        """
        `Artist <https://developers.deezer.com/api/artist>`_: Get Deezer
        catalog information for an artist.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Deezer ID of the artist.

            **Examples**: :code:`3265001`, :code:`"330311461"`.

        Returns
        -------
        artist : dict[str, Any]
            Deezer content metadata for the artist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "link": <str>,
                    "name": <str>,
                    "nb_album": <int>,
                    "nb_fan": <int>,
                    "picture": <str>,
                    "picture_big": <str>,
                    "picture_medium": <str>,
                    "picture_small": <str>,
                    "picture_xl": <str>,
                    "radio": <bool>,
                    "share": <str>,
                    "tracklist": <str>,
                    "type": "artist"
                  }
        """
        return self._request_resource_relationship("GET", "artist", artist_id)

    @TTLCache.cached_method(ttl="popularity")
    def get_artist_top_tracks(
        self,
        artist_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Artist > Top <https://developers.deezer.com/api/artist/top>`_:
        Get Deezer catalog information for an artist's top tracks.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Deezer ID of the artist.

            **Examples**: :code:`3265001`, :code:`"330311461"`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`5`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        top_tracks : dict[str, Any]
            Page of Deezer content metadata for the artist's top tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
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
                        "duration": <int>,
                        "explicit_content_cover": <int>,
                        "explicit_content_lyrics": <int>,
                        "explicit_lyrics": <bool>,
                        "id": <int>,
                        "md5_image": <str>,
                        "preview": <str>,
                        "rank": <int>,
                        "readable": <bool>,
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
            "GET", "artist", artist_id, "top", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_artist_albums(
        self,
        artist_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Artist > Albums <https://developers.deezer.com/api/artist
        /albums>`_: Get Deezer catalog information for an artist's
        albums.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Deezer ID of the artist.

            **Examples**: :code:`3265001`, :code:`"330311461"`.

        limit : int; keyword-only; optional
            Maximum number of albums to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first album to return. Use with `limit` to get
            the next batch of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        albums : dict[str, Any]
            Page of Deezer content metadata for the artist's albums.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "cover": <str>,
                        "cover_big": <str>,
                        "cover_medium": <str>,
                        "cover_small": <str>,
                        "cover_xl": <str>,
                        "explicit_lyrics": <bool>,
                        "fans": <int>,
                        "genre_id": <int>,
                        "id": <int>,
                        "link": <str>,
                        "md5_image": <str>,
                        "record_type": <str>,
                        "release_date": <str>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "album"
                      }
                    ],
                    "prev": <str>,
                    "next": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET", "artist", artist_id, "albums", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_artist_fans(
        self,
        artist_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Artist > Fans <https://developers.deezer.com/api/artist
        /fans>`_: Get Deezer catalog information for an artist's fans.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Deezer ID of the artist.

            **Examples**: :code:`3265001`, :code:`"330311461"`.

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
            Page of Deezer content metadata for the artist's fans.

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
            "GET", "artist", artist_id, "fans", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_similar_artists(
        self,
        artist_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Artist > Related <https://developers.deezer.com/api/artist
        /related>`_: Get Deezer catalog information for other artists
        that are similar to an artist.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Deezer ID of the artist.

            **Examples**: :code:`3265001`, :code:`"330311461"`.

        limit : int; keyword-only; optional
            Maximum number of artists to return.

            **Minimum value**: :code:`1`.

            **API default** :code:`20`.

        offset : int; keyword-only; optional
            Index of the first artist to return. Use with `limit` to get
            the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        artists : dict[str, Any]
            Page of Deezer content metadata for the similar artists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <int>,
                        "link": <str>,
                        "name": <str>,
                        "nb_album": <int>,
                        "nb_fan": <int>,
                        "picture": <str>,
                        "picture_big": <str>,
                        "picture_medium": <str>,
                        "picture_small": <str>,
                        "picture_xl": <str>,
                        "radio": <bool>,
                        "tracklist": <str>,
                        "type": "artist"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET", "artist", artist_id, "related", limit=limit, offset=offset
        )

    def get_artist_radio_tracks(
        self,
        artist_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Artist > Radio <https://developers.deezer.com/api/artist
        /radio>`_: Get Deezer catalog information for algorithmically
        selected tracks in an artist's radio.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Deezer ID of the artist.

            **Examples**: :code:`3265001`, :code:`"330311461"`.

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
            Page of Deezer content metadata for the tracks in the
            artist's radio.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
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
                  }
        """
        return self._request_resource_relationship(
            "GET", "artist", artist_id, "radio", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="daily")
    def get_artist_playlists(
        self,
        artist_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Artist > Playlists <https://developers.deezer.com/api/artist
        /playlists>`_: Get Deezer catalog information for playlists that
        an artist's tracks appear in.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Deezer ID of the artist.

            **Examples**: :code:`3265001`, :code:`"330311461"`.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of Deezer content metadata for the artist's playlists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "add_date": <str>,
                        "checksum": <str>,
                        "creation_date": <str>,
                        "id": <int>,
                        "link": <str>,
                        "md5_image": <str>,
                        "mod_date": <str>,
                        "picture": <str>,
                        "picture_big": <str>,
                        "picture_medium": <str>,
                        "picture_small": <str>,
                        "picture_type": <str>,
                        "picture_xl": <str>,
                        "public": <bool>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "playlist"
                        "user": {
                          "id": <int>,
                          "name": <str>,
                          "tracklist": <str>,
                          "type": "user"
                        }
                      }
                    ],
                    "prev": <str>,
                    "next": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET", "artist", artist_id, "playlists", limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.get_followed_artists)
    def get_followed_artists(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_followed_artists(
            user_id, limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.follow_artists)
    def follow_artists(
        self,
        artist_ids: int | str | list[int | str],
        /,
        *,
        user_id: int | str = "me",
    ) -> bool:
        return self._client.users.follow_artists(artist_ids, user_id=user_id)

    @_copy_docstring(UsersAPI.unfollow_artist)
    def unfollow_artist(
        self, artist_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        return self._client.users.unfollow_artist(artist_id, user_id=user_id)

    @_copy_docstring(UsersAPI.get_user_top_artists)
    def get_user_top_artists(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_user_top_artists(
            user_id, limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.get_artist_recommendations)
    def get_artist_recommendations(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_artist_recommendations(
            user_id, limit=limit, offset=offset
        )
