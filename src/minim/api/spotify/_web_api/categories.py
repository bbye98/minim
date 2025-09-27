from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPICategoryEndpoints:
    """
    Spotify Web API browse category endpoints.

    .. note::

       This class is managed by :class:`minim.api.spotify.WebAPI` and
       should not be instantiated directly.
    """

    def __init__(self, client: "WebAPI", /) -> None:
        """
        Parameters
        ----------
        client : minim.api.spotify.WebAPI
            Minim's Spotify Web API client.
        """
        self._client = client

    def get_category(
        self, category_id: str, /, *, locale: str | None = None
    ) -> dict[str, Any]:
        """
        `Categories > Get Single Browse Category
        <https://developer.spotify.com/documentation/web-api/reference
        /get-a-category>`_: Get a single category used to tag items on
        Spotify.

        Parameters
        ----------
        category_id : str
            Spotify category ID.

            **Examples**: :code:`"dinner"`, :code:`"party"`.

        locale : str, keyword-only, optional
            Locale identifier consisting of an ISO 639-1 language
            code and an ISO 3166-1 alpha-2 country code joined by an
            underscore. When this parameter is provided, the category
            strings are returned in the specified language.

            .. note::

               If a locale identifier is not supplied or  the specified
               language is not available, the category strings returned
               will be in the Spotify default language (American
               English).

            **Example**: :code:`"es_MX"` for Spanish (Mexico).

        Returns
        -------
        category : dict[str, Any]
            Spotify content metadata for the category.

            .. admonition:: Sample response
               :class: dropdown

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
        return self._client._request(
            "GET", f"browse/categories/{category_id}", params={"locale": locale}
        ).json()

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
        /get-categories>`_: Get a list of categories used to tag items
        on Spotify.

        Parameters
        ----------
        locale : str, keyword-only, optional
            Locale identifier consisting of an ISO 639-1 language
            code and an ISO 3166-1 alpha-2 country code joined by an
            underscore. When this parameter is provided, the category
            strings are returned in the specified language.

            .. note::

               If a locale identifier is not supplied or  the specified
               language is not available, the category strings returned
               will be in the Spotify default language (American
               English).

            **Example**: :code:`"es_MX"` for Spanish (Mexico).

        limit : int, keyword-only, optional
            Maximum number of categories to return.

            **Valid values**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first category to return. Use with `limit` to
            get the next set of categories.

            **Default**: :code:`0`.

        Returns
        -------
        categories : dict[str, Any]
            Spotify content metadata for multiple categories.

            .. admonition:: Sample response
               :class: dropdown

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
        return self._client._request(
            "GET",
            "browse/categories",
            params={"locale": locale, "limit": limit, "offset": offset},
        ).json()
