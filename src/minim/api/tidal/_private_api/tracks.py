import base64
from typing import Any
import xml.etree.ElementTree as ET

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import httpx
import json

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

    _AUDIO_QUALITIES = {"LOW", "HIGH", "LOSSLESS", "HI_RES", "HI_RES_LOSSLESS"}

    @TTLCache.cached_method(ttl="popularity")
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

    @TTLCache.cached_method(ttl="static")
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

    @TTLCache.cached_method(ttl="static")
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

    @TTLCache.cached_method(ttl="static")
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

    @TTLCache.cached_method(ttl="static")
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

    @TTLCache.cached_method(ttl="popularity")
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
                 Access and manage the user's collection.

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

    @TTLCache.cached_method(ttl="static")
    def get_track_playback_info(
        self,
        track_id: int | str,
        /,
        *,
        quality: str = "HI_RES_LOSSLESS",
        intent: str = "STREAM",
        preview: bool = False,
    ) -> dict[str, Any]:
        """
        Get playback information for a track.

        .. admonition:: Subscription
           :class: authorization-scope dropdown

           .. tab:: Optional

              TIDAL streaming plan
                 Stream full-length and high-resolution audio.
                 `Learn more. <https://tidal.com/pricing>`__

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"251380837"`.

        quality : str; keyword-only; default: :code:`"HI_RES_LOSSLESS"`
            Audio quality.

            **Valid values**:

            .. container::

               * :code:`"LOW"` – 64 kbps (22.05 kHz) MP3 without user
                 authentication or 96 kbps AAC with user authentication.
               * :code:`"HIGH"` – 320 kbps AAC.
               * :code:`"LOSSLESS"` – 1411 kbps (16-bit, 44.1 kHz) ALAC
                 or FLAC.
               * :code:`"HI_RES_LOSSLESS"` – Up to 9216 kbps (24-bit,
                 192 kHz) FLAC.

        intent : str; keyword-only; default: :code:`"STREAM"`
            Playback mode or intended use of the track.

            **Valid values**:

            .. container::

               * :code:`"OFFLINE"` – Offline download.
               * :code:`"STREAM"` – Streaming playback.

        preview : bool; keyword-only; default: :code:`False`
            Whether to return a 30-second preview instead of the full
            track.

        Returns
        -------
        playback_info : dict[str, Any]
            Playback information for the track.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albumPeakAmplitude": <float>,
                    "albumReplayGain": <float>,
                    "assetPresentation": <str>,
                    "audioMode": <str>,
                    "audioQuality": <str>,
                    "bitDepth": <int>,
                    "licenseSecurityToken": <str>,
                    "manifest": <str>,
                    "manifestHash": <str>,
                    "manifestMimeType": <str>,
                    "sampleRate": <int>,
                    "trackId": <int>,
                    "trackPeakAmplitude": <float>,
                    "trackReplayGain": <float>
                  }
        """
        self._client._validate_tidal_ids(track_id, _recursive=False)
        self._client._validate_type("quality", quality, str)
        quality = quality.strip().upper()
        if quality not in self._AUDIO_QUALITIES:
            audio_qualities_str = "', '".join(self._AUDIO_QUALITIES)
            raise ValueError(
                f"Invalid audio quality {quality!r}. "
                f"Valid values: '{audio_qualities_str}'."
            )
        self._client._validate_type("intent", intent, str)
        intent = intent.strip().upper()
        if intent not in self._PLAYBACK_MODES:
            playback_modes_str = "', '".join(self._PLAYBACK_MODES)
            raise ValueError(
                f"Invalid playback mode {intent!r}. "
                f"Valid values: '{playback_modes_str}'."
            )
        self._client._validate_type("preview", preview, bool)
        return self._client._request(
            "GET",
            f"v1/tracks/{track_id}/playbackinfo",
            params={
                "audioquality": quality,
                "assetpresentation": "PREVIEW" if preview else "FULL",
                "playbackmode": intent,
            },
        ).json()

    @_copy_docstring(PrivateUsersAPI.get_saved_tracks)
    def get_saved_tracks(
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
        return self._client.users.get_saved_tracks(
            user_id,
            country_code=country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @_copy_docstring(PrivateUsersAPI.save_tracks)
    def save_tracks(
        self,
        track_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        on_missing: str | None = None,
    ) -> None:
        self._client.users.save_tracks(
            track_ids,
            user_id=user_id,
            country_code=country_code,
            on_missing=on_missing,
        )

    @_copy_docstring(PrivateUsersAPI.remove_saved_tracks)
    def remove_saved_tracks(
        self,
        track_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        self._client.users.remove_saved_tracks(track_ids, user_id=user_id)

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

    def _get_track_stream(self, manifest: bytes | str, /) -> tuple[str, bytes]:
        """
        Get the audio stream data for a track.

        .. admonition:: Subscription
           :class: authorization-scope dropdown

           .. tab:: Optional

              TIDAL streaming plan
                 Stream full-length and high-resolution audio.
                 `Learn more. <https://tidal.com/pricing>`__

        Parameters
        ----------
        manifest : bytes or str; positional-only
            Metadata for the track's source files.

        Returns
        -------
        codec : str
            Audio codec.

        stream : bytes
            Audio stream data.
        """
        self._client._validate_type("manifest", manifest, bytes | str)
        if isinstance(manifest, str):
            manifest = base64.b64decode(manifest)

        if manifest[0] == 123:  # JSON
            manifest = json.loads(manifest)
            codec = manifest["codecs"]
            stream = httpx.get(manifest["urls"][0]).content
            if (encryption_type := manifest["encryptionType"]) == "OLD_AES":
                key_id = base64.b64decode(manifest["keyId"])
                key_nonce = (
                    Cipher(
                        algorithms.AES(
                            b"P\x89SLC&\x98\xb7\xc6\xa3\n?P.\xb4\xc7"
                            b"a\xf8\xe5n\x8cth\x13E\xfa?\xbah8\xef\x9e"
                        ),
                        modes.CBC(key_id[:16]),
                    )
                    .decryptor()
                    .update(key_id[16:])
                )
                stream = (
                    Cipher(
                        algorithms.AES(key_nonce[:16]),
                        modes.CTR(key_nonce[16:32]),
                    )
                    .decryptor()
                    .update(stream)
                )
            elif encryption_type != "NONE":
                raise RuntimeError(
                    f"Unknown encryption type {encryption_type!r}."
                )
        elif manifest[0] == 60:  # XML
            manifest = ET.fromstring(manifest)
            namespace = ".//{urn:mpeg:dash:schema:mpd:2011}"
            codec = manifest.find(
                f"{namespace}Representation",
            ).get("codecs")
            segments = manifest.find(
                f"{namespace}SegmentTemplate",
            )
            segment_template = segments.get("media").replace("$Number$", "{}")
            stream = httpx.get(
                segments.get("initialization")
            ).content + b"".join(
                httpx.get(segment_template.format(num)).content
                for num in range(
                    1,
                    sum(
                        int(segment.get("r") or 1)
                        for segment in segments.findall(f"{namespace}S")
                    )
                    + 2,
                )
            )
        else:
            raise ValueError(
                "`manifest`, when decoded, is not in the JSON format "
                "or XML format."
            )

        return codec, stream
