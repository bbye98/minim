from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import SpotifyResourceAPI
from .users import UsersAPI


class ArtistsAPI(SpotifyResourceAPI):
    """
    Artists API endpoints for the Spotify Web API.

    .. important::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPI`
       and should not be instantiated directly.
    """

    _ALBUM_TYPES = {"album", "single", "appears_on", "compilation"}

    @TTLCache.cached_method(ttl="popularity")
    def get_artists(self, artist_ids: str | list[str], /) -> dict[str, Any]:
        """
        `Artists > Get Artist <https://developer.spotify.com
        /documentation/web-api/reference/get-an-artist>`_: Get
        Spotify catalog information for a single artist․
        `Artists > Get Several Artists <https://developer.spotify.com
        /documentation/web-api/reference/get-multiple-artists>`_: Get
        Spotify catalog information for multiple artists.

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
        return self._get_resources("artists", artist_ids)

    @TTLCache.cached_method(ttl="daily")
    def get_artist_albums(
        self,
        artist_id: str,
        /,
        *,
        album_types: str | list[str] | None = None,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist's Albums <https://developer.spotify.com
        /documentation/web-api/reference/get-an-artists-albums>`_: Get
        Spotify catalog information for an artist's albums.

        Parameters
        ----------
        artist_id : str; positional-only
            Spotify ID of the artist.

            **Example**: :code:`"0TnOYISbd1XYRBk9myaseg"`.

        album_types : str or list[str]; optional
            Album types to return. If not provided, all album types
            will be returned.

            **Valid values**: :code:`"album"`, :code:`"single"`,
            :code:`"appears_on"`, :code:`"compilation"`.

            **Examples**: :code:`"album"`, :code:`"album,single"`,
            :code:`["single", "appears_on"]`.

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
            Page of Spotify content metadata for the artist's albums.

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
        params = {}
        if album_types is not None:
            album_types = self._prepare_types(
                album_types,
                allowed_types=self._ALBUM_TYPES,
                type_prefix="album",
            )
            params["include_groups"] = album_types
        return self._get_resource_items(
            "artists",
            artist_id,
            "albums",
            country_code=country_code,
            limit=limit,
            offset=offset,
            params=params,
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_artist_top_tracks(
        self, artist_id: str, /, *, country_code: str
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
        artist_id : str; positional-only
            Spotify ID of the artist.

            **Example**: :code:`"0TnOYISbd1XYRBk9myaseg"`.

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
        return self._get_resource_items(
            "artists", artist_id, "top-tracks", country_code=country_code
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_similar_artists(self, artist_id: str, /) -> dict[str, Any]:
        """
        `Artists > Get Artist's Related Artists
        <https://developer.spotify.com/documentation/web-api/reference
        /get-an-artists-related-artists>`_: Get Spotify catalog
        information for artists similar to a given artist.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Required

              Extended quota mode before November 27, 2024
                  Access the :code:`GET /artists/{id}/related-artists`
                  endpoint. `Learn more. <https://developer.spotify.com
                  /blog/2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        artist_id : str; positional-only
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
        return self._get_resource_items(
            "artists", artist_id, "related-artists"
        )

    @TTLCache.cached_method(ttl="hourly")
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
        time_range : str; keyword-only; optional
            Time frame over which the current user's listening history
            is analyzed to determine top artists.

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
            Maximum number of artists to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first artist to return. Use with `limit` to get
            the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        artists : dict[str, Any]
            Page of Spotify content metadata for the current user's top
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
        return self._client.users.get_my_top_items(
            "artists", time_range=time_range, limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.get_my_followed_artists)
    def get_my_followed_artists(
        self, *, cursor: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        return self._client.users.get_my_followed_artists(
            cursor=cursor, limit=limit
        )

    @_copy_docstring(UsersAPI.follow_artists)
    def follow_artists(self, artist_ids: str | list[str], /) -> None:
        self._client.users.follow_artists(artist_ids)

    @_copy_docstring(UsersAPI.unfollow_artists)
    def unfollow_artists(self, artist_ids: str | list[str], /) -> None:
        self._client.users.unfollow_artists(artist_ids)

    @_copy_docstring(UsersAPI.is_following_artists)
    def is_following_artists(
        self, artist_ids: str | list[str], /
    ) -> list[bool]:
        return self._client.users.is_following_artists(artist_ids)
