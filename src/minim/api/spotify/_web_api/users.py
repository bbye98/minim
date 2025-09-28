from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPIUserEndpoints:
    """
    Spotify Web API user endpoints.

    .. note::

       This class is managed by :class:`minim.api.spotify.WebAPI` and
       should not be instantiated directly.
    """

    def __init__(self, client: "WebAPI", /) -> None:
        """
        Parameters
        ----------
        client : minim.api.spotify.WebAPI
            Minim's Spotify Web API client.
        """
        self._client = client

    def get_profile(self, user_id: str | None = None, /) -> dict[str, Any]:
        """
        `Users > Get Current User's Profile
        <https://developer.spotify.com/documentation/web-api/reference
        /get-current-users-profile>`_: Get detailed profile information
        about the current user (including username)․
        `Users > Get User's Profile <https://developer.spotify.com
        /documentation/web-api/reference/get-users-profile>`_: Get
        public profile information about a Spotify user.

        .. admonition:: Authorization scopes
           :class: authorization-scope

           .. tab:: Optional

              :code:`user-read-private`
                 Access your subscription details.
              :code:`user-read-email`
                 Get your real email address.

        Parameters
        ----------
        user_id : str, positional-only, optional
            Spotify user ID. If not provided, the current user's
            profile will be returned.

            **Example**: :code:`"smedjan"`.

        Returns
        -------
        profile : dict[str, Any]
            User's profile information.

            .. admonition:: Sample response
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
        self._client._validate_spotify_id(user_id, strict_length=False)
        return self._client._request(
            "GET", f"users/{user_id}" if user_id else "me"
        ).json()

    def get_top_artists(
        self,
        *,
        time_range: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Users > Get User's Top Artists
        <https://developer.spotify.com/documentation/web-api/reference
        /get-users-top-artists-and-tracks>`_: Get the current user's top
        artists based on calculated affinity.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-top-read`
                 Read your top artists and contents.

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
        time_range : str, keyword-only, optional
            Time frame over which the affinities are computed.

            .. container::

               **Valid values**:

               * :code:`"long_term"`: Approximately one year of data,
                 including all new data as it becomes available.
               * :code:`"medium_term"`: Approximately the last six
                 months of data.
               * :code:`"short_term"`: Approximately the last four weeks
                 of data.

            **Default**: :code:`"medium_term"`.

        limit : int, keyword-only, optional
            Maximum number of items to return.

            **Valid values**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first item to return. Use with `limit` to get
            the next set of items.

            **Default**: :code:`0`.

        Returns
        -------
        top_artists : dict[str, Any]
            Spotify content metadata for the current user's top artists.

            .. admonition:: Sample response
               :class: dropdown

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
        self._client._require_scopes("get_top_artists", "user-top-read")
        return self._client._request(
            "GET",
            "me/top/artists",
            params={"time_range": time_range, "limit": limit, "offset": offset},
        ).json()

    def get_top_tracks(
        self,
        *,
        time_range: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Users > Get User's Top Tracks
        <https://developer.spotify.com/documentation/web-api/reference
        /get-users-top-artists-and-tracks>`_: Get the current user's top
        tracks based on calculated affinity.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-top-read`
                 Read your top artists and contents.

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
        time_range : str, keyword-only, optional
            Time frame over which the affinities are computed.

            .. container::

               **Valid values**:

               * :code:`"long_term"`: Approximately one year of data,
                 including all new data as it becomes available.
               * :code:`"medium_term"`: Approximately the last six
                 months of data.
               * :code:`"short_term"`: Approximately the last four weeks
                 of data.

            **Default**: :code:`"medium_term"`.

        limit : int, keyword-only, optional
            Maximum number of items to return.

            **Valid values**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first item to return. Use with `limit` to get
            the next set of items.

            **Default**: :code:`0`.

        Returns
        -------
        top_tracks : dict[str, Any]
            Spotify content metadata for the current user's top tracks.

            .. admonition:: Sample response
               :class: dropdown

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
        self._client._require_scopes("get_top_tracks", "user-top-read")
        return self._client._request(
            "GET",
            "me/top/tracks",
            params={"time_range": time_range, "limit": limit, "offset": offset},
        ).json()

    def follow_playlist(
        self, playlist_id: str, /, *, public: bool | None = None
    ) -> None:
        """
        `Users > Follow Playlist <https://developer.spotify.com
        /documentation/web-api/reference/follow-playlist>`_: Add the
        current user as a follower of a playlist.

        .. admonition:: Authorization scopes
           :class: authorization-scope

           .. tab:: Required

              :code:`playlist-modify-public`
                 Manage your public playlists.
              :code:`playlist-modify-private`
                 Manage your private playlists.

        Parameters
        ----------
        playlist_id : str, positional-only
            Spotify ID of the playlist.

        public : bool, keyword-only, optional
            Specifies whether the playlist will be included in the
            current user's public playlists.

            **Default**: :code:`True`.
        """
        self._client._require_scopes(
            "follow_playlist",
            f"playlist-modify-{'public' if public else 'private'}",
        )
        self._client._validate_spotify_id(playlist_id)
        self._client._request("PUT", f"playlists/{playlist_id}/followers")

    def unfollow_playlist(self, playlist_id: str, /) -> None:
        """
        `Users > Unfollow Playlist <https://developer.spotify.com
        /documentation/web-api/reference/unfollow-playlist>`_: Remove
        the current user as a follower of a playlist.

        .. admonition:: Authorization scopes
           :class: authorization-scope

           .. tab:: Required

              :code:`playlist-modify-public`
                 Manage your public playlists.
              :code:`playlist-modify-private`
                 Manage your private playlists.

        Parameters
        ----------
        playlist_id : str, positional-only
            Spotify ID of the playlist.
        """
        self._client._require_scopes(
            "unfollow_playlist",
            ["playlist-modify-public", "playlist-modify-private"],
        )
        self._client._validate_spotify_id(playlist_id)
        self._client._request("DELETE", f"playlists/{playlist_id}/followers")

    def get_followed_artists(
        self, *, after: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """
        `Users > Get Followed Artists <https://developer.spotify.com
        /documentation/web-api/reference/get-followed>`_: Get the
        current user's followed artists.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-read`
                 Access your followers and who you are following.

        Parameters
        ----------
        after : str, keyword-only, optional
            Spotify ID of the last artist retrieved in the previous
            request.

            **Example**: :code:`"0I2XqVXqHScXjHhk6AYYRe"`.

        limit : int, keyword-only, optional
            Maximum number of artists to return.

            **Valid values**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        Returns
        -------
        followed_artists : dict[str, Any]
            Spotify content metadata for the current user's followed
            artists.

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
        self._client._require_scopes("get_followed_artists", "user-follow-read")
        return self._client._request(
            "GET",
            "me/following",
            params={"type": "artist", "after": after, "limit": limit},
        ).json()

    def follow_artists(self, artist_ids: str | list[str], /) -> None:
        """
        `Users > Follow Artists <https://developer.spotify.com
        /documentation/web-api/reference/follow-artists-users>`_: Add
        the current user as a follower of one or more artists.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-modify`
                 Manage your saved content.

        Parameters
        ----------
        artist_ids : str or list[str], positional-only
            (Comma-separated) list of Spotify IDs for the artists. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"2CIMQHirSU0MQqyYHq0eOx"`,
            :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6"`,
            :code:`["2CIMQHirSU0MQqyYHq0eOx",
            "57dN52uHvrHOxijzpIgu3E", "1vCWHaC5f2uS3yhpwWbIA6"]`.
        """
        self._client._require_scopes("follow_artists", "user-follow-modify")
        self._client._request(
            "PUT",
            "me/following",
            params={
                "type": "artist",
                "ids": self._client._normalize_spotify_ids(
                    artist_ids, limit=50
                )[0],
            },
        )

    def follow_users(self, user_ids: str | list[str], /) -> None:
        """
        `Users > Follow Users <https://developer.spotify.com
        /documentation/web-api/reference/follow-artists-users>`_: Add
        the current user as a follower of one or more Spotify users.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-modify`
                 Manage your saved content.

        Parameters
        ----------
        user_ids : str or list[str], positional-only
            (Comma-separated) list of Spotify user IDs. A maximum of 50
            IDs can be sent in one request.

            **Examples**: :code:`"2CIMQHirSU0MQqyYHq0eOx"`,
            :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6"`,
            :code:`["2CIMQHirSU0MQqyYHq0eOx",
            "57dN52uHvrHOxijzpIgu3E", "1vCWHaC5f2uS3yhpwWbIA6"]`.
        """
        self._client._require_scopes("follow_users", "user-follow-modify")
        self._client._request(
            "PUT",
            "me/following",
            params={
                "type": "user",
                "ids": self._client._normalize_spotify_ids(
                    user_ids, limit=50, strict_length=False
                )[0],
            },
        )

    def unfollow_artists(self, artist_ids: str | list[str], /) -> None:
        """
        `Users > Unfollow Artists <https://developer.spotify.com
        /documentation/web-api/reference/unfollow-artists-users>`_:
        Remove the current user as a follower of one or more artists.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-modify`
                 Manage your saved content.

        Parameters
        ----------
        artist_ids : str or list[str], positional-only
            (Comma-separated) list of Spotify IDs for the artists. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"2CIMQHirSU0MQqyYHq0eOx"`,
            :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6"`,
            :code:`["2CIMQHirSU0MQqyYHq0eOx",
            "57dN52uHvrHOxijzpIgu3E", "1vCWHaC5f2uS3yhpwWbIA6"]`.
        """
        self._client._require_scopes("unfollow_artists", "user-follow-modify")
        self._client._request(
            "DELETE",
            "me/following",
            params={
                "type": "artist",
                "ids": self._client._normalize_spotify_ids(
                    artist_ids, limit=50
                )[0],
            },
        )

    def unfollow_users(self, user_ids: str | list[str], /) -> None:
        """
        `Users > Unfollow Users <https://developer.spotify.com
        /documentation/web-api/reference/unfollow-artists-users>`_:
        Remove the current user as a follower of one or more Spotify users.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-modify`
                 Manage your saved content.

        Parameters
        ----------
        user_ids : str or list[str], positional-only
            (Comma-separated) list of Spotify user IDs. A maximum of 50
            IDs can be sent in one request.

            **Examples**: :code:`"2CIMQHirSU0MQqyYHq0eOx"`,
            :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6"`,
            :code:`["2CIMQHirSU0MQqyYHq0eOx",
            "57dN52uHvrHOxijzpIgu3E", "1vCWHaC5f2uS3yhpwWbIA6"]`.
        """
        self._client._require_scopes("unfollow_users", "user-follow-modify")
        self._client._request(
            "DELETE",
            "me/following",
            params={
                "type": "user",
                "ids": self._client._normalize_spotify_ids(
                    user_ids, limit=50, strict_length=False
                )[0],
            },
        )

    def is_following_artists(
        self, artist_ids: str | list[str], /
    ) -> list[bool]:
        """
        `Users > Check If User Follows Artists
        <https://developer.spotify.com/documentation/web-api/reference
        /check-current-user-follows>`_: Check whether the current user
        is following one or more artists.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-read`
                 Access your followers and who you are following.

        Parameters
        ----------
        artist_ids : str or list[str], positional-only
            (Comma-separated) list of Spotify IDs for the artists. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"2CIMQHirSU0MQqyYHq0eOx"`,
            :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6"`,
            :code:`["2CIMQHirSU0MQqyYHq0eOx",
            "57dN52uHvrHOxijzpIgu3E", "1vCWHaC5f2uS3yhpwWbIA6"]`.

        Returns
        -------
        is_following_artists : list[bool]
            Whether the current user follows each specified artist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [False, True]
        """
        self._client._require_scopes("is_following_artists", "user-follow-read")
        return self._client._request(
            "GET",
            "me/following/contains",
            params={
                "type": "artist",
                "ids": self._client._normalize_spotify_ids(
                    artist_ids, limit=50
                )[0],
            },
        ).json()

    def is_following_users(self, user_ids: str | list[str], /) -> list[bool]:
        """
        `Users > Check If User Follows Users
        <https://developer.spotify.com/documentation/web-api/reference
        /check-current-user-follows>`_: Check whether the current user
        is following one or more Spotify users.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-follow-read`
                 Access your followers and who you are following.

        Parameters
        ----------
        user_ids : str or list[str], positional-only
            (Comma-separated) list of Spotify user IDs. A maximum of 50
            IDs can be sent in one request.

            **Examples**: :code:`"2CIMQHirSU0MQqyYHq0eOx"`,
            :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6"`,
            :code:`["2CIMQHirSU0MQqyYHq0eOx",
            "57dN52uHvrHOxijzpIgu3E", "1vCWHaC5f2uS3yhpwWbIA6"]`.

        Returns
        -------
        is_following_users : list[bool]
            Whether the current user follows each specified user.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [False, True]
        """
        self._client._require_scopes("is_following_users", "user-follow-read")
        return self._client._request(
            "GET",
            "me/following/contains",
            params={
                "type": "user",
                "ids": self._client._normalize_spotify_ids(
                    user_ids, limit=50, strict_length=False
                )[0],
            },
        ).json()

    def is_following_playlist(self, playlist_id: str, /) -> bool:
        """
        `Users > Check if Current User Follows Playlist
        <https://developer.spotify.com/documentation/web-api/reference
        /check-if-user-follows-playlist>`_: Check whether the current
        user is following a playlist.

        Parameters
        ----------
        playlist_id : str, positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        Returns
        -------
        is_following_playlist : bool
            Whether the current user follows the specified playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  True
        """
        self._client._validate_spotify_id(playlist_id)
        return self._client._request(
            "GET", f"playlists/{playlist_id}/followers/contains"
        ).json()[0]
