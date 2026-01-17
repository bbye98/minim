from typing import Any

from ..._shared import TTLCache
from ._shared import PrivateTIDALResourceAPI


class PrivateSearchAPI(PrivateTIDALResourceAPI):
    """
    Search API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    def _search_resource(
        self,
        resource_type: str | None,
        query: str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for albums, artists, playlists,
        tracks, or videos that match a keyword string.

        Parameters
        ----------
        resource_type : str or None; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"playlists"`, :code:`"tracks"`, :code:`"videos"`.

        query : str; positional-only
            Search query.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of items to return for each resource type.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first item to return for each resource type.
            Use with `limit` to get the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        results : dict[str, Any]
            Page of TIDAL content metadata for the matching items.
        """
        endpoint = "v1/search"
        if resource_type is not None:
            endpoint += f"/{resource_type}"
        self._validate_type("query", query, str)
        query = query.strip()
        if not len(query):
            raise ValueError("No search query provided.")
        params = {"query": query}
        self._client._resolve_country_code(country_code, params=params)
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request("GET", endpoint, params=params).json()

    @TTLCache.cached_method(ttl="search")
    def search(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for albums, artists, playlists,
        tracks, and videos that match a search query.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of items to return for each resource type.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first item to return for each resource type.
            Use with `limit` to get the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        items : dict[str, Any]
            Page of TIDAL content metadata for the matching items.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albums": {
                      "items": [
                        {
                          "adSupportedStreamReady": <bool>,
                          "allowStreaming": <bool>,
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
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "totalNumberOfItems": <int>
                    },
                    "artists": {
                      "items": [
                        {
                          "artistRoles": [
                            {
                              "category": <str>,
                              "categoryId": <int>
                            }
                          ],
                          "artistTypes": <list[str]>
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
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "totalNumberOfItems": <int>
                    },
                    "playlists": {
                      "items": [
                        {
                          "created": <str>,
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "selectedAlbumCoverFallback": None,
                            "type": <str>
                          },
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "popularity": <int>,
                          "promotedArtists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": "MAIN"
                            }
                          ],
                          "publicPlaylist": <bool>,
                          "squareImage": <str>,
                          "title": <str>,
                          "type": <str>,
                          "url": f"http://www.tidal.com/playlist/{uuid}",
                          "uuid": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "totalNumberOfItems": <int>
                    },
                    "topHit": {
                      "type": "ARTISTS",
                      "value": {
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
                    },
                    "tracks": {
                      "items": [
                        {
                          "accessType": <str>,
                          "adSupportedStreamReady": <bool>,
                          "album": {
                            "cover": <str>,
                            "id": <int>,
                            "releaseDate": <str>,
                            "title": <str>,
                            "vibrantColor": <str>,
                            "videoCover": <str>
                          },
                          "allowStreaming": <bool>,
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
                          "url": f"http://www.tidal.com/track/{id}",
                          "version": <str>,
                          "volumeNumber": <int>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "totalNumberOfItems": <int>
                    },
                    "videos": {
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
                          "quality": <int>,
                          "releaseDate": <str>,
                          "stemReady": <bool>,
                          "streamReady": <bool>,
                          "streamStartDate": <str>,
                          "title": <str>,
                          "trackNumber": <int>,
                          "type": "Music Video",
                          "vibrantColor": <str>,
                          "volumeNumber": <int>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "totalNumberOfItems": <int>
                    }
                  }
        """
        return self._search_resource(
            None, query, country_code=country_code, limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="search")
    def search_albums(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for albums that match a search
        query.

        Parameters
        ----------
        query : str; positional-only
            Search query.

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
            Page of TIDAL content metadata for the matching albums.

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
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._search_resource(
            "albums",
            query,
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @TTLCache.cached_method(ttl="search")
    def search_artists(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for artists that match a search
        query.

        Parameters
        ----------
        query : str; positional-only
            Search query.

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

        Returns
        -------
        artists : dict[str, Any]
            Page of TIDAL content metadata for the matching artists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "artistRoles": [
                          {
                            "category": <str>,
                            "categoryId": <int>
                          }
                        ],
                        "artistTypes": <list[str]>
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
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._search_resource(
            "artists",
            query,
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @TTLCache.cached_method(ttl="search")
    def search_playlists(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for playlists that match a search
        query.

        Parameters
        ----------
        query : str; positional-only
            Search query.

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

        Returns
        -------
        playlists : dict[str, Any]
            TIDAL catalog information for the matching playlists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created": <str>,
                        "creator": {
                          "id": <int>,
                          "name": <str>,
                          "picture": <str>,
                          "selectedAlbumCoverFallback": None,
                          "type": <str>
                        },
                        "customImageUrl": <str>,
                        "description": <str>,
                        "duration": <int>,
                        "image": <str>,
                        "lastItemAddedAt": <str>,
                        "lastUpdated": <str>,
                        "numberOfTracks": <int>,
                        "numberOfVideos": <int>,
                        "popularity": <int>,
                        "promotedArtists": [
                          {
                            "handle": <str>,
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": "MAIN"
                          }
                        ],
                        "publicPlaylist": <bool>,
                        "squareImage": <str>,
                        "title": <str>,
                        "type": <str>,
                        "url": <str>,
                        "uuid": <str>
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._search_resource(
            "playlists",
            query,
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @TTLCache.cached_method(ttl="search")
    def search_tracks(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for tracks that match a search
        query.

        Parameters
        ----------
        query : str; positional-only
            Search query.

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
            Index of the first track to return. Use with `limit` to
            get the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of TIDAL content metadata for the matching tracks.

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
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._search_resource(
            "tracks",
            query,
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @TTLCache.cached_method(ttl="search")
    def search_videos(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for videos that match a search
        query.

        Parameters
        ----------
        query : str; positional-only
            Search query.

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
            Index of the first video to return. Use with `limit` to
            get the next batch of videos.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        videos : dict[str, Any]
            Page of TIDAL content metadata for the matching videos.

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
                        "quality": <int>,
                        "releaseDate": <str>,
                        "stemReady": <bool>,
                        "streamReady": <bool>,
                        "streamStartDate": <str>,
                        "title": <str>,
                        "trackNumber": <int>,
                        "type": "Music Video",
                        "vibrantColor": <str>,
                        "volumeNumber": <int>
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._search_resource(
            "videos",
            query,
            country_code=country_code,
            limit=limit,
            offset=offset,
        )
