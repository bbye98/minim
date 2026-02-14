from typing import Any

from ..._shared import TTLCache
from ._shared import DiscogsResourceAPI


class UsersAPI(DiscogsResourceAPI):
    """
    User Identity, User Collection, and User Wantlist API endpoints for
    the Discogs API.

    .. important::

       This class is managed by
       :class:`minim.api.discogs.DiscogsAPIClient` and should not be
       instantiated directly.
    """

    _SORT_FIELDS = {
        "label",
        "artist",
        "title",
        "catno",
        "format",
        "rating",
        "year",
        "added",
    }

    @TTLCache.cached_method(ttl="static")
    def get_my_identity(self) -> dict[str, Any]:
        """
        `User Identity > Identity <https://www.discogs.com/developers
        /#page:user-identity,header:user-identity-identity>`_: Get the
        identity of the current user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Returns
        -------
        identity : dict[str, Any]
            Identity of the current user.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "consumer_name": <str>,
                    "id": <int>,
                    "resource_url": <str>,
                    "username": <str>
                  }
        """
        self._client._require_authentication("users.get_my_identity")
        return self._client._request("GET", "oauth/identity").json()

    @TTLCache.cached_method(ttl="user")
    def get_user(self, username: str | None = None, /) -> dict[str, Any]:
        """
        `User Identity > Profile > Get Profile <https://www.discogs.com
        /developers/#page:user-identity,header:user-identity-profile>`_:
        Get profile information for a Discogs user.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 User authentication
                    Access the :code:`email`, :code:`num_list`,
                    :code:`num_collection`, and :code:`num_wantlist`
                    keys if authenticated as the requested user.

        Parameters
        ----------
        username : str; positional-only; optional
            Username. If not provided, the username of the current user
            is used. Only optional when authenticated.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        user : dict[str, Any]
            User's profile information.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "activated": <bool>,
                    "avatar_url": <str>,
                    "banner_url": <str>,
                    "buyer_num_ratings": <int>,
                    "buyer_rating": <float>,
                    "buyer_rating_stars": <float>,
                    "collection_fields_url": <str>,
                    "collection_folders_url": <str>,
                    "curr_abbr": <str>,
                    "email": <str>,
                    "home_page": <str>,
                    "id": <int>,
                    "inventory_url": <str>,
                    "is_staff": <bool>,
                    "location": <str>,
                    "marketplace_suspended": <bool>,
                    "name": <str>,
                    "num_collection": <int>,
                    "num_for_sale": <int>,
                    "num_lists": <int>,
                    "num_pending": <int>,
                    "num_unread": <int>,
                    "num_wantlist": <int>,
                    "profile": <str>,
                    "rank": <float>,
                    "rating_avg": <float>,
                    "registered": <str>,
                    "releases_contributed": <int>,
                    "releases_rated": <int>,
                    "resource_url": <str>,
                    "seller_num_ratings": <int>,
                    "seller_rating": <float>,
                    "seller_rating_stars": <float>,
                    "uri": <str>,
                    "username": <str>,
                    "wantlist_url": <str>
                  }
        """
        return self._client._request(
            "GET", f"users/{self._resolve_username(username)}"
        ).json()

    def update_user_profile(
        self,
        username: str | None = None,
        /,
        *,
        name: str | None = None,
        website: str | None = None,
        location: str | None = None,
        bio: str | None = None,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """
        `User Identity > Profile > Edit Profile <https://www.discogs.com
        /developers/#page:user-identity,
        header:user-identity-profile-post>`_: Update a user's profile
        information.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        .. important::

           At least one of :code:`name`, :code:`website`,
           :code:`location`, :code:`bio`, or :code:`currency` must be
           specified.

        Parameters
        ----------
        username : str; positional-only; optional
            Username. If not provided, the username of the current user
            is used. Only optional when authenticated.

            **Example**: :code:`"vreon"`.

        name : str; keyword-only; optional
            Full name.

            **Example**: :code:`"Nicolas Cage"`.

        website : str; keyword-only; optional
            Home page or website.

            **Example**: :code:`"www.discogs.com"`.

        location : str; keyword-only; optional
            Geographical location.

            **Example**: :code:`"Portland"`.

        bio : str; keyword-only; optional
            Biographical information or tagline.

            **Example**: :code:`"I am a Discogs user!"`.

        currency : str; keyword-only; optional
            Currency for marketplace data.

            **Valid values**: :code:`"USD"`, :code:`"GBP"`,
            :code:`"EUR"`, :code:`"CAD"`, :code:`"AUD"`, :code:`"JPY"`,
            :code:`"CHF"`, :code:`"MXN"`, :code:`"BRL"`, :code:`"NZD"`,
            :code:`"SEK"`, :code:`"ZAR"`.

        Returns
        -------
        profile : dict[str, Any]
            Updated user's profile information.

            .. admonition:: Sample resposne
               :class: response dropdown

               .. code::

                  {
                    "activated": <bool>,
                    "avatar_url": <str>,
                    "banner_url": <str>,
                    "buyer_num_ratings": <int>,
                    "buyer_rating": <float>,
                    "buyer_rating_stars": <float>,
                    "collection_fields_url": <str>,
                    "collection_folders_url": <str>,
                    "curr_abbr": <str>,
                    "email": <str>,
                    "home_page": <str>,
                    "id": <int>,
                    "inventory_url": <str>,
                    "is_staff": <bool>,
                    "location": <str>,
                    "marketplace_suspended": <bool>,
                    "name": <str>,
                    "num_collection": <int>,
                    "num_for_sale": <int>,
                    "num_lists": <int>,
                    "num_pending": <int>,
                    "num_unread": <int>,
                    "num_wantlist": <int>,
                    "profile": <str>,
                    "rank": <float>,
                    "rating_avg": <float>,
                    "registered": <str>,
                    "releases_contributed": <int>,
                    "releases_rated": <int>,
                    "resource_url": <str>,
                    "seller_num_ratings": <int>,
                    "seller_rating": <float>,
                    "seller_rating_stars": <float>,
                    "uri": <str>,
                    "username": <str>,
                    "wantlist_url": <str>
                  }
        """
        payload = {}
        if name is not None:
            payload["name"] = self._prepare_string(
                "name", name, allow_blank=True
            )
        if website is not None:
            payload["home_page"] = self._prepare_string(
                "website", website, allow_blank=True
            )
        if location is not None:
            payload["location"] = self._prepare_string(
                "location", location, allow_blank=True
            )
        if bio is not None:
            self._validate_type("bio", bio, str)
            payload["profile"] = bio
        if currency is not None:
            currency = self._prepare_string("currency", currency).upper()
            if currency not in self._CURRENCIES:
                raise ValueError(
                    f"Invalid currency {currency!r}. "
                    f"Valid values: {self._join_values(self._CURRENCIES)}."
                )
            payload["curr_abbr"] = currency
        if not payload:
            raise ValueError("At least one change must be specified.")
        return self._client._request(
            "POST", f"users/{self._resolve_username(username)}", json=payload
        ).json()

    @TTLCache.cached_method(ttl="user")
    def get_user_edits(
        self,
        username: str | None = None,
        /,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        `User Identity > User Submissions <https://www.discogs.com
        /developers/#page:user-identity,
        header:user-identity-user-submissions>`_: Get Discogs catalog
        information for edits that a user has made to artists, labels,
        and/or releases.

        Parameters
        ----------
        username : str; positional-only; optional
            Username. If not provided, the username of the current user
            is used. Only optional when authenticated.

            **Example**: :code:`"shooezgirl"`.

        limit : int; keyword-only; optional
            Maximum number of edits to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`50`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of edits.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        Returns
        -------
        edits : dict[str, Any]
            Discogs content metadata for edits made by the user.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

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
                    "submissions": {
                      "artists": [
                        {
                          "data_quality": <str>,
                          "id": <int>,
                          "name": <str>,
                          "namevariations": <list[str]>,
                          "releases_url": <str>,
                          "resource_url": <str>,
                          "uri": <str>
                        }
                      ],
                      "labels": [],
                      "releases": [
                        {
                          "artists": [
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
                              "average": <int>,
                              "count": <int>
                            },
                            "status": <str>,
                            "submitter": {
                              "resource_url": <str>,
                              "username": <str>
                            },
                            "want": <int>
                          },
                          "companies": [],
                          "country": <str>,
                          "data_quality": <str>,
                          "date_added": <str>,
                          "date_changed": <str>,
                          "estimated_weight": <int>,
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
                          "images": [
                            {
                              "height": <int>,
                              "resource_url": <str>,
                              "type": "primary",
                              "uri": <str>,
                              "uri150": <str>,
                              "width": <int>
                            }
                          ],
                          "labels": [
                            {
                              "catno": <str>,
                              "entity_type": <str>,
                              "id": <int>,
                              "name": <str>,
                              "resource_url": <str>
                            }
                          ],
                          "master_id": <int>,
                          "master_url": <str>,
                          "notes": <str>,
                          "released": <str>,
                          "released_formatted": <str>,
                          "resource_url": <str>,
                          "series": [],
                          "status": <str>,
                          "styles": <list[str]>,
                          "thumb": <str>,
                          "title": <str>,
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
                      ],
                    }
                  }
        """
        return self._get_paginated_resources(
            f"users/{self._resolve_username(username)}/submissions",
            limit=limit,
            page=page,
        )

    @TTLCache.cached_method(ttl="user")
    def get_user_creations(
        self,
        username: str | None = None,
        /,
        *,
        limit: int | None = None,
        page: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        `User Identity > User Contributions <https://www.discogs.com
        /developers/#page:user-identity,
        header:user-identity-user-contributions>`_: Get Discogs catalog
        information for artists, labels, and/or releases that a user has
        created.

        Parameters
        ----------
        username : str; positional-only; optional
            Username. If not provided, the username of the current user
            is used. Only optional when authenticated.

            **Example**: :code:`"shooezgirl"`.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`50`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of items.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        sort_by : str; keyword-only; optional
            Field to sort the returned items by.

            **Valid values**: :code:`"label"`, :code:`"artist"`,
            :code:`"title"`, :code:`"catno"`, :code:`"format"`,
            :code:`"rating"`, :code:`"year"`, :code:`"added"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.
        """
        params = {}
        if sort_by is not None:
            sort_by = self._prepare_string("sort_by", sort_by).lower()
            if sort_by not in self._SORT_FIELDS:
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. "
                    f"Valid values: {self._join_values(self._SORT_FIELDS)}."
                )
        if descending is not None:
            self._validate_type("descending", descending, bool)
            params["sort_order"] = "desc" if descending else "asc"
        return self._get_paginated_resources(
            f"users/{self._resolve_username(username)}/contributions",
            limit=limit,
            page=page,
            params=params,
        )
