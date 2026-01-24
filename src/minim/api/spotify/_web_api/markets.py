from functools import cached_property
from ..._shared import TTLCache
from ._shared import SpotifyResourceAPI


class MarketsAPI(SpotifyResourceAPI):
    """
    Markets API endpoints for the Spotify Web API.

    .. note::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPIClient`
       and should not be instantiated directly.
    """

    @cached_property
    def available_markets(self) -> set[str]:
        """
        Markets where Spotify is available.

        .. note::

           Accessing this property may call :meth:`get_markets` and make
           a request to the Spotify Web API.
        """
        return set(self.get_markets()["markets"])

    def _validate_market(self, market: str, /) -> None:
        """
        Validate market.

        Parameters
        ----------
        market : str; positional-only
            ISO 3166-1 alpha-2 country code.
        """
        self._validate_country_code(market)
        if "markets" in self.__dict__ and market not in self.available_markets:
            markets_str = "', '".join(self.available_markets)
            raise ValueError(
                f"{market!r} is not a market in which Spotify is "
                f"available. Valid values: '{markets_str}'."
            )

    @TTLCache.cached_method(ttl="static")
    def get_markets(self) -> dict[str, list[str]]:
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
