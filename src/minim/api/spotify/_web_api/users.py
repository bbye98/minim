from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import SpotifyWebAPI


class UsersAPI(ResourceAPI):
    """
    Users API endpoints for the Spotify Web API.

    .. note::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPI`
       and should not be instantiated directly.
    """

    _PEOPLE_TYPES = {"artists", "users"}
    _TIME_RANGES = {"long_term", "medium_term", "short_term"}
    _client: "SpotifyWebAPI"

    @classmethod
    def _validate_time_range(cls, time_range: str, /) -> None:
        """
        Validate time range.

        Parameters
        ----------
        time_range : str; positional-only
            Time range.
        """
        if (
            not isinstance(time_range, str)
            or time_range.lower() not in cls._TIME_RANGES
        ):
            time_ranges_str = "', '".join(sorted(cls._TIME_RANGES))
            raise ValueError(
                f"Invalid time range {time_range!r}. "
                f"Valid values: '{time_ranges_str}'."
            )

    @TTLCache.cached_method(ttl="catalog")
    def get_my_profile(self) -> dict[str, Any]:
        """
        `Users > Get Current User's Profile
        <https://developer.spotify.com/documentation/web-api/reference
        /get-current-users-profile>`_: Get detailed profile information
        for the current user.

        .. admonition:: Authorization scopes and user authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access private profile information.

           .. tab:: Optional

              :code:`user-read-private`
                 Access your subscription details. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-read-private>`__

              :code:`user-read-email`
                 Get your real email address. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-read-email>`__

        Returns
        -------
        profile : dict[str, Any]
            Current user's profile information.

            .. admonition:: Sample responses
               :class: dropdown

               .. code::

                  {
                    "country": <str>,
                    "display_name": <str>,
                    "email": <str>,
                    "explicit_content": {
                      "filter_enabled": <bool>,
                      "filter_locked": <bool>
                    },
                    "external_urls": {
                      "spotify": <str>
                    },
                    "followers": {
                      "href": <str>,
                      "total": <int>
                    },
                    "href": <str>,
                    "id": <str>,
                    "images": [
                      {
                        "height": <int>,
                        "url": <str>,
                        "width": <int>
                      }
                    ],
                    "product": <str>,
                    "type": "user",
                    "uri": <str>
                  }
        """
        self._client._require_authentication("users.get_my_profile")
        return self._client._request("GET", "me").json()

    @TTLCache.cached_method(ttl="catalog")
    def get_user_profile(
        self, user_id: str | None = None, /
    ) -> dict[str, Any]:
        """
        `Users > Get Current User's Profile
        <https://developer.spotify.com/documentation/web-api/reference
        /get-current-users-profile>`_: Get detailed profile information
        for the current user․
        `Users > Get User's Profile <https://developer.spotify.com
        /documentation/web-api/reference/get-users-profile>`_: Get
        public profile information for a Spotify user.

        .. admonition:: Authorization scopes
           :class: authorization-scope

           .. tab:: Conditional

              User authentication
                 Access private profile information.

           .. tab:: Optional

              :code:`user-read-private`
                 Access your subscription details. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-read-private>`__

              :code:`user-read-email`
                 Get your real email address. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-read-email>`__

        Parameters
        ----------
        user_id : str; positional-only; optional
            Spotify user ID. If not provided, the current user's
            profile is returned.

            **Example**: :code:`"smedjan"`.

        Returns
        -------
        profile : dict[str, Any]
            User's profile information.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Current user

                  .. code::

                     {
                       "country": <str>,
                       "display_name": <str>,
                       "email": <str>,
                       "explicit_content": {
                         "filter_enabled": <bool>,
                         "filter_locked": <bool>
                       },
                       "external_urls": {
                         "spotify": <str>
                       },
                       "followers": {
                         "href": <str>,
                         "total": <int>
                       },
                       "href": <str>,
                       "id": <str>,
                       "images": [
                         {
                           "height": <int>,
                           "url": <str>,
                           "width": <int>
                         }
                       ],
                       "product": <str>,
                       "type": "user",
                       "uri": <str>
                     }

               .. tab:: Public user

                  .. code::

                     {
                       "display_name": <str>,
                       "external_urls": {
                         "spotify": <str>
                       },
                       "followers": {
                         "href": <str>,
                         "total": <int>
                       },
                       "href": <str>,
                       "id": <str>,
                       "images": [
                         {
                           "height": <int>,
                           "url": <str>,
                           "width": <int>
                         }
                       ],
                       "type": "user",
                       "uri": <str>
                     }
        """
        if user_id is None:
            return self.get_my_profile()
        self._client._validate_type("user_id", user_id, str)
        return self._client._request("GET", f"users/{user_id}").json()

    @TTLCache.cached_method(ttl="top")
    def get_my_top_items(
        self,
        item_type: str,
        /,
        *,
        time_range: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Users > Get User's Top Items
        <https://developer.spotify.com/documentation/web-api/reference
        /get-users-top-artists-and-tracks>`_: Get Spotify catalog
        information for the current user's top artists or tracks.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-top-read` scope
                 Read your top artists and contents. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-top-read>`__

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        item_type : str; positional-only
            Type of item to return.

            **Valid values**: :code:`"artists"`, :code:`"tracks"`.

        time_range : str; keyword-only; optional
            Time frame over which the current user's listening history
            is analyzed to determine top artists or tracks.

            **Valid values**:

            .. container::

               * :code:`"long_term"` – Approximately one year of data,
                 including all new data as it becomes available.
               * :code:`"medium_term"` – Approximately the last six
                 months of data.
               * :code:`"short_term"` – Approximately the last four
                 weeks of data.

            **API default**: :code:`"medium_term"`.

        limit : int; keyword-only; optional
            Maximum number of artists or tracks to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first artist or track to return. Use with
            `limit` to get the next batch of artists or tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        items : dict[str, Any]
            Page of Spotify content metadata for the current user's top
            artists or tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. tab:: :code:`resource_type="artists"`

                  .. code::

                     {
                       "href": <str>,
                       "items": [
                         {
                           "external_urls": {
                             "spotify": <str>
                           },
                           "followers": {
                             "href": <str>,
                             "total": <int>
                           },
                           "genres": <list[str]>,
                           "href": <str>,
                           "id": <str>,
                           "images": [
                             {
                               "height": <int>,
                               "url": <str>,
                               "width": <int>
                             }
                           ],
                           "name": <str>,
                           "type": "artist",
                           "uri": <str>
                         }
                       ],
                       "limit": <int>,
                       "next": <str>,
                       "offset": <int>,
                       "previous": <str>,
                       "total": <int>
                     }

               .. tab:: :code:`resource_type="tracks"`

                  .. code::

                     {
                       "href": <str>,
                       "items": [
                         {
                           "album": {
                             "album_type": <str>,
                             "artists": [
                               {
                                 "external_urls": {
                                   "spotify": <str>
                                 },
                                 "href": <str>,
                                 "id": <str>,
                                 "name": <str>,
                                 "type": "artist",
                                 "uri": <str>
                               }
                             ],
                             "available_markets": <list[str]>,
                             "external_urls": {
                               "spotify": <str>
                             },
                             "href": <str>,
                             "id": <str>,
                             "images": [
                               {
                                 "height": <int>,
                                 "url": <str>,
                                 "width": <int>
                               }
                             ],
                             "is_playable": <bool>,
                             "name": <str>,
                             "release_date": <str>,
                             "release_date_precision": <str>,
                             "total_tracks": <int>,
                             "type": "album",
                             "uri": <str>
                           },
                           "artists": [
                             {
                               "external_urls": {
                                 "spotify": <str>
                               },
                               "href": <str>,
                               "id": <str>,
                               "name": <str>,
                               "type": "artist",
                               "uri": <str></str>
                             }
                           ],
                           "available_markets": <list[str]>,
                           "disc_number": <int>,
                           "duration_ms": <int>,
                           "explicit": <bool>,
                           "external_ids": {
                             "isrc": <str>
                           },
                           "external_urls": {
                             "spotify": <str>
                           },
                           "href": <str>,
                           "id": <str>,
                           "is_local": <bool>,
                           "is_playable": <bool>,
                           "name": <str>,
                           "popularity": <int>,
                           "preview_url": <str>,
                           "track_number": <int>,
                           "type": "track",
                           "uri": <str>
                         }
                       ],
                       "limit": <int>,
                       "next": <str>,
                       "offset": <int>,
                       "previous": <str>,
                       "total": <int>
                     }
        """
        self._client._validate_type("item_type", item_type, str)
        item_type = item_type.strip().lower()
        if item_type not in {"artists", "tracks"}:
            raise ValueError(
                f"Invalid item type {item_type!r}. "
                "Valid values: 'artists', 'tracks'."
            )
        self._client._require_scopes(
            f"users.get_top_{item_type}", "user-top-read"
        )
        params = {}
        if time_range is not None:
            self._client.users._validate_time_range(time_range)
            params["time_range"] = time_range
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"me/top/{item_type}", params=params
        ).json()

    def follow_playlist(
        self, playlist_id: str, /, *, public: bool | None = None
    ) -> None:
        """
        `Users > Follow Playlist <https://developer.spotify.com
        /documentation/web-api/reference/follow-playlist>`_: Follow a
        playlist.

        .. admonition:: Authorization scopes and user authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

           .. tab:: Conditional

              :code:`playlist-modify-public` scope
                 Manage your public playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-public>`__

              :code:`playlist-modify-private` scope
                 Manage your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-private>`__

        Parameters
        ----------
        playlist_id : str; positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        public : bool; keyword-only; optional
            Whether the playlist is displayed on the current user's
            profile.

            **API default**: :code:`True`.
        """
        self._client._require_authentication("users.follow_playlist")
        self._client._validate_spotify_id(playlist_id)
        payload = {}
        if isinstance(public, bool):
            self._client._require_scopes(
                "users.follow_playlist",
                f"playlist-modify-{'public' if public else 'private'}",
            )
            payload["public"] = public
        self._client._request(
            "PUT", f"playlists/{playlist_id}/followers", json=payload
        )

    def unfollow_playlist(self, playlist_id: str, /) -> None:
        """
        `Users > Unfollow Playlist <https://developer.spotify.com
        /documentation/web-api/reference/unfollow-playlist>`_: Unfollow
        a playlist.

        .. admonition:: Authorization scopes and user authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

           .. tab:: Conditional

              :code:`playlist-modify-public` scope
                 Manage your public playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-public>`__

              :code:`playlist-modify-private` scope
                 Manage your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-private>`__

        Parameters
        ----------
        playlist_id : str; positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.
        """
        self._client._require_authentication("users.unfollow_playlist")
        self._client._validate_spotify_id(playlist_id)
        self._client._request("DELETE", f"playlists/{playlist_id}/followers")

    def get_my_followed_artists(
        self, *, cursor: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """
        `Users > Get Followed Artists <https://developer.spotify.com
        /documentation/web-api/reference/get-followed>`_: Get Spotify
        catalog information for artists followed by the current user.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-read` scope
                 Access your followers and who you are following. `Learn
                 more. <https://developer.spotify.com/documentation
                 /web-api/concepts/scopes#user-follow-read>`__

        Parameters
        ----------
        cursor : str; keyword-only; optional
            Cursor (Spotify ID of the last artist retrieved in the
            previous request) for fetching the next page of results.

            **Example**: :code:`"0I2XqVXqHScXjHhk6AYYRe"`.

        limit : int; keyword-only; optional
            Maximum number of artists to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        Returns
        -------
        artists : dict[str, Any]
            Spotify content metadata for the artists followed by the
            current user.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "artists": {
                      "cursors": {
                        "after": <str>,
                        "before": <str>
                      },
                      "href": <str>,
                      "items": [
                        {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "followers": {
                            "href": <str>,
                            "total": <int>
                          },
                          "genres": <list[str]>,
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "popularity": <int>,
                          "type": "artist",
                          "uri": <str>
                        }
                      ],
                      "limit": <int>,
                      "next": <str>,
                      "total": <int>
                    }
                  }
        """
        self._client._require_scopes(
            "users.get_followed_artists", "user-follow-read"
        )
        params = {"type": "artist"}
        if cursor is not None:
            self._client._validate_spotify_id(cursor)
            params["after"] = cursor
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        return self._client._request(
            "GET", "me/following", params=params
        ).json()

    def follow_artists(self, artist_ids: str | list[str], /) -> None:
        """
        `Users > Follow Artists <https://developer.spotify.com
        /documentation/web-api/reference/follow-artists-users>`_: Follow
        one or more artists.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-modify` scope
                 Manage your saved content. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-follow-modify>`__

        Parameters
        ----------
        artist_ids : str or list[str]; positional-only
            Spotify IDs of the artists. A maximum of 50 IDs can be sent
            in a request.

            **Examples**:

            .. container::

               * :code:`"2CIMQHirSU0MQqyYHq0eOx"`
               * :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E"`
               * :code:`["2CIMQHirSU0MQqyYHq0eOx",
                 "57dN52uHvrHOxijzpIgu3E"]`
        """
        self._client._require_scopes(
            "users.follow_artists", "user-follow-modify"
        )
        return self._manage_followed_people("PUT", "artists", artist_ids)

    def follow_users(self, user_ids: str | list[str], /) -> None:
        """
        `Users > Follow Users <https://developer.spotify.com
        /documentation/web-api/reference/follow-artists-users>`_: Follow
        one or more Spotify users.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-modify` scope
                 Manage your saved content. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-follow-modify>`__

        Parameters
        ----------
        user_ids : str or list[str]; positional-only
            Spotify user IDs. A maximum of 50 IDs can be sent in a
            request.

            **Examples**: :code:`"smedjan"`, :code:`"smedjan,bbye98"`,
            :code:`["smedjan", "bbye98"]`.
        """
        self._client._require_scopes(
            "users.follow_users", "user-follow-modify"
        )
        return self._manage_followed_people("PUT, users", user_ids)

    def unfollow_artists(self, artist_ids: str | list[str], /) -> None:
        """
        `Users > Unfollow Artists <https://developer.spotify.com
        /documentation/web-api/reference/unfollow-artists-users>`_:
        Unfollow one or more artists.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-modify` scope
                 Manage your saved content. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-follow-modify>`__

        Parameters
        ----------
        artist_ids : str or list[str]; positional-only
            Spotify IDs of the artists. A maximum of 50 IDs can be sent
            in a request.

            **Examples**:

            .. container::

               * :code:`"2CIMQHirSU0MQqyYHq0eOx"`
               * :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E"`
               * :code:`["2CIMQHirSU0MQqyYHq0eOx",
                 "57dN52uHvrHOxijzpIgu3E"]`
        """
        self._client._require_scopes(
            "users.unfollow_artists", "user-follow-modify"
        )
        return self._manage_followed_people("DELETE", "artists", artist_ids)

    def unfollow_users(self, user_ids: str | list[str], /) -> None:
        """
        `Users > Unfollow Users <https://developer.spotify.com
        /documentation/web-api/reference/unfollow-artists-users>`_:
        Unfollow one or more Spotify users.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-modify` scope
                 Manage your saved content. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-follow-modify>`__

        Parameters
        ----------
        user_ids : str or list[str]; positional-only
            Spotify user IDs. A maximum of 50 IDs can be sent in a
            request.

            **Examples**: :code:`"smedjan"`, :code:`"smedjan,bbye98"`,
            :code:`["smedjan", "bbye98"]`.
        """
        self._client._require_scopes(
            "users.unfollow_users", "user-follow-modify"
        )
        return self._manage_followed_people("DELETE", "users", user_ids)

    def is_following_artists(
        self, artist_ids: str | list[str], /
    ) -> list[bool]:
        """
        `Users > Check If Current User Follows Artists
        <https://developer.spotify.com/documentation/web-api/reference
        /check-current-user-follows>`_: Check whether the current user
        is following one or more artists.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-read` scope
                 Access your followers and who you are following. `Learn
                 more. <https://developer.spotify.com/documentation
                 /web-api/concepts/scopes#user-follow-read>`__

        Parameters
        ----------
        artist_ids : str or list[str]; positional-only
            Spotify IDs of the artists. A maximum of 50 IDs can be sent
            in a request.

            **Examples**:

            .. container::

               * :code:`"2CIMQHirSU0MQqyYHq0eOx"`
               * :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E"`
               * :code:`["2CIMQHirSU0MQqyYHq0eOx",
                 "57dN52uHvrHOxijzpIgu3E"]`

        Returns
        -------
        following : list[bool]
            Whether the current user follows the specified artists.

            **Sample response**: :code:`[False, True]`.
        """
        self._client._require_scopes(
            "users.is_following_artists", "user-follow-read"
        )
        return self._is_following_people("artists", artist_ids)

    def is_following_users(self, user_ids: str | list[str], /) -> list[bool]:
        """
        `Users > Check If Current User Follows Users
        <https://developer.spotify.com/documentation/web-api/reference
        /check-current-user-follows>`_: Check whether the current user
        is following one or more Spotify users.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-read` scope
                 Access your followers and who you are following. `Learn
                 more. <https://developer.spotify.com/documentation
                 /web-api/concepts/scopes#user-follow-read>`__

        Parameters
        ----------
        user_ids : str or list[str]; positional-only
            Spotify user IDs. A maximum of 50 IDs can be sent in a
            request.

            **Examples**: :code:`"smedjan"`, :code:`"smedjan,bbye98"`,
            :code:`["smedjan", "bbye98"]`.

        Returns
        -------
        following : list[bool]
            Whether the current user follows the specified users.

            **Sample response**: :code:`[False, True]`.
        """
        self._client._require_scopes(
            "users.is_following_users", "user-follow-read"
        )
        return self._is_following_people("users", user_ids)

    def is_following_playlist(self, playlist_id: str, /) -> list[bool]:
        """
        `Users > Check if Current User Follows Playlist
        <https://developer.spotify.com/documentation/web-api/reference
        /check-if-user-follows-playlist>`_: Check whether the current
        user is following a playlist.

        .. admonition:: Authorization scope and user authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

           .. tab:: Conditional

              :code:`playlist-read-private` scope
                 Access your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-read-private>`__

        Parameters
        ----------
        playlist_id : str; positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        Returns
        -------
        following : list[bool]
            Whether the current user follows the specified playlist.

            **Sample response**: :code:`[True]`.
        """
        self._client._require_authentication("users.is_following_playlist")
        self._client._validate_spotify_id(playlist_id)
        return self._client._request(
            "GET", f"playlists/{playlist_id}/followers/contains"
        ).json()

    def get_my_saved_albums(
        self,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get User's Saved Albums <https://developer.spotify.com
        /documentation/web-api/reference/get-users-saved-albums>`_: Get
        Spotify catalog information for the albums saved in the current
        user's library.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If provided, only content
            available in that market is returned. When a user access
            token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither a country code is provided nor a country can
               be determined from the user account, the content is
               considered unavailable for the client.

            **Example**: :code:`"ES"`.

        limit : int; keyword-only; optional
            Maximum number of albums to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first album to return. Use with `limit` to get
            the next batch of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        albums : dict[str, Any]
            Page of Spotify content metadata for the user's saved
            albums.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "added_at": <str>,
                        "album": {
                          "album_type": <str>,
                          "artists": [
                            {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "href": <str>,
                              "id": <str>,
                              "name": <str>,
                              "type": "artist",
                              "uri": <str>
                            }
                          ],
                          "available_markets": <list[str]>,
                          "copyrights": [
                            {
                              "text": <str>,
                              "type": <str>
                            }
                          ],
                          "external_ids": {
                            "ean": <str>,
                            "isrc": <str>,
                            "upc": <str>
                          },
                          "external_urls": {
                            "spotify": <str>
                          },
                          "genres": <list[str]>,
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "height": <int>,
                              "url": <str>,
                              "width": <int>
                            }
                          ],
                          "label": <str>,
                          "name": <str>,
                          "popularity": <int>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "restrictions": {
                            "reason": <str>
                          },
                          "total_tracks": <int>,
                          "tracks": {
                            "href": <str>,
                            "items": [
                              {
                                "artists": [
                                  {
                                    "external_urls": {
                                      "spotify": <str>
                                    },
                                    "href": <str>,
                                    "id": <str>,
                                    "name": <str>,
                                    "type": "artist",
                                    "uri": <str>
                                  }
                                ],
                                "available_markets": <list[str]>,
                                "disc_number": <int>,
                                "duration_ms": <int>,
                                "explicit": <bool>,
                                "external_urls": {
                                  "spotify": <str>
                                },
                                "href": <str>,
                                "id": <str>,
                                "is_local": <bool>,
                                "is_playable": <bool>,
                                "linked_from": {
                                  "external_urls": {
                                    "spotify": <str>
                                  },
                                  "href": <str>,
                                  "id": <str>,
                                  "type": "track",
                                  "uri": <str>
                                },
                                "name": <str>,
                                "preview_url": <str>,
                                "restrictions": {
                                  "reason": <str>
                                },
                                "track_number": <int>,
                                "type": "track",
                                "uri": <str>
                              }
                            ],
                            "limit": <int>,
                            "next": <str>,
                            "offset": <int>,
                            "previous": <str>,
                            "total": <int>
                          },
                          "type": "album",
                          "uri": <str>
                        }
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        self._client._require_scopes(
            "albums.get_my_saved_albums", "user-library-read"
        )
        return self._get_my_saved_entities(
            "albums", country_code=country_code, limit=limit, offset=offset
        )

    def save_albums(self, album_ids: str | list[str], /) -> None:
        """
        `Albums > Save Albums for Current User
        <https://developer.spotify.com/documentation/web-api/reference
        /save-albums-user>`_: Save one or more albums to the current
        user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify` scope
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        album_ids : str or list[str]; positional-only
            Spotify IDs of the albums. A maximum of 20 IDs can be sent
            in a request.

            **Examples**:

            .. container::

               * :code:`"382ObEPsp2rxGrnsizN5TX"`
               * :code:`"382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo"`
               * :code:`["382ObEPsp2rxGrnsizN5TX",
                 "1A2GTWGtFfWp7KSQTwWOyo"]`
        """
        self._client._require_scopes(
            "albums.save_albums", "user-library-modify"
        )
        self._manage_saved_entities("PUT", "albums", album_ids, limit=20)

    def remove_saved_albums(self, album_ids: str | list[str], /) -> None:
        """
        `Albums > Remove User's Saved Albums
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-albums-user>`_: Remove one or more albums from the
        current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify` scope
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        album_ids : str or list[str]; positional-only
            Spotify IDs of the albums. A maximum of 20 IDs can be sent
            in a request.

            **Examples**:

            .. container::

               * :code:`"382ObEPsp2rxGrnsizN5TX"`
               * :code:`"382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo"`
               * :code:`["382ObEPsp2rxGrnsizN5TX",
                 "1A2GTWGtFfWp7KSQTwWOyo"]`
        """
        self._client._require_scopes(
            "albums.remove_saved_albums", "user-library-modify"
        )
        self._manage_saved_entities("DELETE", "albums", album_ids, limit=20)

    def are_albums_saved(self, album_ids: str | list[str], /) -> list[bool]:
        """
        `Albums > Check User's Saved Albums
        <https://developer.spotify.com/documentation/web-api/reference
        /check-users-saved-albums>`_: Check whether one or more albums
        are saved in the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

        Parameters
        ----------
        album_ids : str or list[str]; positional-only
            Spotify IDs of the albums. A maximum of 20 IDs can be sent
            in a request.

            **Examples**:

            .. container::

               * :code:`"382ObEPsp2rxGrnsizN5TX"`
               * :code:`"382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo"`
               * :code:`["382ObEPsp2rxGrnsizN5TX",
                 "1A2GTWGtFfWp7KSQTwWOyo"]`

        Returns
        -------
        saved : list[bool]
            Whether the current user has the specified albums saved in
            their library.
        """
        self._client._require_scopes(
            "albums.are_albums_saved", "user-library-read"
        )
        return self._are_entities_saved("albums", album_ids, limit=20)

    def get_my_saved_audiobooks(
        self,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Audiobooks > Get User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference
        /get-users-saved-audiobooks>`_: Get Spotify catalog information
        for the audiobooks saved in the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

        Parameters
        ----------
        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If provided, only content
            available in that market is returned. When a user access
            token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither a country code is provided nor a country can
               be determined from the user account, the content is
               considered unavailable for the client.

            **Example**: :code:`"ES"`.

        limit : int; keyword-only; optional
            Maximum number of audiobooks to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first audiobook to return. Use with `limit` to
            get the next batch of audiobooks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        audiobooks : dict[str, Any]
            Page of Spotify content metadata for the user's saved
            audiobooks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "authors": [
                          {
                            "name": <str>
                          }
                        ],
                        "available_markets": <list[str]>,
                        "copyrights": [
                          {
                            "text": <str>,
                            "type": <str>
                          }
                        ],
                        "description": <str>,
                        "edition": <str>,
                        "explicit": <bool>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "html_description": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "height": <int>,
                            "url": <str>,
                            "width": <int>
                          }
                        ],
                        "languages": <list[str]>,
                        "media_type": <str>,
                        "name": <str>,
                        "narrators": [
                          {
                            "name": <str>
                          }
                        ],
                        "publisher": <str>,
                        "total_chapters": <int>,
                        "type": "audiobook",
                        "uri": <str>
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        self._client._require_scopes(
            "audiobooks.get_my_saved_audiobooks", "user-library-read"
        )
        return self._get_my_saved_entities(
            "audiobooks", country_code=country_code, limit=limit, offset=offset
        )

    def save_audiobooks(self, audiobook_ids: str | list[str], /) -> None:
        """
        `Audiobooks > Save Audiobooks for Current User
        <https://developer.spotify.com/documentation/web-api/reference
        /save-albums-user>`_: Save one or more audiobooks to the current
        user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify` scope
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        audiobook_ids : str or list[str]; positional-only
            Spotify IDs of the audiobooks. A maximum of 50 IDs can be
            sent in a request.

            **Examples**:

            .. container::

               * :code:`"18yVqkdbdRvS24c0Ilj2ci"`
               * :code:`"18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ"`
               * :code:`["18yVqkdbdRvS24c0Ilj2ci",
                 "1HGw3J3NxZO1TP1BTtVhpZ"]`
        """
        self._client._require_scopes(
            "audiobooks.save_audiobooks", "user-library-modify"
        )
        self._manage_saved_entities("PUT", "audiobooks", audiobook_ids)

    def remove_saved_audiobooks(
        self, audiobook_ids: str | list[str], /
    ) -> None:
        """
        `Audiobooks > Remove User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-audiobooks-user>`_: Remove one or more audiobooks from
        the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify` scope
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        audiobook_ids : str or list[str]; positional-only
            Spotify IDs of the audiobooks. A maximum of 50 IDs can be
            sent in a request.

            **Examples**:

            .. container::

               * :code:`"18yVqkdbdRvS24c0Ilj2ci"`
               * :code:`"18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ"`
               * :code:`["18yVqkdbdRvS24c0Ilj2ci",
                 "1HGw3J3NxZO1TP1BTtVhpZ"]`
        """
        self._client._require_scopes(
            "audiobooks.remove_saved_audiobooks", "user-library-modify"
        )
        self._manage_saved_entities("DELETE", "audiobooks", audiobook_ids)

    def are_audiobooks_saved(
        self, audiobook_ids: str | list[str], /
    ) -> list[bool]:
        """
        `Audiobooks > Check User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference
        /check-users-saved-audiobooks>`_: Check whether one or more
        audiobooks are saved in the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

        Parameters
        ----------
        audiobook_ids : str or list[str]; positional-only
            Spotify IDs of the audiobooks. A maximum of 50 IDs can be
            sent in a request.

            **Examples**:

            .. container::

               * :code:`"18yVqkdbdRvS24c0Ilj2ci"`
               * :code:`"18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ"`
               * :code:`["18yVqkdbdRvS24c0Ilj2ci",
                 "1HGw3J3NxZO1TP1BTtVhpZ"]`

        Returns
        -------
        saved : list[bool]
            Whether the current user has the specified audiobooks saved
            in their library.
        """
        self._client._require_scopes(
            "audiobooks.are_audiobooks_saved", "user-library-read"
        )
        return self._are_entities_saved("audiobooks", audiobook_ids)

    def get_my_saved_episodes(
        self,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Episodes > Get User's Saved Episodes
        <https://developer.spotify.com/documentation/web-api/reference
        /get-multiple-episodes>`_: Get Spotify catalog information for
        the show episodes saved in the current user's library.

        .. admonition:: Authorization scopes and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

              :code:`user-read-playback-position` scope
                 Read your position in content you have played. `Learn
                 more. <https://developer.spotify.com/documentation
                 /web-api/concepts/scopes#user-read-playback-position>`__

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If provided, only content
            available in that market is returned. When a user access
            token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither a country code is provided nor a country can
               be determined from the user account, the content is
               considered unavailable for the client.

            **Example**: :code:`"ES"`.

        limit : int; keyword-only; optional
            Maximum number of show episodes to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first show episode to return. Use with `limit`
            to get the next batch of show episodes.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        episodes : dict[str, Any]
            Page of Spotify content metadata for the user's saved show
            episodes.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "added_at": <str>,
                        "episode": {
                          "audio_preview_url": <str>,
                          "description": <str>,
                          "duration_ms": <int>,
                          "explicit": <bool>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "html_description": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "height": <int>,
                              "url": <str>,
                              "width": <int>
                            }
                          ],
                          "is_externally_hosted": <bool>,
                          "is_playable": <bool>,
                          "language": <str>,
                          "languages": <list[str]>,
                          "name": <str>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "restrictions": {
                            "reason": <str>
                          },
                          "resume_point": {
                            "fully_played": <bool>,
                            "resume_position_ms": <int>
                          },
                          "show": {
                            "available_markets": <list[str]>,
                            "copyrights": [
                              {
                                "text": <str>,
                                "type": <str>
                              }
                            ],
                            "description": <str>,
                            "explicit": <bool>,
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "html_description": <str>,
                            "id": <str>,
                            "images": [
                              {
                                "height": <int>,
                                "url": <str>,
                                "width": <int>
                              }
                            ],
                            "is_externally_hosted": <bool>,
                            "languages": <list[str]>,
                            "media_type": <str>,
                            "name": <str>,
                            "publisher": <str>,
                            "total_episodes": <int>,
                            "type": "show",
                            "uri": <str>
                          },
                          "type": "episode",
                          "uri": <str>
                        }
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        self._client._require_scopes(
            "episodes.get_my_saved_episodes",
            {"user-library-read", "user-read-playback-position"},
        )
        return self._get_my_saved_entities(
            "episodes",
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    def save_episodes(self, episode_ids: str | list[str], /) -> None:
        """
        `Episodes > Save Episodes for Current User
        <https://developer.spotify.com/documentation/web-api/reference
        /save-episodes-user>`_: Save one or more show episodes to the
        current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify` scope
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        episode_ids : str or list[str]; positional-only
            Spotify IDs of the show episodes. A maximum of 50 IDs can be
            sent in a request.

            **Examples**:

            .. container::

               * :code:`"77o6BIVlYM3msb4MMIL1jH"`
               * :code:`"77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf"`
               * :code:`["77o6BIVlYM3msb4MMIL1jH",
                 "0Q86acNRm6V9GYx55SXKwf"]`
        """
        self._client._require_scopes(
            "episodes.save_episodes", "user-library-modify"
        )
        self._manage_saved_entities("PUT", "episodes", episode_ids)

    def remove_saved_episodes(self, episode_ids: str | list[str], /) -> None:
        """
        `Episodes > Remove User's Saved Episodes
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-episodes-user>`_: Remove one or more show episodes from
        the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify` scope
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        episode_ids : str or list[str]; positional-only
            Spotify IDs of the show episodes. A maximum of 50 IDs can be
            sent in a request.

            **Examples**:

            .. container::

               * :code:`"77o6BIVlYM3msb4MMIL1jH"`
               * :code:`"77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf"`
               * :code:`["77o6BIVlYM3msb4MMIL1jH",
                 "0Q86acNRm6V9GYx55SXKwf"]`
        """
        self._client._require_scopes(
            "episodes.remove_saved_episodes", "user-library-modify"
        )
        self._manage_saved_entities("DELETE", "episodes", episode_ids)

    def are_episodes_saved(
        self, episode_ids: str | list[str], /
    ) -> list[bool]:
        """
        `Episodes > Check User's Saved Episodes
        <https://developer.spotify.com/documentation/web-api/reference
        /check-users-saved-episodes>`_: Check whether one or more show
        episodes are saved in the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

        Parameters
        ----------
        episode_ids : str or list[str]; positional-only
            Spotify IDs of the show episodes. A maximum of 50 IDs can be
            sent in a request.

            **Examples**:

            .. container::

               * :code:`"77o6BIVlYM3msb4MMIL1jH"`
               * :code:`"77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf"`
               * :code:`["77o6BIVlYM3msb4MMIL1jH",
                 "0Q86acNRm6V9GYx55SXKwf"]`

        Returns
        -------
        saved : list[bool]
            Whether the current user has the specified show episodes
            saved in their library.
        """
        self._client._require_scopes(
            "episodes.are_episodes_saved", "user-library-read"
        )
        return self._are_entities_saved("episodes", episode_ids)

    def get_my_playlists(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        `Playlists > Get Current User's Playlists
        <https://developer.spotify.com/documentation/web-api/reference
        /get-a-list-of-current-users-playlists>`_: Get Spotify catalog
        information for playlists owned or followed by the current user.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`playlist-read-private` scope
                 Access your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-read-private>`__

        Parameters
        ----------
        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of Spotify content metadata for the current user's
            playlists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "collaborative": <bool>,
                        "description": <str>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "height": <int>,
                            "url": <str>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "owner": {
                          "display_name": <str>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "type": <str>,
                          "uri": <str>
                        },
                        "public": <bool>,
                        "snapshot_id": <str>,
                        "tracks": {
                          "href": <str>,
                          "total": <int>
                        },
                        "type": <str>,
                        "uri": <str>
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        self._client._require_scopes(
            "playlists.get_my_playlists", "playlist-read-private"
        )
        params = {}
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "me/playlists", params=params
        ).json()

    def get_user_playlists(
        self,
        user_id: str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Current User's Playlists
        <https://developer.spotify.com/documentation/web-api/reference
        /get-a-list-of-current-users-playlists>`_: Get Spotify catalog
        information for playlists owned or followed by the current user․
        `Playlists > Get User's Playlists <https://developer.spotify.com
        /documentation/web-api/reference/get-list-users-playlists>`_:
        Get Spotify catalog information for playlists owned or followed
        by a Spotify user.

        .. admonition:: Authorization scopes
           :class: authorization-scope

           .. tab:: Conditional

              User authentication
                 Access and manage your library.

              :code:`playlist-read-private` scope
                 Access your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-read-private>`__

              :code:`playlist-read-collaborative` scope
                 Access your collaborative playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-read-collaborative>`__

        Parameters
        ----------
        user_id : str; positional-only; optional
            Spotify user ID. If not provided, the current user's
            playlists are returned.

            **Example**: :code:`"smedjan"`.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of Spotify content metadata for the user's playlists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "collaborative": <bool>,
                        "description": <str>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "height": <int>,
                            "url": <str>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "owner": {
                          "display_name": <str>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "type": <str>,
                          "uri": <str>
                        },
                        "public": <bool>,
                        "snapshot_id": <str>,
                        "tracks": {
                          "href": <str>,
                          "total": <int>
                        },
                        "type": <str>,
                        "uri": <str>
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        if user_id is None:
            return self.get_my_playlists(limit=limit, offset=offset)
        params = {}
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        self._client._validate_spotify_id(user_id, enforce_length=False)
        return self._client._request(
            "GET", f"users/{user_id}/playlists", params=params
        ).json()

    def get_my_saved_shows(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        `Shows > Get User's Saved Shows <https://developer.spotify.com
        /documentation/web-api/reference/get-users-saved-shows>`_: Get
        the shows saved in the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

        Parameters
        ----------
        limit : int; keyword-only; optional
            Maximum number of shows to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first show to return. Use with `limit` to get
            the next batch of shows.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        shows : dict[str, Any]
            Page of Spotify content metadata for the user's saved shows.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "added_at": <str>,
                        "show": {
                          "available_markets": <list[str]>,
                          "copyrights": [
                            {
                              "text": <str>,
                              "type": <str>
                            }
                          ],
                          "description": <str>,
                          "explicit": <bool>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "html_description": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "height": <int>,
                              "url": <str>,
                              "width": <int>
                            }
                          ],
                          "is_externally_hosted": <bool>,
                          "languages": <list[str]>,
                          "media_type": <str>,
                          "name": <str>,
                          "publisher": <str>,
                          "total_episodes": <int>,
                          "type": "show",
                          "uri": <str>
                        }
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        self._client._require_scopes(
            "shows.get_my_saved_shows", "user-library-read"
        )
        return self._get_my_saved_entities("shows", limit=limit, offset=offset)

    def save_shows(self, show_ids: str | list[str], /) -> None:
        """
        `Shows > Save Shows for Current User
        <https://developer.spotify.com/documentation/web-api/reference
        /save-shows-user>`_: Save one or more shows to the current
        user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify` scope
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        show_ids : str or list[str]; positional-only
            Spotify IDs of the shows. A maximum of 50 IDs can be sent in
            a request.

            **Examples**:

            .. container::

               * :code:`"5CfCWKI5pZ28U0uOzXkDHe"`
               * :code:`"5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ"`
               * :code:`[5CfCWKI5pZ28U0uOzXkDHe",
                 "5as3aKmN2k11yfDDDSrvaZ"]`
        """
        self._client._require_scopes("shows.save_shows", "user-library-modify")
        self._manage_saved_entities("PUT", "shows", show_ids)

    def remove_saved_shows(self, show_ids: str | list[str], /) -> None:
        """
        `Shows > Remove User's Saved Shows
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-shows-user>`_: Remove one or more shows from the current
        user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify` scope
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        show_ids : str or list[str]; positional-only
            Spotify IDs of the shows. A maximum of 50 IDs can be sent in
            a request.

            **Examples**:

            .. container::

               * :code:`"5CfCWKI5pZ28U0uOzXkDHe"`
               * :code:`"5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ"`
               * :code:`[5CfCWKI5pZ28U0uOzXkDHe",
                 "5as3aKmN2k11yfDDDSrvaZ"]`
        """
        self._client._require_scopes(
            "shows.remove_saved_shows", "user-library-modify"
        )
        self._manage_saved_entities("DELETE", "shows", show_ids)

    def are_shows_saved(self, show_ids: str | list[str], /) -> list[bool]:
        """
        `Shows > Check User's Saved Shows
        <https://developer.spotify.com/documentation/web-api/reference
        /check-users-saved-shows>`_: Check whether one or more shows are
        saved in the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

        Parameters
        ----------
        show_ids : str or list[str]; positional-only
            Spotify IDs of the shows. A maximum of 50 IDs can be sent in
            a request.

            **Examples**:

            .. container::

               * :code:`"5CfCWKI5pZ28U0uOzXkDHe"`
               * :code:`"5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ"`
               * :code:`[5CfCWKI5pZ28U0uOzXkDHe",
                 "5as3aKmN2k11yfDDDSrvaZ"]`

        Returns
        -------
        saved : list[bool]
            Whether the current user has the specified shows saved in
            their library.
        """
        self._client._require_scopes(
            "shows.are_shows_saved", "user-library-read"
        )
        return self._are_entities_saved("shows", show_ids)

    def get_my_saved_tracks(
        self,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get User's Saved Tracks <https://developer.spotify.com
        /documentation/web-api/reference/get-users-saved-tracks>`_: Get
        the tracks saved in the current user's library.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If provided, only content
            available in that market is returned. When a user access
            token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither a country code is provided nor a country can
               be determined from the user account, the content is
               considered unavailable for the client.

            **Example**: :code:`"ES"`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of Spotify content metadata for the user's saved
            tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "added_at": <str>,
                        "track": {
                          "album": {
                            "album_type": <str>,
                            "artists": [
                              {
                                "external_urls": {
                                  "spotify": <str>
                                },
                                "href": <str>,
                                "id": <str>,
                                "name": <str>,
                                "type": "artist",
                                "uri": <str>
                              }
                            ],
                            "available_markets": <list[str]>,
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "images": [
                              {
                                "height": <int>,
                                "url": <str>,
                                "width": <int>
                              }
                            ],
                            "name": <str>,
                            "release_date": <str>,
                            "release_date_precision": <str>,
                            "restrictions": {
                              "reason": <str>
                            },
                            "total_tracks": <int>,
                            "type": "album",
                            "uri": <str>
                          },
                          "artists": [
                            {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "href": <str>,
                              "id": <str>,
                              "name": <str>,
                              "type": "artist",
                              "uri": <str>
                            }
                          ],
                          "available_markets": <list[str]>,
                          "disc_number": <int>,
                          "duration_ms": <int>,
                          "explicit": <bool>,
                          "external_ids": {
                            "ean": <str>,
                            "isrc": <str>,
                            "upc": <str>
                          },
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "is_local": <bool>,
                          "is_playable": <bool>,
                          "linked_from": <dict[str, Any]>,
                          "name": <str>,
                          "popularity": <int>,
                          "preview_url": <str>,
                          "restrictions": {
                            "reason": <str>
                          },
                          "track_number": <int>,
                          "type": "track",
                          "uri": <str>
                        }
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        self._client._require_scopes(
            "tracks.get_my_saved_tracks", "user-library-read"
        )
        return self._get_my_saved_entities(
            "tracks", country_code=country_code, limit=limit, offset=offset
        )

    def save_tracks(
        self,
        track_ids: str
        | tuple[str, str | datetime]
        | dict[str, str | datetime]
        | list[str | tuple[str, str | datetime] | dict[str, str | datetime]],
        /,
    ) -> None:
        """
        `Tracks > Save Tracks for Current User
        <https://developer.spotify.com/documentation/web-api/reference
        /save-tracks-user>`_: Save one or more tracks to the current
        user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify` scope
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        track_ids : str, tuple[str, str | datetime], \
        dict[str, str | datetime], or \
        list[str | tuple[str, str | datetime] | dict[str, str | datetime]]; \
        positional-only
            Spotify IDs of the tracks, optionally accompanied by
            timestamps to maintain a chronological order in the user's 
            library. A maximum of 50 IDs can be sent in one request.

            **Examples**:

            .. container::

               * :code:`"4iV5W9uYEdYUVa79Axb7Rh"`
               * :code:`("4iV5W9uYEdYUVa79Axb7Rh", "2010-01-01T00:00:00Z")`
               * :code:`{"id": "4iV5W9uYEdYUVa79Axb7Rh",
                 "added_at": "2010-01-01T00:00:00Z"}`
               * .. code::

                    [
                        "4iV5W9uYEdYUVa79Axb7Rh",
                        ("11dFghVXANMlKmJXsNCbNl", "2017-05-26T00:00:00Z"),
                        {
                            "id": "7ouMYWpwJ422jRcDASZB7P", 
                            "added_at": "2006-06-28T00:00:00Z"
                        }
                    ]
        """
        self._client._require_scopes(
            "tracks.save_tracks", "user-library-modify"
        )
        if isinstance(track_ids, str):
            track_ids = [
                {
                    "id": track_ids,
                    "added_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            ]
        elif isinstance(track_ids, dict):
            track_ids = [track_ids]
        elif (
            isinstance(track_ids, tuple)
            and len(track_ids) == 2
            and (
                timestamp_is_str := isinstance(track_ids[1], str)
                and len(track_ids[1]) == 20
                or isinstance(track_ids[1], datetime)
            )
        ):
            track_ids = [
                {
                    "id": track_ids[0],
                    "added_at": track_ids[1]
                    if timestamp_is_str
                    else track_ids[1].strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            ]
        else:  # list
            for idx, track in enumerate(track_ids):
                if isinstance(track, str):
                    track_ids[idx] = {
                        "id": track,
                        "added_at": datetime.now().strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                    }
                elif isinstance(track, tuple):
                    track_ids[idx] = {
                        "id": track[0],
                        "added_at": timestamp
                        if isinstance(timestamp := track[1], str)
                        else timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
        self._client._request(
            "PUT", "me/tracks", json={"timestamped_ids": track_ids}
        )

    def remove_saved_tracks(self, track_ids: str | list[str], /) -> None:
        """
        `Tracks > Remove User's Saved Tracks
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-tracks-user>`_: Remove one or more tracks from the
        current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify` scope
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        track_ids : str or list[str]; positional-only
            Spotify IDs of the tracks. A maximum of 50 IDs can be sent
            in a request.

            **Examples**:

            .. container::

               * :code:`"7ouMYWpwJ422jRcDASZB7P"`
               * :code:`"7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ"`
               * :code:`["7ouMYWpwJ422jRcDASZB7P",
                 "4VqPOruhp5EdPBeR92t6lQ"]`
        """
        self._client._require_scopes(
            "tracks.remove_saved_tracks", "user-library-modify"
        )
        self._manage_saved_entities("DELETE", "tracks", track_ids)

    def are_tracks_saved(self, track_ids: str | list[str], /) -> list[bool]:
        """
        `Tracks > Check User's Saved Tracks
        <https://developer.spotify.com/documentation/web-api/reference
        /check-users-saved-tracks>`_: Check whether one or more tracks
        are saved in the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

        Parameters
        ----------
        track_ids : str or list[str]; positional-only
            Spotify IDs of the tracks. A maximum of 50 IDs can be sent
            in a request.

            **Examples**:

            .. container::

               * :code:`"7ouMYWpwJ422jRcDASZB7P"`
               * :code:`"7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ"`
               * :code:`["7ouMYWpwJ422jRcDASZB7P",
                 "4VqPOruhp5EdPBeR92t6lQ"]`

        Returns
        -------
        saved : list[bool]
            Whether the current user has the specified tracks saved in
            their library.
        """
        self._client._require_scopes(
            "tracks.are_tracks_saved", "user-library-read"
        )
        return self._are_entities_saved("tracks", track_ids)

    def _manage_followed_people(
        self, method: str, resource_type: str, resource_ids: str | list[str], /
    ) -> None:
        """
        Follow or unfollow one or more artists or Spotify users.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-modify` scope
                 Manage your saved content. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-follow-modify>`__

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

            **Valid values**: :code:`"PUT"`, :code:`"DELETE"`.

        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"artists"`, :code:`"users"`.

        resource_ids : str or list[str]; positional-only
            Spotify IDs of the artists or users. A maximum of 50 IDs can
            be sent in a request.
        """
        self._client._request(
            method,
            "me/following",
            params={
                "type": resource_type[:-1],
                "ids": self._client._prepare_spotify_ids(
                    resource_ids,
                    limit=50,
                    enforce_length=resource_type == "artists",
                )[0],
            },
        )

    def _is_following_people(
        self, resource_type: str, resource_ids: str | list[str], /
    ) -> list[bool]:
        """
        Check whether the current user is following one or more artists
        or Spotify users.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-read` scope
                 Access your followers and who you are following. `Learn
                 more. <https://developer.spotify.com/documentation
                 /web-api/concepts/scopes#user-follow-read>`__

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"artists"`, :code:`"users"`.

        resource_ids : str or list[str]; positional-only
            Spotify IDs of the artists or users. A maximum of 50 IDs can
            be sent in a request.

        Returns
        -------
        following : list[bool]
            Whether the current user follows the specified artists or
            users.

            **Sample response**: :code:`[False, True]`.
        """
        return self._client._request(
            "GET",
            "me/following/contains",
            params={
                "type": resource_type[:-1],
                "ids": self._client._prepare_spotify_ids(
                    resource_ids,
                    limit=50,
                    enforce_length=resource_type == "artists",
                )[0],
            },
        ).json()

    def _get_my_saved_entities(
        self,
        resource_type: str,
        /,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Spotify catalog information for items of a resource type
        saved in the current user's library.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"audiobooks"`,
            :code:`"episodes"`, :code:`"shows"`, :code:`"tracks"`.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If provided, only content
            available in that market is returned. When a user access
            token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither the market nor the user's country are
               provided, the content is considered unavailable for the
               client.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        items : dict[str, Any]
            Page of Spotify content metadata for the user's saved
            items.
        """
        params = {}
        if country_code is not None:
            self._client._validate_market(country_code)
            params["market"] = country_code
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"me/{resource_type}", params=params
        ).json()

    def _manage_saved_entities(
        self,
        method: str,
        resource_type: str,
        resource_ids: str | list[str],
        /,
        *,
        limit: int = 50,
    ) -> None:
        """
        Save or remove one or more items of a resource type to or from
        the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify` scope
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

            **Valid values**: :code:`"PUT"`, :code:`"DELETE"`.

        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"audiobooks"`,
            :code:`"episodes"`, :code:`"shows"`.

        resource_ids : str or list[str]; positional-only
            Spotify IDs of the items, provided as either a
            comma-separated string or a list of strings.

        limit : int; keyword-only; default: :code:`50`
            Maximum number of Spotify IDs that can be sent in the
            request.
        """
        self._client._request(
            method,
            f"me/{resource_type}",
            params={
                "ids": self._client._prepare_spotify_ids(
                    resource_ids, limit=limit
                )[0]
            },
        )

    def _are_entities_saved(
        self,
        resource_type: str,
        resource_ids: str | list[str],
        /,
        *,
        limit: int = 50,
    ) -> list[bool]:
        """
        Check whether one or more items of a resource type are saved in
        the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"audiobooks"`,
            :code:`"episodes"`, :code:`"shows"`, :code:`"tracks"`.

        resource_ids : str or list[str]; positional-only
            Spotify IDs of the items, provided as either a
            comma-separated string or a list of strings.

        limit : int; keyword-only; default: :code:`50`
            Maximum number of Spotify IDs that can be sent in the
            request.

        Returns
        -------
        saved : list[bool]
            Whether the current user has each of the specified items
            saved in their library.
        """
        return self._client._request(
            "GET",
            f"me/{resource_type}/contains",
            params={
                "ids": self._client._prepare_spotify_ids(
                    resource_ids, limit=limit
                )[0]
            },
        ).json()
