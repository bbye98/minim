from typing import Any

from ..._shared import TTLCache
from ._shared import DeezerResourceAPI


class UsersAPI(DeezerResourceAPI):
    """
    Users API endpoints for the Deezer API.

    .. note::

       This class is managed by :class:`minim.api.deezer.DeezerAPIClient` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="user")
    def get_user(self, user_id: int | str = "me", /) -> dict[str, Any]:
        """
        `User <https://developers.deezer.com/api/user>`_: Get profile
        information for a Deezer user.

        .. admonition:: Permission and user authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's basic information.

              .. tab-item:: Optional

                 :code:`email` permission
                    Access the user's email. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        profile : dict[str, Any]
            Profile information for the specified user.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "birthday": <str>,
                    "country": <str>,
                    "email": <str>,
                    "explicit_content_level": <str>,
                    "explicit_content_levels_available": <list[str]>,
                    "firstname": <str>,
                    "gender": <str>,
                    "id": <int>,
                    "inscription_date": <str>,
                    "is_kid": <bool>,
                    "lang": <str>,
                    "lastname": <str>,
                    "link": <str>,
                    "name": <str>,
                    "picture": <str>,
                    "picture_big": <str>,
                    "picture_medium": <str>,
                    "picture_small": <str>,
                    "picture_xl": <str>,
                    "status": <int>,
                    "tracklist": <str>,
                    "type": "user"
                  }
        """
        self._client._require_authentication("users.get_user")
        return self._request_resource_relationship("GET", "user", user_id)

    @TTLCache.cached_method(ttl="static")
    def get_permissions(
        self, user_id: int | str = "me", /
    ) -> dict[str, dict[str, bool]]:
        """
        `User > Permissions <https://developers.deezer.com/api/user
        /permissions>`_: Get the permissions granted to the client.

        .. admonition:: Permission and user authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's basic information.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        permissions: dict[str, dict[str, bool]]
            Permissions granted to the client.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "permissions": {
                      "basic_access": true,
                      "delete_library": true,
                      "email": true,
                      "listening_history": true,
                      "manage_community": true,
                      "manage_library": true,
                      "offline_access": true
                    }
                  }
        """
        self._client._require_authentication("users.get_permissions")
        return self._request_resource_relationship(
            "GET", "user", user_id, "permissions"
        )

    @TTLCache.cached_method(ttl="static")
    def get_options(self, user_id: int | str = "me", /) -> dict[str, Any]:
        """
        `Options <https://developers.deezer.com/api/options>`_: Get a
        user's options.

        .. admonition:: Permission and user authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's basic information.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        options: dict[str, Any]
            User's options.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "ads_audio": <bool>,
                    "ads_display": <bool>,
                    "can_subscribe": <bool>,
                    "hq": <bool>,
                    "lossless": <bool>,
                    "offline": <bool>,
                    "preview": <bool>,
                    "radio": <bool>,
                    "radio_skips": <int>,
                    "streaming": <bool>,
                    "streaming_duration": <int>,
                    "too_many_devices": <bool>,
                    "type": "options"
                  }
        """
        self._client._require_authentication("users.get_options")
        return self._request_resource_relationship(
            "GET", "user", user_id, "options"
        )

    def send_notification(
        self, message: str, /, *, user_id: int | str = "me"
    ) -> dict[str, bool]:
        """
        `User > Notification <https://developers.deezer.com/api/user
        /notifications>`_: Add a notification to a user's feed.

        Parameters
        ----------
        message : str
            Notification message.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        status : dict[str, bool]
            Whether the request completed successfully.

            **Sample response**: :code:`{"success": True}`.
        """
        self._validate_type("message", message, str)
        if not len(message):
            raise ValueError("The message cannot be blank.")
        return self._request_resource_relationship(
            "POST",
            "user",
            user_id,
            "notifications",
            params={"message": message},
        )

    def get_user_mix_tracks(
        self, user_id: int | str = "me", /
    ) -> dict[str, Any]:
        """
        `User > Flow <https://developers.deezer.com/api/user/flow>`_:
        Get Deezer catalog information for the tracks in a user's Flow
        mix.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        tracks : dict[str, Any]
            Deezer content metadata for tracks in the user's Flow mix.

            .. admonition:: Sample response
               :class: response dropdown

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
        self._client._require_authentication("users.get_user_mix_tracks")
        return self._request_resource_relationship(
            "GET", "user", user_id, "flow"
        )

    @TTLCache.cached_method(ttl="playback")
    def get_recently_played(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > History <https://developers.deezer.com/api/user
        /history>`_: Get Deezer catalog information for tracks recently
        played by a user.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`listening_history` permission
                    Access the user's listening history. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

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
            Page of Deezer content metadata for the recently played
            tracks.

            .. admonition:: Sample response
               :class: response dropdown

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
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_permissions(
            "users.get_recently_played", "listening_history"
        )
        return self._request_resource_relationship(
            "GET", "user", user_id, "history", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_user_top_albums(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Charts > Albums <https://developers.deezer.com/api/user
        /charts/albums>`_: Get Deezer catalog information for a user's
        top albums.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of albums to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first album to return. Use with `limit` to get
            the next batch of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        albums : dict[str, Any]
            Page of Deezer content metadata for the user's top albums.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "checksum": <str>,
                    "data": [
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
                        "cover": <str>,
                        "cover_big": <str>,
                        "cover_medium": <str>,
                        "cover_small": <str>,
                        "cover_xl": <str>,
                        "explicit_lyrics": <bool>,
                        "id": <int>,
                        "link": <str>,
                        "md5_image": <str>,
                        "nb_tracks": <int>,
                        "record_type": <str>,
                        "release_date": <str>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "album"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_my_top_albums")
        return self._request_resource_relationship(
            "GET", "user", user_id, "charts/albums", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_user_top_artists(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Charts > Artists <https://developers.deezer.com/api/user
        /charts/artists>`_: Get Deezer catalog information for a user's
        top artists.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of artists to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first artist to return. Use with `limit` to get
            the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        artists : dict[str, Any]
            Page of Deezer content metadata for the user's top artists.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "checksum": <str>,
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
        self._client._require_authentication("users.get_my_top_artists")
        return self._request_resource_relationship(
            "GET",
            "user",
            user_id,
            "charts/artists",
            limit=limit,
            offset=offset,
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_user_top_playlists(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Charts > Playlists <https://developers.deezer.com/api
        /user/charts/playlists>`_: Get Deezer catalog information for a
        user's top playlists.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of playlists to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of Deezer content metadata for the user's top
            playlists.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "checksum": <str>,
                    "data": [
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
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "playlist"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_my_top_playlists")
        return self._request_resource_relationship(
            "GET",
            "user",
            user_id,
            "charts/playlists",
            limit=limit,
            offset=offset,
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_user_top_tracks(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Charts > Tracks <https://developers.deezer.com/api/user
        /charts/tracks>`_: Get Deezer catalog information for a user's
        top tracks.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

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
            Page of Deezer content metadata for the user's top tracks.

            .. admonition:: Sample response
               :class: response dropdown

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
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_my_top_tracks")
        return self._request_resource_relationship(
            "GET", "user", user_id, "charts/tracks", limit=limit, offset=offset
        )

    def get_album_recommendations(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Recommendations > Albums <https://developers.deezer.com
        /api/user/recommendations/albums>`_: Get album recommendations.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of albums to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first album to return. Use with `limit` to
            get the next batch of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        albums : dict[str, Any]
            Page of Deezer content metadata for the album
            recommendations.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "data": [
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
                        "cover": <str>,
                        "cover_big": <str>,
                        "cover_medium": <str>,
                        "cover_small": <str>,
                        "cover_xl": <str>,
                        "explicit_lyrics": <bool>,
                        "id": <int>,
                        "link": <str>,
                        "md5_image": <str>,
                        "nb_tracks": <int>,
                        "record_type": <str>,
                        "release_date": <str>,
                        "timestamp": <int>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "album"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_album_recommendations")
        return self._request_resource_relationship(
            "GET",
            "user",
            user_id,
            "recommendations/albums",
            limit=limit,
            offset=offset,
        )

    def get_release_recommendations(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Recommendations > Releases
        <https://developers.deezer.com/api/user/recommendations
        /releases>`_: Get new album recommendations.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of albums to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first album to return. Use with `limit` to
            get the next batch of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        albums : dict[str, Any]
            Page of Deezer content metadata for the new album
            recommendations.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "data": [
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
                        "cover": <str>,
                        "cover_big": <str>,
                        "cover_medium": <str>,
                        "cover_small": <str>,
                        "cover_xl": <str>,
                        "explicit_lyrics": <bool>,
                        "id": <int>,
                        "link": <str>,
                        "md5_image": <str>,
                        "nb_tracks": <int>,
                        "record_type": <str>,
                        "release_date": <str>,
                        "timestamp": <int>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "album"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>,
                  }
        """
        self._client._require_authentication(
            "users.get_release_recommendations"
        )
        return self._request_resource_relationship(
            "GET",
            "user",
            user_id,
            "recommendations/releases",
            limit=limit,
            offset=offset,
        )

    def get_artist_recommendations(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Recommendations > Artists <https://developers.deezer.com
        /api/user/recommendations/artists>`_: Get artist
        recommendations.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of artists to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first artist to return. Use with `limit` to
            get the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        artists : dict[str, Any]
            Page of Deezer content metadata for the artist
            recommendations.

            .. admonition:: Sample response
               :class: response dropdown

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
                        "timestamp": <int>,
                        "tracklist": <str>,
                        "type": "artist"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_album_recommendations")
        return self._request_resource_relationship(
            "GET",
            "user",
            user_id,
            "recommendations/albums",
            limit=limit,
            offset=offset,
        )

    def get_playlist_recommendations(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Recommendations > Playlists
        <https://developers.deezer.com/api/user/recommendations
        /playlists>`_: Get playlist recommendations.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of playlists to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of Deezer content metadata for the playlist
            recommendations.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "data": [
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
                        "timestamp": <int>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "playlist"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication(
            "users.get_playlist_recommendations"
        )
        return self._request_resource_relationship(
            "GET",
            "user",
            user_id,
            "recommendations/playlists",
            limit=limit,
            offset=offset,
        )

    def get_radio_recommendations(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Recommendations > Radios <https://developers.deezer.com
        /api/user/recommendations/radios>`_: Get radio recommendations.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of radios to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first radio to return. Use with `limit` to
            get the next batch of radios.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        radios : dict[str, Any]
            Page of Deezer content metadata for the radio
            recommendations.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <int>,
                        "md5_image": <str>,
                        "picture": <str>,
                        "picture_big": <str>,
                        "picture_medium": <str>,
                        "picture_small": <str>,
                        "picture_xl": <str>,
                        "timestamp": <int>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "radio"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_radio_recommendations")
        return self._request_resource_relationship(
            "GET",
            "user",
            user_id,
            "recommendations/radios",
            limit=limit,
            offset=offset,
        )

    def get_track_recommendations(
        self, user_id: int | str = "me", /
    ) -> dict[str, Any]:
        """
        `User > Recommendations > Tracks <https://developers.deezer.com
        /api/user/recommendations/tracks>`_: Get track recommendations.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of tracks to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first track to return. Use with `limit` to
            get the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of Deezer content metadata for the track
            recommendations.

            .. admonition:: Sample response
               :class: response dropdown

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
                        "timestamp": <int>,
                        "title": <str>,
                        "title_short": <str>,
                        "title_version": <str>,
                        "type": "track"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_track_recommendations")
        return self._request_resource_relationship(
            "GET", "user", user_id, "recommendations/tracks"
        )

    @TTLCache.cached_method(ttl="user")
    def get_saved_albums(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Albums <https://developers.deezer.com/api/user
        /albums>`__: Get Deezer catalog information for a user's
        favorite albums.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of albums to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first album to return. Use with `limit` to get
            the next batch of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        albums : dict[str, Any]
            Page of Deezer content metadata for the user's favorite
            albums.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "checksum": <str>,
                    "data": [
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
                        "cover": <str>,
                        "cover_big": <str>,
                        "cover_medium": <str>,
                        "cover_small": <str>,
                        "cover_xl": <str>,
                        "explicit_lyrics": <bool>,
                        "id": <int>,
                        "link": <str>,
                        "md5_image": <str>,
                        "nb_tracks": <int>,
                        "record_type": <str>,
                        "release_date": <str>,
                        "time_add": <int>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "album"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_saved_albums")
        return self._request_resource_relationship(
            "GET", "user", user_id, "albums", limit=limit, offset=offset
        )

    def save_albums(
        self,
        album_ids: int | str | list[int | str],
        /,
        *,
        user_id: int | str = "me",
    ) -> bool:
        """
        `User > Albums <https://developers.deezer.com/api
        /actions-post>`__: Add one or more albums to a user's favorites.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        album_ids : int or str; positional-only
            Deezer IDs of the albums.

            **Examples**: :code:`10546890`, :code:`"816455081"`,
            :code:`"10546890,816455081"`,
            :code:`[10546890, "816455081"]`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "users.save_albums", "manage_library"
        )
        album_ids, num_ids = self._prepare_deezer_ids(album_ids)
        return self._request_resource_relationship(
            "POST",
            "user",
            user_id,
            "albums",
            params={f"album_id{'s' if num_ids > 1 else ''}": album_ids},
        )

    def remove_saved_album(
        self, album_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        """
        `User > Albums <https://developers.deezer.com/api
        /actions-delete>`__: Remove an album from a user's favorites.

        .. admonition:: Permissions
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

                 :code:`delete_library` permission
                    Delete items from a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        album_id : int or str; positional-only
            Deezer ID of the album.

            **Examples**: :code:`10546890`, :code:`"816455081"`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "users.remove_saved_album", {"manage_library", "delete_library"}
        )
        self._validate_deezer_ids(album_id, _recursive=False)
        return self._request_resource_relationship(
            "DELETE", "user", user_id, "albums", params={"album_id": album_id}
        )

    @TTLCache.cached_method(ttl="user")
    def get_followed_artists(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Artists <https://developers.deezer.com/api/user
        /artists>`_: Get Deezer catalog information for a user's
        favorite artists.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of artists to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first artist to return. Use with `limit` to get
            the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        artists : dict[str, Any]
            Page of Deezer content metadata for the user's favorite
            artists.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "checksum": <str>,
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
                        "time_add": <int>,
                        "tracklist": <str>,
                        "type": "artist"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_followed_artists")
        return self._request_resource_relationship(
            "GET", "user", user_id, "artists", limit=limit, offset=offset
        )

    def follow_artists(
        self,
        artist_ids: int | str | list[int | str],
        /,
        *,
        user_id: int | str = "me",
    ) -> bool:
        """
        `User > Artists <https://developers.deezer.com/api
        /actions-post>`__: Add one or more artists to a user's
        favorites.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        artist_ids : int or str; positional-only
            Deezer IDs of the artists.

            **Examples**: :code:`3265001`, :code:`"330311461"`,
            :code:`"3265001,330311461"`,
            :code:`[3265001, "330311461"]`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "users.follow_artists", "manage_library"
        )
        artist_ids, num_ids = self._prepare_deezer_ids(artist_ids)
        return self._request_resource_relationship(
            "POST",
            "user",
            user_id,
            "artists",
            params={f"artist_id{'s' if num_ids > 1 else ''}": artist_ids},
        )

    def unfollow_artist(
        self, artist_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        """
        `User > Artists <https://developers.deezer.com/api
        /actions-delete>`__: Remove an artist from a user's favorites.

        .. admonition:: Permissions
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

                 :code:`delete_library` permission
                    Delete items from a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        artist_id : int or str; positional-only
            Deezer ID of the artist.

            **Examples**: :code:`3265001`, :code:`"330311461"`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "users.unfollow_artist", {"manage_library", "delete_library"}
        )
        self._validate_deezer_ids(artist_id, _recursive=False)
        return self._request_resource_relationship(
            "DELETE",
            "user",
            user_id,
            "artists",
            params={"artist_id": artist_id},
        )

    @TTLCache.cached_method(ttl="user")
    def get_user_playlists(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Playlists <https://developers.deezer.com/api/user
        /playlists>`__: Get Deezer catalog information for a user's
        playlists.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of playlists to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of Deezer content metadata for the user's playlists.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "data": [
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
                        "time_add": <int>,
                        "time_mod": <int>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "playlist"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_user_playlists")
        return self._request_resource_relationship(
            "GET", "user", user_id, "playlists", limit=limit, offset=offset
        )

    def follow_playlists(
        self,
        playlist_ids: int | str | list[int | str],
        /,
        *,
        user_id: int | str = "me",
    ) -> bool:
        """
        `User > Playlists <https://developers.deezer.com/api
        /actions-post>`__: Add one or more playlists to a user's
        favorites.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        playlist_ids : int or str; positional-only
            Deezer IDs of the playlists.

            **Examples**: :code:`13651021241`, :code:`"1495242491"`,
            :code:`"13651021241,1495242491"`,
            :code:`[13651021241, "1495242491"]`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "users.follow_playlists", "manage_library"
        )
        playlist_ids, num_ids = self._prepare_deezer_ids(playlist_ids)
        return self._request_resource_relationship(
            "POST",
            "user",
            user_id,
            "playlists",
            params={f"playlist_id{'s' if num_ids > 1 else ''}": playlist_ids},
        )

    def unfollow_playlist(
        self,
        playlist_id: int | str,
        /,
        *,
        user_id: int | str = "me",
    ) -> bool:
        """
        `User > Playlists <https://developers.deezer.com/api
        /actions-delete>`__: Remove a playlist from a user's favorites.

        .. admonition:: Permissions
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

                 :code:`delete_library` permission
                    Delete items from a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        playlist_ids : int or str; positional-only
            Deezer IDs of the playlists.

            **Examples**: :code:`13651021241`, :code:`"1495242491"`,
            :code:`"13651021241,1495242491"`,
            :code:`[13651021241, "1495242491"]`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "users.unfollow_playlist", {"manage_library", "delete_library"}
        )
        self._validate_deezer_ids(playlist_id, _recursive=False)
        return self._request_resource_relationship(
            "DELETE",
            "user",
            user_id,
            "playlists",
            params={"playlist_id": playlist_id},
        )

    def create_playlist(
        self,
        name: str,
        /,
        *,
        user_id: int | str = "me",
    ) -> dict[str, int]:
        """
        `User > Playlists <https://developers.deezer.com/api
        /actions-post>`__: Create a playlist.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        name : str
            Playlist name.

            **Example**: :code:`"My New Playlist Title"`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        playlist_id : dict[str, int]
            Deezer ID of the newly created playlist.

            **Sample response**: :code:`{"id": <int>}`.
        """
        self._client._require_permissions(
            "users.create_playlist", "manage_library"
        )
        self._validate_type("name", name, str)
        if not len(name):
            raise ValueError("The playlist name cannot be blank.")
        return self._request_resource_relationship(
            "POST", "user", user_id, "playlists", params={"name": name}
        )

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
        """
        `Playlist <https://developers.deezer.com/api
        /playlist#actions>`__: Update the details of a playlist.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        .. important::

           At least one of :code:`name`, :code:`description`,
           :code:`public`, or :code:`collaborative` must be specified.

        Parameters
        ----------
        playlist_id : int or str; positional-only
            Deezer ID of the playlist.

            **Examples**: :code:`13651021241`, :code:`"1495242491"`.

        name : str; keyword-only; optional
            New playlist name.

        description : str; keyword-only; optional
            New playlist description.

        public : bool; keyword-only; optional
            Whether the playlist is displayed on the current user's
            profile.

        collaborative : bool; keyword-only; optional
            Whether other users can modify the playlist.

            .. note::

               :code:`collaborative=True` can only be set on public
               playlists.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "playlists.update_playlist_details", "manage_library"
        )
        params = {}
        if name is not None:
            self._validate_type("name", name, str)
            if not len(name):
                raise ValueError("The playlist name cannot be blank.")
            params["name"] = name
        if description is not None:
            self._validate_type("description", description, str)
            params["description"] = description
        if public is not None:
            self._validate_type("public", public, bool)
            params["public"] = public
        if collaborative is not None:
            self._validate_type("collaborative", collaborative, bool)
            if collaborative:
                if public is None:
                    params["public"] = False
                elif not public:
                    raise ValueError(
                        "`public` must be True when `collaborative` is True."
                    )
            params["collaborative"] = collaborative
        if not params:
            raise ValueError("At least one change must be specified.")
        return self._request_resource_relationship(
            "POST", "playlist", playlist_id, params=params
        )

    def delete_playlist(self, playlist_id: int | str, /) -> bool:
        """
        `Playlist <https://developers.deezer.com/api
        /playlist#actions>`__: Update the details of a playlist.

        .. admonition:: Permissions
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

                 :code:`delete_library` permission
                    Delete items from a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

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
        self._client._require_permissions(
            "playlists.delete_playlist", {"manage_library", "delete_library"}
        )
        return self._request_resource_relationship(
            "DELETE", "playlist", playlist_id
        )

    def add_playlist_tracks(
        self, playlist_id: int | str, /, track_ids: int | str | list[int | str]
    ) -> bool:
        """
        `Playlist > Tracks <https://developers.deezer.com/api
        /actions-post>`__: Add tracks to a playlist.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        playlist_id : int or str; positional-only
            Deezer ID of the playlist.

            **Examples**: :code:`13651021241`, :code:`"1495242491"`.

        track_ids : int, str, or list[int | str]
            Deezer IDs of the tracks.

            **Examples**: :code:`101602968`, :code:`"3541756661"`,
            :code:`"101602968,3541756661"`,
            :code:`[101602968, "3541756661"]`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "playlists.add_playlist_tracks", "manage_library"
        )
        return self._request_resource_relationship(
            "POST",
            "playlist",
            playlist_id,
            "tracks",
            params={"songs": self._prepare_deezer_ids(track_ids)[0]},
        )

    def reorder_playlist_tracks(
        self, playlist_id: int | str, /, track_ids: int | str | list[int | str]
    ) -> Any:
        """
        `Playlist > Tracks <https://developers.deezer.com/api
        /actions-post>`__: Reorder tracks in a playlist.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        playlist_id : int or str; positional-only
            Deezer ID of the playlist.

            **Examples**: :code:`13651021241`, :code:`"1495242491"`.

        track_ids : int, str, or list[int | str]
            Deezer IDs of the tracks in the desired order.

            **Examples**: :code:`101602968`, :code:`"3541756661"`,
            :code:`"101602968,3541756661"`,
            :code:`[101602968, "3541756661"]`.

            .. seealso::

               :meth:`~minim.api.deezer.PlaylistsAPI.get_playlist_tracks`
               – Get Deezer IDs of the tracks in the playlist.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "playlists.reorder_playlist_tracks", "manage_library"
        )
        return self._request_resource_relationship(
            "POST",
            "playlist",
            playlist_id,
            "tracks",
            params={"order": self._prepare_deezer_ids(track_ids)[0]},
        )

    @TTLCache.cached_method(ttl="user")
    def get_followed_podcasts(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Podcasts <https://developers.deezer.com/api/user
        /podcasts>`_: Get Deezer catalog information for a user's
        favorite podcasts.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of podcasts to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first podcast to return. Use with `limit` to
            get the next batch of podcasts.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        podcasts : dict[str, Any]
            Page of Deezer content metadata for the user's favorite
            podcasts.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "checksum": <str>,
                    "data": [
                      {
                        "available": <bool>,
                        "description": <str>,
                        "fans": <int>,
                        "id": <int>,
                        "link": <str>,
                        "picture": <str>,
                        "picture_big": <str>,
                        "picture_medium": <str>,
                        "picture_small": <str>,
                        "picture_xl": <str>,
                        "share": <str>,
                        "time_add": <int>,
                        "title": <str>,
                        "type": "podcast"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_followed_podcasts")
        return self._request_resource_relationship(
            "GET", "user", user_id, "podcasts", limit=limit, offset=offset
        )

    def follow_podcast(
        self, podcast_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        """
        `User > Podcasts <https://developers.deezer.com/api
        /actions-post>`__: Add a podcast to a user's favorites.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        podcast_id : int or str; positional-only
            Deezer ID of the podcast.

            **Examples**: :code:`436862`, :code:`"2740882"`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "users.follow_podcast", "manage_library"
        )
        self._validate_deezer_ids(podcast_id, _recursive=False)
        return self._request_resource_relationship(
            "POST",
            "user",
            user_id,
            "podcasts",
            params={"podcast_id": podcast_id},
        )

    def unfollow_podcast(
        self,
        podcast_id: int | str,
        /,
        *,
        user_id: int | str = "me",
    ) -> bool:
        """
        `User > Podcasts <https://developers.deezer.com/api
        /actions-delete>`__: Remove a podcast from a user's favorites.

        .. admonition:: Permissions
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

                 :code:`delete_library` permission
                    Delete items from a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        podcast_id : int or str; positional-only
            Deezer ID of the podcast.

            **Examples**: :code:`436862`, :code:`"2740882"`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "users.unfollow_podcast", {"manage_library", "delete_library"}
        )
        self._validate_deezer_ids(podcast_id, _recursive=False)
        return self._request_resource_relationship(
            "DELETE",
            "user",
            user_id,
            "podcasts",
            params={"podcast_id": podcast_id},
        )

    def set_episode_resume_point(
        self, episode_id: int | str, /, position: int
    ) -> dict[str, Any]:
        """
        `Episode > Bookmark <https://developers.deezer.com/api
        /actions-post>`__: Set a resume point for a podcast episode.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        episode_id : int or str; positional-only
            Deezer ID of the episode.

            **Example**: :code:`796445891`, :code:`"822265072"`.

        position : int
            Playback position within the episode as a percentage.

            **Valid range**: :code:`0` to :code:`100`.

        Returns
        -------
        status : dict[str, Any]
            Whether the request completed successfully.

            **Sample response**: :code:`{'error': [], 'results': True}`.
        """
        self._client._require_permissions(
            "episodes.set_episode_resume_point", "manage_library"
        )
        self._validate_deezer_ids(episode_id, _recursive=False)
        self._validate_number("position", position, int, 0, 100)
        return self._request_resource_relationship(
            "POST",
            "episode",
            episode_id,
            "bookmark",
            params={"offset": position},
        )

    def remove_episode_resume_point(
        self, episode_id: int | str, /
    ) -> dict[str, Any]:
        """
        `Episode > Bookmark <https://developers.deezer.com/api
        /actions-delete>`__: Remove a resume point for a podcast episode.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        episode_id : int or str; positional-only
            Deezer ID of the episode.

            **Example**: :code:`796445891`, :code:`"822265072"`.

        Returns
        -------
        status : dict[str, Any]
            Whether the request completed successfully.

            **Sample response**: :code:`{'error': [], 'results': True}`.
        """
        self._client._require_permissions(
            "episodes.remove_episode_resume_point", "manage_library"
        )
        self._validate_deezer_ids(episode_id, _recursive=False)
        return self._request_resource_relationship(
            "DELETE", "episode", episode_id, "bookmark"
        )

    @TTLCache.cached_method(ttl="user")
    def get_followed_radios(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Radios <https://developers.deezer.com/api/user
        /radios>`_: Get Deezer catalog information for a user's
        favorite radios.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        limit : int or None; keyword-only; optional
            Maximum number of radios to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first radio to return. Use with `limit` to
            get the next batch of radios.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        radios : dict[str, Any]
            Page of Deezer content metadata for the user's favorite
            radios.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "checksum": <str>,
                    "data": [],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_followed_radios")
        return self._request_resource_relationship(
            "GET", "user", user_id, "radios", limit=limit, offset=offset
        )

    def save_radio(
        self, radio_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        """
        `User > Radios <https://developers.deezer.com/api
        /actions-post>`__: Add a radio to a user's favorites.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        radio_id : int or str; positional-only
            Deezer ID of the radio.

            **Examples**: :code:`31061`, :code:`"37151"`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions("users.save_radio", "manage_library")
        self._validate_deezer_ids(radio_id, _recursive=False)
        return self._request_resource_relationship(
            "POST", "user", user_id, "radios", params={"radio_id": radio_id}
        )

    def remove_saved_radio(
        self, radio_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        """
        `User > Radios <https://developers.deezer.com/api
        /actions-delete>`__: Remove a radio from a user's favorites.

        .. admonition:: Permissions
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

                 :code:`delete_library` permission
                    Delete items from a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        radio_id : int or str; positional-only
            Deezer ID of the radio.

            **Examples**: :code:`31061`, :code:`"37151"`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "users.remove_saved_radio", {"manage_library", "delete_library"}
        )
        self._validate_deezer_ids(radio_id, _recursive=False)
        return self._request_resource_relationship(
            "DELETE", "user", user_id, "radios", params={"radio_id": radio_id}
        )

    @TTLCache.cached_method(ttl="user")
    def get_saved_tracks(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Tracks <https://developers.deezer.com/api/user
        /tracks>`_: Get Deezer catalog information for a user's
        favorite tracks.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

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
            Page of Deezer content metadata for the user's favorite
            tracks.

            .. admonition:: Sample response
               :class: response dropdown

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
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_saved_tracks")
        return self._request_resource_relationship(
            "GET", "user", user_id, "tracks", limit=limit, offset=offset
        )

    def save_tracks(
        self,
        track_ids: int | str | list[int | str],
        /,
        *,
        user_id: int | str = "me",
    ) -> bool:
        """
        `User > Tracks <https://developers.deezer.com/api
        /actions-post>`__: Add one or more tracks to a user's favorites.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        track_ids : int, str, or list[int | str]; positional-only
            Deezer IDs of the tracks.

            **Examples**: :code:`101602968`, :code:`"3541756661"`,
            :code:`"101602968,3541756661"`,
            :code:`[101602968, "3541756661"]`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "users.save_tracks", "manage_library"
        )
        track_ids, num_ids = self._prepare_deezer_ids(track_ids)
        return self._request_resource_relationship(
            "POST",
            "user",
            user_id,
            "tracks",
            params={f"track_id{'s' if num_ids > 1 else ''}": track_ids},
        )

    def remove_saved_track(
        self, track_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        """
        `User > Tracks <https://developers.deezer.com/api
        /actions-delete>`__: Remove a track from a user's favorites.

        .. admonition:: Permissions
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

                 :code:`delete_library` permission
                    Delete items from a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        track_id : int or str; positional-only
            Deezer ID of the track.

            **Examples**: :code:`101602968`, :code:`"3541756661"`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "users.remove_saved_track", {"manage_library", "delete_library"}
        )
        self._validate_deezer_ids(track_id, _recursive=False)
        return self._request_resource_relationship(
            "DELETE", "user", user_id, "tracks", params={"track_id": track_id}
        )

    @TTLCache.cached_method(ttl="user")
    def get_user_tracks(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Personal Songs <https://developers.deezer.com/api/user
        /personal_songs>`_: Get Deezer catalog information for a user's
        uploaded tracks.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

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
            Page of Deezer content metadata for the user's uploaded
            tracks.

            .. admonition:: Sample response
               :class: response dropdown

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
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("users.get_user_tracks")
        return self._request_resource_relationship(
            "GET", "user", user_id, "tracks", limit=limit, offset=offset
        )

    def update_user_track_details(
        self,
        track_id: int | str,
        /,
        *,
        album: str | None = None,
        artist: str | None = None,
        title: str | None = None,
    ) -> bool:
        """
        `Track <https://developers.deezer.com/api/actions-post>`__:
        Update the details of a user-uploaded track.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_library` permission
                    Manage a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        .. important::

           At least one of :code:`album`, :code:`artist`, or
           :code:`title` must be specified.

        Parameters
        ----------
        track_id : int or str; positional-only
            Deezer ID of the track.

            **Examples**: :code:`-3140371023`, :code:`"-3140371043"`.

        album : str; keyword-only; optional
            Album name.

        artist : str; keyword-only; optional
            Artist name.

        title : str; keyword-only; optional
            Track title.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "tracks.update_user_track_details", "manage_library"
        )
        params = {}
        if album is not None:
            self._validate_type("album", album, str)
            if not len(album):
                raise ValueError("`album` is blank.")
            params["album"] = album
        if artist is not None:
            self._validate_type("artist", artist, str)
            if not len(artist):
                raise ValueError("`artist` is blank.")
            params["artist"] = artist
        if title is not None:
            self._validate_type("title", title, str)
            if not len(title):
                raise ValueError("`title` is blank.")
            params["title"] = title
        if not params:
            raise ValueError("At least one change must be specified.")
        return self._request_resource_relationship(
            "POST", "track", track_id, params=params
        )

    def delete_user_track(self, track_id: int | str, /) -> bool:
        """
        `Track <https://developers.deezer.com/api/actions-delete>`__:
        Delete a user-uploaded track.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`delete_library` permission
                    Delete items from a user's library. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        track_id : int or str; positional-only
            Deezer ID of the track.

            **Examples**: :code:`-3140371023`, :code:`"-3140371043"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "tracks.delete_user_track", "delete_library"
        )
        return self._request_resource_relationship("DELETE", "track", track_id)

    @TTLCache.cached_method(ttl="user")
    def get_followed_users(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Followings <https://developers.deezer.com/api/user
        /followings>`_: Get Deezer catalog information for other users
        followed by a user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

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
            Page of Deezer content metadata for the followed users.

            .. admonition:: Sample response
               :class: response dropdown

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
        self._client._require_authentication("users.get_followed_users")
        return self._request_resource_relationship(
            "GET", "user", user_id, "followings", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="user")
    def get_user_followers(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `User > Followers <https://developers.deezer.com/api/user
        /followers>`_: Get Deezer catalog information for a user's
        followers.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access the user's favorite items, playlists, and
                    followed people.

        Parameters
        ----------
        user_id : int or str; positional-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

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
            Page of Deezer content metadata for the user's followers.

            .. admonition:: Sample response
               :class: response dropdown

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
        self._client._require_authentication("users.get_user_followers")
        return self._request_resource_relationship(
            "GET", "user", user_id, "followers", limit=limit, offset=offset
        )

    def follow_user(
        self, follow_user_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        """
        `User > Followings <https://developers.deezer.com/api
        /actions-post>`__: Follow a user.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_community` permission
                    Manage a user's friends. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        follow_user_id : int or str; positional-only
            Deezer ID of the user to follow.

            **Example**: :code:`5395005364`, :code:`"5395005364"`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "users.follow_user", "manage_community"
        )
        self._validate_deezer_ids(follow_user_id, _recursive=False)
        return self._request_resource_relationship(
            "POST",
            "user",
            user_id,
            "followings",
            params={"user_id": follow_user_id},
        )

    def unfollow_user(
        self, unfollow_user_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        """
        `User > Followings <https://developers.deezer.com/api
        /actions-delete>`__: Unfollow a user.

        .. admonition:: Permission
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`manage_community` permission
                    Manage a user's friends. `Learn more.
                    <https://developers.deezer.com/api/permissions>`__

        Parameters
        ----------
        unfollow_user_id : int or str; positional-only
            Deezer ID of the user to unfollow.

            **Example**: :code:`5395005364`, :code:`"5395005364"`.

        user_id : int or str; keyword-only; default: :code:`"me"`
            Deezer ID of the user. If authenticated, :code:`"me"` can be
            used in lieu of a Deezer ID for the current user.

            **Example**: :code:`5395005364`, :code:`"5395005364"`,
            :code:`"me"`.

        Returns
        -------
        success : bool
            Whether the request completed successfully.
        """
        self._client._require_permissions(
            "users.unfollow_user", "manage_community"
        )
        self._validate_deezer_ids(unfollow_user_id, _recursive=False)
        return self._request_resource_relationship(
            "DELETE",
            "user",
            user_id,
            "followings",
            params={"user_id": unfollow_user_id},
        )
