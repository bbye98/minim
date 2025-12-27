from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import PrivateTIDALResourceAPI
from .pages import PrivatePagesAPI
from .users import PrivateUsersAPI


class PrivateAlbumsAPI(PrivateTIDALResourceAPI):
    """
    Albums API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

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
                    "copyright": <str>,
                    "cover": <str>,
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
        """
        return self._get_resource(
            "albums", album_id, country_code=country_code
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_album_credits(
        self, album_id: int | str, /, country_code: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get TIDAL catalog information for an album's credits.

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
            TIDAL content metadata for the album's credits.

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
        return self._get_resource_relationship(
            "albums", album_id, "credits", country_code=country_code
        )

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
            Page of TIDAL content metadata for the tracks and videos in
            the album.

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
                        "type": "track"
                      },
                      {
                        "item": {
                          "adSupportedStreamReady": <bool>,
                          "adsPrePaywallOnly": <bool>,
                          "adsUrl": <str>,
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
                          "type": "Music Video",
                          "vibrantColor": <str>,
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
        return self._get_resource_relationship(
            "albums",
            album_id,
            "items",
            country_code=country_code,
            limit=limit,
            offset=offset,
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
            Page of TIDAL content metadata for the credits of the tracks
            and videos in the album.

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
                          "adsUrl": <str>,
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
                          "type": "Music Video",
                          "vibrantColor": <str>,
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
        return self._get_resource_relationship(
            "albums",
            album_id,
            "items/credits",
            country_code=country_code,
            limit=limit,
            offset=offset,
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
            TIDAL content metadata for the review of or synopsis for the
            album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "lastUpdated": <str>,
                    "source": <str>,
                    "summary": <str>,
                    "text": <str>,
                  }
        """
        return self._get_resource_relationship(
            "albums", album_id, "review", country_code=country_code
        )

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
            Page of TIDAL content metadata for the similar albums.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "adSupportedStreamReady": <bool>,
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
                    "source": <str>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._get_resource_relationship(
            "albums",
            album_id,
            "similar",
            country_code=country_code,
            limit=limit,
            offset=offset,
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
        descending: bool | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_favorite_albums(
            user_id,
            country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
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
