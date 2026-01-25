from functools import cached_property

from ..._shared import TTLCache
from ._shared import SpotifyResourceAPI


class GenresAPI(SpotifyResourceAPI):
    """
    Genres API endpoints for the Spotify Web API.

    .. note::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPIClient`
       and should not be instantiated directly.
    """

    @cached_property
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
        if "available_seed_genres" in self.__dict__:
            if seed_genre not in self.available_seed_genres:
                seed_genres_str = "', '".join(
                    sorted(self.available_seed_genres)
                )
                raise ValueError(
                    f"Invalid seed genre {seed_genre!r}. "
                    f"Valid values: '{seed_genres_str}'."
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
