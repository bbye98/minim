from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPIMarketEndpoints:
    """
    Spotify Web API market endpoints.

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

    def get_available_markets(self) -> dict[str, list[str]]:
        """
        `Markets > Get Available Markets <https://developer.spotify.com
        /documentation/web-api/reference/get-available-markets>`_: Get
        markets where Spotify is available.

        Returns
        -------
        markets : dict[str, list[str]]
            Available markets.

            **Sample response**: :code:`{"markets": ["BR", "CA", "IT"]}`.
        """
        return self._client._request("GET", "markets").json()
