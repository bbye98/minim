import base64
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any
from urllib.parse import urlencode

from .._shared import APIClient
from ._lyrics_api.albums import AlbumsAPI
from ._lyrics_api.artists import ArtistsAPI
from ._lyrics_api.charts import ChartsAPI
from ._lyrics_api.matcher import MatcherAPI
from ._lyrics_api.search import SearchAPI
from ._lyrics_api.tracks import TracksAPI


import httpx


class MusixmatchLyricsAPIClient(APIClient):
    """
    Musixmatch Lyrics API client.
    """

    _ENV_VAR_PREFIX = "MUSIXMATCH_LYRICS_API"
    _PROVIDER = "Musixmatch"
    _QUAL_NAME = f"minim.api.{_PROVIDER.lower()}.{__qualname__}"
    BASE_URL = "https://www.musixmatch.com/ws/1.1"

    def __init__(
        self,
        *,
        api_key: bytes | str | None = None,
        enable_cache: bool = True,
        user_agent: str = "",
    ) -> None:
        """
        Parameters
        ----------
        api_key : bytes or str; keyword-only; optional
            API key. If not provided, a client key with Musixmatch Basic
            plan access is retrieved from the Musixmatch search page.

        enable_cache : bool; keyword-only; default: :code:`True`
            Whether to enable an in-memory time-to-live (TTL) cache with
            a least recently used (LRU) eviction policy for this client.
            If :code:`True`, responses from semi-static endpoints are
            cached for one minute to one day, depending on their
            expected update frequency.

            .. seealso::

               :meth:`clear_cache` – Clear specific or all cache entries
               for this client.

        user_agent : str; keyword-only; default: :code:`""`
            :code:`User-Agent` value to include in the headers of HTTP
            requests.
        """
        super().__init__(enable_cache=enable_cache, user_agent=user_agent)

        # Initialize subclasses for endpoint groups
        #: Albums API endpoints for the Musixmatch Lyrics API.
        self.albums: AlbumsAPI = AlbumsAPI(self)
        #: Artists API endpoints for the Musixmatch Lyrics API.
        self.artists: ArtistsAPI = ArtistsAPI(self)
        #: Charts API endpoints for the Musixmatch Lyrics API.
        self.charts: ChartsAPI = ChartsAPI(self)
        #: Matcher API endpoints for the Musixmatch Lyrics API.
        self.matcher: MatcherAPI = MatcherAPI(self)
        #: Search API endpoints for the Musixmatch Lyrics API.
        self.search: SearchAPI = SearchAPI(self)
        #: Tracks API endpoints for the Musixmatch Lyrics API.
        self.tracks: TracksAPI = TracksAPI(self)

        # Store API key
        self.set_api_key(api_key)

    def _request(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        params: dict[str, Any] | None = None,
        **kwargs: dict[str, Any],
    ) -> "httpx.Response":
        """
        Make an HTTP request to a Musixmatch Lyrics API endpoint.

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

        endpoint : str; positional-only
            Musixmatch Lyrics API endpoint.

        params : dict[str, Any]; keyword-only; optional
            Query parameters to include in the request. If not provided,
            an empty dictionary will be created.

            .. note::

               This `dict` is mutated in-place.

        **kwargs : dict[str, Any]
            Keyword parameters to pass to :meth:`httpx.Client.request`.

        Returns
        -------
        response : httpx.Response
            HTTP response.
        """
        if params is None:
            params = {}
        if self._api_key is None:
            params["app_id"] = "web-desktop-app-v1.0"
            params |= {
                "signature": base64.b64encode(
                    hmac.new(
                        self._client_key,
                        (
                            f"{self.BASE_URL}/{endpoint}?{urlencode(params)}"
                            f"{datetime.now(timezone.utc).strftime('%Y%m%d')}"
                        ).encode(),
                        hashlib.sha256,
                    ).digest()
                ).decode(),
                "signature_protocol": "sha256",
            }
        else:
            params["apikey"] = self._api_key

        resp = self._client.request(method, endpoint, params=params, **kwargs)
        status = resp.status_code
        reason = resp.reason_phrase
        try:
            resp_json = resp.json()
            status = resp_json["message"]["header"]["status_code"]
            reason = None
        except json.JSONDecodeError:
            resp_json = None
        if status == 200:
            return resp
        emsg = str(status)
        if reason:
            emsg += f" {reason}"
        if resp_json is not None and (
            hint := resp_json["message"]["header"].get("hint")
        ):
            emsg += f" – {hint}"
        raise RuntimeError(emsg)

    def _resolve_client_key(self) -> bytes:
        """
        Resolve the client key using the Musixmatch search page.

        Returns
        -------
        client_key : bytes
            Client key.
        """
        with httpx.Client() as client:
            m = re.search(
                r'http[^"]*/_app[^"]*\.js',
                client.get(
                    "https://www.musixmatch.com/search",
                    headers={
                        "User-Agent": self._client.headers.get(
                            "User-Agent", ""
                        )
                    },
                ).text,
            )
            if m is None:
                raise RuntimeError("'_app*.js' was not found.")
            app = client.get(
                m.group(0),
            ).text
            # https://s.mxmcdn.net/mxm-com/prod/1.37.3/_next/static/chunks/pages/_app-0e3826f6a28b74cf.js

        m = re.search(r'from\("(.*?)"', app)
        if m is None:
            raise RuntimeError("...")
        return base64.b64decode(m.group(1)[::-1])

    def set_api_key(self, api_key: bytes | str | None, /) -> None:
        """
        Set or update the API key.

        Parameters
        ----------
        api_key : str or None; positional-only
            API key.
        """
        if api_key is None:
            self._api_key = None
            if not hasattr(self, "_client_key"):
                self._client_key = self._resolve_client_key()
        elif isinstance(api_key, bytes):
            self._api_key = api_key
        elif isinstance(api_key, str):
            self._api_key = api_key.encode()
        else:
            raise TypeError("`api_key` must be a string.")
