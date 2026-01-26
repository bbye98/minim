from typing import Any

from ..._shared import TTLCache
from ._shared import DeezerResourceAPI


class ChartsAPI(DeezerResourceAPI):
    """
    Charts API endpoints for the Deezer API.

    .. important::

       This class is managed by :class:`minim.api.deezer.DeezerAPIClient` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="popularity")
    def get_top_albums(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        `Chart > Albums <https://developers.deezer.com/api/chart
        /albums>`_: Get Deezer catalog information for the top albums on
        Deezer.

        Parameters
        ----------
        limit : int or None; keyword-only; optional
            Maximum number of albums to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`10`.

        offset : int or None; keyword-only; optional
            Index of the first album to return. Use with `limit` to get
            the next batch of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        albums : dict[str, Any]
            Page of Deezer content metadata for the top albums.

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
                    "prev": <str>,
                    "next": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET", "chart", 0, "albums", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_top_artists(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        `Chart > Artists <https://developers.deezer.com/api/chart
        /artists>`_: Get Deezer catalog information for the top artists
        on Deezer.

        Parameters
        ----------
        limit : int or None; keyword-only; optional
            Maximum number of artists to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`10`.

        offset : int or None; keyword-only; optional
            Index of the first artist to return. Use with `limit` to get
            the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        artists : dict[str, Any]
            Page of Deezer content metadata for the top artists.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
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
                    "prev": <str>,
                    "next": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET", "chart", 0, "artists", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_top_playlists(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        `Chart > Playlists <https://developers.deezer.com/api/chart
        /playlists>`_: Get Deezer catalog information for the top
        playlists on Deezer.

        Parameters
        ----------
        limit : int or None; keyword-only; optional
            Maximum number of playlists to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`10`.

        offset : int or None; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of Deezer content metadata for the top playlists.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
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
                    "prev": <str>,
                    "next": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET", "chart", 0, "playlists", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_top_podcasts(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        `Chart > Podcasts <https://developers.deezer.com/api/chart
        /podcasts>`_: Get Deezer catalog information for the top
        podcasts on Deezer.

        Parameters
        ----------
        limit : int or None; keyword-only; optional
            Maximum number of podcasts to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`10`.

        offset : int or None; keyword-only; optional
            Index of the first podcast to return. Use with `limit` to
            get the next batch of podcasts.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        podcasts : dict[str, Any]
            Page of Deezer content metadata for the top podcasts.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
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
                        "title": <str>
                        "type": "podcast"
                      }
                    ],
                    "prev": <str>,
                    "next": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET", "chart", 0, "podcasts", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_top_radios(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        `Radio > Top <https://developers.deezer.com/api/radio/top>`_:
        Get Deezer catalog information for the top radios on Deezer.

        Parameters
        ----------
        limit : int or None; keyword-only; optional
            Maximum number of radios to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`25`.

        offset : int or None; keyword-only; optional
            Index of the first radio to return. Use with `limit` to get
            the next batch of radios.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        radios : dict[str, Any]
            Page of Deezer content metadata for the top radios.
        """
        params = {}
        if limit is not None:
            self._validate_number("limit", limit, int, 1)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["index"] = offset
        return self._client._request("GET", "radio/top", params=params)

    @TTLCache.cached_method(ttl="popularity")
    def get_top_tracks(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        `Chart > Tracks <https://developers.deezer.com/api/chart
        /tracks>`_: Get Deezer catalog information for the top
        tracks on Deezer.

        Parameters
        ----------
        limit : int or None; keyword-only; optional
            Maximum number of tracks to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`10`.

        offset : int or None; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of Deezer content metadata for the top tracks.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
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
                    "prev": <str>,
                    "next": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET", "chart", 0, "tracks", limit=limit, offset=offset
        )
