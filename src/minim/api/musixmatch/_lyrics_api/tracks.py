from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import MusixmatchLyricsAPI


class TracksAPI(ResourceAPI):
    """
    Tracks API endpoints for the Musixmatch Lyrics API.

    .. important::

       This class is managed by
       :class:`minim.api.musixmatch.MusixmatchLyricsAPI` and should not
       be instantiated directly.
    """

    _client: "MusixmatchLyricsAPI"

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
            Dictionary of additional query parameters to include in the
            request. If not provided, a new dictionary will be created.

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
           :class: authorization-scope

           .. tab:: Required

              Musixmatch Basic plan
                 Access music metadata and static lyrics. `Learn more.
                 <https://about.musixmatch.com/api-pricing>`__

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
               :class: dropdown

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
           :class: authorization-scope

           .. tab:: Required

              Musixmatch Basic plan
                 Access music metadata and static lyrics. `Learn more.
                 <https://about.musixmatch.com/api-pricing>`__

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
               :class: dropdown

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

    def get_track_lyrics_moods(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        """ """
        return self._get_track_resource(
            "track.lyrics.mood.get",
            track_id=track_id,
            common_track_id=common_track_id,
            isrc=isrc,
        )

    def get_track_subtitles(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
        subtitle_format: str | None = None,
        subtitle_length: int | str | None = None,
        subtitle_length_max_deviation: int | str | None = None,
    ) -> dict[str, Any]:
        """ """
        params = {}
        if subtitle_format is not None:
            self._validate_type("subtitle_format", subtitle_format, str)
            subtitle_format = subtitle_format.strip().lower()
            if subtitle_format not in (
                SUBTITLE_FORMATS := {"lrc", "dfxp", "mxm"}
            ):
                subtitle_formats_str = "', '".join(sorted(SUBTITLE_FORMATS))
                raise ValueError(
                    f"Invalid subtitle format {subtitle_format!r}. "
                    f"Valid values: '{subtitle_formats_str}'."
                )
            params["subtitle_format"] = subtitle_format
        if subtitle_length is not None:
            self._validate_numeric("subtitle_length", subtitle_length, int, 0)
            params["f_subtitle_length"] = subtitle_length
        if subtitle_length_max_deviation is not None:
            self._validate_numeric(
                "subtitle_length_max_deviation",
                subtitle_length_max_deviation,
                int,
                0,
            )
            params["f_subtitle_length_max_deviation"] = (
                subtitle_length_max_deviation
            )
        return self._get_track_resource(
            "track.subtitles.get",
            track_id=track_id,
            common_track_id=common_track_id,
            isrc=isrc,
            params=params,
        )

    def get_track_rich_sync(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
        rich_sync_length: int | None = None,
        rich_sync_length_max_deviation: int | None = None,
    ) -> dict[str, Any]:
        """ """
        params = {}
        if rich_sync_length is not None:
            self._validate_numeric(
                "rich_sync_length", rich_sync_length, int, 0
            )
            params["f_richsync_length"] = rich_sync_length
        if rich_sync_length_max_deviation is not None:
            self._validate_numeric(
                "rich_sync_length_max_deviation",
                rich_sync_length_max_deviation,
                int,
                0,
            )
            params["f_richsync_length_max_deviation"] = (
                rich_sync_length_max_deviation
            )
        return self._get_track_resource(
            "track.richsync.get",
            track_id=track_id,
            common_track_id=common_track_id,
            isrc=isrc,
            params=params,
        )

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
        release_date_before: str | None = None,
        release_date_after: str | None = None,
        artist_rating_sort_order: str | None = None,
        track_rating_sort_order: str | None = None,
        page: int | str | None = None,
        limit: int | str | None = None,
    ) -> dict[str, Any]:
        """ """

    def get_track_lyrics_snippet(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        """ """
        return self._get_track_resource(
            "track.snippet.get",
            track_id=track_id,
            common_track_id=common_track_id,
            isrc=isrc,
        )

    def get_track_lyrics_translation(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
        language: str | None = None,
        min_translation_ratio: float | str | None = None,
    ) -> dict[str, Any]:
        """ """
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

    def get_track_subtitles_translation(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
        language: str | None = None,
        min_translation_ratio: float | None = None,
        subtitle_length: int | None = None,
        subtitle_length_max_deviation: int | None = None,
    ) -> dict[str, Any]:
        """ """
        params = {}
        if language is not None:
            self._validate_language_code(language)
            params["selected_language"] = language
        if min_translation_ratio is not None:
            self._validate_numeric(
                "min_translation_ratio", min_translation_ratio, float, 0.0, 1.0
            )
            params["min_completed"] = min_translation_ratio
        if subtitle_length is not None:
            self._validate_numeric("subtitle_length", subtitle_length, int, 0)
            params["f_subtitle_length"] = subtitle_length
        if subtitle_length_max_deviation is not None:
            self._validate_numeric(
                "subtitle_length_max_deviation",
                subtitle_length_max_deviation,
                int,
                0,
            )
            params["f_subtitle_length_max_deviation"] = (
                subtitle_length_max_deviation
            )
        return self._get_track_resource(
            "track.lyrics.translation.get",
            track_id=track_id,
            common_track_id=common_track_id,
            isrc=isrc,
            params=params,
        )
