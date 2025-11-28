from collections.abc import Collection
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class UsersAPI(ResourceAPI):
    """ """

    _client: "PrivateTIDALAPI"

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
        """ """
        return self._get_favorite_resources(
            "albums",
            user_id,
            country_code,
            limit=limit,
            offset=offset,
            sort=sort,
            reverse=reverse,
        )

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
        """ """
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
            params["order"] = sort
        if reverse is not None:
            params["orderDirection"] = "DESC" if reverse else "ASC"
        return self._client._request(
            "GET", f"v1/users/{user_id}/favorites/{resource}", params=params
        ).json()

    def _favorite_resources(
        self,
        resource: str,
        resource_ids: int | str | Collection[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        missing: str | None = None,
    ) -> None:
        """ """
        if user_id is None:
            user_id = self._client._get_user_identifier()
        if country_code is None:
            country_code = self._client._my_country_code
        else:
            self._client._validate_country_code(country_code)
        self._client._request(
            "POST",
            f"v1/users/{user_id}/favorites/{resource}",
            params={"countryCode": country_code},
            # data={...}  # TODO
        )

    def _unfavorite_resources(
        self,
        resource: str,
        resource_ids: int | str | Collection[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        """ """
        if user_id is None:
            user_id = self._client._get_user_identifier()
        self._client._request(
            "DELETE",
            f"v1/users/{user_id}/favorites/{resource}",  # TODO
        )
