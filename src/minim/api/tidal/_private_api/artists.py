from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import PrivateTIDALResourceAPI
from .pages import PrivatePagesAPI
from .users import PrivateUsersAPI


class PrivateArtistsAPI(PrivateTIDALResourceAPI):
    """
    Artists API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _ALBUM_TYPES = {"COMPILATIONS", "EPSANDSINGLES"}

    @TTLCache.cached_method(ttl="catalog")
    def get_artist(
        self, artist_id: int | str, /, country_code: str | None = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a single artist.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        artist : dict[str, Any]
            TIDAL content metadata for the artist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
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
        """
        return self._get_resource(
            "artists", artist_id, country_code=country_code
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_albums(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        album_type: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for an artist's albums.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        album_type : str; keyword-only; optional
            Album type to include in the results.

            **Valid values**: :code:`"COMPILATIONS"`, :code:`"EPSANDSINGLES"`.

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
            Page of TIDAL content metadata for the artist's albums.

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
                        "type": <str>,
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
        params = {}
        if album_type is not None:
            if album_type not in self._ALBUM_TYPES:
                album_types_str = "', '".join(sorted(self._ALBUM_TYPES))
                raise ValueError(
                    f"Invalid album type {album_type!r}. "
                    f"Valid values: '{album_types_str}'."
                )
            params["filter"] = album_type
        return self._get_resource_relationship(
            "artists",
            artist_id,
            "albums",
            country_code=country_code,
            limit=limit,
            offset=offset,
            params=params,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_biography(
        self, artist_id: int | str, /, country_code: str | None = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for an artist's biography.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        biography : dict[str, Any]
            TIDAL content metadata for the artist's biography.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "lastUpdated": <str>,
                    "source": <str>,
                    "summary": <str>,
                    "text": <str>
                  }
        """
        return self._get_resource_relationship(
            "artists", artist_id, "bio", country_code=country_code
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_links(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for links to websites associated
        with an artist.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of links to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first link to return. Use with `limit` to get
            the next batch of links.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        links : dict[str, Any]
            Page of TIDAL content metadata for links to websites
            associated with an artist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "siteName": <str>,
                        "url": <str>
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "source": <str>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._get_resource_relationship(
            "artists",
            artist_id,
            "links",
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_mix_id(
        self, artist_id: int | str, /, country_code: str | None = None
    ) -> dict[str, str]:
        """
        Get the TIDAL ID of an artist's mix.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        mix_id : dict[str, str]
            TIDAL ID of the artist's mix.

            **Sample response**: :code:`{"id": <str>}`.
        """
        return self._get_resource_relationship(
            "artists", artist_id, "mix", country_code=country_code
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_radio(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for radio stations generated from
        an artist's music catalog.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

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
        radio : dict[str, Any]
            Page of TIDAL content metadata for the items in the artist
            radio.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
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
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._get_resource_relationship(
            "artists",
            artist_id,
            "radio",
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_top_tracks(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for an artist's top tracks.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

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

        Returns
        -------
        top_tracks : dict[str, Any]
            Page of TIDAL content metadata for the artist's top tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
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
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._get_resource_relationship(
            "artists",
            artist_id,
            "toptracks",
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_videos(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for an artist's videos.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

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

        Returns
        -------
        videos : dict[str, Any]
            Page of TIDAL content metadata for the artist's videos.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
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
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._get_resource_relationship(
            "artists",
            artist_id,
            "videos",
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_similar_artists(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for other artists that are similar
        to an artist.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

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
            the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        similar_artists : dict[str, Any]
            Pages of TIDAL catalog information for the similar artists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "artistRoles": <list[str]>,
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
                        "relationType": <str>,
                        "selectedAlbumCoverFallback": None,
                        "spotlighted": <bool>,
                        "type": <str>,
                        "url": <str>,
                        "userId": <int>
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "source": <str>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._get_resource_relationship(
            "artists",
            artist_id,
            "similar",
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @_copy_docstring(PrivatePagesAPI.get_artist_page)
    def get_artist_page(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
        locale: str | None = None,
    ) -> dict[str, Any]:
        return self._client.pages.get_artist_page(
            artist_id, country_code, device_type=device_type, locale=locale
        )

    @_copy_docstring(PrivateUsersAPI.get_blocked_artists)
    def get_blocked_artists(
        self,
        user_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_blocked_artists(
            user_id, limit=limit, offset=offset
        )

    @_copy_docstring(PrivateUsersAPI.block_artist)
    def block_artist(
        self, artist_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        self._client.users.block_artists(artist_id, user_id)

    @_copy_docstring(PrivateUsersAPI.unblock_artist)
    def unblock_artist(
        self, artist_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        self._client.users.unblock_artists(artist_id, user_id)

    @_copy_docstring(PrivateUsersAPI.favorite_artists)
    def get_favorite_artists(
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
        return self._client.users.get_favorite_artists(
            user_id,
            country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @_copy_docstring(PrivateUsersAPI.favorite_artists)
    def favorite_artists(
        self,
        artist_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        missing_ok: bool | None = None,
    ) -> None:
        self._client.users.favorite_artists(
            artist_ids,
            user_id,
            country_code,
            missing_ok=missing_ok,
        )

    @_copy_docstring(PrivateUsersAPI.unfavorite_artists)
    def unfavorite_artists(
        self,
        artist_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        self._client.users.unfavorite_artists(artist_ids, user_id)
