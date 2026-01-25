from typing import Any

from ..._shared import TTLCache
from ._shared import DeezerResourceAPI


class GenresAPI(DeezerResourceAPI):
    """
    Genres API endpoints for the Deezer API.

    .. note::

       This class is managed by :class:`minim.api.deezer.DeezerAPIClient` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="static")
    def get_genre(
        self, genre_id: int | str | None = None, /
    ) -> dict[str, Any]:
        """
        `Genre <https://developers.deezer.com/api/genre>`_: Get
        Deezer catalog information for a genre or all available genres.

        Parameters
        ----------
        genre_id : int or str; positional-only; optional
            Deezer ID of the genre. If not specified, all available
            genres are returned.

            **Examples**: :code:`0`, :code:`"2"`.

        Returns
        -------
        genre : dict[str, Any]
            Deezer content metadata for the genre(s).

            .. admonition:: Sample response
               :class: response dropdown

               .. tab-set::

                  .. tab-item:: Single genre

                     .. code::

                        {
                          "id": <int>,
                          "name": <str>,
                          "picture": <str>,
                          "picture_big": <str>,
                          "picture_medium": <str>,
                          "picture_small": <str>,
                          "picture_xl": <str>,
                          "type": "genre"
                        }

                  .. tab-item:: Available genres

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
                              "type": "genre"
                            }
                          ]
                        }
        """
        if genre_id is None:
            return self._client._request("GET", "genre").json()
        return self._request_resource_relationship("GET", "genre", genre_id)

    @TTLCache.cached_method(ttl="static")
    def get_genre_artists(self, genre_id: int | str = 0, /) -> dict[str, Any]:
        """
        `Genre > Artists <https://developers.deezer.com/api/genre
        /artists>`_: Get Deezer catalog information for artists
        primarily associated with a genre.

        Parameters
        ----------
        genre_id : int or str; positional-only; defualt: :code:`0`
            Deezer ID of the genre.

            **Examples**: :code:`0`, :code:`"2"`.

        Returns
        -------
        artists : dict[str, Any]
            Deezer content metadata for the genre's artists.

            .. admonition:: Sample response
               :class: response dropdown

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
                        "radio": <bool>,
                        "tracklist": <str>,
                        "type": "artist"
                      }
                    ]
                  }
        """
        return self._request_resource_relationship(
            "GET", "genre", genre_id, "artists"
        )

    @TTLCache.cached_method(ttl="static")
    def get_genre_podcasts(
        self,
        genre_id: int | str = 0,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Genre > Podcasts <https://developers.deezer.com/api/genre
        /podcasts>`_: Get Deezer catalog information for podcasts
        primarily associated with a genre.

        Parameters
        ----------
        genre_id : int or str; positional-only; default: :code:`0`
            Deezer ID of the genre.

            **Examples**: :code:`0`, :code:`"2"`.

        limit : int or None; keyword-only; optional
            Maximum number of podcasts to return.

            **Minimum value**: :code:`1`.

        offset : int or None; keyword-only; optional
            Index of the first podcast to return. Use with `limit` to
            get the next batch of podcasts.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        podcasts : dict[str, Any]
            Page of Deezer content metadata for the genre's podcasts.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "data": [],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET", "genre", genre_id, "podcasts", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="static")
    def get_genre_radios(self, genre_id: int | str = 0, /) -> dict[str, Any]:
        """
        `Genre > Radios <https://developers.deezer.com/api/genre
        /radios>`_: Get Deezer catalog information for a genre's radios.

        Parameters
        ----------
        genre_id : int or str; positional-only; default: :code:`0`
            Deezer ID of the genre.

            **Examples**: :code:`0`, :code:`"2"`.

        Returns
        -------
        radios : dict[str, Any]
            Deezer content metadata for the genre's radio.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <int>,
                        "md5_image": <str>,
                        "picture": <str>,
                        "picture_big": <str>,
                        "picture_medium": <str>,
                        "picture_small": <str>,
                        "picture_xl": <str>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "radio"
                      }
                    ]
                  }
        """
        return self._request_resource_relationship(
            "GET", "genre", genre_id, "radios"
        )
