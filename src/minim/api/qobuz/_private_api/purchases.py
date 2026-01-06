from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .._core import PrivateQobuzAPI


class PrivatePurchasesAPI(ResourceAPI):
    """
    Purchases API endpoints for the private Qobuz API.

    .. important::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    _client: "PrivateQobuzAPI"

    @TTLCache.cached_method(ttl="user")
    def get_my_purchases(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for albums and tracks purchased by
        the current user.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access personal collection and favorites.

        Parameters
        ----------
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
        purchases : dict[str, Any]
            Pages of Qobuz content metadata for purchased albums and
            tracks.

            .. admonition:: Sample responses
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
                          "downloadable_format_ids": <list[str]>,
                          "duration": <int>,
                          "genre": {
                            "color": <int>,
                            "id": <int>,
                            "name": <int>,
                            "path": <list[int]>,
                            "slug": <str>
                          },
                          "hires": <bool>,
                          "hires_purchased": <bool>,
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
                          "maximum_sampling_rate": <int>,
                          "media_count": <int>,
                          "order_id": <int>,
                          "order_line_id": <int>,
                          "parental_warning": <bool>,
                          "popularity": <int>,
                          "previewable": <bool>,
                          "purchasable": <bool>,
                          "purchasable_at": <int>,
                          "purchased_at": <int>,
                          "qobuz_id": <int>,
                          "release_date_download": <str>,
                          "release_date_original": <str>,
                          "release_date_stream": <str>,
                          "released_at": <int>,
                          "sampleable": <bool>,
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
                          "composer": {
                            "id": <int>,
                            "name": <str>
                          },
                          "copyright": <str>,
                          "displayable": <bool>,
                          "downloadable": <bool>,
                          "downloadable_format_ids": <list[int]>,
                          "duration": <int>,
                          "hires": <bool>,
                          "hires_purchased": <bool>,
                          "hires_streamable": <bool>,
                          "id": <int>,
                          "isrc": <str>,
                          "maximum_bit_depth": <int>,
                          "maximum_channel_count": <int>,
                          "maximum_sampling_rate": <float>,
                          "media_number": <int>,
                          "order_id": <int>,
                          "order_line_id": <int>,
                          "parental_warning": <bool>,
                          "performer": {
                            "id": <int>,
                            "name": <str>
                          },
                          "performers": <str>,
                          "previewable": <bool>,
                          "purchasable": <bool>,
                          "purchasable_at": <int>,
                          "purchased_at": <int>,
                          "release_date_download": <str>,
                          "release_date_original": <str>,
                          "release_date_stream": <str>,
                          "sampleable": <bool>,
                          "streamable": <bool>,
                          "streamable_at": <int>,
                          "title": <str>,
                          "track_number": <int>,
                          "type": <str>,
                          "version": <str>,
                          "work": None
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "user": {"id": <int>, "login": <str>}
                  }
        """
        self._client._require_authentication("purchases.get_my_purchases")
        params = {}
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "purchase/getUserPurchases", params=params
        ).json()

    @TTLCache.cached_method(ttl="user")
    def get_my_purchased_item_ids(self) -> dict[str, Any]:
        """
        Get Qobuz IDs of albums and tracks purchased by the current
        user.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access personal collection and favorites.

        Returns
        -------
        item_ids : dict[str, Any]
            Qobuz IDs of purchased albums and tracks.

            .. admonition:: Sample responses
               :class: dropdown

               .. code::

                  {
                    "albums": {
                      "items": [
                        {
                          "id": <str>
                        }
                      ],
                      "total": <int>
                    },
                    "tracks": {
                      "items": [
                        {
                          "bought": <bool>,
                          "id": <int>
                        }
                      ],
                      "total": <int>
                    },
                    "user": {
                      "id": <int>,
                      "login": <str>
                    }
                  }
        """
        self._client._require_authentication("purchases.get_my_purchases")
        return self._client._request(
            "GET", "purchase/getUserPurchasesIds"
        ).json()
