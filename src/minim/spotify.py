"""
:mod:`minim.spotify` -- Spotify Web and Lyrics APIs
===================================================
.. moduleauthor:: Benjamin Ye <GitHub: @bbye98>

This module contains a complete Python implementation of the Spotify Web
API and a minimal implementation of the Spotify Lyrics API.

The public Spotify Web API allows media (albums, tracks, etc.) and
artists to be queried and information about them to be retrieved, as
well as user information (playlists, profile, etc.) to be retrieved and
updated. 

.. seealso::
   For more information, see the `Spotify Web API Reference
   <https://developer.spotify.com/documentation/web-api/reference/#/>`_.

Using the Spotify Web API requires OAuth 2.0 authentication. Valid
client credentials—a client ID and a client secret—must either be 
provided explicitly to the :class:`WebAPISession` constructor or be 
stored in the operating system's environment variables as 
:code:`SPOTIFY_CLIENT_ID` and :code:`SPOTIFY_CLIENT_SECRET`,
respectively. Alternatively, an access token (and optionally, its
accompanying expiry time and refresh token) can be provided to the
:class:`WebAPISession` constructor to bypass the authorization flow.

.. note::
   This module supports the `authorization code 
   <https://developer.spotify.com/documentation/general/guides/
   authorization/code-flow/>`_ and `client credentials 
   <https://developer.spotify.com/documentation/general/guides/
   authorization/client-credentials/>`_ flows.

.. seealso::
   To get client credentials, see the `guide on how to create a new
   Spotify app <https://developer.spotify.com/documentation/general/
   guides/authorization/app-settings/>`_.

The private Spotify Lyrics API, which is powered by Musixmatch, provides
line- or word-synced (if available) lyrics for Spotify tracks. As the
Spotify Lyrics API is not public, there is no available documentation
for it, and its endpoints have been determined by watching HTTP network
traffic.

Using the Spotify Lyrics API requires the :code:`sp_dc` cookie, which
must either be provided explicitly to the :class:`LyricsAPISession` 
constructor or be stored in the operating system's environment variables
as :code:`SPOTIFY_SP_DC`. Alternatively, an access token can be provided
to the :class:`LyricsAPISession` constructor to bypass the token 
exchange.
"""

from abc import abstractmethod
import base64
import datetime
import multiprocessing
import os
import pickle
import re
import requests
import tempfile
import time
from typing import Any, Union
import urllib
import webbrowser

try:
    from flask import Flask, request
    FOUND_FLASK = True
except:
    FOUND_FLASK = False

try:
    from playwright.sync_api import sync_playwright
    FOUND_PLAYWRIGHT = True
except:
    FOUND_PLAYWRIGHT = False

TEMP_DIR = tempfile.gettempdir()

def _file_exists(
        event: multiprocessing.Event, filename: Union[str, bytes, os.PathLike]
    ) -> None:

    """
    Check if a file exists.

    Parameters
    ----------
    event : `multiprocessing.Event`
        An indicator of whether the file has been created or found.

    filename : `str`, `bytes`, or `os.PathLike`
        Filename.
    """
    
    while True:
        if os.path.isfile(filename):
            event.set()
            break
        time.sleep(0.1)

class _Session:

    """
    An abstract Spotify API session.
    """

    def __init__(self):

        """
        Create an abstract Spotify API session.
        """
        
        self.session = requests.Session()

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

    @abstractmethod
    def _request(self):
        pass

class LyricsAPISession(_Session):

    """
    A Spotify Lyrics API session.

    Parameters
    ----------
    sp_dc : `str`, keyword-only, optional
        Spotify Web Player :code:`sp_dc` cookie.

    access_token : `str`, keyword-only, optional
        Access token. If provided, the token exchange is bypassed.

    expiry : `datetime.datetime`, keyword-only, optional
        Expiry time of `access_token`. If provided, the user will be
        reauthenticated using the default authorization flow (if
        possible) when `access_token` expires.

    Attributes
    ----------
    API_URL : `str`
        URL for the Spotify Lyrics API.

    TOKEN_URL : `str`
        URL for access token requests.

    session : `requests.Session`
        A session object with persisting headers.
    """

    API_URL = "https://spclient.wg.spotify.com/color-lyrics/v2/track"
    TOKEN_URL = "https://open.spotify.com/get_access_token"

    def __init__(
            self, *, sp_dc: str = None, access_token: str = None,
            expiry: datetime.datetime = None) -> None:

        """
        Create a Spotify Lyrics API session.
        """
        
        super().__init__()
        self.session.headers.update({"App-Platform": "WebPlayer"})

        self.sp_dc = os.environ.get("SPOTIFY_SP_DC") if sp_dc is None else sp_dc
        if access_token is None:
            self._get_access_token()
        else:
            self.session.headers.update(
                {"Authorization": f"Bearer {access_token}"}
            )
            self._expiry = expiry

    def _get_access_token(self) -> None:

        """
        Get Spotify Lyrics API access token.
        """

        resp = requests.get(
            self.TOKEN_URL,
            headers={"cookie": f"sp_dc={self.sp_dc}"},
            params={"reason": "transport", "productType": "web_player"}
        ).json()

        if resp["isAnonymous"]:
            raise ValueError("Invalid 'sp_dc' cookie.")
        
        self.session.headers.update(
            {"Authorization": f"Bearer {resp['accessToken']}"}
        )
        self._expiry = datetime.datetime.fromtimestamp(
            resp["accessTokenExpirationTimestampMs"] / 1000
        )
    
    def _request(self, method: str, url: str, **kwargs) -> requests.Response:

        """
        Construct and send a request, but with status code checking.

        Parameters
        ----------
        method : `str`
            Method for the request.

        url : `str`
            URL for the request.

        **kwargs
            Keyword arguments passed to :meth:`requests.request`.

        Returns
        -------
        resp : `requests.Response`
            Response to the request.
        """

        if self._expiry is not None and datetime.datetime.now() > self._expiry:
            self._get_access_token()

        resp = self.session.request(method, url, **kwargs)
        if resp.status_code != 200:
            emsg = f"{resp.status_code} {resp.reason}"
            if resp.status_code == 401:
                print(emsg)
                self._get_access_token()
                return self._request(method, url, **kwargs)
            else:
                raise RuntimeError(emsg)
        return resp

    def get_lyrics(self, id: str) -> dict[str, Any]:

        """
        Get lyrics for a Spotify track.

        Parameters
        ----------
        id : `str`
            The Spotify ID for the track.

            **Example**: :code:`"11dFghVXANMlKmJXsNCbNl"`.

        Returns
        -------
        lyrics : `dict`
            Formatted or time-synced lyrics.
        """

        return self._get_json(f"{self.API_URL}/{id}",
                              params={"format": "json",
                                      "market": "from_token"})

class WebAPISession(_Session):

    """
    A Spotify Web API session.

    Parameters
    ----------
    client_id : `str`, keyword-only, optional
        Client ID. If it is not stored as :code:`SPOTIFY_CLIENT_ID` in
        the operating system's environment variables, it must be
        provided here.
    
    client_secret : `str`, keyword-only, optional
        Client secret key. If it is not stored as
        :code:`SPOTIFY_CLIENT_SECRET` in the operating system's
        environment variables, it must be provided here.

    flow : `str`, keyword-only, optional
        Authorization flow.

        .. container::

           **Valid values**:
           
           * :code:`authorization_code` for the authorization code flow.
           * :code:`client_credentials` for the client credentials flow.

           **Default**: :code:`client_credentials`.
    
    browser : `bool`, keyword-only, default: :code:`True`
        Determines whether a web browser is automatically opened and the
        authorization code is automatically retrieved for the
        authorization code flow. If :code:`False`, users will have to
        manually open the generated URL and provide the full callback
        URI via the terminal.

        .. note::
           Either Flask or Playwright must be installed if
           :code:`browser=True`. The `backend` keyword argument can
           be used to specify which backend is used for authorization
           code retrieval.

    backend : `str`, keyword-only, default: :code:`"flask"`
        Backend used for authorization code retrieval when 
        :code:`browser=True`.

        .. container::

           **Valid values**:
           
           * :code:`flask` for the Flask web application framework.
           * :code:`playwright` for the Playwright library by Microsoft.

    scope : `str` or `list`, keyword-only, optional
        Authorization scopes to request user access for in the
        authorization code flow.
    
    access_token : `str`, keyword-only, optional
        Access token. If provided, the authorization flow is completely
        bypassed.
    
    refresh_token : `str`, keyword-only, optional
        Refresh token accompanying `access_token`. If not provided, the
        user will be reauthenticated using the default authorization
        flow when `access_token` expires.
        
    expiry : `datetime.datetime`, keyword-only, optional
        Expiry time of `access_token`. If provided, the user will be
        reauthenticated using `refresh_token` (if available) or the
        default authorization flow (if possible) when `access_token`
        expires.

    Attributes
    ----------
    API_URL : `str`
        URL for the Spotify Web API.

    AUTH_URL : `str`
        URL for authorization code requests.
        
    TOKEN_URL : `str`
        URL for access token requests.

    REDIRECT_URL : `str`
        Redirect URL for the authorization code flow.

    session : `requests.Session`
        A session object with persisting headers.
    """

    _OAUTH_FLOWS = {"authorization_code", "client_credentials"}
    _SCOPES = {
        "images": ["ugc-image-upload"],
        "connect": ["user-read-playback-state", "user-modify-playback-state",
                    "user-read-currently-playing"],
        "playback": ["app-remote-control streaming"],
        "playlists": ["playlist-read-private", "playlist-read-collaborative",
                      "playlist-modify-private", "playlist-modify-public"],
        "follow": ["user-follow-modify", "user-follow-read"],
        "history": ["user-read-playback-position", "user-top-read",
                    "user-read-recently-played"],
        "library": ["user-library-modify", "user-library-read"],
        "users": ["user-read-email", "user-read-private"]
    }

    API_URL = "https://api.spotify.com/v1"
    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    REDIRECT_URI = "http://localhost:8888/callback"

    @classmethod
    def get_scopes(self, categories: Union[str, list[str]]) -> str:

        """
        Get Spotify authorization scopes for the specified categories.

        .. container::

           **Valid values**:

           * :code:`"images"`: Scopes related to images.

             * :code:`ugc-image-upload`

           * :code:`"connect"`: Scopes related to Spotify Connect.

             * :code:`user-read-playback-state`
             * :code:`user-modify-playback-state`
             * :code:`user-read-currently-playing`

           * :code:`"playback"`: Scopes related to playback.

             * :code:`app-remote-control`
             * :code:`streaming`

           * :code:`"playlists"`: Scopes related to modifying and reading 
             playlists.

             * :code:`playlist-read-private`
             * :code:`playlist-read-collaborative`
             * :code:`playlist-modify-private`
             * :code:`playlist-modify-public`

           * :code:`"follow`: Scopes related to following artists and other
             users.

             * :code:`user-follow-modify`
             * :code:`user-follow-read`

           * :code:`"history"`: Scopes related to a user's listening 
             history.

             * :code:`user-read-playback-position`
             * :code:`user-top-read`
             * :code:`user-read-recently-played`

           * :code:`"library"`: Scopes related to modifying and reading
             a user's library.

             * :code:`user-library-modify`
             * :code:`user-library-read`

           * :code:`"users"`: Scopes related to accessing a user's 
             information.

             * :code:`user-read-email`
             * :code:`user-read-private`

           * :code:`"all"`: All scopes above.
           * :code:`"read"`: All scopes above that grant read access.
           * :code:`"modify"`: All scopes above that grant modify access.

        .. seealso::
           For the endpoints that the scopes allow access to, see the
           `Authorization Scopes page of the Spotify Web API Reference
           <https://developer.spotify.com/documentation/general/guides/
           authorization/scopes/>`_.
        """
        
        if isinstance(categories, str):
            if categories == "all":
                return " ".join(s for c in self._SCOPES.values() for s in c)
            if categories == "read":
                return " ".join(s for c in self._SCOPES.values() for s in c
                                if "read" in s)
            if categories == "modify":
                return " ".join(s for c in self._SCOPES.values() for s in c
                                if "modify" in s)
            return self._SCOPES[categories]
        
        return " ".join(s for c in (self.get_scopes[c] for c in categories)
                        for s in c)

    def __init__(
            self, *, client_id: str = None, client_secret: str = None,
            flow: str = "client_credentials", browser: bool = True, 
            backend: str = "flask", scopes: Union[str, list[str]] = None, 
            access_token: str = None, refresh_token: str = None, 
            expiry: datetime.datetime = None):

        """
        Create a Spotify Web API session.
        """

        super().__init__()

        if flow not in self._OAUTH_FLOWS:
            raise ValueError("Invalid OAuth 2.0 authorization flow.")
        self._flow = flow

        if access_token is None:
            self._client_id = os.environ.get("SPOTIFY_CLIENT_ID") \
                              if client_id is None else client_id
            self._client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET") \
                                  if client_secret is None else client_secret
            self._browser = browser
            self._backend = backend
            if flow == "authorization_code" and self._browser:
                if (self._backend == "flask" and not FOUND_FLASK) or \
                        (self._backend == "playwright" and not FOUND_PLAYWRIGHT):
                    print(f"The {self._backend.capitalize()} library "
                          "was not found, so the automatic "
                          "authorization code retrieval is not "
                          "available.")
                    self._browser = False
            self._scopes = " ".join(scopes) if isinstance(scopes, list) \
                           else scopes
            self._get_access_token()
        else:
            self.session.headers.update(
                {"Authorization": f"Bearer {access_token}"}
            )
            self._refresh_token = refresh_token
            self._expiry = expiry

        try:
            self._me = self.get_current_user_profile()
        except:
            pass

    def __repr__(self):

        """
        Set the string representation of the Spotify Web API object.
        """

        if hasattr(self, "_me"):
            return (f"Spotify Web API: user {self._me['display_name']} "
                    f"(ID: {self._me['id']}, email: {self._me['email']})")
        
        return f"<minim.spotify.WebAPISession object at 0x{id(self):x}>"

    def _get_access_token(self) -> None:

        """
        Get Spotify Web API access token.
        """

        if self._client_id is None or self._client_secret is None:
            raise ValueError("Spotify Web API client credentials not "
                             "provided.")
        
        if self._flow == "authorization_code":
            auth_code = self._get_authorization_code()
            self._client64 = base64.b64encode(
                f"{self._client_id}:{self._client_secret}".encode("ascii")
            ).decode("ascii")

            resp = requests.post(
                self.TOKEN_URL,
                data={"code": auth_code, "grant_type": "authorization_code",
                      "redirect_uri": self.REDIRECT_URI},
                headers={"Authorization": f"Basic {self._client64}"}
            ).json()

            self.session.headers.update(
                {"Authorization": f"{resp['token_type']} {resp['access_token']}"}
            )
            self._refresh_token = resp["refresh_token"]
            self._expiry = datetime.datetime.now() \
                           + datetime.timedelta(0, resp["expires_in"])
            
        elif self._flow == "client_credentials":
            resp = requests.post(
                self.TOKEN_URL,
                data={"client_id": self._client_id,
                      "client_secret": self._client_secret,
                      "grant_type": "client_credentials"}
            ).json()

            self.session.headers.update(
                {"Authorization": f"{resp['token_type']} {resp['access_token']}"}
            )
            self._refresh_token = None
            self._expiry = datetime.datetime.now() \
                            + datetime.timedelta(0, resp["expires_in"])

    def _get_authorization_code(self) -> str:

        """
        Get an authorization code to be exchanged for an access token 
        for the Spotify Web API.

        Returns
        -------
        auth_code : `str`
            Authorization code.
        """

        params = {"client_id": os.environ.get("SPOTIFY_CLIENT_ID"),
                  "response_type": "code",
                  "redirect_uri": self.REDIRECT_URI}
        if self._scopes:
            params["scope"] = self._scopes

        auth_url = f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

        if self._browser:
            if self._backend == "flask":
                webbrowser.open(auth_url)

                app = Flask(__name__)
                pickle_file = f"{TEMP_DIR}/spotify.pickle"
                @app.route("/callback", methods=["GET"])
                def _callback() -> str:
                    with open(pickle_file, "wb") as f:
                        pickle.dump(request.args, f)
                    if "error" in request.args:
                        return "Access denied. You may close this page now."
                    return "Access granted. You may close this page now."

                event = multiprocessing.Event()
                server = multiprocessing.Process(target=app.run, 
                                                 args=("0.0.0.0", 8888))
                server.start()
                check = multiprocessing.Process(target=_file_exists, 
                                                args=(event, pickle_file))
                check.start()
                while True:
                    if event.is_set():
                        check.terminate()
                        server.terminate()
                        break
                    time.sleep(0.1)

                with open(pickle_file, "rb") as f:
                    queries = pickle.load(f)
                os.remove(pickle_file)
            
            elif self._backend == "playwright":
                har_file = f"{TEMP_DIR}/spotify.har"
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(headless=False)
                    context = browser.new_context(record_har_path=har_file)
                    page = context.new_page()
                    page.goto(auth_url, timeout=0)
                    try:
                        page.wait_for_url(f"{self.REDIRECT_URI}*", 
                                          wait_until="networkidle")
                    except:
                        pass
                    context.close()
                    browser.close()

                with open(har_file, "r") as f:
                    har = f.read()
                os.remove(har_file)
                queries = dict(
                    urllib.parse.parse_qsl(
                        urllib.parse.urlparse(
                            re.search(f'{self.REDIRECT_URI}\?(.*?)"', har).group(0)
                        ).query
                    )
                )

        else:
            print("To grant Minim access to Spotify data and features, "
                  "open the following link in your web browser:\n\n"
                  f"{auth_url}\n")
            uri = input("After authorizing Minim to access Spotify on "
                        "your behalf, copy and paste the URI in the "
                        "address bar of your web browser beginning "
                        f"with '{self.REDIRECT_URI}' below.\n\nURI: ")
            queries = dict(
                urllib.parse.parse_qsl(urllib.parse.urlparse(uri).query)
            )

        if "error" in queries:
            raise RuntimeError(f"Authorization failed. Error: {queries['error']}")
        return queries["code"]
    
    def _refresh_access_token(self) -> None:

        """
        Refresh the expired excess token.
        """

        if self._refresh_token is None:
            self._get_access_token()
        else:
            resp = requests.post(
                self.TOKEN_URL,
                data={"grant_type": "refresh_token",
                      "refresh_token": self._refresh_token},
                headers={"Authorization": f"Basic {self._client64}"}
            ).json()
            self.session.headers.update(
                {"Authorization": f"{resp['token_type']} {resp['access_token']}"}
            )
            self._expiry = datetime.datetime.now() \
                          + datetime.timedelta(0, resp["expires_in"])
    
    def _request(self, method: str, url: str, **kwargs) -> requests.Response:

        """
        Construct and send a request, but with status code checking.

        Parameters
        ----------
        method : `str`
            Method for the request.

        url : `str`
            URL for the request.

        **kwargs
            Keyword arguments passed to :meth:`requests.request`.

        Returns
        -------
        resp : `requests.Response`
            Response to the request.
        """

        if self._expiry is not None and datetime.datetime.now() > self._expiry:
            self._refresh_access_token()

        resp = self.session.request(method, url, **kwargs)
        if resp.status_code not in range(200, 299):
            error = resp.json()["error"]
            emsg = f"{error['status']} {error['message']}"
            if resp.status_code == 401:
                print(emsg)
                self._get_access_token()
                return self._request(method, url, **kwargs)
            else:
                raise RuntimeError(emsg)
        return resp

    def _check_scope(self, method: str, scope: str) -> None:

        """
        Check if the user has granted the appropriate authorization
        scope for the desired method call.

        Parameters
        ----------
        method : `str`
            Spotify Web API method/endpoint.

        scope : `str`
            Required scope for `method`.
        """

        if self._scopes is None or not scope in self._scopes:
            emsg = (f"spotify.WebAPISession.{method}() requires the "
                    f"'{scope}' authorization scope.")
            raise RuntimeError(emsg)

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
            Spotify catalog information for a single album in JSON
            format.
        """

        return self._get_json(f"{self.API_URL}/albums/{id}",
                              params={"market": market})

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
            A list of Spotify catalog information for multiple albums in
            JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/albums",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids),
                    "market": market}
        )["albums"]

    def get_album_tracks(
            self, id: str, *, limit: int = None, market: str = None,
            offset: int = None) -> dict[str, Any]:

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
            A dictionary containing the Spotify catalog information for
            an album's tracks and the number of results returned.
        """

        return self._get_json(
            f"{self.API_URL}/albums/{id}/tracks",
            params={"limit": limit, "market": market, "offset": offset}
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
            A dictionary containing the Spotify catalog information for
            a user's saved albums and the number of results returned.
        """

        self._check_scope("get_saved_albums", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/albums",
            params={"limit": limit, "market": market, "offset": offset}
        )

    def save_albums(self, ids: Union[str, list[str]]) -> None:
        
        """
        `Albums > Save Albums for Current User
        <https://developer.spotify.com/documentation/web-api/reference/
        save-albums-user>`_: Save one or more albums to the
        current user's 'Your Music' library.
        
        .. admonition:: Authorization scope
        
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
            self._request("put", f"{self.API_URL}/me/albums", 
                          params={"ids": ids})
        elif isinstance(ids, list):
            self._request("put", f"{self.API_URL}/me/albums",
                          json={"ids": ids})

    def remove_saved_albums(self, ids: Union[str, list[str]]) -> None:

        """
        `Albums > Remove Users' Saved Albums
        <https://developer.spotify.com/documentation/web-api/reference/
        remove-albums-user>`_: Remove one or more albums
        from the current user's 'Your Music' library.
        
        .. admonition:: Authorization scope
        
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
            self._request("delete", f"{self.API_URL}/me/albums",
                          params={"ids": ids})
        elif isinstance(ids, list):
            self._request("delete", f"{self.API_URL}/me/albums",
                          json={"ids": ids})

    def check_saved_albums(self, ids: Union[str, list[str]]) -> list[bool]:
        
        """
        `Albums > Check User's Saved Albums
        <https://developer.spotify.com/documentation/web-api/reference/
        check-users-saved-albums>`_: Check if one or more
        albums is already saved in the current Spotify user's 'Your
        Music' library.
        
        .. admonition:: Authorization scope
        
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
        """

        self._check_scope("check_saved_albums", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/albums/contains",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)}
        )

    def get_new_releases(
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
            A list of newly-released albums in JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/browse/new-releases",
            params={"country": country, "limit": limit, "offset": offset}
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
            Spotify catalog information for a single artist in JSON
            format.
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
            A list of Spotify catalog information for multiple artists
            in JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/artists",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)}
        )["artists"]

    def get_artist_albums(
            self, id: str, *, include_groups: Union[str, list[str]] = None,
            limit: int = None, market: str = None, offset: int = None
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
            A list of the artist's albums in JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/artists/{id}/albums",
            params={"include_groups": include_groups, "limit": limit,
                    "market": market, "offset": offset}
        )

    def get_artist_top_tracks(
            self, id: str, *, market: str = None) -> list[dict[str, Any]]:

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
        tracks : `list`
            A list of the artist's top tracks in JSON format.
        """

        return self._get_json(f"{self.API_URL}/artists/{id}/top-tracks",
                             params={"market": market})

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
            A list of the artist's related artists in JSON format.
        """

        return self._get_json(f"{self.API_URL}/artists/{id}/related-artists")

    ### AUDIOBOOKS ############################################################

    def get_audiobook(self, id: str, *, market: str = None) -> dict[str, Any]:

        """
        `Audiobooks > Get an Audiobook
        <https://developer.spotify.com/documentation/web-api/reference/
        get-an-audiobook>`_: Get Spotify catalog
        information for a single audiobook.

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
            Spotify catalog information for a single audiobook in JSON
            format.
        """

        return self._get_json(f"{self.API_URL}/audiobooks/{id}",
                              params={"market": market})

    def get_audiobooks(
            self, ids: Union[int, str, list[Union[int, str]]], *,
            market: str = None) -> list[dict[str, Any]]:
        
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
            A list of Spotify catalog information for multiple
            audiobooks in JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/audiobooks",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids),
                    "market": market}
        )["audiobooks"]

    def get_audiobook_chapters(
            self, id: str, *, limit: int = None, market: str = None,
            offset: int = None) -> dict[str, Any]:

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
            A dictionary containing the Spotify catalog information for
            an audiobook's chapters and the number of results returned.
        """

        return self._get_json(
            f"{self.API_URL}/audiobooks/{id}/chapters",
            params={"limit": limit, "market": market, "offset": offset}
        )

    def get_saved_audiobooks(
            self, *, limit: int = None, offset: int = None) -> dict[str, Any]:

        """
        `Audiobooks > Get User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference/
        get-users-saved-audiobooks>`_: Get a list of the
        albums saved in the current Spotify user's audiobooks library.
        
        .. admonition:: Authorization scope
        
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
            A dictionary containing the Spotify catalog information for
            a user's saved audiobooks and the number of results
            returned.
        """

        self._check_scope("get_saved_audiobooks", "user-library-read")

        return self._get_json(f"{self.API_URL}/me/audiobooks",
                              params={"limit": limit, "offset": offset})

    def save_audiobooks(self, ids: Union[str, list[str]]) -> None:

        """
        `Audiobooks > Save Audiobooks for Current User
        <https://developer.spotify.com/documentation/web-api/reference/
        save-audiobooks-user>`_: Save one or more
        audiobooks to current Spotify user's library.
        
        .. admonition:: Authorization scope
        
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
            "put", f"{self.API_URL}/me/audiobooks",
            params={"ids": f"{ids if isinstance(ids, str) else ','.join(ids)}"}
        )

    def remove_saved_audiobooks(self, ids: Union[str, list[str]]) -> None:

        """
        `Audiobooks > Remove User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference/
        remove-audiobooks-user>`_: Delete one or more
        audiobooks from current Spotify user's library.
        
        .. admonition:: Authorization scope
        
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
            "delete", f"{self.API_URL}/me/audiobooks",
            params={"ids": f"{ids if isinstance(ids, str) else ','.join(ids)}"}
        )

    def check_saved_audiobooks(self, ids: Union[str, list[str]]) -> list[bool]:

        """
        `Audiobooks > Check User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference/
        check-users-saved-audiobooks>`_: Check if one or
        more audiobooks are already saved in the current Spotify user's
        library.
        
        .. admonition:: Authorization scope
        
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
        """

        self._check_scope("check_saved_audiobooks", "user-library-read")
        
        return self._get_json(
            f"{self.API_URL}/me/audiobooks/contains",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)}
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
            Spotify catalog information for a single category in JSON
            format.
        """
        
        return self._get_json(
            f"{self.API_URL}/browse/categories/{category_id}",
            params={"country": country, "locale": locale}
        )
    
    def get_categories(
            self, *, country: str = None, limit: int = None,
            locale: str = None, offset: int = None) -> dict[str, Any]:
        
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
            A dictionary containing the Spotify catalog information for
            the browse categories and the number of results returned.
        """
        
        return self._get_json(
            f"{self.API_URL}/browse/categories",
            params={"country": country, "limit": limit, "locale": locale,
                    "offset": offset}
        )["categories"]

    ### CHAPTERS ##############################################################

    def get_chapter(self, id: str, *, market: str) -> dict[str, Any]:

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
            Spotify catalog information for a single chapter in JSON
            format.
        """

        return self._get_json(f"{self.API_URL}/chapters/{id}",
                              params={"market": market})

    def get_chapters(
            self, ids: Union[int, str, list[Union[int, str]]], *,
            market: str = None) -> list[dict[str, Any]]:
        
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
        chapters : `dict` or `list`
            A list of Spotify catalog information for multiple chapters
            in JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/chapters",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids),
                    "market": market}
        )["chapters"]

    ### EPISODES ##############################################################

    def get_episode(self, id: str, *, market: str) -> dict[str, Any]:

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
            Spotify catalog information for a single episode in JSON
            format.
        """

        return self._get_json(f"{self.API_URL}/episodes/{id}",
                             params={"market": market})

    def get_episodes(
            self, ids: Union[int, str, list[Union[int, str]]], *,
            market: str = None) -> list[dict[str, Any]]:
        
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
        episodes : `dict` or `list`
            A list of Spotify catalog information for multiple episodes in
            JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/episodes",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids),
                    "market": market}
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
            A dictionary containing the Spotify catalog information for
            a user's saved episodes and the number of results returned.
        """

        self._check_scope("get_saved_episodes", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/episodes",
            params={"limit": limit, "market": market, "offset": offset}
        )

    def save_episodes(self, ids: Union[str, list[str]]) -> None:

        """
        `Episodes > Save Episodes for Current User 
        <https://developer.spotify.com/documentation/web-api/reference/
        save-episodes-user>`_: Save one or more episodes to
        the current user's library.
        
        .. admonition:: Authorization scope
        
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
            self._request("put", f"{self.API_URL}/me/episodes",
                          params={"ids": ids})
        elif isinstance(ids, list):
            self._request("put", f"{self.API_URL}/me/episodes", 
                          json={"ids": ids})

    def remove_saved_episodes(self, ids: Union[str, list[str]]) -> None:

        """
        `Episodes > Remove User's Saved Episodes
        <https://developer.spotify.com/documentation/web-api/reference/
        remove-episodes-user>`_: Remove one or more
        episodes from the current user's library.
        
        .. admonition:: Authorization scope
        
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
            self._request("delete", f"{self.API_URL}/me/episodes",
                          params={"ids": ids})
        elif isinstance(ids, list):
            self._request("delete", f"{self.API_URL}/me/episodes", 
                          json={"ids": ids})

    def check_saved_episodes(self, ids: Union[str, list[str]]) -> list[bool]:

        """
        `Episodes > Check User's Saved Episodes
        <https://developer.spotify.com/documentation/web-api/reference/
        check-users-saved-episodes>`_: Check if one or more
        episodes is already saved in the current Spotify user's 'Your
        Episodes' library.
        
        .. admonition:: Authorization scope
        
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
        """

        self._check_scope("check_saved_episodes", "user-library-read")
        
        return self._get_json(
            f"{self.API_URL}/me/episodes/contains",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)}
        )

    ### GENRES ################################################################

    def get_genre_seeds(self) -> list[str]:

        """
        `Genres > Get Available Genre Seeds
        <https://developer.spotify.com/documentation/web-api/reference/
        get-recommendation-genres>`_: Retrieve a list of
        available genres seed parameter values for use in
        :meth:`WebAPISession.get_recommendations`.

        Returns
        -------
        genres : `list`
            Array of genres.
        """
        
        return self._get_json(
            f"{self.API_URL}/recommendations/available-genre-seeds"
        )["genres"]

    ### MARKETS ##############################################################

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
        """
        
        self._check_scope("get_playback_state", "user-read-playback-state")

        return self._get_json(f"{self.API_URL}/me/player",
                              params={"market": market, 
                                      "additional_types": additional_types})
    
    def transfer_playback(
            self, device_ids: Union[str, list[str]], *, play: bool = None
        ) -> None:

        """
        `Player > Transfer Playback <https://developer.spotify.com/
        documentation/web-api/reference/transfer-a-users-playback>`_: 
        Transfer playback to a new device and determine if it should 
        start playing.

        .. admonition:: Authorization scope
        
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

        json = {"device_ids": [device_ids] if isinstance(device_ids, str)
                              else device_ids}
        if play is not None:
            json["play"] = play
        self._request("put", f"{self.API_URL}/me/player", json=json)
    
    def get_available_devices(self) -> list[dict[str, Any]]:

        """
        `Player > Get Available Devices <https://developer.spotify.com/
        documentation/web-api/reference/
        get-a-users-available-devices>`_: Get information about a user's
        available devices.
        
        .. admonition:: Authorization scope
        
           Requires the :code:`user-read-playback-state` scope.

        Returns
        -------
        devices : `list`
            A list containing information about the available devices.
        """

        self._check_scope("get_available_devices", "user-read-playback-state")

        self._get_json(f"{self.API_URL}/me/player/devices")
    
    def get_currently_playing_item(
            self, *, market: str = None, additional_types: str = None
        ) -> dict[str, Any]:

        """
        `Player > Get Currently Playing Track 
        <https://developer.spotify.com/documentation/web-api/reference/
        get-the-users-currently-playing-track>`_: Get the object 
        currently being played on the user's Spotify account.

        .. admonition:: Authorization scope
        
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
        """
        
        self._check_scope("get_currently_playing_item", 
                          "user-read-currently-playing")
        
        self._get_json(f"{self.API_URL}/me/player/currently-playing",
                       params={"market": market, 
                               "additional_types": additional_types})
    
    def start_playback(
            self, *, device_id: str = None, context_uri: str = None,
            uris: list[str] = None, offset: dict[str, Any], 
            position_ms: int = None) -> None:
        
        """
        `Player > Start/Resume Playback <https://developer.spotify.com/
        documentation/web-api/reference/start-a-users-playback>`_: Start
        a new context or resume current playback on the user's active 
        device.

        .. admonition:: Authorization scope
        
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
               * :code:`{"uri": "spotify:track:1301WleyT98MSxVHPZCA6M"}`
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

        self._request("put", f"{self.API_URL}/me/player/play",
                      params={"device_id": device_id}, json=json)
    
    def pause_playback(self, *, device_id: str = None) -> None:

        """
        `Player > Pause Playback <https://developer.spotify.com/
        documentation/web-api/reference/pause-a-users-playback>`_: Pause
        playback on the user's account.

        .. admonition:: Authorization scope
        
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

        self._request("put", f"{self.API_URL}/me/player/pause",
                      params={"device_id": device_id})
    
    def skip_to_next(self, *, device_id: str = None) -> None:

        """
        `Player > Skip To Next <https://developer.spotify.com/
        documentation/web-api/reference/
        skip-users-playback-to-next-track>`_: Skips to next track in the
        user's queue.

        .. admonition:: Authorization scope
        
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

        self._request("post", f"{self.API_URL}/me/player/next",
                      params={"device_id": device_id})

    def skip_to_previous(self, *, device_id: str = None) -> None:

        """
        `Player > Skip To Previous <https://developer.spotify.com/
        documentation/web-api/reference/
        skip-users-playback-to-previous-track>`_: Skips to previous 
        track in the user's queue.

        .. admonition:: Authorization scope
        
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

        self._request("post", f"{self.API_URL}/me/player/previous",
                      params={"device_id": device_id})

    def seek_to_position(
            self, position_ms: int, *, device_id: str = None) -> None:

        """
        `Player > Seek To Position <https://developer.spotify.com/
        documentation/web-api/reference/
        seek-to-position-in-currently-playing-track>`_: Seeks to the
        given position in the user's currently playing track.

        .. admonition:: Authorization scope
        
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
        
        self._request("put", f"{self.API_URL}/me/player/seek",
                      params={"position_ms": position_ms, 
                              "device_id": device_id})
    
    def set_repeat_mode(self, state: str, *, device_id: str = None) -> None:

        """
        `Player > Set Repeat Mode <https://developer.spotify.com/
        documentation/web-api/reference/
        set-repeat-mode-on-users-playback>`_: Set the repeat mode for 
        the user's playback. Options are repeat-track, repeat-context,
        and off.

        .. admonition:: Authorization scope
        
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

        self._request("put", f"{self.API_URL}/me/player/repeat",
                      params={"state": state, "device_id": device_id})
    
    def set_playback_volume(
            self, volume_percent: int, *, device_id: str = None) -> None:
        
        """
        `Player > Set Playback Volume <https://developer.spotify.com/
        documentation/web-api/reference/
        set-volume-for-users-playback>`_: Set the volume for the user's
        current playback device.

        .. admonition:: Authorization scope
        
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

        self._request("put", f"{self.API_URL}/me/player/volume",
                      params={"volume_percent": volume_percent,
                              "device_id": device_id})
    
    def toggle_playback_shuffle(
            self, state: bool, *, device_id: str = None) -> None:
        
        """
        `Player > Toggle Playback Shuffle
        <https://developer.spotify.com/documentation/web-api/reference/
        toggle-shuffle-for-users-playback>`_: Toggle shuffle on or off
        for user's playback.

        .. admonition:: Authorization scope
        
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
        
        self._check_scope("toggle_playback_shuffle", 
                          "user-modify-playback-state")

        self._request("put", f"{self.API_URL}/me/player/shuffle",
                      params={"state": state, "device_id": device_id})
    
    def get_recently_played_tracks(
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
            A dictionary containing the Spotify catalog information for
            the recently played tracks and the number of results 
            returned.
        """
        
        self._check_scope("get_recently_played_tracks", 
                          "user-read-recently-played")
        
        return self._get_json(f"{self.API_URL}/me/player/recently-played",
                              params={"limit": limit, "after": after, 
                                      "before": before})
    
    def get_user_queue(self) -> dict[str, Any]:

        """
        `Player > Get the User's Queue <https://developer.spotify.com/
        documentation/web-api/reference/get-queue>`_: Get the list of
        objects that make up the user's queue.

        .. admonition:: Authorization scope
        
           Requires the :code:`user-read-playback-state` scope.

        Returns
        -------
        queue : `dict`
            Information about the user's queue, such as the currently
            playing item and items in the queue.
        """

        self._check_scope("get_user_queue", "user-read-playback-state")

        return self._get_json(f"{self.API_URL}/me/player/queue")
    
    def add_queue_item(self, uri: str, *, device_id: str = None) -> None:

        """
        `Player > Add Item to Playback Queue 
        <https://developer.spotify.com/documentation/web-api/reference/
        add-to-queue>`_: Add an item to the end of the user's current
        playback queue.

        .. admonition:: Authorization scope
        
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

        self._request("post", f"{self.API_URL}/me/player/queue",
                      params={"uri": uri, "device_id": device_id})

    ### PLAYLISTS #############################################################

    def get_playlist(
            self, playlist_id: str, *,
            additional_types: Union[str, list[str]] = None,
            fields: str = None, market: str = None) -> dict[str, Any]:
        
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
            Spotify catalog information for a single playlist in JSON
            format.
        """

        return self._get_json(
            f"{self.API_URL}/playlists/{playlist_id}",
            params={
                "additional_types": additional_types
                                    if additional_types is None
                                    or isinstance(additional_types, str)
                                    else ",".join(additional_types),
                "fields": fields if fields is None or isinstance(fields, str)
                          else ",".join(fields),
                "market": market
            }
        )

    def change_playlist_details(
            self, playlist_id: str, *, name: str = None, public: bool = None,
            collaborative: bool = None, description: str = None) -> None:

        """
        `Playlists > Change Playlist Details
        <https://developer.spotify.com/documentation/web-api/reference/
        change-playlist-details>`_: Change a playlist's
        name and public/private state. (The user must, of course, own
        the playlist.)

        .. admonition:: Authorization scope
        
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

        self._check_scope("change_playlist_details", 
                          "playlist-modify-" + 
                          ("public" if self.get_playlist(playlist_id)["public"]
                           else "private"))
        
        json = {}
        if name is not None:
            json["name"] = name
        if public is not None:
            json["public"] = public
        if collaborative is not None:
            json["collaborative"] = collaborative
        if description is not None:
            json["description"] = description
        self._request("put", f"{self.API_URL}/playlists/{playlist_id}",
                      json=json)

    def get_playlist_items(
            self, playlist_id: str, *,
            additional_types: Union[str, list[str]] = None,
            fields: str = None, limit: int = None, market: str = None,
            offset: int = None) -> list[dict[str, Any]]:
        
        """
        `Playlists > Get Playlist Items <https://developer.spotify.com/
        documentation/web-api/reference/
        get-playlists-tracks>`_: Get full details of the items of a
        playlist owned by a Spotify user.

        .. admonition:: Authorization scope
        
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
        """

        self._check_scope("get_playlist_item", "playlist-modify-private")

        return self._get_json(
            f"{self.API_URL}/playlists/{playlist_id}/tracks",
            params={
                "additional_types": additional_types
                                    if additional_types is None
                                    or isinstance(additional_types, str)
                                    else ",".join(additional_types),
                "fields": fields if fields is None or isinstance(fields, str)
                          else ",".join(fields),
                "limit": limit,
                "market": market,
                "offset": offset
            }
        )
    
    def add_playlist_items(
            self, playlist_id: str, uris: Union[str, list[str]], *,
            position: int = None) -> str:
        
        """
        `Playlists > Add Items to Playlist
        <https://developer.spotify.com/documentation/web-api/reference/
        add-tracks-to-playlist>`_: Add one or more items to
        a user's playlist.

        .. admonition:: Authorization scope
        
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
            
               **Example**: 
            
               * :code:`0` to insert the items in the first position.
               * :code:`2` to insert the items in the third position.

        Returns
        -------
        snapshot_id : `str`
            The updated playlist's snapshot ID.
        """

        self._check_scope("add_playlist_details", 
                          "playlist-modify-" + 
                          ("public" if self.get_playlist(playlist_id)["public"]
                           else "private"))

        if isinstance(uris, str):
            url = f"{self.API_URL}/playlists/{playlist_id}/tracks?{uris=}"
            if position is not None:
                url += f"{position=}"
            return self._request("post", url).json()["snapshot_id"]
        
        elif isinstance(uris, list):
            json = {"uris": uris}
            if position is not None:
                json["position"] = position
            self._request("post",
                          f"{self.API_URL}/playlists/{playlist_id}/tracks",
                          json=json).json()["snapshot_id"]
    
    def update_playlist_items(
            self, playlist_id: str, *, uris: Union[str, list[str]] = None,
            range_start: int = None, insert_before: int = None,
            range_length: int = 1, snapshot_id: str = None) -> str:
        
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

        self._check_scope("update_playlist_details", 
                          "playlist-modify-" + 
                          ("public" if self.get_playlist(playlist_id)["public"]
                           else "private"))

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
                "put",
                f"{self.API_URL}/playlists/{playlist_id}/tracks",
                json=json
            ).json()["snapshot_id"]
        
        elif isinstance(uris, str):
            return self._request(
                "put", 
                f"{self.API_URL}/playlists/{playlist_id}/tracks?uris={uris}",
                json=json
            ).json()["snapshot_id"]
        
        elif isinstance(uris, list):
            return self._request(
                "put",
                f"{self.API_URL}/playlists/{playlist_id}/tracks",
                json={"uris": uris} | json
            ).json()["snapshot_id"]

    def remove_playlist_items(
            self, playlist_id: str, tracks: list[str], *, 
            snapshot_id: str = None) -> str:

        """
        `Playlists > Remove Playlist Items 
        <https://developer.spotify.com/documentation/web-api/reference/
        remove-tracks-playlist>`_: Remove one or more items from a 
        user's playlist.

        .. admonition:: Authorization scope
        
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

        self._check_scope("remove_playlist_items", 
                          "playlist-modify-" + 
                          ("public" if self.get_playlist(playlist_id)["public"]
                           else "private"))

        json = {"tracks": tracks}
        if snapshot_id is not None:
            json["snapshot_id"] = snapshot_id
        return self._request("delete",
                             f"{self.API_URL}/playlists/{playlist_id}/tracks",
                             json=json).json()["snapshot_id"]
    
    def get_current_user_playlists(
            self, *, limit: int = None, offset: int = None) -> dict[str, Any]:
        
        """
        `Playlist > Get Current User's Playlists 
        <https://developer.spotify.com/documentation/web-api/reference/
        get-a-list-of-current-users-playlists>`_: Get a list of the
        playlists owned or followed by the current Spotify user.

        .. admonition:: Authorization scope
        
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
        """

        self._check_scope("get_current_user_playlists",
                          "playlist-read-private")
        self._check_scope("get_current_user_playlists",
                          "playlist-read-collaborative")
        
        return self._get_json(f"{self.API_URL}/me/playlists",
                              params={"limit": limit, "offset": offset})
    
    def get_user_playlists(
            self, user_id: str, *, limit: int = None, offset: int = None
        ) -> dict[str, Any]:

        """
        `Playlist > Get User's Playlists 
        <https://developer.spotify.com/documentation/web-api/reference/
        get-list-users-playlists>`_: Get a list of the playlists owned
        or followed by a Spotify user.

        .. admonition:: Authorization scope
        
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
        """

        self._check_scope("get_user_playlists", "playlist-read-private")
        self._check_scope("get_user_playlists", "playlist-read-collaborative")
        
        return self._get_json(f"{self.API_URL}/users/{user_id}/playlists",
                              params={"limit": limit, "offset": offset})
    
    def create_playlist(
            self, user_id: str, name: str, public: bool = True,
            collaborative: bool = None, description: str = None
        ) -> dict[str, Any]:

        """
        `Playlists > Create Playlist <https://developer.spotify.com/
        documentation/web-api/reference/create-playlist>`_: Create a
        playlist for a Spotify user. (The playlist will be empty until
        you add tracks.)

        .. admonition:: Authorization scope
        
           Requires the :code:`playlist-modify-public` or the
           :code:`playlist-modify-private` scope.

        Parameters
        ----------
        user_id : `str`
            The user's Spotify user ID.

            **Example**: :code:`"smedjan"`

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
            Spotify catalog information for the newly created playlist
            in JSON format.
        """

        self._check_scope(
            "create_playlist", 
            "playlist-modify-" + ("public" if public else "private")
        )

        json = {"name": name, "public": public}
        if collaborative is not None:
            json["collaborative"] = collaborative
        if description is not None:
            json["description"] = description

        return self._request("post",
                             f"{self.API_URL}/users/{user_id}/playlists",
                             json=json).json()

    def get_featured_playlists(
            self, *, country: str = None, locale: str = None, 
            timestamp: str = None, limit: int = None, offset: int = None
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
        """
        
        return self._get_json(f"{self.API_URL}/browse/featured-playlists",
                              params={"country": country, "locale": locale,
                                      "timestamp": timestamp, "limit": limit,
                                      "offset": offset})
    
    def get_category_playlists(
            self, category_id: str, *, country: str = None, limit: int = None,
            offset: int = None) -> dict[str, Any]:

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
        """

        return self._get_json(
            f"{self.API_URL}/browse/categories/{category_id}/playlists",
            params={"country": country, "limit": limit, "offset": offset}
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
        """

        return self._get_json(f"{self.API_URL}/playlists/{playlist_id}/images")
    
    def add_playlist_cover_image(self, playlist_id: str, image: bytes) -> None:

        """
        `Playlists > Add Custom Playlist Cover Image
        <https://developer.spotify.com/documentation/web-api/reference/
        upload-custom-playlist-cover>`_: Replace the image used to 
        represent a specific playlist.

        .. admonition:: Authorization scope
        
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
        self._check_scope("get_categories", 
                          "playlist-modify-" + 
                          ("public" if self.get_playlist(playlist_id)["public"]
                           else "private"))

        self._request("put", f"{self.API_URL}/playlists/{playlist_id}/images",
                      data=image)

    ### SEARCH ################################################################

    def search(
            self, q: str, type: Union[str, list[str]], *,
            limit: int = None, market: str = None, offset: int = None
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
            The search results in JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/search?q={urllib.parse.quote(q)}",
            params={
                "type": type if isinstance(type, str) else ",".join(type),
                "limit": limit,
                "market": market,
                "offset": offset
            }
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
            Spotify catalog information for a single show in JSON
            format.
        """
        
        return self._get_json(f"{self.API_URL}/shows/{id}",
                              params={"market": market})

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
            A list of Spotify catalog information for multiple shows in
            JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/shows",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids),
                    "market": market}
        )["albums"]

    def get_show_episodes(
            self, id: str, *, limit: int = None, market: str = None,
            offset: int = None) -> dict[str, Any]:

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
            A dictionary containing the Spotify catalog information for
            a show's episodes and the number of results returned.
        """

        return self._get_json(
            f"{self.API_URL}/shows/{id}/episodes",
            params={"limit": limit, "market": market, "offset": offset}
        )
    
    def get_saved_shows(
            self, *, limit: int = None, offset: int = None) -> dict[str, Any]:

        """
        `Shows > Get User's Saved Shows <https://developer.spotify.com/
        documentation/web-api/reference/
        get-users-saved-shows>`_: Get a list of shows saved in the
        current Spotify user's library. Optional parameters can be used
        to limit the number of shows returned.
        
        .. admonition:: Authorization scope
        
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
            A dictionary containing the Spotify catalog information for
            a user's saved shows and the number of results returned.
        """

        self._check_scope("get_saved_shows", "user-library-read")

        return self._get_json(f"{self.API_URL}/me/shows",
                              params={"limit": limit, "offset": offset})

    def save_shows(self, ids: Union[str, list[str]]) -> None:

        """
        `Shows > Save Shows for Current User
        <https://developer.spotify.com/documentation/web-api/reference/
        save-shows-user>`_: Save one or more shows to
        current Spotify user's library.
        
        .. admonition:: Authorization scope
        
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
            "put", f"{self.API_URL}/me/shows",
            params={"ids": f"{ids if isinstance(ids, str) else ','.join(ids)}"}
        )

    def remove_saved_shows(
            self, ids: Union[str, list[str]], *, market: str = None) -> None:

        """
        `Shows > Remove User's Saved Shows
        <https://developer.spotify.com/documentation/web-api/reference/
        remove-shows-user>`_: Delete one or more shows from
        current Spotify user's library.
        
        .. admonition:: Authorization scope
        
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
            
        self._request("delete", f"{self.API_URL}/me/shows",
                      params={"ids": ids if isinstance(ids, str) 
                                     else ",".join(ids),
                              "market": market})

    def check_saved_shows(self, ids: Union[str, list[str]]) -> list[bool]:

        """
        `Shows > Check User's Saved Shows
        <https://developer.spotify.com/documentation/web-api/reference/
        check-users-saved-shows>`_: Check if one or more
        shows is already saved in the current Spotify user's library.
        
        .. admonition:: Authorization scope
        
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
        """

        self._check_scope("check_saved_shows", "user-library-read")
        
        return self._get_json(
            f"{self.API_URL}/me/shows/contains",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)}
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
            Spotify catalog information for a single track in JSON
            format.
        """

        return self._get_json(f"{self.API_URL}/tracks/{id}",
                             params={"market": market})
    
    def get_tracks(
            self, ids: Union[int, str, list[Union[int, str]]], *,
            market: str = None) -> list[dict[str, Any]]:
        
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
            A list of Spotify catalog information for multiple tracks in
            JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/tracks",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids),
                    "market": market}
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
            A dictionary containing the Spotify catalog information for
            a user's saved tracks and the number of results returned.
        """

        self._check_scope("get_saved_tracks", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/tracks",
            params={"limit": limit, "market": market, "offset": offset}
        )

    def save_tracks(self, ids: Union[str, list[str]]) -> None:

        """
        `Tracks > Save Track for Current User 
        <https://developer.spotify.com/documentation/web-api/reference/
        save-tracks-user>`_: Save one or more tracks to the
        current user's 'Your Music' library.
        
        .. admonition:: Authorization scope
        
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
            self._request("put", f"{self.API_URL}/me/tracks",
                          params={"ids": ids})
        elif isinstance(ids, list):
            self._request("put", f"{self.API_URL}/me/tracks", 
                          json={"ids": ids})

    def remove_saved_tracks(self, ids: Union[str, list[str]]) -> None:

        """
        `Tracks > Remove User's Saved Tracks
        <https://developer.spotify.com/documentation/web-api/reference/
        remove-tracks-user>`_: Remove one or more tracks
        from the current user's 'Your Music' library.
        
        .. admonition:: Authorization scope
        
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
            self._request("delete", f"{self.API_URL}/me/tracks",
                          params={"ids": ids})
        elif isinstance(ids, list):
            self._request("delete", f"{self.API_URL}/me/tracks", 
                          json={"ids": ids})

    def check_saved_tracks(self, ids: Union[str, list[str]]) -> list[bool]:

        """
        `Tracks > Check User's Saved Tracks
        <https://developer.spotify.com/documentation/web-api/reference/
        check-users-saved-tracks>`_: Check if one or more
        tracks is already saved in the current Spotify user's 'Your 
        Music' library.
        
        .. admonition:: Authorization scope
        
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
        """

        self._check_scope("check_saved_tracks", "user-library-read")

        return self._get_json(
            f"{self.API_URL}/me/tracks/contains",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)}
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
            The track's audio features in JSON format.
        """

        return self._get_json(f"{self.API_URL}/audio-features/{id}")

    def get_tracks_audio_features(
            self, ids: Union[str, list[str]]) -> list[dict[str, Any]]:

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
            A list of audio features for multiple tracks in JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/audio-features",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)}
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
            The track's audio analysis in JSON format.
        """

        return self._get_json(f"{self.API_URL}/audio-analysis/{id}")

    def get_recommendations(
            self, seed_artists: Union[str, list[str]],
            seed_genres: Union[str, list[str]],
            seed_tracks: Union[str, list[str]], *, limit: int = None,
            market: str = None, **kwargs) -> list[dict[str, Any]]:
        
        """
        `Tracks > Get Recommendations <https://developer.spotify.com/
        documentation/web-api/reference/
        get-recommendations>`_: Recommendations are generated based on
        the available information for a given seed entity and matched
        against similar artists and tracks. If there is sufficient
        information about the provided seeds, a list of tracks will be
        returned together with pool size details. For artists and tracks
        that are very new or obscure there might not be enough data to
        generate a list of tracks.

        Parameters
        ----------
        seed_artists : `str`
            A comma separated list of Spotify IDs for seed artists. 
            
            **Maximum**: Up to 5 seed values may be provided in any
            combination of `seed_artists`, `seed_tracks`, and 
            `seed_genres`.

            **Example**: :code:`"4NHQUGzhtTLFvgF5SZesLK"`.

        seed_genres : `str`
            A comma separated list of any genres in the set of available
            genre seeds.

            **Maximum**: Up to 5 seed values may be provided in any
            combination of `seed_artists`, `seed_tracks`, and 
            `seed_genres`.

            **Example**: :code:`"classical,country"`.

        seed_tracks : `str`
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
            A dictionary containing the Spotify catalog information for
            the recommended tracks.
        """

        return self._get_json(
            f"{self.API_URL}/recommendations",
            params={
                "seed_artists": seed_artists if seed_artists is None
                                or isinstance(seed_artists, str)
                                else ",".join(seed_artists),
                "seed_genres": seed_genres if seed_genres is None
                               or isinstance(seed_genres, str)
                               else ",".join(seed_genres),
                "seed_tracks": seed_tracks if seed_tracks is None
                               or isinstance(seed_tracks, str)
                               else ",".join(seed_tracks),
                "limit": limit,
                "market": market,
                **kwargs
            }
        )

    ### USERS #################################################################

    def get_current_user_profile(self) -> dict[str, Any]:

        """
        `Users > Get Current User's Profile
        <https://developer.spotify.com/documentation/web-api/reference/
        get-current-users-profile>`_: Get detailed profile
        information about the current user (including the current user's
        username).

        .. admonition:: Authorization scope
        
           Requires the :code:`user-read-private` scope.
        
        Returns
        -------
        user : `dict`
            A dictionary containing the current user's information.
        """

        self._check_scope("get_current_user_profile", "user-read-private")

        return self._get_json(f"{self.API_URL}/me")

    def get_user_top_items(
            self, type: str, *, limit: int = None, offset: int = None,
            time_range: str = None) -> dict[str, Any]:

        """
        `Users > Get User's Top Items <https://developer.spotify.com/
        documentation/web-api/reference/
        get-users-top-artists-and-tracks>`_: Get the current user's top
        artists or tracks based on calculated affinity.

        .. admonition:: Authorization scope
        
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
            A dictionary containing the Spotify catalog information for
            a user's top items and the number of results returned.
        """

        self._check_scope("get_user_top_items", "user-top-read")

        return self._get_json(
            f"{self.API_URL}/me/top/{type}",
            params={"limit": limit, "offset": offset, "time_range": time_range}
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
        """
        
        return self._get_json(f"{self.API_URL}/users/{user_id}")
    
    def follow_playlist(self, playlist_id: str) -> None:

        """
        `Users > Follow Playlist <https://developer.spotify.com/
        documentation/web-api/reference/follow-playlist>`_:
        Add the current user as a follower of a playlist.

        .. admonition:: Authorization scope
        
           Requires the :code:`playlist-modify-private` scope.

        Parameters
        ----------
        playlist_id : `str`
            The Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`
        """

        self._check_scope("follow_playlist", "playlist-modify-private")

        self._request("put", 
                      f"{self.API_URL}/playlists/{playlist_id}/followers")

    def unfollow_playlist(self, playlist_id: str) -> None:

        """
        `Users > Unfollow Playlist <https://developer.spotify.com/
        documentation/web-api/reference/
        unfollow-playlist>`_: Remove the current user as a follower of a
        playlist.

        .. admonition:: Authorization scope
        
           Requires the :code:`playlist-modify-private` scope.

        Parameters
        ----------
        playlist_id : `str`
            The Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`
        """

        self._check_scope("unfollow_playlist", "playlist-modify-private")

        self._request("delete", 
                      f"{self.API_URL}/playlists/{playlist_id}/followers")

    def get_followed_artists(
            self, *, after: str = None, limit: int = None) -> dict[str, Any]:
        
        """
        `Users > Get Followed Artists <https://developer.spotify.com/
        documentation/web-api/reference/get-followed>`_: 
        Get the current user's followed artists.

        .. admonition:: Authorization scope
        
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
            A dictionary containing the Spotify catalog information for
            a user's followed artists and the number of results
            returned.
        """

        self._check_scope("get_followed_artists", "user-follow-read")

        return self._get_json(
            f"{self.API_URL}/me/following",
            params={"type": "artist", "after": after, "limit": limit}
        )["artists"]

    def follow_people(self, ids: Union[str, list[str]], type: str) -> None:
        
        """
        `Users > Follow Artists or Users <https://developer.spotify.com/
        documentation/web-api/reference/
        follow-artists-users>`_: Add the current user as a follower of
        one or more artists or other Spotify users.

        .. admonition:: Authorization scope
        
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

        self._check_scope("follow_person", "user-follow-modify")

        if isinstance(ids, str):
            self._request("put", f"{self.API_URL}/me/following",
                          params={"ids": ids, "type": type})
        elif isinstance(ids, list):
            self._request("put", f"{self.API_URL}/me/following",
                          json={"ids": ids}, params={"type": type})

    def unfollow_people(self, ids: Union[str, list[str]], type: str) -> None:
        
        """
        `Users > Unfollow Artists or Users
        <https://developer.spotify.com/documentation/web-api/reference/
        unfollow-artists-users>`_: Remove the current user
        as a follower of one or more artists or other Spotify users.

        .. admonition:: Authorization scope
        
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

        self._check_scope("unfollow_person", "user-follow-modify")

        if isinstance(ids, str):
            self._request("delete", f"{self.API_URL}/me/following",
                          params={"ids": ids, "type": type})
        elif isinstance(ids, list):
            self._request("delete", f"{self.API_URL}/me/following",
                          json={"ids": ids}, params={"type": type})

    def check_followed_people(
            self, ids: Union[str, list[str]], type: str) -> list[bool]:

        """
        `Users > Check If User Follows Artists or Users
        <https://developer.spotify.com/documentation/web-api/reference/
        check-current-user-follows>`_: Check to see if the
        current user is following one or more artists or other Spotify
        users.

        .. admonition:: Authorization scope
        
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
        """

        self._check_scope("check_followed_people", "user-follow-read")
        
        return self._get_json(
            f"{self.API_URL}/me/following/contains",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids),
                    "type": type}
        )

    def check_playlist_followers(
            self, playlist_id: str, ids: Union[str, list[str]]) -> list[bool]:
        
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
        """

        return self._get_json(
            f"{self.API_URL}/playlists/{playlist_id}/followers/contains",
            params={"ids": ids if isinstance(ids, str) else ",".join(ids)}
        )