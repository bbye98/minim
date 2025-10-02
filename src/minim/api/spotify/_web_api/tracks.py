from collections.abc import Collection
from datetime import datetime
from numbers import Number
from typing import TYPE_CHECKING, Any

from ..._shared import _copy_docstring
from .users import WebAPIUserEndpoints

if TYPE_CHECKING:
    from .. import WebAPI


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


class WebAPITrackEndpoints:
    """
    Spotify Web API track endpoints.

    .. note::

       This class is managed by :class:`minim.api.spotify.WebAPI` and
       should not be instantiated directly.
    """

    def __init__(self, client: "WebAPI", /) -> None:
        """
        Parameters
        ----------
        client : minim.api.spotify.WebAPI
            Minim's Spotify Web API client.
        """
        self._client = client

    def get_tracks(
        self, track_ids: str | Collection[str], /, *, market: str | None = None
    ) -> dict[str, Any]:
        """
        `Tracks > Get Track <https://developer.spotify.com/documentation
        /web-api/reference/get-track>`_: Get Spotify catalog information
        for a single track․
        `Tracks > Get Several Tracks <https://developer.spotify.com
        /documentation/web-api/reference/get-several-tracks>`_: Get
        Spotify catalog information for multiple tracks.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
        track_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the tracks. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"11dFghVXANMlKmJXsNCbNl"`,
            :code:`"7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B"`,
            :code:`["7ouMYWpwJ422jRcDASZB7P", "4VqPOruhp5EdPBeR92t6lQ",
            "2takcwOaAZWiXQijPHIx7B"]`.

        market : str, keyword-only, optional
            ISO 3166-1 alpha-2 country code. If specified, only content
            available in that market is returned. When a valid user
            access token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither the market nor the user's country are
               provided, the content is considered unavailable for the
               client.

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
        string = isinstance(track_ids, str)
        track_ids, n_ids = self._client._prepare_spotify_ids(
            track_ids, limit=50
        )
        params = {}
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if string and n_ids == 1:
            return self._client._request(
                "GET", f"tracks/{track_ids}", params=params
            ).json()

        params["ids"] = track_ids
        return self._client._request("GET", "tracks", params=params).json()

    def get_saved_tracks(
        self,
        *,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get User's Saved Tracks <https://developer.spotify.com
        /documentation/web-api/reference/get-users-saved-tracks>`_: Get
        the tracks saved in the current user's "Your Music" library.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read`
                 Access your saved content.

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
        market : str, keyword-only, optional
            ISO 3166-1 alpha-2 country code. If specified, only content
            available in that market is returned. When a valid user
            access token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither the market nor the user's country are
               provided, the content is considered unavailable for the
               client.

            **Example**: :code:`"ES"`.

        limit : int, keyword-only, optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first track to return. Use with `limit` to get
            the next set of tracks.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        saved_tracks : dict[str, Any]
            Spotify content metadata for the user's saved tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "added_at": <str>,
                        "track": {
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
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        self._client._require_scopes("get_saved_tracks", "user-library-read")
        params = {}
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request("GET", "me/tracks", params=params).json()

    def save_tracks(
        self,
        track_ids: str
        | tuple[str, str | datetime]
        | dict[str, str | datetime]
        | list[str | tuple[str, str | datetime] | dict[str, str | datetime]],
        /,
    ) -> None:
        """
        `Tracks > Save Tracks for Current User
        <https://developer.spotify.com/documentation/web-api/reference
        /save-tracks-user>`_: Save one or more tracks to the current
        user's "Your Music" library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify`
                  Manage your saved content.

        Parameters
        ----------
        track_ids : str, tuple[str, str | datetime], \
        dict[str, str | datetime], or \
        list[str | tuple[str, str | datetime] | dict[str, str | datetime]], \
        positional-only
            (Comma-separated) list of Spotify IDs of the tracks,
            optionally accompanied by timestamps to maintain a specific
            chronological order in the user's library. A maximum of 50 
            IDs can be sent in one request.

            **Examples**: 
            
            .. container::
            
               * :code:`"4iV5W9uYEdYUVa79Axb7Rh"`
               * :code:`("4iV5W9uYEdYUVa79Axb7Rh", "2010-01-01T00:00:00Z")`
               * :code:`{"id": "4iV5W9uYEdYUVa79Axb7Rh", 
                 "added_at": "2010-01-01T00:00:00Z"}`
               * .. code::
               
                    [
                        "4iV5W9uYEdYUVa79Axb7Rh", 
                        ("11dFghVXANMlKmJXsNCbNl", "2017-05-26T00:00:00Z"), 
                        {"id": "7ouMYWpwJ422jRcDASZB7P", "added_at": "2006-06-28T00:00:00Z"}
                    ]
        """
        self._client._require_scopes("save_tracks", "user-library-modify")
        if isinstance(track_ids, str):
            track_ids = [
                {
                    "id": track_ids,
                    "added_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            ]
        elif isinstance(track_ids, dict):
            track_ids = [track_ids]
        elif (
            isinstance(track_ids, tuple)
            and len(track_ids) == 2
            and (
                timestamp_is_str := isinstance(track_ids[1], str)
                and len(track_ids[1]) == 20
                or isinstance(track_ids[1], datetime)
            )
        ):
            track_ids = [
                {
                    "id": track_ids[0],
                    "added_at": track_ids[1]
                    if timestamp_is_str
                    else track_ids[1].strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            ]
        else:  # list
            for idx, track in enumerate(track_ids):
                if isinstance(track, str):
                    track_ids[idx] = {
                        "id": track,
                        "added_at": datetime.now().strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                    }
                elif isinstance(track, tuple):
                    track_ids[idx] = {
                        "id": track[0],
                        "added_at": timestamp
                        if isinstance(timestamp := track[1], str)
                        else timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
        self._client._request(
            "PUT", "me/tracks", json={"timestamped_ids": track_ids}
        )

    def remove_saved_tracks(self, track_ids: str | Collection[str], /) -> None:
        """
        `Tracks > Remove User's Saved Tracks
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-tracks-user>`_: Remove one or more tracks from the
        current user's "Your Music" library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify`
                  Manage your saved content.

        Parameters
        ----------
        track_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the tracks. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"11dFghVXANMlKmJXsNCbNl"`,
            :code:`"7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B"`,
            :code:`["7ouMYWpwJ422jRcDASZB7P", "4VqPOruhp5EdPBeR92t6lQ",
            "2takcwOaAZWiXQijPHIx7B"]`.
        """
        self._client._require_scopes(
            "remove_saved_tracks", "user-library-modify"
        )
        self._client._request(
            "DELETE",
            "me/tracks",
            params={
                "ids": self._client._prepare_spotify_ids(track_ids, limit=50)[0]
            },
        )

    def are_tracks_saved(
        self, track_ids: str | Collection[str], /
    ) -> list[bool]:
        """
        `Tracks > Check User's Saved Tracks
        <https://developer.spotify.com/documentation/web-api/reference
        /check-users-saved-tracks>`_: Check if one or more tracks are
        already saved in the current user's "Your Music" library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read`
                  Access your saved content.

        Parameters
        ----------
        track_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the tracks. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"11dFghVXANMlKmJXsNCbNl"`,
            :code:`"7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B"`,
            :code:`["7ouMYWpwJ422jRcDASZB7P", "4VqPOruhp5EdPBeR92t6lQ",
            "2takcwOaAZWiXQijPHIx7B"]`.

        Returns
        -------
        are_tracks_saved : list[bool]
            Whether the current user has each of the specified tracks
            saved in their "Your Music" library.

            **Sample response**: :code:`[False, True]`.
        """
        self._client._require_scopes("are_tracks_saved", "user-library-read")
        return self._client._request(
            "GET",
            "me/tracks/contains",
            params={
                "ids": self._client._prepare_spotify_ids(track_ids, limit=50)[0]
            },
        ).json()

    def get_audio_features(
        self, track_ids: str | Collection[str], /
    ) -> dict[str, Any]:
        """
        `Tracks > Get Track's Audio Features
        <https://developer.spotify.com/documentation/web-api/reference
        /get-audio-features>`_: Get audio feature information for a
        single track․
        `Tracks > Get Several Tracks' Audio Features
        <https://developer.spotify.com/documentation/web-api/reference
        /get-several-audio-features>`_: Get audio feature information
        for multiple tracks.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Required

              Extended quota mode before November 11, 2024
                  Access the :code:`audio-features` endpoint.

        Parameters
        ----------
        track_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the tracks. A
            maximum of 100 IDs can be sent in one request.

            **Examples**: :code:`"11dFghVXANMlKmJXsNCbNl"`,
            :code:`"7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B"`,
            :code:`["7ouMYWpwJ422jRcDASZB7P", "4VqPOruhp5EdPBeR92t6lQ",
            "2takcwOaAZWiXQijPHIx7B"]`.

        Returns
        -------
        audio_features : dict[str, Any]
            Audio feature information for the tracks.

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
                       "type": <str>,
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
                           "type": <str>,
                           "uri": <str>,
                           "valence": <float>
                         }
                       ]
                     }
        """
        string = isinstance(track_ids, str)
        track_ids, n_ids = self._client._prepare_spotify_ids(
            track_ids, limit=100
        )
        if string and n_ids == 1:
            return self._client._request(
                "GET", f"audio-features/{track_ids}"
            ).json()
        return self._client._request(
            "GET", "audio-features", params={"ids": track_ids}
        ).json()

    def get_audio_analysis(self, track_id: str, /) -> dict[str, Any]:
        """
        `Tracks > Get Track's Audio Analysis
        <https://developer.spotify.com/documentation/web-api/reference
        /get-audio-analysis>`_: Get a low-level audio analysis
        (track structure and musical content, including rhythm, pitch,
        and timbre) for a single track.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Required

              Extended quota mode before November 11, 2024
                  Access the :code:`audio-analysis` endpoint.

        Parameters
        ----------
        track_id : str, positional-only
            Spotify ID of the track.

            **Example**: :code:`"11dFghVXANMlKmJXsNCbNl"`.

        Returns
        -------
        audio_analysis : dict[str, Any]
            Audio analysis for the track.

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
        return self._client._request("GET", f"audio-analysis/{track_id}").json()

    def get_recommendations(
        self,
        seed_artists: str | Collection[str] | None = None,
        seed_genres: str | Collection[str] | None = None,
        seed_tracks: str | Collection[str] | None = None,
        *,
        market: str | None = None,
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
        recommendations based on the available information for seed
        entities (artists, genres, and tracks).

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Required

              Extended quota mode before November 11, 2024
                  Access the :code:`recommendations` endpoint.

        .. note::

           For very new or obscure artists and tracks, there might not
           be enough data to generate recommendations.

        .. hint::

           Track attribute parameters (`acousticness`, `danceability`,
           `duration_ms`, etc.) can be specified in one of the following
           ways:

           .. _track-attribute-hint:
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
        seed_artists : str or Collection[str], optional
            (Comma-separated) list of Spotify IDs of seed artists.
            Up to 5 seed values may be provided in any combination of
            :code:`seed_artists`, :code:`seed_genres` and
            :code:`seed_tracks`.

            **Examples**: :code:`"0TnOYISbd1XYRBk9myaseg"`,
            :code:`"2CIMQHirSU0MQqyYHq0eOx,57dN52uHvrHOxijzpIgu3E"`,
            :code:`["2CIMQHirSU0MQqyYHq0eOx", "57dN52uHvrHOxijzpIgu3E"]`.

        seed_genres : str or Collection[str], optional
            (Comma-separated) list of seed genres. Up to 5 seed values
            may be provided in any combination of :code:`seed_artists`,
            :code:`seed_genres` and :code:`seed_tracks`.

            .. seealso::

                :meth:`~minim.api.spotify.WebAPIGenreEndpoints.get_available_seed_genres`
                — Get available seed genres.

        seed_tracks : str or Collection[str], optional
            (Comma-separated) list of Spotify IDs of seed tracks. Up to
            5 seed values may be provided in any combination of
            :code:`seed_artists`, :code:`seed_genres` and
            :code:`seed_tracks`.

            **Examples**: :code:`"11dFghVXANMlKmJXsNCbNl"`,
            :code:`"7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ"`,
            :code:`["7ouMYWpwJ422jRcDASZB7P", "4VqPOruhp5EdPBeR92t6lQ"]`.

        acousticness : float or tuple[float, ...], optional
            Confidence measure of whether a track is acoustic.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            **Valid range**: :code:`0.0` (electronic) to :code:`1.0`
            (acoustic).

            **Example**: :code:`0.00242`.

        danceability : float or tuple[float, ...], optional
            Suitability of a track for dancing based on a combination of
            musical elements, including tempo, rhythim stability, beat
            strength, and overall regularity.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            **Valid range**: :code:`0.0` (least danceable) to
            :code:`1.0` (most danceable).

            **Example**: :code:`0.585`.

        duration_ms : int or tuple[int, ...], optional
            Track duration in milliseconds.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            **Minimum value**: :code:`0`.

            **Example**: :code:`237_040`.

        energy : float or tuple[float, ...], optional
            Perceptual measure of a track's intensity and activity based
            on its dynamic range, perceived loudness, timbre, onset rate,
            and general entropy.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            **Valid range**: :code:`0.0` (e.g., Bach prelude) to
            :code:`1.0` (e.g., death metal).

            **Example**: :code:`0.842`.

        instrumentalness : float or tuple[float, ...], optional
            Confidence measure of whether a track contains no vocals.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            **Valid range**: :code:`0.0` (vocal) to :code:`1.0`
            (instrumental).

            **Example**: :code:`0.00686`.

        key : int or tuple[int, ...], optional
            Key a track is in using standard pitch class notation.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            .. container::

               **Valid values**:

               * :code:`-1` — No key detected.
               * :code:`0` — C.
               * :code:`1` — C♯ or D♭.
               * :code:`2` — D
               * :code:`3` — D♯ or E♭.
               * :code:`4` — E.
               * :code:`5` — F.
               * :code:`6` — F♯ or G♭.
               * :code:`7` — G.
               * :code:`8` — G♯ or A♭.
               * :code:`9` — A.
               * :code:`10` — A♯ or B♭.
               * :code:`11` — B.

        liveness : float or tuple[float, ...], optional
            Confidence measure of whether a track was performed live
            based on the presence of an audience in the recording.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            **Valid range**: :code:`0.0` (studio) to :code:`1.0` (live).

            **Example**: :code:`0.0866`.

        loudness : float or tuple[float, ...], optional
            Overall loudness of a track in decibels.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            **Maximum value**: :code:`0.0`.

            **Example**: :code:`-5.883`.

        mode : int or tuple[int, ...], optional
            Musical mode of a track.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            **Valid values**: :code:`0` for minor scale, :code:`1` for
            major scale.

        popularity : int or tuple[int, ...], optional
            Popularity of a track based on the total number of plays it
            has had and how recent those plays are.

            .. note::

               The popularity value is not updated in real time and may
               lag actual value by a few days.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            **Valid range**: :code:`0` (least popular) to :code:`100`
            (most popular).

        speechiness : float or tuple[float, ...], optional
            Confidence measure of whether a track contains spoken words.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            **Valid range**: :code:`0.0` (music) to :code:`1.0`
            (speech-like).

            **Example**: :code:`0.0556`.

        tempo : float or tuple[float, ...], optional
            Overall estimated tempo of a track in beats per minute.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            **Minimum value**: :code:`0.0`.

            **Example**: :code:`118.211`.

        time_signature : int or tuple[int, ...], optional
            Estimated time signature of the track.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            .. container::

               **Valid values**:

               * :code:`3` — 3/4.
               * :code:`4` — 4/4.
               * :code:`5` — 5/4.
               * :code:`6` — 6/4.
               * :code:`7` — 7/4.

        valence : float or tuple[float, ...], optional
            Confidence measure of the musical positiveness conveyed by a
            track.

            .. seealso::

               :ref:`track-attribute-hint` — How to specify minimum,
               maximum, and/or target values.

            **Valid range**: :code:`0.0` (e.g., happy, cheerful,
            euphoric) to :code:`1.0` (e.g., sad, depressed, angry).

            **Example**: :code:`0.428`.

        Returns
        -------
        recommendations : dict[str, Any]
            Spotify content metadata for the recommendations generated
            from the provided seeds and tuning parameters.

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
                              "type": <str>,
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
                          "type": <str>,
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
                            "type": <str>,
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
                        "type": <str>,
                        "uri": <str>
                      }
                    ]
                  }
        """
        params = {}
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit

        n_seeds = self._parse_seeds(
            "seed_tracks",
            seed_tracks,
            self._parse_seeds(
                "seed_genres",
                seed_genres,
                self._parse_seeds("seed_artists", seed_artists, 0, params),
                params,
            ),
            params,
        )
        if n_seeds == 0:
            raise ValueError("At least one seed must be provided.")
        if n_seeds > 5:
            raise ValueError("A maximum of 5 seeds is allowed.")

        local_variables = locals()
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
                attr, local_variables.get(attr), dtype, range_, params
            )

        return self._client._request(
            "GET", "recommendations", params=params
        ).json()

    @_copy_docstring(WebAPIUserEndpoints.get_my_top_tracks)
    def get_my_top_tracks(
        self,
        *,
        time_range: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_my_top_tracks(
            time_range=time_range, limit=limit, offset=offset
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
        request parameters for :meth:`get_recommendations`.

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
            Data type accepted for the track attribute.

            **Valid values**: :code:`int` or :code:`float`.

        range_ : tuple[int | float, int | float]
            Valid range for track attribute.

        params : dict[str, Any]
            Query parameters for the GET request.

            .. note::

               This `dict` is updated in-place.
        """
        if value is None:
            return

        is_int = data_type is int
        if isinstance(value, data_type):
            self._validate_number(attribute, value, data_type, *range_)
            params[f"target_{attribute}"] = value
        elif isinstance(value, Collection):
            if is_int and any(
                not (isinstance(v, int) or v is None) for v in value
            ):
                raise ValueError(
                    f"Values for track attribute {attribute!r} must "
                    "all be integers (or `None`)."
                )
            elif any(
                not (
                    isinstance(v, Number)
                    or isinstance(v, str)
                    and v.isnumeric()
                    or v is None
                )
                for v in value
            ):
                raise ValueError(
                    f"Values for track attribute {attribute!r} must "
                    "all be numbers (or `None`)."
                )
            length = len(value)
            if length not in range(2, 4):
                raise ValueError(
                    "The tuple provided for track attribute "
                    f"{attribute!r} has an invalid length ({length})."
                )
            else:
                for v in value:
                    self._validate_number(attribute, v, data_type, *range_)
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
                f"is not a `{(dtype := data_type.__name__)}` or a "
                f"tuple of `{dtype}`s."
            )

    def _parse_seeds(
        self,
        seed_type: str,
        seeds: str | Collection[str] | None,
        n_seeds: int,
        params: dict[str, Any],
    ) -> int:
        """
        Parse and add seeds to a dictionary holding the request
        parameters for :meth:`get_recommendations`.

        Parameters
        ----------
        seed_type : str
            Seed type.

            **Valid values**: :code:`"seed_artists"`,
            :code:`"seed_genres"`, :code:`"seed_tracks"`.

        seeds : str, Collection[str], or None
            Seed values.

        n_seeds : int
            Starting number of seed values.

        params : dict[str, Any]
            Query parameters for the GET request.

            .. note::

               This `dict` is updated in-place.

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
        self, seed_genres: str | Collection[str], /, limit: int
    ) -> tuple[str, int]:
        """ """
        if isinstance(seed_genres, str):
            split_genres = set(seed_genres.split(","))
            n_genres = len(split_genres)
            if n_genres > limit:
                raise ValueError(
                    f"A maximum of {limit} seed genres can be sent in "
                    "one request."
                )
            for genre in split_genres:
                self._client._validate_seed_genre(genre)
            return ",".join(sorted(split_genres)), n_genres

        seed_genres = set(seed_genres)
        n_genres = len(split_genres)
        if n_genres > limit:
            raise ValueError(
                f"A maximum of {limit} seed genres can be sent in one request."
            )
        for genre in seed_genres:
            self._client._validate_seed_genre(genre)
        return ",".join(sorted(seed_genres)), n_genres
