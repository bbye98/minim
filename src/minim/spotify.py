"""
Spotify
=======
.. moduleauthor:: Benjamin Ye <GitHub: bbye98>

This module contains a complete implementation of all Spotify Web API
endpoints and a minimal implementation to use the private Spotify Lyrics
service.
"""

import base64
import datetime
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
from multiprocessing import Process
import os
import re
import secrets
import time
from typing import Any, Union
import urllib
import warnings
import webbrowser

import requests

from . import FOUND_FLASK, FOUND_PLAYWRIGHT, DIR_HOME, DIR_TEMP, _config

if FOUND_FLASK:
    from flask import Flask, request
if FOUND_PLAYWRIGHT:
    from playwright.sync_api import sync_playwright

__all__ = ["PrivateLyricsService", "WebAPI"]


class _SpotifyRedirectHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the Spotify authorization code flow.
    """

    def do_GET(self):
        """
        Handles an incoming GET request and parses the query string.
        """

        self.server.response = dict(
            urllib.parse.parse_qsl(urllib.parse.urlparse(f"{self.path}").query)
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        status = "denied" if "error" in self.server.response else "granted"
        self.wfile.write(f"Access {status}. You may close this page now.".encode())


class PrivateLyricsService:
    """
    Spotify Lyrics service client.

    The Spotify Lyrics service, which is powered by Musixmatch (or
    PetitLyrics in Japan), provides line- or word-synced lyrics for
    Spotify tracks when available. The Spotify Lyrics interface is not
    publicly documented, so its endpoints have been determined by
    watching HTTP network traffic.

    .. attention::

       As the Spotify Lyrics service is not designed to be publicly
       accessible, this class can be disabled or removed at any time to
       ensure compliance with the `Spotify Developer Terms of Service
       <https://developer.spotify.com/terms>`_.

    Requests to the Spotify Lyrics endpoints must be accompanied by a
    valid access token in the header. An access token can be obtained
    using the Spotify Web Player :code:`sp_dc` cookie, which must either
    be provided to this class's constructor as a keyword argument or be
    stored as :code:`SPOTIFY_SP_DC` in the operating system's
    environment variables.

    .. hint::

       The :code:`sp_dc` cookie can be extracted from the local storage
       of your web browser after you log into Spotify.

    If an existing access token is available, it and its expiry time can
    be provided to this class's constructor as keyword arguments to
    bypass the access token exchange process. It is recommended that all
    other authorization-related keyword arguments be specified so that
    a new access token can be obtained when the existing one expires.

    .. tip::

       The :code:`sp_dc` cookie and access token can be changed or
       updated at any time using :meth:`set_sp_dc` and
       :meth:`set_access_token`, respectively.

    Minim also stores and manages access tokens and their properties.
    When an access token is acquired, it is automatically saved to the
    Minim configuration file to be loaded on the next instantiation of
    this class. This behavior can be disabled if there are any security
    concerns, like if the computer being used is a shared device.

    Parameters
    ----------
    sp_dc : `str`, optional
        Spotify Web Player :code:`sp_dc` cookie. If it is not stored
        as :code:`SPOTIFY_SP_DC` in the operating system's environment
        variables or found in the Minim configuration file, it must be
        provided here.

    access_token : `str`, keyword-only, optional
        Access token. If provided here or found in the Minim
        configuration file, the authorization process is bypassed. In
        the former case, all other relevant keyword arguments should be
        specified to automatically refresh the access token when it
        expires.

    expiry : `datetime.datetime` or `str`, keyword-only, optional
        Expiry time of `access_token` in the ISO 8601 format
        :code:`%Y-%m-%dT%H:%M:%SZ`. If provided, the user will be
        reauthenticated when `access_token` expires.

    save : `bool`, keyword-only, default: :code:`True`
        Determines whether newly obtained access tokens and their
        associated properties are stored to the Minim configuration
        file.

    Attributes
    ----------
    LYRICS_URL : `str`
        Base URL for the Spotify Lyrics service.

    TOKEN_URL : `str`
        URL for the Spotify Web Player access token endpoint.

    session : `requests.Session`
        Session used to send requests to the Spotify Lyrics service.
    """

    _NAME = f"{__module__}.{__qualname__}"

    LYRICS_URL = "https://spclient.wg.spotify.com/color-lyrics/v2"
    TOKEN_URL = "https://open.spotify.com/get_access_token"

    def __init__(
        self,
        *,
        sp_dc: str = None,
        access_token: str = None,
        expiry: Union[datetime.datetime, str] = None,
        save: bool = True,
    ) -> None:
        """
        Create a Spotify Lyrics service client.
        """

        self.session = requests.Session()
        self.session.headers["App-Platform"] = "WebPlayer"

        if access_token is None and _config.has_section(self._NAME):
            sp_dc = _config.get(self._NAME, "sp_dc")
            access_token = _config.get(self._NAME, "access_token")
            expiry = _config.get(self._NAME, "expiry")

        self.set_sp_dc(sp_dc, save=save)
        self.set_access_token(access_token=access_token, expiry=expiry)

    def _get_json(self, url: str, **kwargs) -> dict:
        """
        Send a GET request and return the JSON-encoded content of the
        response.

        Parameters
        ----------
        url : `str`
            URL for the GET request.

        **kwargs
            Keyword arguments to pass to :meth:`requests.request`.

        Returns
        -------
        resp : `dict`
            JSON-encoded content of the response.
        """

        return self._request("get", url, **kwargs).json()

    def _request(
        self, method: str, url: str, retry: bool = True, **kwargs
    ) -> requests.Response:
        """
        Construct and send a request with status code checking.

        Parameters
        ----------
        method : `str`
            Method for the request.

        url : `str`
            URL for the request.

        retry : `bool`
            Specifies whether to retry the request if the response has
            a non-2xx status code.

        **kwargs
            Keyword arguments passed to :meth:`requests.request`.

        Returns
        -------
        resp : `requests.Response`
            Response to the request.
        """

        if self._expiry is not None and datetime.datetime.now() > self._expiry:
            self.set_access_token()

        r = self.session.request(method, url, **kwargs)
        if r.status_code != 200:
            emsg = f"{r.status_code} {r.reason}"
            if r.status_code == 401 and retry:
                logging.warning(emsg)
                self.set_access_token()
                return self._request(method, url, False, **kwargs)
            else:
                raise RuntimeError(emsg)
        return r

    def set_sp_dc(self, sp_dc: str = None, *, save: bool = True) -> None:
        """
        Set the Spotify Web Player :code:`sp_dc` cookie.

        Parameters
        ----------
        sp_dc : `str`, optional
            Spotify Web Player :code:`sp_dc` cookie.

        save : `bool`, keyword-only, default: :code:`True`
            Determines whether to save the newly obtained access tokens
            and their associated properties to the Minim configuration
            file.
        """

        self._sp_dc = sp_dc or os.environ.get("SPOTIFY_SP_DC")
        self._save = save

    def set_access_token(
        self, access_token: str = None, expiry: Union[datetime.datetime, str] = None
    ) -> None:
        """
        Set the Spotify Lyrics service access token.

        Parameters
        ----------
        access_token : `str`, optional
            Access token. If not provided, an access token is obtained
            from the Spotify Web Player using the :code:`sp_dc` cookie.

        expiry : `str` or `datetime.datetime`, keyword-only, optional
            Access token expiry timestamp in the ISO 8601 format
            :code:`%Y-%m-%dT%H:%M:%SZ`. If provided, the user will be
            reauthenticated (if `sp_dc` is found or provided) when the
            `access_token` expires.
        """

        if access_token is None:
            if not self._sp_dc:
                raise ValueError("Missing sp_dc cookie.")

            r = requests.get(
                self.TOKEN_URL,
                headers={"cookie": f"sp_dc={self._sp_dc}"},
                params={"reason": "transport", "productType": "web_player"},
            ).json()
            if r["isAnonymous"]:
                raise ValueError("Invalid sp_dc cookie.")
            access_token = r["accessToken"]
            expiry = datetime.datetime.fromtimestamp(
                r["accessTokenExpirationTimestampMs"] / 1000
            )

            if self._save:
                _config[self._NAME] = {
                    "sp_dc": self._sp_dc,
                    "access_token": access_token,
                    "expiry": expiry.strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
                with open(DIR_HOME / "minim.cfg", "w") as f:
                    _config.write(f)

        self.session.headers["Authorization"] = f"Bearer {access_token}"
        self._expiry = (
            datetime.datetime.strptime(expiry, "%Y-%m-%dT%H:%M:%SZ")
            if isinstance(expiry, str)
            else expiry
        )

    def get_lyrics(self, track_id: str) -> dict[str, Any]:
        """
        Get lyrics for a Spotify track.

        Parameters
        ----------
        track_id : `str`
            The Spotify ID for the track.

            **Example**: :code:`"0VjIjW4GlUZAMYd2vXMi3b"`.

        Returns
        -------
        lyrics : `dict`
            Formatted or time-synced lyrics.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "lyrics": {
                      "syncType": <str>,
                      "lines": [
                        {
                          "startTimeMs": <str>,
                          "words": <str>,
                          "syllables": [],
                          "endTimeMs": <str>
                        }
                      ],
                      "provider": <str>,
                      "providerLyricsId": <str>,
                      "providerDisplayName": <str>,
                      "syncLyricsUri": <str>,
                      "isDenseTypeface": <bool>,
                      "alternatives": [],
                      "language": <str>,
                      "isRtlLanguage": <bool>,
                      "fullscreenAction": <str>,
                      "showUpsell": <bool>
                    },
                    "colors": {
                      "background": <int>,
                      "text": <int>,
                      "highlightText": <int>
                    },
                    "hasVocalRemoval": <bool>
                  }
        """

        return self._get_json(
            f"{self.LYRICS_URL}/track/{track_id}",
            params={"format": "json", "market": "from_token"},
        )


class WebAPI:
    """
    Spotify Web API client.

    The Spotify Web API enables the creation of applications that can
    interact with Spotify's streaming service, such as retrieving
    content metadata, getting recommendations, creating and managing
    playlists, or controlling playback.

    .. important::

       * Spotify content may not be downloaded.
       * Keep visual content in its original form.
       * Ensure content attribution.

    .. seealso::

       For more information, see the `Spotify Web API Reference
       <https://developer.spotify.com/documentation/web-api>`_.

    Requests to the Spotify Web API endpoints must be accompanied by a
    valid access token in the header. An access token can be obtained
    with or without user authentication. While authentication is not
    necessary to search for and retrieve data from public content, it
    is required to access personal content and control playback.

    Minim can obtain client-only access tokens via the `client
    credentials <https://developer.spotify.com/documentation/general
    /guides/authorization/client-credentials/>`_ flow and user access
    tokens via the `authorization code <https://developer.spotify.com
    /documentation/web-api/tutorials/code-flow>`_ and `authorization
    code with proof key for code exchange (PKCE)
    <https://developer.spotify.com/documentation/web-api/tutorials/
    code-pkce-flow>`_ flows. These OAuth 2.0 authorization flows
    require valid client credentials (client ID and client secret) to
    either be provided to this class's constructor as keyword arguments
    or be stored as :code:`SPOTIFY_CLIENT_ID` and
    :code:`SPOTIFY_CLIENT_SECRET` in the operating system's environment
    variables.

    .. seealso::

       To get client credentials, see the `guide on how to create a new
       Spotify application <https://developer.spotify.com/documentation
       /general/guides/authorization/app-settings/>`_. To take advantage
       of Minim's automatic authorization code retrieval functionality
       for the authorization code (with PKCE) flow, the redirect URI
       should be in the form :code:`http://localhost:{port}/callback`,
       where :code:`{port}` is an open port on :code:`localhost`.

    Alternatively, a access token can be acquired without client
    credentials through the Spotify Web Player, but this approach is not
    recommended and should only be used as a last resort since it is not
    officially supported and can be deprecated by Spotify at any time.
    The access token is client-only unless a Spotify Web Player
    :code:`sp_dc` cookie is either provided to this class's constructor
    as a keyword argument or be stored as :code:`SPOTIFY_SP_DC` in the
    operating system's environment variables, in which case a user
    access token with all authorization scopes is granted instead.

    If an existing access token is available, it and its accompanying
    information (refresh token and expiry time) can be provided to this
    class's constructor as keyword arguments to bypass the access token
    retrieval process. It is recommended that all other
    authorization-related keyword arguments be specified so that a new
    access token can be obtained when the existing one expires.

    .. tip::

       The authorization flow and access token can be changed or updated
       at any time using :meth:`set_flow` and :meth:`set_access_token`,
       respectively.

    Minim also stores and manages access tokens and their properties.
    When any of the authorization flows above are used to acquire an
    access token, it is automatically saved to the Minim configuration
    file to be loaded on the next instantiation of this class. This
    behavior can be disabled if there are any security concerns, like if
    the computer being used is a shared device.

    Parameters
    ----------
    client_id : `str`, keyword-only, optional
        Client ID. Required for the authorization code and client
        credentials flows. If it is not stored as
        :code:`SPOTIFY_CLIENT_ID` in the operating system's environment
        variables or found in the Minim configuration file, it must be
        provided here.

    client_secret : `str`, keyword-only, optional
        Client secret. Required for the authorization code and client
        credentials flows. If it is not stored as
        :code:`SPOTIFY_CLIENT_SECRET` in the operating system's
        environment variables or found in the Minim configuration file,
        it must be provided here.

    flow : `str`, keyword-only, default: :code:`"web_player"`
        Authorization flow.

        .. container::

           **Valid values**:

           * :code:`"authorization_code"` for the authorization code
             flow.
           * :code:`"pkce"` for the authorization code with proof
             key for code exchange (PKCE) flow.
           * :code:`"client_credentials"` for the client credentials
             flow.
           * :code:`"web_player"` for a Spotify Web Player access
             token.

    browser : `bool`, keyword-only, default: :code:`False`
        Determines whether a web browser is automatically opened for the
        authorization code (with PKCE) flow. If :code:`False`, users
        will have to manually open the authorization URL. Not applicable
        when `web_framework="playwright"`.

    web_framework : `str`, keyword-only, optional
        Determines which web framework to use for the authorization code
        (with PKCE) flow.

        .. container::

           **Valid values**:

           * :code:`"http.server"` for the built-in implementation of
             HTTP servers.
           * :code:`"flask"` for the Flask framework.
           * :code:`"playwright"` for the Playwright framework by
             Microsoft.

    port : `int` or `str`, keyword-only, default: :code:`8888`
        Port on :code:`localhost` to use for the authorization code
        flow with the :code:`http.server` and Flask frameworks. Only
        used if `redirect_uri` is not specified.

    redirect_uri : `str`, keyword-only, optional
        Redirect URI for the authorization code flow. If not on
        :code:`localhost`, the automatic authorization code retrieval
        functionality is not available.

    scopes : `str` or `list`, keyword-only, optional
        Authorization scopes to request user access for in the
        authorization code flow.

        .. seealso::

           See :meth:`get_scopes` for the complete list of scopes.

    sp_dc : `str`, keyword-only, optional
        Spotify Web Player :code:`sp_dc` cookie to send with the access
        token request. If provided here, stored as :code:`SPOTIFY_SP_DC`
        in the operating system's environment variables, or found in the
        Minim configuration file, a user access token with all
        authorization scopes is obtained instead of a client-only access
        token.

    access_token : `str`, keyword-only, optional
        Access token. If provided here or found in the Minim
        configuration file, the authorization process is bypassed. In
        the former case, all other relevant keyword arguments should be
        specified to automatically refresh the access token when it
        expires.

    refresh_token : `str`, keyword-only, optional
        Refresh token accompanying `access_token`. If not provided,
        the user will be reauthenticated using the specified
        authorization flow when `access_token` expires.

    expiry : `datetime.datetime` or `str`, keyword-only, optional
        Expiry time of `access_token` in the ISO 8601 format
        :code:`%Y-%m-%dT%H:%M:%SZ`. If provided, the user will be
        reauthenticated using `refresh_token` (if available) or the
        specified authorization flow (if possible) when `access_token`
        expires.

    overwrite : `bool`, keyword-only, default: :code:`False`
        Determines whether to overwrite an existing access token in the
        Minim configuration file.

    save : `bool`, keyword-only, default: :code:`True`
        Determines whether newly obtained access tokens and their
        associated properties are stored to the Minim configuration
        file.

    Attributes
    ----------
    API_URL : `str`
        Base URL for the Spotify Web API.

    AUTH_URL : `str`
        URL for Spotify Web API authorization code requests.

    TOKEN_URL : `str`
        URL for Spotify Web API access token requests.

    WEB_PLAYER_TOKEN_URL : `str`
        URL for Spotify Web Player access token requests.

    session : `requests.Session`
        Session used to send requests to the Spotify Web API.
    """

    _FLOWS = {"authorization_code", "pkce", "client_credentials", "web_player"}
    _NAME = f"{__module__}.{__qualname__}"

    API_URL = "https://api.spotify.com/v1"
    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    WEB_PLAYER_TOKEN_URL = "https://open.spotify.com/get_access_token"

    @classmethod
    def get_scopes(self, categories: Union[str, list[str]]) -> str:
        """
        Get Spotify Web API and Open Access authorization scopes for
        the specified categories.

        Parameters
        ----------
        categories : `str` or `list`
            Categories of authorization scopes to get.

            .. container::

               **Valid values**:

               * :code:`"images"` for scopes related to custom images,
                 such as :code:`ugc-image-upload`.
               * :code:`"spotify_connect"` for scopes related to Spotify
                 Connect, such as

                 * :code:`user-read-playback-state`,
                 * :code:`user-modify-playback-state`, and
                 * :code:`user-read-currently-playing`.

               * :code:`"playback"` for scopes related to playback
                 control, such as :code:`app-remote-control` and
                 :code:`streaming`.
               * :code:`"playlists"` for scopes related to playlists,
                 such as

                 * :code:`playlist-read-private`,
                 * :code:`playlist-read-collaborative`,
                 * :code:`playlist-modify-private`, and
                 * :code:`playlist-modify-public`.

               * :code:`"follow"` for scopes related to followed artists
                 and users, such as :code:`user-follow-modify` and
                 :code:`user-follow-read`.
               * :code:`"listening_history"` for scopes related to
                 playback history, such as

                 * :code:`user-read-playback-position`,
                 * :code:`user-top-read`, and
                 * :code:`user-read-recently-played`.

               * :code:`"library"` for scopes related to saved content,
                 such as :code:`user-library-modify` and
                 :code:`user-library-read`.
               * :code:`"users"` for scopes related to user information,
                 such as :code:`user-read-email` and
                 :code:`user-read-private`.
               * :code:`"all"` for all scopes above.
               * A substring to match in the possible scopes, such as

                 * :code:`"read"` for all scopes above that grant read
                   access, i.e., scopes with :code:`read` in the name,
                 * :code:`"modify"` for all scopes above that grant
                   modify access, i.e., scopes with :code:`modify` in
                   the name, or
                 * :code:`"user"` for all scopes above that grant access
                   to all user-related information, i.e., scopes with
                   :code:`user` in the name.

            .. seealso::

               For the endpoints that the scopes allow access to, see the
               `Scopes page of the Spotify Web API Reference
               <https://developer.spotify.com/documentation/web-api
               /concepts/scopes>`_.
        """

        SCOPES = {
            "images": ["ugc-image-upload"],
            "spotify_connect": [
                "user-read-playback-state",
                "user-modify-playback-state",
                "user-read-currently-playing",
            ],
            "playback": ["app-remote-control streaming"],
            "playlists": [
                "playlist-read-private",
                "playlist-read-collaborative",
                "playlist-modify-private",
                "playlist-modify-public",
            ],
            "follow": ["user-follow-modify", "user-follow-read"],
            "listening_history": [
                "user-read-playback-position",
                "user-top-read",
                "user-read-recently-played",
            ],
            "library": ["user-library-modify", "user-library-read"],
            "users": ["user-read-email", "user-read-private"],
        }

        if isinstance(categories, str):
            if categories in SCOPES.keys():
                return SCOPES[categories]
            if categories == "all":
                return " ".join(s for scopes in SCOPES.values() for s in scopes)
            return " ".join(
                s for scopes in SCOPES.values() for s in scopes if categories in s
            )

        return " ".join(
            s for scopes in (self.get_scopes[c] for c in categories) for s in scopes
        )

    def __init__(
        self,
        *,
        client_id: str = None,
        client_secret: str = None,
        flow: str = "web_player",
        browser: bool = False,
        web_framework: str = None,
        port: Union[int, str] = 8888,
        redirect_uri: str = None,
        scopes: Union[str, list[str]] = "",
        sp_dc: str = None,
        access_token: str = None,
        refresh_token: str = None,
        expiry: Union[datetime.datetime, str] = None,
        overwrite: bool = False,
        save: bool = True,
    ) -> None:
        """
        Create a Spotify Web API client.
        """

        self.session = requests.Session()

        if access_token is None and _config.has_section(self._NAME) and not overwrite:
            flow = _config.get(self._NAME, "flow")
            access_token = _config.get(self._NAME, "access_token")
            refresh_token = _config.get(self._NAME, "refresh_token", fallback=None)
            expiry = _config.get(self._NAME, "expiry", fallback=None)
            client_id = _config.get(self._NAME, "client_id")
            client_secret = _config.get(self._NAME, "client_secret", fallback=None)
            redirect_uri = _config.get(self._NAME, "redirect_uri", fallback=None)
            scopes = _config.get(self._NAME, "scopes")
            sp_dc = _config.get(self._NAME, "sp_dc", fallback=None)

        self.set_flow(
            flow,
            client_id=client_id,
            client_secret=client_secret,
            browser=browser,
            web_framework=web_framework,
            port=port,
            redirect_uri=redirect_uri,
            scopes=scopes,
            sp_dc=sp_dc,
            save=save,
        )
        self.set_access_token(access_token, refresh_token=refresh_token, expiry=expiry)

    def _check_scope(self, endpoint: str, scope: str) -> None:
        """
        Check if the user has granted the appropriate authorization
        scope for the desired endpoint.

        Parameters
        ----------
        endpoint : `str`
            Spotify Web API endpoint.

        scope : `str`
            Required scope for `endpoint`.
        """

        if scope not in self._scopes:
            emsg = (
                f"{self._NAME}.{endpoint}() requires the '{scope}' "
                "authorization scope."
            )
            raise RuntimeError(emsg)

    def _get_authorization_code(self, code_challenge: str = None) -> str:
        """
        Get an authorization code to be exchanged for an access token in
        the authorization code flow.

        Parameters
        ----------
        code_challenge : `str`, optional
            Code challenge for the authorization code with PKCE flow.

        Returns
        -------
        auth_code : `str`
            Authorization code.
        """

        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "response_type": "code",
            "state": secrets.token_urlsafe(),
        }
        if self._scopes:
            params["scope"] = self._scopes
        if code_challenge is not None:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        auth_url = f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

        if self._web_framework == "playwright":
            har_file = DIR_TEMP / "minim_spotify.har"

            with sync_playwright() as playwright:
                browser = playwright.firefox.launch(headless=False)
                context = browser.new_context(record_har_path=har_file)
                page = context.new_page()
                page.goto(auth_url, timeout=0)
                with page.expect_request(
                    "https://accounts.spotify.com/*/authorize/accept*"
                ) as _:
                    pass  # blocking call
                context.close()
                browser.close()

            with open(har_file, "r") as f:
                queries = dict(
                    urllib.parse.parse_qsl(
                        urllib.parse.urlparse(
                            re.search(rf'{self._redirect_uri}\?(.*?)"', f.read()).group(
                                0
                            )
                        ).query
                    )
                )
            har_file.unlink()

        else:
            if self._browser:
                webbrowser.open(auth_url)
            else:
                print(
                    "To grant Minim access to Spotify data and "
                    "features, open the following link in your web "
                    f"browser:\n\n{auth_url}\n"
                )

            if self._web_framework == "http.server":
                httpd = HTTPServer(("", self._port), _SpotifyRedirectHandler)
                httpd.handle_request()
                queries = httpd.response

            elif self._web_framework == "flask":
                app = Flask(__name__)
                json_file = DIR_TEMP / "minim_spotify.json"

                @app.route("/callback", methods=["GET"])
                def _callback() -> str:
                    if "error" in request.args:
                        return "Access denied. You may close this page now."
                    with open(json_file, "w") as f:
                        json.dump(request.args, f)
                    return "Access granted. You may close this page now."

                server = Process(target=app.run, args=("0.0.0.0", self._port))
                server.start()
                while not json_file.is_file():
                    time.sleep(0.1)
                server.terminate()

                with open(json_file, "rb") as f:
                    queries = json.load(f)
                json_file.unlink()

            else:
                uri = input(
                    "After authorizing Minim to access Spotify on "
                    "your behalf, copy and paste the URI beginning "
                    f"with '{self._redirect_uri}' below.\n\nURI: "
                )
                queries = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(uri).query))

        if "error" in queries:
            raise RuntimeError(f"Authorization failed. Error: {queries['error']}")
        if params["state"] != queries["state"]:
            raise RuntimeError("Authorization failed due to state mismatch.")
        return queries["code"]

    def _get_json(self, url: str, **kwargs) -> dict:
        """
        Send a GET request and return the JSON-encoded content of the
        response.

        Parameters
        ----------
        url : `str`
            URL for the GET request.

        **kwargs
            Keyword arguments to pass to :meth:`requests.request`.

        Returns
        -------
        resp : `dict`
            JSON-encoded content of the response.
        """

        return self._request("get", url, **kwargs).json()

    def _refresh_access_token(self) -> None:
        """
        Refresh the expired excess token.
        """

        if (
            self._flow == "web_player"
            or not self._refresh_token
            or not self._client_id
            or not self._client_secret
        ):
            self.set_access_token()
        else:
            client_b64 = base64.urlsafe_b64encode(
                f"{self._client_id}:{self._client_secret}".encode()
            ).decode()
            r = requests.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self._refresh_token,
                },
                headers={"Authorization": f"Basic {client_b64}"},
            ).json()

            self.session.headers["Authorization"] = f"Bearer {r['access_token']}"
            self._refresh_token = r["refresh_token"]
            self._expiry = datetime.datetime.now() + datetime.timedelta(
                0, r["expires_in"]
            )
            self._scopes = r["scope"]

            if self._save:
                _config[self._NAME].update(
                    {
                        "access_token": r["access_token"],
                        "refresh_token": self._refresh_token,
                        "expiry": self._expiry.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "scopes": self._scopes,
                    }
                )
                with open(DIR_HOME / "minim.cfg", "w") as f:
                    _config.write(f)

    def _request(
        self, method: str, url: str, retry: bool = True, **kwargs
    ) -> requests.Response:
        """
        Construct and send a request with status code checking.

        Parameters
        ----------
        method : `str`
            Method for the request.

        url : `str`
            URL for the request.

        retry : `bool`
            Specifies whether to retry the request if the response has
            a non-2xx status code.

        **kwargs
            Keyword arguments passed to :meth:`requests.request`.

        Returns
        -------
        resp : `requests.Response`
            Response to the request.
        """

        if self._expiry is not None and datetime.datetime.now() > self._expiry:
            self._refresh_access_token()

        r = self.session.request(method, url, **kwargs)
        if r.status_code not in range(200, 299):
            error = r.json()["error"]
            emsg = f"{error['status']}"
            if "message" in error:
                emsg += f" {error['message']}"
            if r.status_code == 401 and retry:
                logging.warning(emsg)
                self._refresh_access_token()
                return self._request(method, url, False, **kwargs)
            else:
                raise RuntimeError(emsg)
        return r

    def set_access_token(
        self,
        access_token: str = None,
        *,
        refresh_token: str = None,
        expiry: Union[str, datetime.datetime] = None,
    ) -> None:
        """
        Set the Spotify Web API access token.

        Parameters
        ----------
        access_token : `str`, optional
            Access token. If not provided, an access token is obtained
            using an OAuth 2.0 authorization flow or from the Spotify
            Web Player.

        refresh_token : `str`, keyword-only, optional
            Refresh token accompanying `access_token`.

        expiry : `str` or `datetime.datetime`, keyword-only, optional
            Access token expiry timestamp in the ISO 8601 format
            :code:`%Y-%m-%dT%H:%M:%SZ`. If provided, the user will be
            reauthenticated using the refresh token (if available) or
            the default authorization flow (if possible) when
            `access_token` expires.
        """

        if access_token is None:
            if self._flow == "web_player":
                headers = {"cookie": f"sp_dc={self._sp_dc}"} if self._sp_dc else {}
                r = requests.get(self.WEB_PLAYER_TOKEN_URL, headers=headers).json()
                self._client_id = r["clientId"]
                access_token = r["accessToken"]
                expiry = datetime.datetime.fromtimestamp(
                    r["accessTokenExpirationTimestampMs"] / 1000
                )
                if self._sp_dc and r["isAnonymous"]:
                    wmsg = (
                        "The sp_dc cookie is invalid, so the "
                        "access token granted is client-only."
                    )
                    warnings.warn(wmsg)
            else:
                if not self._client_id or not self._client_secret:
                    emsg = "Spotify Web API client credentials not provided."
                    raise ValueError(emsg)

                if self._flow == "client_credentials":
                    r = requests.post(
                        self.TOKEN_URL,
                        data={
                            "client_id": self._client_id,
                            "client_secret": self._client_secret,
                            "grant_type": "client_credentials",
                        },
                    ).json()
                else:
                    client_b64 = base64.urlsafe_b64encode(
                        f"{self._client_id}:{self._client_secret}".encode()
                    ).decode()
                    data = {
                        "grant_type": "authorization_code",
                        "redirect_uri": self._redirect_uri,
                    }
                    if self._flow == "pkce":
                        data["client_id"] = self._client_id
                        data["code_verifier"] = secrets.token_urlsafe(96)
                        data["code"] = self._get_authorization_code(
                            base64.urlsafe_b64encode(
                                hashlib.sha256(data["code_verifier"].encode()).digest()
                            )
                            .decode()
                            .replace("=", "")
                        )
                    else:
                        data["code"] = self._get_authorization_code()
                    r = requests.post(
                        self.TOKEN_URL,
                        data=data,
                        headers={"Authorization": f"Basic {client_b64}"},
                    ).json()
                    refresh_token = r["refresh_token"]
                access_token = r["access_token"]
                expiry = datetime.datetime.now() + datetime.timedelta(
                    0, r["expires_in"]
                )

            if self._save:
                _config[self._NAME] = {
                    "flow": self._flow,
                    "client_id": self._client_id,
                    "access_token": access_token,
                    "expiry": expiry.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "scopes": self._scopes,
                }
                if refresh_token:
                    _config[self._NAME]["refresh_token"] = refresh_token
                for attr in ("client_secret", "redirect_uri", "sp_dc"):
                    if hasattr(self, f"_{attr}"):
                        _config[self._NAME][attr] = getattr(self, f"_{attr}") or ""
                with open(DIR_HOME / "minim.cfg", "w") as f:
                    _config.write(f)

        self.session.headers["Authorization"] = f"Bearer {access_token}"
        self._refresh_token = refresh_token
        self._expiry = (
            datetime.datetime.strptime(expiry, "%Y-%m-%dT%H:%M:%SZ")
            if isinstance(expiry, str)
            else expiry
        )

        if self._flow in {"authorization_code", "pkce"} or (
            self._flow == "web_player" and self._sp_dc
        ):
            self._user_id = self.get_profile()["id"]

    def set_flow(
        self,
        flow: str,
        *,
        client_id: str = None,
        client_secret: str = None,
        browser: bool = False,
        web_framework: str = None,
        port: Union[int, str] = 8888,
        redirect_uri: str = None,
        scopes: Union[str, list[str]] = "",
        sp_dc: str = None,
        save: bool = True,
    ) -> None:
        """
        Set the authorization flow.

        Parameters
        ----------
        flow : `str`
            Authorization flow.

            .. container::

               **Valid values**:

               * :code:`"authorization_code"` for the authorization code
                 flow.
               * :code:`"pkce"` for the authorization code with proof
                 key for code exchange (PKCE) flow.
               * :code:`"client_credentials"` for the client credentials
                 flow.
               * :code:`"web_player"` for a Spotify Web Player access
                 token.

        client_id : `str`, keyword-only, optional
            Client ID. Required for all OAuth 2.0 authorization flows.

        client_secret : `str`, keyword-only, optional
            Client secret. Required for all OAuth 2.0 authorization
            flows.

        browser : `bool`, keyword-only, default: :code:`False`
            Determines whether a web browser is automatically opened for
            the authorization code (with PKCE) flow. If :code:`False`,
            users will have to manually open the authorization URL.
            Not applicable when `web_framework="playwright"`.

        web_framework : `str`, keyword-only, optional
            Web framework used to automatically complete the
            authorization code (with PKCE) flow.

            .. container::

               **Valid values**:

               * :code:`"http.server"` for the built-in implementation of
                 HTTP servers.
               * :code:`"flask"` for the Flask framework.
               * :code:`"playwright"` for the Playwright framework.

        port : `int` or `str`, keyword-only, default: :code:`8888`
            Port on :code:`localhost` to use for the authorization code
            flow with the :code:`http.server` and Flask frameworks.

        redirect_uri : `str`, keyword-only, optional
            Redirect URI for the authorization code flow. If not
            specified, an open port on :code:`localhost` will be used.

        scopes : `str` or `list`, keyword-only, optional
            Authorization scopes to request access to in the
            authorization code flow.

        sp_dc : `str`, keyword-only, optional
            Spotify Web Player :code:`sp_dc` cookie.

        save : `bool`, keyword-only, default: :code:`True`
            Determines whether to save the newly obtained access tokens
            and their associated properties to the Minim configuration
            file.
        """

        if flow not in self._FLOWS:
            emsg = (
                f"Invalid authorization flow ({flow=}). "
                f"Valid values: {', '.join(self._FLOWS)}."
            )
            raise ValueError(emsg)
        self._flow = flow
        self._save = save

        if flow == "web_player":
            self._sp_dc = sp_dc or os.environ.get("SPOTIFY_SP_DC")
            self._scopes = self.get_scopes("all") if self._sp_dc else ""
        else:
            self._client_id = client_id or os.environ.get("SPOTIFY_CLIENT_ID")
            self._client_secret = client_secret or os.environ.get(
                "SPOTIFY_CLIENT_SECRET"
            )
            if flow in {"authorization_code", "pkce"}:
                self._browser = browser
                self._scopes = " ".join(scopes) if isinstance(scopes, list) else scopes

                if redirect_uri:
                    self._redirect_uri = redirect_uri
                    if "localhost" in redirect_uri:
                        self._port = re.search(r"localhost:(\d+)", redirect_uri).group(
                            1
                        )
                    elif web_framework:
                        wmsg = (
                            "The redirect URI is not on localhost, "
                            "so automatic authorization code "
                            "retrieval is not available."
                        )
                        logging.warning(wmsg)
                        web_framework = None
                elif port:
                    self._port = port
                    self._redirect_uri = f"http://localhost:{port}/callback"
                else:
                    self._port = self._redirect_uri = None

                self._web_framework = (
                    web_framework
                    if web_framework in {None, "http.server"}
                    or globals()[f"FOUND_{web_framework.upper()}"]
                    else None
                )
                if self._web_framework is None and web_framework:
                    wmsg = (
                        f"The {web_framework.capitalize()} web "
                        "framework was not found, so automatic "
                        "authorization code retrieval is not "
                        "available."
                    )
                    warnings.warn(wmsg)

            elif flow == "client_credentials":
                self._scopes = ""

    ### ALBUMS ################################################################

    def get_album(self, id: str, *, market: str = None) -> dict:
        """
        `Albums > Get Album <https://developer.spotify.com/
        documentation/web-api/reference/get-an-album>`_:
        Get Spotify catalog information for a single album.

        Parameters
        ----------
        id : `str`
            The Spotify ID of the album.

            **Example**: :code:`"4aawyAB9vmqN3uQ7FjRGTy"`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        album : `dict`
            Spotify catalog information for a single album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "album_type": <str>,
                    "total_tracks": <int>,
                    "available_markets": [<str>],
                    "external_urls": {
                      "spotify": <str>
                    },
                    "href": <str>,
                    "id": <str>,
                    "images": [
                      {
                        "url": <str>,
                        "height": <int>,
                        "width": <int>
                      }
                    ],
                    "name": <str>,
                    "release_date": <str>,
                    "release_date_precision": <str>,
                    "restrictions": {
                      "reason": <str>
                    },
                    "type": "album",
                    "uri": <str>,
                    "copyrights": [
                      {
                        "text": <str>,
                        "type": <str>
                      }
                    ],
                    "external_ids": {
                      "isrc": <str>,
                      "ean": <str>,
                      "upc": <str>
                    },
                    "genres": [<str>],
                    "label": <str>,
                    "popularity": <int>,
                    "artists": [
                      {
                        "external_urls": {
                          "spotify": <str>
                        },
                        "followers": {
                          "href": <str>,
                          "total": <int>
                        },
                        "genres": [<str>],
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "popularity": <int>,
                        "type": "artist",
                        "uri": <str>
                      }
                    ],
                    "tracks": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "artists": [
                            {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "href": <str>,
                              "id": <str>,
                              "name": <str>,
                              "type": "artist",
                              "uri": <str>
                            }
                          ],
                          "available_markets": [<str>],
                          "disc_number": <int>,
                          "duration_ms": <int>,
                          "explicit": <bool>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "is_playable": <bool>
                          "linked_from": {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "type": <str>,
                            "uri": <str>
                          },
                          "restrictions": {
                            "reason": <str>
                          },
                          "name": <str>,
                          "preview_url": <str>,
                          "track_number": <int>,
                          "type": <str>,
                          "uri": <str>,
                          "is_local": <bool>
                        }
                      ]
                    }
                  }
        """

        return self._get_json(f"{self.API_URL}/albums/{id}", params={"market": market})

    def get_albums(
        self, ids: Union[str, list[str]], *, market: str = None
    ) -> dict[str, Any]:
        """
        `Albums > Get Several Albums <https://developer.spotify.com/
        documentation/web-api/reference/
        get-multiple-albums>`_: Get Spotify catalog information for
        albums identified by their Spotify IDs.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the albums.

            **Maximum**: 20 IDs.

            **Example**: :code:`"382ObEPsp2rxGrnsizN5TX,
            1A2GTWGtFfWp7KSQTwWOyo, 2noRn2Aes5aoNVsU6iWThc"`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        albums : `list`
            A list containing Spotify catalog information for multiple
            albums.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "album_type": <str>,
                      "total_tracks": <int>,
                      "available_markets": [<str>],
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "images": [
                        {
                          "url": <str>,
                          "height": <int>,
                          "width": <int>
                        }
                      ],
                      "name": <str>,
                      "release_date": <str>,
                      "release_date_precision": <str>,
                      "restrictions": {
                        "reason": <str>
                      },
                      "type": "album",
                      "uri": <str>,
                      "copyrights": [
                        {
                          "text": <str>,
                          "type": <str>
                        }
                      ],
                      "external_ids": {
                        "isrc": <str>,
                        "ean": <str>,
                        "upc": <str>
                      },
                      "genres": [<str>],
                      "label": <str>,
                      "popularity": <int>,
                      "artists": [
                        {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "followers": {
                            "href": <str>,
                            "total": <int>
                          },
                          "genres": [<str>],
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "popularity": <int>,
                          "type": "artist",
                          "uri": <str>
                        }
                      ],
                      "tracks": {
                        "href": <str>,
                        "limit": <int>,
                        "next": <str>,
                        "offset": <int>,
                        "previous": <str>,
                        "total": <int>,
                        "items": [
                          {
                            "artists": [
                              {
                                "external_urls": {
                                  "spotify": <str>
                                },
                                "href": <str>,
                                "id": <str>,
                                "name": <str>,
                                "type": "artist",
                                "uri": <str>
                              }
                            ],
                            "available_markets": [<str>],
                            "disc_number": <int>,
                            "duration_ms": <int>,
                            "explicit": <bool>,
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "is_playable": <bool>
                            "linked_from": {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "href": <str>,
                              "id": <str>,
                              "type": <str>,
                              "uri": <str>
                            },
                            "restrictions": {
                              "reason": <str>
                            },
                            "name": <str>,
                            "preview_url": <str>,
                            "track_number": <int>,
                            "type": <str>,
                            "uri": <str>,
                            "is_local": <bool>
                          }
                        ]
                      }
                    }
                  ]
        """

        return self._get_json(
            f"{self.API_URL}/albums",
            params={
                "ids": ids if isinstance(ids, str) else ",".join(ids),
                "market": market,
            },
        )["albums"]

    def get_album_tracks(
        self, id: str, *, limit: int = None, market: str = None, offset: int = None
    ) -> dict[str, Any]:
        """
        `Albums > Get Album Tracks <https://developer.spotify.com/
        documentation/web-api/reference/
        get-an-albums-tracks>`_: Get Spotify catalog information for an
        album's tracks. Optional parameters can be used to limit the
        number of tracks returned.

        Parameters
        ----------
        id : `str`
            The Spotify ID of the album.

            **Example**: :code:`"4aawyAB9vmqN3uQ7FjRGTy"`.

        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Valid values**: `offset` must be between 0 and 1,000.

            **Default**: :code:`0`.

        Returns
        -------
        tracks : `dict`
            A dictionary containing Spotify catalog information for an
            album's tracks and the number of results returned.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "artists": [
                          {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "name": <str>,
                            "type": "artist",
                            "uri": <str>
                          }
                        ],
                        "available_markets": [<str>],
                        "disc_number": <int>,
                        "duration_ms": <int>,
                        "explicit": <bool>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "is_playable": <bool>
                        "linked_from": {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "type": <str>,
                          "uri": <str>
                        },
                        "restrictions": {
                          "reason": <str>
                        },
                        "name": <str>,
                        "preview_url": <str>,
                        "track_number": <int>,
                        "type": <str>,
                        "uri": <str>,
                        "is_local": <bool>
                      }
                    ]
                  }
        """

        return self._get_json(
            f"{self.API_URL}/albums/{id}/tracks",
            params={"limit": limit, "market": market, "offset": offset},
        )

    def get_saved_albums(
        self, *, limit: int = None, market: str = None, offset: int = None
    ) -> dict[str, Any]:
        """
        `Albums > Get User's Saved Albums <https://developer.spotify.com/
        documentation/web-api/reference/
        get-users-saved-albums>`_: Get a list of the albums saved in the
        current Spotify user's 'Your Music' library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-read` scope.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Valid values**: `offset` must be between 0 and 1,000.

            **Default**: :code:`0`.

        Returns
        -------
        albums : `dict`
            A dictionary containing Spotify catalog information for a
            user's saved albums and the number of results returned.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "added_at": <str>,
                        "album": {
                          "album_type": <str>,
                          "total_tracks": <int>,
                          "available_markets": [<str>],
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "restrictions": {
                            "reason": <str>
                          },
                          "type": "album",
                          "uri": <str>,
                          "copyrights": [
                            {
                              "text": <str>,
                              "type": <str>
                            }
                          ],
                          "external_ids": {
                            "isrc": <str>,
                            "ean": <str>,
                            "upc": <str>
                          },
                          "genres": [<str>],
                          "label": <str>,
                          "popularity": <int>,
                          "artists": [
                            {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "followers": {
                                "href": <str>,
                                "total": <int>
                              },
                              "genres": [<str>],
                              "href": <str>,
                              "id": <str>,
                              "images": [
                                {
                                  "url": <str>,
                                  "height": <int>,
                                  "width": <int>
                                }
                              ],
                              "name": <str>,
                              "popularity": <int>,
                              "type": "artist",
                              "uri": <str>
                            }
                          ],
                          "tracks": {
                            "href": <str>,
                            "limit": <int>,
                            "next": <str>,
                            "offset": <int>,
                            "previous": <str>,
                            "total": <int>,
                            "items": [
                              {
                                "artists": [
                                  {
                                    "external_urls": {
                                      "spotify": <str>
                                    },
                                    "href": <str>,
                                    "id": <str>,
                                    "name": <str>,
                                    "type": "artist",
                                    "uri": <str>
                                  }
                                ],
                                "available_markets": [<str>],
                                "disc_number": <int>,
                                "duration_ms": <int>,
                                "explicit": <bool>,
                                "external_urls": {
                                  "spotify": <str>
                                },
                                "href": <str>,
                                "id": <str>,
                                "is_playable": <bool>
                                "linked_from": {
                                  "external_urls": {
                                    "spotify": <str>
                                  },
                                  "href": <str>,
                                  "id": <str>,
                                  "type": <str>,
                                  "uri": <str>
                                },
                                "restrictions": {
                                  "reason": <str>
                                },
                                "name": <str>,
                                "preview_url": <str>,
                                "track_number": <int>,
                                "type": <str>,
                                "uri": <str>,
                                "is_local": <bool>
                              }
                            ]
                          }
                        }
                      }
                    ]
                  }
        """

        self._check_scope("get_saved_albums", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/albums",
            params={"limit": limit, "market": market, "offset": offset},
        )

    def save_albums(self, ids: Union[str, list[str]]) -> None:
        """
        `Albums > Save Albums for Current User
        <https://developer.spotify.com/documentation/web-api/reference/
        save-albums-user>`_: Save one or more albums to the
        current user's 'Your Music' library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-modify` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the albums.

            **Maximum**: 20 (`str`) or 50 (`list`) IDs.

            **Example**: :code:`"382ObEPsp2rxGrnsizN5TX,
            1A2GTWGtFfWp7KSQTwWOyo, 2noRn2Aes5aoNVsU6iWThc"`.
        """

        self._check_scope("save_albums", "user-library-modify")

        if isinstance(ids, str):
            self._request("put", f"{self.API_URL}/me/albums", params={"ids": ids})
        elif isinstance(ids, list):
            self._request("put", f"{self.API_URL}/me/albums", json={"ids": ids})

    def remove_saved_albums(self, ids: Union[str, list[str]]) -> None:
        """
        `Albums > Remove Users' Saved Albums
        <https://developer.spotify.com/documentation/web-api/reference/
        remove-albums-user>`_: Remove one or more albums
        from the current user's 'Your Music' library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-modify` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the albums.

            **Maximum**: 20 (`str`) or 50 (`list`) IDs.

            **Example**: :code:`"382ObEPsp2rxGrnsizN5TX,
            1A2GTWGtFfWp7KSQTwWOyo, 2noRn2Aes5aoNVsU6iWThc"`.
        """

        self._check_scope("remove_saved_albums", "user-library-modify")

        if isinstance(ids, str):
            self._request("delete", f"{self.API_URL}/me/albums", params={"ids": ids})
        elif isinstance(ids, list):
            self._request("delete", f"{self.API_URL}/me/albums", json={"ids": ids})

    def check_saved_albums(self, ids: Union[str, list[str]]) -> list[bool]:
        """
        `Albums > Check User's Saved Albums
        <https://developer.spotify.com/documentation/web-api/reference/
        check-users-saved-albums>`_: Check if one or more
        albums is already saved in the current Spotify user's 'Your
        Music' library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-read` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the albums.

            **Maximum**: 20 IDs.

        Returns
        -------
        contains : `list`
            Array of booleans specifying whether the albums are found in
            the user's 'Your Library > Albums'.

            **Example**: :code:`[False, True]`.
        """

        self._check_scope("check_saved_albums", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/albums/contains",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)},
        )

    def get_new_albums(
        self, *, country: str = None, limit: int = None, offset: int = None
    ) -> list[dict[str, Any]]:
        """
        `Albums > Get New Releases <https://developer.spotify.com/
        documentation/web-api/reference/
        get-new-releases>`_: Get a list of new album releases featured
        in Spotify (shown, for example, on a Spotify player's "Browse"
        tab).

        Parameters
        ----------
        country : `str`, keyword-only, optional
            A country: an ISO 3166-1 alpha-2 country code. Provide this
            parameter if you want the list of returned items to be
            relevant to a particular country. If omitted, the returned
            items will be relevant to all countries.

            **Example**: :code:`"SE"`.

        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Valid values**: `offset` must be between 0 and 1,000.

            **Default**: :code:`0`.

        Returns
        -------
        albums : `list`
            A list containing Spotify catalog information for
            newly-released albums.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "album_type": <str>,
                        "total_tracks": <int>,
                        "available_markets": [<str>],
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "release_date": <str>,
                        "release_date_precision": <str>,
                        "restrictions": {
                          "reason": <str>
                        },
                        "type": "album",
                        "uri": <str>,
                        "copyrights": [
                          {
                            "text": <str>,
                            "type": <str>
                          }
                        ],
                        "external_ids": {
                          "isrc": <str>,
                          "ean": <str>,
                          "upc": <str>
                        },
                        "genres": [<str>],
                        "label": <str>,
                        "popularity": <int>,
                        "album_group": <str>,
                        "artists": [
                          {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "name": <str>,
                            "type": "artist",
                            "uri": <str>
                          }
                        ]
                      }
                    ]
                  }
        """

        return self._get_json(
            f"{self.API_URL}/browse/new-releases",
            params={"country": country, "limit": limit, "offset": offset},
        )["albums"]

    ### ARTISTS ###############################################################

    def get_artist(self, id: str) -> dict[str, Any]:
        """
        `Artists > Get Artist <https://developer.spotify.com/
        documentation/web-api/reference/get-an-artist>`_:
        Get Spotify catalog information for a single artist identified
        by their unique Spotify ID.

        Parameters
        ----------
        id : `str`
            The Spotify ID of the artist.

            **Example**: :code:`"0TnOYISbd1XYRBk9myaseg"`.

        Returns
        -------
        artist : `dict`
            Spotify catalog information for a single artist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "external_urls": {
                      "spotify": <str>
                    },
                    "followers": {
                      "href": <str>,
                      "total": <int>
                    },
                    "genres": [<str>],
                    "href": <str>,
                    "id": <str>,
                    "images": [
                      {
                        "url": <str>,
                        "height": <int>,
                        "width": <int>
                      }
                    ],
                    "name": <str>,
                    "popularity": <int>,
                    "type": "artist",
                    "uri": <str>
                  }
        """

        return self._get_json(f"{self.API_URL}/artists/{id}")

    def get_artists(
        self, ids: Union[int, str, list[Union[int, str]]]
    ) -> list[dict[str, Any]]:
        """
        `Artists > Get Several Artists <https://developer.spotify.com/
        documentation/web-api/reference/
        get-multiple-artists>`_: Get Spotify catalog information for
        several artists based on their Spotify IDs.

        Parameters
        ----------
        ids : `str`
            A (comma-separated) list of the Spotify IDs for the artists.

            **Maximum**: 50 IDs.

            **Example**: :code:`"2CIMQHirSU0MQqyYHq0eOx,
            57dN52uHvrHOxijzpIgu3E, 1vCWHaC5f2uS3yhpwWbIA6"`.

        Returns
        -------
        artists : `list`
            A list containing Spotify catalog information for multiple
            artists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "external_urls": {
                        "spotify": <str>
                      },
                      "followers": {
                        "href": <str>,
                        "total": <int>
                      },
                      "genres": [<str>],
                      "href": <str>,
                      "id": <str>,
                      "images": [
                        {
                          "url": <str>,
                          "height": <int>,
                          "width": <int>
                        }
                      ],
                      "name": <str>,
                      "popularity": <int>,
                      "type": "artist",
                      "uri": <str>
                    }
                  ]
        """

        return self._get_json(
            f"{self.API_URL}/artists",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)},
        )["artists"]

    def get_artist_albums(
        self,
        id: str,
        *,
        include_groups: Union[str, list[str]] = None,
        limit: int = None,
        market: str = None,
        offset: int = None,
    ) -> list[dict[str, Any]]:
        """
        `Artist > Get Artist's Albums <https://developer.spotify.com/
        documentation/web-api/reference/
        get-an-artists-albums>`_: Get Spotify catalog information about
        an artist's albums.

        Parameters
        ----------
        id : `str`
            The Spotify ID of the artist.

            **Example**: :code:`"0TnOYISbd1XYRBk9myaseg"`.

        include_groups : `str` or `list`, keyword-only, optional
            A comma-separated list of keywords that will be used to
            filter the response. If not supplied, all album types will
            be returned.

            .. container::

               **Valid values**:

               * :code:`"album"` for albums.
               * :code:`"single"` for singles or promotional releases.
               * :code:`"appears_on"` for albums that `artist` appears
                 on as a featured artist.
               * :code:`"compilation"` for compilations.

               **Examples**:

               * :code:`"album,single"` for albums and singles where
                 `artist` is the main album artist.
               * :code:`"single,appears_on"` for singles and albums that
                 `artist` appears on.

        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Default**: :code:`0`.

        Returns
        -------
        albums : `list`
            A list containing Spotify catalog information for the
            artist's albums.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "album_type": <str>,
                        "total_tracks": <int>,
                        "available_markets": [<str>],
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "release_date": <str>,
                        "release_date_precision": <str>,
                        "restrictions": {
                          "reason": <str>
                        },
                        "type": "album",
                        "uri": <str>,
                        "copyrights": [
                          {
                            "text": <str>,
                            "type": <str>
                          }
                        ],
                        "external_ids": {
                          "isrc": <str>,
                          "ean": <str>,
                          "upc": <str>
                        },
                        "genres": [<str>],
                        "label": <str>,
                        "popularity": <int>,
                        "album_group": <str>,
                        "artists": [
                          {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "name": <str>,
                            "type": "artist",
                            "uri": <str>
                          }
                        ]
                      }
                    ]
                  }
        """

        return self._get_json(
            f"{self.API_URL}/artists/{id}/albums",
            params={
                "include_groups": include_groups,
                "limit": limit,
                "market": market,
                "offset": offset,
            },
        )

    def get_artist_top_tracks(
        self, id: str, *, market: str = "US"
    ) -> list[dict[str, Any]]:
        """
        `Artist > Get Artist's Top Tracks
        <https://developer.spotify.com/documentation/web-api/reference/
        get-an-artists-top-tracks>`_: Get Spotify catalog
        information about an artist's top tracks by country.

        Parameters
        ----------
        id : `str`
            The Spotify ID of the artist.

            **Example**: :code:`"0TnOYISbd1XYRBk9myaseg"`.

        market : `str`, keyword-only, default: :code:`"US"`
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        tracks : `list`
            A list containing Spotify catalog information for the
            artist's top tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "album": {
                        "album_type": <str>,
                        "total_tracks": <int>,
                        "available_markets": [<str>],
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "release_date": <str>,
                        "release_date_precision": <str>,
                        "restrictions": {
                          "reason": <str>
                        },
                        "type": "album",
                        "uri": <str>,
                        "copyrights": [
                          {
                            "text": <str>,
                            "type": <str>
                          }
                        ],
                        "external_ids": {
                          "isrc": <str>,
                          "ean": <str>,
                          "upc": <str>
                        },
                        "genres": [<str>],
                        "label": <str>,
                        "popularity": <int>,
                        "album_group": <str>,
                        "artists": [
                          {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "name": <str>,
                            "type": "artist",
                            "uri": <str>
                          }
                        ]
                      },
                      "artists": [
                        {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "followers": {
                            "href": <str>,
                            "total": <int>
                          },
                          "genres": [<str>],
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "popularity": <int>,
                          "type": "artist",
                          "uri": <str>
                        }
                      ],
                      "available_markets": [<str>],
                      "disc_number": <int>,
                      "duration_ms": <int>,
                      "explicit": <bool>,
                      "external_ids": {
                        "isrc": <str>,
                        "ean": <str>,
                        "upc": <str>
                      },
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "is_playable": <bool>,
                      "linked_from": {
                      },
                      "restrictions": {
                        "reason": <str>
                      },
                      "name": <str>,
                      "popularity": <int>,
                      "preview_url": <str>,
                      "track_number": <int>,
                      "type": "track",
                      "uri": <str>,
                      "is_local": <bool>
                    }
                  ]
        """

        return self._get_json(
            f"{self.API_URL}/artists/{id}/top-tracks", params={"market": market}
        )["tracks"]

    def get_related_artists(self, id: str) -> list[dict[str, Any]]:
        """
        `Artists > Get Artist's Related Artists
        <https://developer.spotify.com/documentation/web-api/reference/
        get-an-artists-related-artists>`_: Get Spotify
        catalog information about artists similar to a given artist.
        Similarity is based on analysis of the Spotify community's
        listening history.

        Parameters
        ----------
        id : `str`
            The Spotify ID of the artist.

            **Example**: :code:`"0TnOYISbd1XYRBk9myaseg"`.

        Returns
        -------
        artists : `list`
            A list containing Spotify catalog information for the
            artist's related artists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "external_urls": {
                        "spotify": <str>
                      },
                      "followers": {
                        "href": <str>,
                        "total": <int>
                      },
                      "genres": [<str>],
                      "href": <str>,
                      "id": <str>,
                      "images": [
                        {
                          "url": <str>,
                          "height": <int>,
                          "width": <int>
                        }
                      ],
                      "name": <str>,
                      "popularity": <int>,
                      "type": "artist",
                      "uri": <str>
                    }
                  ]
        """

        return self._get_json(f"{self.API_URL}/artists/{id}/related-artists")["artists"]

    ### AUDIOBOOKS ############################################################

    def get_audiobook(self, id: str, *, market: str = None) -> dict[str, Any]:
        """
        `Audiobooks > Get an Audiobook
        <https://developer.spotify.com/documentation/web-api/reference/
        get-an-audiobook>`_: Get Spotify catalog information for a
        single audiobook.

        .. note::

           Audiobooks are only available for the US, UK, Ireland, New
           Zealand, and Australia markets.

        Parameters
        ----------
        id : `str`
            The Spotify ID for the audiobook.

            **Example**: :code:`"7iHfbu1YPACw6oZPAFJtqe"`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        audiobook : `dict`
            Spotify catalog information for a single audiobook.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "authors": [
                      {
                        "name": <str>
                      }
                    ],
                    "available_markets": [<str>],
                    "copyrights": [
                      {
                        "text": <str>,
                        "type": <str>
                      }
                    ],
                    "description": <str>,
                    "html_description": <str>,
                    "edition": <str>,
                    "explicit": <bool>,
                    "external_urls": {
                      "spotify": <str>
                    },
                    "href": <str>,
                    "id": <str>,
                    "images": [
                      {
                        "url": <str>,
                        "height": <int>,
                        "width": <int>
                      }
                    ],
                    "languages": [<str>],
                    "media_type": <str>,
                    "name": <str>,
                    "narrators": [
                      {
                        "name": <str>
                      }
                    ],
                    "publisher": <str>,
                    "type": "audiobook",
                    "uri": <str>,
                    "total_chapters": <int>,
                    "chapters": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "audio_preview_url": <str>,
                          "available_markets": [<str>],
                          "chapter_number": <int>,
                          "description": <str>,
                          "html_description": <str>,
                          "duration_ms": <int>,
                          "explicit": <bool>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "is_playable": <bool>
                          "languages": [<str>],
                          "name": <str>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "resume_point": {
                            "fully_played": <bool>,
                            "resume_position_ms": <int>
                          },
                          "type": "episode",
                          "uri": <str>,
                          "restrictions": {
                            "reason": <str>
                          }
                        }
                      ]
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/audiobooks/{id}", params={"market": market}
        )

    def get_audiobooks(
        self, ids: Union[int, str, list[Union[int, str]]], *, market: str = None
    ) -> list[dict[str, Any]]:
        """
        `Audiobooks > Get Several Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference/
        get-multiple-audiobooks>`_: Get Spotify catalog
        information for several audiobooks identified by their Spotify
        IDs.

        .. note::

           Audiobooks are only available for the US, UK, Ireland, New
           Zealand, and Australia markets.

        Parameters
        ----------
        ids : `int`, `str`, or `list`
            A (comma-separated) list of the Spotify IDs for the
            audiobooks.

            **Maximum**: 50 IDs.

            **Example**: :code:`"18yVqkdbdRvS24c0Ilj2ci,
            1HGw3J3NxZO1TP1BTtVhpZ, 7iHfbu1YPACw6oZPAFJtqe"`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        audiobooks : `dict` or `list`
            A list containing Spotify catalog information for multiple
            audiobooks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "authors": [
                        {
                          "name": <str>
                        }
                      ],
                      "available_markets": [<str>],
                      "copyrights": [
                        {
                          "text": <str>,
                          "type": <str>
                        }
                      ],
                      "description": <str>,
                      "html_description": <str>,
                      "edition": <str>,
                      "explicit": <bool>,
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "images": [
                        {
                          "url": <str>,
                          "height": <int>,
                          "width": <int>
                        }
                      ],
                      "languages": [<str>],
                      "media_type": <str>,
                      "name": <str>,
                      "narrators": [
                        {
                          "name": <str>
                        }
                      ],
                      "publisher": <str>,
                      "type": "audiobook",
                      "uri": <str>,
                      "total_chapters": <int>,
                      "chapters": {
                        "href": <str>,
                        "limit": <int>,
                        "next": <str>,
                        "offset": <int>,
                        "previous": <str>,
                        "total": <int>,
                        "items": [
                          {
                            "audio_preview_url": <str>,
                            "available_markets": [<str>],
                            "chapter_number": <int>,
                            "description": <str>,
                            "html_description": <str>,
                            "duration_ms": <int>,
                            "explicit": <bool>,
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "images": [
                              {
                                "url": <str>,
                                "height": <int>,
                                "width": <int>
                              }
                            ],
                            "is_playable": <bool>
                            "languages": [<str>],
                            "name": <str>,
                            "release_date": <str>,
                            "release_date_precision": <str>,
                            "resume_point": {
                              "fully_played": <bool>,
                              "resume_position_ms": <int>
                            },
                            "type": "episode",
                            "uri": <str>,
                            "restrictions": {
                              "reason": <str>
                            }
                          }
                        ]
                      }
                    }
                  ]
        """

        return self._get_json(
            f"{self.API_URL}/audiobooks",
            params={
                "ids": ids if isinstance(ids, str) else ",".join(ids),
                "market": market,
            },
        )["audiobooks"]

    def get_audiobook_chapters(
        self, id: str, *, limit: int = None, market: str = None, offset: int = None
    ) -> dict[str, Any]:
        """
        `Audiobooks > Get Audiobook Chapters
        <https://developer.spotify.com/documentation/web-api/reference/
        get-audiobook-chapters>`_: Get Spotify catalog
        information about an audiobook's chapters.

        .. note::

           Audiobooks are only available for the US, UK, Ireland, New
           Zealand, and Australia markets.

        Parameters
        ----------
        id : `str`
            The Spotify ID for the audiobook.

            **Example**: :code:`"7iHfbu1YPACw6oZPAFJtqe"`.

        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Valid values**: `offset` must be between 0 and 1,000.

            **Default**: :code:`0`.

        Returns
        -------
        audiobooks : `dict`
            A dictionary containing Spotify catalog information for an
            audiobook's chapters and the number of results returned.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "audio_preview_url": <str>,
                        "available_markets": [<str>],
                        "chapter_number": <int>,
                        "description": <str>,
                        "html_description": <str>,
                        "duration_ms": <int>,
                        "explicit": <bool>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "is_playable": <bool>
                        "languages": [<str>],
                        "name": <str>,
                        "release_date": <str>,
                        "release_date_precision": <str>,
                        "resume_point": {
                          "fully_played": <bool>,
                          "resume_position_ms": <int>
                        },
                        "type": "episode",
                        "uri": <str>,
                        "restrictions": {
                          "reason": <str>
                        }
                      }
                    ]
                  }
        """

        return self._get_json(
            f"{self.API_URL}/audiobooks/{id}/chapters",
            params={"limit": limit, "market": market, "offset": offset},
        )

    def get_saved_audiobooks(
        self, *, limit: int = None, offset: int = None
    ) -> dict[str, Any]:
        """
        `Audiobooks > Get User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference/
        get-users-saved-audiobooks>`_: Get a list of the
        albums saved in the current Spotify user's audiobooks library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-read` scope.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Default**: :code:`0`.

        Returns
        -------
        audiobooks : `dict`
            A dictionary containing Spotify catalog information for a
            user's saved audiobooks and the number of results
            returned.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "authors": [
                          {
                            "name": <str>
                          }
                        ],
                        "available_markets": [<str>],
                        "copyrights": [
                          {
                            "text": <str>,
                            "type": <str>
                          }
                        ],
                        "description": <str>,
                        "html_description": <str>,
                        "edition": <str>,
                        "explicit": <bool>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "languages": [<str>],
                        "media_type": <str>,
                        "name": <str>,
                        "narrators": [
                          {
                            "name": <str>
                          }
                        ],
                        "publisher": <str>,
                        "type": "audiobook",
                        "uri": <str>,
                        "total_chapters": <int>
                      }
                    ]
                  }
        """

        self._check_scope("get_saved_audiobooks", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/audiobooks", params={"limit": limit, "offset": offset}
        )

    def save_audiobooks(self, ids: Union[str, list[str]]) -> None:
        """
        `Audiobooks > Save Audiobooks for Current User
        <https://developer.spotify.com/documentation/web-api/reference/
        save-audiobooks-user>`_: Save one or more
        audiobooks to current Spotify user's library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-modify` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the
            audiobooks.

            **Maximum**: 50 IDs.

            **Example**: :code:`"18yVqkdbdRvS24c0Ilj2ci,
            1HGw3J3NxZO1TP1BTtVhpZ, 7iHfbu1YPACw6oZPAFJtqe"`.
        """

        self._check_scope("save_audiobooks", "user-library-modify")

        self._request(
            "put",
            f"{self.API_URL}/me/audiobooks",
            params={"ids": f"{ids if isinstance(ids, str) else ','.join(ids)}"},
        )

    def remove_saved_audiobooks(self, ids: Union[str, list[str]]) -> None:
        """
        `Audiobooks > Remove User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference/
        remove-audiobooks-user>`_: Delete one or more
        audiobooks from current Spotify user's library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-modify` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the
            audiobooks.

            **Maximum**: 50 IDs.

            **Example**: :code:`"18yVqkdbdRvS24c0Ilj2ci,
            1HGw3J3NxZO1TP1BTtVhpZ, 7iHfbu1YPACw6oZPAFJtqe"`.
        """

        self._check_scope("remove_saved_audiobooks", "user-library-modify")

        self._request(
            "delete",
            f"{self.API_URL}/me/audiobooks",
            params={"ids": f"{ids if isinstance(ids, str) else ','.join(ids)}"},
        )

    def check_saved_audiobooks(self, ids: Union[str, list[str]]) -> list[bool]:
        """
        `Audiobooks > Check User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference/
        check-users-saved-audiobooks>`_: Check if one or
        more audiobooks are already saved in the current Spotify user's
        library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-read` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the
            audiobooks.

            **Maximum**: 50 IDs.

            **Example**: :code:`"18yVqkdbdRvS24c0Ilj2ci,
            1HGw3J3NxZO1TP1BTtVhpZ, 7iHfbu1YPACw6oZPAFJtqe"`.

        Returns
        -------
        contains : `list`
            Array of booleans specifying whether the audiobooks are
            found in the user's saved audiobooks.

            **Example**: :code:`[False, True]`.
        """

        self._check_scope("check_saved_audiobooks", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/audiobooks/contains",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)},
        )

    ### CATEGORIES ############################################################

    def get_category(
        self, category_id: str, *, country: str = None, locale: str = None
    ) -> dict[str, Any]:
        """
        `Categories > Get Single Browse Category
        <https://developer.spotify.com/documentation/web-api/reference/
        get-a-category>`_: Get a single category used to
        tag items in Spotify (on, for example, the Spotify player's
        "Browse" tab).

        Parameters
        ----------
        category_id : `str`
            The Spotify category ID for the category.

            **Example**: :code:`"dinner"`.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. Provide this parameter
            to ensure that the category exists for a particular country.

            **Example**: :code:`"SE"`.

        locale : `str`, keyword-only, optional
            The desired language, consisting of an ISO 639-1 language
            code and an ISO 3166-1 alpha-2 country code, joined by an
            underscore. Provide this parameter if you want the category
            strings returned in a particular language.

            .. note::

               If `locale` is not supplied, or if the specified language
               is not available, the category strings returned will be
               in the Spotify default language (American English).

            **Example**: :code:`"es_MX"` for "Spanish (Mexico)".

        Returns
        -------
        category : `dict`
            Information for a single browse category.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "icons": [
                      {
                        "url": <str>,
                        "height": <int>,
                        "width": <int>
                      }
                    ],
                    "id": <str>,
                    "name": <str>
                  }
        """

        return self._get_json(
            f"{self.API_URL}/browse/categories/{category_id}",
            params={"country": country, "locale": locale},
        )

    def get_categories(
        self,
        *,
        country: str = None,
        limit: int = None,
        locale: str = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        `Categories > Get Several Browse Categories
        <https://developer.spotify.com/documentation/web-api/reference/
        get-categories>`_: Get a list of categories used to
        tag items in Spotify (on, for example, the Spotify player's
        "Browse" tab).

        Parameters
        ----------
        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. Provide this parameter
            to ensure that the category exists for a particular country.

            **Example**: :code:`"SE"`.

        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        locale : `str`, keyword-only, optional
            The desired language, consisting of an ISO 639-1 language
            code and an ISO 3166-1 alpha-2 country code, joined by an
            underscore. Provide this parameter if you want the category
            strings returned in a particular language.

            .. note::

               If locale is not supplied, or if the specified language
               is not available, the category strings returned will be
               in the Spotify default language (American English).

            **Example**: :code:`"es_MX"` for "Spanish (Mexico)".

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Default**: :code:`0`.

        Returns
        -------
        categories : `dict`
            A dictionary containing nformation for the browse categories
            and the number of results returned.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                      "items": [
                        {
                          "href": <str>,
                          "icons": [
                            {
                              "height": <int>,
                              "url": <str>,
                              "width": <int>
                            }
                          ],
                          "id": <str>,
                          "name": <str>
                        }
                      ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """

        return self._get_json(
            f"{self.API_URL}/browse/categories",
            params={
                "country": country,
                "limit": limit,
                "locale": locale,
                "offset": offset,
            },
        )["categories"]

    ### CHAPTERS ##############################################################

    def get_chapter(self, id: str, *, market: str = None) -> dict[str, Any]:
        """
        `Chapters > Get a Chapter <https://developer.spotify.com/
        documentation/web-api/reference/get-a-chapter>`_:
        Get Spotify catalog information for a single chapter.

        .. note::
           Chapters are only available for the US, UK, Ireland, New
           Zealand, and Australia markets.

        Parameters
        ----------
        id : `str`
            The Spotify ID for the chapter.

            **Example**: :code:`"0D5wENdkdwbqlrHoaJ9g29"`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        chapter : `dict`
            Spotify catalog information for a single chapter.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "audio_preview_url": <str>,
                    "available_markets": [<str>],
                    "chapter_number": <int>,
                    "description": <str>,
                    "html_description": <str>,
                    "duration_ms": <int>,
                    "explicit": <bool>,
                    "external_urls": {
                      "spotify": <str>
                    },
                    "href": <str>,
                    "id": <str>,
                    "images": [
                      {
                        "url": <str>,
                        "height": <int>,
                        "width": <int>
                      }
                    ],
                    "is_playable": <bool>
                    "languages": [<str>],
                    "name": <str>,
                    "release_date": <str>,
                    "release_date_precision": <str>,
                    "resume_point": {
                      "fully_played": <bool>,
                      "resume_position_ms": <int>
                    },
                    "type": "episode",
                    "uri": <str>,
                    "restrictions": {
                      "reason": <str>
                    },
                    "audiobook": {
                      "authors": [
                        {
                          "name": <str>
                        }
                      ],
                      "available_markets": [<str>],
                      "copyrights": [
                        {
                          "text": <str>,
                          "type": <str>
                        }
                      ],
                      "description": <str>,
                      "html_description": <str>,
                      "edition": <str>,
                      "explicit": <bool>,
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "images": [
                        {
                          "url": <str>,
                          "height": <int>,
                          "width": <int>
                        }
                      ],
                      "languages": [<str>],
                      "media_type": <str>,
                      "name": <str>,
                      "narrators": [
                        {
                          "name": <str>
                        }
                      ],
                      "publisher": <str>,
                      "type": "audiobook",
                      "uri": <str>,
                      "total_chapters": <int>
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/chapters/{id}", params={"market": market}
        )

    def get_chapters(
        self, ids: Union[int, str, list[Union[int, str]]], *, market: str = None
    ) -> list[dict[str, Any]]:
        """
        `Chapters > Get Several Chapters <https://developer.spotify.com/
        documentation/web-api/reference/
        get-several-chapters>`_: Get Spotify catalog information for
        several chapters identified by their Spotify IDs.

        .. note::
           Chapters are only available for the US, UK, Ireland, New
           Zealand, and Australia markets.

        Parameters
        ----------
        ids : `int`, `str`, or `list`
            A (comma-separated) list of the Spotify IDs for the
            chapters.

            **Maximum**: 50 IDs.

            **Example**: :code:`"0IsXVP0JmcB2adSE338GkK,
            3ZXb8FKZGU0EHALYX6uCzU, 0D5wENdkdwbqlrHoaJ9g29"`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::
               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        chapters : `list`
            A list containing Spotify catalog information for multiple
            chapters.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "audio_preview_url": <str>,
                      "available_markets": [<str>],
                      "chapter_number": <int>,
                      "description": <str>,
                      "html_description": <str>,
                      "duration_ms": <int>,
                      "explicit": <bool>,
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "images": [
                        {
                          "url": <str>,
                          "height": <int>,
                          "width": <int>
                        }
                      ],
                      "is_playable": <bool>
                      "languages": [<str>],
                      "name": <str>,
                      "release_date": <str>,
                      "release_date_precision": <str>,
                      "resume_point": {
                        "fully_played": <bool>,
                        "resume_position_ms": <int>
                      },
                      "type": "episode",
                      "uri": <str>,
                      "restrictions": {
                        "reason": <str>
                      },
                      "audiobook": {
                        "authors": [
                          {
                            "name": <str>
                          }
                        ],
                        "available_markets": [<str>],
                        "copyrights": [
                          {
                            "text": <str>,
                            "type": <str>
                          }
                        ],
                        "description": <str>,
                        "html_description": <str>,
                        "edition": <str>,
                        "explicit": <bool>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "languages": [<str>],
                        "media_type": <str>,
                        "name": <str>,
                        "narrators": [
                          {
                            "name": <str>
                          }
                        ],
                        "publisher": <str>,
                        "type": "audiobook",
                        "uri": <str>,
                        "total_chapters": <int>
                      }
                    }
                  ]
        """

        return self._get_json(
            f"{self.API_URL}/chapters",
            params={
                "ids": ids if isinstance(ids, str) else ",".join(ids),
                "market": market,
            },
        )["chapters"]

    ### EPISODES ##############################################################

    def get_episode(self, id: str, *, market: str = None) -> dict[str, Any]:
        """
        `Episodes > Get Episode <https://developer.spotify.com/
        documentation/web-api/reference/
        get-an-episode>`_: Get Spotify catalog information for a single
        episode identified by its unique Spotify ID.

        Parameters
        ----------
        id : `str`
            The Spotify ID for the episode.

            **Example**: :code:`"512ojhOuo1ktJprKbVcKyQ"`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::
               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        episode : `dict`
            Spotify catalog information for a single episode.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "audio_preview_url": <str>,
                    "description": <str>,
                    "html_description": <str>,
                    "duration_ms": <int>,
                    "explicit": <bool>,
                    "external_urls": {
                      "spotify": <str>
                    },
                    "href": <str>,
                    "id": <str>,
                    "images": [
                      {
                        "url": <str>,
                        "height": <int>,
                        "width": <int>
                      }
                    ],
                    "is_externally_hosted": <bool>,
                    "is_playable": <bool>
                    "language": <str>,
                    "languages": [<str>],
                    "name": <str>,
                    "release_date": <str>,
                    "release_date_precision": <str>,
                    "resume_point": {
                      "fully_played": <bool>,
                      "resume_position_ms": <int>
                    },
                    "type": "episode",
                    "uri": <str>,
                    "restrictions": {
                      "reason": <str>
                    },
                    "show": {
                      "available_markets": [<str>],
                      "copyrights": [
                        {
                          "text": <str>,
                          "type": <str>
                        }
                      ],
                      "description": <str>,
                      "html_description": <str>,
                      "explicit": <bool>,
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "images": [
                        {
                          "url": <str>,
                          "height": <int>,
                          "width": <int>
                        }
                      ],
                      "is_externally_hosted": <bool>,
                      "languages": [<str>],
                      "media_type": <str>,
                      "name": <str>,
                      "publisher": <str>,
                      "type": "show",
                      "uri": <str>,
                      "total_episodes": <int>
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/episodes/{id}", params={"market": market}
        )

    def get_episodes(
        self, ids: Union[int, str, list[Union[int, str]]], *, market: str = None
    ) -> list[dict[str, Any]]:
        """
        `Episodes > Get Several Episodes
        <https://developer.spotify.com/documentation/web-api/reference/
        get-multiple-episodes>`_: Get Spotify catalog
        information for several episodes based on their Spotify IDs.

        Parameters
        ----------
        ids : `int`, `str`, or `list`
            A (comma-separated) list of the Spotify IDs for the episodes.

            **Maximum**: 50 IDs.

            **Example**:
            :code:`"77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf"`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        episodes : `list`
            A list containing Spotify catalog information for multiple
            episodes.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  [
                    {
                      "audio_preview_url": <str>,
                      "description": <str>,
                      "html_description": <str>,
                      "duration_ms": <int>,
                      "explicit": <bool>,
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "images": [
                        {
                          "url": <str>,
                          "height": <int>,
                          "width": <int>
                        }
                      ],
                      "is_externally_hosted": <bool>,
                      "is_playable": <bool>
                      "language": <str>,
                      "languages": [<str>],
                      "name": <str>,
                      "release_date": <str>,
                      "release_date_precision": <str>,
                      "resume_point": {
                        "fully_played": <bool>,
                        "resume_position_ms": <int>
                      },
                      "type": "episode",
                      "uri": <str>,
                      "restrictions": {
                        "reason": <str>
                      },
                      "show": {
                        "available_markets": [<str>],
                        "copyrights": [
                          {
                            "text": <str>,
                            "type": <str>
                          }
                        ],
                        "description": <str>,
                        "html_description": <str>,
                        "explicit": <bool>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "is_externally_hosted": <bool>,
                        "languages": [<str>],
                        "media_type": <str>,
                        "name": <str>,
                        "publisher": <str>,
                        "type": "show",
                        "uri": <str>,
                        "total_episodes": <int>
                      }
                    }
                  ]
        """

        return self._get_json(
            f"{self.API_URL}/episodes",
            params={
                "ids": ids if isinstance(ids, str) else ",".join(ids),
                "market": market,
            },
        )["episodes"]

    def get_saved_episodes(
        self, *, limit: int = None, market: str = None, offset: int = None
    ) -> dict[str, Any]:
        """
        `Episodes > Get User's Saved Episodes
        <https://developer.spotify.com/documentation/web-api/reference/
        get-users-saved-episodes>`_: Get a list of the
        episodes saved in the current Spotify user's library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-read` scope.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Default**: :code:`0`.

        Returns
        -------
        episodes : `dict`
            A dictionary containing Spotify catalog information for a
            user's saved episodes and the number of results returned.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "added_at": <str>,
                        "episode": {
                          "audio_preview_url": <str>,
                          "description": <str>,
                          "html_description": <str>,
                          "duration_ms": <int>,
                          "explicit": <bool>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "is_externally_hosted": <bool>,
                          "is_playable": <bool>
                          "language": <str>,
                          "languages": [<str>],
                          "name": <str>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "resume_point": {
                            "fully_played": <bool>,
                            "resume_position_ms": <int>
                          },
                          "type": "episode",
                          "uri": <str>,
                          "restrictions": {
                            "reason": <str>
                          },
                          "show": {
                            "available_markets": [<str>],
                            "copyrights": [
                              {
                                "text": <str>,
                                "type": <str>
                              }
                            ],
                            "description": <str>,
                            "html_description": <str>,
                            "explicit": <bool>,
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "images": [
                              {
                                "url": <str>,
                                "height": <int>,
                                "width": <int>
                              }
                            ],
                            "is_externally_hosted": <bool>,
                            "languages": [<str>],
                            "media_type": <str>,
                            "name": <str>,
                            "publisher": <str>,
                            "type": "show",
                            "uri": <str>,
                            "total_episodes": <int>
                          }
                        }
                      }
                    ]
                  }
        """

        self._check_scope("get_saved_episodes", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/episodes",
            params={"limit": limit, "market": market, "offset": offset},
        )

    def save_episodes(self, ids: Union[str, list[str]]) -> None:
        """
        `Episodes > Save Episodes for Current User
        <https://developer.spotify.com/documentation/web-api/reference/
        save-episodes-user>`_: Save one or more episodes to
        the current user's library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-modify` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the shows.

            **Maximum**: 50 IDs.

            **Example**:
            :code:`"77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf"`.
        """

        self._check_scope("save_episodes", "user-library-modify")

        if isinstance(ids, str):
            self._request("put", f"{self.API_URL}/me/episodes", params={"ids": ids})
        elif isinstance(ids, list):
            self._request("put", f"{self.API_URL}/me/episodes", json={"ids": ids})

    def remove_saved_episodes(self, ids: Union[str, list[str]]) -> None:
        """
        `Episodes > Remove User's Saved Episodes
        <https://developer.spotify.com/documentation/web-api/reference/
        remove-episodes-user>`_: Remove one or more
        episodes from the current user's library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-modify` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the episodes.

            **Maximum**: 50 IDs.

            **Example**:
            :code:`"77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf"`.
        """

        self._check_scope("remove_saved_episodes", "user-library-modify")

        if isinstance(ids, str):
            self._request("delete", f"{self.API_URL}/me/episodes", params={"ids": ids})
        elif isinstance(ids, list):
            self._request("delete", f"{self.API_URL}/me/episodes", json={"ids": ids})

    def check_saved_episodes(self, ids: Union[str, list[str]]) -> list[bool]:
        """
        `Episodes > Check User's Saved Episodes
        <https://developer.spotify.com/documentation/web-api/reference/
        check-users-saved-episodes>`_: Check if one or more
        episodes is already saved in the current Spotify user's 'Your
        Episodes' library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-read` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the
            episodes.

            **Maximum**: 50 IDs.

            **Example**:
            :code:`"77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf"`.

        Returns
        -------
        contains : `list`
            Array of booleans specifying whether the episodes are found
            in the user's 'Liked Songs'.

            **Example**: :code:`[False, True]`.
        """

        self._check_scope("check_saved_episodes", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/episodes/contains",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)},
        )

    ### GENRES ################################################################

    def get_genre_seeds(self) -> list[str]:
        """
        `Genres > Get Available Genre Seeds
        <https://developer.spotify.com/documentation/web-api/reference/
        get-recommendation-genres>`_: Retrieve a list of
        available genres seed parameter values for use in
        :meth:`get_recommendations`.

        Returns
        -------
        genres : `list`
            Array of genres.

            **Example**: :code:`["acoustic", "afrobeat", ...]`.
        """

        return self._get_json(f"{self.API_URL}/recommendations/available-genre-seeds")[
            "genres"
        ]

    ### MARKETS ###############################################################

    def get_markets(self) -> list[str]:
        """
        `Markets > Get Available Markets <https://developer.spotify.com/
        documentation/web-api/reference/
        get-available-markets>`_: Get the list of markets where Spotify
        is available.

        Returns
        -------
        markets : `list`
            Array of country codes.

            **Example**: :code:`["CA", "BR", "IT"]`.
        """

        return self._get_json(f"{self.API_URL}/markets")["markets"]

    ### PLAYER ################################################################

    def get_playback_state(
        self, *, market: str = None, additional_types: str = None
    ) -> dict[str, Any]:
        """
        `Player > Get Playback State <https://developer.spotify.com/
        documentation/web-api/reference/
        get-information-about-the-users-current-playback>`_: Get
        information about the user's current playback state, including
        track or episode, progress, and active device.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-read-playback-state` scope.

        Parameters
        ----------
        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        additional_types : `str`, keyword-only, optional
            A comma-separated list of item types that your client
            supports besides the default track type.

            .. note::

               This parameter was introduced to allow existing clients
               to maintain their current behavior and might be
               deprecated in the future.

            **Valid**: :code:`"track"` and :code:`"episode"`.

        Returns
        -------
        state : `dict`
            Information about playback state.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "device": {
                      "id": <str>,
                      "is_active": <bool>,
                      "is_private_session": <bool>,
                      "is_restricted": <bool>,
                      "name": <str>,
                      "type": <str>,
                      "volume_percent": <int>
                    },
                    "repeat_state": <str>,
                    "shuffle_state": <bool>,
                    "context": {
                      "type": <str>,
                      "href": <str>,
                      "external_urls": {
                        "spotify": <str>
                      },
                      "uri": <str>
                    },
                    "timestamp": <int>,
                    "progress_ms": <int>,
                    "is_playing": <bool>,
                    "item": {
                      "album": {
                        "album_type": <str>,
                        "total_tracks": <int>,
                        "available_markets": [<str>],
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "release_date": <str>,
                        "release_date_precision": <str>,
                        "restrictions": {
                          "reason": <str>
                        },
                        "type": "album",
                        "uri": <str>,
                        "copyrights": [
                          {
                            "text": <str>,
                            "type": <str>
                          }
                        ],
                        "external_ids": {
                          "isrc": <str>,
                          "ean": <str>,
                          "upc": <str>
                        },
                        "genres": [<str>],
                        "label": <str>,
                        "popularity": <int>,
                        "album_group": <str>,
                        "artists": [
                          {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "name": <str>,
                            "type": "artist",
                            "uri": <str>
                          }
                        ]
                      },
                      "artists": [
                        {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "followers": {
                            "href": <str>,
                            "total": <int>
                          },
                          "genres": [<str>],
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "popularity": <int>,
                          "type": "artist",
                          "uri": <str>
                        }
                      ],
                      "available_markets": [<str>],
                      "disc_number": <int>,
                      "duration_ms": <int>,
                      "explicit": <bool>,
                      "external_ids": {
                        "isrc": <str>,
                        "ean": <str>,
                        "upc": <str>
                      },
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "is_playable": <bool>
                      "linked_from": {
                      },
                      "restrictions": {
                        "reason": <str>
                      },
                      "name": <str>,
                      "popularity": <int>,
                      "preview_url": <str>,
                      "track_number": <int>,
                      "type": "track",
                      "uri": <str>,
                      "is_local": <bool>
                    },
                    "currently_playing_type": <str>,
                    "actions": {
                      "interrupting_playback": <bool>,
                      "pausing": <bool>,
                      "resuming": <bool>,
                      "seeking": <bool>,
                      "skipping_next": <bool>,
                      "skipping_prev": <bool>,
                      "toggling_repeat_context": <bool>,
                      "toggling_shuffle": <bool>,
                      "toggling_repeat_track": <bool>,
                      "transferring_playback": <bool>
                    }
                  }
        """

        self._check_scope("get_playback_state", "user-read-playback-state")

        return self._get_json(
            f"{self.API_URL}/me/player",
            params={"market": market, "additional_types": additional_types},
        )

    def transfer_playback(
        self, device_ids: Union[str, list[str]], *, play: bool = None
    ) -> None:
        """
        `Player > Transfer Playback <https://developer.spotify.com/
        documentation/web-api/reference/transfer-a-users-playback>`_:
        Transfer playback to a new device and determine if it should
        start playing.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-modify-playback-state` scope.

        Parameters
        ----------
        device_ids : `str` or `list`
            The ID of the device on which playback should be started or
            transferred.

            .. note::
               Although an array is accepted, only a single device ID is
               currently supported. Supplying more than one will return
               :code:`400 Bad Request`.

            **Example**: :code:`["74ASZWbe4lXaubB36ztrGX"]`.

        play : `bool`
            If :code:`True`, playback happens on the new device; if
            :code:`False` or not provided, the current playback state is
            kept.
        """

        self._check_scope("transfer_playback", "user-modify-playback-state")

        json = {
            "device_ids": [device_ids] if isinstance(device_ids, str) else device_ids
        }
        if play is not None:
            json["play"] = play
        self._request("put", f"{self.API_URL}/me/player", json=json)

    def get_devices(self) -> list[dict[str, Any]]:
        """
        `Player > Get Available Devices <https://developer.spotify.com/
        documentation/web-api/reference/
        get-a-users-available-devices>`_: Get information about a user's
        available devices.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-read-playback-state` scope.

        Returns
        -------
        devices : `list`
            A list containing information about the available devices.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "devices": [
                        {
                          "id": <str>,
                          "is_active": <bool>,
                          "is_private_session": <bool>,
                          "is_restricted": <bool>,
                          "name": <str>,
                          "type": <str>,
                          "volume_percent": <int>
                        }
                      ]
                    }
                  ]
        """

        self._check_scope("get_available_devices", "user-read-playback-state")

        self._get_json(f"{self.API_URL}/me/player/devices")

    def get_currently_playing(
        self, *, market: str = None, additional_types: str = None
    ) -> dict[str, Any]:
        """
        `Player > Get Currently Playing Track
        <https://developer.spotify.com/documentation/web-api/reference/
        get-the-users-currently-playing-track>`_: Get the object
        currently being played on the user's Spotify account.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-read-currently-playing` scope.

        Parameters
        ----------
        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        additional_types : `str`, keyword-only, optional
            A comma-separated list of item types that your client
            supports besides the default track type.

            .. note::

               This parameter was introduced to allow existing clients
               to maintain their current behavior and might be
               deprecated in the future.

            **Valid**: :code:`"track"` and :code:`"episode"`.

        Returns
        -------
        item : `dict`
            Information about the object currently being played.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "device": {
                      "id": <str>,
                      "is_active": <bool>,
                      "is_private_session": <bool>,
                      "is_restricted": <bool>,
                      "name": <str>,
                      "type": <str>,
                      "volume_percent": <int>
                    },
                    "repeat_state": <str>,
                    "shuffle_state": <bool>,
                    "context": {
                      "type": <str>,
                      "href": <str>,
                      "external_urls": {
                        "spotify": <str>
                      },
                      "uri": <str>
                    },
                    "timestamp": <int>,
                    "progress_ms": <int>,
                    "is_playing": <bool>,
                    "item": {
                      "album": {
                        "album_type": <str>,
                        "total_tracks": <int>,
                        "available_markets": [<str>],
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "release_date": <str>,
                        "release_date_precision": <str>,
                        "restrictions": {
                          "reason": <str>
                        },
                        "type": "album",
                        "uri": <str>,
                        "copyrights": [
                          {
                            "text": <str>,
                            "type": <str>
                          }
                        ],
                        "external_ids": {
                          "isrc": <str>,
                          "ean": <str>,
                          "upc": <str>
                        },
                        "genres": [<str>],
                        "label": <str>,
                        "popularity": <int>,
                        "album_group": <str>,
                        "artists": [
                          {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "name": <str>,
                            "type": "artist",
                            "uri": <str>
                          }
                        ]
                      },
                      "artists": [
                        {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "followers": {
                            "href": <str>,
                            "total": <int>
                          },
                          "genres": [<str>],
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "popularity": <int>,
                          "type": "artist",
                          "uri": <str>
                        }
                      ],
                      "available_markets": [<str>],
                      "disc_number": <int>,
                      "duration_ms": <int>,
                      "explicit": <bool>,
                      "external_ids": {
                        "isrc": <str>,
                        "ean": <str>,
                        "upc": <str>
                      },
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "is_playable": <bool>
                      "linked_from": {
                      },
                      "restrictions": {
                        "reason": <str>
                      },
                      "name": <str>,
                      "popularity": <int>,
                      "preview_url": <str>,
                      "track_number": <int>,
                      "type": "track",
                      "uri": <str>,
                      "is_local": <bool>
                    },
                    "currently_playing_type": <str>,
                    "actions": {
                      "interrupting_playback": <bool>,
                      "pausing": <bool>,
                      "resuming": <bool>,
                      "seeking": <bool>,
                      "skipping_next": <bool>,
                      "skipping_prev": <bool>,
                      "toggling_repeat_context": <bool>,
                      "toggling_shuffle": <bool>,
                      "toggling_repeat_track": <bool>,
                      "transferring_playback": <bool>
                    }
                  }
        """

        self._check_scope("get_currently_playing_item", "user-read-currently-playing")

        self._get_json(
            f"{self.API_URL}/me/player/currently-playing",
            params={"market": market, "additional_types": additional_types},
        )

    def start_playback(
        self,
        *,
        device_id: str = None,
        context_uri: str = None,
        uris: list[str] = None,
        offset: dict[str, Any],
        position_ms: int = None,
    ) -> None:
        """
        `Player > Start/Resume Playback <https://developer.spotify.com/
        documentation/web-api/reference/start-a-users-playback>`_: Start
        a new context or resume current playback on the user's active
        device.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-modify-playback-state` scope.

        Parameters
        ----------
        device_id : `str`, keyword-only, optional
            The ID of the device this method is targeting. If not
            supplied, the user's currently active device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.

        context_uri : `str`, keyword-only, optional
            Spotify URI of the context to play. Only album, artist, and
            playlist contexts are valid.

            **Example**: :code:`"spotify:album:1Je1IMUlBXcx1Fz0WE7oPT"`.

        uris : `list`, keyword-only, optional
            A JSON array of the Spotify track URIs to play.

            **Example**: :code:`["spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
            "spotify:track:1301WleyT98MSxVHPZCA6M"]`.

        offset : `dict`, keyword-only, optional
            Indicates from where in the context playback should start.
            Only available when `context_uri` corresponds to an album or
            a playlist.

            .. container::

               **Valid values**:

               * The value corresponding to the :code:`"position"` key
                 is zero-based and can't be negative.
               * The value corresponding to the :code:`"uri"` key is a
                 string representing the URI of the item to start at.

               **Examples**:

               * :code:`{"position": 5}` to start playback at the sixth
                 item of the collection specified in `context_uri`.
               * :code:`{"uri": <str>}`
                 to start playback at the item designated by the URI.

        position_ms : `int`, keyword-only, optional
            The position in milliseconds to seek to. Passing in a
            position that is greater than the length of the track will
            cause the player to start playing the next song.

            **Valid values**: `position_ms` must be a positive number.
        """

        self._check_scope("start_playback", "user-modify-playback-state")

        json = {}
        if context_uri is not None:
            json["context_uri"] = context_uri
        if uris is not None:
            json["uris"] = uris
        if offset is not None:
            json["offset"] = offset
        if position_ms is not None:
            json["position_ms"] = position_ms

        self._request(
            "put",
            f"{self.API_URL}/me/player/play",
            params={"device_id": device_id},
            json=json,
        )

    def pause_playback(self, *, device_id: str = None) -> None:
        """
        `Player > Pause Playback <https://developer.spotify.com/
        documentation/web-api/reference/pause-a-users-playback>`_: Pause
        playback on the user's account.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-modify-playback-state` scope.

        Parameters
        ----------
        device_id : `str`, keyword-only, optional
            The ID of the device this method is targeting. If not
            supplied, the user's currently active device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """

        self._check_scope("pause_playback", "user-modify-playback-state")

        self._request(
            "put", f"{self.API_URL}/me/player/pause", params={"device_id": device_id}
        )

    def skip_to_next(self, *, device_id: str = None) -> None:
        """
        `Player > Skip To Next <https://developer.spotify.com/
        documentation/web-api/reference/
        skip-users-playback-to-next-track>`_: Skips to next track in the
        user's queue.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-modify-playback-state` scope.

        Parameters
        ----------
        device_id : `str`, keyword-only, optional
            The ID of the device this method is targeting. If not
            supplied, the user's currently active device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """

        self._check_scope("skip_to_next", "user-modify-playback-state")

        self._request(
            "post", f"{self.API_URL}/me/player/next", params={"device_id": device_id}
        )

    def skip_to_previous(self, *, device_id: str = None) -> None:
        """
        `Player > Skip To Previous <https://developer.spotify.com/
        documentation/web-api/reference/
        skip-users-playback-to-previous-track>`_: Skips to previous
        track in the user's queue.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-modify-playback-state` scope.

        Parameters
        ----------
        device_id : `str`, keyword-only, optional
            The ID of the device this method is targeting. If not
            supplied, the user's currently active device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """

        self._check_scope("skip_to_previous", "user-modify-playback-state")

        self._request(
            "post",
            f"{self.API_URL}/me/player/previous",
            params={"device_id": device_id},
        )

    def seek_to_position(self, position_ms: int, *, device_id: str = None) -> None:
        """
        `Player > Seek To Position <https://developer.spotify.com/
        documentation/web-api/reference/
        seek-to-position-in-currently-playing-track>`_: Seeks to the
        given position in the user's currently playing track.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-modify-playback-state` scope.

        Parameters
        ----------
        position_ms : `int`
            The position in milliseconds to seek to. Passing in a
            position that is greater than the length of the track will
            cause the player to start playing the next song.

            **Valid values**: `position_ms` must be a positive number.

            **Example**: :code:`25000`.

        device_id : `str`, keyword-only, optional
            The ID of the device this method is targeting. If not
            supplied, the user's currently active device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """

        self._check_scope("seek_to_position", "user-modify-playback-state")

        self._request(
            "put",
            f"{self.API_URL}/me/player/seek",
            params={"position_ms": position_ms, "device_id": device_id},
        )

    def set_repeat_mode(self, state: str, *, device_id: str = None) -> None:
        """
        `Player > Set Repeat Mode <https://developer.spotify.com/
        documentation/web-api/reference/
        set-repeat-mode-on-users-playback>`_: Set the repeat mode for
        the user's playback. Options are repeat-track, repeat-context,
        and off.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-modify-playback-state` scope.

        Parameters
        ----------
        state : `str`
            Repeat mode.

            .. container::

               **Valid values**:

               * :code:`"track"` will repeat the current track.
               * :code:`"context"` will repeat the current context.
               * :code:`"off"` will turn repeat off.

        device_id : `str`, keyword-only, optional
            The ID of the device this method is targeting. If not
            supplied, the user's currently active device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """

        self._check_scope("set_repeat_mode", "user-modify-playback-state")

        self._request(
            "put",
            f"{self.API_URL}/me/player/repeat",
            params={"state": state, "device_id": device_id},
        )

    def set_playback_volume(
        self, volume_percent: int, *, device_id: str = None
    ) -> None:
        """
        `Player > Set Playback Volume <https://developer.spotify.com/
        documentation/web-api/reference/
        set-volume-for-users-playback>`_: Set the volume for the user's
        current playback device.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-modify-playback-state` scope.

        Parameters
        ----------
        volume_percent : `int`
            The volume to set.

            **Valid values**: `volume_percent` must be a value from 0 to
            100, inclusive.

            **Example**: :code:`50`.

        device_id : `str`, keyword-only, optional
            The ID of the device this method is targeting. If not
            supplied, the user's currently active device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """

        self._check_scope("set_playback_volume", "user-modify-playback-state")

        self._request(
            "put",
            f"{self.API_URL}/me/player/volume",
            params={"volume_percent": volume_percent, "device_id": device_id},
        )

    def toggle_playback_shuffle(self, state: bool, *, device_id: str = None) -> None:
        """
        `Player > Toggle Playback Shuffle
        <https://developer.spotify.com/documentation/web-api/reference/
        toggle-shuffle-for-users-playback>`_: Toggle shuffle on or off
        for user's playback.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-modify-playback-state` scope.

        Parameters
        ----------
        state : `bool`
            Shuffle mode. If :code:`True`, shuffle the user's playback.

        device_id : `str`, keyword-only, optional
            The ID of the device this method is targeting. If not
            supplied, the user's currently active device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """

        self._check_scope("toggle_playback_shuffle", "user-modify-playback-state")

        self._request(
            "put",
            f"{self.API_URL}/me/player/shuffle",
            params={"state": state, "device_id": device_id},
        )

    def get_recently_played(
        self, *, limit: int = None, after: int = None, before: int = None
    ) -> dict[str, Any]:
        """
        `Player > Get Recently Played Tracks
        <https://developer.spotify.com/documentation/web-api/reference/
        get-recently-played>`_: Get tracks from the current user's
        recently played tracks.

        .. note::

           Currently doesn't support podcast episodes.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-read-recently-played` scope.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        after : `int`, keyword-only, optional
            A Unix timestamp in milliseconds. Returns all items after
            (but not including) this cursor position. If `after` is
            specified, `before` must not be specified.

            **Example**: :code:`1484811043508`.

        before : `int`, keyword-only, optional
            A Unix timestamp in milliseconds. Returns all items before
            (but not including) this cursor position. If `before` is
            specified, `after` must not be specified.

        Returns
        -------
        tracks : `dict`
            A dictionary containing Spotify catalog information for
            the recently played tracks and the number of results
            returned.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "cursors": {
                      "after": <str>,
                      "before": <str>
                    },
                    "total": <int>,
                    "items": [
                      {
                        "track": {
                          "album": {
                            "album_type": <str>,
                            "total_tracks": <int>,
                            "available_markets": [<str>],
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "images": [
                              {
                                "url": <str>,
                                "height": <int>,
                                "width": <int>
                              }
                            ],
                            "name": <str>,
                            "release_date": <str>,
                            "release_date_precision": <str>,
                            "restrictions": {
                              "reason": <str>
                            },
                            "type": "album",
                            "uri": <str>,
                            "copyrights": [
                              {
                                "text": <str>,
                                "type": <str>
                              }
                            ],
                            "external_ids": {
                              "isrc": <str>,
                              "ean": <str>,
                              "upc": <str>
                            },
                            "genres": [<str>],
                            "label": <str>,
                            "popularity": <int>,
                            "album_group": <str>,
                            "artists": [
                              {
                                "external_urls": {
                                  "spotify": <str>
                                },
                                "href": <str>,
                                "id": <str>,
                                "name": <str>,
                                "type": "artist",
                                "uri": <str>
                              }
                            ]
                          },
                          "artists": [
                            {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "followers": {
                                "href": <str>,
                                "total": <int>
                              },
                              "genres": [<str>],
                              "href": <str>,
                              "id": <str>,
                              "images": [
                                {
                                  "url": <str>,
                                  "height": <int>,
                                  "width": <int>
                                }
                              ],
                              "name": <str>,
                              "popularity": <int>,
                              "type": "artist",
                              "uri": <str>
                            }
                          ],
                          "available_markets": [<str>],
                          "disc_number": <int>,
                          "duration_ms": <int>,
                          "explicit": <bool>,
                          "external_ids": {
                            "isrc": <str>,
                            "ean": <str>,
                            "upc": <str>
                          },
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "is_playable": <bool>
                          "linked_from": {
                          },
                          "restrictions": {
                            "reason": <str>
                          },
                          "name": <str>,
                          "popularity": <int>,
                          "preview_url": <str>,
                          "track_number": <int>,
                          "type": "track",
                          "uri": <str>,
                          "is_local": <bool>
                        },
                        "played_at": <str>,
                        "context": {
                          "type": <str>,
                          "href": <str>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "uri": <str>
                        }
                      }
                    ]
                  }
        """

        self._check_scope("get_recently_played_tracks", "user-read-recently-played")

        return self._get_json(
            f"{self.API_URL}/me/player/recently-played",
            params={"limit": limit, "after": after, "before": before},
        )

    def get_queue(self) -> dict[str, Any]:
        """
        `Player > Get the User's Queue <https://developer.spotify.com/
        documentation/web-api/reference/get-queue>`_: Get the list of
        objects that make up the user's queue.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-read-playback-state` scope.

        Returns
        -------
        queue : `dict`
            Information about the user's queue, such as the currently
            playing item and items in the queue.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "currently_playing": {
                      "album": {
                        "album_type": <str>,
                        "total_tracks": <int>,
                        "available_markets": [<str>],
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "release_date": <str>,
                        "release_date_precision": <str>,
                        "restrictions": {
                          "reason": <str>
                        },
                        "type": "album",
                        "uri": <str>,
                        "copyrights": [
                          {
                            "text": <str>,
                            "type": <str>
                          }
                        ],
                        "external_ids": {
                          "isrc": <str>,
                          "ean": <str>,
                          "upc": <str>
                        },
                        "genres": [<str>],
                        "label": <str>,
                        "popularity": <int>,
                        "album_group": <str>,
                        "artists": [
                          {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "name": <str>,
                            "type": "artist",
                            "uri": <str>
                          }
                        ]
                      },
                      "artists": [
                        {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "followers": {
                            "href": <str>,
                            "total": <int>
                          },
                          "genres": [<str>],
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "popularity": <int>,
                          "type": "artist",
                          "uri": <str>
                        }
                      ],
                      "available_markets": [<str>],
                      "disc_number": <int>,
                      "duration_ms": <int>,
                      "explicit": <bool>,
                      "external_ids": {
                        "isrc": <str>,
                        "ean": <str>,
                        "upc": <str>
                      },
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "is_playable": <bool>
                      "linked_from": {
                      },
                      "restrictions": {
                        "reason": <str>
                      },
                      "name": <str>,
                      "popularity": <int>,
                      "preview_url": <str>,
                      "track_number": <int>,
                      "type": "track",
                      "uri": <str>,
                      "is_local": <bool>
                    },
                    "queue": [
                      {
                        "album": {
                          "album_type": <str>,
                          "total_tracks": <int>,
                          "available_markets": [<str>],
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "restrictions": {
                            "reason": <str>
                          },
                          "type": "album",
                          "uri": <str>,
                          "copyrights": [
                            {
                              "text": <str>,
                              "type": <str>
                            }
                          ],
                          "external_ids": {
                            "isrc": <str>,
                            "ean": <str>,
                            "upc": <str>
                          },
                          "genres": [<str>],
                          "label": <str>,
                          "popularity": <int>,
                          "album_group": <str>,
                          "artists": [
                            {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "href": <str>,
                              "id": <str>,
                              "name": <str>,
                              "type": "artist",
                              "uri": <str>
                            }
                          ]
                        },
                        "artists": [
                          {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "followers": {
                              "href": <str>,
                              "total": <int>
                            },
                            "genres": [<str>],
                            "href": <str>,
                            "id": <str>,
                            "images": [
                              {
                                "url": <str>,
                                "height": <int>,
                                "width": <int>
                              }
                            ],
                            "name": <str>,
                            "popularity": <int>,
                            "type": "artist",
                            "uri": <str>
                          }
                        ],
                        "available_markets": [<str>],
                        "disc_number": <int>,
                        "duration_ms": <int>,
                        "explicit": <bool>,
                        "external_ids": {
                          "isrc": <str>,
                          "ean": <str>,
                          "upc": <str>
                        },
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "is_playable": <bool>
                        "linked_from": {
                        },
                        "restrictions": {
                          "reason": <str>
                        },
                        "name": <str>,
                        "popularity": <int>,
                        "preview_url": <str>,
                        "track_number": <int>,
                        "type": "track",
                        "uri": <str>,
                        "is_local": <bool>
                      }
                    ]
                  }
        """

        self._check_scope("get_user_queue", "user-read-playback-state")

        return self._get_json(f"{self.API_URL}/me/player/queue")

    def add_to_queue(self, uri: str, *, device_id: str = None) -> None:
        """
        `Player > Add Item to Playback Queue
        <https://developer.spotify.com/documentation/web-api/reference/
        add-to-queue>`_: Add an item to the end of the user's current
        playback queue.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-modify-playback-state` scope.

        Parameters
        ----------
        uri : `str`
            The URI of the item to add to the queue. Must be a track or
            an episode URL.

        device_id : `str`, keyword-only, optional
            The ID of the device this method is targeting. If not
            supplied, the user's currently active device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """

        self._check_scope("add_queue_item", "user-modify-playback-state")

        self._request(
            "post",
            f"{self.API_URL}/me/player/queue",
            params={"uri": uri, "device_id": device_id},
        )

    ### PLAYLISTS #############################################################

    def get_playlist(
        self,
        playlist_id: str,
        *,
        additional_types: Union[str, list[str]] = None,
        fields: str = None,
        market: str = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Playlist <https://developer.spotify.com/
        documentation/web-api/reference/get-playlist>`_:
        Get a playlist owned by a Spotify user.

        Parameters
        ----------
        playlist_id : `str`
            The Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        additional_types : `str` or `list`, keyword-only, optional
            A (comma-separated) list of item types besides the default
            track type.

            .. note::

               This parameter was introduced to allow existing clients
               to maintain their current behavior and might be
               deprecated in the future.

            **Valid values**: :code:`"track"` and :code:`"episode"`.

        fields : `str` or `list`, keyword-only, optional
            Filters for the query: a (comma-separated) list of the
            fields to return. If omitted, all fields are returned.
            A dot separator can be used to specify non-reoccurring
            fields, while parentheses can be used to specify reoccurring
            fields within objects. Use multiple parentheses to drill
            down into nested objects. Fields can be excluded by
            prefixing them with an exclamation mark.

            .. container::

               **Examples**:

               * :code:`"description,uri"` to get just the playlist's
                 description and URI,
               * :code:`"tracks.items(added_at,added_by.id)"` to get just
                 the added date and user ID of the adder,
               * :code:`"tracks.items(track(name,href,album(name,href)))"`
                 to drill down into the album, and
               * :code:`"tracks.items(track(name,href,album(!name,href)))"`
                 to exclude the album name.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        playlist : `dict`
            Spotify catalog information for a single playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "collaborative": <bool>,
                    "description": <str>,
                    "external_urls": {
                      "spotify": <str>
                    },
                    "followers": {
                      "href": <str>,
                      "total": <int>
                    },
                    "href": <str>,
                    "id": <str>,
                    "images": [
                      {
                        "url": <str>,
                        "height": <int>,
                        "width": <int>
                      }
                    ],
                    "name": <str>,
                    "owner": {
                      "external_urls": {
                        "spotify": <str>
                      },
                      "followers": {
                        "href": <str>,
                        "total": <int>
                      },
                      "href": <str>,
                      "id": <str>,
                      "type": "user",
                      "uri": <str>,
                      "display_name": <str>
                    },
                    "public": <bool>,
                    "snapshot_id": <str>,
                    "tracks": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "added_at": <str>,
                          "added_by": {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "followers": {
                              "href": <str>,
                              "total": <int>
                            },
                            "href": <str>,
                            "id": <str>,
                            "type": "user",
                            "uri": <str>
                          },
                          "is_local": <bool>,
                          "track": {
                            "album": {
                              "album_type": <str>,
                              "total_tracks": <int>,
                              "available_markets": [<str>],
                              "external_urls": {
                                "spotify": <str>
                              },
                              "href": <str>,
                              "id": <str>,
                              "images": [
                                {
                                  "url": <str>,
                                  "height": <int>,
                                  "width": <int>
                                }
                              ],
                              "name": <str>,
                              "release_date": <str>,
                              "release_date_precision": <str>,
                              "restrictions": {
                                "reason": <str>
                              },
                              "type": "album",
                              "uri": <str>,
                              "copyrights": [
                                {
                                  "text": <str>,
                                  "type": <str>
                                }
                              ],
                              "external_ids": {
                                "isrc": <str>,
                                "ean": <str>,
                                "upc": <str>
                              },
                              "genres": [<str>],
                              "label": <str>,
                              "popularity": <int>,
                              "album_group": <str>,
                              "artists": [
                                {
                                  "external_urls": {
                                    "spotify": <str>
                                  },
                                  "href": <str>,
                                  "id": <str>,
                                  "name": <str>,
                                  "type": "artist",
                                  "uri": <str>
                                }
                              ]
                            },
                            "artists": [
                              {
                                "external_urls": {
                                  "spotify": <str>
                                },
                                "followers": {
                                  "href": <str>,
                                  "total": <int>
                                },
                                "genres": [<str>],
                                "href": <str>,
                                "id": <str>,
                                "images": [
                                  {
                                    "url": <str>,
                                    "height": <int>,
                                    "width": <int>
                                  }
                                ],
                                "name": <str>,
                                "popularity": <int>,
                                "type": "artist",
                                "uri": <str>
                              }
                            ],
                            "available_markets": [<str>],
                            "disc_number": <int>,
                            "duration_ms": <int>,
                            "explicit": <bool>,
                            "external_ids": {
                              "isrc": <str>,
                              "ean": <str>,
                              "upc": <str>
                            },
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "is_playable": <bool>
                            "linked_from": {
                            },
                            "restrictions": {
                              "reason": <str>
                            },
                            "name": <str>,
                            "popularity": <int>,
                            "preview_url": <str>,
                            "track_number": <int>,
                            "type": "track",
                            "uri": <str>,
                            "is_local": <bool>
                          }
                        }
                      ]
                    },
                    "type": <str>,
                    "uri": <str>
                  }
        """

        return self._get_json(
            f"{self.API_URL}/playlists/{playlist_id}",
            params={
                "additional_types": (
                    additional_types
                    if additional_types is None or isinstance(additional_types, str)
                    else ",".join(additional_types)
                ),
                "fields": (
                    fields
                    if fields is None or isinstance(fields, str)
                    else ",".join(fields)
                ),
                "market": market,
            },
        )

    def change_playlist_details(
        self,
        playlist_id: str,
        *,
        name: str = None,
        public: bool = None,
        collaborative: bool = None,
        description: str = None,
    ) -> None:
        """
        `Playlists > Change Playlist Details
        <https://developer.spotify.com/documentation/web-api/reference/
        change-playlist-details>`_: Change a playlist's
        name and public/private state. (The user must, of course, own
        the playlist.)

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`playlist-modify-public` or the
           :code:`playlist-modify-private` scope.

        Parameters
        ----------
        playlist_id : `str`
            The Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        name : `str`, keyword-only, optional
            The new name for the playlist.

            **Example**: :code:`"My New Playlist Title"`.

        public : `bool`, keyword-only, optional
            If :code:`True`, the playlist will be public. If
            :code:`False`, it will be private.

        collaborative : `bool`, keyword-only, optional
            If :code:`True`, the playlist will become collaborative and
            other users will be able to modify the playlist in their
            Spotify client.

            .. note::

               You can only set :code:`collaborative=True` on non-public
               playlists.

        description : `str`, keyword-only, optional
            Value for playlist description as displayed in Spotify
            clients and in the Web API.
        """

        self._check_scope(
            "change_playlist_details",
            "playlist-modify-"
            + ("public" if self.get_playlist(playlist_id)["public"] else "private"),
        )

        json = {}
        if name is not None:
            json["name"] = name
        if public is not None:
            json["public"] = public
        if collaborative is not None:
            json["collaborative"] = collaborative
        if description is not None:
            json["description"] = description
        self._request("put", f"{self.API_URL}/playlists/{playlist_id}", json=json)

    def get_playlist_items(
        self,
        playlist_id: str,
        *,
        additional_types: Union[str, list[str]] = None,
        fields: str = None,
        limit: int = None,
        market: str = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Playlist Items <https://developer.spotify.com/
        documentation/web-api/reference/
        get-playlists-tracks>`_: Get full details of the items of a
        playlist owned by a Spotify user.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`playlist-modify-private` scope.

        Parameters
        ----------
        playlist_id : `str`
            The Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        additional_types : `str` or `list`, keyword-only, optional
            A (comma-separated) list of item types besides the default
            track type.

            .. note::

               This parameter was introduced to allow existing clients
               to maintain their current behavior and might be
               deprecated in the future.

            **Valid values**: :code:`"track"` and :code:`"episode"`.

        fields : `str` or `list`, keyword-only, optional
            Filters for the query: a (comma-separated) list of the
            fields to return. If omitted, all fields are returned.
            A dot separator can be used to specify non-reoccurring
            fields, while parentheses can be used to specify reoccurring
            fields within objects. Use multiple parentheses to drill
            down into nested objects. Fields can be excluded by
            prefixing them with an exclamation mark.

            .. container::

               **Examples**:

               * :code:`"description,uri"` to get just the playlist's
                 description and URI,
               * :code:`"tracks.items(added_at,added_by.id)"` to get just
                 the added date and user ID of the adder,
               * :code:`"tracks.items(track(name,href,album(name,href)))"`
                 to drill down into the album, and
               * :code:`"tracks.items(track(name,href,album(!name,href)))"`
                 to exclude the album name.

        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Default**: :code:`0`.

        Returns
        -------
        items : `dict`
            A dictionary containing Spotify catalog information for the
            playlist items and the number of results returned.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "added_at": <str>,
                        "added_by": {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "followers": {
                            "href": <str>,
                            "total": <int>
                          },
                          "href": <str>,
                          "id": <str>,
                          "type": "user",
                          "uri": <str>
                        },
                        "is_local": <bool>,
                        "track": {
                          "album": {
                            "album_type": <str>,
                            "total_tracks": <int>,
                            "available_markets": [<str>],
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "images": [
                              {
                                "url": <str>,
                                "height": <int>,
                                "width": <int>
                              }
                            ],
                            "name": <str>,
                            "release_date": <str>,
                            "release_date_precision": <str>,
                            "restrictions": {
                              "reason": <str>
                            },
                            "type": "album",
                            "uri": <str>,
                            "copyrights": [
                              {
                                "text": <str>,
                                "type": <str>
                              }
                            ],
                            "external_ids": {
                              "isrc": <str>,
                              "ean": <str>,
                              "upc": <str>
                            },
                            "genres": [<str>],
                            "label": <str>,
                            "popularity": <int>,
                            "album_group": <str>,
                            "artists": [
                              {
                                "external_urls": {
                                  "spotify": <str>
                                },
                                "href": <str>,
                                "id": <str>,
                                "name": <str>,
                                "type": "artist",
                                "uri": <str>
                              }
                            ]
                          },
                          "artists": [
                            {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "followers": {
                                "href": <str>,
                                "total": <int>
                              },
                              "genres": [<str>],
                              "href": <str>,
                              "id": <str>,
                              "images": [
                                {
                                  "url": <str>,
                                  "height": <int>,
                                  "width": <int>
                                }
                              ],
                              "name": <str>,
                              "popularity": <int>,
                              "type": "artist",
                              "uri": <str>
                            }
                          ],
                          "available_markets": [<str>],
                          "disc_number": <int>,
                          "duration_ms": <int>,
                          "explicit": <bool>,
                          "external_ids": {
                            "isrc": <str>,
                            "ean": <str>,
                            "upc": <str>
                          },
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "is_playable": <bool>
                          "linked_from": {
                          },
                          "restrictions": {
                            "reason": <str>
                          },
                          "name": <str>,
                          "popularity": <int>,
                          "preview_url": <str>,
                          "track_number": <int>,
                          "type": "track",
                          "uri": <str>,
                          "is_local": <bool>
                        }
                      }
                    ]
                  }
        """

        self._check_scope("get_playlist_item", "playlist-modify-private")

        return self._get_json(
            f"{self.API_URL}/playlists/{playlist_id}/tracks",
            params={
                "additional_types": (
                    additional_types
                    if additional_types is None or isinstance(additional_types, str)
                    else ",".join(additional_types)
                ),
                "fields": (
                    fields
                    if fields is None or isinstance(fields, str)
                    else ",".join(fields)
                ),
                "limit": limit,
                "market": market,
                "offset": offset,
            },
        )

    def add_playlist_items(
        self, playlist_id: str, uris: Union[str, list[str]], *, position: int = None
    ) -> str:
        """
        `Playlists > Add Items to Playlist
        <https://developer.spotify.com/documentation/web-api/reference/
        add-tracks-to-playlist>`_: Add one or more items to
        a user's playlist.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`playlist-modify-public` or the
           :code:`playlist-modify-private` scope.

        Parameters
        ----------
        playlist_id : `str`
            The Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        uris : `str` or `list`, keyword-only, optional
            A (comma-separated) list of Spotify URIs to add; can be
            track or episode URIs. A maximum of 100 items can be added
            in one request.

            .. note::

               It is likely that passing a large number of item URIs as
               a query parameter will exceed the maximum length of the
               request URI. When adding a large number of items, it is
               recommended to pass them in the request body (as a
               `list`).

            **Example**: :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7Rh,
            spotify:track:1301WleyT98MSxVHPZCA6M,
            spotify:episode:512ojhOuo1ktJprKbVcKyQ"`.

        position : `int`, keyword-only, optional
            The position to insert the items, a zero-based index. If
            omitted, the items will be appended to the playlist. Items
            are added in the order they are listed in the query string
            or request body.

            .. container::

               **Examples**:

               * :code:`0` to insert the items in the first position.
               * :code:`2` to insert the items in the third position.

        Returns
        -------
        snapshot_id : `str`
            The updated playlist's snapshot ID.
        """

        self._check_scope(
            "add_playlist_details",
            "playlist-modify-"
            + ("public" if self.get_playlist(playlist_id)["public"] else "private"),
        )

        if isinstance(uris, str):
            url = f"{self.API_URL}/playlists/{playlist_id}/tracks?{uris=}"
            if position is not None:
                url += f"{position=}"
            return self._request("post", url).json()["snapshot_id"]

        elif isinstance(uris, list):
            json = {"uris": uris}
            if position is not None:
                json["position"] = position
            self._request(
                "post", f"{self.API_URL}/playlists/{playlist_id}/tracks", json=json
            ).json()["snapshot_id"]

    def update_playlist_items(
        self,
        playlist_id: str,
        *,
        uris: Union[str, list[str]] = None,
        range_start: int = None,
        insert_before: int = None,
        range_length: int = 1,
        snapshot_id: str = None,
    ) -> str:
        """
        `Playlists > Update Playlist Items
        <https://developer.spotify.com/documentation/web-api/reference/
        reorder-or-replace-playlists-tracks>`_: Either reorder or
        replace items in a playlist depending on the request's
        parameters.

        To reorder items, include `range_start`, `insert_before`,
        `range_length`, and `snapshot_id` as keyword arguments. To
        replace items, include `uris` as a keyword argument. Replacing
        items in a playlist will overwrite its existing items. This
        operation can be used for replacing or clearing items in a
        playlist.

        .. note::

           Replace and reorder are mutually exclusive operations which
           share the same endpoint, but have different parameters. These
           operations can't be applied together in a single request.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`playlist-modify-public` or the
           :code:`playlist-modify-private` scope.

        Parameters
        ----------
        playlist_id : `str`
            The Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        uris : `str` or `list`, keyword-only, optional
            A (comma-separated) list of Spotify URIs to add; can be
            track or episode URIs. A maximum of 100 items can be added
            in one request.

            .. note::

               It is likely that passing a large number of item URIs as
               a query parameter will exceed the maximum length of the
               request URI. When adding a large number of items, it is
               recommended to pass them in the request body (as a
               `list`).

            **Example**: :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7Rh,
            spotify:track:1301WleyT98MSxVHPZCA6M,
            spotify:episode:512ojhOuo1ktJprKbVcKyQ"`.

        range_start : `int`, keyword-only, optional
            The position of the first item to be reordered.

        insert_before : `int`, keyword-only, optional
            The position where the items should be inserted. To reorder
            the items to the end of the playlist, simply set
            `insert_before` to the position after the last item.

            .. container::

               **Examples**:

               * :code:`range_start=0, insert_before=10` to reorder the
                 first item to the last position in a playlist with 10
                 items, and
               * :code:`range_start=9, insert_before=0` to reorder the
                 last item in a playlist with 10 items to the start of
                 the playlist.

        range_length : `int`, keyword-only, default: :code:`1`
            The amount of items to be reordered. The range of items to
            be reordered begins from the `range_start` position, and
            includes the `range_length` subsequent items.

            **Example**: :code:`range_start=9, range_length=2` to move
            the items at indices 9–10 to the start of the playlist.

        snapshot_id : `str`, keyword-only, optional
            The playlist's snapshot ID against which you want to make
            the changes.

        Returns
        -------
        snapshot_id : `str`
            The updated playlist's snapshot ID.
        """

        self._check_scope(
            "update_playlist_details",
            "playlist-modify-"
            + ("public" if self.get_playlist(playlist_id)["public"] else "private"),
        )

        json = {}
        if snapshot_id is not None:
            json["snapshot_id"] = snapshot_id

        if uris is None:
            if range_start is not None:
                json["range_start"] = range_start
            if insert_before is not None:
                json["insert_before"] = insert_before
            if range_length is not None:
                json["range_length"] = range_length
            return self._request(
                "put", f"{self.API_URL}/playlists/{playlist_id}/tracks", json=json
            ).json()["snapshot_id"]

        elif isinstance(uris, str):
            return self._request(
                "put",
                f"{self.API_URL}/playlists/{playlist_id}/tracks?uris={uris}",
                json=json,
            ).json()["snapshot_id"]

        elif isinstance(uris, list):
            return self._request(
                "put",
                f"{self.API_URL}/playlists/{playlist_id}/tracks",
                json={"uris": uris} | json,
            ).json()["snapshot_id"]

    def remove_playlist_items(
        self, playlist_id: str, tracks: list[str], *, snapshot_id: str = None
    ) -> str:
        """
        `Playlists > Remove Playlist Items
        <https://developer.spotify.com/documentation/web-api/reference/
        remove-tracks-playlist>`_: Remove one or more items from a
        user's playlist.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`playlist-modify-public` or the
           :code:`playlist-modify-private` scope.

        Parameters
        ----------
        playlist_id : `str`
            The Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        tracks : `list`
            A (comma-separated) list containing Spotify URIs of the
            tracks or episodes to remove.

            **Maximum**: 100 items can be added in one request.

            **Example**: :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7Rh,
            spotify:track:1301WleyT98MSxVHPZCA6M,
            spotify:episode:512ojhOuo1ktJprKbVcKyQ"`.

        snapshot_id : `str`, keyword-only, optional
            The playlist's snapshot ID against which you want to make
            the changes. The API will validate that the specified items
            exist and in the specified positions and make the changes,
            even if more recent changes have been made to the playlist.

        Returns
        -------
        snapshot_id : `str`
            The updated playlist's snapshot ID.
        """

        self._check_scope(
            "remove_playlist_items",
            "playlist-modify-"
            + ("public" if self.get_playlist(playlist_id)["public"] else "private"),
        )

        json = {"tracks": tracks}
        if snapshot_id is not None:
            json["snapshot_id"] = snapshot_id
        return self._request(
            "delete", f"{self.API_URL}/playlists/{playlist_id}/tracks", json=json
        ).json()["snapshot_id"]

    def get_personal_playlists(
        self, *, limit: int = None, offset: int = None
    ) -> dict[str, Any]:
        """
        `Playlist > Get Current User's Playlists
        <https://developer.spotify.com/documentation/web-api/reference/
        get-a-list-of-current-users-playlists>`_: Get a list of the
        playlists owned or followed by the current Spotify user.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`playlist-read-private` and the
           :code:`playlist-read-collaborative` scopes.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Default**: :code:`0`.

        Returns
        -------
        playlists : `dict`
            A dictionary containing the current user's playlists and the
            number of results returned.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "collaborative": <bool>,
                        "description": <str>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "owner": {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "followers": {
                            "href": <str>,
                            "total": <int>
                          },
                          "href": <str>,
                          "id": <str>,
                          "type": "user",
                          "uri": <str>,
                          "display_name": <str>
                        },
                        "public": <bool>,
                        "snapshot_id": <str>,
                        "tracks": {
                          "href": <str>,
                          "total": <int>
                        },
                        "type": <str>,
                        "uri": <str>
                      }
                    ]
                  }
        """

        self._check_scope("get_current_user_playlists", "playlist-read-private")
        self._check_scope("get_current_user_playlists", "playlist-read-collaborative")

        return self._get_json(
            f"{self.API_URL}/me/playlists", params={"limit": limit, "offset": offset}
        )

    def get_user_playlists(
        self, user_id: str, *, limit: int = None, offset: int = None
    ) -> dict[str, Any]:
        """
        `Playlist > Get User's Playlists
        <https://developer.spotify.com/documentation/web-api/reference/
        get-list-users-playlists>`_: Get a list of the playlists owned
        or followed by a Spotify user.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`playlist-read-private` and the
           :code:`playlist-read-collaborative` scopes.

        Parameters
        ----------
        user_id : `str`
            The user's Spotify user ID.

            **Example**: :code:`"smedjan"`.

        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Default**: :code:`0`.

        Returns
        -------
        playlists : `dict`
            A dictionary containing the user's playlists and the number
            of results returned.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "collaborative": <bool>,
                        "description": <str>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "owner": {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "followers": {
                            "href": <str>,
                            "total": <int>
                          },
                          "href": <str>,
                          "id": <str>,
                          "type": "user",
                          "uri": <str>,
                          "display_name": <str>
                        },
                        "public": <bool>,
                        "snapshot_id": <str>,
                        "tracks": {
                          "href": <str>,
                          "total": <int>
                        },
                        "type": <str>,
                        "uri": <str>
                      }
                    ]
                  }
        """

        self._check_scope("get_user_playlists", "playlist-read-private")
        self._check_scope("get_user_playlists", "playlist-read-collaborative")

        return self._get_json(
            f"{self.API_URL}/users/{user_id}/playlists",
            params={"limit": limit, "offset": offset},
        )

    def create_playlist(
        self,
        name: str,
        *,
        public: bool = True,
        collaborative: bool = None,
        description: str = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Create Playlist <https://developer.spotify.com/
        documentation/web-api/reference/create-playlist>`_: Create a
        playlist for a Spotify user. (The playlist will be empty until
        you add tracks.)

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`playlist-modify-public` or the
           :code:`playlist-modify-private` scope.

        Parameters
        ----------
        name : `str`
            The name for the new playlist. This name does not need to be
            unique; a user may have several playlists with the same
            name.

            **Example**: :code:`"Your Coolest Playlist"`.

        public : `bool`, keyword-only, default: `True`
            If :code:`True`, the playlist will be public; if
            :code:`False`, it will be private.

            .. note::

               To be able to create private playlists, the user must
               have granted the :code:`playlist-modify-private` scope.

        collaborative : `bool`, keyword-only, optional
            If :code:`True`, the playlist will be collaborative.

            .. note::

               To create a collaborative playlist, you must also set
               `public` to :code:`False`. To create collaborative
               playlists, you must have granted the
               :code:`playlist-modify-private` and
               :code:`playlist-modify-public` scopes.

            **Default**: :code:`False`.

        description : `str`, keyword-only, optional
            The playlist description, as displayed in Spotify Clients
            and in the Web API.

        Returns
        -------
        playlist : `dict`
            Spotify catalog information for the newly created playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "collaborative": <bool>,
                    "description": <str>,
                    "external_urls": {
                      "spotify": <str>
                    },
                    "followers": {
                      "href": <str>,
                      "total": <int>
                    },
                    "href": <str>,
                    "id": <str>,
                    "images": [
                      {
                        "url": <str>,
                        "height": <int>,
                        "width": <int>
                      }
                    ],
                    "name": <str>,
                    "owner": {
                      "external_urls": {
                        "spotify": <str>
                      },
                      "followers": {
                        "href": <str>,
                        "total": <int>
                      },
                      "href": <str>,
                      "id": <str>,
                      "type": "user",
                      "uri": <str>,
                      "display_name": <str>
                    },
                    "public": <bool>,
                    "snapshot_id": <str>,
                    "tracks": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "added_at": <str>,
                          "added_by": {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "followers": {
                              "href": <str>,
                              "total": <int>
                            },
                            "href": <str>,
                            "id": <str>,
                            "type": "user",
                            "uri": <str>
                          },
                          "is_local": <bool>,
                          "track": {
                            "album": {
                              "album_type": <str>,
                              "total_tracks": <int>,
                              "available_markets": [<str>],
                              "external_urls": {
                                "spotify": <str>
                              },
                              "href": <str>,
                              "id": <str>,
                              "images": [
                                {
                                  "url": <str>,
                                  "height": <int>,
                                  "width": <int>
                                }
                              ],
                              "name": <str>,
                              "release_date": <str>,
                              "release_date_precision": <str>,
                              "restrictions": {
                                "reason": <str>
                              },
                              "type": "album",
                              "uri": <str>,
                              "copyrights": [
                                {
                                  "text": <str>,
                                  "type": <str>
                                }
                              ],
                              "external_ids": {
                                "isrc": <str>,
                                "ean": <str>,
                                "upc": <str>
                              },
                              "genres": [<str>],
                              "label": <str>,
                              "popularity": <int>,
                              "album_group": <str>,
                              "artists": [
                                {
                                  "external_urls": {
                                    "spotify": <str>
                                  },
                                  "href": <str>,
                                  "id": <str>,
                                  "name": <str>,
                                  "type": "artist",
                                  "uri": <str>
                                }
                              ]
                            },
                            "artists": [
                              {
                                "external_urls": {
                                  "spotify": <str>
                                },
                                "followers": {
                                  "href": <str>,
                                  "total": <int>
                                },
                                "genres": [<str>],
                                "href": <str>,
                                "id": <str>,
                                "images": [
                                  {
                                    "url": <str>,
                                    "height": <int>,
                                    "width": <int>
                                  }
                                ],
                                "name": <str>,
                                "popularity": <int>,
                                "type": "artist",
                                "uri": <str>
                              }
                            ],
                            "available_markets": [<str>],
                            "disc_number": <int>,
                            "duration_ms": <int>,
                            "explicit": <bool>,
                            "external_ids": {
                              "isrc": <str>,
                              "ean": <str>,
                              "upc": <str>
                            },
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "is_playable": <bool>
                            "linked_from": {
                            },
                            "restrictions": {
                              "reason": <str>
                            },
                            "name": <str>,
                            "popularity": <int>,
                            "preview_url": <str>,
                            "track_number": <int>,
                            "type": "track",
                            "uri": <str>,
                            "is_local": <bool>
                          }
                        }
                      ]
                    },
                    "type": <str>,
                    "uri": <str>
                  }
        """

        self._check_scope(
            "create_playlist", "playlist-modify-" + ("public" if public else "private")
        )

        json = {"name": name, "public": public}
        if collaborative is not None:
            json["collaborative"] = collaborative
        if description is not None:
            json["description"] = description

        return self._request(
            "post", f"{self.API_URL}/users/{self._user_id}/playlists", json=json
        ).json()

    def get_featured_playlists(
        self,
        *,
        country: str = None,
        locale: str = None,
        timestamp: str = None,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Featured Playlists
        <https://developer.spotify.com/documentation/web-api/reference/
        get-featured-playlists>`_: Get a list of Spotify featured
        playlists (shown, for example, on a Spotify player's 'Browse'
        tab).

        Parameters
        ----------
        country : `str`, keyword-only, optional
            A country: an ISO 3166-1 alpha-2 country code. Provide this
            parameter if you want the list of returned items to be
            relevant to a particular country. If omitted, the returned
            items will be relevant to all countries.

            **Example**: :code:`"SE"`.

        locale : `str`, keyword-only, optional
            The desired language, consisting of an ISO 639-1 language
            code and an ISO 3166-1 alpha-2 country code, joined by an
            underscore. Provide this parameter if you want the category
            strings returned in a particular language.

            .. note::

               If `locale` is not supplied, or if the specified language
               is not available, the category strings returned will be
               in the Spotify default language (American English).

            **Example**: :code:`"es_MX"` for "Spanish (Mexico)".

        timestamp : `str`, keyword-only, optional
            A timestamp in ISO 8601 format: yyyy-MM-ddTHH:mm:ss. Use
            this parameter to specify the user's local time to get
            results tailored for that specific date and time in the day.
            If there were no featured playlists (or there is no data) at
            the specified time, the response will revert to the current
            UTC time. If not provided, the response defaults to the
            current UTC time.

            **Example**: :code:`"2014-10-23T09:00:00"` for a user whose
            local time is 9 AM.

        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Default**: :code:`0`.

        Returns
        -------
        playlists : `dict`
            A dictionary containing a message and a list of featured
            playlists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "message": <str>,
                    "playlists": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "collaborative": <bool>,
                          "description": <str>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "owner": {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "followers": {
                              "href": <str>,
                              "total": <int>
                            },
                            "href": <str>,
                            "id": <str>,
                            "type": "user",
                            "uri": <str>,
                            "display_name": <str>
                          },
                          "public": <bool>,
                          "snapshot_id": <str>,
                          "tracks": {
                            "href": <str>,
                            "total": <int>
                          },
                          "type": <str>,
                          "uri": <str>
                        }
                      ]
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/browse/featured-playlists",
            params={
                "country": country,
                "locale": locale,
                "timestamp": timestamp,
                "limit": limit,
                "offset": offset,
            },
        )

    def get_category_playlists(
        self,
        category_id: str,
        *,
        country: str = None,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Category's Playlists
        <https://developer.spotify.com/documentation/web-api/reference/
        get-a-categories-playlists>`_: Get a list of Spotify playlists
        tagged with a particular category.

        Parameters
        ----------
        category_id : `str`
            The Spotify category ID for the category.

            **Example**: :code:`"dinner"`.

        country : `str`, keyword-only, optional
            A country: an ISO 3166-1 alpha-2 country code. Provide this
            parameter to ensure that the category exists for a
            particular country.

            **Example**: :code:`"SE"`.

        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Valid values**: `offset` must be between 0 and 1,000.

            **Default**: :code:`0`.

        Returns
        -------
        playlists : `dict`
            A dictionary containing a message and a list of playlists in
            a particular category.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "message": <str>,
                    "playlists": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "collaborative": <bool>,
                          "description": <str>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "owner": {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "followers": {
                              "href": <str>,
                              "total": <int>
                            },
                            "href": <str>,
                            "id": <str>,
                            "type": "user",
                            "uri": <str>,
                            "display_name": <str>
                          },
                          "public": <bool>,
                          "snapshot_id": <str>,
                          "tracks": {
                            "href": <str>,
                            "total": <int>
                          },
                          "type": <str>,
                          "uri": <str>
                        }
                      ]
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/browse/categories/{category_id}/playlists",
            params={"country": country, "limit": limit, "offset": offset},
        )

    def get_playlist_cover_image(self, playlist_id: str) -> dict[str, Any]:
        """
        `Playlists > Get Playlist Cover Image
        <https://developer.spotify.com/documentation/web-api/reference/
        get-playlist-cover>`_: Get the current image associated with a
        specific playlist.

        Parameters
        ----------
        playlist_id : `str`
            The Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        Returns
        -------
        image : `dict`
            A dictionary containing the URL to and the dimensions of
            the playlist cover image.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "url": <str>,
                    "height": <int>,
                    "width": <int>
                  }
        """

        return self._get_json(f"{self.API_URL}/playlists/{playlist_id}/images")[0]

    def add_playlist_cover_image(self, playlist_id: str, image: bytes) -> None:
        """
        `Playlists > Add Custom Playlist Cover Image
        <https://developer.spotify.com/documentation/web-api/reference/
        upload-custom-playlist-cover>`_: Replace the image used to
        represent a specific playlist.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`ugc-image-upload` and the
           :code:`playlist-modify-public` or
           :code:`playlist-modify-private` scope.

        Parameters
        ----------
        playlist_id : `str`
            The Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        image : `bytes`
            Base64-encoded JPEG image data. The maximum payload size is
            256 KB.
        """

        self._check_scope("get_categories", "ugc-image-upload")
        self._check_scope(
            "get_categories",
            "playlist-modify-"
            + ("public" if self.get_playlist(playlist_id)["public"] else "private"),
        )

        self._request(
            "put",
            f"{self.API_URL}/playlists/{playlist_id}/images",
            data=image,
            headers={"Content-Type": "image/jpeg"},
        )

    ### SEARCH ################################################################

    def search(
        self,
        q: str,
        type: Union[str, list[str]],
        *,
        limit: int = None,
        market: str = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        `Search > Search for Item <https://developer.spotify.com/
        documentation/web-api/reference/search>`_: Get
        Spotify catalog information about albums, artists, playlists,
        tracks, shows, episodes or audiobooks that match a keyword
        string.

        Parameters
        ----------
        q : `str`
            Your search query.

            .. note::

               You can narrow down your search using field filters. The
               available filters are :code:`album`, :code:`artist`,
               :code:`track`, :code:`year`, :code:`upc`,
               :code:`tag:hipster`, :code:`tag:new`, :code:`isrc`, and
               :code:`genre`. Each field filter only applies to certain
               result types.

               The :code:`artist` and :code:`year` filters can be used
               while searching albums, artists and tracks. You can
               filter on a single :code:`year` or a range (e.g.
               1955-1960).

               The :code:`album` filter can be used while searching
               albums and tracks.

               The :code:`genre` filter can be used while searching
               artists and tracks.

               The :code:`isrc` and :code:`track` filters can be used
               while searching tracks.

               The :code:`upc`, :code:`tag:new` and :code:`tag:hipster`
               filters can only be used while searching albums. The
               :code:`tag:new` filter will return albums released in the
               past two weeks and :code:`tag:hipster` can be used to
               return only albums with the lowest 10% popularity.

            **Example**:
            :code:`"remaster track:Doxy artist:Miles Davis"`.

        type : `str` or `list`
            A comma-separated list of item types to search across.
            Search results include hits from all the specified item
            types.

            **Valid values**: :code:`"album"`, :code:`"artist"`,
            :code:`"audiobook"`, :code:`"episode"`, :code:`"playlist"`,
            :code:`"show"`, and :code:`"track"`.

            .. container::

               **Example**:

               * :code:`"track,artist"` returns both tracks and artists
                 matching `query`.
               * :code:`type=album,track` returns both albums and tracks
                 matching `query`.

        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Valid values**: `offset` must be between 0 and 1,000.

            **Default**: :code:`0`.

        Returns
        -------
        results : `dict`
            The search results.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "tracks": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "album": {
                            "album_type": <str>,
                            "total_tracks": <int>,
                            "available_markets": [<str>],
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "images": [
                              {
                                "url": <str>,
                                "height": <int>,
                                "width": <int>
                              }
                            ],
                            "name": <str>,
                            "release_date": <str>,
                            "release_date_precision": <str>,
                            "restrictions": {
                              "reason": <str>
                            },
                            "type": "album",
                            "uri": <str>,
                            "copyrights": [
                              {
                                "text": <str>,
                                "type": <str>
                              }
                            ],
                            "external_ids": {
                              "isrc": <str>,
                              "ean": <str>,
                              "upc": <str>
                            },
                            "genres": [<str>],
                            "label": <str>,
                            "popularity": <int>,
                            "album_group": <str>,
                            "artists": [
                              {
                                "external_urls": {
                                  "spotify": <str>
                                },
                                "href": <str>,
                                "id": <str>,
                                "name": <str>,
                                "type": "artist",
                                "uri": <str>
                              }
                            ]
                          },
                          "artists": [
                            {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "followers": {
                                "href": <str>,
                                "total": <int>
                              },
                              "genres": [<str>],
                              "href": <str>,
                              "id": <str>,
                              "images": [
                                {
                                  "url": <str>,
                                  "height": <int>,
                                  "width": <int>
                                }
                              ],
                              "name": <str>,
                              "popularity": <int>,
                              "type": "artist",
                              "uri": <str>
                            }
                          ],
                          "available_markets": [<str>],
                          "disc_number": <int>,
                          "duration_ms": <int>,
                          "explicit": <bool>,
                          "external_ids": {
                            "isrc": <str>,
                            "ean": <str>,
                            "upc": <str>
                          },
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "is_playable": <bool>
                          "linked_from": {
                          },
                          "restrictions": {
                            "reason": <str>
                          },
                          "name": <str>,
                          "popularity": <int>,
                          "preview_url": <str>,
                          "track_number": <int>,
                          "type": "track",
                          "uri": <str>,
                          "is_local": <bool>
                        }
                      ]
                    },
                    "artists": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "followers": {
                            "href": <str>,
                            "total": <int>
                          },
                          "genres": [<str>],
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "popularity": <int>,
                          "type": "artist",
                          "uri": <str>
                        }
                      ]
                    },
                    "albums": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "album_type": <str>,
                          "total_tracks": <int>,
                          "available_markets": [<str>],
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "restrictions": {
                            "reason": <str>
                          },
                          "type": "album",
                          "uri": <str>,
                          "copyrights": [
                            {
                              "text": <str>,
                              "type": <str>
                            }
                          ],
                          "external_ids": {
                            "isrc": <str>,
                            "ean": <str>,
                            "upc": <str>
                          },
                          "genres": [<str>],
                          "label": <str>,
                          "popularity": <int>,
                          "album_group": <str>,
                          "artists": [
                            {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "href": <str>,
                              "id": <str>,
                              "name": <str>,
                              "type": "artist",
                              "uri": <str>
                            }
                          ]
                        }
                      ]
                    },
                    "playlists": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "collaborative": <bool>,
                          "description": <str>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "owner": {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "followers": {
                              "href": <str>,
                              "total": <int>
                            },
                            "href": <str>,
                            "id": <str>,
                            "type": "user",
                            "uri": <str>,
                            "display_name": <str>
                          },
                          "public": <bool>,
                          "snapshot_id": <str>,
                          "tracks": {
                            "href": <str>,
                            "total": <int>
                          },
                          "type": <str>,
                          "uri": <str>
                        }
                      ]
                    },
                    "shows": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "available_markets": [<str>],
                          "copyrights": [
                            {
                              "text": <str>,
                              "type": <str>
                            }
                          ],
                          "description": <str>,
                          "html_description": <str>,
                          "explicit": <bool>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "is_externally_hosted": <bool>,
                          "languages": [<str>],
                          "media_type": <str>,
                          "name": <str>,
                          "publisher": <str>,
                          "type": "show",
                          "uri": <str>,
                          "total_episodes": <int>
                        }
                      ]
                    },
                    "episodes": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "audio_preview_url": <str>,
                          "description": <str>,
                          "html_description": <str>,
                          "duration_ms": <int>,
                          "explicit": <bool>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "is_externally_hosted": <bool>,
                          "is_playable": <bool>
                          "language": <str>,
                          "languages": [<str>],
                          "name": <str>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "resume_point": {
                            "fully_played": <bool>,
                            "resume_position_ms": <int>
                          },
                          "type": "episode",
                          "uri": <str>,
                          "restrictions": {
                            "reason": <str>
                          }
                        }
                      ]
                    },
                    "audiobooks": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "authors": [
                            {
                              "name": <str>
                            }
                          ],
                          "available_markets": [<str>],
                          "copyrights": [
                            {
                              "text": <str>,
                              "type": <str>
                            }
                          ],
                          "description": <str>,
                          "html_description": <str>,
                          "edition": <str>,
                          "explicit": <bool>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "languages": [<str>],
                          "media_type": <str>,
                          "name": <str>,
                          "narrators": [
                            {
                              "name": <str>
                            }
                          ],
                          "publisher": <str>,
                          "type": "audiobook",
                          "uri": <str>,
                          "total_chapters": <int>
                        }
                      ]
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/search?q={urllib.parse.quote(q)}",
            params={
                "type": type if isinstance(type, str) else ",".join(type),
                "limit": limit,
                "market": market,
                "offset": offset,
            },
        )[f"{type}s"]

    ### SHOWS #################################################################

    def get_show(self, id: str, *, market: str = None) -> dict[str, Any]:
        """
        `Shows > Get Show <https://developer.spotify.com/documentation/
        web-api/reference/get-a-show>`_: Get Spotify
        catalog information for a single show identified by its unique
        Spotify ID.

        Parameters
        ----------
        id : `str`
            The Spotify ID for the show.

            **Example**: :code:`"38bS44xjbVVZ3No3ByF1dJ"`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        show : `dict`
            Spotify catalog information for a single show.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "available_markets": [<str>],
                    "copyrights": [
                      {
                        "text": <str>,
                        "type": <str>
                      }
                    ],
                    "description": <str>,
                    "html_description": <str>,
                    "explicit": <bool>,
                    "external_urls": {
                      "spotify": <str>
                    },
                    "href": <str>,
                    "id": <str>,
                    "images": [
                      {
                        "url": <str>,
                        "height": <int>,
                        "width": <int>
                      }
                    ],
                    "is_externally_hosted": <bool>,
                    "languages": [<str>],
                    "media_type": <str>,
                    "name": <str>,
                    "publisher": <str>,
                    "type": "show",
                    "uri": <str>,
                    "total_episodes": <int>,
                    "episodes": {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>,
                      "items": [
                        {
                          "audio_preview_url": <str>,
                          "description": <str>,
                          "html_description": <str>,
                          "duration_ms": <int>,
                          "explicit": <bool>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "is_externally_hosted": <bool>,
                          "is_playable": <bool>
                          "language": <str>,
                          "languages": [<str>],
                          "name": <str>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "resume_point": {
                            "fully_played": <bool>,
                            "resume_position_ms": <int>
                          },
                          "type": "episode",
                          "uri": <str>,
                          "restrictions": {
                            "reason": <str>
                          }
                        }
                      ]
                    }
                  }
        """

        return self._get_json(f"{self.API_URL}/shows/{id}", params={"market": market})

    def get_shows(
        self, ids: Union[str, list[str]], *, market: str = None
    ) -> list[dict[str, Any]]:
        """
        `Shows > Get Several Shows <https://developer.spotify.com/
        documentation/web-api/reference/
        get-multiple-shows>`_: Get Spotify catalog information for
        several shows based on their Spotify IDs.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the shows.

            **Maximum**: 50 IDs.

            **Example**:
            :code:`"5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ"`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        shows : `list`
            A list containing Spotify catalog information for multiple
            shows.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "available_markets": [<str>],
                      "copyrights": [
                        {
                          "text": <str>,
                          "type": <str>
                        }
                      ],
                      "description": <str>,
                      "html_description": <str>,
                      "explicit": <bool>,
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "images": [
                        {
                          "url": <str>,
                          "height": <int>,
                          "width": <int>
                        }
                      ],
                      "is_externally_hosted": <bool>,
                      "languages": [<str>],
                      "media_type": <str>,
                      "name": <str>,
                      "publisher": <str>,
                      "type": "show",
                      "uri": <str>,
                      "total_episodes": <int>
                    }
                  ]
        """

        return self._get_json(
            f"{self.API_URL}/shows",
            params={
                "ids": ids if isinstance(ids, str) else ",".join(ids),
                "market": market,
            },
        )["shows"]

    def get_show_episodes(
        self, id: str, *, limit: int = None, market: str = None, offset: int = None
    ) -> dict[str, Any]:
        """
        `Shows > Get Show Episodes <https://developer.spotify.com/
        documentation/web-api/reference/
        get-a-shows-episodes>`_: Get Spotify catalog information about
        an show's episodes. Optional parameters can be used to limit the
        number of episodes returned.

        Parameters
        ----------
        id : `str`
            The Spotify ID for the show.

            **Example**: :code:`"38bS44xjbVVZ3No3ByF1dJ"`.

        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Default**: :code:`0`.

        Returns
        -------
        episodes : `dict`
            A dictionary containing Spotify catalog information for a
            show's episodes and the number of results returned.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "audio_preview_url": <str>,
                        "description": <str>,
                        "html_description": <str>,
                        "duration_ms": <int>,
                        "explicit": <bool>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "is_externally_hosted": <bool>,
                        "is_playable": <bool>
                        "language": <str>,
                        "languages": [<str>],
                        "name": <str>,
                        "release_date": <str>,
                        "release_date_precision": <str>,
                        "resume_point": {
                          "fully_played": <bool>,
                          "resume_position_ms": <int>
                        },
                        "type": "episode",
                        "uri": <str>,
                        "restrictions": {
                          "reason": <str>
                        }
                      }
                    ]
                  }
        """

        return self._get_json(
            f"{self.API_URL}/shows/{id}/episodes",
            params={"limit": limit, "market": market, "offset": offset},
        )

    def get_saved_shows(
        self, *, limit: int = None, offset: int = None
    ) -> dict[str, Any]:
        """
        `Shows > Get User's Saved Shows <https://developer.spotify.com/
        documentation/web-api/reference/
        get-users-saved-shows>`_: Get a list of shows saved in the
        current Spotify user's library. Optional parameters can be used
        to limit the number of shows returned.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-read` scope.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Valid values**: `offset` must be between 0 and 1,000.

            **Default**: :code:`0`.

        Returns
        -------
        shows : `dict`
            A dictionary containing Spotify catalog information for a
            user's saved shows and the number of results returned.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "added_at": <str>,
                        "show": {
                          "available_markets": [
                            <str>
                          ],
                          "copyrights": [
                            {
                              "text": <str>,
                              "type": <str>
                            }
                          ],
                          "description": <str>,
                          "html_description": <str>,
                          "explicit": <bool>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "is_externally_hosted": <bool>,
                          "languages": [
                            <str>
                          ],
                          "media_type": <str>,
                          "name": <str>,
                          "publisher": <str>,
                          "type": "show",
                          "uri": <str>,
                          "total_episodes": <int>
                        }
                      }
                    ]
                  }
        """

        self._check_scope("get_saved_shows", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/shows", params={"limit": limit, "offset": offset}
        )

    def save_shows(self, ids: Union[str, list[str]]) -> None:
        """
        `Shows > Save Shows for Current User
        <https://developer.spotify.com/documentation/web-api/reference/
        save-shows-user>`_: Save one or more shows to
        current Spotify user's library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-modify` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the shows.
            Maximum: 50 IDs.

            **Example**:
            :code:`"5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ"`.
        """

        self._check_scope("save_shows", "user-library-modify")

        self._request(
            "put",
            f"{self.API_URL}/me/shows",
            params={"ids": f"{ids if isinstance(ids, str) else ','.join(ids)}"},
        )

    def remove_saved_shows(
        self, ids: Union[str, list[str]], *, market: str = None
    ) -> None:
        """
        `Shows > Remove User's Saved Shows
        <https://developer.spotify.com/documentation/web-api/reference/
        remove-shows-user>`_: Delete one or more shows from
        current Spotify user's library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-modify` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the shows.
            Maximum: 50 IDs.

            **Example**:
            :code:`"5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ"`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.
        """

        self._check_scope("remove_saved_shows", "user-library-modify")

        self._request(
            "delete",
            f"{self.API_URL}/me/shows",
            params={
                "ids": ids if isinstance(ids, str) else ",".join(ids),
                "market": market,
            },
        )

    def check_saved_shows(self, ids: Union[str, list[str]]) -> list[bool]:
        """
        `Shows > Check User's Saved Shows
        <https://developer.spotify.com/documentation/web-api/reference/
        check-users-saved-shows>`_: Check if one or more
        shows is already saved in the current Spotify user's library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-read` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the shows.

            **Maximum**: 50 IDs.

            **Example**:
            :code:`"5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ"`.

        Returns
        -------
        contains : `list`
            Array of booleans specifying whether the shows are found in
            the user's saved shows.

            **Example**: :code:`[False, True]`.
        """

        self._check_scope("check_saved_shows", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/shows/contains",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)},
        )

    ### TRACKS ################################################################

    def get_track(self, id: str, *, market: str = None) -> dict[str, Any]:
        """
        `Tracks > Get Track <https://developer.spotify.com/
        documentation/web-api/reference/get-track>`_: Get
        Spotify catalog information for a single track identified by its
        unique Spotify ID.

        Parameters
        ----------
        id : `str`
            The Spotify ID for the track.

            **Example**: :code:`"11dFghVXANMlKmJXsNCbNl"`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::
               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        track : `dict`
            Spotify catalog information for a single track.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "album": {
                      "album_type": <str>,
                      "total_tracks": <int>,
                      "available_markets": [<str>],
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "images": [
                        {
                          "url": <str>,
                          "height": <int>,
                          "width": <int>
                        }
                      ],
                      "name": <str>,
                      "release_date": <str>,
                      "release_date_precision": <str>,
                      "restrictions": {
                        "reason": <str>
                      },
                      "type": "album",
                      "uri": <str>,
                      "copyrights": [
                        {
                          "text": <str>,
                          "type": <str>
                        }
                      ],
                      "external_ids": {
                        "isrc": <str>,
                        "ean": <str>,
                        "upc": <str>
                      },
                      "genres": [<str>],
                      "label": <str>,
                      "popularity": <int>,
                      "album_group": <str>,
                      "artists": [
                        {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "name": <str>,
                          "type": "artist",
                          "uri": <str>
                        }
                      ]
                    },
                    "artists": [
                      {
                        "external_urls": {
                          "spotify": <str>
                        },
                        "followers": {
                          "href": <str>,
                          "total": <int>
                        },
                        "genres": [<str>],
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "popularity": <int>,
                        "type": "artist",
                        "uri": <str>
                      }
                    ],
                    "available_markets": [<str>],
                    "disc_number": <int>,
                    "duration_ms": <int>,
                    "explicit": <bool>,
                    "external_ids": {
                      "isrc": <str>,
                      "ean": <str>,
                      "upc": <str>
                    },
                    "external_urls": {
                      "spotify": <str>
                    },
                    "href": <str>,
                    "id": <str>,
                    "is_playable": <bool>
                    "linked_from": {
                    },
                    "restrictions": {
                      "reason": <str>
                    },
                    "name": <str>,
                    "popularity": <int>,
                    "preview_url": <str>,
                    "track_number": <int>,
                    "type": "track",
                    "uri": <str>,
                    "is_local": <bool>
                  }
        """

        return self._get_json(f"{self.API_URL}/tracks/{id}", params={"market": market})

    def get_tracks(
        self, ids: Union[int, str, list[Union[int, str]]], *, market: str = None
    ) -> list[dict[str, Any]]:
        """
        `Tracks > Get Several Tracks <https://developer.spotify.com/
        documentation/web-api/reference/
        get-several-tracks>`_: Get Spotify catalog information for
        multiple tracks based on their Spotify IDs.

        Parameters
        ----------
        ids : `int`, `str`, or `list`
            A (comma-separated) list of the Spotify IDs for the tracks.

            **Maximum**: 50 IDs.

            **Example**: :code:`"7ouMYWpwJ422jRcDASZB7P,
            4VqPOruhp5EdPBeR92t6lQ, 2takcwOaAZWiXQijPHIx7B"`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        tracks : `dict` or `list`
            A list containing Spotify catalog information for multiple
            tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "album": {
                        "album_type": <str>,
                        "total_tracks": <int>,
                        "available_markets": [<str>],
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "release_date": <str>,
                        "release_date_precision": <str>,
                        "restrictions": {
                          "reason": <str>
                        },
                        "type": "album",
                        "uri": <str>,
                        "copyrights": [
                          {
                            "text": <str>,
                            "type": <str>
                          }
                        ],
                        "external_ids": {
                          "isrc": <str>,
                          "ean": <str>,
                          "upc": <str>
                        },
                        "genres": [<str>],
                        "label": <str>,
                        "popularity": <int>,
                        "album_group": <str>,
                        "artists": [
                          {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "name": <str>,
                            "type": "artist",
                            "uri": <str>
                          }
                        ]
                      },
                      "artists": [
                        {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "followers": {
                            "href": <str>,
                            "total": <int>
                          },
                          "genres": [<str>],
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "popularity": <int>,
                          "type": "artist",
                          "uri": <str>
                        }
                      ],
                      "available_markets": [<str>],
                      "disc_number": <int>,
                      "duration_ms": <int>,
                      "explicit": <bool>,
                      "external_ids": {
                        "isrc": <str>,
                        "ean": <str>,
                        "upc": <str>
                      },
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "is_playable": <bool>
                      "linked_from": {
                      },
                      "restrictions": {
                        "reason": <str>
                      },
                      "name": <str>,
                      "popularity": <int>,
                      "preview_url": <str>,
                      "track_number": <int>,
                      "type": "track",
                      "uri": <str>,
                      "is_local": <bool>
                    }
                  ]
        """

        return self._get_json(
            f"{self.API_URL}/tracks",
            params={
                "ids": ids if isinstance(ids, str) else ",".join(ids),
                "market": market,
            },
        )["tracks"]

    def get_saved_tracks(
        self, *, limit: int = None, market: str = None, offset: int = None
    ) -> dict[str, Any]:
        """
        `Tracks > Get User's Saved Tracks
        <https://developer.spotify.com/documentation/web-api/reference/
        get-users-saved-tracks>`_: Get a list of the songs
        saved in the current Spotify user's 'Your Music' library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-read` scope.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Valid values**: `offset` must be between 0 and 1,000.

            **Default**: :code:`0`.

        Returns
        -------
        tracks : `dict`
            A dictionary containing Spotify catalog information for a
            user's saved tracks and the number of results returned.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "added_at": <str>,
                        "track": {
                          "album": {
                            "album_type": <str>,
                            "total_tracks": <int>,
                            "available_markets": [<str>],
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "images": [
                              {
                                "url": <str>,
                                "height": <int>,
                                "width": <int>
                              }
                            ],
                            "name": <str>,
                            "release_date": <str>,
                            "release_date_precision": <str>,
                            "restrictions": {
                              "reason": <str>
                            },
                            "type": "album",
                            "uri": <str>,
                            "copyrights": [
                              {
                                "text": <str>,
                                "type": <str>
                              }
                            ],
                            "external_ids": {
                              "isrc": <str>,
                              "ean": <str>,
                              "upc": <str>
                            },
                            "genres": [<str>],
                            "label": <str>,
                            "popularity": <int>,
                            "album_group": <str>,
                            "artists": [
                              {
                                "external_urls": {
                                  "spotify": <str>
                                },
                                "href": <str>,
                                "id": <str>,
                                "name": <str>,
                                "type": "artist",
                                "uri": <str>
                              }
                            ]
                          },
                          "artists": [
                            {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "followers": {
                                "href": <str>,
                                "total": <int>
                              },
                              "genres": [<str>],
                              "href": <str>,
                              "id": <str>,
                              "images": [
                                {
                                  "url": <str>,
                                  "height": <int>,
                                  "width": <int>
                                }
                              ],
                              "name": <str>,
                              "popularity": <int>,
                              "type": "artist",
                              "uri": <str>
                            }
                          ],
                          "available_markets": [<str>],
                          "disc_number": <int>,
                          "duration_ms": <int>,
                          "explicit": <bool>,
                          "external_ids": {
                            "isrc": <str>,
                            "ean": <str>,
                            "upc": <str>
                          },
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "is_playable": <bool>
                          "linked_from": {
                          },
                          "restrictions": {
                            "reason": <str>
                          },
                          "name": <str>,
                          "popularity": <int>,
                          "preview_url": <str>,
                          "track_number": <int>,
                          "type": "track",
                          "uri": <str>,
                          "is_local": <bool>
                        }
                      }
                    ]
                  }
        """

        self._check_scope("get_saved_tracks", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/tracks",
            params={"limit": limit, "market": market, "offset": offset},
        )

    def save_tracks(self, ids: Union[str, list[str]]) -> None:
        """
        `Tracks > Save Track for Current User
        <https://developer.spotify.com/documentation/web-api/reference/
        save-tracks-user>`_: Save one or more tracks to the
        current user's 'Your Music' library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-modify` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the tracks.

            **Maximum**: 50 IDs.

            **Example**: :code:`"7ouMYWpwJ422jRcDASZB7P,
            4VqPOruhp5EdPBeR92t6lQ, 2takcwOaAZWiXQijPHIx7B"`.
        """

        self._check_scope("save_tracks", "user-library-modify")

        if isinstance(ids, str):
            self._request("put", f"{self.API_URL}/me/tracks", params={"ids": ids})
        elif isinstance(ids, list):
            self._request("put", f"{self.API_URL}/me/tracks", json={"ids": ids})

    def remove_saved_tracks(self, ids: Union[str, list[str]]) -> None:
        """
        `Tracks > Remove User's Saved Tracks
        <https://developer.spotify.com/documentation/web-api/reference/
        remove-tracks-user>`_: Remove one or more tracks
        from the current user's 'Your Music' library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-modify` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the tracks.

            **Maximum**: 50 IDs.

            **Example**: :code:`"7ouMYWpwJ422jRcDASZB7P,
            4VqPOruhp5EdPBeR92t6lQ, 2takcwOaAZWiXQijPHIx7B"`.
        """

        self._check_scope("remove_saved_tracks", "user-library-modify")

        if isinstance(ids, str):
            self._request("delete", f"{self.API_URL}/me/tracks", params={"ids": ids})
        elif isinstance(ids, list):
            self._request("delete", f"{self.API_URL}/me/tracks", json={"ids": ids})

    def check_saved_tracks(self, ids: Union[str, list[str]]) -> list[bool]:
        """
        `Tracks > Check User's Saved Tracks
        <https://developer.spotify.com/documentation/web-api/reference/
        check-users-saved-tracks>`_: Check if one or more
        tracks is already saved in the current Spotify user's 'Your
        Music' library.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-library-read` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the tracks.

            **Maximum**: 50 IDs.

            **Example**: :code:`"7ouMYWpwJ422jRcDASZB7P,
            4VqPOruhp5EdPBeR92t6lQ, 2takcwOaAZWiXQijPHIx7B"`.

        Returns
        -------
        contains : `list`
            Array of booleans specifying whether the tracks are found in
            the user's 'Liked Songs'.

            **Example**: :code:`[False, True]`.
        """

        self._check_scope("check_saved_tracks", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/tracks/contains",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)},
        )

    def get_track_audio_features(self, id: str) -> dict[str, Any]:
        """
        `Tracks > Get Track's Audio Features
        <https://developer.spotify.com/documentation/web-api/reference/
        get-audio-features>`_: Get audio feature information for a
        single track identified by its unique Spotify ID.

        Parameters
        ----------
        id : `str`
            The Spotify ID of the track.

            **Example**: :code:`"11dFghVXANMlKmJXsNCbNl"`.

        Returns
        -------
        audio_features : `dict`
            The track's audio features.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "acousticness": <float>,
                    "analysis_url": <str>,
                    "danceability": <float>,
                    "duration_ms": <int>,
                    "energy": <float>,
                    "id": <str>,
                    "instrumentalness": <float>,
                    "key": <int>,
                    "liveness": <float>,
                    "loudness": <float>,
                    "mode": <int>,
                    "speechiness": <float>,
                    "tempo": <float>,
                    "time_signature": <int>,
                    "track_href": <str>,
                    "type": "audio_features",
                    "uri": <str>,
                    "valence": <float>,
                  }
        """

        return self._get_json(f"{self.API_URL}/audio-features/{id}")

    def get_tracks_audio_features(
        self, ids: Union[str, list[str]]
    ) -> list[dict[str, Any]]:
        """
        `Tracks > Get Tracks' Audio Features
        <https://developer.spotify.com/documentation/web-api/reference/
        get-several-audio-features>`_: Get audio features
        for multiple tracks based on their Spotify IDs.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the Spotify IDs for the tracks.

            **Maximum**: 100 IDs.

            **Example**: :code:`"7ouMYWpwJ422jRcDASZB7P,
            4VqPOruhp5EdPBeR92t6lQ, 2takcwOaAZWiXQijPHIx7B"`.

        Returns
        -------
        audio_features : `dict` or `list`
            A list containing audio features for multiple tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "acousticness": <float>,
                      "analysis_url": <str>,
                      "danceability": <float>,
                      "duration_ms": <int>,
                      "energy": <float>,
                      "id": <str>,
                      "instrumentalness": <float>,
                      "key": <int>,
                      "liveness": <float>,
                      "loudness": <float>,
                      "mode": <int>,
                      "speechiness": <float>,
                      "tempo": <float>,
                      "time_signature": <int>,
                      "track_href": <str>,
                      "type": "audio_features",
                      "uri": <str>,
                      "valence": <float>,
                    }
                  ]
        """

        return self._get_json(
            f"{self.API_URL}/audio-features",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)},
        )["audio_features"]

    def get_track_audio_analysis(self, id: str) -> dict[str, Any]:
        """
        `Tracks > Get Track's Audio Analysis
        <https://developer.spotify.com/documentation/web-api/reference/
        get-audio-analysis>`_: Get a low-level audio
        analysis for a track in the Spotify catalog. The audio analysis
        describes the track's structure and musical content, including
        rhythm, pitch, and timbre.

        Parameters
        ----------
        id : `str`
            The Spotify ID of the track.

            **Example**: :code:`"11dFghVXANMlKmJXsNCbNl"`.

        Returns
        -------
        audio_analysis : `dict`
            The track's audio analysis.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "meta": {
                      "analyzer_version": <str>,
                      "platform": <str>,
                      "detailed_status": <str>,
                      "status_code": <int>,
                      "timestamp": <int>,
                      "analysis_time": <float>,
                      "input_process": <str>
                    },
                    "track": {
                      "num_samples": <int>,
                      "duration": <float>,
                      "sample_md5": <str>,
                      "offset_seconds": <int>,
                      "window_seconds": <int>,
                      "analysis_sample_rate": <int>,
                      "analysis_channels": <int>,
                      "end_of_fade_in": <int>,
                      "start_of_fade_out": <float>,
                      "loudness": <float>,
                      "tempo": <float>,
                      "tempo_confidence": <float>,
                      "time_signature": <int>,
                      "time_signature_confidence": <float>,
                      "key": <int>,
                      "key_confidence": <float>,
                      "mode": <int>,
                      "mode_confidence": <float>,
                      "codestring": <str>,
                      "code_version": <float>,
                      "echoprintstring": <str>,
                      "echoprint_version": <float>,
                      "synchstring": <str>,
                      "synch_version": <int>,
                      "rhythmstring": <str>,
                      "rhythm_version": <int>
                    },
                    "bars": [
                      {
                        "start": <float>,
                        "duration": <float>,
                        "confidence": <float>
                      }
                    ],
                    "beats": [
                      {
                        "start": <float>,
                        "duration": <float>,
                        "confidence": <float>
                      }
                    ],
                    "sections": [
                      {
                        "start": <float>,
                        "duration": <float>,
                        "confidence": <float>,
                        "loudness": <float>,
                        "tempo": <float>,
                        "tempo_confidence": <float>,
                        "key": <int>,
                        "key_confidence": <float>,
                        "mode": <int>,
                        "mode_confidence": <float>,
                        "time_signature": <int>,
                        "time_signature_confidence": <float>
                      }
                    ],
                    "segments": [
                      {
                        "start": <float>,
                        "duration": <float>,
                        "confidence": <float>,
                        "loudness_start": <float>,
                        "loudness_max": <float>,
                        "loudness_max_time": <float>,
                        "loudness_end": <int>,
                        "pitches": [<float>],
                        "timbre": [<float>]
                      }
                    ],
                    "tatums": [
                      {
                        "start": <float>,
                        "duration": <float>,
                        "confidence": <float>
                      }
                    ]
                  }
        """

        return self._get_json(f"{self.API_URL}/audio-analysis/{id}")

    def get_recommendations(
        self,
        seed_artists: Union[str, list[str]] = None,
        seed_genres: Union[str, list[str]] = None,
        seed_tracks: Union[str, list[str]] = None,
        *,
        limit: int = None,
        market: str = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """
        `Tracks > Get Recommendations <https://developer.spotify.com/
        documentation/web-api/reference/
        get-recommendations>`_: Recommendations are generated based on
        the available information for a given seed entity and matched
        against similar artists and tracks. If there is sufficient
        information about the provided seeds, a list of tracks will be
        returned together with pool size details.

        For artists and tracks that are very new or obscure, there might
        not be enough data to generate a list of tracks.

        .. important::

           Spotify content may not be used to train machine learning or
           AI models.

        Parameters
        ----------
        seed_artists : `str`, optional
            A comma separated list of Spotify IDs for seed artists.

            **Maximum**: Up to 5 seed values may be provided in any
            combination of `seed_artists`, `seed_tracks`, and
            `seed_genres`.

            **Example**: :code:`"4NHQUGzhtTLFvgF5SZesLK"`.

        seed_genres : `str`, optional
            A comma separated list of any genres in the set of available
            genre seeds.

            **Maximum**: Up to 5 seed values may be provided in any
            combination of `seed_artists`, `seed_tracks`, and
            `seed_genres`.

            **Example**: :code:`"classical,country"`.

        seed_tracks : `str`, optional
            A comma separated list of Spotify IDs for a seed track.

            **Maximum**: Up to 5 seed values may be provided in any
            combination of `seed_artists`, `seed_tracks`, and
            `seed_genres`.

            **Example**: :code:`"0c6xIDDpzE81m2q797ordA"`.

        limit : `int`, keyword-only, optional
            The target size of the list of recommended tracks. For seeds
            with unusually small pools or when highly restrictive
            filtering is applied, it may be impossible to generate the
            requested number of recommended tracks. Debugging
            information for such cases is available in the response.

            **Minimum**: :code:`1`.

            **Maximum**: :code:`100`.

            **Default**: :code:`20`.

        market : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If a country code is
            specified, only content that is available in that market
            will be returned. If a valid user access token is specified
            in the request header, the country associated with the user
            account will take priority over this parameter.

            .. note::

               If neither market or user country are provided, the
               content is considered unavailable for the client.

            **Example**: :code:`"ES"`.

        **kwargs
            Tunable track attributes. For a list of available options,
            see the `Spotify Web API Reference page for this endpoint
            <https://developer.spotify.com/documentation/web-api/
            reference/get-recommendations>`_.

        Returns
        -------
        tracks : `dict`
            A dictionary containing Spotify catalog information for the
            recommended tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "seeds": [
                      {
                        "afterFilteringSize": <int>,
                        "afterRelinkingSize": <int>,
                        "href": <str>,
                        "id": <str>,
                        "initialPoolSize": <int>,
                        "type": <str>
                      }
                    ],
                    "tracks": [
                      {
                        "album": {
                          "album_type": <str>,
                          "total_tracks": <int>,
                          "available_markets": [<str>],
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "restrictions": {
                            "reason": <str>
                          },
                          "type": "album",
                          "uri": <str>,
                          "copyrights": [
                            {
                              "text": <str>,
                              "type": <str>
                            }
                          ],
                          "external_ids": {
                            "isrc": <str>,
                            "ean": <str>,
                            "upc": <str>
                          },
                          "genres": [<str>],
                          "label": <str>,
                          "popularity": <int>,
                          "album_group": <str>,
                          "artists": [
                            {
                              "external_urls": {
                                "spotify": <str>
                              },
                              "href": <str>,
                              "id": <str>,
                              "name": <str>,
                              "type": "artist",
                              "uri": <str>
                            }
                          ]
                        },
                        "artists": [
                          {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "followers": {
                              "href": <str>,
                              "total": <int>
                            },
                            "genres": [<str>],
                            "href": <str>,
                            "id": <str>,
                            "images": [
                              {
                                "url": <str>,
                                "height": <int>,
                                "width": <int>
                              }
                            ],
                            "name": <str>,
                            "popularity": <int>,
                            "type": "artist",
                            "uri": <str>
                          }
                        ],
                        "available_markets": [<str>],
                        "disc_number": <int>,
                        "duration_ms": <int>,
                        "explicit": <bool>,
                        "external_ids": {
                          "isrc": <str>,
                          "ean": <str>,
                          "upc": <str>
                        },
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "is_playable": <bool>
                        "linked_from": {
                        },
                        "restrictions": {
                          "reason": <str>
                        },
                        "name": <str>,
                        "popularity": <int>,
                        "preview_url": <str>,
                        "track_number": <int>,
                        "type": "track",
                        "uri": <str>,
                        "is_local": <bool>
                      }
                    ]
                  }
        """

        return self._get_json(
            f"{self.API_URL}/recommendations",
            params={
                "seed_artists": (
                    seed_artists
                    if seed_artists is None or isinstance(seed_artists, str)
                    else ",".join(seed_artists)
                ),
                "seed_genres": (
                    seed_genres
                    if seed_genres is None or isinstance(seed_genres, str)
                    else ",".join(seed_genres)
                ),
                "seed_tracks": (
                    seed_tracks
                    if seed_tracks is None or isinstance(seed_tracks, str)
                    else ",".join(seed_tracks)
                ),
                "limit": limit,
                "market": market,
                **kwargs,
            },
        )

    ### USERS #################################################################

    def get_profile(self) -> dict[str, Any]:
        """
        `Users > Get Current User's Profile
        <https://developer.spotify.com/documentation/web-api/reference/
        get-current-users-profile>`_: Get detailed profile
        information about the current user (including the current user's
        username).

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-read-private` scope.

        Returns
        -------
        user : `dict`
            A dictionary containing the current user's information.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "country": <str>,
                    "display_name": <str>,
                    "email": <str>,
                    "explicit_content": {
                      "filter_enabled": <bool>,
                      "filter_locked": <bool>
                    },
                    "external_urls": {
                      "spotify": <str>
                    },
                    "followers": {
                      "href": <str>,
                      "total": <int>
                    },
                    "href": <str>,
                    "id": <str>,
                    "images": [
                      {
                        "url": <str>,
                        "height": <int>,
                        "width": <int>
                      }
                    ],
                    "product": <str>,
                    "type": <str>,
                    "uri": <str>
                  }
        """

        self._check_scope("get_profile", "user-read-private")

        return self._get_json(f"{self.API_URL}/me")

    def get_top_items(
        self,
        type: str,
        *,
        limit: int = None,
        offset: int = None,
        time_range: str = None,
    ) -> dict[str, Any]:
        """
        `Users > Get User's Top Items <https://developer.spotify.com/
        documentation/web-api/reference/
        get-users-top-artists-and-tracks>`_: Get the current user's top
        artists or tracks based on calculated affinity.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-top-read` scope.

        Parameters
        ----------
        type : `str`
            The type of entity to return.

            **Valid values**: :code:`"artists"` and :code:`"tracks"`.

        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of search results.

            **Default**: :code:`0`.

        time_range : `str`, keyword-only, optional
            Over what time frame the affinities are computed.

            .. container::

               **Valid values**:

               * :code:`"long_term"` (calculated from several years of
                 data and including all new data as it becomes
                 available).
               * :code:`"medium_term"` (approximately last 6 months).
               * :code:`"short_term"` (approximately last 4 weeks).

            **Default**: :code:`"medium_term"`.

        Returns
        -------
        items : `dict`
            A dictionary containing Spotify catalog information for a
            user's top items and the number of results returned.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>,
                    "items": [
                      {
                        "external_urls": {
                          "spotify": <str>
                        },
                        "followers": {
                          "href": <str>,
                          "total": <int>
                        },
                        "genres": [<str>],
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "url": <str>,
                            "height": <int>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "popularity": <int>,
                        "type": <str>,
                        "uri": <str>
                      }
                    ]
                  }
        """

        if type not in (TYPES := {"artists", "tracks"}):
            raise ValueError(
                f"Invalid entity type ({type=}). " f"Valid values: {', '.join(TYPES)}."
            )

        self._check_scope("get_top_items", "user-top-read")

        return self._get_json(
            f"{self.API_URL}/me/top/{type}",
            params={"limit": limit, "offset": offset, "time_range": time_range},
        )

    def get_user_profile(self, user_id: str) -> dict[str, Any]:
        """
        `Users > Get User's Profile <https://developer.spotify.com/
        documentation/web-api/reference/
        get-users-profile>`_: Get public profile information about a
        Spotify user.

        Parameters
        ----------
        user_id : `str`
            The user's Spotify user ID.

            **Example**: :code:`"smedjan"`

        Returns
        -------
        user : `dict`
            A dictionary containing the user's information.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "display_name": <str>,
                    "external_urls": {
                      "spotify": <str>
                    },
                    "followers": {
                      "href": <str>,
                      "total": <int>
                    },
                    "href": <str>,
                    "id": <str>,
                    "images": [
                      {
                        "url": <str>,
                        "height": <int>,
                        "width": <int>
                      }
                    ],
                    "type": "user",
                    "uri": <str>
                  }
        """

        return self._get_json(f"{self.API_URL}/users/{user_id}")

    def follow_playlist(self, playlist_id: str) -> None:
        """
        `Users > Follow Playlist <https://developer.spotify.com/
        documentation/web-api/reference/follow-playlist>`_:
        Add the current user as a follower of a playlist.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`playlist-modify-private` scope.

        Parameters
        ----------
        playlist_id : `str`
            The Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`
        """

        self._check_scope("follow_playlist", "playlist-modify-private")

        self._request("put", f"{self.API_URL}/playlists/{playlist_id}/followers")

    def unfollow_playlist(self, playlist_id: str) -> None:
        """
        `Users > Unfollow Playlist <https://developer.spotify.com/
        documentation/web-api/reference/
        unfollow-playlist>`_: Remove the current user as a follower of a
        playlist.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`playlist-modify-private` scope.

        Parameters
        ----------
        playlist_id : `str`
            The Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`
        """

        self._check_scope("unfollow_playlist", "playlist-modify-private")

        self._request("delete", f"{self.API_URL}/playlists/{playlist_id}/followers")

    def get_followed_artists(
        self, *, after: str = None, limit: int = None
    ) -> dict[str, Any]:
        """
        `Users > Get Followed Artists <https://developer.spotify.com/
        documentation/web-api/reference/get-followed>`_:
        Get the current user's followed artists.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-follow-read` scope.

        Parameters
        ----------
        after : `str`, keyword-only, optional
            The last artist ID retrieved from the previous request.

            **Example**: :code:`"0I2XqVXqHScXjHhk6AYYRe"`

        limit : `int`, keyword-only, optional
            The maximum number of results to return in each item type.

            **Valid values**: `limit` must be between 0 and 50.

            **Default**: :code:`20`.

        Returns
        -------
        artists : `dict`
            A dictionary containing Spotify catalog information for a
            user's followed artists and the number of results returned.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                      "href": <str>,
                      "limit": <int>,
                      "next": <str>,
                      "cursors": {
                        "after": <str>,
                        "before": <str>
                      },
                      "total": <int>,
                      "items": [
                        {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "followers": {
                            "href": <str>,
                            "total": <int>
                          },
                          "genres": [<str>],
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "url": <str>,
                              "height": <int>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "popularity": <int>,
                          "type": "artist",
                          "uri": <str>
                        }
                      ]
                    }
        """

        self._check_scope("get_followed_artists", "user-follow-read")

        return self._get_json(
            f"{self.API_URL}/me/following",
            params={"type": "artist", "after": after, "limit": limit},
        )["artists"]

    def follow_people(self, ids: Union[str, list[str]], type: str) -> None:
        """
        `Users > Follow Artists or Users <https://developer.spotify.com/
        documentation/web-api/reference/
        follow-artists-users>`_: Add the current user as a follower of
        one or more artists or other Spotify users.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-follow-modify` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the artist or user Spotify IDs.

            **Maximum**: Up to 50 IDs can be sent in one request.

            **Example**: :code:`"2CIMQHirSU0MQqyYHq0eOx,
            57dN52uHvrHOxijzpIgu3E, 1vCWHaC5f2uS3yhpwWbIA6"`.

        type : `str`
            The ID type.

            **Valid values**: :code:`"artist"` and :code:`"user"`.
        """

        self._check_scope("follow_people", "user-follow-modify")

        if isinstance(ids, str):
            self._request(
                "put", f"{self.API_URL}/me/following", params={"ids": ids, "type": type}
            )
        elif isinstance(ids, list):
            self._request(
                "put",
                f"{self.API_URL}/me/following",
                json={"ids": ids},
                params={"type": type},
            )

    def unfollow_people(self, ids: Union[str, list[str]], type: str) -> None:
        """
        `Users > Unfollow Artists or Users
        <https://developer.spotify.com/documentation/web-api/reference/
        unfollow-artists-users>`_: Remove the current user
        as a follower of one or more artists or other Spotify users.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-follow-modify` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the artist or user Spotify IDs.

            **Maximum**: Up to 50 IDs can be sent in one request.

            **Example**: :code:`"2CIMQHirSU0MQqyYHq0eOx,
            57dN52uHvrHOxijzpIgu3E, 1vCWHaC5f2uS3yhpwWbIA6"`.

        type : `str`
            The ID type.

            **Valid values**: :code:`"artist"` and :code:`"user"`.
        """

        self._check_scope("unfollow_people", "user-follow-modify")

        if isinstance(ids, str):
            self._request(
                "delete",
                f"{self.API_URL}/me/following",
                params={"ids": ids, "type": type},
            )
        elif isinstance(ids, list):
            self._request(
                "delete",
                f"{self.API_URL}/me/following",
                json={"ids": ids},
                params={"type": type},
            )

    def check_followed_people(
        self, ids: Union[str, list[str]], type: str
    ) -> list[bool]:
        """
        `Users > Check If User Follows Artists or Users
        <https://developer.spotify.com/documentation/web-api/reference/
        check-current-user-follows>`_: Check to see if the
        current user is following one or more artists or other Spotify
        users.

        .. admonition:: Authorization scope
           :class: warning

           Requires the :code:`user-follow-read` scope.

        Parameters
        ----------
        ids : `str` or `list`
            A (comma-separated) list of the artist or user Spotify IDs.

            **Maximum**: Up to 50 IDs can be sent in one request.

            **Example**: :code:`"2CIMQHirSU0MQqyYHq0eOx,
            57dN52uHvrHOxijzpIgu3E, 1vCWHaC5f2uS3yhpwWbIA6"`.

        type : `str`
            The ID type.

            **Valid values**: :code:`"artist"` and :code:`"user"`.

        Returns
        -------
        contains : `list`
            Array of booleans specifying whether the user follows the
            specified artists or Spotify users.

            **Example**: :code:`[False, True]`.
        """

        self._check_scope("check_followed_people", "user-follow-read")

        return self._get_json(
            f"{self.API_URL}/me/following/contains",
            params={
                "ids": ids if isinstance(ids, str) else ",".join(ids),
                "type": type,
            },
        )

    def check_playlist_followers(
        self, playlist_id: str, ids: Union[str, list[str]]
    ) -> list[bool]:
        """
        `Users > Check If Users Follow Playlist
        <https://developer.spotify.com/documentation/web-api/reference/
        check-if-user-follows-playlist>`_: Check to see if
        one or more Spotify users are following a specified playlist.

        Parameters
        ----------
        playlist_id : `str`
            The Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        ids : `str` or `list`
            A (comma-separated) list of Spotify user IDs; the IDs of the
            users that you want to check to see if they follow the
            playlist.

            **Maximum**: 5 IDs.

            **Example**: :code:`"jmperezperez,thelinmichael,wizzler"`.

        Returns
        -------
        follows : `list`
            Array of booleans specifying whether the users follow the
            playlist.

            **Example**: :code:`[False, True]`.
        """

        return self._get_json(
            f"{self.API_URL}/playlists/{playlist_id}/followers/contains",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)},
        )
