from typing import Any

from ..._shared import TTLCache
from ._shared import MusixmatchResourceAPI


class AlbumsAPI(MusixmatchResourceAPI):
    """
    Albums API endpoints for the Musixmatch Lyrics API.

    .. important::

       This class is managed by
       :class:`minim.api.musixmatch.MusixmatchLyricsAPIClient` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="popularity")
    def get_album(self, album_id: int | str, /) -> dict[str, Any]:
        """
        `Album > album.get <https://docs.musixmatch.com/lyrics-api/album
        /album-get>`_: Get Musixmatch catalog information for an album.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Basic plan
                    Access music metadata and static lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        Parameters
        ----------
        album_id : int or str; positional-only
            Musixmatch ID of the album.

            **Examples**: :code:`20828982`, :code:`"56126508"`.

        Returns
        -------
        album : dict[str, Any]
            Musixmatch content metadata for the album.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "album": {
                          "album_copyright": <str>,
                          "album_coverart_100x100": <str>,
                          "album_coverart_350x350": <str>,
                          "album_coverart_500x500": <str>,
                          "album_coverart_800x800": <str>,
                          "album_edit_url": <str>,
                          "album_id": <int>,
                          "album_label": <str>,
                          "album_mbid": <str>,
                          "album_name": <str>,
                          "album_pline": <str>,
                          "album_rating": <int>,
                          "album_release_date": <str>,
                          "album_release_type": <str>,
                          "album_track_count": <int>,
                          "album_vanity_id": <str>,
                          "artist_id": <int>,
                          "artist_name": <str>,
                          "external_ids": {
                            "7digital": <list[str]>,
                            "amazon_music": <list[str]>,
                            "itunes": <list[str]>,
                            "pro_pre_release": <list[str]>,
                            "spotify": <list[str]>
                          },
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
                      },
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._validate_numeric("album_id", album_id, int)
        return self._client._request(
            "GET", "album.get", params={"album_id": album_id}
        ).json()

    @TTLCache.cached_method(ttl="popularity")
    def get_album_tracks(
        self,
        album_id: int | str,
        /,
        *,
        has_lyrics: bool | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        `Album > album.tracks.get <https://docs.musixmatch.com
        /lyrics-api/album/album-tracks-get>`_: Get Musixmatch catalog
        information for the tracks in an album.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Basic plan
                    Access music metadata and static lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        Parameters
        ----------
        album_id : int or str; positional-only
            Musixmatch ID of the album.

            **Examples**: :code:`20828982`, :code:`"56126508"`.

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
            Page of Musixmatch content metadata for the tracks in the
            album.

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
                              "subtitle_id": <int>,
                              "track_edit_url": <str>,
                              "track_id": <int>,
                              "track_isrc": <str>,
                              "track_length": <int>,
                              "track_mbid": <str>,
                              "track_name": <str>,
                              "track_name_translation_list": [
                                {
                                  "track_name_translation": {
                                    "language": <str>,
                                    "translation": <str>
                                  }
                                }
                              ],
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
                        "available": <int>,
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._validate_numeric("album_id", album_id, int)
        params = {"album_id": album_id}
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
            "GET", "album.tracks.get", params=params
        ).json()
