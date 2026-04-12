from __future__ import annotations
from typing import TYPE_CHECKING

from ..._shared import TTLCache
from ._shared import DiscogsResourceAPI

if TYPE_CHECKING:
    from typing import Any


class DatabaseAPI(DiscogsResourceAPI):
    """
    Database API endpoints for the Discogs API.

    .. important::

       This class is managed by
       :class:`~minim.api.discogs.DiscogsAPIClient` and should not be
       instantiated directly.
    """

    _ARTIST_SORT_FIELDS = {"year", "title", "format"}
    _RELEASE_SORT_FIELDS = {
        "released",
        "title",
        "format",
        "label",
        "catno",
        "country",
    }
    _SEARCH_RESOURCE_TYPES = {"release", "master", "artist", "label"}

    __slots__ = ()

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
            Discogs metadata for the release.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
        for a release on Discogs.

        Parameters
        ----------
        release_id : int or str; positional-only
            Discogs ID of the release.

            **Examples**: :code:`249504` or :code:`"8649337"`.

        username : str; optional
            Username of the user. If not specified, the username of the
            current user is used. Only optional when authenticated.

            **Example**: :code:`"memory"`.

        Returns
        -------
        rating : dict[str, int | str]
            User's rating for the release.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
        rating for a release on Deezer.

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
            Username of the user. If not specified, the username of the
            current user is used.

            **Example**: :code:`"memory"`.

        Returns
        -------
        rating : dict[str, int | str]
            User's new rating for the release. Returns :code:`None` if
            `rating` is :code:`0`.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
            Username of the user. If not specified, the username of the
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
        header:database-community-release-rating>`_: Get the community
        rating for a release on Deezer.

        Parameters
        ----------
        release_id : int or str; positional-only
            Discogs ID of the release.

            **Examples**: :code:`249504` or :code:`"8649337"`.

        Returns
        -------
        rating : dict[str, Any]
            Community rating for the release.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
        /#page:database,header:database-release-stats>`_: Get community
        statistics for a release on Deezer.

        Parameters
        ----------
        release_id : int or str; positional-only
            Discogs ID of the release.

            **Examples**: :code:`249504` or :code:`"8649337"`.

        Returns
        -------
        commununity_stats : dict[str, Any]
            Community statistics for the release.

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
            Discogs metadata for the master release.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
        header:database-master-release-versions>`_: Get Discogs catalog
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
            Discogs metadata for the master's release versions.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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

    @TTLCache.cached_method(ttl="static")
    def get_artist(self, artist_id: int | str, /) -> dict[str, Any]:
        """
        `Database > Artist <https://www.discogs.com/developers
        /#page:database,header:database-artist>`_: Get Discogs catalog
        information for an artist.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Discogs ID of the artist.

            **Examples**: :code:`108713`, :code:`"3042550"`.

        Returns
        -------
        artist : dict[str, Any]
            Discogs metadata for the artist.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "data_quality": <str>,
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
                    "members": [
                      {
                        "active": <bool>,
                        "id": <int>,
                        "name": <str>,
                        "resource_url": <str>,
                        "thumbnail_url": <str>
                      }
                    ],
                    "name": <str>,
                    "profile": <str>,
                    "releases_url": <str>,
                    "resource_url": <str>,
                    "uri": <str>,
                    "urls": <list[str]>
                  }
        """
        self._validate_numeric("artist_id", artist_id, int, 1)
        return self._client._request("GET", f"artists/{artist_id}").json()

    @TTLCache.cached_method(ttl="daily")
    def get_artist_releases(
        self,
        artist_id: int | str,
        /,
        *,
        limit: int | None = None,
        page: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        `Database > Artist Releases <https://www.discogs.com/developers
        /#page:database,header:database-artist-releases>`_: Get Discogs
        catalog information for releases by an artist.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Discogs ID of the artist.

            **Examples**: :code:`108713`, :code:`"3042550"`.

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

            **Valid values**: :code:`"year"`, :code:`"title"`,
            :code:`"format"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

        Returns
        -------
        releases : dict[str, Any]
            Discogs metadata for the artist's releases.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
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
                    "releases": [
                      {
                        "artist": <str>,
                        "id": <int>,
                        "main_release": <int>,
                        "resource_url": <str>,
                        "role": <str>,
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
                        "thumb": <str>,
                        "title": <str>,
                        "type": <str>,
                        "year": <int>
                      }
                    ]
                  }
        """
        self._validate_numeric("artist_id", artist_id, int, 1)
        params = {}
        if sort_by is not None:
            sort_by = self._prepare_string("sort_by", sort_by).lower()
            if sort_by not in self._ARTIST_SORT_FIELDS:
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. Valid values: "
                    f"{self._join_values(self._ARTIST_SORT_FIELDS)}."
                )
            params["sort"] = sort_by
        if descending is not None:
            self._validate_type("descending", descending, bool)
            params["sort_order"] = "desc" if descending else "asc"
        return self._get_paginated_resources(
            f"artists/{artist_id}/releases",
            limit=limit,
            page=page,
            params=params,
        )

    @TTLCache.cached_method(ttl="static")
    def get_label(self, label_id: int | str, /) -> dict[str, Any]:
        """
        `Database > Label <https://www.discogs.com/developers
        /#page:database,header:database-label>`_: Get Discogs catalog
        information for a label.

        Parameters
        ----------
        label_id : int or str; positional-only
            Discogs ID of the label.

            **Examples**: :code:`1`, :code:`"681"`.

        Returns
        -------
        label : dict[str, Any]
            Discogs metadata for the label.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "contact_info": <str>,
                    "data_quality": <str>,
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
                    "name": <str>,
                    "parent_label": {
                      "id": <int>,
                      "name": <str>,
                      "resource_url": <str>
                    },
                    "profile": <str>,
                    "releases_url": <str>,
                    "resource_url": <str>,
                    "sublabels": [
                      {
                        "id": <int>,
                        "name": <str>,
                        "resource_url": <str>
                      }
                    ],
                    "uri": <str>,
                    "urls": <list[str]>
                  }
        """
        self._validate_number("label_id", label_id, int, 1)
        return self._client._request("GET", f"labels/{label_id}").json()

    @TTLCache.cached_method(ttl="popularity")
    def get_label_releases(
        self,
        label_id: int | str,
        /,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        `Database > All Label Releases <https://www.discogs.com
        /developers/#page:database,
        header:database-all-label-releases>`_: Get Discogs catalog
        information for releases by a label.

        Parameters
        ----------
        label_id : int or str; positional-only
            Discogs ID of the label.

            **Examples**: :code:`1`, :code:`"681"`.

        limit : int; keyword-only; optional
            Maximum number of releases to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`50`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of
            releases.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        Returns
        -------
        releases : dict[str, Any]
            Page of Discogs metadata for the label's releases.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
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
                    "releases": [
                      {
                        "artist": <str>,
                        "catno": <str>,
                        "format": <str>,
                        "id": <int>,
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
                        "title": <str>,
                        "year": <int>
                      }
                    ]
        """
        return self._get_paginated_resources(
            f"labels/{label_id}/releases", limit=limit, page=page
        )

    @TTLCache.cached_method(ttl="search")
    def search(
        self,
        query: str | None = None,
        /,
        *,
        resource_type: str | None = None,
        title: str | None = None,
        release: str | None = None,
        artist: str | None = None,
        artist_variation: str | None = None,
        track: str | None = None,
        credit: str | None = None,
        label: str | None = None,
        genre: str | None = None,
        style: str | None = None,
        release_country: str | None = None,
        release_format: str | None = None,
        release_year: int | str | None = None,
        catalog_number: str | None = None,
        barcode: str | None = None,
        submitter: str | None = None,
        contributor: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        `Database > Search <https://www.discogs.com/developers
        /#page:database,header:database-search>`_: Search for artists,
        releases, labels, and masters in the Discogs catalog.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        query : str; positional-only; optional
            Search query.

            **Example**: :code:`"Nirvana"`.

        resource_type : str; keyword-only; optional
            Resource type to filter search results by.

            **Valid values**: :code:`"release"`, :code:`"master"`,
            :code:`"artist"`, :code:`"label"`.

        title : str; keyword-only; optional
            Combined artist and title search field to filter search
            results by.

            **Example**: :code:`"Nirvana - Nevermind"`.

        release : str; keyword-only; optional
            Release title to filter search results by.

            **Example**: :code:`"Nevermind"`.

        artist : str; keyword-only; optional
            Artist name to filter search results by.

            **Example**: :code:`"Nirvana"`.

        artist_variation : str; keyword-only; optional
            Artist name variation to filter search results by.

            **Example**: :code:`"Nirvana (US)"`.

        track : str; keyword-only; optional
            Track title to filter search results by.

            **Example**: :code:`"Smells Like Teen Spirit"`.

        credit : str; keyword-only; optional
            Release credit to filter search results by.

            **Example**: :code:`"Kurt Cobain"`.

        label : str; keyword-only; optional
            Label name to filter search results by.

            **Example**: :code:`"DGC"`.

        genre : str; keyword-only; optional
            Genre to filter search results by.

            **Example**: :code:`"Rock"`.

        style : str; keyword-only; optional
            Style to filter search results by.

            **Example**: :code:`"Grunge"`.

        release_country : str; keyword-only; optional
            Release country to filter search results by.

            **Example**: :code:`"Canada"`.

        release_format : str; keyword-only; optional
            Release format to filter search results by.

            **Example**: :code:`"Album"`.

        release_year : int or str; keyword-only; optional
            Release year to filter search results by.

            **Examples**: :code:`1991`, :code:`"1991"`.

        catalog_number : str; keyword-only; optional
            Catalog number to filter search results by.

            **Example**: :code:`"DGC-24425"`.

        barcode : str; keyword-only; optional
            Release barcode to filter search results by.

            **Example**: :code:`"7 2064-24425-2 4"`.

        submitter : str; keyword-only; optional
            Username of the Discogs user who submitted the release to
            filter search results by.

            **Example**: :code:`"milKt"`.

        contributor : str; keyword-only; optional
            Username of the Discogs user who contributed to the
            release's metadata to filter search results by.

            **Example**: :code:`"jerome99"`.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`50`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of items.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        Returns
        -------
        results : dict[str, Any]
            Page of Discogs metadata for the matching catalog items.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
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
                    "results": [
                      {
                        "cover_image": <str>,
                        "id": <int>,
                        "master_id": <int>,
                        "master_url": <str>,
                        "resource_url": <str>,
                        "thumb": <str>,
                        "title": <str>,
                        "type": <str>,
                        "uri": <str>,
                        "user_data": {
                          "in_collection": <bool>,
                          "in_wantlist": <bool>
                        }
                      }
                    ]
                  }
        """
        self._client._require_authentication("database.search")
        params = {}
        if query is not None:
            params["query"] = self._prepare_string("query", query)
        if resource_type is not None:
            resource_type = self._prepare_string(
                "resource_type", resource_type
            ).lower()
            if resource_type not in self._SEARCH_RESOURCE_TYPES:
                raise ValueError(
                    f"Invalid resource type {resource_type!r}. Valid values: "
                    f"{self._join_values(self._SEARCH_RESOURCE_TYPES)}."
                )
            params["type"] = resource_type
        if title is not None:
            params["title"] = self._prepare_string("title", title)
        if release is not None:
            params["release_title"] = self._prepare_string("release", release)
        if artist is not None:
            params["artist"] = self._prepare_string("artist", artist)
        if artist_variation is not None:
            params["artist_variation"] = self._prepare_string(
                "artist_variation", artist_variation
            )
        if track is not None:
            params["track"] = self._prepare_string("track", track)
        if credit is not None:
            params["credit"] = self._prepare_string("credit", credit)
        if label is not None:
            params["label"] = self._prepare_string("label", label)
        if genre is not None:
            params["genre"] = self._prepare_string("genre", genre)
        if style is not None:
            params["style"] = self._prepare_string("style", style)
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
        if catalog_number is not None:
            params["catno"] = self._prepare_string(
                "catalog_number", catalog_number
            )
        if barcode is not None:
            params["barcode"] = self._prepare_barcode("barcode", barcode)
        if submitter is not None:
            params["submitter"] = self._prepare_string("submitter", submitter)
        if contributor is not None:
            params["contributor"] = self._prepare_string(
                "contributor", contributor
            )
        return self._get_paginated_resources(
            "database/search", limit=limit, page=page, params=params
        )
