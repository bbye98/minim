import base64
import json
import re
from typing import Any

import httpx

from ..._shared import TTLCache, _copy_docstring
from ._shared import PrivateTIDALResourceAPI
from .pages import PrivatePagesAPI
from .users import PrivateUsersAPI


class PrivateVideosAPI(PrivateTIDALResourceAPI):
    """
    Videos API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _VIDEO_QUALITIES = {"AUDIO_ONLY", "LOW", "MEDIUM", "HIGH"}

    @TTLCache.cached_method(ttl="catalog")
    def get_video(
        self, video_id: int | str, /, country_code: str | None = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a single video.

        Parameters
        ----------
        video_id : int or str; positional-only
            TIDAL ID of the video.

            **Examples**: :code:`29597422`, :code:`"59727844"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        video : dict[str, Any]
            TIDAL content metadata for the video.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "adSupportedStreamReady": <bool>,
                    "adsPrePaywallOnly": <bool>,
                    "adsUrl": <str>,
                    "album": {},
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
                    "videoNumber": <int>,
                    "type": <str>,
                    "vibrantColor": <str>,
                    "volumeNumber": <int>
                  }
        """
        return self._get_resource(
            "videos", video_id, country_code=country_code
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_video_contributors(
        self,
        video_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a video's contributors.

        Parameters
        ----------
        video_id : int or str; positional-only
            TIDAL ID of the video.

            **Examples**: :code:`29597422`, :code:`"59727844"`.

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
        contributors : dict[str, Any]
            TIDAL content metadata for the video's contributors.

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
            "videos",
            video_id,
            "contributors",
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @_copy_docstring(PrivatePagesAPI.get_video_page)
    def get_video_page(
        self,
        video_id: int | str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
        locale: str | None = None,
    ) -> dict[str, Any]:
        return self._client.pages.get_video_page(
            video_id,
            country_code=country_code,
            device_type=device_type,
            locale=locale,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_video_playback_info(
        self,
        video_id: int | str,
        /,
        *,
        quality: str = "HIGH",
        intent: str = "STREAM",
        preview: bool = False,
    ) -> dict[str, Any]:
        """
        Get playback information for a video.

        .. admonition:: Subscription
           :class: authorization-scope dropdown

           .. tab:: Required

              TIDAL streaming plan
                 Stream full-length videos.
                 `Learn more. <https://tidal.com/pricing>`__

        Parameters
        ----------
        video_id : int or str; positional-only
            TIDAL ID of the video.

            **Examples**: :code:`29597422`, :code:`"59727844"`.

        quality : str; keyword-only; default: :code:`"HIGH"`
            Video quality.

            **Valid values**:

            .. container::

               * :code:`"AUDIO_ONLY"` – 96 kbps AAC audio only.
               * :code:`"LOW"` – Up to 360p H.264 video, AAC-LC audio.
               * :code:`"MEDIUM"` – Up to 720p H.264 video, AAC-LC
                 audio.
               * :code:`"HIGH"` – Up to 1080p H.264 video, AAC-LC audio.

        intent : str; keyword-only; default: :code:`"STREAM"`
            Playback mode or intended use of the video.

            **Valid values**:

            .. container::

               * :code:`"OFFLINE"` – Offline download.
               * :code:`"STREAM"` – Streaming playback.

        preview : bool; keyword-only; default: :code:`False`
            Whether to return a 30-second preview instead of the full
            video.

        Returns
        -------
        playback_info : dict[str, Any]
            Playback information for the video.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "assetPresentation": <str>,
                    "licenseSecurityToken": <str>,
                    "manifest": <str>,
                    "manifestHash": <str>,
                    "manifestMimeType": <str>,
                    "streamType": <str>,
                    "trackPeakAmplitude": <float>,
                    "trackReplayGain": <float>,
                    "videoId": <int>,
                    "videoQuality": <str>
                  }
        """
        self._client._require_subscription("videos.get_video_playback_info")
        self._client._validate_tidal_ids(video_id, _recursive=False)
        self._client._validate_type("quality", quality, str)
        quality = quality.strip().upper()
        if quality not in self._VIDEO_QUALITIES:
            video_qualities_str = "', '".join(self._VIDEO_QUALITIES)
            raise ValueError(
                f"Invalid video quality {quality!r}. "
                f"Valid values: '{video_qualities_str}'."
            )
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
            f"v1/videos/{video_id}/playbackinfo",
            params={
                "videoquality": quality,
                "assetpresentation": "PREVIEW" if preview else "FULL",
                "playbackmode": intent,
            },
        ).json()

    @_copy_docstring(PrivateUsersAPI.get_favorite_videos)
    def get_favorite_videos(
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
        return self._client.users.get_favorite_videos(
            user_id,
            country_code=country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @_copy_docstring(PrivateUsersAPI.favorite_videos)
    def favorite_videos(
        self,
        video_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
        country_code: str | None = None,
        *,
        on_missing: str | None = None,
    ) -> None:
        self._client.users.favorite_videos(
            video_ids,
            user_id=user_id,
            country_code=country_code,
            on_missing=on_missing,
        )

    @_copy_docstring(PrivateUsersAPI.unfavorite_videos)
    def unfavorite_videos(
        self,
        video_ids: int | str | list[int | str],
        /,
        user_id: int | str | None = None,
    ) -> None:
        self._client.users.unfavorite_videos(video_ids, user_id=user_id)

    @_copy_docstring(PrivateUsersAPI.get_blocked_videos)
    def get_blocked_videos(
        self,
        user_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_blocked_videos(
            user_id, limit=limit, offset=offset
        )

    @_copy_docstring(PrivateUsersAPI.block_video)
    def block_video(
        self, video_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        self._client.users.block_video(video_id, user_id=user_id)

    @_copy_docstring(PrivateUsersAPI.unblock_video)
    def unblock_video(
        self, video_id: int | str, /, user_id: int | str | None = None
    ) -> None:
        self._client.users.unblock_video(video_id, user_id=user_id)

    def _get_video_stream(self, manifest: bytes | str, /) -> tuple[str, bytes]:
        """
        Get the video stream data for a music video.

        .. admonition:: Subscription
           :class: authorization-scope dropdown

           .. tab:: Optional

              TIDAL streaming plan
                 Stream full-length and high-resolution audio.
                 `Learn more. <https://tidal.com/pricing>`__

        Parameters
        ----------
        manifest : bytes or str; positional-only
            Metadata for the video's source files.

        Returns
        -------
        codec : str
            Video codec.

        stream : bytes
            Video stream data.
        """
        self._client._validate_type("manifest", manifest, bytes | str)
        if isinstance(manifest, str):
            manifest = base64.b64decode(manifest)

        if manifest[0] == 123:  # JSON
            _, codec, m3u = max(
                re.compile(
                    r"#EXT-X-STREAM-INF:(?=[^\n]*BANDWIDTH=(\d+))"
                    r'(?=[^\n]*CODECS="([^"]+)")[^\n]+\n(\S+)'
                ).findall(httpx.get(json.loads(manifest)["urls"][0]).text),
                key=lambda m3u: int(m3u[0]),
            )
            return codec, b"".join(
                httpx.get(ts).content
                for ts in re.compile("(?<=\n).*(http.*)").findall(
                    httpx.get(m3u).text
                )
            )
        elif manifest[0] == 60:  # XML (audio-only)
            return self._client.tracks._get_track_stream(manifest)
        else:
            raise ValueError(
                "`manifest`, when decoded, is not in the JSON format "
                "or XML format."
            )
