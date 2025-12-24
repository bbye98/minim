from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI, _copy_docstring
from .pages import PrivatePagesAPI
from .users import PrivateUsersAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class PrivateAlbumsAPI(ResourceAPI):
    """
    Albums API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _client: "PrivateTIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_album(
        self, album_id: int | str, /, country_code: str | None = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a single album.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        album : dict[str, Any]
            TIDAL content metadata for the album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "adSupportedStreamReady": <bool>,
                    "allowStreaming": <bool>,
                    "artist": {
                      "handle": None,
                      "id": <int>,
                      "name": <str>,
                      "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                      "type": "MAIN"
                    },
                    "artists": [
                      {
                        "handle": None,
                        "id": <int>,
                        "name": <str>,
                        "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                        "type": <str>
                      }
                    ],
                    "audioModes": <list[str]>,
                    "audioQuality": <str>,
                    "copyright": <str>,
                    "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                    "djReady": <bool>,
                    "duration": <int>,
                    "explicit": <bool>,
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
                    "releaseDate": "YYYY-MM-DD",
                    "stemReady": <bool>,
                    "streamReady": <bool>,
                    "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                    "title": <str>,
                    "type": "ALBUM",
                    "upc": <str>,
                    "upload": <bool>,
                    "url": f"http://www.tidal.com/album/{id}",
                    "version": None,
                    "vibrantColor": "#rrggbb",
                    "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
                  }
        """
        if country_code is None:
            country_code = self._client._my_country_code
        else:
            self._client._validate_country_code(country_code)
        return self._client._request(
            "GET",
            f"v1/albums/{album_id}",
            params={"countryCode": country_code},
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_album_credits(
        self, album_id: int | str, /, country_code: str | None = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for an album's contributors.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        credits : dict[str, Any]
            TIDAL content metadata for the album's contributors.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "contributors": [
                        {
                          "id": <int>,
                          "name": <str>
                        }
                      ],
                      "type": <str>
                    }
                  ]
        """
        return self._get_album_resource("credits", album_id, country_code)

    @TTLCache.cached_method(ttl="catalog")
    def get_album_items(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for tracks and videos in an album.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

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

        Returns
        -------
        items : dict[str, Any]
            Pages of TIDAL catalog information for the tracks and videos
            in the album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "item": {
                          "accessType": <str>,
                          "adSupportedStreamReady": <bool>,
                          "album": {
                            "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                            "id": <int>,
                            "title": <str>,
                            "vibrantColor": "#rrggbb",
                            "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
                          },
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": None,
                            "id": <int>,
                            "name": <str>,
                            "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                            "type": "MAIN"
                          },
                          "artists": [
                            {
                              "handle": None,
                              "id": <int>,
                              "name": <str>,
                              "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
                          "isrc": "CCXXXYYNNNNN",
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
                          "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                          "title": <str>,
                          "trackNumber": <int>,
                          "upload": <bool>,
                          "url": f"http://www.tidal.com/track/{id}",
                          "version": None,
                          "volumeNumber": <int>
                        },
                        "type": "track"
                      },
                      {
                        "item": {
                          "adSupportedStreamReady": <bool>,
                          "adsPrePaywallOnly": <bool>,
                          "adsUrl": None,
                          "album": {
                            "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                            "id": <int>,
                            "title": <str>,
                            "vibrantColor": "#rrggbb",
                            "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
                          },
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": None,
                            "id": <int>,
                            "name": <str>,
                            "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                            "type": "MAIN"
                          },
                          "artists": [
                            {
                              "handle": None,
                              "id": <int>,
                              "name": <str>,
                              "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                              "type": <str>
                            }
                          ],
                          "djReady": <bool>,
                          "duration": <int>,
                          "explicit": <bool>,
                          "id": <int>,
                          "imageId": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                          "imagePath": None,
                          "popularity": <int>,
                          "quality": <str>,
                          "releaseDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                          "stemReady": <bool>,
                          "streamReady": <bool>,
                          "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                          "title": <str>,
                          "trackNumber": <int>,
                          "type": "Music Video",
                          "vibrantColor": "#rrggbb",
                          "volumeNumber": <int>
                        },
                        "type": "video"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._get_album_resource(
            "items", album_id, country_code, limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_album_item_credits(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for the credits of the tracks and
        videos in an album.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of credits to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first credit to return. Use with `limit` to get
            the next batch of credits.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        credits : dict[str, Any]
            Pages of TIDAL catalog information for the credits of the
            tracks and videos in the album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "credits": [
                          {
                            "contributors": [
                              {
                                "name": <str>
                              }
                            ],
                            "type": <str>
                          }
                        ],
                        "item": {
                          "accessType": <str>,
                          "adSupportedStreamReady": <bool>,
                          "album": {
                            "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                            "id": <int>,
                            "title": <str>,
                            "vibrantColor": "#rrggbb",
                            "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
                          },
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": None,
                            "id": <int>,
                            "name": <str>,
                            "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                            "type": "MAIN"
                          },
                          "artists": [
                            {
                              "handle": None,
                              "id": <int>,
                              "name": <str>,
                              "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
                          "isrc": "CCXXXYYNNNNN",
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
                          "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                          "title": <str>,
                          "trackNumber": <int>,
                          "upload": <bool>,
                          "url": f"http://www.tidal.com/track/{id}",
                          "version": None,
                          "volumeNumber": <int>
                        },
                        "type": "track"
                      },
                      {
                        "credits": [
                          {
                            "contributors": [
                              {
                                "name": <str>
                              }
                            ],
                            "type": <str>
                          }
                        ],
                        "item": {
                          "adSupportedStreamReady": <bool>,
                          "adsPrePaywallOnly": <bool>,
                          "adsUrl": None,
                          "album": {
                            "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                            "id": <int>,
                            "title": <str>,
                            "vibrantColor": "#rrggbb",
                            "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
                          },
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": None,
                            "id": <int>,
                            "name": <str>,
                            "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                            "type": "MAIN"
                          },
                          "artists": [
                            {
                              "handle": None,
                              "id": <int>,
                              "name": <str>,
                              "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                              "type": <str>
                            }
                          ],
                          "djReady": <bool>,
                          "duration": <int>,
                          "explicit": <bool>,
                          "id": <int>,
                          "imageId": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                          "imagePath": None,
                          "popularity": <int>,
                          "quality": <str>,
                          "releaseDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                          "stemReady": <bool>,
                          "streamReady": <bool>,
                          "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                          "title": <str>,
                          "trackNumber": <int>,
                          "type": "Music Video",
                          "vibrantColor": "#rrggbb",
                          "volumeNumber": <int>
                        },
                        "type": "video"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._get_album_resource(
            "items/credits", album_id, country_code, limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_album_review(
        self, album_id: int | str, /, country_code: str | None = None
    ) -> dict[str, str]:
        """
        Get TIDAL catalog information for a review of or synopsis for an
        album.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        review : dict[str, Any]
            TIDAL catalog information for the review of or synopsis for
            the album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "lastUpdated": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                    "source": <str>,
                    "summary": <str>,
                    "text": <str>,
                  }
        """
        return self._get_album_resource("review", album_id, country_code)

    @TTLCache.cached_method(ttl="catalog")
    def get_similar_albums(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for albums similar to the
        specified album.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

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

        Returns
        -------
        albums : dict[str, Any]
            Pages of TIDAL catalog information for the similar albums.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "adSupportedStreamReady": <bool>,
                        "allowStreaming": <bool>,
                        "artist": {
                          "handle": None,
                          "id": <int>,
                          "name": <str>,
                          "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                          "type": "MAIN"
                        },
                        "artists": [
                          {
                            "handle": None,
                            "id": <int>,
                            "name": <str>,
                            "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                            "type": <str>
                          }
                        ],
                        "audioModes": <list[str]>,
                        "audioQuality": <str>,
                        "copyright": <str>,
                        "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
                        "releaseDate": "YYYY-MM-DD",
                        "stemReady": <bool>,
                        "streamReady": <bool>,
                        "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                        "title": <str>,
                        "type": "ALBUM",
                        "upc": <str>,
                        "upload": <bool>,
                        "url": "http://www.tidal.com/album/{id},
                        "version": <str>,
                        "vibrantColor": "#rrggbb",
                        "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "source": <str>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._get_album_resource(
            "similar", album_id, country_code, limit=limit, offset=offset
        )

    @_copy_docstring(PrivatePagesAPI.get_album_page)
    def get_album_page(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
        locale: str | None = None,
    ) -> dict[str, Any]:
        return self._client.pages.get_album_page(
            album_id, country_code, device_type=device_type, locale=locale
        )

    @_copy_docstring(PrivateUsersAPI.favorite_albums)
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
        return self._client.users.get_favorite_albums(
            user_id,
            country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            reverse=reverse,
        )

    @_copy_docstring(PrivateUsersAPI.favorite_albums)
    def favorite_albums(
        self,
        album_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        missing_ok: bool | None = None,
    ) -> None:
        self._client.users.favorite_albums(
            album_ids,
            user_id,
            country_code,
            missing_ok=missing_ok,
        )

    @_copy_docstring(PrivateUsersAPI.unfavorite_albums)
    def unfavorite_albums(
        self,
        album_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        self._client.users.unfavorite_albums(album_ids, user_id)

    def _get_album_resource(
        self,
        resource: str,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a resource related to an
        album.

        Parameters
        ----------
        resource : str; positional-only
            Related resource type.

            **Valid values**: :code:`"credits"`, :code:`"items"`,
            :code:`"items/credits"`, :code:`"reviews"`,
            :code:`"similar"`.

        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

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
            the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        resource : dict[str, Any]
            Pages of TIDAL catalog information for the related resource.
        """
        params = {}
        self._client._resolve_country_code(country_code, params)
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"v1/albums/{album_id}/{resource}", params=params
        ).json()
