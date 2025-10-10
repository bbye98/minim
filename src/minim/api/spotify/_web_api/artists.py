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

    _ALBUM_TYPES = {"album", "single", "appears_on", "compilation"}

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
            Spotify IDs of the artists, provided as either a
            comma-separated string or a collection of strings. A
            maximum of 50 IDs can be sent in one request.

            .. container::

               **Examples**:

               * :code:`"2CIMQHirSU0MQqyYHq0eOx"`
               * :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E"`
               * :code:`["2CIMQHirSU0MQqyYHq0eOx", "57dN52uHvrHOxijzpIgu3E"]`

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
        is_string = isinstance(artist_ids, str)
        artist_ids, n_ids = self._client._prepare_spotify_ids(
            artist_ids, limit=50
        )
        if is_string and n_ids == 1:
            return self._client._request("GET", f"artists/{artist_ids}").json()

        return self._client._request(
            "GET", "artists", params={"ids": artist_ids}
        ).json()

    def get_artist_albums(
        self,
        artist_id: str,
        /,
        *,
        include_groups: str | Collection[str] | None = None,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist's Albums <https://developer.spotify.com
        /documentation/web-api/reference/get-an-artists-albums>`_: Get
        Spotify catalog information for an artist's albums.

        Parameters
        ----------
        artist_id : str, positional-only
            Spotify ID of the artist.

            **Example**: :code:`"0TnOYISbd1XYRBk9myaseg"`.

        include_groups : str or Collection[str], optional
            Album types to retrieve, provided as either a
            comma-separated string or a collection of strings. If not
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
            Pages of Spotify content metadata for the artist's albums.

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
            include_groups = self._prepare_album_types(include_groups)
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
           :class: authorization-scope dropdown

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

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
        information for artists similar to a given artist.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Required

              Extended quota mode before November 27, 2024
                  Access the :code:`related-artists` endpoint.
                  `Learn more. <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        artist_id : str, positional-only
            Spotify ID of the artist.

            **Example**: :code:`"0TnOYISbd1XYRBk9myaseg"`.

        Returns
        -------
        artists : dict[str, Any]
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
        /get-users-top-artists-and-tracks>`_: Get Spotify catalog
        information for the current user's top artists.

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
        time_range : str, keyword-only, optional
            Time frame over which the current user's listening history
            is analyzed to determine the top artists.

            .. container::

               **Valid values**:

               * :code:`"long_term"` – Approximately one year of data,
                 including all new data as it becomes available.
               * :code:`"medium_term"` – Approximately the last six
                 months of data.
               * :code:`"short_term"` – Approximately the last four
                 weeks of data.

            **Default**: :code:`"medium_term"`.

        limit : int, keyword-only, optional
            Maximum number of artists to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first artist to return. Use with `limit` to get
            the next set of artists.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        artists : dict[str, Any]
            Pages of Spotify content metadata for the current user's top
            artists.

            .. admonition:: Sample response
               :class: dropdown

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
        """
        self._client._require_scopes("get_top_artists", "user-top-read")
        params = {}
        if time_range:
            self._client.users._validate_time_range(time_range)
            params["time_range"] = time_range
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "me/top/artists", params=params
        ).json()

    def get_my_followed_artists(
        self, *, after: str | None = None, limit: int | None = None
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
        self._client._require_scopes("get_followed_artists", "user-follow-read")
        params = {"type": "artist"}
        if after is not None:
            self._client._validate_spotify_id(after)
            params["after"] = after
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        return self._client._request(
            "GET", "me/following", params=params
        ).json()

    def follow_artists(self, artist_ids: str | Collection[str], /) -> None:
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
        artist_ids : str or Collection[str], positional-only
            Spotify IDs of the artists, provided as either a
            comma-separated string or a collection of strings. A
            maximum of 50 IDs can be sent in one request.

            .. container::

               **Examples**:

               * :code:`"2CIMQHirSU0MQqyYHq0eOx"`
               * :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E"`
               * :code:`["2CIMQHirSU0MQqyYHq0eOx", "57dN52uHvrHOxijzpIgu3E"]`
        """
        self._client._require_scopes("follow_artists", "user-follow-modify")
        self._client._request(
            "PUT",
            "me/following",
            params={
                "type": "artist",
                "ids": self._client._prepare_spotify_ids(artist_ids, limit=50)[
                    0
                ],
            },
        )

    def unfollow_artists(self, artist_ids: str | Collection[str], /) -> None:
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
        artist_ids : str or Collection[str], positional-only
            Spotify IDs of the artists, provided as either a
            comma-separated string or a collection of strings. A
            maximum of 50 IDs can be sent in one request.

            .. container::

               **Examples**:

               * :code:`"2CIMQHirSU0MQqyYHq0eOx"`
               * :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E"`
               * :code:`["2CIMQHirSU0MQqyYHq0eOx", "57dN52uHvrHOxijzpIgu3E"]`
        """
        self._client._require_scopes("unfollow_artists", "user-follow-modify")
        self._client._request(
            "DELETE",
            "me/following",
            params={
                "type": "artist",
                "ids": self._client._prepare_spotify_ids(artist_ids, limit=50)[
                    0
                ],
            },
        )

    def is_following_artists(
        self, artist_ids: str | Collection[str], /
    ) -> list[bool]:
        """
        `Users > Check If User Follows Artists
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
        artist_ids : str or Collection[str], positional-only
            Spotify IDs of the artists, provided as either a
            comma-separated string or a collection of strings. A
            maximum of 50 IDs can be sent in one request.

            .. container::

               **Examples**:

               * :code:`"2CIMQHirSU0MQqyYHq0eOx"`
               * :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E"`
               * :code:`["2CIMQHirSU0MQqyYHq0eOx", "57dN52uHvrHOxijzpIgu3E"]`

        Returns
        -------
        following : list[bool]
            Whether the current user follows the specified artists.

            **Sample response**: :code:`[False, True]`.
        """
        self._client._require_scopes("is_following_artists", "user-follow-read")
        return self._client._request(
            "GET",
            "me/following/contains",
            params={
                "type": "artist",
                "ids": self._client._prepare_spotify_ids(artist_ids, limit=50)[
                    0
                ],
            },
        ).json()

    def _prepare_album_types(
        self, album_types: str | Collection[str], /
    ) -> str:
        """
        Stringify a collection of album types into a comma-separated
        string.

        Parameters
        ----------
        album_types : str or Collection[str], positional-only
            Comma-separated string or collection containing album types.

        Returns
        -------
        album_types : str
            Comma-separated string containing album types.
        """
        if isinstance(album_types, str):
            return self._prepare_album_types(album_types.split(","))

        album_types = set(album_types)
        for album_type in album_types:
            if album_type not in self._ALBUM_TYPES:
                _album_types = ", ".join(self._ALBUM_TYPES)
                raise ValueError(
                    f"Invalid album type {album_type!r}. "
                    f"Valid values: '{_album_types}'."
                )
        return ",".join(sorted(album_types))
