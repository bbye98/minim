from collections.abc import Collection
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPIArtistEndpoints:
    """
    Spotify Web API artist endpoints.

    .. important::

       This class is managed by :class:`minim.api.spotify.WebAPI` and
       should not be instantiated directly.
    """

    _GROUPS = {"album", "single", "appears_on", "compilation"}

    def __init__(self, client: "WebAPI", /) -> None:
        """
        Parameters
        ----------
        client : minim.api.spotify.WebAPI
            Minim's Spotify Web API client.
        """
        self._client = client

    def get_artists(
        self, artist_ids: str | Collection[str], /
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist <https://developer.spotify.com
        /documentation/web-api/reference/get-an-artist>`_: Get
        Spotify catalog information for a single artist․
        `Artists > Get Several Artists <https://developer.spotify.com
        /documentation/web-api/reference/get-multiple-artists>`_: Get
        Spotify catalog information for multiple artists.

        Parameters
        ----------
        artist_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the artists. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"0TnOYISbd1XYRBk9myaseg"`,
            :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E,1vCWHaC5f2uS3yhpwWbIA6"`,
            :code:`["2CIMQHirSU0MQqyYHq0eOx", "57dN52uHvrHOxijzpIgu3E",
            "1vCWHaC5f2uS3yhpwWbIA6"]`.

        Returns
        -------
        artists : dict[str, Any]
            Spotify content metadata for the artists.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single artist

                  .. code::

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
                       "popularity": <int>,
                       "type": "artist",
                       "uri": <str>
                     }

               .. tab:: Multiple artists

                  .. code::

                     {
                       "artists": [
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
                           "popularity": <int>,
                           "type": "artist",
                           "uri": <str>
                         }
                       ]
                     }
        """
        string = isinstance(artist_ids, str)
        artist_ids, n_ids = self._client._prepare_spotify_ids(
            artist_ids, limit=50
        )
        if string and n_ids == 1:
            return self._client._request("GET", f"artists/{artist_ids}").json()
        return self._client._request(
            "GET", "artists", params={"ids": artist_ids}
        ).json()

    def get_artist_albums(
        self,
        artist_id: str,
        /,
        *,
        include_groups: str | list[str] | None = None,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist's Albums <https://developer.spotify.com
        /documentation/web-api/reference/get-an-artists-albums>`_: Get
        Spotify catalog information about an artist's albums.

        Parameters
        ----------
        artist_id : str, positional-only
            Spotify ID of the artist.

            **Example**: :code:`"0TnOYISbd1XYRBk9myaseg"`.

        include_groups : str or list[str], optional
            (Comma-separated) list of album types to return. If not
            specified, all album types will be returned.

            **Valid values**: :code:`"album"`, :code:`"single"`,
            :code:`"appears_on"`, :code:`"compilation"`.

            **Examples**: :code:`"album"`, :code:`"album,single"`,
            :code:`["single", "appears_on"]`.

        market : str, keyword-only, optional
            ISO 3166-1 alpha-2 country code. If specified, only content
            available in that market is returned. When a valid user
            access token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither the market nor the user's country are
               provided, the content is considered unavailable for the
               client.

            **Example**: :code:`"ES"`.

        limit : int, keyword-only, optional
            Maximum number of albums to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first album to return. Use with `limit` to get
            the next set of albums.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        albums : dict[str, Any]
            Spotify content metadata for the artist's albums.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "album_group": <str>,
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
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        self._client._validate_spotify_id(artist_id)
        params = {}
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        if include_groups is not None:
            include_groups = self._prepare_groups(include_groups)
            params["include_groups"] = include_groups
        return self._client._request(
            "GET", f"artists/{artist_id}/albums", params=params
        ).json()

    def get_artist_top_tracks(
        self, artist_id: str, /, *, market: str
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist's Top Tracks
        <https://developer.spotify.com/documentation/web-api/reference
        /get-an-artists-top-tracks>`_: Get Spotify catalog information
        for an artist's top tracks.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
        artist_id : str, positional-only
            Spotify ID of the artist.

            **Example**: :code:`"0TnOYISbd1XYRBk9myaseg"`.

        market : str, keyword-only, optional
            ISO 3166-1 alpha-2 country code. If specified, only content
            available in that market is returned. When a valid user
            access token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither the market nor the user's country are
               provided, the content is considered unavailable for the
               client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        top_tracks : dict[str, Any]
            Spotify content metadata for the artist's top tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "tracks": [
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
                        "linked_from": {},
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
                    ]
                  }
        """
        self._client._validate_spotify_id(artist_id)
        params = {}
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        return self._client._request(
            "GET", f"artists/{artist_id}/top-tracks", params=params
        ).json()

    def get_related_artists(self, artist_id: str, /) -> dict[str, Any]:
        """
        `Artists > Get Artist's Related Artists
        <https://developer.spotify.com/documentation/web-api/reference
        /get-an-artists-related-artists>`_: Get Spotify catalog
        information for artists similar to a given artist based on
        an analysis of the Spotify community's listening history.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Required

              Extended quota mode before November 11, 2024
                  Access the :code:`related-artists` endpoint.

        Parameters
        ----------
        artist_id : str, positional-only
            Spotify ID of the artist.

            **Example**: :code:`"0TnOYISbd1XYRBk9myaseg"`.

        Returns
        -------
        related_artists : dict[str, Any]
            Spotify content metadata for the related artists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "artists": [
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
                        "popularity": <int>,
                        "type": "artist",
                        "uri": <str>
                      }
                    ]
                  }
        """
        self._client._validate_spotify_id(artist_id)
        return self._client._request(
            "GET", f"artists/{artist_id}/related-artists"
        ).json()

    def get_my_top_artists(
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

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first item to return. Use with `limit` to get
            the next set of items.

            **Minimum value**: :code:`0`.

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
        return self._client.users.get_my_top_artists(
            time_range=time_range, limit=limit, offset=offset
        )

    def get_my_followed_artists(
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

            **Valid range**: :code:`1` to :code:`50`.

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
        return self._client.users.get_my_followed_artists(
            after=after, limit=limit
        )

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
        self._client.users.follow_artists(artist_ids)

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
        self._client.users.unfollow_artists(artist_ids)

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
        return self._client.users.is_following_artists(artist_ids)

    def _prepare_groups(self, groups: str | Collection[str], /) -> str:
        """
        Stringify a list of album types into a comma-delimited string.

        Parameters
        ----------
        groups : str or Collection[str], positional-only
            (Comma-delimited) list of album types.

        Returns
        -------
        groups : str
            Comma-delimited string containing album types.
        """
        if isinstance(groups, str):
            split_groups = groups.split(",")
            for group in split_groups:
                self._validate_group(group)
            return ",".join(sorted(split_groups))

        groups = set(groups)
        for group in groups:
            self._validate_groups(group)
        return ",".join(sorted(groups))

    def _validate_group(self, group: str, /) -> None:
        """
        Validate album type.

        Parameters
        ----------
        group : str, positional-only
            Album type.
        """
        if group not in self._GROUPS:
            raise ValueError(
                f"{group!r} is not a valid album type. "
                "Valid values: '" + ", ".join(self._GROUPS) + "'."
            )
