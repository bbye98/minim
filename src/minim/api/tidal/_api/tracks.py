from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import TIDALResourceAPI
from .search import SearchAPI
from .users import UsersAPI


class TracksAPI(TIDALResourceAPI):
    """
    Tracks API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _RELATIONSHIPS = {
        "albums",
        "artists",
        "genres",
        "lyrics",
        "owners",
        "providers",
        "radio",
        "shares",
        "similarTracks",
        "sourceFile",
        "trackStatistics",
    }

    @TTLCache.cached_method(ttl="popularity")
    def get_tracks(
        self,
        track_ids: int | str | list[int | str] | None = None,
        /,
        *,
        isrcs: str | list[str] | None = None,
        owner_ids: int | str | list[int | str] | None = None,
        country_code: str | None = None,
        expand: str | list[str] | None = None,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Single Track <https://tidal-music.github.io
        /tidal-api-reference/#/tracks/get_tracks__id_>`_: Get TIDAL
        catalog information for a track․
        `Tracks > Get Multiple Tracks <https://tidal-music.github.io
        /tidal-api-reference/#/tracks/get_tracks>`_: Get TIDAL catalog
        information for multiple tracks.

        .. admonition:: User authentication
           :class: authorization-scope dropdown

           .. tab:: Optional

              User authentication
                 Access information on an item's owners.

        .. note::

           Exactly one of `track_ids`, `isrcs`, or `owner_ids` must
           be provided. When `isrcs` or `owner_ids` is specified, the
           request will always be sent to the endpoint for multiple
           tracks.

        Parameters
        ----------
        track_ids : int, str, or list[int | str]; positional-only; optional
            TIDAL IDs of the tracks.

            **Examples**:

            .. container::

               * :code:`46369325`
               * :code:`"75413016"`
               * :code:`[46369325, "75413016"]`

        isrcs : str or list[str]; keyword-only; optional
            International Standard Recording Codes (ISRCs) of the
            tracks.

            **Examples**: :code:`"QMJMT1701237"`,
            :code:`["QMJMT1701237", "USAT21404265"]`.

        owner_ids : int, str, or list[int | str]; keyword-only; optional
            TIDAL IDs of the tracks' owners.

            **Examples**: :code:`123456`, :code:`"123456"`,
            :code:`[123456, "654321"]`.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        expand : str or list[str]; keyword-only; optional
            Related resources to include metadata for in the response.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"genres"`, :code:`"lyrics"`, :code:`"owners"`,
            :code:`"providers"`, :code:`"radio"`, :code:`"shares"`,
            :code:`"similarTracks"`, :code:`"sourceFile"`,
            :code:`"trackStatistics"`.

            **Examples**: :code:`"lyrics"`,
            :code:`["albums", "artists"]`.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results when requesting
            multiple tracks.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        tracks : dict[str, Any]
            TIDAL content metadata for the tracks.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single track

                  .. code::

                     {
                       "data": {
                         "attributes": {
                           "accessType": <str>,
                           "availability": <list[str]>,
                           "bpm": <float>,
                           "copyright": {
                             "text": <str>
                           },
                           "duration": <str>,
                           "explicit": <bool>,
                           "externalLinks": [
                             {
                               "href": <str>,
                               "meta": {
                                 "type": <str>
                               }
                             }
                           ],
                           "isrc": <str>,
                           "key": <str>,
                           "keyScale": <str>,
                           "mediaTags": <list[str]>,
                           "popularity": <float>,
                           "spotlighted": <bool>,
                           "title": <str>,
                           "toneTags": <list[str]>,
                           "version": <str>
                         },
                         "id": <str>,
                         "relationships": {
                           "albums": {
                             "data": [
                               {
                                 "id": <str>,
                                 "type": "albums"
                               }
                             ],
                             "links": {
                               "self": <str>
                             }
                           },
                           "artists": {
                             "data": [
                               {
                                 "id": <str>,
                                 "type": "artists"
                               }
                             ],
                             "links": {
                               "self": <str>
                             }
                           },
                           "genres": {
                             "data": [],
                             "links": {
                               "self": <str>
                             }
                           },
                           "lyrics": {
                             "data": [],
                             "links": {
                               "self": <str>
                             }
                           },
                           "owners": {
                             "data": [],
                             "links": {
                               "self": <str>
                             }
                           },
                           "providers": {
                             "data": [
                               {
                                 "id": <str>,
                                 "type": "providers"
                               }
                             ],
                             "links": {
                               "self": <str>
                             }
                           },
                           "radio": {
                             "data": [
                               {
                                 "id": <str>,
                                 "type": "playlists"
                               }
                             ],
                             "links": {
                               "self": <str>
                             }
                           },
                           "shares": {
                             "data": [],
                             "links": {
                               "self": <str>
                             }
                           },
                           "similarTracks": {
                             "data": [
                               {
                                 "id": <str>,
                                 "type": "tracks"
                               }
                             ],
                             "links": {
                               "meta": {
                                 "nextCursor": <str>
                               },
                               "next": <str>,
                               "self": <str>
                             }
                           },
                           "sourceFile": {
                             "links": {
                               "self": <str>
                             }
                           },
                           "trackStatistics": {
                             "links": {
                               "self": <str>
                             }
                           }
                         },
                         "type": "tracks"
                       },
                       "included": [
                         {
                           "attributes": {
                             "accessType": <str>,
                             "availability": <list[str]>,
                             "barcodeId": <str>,
                             "copyright": {
                               "text": <str>
                             },
                             "duration": <str>,
                             "explicit": <bool>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "mediaTags": <list[str]>,
                             "numberOfItems": <int>,
                             "numberOfVolumes": <int>,
                             "popularity": <float>,
                             "releaseDate": <str>,
                             "title": <str>,
                             "type": "ALBUM"
                           },
                           "id": <str>,
                           "relationships": {
                             "artists": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "coverArt": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "genres": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "items": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "providers": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "similarAlbums": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "suggestedCoverArts" : {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "albums"
                         },
                         {
                           "attributes": {
                             "contributionsEnabled": <bool>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "name": <str>,
                             "popularity": <float>,
                             "spotlighted": <bool>
                           },
                           "id": <str>,
                           "relationships": {
                             "albums": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "biography": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "followers": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "following": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "profileArt": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "radio": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "roles": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "similarArtists": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "trackProviders": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "tracks": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "videos": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "artists"
                         },
                         {
                           "attributes": {
                             "accessType": <str>,
                             "bounded": <bool>,
                             "createdAt": <str>,
                             "description": <str>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "lastModifiedAt": <str>,
                             "name": <str>,
                             "playlistType": "MIX"
                           },
                           "id": <str>,
                           "relationships": {
                             "coverArt": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "items": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "playlists"
                         },
                         {
                           "attributes": {
                             "name": <str>
                           },
                           "id": <str>,
                           "type": "providers"
                         },
                         {
                           "attributes": {
                             "accessType": <str>,
                             "availability": <list[str]>,
                             "bpm": <float>,
                             "copyright": {
                               "text": <str>
                             },
                             "createdAt": <str>,
                             "duration": <str>,
                             "explicit": <bool>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "isrc": <str>,
                             "key": <str>,
                             "keyScale": <str>,
                             "mediaTags": <list[str]>,
                             "popularity": <float>,
                             "spotlighted": <bool>,
                             "title": <str>,
                             "toneTags": <list[str]>,
                             "version": <str>
                           },
                           "id": <str>,
                           "relationships": {
                             "albums": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "artists": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "genres": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "lyrics": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "providers": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "radio": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "shares": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "similarTracks": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "sourceFile": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "trackStatistics": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "tracks"
                         }
                       ],
                       "links": {
                         "meta": {
                           "nextCursor": <str>
                         },
                         "next": <str>,
                         "self": <str>
                       }
                     }

               .. tab:: Multiple tracks

                  .. code::

                     {
                       "data": [
                         {
                           "attributes": {
                             "accessType": <str>,
                             "availability": <list[str]>,
                             "bpm": <float>,
                             "copyright": {
                               "text": <str>
                             },
                             "duration": <str>,
                             "explicit": <bool>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "isrc": <str>,
                             "key": <str>,
                             "keyScale": <str>,
                             "mediaTags": <list[str]>,
                             "popularity": <float>,
                             "spotlighted": <bool>,
                             "title": <str>,
                             "toneTags": <list[str]>,
                             "version": <str>
                           },
                           "id": <str>,
                           "relationships": {
                             "albums": {
                               "data": [
                                 {
                                   "id": <str>,
                                   "type": "albums"
                                 }
                               ],
                               "links": {
                                 "self": <str>
                               }
                             },
                             "artists": {
                               "data": [
                                 {
                                   "id": <str>,
                                   "type": "artists"
                                 }
                               ],
                               "links": {
                                 "self": <str>
                               }
                             },
                             "genres": {
                               "data": [],
                               "links": {
                                 "self": <str>
                               }
                             },
                             "lyrics": {
                               "data": [],
                               "links": {
                                 "self": <str>
                               }
                             },
                             "owners": {
                               "data": [],
                               "links": {
                                 "self": <str>
                               }
                             },
                             "providers": {
                               "data": [
                                 {
                                   "id": <str>,
                                   "type": "providers"
                                 }
                               ],
                               "links": {
                                 "self": <str>
                               }
                             },
                             "radio": {
                               "data": [
                                 {
                                   "id": <str>,
                                   "type": "playlists"
                                 }
                               ],
                               "links": {
                                 "self": <str>
                               }
                             },
                             "shares": {
                               "data": [],
                               "links": {
                                 "self": <str>
                               }
                             },
                             "similarTracks": {
                               "data": [
                                 {
                                   "id": <str>,
                                   "type": "tracks"
                                 }
                               ],
                               "links": {
                                 "meta": {
                                   "nextCursor": <str>
                                 },
                                 "next": <str>,
                                 "self": <str>
                               }
                             },
                             "sourceFile": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "trackStatistics": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "tracks"
                         }
                       ],
                       "included": [
                         {
                           "attributes": {
                             "accessType": <str>,
                             "availability": <list[str]>,
                             "barcodeId": <str>,
                             "copyright": {
                               "text": <str>
                             },
                             "duration": <str>,
                             "explicit": <bool>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "mediaTags": <list[str]>,
                             "numberOfItems": <int>,
                             "numberOfVolumes": <int>,
                             "popularity": <float>,
                             "releaseDate": <str>,
                             "title": <str>,
                             "type": "ALBUM"
                           },
                           "id": <str>,
                           "relationships": {
                             "artists": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "coverArt": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "genres": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "items": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "providers": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "similarAlbums": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "suggestedCoverArts" : {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "albums"
                         },
                         {
                           "attributes": {
                             "contributionsEnabled": <bool>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "name": <str>,
                             "popularity": <float>,
                             "spotlighted": <bool>
                           },
                           "id": <str>,
                           "relationships": {
                             "albums": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "biography": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "followers": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "following": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "profileArt": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "radio": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "roles": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "similarArtists": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "trackProviders": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "tracks": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "videos": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "artists"
                         },
                         {
                           "attributes": {
                             "accessType": <str>,
                             "bounded": <bool>,
                             "createdAt": <str>,
                             "description": <str>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "lastModifiedAt": <str>,
                             "name": <str>,
                             "playlistType": "MIX"
                           },
                           "id": <str>,
                           "relationships": {
                             "coverArt": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "items": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "playlists"
                         },
                         {
                           "attributes": {
                             "name": <str>
                           },
                           "id": <str>,
                           "type": "providers"
                         },
                         {
                           "attributes": {
                             "accessType": <str>,
                             "availability": <list[str]>,
                             "bpm": <float>,
                             "copyright": {
                               "text": <str>
                             },
                             "createdAt": <str>,
                             "duration": <str>,
                             "explicit": <bool>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "isrc": <str>,
                             "key": <str>,
                             "keyScale": <str>,
                             "mediaTags": <list[str]>,
                             "popularity": <float>,
                             "spotlighted": <bool>,
                             "title": <str>,
                             "toneTags": <list[str]>,
                             "version": <str>
                           },
                           "id": <str>,
                           "relationships": {
                             "albums": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "artists": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "genres": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "lyrics": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "providers": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "radio": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "shares": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "similarTracks": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "sourceFile": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "trackStatistics": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "tracks"
                         }
                       ],
                       "links": {
                         "meta": {
                           "nextCursor": <str>
                         },
                         "next": <str>,
                         "self": <str>
                       }
                     }
        """
        if sum(arg is not None for arg in [track_ids, isrcs, owner_ids]) != 1:
            raise ValueError(
                "Exactly one of `track_ids`, `isrcs`, or "
                "`owner_ids` must be provided."
            )
        params = {}
        if isrcs is not None:
            if isinstance(isrcs, str):
                self._validate_isrc(isrcs)
            elif isinstance(isrcs, list | tuple):
                for isrc in isrcs:
                    self._validate_isrc(isrc)
            else:
                raise ValueError(
                    "`isrcs` must be a string or a list of strings."
                )
            params["filter[isrc]"] = isrcs
        elif owner_ids is not None:
            self._client._validate_tidal_ids(owner_ids)
            params["filter[owners.id]"] = owner_ids
        return self._get_resources(
            "tracks",
            track_ids,
            country_code=country_code,
            expand=expand,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_track_albums(
        self,
        track_id: str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Track Albums <https://tidal-music.github.io
        /tidal-api-reference/#/tracks
        /get_tracks__id__relationships_albums>`_: Get TIDAL catalog
        information for albums containing a track.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the albums
            containing the track.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        albums : dict[str, Any]
            TIDAL content metadata for the albums containing the track.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "type": "albums"
                      }
                    ],
                    "included": [
                      {
                        "attributes": {
                          "accessType": <str>,
                          "availability": <list[str]>,
                          "barcodeId": <str>,
                          "copyright": {
                            "text": <str>
                          },
                          "duration": <str>,
                          "explicit": <bool>,
                          "externalLinks": [
                            {
                              "href": <str>,
                              "meta": {
                                "type": <str>
                              }
                            }
                          ],
                          "mediaTags": <list[str]>,
                          "numberOfItems": <int>,
                          "numberOfVolumes": <int>,
                          "popularity": <float>,
                          "releaseDate": <str>,
                          "title": <str>,
                          "type": "ALBUM"
                        },
                        "id": <str>,
                        "relationships": {
                          "artists": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "coverArt": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "genres": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "items": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "owners": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "providers": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "similarAlbums": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "suggestedCoverArts" : {
                            "links": {
                              "self": <str>
                            }
                          }
                        },
                        "type": "albums"
                      }
                    ],
                    "links": {
                      "meta": {
                        "nextCursor": <str>
                      },
                      "next": <str>,
                      "self": <str>
                    }
                  }
        """
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "albums",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_track_artists(
        self,
        track_id: str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Track Artists <https://tidal-music.github.io
        /tidal-api-reference/#/tracks
        /get_tracks__id__relationships_artists>`_: Get TIDAL catalog
        information for a track's artists.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the track's
            artists.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        artists : dict[str, Any]
            TIDAL content metadata for the track's artists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "type": "artists"
                      }
                    ],
                    "included": [
                      {
                        "attributes": {
                          "contributionsEnabled": <bool>,
                          "externalLinks": [
                            {
                              "href": <str>,
                              "meta": {
                                "type": <str>
                              }
                            }
                          ],
                          "name": <str>,
                          "popularity": <float>,
                          "spotlighted": <bool>
                        },
                        "id": <str>,
                        "relationships": {
                          "albums": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "biography": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "followers": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "following": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "owners": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "profileArt": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "radio": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "roles": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "similarArtists": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "trackProviders": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "tracks": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "videos": {
                            "links": {
                              "self": <str>
                            }
                          }
                        },
                        "type": "artists"
                      }
                    ],
                    "links": {
                      "meta": {
                        "nextCursor": <str>
                      },
                      "next": <str>,
                      "self": <str>
                    }
                  }
        """
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "artists",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_owners(
        self,
        track_id: str,
        /,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Track Owners <https://tidal-music.github.io
        /tidal-api-reference/#/tracks
        /get_tracks__id__relationships_owners>`_: Get TIDAL catalog
        information for a track's owners.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the track's
            owners.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        owners : dict[str, Any]
            TIDAL content metadata for the track's owners.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [],
                    "included": [],
                    "links": {
                      "meta": {
                        "nextCursor": <str>
                      },
                      "next": <str>,
                      "self": <str>
                    }
                  }
        """
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "owners",
            country_code=None,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_providers(
        self,
        track_id: str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Track Providers <https://tidal-music.github.io
        /tidal-api-reference/#/tracks
        /get_tracks__id__relationships_providers>`_: Get TIDAL catalog
        information for a track's providers.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the track's
            providers.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        providers : dict[str, Any]
            TIDAL content metadata for the track's providers.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "type": "providers"
                      }
                    ],
                    "included": [
                      {
                        "attributes": {
                          "name": <str>
                        },
                        "id": <str>,
                        "type": "providers"
                      }
                    ],
                    "links": {
                      "meta": {
                        "nextCursor": <str>
                      },
                      "next": <str>,
                      "self": <str>
                    }
                  }
        """
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "providers",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="daily")
    def get_track_mix(
        self,
        track_id: str,
        /,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Track Radio <https://tidal-music.github.io
        /tidal-api-reference/#/tracks
        /get_tracks__id__relationships_radio>`_: Get TIDAL catalog
        information for a track's mix.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the track's
            mix.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        mix : dict[str, Any]
            TIDAL content metadata for the track's mix.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "type": "playlists"
                      }
                    ],
                    "included": [
                      {
                        "attributes": {
                          "accessType": <str>,
                          "bounded": <bool>,
                          "createdAt": <str>,
                          "description": <str>,
                          "externalLinks": [
                            {
                              "href": <str>,
                              "meta": {
                                "type": <str>
                              }
                            }
                          ],
                          "lastModifiedAt": <str>,
                          "name": <str>,
                          "playlistType": "MIX"
                        },
                        "id": <str>,
                        "relationships": {
                          "coverArt": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "items": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "owners": {
                            "links": {
                              "self": <str>
                            }
                          }
                        },
                        "type": "playlists"
                      }
                    ],
                    "links": {
                      "meta": {
                        "nextCursor": <str>
                      },
                      "next": <str>,
                      "self": <str>
                    }
                  }
        """
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "radio",
            country_code=None,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_shares(
        self,
        track_id: str,
        /,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Track Shares <https://tidal-music.github.io
        /tidal-api-reference/#/tracks
        /get_tracks__id__relationships_shares>`_: Get TIDAL catalog
        information for a track's shares.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the track's
            shares.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        shares : dict[str, Any]
            TIDAL content metadata for the track's shares.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "included": [],
                    "links": {
                      "meta": {
                        "nextCursor": <str>
                      },
                      "next": <str>,
                      "self": <str>
                    }
                  }
        """
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "shares",
            country_code=None,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_similar_tracks(
        self,
        track_id: str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Similar Tracks <https://tidal-music.github.io
        /tidal-api-reference/#/tracks
        /get_tracks__id__relationships_similarTracks>`_: Get TIDAL
        catalog information for other tracks that are similar to a
        track.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the similar
            tracks.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        tracks : dict[str, Any]
            TIDAL content metadata for the similar tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "type": "tracks"
                      }
                    ],
                    "included": [
                      {
                        "attributes": {
                          "accessType": <str>,
                          "availability": <list[str]>,
                          "bpm": <float>,
                          "copyright": {
                            "text": <str>
                          },
                          "createdAt": <str>,
                          "duration": <str>,
                          "explicit": <bool>,
                          "externalLinks": [
                            {
                              "href": <str>,
                              "meta": {
                                "type": <str>
                              }
                            }
                          ],
                          "isrc": <str>,
                          "key": <str>,
                          "keyScale": <str>,
                          "mediaTags": <list[str]>,
                          "popularity": <float>,
                          "spotlighted": <bool>,
                          "title": <str>,
                          "toneTags": <list[str]>,
                          "version": <str>
                        },
                        "id": <str>,
                        "relationships": {
                          "albums": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "artists": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "genres": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "lyrics": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "owners": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "providers": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "radio": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "shares": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "similarTracks": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "sourceFile": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "trackStatistics": {
                            "links": {
                              "self": <str>
                            }
                          }
                        },
                        "type": "tracks"
                      }
                    ],
                    "links": {
                      "meta": {
                        "nextCursor": <str>
                      },
                      "next": <str>,
                      "self": <str>
                    }
                  }
        """
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "similarTracks",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_source_file(
        self,
        track_id: str,
        /,
        *,
        include_metadata: bool = False,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Track Source File <https://tidal-music.github.io
        /tidal-api-reference/#/tracks
        /get_tracks__id__relationships_sourceFile>`_: Get TIDAL
        catalog information for a track's source file.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the track's
            source file.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        source_file : dict[str, Any]
            TIDAL content metadata for the track's source file.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "included": [],
                    "links": {
                      "meta": {
                        "nextCursor": <str>
                      },
                      "next": <str>,
                      "self": <str>
                    }
                  }
        """
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "sourceFile",
            country_code=None,
            include_metadata=include_metadata,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_statistics(
        self,
        track_id: str,
        /,
        *,
        include_metadata: bool = False,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Track Statistics <https://tidal-music.github.io
        /tidal-api-reference/#/tracks
        /get_tracks__id__relationships_trackStatistics>`_: Get TIDAL
        catalog information for a track's statistics.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the track's
            statistics.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        statistics : dict[str, Any]
            TIDAL content metadata for the track's statistics.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "included": [],
                    "links": {
                      "self": <str>
                    }
                  }
        """
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "trackStatistics",
            country_code=None,
            include_metadata=include_metadata,
            share_code=share_code,
        )

    @_copy_docstring(SearchAPI.search_tracks)
    def search_tracks(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        include_explicit: bool | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return self._client.search.search_tracks(
            query,
            country_code=country_code,
            include_explicit=include_explicit,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    @_copy_docstring(UsersAPI.get_saved_tracks)
    def get_saved_tracks(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_saved_tracks(
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include_metadata=include_metadata,
            cursor=cursor,
            sort_by=sort_by,
            descending=descending,
        )

    @_copy_docstring(UsersAPI.save_tracks)
    def save_tracks(
        self,
        track_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        self._client.users.save_tracks(
            track_ids, user_id=user_id, country_code=country_code
        )

    @_copy_docstring(UsersAPI.remove_saved_tracks)
    def remove_saved_tracks(
        self,
        track_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        self._client.users.remove_saved_tracks(
            track_ids, user_id=user_id, country_code=country_code
        )
