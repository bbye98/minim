from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class PrivateUsersAPI(ResourceAPI):
    """
    User Collections and Users API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _FILTERS = {"FOLDER", "PLAYLIST", "FAVORITE_PLAYLIST", "USER_PLAYLIST"}
    _SORTS = {"DATE", "NAME"}
    _client: "PrivateTIDALAPI"

    @classmethod
    def _validate_filters(cls, filters: str | list[str]) -> None:
        """
        Validate one or more playlist types to filter by.

        Parameters
        ----------
        filters : str or list[str]; keyword-only; optional
            Playlist types to include in the results.
        """
        if isinstance(filters, str):
            if filters not in cls._FILTERS:
                _filters = "', '".join(cls._FILTERS)
                raise ValueError(
                    f"Invalid playlist type {filters!r}. "
                    f"Valid values: '{_filters}'."
                )
        elif isinstance(filters, tuple | list):
            for filter in filters:
                cls._validate_filters(filter)
        else:
            raise TypeError(
                "`filter_by` must be a string or a list of strings."
            )

    @TTLCache.cached_method(ttl="catalog")
    def get_my_profile(self) -> dict[str, Any]:
        """
        Get profile information for the current user.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

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
        self._client._require_authentication("users.get_my_profile")
        return self._client._request(
            "GET", "https://login.tidal.com/oauth2/me"
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_session(self) -> dict[str, Any]:
        """
        Get information about the current private TIDAL API session.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

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
        self._client._require_authentication("users.get_session")
        return self._client._request("GET", "v1/sessions").json()

    def get_favorite_ids(
        self, user_id: int | str | None = None, /
    ) -> dict[str, list[str]]:
        """
        Get TIDAL IDs or UUIDs of the albums, artists, playlists,
        tracks, and videos in the current user's collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

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
        self._client._require_authentication("users.get_favorite_ids")
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
        sort_by: str | None = None,
        reverse: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for albums in a user's collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of albums to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first album to return. Use with `limit` to get
            the next set of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the albums by.

            **Valid values**:

            .. container::

               * :code:`"DATE"` - Date added.
               * :code:`"NAME"` - Album name.

            **API default**: :code:`"DATE"`.

        reverse : bool; keyword-only; optional
            Whether to reverse the sort order from ascending to
            descending.

            **API default**: :code:`False`.

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
        self._client._require_authentication("users.get_favorite_albums")
        return self._get_favorite_resources(
            "albums",
            user_id,
            country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
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

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

        Parameters
        ----------
        album_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of albums, provided as either a comma-separated
            string or a list of integers and/or strings.

        user_id : int or str; optional
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

            **API default**: :code:`False`.
        """
        self._client._require_authentication("users.favorite_albums")
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

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

        Parameters
        ----------
        album_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of albums, provided as either a comma-separated
            string or a list of integers and/or strings.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_authentication("users.unfavorite_albums")
        return self._unfavorite_resources("albums", album_ids, user_id)

    def get_blocked_artists(
        self,
        user_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str]:
        """
        Get TIDAL catalog information for artists blocked by a user.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

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
            the next set of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        artists : dict[str]
            Pages of TIDAL catalog information for artists blocked by
            the user.

            .. admonition:: Sample response
               :class: dropdown

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
                          "selectedAlbumCoverFallback": <str>,
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
        if user_id is None:
            user_id = self._client._get_user_identifier()
        params = {}
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"v1/users/{user_id}/blocks/artists", params=params
        ).json()

    def block_artist(
        self, artist_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        """
        Block an artist for a user.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

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
        if user_id is None:
            user_id = self._client._get_user_identifier()
        self._client._request(
            "POST",
            f"v1/users/{user_id}/blocks/artists",
            data={"artistId": artist_id},
        )

    def unblock_artist(
        self, artist_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        """
        Unblock an artist for a user.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

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
        if user_id is None:
            user_id = self._client._get_user_identifier()
        self._client._request(
            "DELETE", f"v1/users/{user_id}/blocks/artists/{artist_id}"
        )

    def get_favorite_artists(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        reverse: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for artists in a user's
        collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of artists to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first artist to return. Use with `limit` to get
            the next set of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the albums by.

            **Valid values**:

            .. container::

               * :code:`"DATE"` - Date added.
               * :code:`"NAME"` - Artist name.

            **API default**: :code:`"DATE"`.

        reverse : bool; keyword-only; optional
            Whether to reverse the sort order from ascending to
            descending.

            **API default**: :code:`False`.

        Returns
        -------
        artists : dict[str, Any]
            TIDAL catalog information for artists in the user's
            collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("users.get_favorite_artists")
        return self._get_favorite_resources(
            "artists",
            user_id,
            country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            reverse=reverse,
        )

    def favorite_artists(
        self,
        artist_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        missing_ok: bool | None = None,
    ) -> None:
        """
        Add albums to a user's collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

        Parameters
        ----------
        artist_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of artists, provided as either a comma-separated
            string or a list of integers and/or strings.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        missing_ok : bool; keyword-only; optional
            Whether to skip artists that are not found in the
            TIDAL catalog (:code:`True`) or raise an error
            (:code:`False`).

            **API default**: :code:`False`.
        """
        self._client._require_authentication("users.favorite_artists")
        return self._favorite_resources(
            "artists", artist_ids, user_id, country_code, missing_ok=missing_ok
        )

    def unfavorite_artists(
        self,
        artist_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        """
        Remove artists from a user's collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

        Parameters
        ----------
        artist_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of artists, provided as either a comma-separated
            string or a list of integers and/or strings.

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_authentication("users.unfavorite_artists")
        return self._unfavorite_resources("artists", artist_ids, user_id)

    def get_my_favorite_mixes(
        self,
        *,
        limit: int = 50,
        cursor: str | None = None,
        sort_by: str | None = None,
        reverse: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for mixes in the current user's
        collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

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

            .. container::

               * :code:`"DATE"` - Date added.
               * :code:`"NAME"` - Mix name.

            **API default**: :code:`"DATE"`.

        reverse : bool; keyword-only; optional
            Whether to reverse the sort order from ascending to
            descending.

            **API default**: :code:`False`.

        Returns
        -------
        mixes : dict[str, Any]
            TIDAL catalog information for mixes in the user's
            collection.

            .. admonition:: Sample response
               :class: dropdown

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
        self._client._require_authentication("users.get_my_favorite_mixes")
        self._client._validate_number("limit", limit, int, 1, 50)
        params = {"limit": limit}
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        if sort_by is not None:
            if sort_by not in self._SORTS:
                sorts = "', '".join(sorted(self._SORTS))
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. Valid values: '{sorts}'."
                )
            params["order"] = sort_by
        if reverse is not None:
            self._client._validate_type("reverse", reverse, bool)
            params["orderDirection"] = "DESC" if reverse else "ASC"
        return self._client._request(
            "GET", "v2/favorites/mixes", params=params
        ).json()

    def get_my_favorite_mix_ids(
        self, *, limit: int = 50, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        Get TIDAL IDs of the mixes in the current user's collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

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
            TIDAL IDs of the mixes in the user's collection.

            **Sample response**:
            :code:`{"content": <list[str]>, "cursor": <str>}`
        """
        self._client._require_authentication("users.get_my_favorite_mix_ids")
        self._client._validate_number("limit", limit, int, 1, 50)
        params = {"limit": limit}
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET", "v2/favorites/mixes/ids", params=params
        ).json()

    def favorite_mixes(
        self, mix_ids: str | list[str], /, *, missing_ok: bool | None = None
    ) -> None:
        """
        Add mixes to the current user's collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

        Parameters
        ----------
        mix_ids : str or list[str]; positional-only
            TIDAL IDs of the mixes, provided as either a comma-separated
            string or a list of strings.

            **Examples**: :code:`"000ec0b01da1ddd752ec5dee553d48"`,
            :code:`"000ec0b01da1ddd752ec5dee553d48,000dd748ceabd5508947c6a5d3880a"`,
            :code:`["000ec0b01da1ddd752ec5dee553d48",
            "000dd748ceabd5508947c6a5d3880a"]`.

        missing_ok : bool; keyword-only; optional
            Whether to skip albums that are not found in the
            TIDAL catalog (:code:`True`) or raise an error
            (:code:`False`).

            **API default**: :code:`False`.
        """
        self._client._require_authentication("users.favorite_mixes")
        data = {"mixIds": self._prepare_mix_ids(mix_ids)}
        if missing_ok is not None:
            self._client._validate_type("missing_ok", missing_ok, bool)
            data["onArtifactNotFound"] = "SKIP" if missing_ok else "FAIL"
        self._client._request("PUT", "v2/favorites/mixes/add", data=data)

    def unfavorite_mixes(self, mix_ids: str | list[str], /) -> None:
        """
        Remove mixes from the current user's collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and modify user's
                 collection.

        Parameters
        ----------
        mix_ids : str or list[str]; positional-only
            TIDAL IDs of the mixes, provided as either a comma-separated
            string or a list of strings.

            **Examples**: :code:`"000ec0b01da1ddd752ec5dee553d48"`,
            :code:`"000ec0b01da1ddd752ec5dee553d48,000dd748ceabd5508947c6a5d3880a"`,
            :code:`["000ec0b01da1ddd752ec5dee553d48",
            "000dd748ceabd5508947c6a5d3880a"]`.
        """
        self._client._require_authentication("users.unfavorite_mixes")
        self._client._request(
            "PUT",
            "v2/favorites/mixes/remove",
            data={"mixIds": self._prepare_mix_ids(mix_ids)},
        )

    def get_my_playlists(
        self,
        *,
        limit: int = 50,
        cursor: str | None = None,
        folder_uuid: str | None = None,
        filter_by: str | list[str] | None = None,
        sort_by: str | None = None,
        reverse: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for playlists in the current
        user's collection.

        Parameters
        ----------
        limit : int; keyword-only; default: :code:`50`
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        folder_uuid : str; keyword-only; optional
            UUID of playlist folder to retrieve playlists from. Use
            :code:`"root"` to target the top-level "Playlists" folder.

            **API default**: :code:`"root"`.

        filter_by : str or list[str]; keyword-only; optional
            Playlist types to include in the results. If not specified,
            all playlists are returned.

            **Valid values**:

            .. container::

               * :code:`FOLDER` – Playlist folders.
               * :code:`PLAYLIST` – All playlists.
               * :code:`FAVORITE_PLAYLIST` – Favorited playlists.
               * :code:`USER_PLAYLIST` – User-created playlists.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**:

            .. container::

               * :code:`"DATE"` - Date added.
               * :code:`"NAME"` - Playlist name.

            **API default**: :code:`"DATE"`.

        reverse : bool; keyword-only; optional
            Whether to reverse the sort order from ascending to
            descending.

            **API default**: :code:`False`.

        Returns
        -------
        playlists : dict[str, Any]
            TIDAL content metadata for the playlists in the current
            user's collection.

            .. admonition:: Sample response
               :class: dropdown

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
                            "picture": <Any>,
                            "type": <str>
                          },
                          "curators": <list[Any]>,
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "itemType": "PLAYLIST",
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": 1,
                          "numberOfVideos": 1,
                          "promotedArtists": <list[Any]>,
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
        self._client._require_authentication("users.get_my_playlists")
        self._client._validate_number("limit", limit, int, 1, 50)
        params = {"limit": limit}
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        if folder_uuid is not None:
            if folder_uuid != "root":
                self._client._validate_uuid(folder_uuid)
            params["folderId"] = folder_uuid
        if filter_by is not None:
            self._validate_filters(filter_by)
            params["includeOnly"] = filter_by
        if sort_by is not None:
            if sort_by not in self._SORTS:
                sorts = "', '".join(sorted(self._SORTS))
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. Valid values: '{sorts}'."
                )
            params["order"] = sort_by
        if reverse is not None:
            self._client._validate_type("reverse", reverse, bool)
            params["orderDirection"] = "DESC" if reverse else "ASC"
        return self._client._request(
            "GET", "v2/my-collection/playlists", params=params
        ).json()

    def get_my_playlist_folders(  # TODO
        self,
    ) -> dict[str, Any]:
        """ """
        # v2/my-collection/playlists/folders
        # v2/my-collection/playlists/folders/flattened

    def get_user_playlists(  # TODO
        self,
    ) -> dict[str, Any]:
        """ """
        # v1/users/{user_id}/playlistsAndFavoritePlaylists?countryCode={country_code}

    def get_user_favorite_playlists(  # TODO
        self,
    ) -> dict[str, Any]:
        """ """
        # v1/users/{user_id}/favorites/playlists?countryCode={country_code}

    def favorite_playlists(  # TODO
        self,
    ) -> None:
        """ """
        ...

    def unfavorite_playlists(  # TODO
        self,
    ) -> None:
        """ """
        ...

    def move_favorite_playlists(  # TODO
        self,
    ) -> None:
        """ """
        ...

    def _get_favorite_resources(
        self,
        resource: str,
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
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

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next set of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the items by.

            **Valid values**:

            .. container::

               * :code:`"DATE"` - Date added.
               * :code:`"NAME"` - Item name.

            **API default**: :code:`"DATE"`.

        reverse : bool; keyword-only; optional
            Whether to reverse the sort order from ascending to
            descending.

            **API default**: :code:`False`.

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
        if sort_by is not None:
            if sort_by not in self._SORTS:
                sorts = "', '".join(sorted(self._SORTS))
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. Valid values: '{sorts}'."
                )
            params["order"] = sort_by
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

        user_id : int or str; optional
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

            **API default**: :code:`False`.
        """
        if user_id is None:
            user_id = self._client._get_user_identifier()
        if country_code is None:
            country_code = self._client._my_country_code
        else:
            self._client._validate_country_code(country_code)
        data = {
            f"{resource[:-1]}Ids": self._client._prepare_tidal_ids(
                item_ids, limit=1_000
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

        user_id : int or str; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        if user_id is None:
            user_id = self._client._get_user_identifier()
        self._client._request(
            "DELETE",
            f"v1/users/{user_id}/favorites/{resource}"
            f"/{self._client._prepare_tidal_ids(item_ids, limit=1_000)}",
        )
