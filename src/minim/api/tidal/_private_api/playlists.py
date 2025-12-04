from typing import TYPE_CHECKING, Any

from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class PrivatePlaylistsAPI(ResourceAPI):
    """
    Playlists API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _client: "PrivateTIDALAPI"

    def get_playlist(
        self, playlist_uuid: str, /, country_code: str | None = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a single playlist.

        Parameters
        ----------
        playlist_uuid : str; positional-only, optional
            UUID of the TIDAL playlist.

            **Example**: :code:`"36ea71a8-445e-41a4-82ab-6628c581535d"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        playlist : dict[str, Any]
            TIDAL content metadata for the playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "created": <str>,
                    "creator": {
                      "id": <int>
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
                        "picture": null,
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
        """
        if country_code is None:
            country_code = self._client._my_country_code
        else:
            self._client._validate_country_code(country_code)
        return self._client._request(
            "GET",
            f"v1/playlists/{playlist_uuid}",
            params={"countryCode": country_code},
        ).json()

    def get_playlist_items(
        self,
        playlist_uuid: str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for tracks and videos in a
        playlist.

        Parameters
        ----------
        playlist_uuid : str; positional-only, optional
            UUID of the TIDAL playlist.

            **Example**: :code:`"36ea71a8-445e-41a4-82ab-6628c581535d"`.

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

        Returns
        -------
        items : dict[str, Any]
            Pages of TIDAL catalog information for the tracks and videos
            in the playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "cut": <Any>,
                        "item": {
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
                          "dateAdded": <str>,
                          "description": <str>,
                          "djReady": <bool>,
                          "duration": <int>,
                          "editable": <bool>,
                          "explicit": <bool>,
                          "id": <int>,
                          "index": <int>,
                          "isrc": <str>,
                          "itemUuid": <str>,
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
                        "cut": <Any>,
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
                          "dateAdded": <str>,
                          "djReady": <bool>,
                          "duration": <int>,
                          "explicit": <bool>,
                          "id": <int>,
                          "imageId": <str>,
                          "imagePath": <str>,
                          "index": <int>,
                          "itemUuid": <str>,
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
                        "type": "video"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
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
            "GET", f"v1/playlists/{playlist_uuid}/items", params=params
        ).json()

    def get_playlist_recommended_tracks(
        self,
        playlist_uuid: str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for tracks recommended based on a
        given playlist.

        Parameters
        ----------
        playlist_uuid : str; positional-only, optional
            UUID of the TIDAL playlist.

            **Example**: :code:`"36ea71a8-445e-41a4-82ab-6628c581535d"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`100`.

            **Default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next set of tracks.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        tracks : dict[str, Any]
            Pages of TIDAL catalog information for the recommended
            tracks.

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
                            "releaseDate": <str>,
                            "title": <str>,
                            "url": <str>,
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
                          "copyright": <str>,
                          "description": <str>,
                          "djReady": <bool>,
                          "doublePopularity": <float>,
                          "duration": <int>,
                          "editable": <bool>,
                          "explicit": <bool>,
                          "id": <int>,
                          "isrc": <str>,
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
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication(
            "playlists.get_playlist_recommended_tracks"
        )
        params = {}
        self._client._resolve_country_code(country_code, params)
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET",
            f"v1/playlists/{playlist_uuid}/recommendations/items",
            params=params,
        ).json()
