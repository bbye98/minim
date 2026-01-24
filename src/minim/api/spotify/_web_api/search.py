from typing import Any

from ..._shared import TTLCache
from ._shared import SpotifyResourceAPI


class SearchAPI(SpotifyResourceAPI):
    """
    Search API endpoints for the Spotify Web API.

    .. note::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPI`
       and should not be instantiated directly.
    """

    _RESOURCE_TYPES = {
        "album",
        "artist",
        "audiobook",
        "episode",
        "playlist",
        "show",
        "track",
    }

    @TTLCache.cached_method(ttl="search")
    def search(
        self,
        query: str,
        /,
        item_types: str | list[str],
        *,
        external_content: str | None = None,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Search > Search for Item <https://developer.spotify.com
        /documentation/web-api/reference/search>`_: Get Spotify catalog
        information for albums, artists, playlists, tracks, shows,
        episodes, and/or audiobooks that match a keyword string.

        .. important::

           Audiobooks are only available in the US, UK, Canada, Ireland,
           New Zealand, and Australia markets.

        .. admonition:: Third-party application mode
           :class: entitlement dropdown

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        query : str, positional-only
            Search query.

            .. tip::

               Searches can be narrowed using field filters, such as
               :code:`album`, :code:`artist`, :code:`track`,
               :code:`year`, :code:`upc`, :code:`tag:hipster`,
               :code:`tag:new`, :code:`isrc`, and :code:`genre`. Each
               filter applies only to certain result types:

               * :code:`artist` and :code:`year` can be used when
                 searching albums, artists and tracks. The :code:`year`
                 filter accepts a year or a range (e.g.,
                 :code:`"year:1955-1960"`).

               * :code:`album` can be used when searching albums and
                 tracks.

               * :code:`genre` can be used when searching artists and
                 tracks.

               * :code:`isrc` and :code:`track` can be used when
                 searching tracks.

               * :code:`upc`, :code:`tag:new`, and :code:`tag:hipster`
                 can be used when searching albums. The :code:`tag:new`
                 filter returns albums released in the past two weeks,
                 and the :code:`tag:hipster` filter returns albums in
                 the lowest 10% popularity.

            **Example**:
            :code:`"remaster track:Doxy artist:Miles Davis"`.

        item_types : str or list[str]
            Types of items to return.

            **Valid values**: :code:`"album"`, :code:`"artist"`,
            :code:`"playlist"`, :code:`"track"`, :code:`"show"`,
            :code:`"episode"`, :code:`"audiobook"`.

            **Examples**: :code:`"artist"`, :code:`"track,episode"`,
            :code:`["album", "playlist"]`.

        external_content : str; keyword-only; optional
            Externally hosted content that the client can play.

            **Valid value**: :code:`"audio"`.

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
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next batch of items.

            **Valid range**: :code:`0` to :code:`1_000`.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        items : dict[str, Any]
            Page of Spotify content metadata for the matching items.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albums": {
                      "href": <str>,
                      "items": [
                        {
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
                        }
                      ],
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <int>,
                      "total": <int>
                    },
                    "artists": {
                      "href": <str>,
                      "items": [
                        {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "followers": {
                            "href": <str>,
                            "total": <int>
                          },
                          "genres": <list[str]>,
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
                          "popularity": <int>,
                          "type": "artist",
                          "uri": <str>
                        }
                      ],
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <int>,
                      "total": <int>
                    },
                    "audiobooks": {
                      "href": <str>,
                      "items": [
                        {
                          "authors": [
                            {
                              "name": <str>
                            }
                          ],
                          "copyrights": <list[str]>,
                          "description": <str>,
                          "edition": <str>,
                          "explicit": <bool>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "html_description": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "height": <int>,
                              "url": <str>,
                              "width": <int>
                            }
                          ],
                          "is_externally_hosted": <bool>,
                          "languages": <list[str]>,
                          "media_type": <str>,
                          "name": <str>,
                          "narrators": [
                            {
                              "name": <str>
                            }
                          ],
                          "publisher": <str>,
                          "total_chapters": <int>,
                          "type": "audiobook",
                          "uri": <str>
                        }
                      ],
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <int>,
                      "total": <int>
                    },
                    "episodes": {
                      "href": <str>,
                      "items": [
                        {
                          "audio_preview_url": <str>,
                          "description": <str>,
                          "duration_ms": <int>,
                          "explicit": <bool>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "html_description": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "height": <int>,
                              "url": <str>,
                              "width": <int>
                            }
                          ],
                          "is_externally_hosted": <bool>,
                          "is_playable": <bool>,
                          "language": <str>,
                          "languages": <list[str]>,
                          "name": <str>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "resume_point": {
                            "fully_played": <bool>,
                            "resume_position_ms": <int>
                          },
                          "type": "episode",
                          "uri": <str>
                        }
                      ],
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <int>,
                      "total": <int>
                    },
                    "playlists": {
                      "href": <str>,
                      "items": [
                        {
                          "collaborative": <bool>,
                          "description": <str>,
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
                          "owner": {
                            "display_name": <str>,
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "type": "user",
                            "uri": <str>
                          },
                          "primary_color": <str>,
                          "public": <bool>,
                          "snapshot_id": <str>,
                          "tracks": {
                            "href": <str>,
                            "total": <int>
                          },
                          "type": "playlist",
                          "uri": <str>
                        }
                      ],
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <int>,
                      "total": <int>
                    },
                    "shows": {
                      "href": <str>,
                      "items": [
                        {
                          "copyrights": <list[str]>,
                          "description": <str>,
                          "explicit": <bool>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "html_description": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "height": <int>,
                              "url": <str>,
                              "width": <int>
                            }
                          ],
                          "is_externally_hosted": <bool>,
                          "languages": <list[str]>,
                          "media_type": <str>,
                          "name": <str>,
                          "publisher": <str>,
                          "total_episodes": <int>,
                          "type": "show",
                          "uri": <str>
                        }
                      ],
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <int>,
                      "total": <int>
                    },
                    "tracks": {
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
                              "uri": <str>
                            }
                          ],
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
                      "previous": <int>,
                      "total": <int>
                    }
                  }
        """
        self._validate_type("query", query, str)
        query = query.strip()
        if not len(query):
            raise ValueError("No search query provided.")
        params = {
            "q": query,
            "type": self._prepare_types(
                item_types,
                allowed_types=self._RESOURCE_TYPES,
                type_prefix="item",
            ),
        }
        if external_content is not None:
            if external_content != "audio":
                raise ValueError(
                    f"Invalid external content {external_content!r}. "
                    "Valid value: 'audio'."
                )
            params["include_external"] = external_content
        if country_code is not None:
            self._client.markets._validate_market(country_code)
            params["market"] = country_code
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0, 1_000)
            params["offset"] = offset
        return self._client._request("GET", "search", params=params).json()
