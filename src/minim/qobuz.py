"""
Qobuz
=====
.. moduleauthor:: Benjamin Ye <GitHub: bbye98>

This module contains a minimum implementation of the private Qobuz API.
"""

import base64
import datetime
import hashlib
import logging
import os
import re
from typing import Any, Union

import requests

from . import FOUND_PLAYWRIGHT, DIR_HOME, DIR_TEMP, _config

if FOUND_PLAYWRIGHT:
    from playwright.sync_api import sync_playwright

__all__ = ["PrivateAPI"]


def _parse_performers(
    performers: str, roles: Union[list[str], set[str]] = None
) -> dict[str, list]:
    """
    Parse a string containing credits for a track.

    Parameters
    ----------
    performers : `str`
        An unformatted string containing the track credits obtained
        from calling :meth:`get_track`.

    roles : `list` or `set`, keyword-only, optional
        Role filter. The special :code:`"Composers"` filter will
        combine the :code:`"Composer"`, :code:`"ComposerLyricist"`,
        :code:`"Lyricist"`, and :code:`"Writer"` roles.

        **Valid values**: :code:`"MainArtist"`,
        :code:`"FeaturedArtist"`, :code:`"Producer"`,
        :code:`"Co-Producer"`, :code:`"Mixer"`,
        :code:`"Composers"` (:code:`"Composer"`,
        :code:`"ComposerLyricist"`, :code:`"Lyricist"`,
        :code:`"Writer"`), :code:`"MusicPublisher"`, etc.

    Returns
    -------
    credits : `dict`
        A dictionary containing the track contributors, with their
        roles (in snake case) being the keys.
    """

    people = {}
    for p in performers.split(" - "):
        if regex := re.search(
            r"(^.*[A-Za-z]\.|^.*&.*|[\d\s\w].*?)(?:, )(.*)", p.rstrip()
        ):
            people[regex.groups()[0]] = regex.groups()[1].split(", ")

    credits = {}
    if roles is None:
        roles = set(c for r in people.values() for c in r)
    elif "Composers" in roles:
        roles.remove("Composers")
        credits["composers"] = sorted(
            {
                p
                for cr in {
                    "Composer",
                    "ComposerLyricist",
                    "Lyricist",
                    "Writer",
                }
                for p, r in people.items()
                if cr in r
            }
        )
    for role in roles:
        credits[
            "_".join(
                re.findall(r"(?:[A-Z][a-z]+)(?:-[A-Z][a-z]+)?", role)
            ).lower()
        ] = [p for p, r in people.items() if role in r]

    return credits


class PrivateAPI:
    """
    Private Qobuz API client.

    The private TIDAL API allows songs, collections (albums, playlists),
    and performers to be queried, and information about them to be
    retrieved. As there is no available official documentation for the
    private Qobuz API, its endpoints have been determined by watching
    HTTP network traffic.

    .. attention::

       As the private Qobuz API is not designed to be publicly
       accessible, this class can be disabled or removed at any time to
       ensure compliance with the `Qobuz API Terms of Use
       <https://static.qobuz.com/apps/api/QobuzAPI-TermsofUse.pdf>`_.

    While authentication is not necessary to search for and retrieve
    data from public content, it is required to access personal content
    and stream media (with an active Qobuz subscription). In the latter
    case, requests to the private Qobuz API endpoints must be
    accompanied by a valid user authentication token in the header.

    Minim can obtain user authentication tokens via the password grant,
    but it is an inherently unsafe method of authentication since it has
    no mechanisms for multifactor authentication or brute force attack
    detection. As such, it is highly encouraged that you obtain a user
    authentication token yourself through the Qobuz Web Player or the
    Android, iOS, macOS, and Windows applications, and then provide it
    and its accompanying app ID and secret to this class's constructor
    as keyword arguments. The app credentials can also be stored as
    :code:`QOBUZ_PRIVATE_APP_ID` and :code:`QOBUZ_PRIVATE_APP_SECRET`
    in the operating system's environment variables, and they will
    automatically be retrieved.

    .. tip::

       The app credentials and user authentication token can be changed
       or updated at any time using :meth:`set_flow` and
       :meth:`set_auth_token`, respectively.

    Minim also stores and manages user authentication tokens and their
    properties. When the password grant is used to acquire a user
    authentication token, it is automatically saved to the Minim
    configuration file to be loaded on the next instantiation of this
    class. This behavior can be disabled if there are any security
    concerns, like if the computer being used is a shared device.

    Parameters
    ----------
    app_id : `str`, keyword-only, optional
        App ID. Required if an user authentication token is provided in
        `auth_token`.

    app_secret : `str`, keyword-only, optional
        App secret. Required if an user authentication token is provided
        in `auth_token`.

    flow : `str`, keyword-only, optional
        Authorization flow.

        .. container::

           **Valid values**:

           * :code:`"password"` for the password flow.
           * :code:`None` for no authentication.

    browser : `bool`, keyword-only, default: :code:`False`
        Determines whether a web browser is opened with the Qobuz login
        page using the Playwright framework by Microsoft to complete the
        password flow. If :code:`False`, the account email and password
        must be provided in `email` and `password`, respectively.

    user_agent : `str`, keyword-only, optional
        User agent information to send in the header of HTTP requests.

    email : `str`, keyword-only, optional
        Account email address. Required if an user authentication token
        is not provided in `auth_token` and :code:`browser=False`.

    password : `str`, keyword-only, optional
        Account password. Required if an user authentication token is
        not provided in `auth_token` and :code:`browser=False`.

    auth_token : `str`, keyword-only, optional
        User authentication token. If provided here or found in the
        Minim configuration file, the authentication process is
        bypassed.

    overwrite : `bool`, keyword-only, default: :code:`False`
        Determines whether to overwrite an existing user authentication
        token in the Minim configuration file.

    save : `bool`, keyword-only, default: :code:`True`
        Determines whether newly obtained user authentication tokens and
        their associated properties are stored to the Minim
        configuration file.

    Attributes
    ----------
    API_URL : `str`
        URL for the Qobuz API.

    WEB_URL : `str`
        URL for the Qobuz Web Player.
    """

    _FLOWS = {"password"}
    _NAME = f"{__module__}.{__qualname__}"

    API_URL = "https://www.qobuz.com/api.json/0.2"
    WEB_URL = "https://play.qobuz.com"

    def __init__(
        self,
        *,
        app_id: str = None,
        app_secret: str = None,
        flow: str = None,
        browser: bool = False,
        user_agent: str = None,
        email: str = None,
        password: str = None,
        auth_token: str = None,
        overwrite: bool = False,
        save: bool = True,
    ) -> None:
        """
        Create a private Qobuz API client.
        """
        self.session = requests.Session()
        if user_agent:
            self.session.headers["User-Agent"] = user_agent

        if (
            auth_token is None
            and _config.has_section(self._NAME)
            and not overwrite
        ):
            flow = _config.get(self._NAME, "flow") or None
            auth_token = _config.get(self._NAME, "auth_token")
            app_id = _config.get(self._NAME, "app_id")
            app_secret = _config.get(self._NAME, "app_secret")

        self.set_flow(
            flow,
            app_id=app_id,
            app_secret=app_secret,
            auth_token=auth_token,
            browser=browser,
            save=save,
        )
        self.set_auth_token(auth_token, email=email, password=password)

    def _check_authentication(self, endpoint: str) -> None:
        """
        Check if the user is authenticated for the desired endpoint.

        Parameters
        ----------
        endpoint : `str`
            Private Qobuz API endpoint.
        """
        if not self._flow:
            emsg = f"{self._NAME}.{endpoint}() requires user authentication."
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

    def _get_json_secret(self, url: str, signature: str, **kwargs) -> dict:
        """
        Send a GET request with a timestamp and a signature containing
        the app secret, and return the JSON-encoded content of the
        response.

        Parameters
        ----------
        url : `str`
            URL for the GET request.

        signature : `str`
            Signature for the request, up to the timestamp and app secret.

        **kwargs
            Keyword arguments to pass to :meth:`requests.request`.

        Returns
        -------
        resp : `dict`
            JSON-encoded content of the response.
        """
        params = kwargs.pop("params", {})
        timestamp = datetime.datetime.now().timestamp()
        params["request_ts"] = timestamp
        params["request_sig"] = hashlib.md5(
            f"{signature}{timestamp}{self._app_secret}".encode()
        ).hexdigest()
        return self._get_json(url, params=params, **kwargs)

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Construct and send a request with status code checking.

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
        r = self.session.request(method, url, **kwargs)
        if r.status_code not in range(200, 299):
            error = r.json()
            raise RuntimeError(f"{error['code']} {error['message']}")
        return r

    def _set_app_credentials(self, app_id: str, app_secret: str) -> None:
        """
        Set the Qobuz app ID and secret.
        """
        if not app_id or not app_secret:
            js = re.search(
                "/resources/.*/bundle.js",
                self.session.get(f"{self.WEB_URL}/login").text,
            ).group(0)
            bundle = self.session.get(f"{self.WEB_URL}{js}").text
            self.session.headers["X-App-Id"] = re.search(
                '(?:production:{api:{appId:")(.*?)(?:",appSecret)', bundle
            ).group(1)
            app_secrets = [
                base64.b64decode("".join((s, *m.groups()))[:-44]).decode()
                for s, m in (
                    (
                        s,
                        re.search(
                            f'(?:{c.capitalize()}",info:")(.*?)(?:",extras:")'
                            '(.*?)(?:"},{offset)',
                            bundle,
                        ),
                    )
                    for s, c in re.findall(
                        r'(?:[a-z].initialSeed\(")(.*?)'
                        r'(?:",window.utimezone.)(.*?)\)',
                        bundle,
                    )
                )
                if m
            ]
            self._sub = False
            logger = logging.getLogger()
            logging_level = logger.getEffectiveLevel()
            logger.setLevel(logging.CRITICAL)
            for app_secret in app_secrets:
                try:
                    self._app_secret = app_secret
                    self.get_track_file_url(24393138, 5)
                    break
                except RuntimeError:
                    continue
            else:
                raise RuntimeError("No valid app secret could be found.")
            logger.setLevel(logging_level)
        else:
            self._app_secret = app_secret
            self.session.headers["X-App-Id"] = app_id

    def set_auth_token(
        self,
        auth_token: str = None,
        *,
        email: str = None,
        password: str = None,
    ) -> None:
        """
        Set the private Qobuz API user authentication token.

        Parameters
        ----------
        auth_token : `str`, optional
            User authentication token.

        email : `str`, keyword-only, optional
            Account email address.

        password : `str`, keyword-only, optional
            Account password.
        """
        if auth_token is None:
            if not self._flow:
                return

            if self._flow == "password":
                if email is None or password is None:
                    if self._browser:
                        har_file = DIR_TEMP / "minim_qobuz_private.har"

                        with sync_playwright() as playwright:
                            browser = playwright.firefox.launch(headless=False)
                            context = browser.new_context(
                                record_har_path=har_file
                            )
                            page = context.new_page()
                            page.goto(f"{self.WEB_URL}/login", timeout=0)
                            page.wait_for_url(
                                f"{self.WEB_URL}/featured", wait_until="commit"
                            )
                            context.close()
                            browser.close()

                        with open(har_file, "r") as f:
                            regex = re.search(
                                '(?<=")https://www.qobuz.com/api.json/0.2/oauth/callback?(.*)(?=")',
                                f.read(),
                            )
                        har_file.unlink()

                        if regex is None:
                            raise RuntimeError("Authentication failed.")
                        auth_token = self._request(
                            "get", regex.group(0)
                        ).json()["token"]
                    else:
                        emsg = (
                            "No account email or password provided "
                            "for the password flow."
                        )
                        raise ValueError(emsg)
                else:
                    r = self._request(
                        "post",
                        f"{self.API_URL}/user/login",
                        params={"email": email, "password": password},
                    ).json()
                    auth_token = r["user_auth_token"]

            if self._save:
                _config[self._NAME] = {
                    "flow": self._flow,
                    "auth_token": auth_token,
                    "app_id": self.session.headers["X-App-Id"],
                    "app_secret": self._app_secret,
                }
                with open(DIR_HOME / "minim.cfg", "w") as f:
                    _config.write(f)

        self.session.headers["X-User-Auth-Token"] = auth_token

        if self._flow:
            me = self.get_profile()
            self._user_id = me["id"]
            self._sub = (
                me["subscription"] is not None
                and datetime.datetime.now()
                <= datetime.datetime.strptime(
                    me["subscription"]["end_date"], "%Y-%m-%d"
                )
                + datetime.timedelta(days=1)
            )
        else:
            self._sub = None

    def set_flow(
        self,
        flow: str,
        *,
        app_id: str = None,
        app_secret: str = None,
        auth_token: str = None,
        browser: bool = False,
        save: bool = True,
    ) -> None:
        """
        Set the authorization flow.

        Parameters
        ----------
        flow : `str`, keyword-only, optional
            Authorization flow.

            .. container::

               **Valid values**:

               * :code:`"password"` for the password flow.
               * :code:`None` for no authentication.

        app_id : `str`, keyword-only, optional
            App ID. Required if an user authentication token is provided
            in `auth_token`.

        app_secret : `str`, keyword-only, optional
            App secret. Required if an user authentication token is
            provided in `auth_token`.

        auth_token : `str`, keyword-only, optional
            User authentication token.

        browser : `bool`, keyword-only, default: :code:`False`
            Determines whether a web browser is opened with the Qobuz login
            page using the Playwright framework by Microsoft to complete the
            password flow.

        save : `bool`, keyword-only, default: :code:`True`
            Determines whether to save the newly obtained access tokens
            and their associated properties to the Minim configuration
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

        self._browser = browser and FOUND_PLAYWRIGHT
        if self._browser != browser:
            logging.warning(
                "The Playwright web framework was not found, so "
                "user authentication via the Qobuz login page is "
                "unavailable."
            )

        app_id = app_id or os.environ.get("QOBUZ_PRIVATE_APP_ID")
        app_secret = app_secret or os.environ.get("QOBUZ_PRIVATE_APP_SECRET")
        if (app_id is None or app_secret is None) and auth_token is not None:
            emsg = (
                "App credentials are required when an user "
                "authentication token is provided."
            )

        self._set_app_credentials(app_id, app_secret)

    ### ALBUMS ################################################################

    def get_album(
        self,
        album_id: str,
        *,
        extras: Union[str, list[str]] = None,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for a single album.

        Parameters
        ----------
        album_id : `str`
            Qobuz album ID.

            **Example**: :code:`"0060254735180"`.

        extras : `str` or `list`, keyword-only, optional
            Specifies extra information about the album to return.

            **Valid values**: :code:`"albumsFromSameArtist"`,
            :code:`"focus"`, :code:`"focusAll"`.

        limit : `int`, keyword-only, optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`500`.

        offset : `int`, keyword-only, optional
            Index of the first track to return. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        album : `dict`
            Qobuz catalog information for a single album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "maximum_bit_depth": <int>,
                    "image": {
                      "small": <str>,
                      "thumbnail": <str>,
                      "large": <str>,
                      "back": <str>
                    },
                    "media_count": <str>,
                    "artist": {
                      "image": <str>,
                      "name": <str>,
                      "id": <int>,
                      "albums_count": <int>,
                      "slug": <str>,
                      "picture": <str>
                    },
                    "artists": [
                      {
                        "id": <int>,
                        "name": <str>,
                        "roles": [<str>]
                      }
                    ],
                    "upc": <str>,
                    "released_at": <int>,
                    "label": {
                      "name": <str>,
                      "id": <int>,
                      "albums_count": <int>,
                      "supplier_id": <int>,
                      "slug": <str>
                    },
                    "title": <str>,
                    "qobuz_id": <int>,
                    "version": <str>,
                    "url": <str>,
                    "duration": <int>,
                    "parental_warning": <bool>,
                    "popularity": <int>,
                    "tracks_count": <int>,
                    "genre": {
                      "path": [<int>],
                      "color": <str>,
                      "name": <str>,
                      "id": <int>,
                      "slug": <str>
                    },
                    "maximum_channel_count": <int>,
                    "id": <str>,
                    "maximum_sampling_rate": <int>,
                    "articles": <list>,
                    "release_date_original": <str>,
                    "release_date_download": <str>,
                    "release_date_stream": <str>,
                    "purchasable": <bool>,
                    "streamable": <bool>,
                    "previewable": <bool>,
                    "sampleable": <bool>,
                    "downloadable": <bool>,
                    "displayable": <bool>,
                    "purchasable_at": <int>,
                    "streamable_at": <int>,
                    "hires": <bool>,
                    "hires_streamable": <bool>,
                    "awards": <list>,
                    "description": <str>,
                    "description_language": <str>,
                    "goodies": <list>,
                    "area": <str>,
                    "catchline": <str>,
                    "composer": {
                      "id": <int>,
                      "name": <str>,
                      "slug": <str>,
                      "albums_count": <int>,
                      "picture": <str>,
                      "image": <str>
                    },
                    "created_at": <int>,
                    "genres_list": [<str>],
                    "period": <str>,
                    "copyright": <str>,
                    "is_official": <bool>,
                    "maximum_technical_specifications": <str>,
                    "product_sales_factors_monthly": <int>,
                    "product_sales_factors_weekly": <int>,
                    "product_sales_factors_yearly": <int>,
                    "product_type": <str>,
                    "product_url": <str>,
                    "recording_information": <str>,
                    "relative_url": <str>,
                    "release_tags": <list>,
                    "release_type": <str>,
                    "slug": <str>,
                    "subtitle": <str>,
                    "tracks": {
                      "offset": <int>,
                      "limit": <int>,
                      "total": <int>,
                      "items": [
                        {
                          "maximum_bit_depth": <int>,
                          "copyright": <str>,
                          "performers": <str>,
                          "audio_info": {
                            "replaygain_track_peak": <float>,
                            "replaygain_track_gain": <float>
                          },
                          "performer": {
                            "name": <str>,
                            "id": <int>
                          },
                          "work": <str>,
                          "composer": {
                            "name": <str>,
                            "id": <int>
                          },
                          "isrc": <str>,
                          "title": <str>,
                          "version": <str>,
                          "duration": <int>,
                          "parental_warning": <bool>,
                          "track_number": <int>,
                          "maximum_channel_count": <int>,
                          "id": <int>,
                          "media_number": <int>,
                          "maximum_sampling_rate": <int>,
                          "release_date_original": <str>,
                          "release_date_download": <str>,
                          "release_date_stream": <str>,
                          "release_date_purchase": <str>,
                          "purchasable": <bool>,
                          "streamable": <bool>,
                          "previewable": <bool>,
                          "sampleable": <bool>,
                          "downloadable": <bool>,
                          "displayable": <bool>,
                          "purchasable_at": <int>,
                          "streamable_at": <int>,
                          "hires": <bool>,
                          "hires_streamable": <bool>
                        }
                      ]
                    }
                  }
        """
        return self._get_json(
            f"{self.API_URL}/album/get",
            params={
                "album_id": album_id,
                "extra": (
                    extras
                    if extras is None or isinstance(extras, str)
                    else ",".join(extras)
                ),
                "limit": limit,
                "offset": offset,
            },
        )

    def get_featured_albums(
        self,
        type: str = "new-releases",
        *,
        genre_ids: Union[int, str, list[Union[int, str]]] = None,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for featured albums.

        Parameters
        ----------
        type : `str`, default: :code:`"new-releases"`
            Feature type.

            **Valid values**: :code:`"best-sellers"`,
            :code:`"editor-picks"`, :code:`"ideal-discography"`,
            :code:`"most-featured"`, :code:`"most-streamed"`,
            :code:`"new-releases"`, :code:`"new-releases-full"`,
            :code:`"press-awards"`, :code:`"recent-releases"`,
            :code:`"qobuzissims"`, :code:`"harmonia-mundi"`,
            :code:`"universal-classic"`, :code:`"universal-jazz"`,
            :code:`"universal-jeunesse"`, and
            :code:`"universal-chanson"`.

        genre_ids : `int`, `str`, or `list`, optional
            Qobuz IDs of the genres used to filter the featured albums
            to return.

            **Examples**: :code:`10`, :code:`"64"`, :code:`"10,64"`,
            :code:`[10, "64"]`.

        limit : `int`, keyword-only, optional
            The maximum number of albums to return.

            **Default**: :code:`50`.

        offset : `int`, keyword-only, optional
            The index of the first album to return. Use with `limit` to
            get the next page of albums.

            **Default**: :code:`0`.

        Returns
        -------
        albums : `dict`
            Qobuz catalog information for the albums.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albums": {
                      "total": <int>,
                      "limit": <int>,
                      "offset": <int>,
                      "items": [
                        {
                          "maximum_bit_depth": <int>,
                          "image": {
                            "small": <str>,
                            "thumbnail": <str>,
                            "large": <str>,
                            "back": <str>
                          },
                          "media_count": <str>,
                          "artist": {
                            "image": <str>,
                            "name": <str>,
                            "id": <int>,
                            "albums_count": <int>,
                            "slug": <str>,
                            "picture": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "roles": [<str>]
                            }
                          ],
                          "upc": <str>,
                          "released_at": <int>,
                          "label": {
                            "name": <str>,
                            "id": <int>,
                            "albums_count": <int>,
                            "supplier_id": <int>,
                            "slug": <str>
                          },
                          "title": <str>,
                          "qobuz_id": <int>,
                          "version": <str>,
                          "url": <str>,
                          "duration": <int>,
                          "parental_warning": <bool>,
                          "popularity": <int>,
                          "tracks_count": <int>,
                          "genre": {
                            "path": [<int>],
                            "color": <str>,
                            "name": <str>,
                            "id": <int>,
                            "slug": <str>
                          },
                          "maximum_channel_count": <int>,
                          "id": <str>,
                          "maximum_sampling_rate": <int>,
                          "articles": <list>,
                          "release_date_original": <str>,
                          "release_date_download": <str>,
                          "release_date_stream": <str>,
                          "purchasable": <bool>,
                          "streamable": <bool>,
                          "previewable": <bool>,
                          "sampleable": <bool>,
                          "downloadable": <bool>,
                          "displayable": <bool>,
                          "purchasable_at": <int>,
                          "streamable_at": <int>,
                          "hires": <bool>,
                          "hires_streamable": <bool>
                        }
                      ]
                    }
                  }
        """
        if type not in (
            ALBUM_FEATURE_TYPES := {
                "best-sellers",
                "editor-picks",
                "ideal-discography",
                "most-featured",
                "most-streamed",
                "new-releases",
                "new-releases-full",
                "press-awards",
                "recent-releases",
                "qobuzissims",
                "harmonia-mundi",
                "universal-classic",
                "universal-jazz",
                "universal-jeunesse",
                "universal-chanson",
            }
        ):
            emsg = (
                "Invalid feature type. Valid values: "
                f"types are {', '.join(ALBUM_FEATURE_TYPES)}."
            )
            raise ValueError(emsg)

        if genre_ids is not None:
            if isinstance(genre_ids, int):
                genre_ids = str(genre_ids)
            elif isinstance(genre_ids, list):
                genre_ids = ",".join(str(genre_id) for genre_id in genre_ids)
        n = 0 if genre_ids is None else (genre_ids.count(",") + 1)

        return self._get_json(
            f"{self.API_URL}/album/getFeatured",
            params={
                "type": type,
                f"genre_id{'s' if n > 1 else ''}": genre_ids,
                "limit": limit,
                "offset": offset,
            },
        )

    ### ARTISTS ###############################################################

    def get_artist(
        self,
        artist_id: Union[int, str],
        *,
        extras: Union[str, list[str]] = None,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for a single artist.

        Parameters
        ----------
        artist_id : `int` or `str`
            Qobuz artist ID.

        extras : `str` or `list`, keyword-only, optional
            Specifies extra information about the artist to return.

            **Valid values**: :code:`"albums"`, :code:`"tracks"`,
            :code:`"playlists"`, :code:`"tracks_appears_on"`, and
            :code:`"albums_with_last_release"`.

        limit : `int`, keyword-only, optional
            The maximum number of extra items to return. Has no effect
            if :code:`extras=None`.

            **Default**: :code:`25`.

        offset : `int`, keyword-only, optional
            The index of the first extra item to return. Use with
            `limit` to get the next page of extra items. Has no effect
            if :code:`extras=None`.

            **Default**: :code:`0`.

        Returns
        -------
        artist : `dict`
            Qobuz catalog information for a single artist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "name": <str>,
                    "albums_as_primary_artist_count": <int>,
                    "albums_as_primary_composer_count": <int>,
                    "albums_count": <int>,
                    "slug": <str>,
                    "picture": <str>,
                    "image": {
                      "small": <str>,
                      "medium": <str>,
                      "large": <str>,
                      "extralarge": <str>,
                      "mega": <str>
                    },
                    "similar_artist_ids": [<int>],
                    "information": <str>,
                    "biography": {
                      "summary": <str>,
                      "content": <str>,
                      "source": <str>,
                      "language": <str>
                    }
                  }
        """
        return self._get_json(
            f"{self.API_URL}/artist/get",
            params={
                "artist_id": artist_id,
                "extra": (
                    extras
                    if extras is None or isinstance(extras, str)
                    else ",".join(extras)
                ),
                "limit": limit,
                "offset": offset,
            },
        )

    def get_artist_releases(
        self,
        artist_id: Union[int, str],
        *,
        release_types: Union[str, list[str]] = None,
        filters: Union[str, list[str]] = None,
        limit: int = None,
        offset: int = None,
        order: str = None,
        order_direction: str = None,
        include_tracks: bool = False,
        track_limit: int = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for an artist's releases.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        artist_id : `int` or `str`
            Qobuz artist ID.

        release_types : `str` or `list`, keyword-only, optional
            Release types to include in the response.

            **Valid values**: :code:`"all"`, :code:`"album"`,
            :code:`"live"`, :code:`"compilation"`, :code:`"epSingle"`,
            :code:`"other"`, :code:`"download"`, :code:`"composer"`.

        filters : `str` or `list`, keyword-only, optional
            Content filters to apply to the releases.

            **Valid values**: :code:`"hires"`, :code:`"explicit"`.

        limit : `int`, keyword-only, optional
            The maximum number of releases to return.

            **Default**: :code:`50`.

        offset : `int`, keyword-only, optional
            The index of the first release to return. Use with `limit`
            to get the next page of releases.

            **Default**: :code:`0`.

        order : `str`, keyword-only, optional
            Field to sort the releases by.

            **Valid values**: :code:`"relevant"`, :code:`"release_date"`.

        order_direction : `str`, keyword-only, optional
            Order to sort in.

            **Valid values**: :code:`"asc"`, :code:`"desc"`.

        include_tracks : `bool`, keyword-only, default: :code:`False`
            Whether to include tracks in the response.

        track_limit : `int`, keyword-only, optional
            The maximum number of tracks to include per release when
            `include_tracks` is :code:`True`.

            **Default**: :code:`10`.

        Returns
        -------
        releases : `dict`
            Qobuz catalog information for the artist's releases.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "has_more": <bool>,
                    "items": [
                      {
                        "artist": {
                          "id": <int>,
                          "name": {
                            "display": <str>
                          }
                        },
                        "artists": [
                          {
                            "id": <int>,
                            "name": <str>,
                            "roles": <list[str]>
                          }
                        ],
                        "audio_info": {
                          "maximum_bit_depth": <int>,
                          "maximum_channel_count": <int>,
                          "maximum_sampling_rate": <float>
                        },
                        "awards": [],
                        "dates": {
                          "download": <str>,
                          "original": <str>,
                          "stream": <str>,
                        },
                        "duration": <int>,
                        "genre": {
                          "id": <int>,
                          "name": <str>,
                          "path": <list[int]>,
                        },
                        "id": <str>,
                        "image": {
                          "large": <str>,
                          "small": <str>,
                          "thumbnail": <str>
                        },
                        "label": {
                          "id": <int>,
                          "name": <str>
                        },
                        "parental_warning": <bool>,
                        "release_tags": [],
                        "release_type": <str>,
                        "rights": {
                          "downloadable": <bool>,
                          "hires_purchasable": <bool>,
                          "hires_streamable": <bool>,
                          "purchasable": <bool>,
                          "streamable": <bool>
                        },
                        "title": <str>,
                        "tracks": {
                          "has_more": <bool>,
                          "items": [
                            {
                              "artist": {
                                "id": <int>,
                                "name": {
                                  "display": <str>
                                }
                              },
                              "artists": [],
                              "audio_info": {
                                "maximum_bit_depth": <int>,
                                "maximum_channel_count": <int>,
                                "maximum_sampling_rate": <float>
                              },
                              "composer": {
                                "id": <int>,
                                "name": <str>,
                              },
                              "duration": <int>,
                              "id": <int>,
                              "isrc": <str>,
                              "parental_warning": <bool>,
                              "physical_support": {
                                "media_number": <int>,
                                "track_number": <int>
                              },
                              "rights": {
                                "downloadable": <bool>,
                                "hires_purchasable": <bool>,
                                "hires_streamable": <bool>,
                                "previewable": <bool>,
                                "purchasable": <bool>,
                                "sampleable": <bool>,
                                "streamable": <bool>
                              },
                              "title": <str>,
                              "version": <str>,
                              "work": None
                            }
                          ]
                        },
                        "tracks_count": <int>,
                        "version": <str>,
                      }
                    ]
                  }
        """
        self._check_authentication("artists.get_artist_releases")
        params = {
            "artist_id": artist_id,
            "release_type": ",".join(release_types),
            "filter": ",".join(filters),
            "limit": limit,
            "offset": offset,
            "order": order,
            "orderDirection": order_direction,
        }
        if include_tracks:
            params["track_size"] = track_limit
            return self._get_json("artist/getReleasesList", params=params)
        return self._get_json("artist/getReleasesGrid", params=params)

    def get_similar_artists(
        self,
        artist_id: Union[int, str],
        /,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for other artists that are similar
        to an artist.

        Parameters
        ----------
        artist_id : `int` or `str`, positional-only
            Qobuz artist ID

        limit : `int`, keyword-only, optional
            The maximum number of artists to return.

            **Default**: :code:`25`.

        offset : `int`, keyword-only, optional
            The index of the first artist to return. Use with `limit` to
            get the next batch of artists.

            **Default**: :code:`0`.

        Returns
        -------
        artists : `dict`
            Qobuz catalog information for similar artists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "artists": {
                      "items": [
                        {
                          "albums_count": <int>,
                          "id": <int>,
                          "image": {
                            "extralarge": <str>,
                            "large": <str>,
                            "medium": <str>,
                            "mega": <str>,
                            "small": <str>
                          },
                          "name": <str>,
                          "picture": <str>,
                          "slug": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    }
                  }
        """
        return self._get_json(
            "artist/getSimilarArtists",
            params={"artist_id": artist_id, "limit": limit, "offset": offset},
        )

    ### CATALOG ###############################################################

    def count_search_matches(self, query: str) -> dict[str, dict[str, int]]:
        """
        Get the counts of catalog search results for a given query.

        Parameters
        ----------
        query : `str`
            Search query.

        Returns
        -------
        counts : `dict`
            Counts of the search results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albums": {
                      "total": <int>
                    },
                    "artists": {
                      "total": <int>
                    },
                    "tracks": {
                      "total": <int>
                    }
                  }
        """
        if not len(query):
            raise ValueError("No search query provided.")
        return self._get_json("catalog/count", params={"query": query.strip()})

    def get_featured(
        self,
        type: str = None,
        genre_ids: Union[int, str, list[Union[int, str]]] = None,
        *,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for featured albums, artists,
        articles, and/or playlists.

        Parameters
        ----------
        type : `str`, optional
            Type of item to return. If not specified, featured items of
            all types are returned.

            **Valid values**: :code:`"albums"`, :code:`"articles"`,
            :code:`"artists"`, :code:`"playlists"`.

        genre_ids : `int`, `str`, or `list`, optional
            Qobuz IDs of the genres used to filter the featured items to
            return.

            **Examples**: :code:`10`, :code:`"64"`, :code:`"10,64"`,
            :code:`[10, "64"]`.

        limit : `int`, keyword-only, optional
            The maximum number of items to return per item type.

            **Default**: :code:`25`.

        offset : `int`, keyword-only, optional
            The index of the first item to return per item type. Use
            with `limit` to get the next page of items.

            **Default**: :code:`0`.

        Returns
        -------
        items : `dict`
            Qobuz catalog information for the featured items.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albums": {
                      "items": [
                        {
                          "articles": [],
                          "artist": {
                            "albums_count": <int>,
                            "id": <int>,
                            "image": None,
                            "name": <str>,
                            "picture": None,
                            "slug": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "roles": <list[str]>
                            }
                          ],
                          "displayable": <bool>,
                          "downloadable": <bool>,
                          "duration": <int>,
                          "genre": {
                            "color": <str>,
                            "id": <int>,
                            "name": <str>,
                            "path": <list[int]>,
                            "slug": <str>
                          },
                          "hires": <bool>,
                          "hires_streamable": <bool>,
                          "id": <str>,
                          "image": {
                            "back": None,
                            "large": <str>,
                            "small": <str>,
                            "thumbnail": <str>
                          },
                          "label": {
                            "albums_count": <int>,
                            "id": <int>,
                            "name": <str>,
                            "slug": <str>,
                            "supplier_id": <int>
                          },
                          "maximum_bit_depth": <int>,
                          "maximum_channel_count": <int>,
                          "maximum_sampling_rate": <float>,
                          "media_count": <int>,
                          "parental_warning": <bool>,
                          "popularity": <int>,
                          "previewable": <bool>,
                          "purchasable": <bool>,
                          "purchasable_at": <int>,
                          "qobuz_id": <int>,
                          "release_date_download": <str>,
                          "release_date_original": <str>,
                          "release_date_stream": <str>,
                          "released_at": <int>,
                          "sampleable": <bool>,
                          "slug": <str>,
                          "streamable": <bool>,
                          "streamable_at": <int>,
                          "title": <str>,
                          "tracks_count": <int>,
                          "upc": <str>,
                          "url": <str>,
                          "version": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "artists": {
                      "items": [
                        {
                          "albums_count": <int>,
                          "id": <int>,
                          "image": {
                            "extralarge": <str>,
                            "large": <str>,
                            "medium": <str>,
                            "mega": <str>,
                            "small": <str>
                          },
                          "name": <str>,
                          "picture": <str>,
                          "slug": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "playlists": {
                      "items": [
                        {
                          "created_at": <int>,
                          "description": <str>,
                          "duration": <int>,
                          "featured_artists": [],
                          "genres": [
                            {
                              "color": <str>,
                              "id": <int>,
                              "name": <str>,
                              "path": <list[int]>,
                              "percent": <int>,
                              "slug": <str>
                            }
                          ],
                          "id": <int>,
                          "image_rectangle": <list[str]>,
                          "image_rectangle_mini": <list[str]>,
                          "images": <list[str]>,
                          "images150": <list[str]>,
                          "images300": <list[str]>,
                          "is_collaborative": <bool>,
                          "is_featured": <bool>,
                          "is_public": <bool>,
                          "name": <str>,
                          "owner": {
                            "id": <int>,
                            "name": <str>
                          },
                          "public_at": <int>,
                          "slug": <str>,
                          "stores": <list[str]>,
                          "tags": [
                            {
                              "color": <str>,
                              "featured_tag_id": <str>,
                              "genre_tag": None,
                              "is_discover": <bool>,
                              "name_json": <str>,
                              "slug": <str>
                            }
                          ],
                          "tracks_count": <int>,
                          "updated_at": <int>,
                          "users_count": <int>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    }
                  }
        """
        return self._get_json(
            "GET",
            "catalog/getFeatured",
            params={
                "type": type,
                "genre_ids": genre_ids
                if isinstance(genre_ids, (int, str))
                else ",".join(str(genre_id) for genre_id in genre_ids),
                "limit": limit,
                "offset": offset,
            },
        )

    ### DYNAMIC TRACKS ########################################################

    def get_curated_tracks(self) -> list[dict[str, Any]]:
        """
        Get weekly curated tracks for the user.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            The maximum number of tracks to return.

            **Default**: :code:`50`.

        offset : `int`, keyword-only, optional
            The index of the first track to return. Use with `limit`
            to get the next page of tracks.

            **Default**: :code:`0`.

        Returns
        -------
        tracks : `list`
            Qobuz catalog information for the curated tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "title": <str>,
                    "baseline": <str>,
                    "description": <str>,
                    "type": "weekly",
                    "step_pagination": <int>,
                    "images": {
                      "small": <str>,
                      "large": <str>
                    },
                    "graphics": {
                      "background": <str>,
                      "foreground": <str>
                    },
                    "duration": <int>,
                    "generated_at": <int>,
                    "expires_on": <int>,
                    "track_count": <int>,
                    "tracks": {
                      "offset": <int>,
                      "limit": <int>,
                      "items": [
                        {
                          "maximum_bit_depth": <int>,
                          "copyright": <str>,
                          "performers": <str>,
                          "audio_info": {
                            "replaygain_track_peak": <float>,
                            "replaygain_track_gain": <float>
                          },
                          "performer": {
                            "name": <str>,
                            "id": <int>
                          },
                          "album": {
                            "image": {
                              "small": <str>,
                              "thumbnail": <str>,
                              "large": <str>
                            },
                            "maximum_bit_depth": <int>,
                            "media_count": <int>,
                            "artist": {
                              "image": <str>,
                              "name": <str>,
                              "id": <int>,
                              "albums_count": <int>,
                              "slug":<str>,
                              "picture": <str>
                            },
                            "upc": <str>,
                            "released_at": <int>,
                            "label": {
                              "name": <str>,
                              "id": <int>,
                              "albums_count": <int>,
                              "supplier_id": <int>,
                              "slug": <str>
                            },
                            "title": <str>,
                            "qobuz_id": <int>,
                            "version": <str>,
                            "duration": <int>,
                            "parental_warning": <bool>,
                            "tracks_count": <int>,
                            "popularity": <int>,
                            "genre": {
                              "path": [<int>],
                              "color": <str>,
                              "name": <str>,
                              "id": <int>,
                              "slug": <str>
                            },
                            "maximum_channel_count": <int>,
                            "id": <str>,
                            "maximum_sampling_rate": <int>,
                            "previewable": <bool>,
                            "sampleable": <bool>,
                            "displayable": <bool>,
                            "streamable": <bool>,
                            "streamable_at": <int>,
                            "downloadable": <bool>,
                            "purchasable_at": <int>,
                            "purchasable": <bool>,
                            "release_date_original": <str>,
                            "release_date_download": <str>,
                            "release_date_stream": <str>,
                            "release_date_purchase": <str>,
                            "hires": <bool>,
                            "hires_streamable": <bool>
                          },
                          "work": <str>,
                          "composer": {
                            "name": <str>,
                            "id": <int>
                          },
                          "isrc": <str>,
                          "title": <str>,
                          "version": <str>,
                          "duration": <int>,
                          "parental_warning": <bool>,
                          "track_number": <int>,
                          "maximum_channel_count": <int>,
                          "id": <int>,
                          "media_number": <int>,
                          "maximum_sampling_rate": <int>,
                          "release_date_original": <str>,
                          "release_date_download": <str>,
                          "release_date_stream": <str>,
                          "release_date_purchase": <str>,
                          "purchasable": <bool>,
                          "streamable": <bool>,
                          "previewable": <bool>,
                          "sampleable": <bool>,
                          "downloadable": <bool>,
                          "displayable": <bool>,
                          "purchasable_at": <int>,
                          "streamable_at": <int>,
                          "hires": <bool>,
                          "hires_streamable": <bool>
                        }
                      ]
                    }
                  }
        """

        self._check_authentication("get_curated_tracks")

        return self._get_json(
            f"{self.API_URL}/dynamic-tracks/get", params={"type": "weekly"}
        )

    # TODO

    ### FAVORITES #############################################################

    def get_favorites(
        self, type: str = None, *, limit: int = None, offset: int = None
    ) -> dict[str, dict]:
        """
        Get the current user's favorite albums, artists, and tracks.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        type : `str`
            Media type to return. If not specified, all of the user's
            favorite items are returned.

            .. container::

               **Valid values**: :code:`"albums"`, :code:`"artists"`,
               and :code:`"tracks"`.

        limit : `int`, keyword-only, optional
            The maximum number of favorited items to return.

            **Default**: :code:`50`.

        offset : `int`, keyword-only, optional
            The index of the first favorited item to return. Use with
            `limit` to get the next page of favorited items.

            **Default**: :code:`0`.

        Returns
        -------
        favorites : `dict`
            A dictionary containing Qobuz catalog information for the
            current user's favorite items and the user's ID and email.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albums": {
                      "offset": <int>,
                      "limit": <int>,
                      "total": <int>,
                      "items": <list>
                    },
                    "user": {
                      "id": <int>,
                      "login": <str>
                    }
                  }
        """
        self._check_authentication("get_favorites")

        if type and type not in (
            MEDIA_TYPES := {"albums", "artists", "tracks"}
        ):
            emsg = (
                f"Invalid media type. Valid values: {', '.join(MEDIA_TYPES)}."
            )
            raise ValueError(emsg)

        return self._get_json_secret(
            f"{self.API_URL}/favorite/getUserFavorites",
            "favoritegetUserFavorites",
            params={"type": type, "limit": limit, "offset": offset},
        )

    def get_favorite_ids(self) -> dict[str, Any]:
        """
        Get Qobuz IDs of the items in the current user's favorites.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Returns
        -------
        saved_ids : `dict`
            Qobuz IDs of the items in the user's favorites.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albums": <list[str]>,
                    "articles": [],
                    "artists": <list[int]>,
                    "awards": [],
                    "labels": [],
                    "tracks": <list[int]>,
                  }
        """
        self._check_authentication("get_favorite_ids")
        return self._get_json(f"{self.API_URL}/favorite/getUserFavoriteIds")

    def favorite_items(
        self,
        *,
        album_ids: Union[str, list[str]] = None,
        artist_ids: Union[int, str, list[Union[int, str]]] = None,
        track_ids: Union[int, str, list[Union[int, str]]] = None,
    ) -> None:
        """
        Favorite albums, artists, and/or tracks.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        .. seealso::

           For playlists, use :meth:`favorite_playlist`.

        Parameters
        ----------
        album_ids : `str` or `list`, keyword-only, optional
            Qobuz album ID(s).

        artist_ids : `int`, `str`, or `list`, keyword-only, optional
            Qobuz artist ID(s).

        track_ids : `int`, `str`, or `list`, keyword-only, optional
            Qobuz track ID(s).
        """
        self._check_authentication("favorite_items")

        data = {}
        if album_ids:
            data["album_ids"] = (
                ",".join(str(a) for a in album_ids)
                if isinstance(album_ids, list)
                else album_ids
            )
        if artist_ids:
            data["artist_ids"] = (
                ",".join(str(a) for a in artist_ids)
                if isinstance(artist_ids, list)
                else artist_ids
            )
        if track_ids:
            data["track_ids"] = (
                ",".join(str(a) for a in track_ids)
                if isinstance(track_ids, list)
                else track_ids
            )
        self._request("post", f"{self.API_URL}/favorite/create", data=data)

    def unfavorite_items(
        self,
        *,
        album_ids: Union[str, list[str]] = None,
        artist_ids: Union[int, str, list[Union[int, str]]] = None,
        track_ids: Union[int, str, list[Union[int, str]]] = None,
    ) -> None:
        """
        Unfavorite albums, artists, and/or tracks.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        .. seealso::

           For playlists, use :meth:`unfavorite_playlist`.

        Parameters
        ----------
        album_ids : `str` or `list`, keyword-only, optional
            Qobuz album ID(s).

        artist_ids : `int`, `str`, or `list`, keyword-only, optional
            Qobuz artist ID(s).

        track_ids : `int`, `str`, or `list`, keyword-only, optional
            Qobuz track ID(s).
        """
        self._check_authentication("unfavorite_items")

        data = {}
        if album_ids:
            data["album_ids"] = (
                ",".join(str(a) for a in album_ids)
                if isinstance(album_ids, list)
                else album_ids
            )
        if artist_ids:
            data["artist_ids"] = (
                ",".join(str(a) for a in artist_ids)
                if isinstance(artist_ids, list)
                else artist_ids
            )
        if track_ids:
            data["track_ids"] = (
                ",".join(str(a) for a in track_ids)
                if isinstance(track_ids, list)
                else track_ids
            )
        self._request("post", f"{self.API_URL}/favorite/delete", data=data)

    def check_favorite(
        self, type: str, item_id: Union[int, str]
    ) -> dict[str, bool]:
        """
        Check whether an item is in the current user's favorites.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        type : `str`
            Type of item.

            **Valid values**: :code:`"album"`, :code:`"artist"`,
            :code:`"article"`, :code:`"award"`, :code:`"label"`,
            :code:`"track"`.

        item_id : `int` or `str`
            Qobuz ID of the item.

        Returns
        -------
        saved : `dict`
            Whether the current user has the specified item in their
            favorites.

            **Sample response**: :code:`{"status": <bool>}`.
        """
        self._check_authentication("check_favorite")

        if f"{type}s" not in (
            _FAVORITE_TYPES := {
                "albums",
                "artists",
                "articles",
                "awards",
                "labels",
                "tracks",
            }
        ):
            favorite_types = "', '".join(ft[:-1] for ft in _FAVORITE_TYPES)
            raise ValueError(
                f"Invalid type {type!r}. Valid values: '{favorite_types}'."
            )
        return self._get_json(
            f"{self.API_URL}/favorite/status",
            params={"type": type, "item_id": item_id},
        )

    def toggle_favorited(
        self, type: str, item_id: Union[int, str]
    ) -> dict[str, bool]:
        """
        Toggle the favorited status of an item.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        type : `str`
            Type of item.

            **Valid values**: :code:`"album"`, :code:`"artist"`,
            :code:`"article"`, :code:`"award"`, :code:`"label"`,
            :code:`"track"`.

        item_id : `int` or `str`
            Qobuz ID of the item.

        Returns
        -------
        saved : dict[str, bool]
            Whether the current user has the specified item in their
            favorites.

            **Sample response**: :code:`{"status": <bool>}`.
        """
        self._check_authentication("toggle_favorited")

        if f"{type}s" not in (
            _FAVORITE_TYPES := {
                "albums",
                "artists",
                "articles",
                "awards",
                "labels",
                "tracks",
            }
        ):
            favorite_types = "', '".join(ft[:-1] for ft in _FAVORITE_TYPES)
            raise ValueError(
                f"Invalid type {type!r}. Valid values: '{favorite_types}'."
            )
        return self._request(
            "POST",
            f"{self.API_URL}/favorite/toggle",
            params={"type": type, "item_id": item_id},
        ).json()

    ### GENRES ################################################################

    # TODO

    ### LABELS ################################################################

    def get_label(
        self,
        label_id: Union[int, str],
        *,
        extras: Union[str, list[str]] = None,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for a record label.

        Parameters
        ----------
        label_id : `int` or `str`
            Qobuz record label ID.

            **Example**: :code:`1153`.

        extras : `str` or `list`, keyword-only, optional
            Related resources to include metadata for in the response.

            **Valid values**: :code:`"albums"`, :code:`"focus"`,
            :code:`"focusAll"`.

        limit : `int`, keyword-only, optional
            The maximum number of albums to return. Has no effect if
            :code:`albums=False`.

            **Default**: :code:`25`.

        offset : `int`, keyword-only, optional
            The index of the first album to return. Use with `limit` to
            get the next page of albums. Has no effect if
            :code:`albums=False`.

            **Default**: :code:`0`.

        Returns
        -------
        label : `dict`
            Qobuz catalog information for the record label.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "name": <str>,
                    "slug": <str>,
                    "supplier_id": <int>,
                    "albums_count": <int>,
                    "image": <str>,
                    "description": <str>
                  }
        """

        return self._get_json(
            f"{self.API_URL}/label/get",
            params={
                "label_id": label_id,
                "extra": (
                    extras
                    if extras is None or isinstance(extras, str)
                    else ",".join(extras)
                ),
                "limit": limit,
                "offset": offset,
            },
        )

    def get_labels(
        self, *, limit: int = None, offset: int = None
    ) -> dict[str, Any]:
        """
        Get available labels.

        Parameters
        ----------
        limit : int; keyword-only; optional
            The maximum number of labels to return.

            **Default**: :code:`25`.

        offset : int; keyword-only; optional
            The index of the first label to return. Use with `limit` to
            get the next page of labels.

            **Default**: :code:`0`.

        Returns
        -------
        labels : dict[str, Any]
            Qobuz catalog information for the labels.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "labels": {
                      "items": [
                        {
                          "albums_count": <int>,
                          "id": <int>,
                          "name": <str>,
                          "slug": <str>,
                          "supplier_id": <int>,
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    }
                  }
        """
        return self._get_json(
            f"{self.API_URL}/label/list",
            params={"limit": limit, "offset": offset},
        )

    ### PLAYLISTS #############################################################

    def get_playlist(
        self,
        playlist_id: Union[int, str],
        *,
        tracks: bool = True,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for a playlist.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz playlist ID.

            **Example**: :code:`15732665`.

        tracks : `bool`, keyword-only, default: :code:`True`
            Specifies whether information on the tracks in the playlist
            is returned.

        limit : `int`, keyword-only, optional
            The maximum number of tracks to return. Has no effect if
            :code:`tracks=False`.

            **Default**: :code:`50`.

        offset : `int`, keyword-only, optional
            The index of the first track to return. Use with `limit` to
            get the next page of tracks. Has no effect if
            :code:`tracks=False`.

            **Default**: :code:`0`.

        Returns
        -------
        playlist : `dict`
            Qobuz catalog information for the playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "image_rectangle_mini": [<str>],
                    "featured_artists": <list>,
                    "description": <str>,
                    "created_at": <int>,
                    "timestamp_position": <int>,
                    "images300": [<str>],
                    "duration": <int>,
                    "updated_at": <int>,
                    "genres": [
                      {
                        "id": <int>,
                        "color": <str>,
                        "name": <str>,
                        "path": [<int>],
                        "slug": <str>,
                        "percent": <float>
                      }
                    ],
                    "image_rectangle": [<str>],
                    "id": <int>,
                    "slug": <str>,
                    "owner": {
                      "id": <int>,
                      "name": <str>
                    },
                    "users_count": <int>,
                    "images150": [<str>],
                    "images": [<str>],
                    "is_collaborative": <bool>,
                    "stores": [<str>],
                    "tags": [
                      {
                        "featured_tag_id": <str>,
                        "name_json": <str>,
                        "slug": <str>,
                        "color": <str>,
                        "genre_tag": <str>,
                        "is_discover": <bool>
                      }
                    ],
                    "tracks_count": <int>,
                    "public_at": <int>,
                    "name": <str>,
                    "is_public": <bool>,
                    "is_featured": <bool>,
                    "tracks": {
                      "offset": <int>,
                      "limit": <int>,
                      "total": <int>,
                      "items": [
                        {
                          "maximum_bit_depth": <int>,
                          "copyright": <str>,
                          "performers": <str>,
                          "audio_info": {
                            "replaygain_track_peak": <float>,
                            "replaygain_track_gain": <float>
                          },
                          "performer": {
                            "name": <str>,
                            "id": <int>
                          },
                          "album": {
                            "image": {
                              "small": <str>,
                              "thumbnail": <str>,
                              "large": <str>
                            },
                            "maximum_bit_depth": <int>,
                            "media_count": <int>,
                            "artist": {
                              "image": <str>,
                              "name": <str>,
                              "id": <int>,
                              "albums_count": <int>,
                              "slug": <str>,
                              "picture": <str>
                            },
                            "upc": <str>,
                            "released_at": <int>,
                            "label": {
                              "name": <str>,
                              "id": <int>,
                              "albums_count": <int>,
                              "supplier_id": <int>,
                              "slug": <str>
                            },
                            "title": <str>,
                            "qobuz_id": <int>,
                            "version": <str>,
                            "duration": <int>,
                            "parental_warning": <bool>,
                            "tracks_count": <int>,
                            "popularity": <int>,
                            "genre": {
                              "path": [<int>],
                              "color": <str>,
                              "name": <str>,
                              "id": <int>,
                              "slug": <str>
                            },
                            "maximum_channel_count": <int>,
                            "id": <str>,
                            "maximum_sampling_rate": <int>,
                            "previewable": <bool>,
                            "sampleable": <bool>,
                            "displayable": <bool>,
                            "streamable": <bool>,
                            "streamable_at": <int>,
                            "downloadable": <bool>,
                            "purchasable_at": <int>,
                            "purchasable": <bool>,
                            "release_date_original": <str>,
                            "release_date_download": <str>,
                            "release_date_stream": <str>,
                            "release_date_purchase": <str>,
                            "hires": <bool>,
                            "hires_streamable": <bool>
                          },
                          "work": <str>,
                          "isrc": <str>,
                          "title": <str>,
                          "version": null,
                          "duration": <int>,
                          "parental_warning": <bool>,
                          "track_number": <int>,
                          "maximum_channel_count": <int>,
                          "id": <int>,
                          "media_number": <int>,
                          "maximum_sampling_rate": <int>,
                          "release_date_original": <str>,
                          "release_date_download": <str>,
                          "release_date_stream": <str>,
                          "release_date_purchase": <str>,
                          "purchasable": <bool>,
                          "streamable": <bool>,
                          "previewable": <bool>,
                          "sampleable": <bool>,
                          "downloadable": <bool>,
                          "displayable": <bool>,
                          "purchasable_at": <int>,
                          "streamable_at": <int>,
                          "hires": <bool>,
                          "hires_streamable": <bool>,
                          "position": <int>,
                          "created_at": <int>,
                          "playlist_track_id": <int>
                        }
                      ]
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/playlist/get",
            params={
                "playlist_id": playlist_id,
                "extra": "tracks" if tracks else None,
                "limit": limit,
                "offset": offset,
            },
        )

    def get_featured_playlists(
        self,
        type: str = "editor-picks",
        *,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for featured playlists.

        Parameters
        ----------
        type : `str`, default: :code:`"editor-picks"`
            Feature type.

            **Valid values**: :code:`"editor-picks"` and
            :code:`"last-created"`.

        limit : `int`, keyword-only, optional
            The maximum number of playlists to return.

            **Default**: :code:`50`.

        offset : `int`, keyword-only, optional
            The index of the first playlist to return. Use with `limit`
            to get the next page of playlists.

            **Default**: :code:`0`.

        Returns
        -------
        playlists : `dict`
            Qobuz catalog information for the playlists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "offset": <int>,
                    "limit": <int>,
                    "total": <int>,
                    "items": [
                      {
                        "owner": {
                          "name": <str>,
                          "id": <int>
                        },
                        "image_rectangle_mini": [<str>],
                        "users_count": <int>,
                        "images150": [<str>],
                        "images": [<str>],
                        "featured_artists": <list>,
                        "is_collaborative": <bool>,
                        "stores": [<str>],
                        "description": <str>,
                        "created_at": <int>,
                        "images300": [<str>],
                        "tags": [
                          {
                            "color": <str>,
                            "is_discover": <bool>,
                            "featured_tag_id": <str>,
                            "name_json": <str>,
                            "slug": <str>,
                            "genre_tag": <str>
                          }
                        ],
                        "duration": <int>,
                        "updated_at": <int>,
                        "genres": [
                          {
                            "path": [<int>],
                            "color": <str>,
                            "name": <str>,
                            "id": <int>,
                            "percent": <float>,
                            "slug": <str>
                          }
                        ],
                        "image_rectangle": [<str>],
                        "tracks_count": <int>,
                        "public_at": <int>,
                        "name": <str>,
                        "is_public": <bool>,
                        "id": <int>,
                        "slug": <str>,
                        "is_featured": <bool>
                      }
                    ]
                  }
        """

        if type not in (
            PLAYLIST_FEATURE_TYPES := {"editor-picks", "last-created"}
        ):
            emsg = (
                "Invalid feature type. Valid types: "
                f"{', '.join(PLAYLIST_FEATURE_TYPES)}."
            )
            raise ValueError(emsg)

        return self._get_json(
            f"{self.API_URL}/playlist/getFeatured",
            params={"type": type, "limit": limit, "offset": offset},
        )["playlists"]

    def get_user_playlists(
        self, *, limit: int = None, offset: int = None
    ) -> dict[str, Any]:
        """
        Get the current user's custom and favorite playlists.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            The maximum number of playlists to return.

            **Default**: :code:`500`.

        offset : `int`, keyword-only, optional
            The index of the first playlist to return. Use with `limit`
            to get the next page of playlists.

            **Default**: :code:`0`.

        Returns
        -------
        playlists : `dict`
            Qobuz catalog information for the current user's custom and
            favorite playlists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "offset": <int>,
                    "limit": <int>,
                    "total": <int>,
                    "items": [
                      {
                        "image_rectangle_mini": [<str>],
                        "is_published": <bool>,
                        "featured_artists": <list>,
                        "description": <str>,
                        "created_at": <int>,
                        "timestamp_position": <int>,
                        "images300": [<str>],
                        "duration": <int>,
                        "updated_at": <int>,
                        "published_to": <int>,
                        "genres": <list>,
                        "image_rectangle": [<str>],
                        "id": <int>,
                        "slug": <str>,
                        "owner": {
                          "id": <int>,
                          "name": <str>
                        },
                        "users_count": <int>,
                        "images150": [<str>],
                        "images": [<str>],
                        "is_collaborative": <bool>.
                        "stores": [<str>],
                        "tracks_count": <int>,
                        "public_at": <int>,
                        "name": "Welcome to Qobuz",
                        "is_public": <bool>,
                        "published_from": <int>,
                        "is_featured": <bool>,
                        "position": <int>
                      }
                    ]
                  }
        """

        self._check_authentication("get_user_playlists")

        return self._get_json(
            f"{self.API_URL}/playlist/getUserPlaylists",
            params={"limit": limit, "offset": offset},
        )["playlists"]

    def create_playlist(
        self,
        name: str,
        *,
        description: str = None,
        public: bool = True,
        collaborative: bool = False,
    ) -> dict[str, Any]:
        """
        Create a user playlist.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        name : `str`
            Qobuz playlist name.

        description : `str`, keyword-only, optional
            Brief playlist description.

        public : `bool`, keyword-only, default: :code:`True`
            Determines whether the playlist is public (:code:`True`) or
            private (:code:`False`).

        collaborative : `bool`, keyword-only, default: :code:`False`
            Determines whether the playlist is collaborative.

        Returns
        -------
        playlist : `str`
            Qobuz catalog information for the newly created playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "name": <str>,
                    "description": <str>,
                    "tracks_count": <int>,
                    "users_count": <int>,
                    "duration": <int>,
                    "public_at": <int>,
                    "created_at": <int>,
                    "updated_at": <int>,
                    "is_public": <bool>,
                    "is_collaborative": <bool>,
                    "owner": {
                      "id": <int>,
                      "name": <str>
                    }
                  }
        """

        self._check_authentication("create_playlist")

        data = {
            "name": name,
            "is_public": str(public).lower(),
            "is_collaborative": str(collaborative).lower(),
        }
        if description:
            data["description"] = description
        return self._request(
            "post", f"{self.API_URL}/playlist/create", data=data
        ).json()

    def update_playlist(
        self,
        playlist_id: Union[int, str],
        *,
        name: str = None,
        description: str = None,
        public: bool = None,
        collaborative: bool = None,
    ) -> dict[str, Any]:
        """
        Update the title, description, and/or privacy of a playlist
        owned by the current user.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz user playlist ID.

            **Example**: :code:`17737508`.

        name : `str`, keyword-only, optional
            Qobuz playlist name.

        description : `str`, keyword-only, optional
            Brief playlist description.

        public : `bool`, keyword-only, optional
            Determines whether the playlist is public (:code:`True`) or
            private (:code:`False`).

        collaborative : `bool`, keyword-only, optional
            Determines whether the playlist is collaborative.

        Returns
        -------
        playlist : `str`
            Qobuz catalog information for the updated playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "name": <str>,
                    "description": <str>,
                    "tracks_count": <int>,
                    "users_count": <int>,
                    "duration": <int>,
                    "public_at": <int>,
                    "created_at": <int>,
                    "updated_at": <int>,
                    "is_public": <bool>,
                    "is_collaborative": <bool>,
                    "owner": {
                      "id": <int>,
                      "name": <str>
                    }
                  }
        """

        self._check_authentication("update_playlist")

        data = {"playlist_id": playlist_id}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if public is not None:
            data["is_public"] = str(public).lower()
        if collaborative is not None:
            data["is_collaborative"] = str(collaborative).lower()
        return self._request(
            "post", f"{self.API_URL}/playlist/update", data=data
        ).json()

    def update_playlist_position(
        self,
        from_playlist_id: Union[int, str],
        to_playlist_id: Union[int, str],
    ) -> None:
        """
        Organize a user's playlists.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        from_playlist_id : `int` or `str`
            Qobuz user playlist ID of playlist to move.

            **Example**: :code:`17737508`.

        to_playlist_id : `int` or `str`
            Qobuz user playlist ID of playlist to swap with that in
            `from_playlist_id`.

            **Example**: :code:`17737509`.
        """

        self._check_authentication("update_playlist_position")

        self._request(
            "post",
            f"{self.API_URL}/playlist/updatePlaylistsPosition",
            data={"playlist_ids": [from_playlist_id, to_playlist_id]},
        )

    def add_playlist_tracks(
        self,
        playlist_id: Union[int, str],
        track_ids: Union[int, str, list[Union[int, str]]],
        *,
        duplicate: bool = False,
    ) -> dict[str, Any]:
        """
        Add tracks to a user playlist.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz user playlist ID.

            **Example**: :code:`17737508`.

        track_ids : `int`, `str`, or `list`
            Qobuz track ID(s).

            **Examples**: :code:`"24393122,24393138"` or
            :code:`[24393122, 24393138]`.

        duplicate : `bool`, keyword-only, default: :code:`False`
            Determines whether duplicate tracks should be added to the
            playlist.

        Returns
        -------
        playlist : `str`
            Qobuz catalog information for the updated playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "name": <str>,
                    "description": <str>,
                    "tracks_count": <int>,
                    "users_count": <int>,
                    "duration": <int>,
                    "public_at": <int>,
                    "created_at": <int>,
                    "updated_at": <int>,
                    "is_public": <bool>,
                    "is_collaborative": <bool>,
                    "owner": {
                      "id": <int>,
                      "name": <str>
                    }
                  }
        """

        self._check_authentication("add_playlist_tracks")

        if isinstance(track_ids, list):
            track_ids = ",".join(str(t) for t in track_ids)
        return self._request(
            "post",
            f"{self.API_URL}/playlist/addTracks",
            data={
                "playlist_id": playlist_id,
                "track_ids": track_ids,
                "no_duplicate": str(not duplicate).lower(),
            },
        ).json()

    def move_playlist_tracks(
        self,
        playlist_id: Union[int, str],
        playlist_track_ids: Union[int, str, list[Union[int, str]]],
        insert_before: int,
    ) -> dict[str, Any]:
        """
        Move tracks in a user playlist.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz user playlist ID.

            **Example**: :code:`17737508`.

        playlist_track_ids : `int`, `str`, or `list`
            Qobuz playlist track ID(s).

            .. note::

               Playlist track IDs are not the same as track IDs. To get
               playlist track IDs, use :meth:`get_playlist`.

        insert_before : `int`
            Position to which to move the tracks specified in
            `track_ids`.

        Returns
        -------
        playlist : `str`
            Qobuz catalog information for the updated playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "name": <str>,
                    "description": <str>,
                    "tracks_count": <int>,
                    "users_count": <int>,
                    "duration": <int>,
                    "public_at": <int>,
                    "created_at": <int>,
                    "updated_at": <int>,
                    "is_public": <bool>,
                    "is_collaborative": <bool>,
                    "owner": {
                      "id": <int>,
                      "name": <str>
                    }
                  }
        """

        self._check_authentication("move_playlist_tracks")

        if isinstance(playlist_track_ids, list):
            playlist_track_ids = ",".join(str(t) for t in playlist_track_ids)
        return self._request(
            "post",
            f"{self.API_URL}/playlist/updateTracksPosition",
            data={
                "playlist_id": playlist_id,
                "playlist_track_ids": playlist_track_ids,
                "insert_before": insert_before,
            },
        ).json()

    def delete_playlist_tracks(
        self,
        playlist_id: Union[int, str],
        playlist_track_ids: Union[int, str, list[Union[int, str]]],
    ) -> dict[str, Any]:
        """
        Delete tracks from a user playlist.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz user playlist ID.

            **Example**: :code:`17737508`.

        playlist_track_ids : `int`, `str`, or `list`
            Qobuz playlist track ID(s).

            .. note::

               Playlist track IDs are not the same as track IDs. To get
               playlist track IDs, use :meth:`get_playlist`.

        Returns
        -------
        playlist : `str`
            Qobuz catalog information for the updated playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "name": <str>,
                    "description": <str>,
                    "tracks_count": <int>,
                    "users_count": <int>,
                    "duration": <int>,
                    "public_at": <int>,
                    "created_at": <int>,
                    "updated_at": <int>,
                    "is_public": <bool>,
                    "is_collaborative": <bool>,
                    "owner": {
                      "id": <int>,
                      "name": <str>
                    }
                  }
        """

        self._check_authentication("delete_playlist_tracks")

        if isinstance(playlist_track_ids, list):
            playlist_track_ids = ",".join(str(t) for t in playlist_track_ids)

        return self._request(
            "post",
            f"{self.API_URL}/playlist/deleteTracks",
            data={
                "playlist_id": playlist_id,
                "playlist_track_ids": playlist_track_ids,
            },
        ).json()

    def delete_playlist(self, playlist_id: Union[int, str]) -> None:
        """
        Delete a user playlist.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz user playlist ID.

            **Example**: :code:`17737508`.
        """

        self._check_authentication("delete_playlist")

        self._request(
            "post",
            f"{self.API_URL}/playlist/delete",
            data={"playlist_id": playlist_id},
        )

    def favorite_playlist(self, playlist_id: Union[int, str]) -> None:
        """
        Subscribe to a playlist.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz playlist ID.

            **Example**: :code:`15732665`.
        """

        self._check_authentication("favorite_playlist")

        self._request(
            "post",
            f"{self.API_URL}/playlist/subscribe",
            data={"playlist_id": playlist_id},
        )

    def unfavorite_playlist(self, playlist_id: Union[int, str]) -> None:
        """
        Unsubscribe from a playlist.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz playlist ID.

            **Example**: :code:`15732665`.
        """

        self._check_authentication("unfavorite_playlist")

        self._request(
            "post",
            f"{self.API_URL}/playlist/unsubscribe",
            data={"playlist_id": playlist_id},
        )

    def get_playlist_tags(self) -> dict[str, list[dict[str, Any]]]:
        """
        Get available playlist tags.

        Returns
        -------
        playlist_tags : `dict`
            Qobuz catalog information for playlist tags.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "tags": [
                      {
                        "color": <str>,
                        "featured_tag_id": <str>,
                        "genre_tag": None,
                        "is_discover": <str>,
                        "name_json": <str>,
                        "position": <str>,
                        "slug": <str>
                      }
                    ]
                  }
        """
        return self._get_json(f"{self.API_URL}/playlist/getTags")

    ### PURCHASES #############################################################

    # TODO

    def get_purchases(
        self, type: str = "albums", *, limit: int = None, offset: int = None
    ) -> dict[str, Any]:
        """
        Get the current user's purchases.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Parameters
        ----------
        type : `str`, default: :code:`"albums"`
            Media type.

            **Valid values**: :code:`"albums"` and :code:`"tracks"`.

        limit : `int`, keyword-only, optional
            The maximum number of albums or tracks to return.

            **Default**: :code:`50`.

        offset : `int`, keyword-only, optional
            The index of the first album or track to return. Use with
            `limit` to get the next page of albums or tracks.

            **Default**: :code:`0`.

        Returns
        -------
        purchases : `dict`
            A dictionary containing Qobuz catalog information for the
            current user's purchases.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "offset": <int>,
                    "limit": <int>,
                    "total": <int>,
                    "items": <list>
                  }
        """

        self._check_authentication("get_purchases")

        if type not in (MEDIA_TYPES := {"albums", "tracks"}):
            emsg = (
                f"Invalid media type. Valid values: {', '.join(MEDIA_TYPES)}."
            )
            raise ValueError(emsg)

        return self._get_json(
            f"{self.API_URL}/purchase/getUserPurchases",
            params={"type": type, "limit": limit, "offset": offset},
        )[type]

    ### SEARCH ################################################################

    def search(
        self,
        query: str,
        type: str = "catalog",
        *,
        limit: int = 10,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Search Qobuz for media and performers.

        Parameters
        ----------
        query : `str`
            Search query.

            .. tip::

               Searches can be narrowed using tags, such as
               :code:`#ByMainArtist`, :code:`#ByComposer`,
               :code:`#ByPerformer`, :code:`#ByReleaseName`,
               :code:`#ByLabel`, :code:`"#NewRelease"`, and
               :code:`#HiRes`.

               Use strict matching instead of fuzzy search by wrapping
               the keyword string in double quotes.

            **Example**: :code:`"Galantis" #ByMainArtist #HiRes`.

        type : `str`, keyword-only, optional
            Resource type.

            **Valid values**: :code:`"album"`, :code:`"artist"`,
            :code:`"catalog"`, :code:`"playlist"`, :code:`"story"`,
            :code:`"track"`.

        limit : `int`, keyword-only, default: :code:`10`
            Maximum number of results to return.

        offset : `int`, keyword-only, default: :code:`0`
            Index of the first result to return. Use with `limit` to get
            the next page of search results.

        Returns
        -------
        results : `dict`
            Search results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "query": <str>,
                    "albums": {
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>,
                      "items": [
                        {
                          "maximum_bit_depth": <int>,
                          "image": {
                            "small": <str>,
                            "thumbnail": <str>,
                            "large": <str>,
                            "back": <str>,
                          },
                          "media_count": <int>,
                          "artist": {
                            "image": <str>,
                            "name": <str>,
                            "id": <int>,
                            "albums_count": <int>,
                            "slug": <str>,
                            "picture": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "roles": [<str>]
                            }
                          ],
                          "upc": <str>,
                          "released_at": <int>,
                          "label": {
                            "name": <str>,
                            "id": <int>,
                            "albums_count": <int>,
                            "supplier_id": <int>,
                            "slug": <str>
                          },
                          "title": <str>,
                          "qobuz_id": <int>,
                          "version": <str>,
                          "url": <str>,
                          "duration": <int>,
                          "parental_warning": <bool>,
                          "popularity": <int>,
                          "tracks_count": <int>,
                          "genre": {
                            "path": [<int>],
                            "color": <str>,
                            "name": <str>,
                            "id": <int>,
                            "slug": <str>
                          },
                          "maximum_channel_count": <int>,
                          "id": <str>,
                          "maximum_sampling_rate": <int>,
                          "articles": <list>,
                          "release_date_original": <str>,
                          "release_date_download": <str>,
                          "release_date_stream": <str>,
                          "purchasable": <bool>,
                          "streamable": <bool>,
                          "previewable": <bool>,
                          "sampleable": <bool>,
                          "downloadable": <bool>,
                          "displayable": <bool>,
                          "purchasable_at": <int>,
                          "streamable_at": <int>,
                          "hires": <bool>,
                          "hires_streamable": <bool>
                        }
                      ]
                    },
                    "tracks": {
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>,
                      "items": [
                        {
                          "maximum_bit_depth": <int>,
                          "copyright": <str>,
                          "performers": <str>,
                          "audio_info": {
                            "replaygain_track_peak": <float>,
                            "replaygain_track_gain": <float>
                          },
                          "performer": {
                            "name": <str>,
                            "id": <int>
                          },
                          "album": {
                            "image": {
                              "small": <str>,
                              "thumbnail": <str>,
                              "large": <str>
                            },
                            "maximum_bit_depth": <int>,
                            "media_count": <int>,
                            "artist": {
                              "image": <str>,
                              "name": <str>,
                              "id": <int>,
                              "albums_count": <int>,
                              "slug":<str>,
                              "picture": <str>
                            },
                            "upc": <str>,
                            "released_at": <int>,
                            "label": {
                              "name": <str>,
                              "id": <int>,
                              "albums_count": <int>,
                              "supplier_id": <int>,
                              "slug": <str>
                            },
                            "title": <str>,
                            "qobuz_id": <int>,
                            "version": <str>,
                            "duration": <int>,
                            "parental_warning": <bool>,
                            "tracks_count": <int>,
                            "popularity": <int>,
                            "genre": {
                              "path": [<int>],
                              "color": <str>,
                              "name": <str>,
                              "id": <int>,
                              "slug": <str>
                            },
                            "maximum_channel_count": <int>,
                            "id": <str>,
                            "maximum_sampling_rate": <int>,
                            "previewable": <bool>,
                            "sampleable": <bool>,
                            "displayable": <bool>,
                            "streamable": <bool>,
                            "streamable_at": <int>,
                            "downloadable": <bool>,
                            "purchasable_at": <int>,
                            "purchasable": <bool>,
                            "release_date_original": <str>,
                            "release_date_download": <str>,
                            "release_date_stream": <str>,
                            "release_date_purchase": <str>,
                            "hires": <bool>,
                            "hires_streamable": <bool>
                          },
                          "work": <str>,
                          "composer": {
                            "name": <str>,
                            "id": <int>
                          },
                          "isrc": <str>,
                          "title": <str>,
                          "version": <str>,
                          "duration": <int>,
                          "parental_warning": <bool>,
                          "track_number": <int>,
                          "maximum_channel_count": <int>,
                          "id": <int>,
                          "media_number": <int>,
                          "maximum_sampling_rate": <int>,
                          "release_date_original": <str>,
                          "release_date_download": <str>,
                          "release_date_stream": <str>,
                          "release_date_purchase": <str>,
                          "purchasable": <bool>,
                          "streamable": <bool>,
                          "previewable": <bool>,
                          "sampleable": <bool>,
                          "downloadable": <bool>,
                          "displayable": <bool>,
                          "purchasable_at": <int>,
                          "streamable_at": <int>,
                          "hires": <bool>,
                          "hires_streamable": <bool>
                        }
                      ]
                    },
                    "artists": {
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>,
                      "items": [
                        {
                          "picture": <str>,
                          "image": {
                            "small": <str>,
                            "medium": <str>,
                            "large": <str>,
                            "extralarge": <str>,
                            "mega": <str>
                          },
                          "name": <str>,
                          "slug": <str>,
                          "albums_count": <int>,
                          "id": <int>
                        }
                      ]
                    },
                    "playlists": {
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>,
                      "items": [
                        {
                          "image_rectangle_mini": [<str>],
                          "is_published": <bool>,
                          "featured_artists": <list>,
                          "description": <str>,
                          "created_at": <int>,
                          "timestamp_position": <int>,
                          "images300": [<str>],
                          "duration": <int>,
                          "updated_at": <int>,
                          "published_to": <int>,
                          "genres": <list>,
                          "image_rectangle": [<str>],
                          "id": <int>,
                          "slug": <str>,
                          "owner": {
                            "id": <int>,
                            "name": <str>
                          },
                          "users_count": <int>,
                          "images150": [<str>],
                          "images": [<str>],
                          "is_collaborative": <bool>,
                          "stores": [<str>],
                          "tags": [
                            {
                              "featured_tag_id": <str>,
                              "name_json": <str>,
                              "slug": <str>,
                              "color": <str>,
                              "genre_tag": <str>,
                              "is_discover": <bool>
                            }
                          ],
                          "tracks_count": <int>,
                          "public_at": <int>,
                          "name": <str>,
                          "is_public": <bool>,
                          "published_from": <int>,
                          "is_featured": <bool>
                        }
                      ]
                    },
                    "focus": {
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>,
                      "items": [
                        {
                          "image": <str>,
                          "name_superbloc": <str>,
                          "accroche": <str>,
                          "id": <str>,
                          "title": <str>,
                          "genre_ids": [<str>],
                          "author": <str>,
                          "date": <str>
                        }
                      ]
                    },
                    "articles": {
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>,
                      "items": [
                        {
                          "image": <str>,
                          "thumbnail": <str>,
                          "root_category": <int>,
                          "author": <str>,
                          "abstract": <str>,
                          "source": <str>,
                          "title": <str>,
                          "type": <str>,
                          "url": <str>,
                          "image_original": <str>,
                          "category_id": <int>,
                          "source_image": <str>,
                          "id": <int>,
                          "published_at": <int>,
                          "category": <str>
                        }
                      ]
                    },
                    "stories": {
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>,
                      "items": [
                        {
                          "id": <str>,
                          "section_slugs": [<str>],
                          "title": <str>,
                          "description_short": <str>,
                          "authors": [
                            {
                              "id": <str>,
                              "name": <str>,
                              "slug": <str>
                            }
                          ],
                          "image": <str>,
                          "display_date": <int>
                        }
                      ]
                    }
                  }
        """
        return self._get_json(
            f"{self.API_URL}/{type}/search",
            params={"query": query, "limit": limit, "offset": offset},
        )

    ### TRACKS ################################################################

    # TODO

    def get_track(self, track_id: Union[int, str]) -> dict[str, Any]:
        """
        Get Qobuz catalog information for a track.

        Parameters
        ----------
        track_id : `int` or `str`
            Qobuz track ID.

            **Example**: :code:`24393138`.

        Returns
        -------
        track : `dict`
            Qobuz catalog information for the track.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "maximum_bit_depth": <int>,
                    "copyright": <str>,
                    "performers": <str>,
                    "audio_info": {
                      "replaygain_track_gain": <float>,
                      "replaygain_track_peak": <float>
                    },
                    "performer": {
                      "id": <int>,
                      "name": <str>
                    },
                    "album": {
                      "maximum_bit_depth": <int>,
                      "image": {
                        "small": <str>,
                        "thumbnail": <str>,
                        "large": <str>,
                        "back": <str>
                      },
                      "media_count": <int>,
                      "artist": {
                        "image": <str>,
                        "name": <str>,
                        "id": <int>,
                        "albums_count": <int>,
                        "slug": <str>,
                        "picture": <str>
                      },
                      "artists": [
                        {
                          "id": <int>,
                          "name": <str>,
                          "roles": [<str>]
                        }
                      ],
                      "upc": <str>,
                      "released_at": <int>,
                      "label": {
                        "name": <str>,
                        "id": <int>,
                        "albums_count": <int>,
                        "supplier_id": <int>,
                        "slug": <str>
                      },
                      "title": <str>,
                      "qobuz_id": <int>,
                      "version": <str>,
                      "url": <str>,
                      "duration": <int>,
                      "parental_warning": <bool>,
                      "popularity": <int>,
                      "tracks_count": <int>,
                      "genre": {
                        "path": [<int>],
                        "color": <str>,
                        "name": <str>,
                        "id": <int>,
                        "slug": <str>
                      },
                      "maximum_channel_count": <int>,
                      "id": <str>,
                      "maximum_sampling_rate": <int>,
                      "articles": <list>,
                      "release_date_original": <str>,
                      "release_date_download": <str>,
                      "release_date_stream": <str>,
                      "purchasable": <bool>,
                      "streamable": <bool>,
                      "previewable": <bool>,
                      "sampleable": <bool>,
                      "downloadable": <bool>,
                      "displayable": <bool>,
                      "purchasable_at": <int>,
                      "streamable_at": <int>,
                      "hires": <bool>,
                      "hires_streamable": <bool>,
                      "awards": <list>,
                      "description": <str>,
                      "description_language": <str>,
                      "goodies": <list>,
                      "area": null,
                      "catchline": <str>,
                      "composer": {
                        "id": <int>,
                        "name": <str>,
                        "slug": <str>,
                        "albums_count": <int>,
                        "picture": <str>,
                        "image": <str>
                      },
                      "created_at": <int>,
                      "genres_list": [<str>],
                      "period": <str>,
                      "copyright": <str>,
                      "is_official": <bool>,
                      "maximum_technical_specifications": <str>,
                      "product_sales_factors_monthly": <int>,
                      "product_sales_factors_weekly": <int>,
                      "product_sales_factors_yearly": <int>,
                      "product_type": <str>,
                      "product_url": <str>,
                      "recording_information": <str>,
                      "relative_url": <str>,
                      "release_tags": <list>,
                      "release_type": <str>,
                      "slug": <str>,
                      "subtitle": <str>
                    },
                    "work": <str>,
                    "composer": {
                      "id": <int>,
                      "name": <str>
                    },
                    "isrc": <str>,
                    "title": <str>,
                    "version": <str>,
                    "duration": <int>,
                    "parental_warning": <bool>,
                    "track_number": <int>,
                    "maximum_channel_count": <int>,
                    "id": <int>,
                    "media_number": <int>,
                    "maximum_sampling_rate": <int>,
                    "articles": <list>,
                    "release_date_original": <str>,
                    "release_date_download": <str>,
                    "release_date_stream": <str>,
                    "release_date_purchase": <str>,
                    "purchasable": <bool>,
                    "streamable": <bool>,
                    "previewable": <bool>,
                    "sampleable": <bool>,
                    "downloadable": <bool>,
                    "displayable": <bool>,
                    "purchasable_at": <int>,
                    "streamable_at": <int>,
                    "hires": <bool>,
                    "hires_streamable": <bool>
                  }
        """
        return self._get_json(
            f"{self.API_URL}/track/get", params={"track_id": track_id}
        )

    def get_track_performers(
        self,
        track_id: Union[int, str] = None,
        *,
        performers: str = None,
        roles: Union[list[str], set[str]] = None,
    ) -> dict[str, list]:
        """
        Get credits for a track.

        .. note::

           This method is provided for convenience and is not a private
           Qobuz API endpoint.

        Parameters
        ----------
        track_id : `int` or `str`, optional
            Qobuz track ID. Required if `performers` is not provided.

            **Example**: :code:`24393138`.

        performers : `str`, keyword-only, optional
            An unformatted string containing the track credits obtained
            from calling :meth:`get_track`.

        roles : `list` or `set`, keyword-only, optional
            Role filter. The special :code:`"Composers"` filter will
            combine the :code:`"Composer"`, :code:`"ComposerLyricist"`,
            :code:`"Lyricist"`, and :code:`"Writer"` roles.

            **Valid values**: :code:`"MainArtist"`,
            :code:`"FeaturedArtist"`, :code:`"Producer"`,
            :code:`"Co-Producer"`, :code:`"Mixer"`,
            :code:`"Composers"` (:code:`"Composer"`,
            :code:`"ComposerLyricist"`, :code:`"Lyricist"`,
            :code:`"Writer"`), :code:`"MusicPublisher"`, etc.

        Returns
        -------
        credits : `dict`
            A dictionary containing the track contributors, with their
            roles (in snake case) being the keys.
        """

        if performers is None:
            if track_id is None:
                emsg = (
                    "Either a Qobuz track ID or an unformatted "
                    "string containing the track credits must be "
                    "provided."
                )
                raise ValueError(emsg)
            performers = self.get_track(track_id)["performers"]

        if performers is None:
            return {}

        return _parse_performers(performers, roles=roles)

    def get_track_file_url(
        self, track_id: Union[int, str], format_id: Union[int, str] = 27
    ) -> dict[str, Any]:
        """
        Get the file URL for a track.

        .. admonition:: Subscription
           :class: warning

           Full track playback information and lossless and Hi-Res audio
           is only available with an active Qobuz subscription.

        Parameters
        ----------
        track_id : `int` or `str`
            Qobuz track ID.

            **Example**: :code:`24393138`.

        format_id : `int` or `str`, default: :code:`27`
            Audio format ID that determines the maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` for constant bitrate (320 kbps) MP3.
               * :code:`6` for CD-quality (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` for up to 24-bit, 192 kHz Hi-Res FLAC.

        Returns
        -------
        url : `dict`
            A dictionary containing the URL and track information, such
            as the audio format, bit depth, etc.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "track_id": <int>,
                    "duration": <int>,
                    "url": <str>,
                    "format_id": <int>,
                    "mime_type": <str>,
                    "restrictions": [
                      {
                        "code": <str>
                      }
                    ],
                    "sampling_rate": <int>,
                    "bit_depth": <int>
                  }

        """

        if not self._flow or not self._sub:
            wmsg = (
                "No user authentication or Qobuz streaming plan "
                "detected. The URL, if available, will lead to a "
                "30-second preview of the track."
            )
            logging.warning(wmsg)

        if int(format_id) not in (FORMAT_IDS := {5, 6, 7, 27}):
            emsg = f"Invalid format ID. Valid values: {', '.join(FORMAT_IDS)}."
            raise ValueError(emsg)

        return self._get_json_secret(
            f"{self.API_URL}/track/getFileUrl",
            f"trackgetFileUrlformat_id{format_id}"
            f"intentstreamtrack_id{track_id}",
            params={
                "track_id": track_id,
                "format_id": format_id,
                "intent": "stream",
            },
        )

    ### STREAMS ###############################################################

    def get_track_stream(
        self, track_id: Union[int, str], *, format_id: Union[int, str] = 27
    ) -> tuple[bytes, str]:
        """
        Get the audio stream data for a track.

        .. admonition:: Subscription
           :class: warning

           Full track playback information and lossless and Hi-Res audio
           is only available with an active Qobuz subscription.

        .. note::

           This method is provided for convenience and is not a private
           Qobuz API endpoint.

        Parameters
        ----------
        track_id : `int` or `str`
            Qobuz track ID.

            **Example**: :code:`24393138`.

        format_id : `int`, default: :code:`27`
            Audio format ID that determines the maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` for constant bitrate (320 kbps) MP3.
               * :code:`6` for CD-quality (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` for up to 24-bit, 192 kHz Hi-Res FLAC.

        Returns
        -------
        stream : `bytes`
            Audio stream data.

        mime_type : `str`
            Audio stream MIME type.
        """

        file = self.get_track_file_url(track_id, format_id=format_id)
        with self.session.get(file["url"]) as r:
            return r.content, file["mime_type"]

    def get_collection_streams(
        self,
        id: Union[int, str],
        type: str,
        *,
        format_id: Union[int, str] = 27,
    ) -> list[tuple[bytes, str]]:
        """
        Get audio stream data for all tracks in an album or a playlist.

        .. admonition:: Subscription
           :class: warning

           Full track playback information and lossless and Hi-Res audio
           is only available with an active Qobuz subscription.

        .. note::

           This method is provided for convenience and is not a private
           Qobuz API endpoint.

        Parameters
        ----------
        id : `int` or `str`
            Qobuz collection ID.

        type : `str`
            Collection type.

            **Valid values**: :code:`"album"` and :code:`"playlist"`.

        format_id : `int`, default: :code:`27`
            Audio format ID that determines the maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` for constant bitrate (320 kbps) MP3.
               * :code:`6` for CD-quality (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` for up to 24-bit, 192 kHz Hi-Res FLAC.

        Returns
        -------
        streams : `list`
            Audio stream data.
        """

        if type not in (COLLECTION_TYPES := {"album", "playlist"}):
            emsg = (
                "Invalid collection type. Valid values: "
                f"{', '.join(COLLECTION_TYPES)}."
            )
            raise ValueError(emsg)

        if type == "album":
            data = self.get_album(id)
        elif type == "playlist":
            data = self.get_playlist(id, limit=500)
        return [
            (
                self.get_track_stream(track["id"], format_id=format_id)
                if track["streamable"]
                else None
            )
            for track in data["tracks"]["items"]
        ]

    ### USER ##################################################################

    # TODO

    def get_profile(self) -> dict[str, Any]:
        """
        Get the current user's profile information.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via the password flow.

        Returns
        -------
        profile : `dict`
            A dictionary containing the current user's profile
            information.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "publicId": <str>,
                    "email": <str>,
                    "login": <str>,
                    "firstname": <str>,
                    "lastname": <str>,
                    "display_name": <str>,
                    "country_code": <str>,
                    "language_code": <str>,
                    "zone": <str>,
                    "store": <str>,
                    "country": <str>,
                    "avatar": <str>,
                    "genre": <str>,
                    "age": <int>,
                    "creation_date": <str>,
                    "subscription": {
                      "offer": <str>,
                      "periodicity": <str>,
                      "start_date": <str>,
                      "end_date": <str>,
                      "is_canceled": <bool>,
                      "household_size_max": <int>
                    },
                    "credential": {
                      "id": <int>,
                      "label": <str>,
                      "description": <str>,
                      "parameters": {
                        "lossy_streaming": <bool>,
                        "lossless_streaming": <bool>,
                        "hires_streaming": <bool>,
                        "hires_purchases_streaming": <bool>,
                        "mobile_streaming": <bool>,
                        "offline_streaming": <bool>,
                        "hfp_purchase": <bool>,
                        "included_format_group_ids": [<int>],
                        "color_scheme": {
                          "logo": <str>
                        },
                        "label": <str>,
                        "short_label": <str>,
                        "source": <str>
                      }
                    },
                    "last_update": {
                      "favorite": <int>,
                      "favorite_album": <int>,
                      "favorite_artist": <int>,
                      "favorite_track": <int>,
                      "playlist": <int>,
                      "purchase": <int>
                    },
                    "store_features": {
                      "download": <bool>,
                      "streaming": <bool>,
                      "editorial": <bool>,
                      "club": <bool>,
                      "wallet": <bool>,
                      "weeklyq": <bool>,
                      "autoplay": <bool>,
                      "inapp_purchase_subscripton": <bool>,
                      "opt_in": <bool>,
                      "music_import": <bool>
                    }
                  }
        """

        self._check_authentication("get_profile")

        return self._get_json(f"{self.API_URL}/user/get")
