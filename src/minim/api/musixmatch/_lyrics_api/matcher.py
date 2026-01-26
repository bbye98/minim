from typing import Any
import warnings

from ..._shared import TTLCache
from ._shared import MusixmatchResourceAPI


class MatcherAPI(MusixmatchResourceAPI):
    """
    Matcher API endpoints for the Musixmatch Lyrics API.

    .. important::

       This class is managed by
       :class:`minim.api.musixmatch.MusixmatchLyricsAPIClient` and
       should not be instantiated directly.
    """

    def _match_resource(
        self,
        endpoint: str,
        /,
        *,
        artist: str | None = None,
        track: str | None = None,
        isrc: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Match a track by artist and track name or by ISRC, and get
        Musixmatch catalog information for it or one of its
        subresources.

        Parameters
        ----------
        artist : str; keyword-only; optional
            Artist name to match.

        track : str; keyword-only; optional
            Track name to match.

        isrc : str; keyword-only; optional
            ISRC of the track.

            **Example**: :code:`"USUM70905526"`.

        Returns
        -------
        resource : dict[str, Any]
            Musixmatch content metadata for the track or one of its
            subresources.
        """
        if params is None:
            params = {}
        if isrc is None:
            if artist is None or track is None:
                raise ValueError(
                    "Both artist and track search queries must be provided."
                )
            params["q_artist"] = self._prepare_string("artist", artist)
            params["q_track"] = self._prepare_string("track", track)
        else:
            self._validate_isrc(isrc)
            if artist or track:
                warnings.warn(
                    "The track ISRC takes precedence over the artist "
                    "and track search queries, so the latter will be "
                    "omitted from the request."
                )
            params["track_isrc"] = isrc
        return self._client._request("GET", endpoint, params=params).json()

    @TTLCache.cached_method(ttl="static")
    def match_track_lyrics(
        self,
        *,
        artist: str | None = None,
        track: str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        """
        `Matcher > matcher.lyrics.get <https://docs.musixmatch.com
        /lyrics-api/matcher/matcher-lyrics-get>`_: Match a track by
        artist and track name or by ISRC, and get Musixmatch
        catalog information for its lyrics.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Basic plan
                    Access music metadata and static lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        Parameters
        ----------
        artist : str; keyword-only; optional
            Artist name to match.

        track : str; keyword-only; optional
            Track name to match.

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
                          "explicit": <int>,
                          "lyrics_body": <str>,
                          "lyrics_copyright": <str>,
                          "lyrics_id": <int>,
                          "lyrics_language": <str>,
                          "pixel_tracking_url": <str>,
                          "region_restriction": {
                            "allowed": <list[str]>,
                            "blocked": <list[str]>
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
        return self._match_resource(
            "matcher.lyrics.get", artist=artist, track=track, isrc=isrc
        )

    @TTLCache.cached_method(ttl="popularity")
    def match_track(
        self,
        *,
        artist: str | None = None,
        track: str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        """
        `Matcher > matcher.track.get <https://docs.musixmatch.com
        /lyrics-api/matcher/matcher-track-get>`_: Match a track by
        artist and track name or by ISRC, and get Musixmatch
        catalog information for it.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Basic plan
                    Access music metadata and static lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        Parameters
        ----------
        artist : str; keyword-only; optional
            Artist name to match.

        track : str; keyword-only; optional
            Track name to match.

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
                      },
                      "header": {
                        "cached": <int>,
                        "confidence": <int>,
                        "execute_time": <float>,
                        "mode": <str>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        return self._match_resource(
            "matcher.track.get", artist=artist, track=track, isrc=isrc
        )

    @TTLCache.cached_method(ttl="static")
    def match_track_subtitles(
        self,
        *,
        artist: str | None = None,
        track: str | None = None,
        isrc: str | None = None,
        duration: int | str | None = None,
        max_duration_deviation: int | str | None = None,
    ) -> dict[str, Any]:
        """
        `Matcher > matcher.subtitle.get <https://docs.musixmatch.com
        /lyrics-api/matcher/matcher-subtitle-get>`_: Match a track by
        artist and track name or by ISRC, and get Musixmatch
        catalog information for its subtitles.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Scale plan
                    Access time-synced lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        Parameters
        ----------
        artist : str; keyword-only; optional
            Artist name to match.

        track : str; keyword-only; optional
            Track name to match.

        isrc : str; keyword-only; optional
            ISRC of the track.

            **Example**: :code:`"USUM70905526"`.

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
                          "html_tracking_url": <str>,
                          "lyrics_copyright": <str>,
                          "pixel_tracking_url": <str>,
                          "published_status": <int>,
                          "publisher_list": [],
                          "restricted": <int>,
                          "script_tracking_url": <str>,
                          "subtitle_avg_count": <int>,
                          "subtitle_body": <str>,
                          "subtitle_id": <int>,
                          "subtitle_language": <str>,
                          "subtitle_language_description": <str>,
                          "subtitle_length": <int>,
                          "updated_time": <str>,
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
        params = {}
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
        return self._match_resource(
            "matcher.subtitle.get",
            artist=artist,
            track=track,
            isrc=isrc,
            params=params,
        )
