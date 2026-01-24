import base64
from datetime import datetime, timezone
import hashlib
import hmac
import re
from typing import Any
from urllib.parse import urlencode

from .._shared import APIClient
from ._lyrics_api.tracks import TracksAPI


import httpx


class MusixmatchLyricsAPI(APIClient):
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
        """ """
        super().__init__(enable_cache=enable_cache, user_agent=user_agent)

        # Initialize subclasses for endpoint groups
        #: Tracks API endpoints for the Musixmatch Lyrics API.
        self.tracks: TracksAPI = TracksAPI(self)

        # Store API key
        if isinstance(api_key, str):
            self._api_key = api_key.encode()
        elif isinstance(api_key, bytes):
            self._api_key = api_key
        elif api_key is None:
            self._api_key = None
            self._resolve_client_key()
        else:
            raise TypeError("...")

    def _request(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        params: dict[str, Any] | None = None,
        **kwargs: dict[str, Any],
    ) -> "httpx.Response":
        """ """
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
                            f"{datetime.now().strftime('%Y%m%d')}"
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
        if 200 <= status < 300:
            return resp

        raise RuntimeError("...")

    def _resolve_client_key(self) -> None:
        """ """
        with httpx.Client() as client:
            m = re.search(
                r'http[^"]*/_app[^"]*\.js',
                client.get(
                    "https://www.musixmatch.com/search",
                    headers={"User-Agent": ""},
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
        self._client_key = base64.b64decode(m.group(1)[::-1])
