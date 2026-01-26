from functools import cached_property
from typing import Any

from ._shared import PrivateQobuzResourceAPI
from ..._shared import TTLCache


class PrivateGenresAPI(PrivateQobuzResourceAPI):
    """
    Genres API endpoints for the private Qobuz API.

    .. note::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPIClient`
       and should not be instantiated directly.
    """

    @cached_property
    def available_genres(self) -> dict[str, dict[str, Any]]:
        """
        Available genres.

        .. note::

           Accessing this property may call :meth:`get_genres` and make
           multiple requests to the Qobuz API.
        """
        genres = []

        # Use iterative depth-first search
        stack = [None]
        while stack:
            subgenres = self._client.genres.get_genres(stack.pop())["genres"]
            if subgenres["total"] > 0:
                genres.extend(subgenres["items"])
                stack.extend(genre["id"] for genre in subgenres["items"])

        # Use recursive depth-first search
        # def get_genres(
        #     genre_id: str | None = None, /, *, genres: list[dict[str, Any]]
        # ) -> dict[str, Any]:
        #     subgenres = self._client.genres.get_genres(genre_id)["genres"]
        #     if subgenres["total"] > 0:
        #         genres.extend(subgenres["items"])
        #         for subgenre in subgenres["items"]:
        #             get_genres(subgenre["id"], genres=genres)

        # get_genres(genres=genres)

        return {genre.pop("id"): genre for genre in genres}

    def _validate_genre_id(self, genre_id: int | str, /) -> None:
        """
        Validate genre ID.

        Parameters
        ----------
        genre_id : str; positional-only
            Genre ID.
        """
        try:
            genre_id = int(genre_id)
        except TypeError:
            raise TypeError(
                "Qobuz genre IDs must be integers or their string "
                "representations."
            )
        if "available_genres" in self.__dict__:
            genre_ids_str = "', '".join(sorted(self.available_genres.keys()))
            if genre_id not in self.available_genres:
                raise ValueError(
                    f"Invalid genre ID {genre_id!r}. "
                    f"Valid values: '{genre_ids_str}'."
                )

    @TTLCache.cached_method(ttl="static")
    def get_genre(self, genre_id: int | str, /) -> dict[str, Any]:
        """
        Get Qobuz catalog information for a genre.

        Parameters
        ----------
        genre_id : int or str; positional-only
            Qobuz ID of the genre.

            **Examples**: :code:`10`, :code:`"64"`.

        Returns
        -------
        genre : dict[str, Any]
            Qobuz content metadata for the genre.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "color": <str>,
                    "id": <int>,
                    "name": <str>,
                    "path": <list[int]>,
                    "slug": <str>
                  }
        """
        self._validate_qobuz_ids(genre_id, _recursive=False)
        return self._client._request(
            "GET", "genre/get", params={"genre_id": genre_id}
        ).json()

    @TTLCache.cached_method(ttl="static")
    def get_genres(
        self,
        genre_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for available top-level genres or
        the subgenres of a specific top-level genre.

        Parameters
        ----------
        genre_id : int or str; positional-only; optional
            Qobuz ID of the top-level genre. If not provided, all
            top-level genres are returned.

            **Examples**: :code:`10`, :code:`"64"`.

        limit : int; keyword-only; optional
            Maximum number of genres to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first genre to return. Use with `limit` to get
            the next batch of genres.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        genres : dict[str, Any]
            Page of Qobuz content metadata for the genres.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "genres": {
                      "items": [
                        {
                          "color": <str>,
                          "id": <int>,
                          "name": <str>,
                          "path": <list[int]>,
                          "slug": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "parent": {
                      "color": <str>,
                      "id": <int>,
                      "name": <str>,
                      "path": <list[int]>,
                      "slug": <str>
                    }
                  }
        """
        params = {}
        if genre_id is not None:
            self._validate_qobuz_ids(genre_id, _recursive=False)
            params["parent_id"] = genre_id
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request("GET", "genre/list", params=params).json()
