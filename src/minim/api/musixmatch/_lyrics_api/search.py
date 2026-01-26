from typing import Any

from ..._shared import TTLCache
from ._shared import MusixmatchResourceAPI


class SearchAPI(MusixmatchResourceAPI):
    """
    Search-related endpoints for the Musixmatch Lyrics API.

    .. note::

       This class groups search-related endpoints for convenience.
       Musixmatch does not provide a dedicated Search API.

    .. important::

       This class is managed by
       :class:`minim.api.musixmatch.MusixmatchLyricsAPIClient` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="search")
    def search_artists(
        self,
        artist_query: str | None = None,
        *,
        artist_id: int | str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        `Artist > artist.search <https://docs.musixmatch.com/lyrics-api
        /artist/artist-search>`_: Search for artists in the Musixmatch
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
        artist_query : str; optional
            Search query matching any word in the artist name.

        artist_id : int or str; keyword-only; optional
            Musixmatch ID of the artist to filter results by.

            **Examples**: :code:`259675`, :code:`"24403590"`.

        limit : int; keyword-only; optional
            Maximum number of artists to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of
            artists.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        Returns
        -------
        artists : dict[str, Any]
            Page of Musixmatch content metadata for the matching
            artists.

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
                                  "artist_alias": <str>,
                                }
                              ],
                              "artist_comment": <str>,
                              "artist_country": <str>,
                              "artist_credits": {
                                "artist_list": []
                              },
                              "artist_crowd_favourites": <int>,
                              "artist_edit_url": <str>,
                              "artist_facebook_url": <str>,
                              "artist_fq_id": <str>,
                              "artist_id": <int>,
                              "artist_instagram_url": <str>,
                              "artist_mbid": <str>,
                              "artist_merchandising_url": <str>,
                              "artist_name": <str>,
                              "artist_name_translation_list": [],
                              "artist_rating": <int>,
                              "artist_share_url": <str>,
                              "artist_tiktok_url": <str>,
                              "artist_tour_url": <str>,
                              "artist_twitter_url": <str>,
                              "artist_vanity_id": <str>,
                              "artist_website_url": <str>,
                              "artist_youtube_url": <str>,
                              "begin_date": <str>,
                              "begin_date_year": <str>,
                              "end_date": <str>,
                              "end_date_year": <str>,
                              "external_ids": {
                                "7digital": <list[str]>,
                                "amazon_music": <list[str]>,
                                "itunes": <list[str]>,
                                "pro_pre_release": <list[str]>,
                                "spotify": <list[str]>
                              },
                              "managed": <int>,
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
        if artist_query is not None:
            self._validate_type("artist_query", artist_query, str)
            params["q_artist"] = artist_query
        if artist_id is not None:
            self._validate_numeric("artist_id", artist_id, int)
            params["f_artist_id"] = artist_id
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["page_size"] = limit
        if page is not None:
            self._validate_number("page", page, int, 1)
            params["page"] = page
        return self._client._request(
            "GET", "artist.search", params=params
        ).json()

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
            self._validate_type("query", query, str)
            params["q"] = query
        if artist_query is not None:
            self._validate_type("artist_query", artist_query, str)
            params["q_artist"] = artist_query
        if lyrics_query is not None:
            self._validate_type("lyrics_query", lyrics_query, str)
            params["q_lyrics"] = lyrics_query
        if track_query is not None:
            self._validate_type("track_query", track_query, str)
            params["q_track"] = track_query
        if track_artist_query is not None:
            self._validate_type("track_artist_query", track_artist_query, str)
            params["q_track_artist"] = track_artist_query
        if writer_query is not None:
            self._validate_type("writer_query", writer_query, str)
            params["q_writer"] = writer_query
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
