from typing import Any

from ..._shared import TTLCache
from ._shared import PrivateQobuzResourceAPI


class PrivateLabelsAPI(PrivateQobuzResourceAPI):
    """
    Labels API endpoints for the private Qobuz Web API.

    .. note::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    _RELATIONSHIPS = {"albums", "focus", "focusAll"}

    @TTLCache.cached_method(ttl="daily")
    def get_label(
        self,
        label_id: int | str,
        /,
        *,
        expand: str | list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for a label.

        Parameters
        ----------
        label_id : int or str; positional-only
            Qobuz ID of the label.

            **Examples**: :code:`1385`, :code:`"8355112"`.

        expand : str or list[str]; keyword-only; optional
            Related resources to include metadata for in the response.

            **Valid values**: :code:`"albums"`, :code:`"focus"`,
            :code:`"focusAll"`.

            **Examples**: :code:`"albums"`, :code:`"focus,focusAll"`,
            :code:`["focus", "focusAll"]`.

        limit : int; keyword-only; optional
            Maximum number of albums to return when :code:`"albums"` is
            included in the `expand` parameter.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first album to return when :code:`"albums"` is
            included in the `expand` parameter. Use with `limit` to get
            the next batch of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        label : dict[str, Any]
            Qobuz content metadata for the label.

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
                          "duration": <int>,
                          "genre": {
                            "color": <str>,
                            "id": <int>,
                            "name": <str>,
                            "path": <list[int]>,
                            "slug": <int>
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
                          "maximum_sampling_rate": <int>,
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
                    "albums_count": <int>,
                    "description": None,
                    "id": <int>,
                    "image": None,
                    "items_focus": None,
                    "name": <str>,
                    "slug": <str>,
                    "supplier_id": <int>
                  }
        """
        self._validate_qobuz_ids(label_id, _recursive=False)
        params = {"label_id": label_id}
        if expand is not None:
            params["extra"] = self._prepare_expand(expand)
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request("GET", "label/get", params=params).json()

    @TTLCache.cached_method(ttl="daily")
    def get_labels(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        Get available labels.

        Parameters
        ----------
        limit : int; keyword-only; optional
            Maximum number of labels to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first label to return. Use with `limit` to get
            the next batch of labels.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        labels : dict[str, Any]
            Page of Qobuz content metadata for the labels.
        """
        params = {}
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request("GET", "label/list", params=params).json()
