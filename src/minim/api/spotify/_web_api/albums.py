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
        self, album_ids: str | list[str], /, *, market: str = None
    ) -> dict[str, Any]:
        """
        `Albums > Get Album <https://developer.spotify.com/documentation
        /web-api/reference/get-an-album>`_: Get Spotify catalog
        information for a single album․
        `Albums > Get Several Albums <https://developer.spotify.com
        /documentation/web-api/reference/get-multiple-albums>`_: Get
        Spotify catalog information for multiple albums.

        Parameters
        ----------
        album_ids : str, positional-only
            Spotify ID of the albums.

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
        albums : `dict[str, Any]`
            Spotify content metadata for the albums.

            .. admonition:: Sample response
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
        if not isinstance(album_ids, str):
            album_ids = ",".join(album_ids)
        if "," not in album_ids:
            return self._client._request(
                "GET", f"albums/{album_ids}", params={"market": market}
            )
        return self._client._request(
            "GET", "albums", params={"ids": album_ids, "market": market}
        )
