from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import PrivateQobuzAPI


class PrivateGenresAPI(ResourceAPI):
    """
    Genres API endpoints for the private Qobuz Web API.

    .. note::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    _client: "PrivateQobuzAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_genre(self, genre_id: int | str, /) -> dict[str, Any]:
        """
        Get Qobuz catalog information for a genre.

        Parameters
        ----------
        genre_id : int or str; positional-only
            Qobuz ID of the genre.

            **Examples**: :code:`10`, :code:`"64"`.

        Returns
        -------
        genre : dict[str, Any]
            Qobuz content metadata for the genre.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "color": <str>,
                    "id": <int>,
                    "name": <str>,
                    "path": <list[int]>,
                    "slug": <str>
                  }
        """
        self._client._validate_qobuz_ids(genre_id, _recursive=False)
        return self._client._request(
            "GET", "genre/get", params={"genre_id": genre_id}
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_subgenres(
        self,
        genre_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get available top-level genres or the subgenres of a specific
        top-level genre.

        Parameters
        ----------
        genre_id : int or str; positional-only; optional
            Qobuz ID of the top-level genre. If not provided, all
            top-level genres are returned.

            **Examples**: :code:`10`, :code:`"64"`.

        limit : int; keyword-only; optional
            Maximum number of genres to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first genre to return. Use with `limit` to get
            the next batch of genres.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        genres : dict[str, Any]
            Page of Qobuz content metadata for the genres.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "genres": {
                      "items": [
                        {
                          "color": <str>,
                          "id": <int>,
                          "name": <str>,
                          "path": <list[int]>,
                          "slug": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "parent": {
                      "color": <str>,
                      "id": <int>,
                      "name": <str>,
                      "path": <list[int]>,
                      "slug": <str>
                    }
                  }
        """
        params = {}
        if genre_id is not None:
            self._client._validate_qobuz_ids(genre_id, _recursive=False)
            params["parent_id"] = genre_id
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request("GET", "genre/list", params=params).json()
