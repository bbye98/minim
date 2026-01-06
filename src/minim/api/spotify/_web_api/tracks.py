from datetime import datetime
from numbers import Number
from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import SpotifyResourceAPI
from .users import UsersAPI


IntAttributeSpec = (
    int
    | tuple[int | None, int | None]
    | tuple[int | None, int | None, int | None]
)
FloatAttributeSpec = (
    float
    | tuple[float | None, float | None]
    | tuple[float | None, float | None, float | None]
)


class TracksAPI(SpotifyResourceAPI):
    """
    Tracks API endpoints for the Spotify Web API.

    .. note::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPI`
       and should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="popularity")
    def get_tracks(
        self, track_ids: str | list[str], /, *, country_code: str | None = None
    ) -> dict[str, Any]:
        """
        `Tracks > Get Track <https://developer.spotify.com/documentation
        /web-api/reference/get-track>`_: Get Spotify catalog information
        for a single track․
        `Tracks > Get Several Tracks <https://developer.spotify.com
        /documentation/web-api/reference/get-several-tracks>`_: Get
        Spotify catalog information for multiple tracks.

        .. admonition:: Third-party application mode
           :class: authorization-scope dropdown

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        track_ids : str or list[str]; positional-only
            Spotify IDs of the tracks. A maximum of 50 IDs can be sent
            in a request.

            **Examples**:

            .. container::

               * :code:`"7ouMYWpwJ422jRcDASZB7P"`
               * :code:`"7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ"`
               * :code:`["7ouMYWpwJ422jRcDASZB7P", "4VqPOruhp5EdPBeR92t6lQ"]`

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If provided, only content
            available in that market is returned. When a user access
            token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither a country code is provided nor a country can
               be determined from the user account, the content is
               considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        tracks : dict[str, Any]
            Spotify content metadata for the tracks.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single track

                  .. code::

                     {
                       "album": {
                         "album_type": <str>,
                         "artists": [
                           {
                             "external_urls": {
                               "spotify": <str>
                             },
                             "href": <str>,
                             "id": <str>,
                             "name": <str>,
                             "type": "artist",
                             "uri": <str>
                           }
                         ],
                         "available_markets": <list[str]>,
                         "external_urls": {
                           "spotify": <str>
                         },
                         "href": <str>,
                         "id": <str>,
                         "images": [
                           {
                             "height": <int>,
                             "url": <str>,
                             "width": <int>
                           }
                         ],
                         "name": <str>,
                         "release_date": <str>,
                         "release_date_precision": <str>,
                         "restrictions": {
                           "reason": <str>
                         },
                         "total_tracks": <int>,
                         "type": "album",
                         "uri": <str>
                       },
                       "artists": [
                         {
                           "external_urls": {
                             "spotify": <str>
                           },
                           "href": <str>,
                           "id": <str>,
                           "name": <str>,
                           "type": "artist",
                           "uri": <str>
                         }
                       ],
                       "available_markets": <list[str]>,
                       "disc_number": <int>,
                       "duration_ms": <int>,
                       "explicit": <bool>,
                       "external_ids": {
                         "ean": <str>,
                         "isrc": <str>,
                         "upc": <str>
                       },
                       "external_urls": {
                         "spotify": <str>
                       },
                       "href": <str>,
                       "id": <str>,
                       "is_local": <bool>,
                       "is_playable": <bool>,
                       "linked_from": <dict[str, Any]>,
                       "name": <str>,
                       "popularity": <int>,
                       "preview_url": <str>,
                       "restrictions": {
                         "reason": <str>
                       },
                       "track_number": <int>,
                       "type": "track",
                       "uri": <str>
                     }

               .. tab:: Multiple tracks

                  .. code::

                     {
                       "tracks": [
                         {
                           "album": {
                             "album_type": <str>,
                             "artists": [
                               {
                                 "external_urls": {
                                   "spotify": <str>
                                 },
                                 "href": <str>,
                                 "id": <str>,
                                 "name": <str>,
                                 "type": "artist",
                                 "uri": <str>
                               }
                             ],
                             "available_markets": <list[str]>,
                             "external_urls": {
                               "spotify": <str>
                             },
                             "href": <str>,
                             "id": <str>,
                             "images": [
                               {
                                 "height": <int>,
                                 "url": <str>,
                                 "width": <int>
                               }
                             ],
                             "name": <str>,
                             "release_date": <str>,
                             "release_date_precision": <str>,
                             "restrictions": {
                               "reason": <str>
                             },
                             "total_tracks": <int>,
                             "type": "album",
                             "uri": <str>
                           },
                           "artists": [
                             {
                               "external_urls": {
                                 "spotify": <str>
                               },
                               "href": <str>,
                               "id": <str>,
                               "name": <str>,
                               "type": "artist",
                               "uri": <str>
                             }
                           ],
                           "available_markets": <list[str]>,
                           "disc_number": <int>,
                           "duration_ms": <int>,
                           "explicit": <bool>,
                           "external_ids": {
                             "ean": <str>,
                             "isrc": <str>,
                             "upc": <str>
                           },
                           "external_urls": {
                             "spotify": <str>
                           },
                           "href": <str>,
                           "id": <str>,
                           "is_local": <bool>,
                           "is_playable": <bool>,
                           "linked_from": <dict[str, Any]>,
                           "name": <str>,
                           "popularity": <int>,
                           "preview_url": <str>,
                           "restrictions": {
                             "reason": <str>
                           },
                           "track_number": <int>,
                           "type": "track",
                           "uri": <str>
                         }
                       ]
                     }
        """
        return self._get_resources(
            "tracks", track_ids, country_code=country_code
        )

    @_copy_docstring(UsersAPI.get_my_saved_tracks)
    def get_my_saved_tracks(
        self,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_my_saved_tracks(
            country_code=country_code, limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.save_tracks)
    def save_tracks(
        self,
        track_ids: str
        | tuple[str, str | datetime]
        | dict[str, str | datetime]
        | list[str | tuple[str, str | datetime] | dict[str, str | datetime]],
        /,
    ) -> None:
        self._client.users.save_tracks(track_ids)

    @_copy_docstring(UsersAPI.remove_saved_tracks)
    def remove_saved_tracks(self, track_ids: str | list[str], /) -> None:
        self._client.users.remove_saved_tracks(track_ids)

    @_copy_docstring(UsersAPI.are_tracks_saved)
    def are_tracks_saved(self, track_ids: str | list[str], /) -> list[bool]:
        return self._client.users.are_tracks_saved(track_ids)

    @TTLCache.cached_method(ttl="static")
    def get_audio_features(
        self, track_ids: str | list[str], /
    ) -> dict[str, Any]:
        """
        `Tracks > Get Track's Audio Features
        <https://developer.spotify.com/documentation/web-api/reference
        /get-audio-features>`_: Get the audio features for a single
        track․
        `Tracks > Get Several Tracks' Audio Features
        <https://developer.spotify.com/documentation/web-api/reference
        /get-several-audio-features>`_: Get the audio features for
        multiple tracks.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Required

              Extended quota mode before November 27, 2024
                  Access the :code:`/audio-features/{id}` endpoint.
                  `Learn more. <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        track_ids : str or list[str]; positional-only
            Spotify IDs of the tracks. A maximum of 50 IDs can be sent
            in a request.

            **Examples**:

            .. container::

               * :code:`"7ouMYWpwJ422jRcDASZB7P"`
               * :code:`"7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ"`
               * :code:`["7ouMYWpwJ422jRcDASZB7P", "4VqPOruhp5EdPBeR92t6lQ"]`

        Returns
        -------
        audio_features : dict[str, Any]
            Audio features for the tracks.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single track

                  .. code::

                     {
                       "acousticness": <float>,
                       "analysis_url": <str>,
                       "danceability": <float>,
                       "duration_ms": <int>,
                       "energy": <float>,
                       "id": <str>,
                       "instrumentalness": <float>,
                       "key": <int>,
                       "liveness": <float>,
                       "loudness": <float>,
                       "mode": <int>,
                       "speechiness": <float>,
                       "tempo": <float>,
                       "time_signature": <int>,
                       "track_href": <str>,
                       "type": "audio_features",
                       "uri": <str>,
                       "valence": <float>
                     }

               .. tab:: Multiple tracks

                  .. code::

                     {
                       "audio_features": [
                         {
                           "acousticness": <float>,
                           "analysis_url": <str>,
                           "danceability": <float>,
                           "duration_ms": <int>,
                           "energy": <float>,
                           "id": <str>,
                           "instrumentalness": <float>,
                           "key": <int>,
                           "liveness": <float>,
                           "loudness": <float>,
                           "mode": <int>,
                           "speechiness": <float>,
                           "tempo": <float>,
                           "time_signature": <int>,
                           "track_href": <str>,
                           "type": "audio_features",
                           "uri": <str>,
                           "valence": <float>
                         }
                       ]
                     }
        """
        return self._get_resources("audio-features", track_ids, limit=100)

    @TTLCache.cached_method(ttl="static")
    def get_audio_analysis(self, track_id: str, /) -> dict[str, Any]:
        """
        `Tracks > Get Track's Audio Analysis
        <https://developer.spotify.com/documentation/web-api/reference
        /get-audio-analysis>`_: Get a low-level audio analysis
        (track structure and musical content, including rhythm, pitch,
        and timbre) of a single track.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Required

              Extended quota mode before November 27, 2024
                  Access the :code:`/audio-analysis/{id}` endpoint.
                  `Learn more. <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        track_id : str; positional-only
            Spotify ID of the track.

            **Example**: :code:`"11dFghVXANMlKmJXsNCbNl"`.

        Returns
        -------
        audio_analysis : dict[str, Any]
            Audio analysis of the track.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "bars": [
                      {
                        "confidence": <float>,
                        "duration": <float>,
                        "start": <float>
                      }
                    ],
                    "beats": [
                      {
                        "confidence": <float>,
                        "duration": <float>,
                        "start": <float>
                      }
                    ],
                    "meta": {
                      "analysis_time": <float>,
                      "analyzer_version": <str>,
                      "detailed_status": <str>,
                      "input_process": <str>,
                      "platform": <str>,
                      "status_code": <int>,
                      "timestamp": <int>
                    },
                    "sections": [
                      {
                        "confidence": <float>,
                        "duration": <float>,
                        "key": <int>,
                        "key_confidence": <float>,
                        "loudness": <float>,
                        "mode": <int>,
                        "mode_confidence": <float>,
                        "start": <float>,
                        "tempo": <float>,
                        "tempo_confidence": <float>,
                        "time_signature": <int>,
                        "time_signature_confidence": <float>
                      }
                    ],
                    "segments": [
                      {
                        "confidence": <float>,
                        "duration": <float>,
                        "loudness_end": <float>,
                        "loudness_max": <float>,
                        "loudness_max_time": <float>,
                        "loudness_start": <float>,
                        "pitches": <list[float]>,
                        "start": <float>,
                        "timbre": <list[float]>
                      }
                    ],
                    "tatums": [
                      {
                        "confidence": <float>,
                        "duration": <float>,
                        "start": <float>
                      }
                    ],
                    "track": {
                      "analysis_channels": <int>,
                      "analysis_sample_rate": <int>,
                      "code_version": <float>,
                      "codestring": <str>,
                      "duration": <float>,
                      "echoprint_version": <float>,
                      "echoprintstring": <str>,
                      "end_of_fade_in": <float>,
                      "key": <int>,
                      "key_confidence": <float>,
                      "loudness": <float>,
                      "mode": <int>,
                      "mode_confidence": <float>,
                      "num_samples": <int>,
                      "offset_seconds": <float>,
                      "rhythm_version": <int>,
                      "rhythmstring": <str>,
                      "sample_md5": <str>,
                      "start_of_fade_out": <float>,
                      "synch_version": <int>,
                      "synchstring": <str>,
                      "tempo": <float>,
                      "tempo_confidence": <float>,
                      "time_signature": <int>,
                      "time_signature_confidence": <float>,
                      "window_seconds": <float>
                    }
                  }
        """
        self._client._validate_spotify_id(track_id)
        return self._client._request(
            "GET", f"audio-analysis/{track_id}"
        ).json()

    @TTLCache.cached_method(ttl="recommendation")
    def get_track_recommendations(
        self,
        seed_artist_ids: str | list[str] | None = None,
        seed_genres: str | list[str] | None = None,
        seed_track_ids: str | list[str] | None = None,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        acousticness: FloatAttributeSpec | None = None,
        danceability: FloatAttributeSpec | None = None,
        duration_ms: IntAttributeSpec | None = None,
        energy: FloatAttributeSpec | None = None,
        instrumentalness: FloatAttributeSpec | None = None,
        key: IntAttributeSpec | None = None,
        liveness: FloatAttributeSpec | None = None,
        loudness: FloatAttributeSpec | None = None,
        mode: IntAttributeSpec | None = None,
        popularity: IntAttributeSpec | None = None,
        speechiness: FloatAttributeSpec | None = None,
        tempo: FloatAttributeSpec | None = None,
        time_signature: IntAttributeSpec | None = None,
        valence: FloatAttributeSpec | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Recommendations <https://developer.spotify.com
        /documentation/web-api/reference/get-recommendations>`_: Get
        track recommendations based on seed artists, genres, and/or
        tracks, with optional tuning parameters.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Required

              Extended quota mode before November 27, 2024
                  Access the :code:`/recommendations` endpoint. `Learn
                  more. <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        .. note::

           For very new or obscure artists and tracks, there might not
           be enough data to generate recommendations.

        .. important::

           Up to 5 seed values may be provided in any combination of
           :code:`seed_artist_ids`, :code:`seed_genres`, and
           :code:`seed_track_ids`.

        .. hint::

           Track attribute parameters (`acousticness`, `danceability`,
           `duration_ms`, etc.) can be provided in one of the following
           ways:

           .. table:: Track attribute specifications

              ============================= ===================================
              Data type                     Specification
              ============================= ===================================
              Number                        Target value
              tuple[Number, Number]         Minimum and maximum values
              tuple[Number, Number, Number] Minimum, maximum, and target values
              ============================= ===================================

        Parameters
        ----------
        seed_artist_ids : str or list[str]; optional
            Spotify IDs of seed artists.

            **Examples**:

            .. container::

               * :code:`"0TnOYISbd1XYRBk9myaseg"`
               * :code:`"0TnOYISbd1XYRBk9myaseg,57dN52uHvrHOxijzpIgu3E"`
               * :code:`["0TnOYISbd1XYRBk9myaseg", "57dN52uHvrHOxijzpIgu3E"]`

        seed_genres : str or list[str]; optional
            Spotify IDs of seed genres.

            .. seealso::

                :meth:`~minim.api.spotify.GenresAPI.get_seed_genres`
                – Get available seed genres.

        seed_track_ids : str or list[str]; optional
            Spotify IDs of seed tracks.

            **Examples**:

            .. container::

               * :code:`"7ouMYWpwJ422jRcDASZB7P"`
               * :code:`"7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ"`
               * :code:`["7ouMYWpwJ422jRcDASZB7P", "4VqPOruhp5EdPBeR92t6lQ"]`

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If provided, only content
            available in that market is returned. When a user access
            token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither a country code is provided nor a country can
               be determined from the user account, the content is
               considered unavailable for the client.

            **Example**: :code:`"ES"`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        acousticness : float or tuple[float, ...]; keyword-only; optional
            Confidence measure of whether a track is acoustic.

            **Valid range**: :code:`0.0` (electronic) to :code:`1.0`
            (acoustic).

            **Example**: :code:`0.00242`.

        danceability : float or tuple[float, ...]; keyword-only; optional
            Suitability of a track for dancing based on a combination of
            musical elements, including tempo, rhythim stability, beat
            strength, and overall regularity.

            **Valid range**: :code:`0.0` (least danceable) to
            :code:`1.0` (most danceable).

            **Example**: :code:`0.585`.

        duration_ms : int or tuple[int, ...]; keyword-only; optional
            Track duration in milliseconds.

            **Minimum value**: :code:`0`.

            **Example**: :code:`237_040`.

        energy : float or tuple[float, ...]; keyword-only; optional
            Perceptual measure of a track's intensity and activity based
            on its dynamic range, perceived loudness, timbre, onset rate,
            and general entropy.

            **Valid range**: :code:`0.0` (e.g., Bach prelude) to
            :code:`1.0` (e.g., death metal).

            **Example**: :code:`0.842`.

        instrumentalness : float or tuple[float, ...]; keyword-only; optional
            Confidence measure of whether a track contains no vocals.

            **Valid range**: :code:`0.0` (vocal) to :code:`1.0`
            (instrumental).

            **Example**: :code:`0.00686`.

        key : int or tuple[int, ...]; keyword-only; optional
            Key a track is in using standard pitch class notation.

            **Valid values**:

            .. container::

               * :code:`-1` – No key detected.
               * :code:`0` – C.
               * :code:`1` – C♯ or D♭.
               * :code:`2` – D
               * :code:`3` – D♯ or E♭.
               * :code:`4` – E.
               * :code:`5` – F.
               * :code:`6` – F♯ or G♭.
               * :code:`7` – G.
               * :code:`8` – G♯ or A♭.
               * :code:`9` – A.
               * :code:`10` – A♯ or B♭.
               * :code:`11` – B.

        liveness : float or tuple[float, ...]; keyword-only; optional
            Confidence measure of whether a track was performed live
            based on the presence of an audience in the recording.

            **Valid range**: :code:`0.0` (studio) to :code:`1.0` (live).

            **Example**: :code:`0.0866`.

        loudness : float or tuple[float, ...]; keyword-only; optional
            Overall loudness of a track in decibels.

            **Maximum value**: :code:`0.0`.

            **Example**: :code:`-5.883`.

        mode : int or tuple[int, ...]; keyword-only; optional
            Musical mode of a track.

            **Valid values**: :code:`0` for minor scale, :code:`1` for
            major scale.

        popularity : int or tuple[int, ...]; keyword-only; optional
            Popularity of a track based on the total number of plays it
            has had and how recent those plays are.

            .. note::

               The popularity value is not updated in real time and may
               lag actual value by a few days.

            **Valid range**: :code:`0` (least popular) to :code:`100`
            (most popular).

        speechiness : float or tuple[float, ...]; keyword-only; optional
            Confidence measure of whether a track contains spoken words.

            **Valid range**: :code:`0.0` (music) to :code:`1.0`
            (speech-like).

            **Example**: :code:`0.0556`.

        tempo : float or tuple[float, ...]; keyword-only; optional
            Overall estimated tempo of a track in beats per minute.

            **Minimum value**: :code:`0.0`.

            **Example**: :code:`118.211`.

        time_signature : int or tuple[int, ...]; keyword-only; optional
            Estimated time signature of the track.

            **Valid values**:

            .. container::

               * :code:`3` – 3/4.
               * :code:`4` – 4/4.
               * :code:`5` – 5/4.
               * :code:`6` – 6/4.
               * :code:`7` – 7/4.

        valence : float or tuple[float, ...]; keyword-only; optional
            Confidence measure of the musical positiveness conveyed by a
            track.

            **Valid range**: :code:`0.0` (e.g., happy, cheerful,
            euphoric) to :code:`1.0` (e.g., sad, depressed, angry).

            **Example**: :code:`0.428`.

        Returns
        -------
        recommendations : dict[str, Any]
            Spotify content metadata for the track recommendations
            generated from the provided seeds and tuning parameters.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "seeds": [
                      {
                        "afterFilteringSize": <int>,
                        "afterRelinkingSize": <int>,
                        "href": <str>,
                        "id": <str>,
                        "initialPoolSize": <int>,
                        "type": <str>
                      }
                    ],
                    "tracks": [
                      {
                        "album": {
                          "album_type": <str>,
                          "artists": [
                            {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "href": <str>,
                              "id": <str>,
                              "name": <str>,
                              "type": "artist",
                              "uri": <str>
                            }
                          ],
                          "available_markets": <list[str]>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "height": <int>,
                              "url": <str>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "restrictions": {
                            "reason": <str>
                          },
                          "total_tracks": <int>,
                          "type": "album",
                          "uri": <str>
                        },
                        "artists": [
                          {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "name": <str>,
                            "type": "artist",
                            "uri": <str>
                          }
                        ],
                        "available_markets": <list[str]>,
                        "disc_number": <int>,
                        "duration_ms": <int>,
                        "explicit": <bool>,
                        "external_ids": {
                          "ean": <str>,
                          "isrc": <str>,
                          "upc": <str>
                        },
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "is_local": <bool>,
                        "is_playable": <bool>,
                        "linked_from": {},
                        "name": <str>,
                        "popularity": <int>,
                        "preview_url": <str>,
                        "restrictions": {
                          "reason": <str>
                        },
                        "track_number": <int>,
                        "type": "track",
                        "uri": <str>
                      }
                    ]
                  }
        """
        params = {}
        if country_code is not None:
            self._client._validate_market(country_code)
            params["market"] = country_code
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit

        n_seeds = self._parse_seeds(
            "seed_tracks",
            seed_track_ids,
            self._parse_seeds(
                "seed_genres",
                seed_genres,
                self._parse_seeds("seed_artists", seed_artist_ids, 0, params),
                params,
            ),
            params,
        )
        if n_seeds == 0:
            raise ValueError("At least one seed must be provided.")
        if n_seeds > 5:
            raise ValueError("A maximum of 5 seeds is allowed.")

        _locals = locals()
        for attr, dtype, range_ in [
            ("acousticness", float, (0.0, 1.0)),
            ("danceability", float, (0.0, 1.0)),
            ("duration_ms", int, (0,)),
            ("energy", float, (0.0, 1.0)),
            ("instrumentalness", float, (0.0, 1.0)),
            ("key", int, (-1, 11)),
            ("liveness", float, (0.0, 1.0)),
            ("loudness", float, (None, 0.0)),
            ("mode", int, (0, 1)),
            ("popularity", int, (0, 100)),
            ("speechiness", float, (0.0, 1.0)),
            ("tempo", float, (0.0,)),
            ("time_signature", int, (3, 7)),
            ("valence", float, (0.0, 1.0)),
        ]:
            self._parse_attribute(
                attr, _locals.get(attr), dtype, range_, params
            )

        return self._client._request(
            "GET", "recommendations", params=params
        ).json()

    @TTLCache.cached_method(ttl="hourly")
    def get_my_top_tracks(
        self,
        *,
        time_range: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Users > Get Current User's Top Tracks
        <https://developer.spotify.com/documentation/web-api/reference
        /get-users-top-artists-and-tracks>`_: Get Spotify catalog
        information for the current user's top tracks.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-top-read` scope
                 Read your top artists and contents. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-top-read>`__

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        time_range : str; keyword-only; optional
            Time frame over which the current user's listening history
            is analyzed to determine top tracks.

            **Valid values**:

            .. container::

               * :code:`"long_term"` – Approximately one year of data,
                 including all new data as it becomes available.
               * :code:`"medium_term"` – Approximately the last six
                 months of data.
               * :code:`"short_term"` – Approximately the last four
                 weeks of data.

            **API default**: :code:`"medium_term"`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        items : dict[str, Any]
            Page of Spotify content metadata for the current user's top
            tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "album": {
                          "album_type": <str>,
                          "artists": [
                            {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "href": <str>,
                              "id": <str>,
                              "name": <str>,
                              "type": "artist",
                              "uri": <str>
                            }
                          ],
                          "available_markets": <list[str]>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "height": <int>,
                              "url": <str>,
                              "width": <int>
                            }
                          ],
                          "is_playable": <bool>,
                          "name": <str>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "total_tracks": <int>,
                          "type": "album",
                          "uri": <str>
                        },
                        "artists": [
                          {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "name": <str>,
                            "type": "artist",
                            "uri": <str></str>
                          }
                        ],
                        "available_markets": <list[str]>,
                        "disc_number": <int>,
                        "duration_ms": <int>,
                        "explicit": <bool>,
                        "external_ids": {
                          "isrc": <str>
                        },
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "is_local": <bool>,
                        "is_playable": <bool>,
                        "name": <str>,
                        "popularity": <int>,
                        "preview_url": <str>,
                        "track_number": <int>,
                        "type": "track",
                        "uri": <str>
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        return self._client.users.get_my_top_items(
            "tracks", time_range=time_range, limit=limit, offset=offset
        )

    def _parse_attribute(
        self,
        attribute: str,
        value: int | float | tuple[int | float | None, ...],
        data_type: type,
        range_: tuple[int | float | None, int | float | None],
        params: dict[str, Any],
    ) -> None:
        """
        Parse and add a track attribute to a dictionary holding the
        request parameters for :meth:`get_track_recommendations`.

        Parameters
        ----------
        attribute : str
            Track attribute.

            **Valid values**: :code:`"acousticness"`,
            :code:`"danceability"`, :code:`"duration_ms"`,
            :code:`"energy"`, :code:`"instrumentalness"`,
            :code:`"key"`, :code:`"liveness"`, :code:`"loudness"`,
            :code:`"mode"`, :code:`"popularity"`, :code:`"speechiness"`,
            :code:`"tempo"`, :code:`"time_signature"`,
            :code:`"valence"`.

        value : int, float, or tuple[int | float, ...]
            Track attribute value.

        data_type : type
            Allowed data type for the track attribute.

            **Valid values**: :code:`int` or :code:`float`.

        range_ : tuple[int | float | None, int | float | None]
            Valid range for the track attribute.

        params : dict[str, Any]
            Query parameters to include in the request.

            .. note::

               This `dict` is mutated in-place.
        """
        if value is None:
            return

        is_int = data_type is int
        if isinstance(value, data_type):
            self._client._validate_number(attribute, value, data_type, *range_)
            params[f"target_{attribute}"] = value
        elif isinstance(value, tuple | list | set):
            if is_int and any(
                not (isinstance(v, int) or v is None) for v in value
            ):
                raise ValueError(
                    f"Values for track attribute {attribute!r} must "
                    "be integers (or None)."
                )
            elif any(
                not (
                    isinstance(v, Number)
                    or isinstance(v, str)
                    and v.isdecimal()
                    or v is None
                )
                for v in value
            ):
                raise ValueError(
                    f"Values for track attribute {attribute!r} must "
                    "be numbers (or None)."
                )
            length = len(value)
            if length not in range(2, 4):
                raise ValueError(
                    "The tuple provided for track attribute "
                    f"{attribute!r} must have length 2 or 3, not "
                    f"length {length}."
                )
            else:
                for v in value:
                    self._client._validate_number(
                        attribute, v, data_type, *range_
                    )
                if length == 2:
                    params[f"min_{attribute}"], params[f"max_{attribute}"] = (
                        value
                    )
                elif length == 3:
                    (
                        params[f"min_{attribute}"],
                        params[f"max_{attribute}"],
                        params[f"target_{attribute}"],
                    ) = value
        else:
            raise ValueError(
                f"The value provided for track attribute {attribute!r} "
                f"must be a {(dtype := data_type.__name__)} or a "
                f"tuple of {dtype}s, not a {type(value).__name__}."
            )

    def _parse_seeds(
        self,
        seed_type: str,
        seeds: str | list[str] | None,
        n_seeds: int,
        params: dict[str, Any],
    ) -> int:
        """
        Parse and add seeds to a dictionary holding the request
        parameters for :meth:`get_track_recommendations`.

        Parameters
        ----------
        seed_type : str
            Seed type.

            **Valid values**: :code:`"seed_artists"`,
            :code:`"seed_genres"`, :code:`"seed_tracks"`.

        seeds : str, list[str], or None
            Seed values.

        n_seeds : int
            Starting number of seed values.

        params : dict[str, Any]
            Query parameters to include in the request.

            .. note::

               This `dict` is mutated in-place.

        Returns
        -------
        n_seeds : int
            Ending number of seed values.
        """
        if seeds is None:
            return n_seeds
        if seed_type != "seed_genres":
            params[seed_type], new_n_seeds = self._prepare_seed_genres(
                seeds, limit=5
            )
        else:
            params[seed_type], new_n_seeds = self._client._prepare_spotify_ids(
                seeds, limit=5
            )
        return n_seeds + new_n_seeds

    def _prepare_seed_genres(
        self, seed_genres: str | list[str], /, limit: int
    ) -> tuple[str, int]:
        """
        Normalize, validate, and serialize seed genres.

        Parameters
        ----------
        seed_genres : str or list[str]; positional-only
            Seed genres.

        limit : int; keyword-only
            Maximum number of seed genres that can be sent in a
            request.

        Returns
        -------
        seed_genres : str
            Comma-separated string of seed genres.

        n_seed_genres : int
            Number of seed genres.
        """
        if isinstance(seed_genres, str):
            return self._prepare_seed_genres(seed_genres.strip().split(","))

        seed_genres = set(seed_genres)
        n_genres = len(seed_genres)
        if n_genres > limit:
            raise ValueError(
                f"A maximum of {limit} seed genres can be sent in a request."
            )
        for genre in seed_genres:
            self._client._validate_seed_genre(genre)
        return ",".join(sorted(seed_genres)), n_genres
