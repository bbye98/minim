from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI, _copy_docstring
from .pages import PrivatePagesAPI
from .users import PrivateUsersAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class PrivateArtistsAPI(ResourceAPI):
    """
    Artists API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _ALBUM_FILTERS = {"COMPILATIONS", "EPSANDSINGLES"}
    _client: "PrivateTIDALAPI"

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
            country associated with the user account is used.

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
                    "selectedAlbumCoverFallback": <str>,
                    "spotlighted": <bool>,
                    "url": <str>,
                    "userId": <int>
                  }
        """
        if country_code is None:
            country_code = self._client._my_country_code
        else:
            self._client._validate_country_code(country_code)
        return self._client._request(
            "GET",
            f"v1/artists/{artist_id}",
            params={"countryCode": country_code},
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_albums(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        filter: str | None = None,
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
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        filter : str; keyword-only; optional
            Filter for the types of albums to return.

            **Valid values**: :code:`"COMPILATIONS"`, :code:`"EPSANDSINGLES"`.

        limit : int; keyword-only; optional
            Maximum number of albums to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first album to return. Use with `limit` to get
            the next set of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        albums : dict[str, Any]
            Pages of TIDAL catalog information for the artist's albums.

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
        if filter is not None:
            if filter not in self._ALBUM_FILTERS:
                filters = "', '".join(sorted(self._ALBUM_FILTERS))
                raise ValueError(
                    f"Invalid filter {filter!r}. Valid values: '{filters}'."
                )
            params["filter"] = filter
        return self._get_artist_resource(
            "albums",
            artist_id,
            country_code,
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
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        biography : dict[str, Any]
            TIDAL catalog information for the artist's biography.

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
        return self._get_artist_resource("bio", artist_id, country_code)

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
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of links to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first link to return. Use with `limit` to get
            the next set of links.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        links : dict[str, Any]
            Pages of TIDAL catalog information for links to websites
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
        return self._get_artist_resource(
            "links",
            artist_id,
            country_code,
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
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        mix_id : dict[str, str]
            TIDAL ID of the artist's mix.

            **Sample response**: :code:`{"id": <str>}`.
        """
        return self._get_artist_resource("mix", artist_id, country_code)

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

        Returns
        -------
        radio : dict[str, Any]
            Pages of TIDAL catalog information for the artist radio.

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
        return self._get_artist_resource(
            "radio",
            artist_id,
            country_code,
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
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next set of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        top_tracks : dict[str, Any]
            Pages of TIDAL catalog information for the artist's top
            tracks.

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
        return self._get_artist_resource(
            "toptracks",
            artist_id,
            country_code,
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
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of videos to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first video to return. Use with `limit` to get
            the next set of videos.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        videos : dict[str, Any]
            Pages of TIDAL catalog information for the artist's videos.

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
        return self._get_artist_resource(
            "videos",
            artist_id,
            country_code,
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
            the next set of artists.

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
                        "selectedAlbumCoverFallback": <str>,
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
        return self._get_artist_resource(
            "similar",
            artist_id,
            country_code,
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
        reverse: bool | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_favorite_artists(
            user_id,
            country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            reverse=reverse,
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

    def _get_artist_resource(
        self,
        resource: str,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a resource related to an
        artist.

        Parameters
        ----------
        resource : str; positional-only
            Related resource type.

            **Valid values**: :code:`"albums"`, :code:`"bio"`,
            :code:`"links"`, :code:`"mix"`, :code:`"radio"`,
            :code:`"toptracks"`, :code:`"videos"`, :code:`"similar"`.

        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

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

        params : dict[str, Any]; keyword-only; optional
            Existing dictionary holding URL query parameters. If not
            provided, a new dictionary will be created.

        Returns
        -------
        resource : dict[str, Any]
            Pages of TIDAL catalog information for the related resource.
        """
        if params is None:
            params = {}
        self._client._resolve_country_code(country_code, params)
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"v1/artists/{artist_id}/{resource}", params=params
        ).json()
