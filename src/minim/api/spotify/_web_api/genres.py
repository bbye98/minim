from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPIGenreEndpoints:
    """
    Spotify Web API genre endpoints.

    .. note::

       This class is managed by :class:`minim.api.spotify.WebAPI` and
       should not be instantiated directly.
    """

    def __init__(self, client: "WebAPI", /) -> None:
        """
        Parameters
        ----------
        client : minim.api.spotify.WebAPI
            Minim's Spotify Web API client.
        """
        self._client = client

    def get_available_seed_genres(self) -> dict[str, list[str]]:
        """
        `Genres > Get Available Seed Genre
        <https://developer.spotify.com/documentation/web-api/reference
        /get-recommendation-genres>`_: Get available seed genres for
        track recommendations.

        .. admonition:: Third-party application mode
           :class: authorization-scope dropdown

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Returns
        -------
        seed_genres : dict[str, list[str]]
            Available seed genres.

            **Sample response**: :code:`{"genres": ["alternative", "samba"]}`.
        """
        return self._client._request(
            "GET", "recommendations/available-genre-seeds"
        ).json()
