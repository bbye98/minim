from __future__ import annotations
from typing import TYPE_CHECKING

from ..._shared import TTLCache, _copy_docstring
from ._shared import TIDALResourceAPI
from .search import SearchAPI
from .users import UsersAPI

if TYPE_CHECKING:
    from typing import Any

    from ...._types import Collection


class AlbumsAPI(TIDALResourceAPI):
    """
    Albums API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`~minim.api.tidal.TIDALAPIClient`
       and should not be instantiated directly.
    """

    _RELATIONSHIPS = {
        "albumStatistics",
        "artists",
        "coverArt",
        "genres",
        "items",
        "owners",
        "priceConfig",
        "providers",
        "replacement",
        "shares",
        "similarAlbums",
        "suggestedCoverArts",
        "usageRules",
    }
    _SORT_FIELDS = {"createdAt", "title"}

    @TTLCache.cached_method(ttl="popularity")
    def get_albums(
        self,
        album_ids: int | str | Collection[int | str] | None = None,
        /,
        *,
        barcodes: int | str | Collection[int | str] | None = None,
        owner_ids: int | str | Collection[int | str] | None = None,
        country_code: str | None = None,
        expand: str | Collection[str] | None = None,
        cursor: str | None = None,
        sort_by: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Single Album <https://tidal-music.github.io
        /tidal-api-reference/#/albums/get_albums__id_>`_: Get TIDAL
        catalog information for an album․
        `Albums > Get Multiple Albums <https://tidal-music.github.io
        /tidal-api-reference/#/albums/get_albums>`_: Get TIDAL catalog
        information for multiple albums.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 User authentication
                    Access information on an item's owners.

        .. important::

           Exactly one of `album_ids`, `barcodes`, or `owner_ids` must
           be provided. When `barcodes` or `owner_ids` is specified, the
           request will always be sent to the endpoint for multiple
           albums.

        Parameters
        ----------
        album_ids : int, str, or Collection[int | str]; \
        positional-only; optional
            TIDAL IDs of the albums.

            **Examples**: :code:`46369321`, :code:`"251380836"`,
            :code:`[46369321, "251380836"]`.

        barcodes : int, str, or Collection[int | str]; keyword-only; \
        optional
            Barcodes (UPCs and/or EANs) of the albums.

            **Examples**: :code:`602448438034`, :code:`"075678671173"`,
            :code:`[602448438034, "075678671173"]`

        owner_ids : int, str, or Collection[int | str]; keyword-only; \
        optional
            TIDAL IDs of the albums' owners. If authenticated,
            :code:`"me"` can be used in lieu of a TIDAL ID for the
            current user.

            **Examples**: :code:"me"`, :code:`123456`, :code:`"654321"`,
            :code:`[123456, "654321"]`.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        expand : str or Collection[str]; keyword-only; optional
            Related resources to include metadata for in the response.

            **Valid values**: :code:`"albumStatistics"`,
            :code:`"artists"`, :code:`"coverArt"`, :code:`"genres"`,
            :code:`"items"`, :code:`"owners"`, :code:`"priceConfig"`,
            :code:`"providers"`, :code:`"replacement"`,
            :code:`"shares"`, :code:`"similarAlbums"`,
            :code:`"suggestedCoverArts"`, :code:`"usageRules"`.

            **Examples**: :code:`"coverArt"`,
            :code:`["artists", "items"]`.

        cursor : str; keyword-only; optional
            Cursor for for fetching the next page of results when
            retrieving multiple albums.

            **Example**: :code:`"3nI1Esi"`.

        sort_by : str; keyword-only; optional
            Field to sort the albums by.

            **Valid values**: :code:`"createdAt"`, :code:`"title"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        albums : dict[str, Any]
            TIDAL metadata for the albums.

            .. admonition:: Sample responses
               :class: response dropdown

               .. tab-set::

                  .. tab-item:: Single album

                     .. code-block::

                        {
                          "data": {
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

                  .. tab-item:: Multiple albums

                     .. code-block::

                        {
                          "data": [
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
        if (
            sum(arg is not None for arg in [album_ids, barcodes, owner_ids])
            != 1
        ):
            raise ValueError(
                "Exactly one of `album_ids`, `barcodes`, or "
                "`owner_ids` must be provided."
            )
        params = {}
        if barcodes is not None:
            if isinstance(barcodes, int | str):
                barcodes = self._prepare_barcode(barcodes)
            elif isinstance(barcodes, list | tuple):
                barcodes = [
                    self._prepare_barcode(barcode) for barcode in barcodes
                ]
            else:
                raise ValueError(
                    "`barcodes` must be an integer, a string, or a "
                    "list of integers and/or strings."
                )
            params["filter[barcodeId]"] = barcodes
        elif owner_ids is not None:
            self._validate_tidal_ids(owner_ids)
            params["filter[owners.id]"] = owner_ids
        if sort_by is not None:
            self._process_sort(
                sort_by,
                prefix="",
                sort_fields=self._SORT_FIELDS,
                params=params,
            )
        return self._get_resources(
            "albums",
            album_ids,
            country_code=country_code,
            expand=expand,
            cursor=cursor,
            share_code=share_code,
            params=params,
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_album_artists(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Artists Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_artists>`_: Get TIDAL catalog
        information for the artists of an album.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the album artists.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        artists : dict[str, Any]
            TIDAL metadata for the album artists.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
            "albums",
            album_id,
            "artists",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="static")
    def get_album_cover_art(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Cover Art Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_coverArt>`_: Get TIDAL
        catalog information for the cover art of an album.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the album cover art.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        cover_art : dict[str, Any]
            TIDAL metadata for the album cover art.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
        return self._get_resource_relationship(
            "albums",
            album_id,
            "coverArt",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_album_items(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Items Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_items>`_: Get TIDAL catalog
        information for tracks and videos on an album.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the tracks and videos
            in the album.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        items : dict[str, Any]
            TIDAL metadata for the album's tracks and videos.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
        return self._get_resource_relationship(
            "albums",
            album_id,
            "items",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="static")
    def get_album_owners(
        self,
        album_id: int | str,
        /,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Owners Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_owners>`_: Get TIDAL catalog
        information for owners of an album.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 User authentication
                    Access information on an item's owners.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the album's owners.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        owners : dict[str, Any]
            TIDAL metadata for the album's owners.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
            "albums",
            album_id,
            "owners",
            country_code=None,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="static")
    def get_album_providers(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Providers Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_providers>`_: Get TIDAL catalog
        information for the providers of an album.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the album's providers.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        providers : dict[str, Any]
            TIDAL metadata for the album's providers.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
        return self._get_resource_relationship(
            "albums",
            album_id,
            "providers",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="recommendation")
    def get_similar_albums(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Similar Albums Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_similarAlbums>`_: Get TIDAL
        catalog information for similar albums.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the similar albums.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        albums : dict[str, Any]
            TIDAL metadata for the similar albums.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
            "albums",
            album_id,
            "similarAlbums",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="static")
    def get_album_usage_rules(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Album Usage Rules Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/albums
        /get_albums__id__relationships_usageRules>`_: Get TIDAL
        catalog information for the usage rules for an album.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the album's usage
            rules.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        cover_art : dict[str, Any]
            TIDAL metadata for the album's usage rules.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
            "albums",
            album_id,
            "usageRules",
            country_code=country_code,
            include_metadata=include_metadata,
            share_code=share_code,
        )

    @_copy_docstring(SearchAPI.search_albums)
    def search_albums(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        include_explicit: bool | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return self._client.search.search_albums(
            query,
            country_code=country_code,
            include_explicit=include_explicit,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    # TODO: def get_user_album_collection(self, ...): pass

    @_copy_docstring(UsersAPI.get_user_saved_albums)
    def get_user_saved_albums(
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
        return self._client.users.get_user_saved_albums(
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include_metadata=include_metadata,
            cursor=cursor,
            sort_by=sort_by,
            descending=descending,
        )

    @_copy_docstring(UsersAPI.save_albums)
    def save_albums(
        self,
        album_ids: int
        | str
        | dict[str, int | str]
        | Collection[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        self._client.users.save_albums(
            album_ids, user_id=user_id, country_code=country_code
        )

    @_copy_docstring(UsersAPI.remove_saved_albums)
    def remove_saved_albums(
        self,
        album_ids: int
        | str
        | dict[str, int | str]
        | Collection[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        self._client.users.remove_saved_albums(
            album_ids, user_id=user_id, country_code=country_code
        )
