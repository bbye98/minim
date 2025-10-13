from typing import TYPE_CHECKING

from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from .. import WebAPI


class MarketsAPI(ResourceAPI):
    """
    Markets API endpoints for the Spotify Web API.

    .. note::

       This class is managed by :class:`minim.api.spotify.WebAPI` and
       should not be instantiated directly.
    """

    _client: "WebAPI"

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
