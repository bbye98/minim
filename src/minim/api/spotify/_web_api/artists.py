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
        artist_ids, n_ids = self._client._normalize_spotify_ids(
            artist_ids, limit=50
        )
        if n_ids > 1:
            return self._client._request(
                "GET", "artists", params={"ids": artist_ids}
            ).json()
        return self._client._request("GET", f"artists/{artist_ids}").json()

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

            **Valid values**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first album to return. Use with `limit` to get
            the next set of albums.

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
        return self._client._request(
            "GET",
            f"artists/{artist_id}/albums",
            params={
                "include_groups": include_groups,
                "market": market,
                "limit": limit,
                "offset": offset,
            },
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
        return self._client._request(
            "GET", f"artists/{artist_id}/top-tracks", params={"market": market}
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
        return self._client._request(
            "GET", f"artists/{artist_id}/related-artists"
        ).json()
