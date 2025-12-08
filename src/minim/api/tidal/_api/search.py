from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache
from ._shared import TIDALResourceAPI

if TYPE_CHECKING:
    from .. import TIDALAPI


class SearchAPI(TIDALResourceAPI):
    """
    Search Results and Search Suggestions API endpoints for the TIDAL
    API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _RESOURCES = {
        "albums",
        "artists",
        "playlists",
        "topHits",
        "tracks",
        "videos",
    }
    _client: "TIDALAPI"

    @TTLCache.cached_method(ttl="search")
    def get_suggestions(
        self,
        query: str,
        /,
        *,
        country_code: str | None = None,
        explicit: bool | None = None,
        include: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """
        `Search Suggestions > Get Search Suggestions
        <https://tidal-music.github.io/tidal-api-reference/#
        /searchSuggestions/get_searchSuggestions__id_>`_: Get TIDAL
        catalog information for search suggestions for a keyword string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include : str or list[str]; keyword-only; optional
            Related resources to include in the response.

            **Valid value**: :code:`"directHits"`.

        Returns
        -------
        search_suggestions : dict[str, Any]
            Search suggestions and associated TIDAL content metadata.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": {
                      "attributes": {
                        "history": <list[str]>,
                        "suggestions": [
                          {
                            "highlights": [
                              {
                                "length": <int>,
                                "start": <int>
                              }
                            ],
                            "query": <str>
                          }
                        ],
                        "trackingId": <str>
                      },
                      "id": <str>,
                      "relationships": {
                        "directHits": {
                          "data": [
                            {
                              "id": <str>,
                              "type": "albums"
                            },
                            {
                              "id": <str>,
                              "type": "artists"
                            },
                            {
                              "id": <str>,
                              "type": "playlists"
                            },
                            {
                              "id": <str>,
                              "type": "tracks"
                            },
                            {
                              "id": <str>,
                              "type": "videos"
                            }
                          ],
                          "links": {
                            "self": <str>
                          }
                        }
                      },
                      "type": "searchSuggestions"
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
                          "duration": <str>,
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
                          "numberOfItems": <int>,
                          "playlistType": <str>
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
                          "isrc":<str>,
                          "popularity": <float>,
                          "releaseDate": <str>,
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
        self._client._validate_type("query", query, str)
        params = {}
        if country_code is not None:
            self._client._validate_country_code(country_code)
            params["countryCode"] = country_code
        if explicit is not None:
            self._client._validate_type("explicit", explicit, bool)
            params["explicitFilter"] = "INCLUDE" if explicit else "EXCLUDE"
        if include is not None:
            params["include"] = self._prepare_include(
                include, resources={"directHits"}
            )
        return self._client._request(
            "GET", f"searchSuggestions/{query}", params=params
        ).json()

    @TTLCache.cached_method(ttl="search")
    def get_direct_hits(
        self,
        query: str,
        /,
        *,
        country_code: str | None = None,
        explicit: bool | None = None,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Search Suggestions > Get Direct Hits
        <https://tidal-music.github.io/tidal-api-reference/#
        /searchSuggestions/get_searchSuggestions__id_>`_: Get TIDAL
        catalog information for direct hits associated with the search
        suggestions.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the direct hits.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        direct_hits : dict[str, Any]
            TIDAL content metadata for the direct hits.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "type": "albums"
                      },
                      {
                        "id": <str>,
                        "type": "artists"
                      },
                      {
                        "id": <str>,
                        "type": "playlists"
                      },
                      {
                        "id": <str>,
                        "type": "tracks"
                      },
                      {
                        "id": <str>,
                        "type": "videos"
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
                          "duration": <str>,
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
                          "numberOfItems": <int>,
                          "playlistType": <str>
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
                          "isrc":<str>,
                          "popularity": <float>,
                          "releaseDate": <str>,
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
        self._client._validate_type("query", query, str)
        params = {}
        if country_code is not None:
            self._client._validate_country_code(country_code)
            params["countryCode"] = country_code
        if explicit is not None:
            self._client._validate_type("explicit", explicit, bool)
            params["explicitFilter"] = "INCLUDE" if explicit else "EXCLUDE"
        if include is not None:
            self._client._validate_type("include", include, bool)
            params["include"] = "directHits"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["page[cursor]"] = cursor
        return self._client._request(
            "GET",
            f"searchSuggestions/{query}/relationships/directHits",
            params=params,
        ).json()

    @TTLCache.cached_method(ttl="search")
    def search(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        explicit: bool | None = None,
        include: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """
        `Search Results > Search <https://tidal-music.github.io
        /tidal-api-reference/#/searchResults/get_searchResults__id_>`_:
        Get TIDAL catalog information for albums, artists, playlists,
        tracks, and videos that match a keyword string.

        .. admonition:: Authorization scope
           :class: authorization-scope dropdown

           .. tab:: Optional

              :code:`search.read` scope
                 Read personalized search results.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include : str or list[str]; keyword-only; optional
            Related resources to include in the response.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"playlists"`, :code:`"topHits"`, :code:`"tracks"`,
            :code:`"videos"`.

        Returns
        -------
        results : dict[str, Any]
            Search results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": {
                      "attributes": {
                        "trackingId": <str>
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
                        "artists": {
                          "data": [
                            {
                              "id": <str>,
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
                        },
                        "playlists": {
                          "data": [
                            {
                              "id": <str>,
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
                        },
                        "topHits": {
                          "data": [
                            {
                              "id": <str>,
                              "type": "albums"
                            },
                            {
                              "id": <str>,
                              "type": "artists"
                            },
                            {
                              "id": <str>,
                              "type": "playlists"
                            },
                            {
                              "id": <str>,
                              "type": "tracks"
                            },
                            {
                              "id": <str>,
                              "type": "videos"
                            }
                          ],
                          "links": {
                            "self": <str>
                          }
                        },
                        "tracks": {
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
                        "videos": {
                          "data": [
                            {
                              "id": <str>,
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
                      },
                      "type": "searchResults"
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
                          "mediaTags": [],
                          "numberOfItems": <int>,
                          "numberOfVolumes": <int>,
                          "popularity": <float>,
                          "releaseDate": <str>,
                          "title": <str>,
                          "type": <str>
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
                          "bounded": true,
                          "createdAt": <str>,
                          "description": <str>,
                          "duration": <str>,
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
                          "numberOfItems": <int>,
                          "playlistType": <str>
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
                          "isrc":<str>,
                          "popularity": <float>,
                          "releaseDate": <str>,
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
        self._client._validate_type("query", query, str)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if explicit is not None:
            self._client._validate_type("explicit", explicit, bool)
            params["explicitFilter"] = "INCLUDE" if explicit else "EXCLUDE"
        if include is not None:
            params["include"] = self._prepare_include(include)
        return self._client._request(
            "GET", f"searchResults/{query}", params=params
        ).json()

    def search_albums(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        explicit: bool | None = None,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Search Results > Search Albums <https://tidal-music.github.io
        /tidal-api-reference/#/searchResults
        /get_searchResults__id__relationships_albums>`_:
        Get TIDAL catalog information for albums that match a keyword
        string.

        .. admonition:: Authorization scope
           :class: authorization-scope dropdown

           .. tab:: Optional

              :code:`search.read` scope
                 Read personalized search results.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the matching albums.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        albums : dict[str, Any]
            TIDAL catalog information for the matching albums.

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
        return self._search_resource(
            "albums",
            query,
            country_code,
            explicit=explicit,
            include=include,
            cursor=cursor,
        )

    def search_artists(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        explicit: bool | None = None,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Search Results > Search Artists <https://tidal-music.github.io
        /tidal-api-reference/#/searchResults
        /get_searchResults__id__relationships_artists>`_:
        Get TIDAL catalog information for artists that match a keyword
        string.

        .. admonition:: Authorization scope
           :class: authorization-scope dropdown

           .. tab:: Optional

              :code:`search.read` scope
                 Read personalized search results.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the matching artists.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        artists : dict[str, Any]
            TIDAL catalog information for the matching artists.

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
        return self._search_resource(
            "artists",
            query,
            country_code,
            explicit=explicit,
            include=include,
            cursor=cursor,
        )

    def search_playlists(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        explicit: bool | None = None,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Search Results > Search Playlists
        <https://tidal-music.github.io/tidal-api-reference/#
        /searchResults
        /get_searchResults__id__relationships_playlists>`_: Get TIDAL
        catalog information for playlists that match a keyword string.

        .. admonition:: Authorization scope
           :class: authorization-scope dropdown

           .. tab:: Optional

              :code:`search.read` scope
                 Read personalized search results.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the matching playlists.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        playlists : dict[str, Any]
            TIDAL catalog information for the matching playlists.

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
                    },
                    "included": [
                      {
                        "attributes": {
                          "accessType": <str>,
                          "bounded": true,
                          "createdAt": <str>,
                          "description": <str>,
                          "duration": <str>,
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
                          "numberOfItems": <int>,
                          "playlistType": <str>
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
        return self._search_resource(
            "playlists",
            query,
            country_code,
            explicit=explicit,
            include=include,
            cursor=cursor,
        )

    def search_top_hits(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        explicit: bool | None = None,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Search Results > Search Top Hits <https://tidal-music.github.io
        /tidal-api-reference/#/searchResults
        /get_searchResults__id__relationships_topHits>`_:
        Get TIDAL catalog information for top hits that match a keyword
        string.

        .. admonition:: Authorization scope
           :class: authorization-scope dropdown

           .. tab:: Optional

              :code:`search.read` scope
                 Read personalized search results.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the matching top hits.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        top_hits : dict[str, Any]
            TIDAL catalog information for the matching top hits.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "type": "albums"
                      },
                      {
                        "id": <str>,
                        "type": "artists"
                      },
                      {
                        "id": <str>,
                        "type": "playlists"
                      },
                      {
                        "id": <str>,
                        "type": "tracks"
                      },
                      {
                        "id": <str>,
                        "type": "videos"
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
                          "mediaTags": [],
                          "numberOfItems": <int>,
                          "numberOfVolumes": <int>,
                          "popularity": <float>,
                          "releaseDate": <str>,
                          "title": <str>,
                          "type": <str>
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
                          "bounded": true,
                          "createdAt": <str>,
                          "description": <str>,
                          "duration": <str>,
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
                          "numberOfItems": <int>,
                          "playlistType": <str>
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
                          "isrc":<str>,
                          "popularity": <float>,
                          "releaseDate": <str>,
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
        return self._search_resource(
            "topHits",
            query,
            country_code,
            explicit=explicit,
            include=include,
            cursor=cursor,
        )

    def search_tracks(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        explicit: bool | None = None,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Search Results > Search Tracks <https://tidal-music.github.io
        /tidal-api-reference/#/searchResults
        /get_searchResults__id__relationships_tracks>`_:
        Get TIDAL catalog information for tracks that match a keyword
        string.

        .. admonition:: Authorization scope
           :class: authorization-scope dropdown

           .. tab:: Optional

              :code:`search.read` scope
                 Read personalized search results.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the matching tracks.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        tracks : dict[str, Any]
            TIDAL catalog information for the matching tracks.

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
        return self._search_resource(
            "tracks",
            query,
            country_code,
            explicit=explicit,
            include=include,
            cursor=cursor,
        )

    def search_videos(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        explicit: bool | None = None,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Search Results > Search Videos <https://tidal-music.github.io
        /tidal-api-reference/#/searchResults
        /get_searchResults__id__relationships_videos>`_:
        Get TIDAL catalog information for videos that match a keyword
        string.

        .. admonition:: Authorization scope
           :class: authorization-scope dropdown

           .. tab:: Optional

              :code:`search.read` scope
                 Read personalized search results.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the matching videos.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        videos : dict[str, Any]
            TIDAL catalog information for the matching videos.

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
                          "isrc":<str>,
                          "popularity": <float>,
                          "releaseDate": <str>,
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
        return self._search_resource(
            "videos",
            query,
            country_code,
            explicit=explicit,
            include=include,
            cursor=cursor,
        )

    def _search_resource(
        self,
        resource: str,
        query: str,
        /,
        country_code: str | None = None,
        *,
        explicit: bool | None = None,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a resource that match a
        keyword string.

        Parameters
        ----------
        resource : str; positional-only
            Related resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"playlists"`, :code:`"topHits"`, :code:`"tracks"`,
            :code:`"videos"`.

        query : str; positional-only
            Search query.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the resource.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        resource : dict[str, Any]
            TIDAL catalog information for the resource.
        """
        self._client._validate_type("query", query, str)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if explicit is not None:
            self._client._validate_type("explicit", explicit, bool)
            params["explicitFilter"] = "INCLUDE" if explicit else "EXCLUDE"
        if include is not None:
            self._client._validate_type("include", include, bool)
            if include:
                params["include"] = resource
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["page[cursor]"] = cursor
        return self._client._request(
            "GET",
            f"searchResults/{query}/relationships/{resource}",
            params=params,
        ).json()
