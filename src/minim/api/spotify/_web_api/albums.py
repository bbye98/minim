from collections.abc import Collection
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPIAlbumEndpoints:
    """
    Spotify Web API album endpoints.

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

    def get_albums(
        self, album_ids: str | Collection[str], /, *, market: str | None = None
    ) -> dict[str, Any]:
        """
        `Albums > Get Album <https://developer.spotify.com/documentation
        /web-api/reference/get-an-album>`_: Get Spotify catalog
        information for a single album․
        `Albums > Get Several Albums <https://developer.spotify.com
        /documentation/web-api/reference/get-multiple-albums>`_: Get
        Spotify catalog information for multiple albums.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
        album_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the albums. A
            maximum of 20 IDs can be sent in one request.

            **Examples**: :code:`"4aawyAB9vmqN3uQ7FjRGTy"`,
            :code:`"382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc"`,
            :code:`["382ObEPsp2rxGrnsizN5TX", "1A2GTWGtFfWp7KSQTwWOyo",
            "2noRn2Aes5aoNVsU6iWThc"]`.

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
                               "type": <str>,
                               "uri": <str>
                             },
                             "name": <str>,
                             "preview_url": <str>,
                             "restrictions": {
                               "reason": <str>
                             },
                             "track_number": <int>,
                             "type": <str>,
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
                                   "type": <str>,
                                   "uri": <str>
                                 },
                                 "name": <str>,
                                 "preview_url": <str>,
                                 "restrictions": {
                                   "reason": <str>
                                 },
                                 "track_number": <int>,
                                 "type": <str>,
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
        is_string = isinstance(album_ids, str)
        album_ids, n_ids = self._client._prepare_spotify_ids(
            album_ids, limit=20
        )
        params = {}
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if is_string and n_ids == 1:
            return self._client._request(
                "GET", f"albums/{album_ids}", params=params
            ).json()

        params["ids"] = album_ids
        return self._client._request("GET", "albums", params=params).json()

    def get_album_tracks(
        self,
        album_id: str,
        /,
        *,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Album Tracks <https://developer.spotify.com
        /documentation/web-api/reference/get-an-albums-tracks>`_: Get
        Spotify catalog information about an album's tracks.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
        album_id : str, positional-only
            Spotify ID of the album.

            **Example**: :code:`"4aawyAB9vmqN3uQ7FjRGTy"`.

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
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first track to return. Use with `limit` to get
            the next set of tracks.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        tracks : dict[str, Any]
            Spotify content metadata for the album's tracks.

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
                          "type": <str>,
                          "uri": <str>
                        },
                        "name": <str>,
                        "preview_url": <str>,
                        "restrictions": {
                          "reason": <str>
                        },
                        "track_number": <int>,
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
        self._client._validate_spotify_id(album_id)
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
        return self._client._request(
            "GET", f"albums/{album_id}/tracks", params=params
        ).json()

    def get_saved_albums(
        self,
        *,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get User's Saved Albums <https://developer.spotify.com
        /documentation/web-api/reference/get-users-saved-albums>`_: Get
        the albums saved in the current user's "Your Music" library.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read`
                 Access your saved content.

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
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
        saved_albums : dict[str, Any]
            Spotify content metadata for the user's saved albums.

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
                                  "type": <str>,
                                  "uri": <str>
                                },
                                "name": <str>,
                                "preview_url": <str>,
                                "restrictions": {
                                  "reason": <str>
                                },
                                "track_number": <int>,
                                "type": <str>,
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
        self._client._require_scopes("get_saved_albums", "user-library-read")
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
        return self._client._request("GET", "me/albums", params=params).json()

    def save_albums(self, album_ids: str | Collection[str], /) -> None:
        """
        `Albums > Save Albums for Current User
        <https://developer.spotify.com/documentation/web-api/reference
        /save-albums-user>`_: Save one or more albums to the current
        user's "Your Music" library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify`
                  Manage your saved content.

        Parameters
        ----------
        album_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the albums. A
            maximum of 20 IDs can be sent in one request.

            **Examples**: :code:`"4aawyAB9vmqN3uQ7FjRGTy"`,
            :code:`"382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc"`,
            :code:`["382ObEPsp2rxGrnsizN5TX", "1A2GTWGtFfWp7KSQTwWOyo",
            "2noRn2Aes5aoNVsU6iWThc"]`.
        """
        self._client._require_scopes("save_albums", "user-library-modify")
        self._client._request(
            "PUT",
            "me/albums",
            params={
                "ids": self._client._prepare_spotify_ids(album_ids, limit=20)[0]
            },
        )

    def remove_saved_albums(self, album_ids: str | Collection[str], /) -> None:
        """
        `Albums > Remove User's Saved Albums
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-albums-user>`_: Remove one or more albums from the
        current user's "Your Music" library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify`
                  Manage your saved content.

        Parameters
        ----------
        album_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the albums. A
            maximum of 20 IDs can be sent in one request.

            **Examples**: :code:`"4aawyAB9vmqN3uQ7FjRGTy"`,
            :code:`"382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc"`,
            :code:`["382ObEPsp2rxGrnsizN5TX", "1A2GTWGtFfWp7KSQTwWOyo",
            "2noRn2Aes5aoNVsU6iWThc"]`.
        """
        self._client._require_scopes(
            "remove_saved_albums", "user-library-modify"
        )
        self._client._request(
            "DELETE",
            "me/albums",
            params={
                "ids": self._client._prepare_spotify_ids(album_ids, limit=20)[0]
            },
        )

    def are_albums_saved(
        self, album_ids: str | Collection[str], /
    ) -> list[bool]:
        """
        `Albums > Check User's Saved Albums
        <https://developer.spotify.com/documentation/web-api/reference
        /check-users-saved-albums>`_: Check if one or more albums are
        already saved in the current user's "Your Music" library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read`
                  Access your saved content.

        Parameters
        ----------
        album_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the albums. A
            maximum of 20 IDs can be sent in one request.

            **Examples**: :code:`"4aawyAB9vmqN3uQ7FjRGTy"`,
            :code:`"382ObEPsp2rxGrnsizN5TX,1A2GTWGtFfWp7KSQTwWOyo,2noRn2Aes5aoNVsU6iWThc"`,
            :code:`["382ObEPsp2rxGrnsizN5TX", "1A2GTWGtFfWp7KSQTwWOyo",
            "2noRn2Aes5aoNVsU6iWThc"]`.

        Returns
        -------
        are_albums_saved : list[bool]
            Whether the current user has each of the specified albums
            saved in their "Your Music" library.

            **Sample response**: :code:`[False, True]`.
        """
        self._client._require_scopes("are_albums_saved", "user-library-read")
        return self._client._request(
            "GET",
            "me/albums/contains",
            params={
                "ids": self._client._prepare_spotify_ids(album_ids, limit=20)[0]
            },
        ).json()

    def get_new_releases(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        `Albums > Get New Releases <https://developer.spotify.com
        /documentation/web-api/reference/get-new-releases>`_: Get a list
        of new album releases featured on Spotify.

        Parameters
        ----------
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
        new_releases : dict[str, Any]
            Spotify content metadata for the new album releases.

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
