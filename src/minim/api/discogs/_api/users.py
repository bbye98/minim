from __future__ import annotations
from typing import TYPE_CHECKING

from ..._shared import TTLCache
from ._shared import DiscogsResourceAPI

if TYPE_CHECKING:
    from typing import Any


class UsersAPI(DiscogsResourceAPI):
    """
    User Identity, User Collection, User Wantlist, and User Lists API
    endpoints for the Discogs API.

    .. important::

       This class is managed by
       :class:`~minim.api.discogs.DiscogsAPIClient` and should not be
       instantiated directly.
    """

    _SORT_FIELDS = {
        "added",
        "artist",
        "catno",
        "format",
        "label",
        "rating",
        "title",
        "year",
    }

    __sort__ = ()

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

               .. code-block::

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
        Get Discogs profile information for a user.

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
            Username of the user. If not specified, the username of the
            current user is used. Only optional when authenticated.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        user : dict[str, Any]
            Discogs profile information for the user.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
        *,
        name: str | None = None,
        website: str | None = None,
        location: str | None = None,
        bio: str | None = None,
        currency: str | None = None,
        username: str | None = None,
    ) -> dict[str, Any]:
        """
        `User Identity > Profile > Edit Profile <https://www.discogs.com
        /developers/#page:user-identity,
        header:user-identity-profile-post>`_: Update the Deezer profile
        information for a user.

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

        username : str; keyword-only; optional
            Username of the user. If not specified, the username of the
            current user is used.

            **Example**: :code:`"vreon"`.

        Returns
        -------
        profile : dict[str, Any]
            Updated Discogs profile information for the user.

            .. admonition:: Sample resposne
               :class: response dropdown

               .. code-block::

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
        self._client._require_authentication("users.update_user_profile")
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
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        `User Identity > User Submissions <https://www.discogs.com
        /developers/#page:user-identity,
        header:user-identity-user-submissions>`_: Get Discogs catalog
        information for a user's edits to artists, labels, and releases.

        Parameters
        ----------
        username : str; optional
            Username of the user. If not specified, the username of the
            current user is used. Only optional when authenticated.

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
            Page of Discogs metadata for the user's edits.

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
    def get_user_contributions(
        self,
        username: str | None = None,
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
        information for a user's contributions of artists, labels, and
        releases.

        Parameters
        ----------
        username : str; optional
            Username of the user. If not specified, the username of the
            current user is used. Only optional when authenticated.

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

        Returns
        -------
        contributions : dict[str, Any]
            Page of Discogs metadata for the user's contributions.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "contributions": [
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
                            "type": <str>,
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
                    }
                  }
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

    @TTLCache.cached_method(ttl="user")
    def get_user_collection_folders(
        self, username: str | None = None
    ) -> dict[str, Any]:
        """
        `User Collection > Collection > Get Collection Folders
        <https://www.discogs.com/developers/#page:user-collection,
        header:user-collection-collection-get>`_: Get Discogs catalog
        information for a user's collection folders.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 User authentication
                    Access private collections if authenticated as the
                    requested user.

        Parameters
        ----------
        username : str; optional
            Username of the user. If not specified, the username of the
            current user is used. Only optional when authenticated.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        folders : dict[str, Any]
            Discogs metadata for the user's collection folders.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "folders": [
                      {
                        "count": <int>,
                        "id": <int>,
                        "name": <str>,
                        "resource_url": <str>
                      }
                    ]
                  }
        """
        return self._client._request(
            "GET",
            f"users/{self._resolve_username(username)}/collection/folders",
        ).json()

    def create_user_collection_folder(
        self, folder_name: str, *, username: str | None = None
    ) -> dict[str, Any]:
        """
        `User Collection > Collection > Create Folder
        <https://www.discogs.com/developers/#page:user-collection,
        header:user-collection-collection-post>`_: Create a collection
        folder.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        folder_name : str
            Folder name.

            **Example**: :code:`"My favorites"`.

        username : str; keyword-only; optional
            Username of the user. If not specified, the username of the
            current user is used.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        folder : dict[str, Any]
            Discogs metadata for the newly created collection folder.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "count": <int>,
                    "id": <int>,
                    "name": <str>,
                    "resource_url": <str>
                  }
        """
        self._client._require_authentication(
            "users.create_user_collection_folder"
        )
        return self._client._request(
            "POST",
            f"users/{self._resolve_username(username)}/collection/folder",
            params={"name": self._prepare_string("folder_name", folder_name)},
        ).json()

    @TTLCache.cached_method(ttl="user")
    def get_user_collection_folder(
        self, folder_id: int | str, /, username: str | None = None
    ) -> dict[str, Any]:
        """
        `User Collection > Collection Folder > Get Folders
        <https://www.discogs.com/developers/#page:user-collection,
        header:user-collection-collection-folder-get>`_: Get Discogs
        catalog information for a user's collection folder.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Conditional

                 User authentication
                    Access collection folders that do not have a
                    `folder_id` of :code:`0` if authenticated as the
                    requested user.

        Parameters
        ----------
        folder_id : int or str; positional-only
            Discogs ID of the collection folder.

            **Examples**: :code:`0`, :code:`"3"`.

        username : str; optional
            Username of the user. If not specified, the username of the
            current user is used. Only optional when authenticated.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        folder : dict[str, Any]
            Discogs metadata for the user's collection folder.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "count": <int>,
                    "id": <int>,
                    "name": <str>,
                    "resource_url": <str>
                  }
        """
        self._validate_numeric("folder_id", folder_id, int, 0)
        if int(folder_id) == 0:
            self._client._require_authentication(
                "users.get_user_collection_folder"
            )
        return self._client._request(
            "GET",
            f"users/{self._resolve_username(username)}/collection/folders/{folder_id}",
        ).json()

    def rename_user_collection_folder(
        self,
        folder_id: int | str,
        /,
        folder_name: str,
        *,
        username: str | None = None,
    ) -> dict[str, Any]:
        """
        `User Collection > Collection Folder > Edit Folder
        <https://www.discogs.com/developers/#page:user-collection,
        header:user-collection-collection-folder-post>`_: Rename a
        user's collection folder.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        folder_id : int or str; positional-only
            Discogs ID of the collection folder. The "All"
            (:code:`folder_id=0`) and "Uncategorized"
            (:code:`folder_id=1`) folders cannot be renamed.

            **Examples**: :code:`2`, :code:`"3"`.

        folder_name : str
            New folder name.

            **Example**: :code:`"My favorites"`.

        username : str; keyword-only; optional
            Username of the user. If not specified, the username of the
            current user is used.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        folder : dict[str, Any]
            Discogs metadata for the renamed collection folder.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "count": <int>,
                    "id": <int>,
                    "name": <str>,
                    "resource_url": <str>
                  }
        """
        self._client._require_authentication(
            "users.rename_user_collection_folder"
        )
        self._validate_numeric("folder_id", folder_id, int, 2)
        return self._client._request(
            "POST",
            f"users/{self._resolve_username(username)}/collection/folders/{folder_id}",
            json={"name": self._prepare_string("folder_name", folder_name)},
        ).json()

    def delete_user_collection_folder(
        self, folder_id: int | str, /, username: str | None = None
    ) -> None:
        """
        `User Collection > Collection Folder > Delete Folder
        <https://www.discogs.com/developers/#page:user-collection,
        header:user-collection-collection-folder-delete>`_: Delete a
        user's collection folder.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        folder_id : int or str; positional-only
            Discogs ID of the collection folder.

            **Examples**: :code:`2`, :code:`"3"`. The "All"
            (:code:`folder_id=0`) and "Uncategorized"
            (:code:`folder_id=1`) folders cannot be deleted.

        username : str; optional
            Username of the user. If not specified, the username of the
            current user is used.

            **Example**: :code:`"rodneyfool"`.
        """
        self._client._require_authentication(
            "users.delete_user_collection_folder"
        )
        self._validate_numeric("folder_id", folder_id, int, 2)
        self._client._request(
            "DELETE",
            f"users/{self._resolve_username(username)}"
            f"/collection/folders/{folder_id}",
        )

    @TTLCache.cached_method(ttl="user")
    def get_user_collection_release_instances(
        self, release_id: int | str, /, username: str | None = None
    ) -> dict[str, Any]:
        """
        `User Collection > Collection Items by Release
        <https://www.discogs.com/developers/#page:user-collection,
        header:user-collection-collection-items-by-release>`_: Get
        Discogs catalog information for instances of a release in a
        user's collection.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 User authentication
                    Access private collections if authenticated as the
                    requested user.

        Parameters
        ----------
        release_id : int or str; positional-only
            Discogs ID of the release.

            **Examples**: :code:`772347`, :code:`"7781525"`.

        username : str; optional
            Username of the user. If not specified, the username of the
            current user is used. Only optional when authenticated.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        instances : dict[str, Any]
            Discogs metadata for the release instances in the user's
            collection.

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
                        "basic_information": {
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
                          "formats": [
                            {
                              "descriptions": <list[str]>,
                              "name": <str>,
                              "qty": <str>,
                              "text": <str>
                            }
                          ],
                          "genres": <list[str]>,
                          "id": <int>,
                          "labels": [
                            {
                              "catno": <str>,
                              "entity_type": <str>,
                              "entity_type_name": <str>,
                              "id": <int>,
                              "name": <str>,
                              "resource_url": <str>,
                            }
                          ],
                          "resource_url": <str>,
                          "styles": <list[str]>,
                          "thumb": <str>,
                          "title": <str>,
                          "year": <int>,
                        },
                        "date_added": <str>,
                        "folder_id": <int>,
                        "id": <int>,
                        "instance_id": <int>,
                        "notes": [
                          {
                            "field_id": <int>,
                            "value": <str>
                          }
                        ]
                        "rating": <int>
                      },
                    ]
                  }
        """
        self._validate_numeric("release_id", release_id, int, 1)
        return self._client._request(
            "GET",
            f"users/{self._resolve_username(username)}"
            f"/collection/releases/{release_id}",
        ).json()

    @TTLCache.cached_method(ttl="user")
    def get_user_collection_folder_releases(
        self,
        folder_id: int | str,
        /,
        username: str | None = None,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        `User Collection > Collection Items by Folder
        <https://www.discogs.com/developers/#page:user-collection,
        header:user-collection-collection-items-by-folder>`_: Get
        Discogs catalog information for releases in a user's collection
        folder.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Conditional

                 User authentication
                    Access collection folders that do not have a
                    `folder_id` of :code:`0` if authenticated as the
                    requested user.

        Parameters
        ----------
        folder_id : int or str; positional-only
            Discogs ID of the collection folder.

            **Examples**: :code:`0`, :code:`"3"`.

        username : str; optional
            Username of the user. If not specified, the username of the
            current user is used. Only optional when authenticated.

            **Example**: :code:`"rodneyfool"`.

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
            Page of Discogs metadata for the releases in the user's
            collection folder.

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
                        "basic_information": {
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
                          "formats": [
                            {
                              "descriptions": <list[str]>,
                              "name": <str>,
                              "qty": <str>,
                              "text": <str>
                            }
                          ],
                          "genres": <list[str]>,
                          "id": <int>,
                          "labels": [
                            {
                              "catno": <str>,
                              "entity_type": <str>,
                              "entity_type_name": <str>,
                              "id": <int>,
                              "name": <str>,
                              "resource_url": <str>,
                            }
                          ],
                          "resource_url": <str>,
                          "styles": <list[str]>,
                          "thumb": <str>,
                          "title": <str>,
                          "year": <int>,
                        },
                        "date_added": <str>,
                        "folder_id": <int>,
                        "id": <int>,
                        "instance_id": <int>,
                        "notes": [
                          {
                            "field_id": <int>,
                            "value": <str>
                          }
                        ]
                        "rating": <int>
                      },
                    ]
                  }
        """
        self._validate_numeric("folder_id", folder_id, int, 0)
        if int(folder_id) == 0:
            self._client._require_authentication(
                "users.get_user_collection_folder_releases"
            )
        return self._get_paginated_resources(
            f"users/{self._resolve_username(username)}"
            f"/collection/folders/{folder_id}/releases",
            limit=limit,
            page=page,
        )

    def add_user_collection_release(
        self,
        folder_id: int | str,
        release_id: int | str,
        *,
        username: str | None = None,
    ) -> dict[str, Any]:
        """
        `User Collection > Add to Collection Folder
        <https://www.discogs.com/developers/#page:user-collection,
        header:user-collection-add-to-collection-folder>`_: Add a
        release to a user's collection folder.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        folder_id : int or str
            Discogs ID of the collection folder. The "All" folder
            (:code:`folder_id=0`) is not allowed, but the
            "Uncategorized" folder (:code:`folder_id=1`) is.

            **Examples**: :code:`1`, :code:`"3"`.

        release_id : int or str
            Discogs ID of the release.

            **Examples**: :code:`772347`, :code:`"7781525"`.

        username : str; keyword-only; optional
            Username of the user. If not specified, the username of the
            current user is used.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        instance : dict[str, Any]
            Discogs metadata for the newly added release instance.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "instance_id": <int>,
                    "resource_url": <str>
                  }
        """
        self._client._require_authentication(
            "users.add_user_collection_release"
        )
        self._validate_numeric("folder_id", folder_id, int, 0)
        self._validate_numeric("release_id", release_id, int, 1)
        return self._client._request(
            "POST",
            f"users/{self._resolve_username(username)}"
            f"/collection/folders/{folder_id}/releases/{release_id}",
        ).json()

    def update_user_collection_release_instance(
        self,
        from_folder_id: int | str,
        release_id: int | str,
        instance_id: int | str,
        *,
        to_folder_id: int | str | None = None,
        rating: int | None = None,
        username: str | None = None,
    ) -> None:
        """
        `User Collection > Change Rating of Release
        <https://www.discogs.com/developers/#page:user-collection,
        header:user-collection-change-rating-of-release>`_: Update the
        rating for a release and/or move a release instance to another
        collection folder.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        .. important::

           Either :code:`to_folder_id` or :code:`rating` must be
           specified.

        Parameters
        ----------
        from_folder_id : int or str
            Discogs ID of the collection folder the release instance is
            currently in.

            **Examples**: :code:`0`, :code:`"3"`.

        release_id : int or str
            Discogs ID of the release.

            **Examples**: :code:`772347`, :code:`"7781525"`.

        instance_id : int or str
            Discogs ID of the release instance.

            **Examples**: :code:`130076`, :code:`"130077"`.

        to_folder_id : int or str; keyword-only; optional
            Discogs ID of the collection folder to move the release
            instance to.

            **Examples**: :code:`0`, :code:`"3"`.

        rating : int; keyword-only; optional
            Star rating for the release. Use :code:`0` to reset the
            rating.

            **Valid range**: :code:`0` to :code:`5`.

        username : str; keyword-only; optional
            Username of the user. If not specified, the username of the
            current user is used.

            **Example**: :code:`"rodneyfool"`.
        """
        self._client._require_authentication(
            "users.update_user_collection_release_instance"
        )
        self._validate_numeric("from_folder_id", from_folder_id, int, 0)
        self._validate_numeric("release_id", release_id, int, 1)
        self._validate_numeric("instance_id", instance_id, int, 1)
        payload = {}
        if to_folder_id is not None:
            self._validate_numeric("to_folder_id", to_folder_id, int, 0)
            payload["folder_id"] = to_folder_id
        if rating is not None:
            self._validate_number("rating", rating, int, 0, 5)
            payload["rating"] = rating
        if not payload:
            raise RuntimeError("At least one change must be specified.")
        return self._client._request(
            "POST",
            f"users/{self._resolve_username(username)}"
            f"/collection/folders/{from_folder_id}"
            f"/releases/{release_id}/instances/{instance_id}",
            json=payload,
        ).json()

    def remove_user_collection_release_instance(
        self,
        folder_id: int | str,
        release_id: int | str,
        instance_id: int | str,
        *,
        username: str | None = None,
    ) -> None:
        """
        `User Collection > Delete Instance from Folder
        <https://www.discogs.com/developers/#page:user-collection,
        header:user-collection-delete-instance-from-folder>`_: Remove a
        release instance from a user's collection folder.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        folder_id : int or str
            Discogs ID of the collection folder.

            **Examples**: :code:`0`, :code:`"3"`.

        release_id : int or str
            Discogs ID of the release.

            **Examples**: :code:`772347`, :code:`"7781525"`.

        instance_id : int or str
            Discogs ID of the release instance.

            **Examples**: :code:`130076`, :code:`"130077"`.

        username : str; keyword-only; optional
            Username of the user. If not specified, the username of the
            current user is used.

            **Example**: :code:`"rodneyfool"`.
        """
        self._client._require_authentication(
            "users.remove_user_collection_release_instance"
        )
        self._validate_numeric("folder_id", folder_id, int, 0)
        self._validate_numeric("release_id", release_id, int, 1)
        self._validate_numeric("instance_id", instance_id, int, 1)
        return self._client._request(
            "DELETE",
            f"users/{self._resolve_username(username)}"
            f"/collection/folders/{folder_id}/releases/{release_id}"
            f"/instances/{instance_id}",
        )

    @TTLCache.cached_method(ttl="user")
    def get_user_collection_fields(
        self, username: str | None = None, /
    ) -> dict[str, Any]:
        """
        `User Collection > List Custom Fields <https://www.discogs.com
        /developers/#page:user-collection,
        header:user-collection-list-custom-fields>`_: Get
        Discogs resource information for user-defined collection note
        fields.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 User authentication
                    Access private collections if authenticated as the
                    requested user.

        Parameters
        ----------
        username : str; optional
            Username of the user. If not specified, the username of the
            current user is used. Only optional when authenticated.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        fields : dict[str, Any]
            Discogs metadata for the collection note fields.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "fields": [
                      {
                        "id": <int>,
                        "name": <str>,
                        "options": <list[str]>,
                        "position": <int>,
                        "public": <bool>,
                        "type": <str>
                      }
                    ]
                  }
        """
        return self._client._request(
            "GET",
            f"users/{self._resolve_username(username)}/collection/fields",
        ).json()

    def update_user_collection_release_field(
        self,
        folder_id: int | str,
        release_id: int | str,
        instance_id: int | str,
        field_id: int | str,
        value: str,
        *,
        username: str | None = None,
    ) -> None:
        """
        `User Collection > Edit Fields Instance <https://www.discogs.com
        /developers/#page:user-collection,
        header:user-collection-edit-fields-instance>`_: Update a note
        field for a release instance in a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        folder_id : int or str
            Discogs ID of the collection folder.

            **Examples**: :code:`0`, :code:`"3"`.

        release_id : int or str
            Discogs ID of the release.

            **Examples**: :code:`772347`, :code:`"7781525"`.

        instance_id : int or str
            Discogs ID of the release instance.

            **Examples**: :code:`130076`, :code:`"130077"`.

        field_id : int or str
            Discogs ID of the note field.

            **Examples**: :code:`1`, :code:`"2"`.

        username : str; keyword-only; optional
            Username of the user. If not specified, the username of the
            current user is used.

            **Example**: :code:`"rodneyfool"`.
        """
        self._client._require_authentication(
            "users.update_user_collection_release_field"
        )
        self._validate_numeric("folder_id", folder_id, int, 0)
        self._validate_numeric("release_id", release_id, int, 1)
        self._validate_numeric("instance_id", instance_id, int, 1)
        self._validate_numeric("field_id", field_id, int, 1)
        self._validate_type("value", value, str)
        self._client._request(
            "POST",
            f"users/{self._resolve_username(username)}/collection"
            f"/folders/{folder_id}/releases/{release_id}"
            f"/instances/{instance_id}/fields/{field_id}",
            params={"value": value},
        )

    @TTLCache.cached_method(ttl="user")
    def get_user_collection_value(
        self, username: str | None = None, /
    ) -> dict[str, Any]:
        """
        `User Collection > Collection Value <https://www.discogs.com
        /developers/#page:user-collection,
        header:user-collection-collection-value>`_: Get the estimated
        monetary value of a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access private endpoints.

        Parameters
        ----------
        username : str; optional
            Username of the user. If not specified, the username of the
            current user is used.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        value : dict[str, Any]
            Estimated value of the user's collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "maximum": <str>,
                    "median": <str>,
                    "minimum": <str>
                  }
        """
        return self._client._request(
            "GET",
            f"users/{self._resolve_username(username)}/collection/value",
        ).json()

    @TTLCache.cached_method(ttl="user")
    def get_user_wantlist_releases(
        self,
        username: str | None = None,
        /,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        `User Wantlist > Wantlist <https://www.discogs.com/developers
        /#page:user-wantlist,header:user-wantlist-wantlist>`_: Get
        Discogs catalog information for releases in a user's wantlist.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 User authentication
                    Access private collections if authenticated as the
                    requested user.

        Parameters
        ----------
        username : str; positional-only; optional
            Username of the user. If not specified, the username of the
            current user is used. Only optional when authenticated.

            **Example**: :code:`"rodneyfool"`.

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
            Page of Discogs metadata for the releases in the user's
            wantlist.

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
                    "wants": [
                      {
                        "basic_information": {
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
                          "formats": [
                            {
                              "descriptions": <list[str]>,
                              "name": <str>,
                              "qty": <str>,
                              "text": <str>
                            }
                          ],
                          "genres": <list[str]>,
                          "id": <int>,
                          "labels": [
                            {
                              "catno": <str>,
                              "entity_type": <str>,
                              "entity_type_name": <str>,
                              "id": <int>,
                              "name": <str>,
                              "resource_url": <str>,
                            }
                          ],
                          "resource_url": <str>,
                          "styles": <list[str]>,
                          "thumb": <str>,
                          "title": <str>,
                          "year": <int>,
                        },
                        "id": <int>,
                        "notes": <str>,
                        "rating": <int>
                      }
                    ]
                  }
        """
        return self._get_paginated_resources(
            f"users/{self._resolve_username(username)}/wants",
            limit=limit,
            page=page,
        )

    def add_user_wantlist_release(
        self,
        release_id: int | str,
        /,
        *,
        username: str | None = None,
    ) -> dict[str, Any]:
        """
        `User Wantlist > Add to Wantlist > Add to Wantlist
        <https://www.discogs.com/developers/#page:user-wantlist,
        header:user-wantlist-add-to-wantlist-put>`_: Add a release to a
        user's wantlist.

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

            **Examples**: :code:`772347`, :code:`"7781525"`.

        username : str; keyword-only; optional
            Username of the user. If not specified, the username of the
            current user is used.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        release : dict[str, Any]
            Discogs metadata for the newly added release.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "basic_information": {
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
                      "formats": [
                        {
                          "descriptions": <list[str]>,
                          "name": <str>,
                          "qty": <str>,
                          "text": <str>
                        }
                      ],
                      "genres": <list[str]>,
                      "id": <int>,
                      "labels": [
                        {
                          "catno": <str>,
                          "entity_type": <str>,
                          "entity_type_name": <str>,
                          "id": <int>,
                          "name": <str>,
                          "resource_url": <str>,
                        }
                      ],
                      "resource_url": <str>,
                      "styles": <list[str]>,
                      "thumb": <str>,
                      "title": <str>,
                      "year": <int>,
                    },
                    "id": <int>,
                    "notes": <str>,
                    "rating": <int>
                  }
        """
        self._client._require_authentication("users.add_user_wantlist_release")
        self._validate_numeric("release_id", release_id, int, 1)
        return self._client._request(
            "PUT",
            f"users/{self._resolve_username(username)}/wants/{release_id}",
        ).json()

    def update_user_wantlist_release(
        self,
        release_id: int | str,
        /,
        *,
        notes: str | None = None,
        rating: int | None = None,
        username: str | None = None,
    ) -> dict[str, Any]:
        """
        `User Wantlist > Add to Wantlist > Edit Release in Wantlist
        <https://www.discogs.com/developers/#page:user-wantlist,
        header:user-wantlist-add-to-wantlist-post>`_: Update the notes
        or rating for a release in a user's wantlist.

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

            **Examples**: :code:`772347`, :code:`"7781525"`.

        notes : str; keyword-only; optional
            User notes to associate with the release.

            **Example**: :code:`"My favorite release"`.

        rating : int; keyword-only; optional
            Star rating for the release.

            **Valid range**: :code:`0` to :code:`5`.

            **API default**: :code:`0`.

        username : str; keyword-only; optional
            Username of the user. If not specified, the username of the
            current user is used.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        release : dict[str, Any]
            Discogs metadata for the updated release.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "basic_information": {
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
                      "formats": [
                        {
                          "descriptions": <list[str]>,
                          "name": <str>,
                          "qty": <str>,
                          "text": <str>
                        }
                      ],
                      "genres": <list[str]>,
                      "id": <int>,
                      "labels": [
                        {
                          "catno": <str>,
                          "entity_type": <str>,
                          "entity_type_name": <str>,
                          "id": <int>,
                          "name": <str>,
                          "resource_url": <str>,
                        }
                      ],
                      "resource_url": <str>,
                      "styles": <list[str]>,
                      "thumb": <str>,
                      "title": <str>,
                      "year": <int>,
                    },
                    "id": <int>,
                    "notes": <str>,
                    "rating": <int>
                  }
        """
        self._client._require_authentication(
            "users.update_user_wantlist_release"
        )
        self._validate_numeric("release_id", release_id, int, 1)
        payload = {}
        if notes is not None:
            payload["notes"] = self._prepare_string(
                "notes", notes, allow_blank=True
            )
        if rating is not None:
            self._validate_number("rating", rating, int, 0, 5)
            payload["rating"] = rating
        return self._client._request(
            "POST",
            f"users/{self._resolve_username(username)}/wants/{release_id}",
            json=payload,
        ).json()

    def remove_user_wantlist_release(
        self, release_id: int | str, /, *, username: str | None = None
    ) -> None:
        """
        `User Wantlist > Add to Wantlist > Delete Release from Wantlist
        <https://www.discogs.com/developers/#page:user-wantlist,
        header:user-wantlist-add-to-wantlist-delete>`_: Remove a release
        from a user's wantlist.

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

            **Examples**: :code:`772347`, :code:`"7781525"`.

        username : str; keyword-only; optional
            Username of the user. If not specified, the username of the
            current user is used.

            **Example**: :code:`"rodneyfool"`.
        """
        self._client._require_authentication(
            "users.remove_user_wantlist_release"
        )
        self._client._request(
            "DELETE",
            f"users/{self._resolve_username(username)}/wants/{release_id}",
        )

    @TTLCache.cached_method(ttl="user")
    def get_user_lists(
        self,
        username: str | None = None,
        /,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        `User Lists > User Lists <https://www.discogs.com/developers
        /#page:user-lists,header:user-lists-user-lists>`_: Get
        Discogs catalog information for a user's lists.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 User authentication
                    Access private collections if authenticated as the
                    requested user.

        Parameters
        ----------
        username : str; positional-only; optional
            Username of the user. If not specified, the username of the
            current user is used. Only optional when authenticated.

            **Example**: :code:`"rodneyfool"`.

        limit : int; keyword-only; optional
            Maximum number of lists to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`50`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of lists.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        Returns
        -------
        lists : dict[str, Any]
            Page of Discogs metadata for the user's lists.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "lists": [
                      {
                        "date_added": <str>,
                        "date_changed": <str>,
                        "description": <str>,
                        "id": <int>,
                        "image_url": <str>,
                        "name": <str>,
                        "public": <bool>,
                        "resource_url": <str>,
                        "uri": <str>,
                        "user": {
                          "avatar_url": <str>,
                          "id": <int>,
                          "resource_url": <str>,
                          "username": <str>
                        }
                      }
                    ],
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
                    }
                  }
        """
        return self._get_paginated_resources(
            f"users/{self._resolve_username(username)}/lists",
            limit=limit,
            page=page,
        )

    @TTLCache.cached_method(ttl="user")
    def get_user_list(self, list_id: int | str, /) -> dict[str, Any]:
        """
        `User Lists > List <https://www.discogs.com/developers
        /#page:user-lists,header:user-lists-list>`_: Get Discogs catalog
        information for a user's list and the releases in it.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 User authentication
                    Access private collections if authenticated as the
                    list's owner.

        Parameters
        ----------
        list_id : int or str; positional-only
            Discogs ID of the list.

            **Examples**: :code:`123`, :code:`"321"`.

        Returns
        -------
        list : dict[str, Any]
            Discogs metadata for the user's list and the items in it.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "date_added": <str>,
                    "date_changed": <str>,
                    "description": <str>,
                    "id": <int>,
                    "image_url": <str>,
                    "items": [
                      {
                        "comment": <str>,
                        "display_title": <str>,
                        "id": <int>,
                        "image_url": <str>,
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
                        "type": "release",
                        "uri": <str>
                      }
                    ],
                    "name": <str>,
                    "public": <bool>,
                    "resource_url": <str>,
                    "uri": <str>,
                    "user": {
                      "avatar_url": <str>,
                      "id": <int>,
                      "resource_url": <str>,
                      "username": <str>
                    }
                  }
        """
        self._validate_numeric("list_id", list_id, int, 1)
        return self._client._request("GET", f"lists/{list_id}").json()
