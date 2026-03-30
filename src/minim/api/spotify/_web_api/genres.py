from __future__ import annotations

from ..._shared import TTLCache
from ._shared import SpotifyResourceAPI


class GenresAPI(SpotifyResourceAPI):
    """
    Genres API endpoints for the Spotify Web API.

    .. important::

       This class is managed by
       :class:`~minim.api.spotify.SpotifyWebAPIClient` and should not be
       instantiated directly.
    """

    __slots__ = ()

    @TTLCache.cached_property(ttl="static")
    def available_seed_genres(self) -> set[str]:
        """
        Available seed genres for track recommendations.

        .. admonition:: Third-party application mode
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Extended quota mode before November 27, 2024
                     Access the :code:`GET /recommendations
                     /available-genre-seeds` endpoint. `Learn more.
                     <https://developer.spotify.com/blog
                     /2024-11-27-changes-to-the-web-api>`__

        .. note::

           Accessing this property may call :meth:`get_seed_genres` and
           make a request to the Spotify Web API.
        """
        return set(self.get_seed_genres()["genres"])

    def _validate_seed_genre(self, seed_genre: str, /) -> None:
        """
        Validate seed genre.

        Parameters
        ----------
        seed_genre : str; positional-only
            Seed genre.
        """
        if (
            cache := self._client._cache
        ) and "available_seed_genres" in cache._store:
            if seed_genre not in self.available_seed_genres:
                raise ValueError(
                    f"Invalid seed genre {seed_genre!r}. Valid values: "
                    f"{self._join_values(self.available_seed_genres)}."
                )
        else:
            self._validate_type("seed_genre", seed_genre, str)

    @TTLCache.cached_method(ttl="static")
    def get_seed_genres(self) -> dict[str, list[str]]:
        """
        `Genres > Get Available Genre Seeds
        <https://developer.spotify.com/documentation/web-api/reference
        /get-recommendation-genres>`_: Get available seed genres for
        track recommendations.

        .. admonition:: Third-party application mode
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Extended quota mode before November 27, 2024
                     Access the :code:`recommendations
                     /available-genre-seeds` endpoint. `Learn more.
                     <https://developer.spotify.com/blog
                     /2024-11-27-changes-to-the-web-api>`__

        Returns
        -------
        seed_genres : dict[str, list[str]]
            Available seed genres.

            **Sample response**:
            :code:`{"genres": ["alternative", "samba"]}`.
        """
        return self._client._request(
            "GET", "recommendations/available-genre-seeds"
        ).json()
