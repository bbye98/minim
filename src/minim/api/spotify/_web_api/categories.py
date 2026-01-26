from typing import Any

from ..._shared import TTLCache
from ._shared import SpotifyResourceAPI


class CategoriesAPI(SpotifyResourceAPI):
    """
    Categories API endpoints for the Spotify Web API.

    .. important::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPIClient`
       and should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="static")
    def get_category(
        self, category_id: str, /, *, locale: str | None = None
    ) -> dict[str, Any]:
        """
        `Categories > Get Single Browse Category
        <https://developer.spotify.com/documentation/web-api/reference
        /get-a-category>`_: Get Spotify catalog information for a
        category.

        Parameters
        ----------
        category_id : str; positional-only
            Spotify category ID.

            **Examples**: :code:`"dinner"`, :code:`"party"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag consisting of an ISO 639-1 language
            code and an ISO 3166-1 alpha-2 country code joined by an
            underscore. If provided, categories are returned in the
            specified language.

            .. note::

               If a locale identifier is not supplied or the specified
               language is not available, categories will be returned in
               the Spotify default language (American English).

            **Example**: :code:`"es_MX"` – Spanish (Mexico).

        Returns
        -------
        category : dict[str, Any]
            Spotify content metadata for the category.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "href": <str>,
                    "icons": [
                      {
                        "height": <int>,
                        "url": <str>,
                        "width": <int>
                      }
                    ],
                    "id": <str>,
                    "name": <str>
                  }
        """
        params = {}
        if locale:
            self._validate_locale(locale)
            params["locale"] = locale
        return self._client._request(
            "GET", f"browse/categories/{category_id}", params=params
        ).json()

    @TTLCache.cached_method(ttl="static")
    def get_categories(
        self,
        *,
        locale: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Categories > Get Several Browse Categories
        <https://developer.spotify.com/documentation/web-api/reference
        /get-categories>`_: Get Spotify catalog information for
        available categories.

        Parameters
        ----------
        locale : str; keyword-only; optional
            IETF BCP 47 language tag consisting of an ISO 639-1 language
            code and an ISO 3166-1 alpha-2 country code joined by an
            underscore. If provided, categories are returned in the
            specified language.

            .. note::

               If a locale identifier is not supplied or the specified
               language is not available, categories will be returned in
               the Spotify default language (American English).

            **Example**: :code:`"es_MX"` – Spanish (Mexico).

        limit : int; keyword-only; optional
            Maximum number of categories to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first category to return. Use with `limit` to
            get the next batch of categories.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        categories : dict[str, Any]
            Page of Spotify content metadata for available categories.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "categories": {
                      "href": <str>,
                      "items": [
                        {
                          "href": <str>,
                          "icons": [
                            {
                              "height": <int>,
                              "url": <str>,
                              "width": <int>
                            }
                          ],
                          "id": <str>,
                          "name": <str>
                        }
                      ],
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <int>,
                      "total": <int>
                    }
                  }
        """
        params = {}
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        if locale:
            self._validate_locale(locale)
            params["locale"] = locale
        return self._client._request(
            "GET", "browse/categories", params=params
        ).json()
