from collections.abc import Collection
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache
from ._shared import TIDALResourceAPI

if TYPE_CHECKING:
    from .. import TIDALAPI


class AlbumsAPI(TIDALResourceAPI):
    """
    Albums API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _RESOURCES = {
        "artists",
        "coverArt",
        "genres",
        "items",
        "owners",
        "providers",
        "similarAlbums",
    }
    _client: "TIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_albums(
        self,
        *,
        album_ids: int | str | Collection[int | str] | None = None,
        barcodes: int | str | Collection[int | str] | None = None,
        country_code: str | None = None,
        include: str | Collection[str] | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Single Album <https://tidal-music.github.io
        /tidal-api-reference/#/albums/get_albums__id_>`_: Get TIDAL
        catalog information for a single album by its TIDAL ID․
        `Albums > Get Multiple Albums <https://tidal-music.github.io
        /tidal-api-reference/#/albums/get_albums>`_: Get TIDAL catalog
        information for multiple albums by their TIDAL IDs or barcodes.

        Parameters
        ----------
        album_ids : int, str, or Collection[int | str], keyword-only, \
        optional
            TIDAL ID(s) of the album(s), provided as either an integer,
            a string, or a collection of integers and/or strings.

            .. note::

               Exactly one of `album_ids` or `barcodes` must be provided.

            **Examples**: 
            
            .. container::

               * :code:`46369321`
               * :code:`"46369321"`
               * :code:`[46369321, 251380836]`
               * :code:`[46369321, "251380836"]`
               * :code:`["46369321", "251380836"]`

        barcodes : int, str, or Collection[int | str], keyword-only, \
        optional
            Barcode ID(s) of the album(s), provided as either an integer,
            a string, or a collection of integers and/or strings.

            .. note::

               Exactly one of `album_ids` or `barcodes` must be provided.

            **Examples**: 
            
            .. container::
            
               * :code:`075678671173`
               * :code:`"075678671173"`
               * :code:`[075678671173, 602448438034]`
               * :code:`[075678671173, "602448438034"]`
               * :code:`["075678671173", "602448438034"]`

        country_code : str, keyword-only, optional
            ISO 3166-1 alpha-2 country code. Only optional when the 
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : str or Collection[str], keyword-only, optional
            Related resources to include in the response.

            **Valid values**: :code:`"artists"`, :code:`"coverArt"`,
            :code:`"genres"`, :code:`"items"`, :code:`"owners"`, 
            `:code:`"providers"`, :code:`"similarAlbums"`.

        cursor : str, keyword-only, optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        albums : dict[str, Any]
            TIDAL content metadata for the albums. 

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single album

                  .. code::

                     {
                       "data": {
                         "attributes": {
                           "accessType": "PUBLIC",
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
                           "coverArt": {
                             "data": [
                               {
                                 "id": <str>,
                                 "type": "artworks"
                               }
                             ],
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
                             "data": [
                               {
                                 "id": <str>,
                                 "meta": {
                                   "trackNumber": <int>,
                                   "volumeNumber": <int>
                                 },
                                 "type": "tracks"
                               },
                               {
                                 "id": <str>,
                                 "meta": {
                                   "trackNumber": <int>,
                                   "volumeNumber": <int>
                                 },
                                 "type": "videos"
                               }
                             ],
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
                           "similarAlbums": {
                             "data": [
                               {
                                 "id": <str>,
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
                         },
                         "type": "albums"
                       },
                       "included": [
                         {
                           "attributes": {
                             "accessType": "PUBLIC",
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
                             }
                           },
                           "type": "albums"
                         },
                         {
                           "attributes": {
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "name": <str>,
                             "popularity": <float>
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
                             "files": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "height": <int>,
                                   "width": <int>
                                 }
                               }
                             ],
                             "mediaType": "IMAGE"
                           },
                           "id": <str>,
                           "relationships": {
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "artworks"
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
                             "accessType": "PUBLIC",
                             "availability": <list[str]>,
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
                             "mediaTags": <list[str]>,
                             "popularity": <float>,
                             "spotlighted": <bool>,
                             "title": <str>,
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
                         },
                         {
                           "attributes": {
                             "availability": <list[str]>,
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
                             "popularity": <float>,
                             "releaseDate": <str>,
                             "title": <str>
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
                             "providers": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "thumbnailArt": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "videos"
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

               .. tab:: Multiple albums

                  .. code::

                     {
                       "data": [
                         {
                           "attributes": {
                             "accessType": "PUBLIC",
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
                             "coverArt": {
                               "data": [
                                 {
                                   "id": <str>,
                                   "type": "artworks"
                                 }
                               ],
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
                               "data": [
                                 {
                                   "id": <str>,
                                   "meta": {
                                     "trackNumber": <int>,
                                     "volumeNumber": <int>
                                   },
                                   "type": "tracks"
                                 },
                                 {
                                   "id": <str>,
                                   "meta": {
                                     "trackNumber": <int>,
                                     "volumeNumber": <int>
                                   },
                                   "type": "videos"
                                 }
                               ],
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
                             "similarAlbums": {
                               "data": [
                                 {
                                   "id": <str>,
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
                           },
                           "type": "albums"
                         }
                       ],
                       "included": [
                         {
                           "attributes": {
                             "accessType": "PUBLIC",
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
                             }
                           },
                           "type": "albums"
                         },
                         {
                           "attributes": {
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "name": <str>,
                             "popularity": <float>
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
                             "files": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "height": <int>,
                                   "width": <int>
                                 }
                               }
                             ],
                             "mediaType": "IMAGE"
                           },
                           "id": <str>,
                           "relationships": {
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "artworks"
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
                             "accessType": "PUBLIC",
                             "availability": <list[str]>,
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
                             "mediaTags": <list[str]>,
                             "popularity": <float>,
                             "spotlighted": <bool>,
                             "title": <str>,
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
                         },
                         {
                           "attributes": {
                             "availability": <list[str]>,
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
                             "popularity": <float>,
                             "releaseDate": <str>,
                             "title": <str>
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
                             "providers": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "thumbnailArt": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "videos"
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
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include is not None:
            params["include"] = params["include"] = self._prepare_include(
                include
            )
        if album_ids is not None:
            if barcodes is not None:
                raise ValueError(
                    "Only one of `album_ids` or `barcodes` can be provided."
                )
            self._client._validate_tidal_ids(album_ids)
            if isinstance(album_ids, int | str):
                return self._client._request(
                    "GET", f"albums/{album_ids}", params=params
                ).json()
            params["filter[id]"] = album_ids
        elif barcodes is not None:
            if isinstance(barcodes, int | str):
                barcodes = [barcodes]
            for barcode in barcodes:
                self._client._validate_barcode(barcode)
            params["filter[barcodeId]"] = barcodes
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request("GET", "albums", params=params).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_album_artists(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Album's Artists
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_artists>`_: Get TIDAL
        catalog information for an album's artists.

        Parameters
        ----------
        album_id : int or str, positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str, optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool, keyword-only, default: :code:`False`
            Specifies whether to include TIDAL content metadata for
            the album's artists.

        cursor : str, keyword-only, optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        artists : dict[str, Any]
            TIDAL catalog information for the album's artists.

            .. admonition:: Sample response
               :class: dropdown

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
                       "externalLinks": [
                         {
                           "href": <str>,
                           "meta": {
                             "type": <str>
                           }
                         }
                       ],
                       "name": <str>,
                       "popularity": <float>
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
        self._client._validate_tidal_ids(album_id, _recursive=False)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = "artists"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET", f"albums/{album_id}/relationships/artists", params=params
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_album_cover_art(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Album's Cover Art
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_coverArt>`_: Get TIDAL
        catalog information for an album's cover art.

        Parameters
        ----------
        album_id : int or str, positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str, optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool, keyword-only, default: :code:`False`
            Specifies whether to include TIDAL content metadata for
            the album's cover art.

        cursor : str, keyword-only, optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        cover_art : dict[str, Any]
            TIDAL catalog information for the album's cover art.

            .. admonition:: Sample response
               :class: dropdown

               {
                 "data": [
                   {
                     "id": <str>,
                     "type": "artworks"
                   }
                 ],
                 "included": [
                   {
                     "attributes": {
                       "files": [
                         {
                           "href": <str>,
                           "meta": {
                             "height": <int>,
                             "width": <int>
                           }
                         }
                       ],
                       "mediaType": "IMAGE"
                     },
                     "id": <str>,
                     "relationships": {
                       "owners": {
                         "links": {
                           "self": <str>
                         }
                       }
                     },
                     "type": "artworks"
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
        self._client._validate_tidal_ids(album_id, _recursive=False)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = "coverArt"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET", f"albums/{album_id}/relationships/coverArt", params=params
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_album_items(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Album's Items
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_items>`_: Get TIDAL
        catalog information for an album's tracks and videos.

        Parameters
        ----------
        album_id : int or str, positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str, optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool, keyword-only, default: :code:`False`
            Specifies whether to include TIDAL content metadata for
            the album's tracks and videos.

        cursor : str, keyword-only, optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        items : dict[str, Any]
            TIDAL catalog information for the album's tracks and videos.

            .. admonition:: Sample response
               :class: dropdown

               {
                 "data": [
                   {
                     "id": <str>,
                     "meta": {
                       "trackNumber": <int>,
                       "volumeNumber": <int>
                     },
                     "type": "tracks"
                   },
                   {
                     "id": <str>,
                     "meta": {
                       "trackNumber": <int>,
                       "volumeNumber": <int>
                     },
                     "type": "videos"
                   }
                 ],
                 "included": [
                   {
                     "attributes": {
                       "accessType": "PUBLIC",
                       "availability": <list[str]>,
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
                       "mediaTags": <list[str]>,
                       "popularity": <float>,
                       "spotlighted": <bool>,
                       "title": <str>,
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
                   },
                   {
                     "attributes": {
                       "availability": <list[str]>,
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
                       "popularity": <float>,
                       "releaseDate": <str>,
                       "title": <str>
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
                       "providers": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "thumbnailArt": {
                         "links": {
                           "self": <str>
                         }
                       }
                     },
                     "type": "videos"
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
        self._client._validate_tidal_ids(album_id, _recursive=False)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = "items"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET", f"albums/{album_id}/relationships/items", params=params
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_album_owners(
        self,
        album_id: int | str,
        /,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Album's Owners
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_owners>`_: Get TIDAL
        catalog information for an album's owners.

        Parameters
        ----------
        album_id : int or str, positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        include : bool, keyword-only, default: :code:`False`
            Specifies whether to include TIDAL content metadata for
            the album's owners.

        cursor : str, keyword-only, optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        owners : dict[str, Any]
            TIDAL catalog information for the album's owners.

            .. admonition:: Sample response
               :class: dropdown

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
        self._client._validate_tidal_ids(album_id, _recursive=False)
        params = {}
        if include:
            params["include"] = "owners"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET", f"albums/{album_id}/relationships/owners", params=params
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_album_providers(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Album's Providers
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_providers>`_: Get TIDAL
        catalog information for an album's providers.

        Parameters
        ----------
        album_id : int or str, positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str, optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool, keyword-only, default: :code:`False`
            Specifies whether to include TIDAL content metadata for
            the album's providers.

        cursor : str, keyword-only, optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        providers : dict[str, Any]
            TIDAL catalog information for the album's providers.

            .. admonition:: Sample response
               :class: dropdown

               {
                 "data": [
                   {
                     "id": <str>,
                     "type": <str>
                   }
                 ],
                 "included": [
                   {
                     "attributes": {
                       "name": <str>
                     },
                     "id": <str>,
                     "type": <str>
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
        self._client._validate_tidal_ids(album_id, _recursive=False)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = "providers"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET", f"albums/{album_id}/relationships/providers", params=params
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_similar_albums(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Similar Albums
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_similarAlbums>`_: Get TIDAL
        catalog information for other albums that are similar to an
        album.

        Parameters
        ----------
        album_id : int or str, positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str, optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool, keyword-only, default: :code:`False`
            Specifies whether to include TIDAL content metadata for
            the similar albums.

        cursor : str, keyword-only, optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        albums : dict[str, Any]
            TIDAL catalog information for the similar albums.

            .. admonition:: Sample response
               :class: dropdown

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
                             "accessType": "PUBLIC",
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
        self._client._validate_tidal_ids(album_id, _recursive=False)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = "similarAlbums"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET",
            f"albums/{album_id}/relationships/similarAlbums",
            params=params,
        ).json()
