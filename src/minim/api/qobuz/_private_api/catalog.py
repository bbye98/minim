from __future__ import annotations
from typing import TYPE_CHECKING

from ..._shared import TTLCache, _copy_docstring
from ._shared import PrivateQobuzResourceAPI
from .search import PrivateSearchAPI

if TYPE_CHECKING:
    from typing import Any

    from ...._types import Collection


class PrivateCatalogAPI(PrivateQobuzResourceAPI):
    """
    Catalog API endpoints for the private Qobuz API.

    .. important::

       This class is managed by
       :class:`~minim.api.qobuz.PrivateQobuzAPIClient` and should not be
       instantiated directly.
    """

    _FEATURED_TYPES = {"albums", "articles", "artists", "playlists"}

    __slots__ = ()

    @TTLCache.cached_method(ttl="search")
    def get_search_match_counts(
        self, query: str, /
    ) -> dict[str, dict[str, int]]:
        """
        Get the number of Qobuz catalog search results for a query.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        Returns
        -------
        counts : dict[str, dict[str, int]]
            Number of search results for the query.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "albums": {
                      "total": <int>
                    },
                    "artists": {
                      "total": <int>
                    },
                    "tracks": {
                      "total": <int>
                    }
                  }
        """
        return self._client._request(
            "GET",
            "catalog/count",
            params={"query": self._prepare_string("query", query)},
        ).json()

    @TTLCache.cached_method(ttl="daily")
    def get_featured(
        self,
        item_type: str | None = None,
        /,
        genre_ids: int | str | Collection[int | str] | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for featured albums, artists,
        articles, and/or playlists.

        Parameters
        ----------
        item_type : str; positional-only; optional
            Type of item to return. If not specified, featured items of
            all types are returned.

            **Valid values**: :code:`"albums"`, :code:`"articles"`,
            :code:`"artists"`, :code:`"playlists"`.

        genre_ids : int, str, or Collection[int | str]; optional
            Qobuz IDs of the genres used to filter the featured items to
            return.

            **Examples**: :code:`10`, :code:`"64"`, :code:`"10,64"`,
            :code:`[10, "64"]`.

        limit : int; keyword-only; optional
            Maximum number of items to return per item type.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first item to return per item type. Use with
            `limit` to get the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        items : dict[str, Any]
            Page of Qobuz metadata for the featured items.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
                    "playlists": {
                      "items": [
                        {
                          "created_at": <int>,
                          "description": <str>,
                          "duration": <int>,
                          "featured_artists": [],
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
                          "is_collaborative": <bool>,
                          "is_featured": <bool>,
                          "is_public": <bool>,
                          "name": <str>,
                          "owner": {
                            "id": <int>,
                            "name": <str>
                          },
                          "public_at": <int>,
                          "slug": <str>,
                          "stores": <list[str]>,
                          "tags": [
                            {
                              "color": <str>,
                              "featured_tag_id": <str>,
                              "genre_tag": None,
                              "is_discover": <bool>,
                              "name_json": <str>,
                              "slug": <str>
                            }
                          ],
                          "tracks_count": <int>,
                          "updated_at": <int>,
                          "users_count": <int>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    }
                  }
        """
        params = {}
        if item_type is not None:
            item_type = self._prepare_string("item_type", item_type).lower()
            if item_type not in self._FEATURED_TYPES:
                raise ValueError(
                    f"Invalid item type {item_type!r}. Valid values: "
                    f"{self._join_values(self._FEATURED_TYPES)}."
                )
            params["type"] = item_type
        if genre_ids is not None:
            self._validate_type(
                "genre_ids", genre_ids, int | str | tuple | list | set
            )
            if not isinstance(genre_ids, int):
                if isinstance(genre_ids, str):
                    genre_ids = genre_ids.strip().split(",")
                for genre_id in genre_ids:
                    self._client.genres._validate_genre_id(genre_id)
            params["genre_ids"] = self._prepare_qobuz_ids(
                genre_ids, data_type=str
            )
        return self._get_paginated_resources(
            "catalog/getFeatured", limit=limit, offset=offset, params=params
        )

    @_copy_docstring(PrivateSearchAPI.search)
    def search(
        self,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.search.search(query, limit=limit, offset=offset)
