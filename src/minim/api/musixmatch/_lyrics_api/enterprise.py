from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import MusixmatchResourceAPI
from .tracks import TracksAPI


class EnterpriseAPI(MusixmatchResourceAPI):
    """
    Enterprise API endpoints for the Musixmatch Lyrics API.

    .. important::

       This class is managed by
       :class:`minim.api.musixmatch.MusixmatchLyricsAPIClient` and
       should not be instantiated directly.
    """

    def submit_work(self) -> None:
        """ """

    def set_work_validity(self) -> None:
        """ """

    @TTLCache.cached_method(ttl="daily")
    def screen_track_lyrics(
        self,
        text: str,
        /,
        *,
        max_candidates: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        `Enterprise > track.lyrics.fingerprint.post
        <https://docs.musixmatch.com/enterprise-integration
        /api-reference/track-lyrics-fingerprint-post>`_: Get Musixmatch
        catalog information for tracks whose lyrics match a text string,
        ranked by similarity.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        Parameters
        ----------
        text : str; positional-only
            Text to screen for potential lyrical content.

        max_candidates : int; keyword-only; optional
            Maximum number of track candidates.

            **Valid range**: :code:`1` to :code:`20`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to `max_candidates`.

        Returns
        -------
        tracks : dict[str, Any]
            Tracks whose lyrics match the text string.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "track_list": [
                          {
                            "similarity": <float>,
                            "track": {
                              "album_coverart_100x100": <str>,
                              "album_coverart_350x350": <str>,
                              "album_coverart_500x500": <str>,
                              "album_coverart_800x800": <str>,
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
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        params = {}
        if max_candidates is not None:
            self._validate_number("max_candidates", max_candidates, int, 1, 20)
            params["size"] = max_candidates
        if limit is not None:
            self._validate_number(
                "limit", limit, int, 1, params.get("size", 20)
            )
            params["limit"] = limit
        return self._client._request(
            "POST",
            "track.lyrics.fingerprint.post",
            headers={"Content-Type": "application/json"},
            json={"data": {"text": text}},
            params=params,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_catalog_record(self, isrc: str) -> dict[str, Any]:
        """
        `Enterprise > track.dump.get <https://docs.musixmatch.com
        /enterprise-integration/api-reference/track-dump-get>`_: Get
        the Musixmatch catalog record for a track.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        Parameters
        ----------
        isrc : str
            ISRC of the track.

            **Example**: :code:`"USUM70905526"`.

        Returns
        -------
        track : dict[str, Any]
            Musixmatch catalog record for a track.

            .. admonition:: Sample reponse
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": [
                        {
                          "artist": <str>,
                          "commontrack_id": <int>,
                          "instrumental": <bool>,
                          "isrcs": <list[str]>,
                          "language_iso_code_1": <str>,
                          "last_updated": <str>,
                          "lyrics": <str>,
                          "lyrics_id": <int>,
                          "lyrics_tracking_url": <str>,
                          "restrictions": {
                            "allow": <list[str]>,
                            "blocked": <list[str]>
                          },
                          "snippet": <str>,
                          "subtitles": [
                            {
                              "body": <str>,
                              "id": <int>,
                              "length": <int>,
                              "tracking_url": <str>,
                            }
                          ],
                          "title": <str>,
                          "writers": [
                            {
                              "id": <int>,
                              "name": <str>
                            }
                          ]
                        }
                      ],
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._client._require_api_key("enterprise.get_track_catalog_record")
        self._validate_isrc(isrc)
        return self._client._request(
            "GET", "track.dump.get", params={"track_isrc": isrc}
        ).json()

    @TTLCache.cached_method(ttl="daily")
    def get_catalog_feeds(self) -> dict[str, Any]:
        """
        `Enterprise > tracks.dump.get <https://docs.musixmatch.com
        /enterprise-integration/api-reference/tracks-dump-get>`_: Get
        the latest Musixmatch catalog feeds.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        Returns
        -------
        catalog_feeds : dict[str, Any]
            Musixmatch catalog feeds.

            .. admonition:: Sample reponse
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": [
                        {
                          "created": <str>,
                          "download_url": <str>,
                          "full": <bool>,
                          "id": <int>
                        }
                      ],
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._client._require_api_key("enterprise.get_catalog_feeds")
        return self._client._request("GET", "tracks.dump.get").json()

    @TTLCache.cached_method(ttl="static")
    def get_languages(
        self, *, include_romanization: bool | None = None
    ) -> dict[str, Any]:
        """
        `Enterprise > languages.get <https://docs.musixmatch.com
        /enterprise-integration/api-reference/languages-get>`_: Get
        languages supported by Musixmatch.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        Parameters
        ----------
        include_romanization : bool; keyword-only; optional
            Whether to include romanization information for romanized
            languages.

            **API default**: :code:`False`.

        Returns
        -------
        languages : dict[str, Any]
            Languages supported by Musixmatch.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "language_list": [
                          {
                            "language": {
                              "has_romanization": <int>,
                              "iso_code_romanization": <str>,
                              "language_iso_code_1": <str>,
                              "language_iso_code_3": <str>,
                              "language_name": <str>
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
        self._client._require_api_key("enterprise.get_languages")
        params = {}
        if include_romanization is not None:
            self._validate_type(include_romanization, bool)
            if include_romanization:
                params["has_romanization"] = "1"
        return self._client._request(
            "GET", "languages.get", params=params
        ).json()

    @_copy_docstring(TracksAPI.get_track_lyrics_analysis)
    def get_track_lyrics_analysis(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        return self._client.tracks.get_track_lyrics_analysis(
            track_id=track_id, common_track_id=common_track_id, isrc=isrc
        )
