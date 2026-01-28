from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import MusixmatchResourceAPI
from .charts import ChartsAPI
from .matcher import MatcherAPI


class TracksAPI(MusixmatchResourceAPI):
    """
    Tracks API endpoints for the Musixmatch Lyrics API.

    .. important::

       This class is managed by
       :class:`minim.api.musixmatch.MusixmatchLyricsAPIClient` and
       should not be instantiated directly.
    """

    def _get_track_resource(
        self,
        endpoint: str,
        /,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get Musixmatch catalog information for a track resource.

        Parameters
        ----------
        endpoint : str; positional-only
            API endpoint for the track resource.

        track_id : int or str; keyword-only; optional
            Musixmatch ID of the track.

        common_track_id : int or str; keyword-only; optional
            Musixmatch common ID of the track.

        isrc : int or str; keyword-only; optional
            ISRC of the track.

        params : dict[str, Any]; keyword-only; optional
            Query parameters to include in the request. If not provided,
            an empty dictionary will be created.

            .. note::

               This `dict` is mutated in-place.

        Returns
        -------
        resource : dict[str, Any]
            Musixmatch content metadata for the track resource.
        """
        _params = {}
        if track_id is not None:
            self._validate_numeric("track_id", track_id, int)
            _params["track_id"] = track_id
        if common_track_id is not None:
            self._validate_numeric("common_track_id", common_track_id, int)
            _params["commontrack_id"] = common_track_id
        if isrc is not None:
            self._validate_isrc(isrc)
            _params["track_isrc"] = isrc
        if not _params:
            raise ValueError(
                "At least one of `track_id'`, `common_track_id`, or `isrc` "
                "must be provided."
            )
        return self._client._request(
            "GET", endpoint, params=(params or {}) | _params
        ).json()

    @TTLCache.cached_method(ttl="popularity")
    def get_track(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        """
        `Track > track.get <https://docs.musixmatch.com/lyrics-api
        /track/track-get>`_: Get Musixmatch catalog information for a
        track.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Basic plan
                    Access music metadata and static lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        .. important::

           At least one of :code:`track_id`, :code:`common_track_id`, or
           :code:`isrc` must be specified.

        Parameters
        ----------
        track_id : int or str; keyword-only; optional
            Musixmatch ID of the track.

            **Examples**: :code:`84584600`, :code:`"359206419"`.

        common_track_id : int or str; keyword-only; optional
            Musixmatch common ID of the track.

            **Examples**: :code:`5920049`, :code:`"40728258"`.

        isrc : str; keyword-only; optional
            ISRC of the track.

            **Example**: :code:`"USUM70905526"`.

        Returns
        -------
        track : dict[str, Any]
            Musixmatch content metadata for the track.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "track": {
                          "album_coverart_100x100": <str>,
                          "album_coverart_350x350": <str>,
                          "album_coverart_500x500": <str>,
                          "album_coverart_800x800": <str>,
                          "album_id": <int>,
                          "album_name": <str>,
                          "album_vanity_id": <str>,
                          "artist_id": <int>,
                          "artist_mbid": <str>,
                          "artist_name": <str>,
                          "commontrack_7digital_ids": <list[int]>,
                          "commontrack_id": <int>,
                          "commontrack_isrcs": <list[list[str]]>,
                          "commontrack_itunes_ids": <list[int]>,
                          "commontrack_spotify_ids": <list[str]>,
                          "commontrack_vanity_id": <str>,
                          "explicit": <int>,
                          "first_release_date": <str>,
                          "has_lyrics": <int>,
                          "has_lyrics_crowd": <int>,
                          "has_richsync": <int>,
                          "has_subtitles": <int>,
                          "has_track_structure": <int>,
                          "instrumental": <int>,
                          "lyrics_id": <int>,
                          "num_favourite": <int>,
                          "primary_genres": {
                            "music_genre_list": [
                              {
                                "music_genre": {
                                  "music_genre_id": <int>,
                                  "music_genre_name": <str>,
                                  "music_genre_name_extended": <str>,
                                  "music_genre_parent_id": <int>,
                                  "music_genre_vanity": <str>
                                }
                              }
                            ]
                          },
                          "restricted": <int>,
                          "secondary_genres": {
                            "music_genre_list": []
                          },
                          "subtitle_id": <int>,
                          "track_edit_url": <str>,
                          "track_id": <int>,
                          "track_isrc": <str>,
                          "track_length": <int>,
                          "track_mbid": <str>,
                          "track_name": <str>,
                          "track_name_translation_list": [],
                          "track_rating": <int>,
                          "track_share_url": <str>,
                          "track_soundcloud_id": <int>,
                          "track_spotify_id": <str>,
                          "track_xboxmusic_id": <str>,
                          "updated_time": <str>
                        }
                      },
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        return self._get_track_resource(
            "track.get",
            track_id=track_id,
            common_track_id=common_track_id,
            isrc=isrc,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_lyrics(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        """
        `Track > track.lyrics.get <https://docs.musixmatch.com
        /lyrics-api/track/track-lyrics-get>`_: Get Musixmatch catalog
        information for a track's lyrics.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Basic plan
                    Access music metadata and static lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        .. important::

           At least one of :code:`track_id`, :code:`common_track_id`, or
           :code:`isrc` must be specified.

        Parameters
        ----------
        track_id : int or str; keyword-only; optional
            Musixmatch ID of the track.

            **Examples**: :code:`84584600`, :code:`"359206419"`.

        common_track_id : int or str; keyword-only; optional
            Musixmatch common ID of the track.

            **Examples**: :code:`5920049`, :code:`"40728258"`.

        isrc : str; keyword-only; optional
            ISRC of the track.

            **Example**: :code:`"USUM70905526"`.

        Returns
        -------
        lyrics : dict[str, Any]
            Musixmatch content metadata for the track's lyrics.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "lyrics": {
                          "action_requested": <str>,
                          "backlink_url": <str>,
                          "can_edit": <int>,
                          "check_validation_overridable": <int>,
                          "explicit": <int>,
                          "html_tracking_url": <str>,
                          "instrumental": <int>,
                          "locked": <int>,
                          "lyrics_body": <str>,
                          "lyrics_copyright": <str>,
                          "lyrics_id": <int>,
                          "lyrics_language": <str>,
                          "lyrics_language_description": <str>,
                          "pixel_tracking_url": <str>,
                          "published_status": <int>,
                          "publisher_list": [],
                          "restricted": <int>,
                          "script_tracking_url": <str>,
                          "updated_time": <str>,
                          "verified": <int>,
                          "writer_list": []
                        }
                      },
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        return self._get_track_resource(
            "track.lyrics.get",
            track_id=track_id,
            common_track_id=common_track_id,
            isrc=isrc,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_lyrics_moods(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        """
        `Track > track.lyrics.mood.get <https://docs.musixmatch.com
        /lyrics-api/track/track-lyrics-mood-get>`_: Get Musixmatch
        catalog information on the five most prevalent moods associated
        with a track's lyrics.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        .. important::

           At least one of :code:`track_id`, :code:`common_track_id`, or
           :code:`isrc` must be specified.

        Parameters
        ----------
        track_id : int or str; keyword-only; optional
            Musixmatch ID of the track.

            **Examples**: :code:`84584600`, :code:`"359206419"`.

        common_track_id : int or str; keyword-only; optional
            Musixmatch common ID of the track.

            **Examples**: :code:`5920049`, :code:`"40728258"`.

        isrc : str; keyword-only; optional
            ISRC of the track.

            **Example**: :code:`"USUM70905526"`.

        Returns
        -------
        moods : dict[str, Any]
            Musixmatch content metadata for the moods associated with
            the track's lyrics.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "mood_list": [
                          {
                            "label": <str>,
                            "value": <float>
                          }
                        ]
                      },
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._client._require_api_key("tracks.get_track_lyrics_moods")
        return self._get_track_resource(
            "track.lyrics.mood.get",
            track_id=track_id,
            common_track_id=common_track_id,
            isrc=isrc,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_subtitles(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
        format: str | None = None,
        duration: int | str | None = None,
        max_duration_deviation: int | str | None = None,
    ) -> dict[str, Any]:
        """
        `Track > track.subtitle.get <https://docs.musixmatch.com
        /lyrics-api/track/track-subtitle-get>`_: Get Musixmatch catalog
        information for a track's subtitles.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Scale plan
                    Access time-synced lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        .. important::

           At least one of :code:`track_id`, :code:`common_track_id`, or
           :code:`isrc` must be specified.

        Parameters
        ----------
        track_id : int or str; keyword-only; optional
            Musixmatch ID of the track.

            **Examples**: :code:`84584600`, :code:`"359206419"`.

        common_track_id : int or str; keyword-only; optional
            Musixmatch common ID of the track.

            **Examples**: :code:`5920049`, :code:`"40728258"`.

        isrc : str; keyword-only; optional
            ISRC of the track.

            **Example**: :code:`"USUM70905526"`.

        format : str; keyword-only; optional
            Subtitle format.

            **Valid values**: :code:`"lrc"`, :code:`"dfxp"`,
            :code:`"mxm"`.

            **API default**: :code:`"lrc"`.

        duration : int or str; keyword-only; optional
            Target subtitle duration, in seconds.

        max_duration_deviation : int or str; keyword-only; optional
            Maximum deviation allowed from the requested duration. Only
            applicable when `duration` is specified.

        Returns
        -------
        subtitles : dict[str, Any]
            Musixmatch content metadata for the track's subtitles.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "subtitle": {
                          "lyrics_copyright": <str>,
                          "pixel_tracking_url": <str>,
                          "script_tracking_url": <str>,
                          "subtitle_body": <str>,
                          "subtitle_id": <int>,
                          "subtitle_language": <str>,
                          "subtitle_language_description": <str>,
                          "subtitle_length": <int>,
                          "updated_time": <str>
                        }
                      },
                      "header": {
                        "execute_time": <float>,
                        "instrumental": <int>,
                        "status_code": <int>,
                      }
                    }
                  }
        """
        self._client._require_api_key("tracks.get_track_subtitles")
        params = {}
        if format is not None:
            format = self._prepare_string("format", format).lower()
            if format not in (SUBTITLE_FORMATS := {"lrc", "dfxp", "mxm"}):
                subtitle_formats_str = "', '".join(sorted(SUBTITLE_FORMATS))
                raise ValueError(
                    f"Invalid subtitle format {format!r}. "
                    f"Valid values: '{subtitle_formats_str}'."
                )
            params["subtitle_format"] = format
        if duration is not None:
            self._validate_numeric("duration", duration, int, 0)
            params["f_subtitle_length"] = duration
            if max_duration_deviation is not None:
                self._validate_numeric(
                    "max_duration_deviation", max_duration_deviation, int, 0
                )
                params["f_subtitle_length_max_deviation"] = (
                    max_duration_deviation
                )
        return self._get_track_resource(
            "track.subtitles.get",
            track_id=track_id,
            common_track_id=common_track_id,
            isrc=isrc,
            params=params,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_rich_sync_lyrics(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
        duration: int | None = None,
        max_duration_deviation: int | None = None,
    ) -> dict[str, Any]:
        """
        `Track > track.richsync.get <https://docs.musixmatch.com
        /lyrics-api/track/track-richsync-get>`_: Get Musixmatch catalog
        information for a track's rich sync lyrics.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        .. important::

           At least one of :code:`track_id`, :code:`common_track_id`, or
           :code:`isrc` must be specified.

        Parameters
        ----------
        track_id : int or str; keyword-only; optional
            Musixmatch ID of the track.

            **Examples**: :code:`84584600`, :code:`"359206419"`.

        common_track_id : int or str; keyword-only; optional
            Musixmatch common ID of the track.

            **Examples**: :code:`5920049`, :code:`"40728258"`.

        isrc : str; keyword-only; optional
            ISRC of the track.

            **Example**: :code:`"USUM70905526"`.

        duration : int or str; keyword-only; optional
            Target rich sync lyrics duration, in seconds.

        max_duration_deviation : int or str; keyword-only; optional
            Maximum deviation allowed from the requested duration. Only
            applicable when `duration` is specified.

        Returns
        -------
        lyrics : dict[str, Any]
            Musixmatch content metadata for the track's rich sync
            lyrics.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "richsync": {
                          "html_tracking_url": <str>,
                          "lyrics_copyright": <str>,
                          "pixel_tracking_url": <str>,
                          "publisher_list": [],
                          "restricted": <int>,
                          "richssync_language": <str>,
                          "richsync_avg_count": <int>,
                          "richsync_body": <str>,
                          "richsync_id": <int>,
                          "richsync_language_description": <str>,
                          "richsync_length": <int>,
                          "script_tracking_url": <str>,
                          "updated_time": <str>,
                          "writer_list": []
                        }
                      },
                      "header": {
                        "available": <int>,
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._client._require_api_key("tracks.get_track_rich_sync_lyrics")
        params = {}
        if duration is not None:
            self._validate_numeric("rich_durationync_length", duration, int, 0)
            params["f_richsync_length"] = duration
        if max_duration_deviation is not None:
            self._validate_numeric(
                "max_duration_deviation", max_duration_deviation, int, 0
            )
            params["f_richsync_length_max_deviation"] = max_duration_deviation
        return self._get_track_resource(
            "track.richsync.get",
            track_id=track_id,
            common_track_id=common_track_id,
            isrc=isrc,
            params=params,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_lyrics_snippet(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        """
        `Track > track.snippet.get <https://docs.musixmatch.com
        /lyrics-api/track/track-snippet-get>`_: Get Musixmatch catalog
        information for a snippet of a track's lyrics.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Basic plan
                    Access music metadata and static lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        .. important::

           At least one of :code:`track_id`, :code:`common_track_id`, or
           :code:`isrc` must be specified.

        Parameters
        ----------
        track_id : int or str; keyword-only; optional
            Musixmatch ID of the track.

            **Examples**: :code:`84584600`, :code:`"359206419"`.

        common_track_id : int or str; keyword-only; optional
            Musixmatch common ID of the track.

            **Examples**: :code:`5920049`, :code:`"40728258"`.

        isrc : str; keyword-only; optional
            ISRC of the track.

            **Example**: :code:`"USUM70905526"`.

        Returns
        -------
        snippet : dict[str, Any]
            Musixmatch content metadata for the snippet of the track's
            lyrics.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "snippet": {
                          "html_tracking_url": <str>,
                          "instrumental": <int>,
                          "pixel_tracking_url": <str>,
                          "region_restriction": {
                            "allowed": <list[str]>,
                            "blocked": []
                          },
                          "restricted": <int>,
                          "script_tracking_url": <str>,
                          "snippet_body": <str>,
                          "snippet_id": <int>,
                          "snippet_language": <str>,
                          "updated_time": <str>
                        }
                      },
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        return self._get_track_resource(
            "track.snippet.get",
            track_id=track_id,
            common_track_id=common_track_id,
            isrc=isrc,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_lyrics_translation(
        self,
        language: str,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
        min_translation_ratio: float | str | None = None,
    ) -> dict[str, Any]:
        """
        `Track > track.lyrics.translation.get
        <https://docs.musixmatch.com/lyrics-api/track
        /track-lyrics-translation-get>`_: Get Musixmatch catalog
        information for a translation of a track's lyrics.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        .. important::

           At least one of :code:`track_id`, :code:`common_track_id`, or
           :code:`isrc` must be specified.

        Parameters
        ----------
        language : str
            ISO 639-1 language code for the desired translation
            language.

            **Example**: :code:`"it"`.

        track_id : int or str; keyword-only; optional
            Musixmatch ID of the track.

            **Examples**: :code:`84584600`, :code:`"359206419"`.

        common_track_id : int or str; keyword-only; optional
            Musixmatch common ID of the track.

            **Examples**: :code:`5920049`, :code:`"40728258"`.

        isrc : str; keyword-only; optional
            ISRC of the track.

            **Example**: :code:`"USUM70905526"`.

        min_translation_ratio : float; keyword-only; optional
            Minimum translation completion ratio.

            **Valid range**: :code:`0.0` to :code:`1.0`.

        Returns
        -------
        translation : dict[str, Any]
            Musixmatch content metadata for the translation of the
            track's lyrics.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "lyrics": {
                          "explicit": <int>,
                          "lyrics_body": <str>,
                          "lyrics_copyright": <str>,
                          "lyrics_id": <int>,
                          "lyrics_language": <str>,
                          "lyrics_translated": {
                            "html_tracking_url": <str>,
                            "lyrics_body": <str>,
                            "pixel_tracking_url": <str>,
                            "restricted": <int>,
                            "script_tracking_url": <str>,
                            "selected_language": <str>
                          },
                          "pixel_tracking_url": <str>,
                          "region_restriction": {
                            "allowed": <list[str]>,
                            "blocked": []
                          },
                          "script_tracking_url": <str>,
                          "updated_time": <str>
                        }
                      },
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._client._require_api_key("tracks.get_track_lyrics_translation")
        params = {}
        if language is not None:
            self._validate_language_code(language)
            params["selected_language"] = language
        if min_translation_ratio is not None:
            self._validate_numeric(
                "min_translation_ratio", min_translation_ratio, float, 0.0, 1.0
            )
            params["min_completed"] = min_translation_ratio
        return self._get_track_resource(
            "track.lyrics.translation.get",
            track_id=track_id,
            common_track_id=common_track_id,
            isrc=isrc,
            params=params,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_subtitles_translation(
        self,
        language: str,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
        min_translation_ratio: float | None = None,
        duration: int | None = None,
        max_duration_deviation: int | None = None,
    ) -> dict[str, Any]:
        """
        `Track > track.subtitle.translation.get
        <https://docs.musixmatch.com/lyrics-api/track
        /track-subtitle-translation-get>`_: Get Musixmatch catalog
        information for a translation of a track's subtitles.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        .. important::

           At least one of :code:`track_id`, :code:`common_track_id`, or
           :code:`isrc` must be specified.

        Parameters
        ----------
        language : str
            ISO 639-1 language code for the desired translation
            language.

            **Example**: :code:`"it"`.

        track_id : int or str; keyword-only; optional
            Musixmatch ID of the track.

            **Examples**: :code:`84584600`, :code:`"359206419"`.

        common_track_id : int or str; keyword-only; optional
            Musixmatch common ID of the track.

            **Examples**: :code:`5920049`, :code:`"40728258"`.

        isrc : str; keyword-only; optional
            ISRC of the track.

            **Example**: :code:`"USUM70905526"`.

        min_translation_ratio : float; keyword-only; optional
            Minimum translation completion ratio.

            **Valid range**: :code:`0.0` to :code:`1.0`.

        duration : int or str; keyword-only; optional
            Target subtitle duration, in seconds.

        max_duration_deviation : int or str; keyword-only; optional
            Maximum deviation allowed from the requested duration. Only
            applicable when `duration` is specified.

        Returns
        -------
        translation : dict[str, Any]
            Musixmatch content metadata for the translation of the
            track's subtitles.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "subtitle": {
                          "lyrics_copyright": <str>,
                          "pixel_tracking_url": <str>,
                          "region_restriction": {
                            "allowed": <list[str]>,
                            "blocked": []
                          },
                          "script_tracking_url": <str>,
                          "subtitle_body": <str>,
                          "subtitle_id": <int>,
                          "subtitle_language": <str>,
                          "subtitle_language_description": <str>,
                          "subtitle_length": <int>,
                          "subtitle_translated": {
                            "html_tracking_url": <str>,
                            "pixel_tracking_url": <str>,
                            "restricted": <int>,
                            "script_tracking_url": <str>,
                            "selected_language": <str>,
                            "subtitle_body": <str>,
                          },
                          "updated_time": <str>
                        }
                      },
                      "header": {
                        "execute_time": <float>,
                        "instrumental": <int>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._client._require_api_key("tracks.get_track_subtitles_translation")
        params = {}
        if language is not None:
            self._validate_language_code(language)
            params["selected_language"] = language
        if min_translation_ratio is not None:
            self._validate_numeric(
                "min_translation_ratio", min_translation_ratio, float, 0.0, 1.0
            )
            params["min_completed"] = min_translation_ratio
        if duration is not None:
            self._validate_numeric("duration", duration, int, 0)
            params["f_subtitle_length"] = duration
            if max_duration_deviation is not None:
                self._validate_numeric(
                    "max_duration_deviation", max_duration_deviation, int, 0
                )
                params["f_subtitle_length_max_deviation"] = (
                    max_duration_deviation
                )
        return self._get_track_resource(
            "track.lyrics.translation.get",
            track_id=track_id,
            common_track_id=common_track_id,
            isrc=isrc,
            params=params,
        )

    @TTLCache.cached_method(ttl="search")
    def search_tracks(
        self,
        query: str | None = None,
        *,
        artist_query: str | None = None,
        lyrics_query: str | None = None,
        track_query: str | None = None,
        track_artist_query: str | None = None,
        writer_query: str | None = None,
        artist_id: int | str | None = None,
        genre_id: int | str | None = None,
        language: str | None = None,
        has_lyrics: bool | None = None,
        release_date_after: str | None = None,
        release_date_before: str | None = None,
        artist_popularity_sort_order: str | None = None,
        track_popularity_sort_order: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        `Track > track.search <https://docs.musixmatch.com/lyrics-api
        /track/track-search>`_: Search for tracks in the Musixmatch
        catalog.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Basic plan
                    Access music metadata and static lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        Parameters
        ----------
        query : str; optional
            Search query matching any word in the artist name, track
            name, or lyrics.

        artist_query : str; keyword-only; optional
            Search query matching any word in the artist name.

        lyrics_query : str; keyword-only; optional
            Search query matching any word in the track's lyrics.

        track_query : str; keyword-only; optional
            Search query matching any word in the track name.

        track_artist_query : str; keyword-only; optional
            Search query matching any word in the track artist name.

        writer_query : str; keyword-only; optional
            Search query matching any word in the track writer name.

        artist_id : int or str; keyword-only; optional
            Musixmatch ID of the artist to filter results by.

            **Examples**: :code:`259675`, :code:`"24403590"`.

        genre_id : int or str; keyword-only; optional
            Musixmatch genre ID to filter results by.

        language : str; keyword-only; optional
            ISO 639-1 language code to filter results by lyrics
            availability.

            **Example**: :code:`"it"`.

        has_lyrics : bool; keyword-only; optional
            Whether to only include tracks that have lyrics.

            **API default**: :code:`False`.

        release_date_after : str; keyword-only; optional
            Minimum release date to filter results by, in
            :code:`YYYYMMDD` format.

        release_date_before : str; keyword-only; optional
            Maximum release date to filter results by, in
            :code:`YYYYMMDD` format.

        artist_popularity_sort_order : str; keyword-only; optional
            Sort order for artist popularity.

            **Valid values**: :code:`"asc"`, :code:`"desc"`.

        track_popularity_sort_order : str; keyword-only; optional
            Sort order for track popularity.

            **Valid values**: :code:`"asc"`, :code:`"desc"`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of
            tracks.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of Musixmatch content metadata for the matching tracks.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "track_list": [
                          {
                            "track": {
                              "album_id": <int>,
                              "album_name": <str>,
                              "artist_id": <int>,
                              "artist_name": <str>,
                              "commontrack_id": <int>,
                              "commontrack_isrcs": <list[list[str]]>,
                              "explicit": <int>,
                              "has_lyrics": <int>,
                              "has_richsync": <int>,
                              "has_subtitles": <int>,
                              "instrumental": <int>,
                              "num_favourite": <int>,
                              "primary_genres": {
                                "music_genre_list": [
                                  {
                                    "music_genre": {
                                      "music_genre_id": <int>,
                                      "music_genre_name": <str>,
                                      "music_genre_name_extended": <str>,
                                      "music_genre_parent_id": <int>,
                                      "music_genre_vanity": <str>
                                    }
                                  }
                                ]
                              },
                              "restricted": <int>,
                              "track_edit_url": <str>,
                              "track_id": <int>,
                              "track_isrc": <str>,
                              "track_length": <int>,
                              "track_lyrics_translation_status": [
                                {
                                  "from": <str>,
                                  "perc": <int>,
                                  "to": <str>
                                }
                              ],
                              "track_name": <str>,
                              "track_rating": <int>,
                              "track_share_url": <str>,
                              "track_spotify_id": <str>,
                              "updated_time": <str>
                            }
                          }
                        ]
                      },
                      "header": {
                        "available": <int>,
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        params = {}
        if query is not None:
            params["q"] = self._prepare_string("query", query)
        if artist_query is not None:
            params["q_artist"] = self._prepare_string(
                "artist_query", artist_query
            )
        if lyrics_query is not None:
            params["q_lyrics"] = self._prepare_string(
                "lyrics_query", lyrics_query
            )
        if track_query is not None:
            params["q_track"] = self._prepare_string(
                "track_query", track_query
            )
        if track_artist_query is not None:
            params["q_track_artist"] = self._prepare_string(
                "track_artist_query", track_artist_query
            )
        if writer_query is not None:
            params["q_writer"] = self._prepare_string(
                "writer_query", writer_query
            )
        if artist_id is not None:
            self._validate_numeric("artist_id", artist_id, int)
            params["f_artist_id"] = artist_id
        if genre_id is not None:
            self._validate_numeric("genre_id", genre_id, int)
            params["f_music_genre_id"] = genre_id
        if language is not None:
            self._validate_language_code(language)
            params["f_lyrics_language"] = language
        if has_lyrics is not None:
            self._validate_type("has_lyrics", has_lyrics, bool)
            params["f_has_lyrics"] = int(has_lyrics)
        if release_date_after is not None:
            params["f_first_release_date_min"] = self._prepare_datetime(
                release_date_after, "%Y%m%d"
            )
        if release_date_before is not None:
            params["f_first_release_date_max"] = self._prepare_datetime(
                release_date_before, "%Y%m%d"
            )
        if artist_popularity_sort_order is not None:
            self._validate_sort_order(
                artist_popularity_sort_order, sort_by="artist popularity"
            )
            params["s_artist_rating"] = artist_popularity_sort_order
        if track_popularity_sort_order is not None:
            self._validate_sort_order(
                track_popularity_sort_order, sort_by="track popularity"
            )
            params["s_track_rating"] = track_popularity_sort_order
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["page_size"] = limit
        if page is not None:
            self._validate_number("page", page, int, 1)
            params["page"] = page
        return self._client._request(
            "GET", "track.search", params=params
        ).json()

    @_copy_docstring(ChartsAPI.get_top_tracks)
    def get_top_tracks(
        self,
        chart_name: str | None = None,
        *,
        country_code: str | None = None,
        has_lyrics: bool | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        return self._client.charts.get_top_tracks(
            chart_name=chart_name,
            country_code=country_code,
            has_lyrics=has_lyrics,
            limit=limit,
            page=page,
        )

    @_copy_docstring(MatcherAPI.match_track_lyrics)
    def match_track_lyrics(
        self,
        *,
        artist: str | None = None,
        track: str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        return self._client.matcher.match_track_lyrics(
            artist=artist, track=track, isrc=isrc
        )

    @_copy_docstring(MatcherAPI.match_track)
    def match_track(
        self,
        *,
        artist: str | None = None,
        track: str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        return self._client.matcher.match_track(
            artist=artist, track=track, isrc=isrc
        )

    @_copy_docstring(MatcherAPI.match_track_subtitles)
    def match_track_subtitles(
        self,
        *,
        artist: str | None = None,
        track: str | None = None,
        isrc: str | None = None,
        duration: int | str | None = None,
        max_duration_deviation: int | str | None = None,
    ) -> dict[str, Any]:
        return self._client.matcher.match_track_subtitles(
            artist=artist,
            track=track,
            isrc=isrc,
            duration=duration,
            max_duration_deviation=max_duration_deviation,
        )
