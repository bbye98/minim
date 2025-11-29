from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class UsersAPI(ResourceAPI):
    """ """

    _SORTS = {"DATE", "NAME"}
    _client: "PrivateTIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_my_profile(self) -> dict[str, Any]:
        """
        Get profile information for the current user.

        Returns
        -------
        profile : dict[str, Any]
            Current user's profile information.

            .. admonition:: Sample response
               :class: dropdown

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
        return self._client._request(
            "GET", "https://login.tidal.com/oauth2/me"
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_session(self) -> dict[str, Any]:
        """
        Get information about the current private TIDAL API session.

        Returns
        -------
        session : dict[str, Any]
            Information about the current private TIDAL API session.

            .. admonition:: Sample response
               :class: dropdown

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
        return self._client._request("GET", "v1/sessions").json()

    def get_favorite_ids(
        self, user_id: int | str | None = None, /
    ) -> dict[str, list[str]]:
        """
        Get TIDAL IDs or UUIDs of the albums, artists, playlists,
        tracks, and videos in the current user's collection.

        Parameters
        ----------
        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        Returns
        -------
        ids : `dict`
            IDs or UUIDs of the items in the current user's collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "ALBUM": <list[str]>,
                    "ARTIST": <list[str]>,
                    "PLAYLIST": <list[str]>,
                    "TRACK": <list[str]>,
                    "VIDEO": <list[str]>,
                  }
        """
        if user_id is None:
            user_id = self._client._get_user_identifier()
        return self._client._request(
            "GET", f"v1/users/{user_id}/favorites/ids"
        ).json()

    def get_favorite_albums(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort: str | None = None,
        reverse: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for albums in a user's collection.

        Parameters
        ----------
        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of albums to return.

            **Valid range**: :code:`1` to :code:`100`.

            **Default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first album to return. Use with `limit` to get
            the next set of albums.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        sort : str; keyword-only; optional
            Field to sort the albums by.

            **Valid values**:

            .. container::

               * :code:`"DATE"` - Date added.
               * :code:`"NAME"` - Album name.

            **Default**: :code:`"DATE"`.

        reverse : bool; keyword-only; optional
            Whether to reverse the sort order.

            **Default**: :code:`False` (ascending order).

        Returns
        -------
        albums : dict[str, Any]
            TIDAL catalog information for albums in the user's
            collection.

            .. admonition:: Sample response
               :class: dropdown

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
        return self._get_favorite_resources(
            "albums",
            user_id,
            country_code,
            limit=limit,
            offset=offset,
            sort=sort,
            reverse=reverse,
        )

    def favorite_albums(
        self,
        album_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        missing_ok: bool | None = None,
    ) -> None:
        """
        Add albums to a user's collection.

        Parameters
        ----------
        album_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of albums, provided as either a comma-separated
            string or a list of integers and/or strings.

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        missing_ok : bool; keyword-only; optional
            Whether to skip albums that are not found in the
            TIDAL catalog (:code:`True`) or raise an error
            (:code:`False`).
        """
        return self._favorite_resources(
            "albums", album_ids, user_id, country_code, missing_ok=missing_ok
        )

    def unfavorite_albums(
        self,
        album_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        """
        Remove albums from a user's collection.

        Parameters
        ----------
        album_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of albums, provided as either a comma-separated
            string or a list of integers and/or strings.

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        return self._unfavorite_resources("albums", album_ids, user_id)

    def _get_favorite_resources(
        self,
        resource: str,
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort: str | None = None,
        reverse: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for items of a specific resource
        type in a user's collection.

        Parameters
        ----------
        resource : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"tracks"`, :code:`"videos"`.

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`100`.

            **Default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next set of items.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        sort : str; keyword-only; optional
            Field to sort the items by.

            **Valid values**:

            .. container::

               * :code:`"DATE"` - Date added.
               * :code:`"NAME"` - Album name.

            **Default**: :code:`"DATE"`.

        reverse : bool; keyword-only; optional
            Whether to reverse the sort order from ascending
            (:code:`False`) to descending (:code:`True`).

            **Default**: :code:`False`.

        Returns
        -------
        items : dict[str, Any]
            TIDAL catalog information for items in the user's
            collection.
        """
        if user_id is None:
            user_id = self._client._get_user_identifier()
        params = {}
        self._client._resolve_country_code(country_code, params)
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        if sort is not None:
            if sort not in self._SORTS:
                sorts = "', '".join(sorted(self._SORTS))
                raise ValueError(
                    f"Invalid sort field {sort!r}. Valid values: '{sorts}'."
                )
            params["order"] = sort
        if reverse is not None:
            self._client._validate_type("reverse", reverse, bool)
            params["orderDirection"] = "DESC" if reverse else "ASC"
        return self._client._request(
            "GET", f"v1/users/{user_id}/favorites/{resource}", params=params
        ).json()

    def _favorite_resources(
        self,
        resource: str,
        item_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        missing_ok: bool | None = None,
    ) -> None:
        """
        Add items of a specific resource type to a user's collection.

        Parameters
        ----------
        resource : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"tracks"`, :code:`"videos"`.

        item_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of items, provided as either a comma-separated
            string or a list of integers and/or strings.

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        missing_ok : bool; keyword-only; optional
            Whether to skip items that are not found in the
            TIDAL catalog (:code:`True`) or raise an error
            (:code:`False`).
        """
        if user_id is None:
            user_id = self._client._get_user_identifier()
        if country_code is None:
            country_code = self._client._my_country_code
        else:
            self._client._validate_country_code(country_code)
        data = {
            f"{resource[:-1]}Ids": self._client._prepare_tidal_ids(
                item_ids, limit=1000000
            )
        }
        if missing_ok is not None:
            self._client._validate_type("missing_ok", missing_ok, bool)
            data["onArtifactNotFound"] = "SKIP" if missing_ok else "FAIL"
        self._client._request(
            "POST",
            f"v1/users/{user_id}/favorites/{resource}",
            params={"countryCode": country_code},
            data=data,
        )

    def _unfavorite_resources(
        self,
        resource: str,
        item_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        """
        Remove items of a specific resource type from a user's collection.

        Parameters
        ----------
        resource : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"tracks"`, :code:`"videos"`.

        item_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of items, provided as either a comma-separated
            string or a list of integers and/or strings.

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        if user_id is None:
            user_id = self._client._get_user_identifier()
        self._client._request(
            "DELETE",
            f"v1/users/{user_id}/favorites/{resource}"
            f"/{self._client._prepare_tidal_ids(item_ids, limit=1000000)}",
        )
