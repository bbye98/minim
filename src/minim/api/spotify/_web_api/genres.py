from typing import TYPE_CHECKING

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import SpotifyWebAPI


class GenresAPI(ResourceAPI):
    """
    Genres API endpoints for the Spotify Web API.

    .. note::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPI`
       and should not be instantiated directly.
    """

    _client: "SpotifyWebAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_available_seed_genres(self) -> dict[str, list[str]]:
        """
        `Genres > Get Available Genre Seeds
        <https://developer.spotify.com/documentation/web-api/reference
        /get-recommendation-genres>`_: Get available seed genres for
        track recommendations.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Required

              Extended quota mode before November 27, 2024
                  Access the
                  :code:`recommendations/available-genre-seeds`
                  endpoint. `Learn more. <https://developer.spotify.com
                  /blog/2024-11-27-changes-to-the-web-api>`__

        Returns
        -------
        seed_genres : dict[str, list[str]]
            Available seed genres.

            **Sample response**: :code:`{"genres": ["alternative", "samba"]}`.
        """
        return self._client._request(
            "GET", "recommendations/available-genre-seeds"
        ).json()
