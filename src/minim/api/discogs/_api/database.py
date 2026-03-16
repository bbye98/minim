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

    _RELEASE_SORT_FIELDS = {
        "released",
        "title",
        "format",
        "label",
        "catno",
        "country",
    }

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

        username : str; optional
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

    def set_release_user_rating(
        self,
        release_id: int | str,
        /,
        rating: int,
        *,
        username: str | None = None,
    ) -> dict[str, int | str] | None:
        """
        `Database > Release Rating By User > Update Release Rating By
        User <https://www.discogs.com/developers/#page:database,
        header:database-release-rating-by-user-put>`_: Set a user's
        rating for a release.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        release_id : int or str; positional-only
            Discogs ID of the release.

            **Examples**: :code:`249504` or :code:`"8649337"`.

        rating : int; keyword-only; optional
            Star rating for the release. Use :code:`0` to reset the
            rating.

            **Valid range**: :code:`0` to :code:`5`.

        username : str; keyword-only; optional
            Username of the user. If not provided, the username of the
            current user is used.

            **Example**: :code:`"memory"`.

        Returns
        -------
        rating : dict[str, int | str]
            User's new rating for the release. Only returned if `rating`
            is not :code:`0`.

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
        self._validate_number("rating", rating, int, 0, 5)
        if rating:
            return self._client._request(
                "PUT",
                f"releases/{release_id}/rating/{self._resolve_username(username)}",
                json={"rating": rating},
            ).json()
        self.delete_release_user_rating(release_id, username=username)

    def delete_release_user_rating(
        self, release_id: int | str, /, *, username: str | None = None
    ) -> None:
        """
        `Database > Release Rating By User > Delete Release Rating By
        User <https://www.discogs.com/developers/#page:database,
        header:database-release-rating-by-user-delete>`_: Delete a
        user's rating for a release.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        release_id : int or str; positional-only
            Discogs ID of the release.

            **Examples**: :code:`249504` or :code:`"8649337"`.

        username : str; keyword-only; optional
            Username of the user. If not provided, the username of the
            current user is used.

            **Example**: :code:`"memory"`.
        """
        self._validate_numeric("release_id", release_id, int, 1)
        self._client._request(
            "DELETE",
            f"releases/{release_id}/rating/{self._resolve_username(username)}",
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_release_community_rating(
        self, release_id: int | str, /
    ) -> dict[str, Any]:
        """
        `Database > Community Release Rating <https://www.discogs.com
        /developers/#page:database,
        header:database-community-release-rating>`_: Get the average
        rating and number of user ratings for a release.

        Parameters
        ----------
        release_id : int or str; positional-only
            Discogs ID of the release.

            **Examples**: :code:`249504` or :code:`"8649337"`.

        Returns
        -------
        rating : dict[str, Any]
            Average rating and number of user ratings for the release.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "rating": {
                      "average": <float>,
                      "count": <int>
                    },
                    "release_id": <int>
                  }
        """
        self._validate_numeric("release_id", release_id, int, 1)
        return self._client._request(
            "GET", f"releases/{release_id}/rating"
        ).json()

    @TTLCache.cached_method(ttl="popularity")
    def get_release_community_stats(
        self, release_id: int | str, /
    ) -> dict[str, Any]:
        """
        `Database > Release Stats <https://www.discogs.com/developers
        /#page:database,header:database-release-stats>`_: Get a
        release's community statistics.

        Parameters
        ----------
        release_id : int or str; positional-only
            Discogs ID of the release.

            **Examples**: :code:`249504` or :code:`"8649337"`.

        Returns
        -------
        commununity_stats : dict[str, Any]
            Release's community statistics.

            **Sample response**:
            :code:`{"num_have": <int>, "num_want": <int>}`.
        """
        self._validate_numeric("release_id", release_id, int, 1)
        return self._client._request(
            "GET", f"releases/{release_id}/stats"
        ).json()

    @TTLCache.cached_method(ttl="popularity")
    def get_master(self, master_id: int | str, /) -> dict[str, Any]:
        """
        `Database > Master Release <https://www.discogs.com/developers
        /#page:database,header:database-master-release>`_: Get Discogs
        catalog information for a master release.

        Parameters
        ----------
        master_id : int or str; positional-only
            Discogs ID of the master release.

            **Examples**: :code:`1000`, :code:`"846354"`.

        Returns
        -------
        master : dict[str, Any]
            Discogs content metadata for the master release.

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
                    "data_quality": <str>,
                    "genres": <list[str]>,
                    "id": <int>,
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
                    "lowest_price": <float>,
                    "main_release": <int>,
                    "main_release_url": <str>,
                    "most_recent_release": <int>,
                    "most_recent_release_url": <str>,
                    "num_for_sale": <int>,
                    "resource_url": <str>,
                    "styles": <list[str]>,
                    "title": <str>,
                    "tracklist": [
                      {
                        "duration": <str>,
                        "position": <str>,
                        "title": <str>,
                        "type_": "track"
                      }
                    ],
                    "uri": <str>,
                    "versions_url": <str>,
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
        self._validate_numeric("master_id", master_id, int, 1)
        return self._client._request("GET", f"masters/{master_id}").json()

    @TTLCache.cached_method(ttl="popularity")
    def get_master_versions(
        self,
        master_id: int | str,
        /,
        *,
        label: str | None = None,
        release_country: str | None = None,
        release_format: str | None = None,
        release_year: int | str | None = None,
        limit: int | None = None,
        page: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        `Database > Master Release Versions <https://www.discogs.com
        /developers/#page:database,
        header:database-master-release-versions`_: Get Discogs catalog
        information for a master's release versions.

        Parameters
        ----------
        master_id : int or str; positional-only
            Discogs ID of the master release.

            **Examples**: :code:`1000`, :code:`"846354"`.

        label : str; keyword-only; optional
            Label to filter releases by.

            **Example**: :code:`"Scorpio Music"`.

        release_country : str; keyword-only; optional
            Release country to filter releases by.

            **Example**: :code:`"Belgium"`.

        release_format : str; keyword-only; optional
            Release format to filter releases by.

            **Example**: :code:`"Vinyl"`.

        release_year : int or str; keyword-only; optional
            Release year to filter releases by.

            **Examples**: :code:`1992`, :code:`"1998"`.

        limit : int; keyword-only; optional
            Maximum number of releases to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`50`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of
            releases.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        sort_by : str; keyword-only; optional
            Field to sort releases by.

            **Valid values**: :code:`"released"`, :code:`"title"`,
            :code:`"format"`, :code:`"label"`, :code:`"catno"`,
            :code:`"country"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

        Returns
        -------
        versions : dict[str, Any]
            Discogs content metadata for the master's release versions.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "filter_facets": [
                      {
                        "allows_multiple_values": <bool>,
                        "id": <str>,
                        "title": <str>,
                        "values": [
                          {
                            "count": <int>,
                            "title": <str>,
                            "value": <str>
                          }
                        ]
                      }
                    ],
                    "filters": {
                      "applied": {},
                      "available": {
                        "country": <dict[str, int]>,
                        "format": <dict[str, int]>,
                        "label": <dict[str, int]>,
                        "released": <dict[str, int]>
                      }
                    },
                    "pagination": {
                      "items": <int>,
                      "page": <int>,
                      "pages": <int>,
                      "per_page": <int>,
                      "urls": {
                        "first": <str>,
                        "last": <str>,
                        "next": <str>,
                        "prev": <str>
                      }
                    },
                    "versions": [
                      {
                        "catno": <str>,
                        "country": <str>,
                        "format": <str>,
                        "id": <int>,
                        "label": <str>,
                        "major_formats": <list[str]>,
                        "released": <str>,
                        "resource_url": <str>,
                        "stats": {
                          "community": {
                            "in_collection": <int>,
                            "in_wantlist": <int>
                          },
                          "user": {
                            "in_collection": <int>,
                            "in_wantlist": <int>
                          }
                        },
                        "status": <str>,
                        "thumb": <str>,
                        "title": <str>
                      }
                    ]
                  }
        """
        self._validate_numeric("master_id", master_id, int, 1)
        params = {}
        if label is not None:
            params["label"] = self._prepare_string("label", label)
        if release_country is not None:
            params["country"] = self._prepare_string(
                "release_country", release_country
            )
        if release_format is not None:
            params["format"] = self._prepare_string(
                "release_format", release_format
            )
        if release_year is not None:
            self._validate_numeric("release_year", release_year, int, 0)
            params["year"] = str(release_year)
        if sort_by is not None:
            sort_by = self._prepare_string("sort_by", sort_by).lower()
            if sort_by not in self._RELEASE_SORT_FIELDS:
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. Valid values: "
                    f"{self._join_values(self._RELEASE_SORT_FIELDS)}."
                )
            params["sort"] = sort_by
        if descending is not None:
            self._validate_type("descending", descending, bool)
            params["sort_order"] = "desc" if descending else "asc"
        return self._get_paginated_resources(
            f"masters/{master_id}/versions",
            limit=limit,
            page=page,
            params=params,
        )
