from datetime import datetime
import time
from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import PrivateQobuzResourceAPI
from .search import PrivateSearchEndpoints
from .users import PrivateUsersAPI


class PrivateTracksAPI(PrivateQobuzResourceAPI):
    """
    Tracks API endpoints for the private Qobuz API.

    .. important::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    _INTENTS = {"download", "import", "stream"}

    @TTLCache.cached_method(ttl="popularity")
    def get_tracks(
        self, track_ids: int | str | list[int | str], /
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for one or more tracks.

        Parameters
        ----------
        track_ids : int, str, or list[int | str]; positional-only
            Qobuz IDs of the tracks.

            **Examples**: :code:`23929516`, :code:`"344521217"`,
            :code:`"23929516,344521217"`,
            :code:`[23929516, "344521217"]`.

        Returns
        -------
        tracks : dict[str, Any]
            Qobuz content metadata for the tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. tab:: Single track

                  .. code::

                     {
                       "album": {
                         "area": None,
                         "articles": [],
                         "artist": {
                           "albums_count": <int>,
                           "id": <int>,
                           "image": None,
                           "name": <str>,
                           "picture": None,
                           "slug": <str>
                         },
                         "artists": [
                           {
                             "id": <int>,
                             "name": <str>,
                             "roles": <list[str]>
                           }
                         ],
                         "awards": [
                           {
                             "award_id": <str>,
                             "award_slug": <str>,
                             "awarded_at": <int>,
                             "name": <str>,
                             "publication_id": <str>,
                             "publication_name": <str>,
                             "publication_slug": <str>,
                             "slug": <str>
                           }
                         ],
                         "catchline": <str>,
                         "composer": {
                           "albums_count": <int>,
                           "id": <int>,
                           "image": None,
                           "name": <str>,
                           "picture": None,
                           "slug": <str>
                         },
                         "copyright": <str>,
                         "created_at": <int>,
                         "description": <str>,
                         "description_language": <str>,
                         "displayable": <bool>,
                         "downloadable": <bool>,
                         "duration": <int>,
                         "genre": {
                           "color": <int>,
                           "id": <int>,
                           "name": <int>,
                           "path": <list[int]>,
                           "slug": <str>
                         },
                         "genres_list": <list[str]>,
                         "goodies": [],
                         "hires": <bool>,
                         "hires_streamable": <bool>,
                         "id": <str>,
                         "image": {
                           "back": None,
                           "large": <str>,
                           "small": <str>,
                           "thumbnail": <str>
                         },
                         "is_official": <bool>,
                         "label": {
                           "albums_count": <int>,
                           "id": <int>,
                           "name": <str>,
                           "slug": <str>,
                           "supplier_id": <int>
                         },
                         "maximum_bit_depth": <int>,
                         "maximum_channel_count": <int>,
                         "maximum_sampling_rate": <int>,
                         "maximum_technical_specifications": <str>,
                         "media_count": <int>,
                         "parental_warning": <bool>,
                         "period": None,
                         "popularity": <int>,
                         "previewable": <bool>,
                         "product_sales_factors_monthly": <int>,
                         "product_sales_factors_weekly": <int>,
                         "product_sales_factors_yearly": <int>,
                         "product_type": <str>,
                         "product_url": <str>,
                         "purchasable": <bool>,
                         "purchasable_at": <int>,
                         "qobuz_id": <int>,
                         "recording_information": <str>,
                         "relative_url": <str>,
                         "release_date_download": <str>,
                         "release_date_original": <str>,
                         "release_date_stream": <str>,
                         "release_tags": <list[str]>,
                         "release_type": <str>,
                         "released_at": <int>,
                         "sampleable": <bool>,
                         "slug": <str>,
                         "streamable": <bool>,
                         "streamable_at": <int>,
                         "subtitle": <str>,
                         "title": <str>,
                         "tracks_count": <int>,
                         "upc": <str>,
                         "url": <str>,
                         "version": <str>
                       },
                       "articles": [],
                       "audio_info": {
                         "replaygain_track_gain": <float>,
                         "replaygain_track_peak": <float>
                       },
                       "composer": {
                         "id": <int>,
                         "name": <str>
                       },
                       "copyright": <str>,
                       "created_at": <int>,
                       "displayable": <bool>,
                       "downloadable": <bool>,
                       "duration": <int>,
                       "hires": <bool>,
                       "hires_streamable": <bool>,
                       "id": <int>,
                       "indexed_at": <int>,
                       "isrc": <str>,
                       "maximum_bit_depth": <int>,
                       "maximum_channel_count": <int>,
                       "maximum_sampling_rate": <float>,
                       "media_number": <int>,
                       "parental_warning": <bool>,
                       "performer": {
                         "id": <int>,
                         "name": <str>
                       },
                       "performers": <str>,
                       "previewable": <bool>,
                       "purchasable": <bool>,
                       "purchasable_at": <int>,
                       "release_date_download": <str>,
                       "release_date_original": <str>,
                       "release_date_purchase": <str>,
                       "release_date_stream": <str>,
                       "sampleable":<bool>,
                       "streamable": <bool>,
                       "streamable_at": <int>,
                       "title": <str>,
                       "track_number": <int>,
                       "version": <str>,
                       "work": None
                     }

               .. tab:: Multiple tracks

                  .. code::

                     {
                       "items": {
                         "album": {
                           "area": None,
                           "articles": [],
                           "artist": {
                             "albums_count": <int>,
                             "id": <int>,
                             "image": None,
                             "name": <str>,
                             "picture": None,
                             "slug": <str>
                           },
                           "artists": [
                             {
                               "id": <int>,
                               "name": <str>,
                               "roles": <list[str]>
                             }
                           ],
                           "awards": [
                             {
                               "award_id": <str>,
                               "award_slug": <str>,
                               "awarded_at": <int>,
                               "name": <str>,
                               "publication_id": <str>,
                               "publication_name": <str>,
                               "publication_slug": <str>,
                               "slug": <str>
                             }
                           ],
                           "catchline": <str>,
                           "composer": {
                             "albums_count": <int>,
                             "id": <int>,
                             "image": None,
                             "name": <str>,
                             "picture": None,
                             "slug": <str>
                           },
                           "copyright": <str>,
                           "created_at": <int>,
                           "description": <str>,
                           "description_language": <str>,
                           "displayable": <bool>,
                           "downloadable": <bool>,
                           "duration": <int>,
                           "genre": {
                             "color": <int>,
                             "id": <int>,
                             "name": <int>,
                             "path": <list[int]>,
                             "slug": <str>
                           },
                           "genres_list": <list[str]>,
                           "goodies": [],
                           "hires": <bool>,
                           "hires_streamable": <bool>,
                           "id": <str>,
                           "image": {
                             "back": None,
                             "large": <str>,
                             "small": <str>,
                             "thumbnail": <str>
                           },
                           "is_official": <bool>,
                           "label": {
                             "albums_count": <int>,
                             "id": <int>,
                             "name": <str>,
                             "slug": <str>,
                             "supplier_id": <int>
                           },
                           "maximum_bit_depth": <int>,
                           "maximum_channel_count": <int>,
                           "maximum_sampling_rate": <int>,
                           "maximum_technical_specifications": <str>,
                           "media_count": <int>,
                           "parental_warning": <bool>,
                           "period": None,
                           "popularity": <int>,
                           "previewable": <bool>,
                           "product_sales_factors_monthly": <int>,
                           "product_sales_factors_weekly": <int>,
                           "product_sales_factors_yearly": <int>,
                           "product_type": <str>,
                           "product_url": <str>,
                           "purchasable": <bool>,
                           "purchasable_at": <int>,
                           "qobuz_id": <int>,
                           "recording_information": <str>,
                           "relative_url": <str>,
                           "release_date_download": <str>,
                           "release_date_original": <str>,
                           "release_date_stream": <str>,
                           "release_tags": <list[str]>,
                           "release_type": <str>,
                           "released_at": <int>,
                           "sampleable": <bool>,
                           "slug": <str>,
                           "streamable": <bool>,
                           "streamable_at": <int>,
                           "subtitle": <str>,
                           "title": <str>,
                           "tracks_count": <int>,
                           "upc": <str>,
                           "url": <str>,
                           "version": <str>
                         },
                         "articles": [],
                         "audio_info": {
                           "replaygain_track_gain": <float>,
                           "replaygain_track_peak": <float>
                         },
                         "composer": {
                           "id": <int>,
                           "name": <str>
                         },
                         "copyright": <str>,
                         "created_at": <int>,
                         "displayable": <bool>,
                         "downloadable": <bool>,
                         "duration": <int>,
                         "hires": <bool>,
                         "hires_streamable": <bool>,
                         "id": <int>,
                         "indexed_at": <int>,
                         "isrc": <str>,
                         "maximum_bit_depth": <int>,
                         "maximum_channel_count": <int>,
                         "maximum_sampling_rate": <int>,
                         "media_number": <int>,
                         "parental_warning": <bool>,
                         "performer": {
                           "id": <int>,
                           "name": <str>
                         },
                         "performers": <str>,
                         "previewable": <bool>,
                         "purchasable": <bool>,
                         "purchasable_at": <int>,
                         "release_date_download": <str>,
                         "release_date_original": <str>,
                         "release_date_purchase": <str>,
                         "release_date_stream": <str>,
                         "sampleable":<bool>,
                         "streamable": <bool>,
                         "streamable_at": <int>,
                         "title": <str>,
                         "track_number": <int>,
                         "version": <str>,
                         "work": None
                       },
                       "total": <int>
                     }
        """
        self._client._validate_type(
            "track_ids", track_ids, int | str | tuple | list
        )
        track_ids = self._prepare_qobuz_ids(track_ids, data_type=list)
        if len(track_ids) > 1:
            return self._client._request(
                "POST",
                "track/getList",
                json={"tracks_id": track_ids},
            ).json()
        return self._client._request(
            "GET", "track/get", params={"track_id": track_ids[0]}
        ).json()

    @TTLCache.cached_method(ttl="static")
    def get_track_playback_info(
        self,
        track_id: int | str,
        /,
        *,
        format_id: int | str | None = None,
        intent: str | None = None,
        preview: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get playback information for a track.

        .. admonition:: Subscription
           :class: authorization-scope dropdown

           .. tab:: Optional

              Qobuz streaming plan
                 Stream full-length and high-resolution audio.
                 `Learn more. <https://www.qobuz.com/us-en/music
                 /streaming/offers>`__

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`23929516`, :code:`"344521217"`.

        format_id : int or str; keyword-only; optional
            Audio format identifier.

            .. container::

               **Valid values**:

               * :code:`5` – Constant 320 kbps bitrate MP3.
               * :code:`6` – CD-quality (16-bit, 44.1 kHz) FLAC.
               * :code:`7` – Up to 24-bit, 96 kHz FLAC.
               * :code:`27` – Up to 24-bit, 192 kHz FLAC.

        intent : str; keyword-only; optional
            Playback mode or intended use of the track.

            **Valid values**:

            .. container::

               * :code:`"download"` – Offline download.
               * :code:`"import"` – Library import.
               * :code:`"stream"` – Streaming playback.

            **API default**: :code:`"stream"`.

        preview : bool; keyword-only; optional
            Whether to return a 30-second preview instead of the full
            track.

            **API default**: :code:`False`.

        Returns
        -------
        playback_info : dict[str, Any]
            Playback information for the track.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "bit_depth": <int>,
                    "blob": <str>,
                    "duration": <int>,
                    "format_id": <int>,
                    "mime_type": <str>,
                    "restrictions": [
                      {
                        "code": <str>
                      }
                    ],
                    "sample": <bool>,
                    "sampling_rate": <float>,
                    "track_id": <int>,
                    "url": <str>
                  }
        """
        self._validate_qobuz_ids(track_id, _recursive=False)
        params = {"track_id": track_id}
        if format_id is not None:
            self._client._validate_numeric("format_id", format_id, int)
            if int(format_id) not in {5, 6, 7, 27}:
                raise ValueError(
                    f"Invalid format ID {format_id!r}. "
                    "Valid values: 5, 6, 7, 27."
                )
            params["format_id"] = format_id
        if intent is not None:
            self._client._validate_type("intent", intent, str)
            intent = intent.lower()
            if intent not in self._INTENTS:
                intents_str = "', '".join(self._INTENTS)
                raise ValueError(
                    f"Invalid intent {intent!r}. "
                    f"Valid values: '{intents_str}'."
                )
            params["intent"] = intent
        if preview is not None:
            self._client._validate_type("preview", preview, bool)
            params["sample"] = preview
        return self._client._request(
            "GET",
            "track/getFileUrl",
            params=params,
            signed=True,
            sig_params=params,
        ).json()

    def report_streaming_start(
        self,
        track_id: int | str,
        /,
        *,
        format_id: int | str,
        started_at: int | datetime,
        online: bool,
        local: bool,
        user_id: int | str | None = None,
        credential_id: int | str | None = None,
        device_id: int | str | None = None,
        intent: str | None = None,
        purchased: bool | None = None,
        preview: bool | None = None,
    ) -> dict[str, str]:
        """
        Report the start of a streaming event.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Report streaming.

        Parameters
        ----------
        track_id : int or str; positional-only
            Qobuz ID of the track.

            **Examples**: :code:`23929516`, :code:`"344521217"`.

        format_id : int or str; keyword-only
            Audio format identifier.

            .. container::

               **Valid values**:

               * :code:`5` – Constant 320 kbps bitrate MP3.
               * :code:`6` – CD-quality (16-bit, 44.1 kHz) FLAC.
               * :code:`7` – Up to 24-bit, 96 kHz FLAC.
               * :code:`27` – Up to 24-bit, 192 kHz FLAC.

        started_at : int or datetime.datetime; keyword-only
            Unix time at which the streaming started.

        online : bool; keyword-only
            Whether the streaming was performed online.

        local : bool; keyword-only
            Whether the streaming was played from a local source
            (:code:`True`) or from Qobuz servers (:code:`False`).

        user_id : int or str; keyword-only; optional
            Qobuz ID of the user who streamed the track. If not
            specified, the current user's Qobuz ID is used.

        credential_id : int or str; keyword-only; optional
           Qobuz ID of the credentials used for the streaming event.

        device_id : int or str; keyword-only; optional
           Qobuz ID of the streaming device.

        intent : str; keyword-only; optional
            Playback mode or intended use of the track.

            **Valid values**:

            .. container::

               * :code:`"download"` – Offline download.
               * :code:`"import"` – Library import.
               * :code:`"stream"` – Streaming playback.

            **API default**: :code:`"stream"`.

        purchased : bool; keyword-only; optional
            Whether the streamed track was purchased.

        preview : bool; keyword-only; optional
            Whether the streamed track is a 30-second preview instead of
            the full track.

        Returns
        -------
        response : dict[str, str]
            API JSON response.

            **Sample response**: :code:`{"code": 200,
            "status": "success", "transUId": <str>}`.
        """
        self._client._require_authentication("tracks.report_streaming_start")
        return self._report_streaming_event(
            track_id,
            format_id=format_id,
            started_at=started_at,
            online=online,
            local=local,
            user_id=user_id,
            credential_id=credential_id,
            device_id=device_id,
            intent=intent,
            purchased=purchased,
            preview=preview,
        )

    def report_streaming_end(
        self,
        track_id: int | str,
        /,
        *,
        format_id: int | str,
        started_at: int | datetime,
        duration: int,
        online: bool,
        local: bool,
        user_id: int | str | None = None,
        credential_id: int | str | None = None,
        device_id: int | str | None = None,
        intent: str | None = None,
        purchased: bool | None = None,
        preview: bool | None = None,
    ) -> dict[str, str]:
        """
        Report the end of a streaming event.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Report streaming.

        Parameters
        ----------
        track_id : int or str; positional-only
            Qobuz ID of the track.

            **Examples**: :code:`23929516`, :code:`"344521217"`.

        format_id : int or str; keyword-only
            Audio format identifier.

            .. container::

               **Valid values**:

               * :code:`5` – Constant 320 kbps bitrate MP3.
               * :code:`6` – CD-quality (16-bit, 44.1 kHz) FLAC.
               * :code:`7` – Up to 24-bit, 96 kHz FLAC.
               * :code:`27` – Up to 24-bit, 192 kHz FLAC.

        started_at : int or datetime.datetime; keyword-only
            Unix time at which the streaming started.

        duration : int; keyword-only; default: :code:`0`
            Duration of the streaming event, in seconds.

        online : bool; keyword-only
            Whether the streaming was performed online.

        local : bool; keyword-only
            Whether the streaming was played from a local source
            (:code:`True`) or from Qobuz servers (:code:`False`).

        user_id : int or str; keyword-only; optional
            Qobuz ID of the user who streamed the track. If not
            specified, the current user's Qobuz ID is used.

        credential_id : int or str; keyword-only; optional
           Qobuz ID of the credentials used for the streaming event.

        device_id : int or str; keyword-only; optional
           Qobuz ID of the streaming device.

        intent : str; keyword-only; optional
            Playback mode or intended use of the track.

            **Valid values**:

            .. container::

               * :code:`"download"` – Offline download.
               * :code:`"import"` – Library import.
               * :code:`"stream"` – Streaming playback.

            **API default**: :code:`"stream"`.

        purchased : bool; keyword-only; optional
            Whether the streamed track was purchased.

        preview : bool; keyword-only; optional
            Whether the streamed track is a 30-second preview instead of
            the full track.

        Returns
        -------
        response : dict[str, str]
            API JSON response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        self._client._require_authentication("tracks.report_streaming_end")
        return self._report_streaming_event(
            track_id,
            format_id=format_id,
            started_at=started_at,
            duration=duration,
            online=online,
            local=local,
            user_id=user_id,
            credential_id=credential_id,
            device_id=device_id,
            intent=intent,
            purchased=purchased,
            preview=preview,
        )

    def save_tracks(
        self, track_ids: int | str | list[int | str], /
    ) -> dict[str, str]:
        """
        Save one or more tracks to the current user's favorites.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        track_ids : int, str, or list[int | str]; positional-only
            Qobuz IDs of the tracks.

            **Examples**: :code:`23929516`, :code:`"344521217"`,
            :code:`"23929516,344521217"`,
            :code:`[23929516, "344521217"]`.

        Returns
        -------
        response : dict[str, str]
            API JSON response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        return self._client.favorites.save(track_ids=track_ids)

    def remove_saved_tracks(
        self, track_ids: int | str | list[int | str], /
    ) -> dict[str, str]:
        """
        Remove one or more tracks from the current user's favorites.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        track_ids : int, str, or list[int | str]; positional-only
            Qobuz IDs of the tracks.

            **Examples**: :code:`23929516`, :code:`"344521217"`,
            :code:`"23929516,344521217"`,
            :code:`[23929516, "344521217"]`.

        Returns
        -------
        response : dict[str, str]
            API JSON response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        return self._client.favorites.remove_saved(track_ids=track_ids)

    def get_my_saved_tracks(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for the tracks in the current
        user's favorites.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        saved_items : dict[str, Any]
            Page of Qobuz content metadata for tracks in the user's
            favorites.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "tracks": {
                      "items": [
                        {
                          "album": {
                            "artist": {
                              "albums_count": <int>,
                              "id": <int>,
                              "image": None,
                              "name": <str>,
                              "picture": None,
                              "slug": <str>
                            },
                            "displayable": <bool>,
                            "downloadable": <bool>,
                            "duration": <int>,
                            "genre": {
                              "id": <int>,
                              "name": <str>,
                              "path": <list[int]>,
                              "slug": <str>
                            },
                            "hires": <bool>,
                            "hires_streamable": <bool>,
                            "id": <str>,
                            "image": {
                              "large": <str>,
                              "small": <str>,
                              "thumbnail": <str>
                            },
                            "label": {
                              "albums_count": <int>,
                              "id": <int>,
                              "name": <str>,
                              "slug": <str>,
                              "supplier_id": <int>
                            },
                            "maximum_bit_depth": <int>,
                            "maximum_channel_count": <int>,
                            "maximum_sampling_rate": <float>,
                            "media_count": <int>,
                            "parental_warning": <bool>,
                            "previewable": <bool>,
                            "purchasable": <bool>,
                            "purchasable_at": null,
                            "qobuz_id": <int>,
                            "release_date_download": <str>,
                            "release_date_original": <str>,
                            "release_date_purchase": <str>,
                            "release_date_stream": <str>,
                            "released_at": <int>,
                            "sampleable": <bool>,
                            "streamable": <bool>,
                            "streamable_at": <int>,
                            "title": <str>,
                            "tracks_count": <int>,
                            "upc": <str>,
                            "version": None
                          },
                          "audio_info": {
                            "replaygain_track_gain": <float>,
                            "replaygain_track_peak": <float>,
                          },
                          "composer": {
                            "id": <int>,
                            "name": <str>
                          },
                          "copyright": <str>,
                          "displayable": <bool>,
                          "downloadable": <bool>,
                          "duration": <int>,
                          "favorited_at": <int>,
                          "hires": <bool>,
                          "hires_streamable": <bool>,
                          "id": <int>,
                          "isrc": <str>,
                          "maximum_bit_depth": <int>,
                          "maximum_channel_count": <int>,
                          "maximum_sampling_rate": <float>,
                          "media_number": <int>,
                          "parental_warning": <bool>,
                          "performer": {
                            "id": <int>,
                            "name": <str>
                          },
                          "performers": <str>,
                          "previewable": <bool>,
                          "purchasable": <bool>,
                          "purchasable_at": <int>,
                          "release_date_download": <str>,
                          "release_date_original": <str>,
                          "release_date_purchase": <str>,
                          "release_date_stream": <str>,
                          "sampleable": <bool>,
                          "streamable": <bool>,
                          "streamable_at": <int>,
                          "title": <str>,
                          "track_number": <int>,
                          "version": <str>,
                          "work": None
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "user": {
                      "id": <int>,
                      "login": <str>
                    }
                  }
        """
        return self._client.favorites.get_my_saved(
            "tracks", limit=limit, offset=offset
        )

    def is_track_saved(self, track_id: int | str, /) -> dict[str, bool]:
        """
        Check whether a track is in the current user's favorites.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`23929516`, :code:`"344521217"`.

        Returns
        -------
        saved : dict[str, bool]
            Whether the current user has the specified track in their
            favorites.

            **Sample response**: :code:`{"status": <bool>}`.
        """
        return self._client.favorites.is_saved("track", track_id)

    def toggle_track_saved(self, track_id: int | str, /) -> dict[str, bool]:
        """
        Toggle the saved status of a track.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`23929516`, :code:`"344521217"`.

        Returns
        -------
        saved : dict[str, bool]
            Whether the current user has the specified track in their
            favorites.

            **Sample response**: :code:`{"status": <bool>}`.
        """
        return self._client.favorites.toggle_saved("track", track_id)

    @_copy_docstring(PrivateSearchEndpoints.search_tracks)
    def search_tracks(
        self,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.search.search_tracks(
            query, limit=limit, offset=offset
        )

    @_copy_docstring(PrivateUsersAPI.get_track_recommendations)
    def get_track_recommendations(
        self,
        seed_track_ids: int | str | list[int | str],
        /,
        exclude_track_ids: int | str | list[int | str] | None = None,
        *,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_track_recommendations(
            seed_track_ids, exclude_track_ids=exclude_track_ids, limit=limit
        )

    def _report_streaming_event(
        self,
        track_id: int | str,
        /,
        *,
        format_id: int | str,
        started_at: int | datetime,
        online: bool,
        local: bool,
        user_id: int | str | None = None,
        credential_id: int | str | None = None,
        device_id: int | str | None = None,
        intent: str | None = None,
        duration: int = 0,
        purchased: bool | None = None,
        preview: bool | None = None,
    ) -> dict[str, str]:
        """
        Report a streaming event.

        Parameters
        ----------
        track_id : int or str; positional-only
            Qobuz ID of the track.

            **Examples**: :code:`23929516`, :code:`"344521217"`.

        format_id : int or str; keyword-only
            Audio format identifier.

            .. container::

               **Valid values**:

               * :code:`5` – Constant 320 kbps bitrate MP3.
               * :code:`6` – CD-quality (16-bit, 44.1 kHz) FLAC.
               * :code:`7` – Up to 24-bit, 96 kHz FLAC.
               * :code:`27` – Up to 24-bit, 192 kHz FLAC.

        started_at : int or datetime.datetime; keyword-only
            Unix time at which the streaming started.

        online : bool; keyword-only
            Whether the streaming was performed online.

        local : bool; keyword-only
            Whether the streaming was played from a local source
            (:code:`True`) or from Qobuz servers (:code:`False`).

        user_id : int or str; keyword-only; optional
            Qobuz ID of the user who streamed the track. If not
            specified, the current user's Qobuz ID is used.

        credential_id : int or str; keyword-only; optional
           Qobuz ID of the credentials used for the streaming event.

        device_id : int or str; keyword-only; optional
           Qobuz ID of the streaming device.

        intent : str; keyword-only; optional
            Playback mode or intended use of the track.

            **Valid values**:

            .. container::

               * :code:`"download"` – Offline download.
               * :code:`"import"` – Library import.
               * :code:`"stream"` – Streaming playback.

            **API default**: :code:`"stream"`.

        duration : int; keyword-only; default: :code:`0`
            Duration of the streaming event, in seconds.

        purchased : bool; keyword-only; optional
            Whether the streamed track was purchased.

        preview : bool; keyword-only; optional
            Whether the streamed track is a 30-second preview instead of
            the full track.

        Returns
        -------
        response : dict[str, str]
            API JSON response.
        """
        self._validate_qobuz_ids(track_id, _recursive=False)
        self._validate_qobuz_ids(format_id, _recursive=False)
        if isinstance(started_at, datetime):
            started_at = int(started_at.timestamp())
        self._client._validate_number(
            "started_at", started_at, int, 0, time.time()
        )
        self._client._validate_type("online", online, bool)
        self._client._validate_type("local", local, bool)
        if user_id is None:
            user_id = self._client._resolve_user_identifier()
        else:
            self._validate_qobuz_ids(user_id, _recursive=False)
        event = {
            "user_id": int(user_id),
            "track_id": int(track_id),
            "format_id": int(format_id),
            "date": started_at,
            "duration": duration,
            "online": online,
            "local": local,
        }
        if credential_id is not None:
            self._validate_qobuz_ids(credential_id, _recursive=False)
            event["credential_id"] = credential_id
        if device_id is not None:
            self._validate_qobuz_ids(device_id, _recursive=False)
            event["device_id"] = device_id
        if intent is not None:
            self._client._validate_type("intent", intent, str)
            intent = intent.lower()
            if intent not in self._INTENTS:
                intents_str = "', '".join(self._INTENTS)
                raise ValueError(
                    f"Invalid intent {intent!r}. "
                    f"Valid values: '{intents_str}'."
                )
            event["intent"] = intent
        if purchased is not None:
            self._client._validate_type("purchased", purchased, bool)
            event["purchased"] = purchased
        if preview is not None:
            self._client._validate_type("preview", preview, bool)
            event["sample"] = preview
        return self._client._request(
            "POST",
            f"track/reportStreaming{'Start' if duration == 0 else 'End'}",
            json={"events": [event]},
            signed=True,
            sig_params=event,
        ).json()
