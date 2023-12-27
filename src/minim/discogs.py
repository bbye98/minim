"""
Discogs
=======
.. moduleauthor:: Benjamin Ye <GitHub: bbye98>
"""

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

from . import (FOUND_FLASK, FOUND_PLAYWRIGHT, VERSION, REPOSITORY_URL, 
               DIR_HOME, DIR_TEMP, config)
if FOUND_FLASK:
    from . import Flask, request
if FOUND_PLAYWRIGHT:
    from . import sync_playwright

__all__ = ["API"]

class _DiscogsRedirectHandler(BaseHTTPRequestHandler):
    
    """
    HTTP request handler for the Discogs OAuth 1.0a flow.
    """

    def do_GET(self):
        
        """
        Handles an incoming GET request and parses the query string.
        """

        self.server.response = dict(
            urllib.parse.parse_qsl(
                urllib.parse.urlparse(f"{self.path}").query
            )
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        status = "denied" if "denied" in self.server.response else "granted" 
        self.wfile.write(
            f"Access {status}. You may close this page now.".encode()
        )

class API:

    """
    Discogs API client.

    The Discogs API lets developers build their own Discogs-powered 
    applications for the web, desktop, and mobile devices. It is a
    RESTful interface to Discogs data and enables accessing JSON-
    formatted information about artists, releases, and labels,
    managing user collections and wantlists, creating marketplace
    listings, and more.

    .. seealso::

       For more information, see the `Discogs API home page 
       <https://www.discogs.com/developers>`_.

    The Discogs API can be accessed with or without authentication.
    (client credentials, personal access token, or OAuth access token 
    and access token secret). However, it is recommended that users at
    least provide client credentials to enjoy higher rate limits and 
    access to image URLs. The consumer key and consumer secret can 
    either be provided to this class's constructor as keyword arguments 
    or be stored as :code:`DISCOGS_CONSUMER_KEY` and 
    :code:`DISCOGS_CONSUMER_SECRET` in the operating system's 
    environment variables. 
    
    .. seealso::

       To get client credentials, see the Registration section of the
       `Authentication page <https://www.discogs.com/developers
       /#page:authentication>`_ of the Discogs API website. To take 
       advantage of Minim's automatic access token retrieval 
       functionality for the OAuth 1.0a flow, the redirect URI should be
       in the form :code:`http://localhost:{port}/callback`, where 
       :code:`{port}` is an open port on :code:`localhost`.
    
    To view and make changes to account information and resources, users
    must either provide a personal access token to this class's 
    constructor as a keyword argument or undergo the OAuth 1.0a flow, 
    which require valid client credentials, using Minim. If an existing
    OAuth access token/secret pair is available, it can be provided to
    this class's constructor as keyword arguments to bypass the access
    token retrieval process.

    .. tip::

       The authorization flow and access token can be changed or updated
       at any time using :meth:`set_flow` and :meth:`set_access_token`,
       respectively.

    Minim also stores and manages access tokens and their properties. 
    When the OAuth 1.0a flow is used to acquire an access token/secret 
    pair, it is automatically saved to the Minim configuration file to 
    be loaded on the next instantiation of this class. This behavior can
    be disabled if there are any security concerns, like if the computer
    being used is a shared device.

    Parameters
    ----------
    consumer_key : `str`, keyword-only, optional
        Consumer key. Required for the OAuth 1.0a flow, and can be used
        in the Discogs authorization flow alongside a consumer secret. 
        If it is not stored as :code:`DISCOGS_CONSUMER_KEY` in the 
        operating system's environment variables or found in the Minim
        configuration file, it can be provided here.

    consumer_secret : `str`, keyword-only, optional
        Consumer secret. Required for the OAuth 1.0a flow, and can be
        used in the Discogs authorization flow alongside a consumer key.
        If it is not stored as :code:`DISCOGS_CONSUMER_SECRET` in the 
        operating system's environment variables or found in the Minim
        configuration file, it can be provided here.

    flow : `str`, keyword-only, optional
        Authorization flow. If :code:`None` and no access token is 
        provided, no user authentication will be performed and client
        credentials will not be attached to requests, even if found or
        provided.

        .. container::

           **Valid values**:

           * :code:`None` for no user authentication.
           * :code:`"discogs"` for the Discogs authentication flow.
           * :code:`"oauth"` for the OAuth 1.0a flow.

    browser : `bool`, keyword-only, default: :code:`False`
        Determines whether a web browser is automatically opened for the
        OAuth 1.0a flow. If :code:`False`, users will have to manually 
        open the authorization URL and provide the full callback URI via
        the terminal.

    web_framework : `str`, keyword-only, optional
        Determines which web framework to use for the OAuth 1.0a flow.
        
        .. container::

           **Valid values**:

           * :code:`"http.server"` for the built-in implementation of
             HTTP servers.
           * :code:`"flask"` for the Flask framework.
           * :code:`"playwright"` for the Playwright framework by 
             Microsoft.

    port : `int` or `str`, keyword-only, default: :code:`8888`
        Port on :code:`localhost` to use for the OAuth 1.0a flow with
        the :code:`http.server` and Flask frameworks. Only used if 
        `redirect_uri` is not specified.

    redirect_uri : `str`, keyword-only, optional
        Redirect URI for the OAuth 1.0a flow. If not on 
        :code:`localhost`, the automatic request access token retrieval
        functionality is not available.

    access_token : `str`, keyword-only, optional
        Personal or OAuth access token. If provided here or found in the
        Minim configuration file, the authentication process is 
        bypassed.

    access_token_secret : `str`, keyword-only, optional
        OAuth access token secret accompanying `access_token`.

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
        Base URL for the Discogs API.

    ACCESS_TOKEN_URL : `str`
        URL for the OAuth 1.0a access token endpoint.

    AUTH_URL : `str`
        URL for the OAuth 1.0a authorization endpoint.

    REQUEST_TOKEN_URL : `str`
        URL for the OAuth 1.0a request token endpoint.
        
    session : `requests.Session`
        Session used to send requests to the Discogs API.
    """

    _FLOWS = {"discogs", "oauth"}
    _NAME = f"{__module__}.{__qualname__}"

    API_URL = "https://api.discogs.com"
    ACCESS_TOKEN_URL = f"{API_URL}/oauth/access_token"
    AUTH_URL = "https://www.discogs.com/oauth/authorize"
    REQUEST_TOKEN_URL = f"{API_URL}/oauth/request_token"

    def __init__(
            self, *, consumer_key: str = None, consumer_secret: str = None,
            flow: str = None, browser: bool = False, web_framework: str = None, 
            port: Union[int, str] = 8888, redirect_uri: str = None, 
            access_token: str = None, access_token_secret: str = None, 
            overwrite: bool = False, save: bool = True) -> None:
        
        """
        Create a Discogs API client.
        """

        self.session = requests.Session()
        self.session.headers["User-Agent"] = f"Minim/{VERSION} +{REPOSITORY_URL}"

        if (access_token is None and config.has_section(self._NAME) 
                and not overwrite):
            flow = config.get(self._NAME, "flow")
            access_token = config.get(self._NAME, "access_token")
            access_token_secret = config.get(self._NAME, "access_token_secret")
            consumer_key = config.get(self._NAME, "consumer_key")
            consumer_secret = config.get(self._NAME, "consumer_secret")
        elif flow is None and access_token is not None:
            flow = "discogs" if access_token_secret is None else "oauth"

        self.set_flow(
            flow, consumer_key=consumer_key, consumer_secret=consumer_secret,
            browser=browser, web_framework=web_framework, port=port, 
            redirect_uri=redirect_uri, save=save
        )
        self.set_access_token(access_token, access_token_secret)

    def _check_authentication(
            self, endpoint: str, token: bool = True) -> None:

        """
        Check if the user is authenticated for the desired endpoint.

        Parameters
        ----------
        endpoint : `str`
            Discogs API endpoint.

        token : `bool`, default: :code:`True`
            Specifies whether a personal access token or OAuth access
            token is required for the endpoint. If :code:`False`, only
            client credentials are required.
        """

        if token and (
                self._flow != "oauth" 
                or self._flow == "discogs" 
                   and "token" not in self.session.headers["Authorization"]
            ):
            emsg = (f"{self._NAME}.{endpoint}() requires user "
                    "authentication.")
            raise RuntimeError(emsg)
        elif self._flow is None:
            emsg = f"{self._NAME}.{endpoint}() requires client credentials."
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
            Keyword arguments to pass to :meth:`requests.request`.

        Returns
        -------
        resp : `dict`
            JSON-encoded content of the response.
        """

        return self._request("get", url, **kwargs).json()

    def _request(
            self, method: str, url: str, *, oauth: dict[str, Any] = None, 
            **kwargs) -> requests.Response:

        """
        Construct and send a request with status code checking.

        Parameters
        ----------
        method : `str`
            Method for the request.

        url : `str`
            URL for the request.

        oauth : `dict`, keyword-only, optional
            OAuth-related values to be included in the authorization
            header.

        **kwargs
            Keyword arguments passed to :meth:`requests.request`.

        Returns
        -------
        resp : `requests.Response`
            Response to the request.
        """

        if self._flow == "oauth" \
                and "Authorization" not in kwargs.get("headers", {}):
            if oauth is None:
                oauth = {}
            oauth = self._oauth | {
                "oauth_nonce": secrets.token_hex(32), 
                "oauth_timestamp": f"{time.time():.0f}"
            } | oauth

            if "headers" not in kwargs:
                kwargs["headers"] = {}
            kwargs["headers"]["Authorization"] = "OAuth " + ", ".join(
                f'{k}="{v}"' for k, v in oauth.items()
            )

        r = self.session.request(method, url, **kwargs)
        if r.status_code not in range(200, 299):
            raise RuntimeError(f"{r.status_code}: {r.json()['message']}")
        return r

    def set_access_token(
            self, access_token: str = None, access_token_secret: str = None
        ) -> None:

        """
        Set the Discogs API personal or OAuth access token (and secret).

        Parameters
        ----------
        access_token : `str`, optional
            Personal or OAuth access token.

        access_token_secret : `str`, optional
            OAuth access token secret.
        """

        if self._flow == "oauth":
            self._oauth = {
                "oauth_consumer_key": self._consumer_key,
                "oauth_signature_method": "PLAINTEXT"
            }

            if access_token is None:
                oauth = {"oauth_signature": f"{self._consumer_secret}&"}
                if self._redirect_uri is not None:
                    oauth["oauth_callback"] = self._redirect_uri
                r = self._request(
                    "get",
                    self.REQUEST_TOKEN_URL, 
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    oauth=oauth
                )
                auth_url = f"{self.AUTH_URL}?{r.text}"
                oauth = dict(urllib.parse.parse_qsl(r.text))

                if self._web_framework == "playwright":
                    har_file = DIR_TEMP / "minim_discogs.har"
                    
                    with sync_playwright() as playwright:
                        browser = playwright.firefox.launch(headless=False)
                        context = browser.new_context(record_har_path=har_file)
                        page = context.new_page()
                        page.goto(auth_url, timeout=0)
                        page.wait_for_url(f"{self._redirect_uri}*", 
                                            wait_until="commit")
                        context.close()
                        browser.close()

                    with open(har_file, "r") as f:
                        oauth |= dict(
                            urllib.parse.parse_qsl(
                                urllib.parse.urlparse(
                                    re.search(f'{self._redirect_uri}\?(.*?)"', 
                                                f.read()).group(0)
                                ).query
                            )
                        )
                    har_file.unlink()

                else:
                    if self._browser:
                        webbrowser.open(auth_url)
                    else:
                        print("To grant Minim access to Discogs data "
                              "and features, open the following link "
                              f"in your web browser:\n\n{auth_url}\n")

                    if self._web_framework == "http.server":
                        httpd = HTTPServer(("", self._port), 
                                           _DiscogsRedirectHandler)
                        httpd.handle_request()
                        oauth |= httpd.response

                    elif self._web_framework == "flask":
                        app = Flask(__name__)
                        json_file = DIR_TEMP / "minim_discogs.json"

                        @app.route("/callback", methods=["GET"])
                        def _callback() -> str:
                            if "error" in request.args:
                                return ("Access denied. You may close "
                                        "this page now.")
                            with open(json_file, "w") as f:
                                json.dump(request.args, f)
                            return ("Access granted. You may close "
                                    "this page now.")

                        server = Process(target=app.run, 
                                         args=("0.0.0.0", self._port))
                        server.start()
                        while not json_file.is_file():
                            time.sleep(0.1)
                        server.terminate()

                        with open(json_file, "rb") as f:
                            oauth |= json.load(f)
                        json_file.unlink()

                    else:
                        oauth["oauth_verifier"] = input(
                            "After authorizing Minim to access Discogs "
                            "on your behalf, enter the displayed code "
                            "below.\n\nCode: "
                        )

                if "denied" in oauth:
                    raise RuntimeError("Authorization failed.")

                oauth["oauth_signature"] = (f"{self._consumer_secret}"
                                            f"&{oauth['oauth_token_secret']}")
                r = self._request(
                    "post",
                    self.ACCESS_TOKEN_URL,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    oauth=oauth
                )
                access_token, access_token_secret = \
                    dict(urllib.parse.parse_qsl(r.text)).values()

                if self._save:
                    config[self._NAME] = {
                        "flow": self._flow,
                        "access_token": access_token,
                        "access_token_secret": access_token_secret,
                        "consumer_key": self._consumer_key,
                        "consumer_secret": self._consumer_secret
                    }
                    with open(DIR_HOME / "minim.cfg", "w") as f:
                        config.write(f)
        
            self._oauth |= {
                "oauth_token": access_token,
                "oauth_signature": self._consumer_secret
                                   + f"&{access_token_secret}"
            }

        elif self._flow == "discogs":
            if access_token is None:
                if self._consumer_key is None or self._consumer_secret is None:
                    emsg = "Discogs API client credentials not provided."
                    raise ValueError(emsg)
                self.session.headers["Authorization"] = (
                    f"Discogs key={self._consumer_key}, "
                    f"secret={self._consumer_secret}"
                )
            else:
                self.session.headers["Authorization"] = \
                    f"Discogs token={access_token}"
                
        if (self._flow == "oauth" 
                or self._flow == "discogs" 
                   and "token" in self.session.headers["Authorization"]):
            identity = self.get_identity()
            self._username = identity["username"]

    def set_flow(
            self, flow: str, *, consumer_key: str = None,
            consumer_secret: str = None, browser: bool = False,
            web_framework: str = None, port: Union[int, str] = 8888,
            redirect_uri: str = None, save: bool = True) -> None:

        """
        Set the authorization flow.

        Parameters
        ----------
        flow : `str`
            Authorization flow. If :code:`None`, no user authentication
            will be performed and client credentials will not be 
            attached to requests, even if found or provided.

            .. container::

               **Valid values**:

               * :code:`None` for no user authentication.
               * :code:`"discogs"` for the Discogs authentication flow.
               * :code:`"oauth"` for the OAuth 1.0a flow.

        consumer_key : `str`, keyword-only, optional
        """

        if flow and flow not in self._FLOWS:
            emsg = (f"Invalid authorization flow ({flow=}). "
                    f"Valid values: {', '.join(self._FLOWS)}.")
            raise ValueError(emsg)
        self._flow = flow
        self._save = save

        self._consumer_key = \
            consumer_key or os.environ.get("DISCOGS_CONSUMER_KEY")
        self._consumer_secret = \
            consumer_secret or os.environ.get("DISCOGS_CONSUMER_SECRET")

        if flow == "oauth":
            self._browser = browser
            if redirect_uri:
                self._redirect_uri = redirect_uri
                if "localhost" in redirect_uri:
                    self._port = re.search("localhost:(\d+)", 
                                            redirect_uri).group(1)
                elif web_framework:
                    wmsg = ("The redirect URI is not on localhost, "
                            "so automatic authorization code "
                            "retrieval is not available.")
                    logging.warning(wmsg)
                    web_framework = None
            elif port:
                self._port = port
                self._redirect_uri = f"http://localhost:{port}/callback"
            else:
                self._port = self._redirect_uri = None

            self._web_framework = (
                web_framework 
                if web_framework is None 
                   or web_framework == "http.server"
                   or globals()[f"FOUND_{web_framework.upper()}"]
                else None
            )
            if self._web_framework is None and web_framework:
                wmsg = (f"The {web_framework.capitalize()} web "
                        "framework was not found, so automatic "
                        "authorization code retrieval is not "
                        "available.")
                warnings.warn(wmsg)

    ### DATABASE ##############################################################
                
    ### MARKETPLACE ###########################################################
                
    ### INVENTORY EXPORT ######################################################
                
    ### INVENTORY UPLOAD ######################################################
                
    ### USER IDENTITY #########################################################

    def get_identity(self) -> dict[str, Any]:

        """
        `User Identity > Identity <https://www.discogs.com/developers
        /#page:user-identity,header:user-identity-identity-get>`_:
        Retrieve basic information about the authenticated user.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        You can use this resource to find out who you're authenticated 
        as, and it also doubles as a good sanity check to ensure that 
        you're using OAuth correctly.

        For more detailed information, make another request for the 
        user's profile using :meth:`get_profile`.

        Returns
        -------
        identity : `dict`
            Basic information about the authenticated user.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "id": <int><int>,
                    "username": <str>,
                    "resource_url": <str>,
                    "consumer_name": <str>
                  }
        """

        self._check_authentication("get_identity")

        return self._get_json(f"{self.API_URL}/oauth/identity")
    
    def get_profile(self, username: str = None) -> dict[str, Any]:

        """
        `User Identity > Profile > Get Profile 
        <https://www.discogs.com/developers
        /#page:user-identity,header:user-identity-profile-get>`_:
        Retrieve a user by username.

        If authenticated as the requested user, the :code:`"email"` key
        will be visible, and the :code:`"num_lists"` count will include
        the user's private lists.

        If authenticated as the requested user or the user's 
        collection/wantlist is public, the 
        :code:`"num_collection"`/:code:`"num_wantlist"` keys will be
        visible.

        Parameters
        ----------
        username : `str`, optional
            The username of whose profile you are requesting. If not
            specified, the username of the authenticated user is used.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        profile : `dict`
            Detailed information about the user.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "profile": <str>,
                    "wantlist_url": <str>,
                    "rank": <int>,
                    "num_pending": <int>,
                    "id": <int><int>,
                    "num_for_sale": <int>,
                    "home_page": <str>,
                    "location": <str>,
                    "collection_folders_url": <str>,
                    "username": <str>,
                    "collection_fields_url": <str>,
                    "releases_contributed": <int>,
                    "registered": <str>,
                    "rating_avg": <float>,
                    "num_collection": <int>,
                    "releases_rated": <int>,
                    "num_lists": <int>,
                    "name": <str>,
                    "num_wantlist": <int>,
                    "inventory_url": <str>,
                    "avatar_url": <str>,
                    "banner_url": <str>,
                    "uri": <str>,
                    "resource_url": <str>,
                    "buyer_rating": <float>,
                    "buyer_rating_stars": <int>,
                    "buyer_num_ratings": <int>,
                    "seller_rating": <float>,
                    "seller_rating_stars": <int>,
                    "seller_num_ratings": <int>,
                    "curr_abbr": <str>,
                  }
        """

        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise ValueError("No username provided.")
        return self._get_json(f"{self.API_URL}/users/{username}")
    
    def edit_profile(
            self, *, name: str = None, home_page: str = None,
            location: str = None, profile: str = None,
            curr_abbr: str = None) -> dict[str, Any]:
        
        """
        `User Identity > Profile > Edit Profile 
        <https://www.discogs.com/developers
        /#page:user-identity,header:user-identity-profile-post>`_:
        Edit a user's profile data.

        .. admonition:: User authentication
            :class: warning
  
            Requires user authentication with a personal access token or
            via the OAuth 1.0a flow.

        Parameters
        ----------
        name : `str`, keyword-only, optional
            The real name of the user.

            **Example**: :code:`"Nicolas Cage"`.

        home_page : `str`, keyword-only, optional
            The user's website.

            **Example**: :code:`"www.discogs.com"`.

        location : `str`, keyword-only, optional
            The geographical location of the user.

            **Example**: :code:`"Portland"`.

        profile : `str`, keyword-only, optional
            Biological information about the user.

            **Example**: :code:`"I am a Discogs user!"`.

        curr_abbr : `str`, keyword-only, optional
            Currency abbreviation for marketplace data.

            **Valid values**: :code:`"USD"`, :code:`"GBP"`, 
            :code:`"EUR"`, :code:`"CAD"`, :code:`"AUD"`, :code:`"JPY"`, 
            :code:`"CHF"`, :code:`"MXN"`, :code:`"BRL"`, :code:`"NZD"`,
            :code:`"SEK"`, and :code:`"ZAR"`.

        Returns
        -------
        profile : `dict`
            Updated profile.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "id": <int><int>,
                    "username": <str>,
                    "name": <str>,
                    "email": <str>,
                    "resource_url": <str>,
                    "inventory_url": <str>,
                    "collection_folders_url": <str>,
                    "collection_fields_url": <str>,
                    "wantlist_url": <str>,
                    "uri": <str>,
                    "profile": <str>,
                    "home_page": <str>,
                    "location": <str>,
                    "registered": <str>,
                    "num_lists": <int>,
                    "num_for_sale": <int>,
                    "num_collection": <int>,
                    "num_wantlist": <int>,
                    "num_pending": <int>,
                    "releases_contributed": <int>,
                    "rank": <int>,
                    "releases_rated": <int>,
                    "rating_avg": <float>
                  }
        """
        
        self._check_authentication("edit_profile")

        if curr_abbr and curr_abbr not in (
                CURRENCIES := {
                    "USD", "GBP", "EUR", "CAD", "AUD", "JPY",
                    "CHF", "MXN", "BRL", "NZD", "SEK", "ZAR"
                }
            ):
            emsg = (f"Invalid currency abbreviation ({curr_abbr=}). "
                    f"Valid values: {', '.join(CURRENCIES)}.")
            raise ValueError(emsg)

        return self._request(
            "post", 
            f"{self.API_URL}/users/{self._username}",
            json={
                "name": name,
                "home_page": home_page,
                "location": location,
                "profile": profile,
                "curr_abbr": curr_abbr
            }
        ).json()

    def get_user_submissions(
            self, username: str = None, *, page: int = None, 
            per_page: int = None) -> dict[str, Any]:

        """
        `User Identity > User Submissions <https://www.discogs.com
        /developers/#page:user-identity,header
        :user-identity-user-submissions-get>`_: Retrieve a user's
        submissions (edits made to releases, labels, and artists) by
        username.

        Parameters
        ----------
        username : `str`, optional
            The username of the submissions you are trying to fetch. If 
            not specified, the username of the authenticated user is 
            used.

            **Example**: :code:`"shooezgirl"`.

        page : `int`, keyword-only, optional
            Page of results to fetch.

        per_page : `int`, keyword-only, optional
            Number of results per page.

        Returns
        -------
        submissions : `dict`
            Submissions made by the user.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "pagination": {
                      "items": <int>,
                      "page": <int>,
                      "pages": <int>,
                      "per_page": <int>,
                      "urls": {}
                    },
                    "submissions": {
                      "artists": [
                        {
                          "data_quality": <str>,
                          "id": <int>,
                          "name": <str>,
                          "namevariations": [<str>],
                          "releases_url": <str>,
                          "resource_url": <str>,
                          "uri": <str>
                        }
                      ],
                      "labels": [],
                      "releases": [
                        {
                          "artists": [
                            {
                              "anv": <str>,
                              "id": <int>,
                              "join": <str>,
                              "name": <str>,
                              "resource_url": <str>,
                              "role": <str>,
                              "tracks": <str>
                            }
                          ],
                          "community": {
                            "contributors": [
                              {
                                "resource_url": <str>,
                                "username": <str>
                              },
                              {
                                "resource_url": <str>,
                                "username": <str>
                              }
                            ],
                            "data_quality": <str>,
                            "have": <int>,
                            "rating": {
                              "average": <int>,
                              "count": <int>
                            },
                            "status": <str>,
                            "submitter": {
                              "resource_url": <str>,
                              "username": <str>
                            },
                            "want": <int>
                          },
                          "companies": [],
                          "country": <str>,
                          "data_quality": <str>,
                          "date_added": <str>,
                          "date_changed": <str>,
                          "estimated_weight": <int>,
                          "format_quantity": <int>,
                          "formats": [
                            {
                              "descriptions": [<str>],
                              "name": <str>,
                              "qty": <str>
                            }
                          ],
                          "genres": [<str>],
                          "id": <int>,
                          "images": [
                            {
                              "height": <int>,
                              "resource_url": <str>,
                              "type": <str>,
                              "uri": <str>,
                              "uri150": <str>,
                              "width": <int>
                            },
                            {
                              "height": <int>,
                              "resource_url": <str>,
                              "type": <str>,
                              "uri": <str>,
                              "uri150": <str>,
                              "width": <int>
                            }
                          ],
                          "labels": [
                            {
                              "catno": <str>,
                              "entity_type": <str>,
                              "id": <int>,
                              "name": <str>,
                              "resource_url": <str>
                            }
                          ],
                          "master_id": <int>,
                          "master_url": <str>,
                          "notes": <str>,
                          "released": <str>,
                          "released_formatted": <str>,
                          "resource_url": <str>,
                          "series": [],
                          "status": <str>,
                          "styles": [<str>],
                          "thumb": <str>,
                          "title": <str>,
                          "uri": <str>,
                          "videos": [
                            {
                              "description": <str>,
                              "duration": <int>,
                              "embed": <bool>,
                              "title": <str>,
                              "uri": <str>
                            },
                            {
                              "description": <str>,
                              "duration": <int>,
                              "embed": <bool>,
                              "title": <str>,
                              "uri": <str>
                            },
                            {
                              "description": <str>,
                              "duration": <int>,
                              "embed": <bool>,
                              "title": <str>,
                              "uri": <str>
                            }
                          ],
                          "year": <int>
                        }
                      ]
                    }
                  }
        """

        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise ValueError("No username provided.")

        return self._get_json(
            f"{self.API_URL}/users/{username}/submissions",
            params={"page": page, "per_page": per_page}
        )
    
    def get_user_contributions(
            self, username: str = None, *, page: int = None, 
            per_page: int = None, sort: str = None, sort_order: str = None
        ) -> dict[str, Any]:
        
        """
        `User Identity > User Contributions <https://www.discogs.com
        /developers/#page:user-identity,header
        :user-identity-user-contributions-get>`_: Retrieve a user's 
        contributions (releases, labels, artists) by username.

        Parameters
        ----------
        username : `str`, optional
            The username of the contributions you are trying to fetch.
            If not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"shooezgirl"`.

        page : `int`, keyword-only, optional
            Page of results to fetch.

        per_page : `int`, keyword-only, optional
            Number of results per page.

        sort : `str`, keyword-only, optional
            Sort items by this field.

            **Valid values**: :code:`"label"`, :code:`"artist"`,
            :code:`"title"`, :code:`"catno"`, :code:`"format"`,
            :code:`"rating"`, :code:`"year"`, and :code:`"added"`.

        sort_order : `str`, keyword-only, optional
            Sort items in a particular order.

            **Valid values**: :code:`"asc"` and :code:`"desc"`.
            
        Returns
        -------
        contributions : `dict`
            Contributions made by the user.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "pagination": {
                      "items": <int>,
                      "page": <int>,
                      "pages": <int>,
                      "per_page": <int>,
                      "urls": {}
                    },
                    "contributions": [
                      {
                        "artists": [
                          {
                            "anv": <str>,
                            "id": <int>,
                            "join": <str>,
                            "name": <str>,
                            "resource_url": <str>,
                            "role": <str>,
                            "tracks": <str>
                          }
                        ],
                        "community": {
                          "contributors": [
                            {
                              "resource_url": <str>,
                              "username": <str>
                            },
                            {
                              "resource_url": <str>,
                              "username": <str>
                            }
                          ],
                          "data_quality": <str>,
                          "have": <int>,
                          "rating": {
                            "average": <int>,
                            "count": <int>
                          },
                          "status": <str>,
                          "submitter": {
                            "resource_url": <str>,
                            "username": <str>
                          },
                          "want": <int>
                        },
                        "companies": [],
                        "country": <str>,
                        "data_quality": <str>,
                        "date_added": <str>,
                        "date_changed": <str>,
                        "estimated_weight": <int>,
                        "format_quantity": <int>,
                        "formats": [
                          {
                            "descriptions": [<str>],
                            "name": <str>,
                            "qty": <str>
                          }
                        ],
                        "genres": [<str>],
                        "id": <int>,
                        "images": [
                          {
                            "height": <int>,
                            "resource_url": <str>,
                            "type": <str>,
                            "uri": <str>,
                            "uri150": <str>,
                            "width": <int>
                          }
                        ],
                        "labels": [
                          {
                            "catno": <str>,
                            "entity_type": <str>,
                            "id": <int>,
                            "name": <str>,
                            "resource_url": <str>
                          }
                        ],
                        "master_id": <int>,
                        "master_url": <str>,
                        "notes": <str>,
                        "released": <str>,
                        "released_formatted": <str>,
                        "resource_url": <str>,
                        "series": [],
                        "status": <str>,
                        "styles": [<str>],
                        "thumb": <str>,
                        "title": <str>,
                        "uri": <str>,
                        "videos": [
                          {
                            "description": <str>,
                            "duration": <int>,
                            "embed": <bool>,
                            "title": <str>,
                            "uri": <str>
                          }
                        ],
                        "year": <int>
                      }
                    ]
                  }
        """

        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise ValueError("No username provided.")

        return self._get_json(
            f"{self.API_URL}/users/{username}/contributions",
            params={"page": page, "per_page": per_page, "sort": sort,
                    "sort_order": sort_order}
        )
    
    ### USER COLLECTION #######################################################

    ### USER WANTLIST #########################################################

    ### USER LISTS ############################################################