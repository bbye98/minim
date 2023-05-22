"""
:mod:`minim.tidal` -- TIDAL API
===============================
.. moduleauthor:: Benjamin Ye <GitHub: @bbye98>

This module contains a minimal Python implementation of the TIDAL API,
which allows media (tracks, videos), collections (albums, playlists),
and performers to be queried, and information about them to be 
retrieved. As the TIDAL API is not public, there is no available
official documentation for it. Its endpoints have been determined by 
watching HTTP network traffic.

Without authentication, the TIDAL API can be used to query for and
retrieve information about media and performers.

With OAuth 2.0 authentication, the TIDAL API allows access to user
information and media streaming. Valid client credentials—a client ID
and a client secret—must either be provided explicitly to the 
:class:`Session` constructor or be stored in the operating system's 
environment variables as :code:`TIDAL_CLIENT_ID` and 
:code:`TIDAL_CLIENT_SECRET`, respectively. Alternatively, an access
token (and optionally, its accompanying expiry time and refresh token) 
can be provided to the :class:`Session` constructor to bypass the 
authorization flow.

.. note::
   This module supports the authorization code and device code flows.
"""

import base64
import datetime
import hashlib
import json
import os
import re
import secrets
import subprocess
import tempfile
import time
from typing import Any, Union
import urllib
import webbrowser
from xml.dom import minidom

from Crypto.Cipher import AES
from Crypto.Util import Counter
import requests

try:
    from playwright.sync_api import sync_playwright
    FOUND_PLAYWRIGHT = True
except:
    FOUND_PLAYWRIGHT = False

from . import audio, utility

TEMP_DIR = tempfile.gettempdir()

class Session:

    """
    A TIDAL API session.

    Parameters
    ----------
    client_id : `str`, keyword-only, optional
        Client ID. If it is not stored as :code:`TIDAL_CLIENT_ID` in
        the operating system's environment variables, it must be
        provided here.
    
    client_secret : `str`, keyword-only, optional
        Client secret key. If it is not stored as
        :code:`TIDAL_CLIENT_SECRET` in the operating system's
        environment variables, it must be provided here if the device
        code flow will be used for user authentication.

    flow : `str`, keyword-only, optional
        Authorization flow. If not specified, no user authentication
        will be performed.

        .. container::

           **Valid values**:
           
           * :code:`authorization_code` for the authorization code flow.
           * :code:`device_code` for the device_code flow.
    
    scopes : `str` or `list`, keyword-only, optional
        Authorization scopes to request user access for in the
        device code flow.

        **Valid values**: :code:`"r_usr"`, :code:`"w_usr"`, 
        :code:`"w_sub"`.

        **Default**: :code:`"r_usr w_usr"`.

    browser : `bool`, keyword-only, default: :code:`True`
        Determines whether a web browser is automatically opened for the
        authorization code or device code flows. If :code:`False`, users 
        will have to manually open the specified URL, and for the
        authorization code flow, provide the full callback URI via the
        terminal.
    
    access_token : `str`, keyword-only, optional
        Access token. If provided, the authorization flow is completely
        bypassed.
    
    refresh_token : `str`, keyword-only, optional
        Refresh token accompanying `access_token`. If not specified, the
        user will be reauthenticated using the default authorization
        flow when `access_token` expires.
        
    expiry : `datetime.datetime`, keyword-only, optional
        Expiry time of `access_token`. If provided, the user will be
        reauthenticated using `refresh_token` (if available) or the
        default authorization flow (if possible) when `access_token`
        expires.

    user_agent : `str`, keyword-only, optional
        User agent information to send in the header of HTTP requests.
        
        .. note::
           If not specified, TIDAL may temporarily block your IP address
           if you are making requests too quickly.

    Attributes
    ----------
    API_URL : `str`
        URL for the TIDAL API.

    AUTH_URL : `str`
        URL for device code requests.

    LOGIN_URL : `str`
        URL for authorization code requests.

    RESOURCES_URL : `str`
        URL for cover art and images.
        
    TOKEN_URL : `str`
        URL for access token requests.

    WEB_URL : `str`
        URL for the TIDAL web player.
    """

    _ASSET_PRESENTATIONS = {"FULL", "PREVIEW"}
    _AUDIO_FORMATS_EXTENSIONS = {
        "alac": "m4a",
        "flac": "flac",
        "m4a": "m4a",
        "mp3": "mp3",
        "mpeg": "mp3",
        "mp4a": "m4a",
        "mqa": "flac"
    }
    _AUDIO_QUALITIES = {"LOW", "HIGH", "LOSSLESS", "HI_RES"}
    _COLLECTION_TYPES = {"album", "mix", "playlist"}
    _DEVICE_TYPES = {"BROWSER", "DESKTOP", "PHONE", "TV"}
    _COMPOSER_ROLES = {"Composer", "Lyricist", "Writer"}
    _ILLEGAL_CHARACTERS = {ord(c): '_' for c in '<>:"/\|?*'}
    _IMAGE_SIZES = {
        "artist": (750, 750),
        "album": (1280, 1280),
        "playlist": (1080, 1080),
        "track": (1280, 1280),
        "video": (640, 360)
    }
    _MASTER_KEY = base64.b64decode('UIlTTEMmmLfGowo/UC60x2H45W6MdGgTRfo/umg4754=')
    _MEDIA_TYPES = {"artist", "album", "playlist", "track", "userProfile", "video"}
    _OAUTH_FLOWS = {"authorization_code", "device_code"}
    _PLAYBACK_MODES = {"STREAM", "OFFLINE"}
    _VIDEO_QUALITIES = {"AUDIO_ONLY", "LOW", "MEDIUM", "HIGH"}

    API_URL = "https://api.tidal.com"
    AUTH_URL = "https://auth.tidal.com/v1/oauth2"
    LOGIN_URL = "https://login.tidal.com"
    REDIRECT_URI = "tidal://login/auth"
    RESOURCES_URL = "http://resources.tidal.com"
    WEB_URL = "https://listen.tidal.com"

    def __init__(
            self, *, client_id: str = None, client_secret: str = None,
            country: str = None, flow: str = None,
            scopes: Union[str, list[str]] = "r_usr w_usr",
            browser: bool = True, access_token: str = None,
            refresh_token: str = None, expiry: datetime.datetime = None,
            user_agent: str = None):
        
        """
        Create a TIDAL API session.
        """
        
        self.session = requests.Session()
        if user_agent:
            self.session.headers.update({"User-Agent": user_agent})

        if access_token is not None:
            self.session.headers.update({"Authorization": f"Bearer {access_token}"})
            self._client_id = os.environ.get("TIDAL_CLIENT_ID") \
                              if client_id is None else client_id
            self._refresh_token = refresh_token
            self._expiry = expiry
            self._session = self.get_session()
            self._me = self.get_me()
            self._country = country if country else self._me["countryCode"]
        elif flow is None:
            self._client_id = os.environ.get("TIDAL_CLIENT_ID") \
                              if client_id is None else client_id
            self._expiry = None
            self._flow = flow
            self._country = country if country else self.get_country_code()
            self.session.headers.update({"x-tidal-token": self._client_id})
        else:
            if flow and flow not in self._OAUTH_FLOWS:
                raise ValueError("Invalid OAuth 2.0 authorization flow.")
            self._flow = flow
            self._client_id = os.environ.get("TIDAL_CLIENT_ID") \
                              if client_id is None else client_id
            self._client_secret = os.environ.get("TIDAL_CLIENT_SECRET") \
                                  if client_secret is None \
                                  else client_secret
            self._scopes = " ".join(scopes) if isinstance(scopes, list) else scopes
            self._browser = browser
            self._get_access_token()
            self._session = self.get_session()
            if self._flow == "device_code":
                self._me = self.get_me()
            self._country = country if country else self._me["countryCode"]

    def __repr__(self) -> None:

        """
        Set the string representation of the TIDAL API object.
        """

        if hasattr(self, "_session") and hasattr(self, "_me"):
            return (f"TIDAL API: client {self._session['client']['name']} / "
                    f"session {self._session['sessionId']} / "
                    f"user {self._me['nickname']} (ID: {self._me['userId']}, "
                    f"email: {self._me['email']})")
        return f"<minim.tidal.Session object at 0x{id(self):x}>"

    def _get_access_token(self) -> None:

        """
        Get TIDAL API access token.
        """

        if self._flow == "authorization_code":
            if self._client_id is None:
                raise ValueError("TIDAL API client ID not provided.")
            
            code_verifier = secrets.token_urlsafe(32)
            code_challenge = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode("ascii")).digest()
            ).decode("ascii")
            if code_challenge[-1] == "=":
                code_challenge = code_challenge[:-1]

            auth_code = self._get_authorization_code(code_challenge)

            resp = requests.post(
                f"{self.LOGIN_URL}/oauth2/token",
                json={"client_id": self._client_id,
                      "code": auth_code,
                      "code_verifier": code_verifier, 
                      "grant_type": "authorization_code", 
                      "redirect_uri": self.REDIRECT_URI, 
                      "scope": self._scopes}
            ).json()

            self.session.headers.update(
                {"Authorization": f"{resp['token_type']} {resp['access_token']}"}
            )
            self._refresh_token = resp["refresh_token"]
            self._expiry = datetime.datetime.now() \
                           + datetime.timedelta(0, resp["expires_in"])
            self._me = resp["user"]
            
        elif self._flow == "device_code":
            if self._client_id is None or self._client_secret is None:
                raise ValueError("TIDAL API client credentials not provided.")
            
            data = {"client_id": self._client_id}
            if self._scopes:
                data["scope"] = self._scopes
        
            resp = requests.post(f"{self.AUTH_URL}/device_authorization",
                                 data=data).json()
            if "error" in resp:
                raise ValueError(f"{resp['status']}.{resp['sub_status']} {resp['error_description']}")
            data["device_code"] = resp["deviceCode"]
            data["grant_type"] = "urn:ietf:params:oauth:grant-type:device_code"
            verification_uri = f"http://{resp['verificationUriComplete']}"

            if self._browser:
                webbrowser.open(verification_uri)
            else:
                print("To grant Minim access to TIDAL data and features, open the "
                      f"following link in your web browser:\n\n{verification_uri}\n")

            while True:
                time.sleep(2)
                resp = requests.post(f"{self.AUTH_URL}/token", data=data,
                                     auth=(self._client_id, self._client_secret)).json()
                if "error" not in resp:
                    break
                elif resp["error"] != "authorization_pending":
                    raise RuntimeError(f"{resp['status']}.{resp['sub_status']} "
                                       f"{resp['error_description']}")

            self.session.headers.update(
                {"Authorization": f"{resp['token_type']} {resp['access_token']}"}
            )
            self._refresh_token = resp["refresh_token"]
            self._expiry = datetime.datetime.now() \
                           + datetime.timedelta(0, resp["expires_in"])

    def _get_authorization_code(self, code_challenge: str) -> str:

        """
        Get an authorization code to be exchanged for an access token 
        for the TIDAL Web API.

        Parameters
        ----------
        code_challenge : `str`
            Code challenge.

        Returns
        -------
        auth_code : `str`
            Authorization code.
        """

        if self._client_id is None:
            raise ValueError("TIDAL API client ID not provided.")

        params = {
            "client_id": self._client_id,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "redirect_uri": self.REDIRECT_URI,
            "response_type": "code",
        }
        if self._scopes:
            params["scope"] = self._scopes

        auth_url = (f"{self.LOGIN_URL}/authorize?"
                    f"{urllib.parse.urlencode(params)}")

        if self._browser:
            har_file = f"{TEMP_DIR}/tidal.har"

            with sync_playwright() as playwright:
                browser = playwright.firefox.launch(headless=False)
                context = browser.new_context(
                    locale="en-US",
                    timezone_id="America/Los_Angeles",
                    record_har_path=har_file, 
                    **playwright.devices["Desktop Firefox HiDPI"]
                )
                page = context.new_page()
                page.goto(auth_url, timeout=0)
                try:
                    page.wait_for_url(f"tidal://login/auth*", 
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
            print("To grant Minim access to TIDAL data and features, "
                  "open the following link in your web browser:\n\n"
                  f"{auth_url}\n")
            uri = input("After authorizing Minim to access TIDAL "
                        "on your behalf, provide the redirect URI "
                        f"beginning with '{self.REDIRECT_URI}' "
                        "below.\n\nURI: ")
            queries = dict(
                urllib.parse.parse_qsl(urllib.parse.urlparse(uri).query)
            )
        
        if "code" not in queries:
            raise RuntimeError("Authorization failed.")
        return queries["code"]

    def _refresh_access_token(self) -> None:

        """
        Refresh the expired excess token.
        """

        if self._refresh_token is None:
            self._get_access_token()
        else:
            if self._client_id is None:
                raise ValueError("TIDAL API client ID not provided.")
            
            resp = self._request(
                "post",
                f"{self.LOGIN_URL}/oauth2/token",
                json={"client_id": self._client_id, 
                      "grant_type": "refresh_token",
                      "refresh_token": self._refresh_token},
                check_expiry=False
            ).json()

        self.session.headers.update(
            {"Authorization": f"{resp['token_type']} {resp['access_token']}"}
        )
        self._expiry = datetime.datetime.now() \
                       + datetime.timedelta(0, resp["expires_in"])
    
    def _request(
            self, method: str, url: str, *, check_expiry: bool = True, **kwargs
        ) -> requests.Response:

        """
        Construct and send a request, but with status code checking.

        Parameters
        ----------
        method : `str`
            Method for the request.

        url : `str`
            URL for the request.

        check_expiry : `bool`, keyword-only, default: :code:`True`
            Determines whether a check is performed to see if the access
            token has expired.

        **kwargs
            Keyword arguments passed to :meth:`requests.request`.

        Returns
        -------
        resp : `requests.Response`
            Response to the request.
        """

        if check_expiry and self._expiry is not None \
                and datetime.datetime.now() > self._expiry:
            self._refresh_access_token()

        resp = self.session.request(method, url, **kwargs)
        status = resp.status_code
        if resp.status_code in range(200, 209):
            return resp
        elif resp.status_code == 404:
            raise RuntimeError(f"{resp.status_code} {resp.reason}")
        else: 
            error = resp.json()
            substatus = error["subStatus"] if "subStatus" in error \
                        else error["sub_status"] if "sub_status" in error \
                        else ""
            description = error["userMessage"] if "userMessage" in error \
                          else error["description"] if "description" in error \
                          else error["error_description"] if "error_description" in error \
                          else ""
            
            emsg = f"{status}"
            if substatus:
                emsg += f".{substatus}"
            emsg += f" {description}"

            if resp.status_code == 401 and substatus == 11003:
                print(emsg)
                self._get_access_token()
                return self.session.request(method, url, **kwargs)
            else:
                raise RuntimeError(emsg)

    def _get_json(self, url: str, **kwargs) -> dict:

        """
        Send a GET request and return the JSON-encoded content of the 
        response.

        Parameters
        ----------
        url : `str`
            URL for the GET request.
        
        **kwargs
            Keyword arguments passed to :meth:`requests.request`.

        Returns
        -------
        resp : `dict`
            JSON-encoded content of the response.
        """

        return self._request("get", url, **kwargs).json()

    ### ARTISTS ###############################################################

    def get_artist(
            self, id: Union[int, str], *, country: str = None
        ) -> dict[str, Any]:

        """
        Get TIDAL catalog information for an artist.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL artist ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        artist : `dict`
            TIDAL catalog information for the artist in JSON format.
        """
        
        return self._get_json(
            f"{self.API_URL}/v1/artists/{id}",
            params={"countryCode": self._country if country is None 
                                   else country}
        )

    def get_artist_albums(
            self, id: Union[int, str], *, country: str = None, 
            limit: int = 100, offset: int = None) -> dict[str, Any]:

        """
        Get TIDAL catalog information for an artist's albums.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL artist ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`100`
            The maximum number of results to return.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of results.

            **Default**: :code:`0`.

        Returns
        -------
        albums : `dict`
            A dictionary containing the artist's albums and the number
            of results returned.
        """

        return self._get_json(
            f"{self.API_URL}/v1/artists/{id}/albums",
            params={"countryCode": self._country if country is None 
                                   else country,
                    "limit": limit, "offset": offset}
        )

    def get_artist_top_tracks(
            self, id: Union[int, str], *, country: str = None, 
            limit: int = 100, offset: int = None) -> dict[str, Any]:

        """
        Get TIDAL catalog information for an artist's top tracks.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL artist ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`100`
            The maximum number of results to return.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of results.

            **Default**: :code:`0`.

        Returns
        -------
        tracks : `dict`
            A dictionary containing the artist's top tracks and the
            number of results returned.
        """

        return self._get_json(
            f"{self.API_URL}/v1/artists/{id}/toptracks",
            params={"countryCode": self._country if country is None 
                                   else country,
                    "limit": limit, "offset": offset}
        )

    def get_artist_videos(
            self, id: Union[int, str], *, country: str = None, 
            limit: int = 100, offset: int = None) -> dict[str, Any]:

        """
        Get TIDAL catalog information for an artist's videos.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL artist ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`100`
            The maximum number of results to return.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of results.

            **Default**: :code:`0`.

        Returns
        -------
        videos : `dict`
            A dictionary containing the artist's videos and the number
            of results returned.
        """

        return self._get_json(
            f"{self.API_URL}/v1/artists/{id}/videos",
            params={"countryCode": self._country if country is None 
                                   else country,
                    "limit": limit, "offset": offset}
        )

    def get_artist_mix(
            self, id: Union[int, str], *, country: str = None) -> str:

        """
        Get the curated mix of tracks related to an artist's works.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL artist ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        mix_id : `str`
            TIDAL mix ID.
        """

        return self._get_json(
            f"{self.API_URL}/v1/artists/{id}/mix",
            params={"countryCode": self._country if country is None 
                                   else country}
        )["id"]

    def get_artist_biography(
            self, id: Union[int, str], *, country: str = None
        ) -> dict[str, str]:

        """
        Get an artist's biographical information.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL artist ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        bio : `dict`
            A dictionary containing an artist's biographical information
            and its source.
        """

        return self._get_json(
            f"{self.API_URL}/v1/artists/{id}/bio",
            params={"countryCode": self._country if country is None 
                                   else country}
        )

    def get_artist_links(
            self, id: Union[int, str], *, country: str = None, 
            limit: int = None, offset: int = None) -> dict[str, Any]:

        """
        Get links to websites associated with an artist.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL artist ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, optional
            The maximum number of results to return.

            **Default**: :code:`10`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of results.

            **Default**: :code:`0`.

        Returns
        -------
        links : `dict`
            A dictionary containing the artist's links and the number of
            results returned.
        """

        return self._get_json(
            f"{self.API_URL}/v1/artists/{id}/links",
            params={"countryCode": self._country if country is None 
                                   else country,
                    "limit": limit, "offset": offset}
        )

    def get_favorite_artists(
            self, *, limit: int = 50, offset: int = None, order: str = "DATE",
            order_direction: str = "DESC", country: str = None):
        
        """
        Get the current user's favorite artists.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        limit : `int`, keyword-only, default: :code:`50`
            The maximum number of results to return.

        offset : `int`, keyword-only, optional
            Index of the first result to return. Use with `limit` to get
            the next page of search results.

            **Default**: :code:`0`.

        order : `str`, keyword-only, default: :code:`"DATE"`
            Sorting order.

            **Valid values**: :code:`"DATE"` and :code:`"NAME"`.

        order_direction : `str`, keyword-only, default: :code:`"DESC"`
            Sorting order direction.

            **Valid values**: :code:`"DESC"` and :code:`"ASC"`.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        artists : `dict`
            A dictionary containing the current user's artists and the
            number of results returned.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_favorite_artists() "
                               "requires user authentication.")

        return self._get_json(
            f"{self.API_URL}/v1/users/{self._me['userId']}/favorites/artists", 
            params={"limit": limit, "offset": offset,
                    "order": order, "orderDirection": order_direction, 
                    "countryCode": self._country if country is None
                                   else country}
        )

    def favorite_artists(
            self, ids: Union[int, str, list[Union[int, str]]], *, 
            on_not_found: str = "FAIL", country: str = None) -> None:

        """
        Favorite artists.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        ids : `int`, `str`, or `list`
            TIDAL artist ID(s).

        on_not_found : `str`, keyword-only, default: :code:`"FAIL"`
            Behavior when the item to be added does not exist.

            **Valid value**: :code:`"FAIL"`.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.favorite_artist() "
                               "requires user authentication.")

        self._request(
            "post", 
            f"{self.API_URL}/v1/users/{self._me['userId']}/favorites/artists",
            params={"countryCode": self._country if country is None
                                   else country},
            data={"artistIds": ids, "onArtifactNotFound": on_not_found}
        )

    def unfavorite_artists(self):

        """
        Unfavorite artists.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        ids : `int`, `str`, or `list`
            TIDAL artist ID(s).
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.unfavorite_artist() "
                               "requires user authentication.")
        
        if isinstance(ids, list):
            ids = ",".join(map(str, ids))

        self._request("delete", 
                      f"{self.API_URL}/v1/users/{self._me['userId']}"
                      f"/favorites/artists/{ids}")

    def get_blocked_artists(
            self, *, limit: int = 50, offset: int = None) -> dict[str, Any]:

        """
        Get artists blocked by the current user.
        
        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        limit : `int`, keyword-only, default: :code:`50`
            Maximum number of results to return.

        offset : `int`, keyword-only, optional
            Index of the first result to return. Use with `limit` to get
            the next page of search results.

            **Default**: :code:`0`.

        Returns
        -------
        artists : `dict`
            A dictionary containing the artists blocked by the current 
            user and the number of results.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_blocked_artists() "
                               "requires user authentication.")

        return self._get_json(
            f"{self.API_URL}/v1/users/{self._me['userId']}/blocks/artists",
            params={"limit": limit, "offset": offset}
        )

    def block_artist(self, id: Union[int, str]) -> None:

        """
        Block an artist from mixes and the radio.
        
        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL artist ID.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.block_artist() "
                               "requires user authentication.")

        self._request(
            "post",
            f"{self.API_URL}/v1/users/{self._me['userId']}/blocks/artists",
            data={"artistId": id}
        )

    def unblock_artist(self, id: Union[int, str]) -> None:

        """
        Unblock an artist from mixes and the radio.
        
        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL artist ID.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.unblock_artist() "
                               "requires user authentication.")

        self._request(
            "delete",
            f"{self.API_URL}/v1/users/{self._me['userId']}/blocks/artists/{id}"
        )

    ### ALBUMS ################################################################

    def get_album(
            self, id: Union[int, str], *, country: str = None
        ) -> dict[str, Any]:

        """
        Get TIDAL catalog information for an album.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL album ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        album : `dict`
            TIDAL catalog information for the album in JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/v1/albums/{id}",
            params={"countryCode": self._country if country is None 
                                   else country}
        )

    def get_album_items(
            self, id: Union[int, str], *, credits: bool = False, 
            country: str = None, limit: int = 100, offset: int = None
        ) -> dict[str, Any]:

        """
        Get TIDAL catalog information for all tracks and videos in an
        album.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL album ID.

        credits : `bool`, keyword-only, default: :code:`False`
            Determines whether credits for each item is returned.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`100`
            The maximum number of results to return.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of results.

            **Default**: :code:`0`.
            
        Returns
        -------
        items : `dict`
            A dictionary containing the items in the album and the
            number of results returned.
        """

        url = f"{self.API_URL}/v1/albums/{id}/items"
        if credits:
            url += "/credits"

        return self._get_json(
            url,
            params={"countryCode": self._country if country is None 
                                   else country,
                    "limit": limit, "offset": offset}
        )

    def get_album_credits(
            self, id: Union[int, str], *, country: str = None
        ) -> dict[str, Any]:

        """
        Get credits for an album.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL album ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        credits : `dict`
            A dictionary containing the album contributors.
        """

        return self._get_json(
            f"{self.API_URL}/v1/albums/{id}/credits",
            params={"countryCode": self._country if country is None 
                                   else country}
        )

    def get_album_review(
            self, id: Union[int, str], *, country: str = None
        ) -> dict[str, str]:

        """
        Get a review of or a synopsis for an album.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL album ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        review : `dict`
            A dictionary containing a review of or a synopsis for an 
            album and its source.
        """
        
        return self._get_json(
            f"{self.API_URL}/v1/albums/{id}/review",
            params={"countryCode": self._country if country is None 
                                   else country}
        )

    def get_favorite_albums(
            self, *, limit: int = 50, offset: int = None, order: str = "DATE",
            order_direction: str = "DESC", country: str = None):
        
        """
        Get the current user's favorite albums.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        limit : `int`, keyword-only, default: :code:`50`
            The maximum number of results to return.

        offset : `int`, keyword-only, optional
            Index of the first result to return. Use with `limit` to get
            the next page of search results.

            **Default**: :code:`0`.
            
        order : `str`, keyword-only, default: :code:`"DATE"`
            Sorting order.

            **Valid values**: :code:`"DATE"` and :code:`"NAME"`.

        order_direction : `str`, keyword-only, default: :code:`"DESC"`
            Sorting order direction.

            **Valid values**: :code:`"DESC"` and :code:`"ASC"`.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        albums : `dict`
            A dictionary containing the current user's albums and the
            number of results returned.
        """
        
        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_favorite_albums() "
                               "requires user authentication.")

        return self._get_json(
            f"{self.API_URL}/v1/users/{self._me['userId']}/favorites/albums", 
            params={"limit": limit, "offset": offset,
                    "order": order, "orderDirection": order_direction, 
                    "countryCode": self._country if country is None
                                   else country}
        )

    def favorite_albums(
            self, ids: Union[int, str, list[Union[int, str]]], *, 
            on_not_found: str = "FAIL", country: str = None) -> None:

        """
        Favorite albums.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        ids : `int`, `str`, or `list`
            TIDAL album ID(s).

        on_not_found : `str`, keyword-only, default: :code:`"FAIL"`
            Behavior when the item to be added does not exist.

            **Valid value**: :code:`"FAIL"`.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.favorite_album() "
                               "requires user authentication.")
        
        if isinstance(ids, list):
            ids = ",".join(map(str, ids))

        self._request(
            "post", 
            f"{self.API_URL}/v1/users/{self._me['userId']}/favorites/albums",
            params={"countryCode": self._country if country is None
                                   else country},
            data={"albumIds": ids, "onArtifactNotFound": on_not_found}
        )

    def unfavorite_albums(self, ids: Union[int, str, list[Union[int, str]]]):

        """
        Unfavorite albums.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        ids : `int`, `str`, or `list`
            TIDAL album ID(s).
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.unfavorite_album() "
                               "requires user authentication.")
        
        if isinstance(ids, list):
            ids = ",".join(map(str, ids))

        self._request("delete", 
                      f"{self.API_URL}/v1/users/{self._me['userId']}"
                      f"/favorites/albums/{ids}")

    ### MARKETS ###############################################################

    def get_country_code(self) -> str:

        """
        Get the country code based on the current IP address.

        Returns
        -------
        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code.
        """

        return self._get_json(f"{self.API_URL}/v1/country")["countryCode"]

    ### ME ####################################################################

    def get_me(self) -> dict[str, Any]:

        """
        Get the current user's profile information.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.
        
        Returns
        -------
        me : `dict`
            The current user's profile information.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_me() requires user "
                               "authentication.")

        return self._get_json(f"{self.LOGIN_URL}/oauth2/me")

    def get_session(self) -> dict[str, Any]:

        """
        Get information about the current TIDAL API session.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Returns
        -------
        session : `dict`
            Information about the current TIDAL API session.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_session() requires "
                               "user authentication.")
        
        return self._get_json(f"{self.API_URL}/v1/sessions")

    def get_favorite_ids(self) -> dict[str, list[Union[int, str]]]:

        """
        Get IDs or UUIDs of the current user's favorite albums, artists,
        playlists, tracks, and videos.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Returns
        -------
        ids : `dict`
            A dictionary containing the IDs or UUIDs of the current
            user's favorite items.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_favorite_ids() "
                               "requires user authentication.")

        return self._get_json(
            f"{self.API_URL}/v1/users/{self._me['userId']}/favorites/ids"
        )

    ### MISCELLANEOUS #########################################################

    def get_image(
            self, uuid: str, type: str = None, *, width: int = None, 
            height: int = None, filename: str = None) -> str:

        """
        Get cover art or image for a TIDAL object.

        Parameters
        ----------
        uuid : `str`
            Image UUID.

        type : `str`
            TIDAL object type.

        Returns
        -------
        url : `str`
            URL of the cover art or image.
        """
        
        if width is None or height is None:
            if type and type in self._MEDIA_TYPES:
                width, height = self._IMAGE_SIZES[type.lower()]
            else:
                raise ValueError("Either the image dimensions or a "
                                 "valid media type must be specified.")

        with urllib.request.urlopen(f"{self.RESOURCES_URL}/images"
                                    f"/{uuid.replace('-', '/')}"
                                    f"/{width}x{height}.jpg") as r:
            image = r.read()

        if filename:
            with open(filename, "wb") as f:
                f.write(image)
        else:
            return image

    ### MIXES #################################################################

    def get_mix_items(self, id: str, *, country: str = None) -> dict[str, Any]:

        """
        Get TIDAL catalog information for all tracks and videos in a
        mix.

        Parameters
        ----------
        id : `str`
            TIDAL mix ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        items : `dict`
            A dictionary containing the items in the album and the
            number of results returned.
        """

        return self._get_json(
            f"{self.API_URL}/v1/mixes/{id}/items",
            params={"countryCode": self._country if country is None 
                                   else country})

    def get_favorite_mixes(
            self, *, id: bool = False, limit: int = 50, cursor: str = None
        ) -> dict[str, Any]:

        """
        Get the current user's favorite mixes.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `bool`, keyword-only, default: :code:`False`
            Determine whether TIDAL catalog information about the mixes
            (:code:`False`) or the mix IDs (:code:`True`) are returned.

        limit : `int`, keyword-only, default: :code:`50`
            Maximum number of results to return.

        cursor : `str`, keyword-only, optional
            Cursor position of the last item in previous search results.
            Use with `limit` to get the next page of search results.

        Returns
        -------
        mixes : `dict`
            A dictionary containing the mixes (or mix IDs) and the 
            cursor position.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_favorite_mixes() "
                               "requires user authentication.")

        url = f"{self.API_URL}/v2/favorites/mixes"
        if id:
            url += "/ids"

        return self._get_json(url, params={"limit": limit, "cursor": cursor})

    def favorite_mixes(
            self, uuids: Union[str, list[str]], *, on_not_found: str = "FAIL"
        ) -> None:

        """
        Favorite mixes.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuids : `str` or `list`
            TIDAL mix UUID(s).

        on_not_found : `str`, keyword-only, default: :code:`"FAIL"`
            Behavior when the item to be added does not exist.

            **Valid value**: :code:`"FAIL"`.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.favorite_mixes() "
                               "requires user authentication.")

        self._request("put", f"{self.API_URL}/v2/favorites/mixes/add",
                      data={"mixIds": uuids, 
                            "onArtifactNotFound": on_not_found})

    def unfavorite_mixes(self, uuids: Union[str, list[str]]) -> None:

        """
        Unfavorite mixes.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuids : `str` or `list`
            TIDAL mix UUID(s).
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.unfavorite_mixes() "
                               "requires user authentication.")

        self._request("put", f"{self.API_URL}/v2/favorites/mixes/remove",
                      data={"mixIds": uuids})

    ### PAGES #################################################################

    def get_album_page(
            self, id: Union[int, str], *, device: str = "BROWSER",
            country: str = None) -> dict[str, Any]:
    
        """
        Get an album's TIDAL page.

        Parameters
        ----------
        id : `str`
            TIDAL album ID.

        device : `str`, keyword-only, default: :code:`"BROWSER"`
            Device type.

            .. container::

               **Valid values**:

               * :code:`"BROWSER"` for a web browser.
               * :code:`"DESKTOP"` for the desktop TIDAL application.
               * :code:`"PHONE"` for the mobile TIDAL application.
               * :code:`"TV"` for the smart TV TIDAL application.
            
        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        page : `dict`
            A dictionary containing the page ID, title, and submodules.
        """

        if device not in self._DEVICE_TYPES:
            raise ValueError("Invalid device type. The supported types "
                             f"are {', '.join(self._DEVICE_TYPES)}.")

        return self._get_json(
            f"{self.API_URL}/v1/pages/album",
            params={"albumId": id, 
                    "deviceType": device,
                    "countryCode": self._country if country is None 
                                    else country})

    def get_artist_page(
            self, id: Union[int, str], *, device: str = "BROWSER",
            country: str = None) -> dict[str, Any]:
    
        """
        Get an artist's TIDAL page.

        Parameters
        ----------
        id : `str`
            TIDAL artist ID.

        device : `str`, keyword-only, default: :code:`"BROWSER"`
            Device type.

            .. container::

               **Valid values**:

               * :code:`"BROWSER"` for a web browser.
               * :code:`"DESKTOP"` for the desktop TIDAL application.
               * :code:`"PHONE"` for the mobile TIDAL application.
               * :code:`"TV"` for the smart TV TIDAL application.
            
        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        page : `dict`
            A dictionary containing the page ID, title, and submodules.
        """

        if device not in self._DEVICE_TYPES:
            raise ValueError("Invalid device type. The supported types "
                             f"are {', '.join(self._DEVICE_TYPES)}.")

        return self._get_json(
            f"{self.API_URL}/v1/pages/artist",
            params={"artistID": id, 
                    "deviceType": device,
                    "countryCode": self._country if country is None 
                                    else country})
    
    def get_mix_page(
            self, uuid: str, *, device: str = "BROWSER", country: str = None
        ) -> dict[str, Any]:
    
        """
        Get a mix's TIDAL page.

        Parameters
        ----------
        uuid : `str`
            TIDAL mix UUID.

        device : `str`, keyword-only, default: :code:`"BROWSER"`
            Device type.

            .. container::

               **Valid values**:

               * :code:`"BROWSER"` for a web browser.
               * :code:`"DESKTOP"` for the desktop TIDAL application.
               * :code:`"PHONE"` for the mobile TIDAL application.
               * :code:`"TV"` for the smart TV TIDAL application.
            
        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        page : `dict`
            A dictionary containing the page ID, title, and submodules.
        """

        if device not in self._DEVICE_TYPES:
            raise ValueError("Invalid device type. The supported types "
                             f"are {', '.join(self._DEVICE_TYPES)}.")

        return self._get_json(
            f"{self.API_URL}/v1/pages/mix",
            params={"mixId": uuid, 
                    "deviceType": device,
                    "countryCode": self._country if country is None 
                                    else country})
    
    def get_video_page(
            self, id: Union[int, str], *, device: str = "BROWSER",
            country: str = None) -> dict[str, Any]:
    
        """
        Get a video's TIDAL page.

        Parameters
        ----------
        id : `str`
            TIDAL video ID.

        device : `str`, keyword-only, default: :code:`"BROWSER"`
            Device type.

            .. container::

               **Valid values**:

               * :code:`"BROWSER"` for a web browser.
               * :code:`"DESKTOP"` for the desktop TIDAL application.
               * :code:`"PHONE"` for the mobile TIDAL application.
               * :code:`"TV"` for the smart TV TIDAL application.
            
        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        page : `dict`
            A dictionary containing the page ID, title, and submodules.
        """

        if device not in self._DEVICE_TYPES:
            raise ValueError("Invalid device type. The supported types "
                             f"are {', '.join(self._DEVICE_TYPES)}.")

        return self._get_json(
            f"{self.API_URL}/v1/pages/videos",
            params={"videoId": id, 
                    "deviceType": device,
                    "countryCode": self._country if country is None 
                                    else country})

    ### PLAYLISTS #############################################################

    def get_playlist(
            self, uuid: Union[int, str], *, country: str = None
        ) -> dict[str, Any]:
        
        """
        Get TIDAL catalog information for a playlist.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist UUID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        playlist : `dict`
            TIDAL catalog information for the playlist in JSON format.
        """
                
        return self._get_json(
            f"{self.API_URL}/v1/playlists/{uuid}",
            params={"countryCode": self._country if country is None 
                                   else country}
        )

    def get_playlist_etag(
            self, uuid: Union[int, str], *, country: str = None) -> str:

        """
        Get a playlist's ETag.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

            **Note**: This method is provided for convenience and is not
            a TIDAL API endpoint.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist UUID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        etag : `str`
            ETag for a TIDAL playlist.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_playlist_etag() "
                               "requires user authentication.")

        resp = self._request(
            "get", 
            f"{self.API_URL}/v1/playlists/{uuid}", 
            params={"countryCode": self._country if country is None
                                   else country}
        )
        return resp.headers["ETag"].replace('"', "")

    def get_playlist_items(
            self, uuid: str, *, country: str = None, limit: int = 100,
            offset: int = None) -> dict[str, Any]:

        """
        Get TIDAL catalog information for all tracks and videos in a
        playlist.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist UUID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`100`
            The maximum number of results to return.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of results.

            **Default**: :code:`0`.

        Returns
        -------
        items : `dict`
            A dictionary containing the items in the playlist and the
            number of results returned.
        """

        return self._get_json(
            f"{self.API_URL}/v1/playlists/{uuid}/items",
            params={"countryCode": self._country if country is None 
                                   else country,
                    "limit": limit, "offset": offset}
        )

    def get_playlist_recommendations(
            self, uuid: str, *, country: str = None, limit: int = None,
            offset: int = None) -> dict[str, Any]:

        """
        Get TIDAL catalog information for a playlist's recommended 
        tracks.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist UUID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, optional
            The maximum number of results to return.

            **Default**: :code:`10`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of results.

            **Default**: :code:`0`.

        Returns
        -------
        items : `dict`
            A dictionary containing the recommended tracks and the
            number of results returned.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_playlist_recommendations() "
                               "requires user authentication.")

        return self._get_json(
            f"{self.API_URL}/v1/playlists/{uuid}/recommendations/items",
            params={"countryCode": self._country if country is None 
                                   else country,
                    "limit": limit, "offset": offset}
        )

    def favorite_playlists(
            self, uuids: Union[str, list[str]], *, folder_id: str = "root"
        ) -> None:
        
        """
        Favorite playlists.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuids : `str`
            TIDAL playlist UUID(s).

        folder_id : `str`, keyword-only, default: :code:`"root"`
            ID of the folder to move the TIDAL playlist into. To place a
            playlist directly under "My Playlists", use 
            :code:`folder_id="root"`.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.add_favorite_playlist() "
                               "requires user authentication.")
        
        self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/add-favorites",
            params={"uuids": uuids, "folderId": folder_id}
        )

    def move_playlist(self, uuid: str, folder_id: str) -> None:

        """
        Move a playlist.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist UUID.

        folder_id : `str`
            ID of the folder to move the TIDAL playlist into. To place a
            playlist directly under "My Playlists", use 
            :code:`folder_id="root"`.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.move_playlist() "
                               "requires user authentication.")

        self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/move",
            params={"trns": f"trn:playlist:{uuid}", "folderId": folder_id}
        )

    def unfavorite_playlist(self, uuid: str) -> None:

        """
        Remove a favorite playlist.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist UUID.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.unfavorite_playlist() "
                               "requires user authentication.")

        self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/remove",
            params={"trns": f"trn:playlist:{uuid}"}
        )

    def get_user_playlist(self, uuid: str) -> dict[str, Any]:

        """
        Get information about a user playlist.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist UUID.

        Returns
        -------
        playlist : `dict`
            Information about the TIDAL playlist.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_user_playlist() "
                               "requires user authentication.")

        return self._get_json(
            f"{self.API_URL}/v2/user-playlists/{uuid}"
        )

    def get_user_playlists(
            self, id: Union[int, str] = None, *, limit: int = 50, 
            offset: int = None, country: str = None) -> dict[str, Any]:

        """
        Get a user's playlists.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `str` 
            TIDAL user ID. If not specified, the current user's ID is
            used.

        limit : `int`, keyword-only, default: :code:`50`
            The maximum number of results to return.

        offset : `int`, keyword-only, optional
            Index of the first result to return. Use with `limit` to get
            the next page of search results.

            **Default**: :code:`0`.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_user_playlists() "
                               "requires user authentication.")

        if id is None:
            id = self._me["userId"]

        return self._get_json(
            f"{self.API_URL}/v1/users/{id}/playlists",
            params={"limit": limit, "offset": offset,
                    "countryCode": self._country if country is None 
                                   else country}
        )

    def get_user_public_playlists(
            self, id: Union[int, str] = None, *, limit: int = 50, 
            cursor: str = None) -> dict[str, Any]:

        """
        Get a user's public playlists.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `str` 
            TIDAL user ID. If not specified, the current user's ID is
            used.

        limit : `int`, keyword-only, default: :code:`50`
            The maximum number of results to return.

        cursor : `str`, keyword-only, optional
            Cursor position of the last item in previous search results.
            Use with `limit` to get the next page of search results.

        Returns
        -------
        playlists : `dict`
            A dictionary containing the user's playlists and the cursor
            position.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_user_public_playlists() "
                               "requires user authentication.")

        if id is None:
            id = self._me["userId"]

        return self._get_json(f"{self.API_URL}/v2/user-playlists/{id}/public",
                              params={"limit": limit, "cursor": cursor})

    def get_my_playlists(
            self, folder_uuid: str = None, *, flattened: bool = False,
            include: str = None, limit: int = 50, order: str = "DATE",
            order_direction: str = "DESC") -> list[dict[str, Any]]:

        """
        Get the current user's playlist folders and playlists.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        folder_uuid : `str`, optional
            UUID of the folder in which to look for playlists and other
            folders. If not specified, all folders and playlists in "My
            Playlists" are returned.

        flattened : `bool`, keyword-only, default: :code:`False`
            Determines whether the results are flattened into a list.

        include : `str`, keyword-only, optional
            Type of playlist-related item to return.

            **Valid values**: :code:`"FAVORITE_PLAYLIST"`, 
            :code:`"FOLDER"`, and :code:`"PLAYLIST"`.

        limit : `int`, keyword-only, default: :code:`50`
            The maximum number of results to return.

        order : `str`, keyword-only, default: :code:`"DATE"`
            Sorting order.

            **Valid values**: :code:`"DATE"`, :code:`"DATE_UPDATED"`, 
            and :code:`"NAME"`.

        order_direction : `str`, keyword-only, default: :code:`"DESC"`
            Sorting order direction.

            **Valid values**: :code:`"DESC"` and :code:`"ASC"`.

        Returns
        -------
        items : `dict`
            A dictionary containing playlist-related items and the total
            number of items available.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_my_playlists() "
                               "requires user authentication.")
        
        _allowed_includes = {None, "FAVORITE_PLAYLIST", "FOLDER", "PLAYLIST"}
        if include not in _allowed_includes:
            raise ValueError("Invalid include type. The supported "
                             f"types are {', '.join(_allowed_includes)}.")

        url = f"{self.API_URL}/v2/my-collection/playlists/folders"
        params = {}

        if flattened:
            url += "flattened"
        else:
            params["folderId"] = folder_uuid if folder_uuid else "root"

        return self._get_json(
            url,
            params={"limit": limit, "includeOnly": include,
                    "order": order, "orderDirection": order_direction} | params
        )

    def update_playlist(
            self, uuid: str, *, title: str = None, description: str = None
        ) -> None:

        """
        Update the title or description of a playlist owned by the
        current user.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist UUID.

        title : `str`, keyword-only, optional
            New playlist title.

        description : `str`, keyword-only, optional
            New playlist description.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.update_playlist() "
                               "requires user authentication.")

        body = {}
        if title is None and description is None:
            raise ValueError("Nothing to update!")
        if title is not None:
            body["title"] = title
        if description is not None:
            body["description"] = description

        self._request("post", f"{self.API_URL}/v1/playlists/{uuid}", json=body)

    def set_playlist_privacy(self, uuid: str, public: bool) -> None:

        """
        Set the privacy of a playlist owned by the current user.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist UUID.

        public : `bool`
            Determines whether the playlist is public (:code:`True`) or
            private (:code:`False`).
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.set_playlist_privacy() "
                               "requires user authentication.")

        self._request("put",
                      f"{self.API_URL}/v2/playlists/{uuid}/"
                      f"set-{'public' if public else 'private'}")

    def create_playlist(
            self, name: str, *, description: str = None, 
            folder_uuid: str = "root", public: bool = None) -> None:
        
        """
        Create a playlist.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        name : `str`
            TIDAL playlist name.

        description : `str`, keyword-only, optional
            Brief playlist description.
        
        folder_uuid : `str`, keyword-only, default: :code:`"root"`
            UUID of the folder the new playlist will be placed in. To 
            place a playlist directly under "My Playlists", use 
            :code:`folder_id="root"`.

        public : `bool`, keyword-only, optional
            Determines whether the playlist is public (:code:`True`) or
            private (:code:`False`).
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.create_playlist() "
                               "requires user authentication.")

        self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/create-playlist",
            params={"name": name, "description": description, 
                    "folderId": folder_uuid, "isPublic": public}
        )

    def delete_playlist(self, uuid: str) -> None:

        """
        Delete a playlist.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist UUID.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.delete_playlist() "
                               "requires user authentication.")

        self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/remove",
            params={"trns": f"trn:playlist:{uuid}"}
        )

    def create_playlist_folder(
            self, name: str, *, folder_id: str = "root") -> None:

        """
        Create a user playlist folder.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        name : `str`
            Playlist folder name.

        folder_id : `str`, keyword-only, default: :code:`"root"`
            ID of the folder in which the new playlist folder should be
            created in. To create a folder directly under "My 
            Playlists", use :code:`folder_id="root"`.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.create_playlist_folder() "
                               "requires user authentication.")
        
        self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/create-folder",
            params={"name": name, "folderId": folder_id}
        )

    def delete_playlist_folder(self, uuid: str) -> None:

        """
        Delete a user playlist folder.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist folder UUID.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.delete_playlist_folder() "
                               "requires user authentication.")
        
        self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/remove",
            params={"trns": f"trn:folder:{uuid}"}
        )

    def add_playlist_items(
            self, uuid: str, 
            items: Union[int, str, list[Union[int, str]]] = None, *, 
            from_playlist_uuid: str = None, on_duplicate: str = "FAIL", 
            on_not_found: str = "FAIL") -> None:
        
        """
        Add items to a user playlist.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist UUID.

        items : `int`, `str`, or `list`, optional
            Items to add to the playlist. If not specified, 
            `from_playlist_uuid` must be provided. 
            
            .. note::
                
               If both `items` and `from_playlist_uuid` are specified,
               only the items in `items` will be added to the playlist.

        from_playlist_uuid : `str`, keyword-only, optional
            TIDAL playlist from which to copy items.
        
        on_duplicate : `str`, keyword-only, default: :code:`"FAIL"`
            Behavior when the item to be added is already in the 
            playlist.

            **Valid values**: :code:`"ADD"`, :code:`"SKIP"`, and 
            :code:`"FAIL"`.

        on_not_found : `str`, keyword-only, default: :code:`"FAIL"`
            Behavior when the item to be added does not exist.

            **Valid value**: :code:`"FAIL"`.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.add_playlist_items() "
                               "requires user authentication.")

        if items is None and from_playlist_uuid is None:
            raise ValueError(f"No items to add to playlist!")
        elif items:
            body = {"trackIds": items}
        else:
            body = {"fromPlaylistUuid": from_playlist_uuid}

        self._request(
            "put",
            f"{self.API_URL}/v1/playlist/{uuid}/items",
            json=body | {"onArtifactNotFound": on_not_found, 
                         "onDuplicate": on_duplicate}
        )

    def move_playlist_item(
            self, uuid: str, from_index: Union[int, str], 
            to_index: Union[int, str]) -> None:
        
        """
        Move an item in a user playlist.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist UUID.

        from_index : `int` or `str`
            Current item index.

        to_index : `int` or `str`
            Desired item index.
        """
        
        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.move_playlist_item() "
                               "requires user authentication.")

        self._request(
            "put",
            f"{self.API_URL}/v1/playlists/{uuid}/items/{from_index}",
            params={"toIndex": to_index}
        )

    def delete_playlist_item(
            self, uuid: str, index: Union[int, str]) -> None:
        
        """
        Delete an item from a user playlist.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        uuid : `str`
            TIDAL playlist UUID.

        index : `int` or `str`
            Item index.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.delete_playlist_item() "
                               "requires user authentication.")

        self._request(
            "delete",
            f"{self.API_URL}/v1/playlists/{uuid}/items/{index}",
            headers={"If-None-Match": self.get_playlist_etag(uuid)}
        )

    ### SEARCH ################################################################

    def search(
            self, query: str, *, type: str, limit: int = None, 
            offset: int = None, country: str = None) -> dict[str, Any]:
    
        """
        Search TIDAL for media and performers.

        Parameters
        ----------
        query : `str`
            Search query.

        type : `str`, keyword-only, optional
            Specific media type to search for.

            **Valid values**: :code:`"artist"`, :code:`"album"`, 
            :code:`"playlist"`, :code:`"track"`, :code:`"userProfile"`,
            and :code:`"video"`.

        limit : `int`, keyword-only, optional
            Maximum number of results to return.

            **Default**: :code:`10`.

        offset : `int`, keyword-only, optional
            Index of the first result to return. Use with `limit` to get
            the next page of search results.

            **Default**: :code:`0`.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        results : `dict`
            The search results in JSON format.
        """

        url = f"{self.API_URL}/v1/search"
        if type:
            if type not in self._MEDIA_TYPES:
                raise ValueError("Invalid media type. The supported "
                                 f"types are {', '.join(self._MEDIA_TYPES)}.")
            url += f"/{type}s"

        return self._get_json(
            url,
            params={"query": query, "type": type,
                    "limit": limit, "offset": offset,
                    "countryCode": self._country if country is None
                                   else country}
        )

    ### STREAMS ###############################################################

    def get_streams(
            self, id: Union[int, str], type: str, *, device: str = "BROWSER",
            audio_quality: str = "HI_RES", video_quality: str = "HIGH", 
            playback_mode: str = "STREAM", asset_presentation: str = "FULL", 
            streaming_session_id: str = None, save: bool = False, 
            path: str = None, folder: bool = False, metadata: bool = True
        ) -> Union[None, list[bytes]]:

        """
        Get audio and video stream data for all tracks and videos in an 
        album, mix, or playlist.

        .. admonition:: OAuth 2.0 authentication

           Requires user authentication for high-quality, offline, or 
           full audio and video streams.

        .. note::
           This method is provided for convenience and is not a TIDAL 
           API endpoint.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL collection ID or UUID.

        type : `str`
            TIDAL collection type.

            **Valid values**: :code:`"album"`, :code:`"mix"`, and 
            :code:`"playlist"`.

        device : `str`, keyword-only, default: :code:`"BROWSER"`
            Device type.

            .. container::

               **Valid values**:

               * :code:`"BROWSER"` for a web browser.
               * :code:`"DESKTOP"` for the desktop TIDAL application.
               * :code:`"PHONE"` for the mobile TIDAL application.
               * :code:`"TV"` for the smart TV TIDAL application.

        audio_quality : `str`, keyword-only, default: :code:`"HI-RES"`
            Audio quality.

            .. container::

               **Valid values**:

               * :code:`"LOW"` for 64 kbps (22.05 kHz) MP3 without user 
                 authentication or 96 kbps AAC with user authentication.
               * :code:`"HIGH"` for 320 kbps AAC.
               * :code:`"LOSSLESS"` for 1411 kbps (16-bit, 44.1 kHz) ALAC 
                 or FLAC.
               * :code:`"HI_RES"` for Up to 9216 kbps (24-bit, 96 kHz) 
                 MQA-encoded FLAC.

        video_quality : `str`, keyword-only, default: :code:`"HIGH"`
            Video quality.

            **Valid values**: :code:`"AUDIO_ONLY"`, :code:`"LOW"`,
            :code:`"MEDIUM"`, and :code:`"HIGH"`.

        playback_mode : `str`, keyword-only, default: :code:`"STREAM"`
            Playback mode.

            **Valid values**: :code:`"STREAM"` and :code:`"OFFLINE"`.

        asset_presentation : `str`, keyword-only, default: :code:`"FULL"`

            Asset presentation.

            .. container::

               **Valid values**:
            
               * :code:`"FULL"`: Full track or video.
               * :code:`"PREVIEW"`: 30-second preview of the track or 
                 video.

        streaming_session_id : `str`, keyword-only, optional
            Streaming session ID.

        save : `bool`, keyword-only, default: :code:`False`
            Determines whether the stream is saved to an audio file.

        path : `str`, keyword-only, optional
            If :code:`save=True`, path in which the audio file is saved.

        folder : `bool`, keyword-only, default: :code:`False`
            Determines whether a folder in `path` (or in the current
            directory if `path` is not specified) is created to hold the
            audio file.

        metadata : `bool`, keyword-only, default: :code:`True`
            Determines whether the audio file's metadata is
            populated.

        Returns
        -------
        stream : `bytes`
            Audio stream data. If :code:`save=True`, :code:`None` is 
            returned and the stream data is saved to an audio file 
            instead.
        """

        if type not in self._COLLECTION_TYPES:
            raise ValueError("Invalid collection type. The supported " 
                             f"types are {', '.join(self._COLLECTION_TYPES)}.")

        if type == "album":
            data = self.get_album(id)
            artist = utility.multivalue_formatter(
                [a["name"] for a in data["artists"] if a["type"] == "MAIN"], 
                False
            )
            title = data["title"]
        elif type == "mix":
            data = self.get_mix_page(id, device=device)
            artist = data["rows"][0]["modules"][0]["mix"]["subTitle"]
            title = data["rows"][0]["modules"][0]["mix"]["title"]
        else:
            data = self.get_playlist(id)
            artist = utility.multivalue_formatter(
                [a["name"] for a in data["promotedArtists"] if a["type"] == "MAIN"], 
                False
            )
            title = data["title"]

        if save:
            if path is not None:
                os.chdir(path)
            if folder:
                dirname = f"{artist} - {title}"
                if not os.path.isdir(dirname):
                    os.mkdir(dirname)
                os.chdir(dirname)
        else:
            streams = []

        if type == "album":
            items = self.get_album_items(id)["items"]
        elif type == "mix":
            items = self.get_mix_items(id)["items"]
        else:
            items = self.get_playlist_items(id)["items"]

        for item in items:
            if item["type"] == "track":
                stream = self.get_track_stream(
                    item["item"]["id"], audio_quality=audio_quality, 
                    playback_mode=playback_mode, 
                    asset_presentation=asset_presentation,
                    streaming_session_id=streaming_session_id,
                    save=save, metadata=metadata, album_data=data
                )
            elif item["type"] == "video":
                stream = self.get_video_stream(
                    item["item"]["id"], video_quality=video_quality, 
                    playback_mode=playback_mode, 
                    asset_presentation=asset_presentation,
                    streaming_session_id=streaming_session_id,
                    save=save, metadata=metadata
                )
            if not save:
                streams.append(stream)
        
        if not save:
            return streams
        elif folder:
            os.chdir("..")

    def get_track_stream(
            self, id: Union[int, str], *, audio_quality: str = "HI_RES", 
            playback_mode: str = "STREAM", asset_presentation: str = "FULL",
            streaming_session_id: str = None, album_data: dict = None,
            save: bool = False, path: str = None, folder: bool = False, 
            metadata: bool = True) -> Union[None, bytes]:

        """
        Get a track's audio stream data.

        .. admonition:: OAuth 2.0 authentication

           Requires user authentication for high-quality, offline, or 
           full audio streams.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL track ID.

        audio_quality : `str`, keyword-only, default: :code:`"HI-RES"`
            Audio quality.

            .. container::

               **Valid values**:

               * :code:`"LOW"` for 64 kbps (22.05 kHz) MP3 without user 
                 authentication or 96 kbps AAC with user authentication.
               * :code:`"HIGH"` for 320 kbps AAC.
               * :code:`"LOSSLESS"` for 1411 kbps (16-bit, 44.1 kHz) ALAC 
                 or FLAC.
               * :code:`"HI_RES"` for Up to 9216 kbps (24-bit, 96 kHz) 
                 MQA-encoded FLAC.

        playback_mode : `str`, keyword-only, default: :code:`"STREAM"`
            Playback mode.

            **Valid values**: :code:`"STREAM"` and :code:`"OFFLINE"`.

        asset_presentation : `str`, keyword-only, default: :code:`"FULL"`
            Asset presentation.

            .. container::

               **Valid values**:
            
               * :code:`"FULL"`: Full track.
               * :code:`"PREVIEW"`: 30-second preview of the track.

        streaming_session_id : `str`, keyword-only, optional
            Streaming session ID.

        album_data : `dict`, keyword-only, optional
            TIDAL catalog information for an album. If not provided, it
            will be retrieved.

        save : `bool`, keyword-only, default: :code:`False`
            Determines whether the stream is saved to an audio file.

        path : `str`, keyword-only, optional
            If :code:`save=True`, path in which the audio file is saved.

        folder : `bool`, keyword-only, default: :code:`False`
            Determines whether a folder in `path` (or in the current
            directory if `path` is not specified) is created to hold the
            audio file.

        metadata : `bool`, keyword-only, default: :code:`True`
            Determines whether the audio file's metadata is
            populated.

        Returns
        -------
        stream : `bytes`
            Audio stream data. If :code:`save=True`, :code:`None` is 
            returned and the stream data is saved to an audio file 
            instead.
        """

        data = self.get_track(id)
        if album_data is None:
            album_data = self.get_album(data["album"]["id"])
        artist = utility.multivalue_formatter(
            [a["name"] for a in album_data["artists"] if a["type"] == "MAIN"],
            False
        )
        title = data["title"]

        if save:
            if path is not None:
                os.chdir(path)
            if folder:
                dirname = f"{artist} - {title}"
                if not os.path.isdir(dirname):
                    os.mkdir(dirname)
                os.chdir(dirname)

        manifest = base64.b64decode(
            self.get_track_playback_info(
                id, 
                audio_quality=audio_quality, 
                playback_mode=playback_mode, 
                asset_presentation=asset_presentation,
                streaming_session_id=streaming_session_id
            )["manifest"]
        )

        if b"urn:mpeg:dash" in manifest:
            manifest = minidom.parseString(manifest)
            codec = manifest.getElementsByTagName(
                "Representation"
            )[0].getAttribute("codecs")
            if "." in codec:
                codec = codec[:codec.index(".")]
            format = self._AUDIO_FORMATS_EXTENSIONS[codec]
            segment = manifest.getElementsByTagName("SegmentTemplate")[0]
            stream = bytearray()
            with urllib.request.urlopen(
                    segment.getAttribute("initialization")
                ) as r:
                stream.extend(r.read())
            for i in range(1, sum(int(tl.getAttribute("r")) 
                                  if tl.hasAttribute("r") else 1 
                                  for tl in 
                                  segment.getElementsByTagName("S")) + 1):
                with urllib.request.urlopen(
                        segment.getAttribute("media").replace(
                            "$Number$", str(i)
                        )
                    ) as r:
                    stream.extend(r.read())
        else:
            manifest = json.loads(manifest)
            codec = manifest["codecs"]
            if "." in codec:
                codec = codec[:codec.index(".")]
            format = self._AUDIO_FORMATS_EXTENSIONS[codec]
            with urllib.request.urlopen(manifest["urls"][0]) as r:
                stream = r.read()
            if manifest["encryptionType"] != "NONE":
                d_key_id = base64.b64decode(manifest['keyId'])
                d_id = AES.new(self._MASTER_KEY, AES.MODE_CBC, 
                                d_key_id[:16]).decrypt(d_key_id[16:])
                d_key, d_nonce = d_id[:16], d_id[16:24]
                stream = AES.new(
                    d_key, AES.MODE_CTR,
                    counter=Counter.new(64, prefix=d_nonce, 
                                        initial_value=0)
                ).decrypt(stream)
        
        if save:
            file = (f"{data['trackNumber']:02} "
                    f"{data['title'].translate(self._ILLEGAL_CHARACTERS)}"
                    f".{self._AUDIO_FORMATS_EXTENSIONS[format]}")
            with open(file, "wb") as f:
                f.write(stream)

            if metadata:
                try:
                    Track = audio.Audio(file)
                except:
                    tempfile = f"temp_{file}"
                    subprocess.run(
                        f"ffmpeg -y -i '{file}' -c:a copy '{tempfile}'",
                        shell=True
                    )
                    os.remove(file)
                    os.rename(tempfile, file)
                    Track = audio.Audio(file)

                Track.from_tidal(
                    data,
                    album_data=album_data,
                    composers=self.get_track_composers(id),
                    artwork=self.get_image(data["album"]["cover"], "album"),
                    lyrics=self.get_track_lyrics(id), comment=data["url"]
                )
                Track.write_metadata()

            if folder:
                os.chdir("..")
        
        else:
            return stream
        
    def get_video_stream(
            self, id: Union[int, str], *, video_quality: str = "HIGH",
            max_resolution: int = 2160, playback_mode: str = "STREAM", 
            asset_presentation: str = "FULL", streaming_session_id: str = None,
            save: bool = False, path: str = None, folder: bool = False, 
            metadata: bool = True) -> Union[None, bytes]:

        """
        Get a video's audio and video stream data.

        .. admonition:: OAuth 2.0 authentication

           Requires user authentication for high-quality, offline, or 
           full video streams.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL video ID.

        video_quality : `str`, keyword-only, default: :code:`"HIGH"`
            Video quality.

            **Valid values**: :code:`"AUDIO_ONLY"`, :code:`"LOW"`,
            :code:`"MEDIUM"`, and :code:`"HIGH"`.

        max_resolution : `int`, keyword-only, default: :code:`2160`
            Maximum video resolution (number of vertical pixels).

        playback_mode : `str`, keyword-only, default: :code:`"STREAM"`
            Playback mode.

            **Valid values**: :code:`"STREAM"` and :code:`"OFFLINE"`.

        asset_presentation : `str`, keyword-only, default: :code:`"FULL"`
            Asset presentation.

            .. container::

               **Valid values**:
            
               * :code:`"FULL"`: Full video.
               * :code:`"PREVIEW"`: 30-second preview of the video.

        streaming_session_id : `str`, keyword-only, optional
            Streaming session ID.

        save : `bool`, keyword-only, default: :code:`False`
            Determines whether the stream is saved to a video file.

        path : `str`, keyword-only, optional
            If :code:`save=True`, path in which the video file is saved.

        folder : `bool`, keyword-only, default: :code:`False`
            Determines whether a folder in `path` (or in the current
            directory if `path` is not specified) is created to hold the
            video file.

        metadata : `bool`, keyword-only, default: :code:`True`
            Determines whether the video file's metadata is
            populated.

        Returns
        -------
        stream : `bytes`
            Video stream data. If :code:`save=True`, :code:`None` is 
            returned and the stream data is saved to a video file 
            instead.
        """

        data = self.get_video(id)
        artist = utility.multivalue_formatter(
            [a["name"] for a in data["artists"] if a["type"] == "MAIN"],
            False
        )
        title = data["title"]

        if save:
            if path is not None:
                os.chdir(path)
            if folder:
                dirname = f"{artist} - {title}"
                if not os.path.isdir(dirname):
                    os.mkdir(dirname)
                os.chdir(dirname)

        manifest = base64.b64decode(
            self.get_video_playback_info(
                id, 
                video_quality=video_quality, 
                playback_mode=playback_mode, 
                asset_presentation=asset_presentation,
                streaming_session_id=streaming_session_id
            )["manifest"]
        )

        m3u8 = next(
            pl for res, pl in re.findall(
                "(?<=RESOLUTION=)\d+x(\d+)\n(http.*)", 
                requests.get(
                    json.loads(manifest)["urls"][0]
                ).content.decode("utf-8")
            )[::-1] if int(res) < max_resolution
        )

        stream = bytearray()
        for ts in re.findall("(?<=\n).*(http.*)", 
                             requests.get(m3u8).content.decode("utf-8")):
            with urllib.request.urlopen(ts) as r:
                stream.extend(r.read())

        if save:
            file = (f"{data['trackNumber']:02} "
                    f"{data['title'].translate(self._ILLEGAL_CHARACTERS)}.mkv")
            with open(file, "wb") as f:
                f.write(stream)

            if metadata:
                # TODO
                pass

            if folder:
                os.chdir("..")
        
        else:
            return stream

    ### TRACKS ################################################################

    def get_track(
            self, id: Union[int, str], *, country: str = None
        ) -> dict[str, Any]:
        
        """
        Get TIDAL catalog information for a track.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL track ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        track : `dict`
            TIDAL catalog information for the track in JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/v1/tracks/{id}",
            params={"countryCode": self._country if country is None 
                                   else country}
        )

    def get_track_composers(self, id: Union[int, str]) -> list[str]:

        """
        Get the composers, lyricists, and/or writers of a track.

        .. note::
           This method is provided for convenience and is not a TIDAL 
           API endpoint.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL track ID.
        
        Returns
        -------
        composers : `list`
            The composers, lyricists, and/or writers of the track.
        """
        
        lookup = set()
        return [p["name"] for p in self.get_track_contributors(id)["items"]
                if p["role"] in self._COMPOSER_ROLES 
                and p["name"] not in lookup
                and lookup.add(p["name"]) is None]

    def get_track_contributors(
            self, id: Union[int, str], *, country: str = None, 
            limit: int = None, offset: int = None) -> dict[str, Any]:

        """
        Get the contributors of a track.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL track ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, optional
            The maximum number of results to return.

            **Default**: :code:`10`.

        offset : `int`, keyword-only, optional
            The index of the first result to return. Use with `limit` to
            get the next page of results.

            **Default**: :code:`0`.

        Returns
        -------
        contributors : `dict`
            A dictionary containing the track's contributors and the
            number of results returned.
        """

        return self._get_json(
            f"{self.API_URL}/v1/tracks/{id}/contributors",
            params={"countryCode": self._country if country is None 
                                   else country,
                    "limit": limit, "offset": offset}
        )

    def get_track_credits(
            self, id: Union[int, str], *, country: str = None
        ) -> Union[dict[str, Any], None]:

        """
        Get credits for a track.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL track ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        credits : `dict`
            A dictionary containing the track contributors.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_track_credits() "
                               "requires user authentication.")

        return self._get_json(
            f"{self.API_URL}/v1/tracks/{id}/credits",
            params={"countryCode": self._country if country is None 
                                   else country}
        )

    def get_track_lyrics(
            self, id: Union[int, str], *, country: str = None
        ) -> Union[dict[str, Any], None]:

        """
        Get lyrics for a track.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL track ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        lyrics : `dict`
            A dictionary containing formatted and time-synced lyrics. If
            no lyrics are available, :code:`None` is returned.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_track_lyrics() "
                               "requires user authentication.")

        try:
            return self._get_json(
                f"{self.WEB_URL}/v1/tracks/{id}/lyrics",
                params={"countryCode": self._country if country is None 
                                       else country}
            )
        except:
            return None
        
    def get_track_mix(
            self, id: Union[int, str], *, country: str = None) -> str:
        
        """
        Get the curated mix of tracks related to a track.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL track ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        **kwargs
            Additional keyword arguments to pass as parameters in the
            request URL, like `locale` and `deviceType`.

        Returns
        -------
        mix_id : `str`
            TIDAL mix ID.
        """

        return self._get_json(
            f"{self.API_URL}/v1/tracks/{id}/mix",
            params={"countryCode": self._country if country is None 
                                   else country}
        )["id"]

    def get_track_playback_info(
            self, id: Union[int, str], *, audio_quality: str = "HI_RES", 
            playback_mode: str = "STREAM", asset_presentation: str = "FULL",
            streaming_session_id: str = None) -> dict[str, Any]:
        
        """
        Get playback information for a track.

        .. admonition:: OAuth 2.0 authentication

           Requires user authentication for high-quality, offline, or 
           full audio playback information.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL track ID.

        audio_quality : `str`, keyword-only, default: :code:`"HI-RES"`
            Audio quality.

            .. container::

               **Valid values**:

               * :code:`"LOW"` for 64 kbps (22.05 kHz) MP3 without user 
                 authentication or 96 kbps AAC with user authentication.
               * :code:`"HIGH"` for 320 kbps AAC.
               * :code:`"LOSSLESS"` for 1411 kbps (16-bit, 44.1 kHz) ALAC 
                 or FLAC.
               * :code:`"HI_RES"` for Up to 9216 kbps (24-bit, 96 kHz) 
                 MQA-encoded FLAC.

        playback_mode : `str`, keyword-only, default: :code:`"STREAM"`
            Playback mode.

            **Valid values**: :code:`"STREAM"` and :code:`"OFFLINE"`.

        asset_presentation : `str`, keyword-only, default: :code:`"FULL"`
            Asset presentation.

            .. container::

               **Valid values**:
            
               * :code:`"FULL"`: Full track.
               * :code:`"PREVIEW"`: 30-second preview of the track.

        streaming_session_id : `str`, keyword-only, optional
            Streaming session ID.

        Returns
        -------
        info : `dict`
            Track playback information.
        """

        if audio_quality not in self._AUDIO_QUALITIES:
            raise ValueError("Invalid audio quality. The supported "
                             "qualities are "
                             f"{', '.join(self._AUDIO_QUALITIES)}.")
        if playback_mode not in self._PLAYBACK_MODES:
            raise ValueError("Invalid playback mode. The supported "
                             "playback modes are "
                             f"{', '.join(self._PLAYBACK_MODES)}.")
        if asset_presentation not in self._ASSET_PRESENTATIONS:
            raise ValueError("Invalid asset presentation. The "
                             "supported asset presentations are "
                             f"{', '.join(self._ASSET_PRESENTATIONS)}.")

        if (audio_quality != "LOW" or playback_mode != "STREAM" 
            or asset_presentation != "PREVIEW") \
                and "Authorization" not in self.session.headers:
            raise RuntimeError(
                "tidal.Session.get_track_playback_info() requires user "
                f"authentication when {audio_quality=}, "
                f"{playback_mode=}, and {asset_presentation=}."
            )
        
        url = f"{self.API_URL}/v1/tracks/{id}/playbackinfo"
        url += "postpaywall" if "Authorization" in self.session.headers \
               else "prepaywall"
        
        return self._get_json(
            url,
            params={
                "audioquality": audio_quality,
                "assetpresentation": asset_presentation,
                "playbackmode": playback_mode,
                "streamingsessionid": streaming_session_id
            }
        )

    def get_track_recommendations(
            self, id: Union[int, str], *, country: str = None, 
            limit: int = None) -> dict[str, Any]:

        """
        Get TIDAL catalog information for a track's recommended 
        tracks and videos.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL track ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.
            
        limit : `int`, keyword-only, optional
            The maximum number of results to return.

            **Default**: :code:`10`.

        Returns
        -------
        recommendations : `dict`
            A dictionary containing recommendations based on a track.
        """
        
        return self._get_json(
            f"{self.API_URL}/v1/tracks/{id}/recommendations",
            params={"limit": limit,
                    "countryCode": self._country if country is None 
                                   else country}
        )

    def get_favorite_tracks(
            self, *, limit: int = 50, offset: int = None, order: str = "DATE",
            order_direction: str = "DESC", country: str = None):
        
        """
        Get the current user's favorite tracks.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        limit : `int`, keyword-only, default: :code:`50`
            The maximum number of results to return.

        offset : `int`, keyword-only, optional
            Index of the first result to return. Use with `limit` to get
            the next page of search results.

            **Default**: :code:`0`.
            
        order : `str`, keyword-only, default: :code:`"DATE"`
            Sorting order.

            **Valid values**: :code:`"DATE"` and :code:`"NAME"`.

        order_direction : `str`, keyword-only, default: :code:`"DESC"`
            Sorting order direction.

            **Valid values**: :code:`"DESC"` and :code:`"ASC"`.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        tracks : `dict`
            A dictionary containing the current user's tracks and the
            number of results returned.
        """
        
        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_favorite_tracks() "
                               "requires user authentication.")

        return self._get_json(
            f"{self.API_URL}/v1/users/{self._me['userId']}/favorites/tracks", 
            params={"limit": limit, "offset": offset,
                    "order": order, "orderDirection": order_direction, 
                    "countryCode": self._country if country is None
                                   else country}
        )

    def favorite_tracks(
            self, ids: Union[int, str, list[Union[int, str]]], *, 
            on_not_found: str = "FAIL", country: str = None) -> None:

        """
        Favorite tracks.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        ids : `int`, `str`, or `list`
            TIDAL track ID(s).

        on_not_found : `str`, keyword-only, default: :code:`"FAIL"`
            Behavior when the item to be added does not exist.

            **Valid value**: :code:`"FAIL"`.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.favorite_tracks() "
                               "requires user authentication.")

        self._request(
            "post", 
            f"{self.API_URL}/v1/users/{self._me['userId']}/favorites/tracks",
            params={"countryCode": self._country if country is None
                                   else country},
            data={"trackIds": ids, "onArtifactNotFound": on_not_found}
        )

    def unfavorite_tracks(self, ids: Union[int, str, list[Union[int, str]]]):

        """
        Unfavorite tracks.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        ids : `int`, `str`, or `list`
            TIDAL track ID(s).
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.unfavorite_tracks() "
                               "requires user authentication.")
        
        if isinstance(ids, list):
            ids = ",".join(map(str, ids))

        self._request("delete", 
                      f"{self.API_URL}/v1/users/{self._me['userId']}"
                      f"/favorites/tracks/{ids}")

    ### USERS #################################################################

    def get_user(self, id: Union[int, str]) -> dict[str, Any]:

        """
        Get a user's profile information.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `str` 
            TIDAL user ID. If not specified, the current user's ID is
            used.

        Returns
        -------
        user : `dict`
            A dictionary containing the user's profile information.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_user() requires user "
                               "authentication.")

        if id is None:
            id = self._me["userId"]

        return self._get_json(f"{self.API_URL}/v2/profiles/{id}")

    def get_user_favorites(self, id: Union[int, str] = None) -> dict[str, Any]:

        """
        Get a user's favorite albums, artists, playlists, tracks, and
        videos.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `int` or `str`, optional 
            TIDAL user ID. If not specified, the current user's ID is
            used.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_user_favorites() "
                               "requires user authentication.")

        if id is None:
            id = self._me["userId"]
        
        return self._get_json(f"{self.API_URL}/v1/users/{id}/favorites/ids")

    def get_user_followers(
            self, id: Union[int, str] = None, *, limit: int = 500, 
            cursor: str = None) -> dict[str, Any]:

        """
        Get a user's followers.
        
        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `int` or `str`, optional 
            TIDAL user ID. If not specified, the current user's ID is
            used.

        limit : `int`, keyword-only, default: :code:`500`
            The maximum number of results to return.

        cursor : `str`, keyword-only, optional
            Cursor position of the last item in previous search results.
            Use with `limit` to get the next page of search results.

        Returns
        -------
        followers : `dict`
            A dictionary containing the user's followers and the cursor
            position.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_user_followers() "
                               "requires user authentication.")

        if id is None:
            id = self._me["userId"]

        return self._get_json(f"{self.API_URL}/v2/profiles/{id}/followers",
                              params={"limit": limit, "cursor": cursor})

    def get_user_following(
            self, id: Union[int, str] = None, *, include: str = None,
            limit: int = 500, cursor: str = None):

        """
        Get the people (artists, users, etc.) a user follows.
        
        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `int` or `str`, optional 
            TIDAL user ID. If not specified, the current user's ID is
            used.

        include : `str`, keyword-only, optional
            Type of people to return.

            **Valid values**: :code:`"ARTIST"` and :code:`"USER"`.

        limit : `int`, keyword-only, default: :code:`500`
            The maximum number of results to return.

        cursor : `str`, keyword-only, optional
            Cursor position of the last item in previous search results.
            Use with `limit` to get the next page of search results.

        Returns
        -------
        followers : `dict`
            A dictionary containing the user's followers and the cursor
            position.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_user_following() "
                               "requires user authentication.")

        _allowed_includes = {None, "ARTIST", "USER"}
        if include not in _allowed_includes:
            raise ValueError("Invalid include type. The supported "
                             f"types are {', '.join(_allowed_includes)}.")

        if id is None:
            id = self._me["userId"]

        return self._get_json(
            f"{self.API_URL}/v2/profiles/{id}/following",
            params={"includeOnly": include, "limit": limit, "cursor": cursor}
        )

    def get_blocked_users(
            self, *, limit: int = None, offset: int = None) -> dict[str, Any]:

        """
        Get users blocked by the current user.
        
        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            Maximum number of results to return.

            **Default**: :code:`50`.

        offset : `int`, keyword-only, optional
            Index of the first result to return. Use with `limit` to get
            the next page of search results.

            **Default**: :code:`0`.

        Returns
        -------
        users : `dict`
            A dictionary containing the users blocked by the current 
            user and the number of results.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_blocked_users() "
                               "requires user authentication.")
        
        return self._get_json(f"{self.API_URL}/v2/profiles/blocked-profiles",
                              params={"limit": limit, "offset": offset})

    def follow_user(self, id: Union[int, str]) -> None:

        """
        Follow a user.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `int` or `str`, optional 
            TIDAL user ID.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.follow_user() requires "
                               "user authentication.")

        self._request("put", f"{self.API_URL}/v2/follow", 
                      params={"trn": f"trn:user:{id}"})

    def unfollow_user(self, id: Union[int, str]) -> None:

        """
        Unfollow a user.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `int` or `str`, optional 
            TIDAL user ID.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.unfollow_user() requires "
                               "user authentication.")

        self._request("delete", f"{self.API_URL}/v2/follow", 
                      params={"trn": f"trn:user:{id}"})

    def block_user(self, id: Union[int, str]) -> None:

        """
        Block a user.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `int` or `str`, optional 
            TIDAL user ID.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.block_user() requires "
                               "user authentication.")

        self._request("put", f"{self.API_URL}/v2/profiles/block/{id}")

    def unblock_user(self, id: Union[int, str]) -> None:

        """
        Unblock a user.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        id : `int` or `str`, optional 
            TIDAL user ID.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.unblock_user() requires "
                               "user authentication.")

        self._request("delete", f"{self.API_URL}/v2/profiles/block/{id}")

    ### VIDEOS ################################################################

    def get_video(
            self, id: Union[int, str], *, country: str = None
        ) -> dict[str, Any]:
        
        """
        Get TIDAL catalog information for a video.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL video ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.      

        Returns
        -------
        track : `dict`
            TIDAL catalog information for the video in JSON format.
        """
                
        return self._get_json(
            f"{self.API_URL}/v1/videos/{id}",
            params={"countryCode": self._country if country is None 
                                   else country}
        )

    def get_video_playback_info(
            self, id: Union[int, str], *, video_quality: str = "HIGH", 
            playback_mode: str = "STREAM", asset_presentation: str = "FULL",
            streaming_session_id: str = None) -> dict[str, Any]:
        
        """
        Get playback information for a video.

        .. admonition:: OAuth 2.0 authentication

           Requires user authentication for high-quality, offline, or 
           full video playback information.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL video ID.

        video_quality : `str`, keyword-only, default: :code:`"HIGH"`
            Video quality.

            **Valid values**: :code:`"AUDIO_ONLY"`, :code:`"LOW"`,
            :code:`"MEDIUM"`, and :code:`"HIGH"`.

        playback_mode : `str`, keyword-only, default: :code:`"STREAM"`
            Playback mode.

            **Valid values**: :code:`"STREAM"` and :code:`"OFFLINE"`.

        asset_presentation : `str`, keyword-only, default: :code:`"FULL"`
            Asset presentation.

            .. container::

               **Valid values**:
            
               * :code:`"FULL"`: Full video.
               * :code:`"PREVIEW"`: 30-second preview of the video.

        streaming_session_id : `str`, keyword-only, optional
            Streaming session ID.

        Returns
        -------
        info : `dict`
            Video playback information.
        """

        if video_quality not in self._VIDEO_QUALITIES:
            raise ValueError("Invalid video quality. The supported "
                             "qualities are "
                             f"{', '.join(self._VIDEO_QUALITIES)}.")
        if playback_mode not in self._PLAYBACK_MODES:
            raise ValueError("Invalid playback mode. The supported "
                             "playback modes are "
                             f"{', '.join(self._PLAYBACK_MODES)}.")
        if asset_presentation not in self._ASSET_PRESENTATIONS:
            raise ValueError("Invalid asset presentation. The "
                             "supported asset presentations are "
                             f"{', '.join(self._ASSET_PRESENTATIONS)}.")

        if (video_quality != "LOW" or playback_mode != "STREAM" 
            or asset_presentation != "PREVIEW") \
                and "Authorization" not in self.session.headers:
            raise RuntimeError(
                "tidal.Session.get_video_playback_info() requires user "
                f"authentication when {video_quality=}, "
                f"{playback_mode=}, and {asset_presentation=}."
            )
        
        url = f"{self.API_URL}/v1/videos/{id}/playbackinfo"
        url += "postpaywall" if "Authorization" in self.session.headers \
               else "prepaywall"
        
        return self._get_json(
            url,
            params={
                "videoquality": video_quality,
                "assetpresentation": asset_presentation,
                "playbackmode": playback_mode,
                "streamingsessionid": streaming_session_id
            }
        )

    def get_favorite_videos(
            self, *, limit: int = 50, offset: int = None, order: str = "DATE",
            order_direction: str = "DESC", country: str = None):
        
        """
        Get the current user's favorite videos.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        limit : `int`, keyword-only, default: :code:`50`
            The maximum number of results to return.

        offset : `int`, keyword-only, optional
            Index of the first result to return. Use with `limit` to get
            the next page of search results.

            **Default**: :code:`0`.
            
        order : `str`, keyword-only, default: :code:`"DATE"`
            Sorting order.

            **Valid values**: :code:`"DATE"` and :code:`"NAME"`.

        order_direction : `str`, keyword-only, default: :code:`"DESC"`
            Sorting order direction.

            **Valid values**: :code:`"DESC"` and :code:`"ASC"`.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        videos : `dict`
            A dictionary containing the current user's videos and the
            number of results returned.
        """
        
        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.get_favorite_videos() "
                               "requires user authentication.")

        return self._get_json(
            f"{self.API_URL}/v1/users/{self._me['userId']}/favorites/videos", 
            params={"limit": limit, "offset": offset,
                    "order": order, "orderDirection": order_direction, 
                    "countryCode": self._country if country is None
                                   else country}
        )

    def favorite_videos(
            self, ids: Union[int, str, list[Union[int, str]]], *, 
            on_not_found: str = "FAIL", country: str = None) -> None:

        """
        Favorite videos.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        ids : `int`, `str`, or `list`
            TIDAL video ID(s).

        on_not_found : `str`, keyword-only, default: :code:`"FAIL"`
            Behavior when the item to be added does not exist.

            **Valid value**: :code:`"FAIL"`.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.favorite_videos() "
                               "requires user authentication.")

        self._request(
            "post", 
            f"{self.API_URL}/v1/users/{self._me['userId']}/favorites/videos",
            params={"countryCode": self._country if country is None
                                   else country},
            data={"videoIds": ids, "onArtifactNotFound": on_not_found}
        )

    def unfavorite_videos(self, ids: Union[int, str, list[Union[int, str]]]):

        """
        Unfavorite videos.

        .. admonition:: OAuth 2.0 authentication
        
           Requires user authentication.

        Parameters
        ----------
        ids : `int`, `str`, or `list`
            TIDAL video ID(s).
        """

        if "Authorization" not in self.session.headers:
            raise RuntimeError("tidal.Session.unfavorite_videos() "
                               "requires user authentication.")
        
        if isinstance(ids, list):
            ids = ",".join(map(str, ids))

        self._request("delete", 
                      f"{self.API_URL}/v1/users/{self._me['userId']}"
                      f"/favorites/videos/{ids}")