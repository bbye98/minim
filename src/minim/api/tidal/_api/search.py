from typing import Any

from ..._shared import TTLCache
from ._shared import TIDALResourceAPI


class SearchAPI(TIDALResourceAPI):
    """
    Search Results and Search Suggestions API endpoints for the TIDAL
    API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _RELATIONSHIPS = {
        "albums",
        "artists",
        "playlists",
        "topHits",
        "tracks",
        "videos",
    }

    @TTLCache.cached_method(ttl="search")
    def get_search_suggestions(
        self,
        query: str,
        /,
        *,
        country_code: str | None = None,
        include_explicit: bool | None = None,
        expand: str | list[str] | None = None,
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

        include_explicit : bool; keyword-only; optional
            Whether to include explicit content in the results.

            **API default**: :code:`True`.

        expand : str or list[str]; keyword-only; optional
            Related resources to include metadata for in the response.

            **Valid value**: :code:`"directHits"`.

            **Examples**: :code:`"directHits"`, :code:`["directHits"]`.

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
        self._validate_type("query", query, str)
        query = query.strip()
        if not len(query):
            raise ValueError("No search query provided.")
        return self._get_resources(
            "searchSuggestions",
            query,
            country_code=country_code,
            include_explicit=include_explicit,
            expand=expand,
            resource_identifier_type="query",
        )

    @TTLCache.cached_method(ttl="search")
    def get_search_direct_hits(
        self,
        query: str,
        /,
        *,
        country_code: str | None = None,
        include_explicit: bool | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Search Suggestions > Get Direct Hits
        <https://tidal-music.github.io/tidal-api-reference/#
        /searchSuggestions
        /get_searchSuggestions__id__relationships_directHits>`_: Get
        TIDAL catalog information for direct hits associated with the
        search suggestions.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_explicit : bool; keyword-only; optional
            Whether to include explicit content in the results.

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
        self._validate_type("query", query, str)
        query = query.strip()
        if not len(query):
            raise ValueError("No search query provided.")
        return self._get_resource_relationship(
            "searchSuggestions",
            query,
            "directHits",
            country_code=country_code,
            include_explicit=include_explicit,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="search")
    def search(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        include_explicit: bool | None = None,
        expand: str | list[str] | None = None,
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
            ISO 3166-1 alpha-2 country code. If not specified, it will
            be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include_explicit : bool; keyword-only; optional
            Whether to include explicit content in the results.

            **API default**: :code:`True`.

        expand : str or list[str]; keyword-only; optional
            Related resources to include metadata for in the response.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"playlists"`, :code:`"topHits"`, :code:`"tracks"`,
            :code:`"videos"`.

            **Examples**: :code:`"topHits"`,
           :code:`["albums", "tracks"]`.

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
        self._validate_type("query", query, str)
        query = query.strip()
        if not len(query):
            raise ValueError("No search query provided.")
        return self._get_resources(
            "searchResults",
            query,
            country_code=country_code,
            include_explicit=include_explicit,
            expand=expand,
            resource_identifier_type="query",
        )

    @TTLCache.cached_method(ttl="search")
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
            ISO 3166-1 alpha-2 country code. If not specified, it will
            be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include_explicit : bool; keyword-only; optional
            Whether to include explicit content in the results.

            **API default**: :code:`True`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the matching albums.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        albums : dict[str, Any]
            TIDAL content metadata for the matching albums.

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
        self._validate_type("query", query, str)
        return self._get_resource_relationship(
            "searchResults",
            query,
            "albums",
            country_code=country_code,
            include_explicit=include_explicit,
            include_metadata=include_metadata,
            cursor=cursor,
            resource_identifier_type="query",
        )

    @TTLCache.cached_method(ttl="search")
    def search_artists(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        include_explicit: bool | None = None,
        include_metadata: bool = False,
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
            ISO 3166-1 alpha-2 country code. If not specified, it will
            be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include_explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the matching artists.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        artists : dict[str, Any]
            TIDAL content metadata for the matching artists.

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
        self._validate_type("query", query, str)
        query = query.strip()
        if not len(query):
            raise ValueError("No search query provided.")
        return self._get_resource_relationship(
            "searchResults",
            query,
            "artists",
            country_code=country_code,
            include_explicit=include_explicit,
            include_metadata=include_metadata,
            cursor=cursor,
            resource_identifier_type="query",
        )

    @TTLCache.cached_method(ttl="search")
    def search_playlists(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        include_explicit: bool | None = None,
        include_metadata: bool = False,
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
            ISO 3166-1 alpha-2 country code. If not specified, it will
            be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include_explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the matching playlists.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        playlists : dict[str, Any]
            TIDAL content metadata for the matching playlists.

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
        self._validate_type("query", query, str)
        query = query.strip()
        if not len(query):
            raise ValueError("No search query provided.")
        return self._get_resource_relationship(
            "searchResults",
            query,
            "playlists",
            country_code=country_code,
            include_explicit=include_explicit,
            include_metadata=include_metadata,
            cursor=cursor,
            resource_identifier_type="query",
        )

    @TTLCache.cached_method(ttl="search")
    def search_top_hits(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        include_explicit: bool | None = None,
        include_metadata: bool = False,
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
            ISO 3166-1 alpha-2 country code. If not specified, it will
            be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include_explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the matching top hits.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        top_hits : dict[str, Any]
            TIDAL content metadata for the matching top hits.

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
        self._validate_type("query", query, str)
        query = query.strip()
        if not len(query):
            raise ValueError("No search query provided.")
        return self._get_resource_relationship(
            "searchResults",
            query,
            "topHits",
            country_code=country_code,
            include_explicit=include_explicit,
            include_metadata=include_metadata,
            cursor=cursor,
            resource_identifier_type="query",
        )

    @TTLCache.cached_method(ttl="search")
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
            ISO 3166-1 alpha-2 country code. If not specified, it will
            be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include_explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the matching tracks.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        tracks : dict[str, Any]
            TIDAL content metadata for the matching tracks.

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
        self._validate_type("query", query, str)
        query = query.strip()
        if not len(query):
            raise ValueError("No search query provided.")
        return self._get_resource_relationship(
            "searchResults",
            query,
            "tracks",
            country_code=country_code,
            include_explicit=include_explicit,
            include_metadata=include_metadata,
            cursor=cursor,
            resource_identifier_type="query",
        )

    @TTLCache.cached_method(ttl="search")
    def search_videos(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        include_explicit: bool | None = None,
        include_metadata: bool = False,
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
            ISO 3166-1 alpha-2 country code. If not specified, it will
            be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include_explicit : bool; keyword-only; optional
            Whether to include items with explicit language.

            **API default**: :code:`True`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the matching videos.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        videos : dict[str, Any]
            TIDAL content metadata for the matching videos.

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
        self._validate_type("query", query, str)
        query = query.strip()
        if not len(query):
            raise ValueError("No search query provided.")
        return self._get_resource_relationship(
            "searchResults",
            query,
            "videos",
            country_code=country_code,
            include_explicit=include_explicit,
            include_metadata=include_metadata,
            cursor=cursor,
            resource_identifier_type="query",
        )
