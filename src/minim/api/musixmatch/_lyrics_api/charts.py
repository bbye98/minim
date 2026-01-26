from typing import Any

from ..._shared import TTLCache
from ._shared import MusixmatchResourceAPI


class ChartsAPI(MusixmatchResourceAPI):
    """
    Charts API endpoints for the Musixmatch Lyrics API.

    .. important::

       This class is managed by
       :class:`minim.api.musixmatch.MusixmatchLyricsAPIClient` and
       should not be instantiated directly.
    """

    _CHART_NAMES = {"top", "hot", "mxmweekly", "mxmweekly_new"}

    @TTLCache.cached_method(ttl="popularity")
    def get_top_tracks(
        self,
        chart_name: str | None = None,
        *,
        country_code: str | None = None,
        has_lyrics: bool | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        `Charts > chart.tracks.get <https://docs.musixmatch.com
        /lyrics-api/charts/chart-tracks-get>`_: Get Musixmatch catalog
        information for the top tracks on Musixmatch.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Basic plan
                    Access music metadata and static lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        Parameters
        ----------
        chart_name : str; optional
            Name of the chart to retrieve.

            **Valid values**:

            * :code:`"top"` – Editorial chart.
            * :code:`"hot"` – Most viewed lyrics in the last two hours.
            * :code:`"mxmweekly"` – Most viewed lyrics in the last seven
              days.
            * :code:`"mxmweekly_new"` – Most viewed lyrics in the last
              seven days, limited to new releases only.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. Use :code:`"XW"` for
            worldwide. Only applicable when `chart_name` is not
            :code:`"top"`.

            **Example**: :code:`"it"`.

            **API default**: :code:`"US"`.

        has_lyrics : bool; keyword-only; optional
            Whether to only include tracks that have lyrics.

            **API default**: :code:`False`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`100`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of
            tracks.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of Musixmatch content metadata for the top tracks.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "track_list": [
                          {
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
        if chart_name is not None:
            self._validate_type("chart_name", chart_name, str)
            chart_name = chart_name.strip().lower()
            if chart_name not in self._CHART_NAMES:
                chart_names_str = "', '".join(self._CHART_NAMES)
                raise ValueError(
                    f"Invalid chart {chart_name}. "
                    f"Valid values: '{chart_names_str}'."
                )
            params["chart_name"] = chart_name
        if country_code is not None:
            self._validate_country_code(country_code)
            params["country"] = country_code
        if has_lyrics is not None:
            self._validate_type("has_lyrics", has_lyrics, bool)
            params["f_has_lyrics"] = int(has_lyrics)
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["page_size"] = limit
        if page is not None:
            self._validate_number("page", page, int, 1)
            params["page"] = page
        return self._client._request(
            "GET", "chart.tracks.get", params=params
        ).json()

    @TTLCache.cached_method(ttl="popularity")
    def get_top_artists(
        self,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        `Charts > chart.artists.get <https://docs.musixmatch.com
        /lyrics-api/charts/chart-artists-get>`_: Get Musixmatch catalog
        information for the top artists on Musixmatch.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Basic plan
                    Access music metadata and static lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        Parameters
        ----------
        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. Use :code:`"XW"` for
            worldwide.

            **Example**: :code:`"it"`.

            **API default**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of artists to return.

            **Valid range**: :code:`1` to :code:`100`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of
            artists.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        Returns
        -------
        artists : dict[str, Any]
            Page of Musixmatch content metadata for the top artists.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "artist_list": [
                          {
                            "artist": {
                              "artist_alias_list": [
                                {
                                  "artist_alias": <str>
                                }
                              ],
                              "artist_comment": <str>,
                              "artist_country": <str>,
                              "artist_credits": {
                                "artist_list": []
                              },
                              "artist_id": <int>,
                              "artist_name": <str>,
                              "artist_name_translation_list": [
                                {
                                  "artist_name_translation": {
                                    "language": <str>,
                                    "translation": <str>
                                  }
                                }
                              ],
                              "artist_twitter_url": <str>,
                              "begin_date": <str>,
                              "begin_date_year": <str>,
                              "end_date": <str>,
                              "end_date_year": <str>,
                              "restricted": <int>,
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
        if country_code is not None:
            self._validate_country_code(country_code)
            params["country"] = country_code
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["page_size"] = limit
        if page is not None:
            self._validate_number("page", page, int, 1)
            params["page"] = page
        return self._client._request(
            "GET", "chart.artists.get", params=params
        ).json()

    @TTLCache.cached_method(ttl="static")
    def get_genres(self) -> dict[str, Any]:
        """
        `Charts > music.genres.get <https://docs.musixmatch.com
        /lyrics-api/charts/music-genres-get>`_: Get Musixmatch catalog
        information for available genres.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Basic plan
                    Access music metadata and static lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        Returns
        -------
        genres : dict[str, Any]
            Musixmatch content metadata for the available genres.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
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
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        return self._client._request("GET", "music.genres.get").json()
