"""
Discogs
=======
.. moduleauthor:: Benjamin Ye <GitHub: bbye98>

This module contains a complete implementation of the Discogs API.
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

from . import (
    FOUND_FLASK,
    FOUND_PLAYWRIGHT,
    VERSION,
    REPOSITORY_URL,
    DIR_HOME,
    DIR_TEMP,
    _config,
)

if FOUND_FLASK:
    from flask import Flask, request
if FOUND_PLAYWRIGHT:
    from playwright.sync_api import sync_playwright

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
            urllib.parse.parse_qsl(urllib.parse.urlparse(f"{self.path}").query)
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        status = "denied" if "denied" in self.server.response else "granted"
        self.wfile.write(f"Access {status}. You may close this page now.".encode())


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
        self,
        *,
        consumer_key: str = None,
        consumer_secret: str = None,
        flow: str = None,
        browser: bool = False,
        web_framework: str = None,
        port: Union[int, str] = 8888,
        redirect_uri: str = None,
        access_token: str = None,
        access_token_secret: str = None,
        overwrite: bool = False,
        save: bool = True,
    ) -> None:
        """
        Create a Discogs API client.
        """

        self.session = requests.Session()
        self.session.headers["User-Agent"] = f"Minim/{VERSION} +{REPOSITORY_URL}"

        if access_token is None and _config.has_section(self._NAME) and not overwrite:
            flow = _config.get(self._NAME, "flow")
            access_token = _config.get(self._NAME, "access_token")
            access_token_secret = _config.get(self._NAME, "access_token_secret")
            consumer_key = _config.get(self._NAME, "consumer_key")
            consumer_secret = _config.get(self._NAME, "consumer_secret")
        elif flow is None and access_token is not None:
            flow = "discogs" if access_token_secret is None else "oauth"

        self.set_flow(
            flow,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            browser=browser,
            web_framework=web_framework,
            port=port,
            redirect_uri=redirect_uri,
            save=save,
        )
        self.set_access_token(access_token, access_token_secret)

    def _check_authentication(self, endpoint: str, token: bool = True) -> None:
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
            emsg = f"{self._NAME}.{endpoint}() requires user " "authentication."
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
        self, method: str, url: str, *, oauth: dict[str, Any] = None, **kwargs
    ) -> requests.Response:
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

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        if self._flow == "oauth" and "Authorization" not in kwargs["headers"]:
            if oauth is None:
                oauth = {}
            oauth = (
                self._oauth
                | {
                    "oauth_nonce": secrets.token_hex(32),
                    "oauth_timestamp": f"{time.time():.0f}",
                }
                | oauth
            )
            kwargs["headers"]["Authorization"] = "OAuth " + ", ".join(
                f'{k}="{v}"' for k, v in oauth.items()
            )

        r = self.session.request(method, url, **kwargs)
        if r.status_code not in range(200, 299):
            j = r.json()
            emsg = f"{r.status_code}: {j['message']}"
            if "detail" in j["message"]:
                emsg += f"\n{json.dumps(j['detail'], indent=2)}"
            raise RuntimeError(emsg)
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
                "oauth_signature_method": "PLAINTEXT",
            }

            if access_token is None:
                oauth = {"oauth_signature": f"{self._consumer_secret}&"}
                if self._redirect_uri is not None:
                    oauth["oauth_callback"] = self._redirect_uri
                r = self._request(
                    "get",
                    self.REQUEST_TOKEN_URL,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    oauth=oauth,
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
                        page.wait_for_url(f"{self._redirect_uri}*", wait_until="commit")
                        context.close()
                        browser.close()

                    with open(har_file, "r") as f:
                        oauth |= dict(
                            urllib.parse.parse_qsl(
                                urllib.parse.urlparse(
                                    re.search(
                                        rf'{self._redirect_uri}\?(.*?)"', f.read()
                                    ).group(0)
                                ).query
                            )
                        )
                    har_file.unlink()

                else:
                    if self._browser:
                        webbrowser.open(auth_url)
                    else:
                        print(
                            "To grant Minim access to Discogs data "
                            "and features, open the following link "
                            f"in your web browser:\n\n{auth_url}\n"
                        )

                    if self._web_framework == "http.server":
                        httpd = HTTPServer(("", self._port), _DiscogsRedirectHandler)
                        httpd.handle_request()
                        oauth |= httpd.response

                    elif self._web_framework == "flask":
                        app = Flask(__name__)
                        json_file = DIR_TEMP / "minim_discogs.json"

                        @app.route("/callback", methods=["GET"])
                        def _callback() -> str:
                            if "error" in request.args:
                                return "Access denied. You may close " "this page now."
                            with open(json_file, "w") as f:
                                json.dump(request.args, f)
                            return "Access granted. You may close " "this page now."

                        server = Process(target=app.run, args=("0.0.0.0", self._port))
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

                oauth["oauth_signature"] = (
                    f"{self._consumer_secret}" f"&{oauth['oauth_token_secret']}"
                )
                r = self._request(
                    "post",
                    self.ACCESS_TOKEN_URL,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    oauth=oauth,
                )
                access_token, access_token_secret = dict(
                    urllib.parse.parse_qsl(r.text)
                ).values()

                if self._save:
                    _config[self._NAME] = {
                        "flow": self._flow,
                        "access_token": access_token,
                        "access_token_secret": access_token_secret,
                        "consumer_key": self._consumer_key,
                        "consumer_secret": self._consumer_secret,
                    }
                    with open(DIR_HOME / "minim.cfg", "w") as f:
                        _config.write(f)

            self._oauth |= {
                "oauth_token": access_token,
                "oauth_signature": self._consumer_secret + f"&{access_token_secret}",
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
                self.session.headers["Authorization"] = f"Discogs token={access_token}"

        if (
            self._flow == "oauth"
            or self._flow == "discogs"
            and "token" in self.session.headers["Authorization"]
        ):
            identity = self.get_identity()
            self._username = identity["username"]

    def set_flow(
        self,
        flow: str,
        *,
        consumer_key: str = None,
        consumer_secret: str = None,
        browser: bool = False,
        web_framework: str = None,
        port: Union[int, str] = 8888,
        redirect_uri: str = None,
        save: bool = True,
    ) -> None:
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
            Consumer key. Required for the OAuth 1.0a flow, and can be
            used in the Discogs authorization flow alongside a consumer
            secret. If it is not stored as :code:`DISCOGS_CONSUMER_KEY`
            in the operating system's environment variables or found in
            the Minim configuration file, it can be provided here.

        consumer_secret : `str`, keyword-only, optional
            Consumer secret. Required for the OAuth 1.0a flow, and can
            be used in the Discogs authorization flow alongside a
            consumer key. If it is not stored as
            :code:`DISCOGS_CONSUMER_SECRET` in the operating system's
            environment variables or found in the Minim configuration
            file, it can be provided here.

        browser : `bool`, keyword-only, default: :code:`False`
            Determines whether a web browser is automatically opened for
            the OAuth 1.0a flow. If :code:`False`, users will have to
            manually open the authorization URL and provide the full
            callback URI via the terminal.

        web_framework : `str`, keyword-only, optional
            Determines which web framework to use for the OAuth 1.0a
            flow.

            .. container::

               **Valid values**:

               * :code:`"http.server"` for the built-in implementation
                 of HTTP servers.
               * :code:`"flask"` for the Flask framework.
               * :code:`"playwright"` for the Playwright framework by
                 Microsoft.

        port : `int` or `str`, keyword-only, default: :code:`8888`
            Port on :code:`localhost` to use for the OAuth 1.0a flow
            with the :code:`http.server` and Flask frameworks. Only used
            if `redirect_uri` is not specified.

        redirect_uri : `str`, keyword-only, optional
            Redirect URI for the OAuth 1.0a flow. If not on
            :code:`localhost`, the automatic request access token
            retrieval functionality is not available.

        save : `bool`, keyword-only, default: :code:`True`
            Determines whether newly obtained access tokens and their
            associated properties are stored to the Minim configuration
            file.
        """

        if flow and flow not in self._FLOWS:
            emsg = (
                f"Invalid authorization flow ({flow=}). "
                f"Valid values: {', '.join(self._FLOWS)}."
            )
            raise ValueError(emsg)
        self._flow = flow
        self._save = save

        self._consumer_key = consumer_key or os.environ.get("DISCOGS_CONSUMER_KEY")
        self._consumer_secret = consumer_secret or os.environ.get(
            "DISCOGS_CONSUMER_SECRET"
        )

        if flow == "oauth":
            self._browser = browser
            if redirect_uri:
                self._redirect_uri = redirect_uri
                if "localhost" in redirect_uri:
                    self._port = re.search(r"localhost:(\d+)", redirect_uri).group(1)
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
                if web_framework is None
                or web_framework == "http.server"
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

    ### DATABASE ##############################################################

    def get_release(
        self, release_id: Union[int, str], *, curr_abbr: str = None
    ) -> dict[str, Any]:
        """
        `Database > Release <https://www.discogs.com
        /developers/#page:database,header:database-release-get>`_:
        Get a release (physical or digital object released by one or
        more artists).

        Parameters
        ----------
        release_id : `int` or `str`
            The release ID.

            **Example**: :code:`249504`.

        curr_abbr : `str`, keyword-only, optional
            Currency abbreviation for marketplace data. Defaults to the
            authenticated user's currency.

            **Valid values**: :code:`"USD"`, :code:`"GBP"`,
            :code:`"EUR"`, :code:`"CAD"`, :code:`"AUD"`, :code:`"JPY"`,
            :code:`"CHF"`, :code:`"MXN"`, :code:`"BRL"`, :code:`"NZD"`,
            :code:`"SEK"`, and :code:`"ZAR"`.

        Returns
        -------
        release : `dict`
            Discogs database information for a single release.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "title": <str>,
                    "id": <int>,
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
                    "data_quality": <str>,
                    "thumb": <str>,
                    "community": {
                      "contributors": [
                        {
                          "resource_url": <str>,
                          "username": <str>
                        }
                      ],
                      "data_quality": <str>,
                      "have": <int>,
                      "rating": {
                        "average": <float>,
                        "count": <int>
                      },
                      "status": <str>,
                      "submitter": {
                        "resource_url": <str>,
                        "username": <str>
                      },
                      "want": <int>
                    },
                    "companies": [
                      {
                        "catno": <str>,
                        "entity_type": <str>,
                        "entity_type_name": <str>,
                        "id": <int>,
                        "name": <str>,
                        "resource_url": <str>
                      }
                    ],
                    "country": <str>,
                    "date_added": <str>,
                    "date_changed": <str>,
                    "estimated_weight": <int>,
                    "extraartists": [
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
                    "format_quantity": <int>,
                    "formats": [
                      {
                        "descriptions": [<str>],
                        "name": <str>,
                        "qty": <str>
                      }
                    ],
                    "genres": [<str>],
                    "identifiers": [
                      {
                        "type": <str>,
                        "value": <str>
                      },
                    ],
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
                    "lowest_price": <float>,
                    "master_id": <int>,
                    "master_url": <str>,
                    "notes": <str>,
                    "num_for_sale": <int>,
                    "released": <str>,
                    "released_formatted": <str>,
                    "resource_url": <str>,
                    "series": [],
                    "status": <str>,
                    "styles": [<str>],
                    "tracklist": [
                      {
                        "duration": <str>,
                        "position": <str>,
                        "title": <str>,
                        "type_": <str>
                      }
                    ],
                    "uri": <str>,
                    "videos": [
                      {
                        "description": <str>,
                        "duration": <int>,
                        "embed": <bool>,
                        "title": <str>,
                        "uri": <str>
                      },
                    ],
                    "year": <int>
                  }
        """

        if curr_abbr and curr_abbr not in (
            CURRENCIES := {
                "USD",
                "GBP",
                "EUR",
                "CAD",
                "AUD",
                "JPY",
                "CHF",
                "MXN",
                "BRL",
                "NZD",
                "SEK",
                "ZAR",
            }
        ):
            emsg = (
                f"Invalid currency abbreviation ({curr_abbr=}). "
                f"Valid values: {', '.join(CURRENCIES)}."
            )
            raise ValueError(emsg)

        return self._get_json(
            f"{self.API_URL}/releases/{release_id}", params={"curr_abbr": curr_abbr}
        )

    def get_user_release_rating(
        self, release_id: Union[int, str], username: str = None
    ) -> dict[str, Any]:
        """
        `Database > Release Rating By User > Get Release Rating By User
        <https://www.discogs.com/developers
        /#page:database,header:database-release-get>`_: Retrieves the
        release's rating for a given user.

        Parameters
        ----------
        release_id : `int` or `str`
            The release ID.

            **Example**: :code:`249504`.

        username : `str`, optional
            The username of the user whose rating you are requesting. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"memory"`.

        Returns
        -------
        rating : `dict`
            Rating for the release by the given user.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "username": <str>,
                    "release_id": <int>,
                    "rating": <int>
                  }
        """

        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise ValueError("No username provided.")

        return self._get_json(f"{self.API_URL}/releases/{release_id}/rating/{username}")

    def update_user_release_rating(
        self, release_id: Union[int, str], rating: int, username: str = None
    ) -> dict[str, Any]:
        """
        `Database > Release Rating By User > Update Release Rating By
        User <https://www.discogs.com/developers
        /#page:database,header:database-release-rating-by-user-put>`_:
        Updates the release's rating for a given user.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        release_id : `int` or `str`
            The release ID.

            **Example**: :code:`249504`.

        rating : `int`
            The new rating for a release between :math:`1` and :math:`5`.

        username : `str`, optional
            The username of the user whose rating you are requesting. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"memory"`.

        Returns
        -------
        rating : `dict`
            Updated rating for the release by the given user.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "username": <str>,
                    "release_id": <int>,
                    "rating": <int>
                  }
        """

        self._check_authentication("update_user_release_rating")

        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise ValueError("No username provided.")

        return self._request(
            "put",
            f"{self.API_URL}/releases/{release_id}/rating/{username}",
            json={"rating": rating},
        )

    def delete_user_release_rating(
        self, release_id: Union[int, str], username: str = None
    ) -> None:
        """
        `Database > Release Rating By User > Delete Release Rating By
        User <https://www.discogs.com/developers
        /#page:database,header:database-release-rating-by-user-delete>`_:
        Deletes the release's rating for a given user.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        release_id : `int` or `str`
            The release ID.

            **Example**: :code:`249504`.

        username : `str`, optional
            The username of the user whose rating you are requesting. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"memory"`.
        """

        self._check_authentication("delete_user_release_rating")

        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise ValueError("No username provided.")

        return self._request(
            "delete", f"{self.API_URL}/releases/{release_id}/rating/{username}"
        )

    def get_community_release_rating(
        self, release_id: Union[int, str]
    ) -> dict[str, Any]:
        """
        `Database > Community Release Rating <https://www.discogs.com
        /developers/#page:database,header
        :database-community-release-rating-get>`_: Retrieves the
        community release rating average and count.

        Parameters
        ----------
        release_id : `int` or `str`
            The release ID.

            **Example**: :code:`249504`.

        Returns
        -------
        rating : `dict`
            Community release rating average and count.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "rating": {
                        "count": <int>,
                        "average": <float>
                    },
                    "release_id": <int>
                  }
        """

        return self._get_json(f"{self.API_URL}/releases/{release_id}/rating")

    def get_release_stats(self, release_id: Union[int, str]) -> dict[str, Any]:
        """
        `Database > Release Stats <https://www.discogs.com/developers
        /#page:database,header:database-release-stats-get>`_: Retrieves
        the release's "have" and "want" counts.

        .. attention::

           This endpoint does not appear to be working correctly.
           Currently, the response will be of the form

           .. code::

              {
                "is_offense": <bool>
              }

        Parameters
        ----------
        release_id : `int` or `str`
            The release ID.

            **Example**: :code:`249504`.

        Returns
        -------
        stats : `dict`
            Release "have" and "want" counts.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "num_have": <int>,
                    "num_want": <int>
                  }
        """

        return self._get_json(f"{self.API_URL}/releases/{release_id}/stats")

    def get_master_release(self, master_id: Union[int, str]) -> dict[str, Any]:
        """
        `Database > Master Release <https://www.discogs.com/developers
        /#page:database,header:database-master-release-get>`_: Get a
        master release.

        Parameters
        ----------
        master_id : `int` or `str`
            The master release ID.

            **Example**: :code:`1000`.

        Returns
        -------
        master_release : `dict`
            Discogs database information for a single master release.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "styles": [<str>],
                    "genres": [<str>],
                    "videos": [
                      {
                        "duration": <int>,
                        "description": <str>,
                        "embed": <bool>,
                        "uri": <str>,
                        "title": <str>
                      }
                    ],
                    "title": <str>,
                    "main_release": <int>,
                    "main_release_url": <str>,
                    "uri": <str>,
                    "artists": [
                      {
                        "join": <str>,
                        "name": <str>,
                        "anv": <str>,
                        "tracks": <str>,
                        "role": <str>,
                        "resource_url": <str>,
                        "id": <int>
                      }
                    ],
                    "versions_url": <str>,
                    "year": <int>,
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
                    "resource_url": <str>,
                    "tracklist": [
                      {
                        "duration": <str>,
                        "position": <str>,
                        "type_": <str>,
                        "extraartists": [
                          {
                            "join": <str>,
                            "name": <str>,
                            "anv": <str>,
                            "tracks": <str>,
                            "role": <str>,
                            "resource_url": <str>,
                            "id": <int>
                          }
                        ],
                        "title": <str>
                      }
                    ],
                    "id": <int>,
                    "num_for_sale": <int>,
                    "lowest_price": <float>,
                    "data_quality": <str>
                  }
        """

        return self._get_json(f"{self.API_URL}/masters/{master_id}")

    def get_master_release_versions(
        self,
        master_id: Union[int, str],
        *,
        country: str = None,
        format: str = None,
        label: str = None,
        released: str = None,
        page: Union[int, str] = None,
        per_page: Union[int, str] = None,
        sort: str = None,
        sort_order: str = None,
    ) -> dict[str, Any]:
        """
        `Database > Master Release Versions <https://www.discogs.com
        /developers/#page:database,header
        :database-master-release-versions-get>`_: Retrieves a list of
        all releases that are versions of this master.

        Parameters
        ----------
        master_id : `int` or `str`
            The master release ID.

            **Example**: :code:`1000`.

        country : `str`, keyword-only, optional
            The country to filter for.

            **Example**: :code:`"Belgium"`.

        format : `str`, keyword-only, optional
            The format to filter for.

            **Example**: :code:`"Vinyl"`.

        label : `str`, keyword-only, optional
            The label to filter for.

            **Example**: :code:`"Scorpio Music"`.

        released : `str`, keyword-only, optional
            The release year to filter for.

            **Example**: :code:`"1992"`.

        page : `int` or `str`, keyword-only, optional
            The page you want to request.

            **Example**: :code:`3`.

        per_page : `int` or `str`, keyword-only, optional
            The number of items per page.

            **Example**: :code:`25`.

        sort : `str`, keyword-only, optional
            Sort items by this field.

            **Valid values**: :code:`"released"`, :code:`"title"`,
            :code:`"format"`, :code:`"label"`, :code:`"catno"`,
            and :code:`"country"`.

        sort_order : `str`, keyword-only, optional
            Sort items in a particular order.

            **Valid values**: :code:`"asc"` and :code:`"desc"`.

        Returns
        -------
        versions : `dict`
            Discogs database information for all releases that are
            versions of the specified master.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "pagination": {
                      "items": <int>,
                      "page": <int>,
                      "pages": <int>,
                      "per_page": <int>,
                      "urls": {
                        "last": <str>,
                        "next": <str>
                      }
                    },
                    "versions": [
                      {
                        "status": <str>,
                        "stats": {
                          "user": {
                            "in_collection": <int>,
                            "in_wantlist": <int>
                          },
                          "community": {
                            "in_collection": <int>,
                            "in_wantlist": <int>
                          }
                        },
                        "thumb": <str>,
                        "format": <str>,
                        "country": <str>,
                        "title": <str>,
                        "label": <str>,
                        "released": <str>,
                        "major_formats": [<str>],
                        "catno": <str>,
                        "resource_url": <str>,
                        "id": <int>
                      }
                    ]
                  }
        """

        return self._get_json(
            f"{self.API_URL}/masters/{master_id}/versions",
            params={
                "country": country,
                "format": format,
                "label": label,
                "released": released,
                "page": page,
                "per_page": per_page,
                "sort": sort,
                "sort_order": sort_order,
            },
        )

    def get_artist(self, artist_id: Union[int, str]) -> dict[str, Any]:
        """
        `Database > Artist <https://www.discogs.com/developers
        /#page:database,header:database-artist-get>`_: Get an artist.

        Parameters
        ----------
        artist_id : `int` or `str`
            The artist ID.

            **Example**: :code:`108713`.

        Returns
        -------
        artist : `dict`
            Discogs database information for a single artist.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "namevariations": [<str>],
                    "profile": <str>,
                    "releases_url": <str>,
                    "resource_url": <str>,
                    "uri": <str>,
                    "urls": [<str>],
                    "data_quality": <str>,
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
                    "members": [
                      {
                        "active": <bool>,
                        "id": <int>,
                        "name": <str>,
                        "resource_url": <str>
                      }
                    ]
                  }
        """

        return self._get_json(f"{self.API_URL}/artists/{artist_id}")

    def get_artist_releases(
        self,
        artist_id: Union[int, str],
        *,
        page: Union[int, str] = None,
        per_page: Union[int, str] = None,
        sort: str = None,
        sort_order: str = None,
    ) -> dict[str, Any]:
        """
        `Database > Artist Releases <https://www.discogs.com/developers
        /#page:database,header:database-artist-releases-get>`_: Get an
        artist's releases and masters.

        Parameters
        ----------
        artist_id : `int` or `str`
            The artist ID.

            **Example**: :code:`108713`.

        page : `int` or `str`, keyword-only, optional
            Page of results to fetch.

        per_page : `int` or `str`, keyword-only, optional
            Number of results per page.

        sort : `str`, keyword-only, optional
            Sort results by this field.

            **Valid values**: :code:`"year"`, :code:`"title"`, and
            :code:`"format"`.

        sort_order : `str`, keyword-only, optional
            Sort results in a particular order.

            **Valid values**: :code:`"asc"` and :code:`"desc"`.

        Returns
        -------
        releases : `dict`
            Discogs database information for all releases by the
            specified artist.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "pagination": {
                      "items": <int>,
                      "page": <int>,
                      "pages": <int>,
                      "per_page": <int>,
                      "urls": {
                        "last": <str>,
                        "next": <str>
                      }
                    },
                    "releases": [
                      {
                        "artist": <str>,
                        "id": <int>,
                        "main_release": <int>,
                        "resource_url": <str>,
                        "role": <str>,
                        "thumb": <str>,
                        "title": <str>,
                        "type": <str>,
                        "year": <int>
                      }
                    ]
                  }
        """

        return self._get_json(
            f"{self.API_URL}/artists/{artist_id}/releases",
            params={
                "page": page,
                "per_page": per_page,
                "sort": sort,
                "sort_order": sort_order,
            },
        )

    def get_label(self, label_id: Union[int, str]) -> dict[str, Any]:
        """
        `Database > Label <https://www.discogs.com/developers
        /#page:database,header:database-label-get>`_: Get a label,
        company, recording studio, locxation, or other entity involved
        with artists and releases.

        Parameters
        ----------
        label_id : `int` or `str`
            The label ID.

            **Example**: :code:`1`.

        Returns
        -------
        label : `dict`
            Discogs database information for a single label.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "profile": <str>,
                    "releases_url": <str>,
                    "name": <str>,
                    "contact_info": <str>,
                    "uri": <str>,
                    "sublabels": [
                      {
                        "resource_url": <str>,
                        "id": <int>,
                        "name": <str>
                      }
                    ],
                    "urls": [<str>],
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
                    "resource_url": <str>,
                    "id": <int>,
                    "data_quality": <str>
                  }
        """

        return self._get_json(f"{self.API_URL}/labels/{label_id}")

    def get_label_releases(
        self,
        label_id: Union[int, str],
        *,
        page: Union[int, str] = None,
        per_page: Union[int, str] = None,
    ) -> dict[str, Any]:
        """
        `Database > Label Releases <https://www.discogs.com/developers
        /#page:database,header:database-all-label-releases-get>`_: Get a
        list of releases associated with the label.

        Parameters
        ----------
        label_id : `int` or `str`
            The label ID.

            **Example**: :code:`1`.

        page : `int` or `str`, keyword-only, optional
            Page of results to fetch.

        per_page : `int` or `str`, keyword-only, optional
            Number of results per page.

        Returns
        -------
        releases : `dict`
            Discogs database information for all releases by the
            specified label.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "pagination": {
                      "items": <int>,
                      "page": <int>,
                      "pages": <int>,
                      "per_page": <int>,
                      "urls": {
                        "last": <str>,
                        "next": <str>
                      }
                    },
                    "releases": [
                      {
                        "artist": <str>,
                        "catno": <str>,
                        "format": <str>,
                        "id": <int>,
                        "resource_url": <str>,
                        "status": <str>,
                        "thumb": <str>,
                        "title": <str>,
                        "year": <int>
                      }
                    ]
                  }
        """

        return self._get_json(
            f"{self.API_URL}/labels/{label_id}/releases",
            params={"page": page, "per_page": per_page},
        )

    def search(
        self,
        query: str = None,
        *,
        type: str = None,
        title: str = None,
        release_title: str = None,
        credit: str = None,
        artist: str = None,
        anv: str = None,
        label: str = None,
        genre: str = None,
        style: str = None,
        country: str = None,
        year: str = None,
        format: str = None,
        catno: str = None,
        barcode: str = None,
        track: str = None,
        submitter: str = None,
        contributor: str = None,
    ) -> dict[str, Any]:
        """
        `Database > Search <https://www.discogs.com/developers
        /#page:database,header:database-search-get>`_: Issue a search
        query to the Discogs database.

        .. admonition:: Authentication
           :class: warning

           Requires authentication with consumer credentials, with a
           personal access token, or via the OAuth 1.0a flow.

        Parameters
        ----------
        query : `str`, optional
            The search query.

            **Example**: :code:`"Nirvana"`.

        type : `str`, keyword-only, optional
            The type of item to search for.

            **Valid values**: :code:`"release"`, :code:`"master"`,
            :code:`"artist"`, and :code:`"label"`.

        title : `str`, keyword-only, optional
            Search by combined :code:`"<artist name> - <release title>"`
            title field.

            **Example**: :code:`"Nirvana - Nevermind"`.

        release_title : `str`, keyword-only, optional
            Search release titles.

            **Example**: :code:`"Nevermind"`.

        credit : `str`, keyword-only, optional
            Search release credits.

            **Example**: :code:`"Kurt"`.

        artist : `str`, keyword-only, optional
            Search artist names.

            **Example**: :code:`"Nirvana"`.

        anv : `str`, keyword-only, optional
            Search artist name variations (ANV).

            **Example**: :code:`"Nirvana"`.

        label : `str`, keyword-only, optional
            Search labels.

            **Example**: :code:`"DGC"`.

        genre : `str`, keyword-only, optional
            Search genres.

            **Example**: :code:`"Rock"`.

        style : `str`, keyword-only, optional
            Search styles.

            **Example**: :code:`"Grunge"`.

        country : `str`, keyword-only, optional
            Search release country.

            **Example**: :code:`"Canada"`.

        year : `str`, keyword-only, optional
            Search release year.

            **Example**: :code:`"1991"`.

        format : `str`, keyword-only, optional
            Search formats.

            **Example**: :code:`"Album"`.

        catno : `str`, keyword-only, optional
            Search catalog number.

            **Example**: :code:`"DGCD-24425"`.

        barcode : `str`, keyword-only, optional
            Search barcode.

            **Example**: :code:`"720642442524"`.

        track : `str`, keyword-only, optional
            Search track.

            **Example**: :code:`"Smells Like Teen Spirit"`.

        submitter : `str`, keyword-only, optional
            Search submitter username.

            **Example**: :code:`"milKt"`.

        contributor : `str`, keyword-only, optional
            Search contributor username.

            **Example**: :code:`"jerome99"`.

        Returns
        -------
        results : `dict`
            Search results.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "pagination": {
                      "items": <int>,
                      "page": <int>,
                      "pages": <int>,
                      "per_page": <int>,
                      "urls": {
                        "last": <str>,
                        "next": <str>
                      }
                    },
                    "results": [
                      {
                        "style": [<str>],
                        "thumb": <str>,
                        "title": <str>,
                        "country": <str>,
                        "format": [<str>],
                        "uri": <str>,
                        "community": {
                          "want": <int>,
                          "have": <int>
                        },
                        "label": [<str>],
                        "catno": <str>,
                        "year": <str>,
                        "genre": [<str>],
                        "resource_url": <str>,
                        "type": <str>,
                        "id": <int>
                      }
                    ]
                  }
        """

        self._check_authentication("search", False)

        return self._get_json(
            f"{self.API_URL}/database/search",
            params={
                "q": query,
                "type": type,
                "title": title,
                "release_title": release_title,
                "credit": credit,
                "artist": artist,
                "anv": anv,
                "label": label,
                "genre": genre,
                "style": style,
                "country": country,
                "year": year,
                "format": format,
                "catno": catno,
                "barcode": barcode,
                "track": track,
                "submitter": submitter,
                "contributor": contributor,
            },
        )

    ### MARKETPLACE ###########################################################

    def get_inventory(
        self,
        username: str = None,
        *,
        status: str = None,
        page: Union[int, str] = None,
        per_page: Union[int, str] = None,
        sort: str = None,
        sort_order: str = None,
    ) -> dict[str, Any]:
        """
        `Marketplace > Inventory <https://www.discogs.com/developers
        /#page:marketplace,header:marketplace-inventory-get>`_:
        Get a seller's inventory.

        .. admonition:: User authentication
           :class: dropdown warning

           If you are authenticated as the inventory owner, additional
           fields will be returned in the response, such as
           :code:`"weight"`, :code:`"format_quantity"`,
           :code:`"external_id"`, :code:`"location"`, and
           :code:`"quantity"`.

        Parameters
        ----------
        username : `str`
            The username of the inventory owner. If not specified, the
            username of the authenticated user is used.

            **Example**: :code:`"360vinyl"`.

        status : `str`, keyword-only, optional
            The status of the listings to return.

            **Valid values**: :code:`"For Sale"`, :code:`"Draft"`,
            :code:`"Expired"`, :code:`"Sold"`, and :code:`"Deleted"`.

        page : `int` or `str`, keyword-only, optional
            The page you want to request.

            **Example**: :code:`3`.

        per_page : `int` or `str`, keyword-only, optional
            The number of items per page.

            **Example**: :code:`25`.

        sort : `str`, keyword-only, optional
            Sort items by this field.

            **Valid values**: :code:`"listed"`, :code:`"price"`,
            :code:`"item"`, :code:`"artist"`, :code:`"label"`,
            :code:`"catno"`, :code:`"audio"`, :code:`"status"`, and
            :code:`"location"`.

        sort_order : `str`, keyword-only, optional
            Sort items in a particular order.

            **Valid values**: :code:`"asc"` and :code:`"desc"`.

        Returns
        -------
        inventory : `dict`
            The seller's inventory.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "pagination": {
                      "page": <int>,
                      "pages": <int>,
                      "per_page": <int>,
                      "items": <int>,
                      "urls": {}
                    },
                    "listings": [
                      {
                        "status": <str>,
                        "price": {
                          "currency": <str>,
                          "value": <float>
                        },
                        "allow_offers": <bool>,
                        "sleeve_condition": <str>,
                        "id": <int>,
                        "condition": <str>,
                        "posted": <str>,
                        "ships_from": <str>,
                        "uri": <str>,
                        "comments": <str>,
                        "seller": {
                          "username": <str>,
                          "resource_url": <str>,
                          "id": <int>
                        },
                        "release": {
                          "catalog_number": <str>,
                          "resource_url": <str>,
                          "year": <int>,
                          "id": <int>,
                          "description": <str>,
                          "artist": <str>,
                          "title": <str>,
                          "format": <str>,
                          "thumbnail": <str>
                        },
                        "resource_url": <str>,
                        "audio": <bool>
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
            f"{self.API_URL}/users/{username}/inventory",
            params={
                "status": status,
                "page": page,
                "per_page": per_page,
                "sort": sort,
                "sort_order": sort_order,
            },
        )

    def get_listing(
        self, listing_id: Union[int, str], *, curr_abbr: str = None
    ) -> dict[str, Any]:
        """
        `Marketplace > Listing <https://www.discogs.com/developers
        /#page:marketplace,header:marketplace-listing-get>`_: View
        marketplace listings.

        Parameters
        ----------
        listing_id : `int` or `str`
            The ID of the listing you are fetching.

            **Example**: :code:`172723812`.

        curr_abbr : `str`, keyword-only, optional
            Currency abbreviation for marketplace listings. Defaults to
            the authenticated user's currency.

            **Valid values**: :code:`"USD"`, :code:`"GBP"`, :code:`"EUR"`,
            :code:`"CAD"`, :code:`"AUD"`, :code:`"JPY"`, :code:`"CHF"`,
            :code:`"MXN"`, :code:`"BRL"`, :code:`"NZD"`, :code:`"SEK"`,
            and :code:`"ZAR"`.

        Returns
        -------
        listing : `dict`
            The marketplace listing.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "status": <str>,
                    "price": {
                      "currency": <str>,
                      "value": <int>
                    },
                    "original_price": {
                      "curr_abbr": <str>,
                      "curr_id": <int>,
                      "formatted": <str>,
                      "value": <float>
                    },
                    "allow_offers": <bool>,
                    "sleeve_condition": <str>,
                    "id": <int>,
                    "condition": <str>,
                    "posted": <str>,
                    "ships_from": <str>,
                    "uri": <str>,
                    "comments": <str>,
                    "seller": {
                      "username": <str>,
                      "avatar_url": <str>,
                      "resource_url": <str>,
                      "url": <str>,
                      "id": <int>,
                      "shipping": <str>,
                      "payment": <str>,
                      "stats": {
                        "rating": <str>,
                        "stars": <float>,
                        "total": <int>
                      }
                    },
                    "shipping_price": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "original_shipping_price": {
                      "curr_abbr": <str>,
                      "curr_id": <int>,
                      "formatted": <str>,
                      "value": <float>
                    },
                    "release": {
                      "catalog_number": <str>,
                      "resource_url": <str>,
                      "year": <int>,
                      "id": <int>,
                      "description": <str>,
                      "thumbnail": <str>,
                    },
                    "resource_url": <str>,
                    "audio": <bool>
                  }
        """

        return self._get_json(
            f"{self.API_URL}/marketplace/listings/{listing_id}",
            params={"curr_abbr": curr_abbr},
        )

    def create_listing(
        self,
        release_id: Union[int, str],
        condition: str,
        price: float,
        status: str = "For Sale",
        *,
        sleeve_condition: str = None,
        comments: str = None,
        allow_offers: bool = None,
        external_id: str = None,
        location: str = None,
        weight: float = None,
        format_quantity: int = None,
    ) -> dict[str, Any]:
        """
        `Marketplace > New Listing <https://www.discogs.com/developers
        /#page:marketplace,header:marketplace-new-listing>`_: Create a
        marketplace listing.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        release_id : `int` or `str`
            The ID of the release you are posting.

            **Example**: :code:`249504`.

        condition : `str`
            The condition of the release you are posting.

            **Valid values**: :code:`"Mint (M)"`,
            :code:`"Near Mint (NM or M-)"`,
            :code:`"Very Good Plus (VG+)"`,
            :code:`"Very Good (VG)"`, :code:`"Good Plus (G+)"`,
            :code:`"Good (G)"`, :code:`"Fair (F)"`, and
            :code:`"Poor (P)"`.

        price : `float`
            The price of the item (in the seller's currency).

            **Example**: :code:`10.00`.

        status : `str`, default: :code:`"For Sale"`
            The status of the listing.

            **Valid values**: :code:`"For Sale"` (the listing is ready
            to be shwon on the marketplace) and :code:`"Draft"` (the
            listing is not ready for public display).

        sleeve_condition : `str`, optional
            The condition of the sleeve of the item you are posting.

            **Valid values**: :code:`"Mint (M)"`,
            :code:`"Near Mint (NM or M-)"`,
            :code:`"Very Good Plus (VG+)"`,
            :code:`"Very Good (VG)"`, :code:`"Good Plus (G+)"`,
            :code:`"Good (G)"`, :code:`"Fair (F)"`, and
            :code:`"Poor (P)"`.

        comments : `str`, optional
            Any remarks about the item that will be displated to buyers.

        allow_offers : `bool`, optional
            Whether or not to allow buyers to make offers on the item.

            **Default**: :code:`False`.

        external_id : `str`, optional
            A freeform field that can be used for the seller's own
            reference. Information stored here will not be displayed to
            anyone other than the seller. This field is called “Private
            Comments” on the Discogs website.

        location : `str`, optional
            A freeform field that is intended to help identify an item's
            physical storage location. Information stored here will not
            be displayed to anyone other than the seller. This field
            will be visible on the inventory management page and will be
            available in inventory exports via the website.

        weight : `float`, optional
            The weight, in grams, of this listing, for the purpose of
            calculating shipping. Set this field to :code:`"auto"` to
            have the weight automatically estimated for you.

        format_quantity : `int`, optional
            The number of items this listing counts as, for the purpose
            of calculating shipping. This field is called "Counts As" on
            the Discogs website. Set this field to :code:`"auto"` to
            have the quantity automatically estimated for you.
        """

        return self._request(
            "post",
            f"{self.API_URL}/marketplace/listings",
            params={
                "release_id": release_id,
                "condition": condition,
                "price": price,
                "status": status,
                "sleeve_condition": sleeve_condition,
                "comments": comments,
                "allow_offers": allow_offers,
                "external_id": external_id,
                "location": location,
                "weight": weight,
                "format_quantity": format_quantity,
            },
        ).json()

    def edit_listing(
        self,
        listing_id: Union[int, str],
        release_id: Union[int, str],
        condition: str,
        price: float,
        status: str = "For Sale",
        *,
        sleeve_condition: str = None,
        comments: str = None,
        allow_offers: bool = None,
        external_id: str = None,
        location: str = None,
        weight: float = None,
        format_quantity: int = None,
    ) -> None:
        """
        `Marketplace > Listing > Edit Listing <https://www.discogs.com
        /developers/#page:marketplace,header:marketplace-listing-post>`_:
        Edit the data associated with a listing.

        If the listing's status is not :code:`"For Sale"`,
        :code:`"Draft"`, or :code:`"Expired"`, it cannot be
        modified—only deleted. To re-list a :code:`"Sold"` listing, a
        new listing must be created.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        listing_id : `int` or `str`
            The ID of the listing you are fetching.

            **Example**: :code:`172723812`.

        release_id : `int` or `str`
            The ID of the release you are posting.

            **Example**: :code:`249504`.

        condition : `str`
            The condition of the release you are posting.

            **Valid values**: :code:`"Mint (M)"`,
            :code:`"Near Mint (NM or M-)"`,
            :code:`"Very Good Plus (VG+)"`,
            :code:`"Very Good (VG)"`, :code:`"Good Plus (G+)"`,
            :code:`"Good (G)"`, :code:`"Fair (F)"`, and
            :code:`"Poor (P)"`.

        price : `float`
            The price of the item (in the seller's currency).

            **Example**: :code:`10.00`.

        status : `str`, default: :code:`"For Sale"`
            The status of the listing.

            **Valid values**: :code:`"For Sale"` (the listing is ready
            to be shwon on the marketplace) and :code:`"Draft"` (the
            listing is not ready for public display).

        sleeve_condition : `str`, optional
            The condition of the sleeve of the item you are posting.

            **Valid values**: :code:`"Mint (M)"`,
            :code:`"Near Mint (NM or M-)"`,
            :code:`"Very Good Plus (VG+)"`,
            :code:`"Very Good (VG)"`, :code:`"Good Plus (G+)"`,
            :code:`"Good (G)"`, :code:`"Fair (F)"`, and
            :code:`"Poor (P)"`.

        comments : `str`, optional
            Any remarks about the item that will be displated to buyers.

        allow_offers : `bool`, optional
            Whether or not to allow buyers to make offers on the item.

            **Default**: :code:`False`.

        external_id : `str`, optional
            A freeform field that can be used for the seller's own
            reference. Information stored here will not be displayed to
            anyone other than the seller. This field is called “Private
            Comments” on the Discogs website.

        location : `str`, optional
            A freeform field that is intended to help identify an item's
            physical storage location. Information stored here will not
            be displayed to anyone other than the seller. This field
            will be visible on the inventory management page and will be
            available in inventory exports via the website.

        weight : `float`, optional
            The weight, in grams, of this listing, for the purpose of
            calculating shipping. Set this field to :code:`"auto"` to
            have the weight automatically estimated for you.

        format_quantity : `int`, optional
            The number of items this listing counts as, for the purpose
            of calculating shipping. This field is called "Counts As" on
            the Discogs website. Set this field to :code:`"auto"` to
            have the quantity automatically estimated for you.
        """

        self._check_authentication("edit_listing")

        self._request(
            "post",
            f"{self.API_URL}/marketplace/listings/{listing_id}",
            json={
                "release_id": release_id,
                "condition": condition,
                "price": price,
                "status": status,
                "sleeve_condition": sleeve_condition,
                "comments": comments,
                "allow_offers": allow_offers,
                "external_id": external_id,
                "location": location,
                "weight": weight,
                "format_quantity": format_quantity,
            },
        )

    def delete_listing(self, listing_id: Union[int, str]) -> None:
        """
        `Marketplace > Listing > Delete Listing <https://www.discogs.com
        /developers/#page:marketplace,header
        :marketplace-listing-delete>`_: Permanently remove a listing
        from the marketplace.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        listing_id : `int` or `str`
            The ID of the listing you are fetching.

            **Example**: :code:`172723812`.
        """

        self._check_authentication("delete_listing")

        self._request("delete", f"{self.API_URL}/marketplace/listings/{listing_id}")

    def get_order(self, order_id: str) -> dict[str, Any]:
        """
        `Marketplace > Order > Get Order <https://www.discogs.com/developers
        #page:marketplace,header:marketplace-order-get>`_: View the data
        associated with an order.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        order_id : `str`
            The ID of the order you are fetching.

            **Example**: :code:`1-1`.

        Returns
        -------
        order : `dict`
            The marketplace order.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "id": <str>,
                    "resource_url": <str>,
                    "messages_url": <str>,
                    "uri": <str>,
                    "status": <str>,
                    "next_status": [<str>],
                    "fee": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "created": <str>,
                    "items": [
                      {
                        "release": {
                          "id": <int>,
                          "description": <str>,
                        },
                        "price": {
                          "currency": <str>,
                          "value": <int>
                        },
                        "media_condition": <str>,
                        "sleeve_condition": <str>,
                        "id": <int>
                      }
                    ],
                    "shipping": {
                      "currency": <str>,
                      "method": <str>,
                      "value": <int>
                    },
                    "shipping_address": <str>,
                    "additional_instructions": <str>,
                    "archived": <bool>,
                    "seller": {
                      "resource_url": <str>,
                      "username": <str>,
                      "id": <int>
                    },
                    "last_activity": <str>,
                    "buyer": {
                      "resource_url": <str>,
                      "username": <str>,
                      "id": <int>
                    },
                    "total": {
                      "currency": <str>,
                      "value": <int>
                    }
                  }
        """

        self._check_authentication("get_order")

        return self._get_json(f"{self.API_URL}/marketplace/orders/{order_id}")

    def edit_order(
        self, order_id: str, status: str, *, shipping: float = None
    ) -> dict[str, Any]:
        """
        `Marketplace > Order > Edit Order <https://www.discogs.com/developers
        #page:marketplace,header:marketplace-order-post>`_: Edit the data
        associated with an order.

        The response contains a :code:`"next_status"` key—an array of
        valid next statuses for this order.

        Changing the order status using this resource will always message
        the buyer with

            Seller changed status from [...] to [...]

        and does not provide a facility for including a custom message
        along with the change. For more fine-grained control, use the
        :meth:`add_order_message` method, which allows you to
        simultaneously add a message and change the order status. If the
        order status is not :code:`"Cancelled"`,
        :code:`"Payment Received"`, or :code:`"Shipped"`, you can change
        the shipping. Doing so will send an invoice to the buyer and set
        the order status to :code:`"Invoice Sent"`. (For that reason,
        you cannot set the shipping and the order status in the same
        request.)

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        order_id : `str`
            The ID of the order you are fetching.

            **Example**: :code:`1-1`.

        status : `str`
            The status of the order you are updating. The new status must
            be present in the order's :code:`"next_status"` list.

            **Valid values**: :code:`"New Order"`,
            :code:`"Buyer Contacted"`, :code:`"Invoice Sent"`,
            :code:`"Payment Pending"`, :code:`"Payment Received"`,
            :code:`"In Progress"`, :code:`"Shipped"`,
            :code:`"Refund Sent"`, :code:`"Cancelled (Non-Paying Buyer)"`,
            :code:`"Cancelled (Item Unavailable)"`, and
            :code:`"Cancelled (Per Buyer's Request)"`.

        shipping : `float`, optional
            The order shipping amount. As a side effect of setting this
            value, the buyer is invoiced and the order status is set to
            :code:`"Invoice Sent"`.

            **Example**: :code:`5.00`.

        Returns
        -------
        order : `dict`
            The marketplace order.

            .. admonition:: Sample
                :class: dropdown

                .. code::

                  {
                    "id": <str>,
                    "resource_url": <str>,
                    "messages_url": <str>,
                    "uri": <str>,
                    "status": <str>,
                    "next_status": [<str>],
                    "fee": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "created": <str>,
                    "items": [
                      {
                        "release": {
                          "id": <int>,
                          "description": <str>,
                        },
                        "price": {
                          "currency": <str>,
                          "value": <int>
                        },
                        "media_condition": <str>,
                        "sleeve_condition": <str>,
                        "id": <int>
                      }
                    ],
                    "shipping": {
                      "currency": <str>,
                      "method": <str>,
                      "value": <int>
                    },
                    "shipping_address": <str>,
                    "additional_instructions": <str>,
                    "archived": <bool>,
                    "seller": {
                      "resource_url": <str>,
                      "username": <str>,
                      "id": <int>
                    },
                    "last_activity": <str>,
                    "buyer": {
                      "resource_url": <str>,
                      "username": <str>,
                      "id": <int>
                    },
                    "total": {
                      "currency": <str>,
                      "value": <int>
                    }
                  }
        """

        self._check_authentication("edit_order")

        return self._request(
            "post",
            f"{self.API_URL}/marketplace/orders/{order_id}",
            json={"status": status, "shipping": shipping},
        ).json()

    def get_user_orders(
        self,
        *,
        status: str = None,
        created_after: str = None,
        created_before: str = None,
        archived: bool = None,
        page: Union[int, str] = None,
        per_page: Union[int, str] = None,
        sort: str = None,
        sort_order: str = None,
    ) -> dict[str, Any]:
        """
        `Marketplace > List Orders <https://www.discogs.com/developers
        /#page:marketplace,header:marketplace-list-orders-get>`_:
        Returns a list of the authenticated user's orders.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        status : `str`, keyword-only, optional
            Only show orders with this status.

            **Valid values**: :code:`"All"`, :code:`"New Order"`,
            :code:`"Buyer Contacted"`, :code:`"Invoice Sent"`,
            :code:`"Payment Pending"`, :code:`"Payment Received"`,
            :code:`"In Progress"`, :code:`"Shipped"`,
            :code:`"Merged"`, :code:`"Order Changed"`,
            :code:`"Refund Sent"`, :code:`"Cancelled"`,
            :code:`"Cancelled (Non-Paying Buyer)"`,
            :code:`"Cancelled (Item Unavailable)"`,
            :code:`"Cancelled (Per Buyer's Request)"`, and
            :code:`"Cancelled (Refund Received)"`.

        created_after : `str`, keyword-only, optional
            Only show orders created after this ISO 8601 timestamp.

            **Example**: :code:`"2019-06-24T20:58:58Z"`.

        created_before : `str`, keyword-only, optional
            Only show orders created before this ISO 8601 timestamp.

            **Example**: :code:`"2019-06-24T20:58:58Z"`.

        archived : `bool`, keyword-only, optional
            Only show orders with a specific archived status. If no key
            is provided, both statuses are returned.

        page : `int` or `str`, keyword-only, optional
            The page you want to request.

            **Example**: :code:`3`.

        per_page : `int`, keyword-only, optional
            The number of items per page.

            **Example**: :code:`25`.

        sort : `str`, keyword-only, optional
            Sort items by this field.

            **Valid values**: :code:`"id"`, :code:`"buyer"`,
            :code:`"created"`, :code:`"status"`, and
            :code:`"last_activity"`.

        sort_order : `str`, keyword-only, optional
            Sort items in a particular order.

            **Valid values**: :code:`"asc"` and :code:`"desc"`.

        Returns
        -------
        orders : `dict`
            The authenticated user's orders.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "pagination": {
                      "page": <int>,
                      "pages": <int>,
                      "per_page": <int>,
                      "items": <int>,
                      "urls": {}
                    },
                    "orders": [
                      {
                        "id": <str>,
                        "resource_url": <str>,
                        "messages_url": <str>,
                        "uri": <str>,
                        "status": <str>,
                        "next_status": [<str>],
                        "fee": {
                          "currency": <str>,
                          "value": <float>
                        },
                        "created": <str>,
                        "items": [
                          {
                            "release": {
                              "id": <int>,
                              "description": <str>,
                            },
                            "price": {
                              "currency": <str>,
                              "value": <int>
                            },
                            "media_condition": <str>,
                            "sleeve_condition": <str>,
                            "id": <int>
                          }
                        ],
                        "shipping": {
                          "currency": <str>,
                          "method": <str>,
                          "value": <int>
                        },
                        "shipping_address": <str>,
                        "additional_instructions": <str>,
                        "archived": <bool>,
                        "seller": {
                          "resource_url": <str>,
                          "username": <str>,
                          "id": <int>
                        },
                        "last_activity": <str>,
                        "buyer": {
                          "resource_url": <str>,
                          "username": <str>,
                          "id": <int>
                        },
                        "total": {
                          "currency": <str>,
                          "value": <int>
                        }
                      }
                    ]
                  }
        """

        self._check_authentication("get_user_orders")

        return self._get_json(
            f"{self.API_URL}/marketplace/orders",
            params={
                "status": status,
                "created_after": created_after,
                "created_before": created_before,
                "archived": archived,
                "page": page,
                "per_page": per_page,
                "sort": sort,
                "sort_order": sort_order,
            },
        )

    def get_order_messages(
        self,
        order_id: str,
        *,
        page: Union[int, str] = None,
        per_page: Union[int, str] = None,
    ) -> dict[str, Any]:
        """
        `Marketplace > List Order Messages > List Order Messages
        <https://www.discogs.com/developers/
        #page:marketplace,header:marketplace-list-order-messages-get>`_:
        Returns a list of the order's messages with the most recent
        first.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        order_id : `str`
            The ID of the order you are fetching.

            **Example**: :code:`1-1`.

        page : `int` or `str`, keyword-only, optional
            The page you want to request.

            **Example**: :code:`3`.

        per_page : `int` or `str`, keyword-only, optional
            The number of items per page.

            **Example**: :code:`25`.

        Returns
        -------
        messages : `dict`
            The order's messages.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "pagination": {
                      "per_page": <int>,
                      "items": <int>,
                      "page": <int>,
                      "urls": {
                        "last": <str>,
                        "next": <str>
                      },
                      "pages": <int>
                    },
                    "messages": [
                      {
                        "refund": {
                          "amount": <int>,
                          "order": {
                            "resource_url": <str>,
                            "id": <str>
                          }
                        },
                        "timestamp": <str>,
                        "message": <str>,
                        "type": <str>,
                        "order": {
                          "resource_url": <str>,
                          "id": <str>,
                        },
                        "subject": <str>
                      }
                    ]
                  }
        """

        self._check_authentication("get_order_messages")

        return self._get_json(
            f"{self.API_URL}/marketplace/orders/{order_id}/messages",
            params={"page": page, "per_page": per_page},
        )

    def add_order_message(
        self, order_id: str, message: str = None, status: str = None
    ) -> dict[str, Any]:
        """
        `Marketplace > List Order Messages > Add New Message
        <https://www.discogs.com/developers/
        #page:marketplace,header:marketplace-list-order-messages-post>`_:
        Adds a new message to the order's message log.

        When posting a new message, you can simultaneously change the
        order status. IF you do, the message will automatically be
        prepended with:

            Seller changed status from [...] to [...]

        While `message` and `status` are each optional, one or both
        must be present.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        order_id : `str`
            The ID of the order you are fetching.

            **Example**: :code:`1-1`.

        message : `str`, optional
            The message you are posting.

            **Example**: :code:`"hello world"`

        status : `str`, optional
            The status of the order you are updating.

            **Valid values**: :code:`"New Order"`,
            :code:`"Buyer Contacted"`, :code:`"Invoice Sent"`,
            :code:`"Payment Pending"`, :code:`"Payment Received"`,
            :code:`"In Progress"`, :code:`"Shipped"`,
            :code:`"Refund Sent"`, :code:`"Cancelled (Non-Paying Buyer)"`,
            :code:`"Cancelled (Item Unavailable)"`, and
            :code:`"Cancelled (Per Buyer's Request)"`.

        Returns
        -------
        message : `dict`
            The order's message.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "from": {
                      "username": <str>,
                      "resource_url": <str>
                    },
                    "message": <str>,
                    "order": {
                      "resource_url": <str>,
                      "id": <str>
                    },
                    "timestamp": <str>,
                    "subject": <str>
                  }
        """

        self._check_authentication("add_order_message")

        if message is None and status is None:
            emsg = "Either 'message' or 'status' must be provided."
            raise ValueError(emsg)

        return self._request(
            "post",
            f"{self.API_URL}/marketplace/orders/{order_id}/messages",
            json={"message": message, "status": status},
        ).json()

    def get_fee(self, price: float, *, currency: str = "USD") -> dict[str, Any]:
        """
        `Marketplace > Fee with currency
        <https://www.discogs.com/developers/#page:marketplace,header
        :marketplace-fee-with-currency-get>`_: Calculates the fee for
        selling an item on the marketplace given a particular currency.

        Parameters
        ----------
        price : `float`
            The price of the item (in the seller's currency).

            **Example**: :code:`10.00`.

        currency : `str`, keyword-only, default: :code:`"USD"`
            The currency abbreviation for the fee calculation.

            **Valid values**: :code:`"USD"`, :code:`"GBP"`, :code:`"EUR"`,
            :code:`"CAD"`, :code:`"AUD"`, :code:`"JPY"`, :code:`"CHF"`,
            :code:`"MXN"`, :code:`"BRL"`, :code:`"NZD"`, :code:`"SEK"`,
            and :code:`"ZAR"`.

        Returns
        -------
        fee : `dict`
            The fee for selling an item on the marketplace.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "value": <float>,
                    "currency": <str>,
                  }
        """

        return self._get_json(f"{self.API_URL}/marketplace/fee/{price}/{currency}")

    def get_price_suggestions(self, release_id: Union[int, str]) -> dict[str, Any]:
        """
        `Marketplace > Price Suggestions <https://www.discogs.com
        /developers/#page:marketplace,header
        :marketplace-price-suggestions>`_: Retrieve price suggestions in
        the user's selling currency for the provided release ID.

        If no suggestions are available, an empty object will be
        returned.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        release_id : `int` or `str`
            The ID of the release you are fetching.

            **Example**: :code:`249504`.

        Returns
        -------
        prices : `dict`
            The price suggestions for the release.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "Very Good (VG)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Good Plus (G+)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Near Mint (NM or M-)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Good (G)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Very Good Plus (VG+)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Mint (M)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Fair (F)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Poor (P)": {
                      "currency": <str>,
                      "value": <float>
                    }
                  }
        """

        self._check_authentication("get_price_suggestions")

        return self._get_json(
            f"{self.API_URL}/marketplace/price_suggestions/{release_id}"
        )

    def get_release_marketplace_stats(
        self, release_id: Union[int, str], *, curr_abbr: str = None
    ) -> dict[str, Any]:
        """
        `Marketplace > Release Statistics <https://www.discogs.com
        /developers/#page:marketplace,header
        :marketplace-release-statistics-get>`_: Retrieve marketplace
        statistics for the provided release ID.

        These statistics reflect the state of the release in the
        marketplace currently, and include the number of items currently
        for sale, lowest listed price of any item for sale, and whether
        the item is blocked for sale in the marketplace.

        Releases that have no items or are blocked for sale in the
        marketplace will return a body with null data in the
        :code:`"lowest_price"` and :code:`"num_for_sale"` keys.

        .. admonition:: User authentication
           :class: dropdown warning

           Authentication is optional. Authenticated users will by
           default have the lowest currency expressed in their own buyer
           currency, configurable in buyer settings, in the absence of
           the `curr_abbr` query parameter to specify the currency.
           Unauthenticated users will have the price expressed in US
           Dollars, if no `curr_abbr` is provided.

        Parameters
        ----------
        release_id : `int` or `str`
            The ID of the release you are fetching.

            **Example**: :code:`249504`.

        curr_abbr : `str`, keyword-only, optional
            Currency abbreviation for marketplace data.

            **Valid values**: :code:`"USD"`, :code:`"GBP"`,
            :code:`"EUR"`, :code:`"CAD"`, :code:`"AUD"`, :code:`"JPY"`,
            :code:`"CHF"`, :code:`"MXN"`, :code:`"BRL"`, :code:`"NZD"`,
            :code:`"SEK"`, and :code:`"ZAR"`.

        Returns
        -------
        stats : `dict`
            The marketplace statistics for the release.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "lowest_price": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "num_for_sale": <int>,
                    "blocked_from_sale": <bool>
                  }
        """

        return self._get_json(
            f"{self.API_URL}/marketplace/stats/{release_id}",
            params={"curr_abbr": curr_abbr},
        )

    ### INVENTORY EXPORT ######################################################

    def export_inventory(
        self, *, download: bool = True, filename: str = None, path: str = None
    ) -> str:
        """
        `Inventory Export > Export Your Inventory <https://www.discogs.com
        /developers/#page:inventory-export,header
        :inventory-export-export-your-inventory-post>`_: Request an
        export of your inventory as a CSV.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        download : `bool`, keyword-only, default: :code:`True`
            Specifies whether to download the CSV file. If
            :code:`False`, the export ID is returned.

        filename : `str`, optional
            Filename of the exported CSV file. A :code:`.csv` extension
            will be appended if not present. If not specified, the CSV
            file is saved as
            :code:`<username>-inventory-<date>-<number>.csv`.

        path : `str`, optional
            Path to save the exported CSV file. If not specified, the
            file is saved in the current working directory.

        Returns
        -------
        path_or_id : `str`
            Full path to the exported CSV file (:code:`download=True`)
            or the export ID (:code:`download=False`).
        """

        self._check_authentication("export_inventory")

        r = self._request("post", f"{self.API_URL}/inventory/export")
        if download:
            return self.download_inventory_export(
                r.headers["Location"].split("/")[-1], filename=filename, path=path
            )
        return r.headers["Location"]

    def get_inventory_exports(
        self, *, page: int = None, per_page: int = None
    ) -> dict[str, Any]:
        """
        `Inventory Export > Get Recent Exports <https://www.discogs.com
        /developers/#page:inventory-export,header
        :inventory-export-get-recent-exports-get>`_: Get all recent
        exports of your inventory.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        page : `int`, keyword-only, optional
            The page you want to request.

            **Example**: :code:`3`.

        per_page : `int`, keyword-only, optional
            The number of items per page.

            **Example**: :code:`25`.

        Returns
        -------
        exports : `dict`
            The authenticated user's inventory exports.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "status": <str>,
                        "created_ts": <str>,
                        "url": <str>,
                        "finished_ts": <str>,
                        "download_url": <str>,
                        "filename": <str>,
                        "id": <int>
                      }
                    ],
                    "pagination": {
                      "per_page": <int>,
                      "items": <int>,
                      "page": <int>,
                      "urls": {
                        "last": <str>,
                        "next": <str>
                      },
                      "pages": <int>
                    }
                  }
        """

        self._check_authentication("get_inventory_exports")

        return self._get_json(
            f"{self.API_URL}/inventory/export",
            json={"page": page, "per_page": per_page},
        )

    def get_inventory_export(self, export_id: int) -> dict[str, Union[int, str]]:
        """
        `Inventory Export > Get An Export <https://www.discogs.com
        /developers/#page:inventory-export,header
        :inventory-export-get-an-export-get>`_: Get details about the
        status of an inventory export.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        export_id : `int`
            ID of the export.

        Returns
        -------
        export : `dict`
            Details about the status of the inventory export.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "status": <str>,
                    "created_ts": <str>,
                    "url": <str>,
                    "finished_ts": <str>,
                    "download_url": <str>,
                    "filename": <str>,
                    "id": <int>
                  }
        """

        self._check_authentication("get_inventory_export")

        return self._get_json(f"{self.API_URL}/inventory/export/{export_id}")

    def download_inventory_export(
        self, export_id: int, *, filename: str = None, path: str = None
    ) -> str:
        """
        `Inventory Export > Download An Export <https://www.discogs.com
        /developers/#page:inventory-export,header
        :inventory-export-download-an-export-get>`_: Download the
        results of an inventory export.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        export_id : `int`
            ID of the export.

        filename : `str`, optional
            Filename of the exported CSV file. A :code:`.csv` extension
            will be appended if not present. If not specified, the CSV
            file is saved as
            :code:`<username>-inventory-<date>-<number>.csv`.

        path : `str`, optional
            Path to save the exported CSV file. If not specified, the
            file is saved in the current working directory.

        Returns
        -------
        path : `str`
            Full path to the exported CSV file.
        """

        self._check_authentication("download_inventory_export")

        while True:
            r = self.get_inventory_export(export_id)
            if r["status"] == "success":
                break
            time.sleep(1)

        r = self._request(
            "get", f"{self.API_URL}/inventory/export/{export_id}/download"
        )

        if filename is None:
            filename = r.headers["Content-Disposition"].split("=")[1]
        else:
            if not filename.endswith(".csv"):
                filename += ".csv"

        with open(path := os.path.join(path or os.getcwd(), filename), "w") as f:
            f.write(r.text)

        return path

    ### INVENTORY UPLOAD ######################################################

    # TODO

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
                    "id": <int>,
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

        .. admonition:: User authentication
           :class: dropdown warning

           If authenticated as the requested user, the :code:`"email"`
           key will be visible, and the :code:`"num_lists"` count will
           include the user's private lists.

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
                    "id": <int>,
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
        self,
        *,
        name: str = None,
        home_page: str = None,
        location: str = None,
        profile: str = None,
        curr_abbr: str = None,
    ) -> dict[str, Any]:
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

        if (
            name is None
            and home_page is None
            and location is None
            and profile is None
            and curr_abbr is None
        ):
            wmsg = "No changes were specified or made to the user profile."
            warnings.warn(wmsg)
            return

        if curr_abbr and curr_abbr not in (
            CURRENCIES := {
                "USD",
                "GBP",
                "EUR",
                "CAD",
                "AUD",
                "JPY",
                "CHF",
                "MXN",
                "BRL",
                "NZD",
                "SEK",
                "ZAR",
            }
        ):
            emsg = (
                f"Invalid currency abbreviation ({curr_abbr=}). "
                f"Valid values: {', '.join(CURRENCIES)}."
            )
            raise ValueError(emsg)

        return self._request(
            "post",
            f"{self.API_URL}/users/{self._username}",
            json={
                "name": name,
                "home_page": home_page,
                "location": location,
                "profile": profile,
                "curr_abbr": curr_abbr,
            },
        ).json()

    def get_user_submissions(
        self,
        username: str = None,
        *,
        page: Union[int, str] = None,
        per_page: Union[int, str] = None,
    ) -> dict[str, Any]:
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

        page : `int` or `str`, keyword-only, optional
            Page of results to fetch.

        per_page : `int` or `str`, keyword-only, optional
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
                      "urls": {
                        "last": <str>,
                        "next": <str>
                      }
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
                  }
        """

        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise ValueError("No username provided.")

        return self._get_json(
            f"{self.API_URL}/users/{username}/submissions",
            params={"page": page, "per_page": per_page},
        )

    def get_user_contributions(
        self,
        username: str = None,
        *,
        page: Union[int, str] = None,
        per_page: Union[int, str] = None,
        sort: str = None,
        sort_order: str = None,
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

        page : `int` or `str`, keyword-only, optional
            Page of results to fetch.

        per_page : `int` or `str`, keyword-only, optional
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
                      "urls": {
                        "last": <str>,
                        "next": <str>
                      }
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
            params={
                "page": page,
                "per_page": per_page,
                "sort": sort,
                "sort_order": sort_order,
            },
        )

    ### USER COLLECTION #######################################################

    def get_collection_folders(self, username: str = None) -> list[dict[str, Any]]:
        """
        `User Collection > Collection > Get Collection Folders
        <https://www.discogs.com/developers/#page:user-collection,header
        :user-collection-collection-get>`_: Retrieve a list of folders
        in a user's collection.

        .. admonition:: User authentication
           :class: dropdown warning

           If the collection has been made private by its owner,
           authentication as the collection owner is required. If you
           are not authenticated as the collection owner, only folder ID
           :code:`0` (the "All" folder) will be visible (if the
           requested user's collection is public).

        Parameters
        ----------
        username : `str`, optional
            The username of the collection you are trying to fetch. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        folders : `list`
            A list of folders in the user's collection.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  [
                    {
                      "id": <int>,
                      "name": <str>,
                      "count": <int>,
                      "resource_url": <str>
                    }
                  ]
        """

        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise ValueError("No username provided.")

        return self._get_json(f"{self.API_URL}/users/{username}/collection/folders")[
            "folders"
        ]

    def create_collection_folder(self, name: str) -> dict[str, Union[int, str]]:
        """
        `User Collection > Collection > Create Folder
        <https://www.discogs.com/developers/#page:user-collection,header
        :user-collection-collection-post>`_: Create a new folder in a
        user's collection.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        name : `str`
            The name of the newly-created folder.

            **Example**: :code:`"My favorites"`.

        Returns
        -------
        folder : `dict`
            Information about the newly-created folder.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "name": <str>,
                    "count": <int>,
                    "resource_url": <str>
                  }
        """

        self._check_authentication("create_collection_folder")

        return self._request(
            "post",
            f"{self.API_URL}/users/{self._username}/collection/folders",
            json={"name": name},
        ).json()

    def get_collection_folder(
        self, folder_id: int, *, username: str = None
    ) -> dict[str, Union[int, str]]:
        """
        `User Collection > Collection Folder > Get Folders
        <https://www.discogs.com/developers/#page:user-collection,header
        :user-collection-collection-folder-get>`_: Retrieve metadata
        about a folder in a user's collection.

        .. admonition:: User authentication
           :class: dropdown warning

           If `folder_id` is not :code:`0`, authentication as the
           collection owner is required.

        Parameters
        ----------
        folder_id : `int`
            The ID of the folder to request.

            **Example**: :code:`3`.

        username : `str`, keyword-only, optional
            The username of the collection you are trying to request. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        folder : `dict`
            Metadata about the folder.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "name": <str>,
                    "count": <int>,
                    "resource_url": <str>
                  }
        """

        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise ValueError("No username provided.")

        if folder_id != 0:
            self._check_authentication("get_collection_folder")

        return self._get_json(
            f"{self.API_URL}/users/{self._username}" f"/collection/folders/{folder_id}"
        )

    def rename_collection_folder(
        self, folder_id: int, name: str, *, username: str = None
    ) -> dict[str, Union[int, str]]:
        """
        `User Collection > Collection Folder > Edit Folder
        <https://www.discogs.com/developers/#page:user-collection,header
        :user-collection-collection-folder-post>`_: Rename a folder.

        Folders :code:`0` and :code:`1` cannot be renamed.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        folder_id : `int`
            The ID of the folder to modify.

            **Example**: :code:`3`.

        name : `str`
            The new name of the folder.

            **Example**: :code:`"My favorites"`.

        username : `str`, keyword-only, optional
            The username of the collection you are trying to modify. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        folder : `dict`
            Information about the edited folder.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "name": <str>,
                    "count": <int>,
                    "resource_url": <str>
                  }
        """

        self._check_authentication("rename_collection_folder")

        return self._request(
            "post",
            f"{self.API_URL}/users/{self._username}" f"/collection/folders/{folder_id}",
            json={"name": name},
        ).json()

    def delete_collection_folder(self, folder_id: int, *, username: str = None) -> None:
        """
        `User Collection > Collection Folder > Delete Folder
        <https://www.discogs.com/developers/#page:user-collection,header
        :user-collection-collection-folder-delete>`_: Delete a folder
        from a user's collection.

        A folder must be empty before it can be deleted.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        folder_id : `int`
            The ID of the folder to delete.

            **Example**: :code:`3`.

        username : `str`, keyword-only, optional
            The username of the collection you are trying to delete. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"rodneyfool"`.
        """

        self._check_authentication("delete_collection_folder")

        self._request(
            "delete",
            f"{self.API_URL}/users/{self._username}" f"/collection/folders/{folder_id}",
        )

    def get_collection_folders_by_release(
        self, release_id: Union[int, str], *, username: str = None
    ) -> dict[str, Any]:
        """
        `User Collection > Collection Items By Release
        <https://www.discogs.com/developers/#page:user-collection,header
        :user-collection-collection-items-by-release-get>`_: View the
        user's collection folders which contain a specified release.
        This will also show information about each release instance.

        Parameters
        ----------
        release_id : `int` or `str`
            The ID of the release to request.

            **Example**: :code:`7781525`.

        username : `str`, keyword-only, optional
            The username of the collection you are trying to view. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"susan.salkeld"`.

        Returns
        -------
        releases : `list`
            A list of releases and their folders.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "pagination": {
                      "per_page": <int>,
                      "items": <int>,
                      "page": <int>,
                      "urls": {
                        "last": <str>,
                        "next": <str>
                      },
                      "pages": <int>
                    },
                    "releases": [
                      {
                        "instance_id": <int>,
                        "rating": <int>,
                        "basic_information": {
                          "labels": [
                            {
                              "name": <str>,
                              "entity_type": <str>,
                              "catno": <str>,
                              "resource_url": <str>,
                              "id": <int>,
                              "entity_type_name": <str>
                            }
                          ],
                          "formats": [
                            {
                              "descriptions": [<str>],
                              "name": <str>,
                              "qty": <str>
                            }
                          ],
                          "thumb": <str>,
                          "title": <str>,
                          "artists": [
                            {
                              "join": <str>,
                              "name": <str>,
                              "anv": <str>,
                              "tracks": <str>,
                              "role": <str>,
                              "resource_url": <str>,
                              "id": <int>
                            }
                          ],
                          "resource_url": <str>,
                          "year": <int>,
                          "id": <int>,
                        },
                        "folder_id": <int>,
                        "date_added": <str>,
                        "id": <int>
                      }
                    ]
                  }
        """

        return self._get_json(
            f"{self.API_URL}/users/{self._username}/collection"
            f"/releases/{release_id}"
        )["folders"]

    def get_collection_folder_releases(
        self,
        folder_id: int,
        *,
        username: str = None,
        page: int = None,
        per_page: int = None,
        sort: str = None,
        sort_order: str = None,
    ) -> dict[str, Any]:
        """
        `User Collection > Collection Items By Folder
        <https://www.discogs.com/developers/#page:user-collection,header
        :user-collection-collection-items-by-folder>`_: Returns the items
        in a folder in a user's collection.

        Basic information about each release is provided, suitable for
        display in a list. For detailed information, make another call
        to fetch the corresponding release.

        .. admonition:: User authentication
           :class: dropdown warning

           If `folder_id` is not :code:`0` or the collection has been
           made private by its owner, authentication as the collection
           owner is required.

           If you are not authenticated as the collection owner, only
           the public notes fields will be visible.

        Parameters
        ----------
        folder_id : `int`
            The ID of the folder to request.

            **Example**: :code:`3`.

        username : `str`, keyword-only, optional
            The username of the collection you are trying to request. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"rodneyfool"`.

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
        items : `dict`
            Items in the folder.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "pagination": {
                      "per_page": <int>,
                      "items": <int>,
                      "page": <int>,
                      "urls": {
                        "last": <str>,
                        "next": <str>
                      },
                      "pages": <int>
                    },
                    "releases": [
                      {
                        "instance_id": <int>,
                        "rating": <int>,
                        "basic_information": {
                          "labels": [
                            {
                              "name": <str>,
                              "entity_type": <str>,
                              "catno": <str>,
                              "resource_url": <str>,
                              "id": <int>,
                              "entity_type_name": <str>
                            }
                          ],
                          "formats": [
                            {
                              "descriptions": [<str>],
                              "name": <str>,
                              "qty": <str>
                            }
                          ],
                          "thumb": <str>,
                          "title": <str>,
                          "artists": [
                            {
                              "join": <str>,
                              "name": <str>,
                              "anv": <str>,
                              "tracks": <str>,
                              "role": <str>,
                              "resource_url": <str>,
                              "id": <int>
                            }
                          ],
                          "resource_url": <str>,
                          "year": <int>,
                          "id": <int>,
                        },
                        "folder_id": <int>,
                        "date_added": <str>,
                        "id": <int>
                      }
                    ]
                  }
        """

        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise ValueError("No username provided.")

        if folder_id != 0:
            self._check_authentication("get_collection_folder_releases")

        return self._get_json(
            f"{self.API_URL}/users/{username}/collection"
            f"/folders/{folder_id}/releases",
            params={
                "page": page,
                "per_page": per_page,
                "sort": sort,
                "sort_order": sort_order,
            },
        )

    def add_collection_folder_release(
        self, folder_id: int, release_id: int, *, username: str = None
    ) -> dict[str, Union[int, str]]:
        """
        `User Collection > Add To Collection Folder
        <https://www.discogs.com/developers/#page:user-collection,header
        :user-collection-add-to-collection-folder-post>`_: Add a release
        to a folder in a user's collection.

        The `folder_id` must be non-zero. You can use :code:`1` for
        "Uncategorized".

        .. admonition:: User authentication
            :class: warning

            Requires user authentication with a personal access token or
            via the OAuth 1.0a flow.

        Parameters
        ----------
        folder_id : `int`
            The ID of the folder to modify.

            **Example**: :code:`3`.

        release_id : `int`
            The ID of the release you are adding.

            **Example**: :code:`130076`.

        username : `str`, keyword-only, optional
            The username of the collection you are trying to modify. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        folder : `dict`
            Information about the folder.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "instance_id": <int>,
                    "resource_url": <str>
                  }
        """

        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise ValueError("No username provided.")

        return self._request(
            "post",
            f"{self.API_URL}/users/{username}/collection"
            f"/folders/{folder_id}/releases/{release_id}",
        ).json()

    def edit_collection_folder_release(
        self,
        folder_id: int,
        release_id: int,
        instance_id: int,
        *,
        username: str = None,
        new_folder_id: int,
        rating: int = None,
    ) -> None:
        """
        `User Collection > Change Rating Of Release
        <https://www.discogs.com/developers#page:user-collection,header
        :user-collection-change-rating-of-release-post>`_: Change the
        rating on a release and/or move the instance to another folder.

        This endpoint potentially takes two folder ID parameters:
        `folder_id` (which is the folder you are requesting, and is
        required), and `new_folder_id` (representing the folder you want
        to move the instance to, which is optional).

        .. admonition:: User authentication
            :class: warning

            Requires user authentication with a personal access token or
            via the OAuth 1.0a flow.

        Parameters
        ----------
        folder_id : `int`
            The ID of the folder to modify.

            **Example**: :code:`3`.

        release_id : `int`
            The ID of the release you are modifying.

            **Example**: :code:`130076`.

        instance_id : `int`
            The ID of the instance.

            **Example**: :code:`1`.

        username : `str`, keyword-only, optional
            The username of the collection you are trying to modify. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"rodneyfool"`.

        new_folder_id : `int`
            The ID of the folder to move the instance to.

            **Example**: :code:`4`.

        rating : `int`, keyword-only, optional
            The rating of the instance you are supplying.

            **Example**: :code:`5`.
        """

        self._request(
            "post",
            f"{self.API_URL}/users/{username}/collection/folders"
            f"/{folder_id}/releases/{release_id}/instances/{instance_id}",
            json={"folder_id": new_folder_id, "rating": rating},
        )

    def delete_collection_folder_release(
        self, folder_id: int, release_id: int, instance_id: int, *, username: str = None
    ) -> None:
        """
        `User Collection > Delete Instance From Folder
        <https://www.discogs.com/developers/#page:user-collection,header
        :user-collection-delete-instance-from-folder-delete>`_: Remove an
        instance of a release from a user's collection folder.

        To move the release to the "Uncategorized" folder instead, use
        the :meth:`edit_collection_folder_release` method.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        folder_id : `int`
            The ID of the folder to modify.

            **Example**: :code:`3`.

        release_id : `int`
            The ID of the release you are modifying.

            **Example**: :code:`130076`.

        instance_id : `int`
            The ID of the instance.

            **Example**: :code:`1`.

        username : `str`, keyword-only, optional
            The username of the collection you are trying to modify. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"rodneyfool"`.
        """

        self._request(
            "delete",
            f"{self.API_URL}/users/{username}/collection/folders"
            f"/{folder_id}/releases/{release_id}/instances/{instance_id}",
        )

    def get_collection_fields(self, username: str = None) -> list[dict[str, Any]]:
        """
        `User Collection > Collection Fields
        <https://www.discogs.com/developers/#page:user-collection,header
        :user-collection-list-custom-fields-get>`_: Retrieve a list of
        user-defined collection notes fields.

        These fields are available on every release in the collection.

        .. admonition:: User authentication
           :class: dropdown warning

           If the collection has been made private by its owner,
           authentication as the collection owner is required.

           If you are not authenticated as the collection owner, only
           fields with public set to true will be visible.

        Parameters
        ----------
        username : `str`, optional
            The username of the collection you are trying to fetch. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        fields : `list`
            A list of user-defined collection fields.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  [
                    {
                      "id": <int>,
                      "name": <str>,
                      "options": [<str>],
                      "public": <bool>,
                      "position": <int>,
                      "type": "dropdown"
                    },
                    {
                      "id": <int>,
                      "name": <str>,
                      "lines": <int>,
                      "public": <bool>,
                      "position": <int>,
                      "type": "textarea"
                    }
                  ]
        """

        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise ValueError("No username provided.")

        return self._get_json(f"{self.API_URL}/users/{username}/collection/fields")[
            "fields"
        ]

    def edit_collection_release_field(
        self,
        folder_id: int,
        release_id: int,
        instance_id: int,
        field_id: int,
        value: str,
        *,
        username: str = None,
    ) -> None:
        """
        `User Collection > Edit Fields Instance
        <https://www.discogs.com/developers/#page:user-collection,header
        :user-collection-edit-fields-instance-post>`_: Change the value
        of a notes field on a particular instance.

        .. admonition:: User authentication
           :class: dropdown warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        folder_id : `int`
            The ID of the folder to modify.

            **Example**: :code:`3`.

        release_id : `int`
            The ID of the release you are modifying.

            **Example**: :code:`130076`.

        instance_id : `int`
            The ID of the instance.

            **Example**: :code:`1`.

        field_id : `int`
            The ID of the field you are modifying.

            **Example**: :code:`1`.

        value : `str`
            The new value of the field. If the field's type is
            :code:`"dropdown"`, `value` must match one of the values in
            the field's list of options.

        username : `str`, keyword-only, optional
            The username of the collection you are trying to modify. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"rodneyfool"`.
        """

        self._check_authentication("edit_collection_fields")

        self._request(
            "post",
            f"{self.API_URL}/users/{username}/collection/folders"
            f"/{folder_id}/releases/{release_id}/instances/{instance_id}"
            f"/fields/{field_id}",
            params={"value": value},
        )

    def get_collection_value(self, username: str = None) -> dict[str, Any]:
        """
        `User Collection > Collection Value
        <https://www.discogs.com/developers/#page:user-collection,header
        :user-collection-collection-value-get>`_: Returns the minimum,
        median, and maximum value of a user's collection.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication with a personal access token or
           via the OAuth 1.0a flow.

        Parameters
        ----------
        username : `str`, optional
            The username of the collection you are trying to fetch. If
            not specified, the username of the authenticated user is
            used.

            **Example**: :code:`"rodneyfool"`.

        Returns
        -------
        value : `dict`
            The total minimum value of the user's collection.

            .. admonition:: Sample
               :class: dropdown

               .. code::

                  {
                    "maximum": <str>,
                    "median": <str>,
                    "minimum": <str>
                  }
        """

        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise ValueError("No username provided.")

        return self._get_json(f"{self.API_URL}/users/{username}/collection/value")

    ### USER WANTLIST #########################################################

    # TODO

    ### USER LISTS ############################################################

    # TODO
