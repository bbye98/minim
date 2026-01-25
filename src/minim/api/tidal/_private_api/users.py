from typing import Any

from ..._shared import TTLCache
from ._shared import PrivateTIDALResourceAPI


class PrivateUsersAPI(PrivateTIDALResourceAPI):
    """
    User Collections and Users API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPIClient`
       and should not be instantiated directly.
    """

    _SORT_FIELDS = {"DATE", "NAME"}

    @staticmethod
    def _prepare_mix_ids(
        mix_ids: str | list[str], /, *, limit: int = 100
    ) -> str:
        """
        Normalize, validate, and serialize TIDAL mix IDs.

        Parameters
        ----------
        mix_ids : int, str, or list[str]; positional-only
            Comma-separated string or list of mix IDs.

        limit : int; keyword-only, default: :code:`100`
            Maximum number of mix IDs that can be sent in the request.

        Returns
        -------
        mix_ids : str
            Comma-separated string of mix IDs.
        """
        if not mix_ids:
            raise ValueError("At least one mix ID must be specified.")

        if isinstance(mix_ids, str):
            return PrivateUsersAPI._prepare_mix_ids(
                mix_ids.split(","), limit=limit
            )

        num_ids = len(mix_ids)
        if num_ids > limit:
            raise ValueError(
                f"A maximum of {limit} mix IDs can be sent in a request."
            )
        for id_ in mix_ids:
            if not isinstance(id_, str) or len(id_) != 30:
                raise ValueError(f"Invalid mix ID {id_!r}.")
        return ",".join(mix_ids)

    def _get_blocked_resources(
        self,
        resource_type: str,
        user_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for resources blocked by a user.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        resources : dict[str, Any]
            Page of TIDAL content metadata for resources blocked by the
            user.
        """
        if user_id is None:
            user_id = self._client._resolve_user_identifier()
        params = {}
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"v1/users/{user_id}/blocks/{resource_type}", params=params
        ).json()

    def _manage_blocked_resources(
        self,
        method: str,
        resource_type: str,
        resource_id: int | str,
        /,
        user_id: int | str | None = None,
    ) -> None:
        """
        Block or unblock a resource for a user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        resource_id : int or str; positional-only
            TIDAL ID of the resource.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        if user_id is None:
            user_id = self._client._resolve_user_identifier()
        if method == "POST":
            self._client._request(
                "POST",
                f"v1/users/{user_id}/blocks/{resource_type}s",
                data={f"{resource_type}Id": resource_id},
            )
        else:
            self._client._request(
                "DELETE",
                f"v1/users/{user_id}/blocks/{resource_type}s/{resource_id}",
            )

    def _get_saved_resources(
        self,
        resource_type: str,
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for items of a specific resource
        type in a user's collection.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"tracks"`, :code:`"videos"`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the items by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Item name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        items : dict[str, Any]
            Page of TIDAL catalog information for items in the user's
            collection.
        """
        if user_id is None:
            user_id = self._client._resolve_user_identifier()
        params = {}
        self._client._resolve_country_code(country_code, params)
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        if sort_by is not None:
            if sort_by not in self._SORT_FIELDS:
                sort_fields_str = "', '".join(sorted(self._SORT_FIELDS))
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. "
                    f"Valid values: '{sort_fields_str}'."
                )
            params["order"] = sort_by
        if descending is not None:
            self._validate_type("descending", descending, bool)
            params["orderDirection"] = "DESC" if descending else "ASC"
        return self._client._request(
            "GET",
            f"v1/users/{user_id}/favorites/{resource_type}",
            params=params,
        ).json()

    def _save_resources(
        self,
        resource_type: str,
        item_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        on_missing: str | None = None,
    ) -> None:
        """
        Add items of a specific resource type to a user's collection.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"tracks"`, :code:`"videos"`.

        item_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of the items.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        on_missing : str; keyword-only; optional
            Behavior when the items to be favorited cannot be found in
            the TIDAL catalog.

            **API default**: :code:`"FAIL"`.
        """
        if user_id is None:
            user_id = self._client._resolve_user_identifier()
        if country_code is None:
            country_code = self._client._my_country_code
        else:
            self._validate_country_code(country_code)
        data = {
            f"{resource_type[:-1]}Ids": self._prepare_tidal_ids(
                item_ids, limit=1_000
            )
        }
        if on_missing is not None:
            self._validate_type("on_missing", on_missing, str)
            on_missing = on_missing.strip().upper()
            if on_missing not in {"FAIL", "SKIP"}:
                raise ValueError(
                    f"Invalid behavior {on_missing!r} for missing "
                    "items. Valid values: 'FAIL', 'SKIP'."
                )
            data["onArtifactNotFound"] = on_missing
        self._client._request(
            "POST",
            f"v1/users/{user_id}/favorites/{resource_type}",
            params={"countryCode": country_code},
            data=data,
        )

    def _remove_saved_resources(
        self,
        resource_type: str,
        item_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        """
        Remove items of a specific resource type from a user's
        collection.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"tracks"`, :code:`"videos"`.

        item_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of the items.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        if user_id is None:
            user_id = self._client._resolve_user_identifier()
        self._client._request(
            "DELETE",
            f"v1/users/{user_id}/favorites/{resource_type}"
            f"/{self._prepare_tidal_ids(item_ids, limit=1_000)}",
        )

    def _get_user_relationship(
        self,
        resource_type: str,
        relationship: str,
        user_id: int | str | None = None,
        /,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a resource related to a user.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

        relationship : str; positional-only
            Related resource type.

        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        limit : int; keyword-only; default: :code:`50`
            Maximum number of items to return.

        Returns
        -------
        resource : dict[str, Any]
            TIDAL content metadata for the related resource.
        """
        if user_id is None:
            user_id = self._client._resolve_user_identifier()
        params = {}
        if cursor is not None:
            self._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        return self._client._request(
            f"v2/{resource_type}/{user_id}/{relationship}", params=params
        ).json()

    def _get_my_playlists(
        self,
        subresource: str,
        /,
        *,
        cursor: str | None = None,
        limit: int = 50,
        playlist_types: str | list[str] | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for playlist folders and/or
        playlists in the current user's collection.

        Parameters
        ----------
        subresource : str; positional-only
            Subresource of the endpoint to call.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        limit : int; keyword-only; default: :code:`50`
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

        playlist_types : str or list[str]; keyword-only; optional
            Playlist types to return. If not specified, all playlists
            are returned.

            **Valid values**:

            * :code:`"FOLDER"` – Playlist folders.
            * :code:`"PLAYLIST"` – All playlists.
            * :code:`"FAVORITE_PLAYLIST"` – Favorited playlists.
            * :code:`"USER_PLAYLIST"` – User-created playlists.

            **Examples**: :code:`"USER_PLAYLIST"`,
            :code:`"FOLDER,USER_PLAYLIST"`,
            :code:`["FOLDER", "USER_PLAYLIST"]`.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Playlist name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        params : dict[str, Any]; keyword-only; optional
            Dictionary of additional query parameters to include in the
            request. If not provided, a new dictionary will be created.

            .. note::

               This `dict` is mutated in-place.

        Returns
        -------
        playlists : dict[str, Any]
            Page of TIDAL content metadata for the playlist folders
            and/or playlists in the current user's collection.
        """
        self._validate_number("limit", limit, int, 1, 50)
        if params is None:
            params = {"limit": limit}
        else:
            params["limit"] = limit
        if cursor is not None:
            self._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        if playlist_types is not None:
            self._client.playlists._validate_types(playlist_types)
            params["includeOnly"] = playlist_types
        if sort_by is not None:
            if sort_by not in self._SORT_FIELDS:
                sort_fields_str = "', '".join(sorted(self._SORT_FIELDS))
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. "
                    f"Valid values: '{sort_fields_str}'."
                )
            params["order"] = sort_by
        if descending is not None:
            self._validate_type("descending", descending, bool)
            params["orderDirection"] = "DESC" if descending else "ASC"
        return self._client._request(
            "GET", f"v2/my-collection/{subresource}", params=params
        ).json()

    def _get_user_playlists(
        self,
        subresource: str,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for playlists in a user's
        collection.

        Parameters
        ----------
        subresource : str; positional-only
            Subresource of the endpoint to call.

        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Playlist name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of TIDAL catalog information for playlists in the
            user's collection.
        """
        if user_id is None:
            user_id = self._client._resolve_user_identifier()
        params = {}
        self._client._resolve_country_code(country_code, params)
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        if sort_by is not None:
            if sort_by not in self._SORT_FIELDS:
                sort_fields_str = "', '".join(sorted(self._SORT_FIELDS))
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. "
                    f"Valid values: '{sort_fields_str}'."
                )
            params["order"] = sort_by
        if descending is not None:
            self._validate_type("descending", descending, bool)
            params["orderDirection"] = "DESC" if descending else "ASC"
        return self._client._request(
            "GET", f"v1/users/{user_id}/{subresource}", params=params
        ).json()

    def _manage_followed_users(
        self, method: str, user_id: int | str, /
    ) -> None:
        """
        Follow or unfollow a TIDAL user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

            **Valid values**: :code:`"PUT"`, :code:`"DELETE"`.

        user_id : int or str; positional-only
            TIDAL ID of the user.
        """
        self._validate_tidal_ids(user_id, _recursive=False)
        self._client._request(
            method, "v2/follow", params={"trn": f"trn:user:{user_id}"}
        )

    def _manage_blocked_users(
        self, method: str, user_id: int | str, /
    ) -> None:
        """
        Block or unblock a TIDAL user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

            **Valid values**: :code:`"PUT"`, :code:`"DELETE"`.

        user_id : int or str; positional-only
            TIDAL ID of the user.
        """
        self._validate_tidal_ids(user_id, _recursive=False)
        self._client._request(method, f"v2/profiles/block/{user_id}")

    @TTLCache.cached_method(ttl="static")
    def get_me(self) -> dict[str, Any]:
        """
        Get profile information for the current user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Returns
        -------
        profile : dict[str, Any]
            Current user's profile information.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "acceptedEULA": <bool>,
                    "accountLinkCreated": <bool>,
                    "address": <str>,
                    "appleUid": <int>,
                    "birthday": <int>,
                    "channelId": <int>,
                    "city": <str>,
                    "countryCode": <str>,
                    "created": <int>,
                    "email": <str>,
                    "emailVerified": <bool>,
                    "facebookUid": <int>,
                    "firstName": <str>,
                    "fullName": <str>,
                    "googleUid": <int>,
                    "lastName": <str>,
                    "newUser": <bool>,
                    "nickname": <str>,
                    "parentId": <int>,
                    "phoneNumber": <str>,
                    "postalcode": <str>,
                    "updated": <int>,
                    "usState": <str>,
                    "userId": <int>,
                    "username": <str>
                  }
        """
        self._client._require_authentication("users.get_me")
        return self._client._request(
            "GET", "https://login.tidal.com/oauth2/me"
        ).json()

    @TTLCache.cached_method(ttl="static")
    def get_session(self) -> dict[str, Any]:
        """
        Get information about the current private TIDAL API session.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access client, session, and user account
                    information.

        Returns
        -------
        session : dict[str, Any]
            Session information.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "channelId": <int>,
                    "client": {
                      "authorizedForOffline": <bool>,
                      "authorizedForOfflineDate": <str>,
                      "id": <int>,
                      "name": <str>
                    },
                    "countryCode": <str>,
                    "partnerId": <int>
                    "sessionId": <str>,
                    "userId": <int>
                  }
        """
        self._client._require_authentication("users.get_session")
        return self._client._request("GET", "v1/sessions").json()

    @TTLCache.cached_method(ttl="user")
    def get_clients(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Get information about a user's TIDAL clients.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access client, session, and user account
                    information.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        clients : dict[str, Any]
            Information about the user's TIDAL clients.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "items": [
                      {
                        "application": {
                          "name": <str>,
                          "service": "TIDAL",
                          "type": {
                            "name": <str>
                          }
                        },
                        "authorizedForOffline": <bool>,
                        "authorizedForOfflineDate": <str>,
                        "created": <str>,
                        "id": <int>,
                        "lastLogin": <str>,
                        "name": <str>,
                        "numberOfOfflineAlbums": <int>,
                        "numberOfOfflinePlaylists": <int>,
                        "uniqueKey": <str>
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("users.get_clients")
        if user_id is None:
            user_id = self._client._resolve_user_identifier()
        return self._get_resource_relationship(
            "users", user_id, "clients", country_code=country_code
        )

    @TTLCache.cached_method(ttl="user")
    def get_subscription(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Get information about a user's TIDAL subscription status.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access client, session, and user account
                    information.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        subscription : dict[str, Any]
            Information about the user's TIDAL subscription status.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "canGetTrial": <bool>,
                    "highestSoundQuality": <str>,
                    "paymentOverdue": <bool>,
                    "paymentType": <str>,
                    "premiumAccess": <bool>,
                    "startDate": <str>,
                    "status": <str>,
                    "subscription": {
                      "offlineGracePeriod": <int>,
                      "type": <str>
                    },
                    "validUntil": <str>
                  }
        """
        self._client._require_authentication("users.get_subscription")
        if user_id is None:
            user_id = self._client._resolve_user_identifier()
        return self._get_resource_relationship(
            "users", user_id, "subscription", country_code=country_code
        )

    @TTLCache.cached_method(ttl="user")
    def get_saved_item_ids(
        self, user_id: int | str | None = None, /
    ) -> dict[str, list[str]]:
        """
        Get TIDAL IDs or UUIDs of the albums, artists, playlists,
        tracks, and videos in a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        Returns
        -------
        ids : `dict`
            IDs or UUIDs of the items in the current user's collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "ALBUM": <list[str]>,
                    "ARTIST": <list[str]>,
                    "PLAYLIST": <list[str]>,
                    "TRACK": <list[str]>,
                    "VIDEO": <list[str]>,
                  }
        """
        self._client._require_authentication("users.get_saved_item_ids")
        return self._get_saved_resources("ids", user_id)

    @TTLCache.cached_method(ttl="user")
    def get_saved_albums(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for albums in a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of albums to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first album to return. Use with `limit` to get
            the next batch of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the albums by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Album name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        albums : dict[str, Any]
            Page of TIDAL content metadata for albums in the user's
            collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created": <str>,
                        "item": {
                          "adSupportedStreamReady": <bool>,
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": <str>,
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "artists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "audioModes": <list[str]>,
                          "audioQuality": <str>,
                          "copyright": <str>,
                          "cover": <str>,
                          "djReady": <bool>,
                          "duration": <int>,
                          "explicit": <bool>
                          "id": <int>,
                          "mediaMetadata": {
                            "tags": <list[str]>
                          },
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "numberOfVolumes": <int>,
                          "payToStream": <bool>,
                          "popularity": <int>,
                          "premiumStreamingOnly": <bool>,
                          "releaseDate": <str>,
                          "stemReady": <bool>,
                          "streamReady": <bool>,
                          "streamStartDate": <str>,
                          "title": <str>,
                          "type": "ALBUM",
                          "upc": <str>,
                          "upload": <bool>,
                          "url": <str>,
                          "version": <str>,
                          "vibrantColor": <str>,
                          "videoCover": <str>
                        }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("users.get_saved_albums")
        return self._get_saved_resources(
            "albums",
            user_id,
            country_code=country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    def save_albums(
        self,
        album_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        on_missing: str | None = None,
    ) -> None:
        """
        Add albums to a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        album_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of the albums.

            **Examples**: :code:`46369321`, :code:`"251380836"`,
            :code:`"46369321,251380836"`,
            :code:`[46369321, "251380836"]`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        on_missing : str; keyword-only; optional
            Behavior when the albums to be favorited cannot be found in
            the TIDAL catalog.

            **API default**: :code:`"FAIL"`.
        """
        self._client._require_authentication("users.save_albums")
        return self._save_resources(
            "albums",
            album_ids,
            user_id=user_id,
            country_code=country_code,
            on_missing=on_missing,
        )

    def remove_saved_albums(
        self,
        album_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        """
        Remove albums from a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        album_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of the albums.

            **Examples**: :code:`46369321`, :code:`"251380836"`,
            :code:`"46369321,251380836"`,
            :code:`[46369321, "251380836"]`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_authentication("users.remove_saved_albums")
        return self._remove_saved_resources(
            "albums", album_ids, user_id=user_id
        )

    @TTLCache.cached_method(ttl="user")
    def get_blocked_artists(
        self,
        user_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for artists blocked by a user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        limit : int; keyword-only; optional
            Maximum number of artists to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first artist to return. Use with `limit` to get
            the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        artists : dict[str, Any]
            Page of TIDAL content metadata for artists blocked by the
            user.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created": <str>,
                        "item": {
                          "artistRoles": [
                            {
                              "category": <str>,
                              "categoryId": <int>
                            }
                          ],
                          "artistTypes": <list[str]>,
                          "banner": <str>,
                          "handle": <str>,
                          "id": <int>,
                          "mixes": {
                            "ARTIST_MIX": <str>
                          },
                          "name": <str>,
                          "picture": <str>,
                          "popularity": <int>,
                          "selectedAlbumCoverFallback": None,
                          "spotlighted": <bool>,
                          "type": <str>,
                          "url": <str>,
                          "userId": <int>
                        },
                        "type": "ARTIST"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("users.get_blocked_artists")
        return self._get_blocked_resources(
            "artists", user_id, limit=limit, offset=offset
        )

    def block_artist(
        self, artist_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        """
        Block an artist for a user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_authentication("users.block_artist")
        self._manage_blocked_resources(
            "POST", "artist", artist_id, user_id=user_id
        )

    def unblock_artist(
        self, artist_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        """
        Unblock an artist for a user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_authentication("users.unblock_artist")
        self._manage_blocked_resources(
            "DELETE", "artist", artist_id, user_id=user_id
        )

    @TTLCache.cached_method(ttl="user")
    def get_followed_artists(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for artists in a user's
        collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of artists to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first artist to return. Use with `limit` to get
            the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the albums by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Artist name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        artists : dict[str, Any]
            Page of TIDAL content metadata for artists in the user's
            collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created": <str>,
                        "item": {
                          "artistRoles": [
                            {
                              "category": <str>,
                              "categoryId": <int>
                            }
                          ],
                          "artistTypes": <list[str]>,
                          "handle": <str>,
                          "id": <int>,
                          "mixes": {
                            "ARTIST_MIX": <str>
                          },
                          "name": <str>,
                          "picture": <str>,
                          "popularity": <int>,
                          "selectedAlbumCoverFallback": None,
                          "spotlighted": <bool>,
                          "url": <str>,
                          "userId": <int>
                        }
                      }
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("users.get_followed_artists")
        return self._get_saved_resources(
            "artists",
            user_id,
            country_code=country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    def follow_artists(
        self,
        artist_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        on_missing: str | None = None,
    ) -> None:
        """
        Add artists to a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        artist_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of the artists.

            **Examples**: :code:`1566`, :code:`"4676988"`,
            :code:`"1566,4676988"`, :code:`[1566, "4676988"]`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        on_missing : str; keyword-only; optional
            Behavior when the artists to be favorited cannot be found in
            the TIDAL catalog.

            **API default**: :code:`"FAIL"`.
        """
        self._client._require_authentication("users.follow_artists")
        return self._save_resources(
            "artists",
            artist_ids,
            user_id=user_id,
            country_code=country_code,
            on_missing=on_missing,
        )

    def unfollow_artists(
        self,
        artist_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        """
        Remove artists from a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        artist_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of the artists.

            **Examples**: :code:`1566`, :code:`"4676988"`,
            :code:`"1566,4676988"`, :code:`[1566, "4676988"]`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_authentication("users.unfollow_artists")
        return self._remove_saved_resources(
            "artists", artist_ids, user_id=user_id
        )

    @TTLCache.cached_method(ttl="user")
    def get_my_followed_mixes(
        self,
        *,
        limit: int = 50,
        cursor: str | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for mixes in the current user's
        collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        limit : int; keyword-only; default: :code:`50`
            Maximum number of mixes to return.

            **Valid range**: :code:`1` to :code:`50`.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        sort_by : str; keyword-only; optional
            Field to sort the mixes by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Mix name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        mixes : dict[str, Any]
            Page of TIDAL content metadata for mixes in the current
            user's collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "cursor": <str>,
                    "items": [
                      {
                        "dateAdded": <str>,
                        "detailImages": {
                          "LARGE": {
                            "height": <int>,
                            "url": <str>,
                            "width": <int>
                          },
                          "MEDIUM": {
                            "height": <int>,
                            "url": <str>,
                            "width": <int>
                          },
                          "SMALL": {
                            "height": <int>,
                            "url": <str>,
                            "width": <int>
                          }
                        },
                        "id": <str>,
                        "images": {
                          "LARGE": {
                            "height": <int>,
                            "url": <str>,
                            "width": <int>
                          },
                          "MEDIUM": {
                            "height": <int>,
                            "url": <str>,
                            "width": <int>
                          },
                          "SMALL": {
                            "height": <int>,
                            "url": <str>,
                            "width": <int>
                          }
                        },
                        "master": <bool>,
                        "mixType": <str>,
                        "subTitle": <str>,
                        "subTitleTextInfo": {
                          "color": <str>,
                          "text": <str>
                        },
                        "title": <str>,
                        "titleTextInfo": {
                          "color": <str>,
                          "text": <str>
                        },
                        "updated": <str>
                      }
                    ],
                    "lastModifiedAt": <str>
                  }
        """
        self._client._require_authentication("users.get_my_followed_mixes")
        self._validate_number("limit", limit, int, 1, 50)
        params = {"limit": limit}
        if cursor is not None:
            self._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        if sort_by is not None:
            if sort_by not in self._SORT_FIELDS:
                sort_fields_str = "', '".join(sorted(self._SORT_FIELDS))
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. "
                    f"Valid values: '{sort_fields_str}'."
                )
            params["order"] = sort_by
        if descending is not None:
            self._validate_type("descending", descending, bool)
            params["orderDirection"] = "DESC" if descending else "ASC"
        return self._client._request(
            "GET", "v2/favorites/mixes", params=params
        ).json()

    @TTLCache.cached_method(ttl="user")
    def get_my_followed_mix_ids(
        self, *, limit: int = 50, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        Get TIDAL IDs of the mixes in the current user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        limit : int; keyword-only; default: :code:`50`
            Maximum number of mix IDs to return.

            **Valid range**: :code:`1` to :code:`50`.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        Returns
        -------
        mix_ids : dict[str, Any]
            Page of TIDAL IDs of the mixes in the user's collection.

            **Sample response**:
            :code:`{"content": <list[str]>, "cursor": <str>}`
        """
        self._client._require_authentication("users.get_my_followed_mix_ids")
        self._validate_number("limit", limit, int, 1, 50)
        params = {"limit": limit}
        if cursor is not None:
            self._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET", "v2/favorites/mixes/ids", params=params
        ).json()

    def follow_mixes(
        self, mix_ids: str | list[str], /, *, on_missing: str | None = None
    ) -> None:
        """
        Add mixes to the current user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        mix_ids : str or list[str]; positional-only
            TIDAL IDs of the mixes.

            **Examples**:

            * :code:`"000ec0b01da1ddd752ec5dee553d48"`
            * :code:`"000ec0b01da1ddd752ec5dee553d48,000dd748ceabd5508947c6a5d3880a"`
            * :code:`["000ec0b01da1ddd752ec5dee553d48",
              "000dd748ceabd5508947c6a5d3880a"]`

        on_missing : str; keyword-only; optional
            Behavior when the mixes to be favorited cannot be found in
            the TIDAL catalog.

            **API default**: :code:`"FAIL"`.
        """
        self._client._require_authentication("users.follow_mixes")
        data = {"mixIds": self._prepare_mix_ids(mix_ids)}
        if on_missing is not None:
            self._validate_type("on_missing", on_missing, str)
            on_missing = on_missing.strip().upper()
            if on_missing not in {"FAIL", "SKIP"}:
                raise ValueError(
                    f"Invalid behavior {on_missing!r} for missing "
                    "items. Valid values: 'FAIL', 'SKIP'."
                )
            data["onArtifactNotFound"] = on_missing
        self._client._request("PUT", "v2/favorites/mixes/add", data=data)

    def unfollow_mixes(self, mix_ids: str | list[str], /) -> None:
        """
        Remove mixes from the current user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        mix_ids : str or list[str]; positional-only
            TIDAL IDs of the mixes.

            **Examples**:

            * :code:`"000ec0b01da1ddd752ec5dee553d48"`
            * :code:`"000ec0b01da1ddd752ec5dee553d48,000dd748ceabd5508947c6a5d3880a"`
            * :code:`["000ec0b01da1ddd752ec5dee553d48",
              "000dd748ceabd5508947c6a5d3880a"]`
        """
        self._client._require_authentication("users.unfollow_mixes")
        self._client._request(
            "PUT",
            "v2/favorites/mixes/remove",
            data={"mixIds": self._prepare_mix_ids(mix_ids)},
        )

    @TTLCache.cached_method(ttl="user")
    def get_followed_playlists(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for editorial playlists in a
        user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Playlist name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of TIDAL content metadata for editorial playlists in
            the user's collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created": <str>,
                        "item": {
                          "created": <str>,
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos":<int>,
                          "popularity": <int>,
                          "promotedArtists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "publicPlaylist": <bool>,
                          "squareImage": <str>,
                          "title": <str>,
                          "type": <str>,
                          "url": <str>,
                          "uuid": <str>
                        }
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("users.get_followed_playlists")
        return self._get_saved_resources(
            "playlists",
            user_id,
            country_code=country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    def follow_playlists(
        self,
        playlist_uuids: str | list[str],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        folder_uuid: str | None = None,
        api_version: int = 2,
    ) -> None:
        """
        Add playlists to a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access user recommendations, and view and modify
                    user's collection.

        Parameters
        ----------
        playlist_uuids : str or list[str]; positional-only; optional
            Playlist UUIDs.

            **Examples**:

            * :code:`"0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`
            * :code:`"0ae80812-f8d6-4fc4-90ea-b2df4ecc3861,24c9cc46-2fcd-4afb-bcc6-d6c42315f32e"`
            * :code:`["0ae80812-f8d6-4fc4-90ea-b2df4ecc3861",
              "24c9cc46-2fcd-4afb-bcc6-d6c42315f32e"]`

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used. Only applicable when `version` is
            :code:`1`.

            **Example**: :code:`"US"`.

        folder_uuid : str; keyword-only; optional
            UUID of the TIDAL playlist folder to add playlists to. Use
            :code:`"root"` or leave blank to target the top-level
            "Playlists" folder. Only applicable when `version` is
            :code:`2`.

        api_version : int; keyword-only; default: :code:`2`
            Private TIDAL API version.

            **Valid values**:

            * :code:`1` – Legacy
              :code:`POST /v1/users/{user_id}/favorites/playlists`
              endpoint.
            * :code:`2` – Current
              :code:`PUT /v2/my-collection/playlists/folders/add-favorites`
              endpoint.
        """
        self._client._require_authentication("users.follow_playlists")
        params = {"uuids": self._prepare_uuids("playlist", playlist_uuids)}
        self._validate_number("api_version", api_version, int, 1, 2)
        if api_version == 1:
            if user_id is None:
                user_id = self._client._resolve_user_identifier()
            if country_code is None:
                country_code = self._client._my_country_code
            else:
                self._validate_country_code(country_code)
            self._client._request(
                "POST",
                f"v1/users/{user_id}/favorites/playlists",
                params={"countryCode": country_code},
                data=params,
            )
        else:
            if folder_uuid is not None:
                if folder_uuid != "root":
                    self._validate_uuid(folder_uuid)
                params["folderId"] = folder_uuid
            self._client._request(
                "PUT",
                "v2/my-collection/playlists/folders/add-favorites",
                params=params,
            )

    def unfollow_playlists(
        self,
        playlist_uuids: str | list[str],
        /,
        *,
        user_id: int | str | None = None,
        api_version: int = 2,
    ) -> None:
        """
        Remove playlists from a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        playlist_uuids : str or list[str]; positional-only; optional
            Playlist UUIDs. TIDAL resource names may be provided
            only when :code:`version=2`.

            **Examples**:

            * :code:`"trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`
            * :code:`"trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861,24c9cc46-2fcd-4afb-bcc6-d6c42315f32e"`
            * :code:["trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861",
              "24c9cc46-2fcd-4afb-bcc6-d6c42315f32e"]

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used. Only applicable when `version` is
            :code:`1`.

        api_version : int; keyword-only; default: :code:`2`
            Private TIDAL API version.

            **Valid values**:

            * :code:`1` – Legacy
              :code:`POST /v1/users/{user_id}/favorites/playlists`
              endpoint.
            * :code:`2` – Current
              :code:`PUT /v2/my-collection/playlists/folders/add-favorites`
              endpoint.
        """
        self._client._require_authentication("users.unfollow_playlists")
        self._validate_number("api_version", api_version, int, 1, 2)
        if api_version == 1:
            if user_id is None:
                user_id = self._client._resolve_user_identifier()
            self._client._request(
                "DELETE",
                f"v1/users/{user_id}/favorites/playlists"
                f"/{self._prepare_uuids('playlist', playlist_uuids)}",
            )
        else:
            self._client._request(
                "PUT",
                "v2/my-collection/playlists/folders/remove",
                params={
                    "trns": self._prepare_uuids(
                        "playlist", playlist_uuids, has_prefix=True
                    )
                },
            )

    @TTLCache.cached_method(ttl="user")
    def get_my_playlists(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        playlist_types: str | list[str] | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for playlists in the current
        user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        limit : int; keyword-only; default: :code:`50`
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

        playlist_types : str or list[str]; keyword-only; optional
            Playlist types to return. If not specified, all playlists
            are returned.

            **Valid values**:

            * :code:`"FOLDER"` – Playlist folders.
            * :code:`"PLAYLIST"` – All playlists.
            * :code:`"FAVORITE_PLAYLIST"` – Favorited playlists.
            * :code:`"USER_PLAYLIST"` – User-created playlists.

            **Examples**: :code:`"USER_PLAYLIST"`,
            :code:`"FOLDER,USER_PLAYLIST"`,
            :code:`["FOLDER", "USER_PLAYLIST"]`.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Playlist name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of TIDAL content metadata for the playlists in the
            current user's collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "cursor": <str>,
                    "items": [
                      {
                        "addedAt": <str>,
                        "data": {
                          "createdAt": <str>,
                          "id": <str>,
                          "itemType": "FOLDER",
                          "lastModifiedAt": <str>,
                          "name": <str>,
                          "totalNumberOfItems": <int>,
                          "trn": <str>,
                        },
                        "itemType": "FOLDER",
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "parent": {
                          "id": <str>,
                          "name": <str>
                        },
                        "trn": <str>,
                      },
                      {
                        "addedAt": <str>,
                        "data": {
                          "contentBehavior": <str>,
                          "created": <str>,
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "curators": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>
                            }
                          ],
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "itemType": "PLAYLIST",
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "promotedArtists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>
                            }
                          ],
                          "sharingLevel": <str>,
                          "source": <str>,
                          "squareImage": <str>,
                          "status": <str>,
                          "title": <str>,
                          "trn": <str>,
                          "type": <str>,
                          "url": <str>,
                          "uuid": <str>
                        },
                        "itemType": "PLAYLIST",
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "parent": {
                          "id": <str>,
                          "name": <str>
                        },
                        "trn": <str>
                      }
                    ],
                    "lastModifiedAt": <str>
                  }
        """
        self._client._require_authentication("playlists.get_my_playlists")
        return self._get_my_playlists(
            "playlists",
            cursor=cursor,
            limit=limit,
            playlist_types=playlist_types,
            sort_by=sort_by,
            descending=descending,
        )

    @TTLCache.cached_method(ttl="user")
    def get_my_folder(
        self,
        folder_uuid: str | None = None,
        /,
        *,
        cursor: str | None = None,
        limit: int = 50,
        playlist_types: str | list[str] | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for playlists in a playlist folder
        in the current user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        folder_uuid : str; positional-only; optional
            UUID of TIDAL playlist folder to retrieve playlists from.
            Use :code:`"root"` or leave blank to target the top-level
            "Playlists" folder.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        limit : int; keyword-only; default: :code:`50`
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

        playlist_types : str or list[str]; keyword-only; optional
            Playlist types to return. If not specified, all playlists
            are returned.

            **Valid values**:

            * :code:`"FOLDER"` – Playlist folders.
            * :code:`"PLAYLIST"` – All playlists.
            * :code:`"FAVORITE_PLAYLIST"` – Favorited playlists.
            * :code:`"USER_PLAYLIST"` – User-created playlists.

            **Examples**: :code:`"USER_PLAYLIST"`,
            :code:`"FOLDER,USER_PLAYLIST"`,
            :code:`["FOLDER", "USER_PLAYLIST"]`.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Playlist name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of TIDAL content metadata for the playlists in the
            specified playlist folder in the current user's collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "cursor": <str>,
                    "items": [
                      {
                        "addedAt": <str>,
                        "data": {
                          "createdAt": <str>,
                          "id": <str>,
                          "itemType": "FOLDER",
                          "lastModifiedAt": <str>,
                          "name": <str>,
                          "totalNumberOfItems": <int>,
                          "trn": <str>,
                        },
                        "itemType": "FOLDER",
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "parent": {
                          "id": <str>,
                          "name": <str>
                        },
                        "trn": <str>,
                      },
                      {
                        "addedAt": <str>,
                        "data": {
                          "contentBehavior": <str>,
                          "created": <str>,
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "curators": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>
                            }
                          ],
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "itemType": "PLAYLIST",
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "promotedArtists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>
                            }
                          ],
                          "sharingLevel": <str>,
                          "source": <str>,
                          "squareImage": <str>,
                          "status": <str>,
                          "title": <str>,
                          "trn": <str>,
                          "type": <str>,
                          "url": <str>,
                          "uuid": <str>
                        },
                        "itemType": "PLAYLIST",
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "parent": {
                          "id": <str>,
                          "name": <str>
                        },
                        "trn": <str>
                      }
                    ],
                    "lastModifiedAt": <str>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("playlists.get_my_folder")
        params = {}
        if folder_uuid is not None:
            if folder_uuid != "root":
                self._validate_uuid(folder_uuid)
            params["folderId"] = folder_uuid
        return self._get_my_playlists(
            "playlists/folders",
            cursor=cursor,
            limit=limit,
            playlist_types=playlist_types,
            sort_by=sort_by,
            descending=descending,
            params=params,
        )

    @TTLCache.cached_method(ttl="user")
    def get_my_folders_and_playlists(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        playlist_types: str | list[str] | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for all playlist folders and
        playlists in the current user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        limit : int; keyword-only; default: :code:`50`
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

        playlist_types : str or list[str]; keyword-only; optional
            Playlist types to return. If not specified, all playlists
            are returned.

            **Valid values**:

            * :code:`"FOLDER"` – Playlist folders.
            * :code:`"PLAYLIST"` – All playlists.
            * :code:`"FAVORITE_PLAYLIST"` – Favorited playlists.
            * :code:`"USER_PLAYLIST"` – User-created playlists.

            **Examples**: :code:`"USER_PLAYLIST"`,
            :code:`"FOLDER,USER_PLAYLIST"`,
            :code:`["FOLDER", "USER_PLAYLIST"]`.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Playlist name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of TIDAL content metadata for the playlist folders and
            playlists in the current user's collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "cursor": <str>,
                    "items": [
                      {
                        "addedAt": <str>,
                        "data": {
                          "createdAt": <str>,
                          "id": <str>,
                          "itemType": "FOLDER",
                          "lastModifiedAt": <str>,
                          "name": <str>,
                          "totalNumberOfItems": <int>,
                          "trn": <str>,
                        },
                        "itemType": "FOLDER",
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "parent": {
                          "id": <str>,
                          "name": <str>
                        },
                        "trn": <str>,
                      },
                      {
                        "addedAt": <str>,
                        "data": {
                          "contentBehavior": <str>,
                          "created": <str>,
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "curators": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>
                            }
                          ],
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "itemType": "PLAYLIST",
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "promotedArtists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>
                            }
                          ],
                          "sharingLevel": <str>,
                          "source": <str>,
                          "squareImage": <str>,
                          "status": <str>,
                          "title": <str>,
                          "trn": <str>,
                          "type": <str>,
                          "url": <str>,
                          "uuid": <str>
                        },
                        "itemType": "PLAYLIST",
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "parent": {
                          "id": <str>,
                          "name": <str>
                        },
                        "trn": <str>
                      }
                    ],
                    "lastModifiedAt": <str>,
                  }
        """
        self._client._require_authentication(
            "playlists.get_my_folders_and_playlists"
        )
        return self._get_my_playlists(
            "playlists/folders/flattened",
            cursor=cursor,
            limit=limit,
            playlist_types=playlist_types,
            sort_by=sort_by,
            descending=descending,
        )

    @TTLCache.cached_method(ttl="user")
    def get_user_playlists(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for editorial and user-created
        playlists in a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Playlist name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of TIDAL content metadata for editorial and
            user-created playlists in the user's collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created": <str>,
                        "playlist": {
                          "created": <str>,
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos":<int>,
                          "popularity": <int>,
                          "promotedArtists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "publicPlaylist": <bool>,
                          "squareImage": <str>,
                          "title": <str>,
                          "type": <str>,
                          "url": <str>,
                          "uuid": <str>
                        },
                        "type": "USER_CREATED"
                      },
                      {
                        "created": <str>,
                        "playlist": {
                          "created": <str>,
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos":<int>,
                          "popularity": <int>,
                          "promotedArtists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "publicPlaylist": <bool>,
                          "squareImage": <str>,
                          "title": <str>,
                          "type": <str>,
                          "url": <str>,
                          "uuid": <str>
                        },
                        "type": "USER_FAVORITE"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("playlists.get_user_playlists")
        return self._get_user_playlists(
            "playlistsAndFavoritePlaylists",
            user_id,
            country_code=country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @TTLCache.cached_method(ttl="user")
    def get_user_created_playlists(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for user-created playlists in a
        user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Playlist name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of TIDAL content metadata for user-created playlists in
            the user's collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created": <str>,
                        "playlist": {
                          "created": <str>,
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos":<int>,
                          "popularity": <int>,
                          "promotedArtists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "publicPlaylist": <bool>,
                          "squareImage": <str>,
                          "title": <str>,
                          "type": <str>,
                          "url": <str>,
                          "uuid": <str>
                        },
                        "type": "USER_CREATED"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication(
            "playlists.get_user_created_playlists"
        )
        return self._get_user_playlists(
            "playlists",
            user_id,
            country_code=country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @TTLCache.cached_method(ttl="user")
    def get_user_public_playlists(
        self,
        user_id: int | str | None = None,
        /,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for public playlists in a user's
        collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`10_000`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of TIDAL content metadata for the public playlists in a
            user's collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "cursor": <str>,
                    "items": [
                      {
                        "followInfo": {
                          "followType": "PLAYLIST",
                          "followed": <bool>,
                          "nrOfFollowers": <int>,
                          "tidalResourceName": <str>
                        },
                        "playlist": {
                          "contentBehavior": <str>,
                          "created": <str>,
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": "USER"
                          },
                          "curators": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>
                            }
                          ],
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "promotedArtists": [
                            {
                              "contributionLinkUrl": <str>,
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>,
                              "userId": <int>
                            }
                          ],
                          "sharingLevel": "PUBLIC",
                          "source": <str>,
                          "squareImage": <str>,
                          "status": <str>,
                          "title": <str>,
                          "trn": <str>,
                          "type": "USER",
                          "url": <str>,
                          "uuid": <str>
                        },
                        "profile": {
                          "color": <list[str]>,
                          "name": <str>,
                          "userId": <int>
                        }
                      }
                    ]
                  }
        """
        self._client._require_authentication(
            "playlists.get_user_public_playlists"
        )
        return self._get_user_relationship(
            "user-playlists",
            "public",
            user_id=user_id,
            cursor=cursor,
            limit=limit,
        )

    @TTLCache.cached_method(ttl="user")
    def get_user_followers(
        self,
        user_id: int | str | None = None,
        /,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a user's followers.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        limit : int; keyword-only; optional
            Maximum number of users to return.

            **Valid range**: :code:`1` to :code:`10_000`.

        Returns
        -------
        followers : dict[str, Any]
            TIDAL content metadata for the user's followers.

            **Sample response**: :code:`{'cursor': None, 'items': {}}`.
        """
        self._client._require_authentication("playlists.get_user_followers")
        return self._get_user_relationship(
            "profiles",
            "followers",
            user_id=user_id,
            cursor=cursor,
            limit=limit,
        )

    @TTLCache.cached_method(ttl="user")
    def get_followed_users(
        self,
        user_id: int | str | None = None,
        /,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for the people followed by a user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        limit : int; keyword-only; optional
            Maximum number of users to return.

            **Valid range**: :code:`1` to :code:`10_000`.

        Returns
        -------
        following : dict[str, Any]
            TIDAL content metadata for the people followed by the user.

            **Sample response**: :code:`{'cursor': None, 'items': {}}`.
        """
        self._client._require_authentication("playlists.get_user_following")
        return self._get_user_relationship(
            "profiles",
            "following",
            user_id=user_id,
            cursor=cursor,
            limit=limit,
        )

    def follow_user(self, user_id: int | str, /) -> None:
        """
        Follow a TIDAL user.

        .. caution::

           This endpoint appears to have been deprecated by TIDAL.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only
            TIDAL ID of the user.
        """
        self._manage_followed_users("PUT", user_id)

    def unfollow_user(self, user_id: int | str, /) -> None:
        """
        Unfollow a TIDAL user.

        .. caution::

           This endpoint appears to have been deprecated by TIDAL.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only
            TIDAL ID of the user.
        """
        self._manage_followed_users("DELETE", user_id)

    @TTLCache.cached_method(ttl="user")
    def get_my_blocked_users(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for the users blocked by the
        current user.

        .. caution::

           This endpoint appears to have been deprecated by TIDAL.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        limit : int; keyword-only; optional
            Maximum number of users to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first user to return. Use with `limit` to get
            the next batch of users.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        users : dict[str, Any]
            Page of TIDAL content metadata for users blocked by the
            current user.

            **Sample response**: :code:`{'items': [], 'limit': 0,
            'offset': 0, 'totalNumberOfItems': 0}`.
        """
        self._client._require_authentication("playlists.get_my_blocked_users")
        params = {}
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "v2/profiles/blocked-profiles", params=params
        ).json()

    def block_user(self, user_id: int | str, /) -> None:
        """
        Block a TIDAL user.

        .. caution::

           This endpoint appears to have been deprecated by TIDAL.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only
            TIDAL ID of the user.
        """
        self._manage_blocked_users("PUT", user_id)

    def unblock_user(self, user_id: int | str, /) -> None:
        """
        Unblock a TIDAL user.

        .. caution::

           This endpoint appears to have been deprecated by TIDAL.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only
            TIDAL ID of the user.
        """
        self._manage_blocked_users("DELETE", user_id)

    @TTLCache.cached_method(ttl="user")
    def get_saved_tracks(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for tracks in a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the tracks by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Track name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of TIDAL content metadata for tracks in the user's
            collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created": <str>,
                        "item": {
                          "accessType": <str>,
                          "adSupportedStreamReady": <bool>,
                          "album": {
                            "cover": <str>,
                            "id": <int>,
                            "title": <str>,
                            "vibrantColor": <str>,
                            "videoCover": <str>
                          },
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": <str>,
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": "MAIN"
                          },
                          "artists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "audioModes": <list[str]>,
                          "audioQuality": <str>,
                          "bpm": 128,
                          "copyright": <str>,
                          "djReady": <bool>,
                          "duration": <int>,
                          "editable": <bool>,
                          "explicit": <bool>,
                          "id": <int>,
                          "isrc": <str>,
                          "key": <str>,
                          "keyScale": <str>,
                          "mediaMetadata": {
                            "tags": <list[str]>
                          },
                          "mixes": {
                            "TRACK_MIX": <str>
                          },
                          "payToStream": <bool>,
                          "peak": <float>,
                          "popularity": <int>,
                          "premiumStreamingOnly": <bool>,
                          "replayGain": <float>,
                          "spotlighted": <bool>,
                          "stemReady": <bool>,
                          "streamReady": <bool>,
                          "streamStartDate": <str>,
                          "title": <str>,
                          "trackNumber": <int>,
                          "upload": <bool>,
                          "url": <str>,
                          "version": <str>,
                          "volumeNumber": <int>,
                        }
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("users.get_saved_tracks")
        return self._get_saved_resources(
            "tracks",
            user_id,
            country_code=country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    def save_tracks(
        self,
        track_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        on_missing: str | None = None,
    ) -> None:
        """
        Add tracks to a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        track_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of the tracks.

            **Examples**: :code:`46369325`, :code:`"251380837"`,
            :code:`"46369325,251380837"`,
            :code:`[46369325, "251380837"]`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        on_missing : str; keyword-only; optional
            Behavior when the tracks to be favorited cannot be found in
            the TIDAL catalog.

            **API default**: :code:`"FAIL"`.
        """
        self._client._require_authentication("users.save_tracks")
        return self._save_resources(
            "tracks",
            track_ids,
            user_id=user_id,
            country_code=country_code,
            on_missing=on_missing,
        )

    def remove_saved_tracks(
        self,
        track_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        """
        Remove tracks from a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        track_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of the tracks.

            **Examples**: :code:`46369325`, :code:`"251380837"`,
            :code:`"46369325,251380837"`,
            :code:`[46369325, "251380837"]`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_authentication("users.remove_saved_tracks")
        return self._remove_saved_resources(
            "tracks", track_ids, user_id=user_id
        )

    @TTLCache.cached_method(ttl="user")
    def get_blocked_tracks(
        self,
        user_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for tracks blocked by a user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of TIDAL content metadata for tracks blocked by the
            user.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created": <str>,
                        "item": {
                          "accessType": <str>,
                          "adSupportedStreamReady": <bool>,
                          "album": {
                            "cover": <str>,
                            "id": <int>,
                            "title": <str>,
                            "vibrantColor": <str>,
                            "videoCover": <str>
                          },
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": <str>,
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": "MAIN"
                          },
                          "artists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "audioModes": <list[str]>,
                          "audioQuality": <str>,
                          "bpm": <int>,
                          "copyright": <str>,
                          "djReady": <bool>,
                          "duration": <int>,
                          "editable": <bool>,
                          "explicit": <bool>,
                          "id": <int>,
                          "isrc": <str>,
                          "key": <str>,
                          "keyScale": <str>,
                          "mediaMetadata": {
                            "tags": <list[str]>
                          },
                          "mixes": {
                            "TRACK_MIX": <str>
                          },
                          "payToStream": <bool>,
                          "peak": <float>,
                          "popularity": <int>,
                          "premiumStreamingOnly": <bool>,
                          "replayGain": <float>,
                          "spotlighted": <bool>,
                          "stemReady": <bool>,
                          "streamReady": <bool>,
                          "streamStartDate": <str>,
                          "title": <str>,
                          "trackNumber": <int>,
                          "upload": <bool>,
                          "url": <str>,
                          "version": <str>,
                          "volumeNumber": <int>
                        },
                        "type": "TRACK"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("users.get_blocked_tracks")
        return self._get_blocked_resources(
            "tracks", user_id, limit=limit, offset=offset
        )

    def block_track(
        self, track_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        """
        Block a track for a user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"251380837"`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_authentication("users.block_track")
        self._manage_blocked_resources(
            "POST", "track", track_id, user_id=user_id
        )

    def unblock_track(
        self, track_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        """
        Unblock a track for a user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"251380837"`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_authentication("users.unblock_track")
        self._manage_blocked_resources(
            "DELETE", "track", track_id, user_id=user_id
        )

    @TTLCache.cached_method(ttl="user")
    def get_saved_videos(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for videos in a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of videos to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first video to return. Use with `limit` to get
            the next batch of videos.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the videos by.

            **Valid values**:

            * :code:`"DATE"` - Date added.
            * :code:`"NAME"` - Video name.

            **API default**: :code:`"DATE"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        videos : dict[str, Any]
            Page of TIDAL content metadata for videos in the user's
            collection.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created": <str>,
                        "item": {
                          "adSupportedStreamReady": <bool>,
                          "adsPrePaywallOnly": <bool>,
                          "adsUrl": <str>,
                          "album": {},
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": <str>,
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": "MAIN"
                          },
                          "artists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "djReady": <bool>,
                          "duration": <int>,
                          "explicit": <bool>,
                          "id": <int>,
                          "imageId": <str>,
                          "imagePath": <str>,
                          "popularity": <int>,
                          "quality": <str>,
                          "releaseDate": <str>,
                          "stemReady": <bool>,
                          "streamReady": <bool>,
                          "streamStartDate": <str>,
                          "title": <str>,
                          "trackNumber": <int>,
                          "type": <str>,
                          "vibrantColor": <str>,
                          "volumeNumber": <int>
                        }
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("users.get_saved_videos")
        return self._get_saved_resources(
            "videos",
            user_id,
            country_code=country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    def save_videos(
        self,
        video_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        on_missing: str | None = None,
    ) -> None:
        """
        Add videos to a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        video_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of the videos.

            **Examples**: :code:`29597422`, :code:`"59727844"`,
            :code:`"29597422,59727844"`, :code:`[29597422, "59727844"]`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        on_missing : str; keyword-only; optional
            Behavior when the videos to be favorited cannot be found in
            the TIDAL catalog.

            **API default**: :code:`"FAIL"`.
        """
        self._client._require_authentication("users.save_videos")
        return self._save_resources(
            "videos",
            video_ids,
            user_id=user_id,
            country_code=country_code,
            on_missing=on_missing,
        )

    def remove_saved_videos(
        self,
        video_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        """
        Remove videos from a user's collection.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        video_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of the videos.

            **Examples**: :code:`29597422`, :code:`"59727844"`,
            :code:`"29597422,59727844"`, :code:`[29597422, "59727844"]`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_authentication("users.remove_saved_videos")
        return self._remove_saved_resources(
            "videos", video_ids, user_id=user_id
        )

    @TTLCache.cached_method(ttl="user")
    def get_blocked_videos(
        self,
        user_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for videos blocked by a user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        limit : int; keyword-only; optional
            Maximum number of videos to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first video to return. Use with `limit` to get
            the next batch of videos.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        videos : dict[str, Any]
            Page of TIDAL content metadata for videos blocked by the
            user.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created": <str>,
                        "item": {
                          "adSupportedStreamReady": <bool>,
                          "adsPrePaywallOnly": <bool>,
                          "adsUrl": <str>,
                          "album": {},
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": <str>,
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": "MAIN"
                          },
                          "artists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "djReady": <bool>,
                          "duration": <int>,
                          "explicit": <bool>,
                          "id": <int>,
                          "imageId": <str>,
                          "imagePath": <str>,
                          "popularity": <int>,
                          "quality": <str>,
                          "releaseDate": <str>,
                          "stemReady": <bool>,
                          "streamReady": <bool>,
                          "streamStartDate": <str>,
                          "title": <str>,
                          "trackNumber": <int>,
                          "type": <str>,
                          "vibrantColor": <str>,
                          "volumeNumber": <int>
                        },
                        "type": "VIDEO"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("users.get_blocked_videos")
        return self._get_blocked_resources(
            "videos", user_id, limit=limit, offset=offset
        )

    def block_video(
        self, video_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        """
        Block a video for a user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        video_id : int or str; positional-only
            TIDAL ID of the video.

            **Examples**: :code:`29597422`, :code:`"59727844"`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_authentication("users.block_video")
        self._manage_blocked_resources(
            "POST", "video", video_id, user_id=user_id
        )

    def unblock_video(
        self, video_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        """
        Unblock a video for a user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access and manage the user's collection.

        Parameters
        ----------
        video_id : int or str; positional-only
            TIDAL ID of the video.

            **Examples**: :code:`29597422`, :code:`"59727844"`.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_authentication("users.unblock_video")
        self._manage_blocked_resources(
            "DELETE", "video", video_id, user_id=user_id
        )
