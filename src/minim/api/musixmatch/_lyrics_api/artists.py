from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import MusixmatchResourceAPI
from .charts import ChartsAPI


class ArtistsAPI(MusixmatchResourceAPI):
    """
    Artists API endpoints for the Musixmatch Lyrics API.

    .. important::

       This class is managed by
       :class:`minim.api.musixmatch.MusixmatchLyricsAPIClient` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="static")
    def get_artist(self, artist_id: int | str, /) -> dict[str, Any]:
        """
        `Artist > artist.get <https://docs.musixmatch.com/lyrics-api
        /artist/artist-get>`_: Get Musixmatch catalog information for an
        artist.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Basic plan
                    Access music metadata and static lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        Parameters
        ----------
        artist_id : int or str; positional-only
            Musixmatch ID of the artist.

            **Examples**: :code:`259675`, :code:`"24403590"`.

        Returns
        -------
        artist : dict[str, Any]
            Musixmatch catalog information for the artist.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
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
                      },
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._validate_numeric("artist_id", artist_id, int)
        return self._client._request(
            "GET", "artist.get", params={"artist_id": artist_id}
        ).json()

    @TTLCache.cached_method(ttl="static")
    def get_artist_albums(
        self,
        artist_id: int | str,
        /,
        *,
        group_by_album_name: bool | None = None,
        release_date_sort_order: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        `Artist > artist.albums.get <https://docs.musixmatch.com
        /lyrics-api/artist/artist-albums-get>`_: Get Musixmatch catalog
        information for an artist's albums.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Basic plan
                    Access music metadata and static lyrics. `Learn more.
                    <https://about.musixmatch.com/api-pricing>`__

        Parameters
        ----------
        artist_id : int or str; positional-only
            Musixmatch ID of the artist.

            **Examples**: :code:`259675`, :code:`"24403590"`.

        group_by_album_name : bool; keyword-only; optional
            Whether to group the returned albums by their names.

        release_date_sort_order : str; keyword-only; optional
            Sort order for release date.

            **Valid values**: :code:`"asc"`, :code:`"desc"`.

        limit : int; keyword-only; optional
            Maximum number of albums to return.

            **Valid range**: :code:`1` to :code:`100`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of
            albums.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        Returns
        -------
        albums : dict[str, Any]
            Page of Musixmatch content metadata for the artist's albums.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "album_list": [
                          {
                            "album": {
                              "album_id": <int>,
                              "album_name": <str>,
                              "album_release_date": <str>,
                              "artist_id": <int>,
                              "artist_name": <str>,
                              "restricted": <int>,
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
        self._validate_numeric("artist_id", artist_id, int)
        params = {"artist_id": artist_id}
        if group_by_album_name is not None:
            self._validate_type(
                "group_by_album_name", group_by_album_name, bool
            )
            if group_by_album_name:
                params["g_album_name"] = 1
        if release_date_sort_order is not None:
            self._validate_sort_order(
                release_date_sort_order, sort_by="release date"
            )
            params["s_release_date"] = release_date_sort_order
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["page_size"] = limit
        if page is not None:
            self._validate_number("page", page, int, 1)
            params["page"] = page
        return self._client._request(
            "GET", "artist.albums.get", params=params
        ).json()

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
            params["q_artist"] = self._prepare_string(
                "artist_query", artist_query
            )
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

    @_copy_docstring(ChartsAPI.get_top_artists)
    def get_top_artists(
        self,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        return self._client.charts.get_top_artists(
            country_code=country_code, limit=limit, page=page
        )
