from typing import Any

from ..._shared import TTLCache
from ._shared import DeezerResourceAPI


class EditorialAPI(DeezerResourceAPI):
    """
    Editorial API endpoints for the Deezer API.

    .. important::

       This class is managed by :class:`minim.api.deezer.DeezerAPIClient` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="static")
    def get_editorial(
        self,
        editorial_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Editorial <https://developers.deezer.com/api/editorial>`_: Get
        Deezer catalog information for an editorial or all available
        editorials.

        Parameters
        ----------
        editorial_id : int or str; positional-only; optional
            Deezer ID of the editorial. If not specified, all available
            editorials are returned.

            **Examples**: :code:`0`, :code:`"2"`.

        limit : int or None; keyword-only; optional
            Maximum number of editorials to return. Only applicable when
            `editorial_id` is :code:`None`.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first editorial to return. Use with `limit` to
            get the next batch of editorials. Only applicable when
            `editorial_id` is :code:`None`.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        editorial : dict[str, Any]
            Deezer content metadata for the editorial(s).

            .. admonition:: Sample response
               :class: response dropdown

               .. tab-set::

                  .. tab-item:: Single editorial

                     .. code::

                        {
                          "id": <int>,
                          "name": <str>,
                          "picture": <str>,
                          "picture_big": <str>,
                          "picture_medium": <str>,
                          "picture_small": <str>,
                          "picture_xl": <str>,
                          "type": "editorial"
                        }

                  .. tab-item:: Available editorials

                     .. code::

                        {
                          "data": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "picture_big": <str>,
                              "picture_medium": <str>,
                              "picture_small": <str>,
                              "picture_xl": <str>,
                              "type": "editorial"
                            }
                          ],
                          "prev": <str>,
                          "next": <str>,
                          "total": <int>
                        }
        """
        if editorial_id is None:
            return self._client._request("GET", "editorial").json()
        return self._request_resource_relationship(
            "GET", "editorial", editorial_id, limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="daily")
    def get_editorial_albums(
        self, editorial_id: int | str = 0, /
    ) -> dict[str, Any]:
        """
        `Editorial > Selection <https://developers.deezer.com/api
        /editorial/selection>`_: Get Deezer catalog information for
        albums selected weekly by the Deezer team.

        Parameters
        ----------
        editorial_id : int or str; positional-only; default: :code:`0`
            Deezer ID of the editorial.

            **Examples**: :code:`0`, :code:`"2"`.

        Returns
        -------
        albums : dict[str, Any]
            Deezer content metadata for the featured albums.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "data": [
                      {
                        "artist": {
                          "id": <int>,
                          "link": <str>,
                          "name": <str>,
                          "tracklist": <str>,
                          "type": "artist"
                        },
                        "cover": <str>,
                        "cover_big": <str>,
                        "cover_medium": <str>,
                        "cover_small": <str>,
                        "cover_xl": <str>,
                        "explicit_lyrics": <bool>,
                        "genre_id": <int>,
                        "id": <int>,
                        "md5_image": <str>,
                        "record_type": <str>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "album"
                      }
                    ]
                  }
        """
        return self._request_resource_relationship(
            "GET", "editorial", editorial_id, "selection"
        )

    @TTLCache.cached_method(ttl="daily")
    def get_editorial_charts(
        self,
        editorial_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Editorial > Charts <https://developers.deezer.com/api/editorial
        /charts>`_: Get Deezer catalog information for the top editorial
        albums, artists, playlists and tracks.

        Parameters
        ----------
        editorial_id : int or str; positional-only; default: :code:`0`
            Deezer ID of the editorial.

            **Examples**: :code:`0`, :code:`"2"`.

        limit : int or None; keyword-only; optional
            Maximum number of items to return per item type.

            **Minimum value**: :code:`1`.

            **API default**: :code:`10`.

        offset : int or None; keyword-only; optional
            Index of the first item to return per item type. Use with
            `limit` to get the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        charts : dict[str, Any]
            Page of Deezer content metadata for the top items.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "albums": {
                      "data": [
                        {
                          "artist": {
                            "id": <int>,
                            "link": <str>,
                            "name": <str>,
                            "picture": <str>,
                            "picture_big": <str>,
                            "picture_medium": <str>,
                            "picture_small": <str>,
                            "picture_xl": <str>,
                            "radio": <bool>,
                            "tracklist": <str>,
                            "type": "artist"
                          },
                          "cover": <str>,
                          "cover_big": <str>,
                          "cover_medium": <str>,
                          "cover_small": <str>,
                          "cover_xl": <str>,
                          "explicit_lyrics": <bool>,
                          "id": <int>,
                          "link": <str>,
                          "md5_image": <str>,
                          "position": <int>,
                          "record_type": <str>,
                          "title": <str>,
                          "tracklist": <str>,
                          "type": "album"
                        }
                      ],
                      "total": <int>
                    },
                    "artists": {
                      "data": [
                        {
                          "id": <int>,
                          "link": <str>,
                          "name": <str>,
                          "picture": <str>,
                          "picture_big": <str>,
                          "picture_medium": <str>,
                          "picture_small": <str>,
                          "picture_xl": <str>,
                          "position": <int>,
                          "radio": <bool>,
                          "tracklist": <str>,
                          "type": "artist"
                        }
                      ],
                      "total": <int>
                    },
                    "playlists": {
                      "data": [
                        {
                          "add_date": <str>,
                          "checksum": <str>,
                          "creation_date": <str>,
                          "id": <int>,
                          "link": <str>,
                          "md5_image": <str>,
                          "mod_date": <str>,
                          "nb_tracks": <int>,
                          "picture": <str>,
                          "picture_big": <str>,
                          "picture_medium": <str>,
                          "picture_small": <str>,
                          "picture_type": <str>,
                          "picture_xl": <str>,
                          "public": <bool>,
                          "title": <str>,
                          "tracklist": <str>,
                          "type": "playlist",
                          "user": {
                            "id": <int>,
                            "name": <str>,
                            "tracklist": <str>,
                            "type": "user"
                          }
                        }
                      ],
                      "total": <int>
                    },
                    "podcasts": {
                      "data": [
                        {
                          "available": <bool>,
                          "description": <str>,
                          "fans": <int>,
                          "id": <int>,
                          "link": <str>,
                          "picture": <str>,
                          "picture_big": <str>,
                          "picture_medium": <str>,
                          "picture_small": <str>,
                          "picture_xl": <str>,
                          "share": <str>,
                          "title": <str>,
                          "type": "podcast"
                        }
                      ],
                      "total": <int>
                    },
                    "tracks": {
                      "data": [
                        {
                          "album": {
                            "cover": <str>,
                            "cover_big": <str>,
                            "cover_medium": <str>,
                            "cover_small": <str>,
                            "cover_xl": <str>,
                            "id": <int>,
                            "md5_image": <str>,
                            "title": <str>,
                            "tracklist": <str>,
                            "type": "album"
                          },
                          "artist": {
                            "id": <int>,
                            "link": <str>,
                            "name": <str>,
                            "picture": <str>,
                            "picture_big": <str>,
                            "picture_medium": <str>,
                            "picture_small": <str>,
                            "picture_xl": <str>,
                            "radio": <bool>,
                            "tracklist": <str>,
                            "type": "artist"
                          },
                          "duration": <int>,
                          "explicit_content_cover": <int>,
                          "explicit_content_lyrics": <int>,
                          "explicit_lyrics": <bool>,
                          "id": <int>,
                          "link": <str>,
                          "md5_image": <str>,
                          "position": <int>,
                          "preview": <str>,
                          "rank": <int>,
                          "title": <str>,
                          "title_short": <str>,
                          "title_version": <str>,
                          "type": "track"
                        }
                      ],
                      "total": <int>
                    }
                  }
        """
        return self._request_resource_relationship(
            "GET",
            "editorial",
            editorial_id,
            "charts",
            limit=limit,
            offset=offset,
        )

    @TTLCache.cached_method(ttl="daily")
    def get_editorial_releases(
        self,
        editorial_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Editorial > Releases <https://developers.deezer.com/api
        /editorial/releases>`_: Get Deezer catalog information for
        new releases selected weekly by the Deezer team.

        Parameters
        ----------
        editorial_id : int or str; positional-only; default: :code:`0`
            Deezer ID of the editorial.

            **Examples**: :code:`0`, :code:`"2"`.

        limit : int or None; keyword-only; optional
            Maximum number of releases to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`20`.

        offset : int or None; keyword-only; optional
            Index of the first release to return. Use with `limit` to
            get the next batch of releases.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        albums : dict[str, Any]
            Deezer content metadata for the newly released albums.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "data": [
                      {
                        "artist": {
                          "id": <int>,
                          "name": <str>,
                          "tracklist": <str>,
                          "type": "artist"
                        },
                        "cover": <str>,
                        "cover_big": <str>,
                        "cover_medium": <str>,
                        "cover_small": <str>,
                        "cover_xl": <str>,
                        "id": <int>,
                        "md5_image": <str>,
                        "release_date": <str>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "album"
                      }
                    ],
                    "prev": <str>,
                    "next": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET",
            "editorial",
            editorial_id,
            "releases",
            limit=limit,
            offset=offset,
        )
