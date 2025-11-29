from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import TIDALResourceAPI
from .users import UsersAPI

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
        "suggestedCoverArts",
    }
    _client: "TIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_albums(
        self,
        album_ids: int | str | list[int | str] | None = None,
        /,
        *,
        barcodes: int | str | list[int | str] | None = None,
        owner_ids: int | str | list[int | str] | None = None,
        country_code: str | None = None,
        include: str | list[str] | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Single Album <https://tidal-music.github.io
        /tidal-api-reference/#/albums/get_albums__id_>`_: Get TIDAL
        catalog information for a single album․
        `Albums > Get Multiple Albums <https://tidal-music.github.io
        /tidal-api-reference/#/albums/get_albums>`_: Get TIDAL catalog
        information for multiple albums.

        .. admonition:: User authentication
           :class: authorization-scope dropdown

           .. tab:: Optional

              User authentication
                 Access information on an item's owners.

        Parameters
        ----------
        album_ids : int, str, or list[int | str]; positional-only; \
        optional
            TIDAL IDs of the albums, provided as either an integer, a
            string, or a list of integers and/or strings.

            .. note::

               Exactly one of `album_ids`, `barcodes`, or `owner_ids`
               must be provided.

            **Examples**:

            .. container::

               * :code:`46369321`
               * :code:`"46369321"`
               * :code:`[46369321, "251380836"]`

        barcodes : int, str, or list[int | str]; keyword-only; optional
            Barcodes of the albums, provided as either an integer, a
            string, or a list of integers and/or strings.

            .. note::

               Exactly one of `album_ids`, `barcodes`, or `owner_ids`
               must be provided. When this parameter is specified, the
               request will always be sent to the endpoint for multiple
               albums.

            **Examples**:

            .. container::

               * :code:`075678671173`
               * :code:`"075678671173"`
               * :code:`[075678671173, "602448438034"]`

        owner_ids : int, str, or list[int | str]; keyword-only; optional
            TIDAL IDs of the albums' owners, provided either as an
            integer, a string, or a list of integers and/or
            strings.

            .. note::

               Exactly one of `album_ids`, `barcodes`, or `owner_ids`
               must be provided. When this parameter is specified, the
               request will always be sent to the endpoint for multiple
               albums.

            **Examples**: :code:`123456`, :code:`"123456"`,
            :code:`["123456"]`.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : str or list[str]; keyword-only; optional
            Related resources to include in the response.

            **Valid values**: :code:`"artists"`, :code:`"coverArt"`,
            :code:`"genres"`, :code:`"items"`, :code:`"owners"`,
            :code:`"providers"`, :code:`"similarAlbums"`,
            :code:`"suggestedCoverArts"`.

        cursor : str; keyword-only; optional
            Cursor for pagination when requesting multiple albums.

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
                           },
                           "suggestedCoverArts" : {
                             "links": {
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
            params["include"] = self._prepare_include(include)
        if (
            sum(arg is not None for arg in (album_ids, barcodes, owner_ids))
            != 1
        ):
            raise ValueError(
                "Exactly one of `album_ids`, `barcodes`, or "
                "`owner_ids` must be provided."
            )
        if album_ids is not None:
            self._client._validate_tidal_ids(album_ids)
            if isinstance(album_ids, int | str):
                return self._client._request(
                    "GET", f"albums/{album_ids}", params=params
                ).json()
            params["filter[id]"] = album_ids
        elif barcodes is not None:
            if isinstance(barcodes, int | str):
                self._client._validate_barcode(barcodes)
            else:
                for barcode in barcodes:
                    self._client._validate_barcode(barcode)
            params["filter[barcodeId]"] = barcodes
        else:
            self._client._validate_tidal_ids(owner_ids)
            params["filter[owners.id]"] = owner_ids
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["page[cursor]"] = cursor
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
        `Albums > Get Album Artists
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_artists>`_: Get TIDAL
        catalog information for an album's artists.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the album artists.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        artists : dict[str, Any]
            TIDAL catalog information for the album artists.

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
        return self._get_album_resource(
            "artists", album_id, country_code, include=include, cursor=cursor
        )

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
        `Albums > Get Album Cover Art
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_coverArt>`_: Get TIDAL
        catalog information for an album's cover art.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the album's cover art.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        cover_art : dict[str, Any]
            TIDAL catalog information for the album's cover art.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

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
        return self._get_album_resource(
            "coverArt", album_id, country_code, include=include, cursor=cursor
        )

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
        `Albums > Get Album Items
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_items>`_: Get TIDAL
        catalog information for tracks and videos in an album.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the tracks and videos in the album.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        items : dict[str, Any]
            TIDAL catalog information for the tracks and videos in the
            album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

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
        return self._get_album_resource(
            "items", album_id, country_code, include=include, cursor=cursor
        )

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
        `Albums > Get Album Owners
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_owners>`_: Get TIDAL
        catalog information for an album's owners.

        .. admonition:: User authentication
           :class: authorization-scope dropdown

           .. tab:: Optional

              User authentication
                 Access information on an item's owners.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the album's owners.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        owners : dict[str, Any]
            TIDAL catalog information for the album's owners.

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
        return self._get_album_resource(
            "owners", album_id, False, include=include, cursor=cursor
        )

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
        `Albums > Get Album Providers
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_providers>`_: Get TIDAL
        catalog information for an album's providers.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the album's providers.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        providers : dict[str, Any]
            TIDAL catalog information for the album's providers.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

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
        return self._get_album_resource(
            "providers", album_id, country_code, include=include, cursor=cursor
        )

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
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the similar albums.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        albums : dict[str, Any]
            TIDAL catalog information for the similar albums.

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
        return self._get_album_resource(
            "similarAlbums",
            album_id,
            country_code,
            include=include,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_album_suggested_cover_arts(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Album's Suggested Cover Artworks
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_suggestedCoverArts>`_: Get TIDAL
        catalog information for an album's suggested cover artworks.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the suggested cover artworks.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        cover_artworks : dict[str, Any]
            TIDAL catalog information for the album's suggested cover
            artworks.

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
        return self._get_album_resource(
            "suggestedCoverArts",
            album_id,
            country_code,
            include=include,
            cursor=cursor,
        )

    @_copy_docstring(UsersAPI.get_favorite_albums)
    def get_favorite_albums(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include: bool = False,
        cursor: str | None = None,
        sort: str | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_favorite_albums(
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include=include,
            cursor=cursor,
            sort=sort,
        )

    @_copy_docstring(UsersAPI.favorite_albums)
    def favorite_albums(
        self,
        album_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        self._client.users.favorite_albums(
            album_ids, user_id=user_id, country_code=country_code
        )

    @_copy_docstring(UsersAPI.unfavorite_albums)
    def unfavorite_albums(
        self,
        album_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        self._client.users.unfavorite_albums(
            album_ids, user_id=user_id, country_code=country_code
        )

    def _get_album_resource(
        self,
        resource: str,
        album_id: int | str,
        /,
        country_code: bool | str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a resource related to an
        album.

        Parameters
        ----------
        resource : str; positional-only
            Related resource type.

            **Valid values**: :code:`"artists"`, :code:`"coverArt"`,
            :code:`"genres"`, :code:`"items"`, :code:`"owners"`,
            :code:`"providers"`, :code:`"similarAlbums"`.

        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : bool or str; optional
            ISO 3166-1 alpha-2 country code. If :code:`False`, the
            country code is not included in the request.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the related resource.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        resource : dict[str, Any]
            TIDAL catalog information for the related resource.
        """
        self._client._validate_tidal_ids(album_id, _recursive=False)
        params = {}
        if country_code is not False:
            self._client._resolve_country_code(country_code, params)
        if include is not None:
            self._client._validate_type("include", include, bool)
            if include:
                params["include"] = resource
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["page[cursor]"] = cursor
        return self._client._request(
            "GET",
            f"albums/{album_id}/relationships/{resource}",
            params=params,
        ).json()
