from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import SpotifyResourceAPI
from .users import UsersAPI


class AlbumsAPI(SpotifyResourceAPI):
    """
    Albums API endpoints for the Spotify Web API.

    .. important::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPI`
       and should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="catalog")
    def get_albums(
        self, album_ids: str | list[str], /, *, country_code: str | None = None
    ) -> dict[str, Any]:
        """
        `Albums > Get Album <https://developer.spotify.com/documentation
        /web-api/reference/get-an-album>`_: Get Spotify catalog
        information for a single album․
        `Albums > Get Several Albums <https://developer.spotify.com
        /documentation/web-api/reference/get-multiple-albums>`_: Get
        Spotify catalog information for multiple albums.

        .. admonition:: Third-party application mode
           :class: authorization-scope dropdown

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

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
        albums : dict[str, Any]
            Spotify content metadata for the albums.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single album

                  .. code::

                     {
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

               .. tab:: Multiple albums

                  .. code::

                     {
                       "albums": [
                         {
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
                       ]
                     }
        """
        return self._get_resources(
            "albums", album_ids, country_code=country_code, limit=20
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_album_tracks(
        self,
        album_id: str,
        /,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Album Tracks <https://developer.spotify.com
        /documentation/web-api/reference/get-an-albums-tracks>`_: Get
        Spotify catalog information for tracks in an album.

        .. admonition:: Third-party application mode
           :class: authorization-scope dropdown

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        album_id : str; positional-only
            Spotify ID of the album.

            **Example**: :code:`"4aawyAB9vmqN3uQ7FjRGTy"`.

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
            Page of Spotify content metadata for the tracks in the
            album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
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
                  }
        """
        return self._get_resource_items(
            "albums",
            album_id,
            "tracks",
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @_copy_docstring(UsersAPI.get_my_saved_albums)
    def get_my_saved_albums(
        self,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_my_saved_albums(
            country_code=country_code, limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.save_albums)
    def save_albums(self, album_ids: str | list[str], /) -> None:
        self._client.users.save_albums(album_ids)

    @_copy_docstring(UsersAPI.remove_saved_albums)
    def remove_saved_albums(self, album_ids: str | list[str], /) -> None:
        self._client.users.remove_saved_albums(album_ids)

    @_copy_docstring(UsersAPI.are_albums_saved)
    def are_albums_saved(self, album_ids: str | list[str], /) -> list[bool]:
        return self._client.users.are_albums_saved(album_ids)

    @TTLCache.cached_method(ttl="featured")
    def get_new_releases(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        `Albums > Get New Releases <https://developer.spotify.com
        /documentation/web-api/reference/get-new-releases>`_: Get
        Spotify catalog information for featured new releases.

        Parameters
        ----------
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
            Page of Spotify content metadata for the featured new
            releases.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albums": {
                      "href": <str>,
                      "items": [
                        {
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
                  }
        """
        params = {}
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "browse/new-releases", params=params
        ).json()
