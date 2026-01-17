from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import PrivateQobuzResourceAPI
from .search import PrivateSearchEndpoints


class PrivateAlbumsAPI(PrivateQobuzResourceAPI):
    """
    Albums API endpoints for the private Qobuz API.

    .. important::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    _FEATURED_TYPES = {
        "most-streamed",
        "best-sellers",
        "new-releases",
        "press-awards",
        "editors-picks",
        "most-featured",
        "harmonia-mundi",
        "universal-classic",
        "universal-jazz",
        "universal-jeunesse",
        "universal-chanson",
        "new-releases-full",
        "recent-releases",
        "ideal-discography",
        "qobuzissims",
        "album-of-the-week",
        "re-release-of-the-week",
    }
    _RELATIONSHIPS = {"albumsFromSameArtist", "focus", "focusAll"}

    def get_album(
        self,
        album_id: str,
        /,
        *,
        expand: str | list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for an album.

        Parameters
        ----------
        album_id : str; positional-only
            Qobuz ID of the album.

            **Examples**: :code:`"0075679933652"`,
            :code:`"aaxy9wirwgn2a"`.

        expand : str or list[str]; keyword-only; optional
            Related resources to include metadata for in the response.

            **Valid values**: :code:`"albumsFromSameArtist"`,
            :code:`"focus"`, :code:`"focusAll"`.

            **Examples**: :code:`"albumsFromSameArtist"`,
            :code:`"focus,focusAll"`, :code:`["focus", "focusAll"]`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`500`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        album : dict[str, Any]
            Qobuz content metadata for the album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albums_same_artist": {
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
                          "description": [],
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
                      ]
                    },
                    "area": None,
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
                    "awards": [],
                    "catchline": <str>,
                    "copyright": <str>,
                    "created_at": <int>,
                    "description": <str>,
                    "description_language": <str>,
                    "displayable": <bool>,
                    "downloadable": <bool>,
                    "duration": <int>,
                    "genre": {
                      "color": <str>,
                      "id": <int>,
                      "name": <str>",
                      "path": <list[int]>,
                      "slug": <str>
                    },
                    "genres_list": <list[str]>,
                    "goodies": [],
                    "hires": <bool>,
                    "hires_streamable": <bool>,
                    "id": <str>,
                    "image": {
                      "back": None,
                      "large": <str>,
                      "small": <str>,
                      "thumbnail": <str>
                    },
                    "is_official": <bool>,
                    "items_focus": None,
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
                    "period": None,
                    "popularity": <int>,
                    "previewable": <bool>,
                    "product_sales_factors_monthly": <int>,
                    "product_sales_factors_weekly": <int>,
                    "product_sales_factors_yearly": <int>,
                    "product_type": <str>,
                    "product_url": <str>,
                    "purchasable": <bool>,
                    "purchasable_at": <int>,
                    "qobuz_id": <int>,
                    "recording_information": <str>,
                    "relative_url": <str>,
                    "release_date_download": <str>,
                    "release_date_original": <str>,
                    "release_date_stream": <str>,
                    "release_tags": [],
                    "release_type": <str>,
                    "released_at": <int>,
                    "sampleable": <bool>,
                    "slug": <str>,
                    "streamable": <bool>,
                    "streamable_at": <int>,
                    "subtitle": <str>,
                    "title": <str>,
                    "tracks": {
                      "items": [
                        {
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
                          "maximum_sampling_rate": <int>,
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
                    },
                    "tracks_count": <int>,
                    "upc": <str>,
                    "url": <str>,
                    "version": <str>
                  }
        """
        self._validate_album_id(album_id)
        params = {"album_id": album_id}
        if expand is not None:
            params["extra"] = self._prepare_expand(expand)
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request("GET", "album/get", params=params).json()

    @TTLCache.cached_method(ttl="popularity")
    def get_featured_albums(
        self,
        featured_type: str,
        *,
        genre_ids: int | str | list[int | str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for featured albums.

        Parameters
        ----------
        featured_type : str; positional-only
            Type of featured albums to return.

            **Valid values**: :code:`"most-streamed"`,
            :code:`"best-sellers"`, :code:`"new-releases"`,
            :code:`"press-awards"`, :code:`"editors-picks"`,
            :code:`"most-featured"`, :code:`"harmonia-mundi"`,
            :code:`"universal-classic"`, :code:`"universal-jazz"`,
            :code:`"universal-jeunesse"`, :code:`"universal-chanson"`,
            :code:`"new-releases-full"`, :code:`"recent-releases"`,
            :code:`"ideal-discography"`, :code:`"qobuzissims"`,
            :code:`"album-of-the-week"`,
            :code:`"re-release-of-the-week"`.

        genre_ids : int, str, or list[int | str]; optional
            Qobuz IDs of the genres used to filter the featured albums
            to return.

            **Examples**: :code:`10`, :code:`"64"`, :code:`"10,64"`,
            :code:`[10, "64"]`.

        limit : int; keyword-only; optional
            Maximum number of albums to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first album to return. Use with `limit` to get
            the next batch of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        albums : dict[str, Any]
            Page of Qobuz content metadata for the featured albums.

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
                    }
                  }
        """
        featured_type = featured_type.strip().lower()
        if featured_type not in self._FEATURED_TYPES:
            featured_types_str = "', '".join(sorted(self._FEATURED_TYPES))
            raise ValueError(
                f"Invalid featured_type {featured_type!r}. "
                f"Valid values: '{featured_types_str!r}'."
            )
        params = {"type": featured_type}
        if genre_ids is not None:
            self._validate_type(
                "genre_ids", genre_ids, int | str | tuple | list | set
            )
            if not isinstance(genre_ids, int):
                if isinstance(genre_ids, str):
                    genre_ids = genre_ids.strip().split(",")
                for genre_id in genre_ids:
                    self._client.genres._validate_genre_id(genre_id)
            genre_ids = self._prepare_qobuz_ids(genre_ids, data_type=str)
            params[f"genre_id{'s' if ',' in genre_ids else ''}"] = genre_ids
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "album/getFeatured", params=params
        ).json()

    def save_albums(
        self, album_ids: str | list[str] | None = None, /
    ) -> dict[str, str]:
        """
        Save one or more albums to the current user's favorites.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        album_ids : str or list[str]; positional-only; optional
            Qobuz IDs of the albums.

            **Examples**: :code:`"0075679933652"`,
            :code:`"0075679933652,aaxy9wirwgn2a"`.

        Returns
        -------
        response : dict[str, str]
            API JSON response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        return self._client.favorites.save(album_ids=album_ids)

    def remove_saved_albums(
        self, album_ids: str | list[str] | None = None, /
    ) -> dict[str, str]:
        """
        Remove one or more albums from the current user's favorites.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        album_ids : str or list[str]; positional-only; optional
            Qobuz IDs of the albums.

            **Examples**: :code:`"0075679933652"`,
            :code:`"0075679933652,aaxy9wirwgn2a"`.

        Returns
        -------
        response : dict[str, str]
            API JSON response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        return self._client.favorites.remove_saved(album_ids=album_ids)

    def get_my_saved_albums(
        self,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get the current user's saved albums.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        limit : int; keyword-only; optional
            Maximum number of artists to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first artist to return. Use with `limit` to get
            the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        albums : dict[str, Any]
            Page of Qobuz content metadata for albums in the user's
            favorites.

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
                          "favorited_at": <int>,
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
                            "thumbnail": <str>,
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
                    "user": {
                      "id": <int>,
                      "login": <str>
                    }
                  }
        """
        return self._client.favorites.get_my_saved(
            "albums", limit=limit, offset=offset
        )

    def is_album_saved(self, album_id: str, /) -> dict[str, bool]:
        """
        Check whether an album is in the current user's favorites.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        album_id : str; positional-only
            Qobuz ID of the album.

            **Examples**: :code:`"0075679933652"`,
            :code:`"aaxy9wirwgn2a"`.

        Returns
        -------
        saved : dict[str, bool]
            Whether the current user has the specified album in their
            favorites.

            **Sample response**: :code:`{"status": <bool>}`.
        """
        return self._client.favorites.is_saved("album", album_id)

    def toggle_album_saved(self, album_id: str, /) -> dict[str, str]:
        """
        Toggle the saved status of an album.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        album_id : str; positional-only
            Qobuz ID of the album.

            **Examples**: :code:`"0075679933652"`,
            :code:`"aaxy9wirwgn2a"`.

        Returns
        -------
        saved : dict[str, bool]
            Whether the current user has the specified album in their
            favorites.

            **Sample response**: :code:`{"status": <bool>}`.
        """
        return self._client.favorites.toggle_saved("album", album_id)

    @_copy_docstring(PrivateSearchEndpoints.search_albums)
    def search_albums(
        self,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.search.search_albums(
            query, limit=limit, offset=offset
        )
