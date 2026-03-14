from typing import Any

from ..._shared import TTLCache
from ._shared import DiscogsResourceAPI


class DatabaseAPI(DiscogsResourceAPI):
    """
    Database API endpoints for the Discogs API.

    .. important::

       This class is managed by
       :class:`minim.api.discogs.DiscogsAPIClient` and should not be
       instantiated directly.
    """

    @TTLCache.cached_method(ttl="popularity")
    def get_release(
        self,
        release_id: int | str,
        /,
        *,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """
        `Database > Release <https://www.discogs.com/developers
        /#page:database,header:database-release>`_: Get Discogs catalog
        information for a release.

        Parameters
        ----------
        release_id : int or str; positional-only
            Discogs ID of the release.

            **Examples**: :code:`249504` or :code:`"8649337"`.

        currency : str; keyword-only; optional
            Currency for marketplace data.

            **Valid values**: :code:`"USD"`, :code:`"GBP"`,
            :code:`"EUR"`, :code:`"CAD"`, :code:`"AUD"`, :code:`"JPY"`,
            :code:`"CHF"`, :code:`"MXN"`, :code:`"BRL"`, :code:`"NZD"`,
            :code:`"SEK"`, :code:`"ZAR"`.

        Returns
        -------
        release : dict[str, Any]
            Discogs content metadata for the release.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "artists": [
                      {
                        "anv": <str>,
                        "id": <int>,
                        "join": <str>,
                        "name": <str>,
                        "resource_url": <str>,
                        "role": <str>,
                        "thumbnail_url": <str>,
                        "tracks": <str>
                      }
                    ],
                    "artists_sort": <str>,
                    "blocked_from_sale": <bool>,
                    "community": {
                      "contributors": [
                        {
                          "resource_url": <str>,
                          "username": <str>
                        }
                      ],
                      "data_quality": <str>,
                      "have": <int>,
                      "rating": {
                        "average": <float>,
                        "count": <int>
                      },
                      "status": <str>,
                      "submitter": {
                        "resource_url": <str>,
                        "username": <str>
                      },
                      "want": <int>
                    },
                    "companies": [
                      {
                        "catno": <str>,
                        "entity_type": <str>,
                        "entity_type_name": <str>,
                        "id": <int>,
                        "name": <str>,
                        "resource_url": <str>
                      }
                    ],
                    "country": <str>,
                    "data_quality": <str>,
                    "date_added": <str>,
                    "date_changed": <str>,
                    "estimated_weight": <int>,
                    "extraartists": [
                      {
                        "anv": <str>,
                        "id": <int>,
                        "join": <str>,
                        "name": <str>,
                        "resource_url": <str>,
                        "role": <str>,
                        "tracks": <str>
                      }
                    ],
                    "format_quantity": <int>,
                    "formats": [
                      {
                        "descriptions": <list[str]>,
                        "name": <str>,
                        "qty": <str>
                      }
                    ],
                    "genres": <list[str]>,
                    "id": <int>,
                    "identifiers": [
                      {
                        "description": <str>,
                        "type": <str>,
                        "value": <str>
                      }
                    ],
                    "images": [
                      {
                        "height": <int>,
                        "resource_url": <str>,
                        "type": <str>,
                        "uri": <str>,
                        "uri150": <str>,
                        "width": <int>
                      }
                    ],
                    "is_offensive": <bool>,
                    "labels": [
                      {
                        "catno": <str>,
                        "entity_type": <str>,
                        "entity_type_name": <str>,
                        "id": <int>,
                        "name": <str>,
                        "resource_url": <str>,
                        "thumbnail_url": <str>
                      }
                    ],
                    "lowest_price": None,
                    "master_id": <int>,
                    "master_url": <str>,
                    "notes": <str>,
                    "num_for_sale": <int>,
                    "released": <str>,
                    "released_formatted": <str>,
                    "resource_url": <str>,
                    "series": [],
                    "status": <str>,
                    "styles": <list[str]>,
                    "thumb": <str>,
                    "title": <str>,
                    "tracklist": [
                      {
                        "duration": <str>,
                        "extraartists": [
                          {
                            "anv": <str>,
                            "id": <int>,
                            "join": <str>,
                            "name": <str>,
                            "resource_url": <str>,
                            "role": <str>,
                            "tracks": <str>
                          }
                        ],
                        "position": <str>,
                        "title": <str>,
                        "type_": "track"
                      }
                    ],
                    "uri": <str>,
                    "videos": [
                      {
                        "description": <str>,
                        "duration": <int>,
                        "embed": <bool>,
                        "title": <str>,
                        "uri": <str>
                      }
                    ],
                    "year": <int>
                  }
        """
        self._validate_numeric("release_id", release_id, int, 1)
        params = {}
        if currency is not None:
            currency = self._prepare_string("currency", currency).upper()
            if currency not in self._CURRENCIES:
                raise ValueError(
                    f"Invalid currency {currency!r}. "
                    f"Valid values: {self._join_values(self._CURRENCIES)}."
                )
            params["curr_abbr"] = currency
        return self._client._request(
            "GET", f"releases/{release_id}", params=params
        ).json()

    @TTLCache.cached_method(ttl="user")
    def get_release_user_rating(
        self, release_id: int | str, /, username: str | None = None
    ) -> dict[str, int | str]:
        """
        `Database > Release Rating By User > Get Release Rating By User
        <https://www.discogs.com/developers/#page:database,
        header:database-release-rating-by-user>`_: Get a user's rating
        for a release.

        Parameters
        ----------
        release_id : int or str; positional-only
            Discogs ID of the release.

            **Examples**: :code:`249504` or :code:`"8649337"`.

        username : str; positional-only; optional
            Username of the user. If not provided, the username of the
            current user is used. Only optional when authenticated.

            **Example**: :code:`"memory"`.

        Returns
        -------
        rating : dict[str, int | str]
            User's rating for the release.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "rating": <int>,
                    "release_id": <int>,
                    "username": <str>
                  }
        """
        self._validate_numeric("release_id", release_id, int, 1)
        return self._client._request(
            "GET",
            f"releases/{release_id}/rating/{self._resolve_username(username)}",
        ).json()
