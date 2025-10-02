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

    def get_available_seed_genres(self) -> list[str]:
        """
        `Genres > Get Available Seed Genre
        <https://developer.spotify.com/documentation/web-api/reference
        /get-recommendation-genres>`_: Get a list of available seed
        genres for track recommendations.

        Returns
        -------
        seed_genres : list[str]
            Seed genres.

            **Sample response**: :code:`["alternative", "samba"]`.
        """
        return self._client._request(
            "GET", "recommendations/available-genre-seeds"
        ).json()["genres"]
