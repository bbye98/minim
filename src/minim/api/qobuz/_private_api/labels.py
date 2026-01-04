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

    @TTLCache.cached_method(ttl="catalog")
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
                    "albums_count": <int>,
                    "description": None,
                    "id": <int>,
                    "image": None,
                    "name": <str>,
                    "slug": <str>,
                    "supplier_id": <int>
                  }
        """
        self._client._validate_qobuz_ids(label_id, _recursive=False)
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
