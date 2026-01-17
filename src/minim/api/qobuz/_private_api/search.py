from typing import Any

from ..._shared import TTLCache
from ._shared import PrivateQobuzResourceAPI


class PrivateSearchEndpoints(PrivateQobuzResourceAPI):
    """
    Search-related endpoints for the private Qobuz API.

    .. note::

       This class groups search-related endpoints for convenience.
       Qobuz does not provide a dedicated Search API.

    .. important::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    def _search_resources(
        self,
        resource_type: str,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for albums, artists, playlists,
        or tracks that match a keyword string.

        Parameters
        ----------
        resource_type : str or None; positional-only
            Resource type.

            **Valid values**: :code:`"album"`, :code:`"artist"`,
            :code:`"catalog"`, :code:`"playlist"`, :code:`"story"`,
            :code:`"track"`.

        query : str; positional-only
            Search query.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to
            get the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        results : dict[str, Any]
            Page of Qobuz content metadata for the matching items.
        """
        self._validate_type("query", query, str)
        query = query.strip()
        if not len(query):
            raise ValueError("No search query provided.")
        params = {"query": query}
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"{resource_type}/search", params=params
        ).json()

    @TTLCache.cached_method(ttl="search")
    def search(
        self,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for albums, artists, playlists,
        stories, and/or tracks that match a keyword string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

            .. tip::

               Searches can be narrowed using tags, such as
               :code:`#ByMainArtist`, :code:`#ByComposer`,
               :code:`#ByPerformer`, :code:`#ByReleaseName`,
               :code:`#ByLabel`, :code:`#NewRelease`, and
               :code:`#HiRes`.

               Use strict matching instead of fuzzy search by wrapping
               the keyword string in double quotes.

            **Example**: :code:`"Galantis" #ByMainArtist #HiRes`.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to
            get the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        items : dict[str, Any]
            Page of Qobuz content metadata for the matching items.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albums": {
                      "items": [
                        {
                          "articles": [],
                          "artist": {
                            "albums_count": <int>,
                            "id": <int>,
                            "image": None,
                            "name": <str>,
                            "picture": None,
                            "slug": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "roles": <list[str]>
                            }
                          ],
                          "displayable": <bool>,
                          "downloadable": <bool>,
                          "duration": <int>,
                          "genre": {
                            "color": <str>,
                            "id": <int>,
                            "name": <str>,
                            "path": <list[int]>,
                            "slug": <str>
                          },
                          "hires": <bool>,
                          "hires_streamable": <bool>,
                          "id": <str>,
                          "image": {
                            "back": None,
                            "large": <str>,
                            "small": <str>,
                            "thumbnail": <str>
                          },
                          "label": {
                            "albums_count": <int>,
                            "id": <int>,
                            "name": <str>,
                            "slug": <str>,
                            "supplier_id": <int>
                          },
                          "maximum_bit_depth": <int>,
                          "maximum_channel_count": <int>,
                          "maximum_sampling_rate": <float>,
                          "media_count": <int>,
                          "parental_warning": <bool>,
                          "popularity": <int>,
                          "previewable": <bool>,
                          "purchasable": <bool>,
                          "purchasable_at": <int>,
                          "qobuz_id": <int>,
                          "release_date_download": <str>,
                          "release_date_original": <str>,
                          "release_date_stream": <str>,
                          "released_at": <int>,
                          "sampleable": <bool>,
                          "slug": <str>,
                          "streamable": <bool>,
                          "streamable_at": <int>,
                          "title": <str>,
                          "tracks_count": <int>,
                          "upc": <str>,
                          "url": <str>,
                          "version": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "artists": {
                      "items": [
                        {
                          "albums_count": <int>,
                          "id": <int>,
                          "image": {
                            "extralarge": <str>,
                            "large": <str>,
                            "medium": <str>,
                            "mega": <str>,
                            "small": <str>
                          },
                          "name": <str>,
                          "picture": <str>,
                          "slug": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "most_popular": {
                      "items": [
                        {
                          "content": {
                            "articles": [],
                            "artist": {
                              "albums_count": <int>,
                              "id": <int>,
                              "image": None,
                              "name": <str>,
                              "picture": None,
                              "slug": <str>,
                            },
                            "artists": [
                              {
                                "id": <int>,
                                "name": <str>,
                                "roles": <list[str]>
                              }
                            ],
                            "displayable": <bool>,
                            "downloadable": <bool>,
                            "duration": <int>,
                            "genre": {
                              "color": <str>,
                              "id": <int>,
                              "name": <str>,
                              "path": <list[int]>,
                              "slug": <str>
                            },
                            "hires": <bool>,
                            "hires_streamable": <bool>,
                            "id": <str>,
                            "image": {
                              "back": None,
                              "large": <str>,
                              "small": <str>,
                              "thumbnail": <str>
                            },
                            "label": {
                              "albums_count": <int>,
                              "id": <int>,
                              "name": <str>,
                              "slug": <str>,
                              "supplier_id": <int>
                            },
                            "maximum_bit_depth": <int>,
                            "maximum_channel_count": <int>,
                            "maximum_sampling_rate": <float>,
                            "media_count": <int>,
                            "parental_warning": <bool>,
                            "popularity": <int>,
                            "previewable": <bool>,
                            "purchasable": <bool>,
                            "purchasable_at": <int>,
                            "qobuz_id": <int>,
                            "release_date_download": <str>,
                            "release_date_original": <str>,
                            "release_date_stream": <str>,
                            "released_at": <int>,
                            "sampleable": <bool>,
                            "slug": <str>,
                            "streamable": <bool>,
                            "streamable_at": <int>,
                            "title": <str>,
                            "tracks_count": <int>,
                            "type": <str>,
                            "upc": <str>,
                            "url": <str>,
                            "version": <str>
                          },
                          "type": "albums"
                        },
                        {
                          "content": {
                            "albums_count": <int>,
                            "id": <int>,
                            "image": {
                              "extralarge": <str>,
                              "large": <str>,
                              "medium": <str>,
                              "mega": <str>,
                              "small": <str>
                            },
                            "name": <str>,
                            "picture": <str>,
                            "slug": <str>,
                            "type": "artists"
                          },
                          "type": "artists"
                        },
                        {
                          "content": {
                            "album": {
                              "artist": {
                                "albums_count": <int>,
                                "id": <int>,
                                "image": None,
                                "name": <str>,
                                "picture": None,
                                "slug": <str>
                              },
                              "displayable": <bool>,
                              "downloadable": <bool>,
                              "duration": <int>,
                              "genre": {
                                "id": <int>,
                                "name": <str>,
                                "path": <list[int]>,
                                "slug": <str>
                              },
                              "hires": <bool>,
                              "hires_streamable": <bool>,
                              "id": <str>,
                              "image": {
                                "large": <str>,
                                "small": <str>,
                                "thumbnail": <str>
                              },
                              "label": {
                                "albums_count": <int>,
                                "id": <int>,
                                "name": <str>,
                                "slug": <str>,
                                "supplier_id": <int>
                              },
                              "maximum_bit_depth": <int>,
                              "maximum_channel_count": <int>,
                              "maximum_sampling_rate": <float>,
                              "maximum_technical_specifications": <str>,
                              "media_count": <int>,
                              "parental_warning": <bool>,
                              "previewable": <bool>,
                              "purchasable": <bool>,
                              "purchasable_at": None,
                              "qobuz_id": <int>,
                              "release_date_download": <str>,
                              "release_date_original": <str>,
                              "release_date_purchase": <str>,
                              "release_date_stream": <str>,
                              "released_at": <int>,
                              "sampleable": <bool>,
                              "streamable": <bool>,
                              "streamable_at": <int>,
                              "title": <str>,
                              "tracks_count": <int>,
                              "upc": <str>,
                              "version": <str>
                            },
                            "article_ids": dict[str, int],
                            "articles": [
                              {
                                "currency": <str>,
                                "description": <str>,
                                "id": <int>,
                                "label": <str>,
                                "price": <float>,
                                "type": <str>,
                                "url": <str>
                              }
                            ],
                            "audio_info": {
                              "replaygain_track_gain": <float>,
                              "replaygain_track_peak": <float>
                            },
                            "composer": {
                              "id": <int>,
                              "name": <str>
                            },
                            "copyright": <str>,
                            "displayable": <bool>,
                            "downloadable": <bool>,
                            "duration": <int>,
                            "hires": <bool>,
                            "hires_streamable": <bool>,
                            "id": <int>,
                            "isrc": <str>,
                            "maximum_bit_depth": <int>,
                            "maximum_channel_count": <int>,
                            "maximum_sampling_rate": <float>,
                            "maximum_technical_specifications": <str>,
                            "media_number": <int>,
                            "parental_warning": <bool>,
                            "performer": {
                              "id": <int>,
                              "name": <str>
                            },
                            "performers": <str>,
                            "previewable": <bool>,
                            "purchasable": <bool>,
                            "purchasable_at": <int>,
                            "release_date_download": <str>,
                            "release_date_original": <str>,
                            "release_date_purchase": <str>,
                            "release_date_stream": <str>,
                            "sampleable": <bool>,
                            "streamable": <bool>,
                            "streamable_at": <int>,
                            "title": <str>,
                            "track_number": <int>,
                            "type": "tracks",
                            "version": <str>,
                            "work": None
                          },
                          "type": "tracks"
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "query": <str>,
                    "stories": {
                      "items": [
                        {
                          "authors": [
                            {
                              "id": <str>,
                              "name": <str>,
                              "slug": <str>
                            }
                          ],
                          "description_short": <str>,
                          "display_date": <int>,
                          "id": <str>,
                          "image": <str>,
                          "images": [
                            {
                              "format": <str>,
                              "url": <str>
                            }
                          ],
                          "section_slugs": <list[str]>,
                          "title": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "tracks": {
                      "items": [
                        {
                          "album": {
                            "artist": {
                              "albums_count": <int>,
                              "id": <int>,
                              "image": None,
                              "name": <str>,
                              "picture": None,
                              "slug": <str>
                            },
                            "displayable": <bool>,
                            "downloadable": <bool>,
                            "duration": <int>,
                            "genre": {
                              "color": <int>,
                              "id": <int>,
                              "name": <int>,
                              "path": <list[int]>,
                              "slug": <str>
                            },
                            "hires": <bool>,
                            "hires_streamable": <bool>,
                            "id": <str>,
                            "image": {
                              "large": <str>,
                              "small": <str>,
                              "thumbnail": <str>
                            },
                            "label": {
                              "albums_count": <int>,
                              "id": <int>,
                              "name": <str>,
                              "slug": <str>,
                              "supplier_id": <int>
                            },
                            "maximum_bit_depth": <int>,
                            "maximum_channel_count": <int>,
                            "maximum_sampling_rate": <int>,
                            "maximum_technical_specifications": <str>,
                            "media_count": <int>,
                            "parental_warning": <bool>,
                            "previewable": <bool>,
                            "purchasable": <bool>,
                            "purchasable_at": <int>,
                            "qobuz_id": <int>,
                            "release_date_download": <str>,
                            "release_date_original": <str>,
                            "release_date_purchase": <str>,
                            "release_date_stream": <str>,
                            "released_at": <int>,
                            "sampleable": <bool>,
                            "streamable": <bool>,
                            "streamable_at": <int>,
                            "title": <str>,
                            "tracks_count": <int>,
                            "upc": <str>,
                            "version": <str>
                          },
                          "audio_info": {
                            "replaygain_track_gain": <float>,
                            "replaygain_track_peak": <float>
                          },
                          "copyright": <str>,
                          "displayable": <bool>,
                          "downloadable": <bool>,
                          "duration": <int>,
                          "hires": <bool>,
                          "hires_streamable": <bool>,
                          "id": <int>,
                          "isrc": <str>,
                          "maximum_bit_depth": <int>,
                          "maximum_channel_count": <int>,
                          "maximum_sampling_rate": <float>,
                          "maximum_technical_specifications": <str>,
                          "media_number": <int>,
                          "parental_warning": <bool>,
                          "performer": {
                            "id": <int>,
                            "name": <str>
                          },
                          "performers": <str>,
                          "previewable": <bool>,
                          "purchasable": <bool>,
                          "purchasable_at": <int>,
                          "release_date_download": <str>,
                          "release_date_original": <str>,
                          "release_date_purchase": <str>,
                          "release_date_stream": <str>,
                          "sampleable": <bool>,
                          "streamable": <bool>,
                          "streamable_at": <int>,
                          "title": <str>,
                          "track_number": <int>,
                          "version": <str>,
                          "work": None
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    }
                  }
        """
        return self._search_resources(
            "catalog", query, limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="search")
    def search_albums(
        self,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for albums that match a keyword
        string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

            .. tip::

               Searches can be narrowed using tags, such as
               :code:`#ByMainArtist`, :code:`#ByComposer`,
               :code:`#ByPerformer`, :code:`#ByReleaseName`,
               :code:`#ByLabel`, :code:`#NewRelease`, and
               :code:`#HiRes`.

               Use strict matching instead of fuzzy search by wrapping
               the keyword string in double quotes.

            **Example**: :code:`"Galantis" #ByMainArtist #HiRes`.

        limit : int; keyword-only; optional
            Maximum number of albums to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first album to return. Use with `limit` to
            get the next batch of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        albums : dict[str, Any]
            Page of Qobuz content metadata for the matching albums.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albums": {
                      "items": [
                        {
                          "articles": [],
                          "artist": {
                            "albums_count": <int>,
                            "id": <int>,
                            "image": None,
                            "name": <str>,
                            "picture": None,
                            "slug": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "roles": <list[str]>
                            }
                          ],
                          "displayable": <bool>,
                          "downloadable": <bool>,
                          "duration": <int>,
                          "genre": {
                            "color": <str>,
                            "id": <int>,
                            "name": <str>,
                            "path": <list[int]>,
                            "slug": <str>
                          },
                          "hires": <bool>,
                          "hires_streamable": <bool>,
                          "id": <str>,
                          "image": {
                            "back": None,
                            "large": <str>,
                            "small": <str>,
                            "thumbnail": <str>
                          },
                          "label": {
                            "albums_count": <int>,
                            "id": <int>,
                            "name": <str>,
                            "slug": <str>,
                            "supplier_id": <int>
                          },
                          "maximum_bit_depth": <int>,
                          "maximum_channel_count": <int>,
                          "maximum_sampling_rate": <float>,
                          "media_count": <int>,
                          "parental_warning": <bool>,
                          "popularity": <int>,
                          "previewable": <bool>,
                          "purchasable": <bool>,
                          "purchasable_at": <int>,
                          "qobuz_id": <int>,
                          "release_date_download": <str>,
                          "release_date_original": <str>,
                          "release_date_stream": <str>,
                          "released_at": <int>,
                          "sampleable": <bool>,
                          "slug": <str>,
                          "streamable": <bool>,
                          "streamable_at": <int>,
                          "title": <str>,
                          "tracks_count": <int>,
                          "upc": <str>,
                          "url": <str>,
                          "version": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "query": <str>
                  }
        """
        return self._search_resources(
            "album", query, limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="search")
    def search_artists(
        self,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for artists that match a keyword
        string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

            .. tip::

               Searches can be narrowed using tags, such as
               :code:`#ByMainArtist`, :code:`#ByComposer`,
               :code:`#ByPerformer`, :code:`#ByReleaseName`,
               :code:`#ByLabel`, :code:`#NewRelease`, and
               :code:`#HiRes`.

               Use strict matching instead of fuzzy search by wrapping
               the keyword string in double quotes.

            **Example**: :code:`"Galantis" #ByMainArtist #HiRes`.

        limit : int; keyword-only; optional
            Maximum number of artists to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first artist to return. Use with `limit` to
            get the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        artists : dict[str, Any]
            Page of Qobuz content metadata for the matching artists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "artists": {
                      "items": [
                        {
                          "albums_count": <int>,
                          "id": <int>,
                          "image": {
                            "extralarge": <str>,
                            "large": <str>,
                            "medium": <str>,
                            "mega": <str>,
                            "small": <str>
                          },
                          "name": <str>,
                          "picture": <str>,
                          "slug": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "query": <str>
                  }
        """
        return self._search_resources(
            "artist", query, limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="search")
    def search_most_popular(
        self, query: str, /, *, offset: int | None = None
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for the 30 most popular albums,
        artists, and tracks that match a keyword string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

            .. tip::

               Searches can be narrowed using tags, such as
               :code:`#ByMainArtist`, :code:`#ByComposer`,
               :code:`#ByPerformer`, :code:`#ByReleaseName`,
               :code:`#ByLabel`, :code:`#NewRelease`, and
               :code:`#HiRes`.

               Use strict matching instead of fuzzy search by wrapping
               the keyword string in double quotes.

            **Example**: :code:`"Galantis" #ByMainArtist #HiRes`.

        offset : int; keyword-only; optional
            Index of the first item to return.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        items : dict[str, Any]
            Page of Qobuz content metadata for the most popular items.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "most_popular": {
                      "items": [
                        {
                          "content": {
                            "articles": [],
                            "artist": {
                              "albums_count": <int>,
                              "id": <int>,
                              "image": None,
                              "name": <str>,
                              "picture": None,
                              "slug": <str>,
                            },
                            "artists": [
                              {
                                "id": <int>,
                                "name": <str>,
                                "roles": <list[str]>
                              }
                            ],
                            "displayable": <bool>,
                            "downloadable": <bool>,
                            "duration": <int>,
                            "genre": {
                              "color": <str>,
                              "id": <int>,
                              "name": <str>,
                              "path": <list[int]>,
                              "slug": <str>
                            },
                            "hires": <bool>,
                            "hires_streamable": <bool>,
                            "id": <str>,
                            "image": {
                              "back": None,
                              "large": <str>,
                              "small": <str>,
                              "thumbnail": <str>
                            },
                            "label": {
                              "albums_count": <int>,
                              "id": <int>,
                              "name": <str>,
                              "slug": <str>,
                              "supplier_id": <int>
                            },
                            "maximum_bit_depth": <int>,
                            "maximum_channel_count": <int>,
                            "maximum_sampling_rate": <float>,
                            "media_count": <int>,
                            "parental_warning": <bool>,
                            "popularity": <int>,
                            "previewable": <bool>,
                            "purchasable": <bool>,
                            "purchasable_at": <int>,
                            "qobuz_id": <int>,
                            "release_date_download": <str>,
                            "release_date_original": <str>,
                            "release_date_stream": <str>,
                            "released_at": <int>,
                            "sampleable": <bool>,
                            "slug": <str>,
                            "streamable": <bool>,
                            "streamable_at": <int>,
                            "title": <str>,
                            "tracks_count": <int>,
                            "type": <str>,
                            "upc": <str>,
                            "url": <str>,
                            "version": <str>
                          },
                          "type": "albums"
                        },
                        {
                          "content": {
                            "albums_count": <int>,
                            "id": <int>,
                            "image": {
                              "extralarge": <str>,
                              "large": <str>,
                              "medium": <str>,
                              "mega": <str>,
                              "small": <str>
                            },
                            "name": <str>,
                            "picture": <str>,
                            "slug": <str>,
                            "type": "artists"
                          },
                          "type": "artists"
                        },
                        {
                          "content": {
                            "album": {
                              "artist": {
                                "albums_count": <int>,
                                "id": <int>,
                                "image": None,
                                "name": <str>,
                                "picture": None,
                                "slug": <str>
                              },
                              "displayable": <bool>,
                              "downloadable": <bool>,
                              "duration": <int>,
                              "genre": {
                                "id": <int>,
                                "name": <str>,
                                "path": <list[int]>,
                                "slug": <str>
                              },
                              "hires": <bool>,
                              "hires_streamable": <bool>,
                              "id": <str>,
                              "image": {
                                "large": <str>,
                                "small": <str>,
                                "thumbnail": <str>
                              },
                              "label": {
                                "albums_count": <int>,
                                "id": <int>,
                                "name": <str>,
                                "slug": <str>,
                                "supplier_id": <int>
                              },
                              "maximum_bit_depth": <int>,
                              "maximum_channel_count": <int>,
                              "maximum_sampling_rate": <float>,
                              "maximum_technical_specifications": <str>,
                              "media_count": <int>,
                              "parental_warning": <bool>,
                              "previewable": <bool>,
                              "purchasable": <bool>,
                              "purchasable_at": None,
                              "qobuz_id": <int>,
                              "release_date_download": <str>,
                              "release_date_original": <str>,
                              "release_date_purchase": <str>,
                              "release_date_stream": <str>,
                              "released_at": <int>,
                              "sampleable": <bool>,
                              "streamable": <bool>,
                              "streamable_at": <int>,
                              "title": <str>,
                              "tracks_count": <int>,
                              "upc": <str>,
                              "version": <str>
                            },
                            "article_ids": dict[str, int],
                            "articles": [
                              {
                                "currency": <str>,
                                "description": <str>,
                                "id": <int>,
                                "label": <str>,
                                "price": <float>,
                                "type": <str>,
                                "url": <str>
                              }
                            ],
                            "audio_info": {
                              "replaygain_track_gain": <float>,
                              "replaygain_track_peak": <float>
                            },
                            "composer": {
                              "id": <int>,
                              "name": <str>
                            },
                            "copyright": <str>,
                            "displayable": <bool>,
                            "downloadable": <bool>,
                            "duration": <int>,
                            "hires": <bool>,
                            "hires_streamable": <bool>,
                            "id": <int>,
                            "isrc": <str>,
                            "maximum_bit_depth": <int>,
                            "maximum_channel_count": <int>,
                            "maximum_sampling_rate": <float>,
                            "maximum_technical_specifications": <str>,
                            "media_number": <int>,
                            "parental_warning": <bool>,
                            "performer": {
                              "id": <int>,
                              "name": <str>
                            },
                            "performers": <str>,
                            "previewable": <bool>,
                            "purchasable": <bool>,
                            "purchasable_at": <int>,
                            "release_date_download": <str>,
                            "release_date_original": <str>,
                            "release_date_purchase": <str>,
                            "release_date_stream": <str>,
                            "sampleable": <bool>,
                            "streamable": <bool>,
                            "streamable_at": <int>,
                            "title": <str>,
                            "track_number": <int>,
                            "type": "tracks",
                            "version": <str>,
                            "work": None
                          },
                          "type": "tracks"
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "query": <str>
                  }
        """
        self._validate_type("query", query, str)
        params = {"query": query.strip()}
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "most-popular/get", params=params
        ).json()

    @TTLCache.cached_method(ttl="search")
    def search_playlists(
        self,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for playlists that match a keyword
        string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

            .. tip::

               Searches can be narrowed using tags, such as
               :code:`#ByMainArtist`, :code:`#ByComposer`,
               :code:`#ByPerformer`, :code:`#ByReleaseName`,
               :code:`#ByLabel`, :code:`#NewRelease`, and
               :code:`#HiRes`.

               Use strict matching instead of fuzzy search by wrapping
               the keyword string in double quotes.

            **Example**: :code:`"Galantis" #ByMainArtist #HiRes`.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of Qobuz content metadata for the matching playlists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "playlists": {
                      "items": [
                        {
                          "created_at": <int>,
                          "description": <str>,
                          "duration": <int>,
                          "featured_artists": [
                            {
                              "albums_count": <int>,
                              "id": <int>,
                              "image": None,
                              "name": <str>,
                              "picture": None,
                              "slug": <str>
                            }
                          ],
                          "genres": [
                            {
                              "color": <str>,
                              "id": <int>,
                              "name": <str>,
                              "path": <list[int]>,
                              "percent": <int>,
                              "slug": <str>
                            }
                          ],
                          "id": <int>,
                          "image_rectangle": <list[str]>,
                          "image_rectangle_mini": <list[str]>,
                          "images": <list[str]>,
                          "images150": <list[str]>,
                          "images300": <list[str]>,
                          "indexed_at": <int>,
                          "is_collaborative": <bool>,
                          "is_featured": <bool>,
                          "is_public": <bool>,
                          "is_published": <bool>,
                          "name": <str>,
                          "owner": {
                            "id": <int>,
                            "name": <str>
                          },
                          "public_at": <int>,
                          "published_from": <int>,
                          "published_to": <int>,
                          "slug": <str>,
                          "stores": <list[str]>,
                          "tags": [
                            {
                              "color": <str>,
                              "featured_tag_id": <str>,
                              "genre_tag": {
                                "genre_id": <str>,
                                "name": <str>
                              },
                              "is_discover": <bool>,
                              "name_json": <str>,
                              "slug": <str>
                            }
                          ],
                          "timestamp_position": <int>,
                          "tracks_count": <int>,
                          "updated_at": <int>,
                          "users_count": <int>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "query": <str>
                  }
        """
        return self._search_resources(
            "playlist", query, limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="search")
    def search_stories(
        self,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for stories that match a keyword
        string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

            .. tip::

               Searches can be narrowed using tags, such as
               :code:`#ByMainArtist`, :code:`#ByComposer`,
               :code:`#ByPerformer`, :code:`#ByReleaseName`,
               :code:`#ByLabel`, :code:`#NewRelease`, and
               :code:`#HiRes`.

               Use strict matching instead of fuzzy search by wrapping
               the keyword string in double quotes.

            **Example**: :code:`"Galantis" #ByMainArtist #HiRes`.

        limit : int; keyword-only; optional
            Maximum number of stories to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first story to return. Use with `limit` to
            get the next batch of stories.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        stories : dict[str, Any]
            Page of Qobuz content metadata for the matching stories.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "query": <str>,
                    "stories": {
                      "items": [
                        {
                          "authors": [
                            {
                              "id": <str>,
                              "name": <str>,
                              "slug": <str>
                            }
                          ],
                          "description_short": <str>,
                          "display_date": <int>,
                          "id": <str>,
                          "image": <str>,
                          "images": [
                            {
                              "format": <str>,
                              "url": <str>
                            }
                          ],
                          "section_slugs": <list[str]>,
                          "title": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    }
                  }
        """
        return self._search_resources(
            "story", query, limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="search")
    def search_tracks(
        self,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for tracks that match a keyword
        string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

            .. tip::

               Searches can be narrowed using tags, such as
               :code:`#ByMainArtist`, :code:`#ByComposer`,
               :code:`#ByPerformer`, :code:`#ByReleaseName`,
               :code:`#ByLabel`, :code:`#NewRelease`, and
               :code:`#HiRes`.

               Use strict matching instead of fuzzy search by wrapping
               the keyword string in double quotes.

            **Example**: :code:`"Galantis" #ByMainArtist #HiRes`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to
            get the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of Qobuz content metadata for the matching tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "query": <str>,
                    "tracks": {
                      "items": [
                        {
                          "album": {
                            "artist": {
                              "albums_count": <int>,
                              "id": <int>,
                              "image": None,
                              "name": <str>,
                              "picture": None,
                              "slug": <str>
                            },
                            "displayable": <bool>,
                            "downloadable": <bool>,
                            "duration": <int>,
                            "genre": {
                              "color": <int>,
                              "id": <int>,
                              "name": <int>,
                              "path": <list[int]>,
                              "slug": <str>
                            },
                            "hires": <bool>,
                            "hires_streamable": <bool>,
                            "id": <str>,
                            "image": {
                              "large": <str>,
                              "small": <str>,
                              "thumbnail": <str>
                            },
                            "label": {
                              "albums_count": <int>,
                              "id": <int>,
                              "name": <str>,
                              "slug": <str>,
                              "supplier_id": <int>
                            },
                            "maximum_bit_depth": <int>,
                            "maximum_channel_count": <int>,
                            "maximum_sampling_rate": <int>,
                            "maximum_technical_specifications": <str>,
                            "media_count": <int>,
                            "parental_warning": <bool>,
                            "previewable": <bool>,
                            "purchasable": <bool>,
                            "purchasable_at": <int>,
                            "qobuz_id": <int>,
                            "release_date_download": <str>,
                            "release_date_original": <str>,
                            "release_date_purchase": <str>,
                            "release_date_stream": <str>,
                            "released_at": <int>,
                            "sampleable": <bool>,
                            "streamable": <bool>,
                            "streamable_at": <int>,
                            "title": <str>,
                            "tracks_count": <int>,
                            "upc": <str>,
                            "version": <str>
                          },
                          "audio_info": {
                            "replaygain_track_gain": <float>,
                            "replaygain_track_peak": <float>
                          },
                          "copyright": <str>,
                          "displayable": <bool>,
                          "downloadable": <bool>,
                          "duration": <int>,
                          "hires": <bool>,
                          "hires_streamable": <bool>,
                          "id": <int>,
                          "isrc": <str>,
                          "maximum_bit_depth": <int>,
                          "maximum_channel_count": <int>,
                          "maximum_sampling_rate": <float>,
                          "maximum_technical_specifications": <str>,
                          "media_number": <int>,
                          "parental_warning": <bool>,
                          "performer": {
                            "id": <int>,
                            "name": <str>
                          },
                          "performers": <str>,
                          "previewable": <bool>,
                          "purchasable": <bool>,
                          "purchasable_at": <int>,
                          "release_date_download": <str>,
                          "release_date_original": <str>,
                          "release_date_purchase": <str>,
                          "release_date_stream": <str>,
                          "sampleable": <bool>,
                          "streamable": <bool>,
                          "streamable_at": <int>,
                          "title": <str>,
                          "track_number": <int>,
                          "version": <str>,
                          "work": None
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    }
                  }
        """
        return self._search_resources(
            "track", query, limit=limit, offset=offset
        )
