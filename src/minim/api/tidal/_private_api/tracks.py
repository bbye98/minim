from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import PrivateTIDALResourceAPI
from .users import PrivateUsersAPI


class PrivateTracksAPI(PrivateTIDALResourceAPI):
    """
    Tracks API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="catalog")
    def get_track(
        self, track_id: int | str, /, country_code: str | None = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a single track.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"251380837"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        track : dict[str, Any]
            TIDAL content metadata for the track.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

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
        """
        return self._get_resource(
            "tracks", track_id, country_code=country_code
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_track_contributors(
        self,
        track_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for an track's contributors.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"251380837"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of contributors to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first contributor to return. Use with `limit`
            to get the next batch of contributors.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        contributors : dict[str, Any]
            TIDAL content metadata for the track's contributors.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "name": <str>,
                        "role": <str>
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "contributors",
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_track_credits(
        self, track_id: int | str, /, country_code: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get TIDAL catalog information for an track's credits.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"251380837"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        credits : dict[str, Any]
            TIDAL content metadata for the track's credits.

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
            "tracks", track_id, "credits", country_code=country_code
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_track_lyrics(
        self, track_id: int | str, /, country_code: str | None = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a track's lyrics.

        .. admonition:: Subscription
           :class: authorization-scope

           .. tab:: Required

              TIDAL streaming plan
                 Access track and video playback information.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"251380837"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        lyrics : dict[str, Any]
            TIDAL content metadata for the track's formatted and/or
            time-synced lyrics.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "trackId": <int>,
                    "lyricsProvider": <str>,
                    "providerCommontrackId": <str>,
                    "providerLyricsId": <str>,
                    "lyrics": <str>,
                    "subtitles": <str>,
                    "isRightToLeft": <bool>
                  }
        """
        self._client._require_subscription("tracks.get_track_lyrics")
        return self._get_resource_relationship(
            "tracks", track_id, "lyrics", country_code=country_code
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_track_mix_id(
        self, track_id: int | str, /, country_code: str | None = None
    ) -> dict[str, str]:
        """
        Get the TIDAL ID of a track's mix.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"251380837"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        mix_id : dict[str, str]
            TIDAL ID of the track's mix.

            **Sample response**: :code:`{"id": <str>}`.
        """
        return self._get_resource_relationship(
            "tracks", track_id, "mix", country_code=country_code
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_track_recommendations(
        self,
        track_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for tracks recommended based on a
        given track.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations and view or modify the
                 user's collection.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"251380837"`.

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
        tracks : dict[str, Any]
            Page of TIDAL content metadata for the recommended tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "sources": [
                          "SUGGESTED_TRACKS"
                        ],
                        "track": {
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
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication(
            "tracks.get_track_recommendations"
        )
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "recommendations",
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @_copy_docstring(PrivateUsersAPI.get_favorite_tracks)
    def get_favorite_tracks(
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
        return self._client.users.get_favorite_tracks(
            user_id,
            country_code=country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @_copy_docstring(PrivateUsersAPI.favorite_tracks)
    def favorite_tracks(
        self,
        track_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        on_missing: str | None = None,
    ) -> None:
        self._client.users.favorite_tracks(
            track_ids,
            user_id=user_id,
            country_code=country_code,
            on_missing=on_missing,
        )

    @_copy_docstring(PrivateUsersAPI.unfavorite_tracks)
    def unfavorite_tracks(
        self,
        track_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        self._client.users.unfavorite_tracks(track_ids, user_id=user_id)

    @_copy_docstring(PrivateUsersAPI.get_blocked_tracks)
    def get_blocked_tracks(
        self,
        user_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_blocked_tracks(
            user_id, limit=limit, offset=offset
        )

    @_copy_docstring(PrivateUsersAPI.block_track)
    def block_track(
        self, track_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        self._client.users.block_track(track_id, user_id=user_id)

    @_copy_docstring(PrivateUsersAPI.unblock_track)
    def unblock_track(
        self, track_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        self._client.users.unblock_track(track_id, user_id=user_id)

    @TTLCache.cached_method(ttl="catalog")
    def get_track_pre_paywall_playback_info(
        self, track_id: int | str, /
    ) -> dict[str, Any]:
        """ """
        pass  # TODO

    @TTLCache.cached_method(ttl="catalog")
    def get_track_post_paywall_playback_info(
        self, track_id: int | str, /
    ) -> dict[str, Any]:
        """ """
        pass  # TODO

    def _get_track_playback_info(
        self, track_id: int | str, paywall_phase: str, /
    ) -> dict[str, Any]:
        """ """
        pass  # TODO
