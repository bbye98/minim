from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import TIDALResourceAPI
from .users import UsersAPI

if TYPE_CHECKING:
    from .. import TIDALAPI


class ArtistsAPI(TIDALResourceAPI):
    """
    Artist Roles and Artists API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _RESOURCES = {
        "albums",
        "biography",
        "followers",
        "following",
        "owners",
        "profileArt",
        "radio",
        "roles",
        "similarArtists",
        "trackProviders",
        "tracks",
        "videos",
    }
    _client: "TIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_roles(
        self, artist_role_ids: int | str | list[int | str], /
    ) -> dict[str, Any]:
        """
        `Artist Roles > Get Single Artist Role
        <https://tidal-music.github.io/tidal-api-reference/#/artistRoles
        /get_artistRoles>`_: Get TIDAL catalog information for a single
        artist role․
        `Artist Roles > Get Multiple Artist Roles
        <https://tidal-music.github.io/tidal-api-reference/#/artistRoles
        /get_artistRoles__id_>`_: Get TIDAL catalog information for
        multiple artist roles.

        Parameters
        ----------
        artist_role_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of the artist roles, provided as either an
            integer, a string, or a list of integers and/or strings.

        Returns
        -------
        artist_roles : dict[str, Any]
            TIDAL catalog information for the artist roles.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single artist role

                  .. code::

                     {
                       "data": {
                         "attributes": {
                           "name": <str>
                         },
                         "id": <str>,
                         "type": "artistRoles"
                       },
                       "links": {
                         "self": <str>
                       }
                     }

               .. tab:: Multiple artist roles

                  .. code::

                     {
                       "data": [
                         {
                           "attributes": {
                             "name": <str>
                           },
                           "id": <str>,
                           "type": "artistRoles"
                         }
                       ],
                       "links": {
                         "self": <str>
                       }
                     }
        """
        self._client._validate_tidal_ids(artist_role_ids)
        if isinstance(artist_role_ids, int | str):
            return self._client._request(
                "GET", f"artistRoles/{artist_role_ids}"
            ).json()
        return self._client._request(
            "GET", "artistRoles", params={"filter[id]": artist_role_ids}
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_artists(
        self,
        artist_ids: int | str | list[int | str] | None = None,
        /,
        *,
        handles: str | list[str] | None = None,
        country_code: str | None = None,
        include: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """
        `Artists > Get Single Artist <https://tidal-music.github.io
        /tidal-api-reference/#/artists/get_artists__id_>`_: Get TIDAL
        catalog information for a single artist․
        `Artists > Get Multiple Artists <https://tidal-music.github.io
        /tidal-api-reference/#/artists/get_artists>`_: Get TIDAL catalog
        information for multiple artists.

        .. admonition:: User authentication
           :class: authorization-scope dropdown

           .. tab:: Optional

              User authentication
                 Access information on an item's owners.

        Parameters
        ----------
        artist_ids : int, str, or list[int | str], positional-only; \
        optional
            TIDAL ID(s) of the artist(s), provided as either an integer,
            a string, or a list of integers and/or strings.

            .. note::

               Exactly one of `artist_ids` or `handles` must be
               provided.

            **Examples**:

            .. container::

               * :code:`1566`
               * :code:`"4676988"`
               * :code:`[1566, "4676988"]`

        handles : str or list[str]; keyword-only; optional
            Artist handles.

            .. note::

               Exactly one of `artist_ids` or `handles` must be
               provided. When this parameter is specified, the request
               will always be sent to the endpoint for multiple artists.

            **Example**: :code:`"jayz"`.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : str or list[str]; keyword-only; optional
            Related resources to include in the response.

            **Valid values**: :code:`"albums"`, :code:`"biography"`,
            :code:`"followers"`, :code:`"following"`, :code:`"owners"`,
            :code:`"profileArt"`, :code:`"radio"`, :code:`"roles"`,
            :code:`"similarArtists"`, :code:`"trackProviders"`,
            :code:`"tracks"`, :code:`"videos"`.

        Returns
        -------
        artists : dict[str, Any]
            TIDAL content metadata for the artists.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single artist

                  .. code::

                     {
                       "data": {
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
                           "biography": {
                             "data": {
                               "id": <str>,
                               "type": "artistBiographies"
                             },
                             "links": {
                               "self": <str>
                             }
                           },
                           "followers": {
                             "data": [],
                             "links": {
                               "self": <str>
                             }
                           },
                           "following": {
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
                           "profileArt": {
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
                           "roles": {
                             "data": [
                               {
                                 "id": <str>,
                                 "type": "artistRoles"
                               }
                             ],
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
                             "name": <str>
                           },
                           "id": <str>,
                           "type": "artistRoles"
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
                             "accessType": "PUBLIC",
                             "bounded": <bool>,
                             "createdAt": <str>,
                             "description": "Artist Radio",
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
                             "name": <str>
                           },
                           "id": <str>,
                           "type": "providers"
                         },
                         {
                           "attributes": {
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
                         "self": <str>
                       }
                     }

               .. tab:: Multiple artists

                  .. code::

                     {
                       "data": [
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
                             "biography": {
                               "data": {
                                 "id": <str>,
                                 "type": "artistBiographies"
                               },
                               "links": {
                                 "self": <str>
                               }
                             },
                             "followers": {
                               "data": [],
                               "links": {
                                 "self": <str>
                               }
                             },
                             "following": {
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
                             "profileArt": {
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
                             "roles": {
                               "data": [
                                 {
                                   "id": <str>,
                                   "type": "artistRoles"
                                 }
                               ],
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
                             "name": <str>
                           },
                           "id": <str>,
                           "type": "artistRoles"
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
                             "accessType": "PUBLIC",
                             "bounded": <bool>,
                             "createdAt": <str>,
                             "description": "Artist Radio",
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
                             "name": <str>
                           },
                           "id": <str>,
                           "type": "providers"
                         },
                         {
                           "attributes": {
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
                         "self": <str>
                       }
                     }
        """
        self._client._validate_tidal_ids(artist_ids)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include is not None:
            params["include"] = self._prepare_include(include)
        if sum(arg is not None for arg in (artist_ids, handles)) != 1:
            raise ValueError(
                "Exactly one of `artist_ids` or `handles` must be provided."
            )
        if artist_ids is not None:
            if isinstance(artist_ids, int | str):
                return self._client._request(
                    "GET", f"artists/{artist_ids}", params=params
                ).json()
            params["filter[id]"] = artist_ids
        elif handles is not None:
            if not isinstance(handles, str):
                for handle in handles:
                    if not isinstance(handle, str):
                        raise ValueError("Artist handles must be strings.")
            params["handle"] = handles
        return self._client._request("GET", "artists", params=params).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_albums(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist's Albums
        <https://tidal-music.github.io/tidal-api-reference/#/artists
        /get_artists__id__relationships_albums>`_: Get TIDAL
        catalog information for an artist's albums.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the artist's albums.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        albums : dict[str, Any]
            TIDAL catalog information for the artist's albums.

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
        return self._get_artist_resource(
            "albums", artist_id, country_code, include=include, cursor=cursor
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_biography(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist's Biography <https://tidal-music.github.io
        /tidal-api-reference/#/artists
        /get_artists__id__relationships_biography>`_: Get TIDAL catalog
        information for an artist's biography.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the artist's biography.

        Returns
        -------
        biography : dict[str, Any]
            TIDAL catalog information for the artist's biography.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": {
                      "id": <str>,
                      "type": "artistBiographies"
                    },
                    "included": [],
                    "links": {
                      "self": <str>
                    }
                  }
        """
        return self._get_artist_resource(
            "biography", artist_id, country_code, include=include
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_owners(
        self,
        artist_id: int | str,
        /,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist's Owners <https://tidal-music.github.io
        /tidal-api-reference/#/artists
        /get_artists__id__relationships_owners>`_: Get TIDAL catalog
        information for an artist's owners.

        .. admonition:: User authentication
           :class: authorization-scope dropdown

           .. tab:: Optional

              User authentication
                 Access information on an item's owners.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the artist's owners.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        owners : dict[str, Any]
            TIDAL catalog information for the artist's owners.

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
        return self._get_artist_resource(
            "owners", artist_id, False, include=include, cursor=cursor
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_profile_art(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist's Profile Art
        <https://tidal-music.github.io/tidal-api-reference/#/artists
        /get_artists__id__relationships_profileArt>`_: Get TIDAL catalog
        information for an artist's profile art.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the artist's profile art.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        profile_art : dict[str, Any]
            TIDAL catalog information for the artist's profile art.

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
        return self._get_artist_resource(
            "profileArt",
            artist_id,
            country_code,
            include=include,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_radio(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist Radio
        <https://tidal-music.github.io/tidal-api-reference/#/artists
        /get_artists__id__relationships_radio>`_: Get TIDAL catalog
        information for radio stations generated from an artist's music
        catalog.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the artist radio.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        radio : dict[str, Any]
            TIDAL catalog information for the artist radio.

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
                          "accessType": "PUBLIC",
                          "bounded": <bool>,
                          "createdAt": <str>,
                          "description": "Artist Radio",
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
        return self._get_artist_resource(
            "radio", artist_id, country_code, include=include, cursor=cursor
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_roles(
        self,
        artist_id: int | str,
        /,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist's Roles
        <https://tidal-music.github.io/tidal-api-reference/#/artists
        /get_artists__id__relationships_artistRoles>`_: Get TIDAL
        catalog information for an artist's roles.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the artist's roles.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        roles : dict[str, Any]
            TIDAL catalog information for the artist's roles.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "type": "artistRoles"
                      }
                    ],
                    "included": [
                      {
                        "attributes": {
                          "name": <str>
                        },
                        "id": <str>,
                        "type": "artistRoles"
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
        return self._get_artist_resource(
            "roles", artist_id, False, include=include, cursor=cursor
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_similar_artists(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Artists > Get Similar Artists
        <https://tidal-music.github.io/tidal-api-reference/#/artists
        /get_artists__id__relationships_similarArtists>`_: Get TIDAL
        catalog information for other artists that are similar to an
        artist.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the similar artists.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        artists : dict[str, Any]
            TIDAL catalog information for the similar artists.

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
        return self._get_artist_resource(
            "similarArtists",
            artist_id,
            country_code,
            include=include,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_track_providers(
        self,
        artist_id: int | str,
        /,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist's Track Providers
        <https://tidal-music.github.io/tidal-api-reference/#/artists
        /get_artists__id__relationships_trackProviders>`_: Get TIDAL
        catalog information for an artist's track providers.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the artist's track providers.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        providers : dict[str, Any]
            TIDAL catalog information for the artist's track providers.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "meta": {
                          "numberOfTracks": <int>
                        },
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
        return self._get_artist_resource(
            "trackProviders", artist_id, False, include=include, cursor=cursor
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_tracks(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        collapse_by: str = "FINGERPRINT",
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist's Tracks
        <https://tidal-music.github.io/tidal-api-reference/#/artists
        /get_artists__id__relationships_tracks>`_: Get TIDAL
        catalog information for an artist's tracks.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        collapse_by : str; keyword-only; default: :code:`"FINGERPRINT"`
            Controls how the returned tracks are grouped.

            **Valid values**:

            .. container::

               * :code:`"FINGERPRINT"` – Collapses tracks that share the
                 same audio fingerprint.
               * :code:`"ID"` – Returns every track as a separate item.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the artist's tracks.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        tracks : dict[str, Any]
            TIDAL catalog information for the artist's tracks.

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
        if collapse_by.upper() not in {"FINGERPRINT", "ID"}:
            raise ValueError(
                f"Cannot group tracks by {collapse_by!r}. "
                "Valid values: 'FINGERPRINT', 'ID'."
            )
        return self._get_artist_resource(
            "tracks",
            artist_id,
            country_code,
            include=include,
            cursor=cursor,
            params={"collapseBy": collapse_by},
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_videos(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Artists > Get Artist's Videos
        <https://tidal-music.github.io/tidal-api-reference/#/artists
        /get_artists__id__relationships_videos>`_: Get TIDAL
        catalog information for an artist's videos.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the artist's videos.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        videos : dict[str, Any]
            TIDAL catalog information for the artist's videos.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "type": "videos"
                      }
                    ],
                    "included": [
                      {
                        "attributes": {
                          "copyright": {
                            "text": <str>
                          },
                          "duration": <str>,
                          "explicit": false,
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
        return self._get_artist_resource(
            "videos", artist_id, country_code, include=include, cursor=cursor
        )

    @_copy_docstring(UsersAPI.get_favorite_artists)
    def get_favorite_artists(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include: bool = False,
        cursor: str | None = None,
        sort: str | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_favorite_artists(
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include=include,
            cursor=cursor,
            sort=sort,
        )

    @_copy_docstring(UsersAPI.favorite_artists)
    def favorite_artists(
        self,
        artist_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        self._client.users.favorite_artists(
            artist_ids, user_id=user_id, country_code=country_code
        )

    @_copy_docstring(UsersAPI.unfavorite_artists)
    def unfavorite_artists(
        self,
        artist_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        self._client.users.unfavorite_artists(
            artist_ids, user_id=user_id, country_code=country_code
        )

    def _get_artist_resource(
        self,
        resource: str,
        artist_id: int | str,
        /,
        country_code: bool | str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a resource related to an
        artist.

        Parameters
        ----------
        resource : str; positional-only
            Related resource type.

            **Valid values**: :code:`"albums"`, :code:`"biography"`,
            :code:`"followers"`, :code:`"following"`, :code:`"owners"`,
            :code:`"profileArt"`, :code:`"radio"`, :code:`"roles"`,
            :code:`"similarArtists"`, :code:`"trackProviders"`,
            :code:`"tracks"`, :code:`"videos"`.

        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : bool or str; optional
            ISO 3166-1 alpha-2 country code. If :code:`False`, the
            country code is not included in the request.

            **Example**: :code:`"US"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the artist's videos.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        params : dict[str, Any]; keyword-only; optional
            Existing dictionary holding URL query parameters. If not
            provided, a new dictionary will be created.

        Returns
        -------
        resource : dict[str, Any]
            TIDAL catalog information for the related resource.
        """
        self._client._validate_tidal_ids(artist_id, _recursive=False)
        if params is None:
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
            f"artists/{artist_id}/relationships/{resource}",
            params=params,
        ).json()
