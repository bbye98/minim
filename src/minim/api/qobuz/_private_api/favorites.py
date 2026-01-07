from typing import Any

from ..._shared import TTLCache
from ._shared import PrivateQobuzResourceAPI


class PrivateFavoritesAPI(PrivateQobuzResourceAPI):
    """
    Favorites API endpoints for the private Qobuz Web API.

    .. note::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    _FAVORITE_TYPES = {
        "albums",
        "artists",
        "articles",
        "awards",
        "labels",
        "tracks",
    }

    def save(
        self,
        *,
        album_ids: str | list[str] | None = None,
        artist_ids: int | str | list[int | str] | None = None,
        track_ids: int | str | list[int | str] | None = None,
    ) -> dict[str, str]:
        """
        Save one or more albums, artists, and/or tracks to the current
        user's favorites.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        album_ids : str or list[str]; keyword-only; optional
            Qobuz IDs of the albums.

            **Examples**: :code:`"0075679933652"`,
            :code:`"0075679933652,aaxy9wirwgn2a"`.

        artist_ids : int, str, or list[int | str]; keyword-only; \
        optional
            Qobuz IDs of the artists.

            **Examples**: :code:`865362`, :code:`"21473137"`,
            :code:`"865362,21473137"`, :code:`[865362, "21473137"]`.

        track_ids : int, str, or list[int | str]; keyword-only; \
        optional
            Qobuz IDs of the tracks.

            **Examples**: :code:`23929516`, :code:`"344521217"`,
            :code:`"23929516,344521217"`,
            :code:`[23929516, "344521217"]`.

        Returns
        -------
        response : dict[str, str]
            API JSON response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        self._client._require_authentication("favorites.save")
        payload = {}
        if album_ids is not None:
            payload["album_ids"] = self._prepare_album_ids(album_ids)
        if artist_ids is not None:
            payload["artist_ids"] = self._prepare_qobuz_ids(
                artist_ids, data_type=str
            )
        if track_ids is not None:
            payload["track_ids"] = self._prepare_qobuz_ids(
                track_ids, data_type=str
            )
        if not payload:
            raise RuntimeError(
                "At least one of `album_ids`, `artist_ids`, or "
                "`track_ids` must be specified."
            )
        return self._client._request(
            "POST", "favorite/create", data=payload
        ).json()

    def remove_saved(
        self,
        *,
        album_ids: str | list[str] | None = None,
        artist_ids: int | str | list[int | str] | None = None,
        track_ids: int | str | list[int | str] | None = None,
    ) -> dict[str, str]:
        """
        Remove one or more albums, artists, and/or tracks from the
        current user's favorites.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        album_ids : str or list[str]; keyword-only; optional
            Qobuz IDs of the albums.

            **Examples**: :code:`"0075679933652"`,
            :code:`"0075679933652,aaxy9wirwgn2a"`.

        artist_ids : int, str, or list[int | str]; keyword-only;
        optional
            Qobuz IDs of the artists.

            **Examples**: :code:`865362`, :code:`"21473137"`,
            :code:`"865362,21473137"`, :code:`[865362, "21473137"]`.

        track_ids : int, str, or list[int | str]; keyword-only;
        optional
            Qobuz IDs of the tracks.

            **Examples**: :code:`23929516`, :code:`"344521217"`,
            :code:`"23929516,344521217"`,
            :code:`[23929516, "344521217"]`.

        Returns
        -------
        response : dict[str, str]
            API JSON response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        self._client._require_authentication("favorites.remove_saved")
        payload = {}
        if album_ids is not None:
            payload["album_ids"] = self._prepare_album_ids(album_ids)
        if artist_ids is not None:
            payload["artist_ids"] = self._prepare_qobuz_ids(
                artist_ids, data_type=str
            )
        if track_ids is not None:
            payload["track_ids"] = self._prepare_qobuz_ids(
                track_ids, data_type=str
            )
        if not payload:
            raise RuntimeError(
                "At least one of `album_ids`, `artist_ids`, or "
                "`track_ids` must be specified."
            )
        return self._client._request(
            "POST", "favorite/delete", data=payload
        ).json()

    @TTLCache.cached_method(ttl="user")
    def get_my_saved(
        self,
        item_type: str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for the items in the current
        user's favorites.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        item_type : str; positional-only; optional
            Type of item to return. If not specified, favorites of all
            types are returned.

            **Valid values**: :code:`"albums"`, :code:`"articles"`,
            :code:`"artists"`, :code:`"awards"`, :code:`"labels"`,
            :code:`"tracks"`.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        saved_items : dict[str, Any]
            Page of Qobuz content metadata for items in the user's
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
                    "artists": {
                      "items": [
                        {
                          "albums_count": <int>,
                          "favorited_at": <int>,
                          "id": <int>,
                          "image": {
                            "extralarge": <str>,
                            "large": <str>,
                            "medium": <str>,
                            "mega": <str>,
                            "small": <str>,
                          },
                          "name": <str>,
                          "slug": <str>
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
                            "media_count": <int>,
                            "parental_warning": <bool>,
                            "previewable": <bool>,
                            "purchasable": <bool>,
                            "purchasable_at": null,
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
                            "version": None
                          },
                          "audio_info": {
                            "replaygain_track_gain": <float>,
                            "replaygain_track_peak": <float>,
                          },
                          "composer": {
                            "id": <int>,
                            "name": <str>
                          },
                          "copyright": <str>,
                          "displayable": <bool>,
                          "downloadable": <bool>,
                          "duration": <int>,
                          "favorited_at": <int>,
                          "hires": <bool>,
                          "hires_streamable": <bool>,
                          "id": <int>,
                          "isrc": <str>,
                          "maximum_bit_depth": <int>,
                          "maximum_channel_count": <int>,
                          "maximum_sampling_rate": <float>,
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
                    "user": {
                      "id": <int>,
                      "login": <str>
                    }
                  }
        """
        self._client._require_authentication("favorites.get_my_saved")
        params = {}
        if item_type is not None:
            self._client._validate_type("item_type", item_type, str)
            item_type = item_type.strip().lower()
            if item_type not in self._FAVORITE_TYPES:
                favorite_types_str = "', '".join(self._FAVORITE_TYPES)
                raise ValueError(
                    f"Invalid item type {item_type!r}. "
                    f"Valid values: '{favorite_types_str}'."
                )
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "favorite/getUserFavorites", params=params
        ).json()

    @TTLCache.cached_method(ttl="user")
    def get_my_saved_ids(self) -> dict[str, Any]:
        """
        Get Qobuz IDs of the items in the current user's favorites.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Returns
        -------
        saved_ids : dict[str, Any]
            Qobuz IDs of the items in the user's favorites.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albums": <list[str]>,
                    "articles": [],
                    "artists": <list[int]>,
                    "awards": [],
                    "labels": [],
                    "tracks": <list[int]>,
                  }
        """
        self._client._require_authentication("favorites.get_my_saved_ids")
        return self._client._request(
            "GET", "favorite/getUserFavoriteIds"
        ).json()

    @TTLCache.cached_method(ttl="user")
    def is_saved(
        self, item_type: str, item_id: int | str, /
    ) -> dict[str, bool]:
        """
        Check whether an item is in the current user's favorites.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        item_type : str; positional-only
            Type of item.

            **Valid values**: :code:`"album"`, :code:`"artist"`,
            :code:`"article"`, :code:`"award"`, :code:`"label"`,
            :code:`"track"`.

        item_id : int or str; positional-only
            Qobuz ID of the item.

        Returns
        -------
        saved : dict[str, bool]
            Whether the current user has the specified item in their
            favorites.

            **Sample response**: :code:`{"status": <bool>}`.
        """
        self._client._require_authentication("favorites.is_saved")
        self._client._validate_type("item_type", item_type, str)
        item_type = item_type.strip().lower()
        if f"{item_type}s" not in self._FAVORITE_TYPES:
            favorite_types_str = "', '".join(
                ft[:-1] for ft in self._FAVORITE_TYPES
            )
            raise ValueError(
                f"Invalid item type {item_type!r}. "
                f"Valid values: '{favorite_types_str}'."
            )
        if item_type == "album":
            self._validate_album_id(item_id)
        else:
            self._validate_qobuz_ids(item_id, _recursive=False)
        return self._client._request(
            "GET",
            "favorite/status",
            params={"type": item_type, "item_id": item_id},
        ).json()

    def toggle_saved(
        self, item_type: str, item_id: int | str, /
    ) -> dict[str, bool]:
        """
        Toggle the saved status of an item.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        item_type : str; positional-only
            Type of item.

            **Valid values**: :code:`"album"`, :code:`"artist"`,
            :code:`"article"`, :code:`"award"`, :code:`"label"`,
            :code:`"track"`.

        item_id : int or str; positional-only
            Qobuz ID of the item.

        Returns
        -------
        saved : dict[str, bool]
            Whether the current user has the specified item in their
            favorites.

            **Sample response**: :code:`{"status": <bool>}`.
        """
        self._client._require_authentication("favorites.toggle_saved")
        self._client._validate_type("item_type", item_type, str)
        item_type = item_type.strip().lower()
        if f"{item_type}s" not in self._FAVORITE_TYPES:
            favorite_types_str = "', '".join(
                ft[:-1] for ft in self._FAVORITE_TYPES
            )
            raise ValueError(
                f"Invalid item type {item_type!r}. "
                f"Valid values: '{favorite_types_str}'."
            )
        if item_type == "album":
            self._validate_album_id(item_id)
        else:
            self._validate_qobuz_ids(item_id, _recursive=False)
        return self._client._request(
            "POST",
            "favorite/toggle",
            params={"type": item_type, "item_id": item_id},
        )
