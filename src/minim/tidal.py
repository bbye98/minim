"""
TIDAL
=====
.. moduleauthor:: Benjamin Ye <GitHub: bbye98>

This module contains a complete implementation of all public TIDAL API
endpoints and a minimum implementation of the more robust but private
TIDAL API.
"""

import base64
import datetime
import hashlib
import json
import logging
import os
import pathlib
import re
import secrets
import time
from typing import Any, Union
import urllib
import warnings
import webbrowser
from xml.dom import minidom

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import requests

from . import FOUND_PLAYWRIGHT, DIR_HOME, DIR_TEMP, _config

if FOUND_PLAYWRIGHT:
    from playwright.sync_api import sync_playwright

__all__ = ["API", "PrivateAPI"]


class API:
    """
    TIDAL API client.

    The TIDAL API exposes TIDAL functionality and data, making it
    possible to build applications that can search for and retrieve
    metadata from the TIDAL catalog.

    .. seealso::

       For more information, see the `TIDAL API Reference
       <https://developer.tidal.com/apiref>`_.

    Requests to the TIDAL API endpoints must be accompanied by a valid
    access token in the header. Minim can obtain client-only access
    tokens via the client credentials flow, which requires valid client
    credentials (client ID and client secret) to either be provided to
    this class's constructor as keyword arguments or be stored as
    :code:`TIDAL_CLIENT_ID` and :code:`TIDAL_CLIENT_SECRET` in the
    operating system's environment variables.

    .. seealso::

       To get client credentials, see the `guide on how to register a new
       TIDAL application <https://developer.tidal.com/documentation
       /dashboard/dashboard-client-credentials>`_.

    If an existing access token is available, it and its expiry time can
    be provided to this class's constructor as keyword arguments to
    bypass the access token retrieval process. It is recommended that
    all other authorization-related keyword arguments be specified so
    that a new access token can be obtained when the existing one
    expires.

    .. tip::

       The authorization flow and access token can be changed or updated
       at any time using :meth:`set_auflow` and :meth:`set_access_token`,
       respectively.

    Minim also stores and manages access tokens and their properties.
    When an access token is acquired, it is automatically saved to the
    Minim configuration file to be loaded on the next instantiation of
    this class. This behavior can be disabled if there are any security
    concerns, like if the computer being used is a shared device.

    Parameters
    ----------
    client_id : `str`, keyword-only, optional
        Client ID. Required for the client credentials flow. If it is
        not stored as :code:`TIDAL_CLIENT_ID` in the operating system's
        environment variables or found in the Minim configuration file,
        it must be provided here.

    client_secret : `str`, keyword-only, optional
        Client secret. Required for the client credentials flow. If it
        is not stored as :code:`TIDAL_CLIENT_SECRET` in the operating
        system's environment variables or found in the Minim
        configuration file, it must be provided here.

    flow : `str`, keyword-only, optional
        Authorization flow.

        .. container::

           **Valid values**:

           * :code:`"client_credentials"` for the client credentials
             flow.

    access_token : `str`, keyword-only, optional
        Access token. If provided here or found in the Minim
        configuration file, the authorization process is bypassed. In
        the former case, all other relevant keyword arguments should be
        specified to automatically refresh the access token when it
        expires.

    expiry : `datetime.datetime` or `str`, keyword-only, optional
        Expiry time of `access_token` in the ISO 8601 format
        :code:`%Y-%m-%dT%H:%M:%SZ`. If provided, the user will be
        reauthenticated using the specified authorization flow (if
        possible) when `access_token` expires.

    overwrite : `bool`, keyword-only, default: :code:`False`
        Determines whether to overwrite an existing access token in the
        Minim configuration file.

    save : `bool`, keyword-only, default: :code:`True`
        Determines whether newly obtained access tokens and their
        associated properties are stored to the Minim configuration
        file.

    Attributes
    ----------
    session : `requests.Session`
        Session used to send requests to the TIDAL API.

    API_URL : `str`
        Base URL for the TIDAL API.

    TOKEN_URL : `str`
        URL for the TIDAL API token endpoint.
    """

    _FLOWS = {"client_credentials"}
    _NAME = f"{__module__}.{__qualname__}"
    API_URL = "https://openapi.tidal.com"
    TOKEN_URL = "https://auth.tidal.com/v1/oauth2/token"

    def __init__(
        self,
        *,
        client_id: str = None,
        client_secret: str = None,
        flow: str = "client_credentials",
        access_token: str = None,
        expiry: Union[datetime.datetime, str] = None,
        overwrite: bool = False,
        save: bool = True,
    ) -> None:
        """
        Create a TIDAL API client.
        """

        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/vnd.tidal.v1+json"

        if access_token is None and _config.has_section(self._NAME) and not overwrite:
            flow = _config.get(self._NAME, "flow")
            access_token = _config.get(self._NAME, "access_token")
            expiry = _config.get(self._NAME, "expiry")
            client_id = _config.get(self._NAME, "client_id")
            client_secret = _config.get(self._NAME, "client_secret")

        self.set_flow(flow, client_id=client_id, client_secret=client_secret, save=save)
        self.set_access_token(access_token, expiry=expiry)

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

        if self._expiry is not None and datetime.datetime.now() > self._expiry:
            self.set_access_token()

        r = self.session.request(method, url, **kwargs)
        if r.status_code not in range(200, 299):
            try:
                error = r.json()["errors"][0]
                emsg = f"{r.status_code} {error['code']}: {error['detail']}"
            except requests.exceptions.JSONDecodeError:
                emsg = f"{r.status_code} {r.reason}"
            raise RuntimeError(emsg)
        return r

    def set_access_token(
        self, access_token: str = None, *, expiry: Union[str, datetime.datetime] = None
    ) -> None:
        """
        Set the TIDAL API access token.

        Parameters
        ----------
        access_token : `str`, optional
            Access token. If not provided, an access token is obtained
            using an OAuth 2.0 authorization flow.

        expiry : `str` or `datetime.datetime`, keyword-only, optional
            Access token expiry timestamp in the ISO 8601 format
            :code:`%Y-%m-%dT%H:%M:%SZ`. If provided, the user will be
            reauthenticated using the default authorization flow (if
            possible) when `access_token` expires.
        """

        if access_token is None:
            if not self._client_id or not self._client_secret:
                raise ValueError("TIDAL API client credentials not provided.")

            if self._flow == "client_credentials":
                client_b64 = base64.urlsafe_b64encode(
                    f"{self._client_id}:{self._client_secret}".encode()
                ).decode()
                r = requests.post(
                    self.TOKEN_URL,
                    data={"grant_type": "client_credentials"},
                    headers={"Authorization": f"Basic {client_b64}"},
                ).json()
                access_token = r["access_token"]
                expiry = datetime.datetime.now() + datetime.timedelta(
                    0, r["expires_in"]
                )

            if self._save:
                _config[self._NAME] = {
                    "flow": self._flow,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
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

    def set_flow(
        self,
        flow: str,
        *,
        client_id: str = None,
        client_secret: str = None,
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

               * :code:`"client_credentials"` for the client credentials
                 flow.

        client_id : `str`, keyword-only, optional
            Client ID. Required for all authorization flows.

        client_secret : `str`, keyword-only, optional
            Client secret. Required for all authorization flows.

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

        if flow == "client_credentials":
            self._client_id = client_id or os.environ.get("TIDAL_CLIENT_ID")
            self._client_secret = client_secret or os.environ.get("TIDAL_CLIENT_SECRET")

    ### ALBUM API #############################################################

    def get_album(self, album_id: Union[int, str], country_code: str) -> dict[str, Any]:
        """
        `Album API > Get single album
        <https://developer.tidal.com/apiref?ref=get-album>`_: Retrieve
        album details by TIDAL album ID.

        Parameters
        ----------
        album_id : `int` or `str`
            TIDAL album ID.

            **Example**: :code:`251380836`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        Returns
        -------
        album : `dict`
            TIDAL catalog information for a single album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <str>,
                    "barcodeId": <str>,
                    "title": <str>,
                    "artists": [
                      {
                        "id": <str>,
                        "name": <str>,
                        "picture": [
                          {
                            "url": <str>,
                            "width": <int>,
                            "height": <int>
                          }
                        ],
                        "main": <bool>
                      }
                    ],
                    "duration": <int>,
                    "releaseDate": <str>,
                    "imageCover": [
                      {
                        "url": <str>,
                        "width": <int>,
                        "height": <int>
                      }
                    ],
                    "videoCover": [
                      {
                        "url": <str>,
                        "width": <int>,
                        "height": <int>
                      }
                    ],
                    "numberOfVolumes": <int>,
                    "numberOfTracks": <int>,
                    "numberOfVideos": <int>,
                    "type": "ALBUM",
                    "copyright": <str>,
                    "mediaMetadata": {
                      "tags": [<str>]
                    },
                    "properties": {
                      "content": [<str>]
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/albums/{album_id}", params={"countryCode": country_code}
        )["resource"]

    def get_albums(
        self, album_ids: Union[int, str, list[Union[int, str]]], country_code: str
    ) -> list[dict[str, Any]]:
        """
        `Album API > Get multiple albums
        <https://developer.tidal.com/apiref?ref=get-albums-by-ids>`_:
        Retrieve a list of album details by TIDAL album IDs.

        Parameters
        ----------
        album_ids : `int`, `str`, or `list`
            TIDAL album ID(s).

            **Examples**: :code:`"251380836,275646830"` or
            :code:`[251380836, 275646830]`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        Returns
        -------
        albums : `dict`
            A dictionary containing TIDAL catalog information for
            multiple albums and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "resource": {
                          "id": <str>,
                          "barcodeId": <str>,
                          "title": <str>,
                          "artists": [
                            {
                              "id": <str>,
                              "name": <str>,
                              "picture": [
                                {
                                  "url": <str>,
                                  "width": <int>,
                                  "height": <int>
                                }
                              ],
                              "main": <bool>
                            }
                          ],
                          "duration": <int>,
                          "releaseDate": <str>,
                          "imageCover": [
                            {
                              "url": <str>,
                              "width": <int>,
                              "height": <int>
                            }
                          ],
                          "videoCover": [
                            {
                              "url": <str>,
                              "width": <int>,
                              "height": <int>
                            }
                          ],
                          "numberOfVolumes": <int>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "type": "ALBUM",
                          "copyright": <str>,
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "properties": {
                            "content": [<str>]
                          }
                        },
                        "id": <str>,
                        "status": 200,
                        "message": "success"
                      }
                    ],
                    "metadata": {
                      "requested": <int>,
                      "success": <int>,
                      "failure": <int>
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/albums/byIds",
            params={"ids": album_ids, "countryCode": country_code},
        )

    def get_album_items(
        self,
        album_id: Union[int, str],
        country_code: str,
        *,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        `Album API > Get album items
        <https://developer.tidal.com/apiref?ref=get-album-items>`_:
        Retrieve a list of album items (tracks and videos) by TIDAL
        album ID.

        Parameters
        ----------
        album_id : `int` or `str`
            TIDAL album ID.

            **Examples**: :code:`251380836`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, optional
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        items : `dict`
            A dictionary containing TIDAL catalog information for
            tracks and videos in the specified album and metadata for
            the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "resource": {
                          "artifactType": <str>,
                          "id": <str>,
                          "title": str>,
                          "artists": [
                            {
                              "id": <str>,
                              "name": <str>,
                              "picture": [
                                {
                                  "url": <str>,
                                  "width": <int>,
                                  "height": <int>
                                }
                              ],
                              "main": <bool>
                            }
                          ],
                          "album": {
                            "id": <str>,
                            "title": <str>,
                            "imageCover": [
                              {
                                "url": <str>,
                                "width": <int>,
                                "height": <int>
                              }
                            ],
                            "videoCover": []
                          },
                          "duration": <int>,
                          "trackNumber": <int>,
                          "volumeNumber": <int>,
                          "isrc": <str>,
                          "copyright": <str>,
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "properties": {
                            "content": [<str>]
                          }
                        },
                        "id": <str>,
                        "status": 200,
                        "message": "success"
                      }
                    ],
                    "metadata": {
                      "total": <int>
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/albums/{album_id}/items",
            params={"countryCode": country_code, "limit": limit, "offset": offset},
        )

    def get_album_by_barcode_id(
        self, barcode_id: Union[int, str], country_code: str
    ) -> dict[str, Any]:
        """
        `Album API > Get album by barcode ID
        <https://developer.tidal.com
        /apiref?ref=get-albums-by-barcode-id>`_: Retrieve a list of album
        details by barcode ID.

        Parameters
        ----------
        barcode_id : `int` or `str`
            Barcode ID in EAN-13 or UPC-A format.

            **Example**: :code:`196589525444`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        Returns
        -------
        album : `dict`
            TIDAL catalog information for a single album.

            .. admonition:: Sample response
                :class: dropdown

                .. code::

                  {
                    "data": [
                      {
                        "resource": {
                          "id": <str>,
                          "barcodeId": <str>,
                          "title": <str>,
                          "artists": [
                            {
                              "id": <str>,
                              "name": <str>,
                              "picture": [
                                {
                                  "url": <str>,
                                  "width": <int>,
                                  "height": <int>
                                }
                              ],
                              "main": <bool>
                            }
                          ],
                          "duration": <int>,
                          "releaseDate": <str>,
                          "imageCover": [
                            {
                              "url": <str>,
                              "width": <int>,
                              "height": <int>
                            }
                          ],
                          "videoCover": [
                            {
                              "url": <str>,
                              "width": <int>,
                              "height": <int>
                            }
                          ],
                          "numberOfVolumes": <int>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "type": "ALBUM",
                          "copyright": <str>,
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "properties": {
                            "content": [<str>]
                          }
                        },
                        "id": <str>,
                        "status": 200,
                        "message": "success"
                      }
                    ],
                    "metadata": {
                      "requested": 1,
                      "success": 1,
                      "failure": 0
                    }
                  }

        """

        return self._get_json(
            f"{self.API_URL}/albums/byBarcodeId",
            params={"barcodeId": barcode_id, "countryCode": country_code},
        )

    def get_similar_albums(
        self,
        album_id: Union[int, str],
        country_code: str,
        *,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        `Album API > Get similar albums for the given album
        <https://developer.tidal.com/apiref?ref=get-similar-albums>`_:
        Retrieve a list of albums similar to the given album.

        Parameters
        ----------
        album_id : `int` or `str`
            TIDAL album ID.

            **Examples**: :code:`251380836`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, optional
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        album_ids : `dict`
            A dictionary containing TIDAL album IDs for similar albums
            and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "resource": {
                          "id": <str>
                        }
                      }
                    ],
                    "metadata": {
                      "total": <int>
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/albums/{album_id}/similar",
            params={"countryCode": country_code, "limit": limit, "offset": offset},
        )

    ### ARTIST API ############################################################

    def get_artist(
        self, artist_id: Union[int, str], country_code: str
    ) -> dict[str, Any]:
        """
        `Artist API > Get single artist
        <https://developer.tidal.com/apiref?ref=get-artist>`_: Retrieve
        artist details by TIDAL artist ID.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        Returns
        -------
        artist : `dict`
            TIDAL catalog information for a single artist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <str>,
                    "name": <str>,
                    "picture": [
                      {
                        "url": <str>,
                        "width": <int>,
                        "height": <int>
                      }
                    ]
                  }
        """

        return self._get_json(
            f"{self.API_URL}/artists/{artist_id}", params={"countryCode": country_code}
        )["resource"]

    def get_artists(
        self, artist_ids: Union[int, str, list[Union[int, str]]], country_code: str
    ) -> dict[str, Any]:
        """
        `Artist API > Get multiple artists
        <https://developer.tidal.com/apiref?ref=get-artists-by-ids>`_:
        Retrieve a list of artist details by TIDAL artist IDs.

        Parameters
        ----------
        artist_ids : `int`, `str`, or `list`
            TIDAL artist ID(s).

            **Examples**: :code:`"1566,7804"` or :code:`[1566, 7804]`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        Returns
        -------
        artists : `dict`
            A dictionary containing TIDAL catalog information for
            multiple artists and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                {
                  "data": [
                    {
                      "resource": {
                        "id": <str>,
                        "name": <str>,
                        "picture": [
                          {
                            "url": <str>,
                            "width": <int>,
                            "height": <int>
                          }
                        ]
                      },
                      "id": <str>,
                      "status": 200,
                      "message": "success"
                    }
                  ],
                  "metadata": {
                    "requested": <int>,
                    "success": <int>,
                    "failure": <int>
                  }
                }
        """

        return self._get_json(
            f"{self.API_URL}/artists",
            params={"ids": artist_ids, "countryCode": country_code},
        )

    def get_artist_albums(
        self,
        artist_id: Union[int, str],
        country_code: str,
        *,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        `Artist API > Get albums by artist
        <https://developer.tidal.com/apiref?ref=get-artist-albums>`_:
        Retrieve a list of albums by TIDAL artist ID.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, optional
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        albums : `dict`
            A dictionary containing TIDAL catalog information for
            albums by the specified artist and metadata for the
            returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "resource": {
                          "id": <str>,
                          "barcodeId": <str>,
                          "title": <str>,
                          "artists": [
                            {
                              "id": <str>,
                              "name": <str>,
                              "picture": [
                                {
                                  "url": <str>,
                                  "width": <int>,
                                  "height": <int>
                                }
                              ],
                              "main": <bool>
                            }
                          ],
                          "duration": <int>,
                          "releaseDate": <str>,
                          "imageCover": [
                            {
                              "url": <str>,
                              "width": <int>,
                              "height": <int>
                            }
                          ],
                          "videoCover": [
                            {
                              "url": <str>,
                              "width": <int>,
                              "height": <int>
                            }
                          ],
                          "numberOfVolumes": <int>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "type": "ALBUM",
                          "copyright": <str>,
                          "mediaMetadata": {
                            "tags": <str>
                          },
                          "properties": {
                            "content": <str>
                          }
                        },
                        "id": <str>,
                        "status": 200,
                        "message": "success"
                      }
                    ],
                    "metadata": {
                      "total": <int>
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/artists/{artist_id}/albums",
            params={"countryCode": country_code, "limit": limit, "offset": offset},
        )

    def get_artist_tracks(
        self,
        artist_id: Union[int, str],
        country_code: str,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        `Track API > Get tracks by artist
        <https://developer.tidal.com/apiref?ref=get-tracks-by-artist>`_:
        Retrieve a list of tracks made by the specified artist.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, optional
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        tracks : `dict`
            A dictionary containing TIDAL catalog information for tracks
            by the specified artist and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "resource": {
                          "properties": {
                            "content": <str>
                          },
                          "id": <str>,
                          "version": <str>,
                          "duration": <int>,
                          "album": {
                            "id": <str>,
                            "title": <str>,
                            "imageCover": [
                              {
                                "url": <str>,
                                "width": <int>,
                                "height": <int>
                              }
                            ],
                            "videoCover": [
                              {
                                "url": <str>,
                                "width": <int>,
                                "height": <int>
                              }
                            ]
                          },
                          "title": <str>,
                          "copyright": <str>,
                          "artists": [
                            {
                              "id": <str>,
                              "name": <str>,
                              "picture": [
                                {
                                  "url": <str>,
                                  "width": <int>,
                                  "height": <int>
                                }
                              ],
                              "main": <bool>
                            }
                          ],
                          "popularity": <float>,
                          "isrc": <str>,
                          "trackNumber": <int>,
                          "volumeNumber": <int>,
                          "tidalUrl": <str>,
                          "providerInfo": {
                            "providerId": <str>,
                            "providerName": <str>
                          },
                          "artifactType": <str>,
                          "mediaMetadata": {
                            "tags": <str>
                          }
                        },
                        "id": <str>,
                        "status": <int>,
                        "message": <str>
                      }
                    ],
                    "metadata": {
                      "total": <int>
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/artists/{artist_id}/tracks",
            params={"countryCode": country_code, "limit": limit, "offset": offset},
        )

    def get_similar_artists(
        self,
        artist_id: Union[int, str],
        country_code: str,
        *,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        `Artist API > Get similar artists for the given artist
        <https://developer.tidal.com/apiref?ref=get-similar-artists>`_:
        Retrieve a list of artists similar to the given artist.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, optional
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        artist_ids : `dict`
            A dictionary containing TIDAL artist IDs for similar albums
            and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "resource": {
                          "id": <str>
                        }
                      }
                    ],
                    "metadata": {
                      "total": <int>
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/artists/{artist_id}/similar",
            params={"countryCode": country_code, "limit": limit, "offset": offset},
        )

    ### TRACK API #############################################################

    def get_track(self, track_id: Union[int, str], country_code: str) -> dict[str, Any]:
        """
        `Track API > Get single track
        <https://developer.tidal.com/apiref?ref=get-track>`_: Retrieve
        track details by TIDAL track ID.

        Parameters
        ----------
        track_id : `int` or `str`
            TIDAL track ID.

            **Example**: :code:`251380837`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        Returns
        -------
        track : `dict`
            TIDAL catalog information for a single track.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                    {
                      "artifactType": "track",
                      "id": <str>,
                      "title": <str>,
                      "artists": [
                        {
                          "id": <str>,
                          "name": <str>,
                          "picture": [
                            {
                              "url": <str>,
                              "width": <int>,
                              "height": <int>
                            }
                          ],
                          "main": <bool>
                        }
                      ],
                      "album": {
                        "id": <str>,
                        "title": <str>,
                        "imageCover": [
                          {
                            "url": <str>,
                            "width": <int>,
                            "height": <int>
                          }
                        ],
                        "videoCover": [
                            {
                              "url": <str>,
                              "width": <int>,
                              "height": <int>
                            }
                        ]
                      },
                      "duration": <int>,
                      "trackNumber": <int>,
                      "volumeNumber": <int>,
                      "isrc": <int>,
                      "copyright": <int>,
                      "mediaMetadata": {
                        "tags": [<str>]
                      },
                      "properties": {
                        "content": [<str>]
                      }
                    }
        """

        return self._get_json(
            f"{self.API_URL}/tracks/{track_id}", params={"countryCode": country_code}
        )["resource"]

    def get_tracks(
        self, track_ids: Union[int, str, list[Union[int, str]]], country_code: str
    ) -> dict[str, Any]:
        """
        `Album API > Get multiple tracks
        <https://developer.tidal.com/apiref?ref=get-tracks-by-ids>`_:
        Retrieve a list of track details by TIDAL track IDs.

        Parameters
        ----------
        track_ids : `int`, `str`, or `list`
            TIDAL track ID(s).

            **Examples**: :code:`"251380837,251380838"` or
            :code:`[251380837, 251380838]`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        Returns
        -------
        tracks : `dict`
            A dictionary containing TIDAL catalog information for
            multiple tracks and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "resource": {
                          "artifactType": "track",
                          "id": <str>,
                          "title": <str>,
                          "artists": [
                            {
                              "id": <str>,
                              "name": <str>,
                              "picture": [
                                {
                                  "url": <str>,
                                  "width": <int>,
                                  "height": <int>
                                }
                              ],
                              "main": <bool>
                            }
                          ],
                          "album": {
                            "id": <str>,
                            "title": <str>,
                            "imageCover": [
                              {
                                "url": <str>,
                                "width": <int>,
                                "height": <int>
                              }
                            ],
                            "videoCover": [
                                {
                                  "url": <str>,
                                  "width": <int>,
                                  "height": <int>
                                }
                            ]
                          },
                          "duration": <int>,
                          "trackNumber": <int>,
                          "volumeNumber": <int>,
                          "isrc": <int>,
                          "copyright": <int>,
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "properties": {
                            "content": [<str>]
                          }
                        },
                        "id": <str>,
                        "status": 200,
                        "message": "success"
                      }
                    ],
                    "metadata": {
                      "requested": <int>,
                      "success": <int>,
                      "failure": <int>
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/tracks",
            params={"ids": track_ids, "countryCode": country_code},
        )

    def get_tracks_by_isrc(
        self, isrc: str, country_code: str, limit: int = None, offset: int = None
    ) -> dict[str, Any]:
        """
        `Track API > Get tracks by ISRC
        <https://developer.tidal.com/apiref?ref=get-tracks-by-isrc>`_:
        Retrieve a list of track details by ISRC.

        Parameters
        ----------
        isrc : `str`
            Valid ISRC code (usually comprises 12 alphanumeric
            characters).

            **Example**: :code:`"USSM12209515"`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        limit : `int`, optional
            Page size.

            **Example**: :code:`10`.

        offset : `int`, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        tracks : `dict`
            A dictionary containing TIDAL catalog information for
            tracks with the specified ISRC and metadata for the
            returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "resource": {
                          "artifactType": "track",
                          "id": <str>,
                          "title": <str>,
                          "artists": [
                            {
                              "id": <str>,
                              "name": <str>,
                              "picture": [
                                {
                                  "url": <str>,
                                  "width": <int>,
                                  "height": <int>
                                }
                              ],
                              "main": <bool>
                            }
                          ],
                          "album": {
                            "id": <str>,
                            "title": <str>,
                            "imageCover": [
                              {
                                "url": <str>,
                                "width": <int>,
                                "height": <int>
                              }
                            ],
                            "videoCover": [
                                {
                                  "url": <str>,
                                  "width": <int>,
                                  "height": <int>
                                }
                            ]
                          },
                          "duration": <int>,
                          "trackNumber": <int>,
                          "volumeNumber": <int>,
                          "isrc": <int>,
                          "copyright": <int>,
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "properties": {
                            "content": [<str>]
                          }
                        },
                        "id": <str>,
                        "status": 200,
                        "message": "success"
                      }
                    ],
                    "metadata": {
                      "requested": <int>,
                      "success": <int>,
                      "failure": <int>
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/tracks/byIsrc",
            params={
                "isrc": isrc,
                "countryCode": country_code,
                "limit": limit,
                "offset": offset,
            },
        )

    def get_similar_tracks(
        self,
        track_id: Union[int, str],
        country_code: str,
        *,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        `Track API > Get similar tracks for the given track
        <https://developer.tidal.com/apiref?ref=get-similar-tracks>`_:
        Retrieve a list of tracks similar to the given track.

        Parameters
        ----------
        track_id : `int` or `str`
            TIDAL track ID.

            **Example**: :code:`251380837`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, optional
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        track_ids : `dict`
            A dictionary containing TIDAL track IDs for similar albums
            and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "resource": {
                          "id": <str>
                        }
                      }
                    ],
                    "metadata": {
                      "total": <int>
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/tracks/{track_id}/similar",
            params={"countryCode": country_code, "limit": limit, "offset": offset},
        )

    ### VIDEO API #############################################################

    def get_video(self, video_id: Union[int, str], country_code: str) -> dict[str, Any]:
        """
        `Video API > Get single video
        <https://developer.tidal.com/apiref?ref=get-video>`_: Retrieve
        video details by TIDAL video ID.

        Parameters
        ----------
        video_id : `int` or `str`
            TIDAL video ID.

            **Example**: :code:`75623239`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        Returns
        -------
        video : `dict`
            TIDAL catalog information for a single video.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "artifactType": "video",
                    "id": <str>,
                    "title": <str>,
                    "image": [
                          {
                            "url": <str>,
                            "width": <int>,
                            "height": <int>
                          }
                    ],
                    "releaseDate": <str>,
                    "artists": [
                      {
                        "id": <str>,
                        "name": <str>,
                        "picture": [
                          {
                            "url": <str>,
                            "width": <int>,
                            "height": <int>
                          }
                        ],
                        "main": <bool>
                      }
                    ],
                    "duration": <int>,
                    "trackNumber": <int>,
                    "volumeNumber": <int>,
                    "isrc": <str>,
                    "properties": {
                      "content": [<str>]
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/videos/{video_id}", params={"countryCode": country_code}
        )["resource"]

    def get_videos(
        self, video_ids: Union[int, str, list[Union[int, str]]], country_code: str
    ) -> list[dict[str, Any]]:
        """
        `Album API > Get multiple videos
        <https://developer.tidal.com/apiref?ref=get-videos-by-ids>`_:
        Retrieve a list of video details by TIDAL video IDs.

        Parameters
        ----------
        video_ids : `int`, `str`, or `list`
            TIDAL video ID(s).

            **Examples**: :code:`"59727844,75623239"` or
            :code:`[59727844, 75623239]`.

        country_code : `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        Returns
        -------
        videos : `dict`
            A dictionary containing TIDAL catalog information for
            multiple videos and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "artifactType": "video",
                        "id": <str>,
                        "title": <str>,
                        "image": [
                              {
                                "url": <str>,
                                "width": <int>,
                                "height": <int>
                              }
                        ],
                        "releaseDate": <str>,
                        "artists": [
                          {
                            "id": <str>,
                            "name": <str>,
                            "picture": [
                              {
                                "url": <str>,
                                "width": <int>,
                                "height": <int>
                              }
                            ],
                            "main": <bool>
                          }
                        ],
                        "duration": <int>,
                        "trackNumber": <int>,
                        "volumeNumber": <int>,
                        "isrc": <str>,
                        "properties": {
                          "content": [<str>]
                        }
                      }
                    ],
                    "metadata": {
                      "requested": <int>,
                      "success": <int>,
                      "failure": <int>
                    }
                  }
        """

        return self._get_json(
            f"{self.API_URL}/videos",
            params={"ids": video_ids, "countryCode": country_code},
        )

    ### SEARCH API ############################################################

    def search(
        self,
        query: str,
        country_code: str,
        *,
        type: str = None,
        limit: int = None,
        offset: int = None,
        popularity: str = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        `Search API > Search for catalog items
        <https://developer.tidal.com/apiref?ref=search>`_: Search for
        albums, artists, tracks, and videos.

        Parameters
        ----------
        query : `str`
            Search query.

            **Example**: :code:`"Beyoncé"`.

        country_code: `str`
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        type : `str`, keyword-only, optional
            Target search type. Searches for all types if not specified.

            **Valid values**: :code:`"ALBUMS"`, :code:`"ARTISTS"`,
            :code:`"TRACKS"`, :code:`"VIDEOS"`.

        limit : `int`, keyword-only, optional
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        popularity : `str`, keyword-only, optional
            Specify which popularity type to apply for query result.
            :code:`"WORLDWIDE"` is used if not specified.

            **Valid values**: :code:`"WORLDWIDE"` or :code:`"COUNTRY"`.

        Returns
        -------
        results : `dict`
            A dictionary containing TIDAL catalog information for
            albums, artists, tracks, and videos matching the search
            query, and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "albums": [
                      {
                        "resource": {
                          "id": <str>,
                          "barcodeId": <str>,
                          "title": <str>,
                          "artists": [
                            {
                              "id": <str>,
                              "name": <str>,
                              "picture": [
                                {
                                  "url": <str>,
                                  "width": <int>,
                                  "height": <int>
                                }
                              ],
                              "main": <bool>
                            }
                          ],
                          "duration": <int>,
                          "releaseDate": <str>,
                          "imageCover": [
                            {
                              "url": <str>,
                              "width": <int>,
                              "height": <int>
                            }
                          ],
                          "videoCover": [
                            {
                              "url": <str>,
                              "width": <int>,
                              "height": <int>
                            }
                          ],
                          "numberOfVolumes": <int>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "type": "ALBUM",
                          "copyright": <str>,
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "properties": {
                            "content": [<str>]
                          }
                        },
                        "id": <str>,
                        "status": 200,
                        "message": "success"
                      }
                    ],
                    "artists": [
                      {
                        "resource": {
                          "id": <str>,
                          "name": <str>,
                          "picture": [
                            {
                              "url": <str>,
                              "width": <int>,
                              "height": <int>
                            }
                          ]
                        },
                        "id": <str>,
                        "status": 200,
                        "message": "success"
                      }
                    ],
                    "tracks": [
                      {
                        "resource": {
                          "artifactType": "track",
                          "id": <str>,
                          "title": <str>,
                          "artists": [
                            {
                              "id": <str>,
                              "name": <str>,
                              "picture": [
                                {
                                  "url": <str>,
                                  "width": <int>,
                                  "height": <int>
                                }
                              ],
                              "main": <bool>
                            }
                          ],
                          "album": {
                            "id": <str>,
                            "title": <str>,
                            "imageCover": [
                              {
                                "url": <str>,
                                "width": <int>,
                                "height": <int>
                              }
                            ],
                            "videoCover": [
                                {
                                  "url": <str>,
                                  "width": <int>,
                                  "height": <int>
                                }
                            ]
                          },
                          "duration": <int>,
                          "trackNumber": <int>,
                          "volumeNumber": <int>,
                          "isrc": <int>,
                          "copyright": <int>,
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "properties": {
                            "content": [<str>]
                          }
                        },
                        "id": <str>,
                        "status": 200,
                        "message": "success"
                      }
                    ],
                    "videos": [
                      {
                        "artifactType": "video",
                        "id": <str>,
                        "title": <str>,
                        "image": [
                              {
                                "url": <str>,
                                "width": <int>,
                                "height": <int>
                              }
                        ],
                        "releaseDate": <str>,
                        "artists": [
                          {
                            "id": <str>,
                            "name": <str>,
                            "picture": [
                              {
                                "url": <str>,
                                "width": <int>,
                                "height": <int>
                              }
                            ],
                            "main": <bool>
                          }
                        ],
                        "duration": <int>,
                        "trackNumber": <int>,
                        "volumeNumber": <int>,
                        "isrc": <str>,
                        "properties": {
                          "content": [<str>]
                        }
                      }
                    ]
                  }
        """

        if type and type not in (TYPES := {"ALBUMS", "ARTISTS", "TRACKS", "VIDEOS"}):
            emsg = "Invalid target search type. Valid values: " f"{', '.join(TYPES)}."
            raise ValueError(emsg)

        return self._get_json(
            f"{self.API_URL}/search",
            params={
                "query": query,
                "countryCode": country_code,
                "type": type,
                "limit": limit,
                "offset": offset,
                "popularity": popularity,
            },
        )


class PrivateAPI:
    """
    Private TIDAL API client.

    The private TIDAL API allows media (tracks, videos), collections
    (albums, playlists), and performers to be queried, and information
    about them to be retrieved. As there is no available official
    documentation for the private TIDAL API, its endpoints have been
    determined by watching HTTP network traffic.

    .. attention::

       As the private TIDAL API is not designed to be publicly
       accessible, this class can be disabled or removed at any time to
       ensure compliance with the `TIDAL Developer Terms of Service
       <https://developer.tidal.com/documentation/guidelines
       /guidelines-developer-terms>`_.

    While authentication is not necessary to search for and retrieve
    data from public content, it is required to access personal content
    and stream media (with an active TIDAL subscription). In the latter
    case, requests to the private TIDAL API endpoints must be
    accompanied by a valid user access token in the header.

    Minim can obtain user access tokens via the authorization code with
    proof key for code exchange (PKCE) and device code flows. These
    OAuth 2.0 authorization flows require valid client credentials
    (client ID and client secret) to either be provided to this class's
    constructor as keyword arguments or be stored as
    :code:`TIDAL_PRIVATE_CLIENT_ID` and
    :code:`TIDAL_PRIVATE_CLIENT_SECRET` in the operating system's
    environment variables.

    .. hint::

       Client credentials can be extracted from the software you use to
       access TIDAL, including but not limited to the TIDAL Web Player
       and the Android, iOS, macOS, and Windows applications. Only the
       TIDAL Web Player and desktop application client credentials can
       be used without authorization.

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
    When an access token is acquired, it is automatically saved to the
    Minim configuration file to be loaded on the next instantiation of
    this class. This behavior can be disabled if there are any security
    concerns, like if the computer being used is a shared device.

    Parameters
    ----------
    client_id : `str`, keyword-only, optional
        Client ID. If it is not stored as
        :code:`TIDAL_PRIVATE_CLIENT_ID` in the operating system's
        environment variables or found in the Minim configuration file,
        it must be provided here.

    client_secret : `str`, keyword-only, optional
        Client secret. Required for the authorization code and device
        code flows. If it is not stored as
        :code:`TIDAL_PRIVATE_CLIENT_SECRET` in the operating system's
        environment variables or found in the Minim configuration file,
        it must be provided here.

    flow : `str`, keyword-only, optional
        Authorization flow. If not specified, no user authorization
        will be performed.

        .. container::

           **Valid values**:

           * :code:`"pkce"` for the authorization code with proof key
             for code exchange (PKCE) flow.
           * :code:`"device_code"` for the device code flow.

    browser : `bool`, keyword-only, default: :code:`False`
        Determines whether a web browser is automatically opened for the
        authorization code with PKCE or device code flows. If
        :code:`False`, users will have to manually open the
        authorization URL, and for the authorization code flow, provide
        the full callback URI via the terminal. For the authorization
        code with PKCE flow, the Playwright framework by Microsoft is
        used.

    scopes : `str` or `list`, keyword-only, default: :code:`"r_usr"`
        Authorization scopes to request user access for in the OAuth 2.0
        flows.

        **Valid values**: :code:`"r_usr"`, :code:`"w_usr"`, and
        :code:`"w_sub"` (device code flow only).

    user_agent : `str`, keyword-only, optional
        User agent information to send in the header of HTTP requests.

        .. note::

           If not specified, TIDAL may temporarily block your IP address
           if you are making requests too quickly.

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
        Base URL for the private TIDAL API.

    AUTH_URL : `str`
        URL for device code requests.

    LOGIN_URL : `str`
        URL for authorization code requests.

    REDIRECT_URL : `str`
        URL for authorization code callbacks.

    RESOURCES_URL : `str`
        URL for cover art and image requests.

    TOKEN_URL : `str`
        URL for access token requests.

    WEB_URL : `str`
        URL for the TIDAL Web Player.

    session : `requests.Session`
        Session used to send requests to the private TIDAL API.
    """

    _FLOWS = {"pkce", "device_code"}
    _NAME = f"{__module__}.{__qualname__}"

    API_URL = "https://api.tidal.com"
    AUTH_URL = "https://auth.tidal.com/v1/oauth2"
    LOGIN_URL = "https://login.tidal.com"
    REDIRECT_URI = "tidal://login/auth"
    RESOURCES_URL = "http://resources.tidal.com"
    WEB_URL = "https://listen.tidal.com"

    def __init__(
        self,
        *,
        client_id: str = None,
        client_secret: str = None,
        flow: str = None,
        browser: bool = False,
        scopes: Union[str, list[str]] = "r_usr",
        user_agent: str = None,
        access_token: str = None,
        refresh_token: str = None,
        expiry: datetime.datetime = None,
        overwrite: bool = False,
        save: bool = True,
    ) -> None:
        """
        Create a private TIDAL API client.
        """

        self.session = requests.Session()
        if user_agent:
            self.session.headers["User-Agent"] = user_agent

        if access_token is None and _config.has_section(self._NAME) and not overwrite:
            flow = _config.get(self._NAME, "flow")
            access_token = _config.get(self._NAME, "access_token")
            refresh_token = _config.get(self._NAME, "refresh_token")
            expiry = _config.get(self._NAME, "expiry")
            client_id = _config.get(self._NAME, "client_id")
            client_secret = _config.get(self._NAME, "client_secret")
            scopes = _config.get(self._NAME, "scopes")

        self.set_flow(
            flow,
            client_id=client_id,
            client_secret=client_secret,
            browser=browser,
            scopes=scopes,
            save=save,
        )
        self.set_access_token(access_token, refresh_token=refresh_token, expiry=expiry)

    def _check_scope(
        self,
        endpoint: str,
        scope: str = None,
        *,
        flows: Union[str, list[set], set[str]] = None,
        require_authentication: bool = True,
    ) -> None:
        """
        Check if the user has granted the appropriate authorization
        scope for the desired endpoint.

        Parameters
        ----------
        endpoint : `str`
            Private TIDAL API endpoint.

        scope : `str`, optional
            Required scope for `endpoint`.

        flows : `str`, `list`, or `set`, keyword-only, optional
            Authorization flows for which `scope` is required. If not
            specified, `flows` defaults to all supported authorization
            flows.

        require_authentication : `bool`, keyword-only, default: :code:`True`
            Specifies whether the endpoint requires user authentication.
            Some endpoints can be used without authentication but require
            specific scopes when user authentication has been performed.
        """

        if flows is None:
            flows = self._FLOWS

        if require_authentication:
            if self._flow is None:
                emsg = f"{self._NAME}.{endpoint}() requires user " "authentication."
            elif self._flow in flows and scope and scope not in self._scopes:
                emsg = (
                    f"{self._NAME}.{endpoint}() requires the '{scope}' "
                    "authorization scope."
                )
            else:
                return
        elif self._flow in flows and scope and scope not in self._scopes:
            emsg = (
                f"{self._NAME}.{endpoint}() requires the '{scope}' "
                "authorization scope when user authentication has "
                f"been performed via the '{self._flow}' "
                "authorization flow."
            )
        else:
            return
        raise RuntimeError(emsg)

    def _get_authorization_code(self, code_challenge: str) -> str:
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
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "redirect_uri": self.REDIRECT_URI,
            "response_type": "code",
        }
        if self._scopes:
            params["scope"] = self._scopes
        auth_url = f"{self.LOGIN_URL}/authorize?" f"{urllib.parse.urlencode(params)}"

        if self._browser:
            har_file = DIR_TEMP / "minim_tidal_private.har"

            with sync_playwright() as playwright:
                browser = playwright.firefox.launch(headless=False)
                context = browser.new_context(
                    locale="en-US",
                    timezone_id="America/Los_Angeles",
                    record_har_path=har_file,
                    **playwright.devices["Desktop Firefox HiDPI"],
                )
                page = context.new_page()
                page.goto(auth_url, timeout=0)
                page.wait_for_url(f"{self.REDIRECT_URI}*", wait_until="commit")
                context.close()
                browser.close()

            with open(har_file, "r") as f:
                queries = dict(
                    urllib.parse.parse_qsl(
                        urllib.parse.urlparse(
                            re.search(rf'{self.REDIRECT_URI}\?(.*?)"', f.read()).group(
                                0
                            )
                        ).query
                    )
                )
            har_file.unlink()

        else:
            print(
                "To grant Minim access to TIDAL data and features, "
                "open the following link in your web browser:\n\n"
                f"{auth_url}\n"
            )
            uri = input(
                "After authorizing Minim to access TIDAL on "
                "your behalf, copy and paste the URI beginning "
                f"with '{self.REDIRECT_URI}' below.\n\nURI: "
            )
            queries = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(uri).query))

        if "code" not in queries:
            raise RuntimeError("Authorization failed.")
        return queries["code"]

    def _get_country_code(self, country_code: str = None) -> str:
        """
        Get the ISO 3166-1 alpha-2 country code to use for requests.

        Parameters
        ----------
        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        country_code : `str`
            ISO 3166-1 alpha-2 country code.
        """

        return (
            country_code
            or getattr(self, "_country_code", None)
            or self.get_country_code()
        )

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
            self._flow is None
            or not self._refresh_token
            or not self._client_id
            or (self._flow == "device_code" and not self._client_secret)
        ):
            self.set_access_token()
        else:
            r = requests.post(
                f"{self.LOGIN_URL}/oauth2/token",
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": self._refresh_token,
                },
            ).json()

            self.session.headers["Authorization"] = f"Bearer {r['access_token']}"
            self._expiry = datetime.datetime.now() + datetime.timedelta(
                0, r["expires_in"]
            )
            self._scopes = r["scope"]

            if self._save:
                _config[self._NAME].update(
                    {
                        "access_token": r["access_token"],
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
            if r.text:
                error = r.json()
                substatus = (
                    error["subStatus"]
                    if "subStatus" in error
                    else error["sub_status"] if "sub_status" in error else ""
                )
                description = (
                    error["userMessage"]
                    if "userMessage" in error
                    else (
                        error["description"]
                        if "description" in error
                        else (
                            error["error_description"]
                            if "error_description" in error
                            else ""
                        )
                    )
                )
                emsg = f"{r.status_code}"
                if substatus:
                    emsg += f".{substatus}"
                emsg += f" {description}"
            else:
                emsg = f"{r.status_code} {r.reason}"
            if r.status_code == 401 and substatus == 11003 and retry:
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
        Set the private TIDAL API access token.

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
            if self._flow is None:
                self._expiry = datetime.datetime.max
                return
            else:
                if not self._client_id:
                    emsg = "Private TIDAL API client ID not provided."
                    raise ValueError(emsg)

                if self._flow == "pkce":
                    data = {
                        "client_id": self._client_id,
                        "code_verifier": secrets.token_urlsafe(32),
                        "grant_type": "authorization_code",
                        "redirect_uri": self.REDIRECT_URI,
                        "scope": self._scopes,
                    }
                    data["code"] = self._get_authorization_code(
                        base64.urlsafe_b64encode(
                            hashlib.sha256(data["code_verifier"].encode()).digest()
                        )
                        .decode()
                        .rstrip("=")
                    )
                    r = requests.post(
                        f"{self.LOGIN_URL}/oauth2/token", json=data
                    ).json()
                elif self._flow == "device_code":
                    if not self._client_id:
                        emsg = "Private TIDAL API client secret not provided."
                        raise ValueError(emsg)

                    data = {"client_id": self._client_id}
                    if self._scopes:
                        data["scope"] = self._scopes
                    r = requests.post(
                        f"{self.AUTH_URL}/device_authorization", data=data
                    ).json()
                    if "error" in r:
                        emsg = (
                            f"{r['status']}.{r['sub_status']} "
                            f"{r['error_description']}"
                        )
                        raise ValueError(emsg)
                    data["device_code"] = r["deviceCode"]
                    data["grant_type"] = "urn:ietf:params:oauth:grant-type:device_code"

                    verification_uri = f"http://{r['verificationUriComplete']}"
                    if self._browser:
                        webbrowser.open(verification_uri)
                    else:
                        print(
                            "To grant Minim access to TIDAL data and "
                            "features, open the following link in "
                            f"your web browser:\n\n{verification_uri}\n"
                        )
                    while True:
                        time.sleep(2)
                        r = requests.post(
                            f"{self.AUTH_URL}/token",
                            auth=(self._client_id, self._client_secret),
                            data=data,
                        ).json()
                        if "error" not in r:
                            break
                        elif r["error"] != "authorization_pending":
                            raise RuntimeError(
                                f"{r['status']}.{r['sub_status']} "
                                f"{r['error_description']}"
                            )
                access_token = r["access_token"]
                refresh_token = r["refresh_token"]
                expiry = datetime.datetime.now() + datetime.timedelta(
                    0, r["expires_in"]
                )

                if self._save:
                    _config[self._NAME] = {
                        "flow": self._flow,
                        "client_id": self._client_id,
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expiry": expiry.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "scopes": self._scopes,
                    }
                    if hasattr(self, "_client_secret"):
                        _config[self._NAME]["client_secret"] = self._client_secret
                    with open(DIR_HOME / "minim.cfg", "w") as f:
                        _config.write(f)

        if len(access_token) == 16:
            self.session.headers["x-tidal-token"] = access_token
            self._refresh_token = self._expiry = None
        else:
            self.session.headers["Authorization"] = f"Bearer {access_token}"
            self._refresh_token = refresh_token
            self._expiry = (
                datetime.datetime.strptime(expiry, "%Y-%m-%dT%H:%M:%SZ")
                if isinstance(expiry, str)
                else expiry
            )

            if self._flow is not None:
                me = self.get_profile()
                self._country_code = me["countryCode"]
                self._user_id = me["userId"]

    def set_flow(
        self,
        flow: str,
        client_id: str,
        *,
        client_secret: str = None,
        browser: bool = False,
        scopes: Union[str, list[str]] = "",
        save: bool = True,
    ) -> None:
        """
        Set the authorization flow.

        Parameters
        ----------
        flow : `str`
            Authorization flow. If not specified, no user authentication
            will be performed.

            .. container::

               **Valid values**:

               * :code:`"pkce"` for the authorization code with proof
                 key for code exchange (PKCE) flow.
               * :code:`"client_credentials"` for the client credentials
                 flow.

        client_id : `str`
            Client ID.

        client_secret : `str`, keyword-only, optional
            Client secret. Required for all OAuth 2.0 authorization
            flows.

        browser : `bool`, keyword-only, default: :code:`False`
            Determines whether a web browser is automatically opened for
            the authorization code with PKCE or device code flows. If
            :code:`False`, users will have to manually open the
            authorization URL, and for the authorization code flow,
            provide the full callback URI via the terminal. For the
            authorization code with PKCE flow, the Playwright framework
            by Microsoft is used.

        scopes : `str` or `list`, keyword-only, optional
            Authorization scopes to request user access for in the OAuth
            2.0 flows.

            **Valid values**: :code:`"r_usr"`, :code:`"w_usr"`, and
            :code:`"w_sub"` (device code flow only).

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
        self._client_id = client_id or os.environ.get("TIDAL_PRIVATE_CLIENT_ID")

        if flow:
            if "x-tidal-token" in self.session.headers:
                del self.session.headers["x-tidal-token"]

            self._browser = browser
            if flow == "pkce" and browser and not FOUND_PLAYWRIGHT:
                self._browser = False
                wmsg = (
                    "The Playwright web framework was not found, "
                    "so automatic authorization code retrieval is "
                    "not available."
                )
                warnings.warn(wmsg)

            self._client_secret = client_secret or os.environ.get(
                "TIDAL_PRIVATE_CLIENT_SECRET"
            )
            self._scopes = " ".join(scopes) if isinstance(scopes, list) else scopes
        else:
            self.session.headers["x-tidal-token"] = self._client_id
            self._scopes = ""

    ### ALBUMS ################################################################

    def get_album(
        self, album_id: Union[int, str], country_code: str = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for an album.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        album_id : `int` or `str`
            TIDAL album ID.

            **Example**: :code:`251380836`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        album : `dict`
            TIDAL catalog information for an album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "title": <str>,
                    "duration": <int>,
                    "streamReady": <bool>,
                    "adSupportedStreamReady": <bool>,
                    "djReady": <bool>,
                    "stemReady": <bool>,
                    "streamStartDate": <str>,
                    "allowStreaming": <bool>,
                    "premiumStreamingOnly": <bool>,
                    "numberOfTracks": <int>,
                    "numberOfVideos": <int>,
                    "numberOfVolumes": <int>,
                    "releaseDate": <str>,
                    "copyright": <str>,
                    "type": "ALBUM",
                    "version": <str>,
                    "url": <str>,
                    "cover": <str>,
                    "vibrantColor": <str>,
                    "videoCover": <str>,
                    "explicit": <bool>,
                    "upc": <str>,
                    "popularity": <int>,
                    "audioQuality": <str>,
                    "audioModes": [<str>],
                    "mediaMetadata": {
                      "tags": [<str>]
                    },
                    "artist": {
                      "id": <int>,
                      "name": <str>,
                      "type": <str>,
                      "picture": <str>
                    },
                    "artists": [
                      {
                        "id": <int>,
                        "name": <str>,
                        "type": <str>,
                        "picture": <str>
                      }
                    ]
                  }
        """

        self._check_scope(
            "get_album", "r_usr", flows={"device_code"}, require_authentication=False
        )

        return self._get_json(
            f"{self.API_URL}/v1/albums/{album_id}",
            params={"countryCode": self._get_country_code(country_code)},
        )

    def get_album_items(
        self,
        album_id: Union[int, str],
        country_code: str = None,
        *,
        limit: int = 100,
        offset: int = None,
        credits: bool = False,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for items (tracks and videos) in
        an album.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        album_id : `int` or `str`
            TIDAL album ID.

            **Examples**: :code:`251380836`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`100`
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        credits : `bool`, keyword-only, default: :code:`False`
            Determines whether credits for each item is returned.

        Returns
        -------
        items : `dict`
            A dictionary containing TIDAL catalog information for
            tracks and videos in the specified album and metadata for
            the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "item": {
                          "id": <int>,
                          "title": <str>,
                          "duration": <int>,
                          "replayGain": <float>,
                          "peak": <float>,
                          "allowStreaming": <bool>,
                          "streamReady": <bool>,
                          "adSupportedStreamReady": <bool>,
                          "djReady": <bool>,
                          "stemReady": <bool>,
                          "streamStartDate": <str>,
                          "premiumStreamingOnly": <bool>,
                          "trackNumber": <int>,
                          "volumeNumber": >int>,
                          "version": <str>,
                          "popularity": <int>,
                          "copyright": <str>,
                          "url": <str>,
                          "isrc": <str>,
                          "editable": <bool>,
                          "explicit": <bool>,
                          "audioQuality": <str>,
                          "audioModes": [<str>],
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "artist": {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>,
                              "picture": <str>
                            }
                          ],
                          "album": {
                            "id": <int>,
                            "title": <str>,
                            "cover": <str>,
                            "vibrantColor": <str>,
                            "videoCover": <str>
                          },
                          "mixes": {
                            "TRACK_MIX": <str>
                          }
                        },
                        "type": "track"
                      }
                    ]
                  }
        """

        self._check_scope(
            "get_album_items",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        url = f"{self.API_URL}/v1/albums/{album_id}/items"
        if credits:
            url += "/credits"
        return self._get_json(
            url,
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
            },
        )

    def get_album_credits(
        self, album_id: Union[int, str], country_code: str = None
    ) -> dict[str, Any]:
        """
        Get credits for an album.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        album_id : `int` or `str`
            TIDAL album ID.

            **Example**: :code:`251380836`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        credits : `dict`
            A dictionary containing TIDAL catalog information for the
            album contributors.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "type": <str>,
                      "contributors": [
                        {
                          "name": <str>
                        }
                      ]
                    }
                  ]
        """

        self._check_scope(
            "get_album_credits",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/albums/{album_id}/credits",
            params={"countryCode": self._get_country_code(country_code)},
        )

    def get_album_review(
        self, album_id: Union[int, str], country_code: str = None
    ) -> dict[str, str]:
        """
        Get a review of or a synopsis for an album.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        album_id : `int` or `str`
            TIDAL album ID.

            **Example**: :code:`251380836`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        review : `dict`
            A dictionary containing a review of or a synopsis for an
            album and its source.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "source": <str>,
                    "lastUpdated": <str>,
                    "text": <str>,
                    "summary": <str>
                  }
        """

        self._check_scope(
            "get_album_review",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/albums/{album_id}/review",
            params={"countryCode": self._get_country_code(country_code)},
        )

    def get_similar_albums(
        self, album_id: Union[int, str], country_code: str = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for albums similar to the
        specified album.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        album_id : `int` or `str`
            TIDAL album ID.

            **Example**: :code:`251380836`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        album : `dict`
            TIDAL catalog information for an album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "id": <int>,
                        "title": <str>,
                        "duration": <int>,
                        "streamReady": <bool>,
                        "adSupportedStreamReady": <bool>,
                        "djReady": <bool>,
                        "stemReady": <bool>,
                        "streamStartDate": <str>,
                        "allowStreaming": <bool>,
                        "premiumStreamingOnly": <bool>,
                        "numberOfTracks": <int>,
                        "numberOfVideos": <int>,
                        "numberOfVolumes": <int>,
                        "releaseDate": <str>,
                        "copyright": <str>,
                        "type": "ALBUM",
                        "version": <str>,
                        "url": <str>,
                        "cover": <str>,
                        "vibrantColor": <str>,
                        "videoCover": <str>,
                        "explicit": <bool>,
                        "upc": <str>,
                        "popularity": <int>,
                        "audioQuality": <str>,
                        "audioModes": [<str>],
                        "mediaMetadata": {
                          "tags": [<str>]
                        },
                        "artist": {
                          "id": <int>,
                          "name": <str>,
                          "type": <str>,
                          "picture": <str>
                        },
                        "artists": [
                          {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          }
                        ]
                      }
                    ],
                    "source": <str>
                  }
        """

        self._check_scope(
            "get_similar_albums",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/albums/{album_id}/similar",
            params={"countryCode": self._get_country_code(country_code)},
        )

    def get_favorite_albums(
        self,
        country_code: str = None,
        *,
        limit: int = 50,
        offset: int = None,
        order: str = "DATE",
        order_direction: str = "DESC",
    ) -> None:
        """
        Get TIDAL catalog information for albums in the current user's
        collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`50`
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        order : `str`, keyword-only, default: :code:`"DATE"`
            Sorting order.

            **Valid values**: :code:`"DATE"` and :code:`"NAME"`.

        order_direction : `str`, keyword-only, default: :code:`"DESC"`
            Sorting order direction.

            **Valid values**: :code:`"DESC"` and :code:`"ASC"`.

        Returns
        -------
        albums : `dict`
            A dictionary containing TIDAL catalog information for albums
            in the current user's collection and metadata for the
            returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "created": <str>,
                        "item": {
                          "id": <int>,
                          "title": <str>,
                          "duration": <int>,
                          "streamReady": <bool>,
                          "adSupportedStreamReady": <bool>,
                          "djReady": <bool>,
                          "stemReady": <bool>,
                          "streamStartDate": <str>,
                          "allowStreaming": <bool>,
                          "premiumStreamingOnly": <bool>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "numberOfVolumes": <int>,
                          "releaseDate": <str>,
                          "copyright": <str>,
                          "type": "ALBUM",
                          "version": <str>,
                          "url": <str>,
                          "cover": <str>,
                          "vibrantColor": <str>,
                          "videoCover": <str>,
                          "explicit": <bool>,
                          "upc": <str>,
                          "popularity": <int>,
                          "audioQuality": <str>,
                          "audioModes": [<str>],
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "artist": {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>,
                              "picture": <str>
                            }
                          ]
                        }
                      }
                    ]
                  }
        """

        self._check_scope("get_favorite_albums", "r_usr", flows={"device_code"})

        return self._get_json(
            f"{self.API_URL}/v1/users/{self._user_id}/favorites/albums",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
                "order": order,
                "orderDirection": order_direction,
            },
        )

    def favorite_albums(
        self,
        album_ids: Union[int, str, list[Union[int, str]]],
        country_code: str = None,
        *,
        on_artifact_not_found: str = "FAIL",
    ) -> None:
        """
        Add albums to the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        album_ids : `int`, `str`, or `list`
            TIDAL album ID(s).

            **Examples**: :code:`"251380836,275646830"` or
            :code:`[251380836, 275646830]`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        on_artifact_not_found : `str`, keyword-only, default: :code:`"FAIL"`
            Behavior when the item to be added does not exist.

            **Valid values**: :code:`"FAIL"` or :code:`"SKIP"`.
        """

        self._check_scope("favorite_albums", "r_usr", flows={"device_code"})

        self._request(
            "post",
            f"{self.API_URL}/v1/users/{self._user_id}/favorites/albums",
            params={"countryCode": self._get_country_code(country_code)},
            data={
                "albumIds": (
                    ",".join(map(str, album_ids))
                    if isinstance(album_ids, list)
                    else album_ids
                ),
                "onArtifactNotFound": on_artifact_not_found,
            },
        )

    def unfavorite_albums(
        self, album_ids: Union[int, str, list[Union[int, str]]]
    ) -> None:
        """
        Remove albums from the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        album_ids : `int`, `str`, or `list`
            TIDAL album ID(s).

            **Examples**: :code:`"251380836,275646830"` or
            :code:`[251380836, 275646830]`.
        """

        self._check_scope("unfavorite_albums", "r_usr", flows={"device_code"})

        if isinstance(album_ids, list):
            album_ids = ",".join(map(str, album_ids))
        self._request(
            "delete",
            f"{self.API_URL}/v1/users/{self._user_id}" f"/favorites/albums/{album_ids}",
        )

    ### ARTISTS ###############################################################

    def get_artist(
        self, artist_id: Union[int, str], country_code: str = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for an artist.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        artist : `dict`
            TIDAL catalog information for an artist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "name": <str>,
                    "artistTypes": [<str>],
                    "url": <str>,
                    "picture": <str>,
                    "popularity": <int>,
                    "artistRoles": [
                      {
                        "categoryId": <int>,
                        "category": <str>
                      }
                    ],
                    "mixes": {
                      "ARTIST_MIX": <str>
                    }
                  }
        """

        self._check_scope(
            "get_artist", "r_usr", flows={"device_code"}, require_authentication=False
        )

        return self._get_json(
            f"{self.API_URL}/v1/artists/{artist_id}",
            params={"countryCode": self._get_country_code(country_code)},
        )

    def get_artist_albums(
        self,
        artist_id: Union[int, str],
        country_code: str = None,
        *,
        filter: str = None,
        limit: int = 100,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for albums by an artist.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        filter : `str`, keyword-only, optional
            Subset of albums to retrieve.

            **Valid values**: :code:`"EPSANDSINGLES"` and
            :code:`"COMPILATIONS"`.

        limit : `int`, keyword-only, default: :code:`100`
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        albums : `dict`
            A dictionary containing TIDAL catalog information for
            albums by the specified artist and metadata for the
            returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "id": <int>,
                        "title": <str>,
                        "duration": <int>,
                        "streamReady": <bool>,
                        "adSupportedStreamReady": <bool>,
                        "djReady": <bool>,
                        "stemReady": <bool>,
                        "streamStartDate": <str>,
                        "allowStreaming": <bool>,
                        "premiumStreamingOnly": <bool>,
                        "numberOfTracks": <int>,
                        "numberOfVideos": <int>,
                        "numberOfVolumes": <int>,
                        "releaseDate": <str>,
                        "copyright": <str>,
                        "type": "ALBUM",
                        "version": <str>,
                        "url": <str>,
                        "cover": <str>,
                        "vibrantColor": <str>,
                        "videoCover": <str>,
                        "explicit": <bool>,
                        "upc": <str>,
                        "popularity": <int>,
                        "audioQuality": <str>,
                        "audioModes": [<str>],
                        "mediaMetadata": {
                          "tags": [<str>]
                        },
                        "artist": {
                          "id": <int>,
                          "name": <str>,
                          "type": <str>,
                          "picture": <str>
                        },
                        "artists": [
                          {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          }
                        ]
                      }
                    ]
                  }
        """

        self._check_scope(
            "get_artist_albums",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/artists/{artist_id}/albums",
            params={
                "countryCode": self._get_country_code(country_code),
                "filter": filter,
                "limit": limit,
                "offset": offset,
            },
        )

    def get_artist_top_tracks(
        self,
        artist_id: Union[int, str],
        country_code: str = None,
        *,
        limit: int = 100,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for an artist's top tracks.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`100`
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        tracks : `dict`
            A dictionary containing TIDAL catalog information for the
            artist's top tracks and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "id": <int>,
                        "title": <str>,
                        "duration": <int>,
                        "replayGain": <float>,
                        "peak": <float>,
                        "allowStreaming": <bool>,
                        "streamReady": <bool>,
                        "adSupportedStreamReady": <bool>,
                        "djReady": <bool>,
                        "stemReady": <bool>,
                        "streamStartDate": <str>,
                        "premiumStreamingOnly": <bool>,
                        "trackNumber": <int>,
                        "volumeNumber": <int>,
                        "version": <str>,
                        "popularity": <int>,
                        "copyright": <str>,
                        "url": <str>,
                        "isrc": <str>,
                        "editable": <bool>,
                        "explicit": <bool>,
                        "audioQuality": <str>,
                        "audioModes": [<str>],
                        "mediaMetadata": {
                          "tags": [<str>]
                        },
                        "artist": {
                          "id": <int>,
                          "name": <str>,
                          "type": <str>,
                          "picture": <str>
                        },
                        "artists": [
                          {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          }
                        ],
                        "album": {
                          "id": <int>,
                          "title": <str>,
                          "cover": <str>,
                          "vibrantColor": <str>,
                          "videoCover": <str>
                        },
                        "mixes": {
                          "TRACK_MIX": <str>
                        }
                      }
                    ]
                  }
        """

        self._check_scope(
            "get_artist_top_tracks",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/artists/{artist_id}/toptracks",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
            },
        )

    def get_artist_videos(
        self,
        artist_id: Union[int, str],
        country_code: str = None,
        *,
        limit: int = 100,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for an artist's videos.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`100`
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        videos : `dict`
            A dictionary containing TIDAL catalog information for the
            artist's videos and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "id": <int>,
                        "title": <str>,
                        "volumeNumber": <int>,
                        "trackNumber": <int>,
                        "releaseDate": <str>,
                        "imagePath": <str>,
                        "imageId": <str>,
                        "vibrantColor": <str>,
                        "duration": <int>,
                        "quality": <str>,
                        "streamReady": <bool>,
                        "adSupportedStreamReady": <bool>,
                        "djReady": <bool>,
                        "stemReady": <bool>,
                        "streamStartDate": <str>,
                        "allowStreaming": <bool>,
                        "explicit": <bool>,
                        "popularity": <int>,
                        "type": "Music Video",
                        "adsUrl": <str>,
                        "adsPrePaywallOnly": <bool>,
                        "artist": {
                          "id": <int>,
                          "name": <str>,
                          "type": <str>,
                          "picture": <str>
                        },
                        "artists": [
                          {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          }
                        ],
                        "album": <dict>
                      }
                    ]
                  }
        """

        self._check_scope(
            "get_artist_videos",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/artists/{artist_id}/videos",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
            },
        )

    def get_artist_mix_id(
        self, artist_id: Union[int, str], country_code: str = None
    ) -> str:
        """
        Get the ID of a curated mix of tracks based on an artist's
        works.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        mix_id : `str`
            TIDAL mix ID.

            **Example**: :code:`"000ec0b01da1ddd752ec5dee553d48"`.
        """

        self._check_scope(
            "get_artist_mix_id",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/artists/{artist_id}/mix",
            params={"countryCode": self._get_country_code(country_code)},
        )["id"]

    def get_artist_radio(
        self,
        artist_id: Union[int, str],
        country_code: str = None,
        *,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for tracks inspired by an artist's
        works.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        .. note::

           This method is functionally identical to first getting the
           artist mix ID using :meth:`get_artist_mix_id` and then
           retrieving TIDAL catalog information for the items in the mix
           using :meth:`get_mix_items`.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, optional
            Page size.

            **Default**: :code:`100`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        tracks : `dict`
            A dictionary containing TIDAL catalog information for tracks
            inspired by an artist's works and metadata for the returned
            results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "id": <int>,
                        "title": <str>,
                        "duration": <int>,
                        "replayGain": <float>,
                        "peak": <float>,
                        "allowStreaming": <bool>,
                        "streamReady": <bool>,
                        "adSupportedStreamReady": <bool>,
                        "djReady": <bool>,
                        "stemReady": <bool>,
                        "streamStartDate": <str>,
                        "premiumStreamingOnly": <bool>,
                        "trackNumber": <int>,
                        "volumeNumber": <int>,
                        "version": <str>,
                        "popularity": <int>,
                        "copyright": <str>,
                        "url": <str>,
                        "isrc": <str>,
                        "editable": <bool>,
                        "explicit": <bool>,
                        "audioQuality": <str>,
                        "audioModes": [<str>],
                        "mediaMetadata": {
                          "tags": [<str>]
                        },
                        "artist": {
                          "id": <int>,
                          "name": <str>,
                          "type": <str>,
                          "picture": <str>
                        },
                        "artists": [
                          {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          }
                        ],
                        "album": {
                          "id": <int>,
                          "title": <str>,
                          "cover": <str>,
                          "vibrantColor": <str>,
                          "videoCover": <str>
                        },
                        "mixes": {
                          "TRACK_MIX": <str>
                        }
                      }
                    ]
                  }
        """

        self._check_scope(
            "get_artist_radio",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/artists/{artist_id}/radio",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
            },
        )

    def get_artist_biography(
        self, artist_id: Union[int, str], country_code: str = None
    ) -> dict[str, str]:
        """
        Get an artist's biographical information.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        biography : `dict`
            A dictionary containing an artist's biographical information
            and its source.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "source": <str>,
                    "lastUpdated": <str>,
                    "text": <str>,
                    "summary": <str>
                  }
        """

        self._check_scope(
            "get_artist_biography",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/artists/{artist_id}/bio",
            params={"countryCode": self._get_country_code(country_code)},
        )

    def get_artist_links(
        self,
        artist_id: Union[int, str],
        country_code: str = None,
        *,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get links to websites associated with an artist.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, optional
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        links : `dict`
            A dictionary containing the artist's links and metadata for
            the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "url": <str>,
                        "siteName": <str>
                      }
                    ],
                    "source": <str>
                  }
        """

        self._check_scope(
            "get_artist_links",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/artists/{artist_id}/links",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
            },
        )

    def get_similar_artists(
        self,
        artist_id: str,
        country_code: str = None,
        *,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for artists similar to a specified
        artist.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`100`
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        artists : `dict`
            A dictionary containing TIDAL catalog information for
            artists similar to the specified artist and metadata for the
            returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "id": <int>,
                        "name": <str>,
                        "type": None,
                        "artistTypes": [<str>],
                        "url": <str>,
                        "picture": <str>,
                        "popularity": <int>,
                        "banner": <str>,
                        "artistRoles": <list>,
                        "mixes": <dict>,
                        "relationType": "SIMILAR_ARTIST"
                      }
                    ],
                    "source": "TIDAL"
                  }
        """

        self._check_scope(
            "get_similar_artists",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/artists/{artist_id}/similar",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
            },
        )

    def get_favorite_artists(
        self,
        country_code: str = None,
        *,
        limit: int = 50,
        offset: int = None,
        order: str = "DATE",
        order_direction: str = "DESC",
    ) -> None:
        """
        Get TIDAL catalog information for artists in the current user's
        collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`50`
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        order : `str`, keyword-only, default: :code:`"DATE"`
            Sorting order.

            **Valid values**: :code:`"DATE"` and :code:`"NAME"`.

        order_direction : `str`, keyword-only, default: :code:`"DESC"`
            Sorting order direction.

            **Valid values**: :code:`"DESC"` and :code:`"ASC"`.

        Returns
        -------
        artists : `dict`
            A dictionary containing TIDAL catalog information for
            artists in the current user's collection and metadata for
            the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "created": <str>,
                        "item": {
                          "id": <int>,
                          "name": <str>,
                          "artistTypes": [<str>],
                          "url": <str>,
                          "picture": <str>,
                          "popularity": <int>,
                          "artistRoles": [
                            {
                              "categoryId": <int>,
                              "category": <str>
                            }
                          ],
                          "mixes": {
                            "ARTIST_MIX": <str>
                          }
                        }
                      }
                    ]
                  }
        """

        self._check_scope("get_favorite_artists", "r_usr", flows={"device_code"})

        return self._get_json(
            f"{self.API_URL}/v1/users/{self._user_id}/favorites/artists",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
                "order": order,
                "orderDirection": order_direction,
            },
        )

    def favorite_artists(
        self,
        artist_ids: Union[int, str, list[Union[int, str]]],
        country_code: str = None,
        *,
        on_artifact_not_found: str = "FAIL",
    ) -> None:
        """
        Add artists to the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        artist_ids : `int`, `str`, or `list`
            TIDAL artist ID(s).

            **Examples**: :code:`"1566,7804"` or :code:`[1566, 7804]`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        on_artifact_not_found : `str`, keyword-only, default: :code:`"FAIL"`
            Behavior when the item to be added does not exist.

            **Valid values**: :code:`"FAIL"` or :code:`"SKIP"`.
        """

        self._check_scope("favorite_artists", "r_usr", flows={"device_code"})

        self._request(
            "post",
            f"{self.API_URL}/v1/users/{self._user_id}/favorites/artists",
            params={"countryCode": self._get_country_code(country_code)},
            data={
                "artistIds": (
                    ",".join(map(str, artist_ids))
                    if isinstance(artist_ids, list)
                    else artist_ids
                ),
                "onArtifactNotFound": on_artifact_not_found,
            },
        )

    def unfavorite_artists(
        self, artist_ids: Union[int, str, list[Union[int, str]]]
    ) -> None:
        """
        Remove artists from the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        artist_ids : `int`, `str`, or `list`
            TIDAL artist ID(s).

            **Examples**: :code:`"1566,7804"` or :code:`[1566, 7804]`.
        """

        self._check_scope("unfavorite_artists", "r_usr", flows={"device_code"})

        if isinstance(artist_ids, list):
            artist_ids = ",".join(map(str, artist_ids))
        self._request(
            "delete",
            f"{self.API_URL}/v1/users/{self._user_id}"
            f"/favorites/artists/{artist_ids}",
        )

    def get_blocked_artists(
        self, *, limit: int = 50, offset: int = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for the current user's blocked
        artists.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        limit : `int`, keyword-only, default: :code:`50`
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        artists : `dict`
            A dictionary containing TIDAL catalog information for the
            the current user's blocked artists and metadata for the
            returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "item": {
                          "id": <int>,
                          "name": <str>,
                          "type": <str>,
                          "artistTypes": [<str>],
                          "url": <str>,
                          "picture": <str>,
                          "popularity": <int>,
                          "banner": <str>,
                          "artistRoles": [
                            {
                              "categoryId": <int>,
                              "category": <str>
                            }
                          ],
                          "mixes": {
                            "ARTIST_MIX": <str>
                          }
                        },
                        "created": <str>,
                        "type": "ARTIST"
                      }
                    ]
                  }
        """

        self._check_scope("get_blocked_artists", "r_usr", flows={"device_code"})

        return self._get_json(
            f"{self.API_URL}/v1/users/{self._user_id}/blocks/artists",
            params={"limit": limit, "offset": offset},
        )

    def block_artist(self, artist_id: Union[int, str]) -> None:
        """
        Block an artist from appearing in mixes and the radio.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.
        """

        self._check_scope("block_artist", "r_usr", flows={"device_code"})

        self._request(
            "post",
            f"{self.API_URL}/v1/users/{self._user_id}/blocks/artists",
            data={"artistId": artist_id},
        )

    def unblock_artist(self, artist_id: Union[int, str]) -> None:
        """
        Unblock an artist from appearing in mixes and the radio.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.
        """

        self._check_scope("unblock_artist", "r_usr", flows={"device_code"})

        self._request(
            "delete",
            f"{self.API_URL}/v1/users/{self._user_id}" f"/blocks/artists/{artist_id}",
        )

    ### COUNTRY ###############################################################

    def get_country_code(self) -> str:
        """
        Get the country code based on the current IP address.

        Returns
        -------
        country : `str`, keyword-only, optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.
        """

        return self._get_json(f"{self.API_URL}/v1/country")["countryCode"]

    ### IMAGES ################################################################

    def get_image(
        self,
        uuid: str,
        type: str = None,
        animated: bool = False,
        *,
        width: int = None,
        height: int = None,
        filename: Union[str, pathlib.Path] = None,
    ) -> bytes:
        """
        Get (animated) cover art or image for a TIDAL item.

        .. note::

           This method is provided for convenience and is not a private
           TIDAL API endpoint.

        Parameters
        ----------
        uuid : `str`
            Image UUID.

            **Example**: :code:`"d3c4372b-a652-40e0-bdb1-fc8d032708f6"`.

        type : `str`
            Item type.

            **Valid values**: :code:`"artist"`, :code:`"album"`,
            :code:`"playlist"`, :code:`"track"`, :code:`"userProfile"`,
            and :code:`"video"`.

        animated : `bool`, default: :code:`False`
            Specifies whether the image is animated.

        width : `int`, keyword-only, optional
            Valid image width for the item type. If not specified, the
            default size for the item type is used.

        height : `int`, keyword-only, optional
            Valid image height for the item type. If not specified, the
            default size for the item type is used.

        filename : `str` or `pathlib.Path`, keyword-only, optional
            Filename with the :code:`.jpg` or :code:`.mp4` extension. If
            specified, the image is saved to a file instead.

        Returns
        -------
        image : `bytes`
            Image data. If :code:`save=True`, the stream data is saved
            to an image or video file and its filename is returned
            instead.
        """

        IMAGE_SIZES = {
            "artist": (750, 750),
            "album": (1280, 1280),
            "playlist": (1080, 1080),
            "track": (1280, 1280),
            "userProfile": (1080, 1080),
            "video": (640, 360),
        }

        if width is None or height is None:
            if type and type in IMAGE_SIZES.keys():
                width, height = IMAGE_SIZES[type.lower()]
            else:
                emsg = (
                    "Either the image dimensions or a valid item "
                    "type must be specified."
                )
                raise ValueError(emsg)

        if animated:
            extension = ".mp4"
            media_type = "videos"
        else:
            extension = ".jpg"
            media_type = "images"

        with self.session.get(
            f"{self.RESOURCES_URL}/{media_type}"
            f"/{uuid.replace('-', '/')}"
            f"/{width}x{height}.{extension}"
        ) as r:
            image = r.content

        if filename:
            if not isinstance(filename, pathlib.Path):
                filename = pathlib.Path(filename)
            if not filename.name.endswith(extension):
                filename += extension
            with open(filename, "wb") as f:
                f.write(image)
        else:
            return image

    ### MIXES #################################################################

    def get_mix_items(self, mix_id: str, country_code: str = None) -> dict[str, Any]:
        """
        Get TIDAL catalog information for items (tracks and videos) in
        a mix.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        mix_id : `str`
            TIDAL mix ID.

            **Example**: :code:`"000ec0b01da1ddd752ec5dee553d48"`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        items : `dict`
            A dictionary containing TIDAL catalog information for
            tracks and videos in the specified mix and metadata for
            the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "item": {
                          "id": <int>,
                          "title": <str>,
                          "duration": <int>,
                          "replayGain": <float>,
                          "peak": <float>,
                          "allowStreaming": <bool>,
                          "streamReady": <bool>,
                          "adSupportedStreamReady": <bool>,
                          "djReady": <bool>,
                          "stemReady": <bool>,
                          "streamStartDate": <str>,
                          "premiumStreamingOnly": <bool>,
                          "trackNumber": <int>,
                          "volumeNumber": >int>,
                          "version": <str>,
                          "popularity": <int>,
                          "copyright": <str>,
                          "url": <str>,
                          "isrc": <str>,
                          "editable": <bool>,
                          "explicit": <bool>,
                          "audioQuality": <str>,
                          "audioModes": [<str>],
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "artist": {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>,
                              "picture": <str>
                            }
                          ],
                          "album": {
                            "id": <int>,
                            "title": <str>,
                            "cover": <str>,
                            "vibrantColor": <str>,
                            "videoCover": <str>
                          },
                          "mixes": {
                            "TRACK_MIX": <str>
                          }
                        },
                        "type": "track"
                      }
                    ]
                  }
        """

        self._check_scope(
            "get_mix_items",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/mixes/{mix_id}/items",
            params={"countryCode": self._get_country_code(country_code)},
        )

    def get_favorite_mixes(
        self, *, ids: bool = False, limit: int = 50, cursor: str = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for or IDs of mixes in the
        current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        ids : `bool`, keyword-only, default: :code:`False`
            Determine whether TIDAL catalog information about the mixes
            (:code:`False`) or the mix IDs (:code:`True`) are
            returned.

        limit : `int`, keyword-only, default: :code:`50`
            Page size.

            **Example**: :code:`10`.

        cursor : `str`, keyword-only, optional
            Cursor position of the last item in previous search results.
            Use with `limit` to get the next page of search results.

        Returns
        -------
        mixes : `dict`
            A dictionary containing the TIDAL catalog information for or
            IDs of the mixes in the current user's collection and the
            cursor position.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "dateAdded": <str>,
                        "title": <str>,
                        "id": <str>,
                        "mixType": <str>,
                        "updated": <str>,
                        "subTitleTextInfo": {
                          "text": <str>,
                          "color": <str>
                        },
                        "images": {
                          "SMALL": {
                            "width": <int>,
                            "height": <int>,
                            "url": <str>
                          },
                          "MEDIUM": {
                            "width": <int>,
                            "height": <int>,
                            "url": <str>
                          },
                          "LARGE": {
                            "width": <int>,
                            "height": <int>,
                            "url": <str>
                          },
                        },
                        "detailImages": {
                          "SMALL": {
                            "width": <int>,
                            "height": <int>,
                            "url": <str>
                          },
                          "MEDIUM": {
                            "width": <int>,
                            "height": <int>,
                            "url": <str>
                          },
                          "LARGE": {
                            "width": <int>,
                            "height": <int>,
                            "url": <str>
                          }
                        },
                        "master": <bool>,
                        "subTitle": <str>,
                        "titleTextInfo": {
                          "text": <str>,
                          "color": <str>
                        }
                      }
                    ],
                    "cursor": <str>,
                    "lastModifiedAt": <str>
                  }
        """

        self._check_scope("get_favorite_mixes", "r_usr", flows={"device_code"})

        url = f"{self.API_URL}/v2/favorites/mixes"
        if ids:
            url += "/ids"
        return self._get_json(url, params={"limit": limit, "cursor": cursor})

    def favorite_mixes(
        self, mix_ids: Union[str, list[str]], *, on_artifact_not_found: str = "FAIL"
    ) -> None:
        """
        Add mixes to the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        mix_ids : `str` or `list`
            TIDAL mix ID(s).

            **Examples**: :code:`"000ec0b01da1ddd752ec5dee553d48,\
            000dd748ceabd5508947c6a5d3880a"` or
            :code:`["000ec0b01da1ddd752ec5dee553d48",
            "000dd748ceabd5508947c6a5d3880a"]`

        on_artifact_not_found : `str`, keyword-only, default: :code:`"FAIL"`
            Behavior when the item to be added does not exist.

            **Valid values**: :code:`"FAIL"` or :code:`"SKIP"`.
        """

        self._check_scope("favorite_mixes", "r_usr", flows={"device_code"})

        self._request(
            "put",
            f"{self.API_URL}/v2/favorites/mixes/add",
            data={"mixIds": mix_ids, "onArtifactNotFound": on_artifact_not_found},
        )

    def unfavorite_mixes(self, mix_ids: Union[str, list[str]]) -> None:
        """
        Remove mixes from the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        mix_ids : `str` or `list`
            TIDAL mix ID(s).

            **Examples**: :code:`"000ec0b01da1ddd752ec5dee553d48,\
            000dd748ceabd5508947c6a5d3880a"` or
            :code:`["000ec0b01da1ddd752ec5dee553d48",
            "000dd748ceabd5508947c6a5d3880a"]`
        """

        self._check_scope("unfavorite_mixes", "r_usr", flows={"device_code"})

        self._request(
            "put", f"{self.API_URL}/v2/favorites/mixes/remove", data={"mixIds": mix_ids}
        )

    ### PAGES #################################################################

    def get_album_page(
        self,
        album_id: Union[int, str],
        country_code: str = None,
        *,
        device_type: str = "BROWSER",
    ) -> dict[str, Any]:
        """
        Get the TIDAL page for an album.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        album_id : `int` or `str`
            TIDAL album ID.

            **Example**: :code:`251380836`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        device_type : `str`, keyword-only, default: :code:`"BROWSER"`
            Device type.

            .. container::

               **Valid values**:

               * :code:`"BROWSER"` for a web browser.
               * :code:`"DESKTOP"` for the desktop TIDAL application.
               * :code:`"PHONE"` for the mobile TIDAL application.
               * :code:`"TV"` for the smart TV TIDAL application.

        Returns
        -------
        page : `dict`
            A dictionary containing the page ID, title, and submodules.
        """

        self._check_scope(
            "get_album_page",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        if device_type not in (DEVICE_TYPES := {"BROWSER", "DESKTOP", "PHONE", "TV"}):
            emsg = "Invalid device type. Valid values: " f"{', '.join(DEVICE_TYPES)}."
            raise ValueError(emsg)

        return self._get_json(
            f"{self.API_URL}/v1/pages/album",
            params={
                "albumId": album_id,
                "countryCode": self._get_country_code(country_code),
                "deviceType": device_type,
            },
        )

    def get_artist_page(
        self,
        artist_id: Union[int, str],
        country_code: str = None,
        *,
        device_type: str = "BROWSER",
    ) -> dict[str, Any]:
        """
        Get the TIDAL page for an artist.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        artist_id : `int` or `str`
            TIDAL artist ID.

            **Example**: :code:`1566`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        device_type : `str`, keyword-only, default: :code:`"BROWSER"`
            Device type.

            .. container::

               **Valid values**:

               * :code:`"BROWSER"` for a web browser.
               * :code:`"DESKTOP"` for the desktop TIDAL application.
               * :code:`"PHONE"` for the mobile TIDAL application.
               * :code:`"TV"` for the smart TV TIDAL application.

        Returns
        -------
        page : `dict`
            A dictionary containing the page ID, title, and submodules.
        """

        self._check_scope(
            "get_artist_page",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        if device_type not in (DEVICE_TYPES := {"BROWSER", "DESKTOP", "PHONE", "TV"}):
            emsg = "Invalid device type. Valid values: " f"{', '.join(DEVICE_TYPES)}."
            raise ValueError(emsg)

        return self._get_json(
            f"{self.API_URL}/v1/pages/artist",
            params={
                "artistID": artist_id,
                "countryCode": self._get_country_code(country_code),
                "deviceType": device_type,
            },
        )

    def get_mix_page(
        self, mix_id: str, country_code: str = None, *, device_type: str = "BROWSER"
    ) -> dict[str, Any]:
        """
        Get the TIDAL page for a mix.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        mix_id : `str`
            TIDAL mix ID.

            **Example**: :code:`"000ec0b01da1ddd752ec5dee553d48"`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        device_type : `str`, keyword-only, default: :code:`"BROWSER"`
            Device type.

            .. container::

               **Valid values**:

               * :code:`"BROWSER"` for a web browser.
               * :code:`"DESKTOP"` for the desktop TIDAL application.
               * :code:`"PHONE"` for the mobile TIDAL application.
               * :code:`"TV"` for the smart TV TIDAL application.

        Returns
        -------
        page : `dict`
            A dictionary containing the page ID, title, and submodules.
        """

        self._check_scope(
            "get_mix_page", "r_usr", flows={"device_code"}, require_authentication=False
        )

        if device_type not in (DEVICE_TYPES := {"BROWSER", "DESKTOP", "PHONE", "TV"}):
            emsg = "Invalid device type. Valid values: " f"{', '.join(DEVICE_TYPES)}."
            raise ValueError(emsg)

        return self._get_json(
            f"{self.API_URL}/v1/pages/mix",
            params={
                "mixId": mix_id,
                "countryCode": self._get_country_code(country_code),
                "deviceType": device_type,
            },
        )

    def get_video_page(
        self,
        video_id: Union[int, str],
        country_code: str = None,
        *,
        device_type: str = "BROWSER",
    ) -> dict[str, Any]:
        """
        Get the TIDAL page for a video.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        video_id : `int` or `str`
            TIDAL video ID.

            **Example**: :code:`75623239`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        device_type : `str`, keyword-only, default: :code:`"BROWSER"`
            Device type.

            .. container::

               **Valid values**:

               * :code:`"BROWSER"` for a web browser.
               * :code:`"DESKTOP"` for the desktop TIDAL application.
               * :code:`"PHONE"` for the mobile TIDAL application.
               * :code:`"TV"` for the smart TV TIDAL application.

        Returns
        -------
        page : `dict`
            A dictionary containing the page ID, title, and submodules.
        """

        self._check_scope(
            "get_video_page",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        if device_type not in (DEVICE_TYPES := {"BROWSER", "DESKTOP", "PHONE", "TV"}):
            emsg = "Invalid device type. Valid values: " f"{', '.join(DEVICE_TYPES)}."
            raise ValueError(emsg)

        return self._get_json(
            f"{self.API_URL}/v1/pages/videos",
            params={
                "videoId": video_id,
                "countryCode": self._get_country_code(country_code),
                "deviceType": device_type,
            },
        )

    ### PLAYLISTS #############################################################

    def get_playlist(
        self, playlist_uuid: str, country_code: str = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a playlist.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        playlist_uuid : `str`
            TIDAL playlist UUID.

            **Example**: :code:`"36ea71a8-445e-41a4-82ab-6628c581535d"`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        playlist : `dict`
            TIDAL catalog information for a playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "uuid": <str>,
                    "title": <str>,
                    "numberOfTracks": <int>,
                    "numberOfVideos": <int>,
                    "creator": {
                      "id": <int>
                    },
                    "description": <str>,
                    "duration": <int>,
                    "lastUpdated": <str>,
                    "created": <str>,
                    "type": <str>,
                    "publicPlaylist": <bool>,
                    "url": <str>,
                    "image": <str>,
                    "popularity": <int>,
                    "squareImage": <str>,
                    "promotedArtists": [
                      {
                        "id": <int>,
                        "name": <str>,
                        "type": <str>,
                        "picture": <str>,
                      }
                    ],
                    "lastItemAddedAt": <str>
                  }
        """

        self._check_scope(
            "get_playlist", "r_usr", flows={"device_code"}, require_authentication=False
        )

        return self._get_json(
            f"{self.API_URL}/v1/playlists/{playlist_uuid}",
            params={"countryCode": self._get_country_code(country_code)},
        )

    def get_playlist_etag(self, playlist_uuid: str, country_code: str = None) -> str:
        """
        Get the entity tag (ETag) for a playlist.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        .. note::

           This method is provided for convenience and is not a private
           TIDAL API endpoint.

        Parameters
        ----------
        playlist_uuid : `str`
            TIDAL playlist UUID.

            **Example**: :code:`"36ea71a8-445e-41a4-82ab-6628c581535d"`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        etag : `str`
            ETag for a playlist.

            **Example**: :code:`"1698984074453"`.
        """

        self._check_scope(
            "get_playlist_etag",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        r = self._request(
            "get",
            f"{self.API_URL}/v1/playlists/{playlist_uuid}",
            params={"countryCode": self._get_country_code(country_code)},
        )
        return r.headers["ETag"].replace('"', "")

    def get_playlist_items(
        self,
        playlist_uuid: str,
        country_code: str = None,
        *,
        limit: int = 100,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for items (tracks and videos) in
        a playlist.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        playlist_uuid : `str`
            TIDAL playlist UUID.

            **Example**: :code:`"36ea71a8-445e-41a4-82ab-6628c581535d"`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`100`
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        items : `dict`
            A dictionary containing TIDAL catalog information for
            tracks and videos in the specified playlist and metadata for
            the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "item": {
                          "id": <int>,
                          "title": <str>,
                          "duration": <int>,
                          "replayGain": <float>,
                          "peak": <float>,
                          "allowStreaming": <bool>,
                          "streamReady": <bool>,
                          "adSupportedStreamReady": <bool>,
                          "djReady": <bool>,
                          "stemReady": <bool>,
                          "streamStartDate": <str>,
                          "premiumStreamingOnly": <bool>,
                          "trackNumber": <int>,
                          "volumeNumber": >int>,
                          "version": <str>,
                          "popularity": <int>,
                          "copyright": <str>,
                          "url": <str>,
                          "isrc": <str>,
                          "editable": <bool>,
                          "explicit": <bool>,
                          "audioQuality": <str>,
                          "audioModes": [<str>],
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "artist": {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>,
                              "picture": <str>
                            }
                          ],
                          "album": {
                            "id": <int>,
                            "title": <str>,
                            "cover": <str>,
                            "vibrantColor": <str>,
                            "videoCover": <str>
                          },
                          "mixes": {
                            "TRACK_MIX": <str>
                          }
                        },
                        "type": "track"
                      }
                    ]
                  }
        """

        self._check_scope(
            "get_playlist_items",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/playlists/{playlist_uuid}/items",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
            },
        )

    def get_playlist_recommendations(
        self,
        playlist_uuid: str,
        country_code: str = None,
        *,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for recommended tracks based on a
        playlist's items.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        playlist_uuid : `str`
            TIDAL playlist UUID.

            **Example**: :code:`"36ea71a8-445e-41a4-82ab-6628c581535d"`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, optional
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        items : `dict`
            A dictionary containing TIDAL catalog information for
            recommended tracks and videos and metadata for the returned
            results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "item": {
                          "id": <int>,
                          "title": <str>,
                          "duration": <int>,
                          "replayGain": <float>,
                          "peak": <float>,
                          "allowStreaming": <bool>,
                          "streamReady": <bool>,
                          "adSupportedStreamReady": <bool>,
                          "djReady": <bool>,
                          "stemReady": <bool>,
                          "streamStartDate": <str>,
                          "premiumStreamingOnly": <bool>,
                          "trackNumber": <int>,
                          "volumeNumber": >int>,
                          "version": <str>,
                          "popularity": <int>,
                          "copyright": <str>,
                          "url": <str>,
                          "isrc": <str>,
                          "editable": <bool>,
                          "explicit": <bool>,
                          "audioQuality": <str>,
                          "audioModes": [<str>],
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "artist": {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>,
                              "picture": <str>
                            }
                          ],
                          "album": {
                            "id": <int>,
                            "title": <str>,
                            "cover": <str>,
                            "vibrantColor": <str>,
                            "videoCover": <str>
                          },
                          "mixes": {
                            "TRACK_MIX": <str>
                          }
                        },
                        "type": "track"
                      }
                    ]
                  }
        """

        self._check_scope(
            "get_playlist_recommendations", "r_usr", flows={"device_code"}
        )

        return self._get_json(
            f"{self.API_URL}/v1/playlists/{playlist_uuid}" "/recommendations/items",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
            },
        )

    def favorite_playlists(
        self, playlist_uuids: Union[str, list[str]], *, folder_id: str = "root"
    ) -> None:
        """
        Add playlists to the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        playlist_uuids : `str` or `list`
            TIDAL playlist UUID(s).

            **Example**: :code:`["36ea71a8-445e-41a4-82ab-6628c581535d",
            "4261748a-4287-4758-aaab-6d5be3e99e52"]`.

        folder_id : `str`, keyword-only, default: :code:`"root"`
            ID of the folder to move the playlist into. To place a
            playlist directly under "My Playlists", use
            :code:`folder_id="root"`.
        """

        self._check_scope("favorite_playlists", "r_usr", flow={"device_code"})

        self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/add-favorites",
            params={"uuids": playlist_uuids, "folderId": folder_id},
        )

    def move_playlist(self, playlist_uuid: str, folder_id: str) -> None:
        """
        Move a playlist in the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        playlist_uuid : `str`
            TIDAL playlist UUID.

            **Example**: :code:`"36ea71a8-445e-41a4-82ab-6628c581535d"`.

        folder_id : `str`
            ID of the folder to move the playlist into. To place a
            playlist directly under "My Playlists", use
            :code:`folder_id="root"`.
        """

        self._check_scope("move_playlist", "r_usr", flows={"device_code"})

        self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/move",
            params={"folderId": folder_id, "trns": f"trn:playlist:{playlist_uuid}"},
        )

    def unfavorite_playlist(self, playlist_uuid: str) -> None:
        """
        Remove a playlist from the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        playlist_uuid : `str`
            TIDAL playlist UUID.

            **Example**: :code:`"36ea71a8-445e-41a4-82ab-6628c581535d"`.
        """

        self._check_scope("unfavorite_playlist", "r_usr", flows={"device_code"})

        self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/remove",
            params={"trns": f"trn:playlist:{playlist_uuid}"},
        )

    def get_user_playlist(self, playlist_uuid: str) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a user playlist.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        playlist_uuid : `str`
            TIDAL user playlist UUID.

            **Example**: :code:`"e09ab9ce-2e87-41b8-b404-3cd712bf706e"`.

        Returns
        -------
        playlist : `dict`
            TIDAL catalog information for a user playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "playlist": {
                      "uuid": <str>,
                      "type": "USER",
                      "creator": {
                        "id": <int>,
                        "name": <str>,
                        "picture": <str>,
                        "type": "USER"
                      },
                      "contentBehavior": <str>,
                      "sharingLevel": <str>,
                      "status": <str>,
                      "source": <str>,
                      "title": <str>,
                      "description": <str>,
                      "image": <str>,
                      "squareImage": <str>,
                      "url": <str>,
                      "created": <str>,
                      "lastUpdated": <str>,
                      "lastItemAddedAt": <str>,
                      "duration": <int>,
                      "numberOfTracks": <int>,
                      "numberOfVideos": <int>,
                      "promotedArtists": [],
                      "trn": <str>,
                    },
                    "followInfo": {
                      "nrOfFollowers": <int>,
                      "tidalResourceName": <str>,
                      "followed": <bool>,
                      "followType": "PLAYLIST"
                    },
                    "profile": {
                      "userId": <int>,
                      "name": <str>,
                      "color": [<str>]
                    }
                  }
        """

        self._check_scope("get_user_playlist", "r_usr", flows={"device_code"})

        return self._get_json(f"{self.API_URL}/v2/user-playlists/{playlist_uuid}")

    def get_user_playlists(
        self, user_id: Union[int, str] = None, *, limit: int = 50, cursor: str = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for playlists created by a TIDAL
        user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        user_id : `str`
            TIDAL user ID. If not specified, the ID associated with the
            user account in the current session is used.

        limit : `int`, keyword-only, default: :code:`50`
            Page size.

            **Example**: :code:`10`.

        cursor : `str`, keyword-only, optional
            Cursor position of the last item in previous search results.
            Use with `limit` to get the next page of search results.

        Returns
        -------
        playlists : `dict`
            A dictionary containing the user's playlists and the cursor
            position.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "playlist": {
                          "uuid": <str>,
                          "type": "USER",
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": "USER"
                          },
                          "contentBehavior": <str>,
                          "sharingLevel": <str>,
                          "status": <str>,
                          "source": <str>,
                          "title": <str>,
                          "description": <str>,
                          "image": <str>,
                          "squareImage": <str>,
                          "url": <str>,
                          "created": <str>,
                          "lastUpdated": <str>,
                          "lastItemAddedAt": <str>,
                          "duration": <int>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "promotedArtists": [],
                          "trn": <str>,
                        },
                        "followInfo": {
                          "nrOfFollowers": <int>,
                          "tidalResourceName": <str>,
                          "followed": <bool>,
                          "followType": "PLAYLIST"
                        },
                        "profile": {
                          "userId": <int>,
                          "name": <str>,
                          "color": [<str>]
                        }
                      }
                    ],
                    "cursor": <str>
                  }
        """

        self._check_scope("get_user_playlists", "r_usr", flows={"device_code"})

        if user_id is None:
            user_id = self._user_id
        return self._get_json(
            f"{self.API_URL}/v2/user-playlists/{user_id}/public",
            params={"limit": limit, "cursor": cursor},
        )

    def get_personal_playlists(
        self, country_code: str = None, *, limit: int = 50, offset: int = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for playlists created by the
        current user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`50`
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        playlists : `dict`
            TIDAL catalog information for a user playlists created by
            the current user and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "uuid": <str>",
                        "title": <str>,
                        "numberOfTracks": <int>,
                        "numberOfVideos": <int>,
                        "creator": {
                          "id": <int>
                        },
                        "description": <str>,
                        "duration": <int>,
                        "lastUpdated": <str>,
                        "created": <str>,
                        "type": "USER",
                        "publicPlaylist": <bool>,
                        "url": <str>,
                        "image": <str>,
                        "popularity": <int>,
                        "squareImage": <str>,
                        "promotedArtists": [],
                        "lastItemAddedAt": <str>
                      }
                    ]
                  }
        """

        self._check_scope("get_personal_playlists", "r_usr", flows={"device_code"})

        return self._get_json(
            f"{self.API_URL}/v1/users/{self._user_id}/playlists",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
            },
        )

    def create_playlist(
        self,
        name: str,
        *,
        description: str = None,
        folder_uuid: str = "root",
        public: bool = None,
    ) -> dict[str, Any]:
        """
        Create a user playlist.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        name : `str`
            Playlist name.

        description : `str`, keyword-only, optional
            Brief playlist description.

        folder_uuid : `str`, keyword-only, default: :code:`"root"`
            UUID of the folder the new playlist will be placed in. To
            place a playlist directly under "My Playlists", use
            :code:`folder_id="root"`.

        public : `bool`, keyword-only, optional
            Determines whether the playlist is public (:code:`True`) or
            private (:code:`False`).

        Returns
        -------
        playlist : `dict`
            TIDAL catalog information for the newly created playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "trn": <str>,
                    "itemType": "PLAYLIST",
                    "addedAt": <str>,
                    "lastModifiedAt": <str>,
                    "name": <str>,
                    "parent": <str>,
                    "data": {
                      "uuid": <str>,
                      "type": "USER",
                      "creator": {
                        "id": <int>,
                        "name": <str>,
                        "picture": <str>,
                        "type": "USER"
                      },
                      "contentBehavior": <str>,
                      "sharingLevel": <str>,
                      "status": "READY",
                      "source": <str>,
                      "title": <str>,
                      "description": <str>,
                      "image": <str>,
                      "squareImage": <str>,
                      "url": <str>,
                      "created": <str>,
                      "lastUpdated": <str>,
                      "lastItemAddedAt": <str>,
                      "duration": <int>,
                      "numberOfTracks": <int>,
                      "numberOfVideos": <int>,
                      "promotedArtists": <list>,
                      "trn": <str>,
                      "itemType": "PLAYLIST"
                    }
                  }
        """

        self._check_scope("create_playlist", "r_usr", flows={"device_code"})

        return self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/create-playlist",
            params={
                "name": name,
                "description": description,
                "folderId": folder_uuid,
                "isPublic": public,
            },
        ).json()

    def update_playlist(
        self, playlist_uuid: str, *, title: str = None, description: str = None
    ) -> None:
        """
        Update the title or description of a playlist owned by the
        current user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        playlist_uuid : `str`
            TIDAL playlist UUID.

            **Example**: :code:`"e09ab9ce-2e87-41b8-b404-3cd712bf706e"`.

        title : `str`, keyword-only, optional
            New playlist title.

        description : `str`, keyword-only, optional
            New playlist description.
        """

        self._check_scope("update_playlist", "r_usr", flows={"device_code"})

        if title is None and description is None:
            wmsg = "No changes were specified or made to the playlist."
            warnings.warn(wmsg)
            return

        data = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        self._request("post", f"{self.API_URL}/v1/playlists/{playlist_uuid}", data=data)

    def set_playlist_privacy(self, playlist_uuid: str, public: bool) -> None:
        """
        Set the privacy of a playlist owned by the current user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        playlist_uuid : `str`
            TIDAL playlist UUID.

            **Example**: :code:`"e09ab9ce-2e87-41b8-b404-3cd712bf706e"`.

        public : `bool`
            Determines whether the playlist is public (:code:`True`) or
            private (:code:`False`).
        """

        self._check_scope("set_playlist_privacy", "r_usr", flows={"device_code"})

        self._request(
            "put",
            f"{self.API_URL}/v2/playlists/{playlist_uuid}/set-"
            f"{'public' if public else 'private'}",
        )

    def add_playlist_items(
        self,
        playlist_uuid: str,
        items: Union[int, str, list[Union[int, str]]] = None,
        *,
        from_playlist_uuid: str = None,
        on_duplicate: str = "FAIL",
        on_artifact_not_found: str = "FAIL",
    ) -> None:
        """
        Add items to a playlist owned by the current user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        playlist_uuid : `str`
            TIDAL playlist UUID.

            **Example**: :code:`"e09ab9ce-2e87-41b8-b404-3cd712bf706e"`.

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

        on_artifact_not_found : `str`, keyword-only, default: :code:`"FAIL"`
            Behavior when the item to be added does not exist.

            **Valid values**: :code:`"FAIL"`.
        """

        self._check_scope("add_playlist_items", "r_usr", flows={"device_code"})

        if items is None and from_playlist_uuid is None:
            wmsg = "No changes were specified or made to the playlist."
            warnings.warn(wmsg)
            return

        data = {
            "onArtifactNotFound": on_artifact_not_found,
            "onDuplicate": on_duplicate,
        }
        if items:
            data |= {"trackIds": items}
        else:
            data |= {"fromPlaylistUuid": from_playlist_uuid}
        self._request(
            "post",
            f"{self.API_URL}/v1/playlists/{playlist_uuid}/items",
            data=data,
            headers={"If-None-Match": self.get_playlist_etag(playlist_uuid)},
        )

    def move_playlist_item(
        self, playlist_uuid: str, from_index: Union[int, str], to_index: Union[int, str]
    ) -> None:
        """
        Move an item in a playlist owned by the current user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        playlist_uuid : `str`
            TIDAL playlist UUID.

            **Example**: :code:`"e09ab9ce-2e87-41b8-b404-3cd712bf706e"`.

        from_index : `int` or `str`
            Current item index.

        to_index : `int` or `str`
            Desired item index.
        """

        self._check_scope("move_playlist_item", "r_usr", flows={"device_code"})

        self._request(
            "post",
            f"{self.API_URL}/v1/playlists/{playlist_uuid}/items/{from_index}",
            params={"toIndex": to_index},
            headers={"If-None-Match": self.get_playlist_etag(playlist_uuid)},
        )

    def delete_playlist_item(self, playlist_uuid: str, index: Union[int, str]) -> None:
        """
        Delete an item from a playlist owned by the current user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        playlist_uuid : `str`
            TIDAL playlist UUID.

            **Example**: :code:`"e09ab9ce-2e87-41b8-b404-3cd712bf706e"`.

        index : `int` or `str`
            Item index.
        """

        self._check_scope("delete_playlist_item", "r_usr", flows={"device_code"})

        self._request(
            "delete",
            f"{self.API_URL}/v1/playlists/{playlist_uuid}/items/{index}",
            headers={"If-None-Match": self.get_playlist_etag(playlist_uuid)},
        )

    def delete_playlist(self, playlist_uuid: str) -> None:
        """
        Delete a playlist owned by the current user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        playlist_uuid : `str`
            TIDAL playlist UUID.

            **Example**: :code:`"e09ab9ce-2e87-41b8-b404-3cd712bf706e"`.
        """

        self._check_scope("delete_playlist", "r_usr", flows={"device_code"})

        self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/remove",
            params={"trns": f"trn:playlist:{playlist_uuid}"},
        )

    def get_personal_playlist_folders(
        self,
        folder_uuid: str = None,
        *,
        flattened: bool = False,
        include_only: str = None,
        limit: int = 50,
        order: str = "DATE",
        order_direction: str = "DESC",
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a playlist folder (and
        optionally, playlists and other playlist folders in it) created
        by the current user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        folder_uuid : `str`, optional
            UUID of the folder in which to look for playlists and other
            folders. If not specified, all folders and playlists in "My
            Playlists" are returned.

        flattened : `bool`, keyword-only, default: :code:`False`
            Determines whether the results are flattened into a list.

        include_only : `str`, keyword-only, optional
            Type of playlist-related item to return.

            **Valid values**: :code:`"FAVORITE_PLAYLIST"`,
            :code:`"FOLDER"`, and :code:`"PLAYLIST"`.

        limit : `int`, keyword-only, default: :code:`50`
            Page size.

            **Example**: :code:`10`.

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

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "lastModifiedAt": <str>,
                    "items": [
                      {
                        "trn": <str>,
                        "itemType": "FOLDER",
                        "addedAt": <str>,
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "parent": <str>,
                        "data": {
                          "trn": <str>,
                          "name": <str>,
                          "createdAt": <str>,
                          "lastModifiedAt": <str>,
                          "totalNumberOfItems": <int>,
                          "id": <str>,
                          "itemType": "FOLDER"
                        }
                      }
                    ],
                    "totalNumberOfItems": <int>,
                    "cursor": <str>
                  }
        """

        self._check_scope(
            "get_personal_playlist_folders", "r_usr", flows={"device_code"}
        )

        if include_only and include_only not in (
            ALLOWED_INCLUDES := {"FAVORITE_PLAYLIST", "FOLDER", "PLAYLIST"}
        ):
            emsg = (
                "Invalid include type. Valid values: " f"{', '.join(ALLOWED_INCLUDES)}."
            )
            raise ValueError(emsg)

        url = f"{self.API_URL}/v2/my-collection/playlists/folders"
        if flattened:
            url += "/flattened"
        return self._get_json(
            url,
            params={
                "folderId": folder_uuid if folder_uuid else "root",
                "limit": limit,
                "includeOnly": include_only,
                "order": order,
                "orderDirection": order_direction,
            },
        )

    def create_playlist_folder(self, name: str, *, folder_uuid: str = "root") -> None:
        """
        Create a user playlist folder.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        name : `str`
            Playlist folder name.

        folder_uuid : `str`, keyword-only, default: :code:`"root"`
            UUID of the folder in which the new playlist folder should
            be created in. To create a folder directly under "My
            Playlists", use :code:`folder_id="root"`.
        """

        self._check_scope("create_playlist_folder", "r_usr", flows={"device_code"})

        self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/create-folder",
            params={"name": name, "folderId": folder_uuid},
        )

    def delete_playlist_folder(self, folder_uuid: str) -> None:
        """
        Delete a playlist folder owned by the current user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        folder_uuid : `str`
            TIDAL playlist folder UUID.

            **Example**: :code:`"92b3c1ea-245a-4e5a-a5a4-c215f7a65b9f"`.
        """

        self._check_scope("delete_playlist_folder", "r_usr", flows={"device_code"})

        self._request(
            "put",
            f"{self.API_URL}/v2/my-collection/playlists/folders/remove",
            params={"trns": f"trn:folder:{folder_uuid}"},
        )

    ### SEARCH ################################################################

    def search(
        self,
        query: str,
        country_code: str = None,
        *,
        type: str = None,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Search for albums, artists, tracks, and videos.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        query : `str`
            Search query.

            **Example**: :code:`"Beyoncé"`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        type : `str`, keyword-only, optional
            Target search type. Searches for all types if not specified.

            **Valid values**: :code:`"ALBUMS"`, :code:`"ARTISTS"`,
            :code:`"TRACKS"`, :code:`"VIDEOS"`.

        limit : `int`, keyword-only, optional
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        results : `dict`
            A dictionary containing TIDAL catalog information for
            albums, artists, tracks, and videos matching the search
            query, and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "artists": {
                      "limit": <int>,
                      "offset": <int>,
                      "totalNumberOfItems": <int>,
                      "items": [
                        {
                          "id": <int>,
                          "name": <str>,
                          "artistTypes": [<str>],
                          "url": <str>,
                          "picture": <str>,
                          "popularity": <int>,
                          "artistRoles": [
                            {
                              "categoryId": <int>,
                              "category": <str>
                            }
                          ],
                          "mixes": {
                            "ARTIST_MIX": <str>
                          }
                        }
                      ]
                    },
                    "albums": {
                      "limit": <int>,
                      "offset": <int>,
                      "totalNumberOfItems": <int>,
                      "items": [
                        {
                          "id": <int>,
                          "title": <str>,
                          "duration": <int>,
                          "streamReady": <bool>,
                          "adSupportedStreamReady": <bool>,
                          "djReady": <bool>,
                          "stemReady": <bool>,
                          "streamStartDate": <str>,
                          "allowStreaming": <bool>,
                          "premiumStreamingOnly": <bool>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "numberOfVolumes": <int>,
                          "releaseDate": <str>,
                          "copyright": <str>,
                          "type": "ALBUM",
                          "version": <str>,
                          "url": <str>,
                          "cover": <str>,
                          "vibrantColor": <str>,
                          "videoCover": <str>,
                          "explicit": <bool>,
                          "upc": <str>,
                          "popularity": <int>,
                          "audioQuality": <str>,
                          "audioModes": [<str>],
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "artist": {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>,
                              "picture": <str>
                            }
                          ]
                        }
                      ]
                    },
                    "playlists": {
                      "limit": <int>,
                      "offset": <int>,
                      "totalNumberOfItems": <int>,
                      "items": [
                        {
                          "uuid": <str>,
                          "title": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "creator": {
                            "id": <int>
                          },
                          "description": <str>,
                          "duration": <int>,
                          "lastUpdated": <str>,
                          "created": <str>,
                          "type": <str>,
                          "publicPlaylist": <bool>,
                          "url": <str>,
                          "image": <str>,
                          "popularity": <int>,
                          "squareImage": <str>,
                          "promotedArtists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>,
                              "picture": <str>,
                            }
                          ],
                          "lastItemAddedAt": <str>
                        }
                      ]
                    },
                    "tracks": {
                      "limit": <int>,
                      "offset": <int>,
                      "totalNumberOfItems": <int>,
                      "items": [
                        {
                          "id": <int>,
                          "title": <str>,
                          "duration": <int>,
                          "replayGain": <float>,
                          "peak": <float>,
                          "allowStreaming": <bool>,
                          "streamReady": <bool>,
                          "adSupportedStreamReady": <bool>,
                          "djReady": <bool>,
                          "stemReady": <bool>,
                          "streamStartDate": <str>,
                          "premiumStreamingOnly": <bool>,
                          "trackNumber": <int>,
                          "volumeNumber": <int>,
                          "version": <str>,
                          "popularity": <int>,
                          "copyright": <str>,
                          "url": <str>,
                          "isrc": <str>,
                          "editable": <bool>,
                          "explicit": <bool>,
                          "audioQuality": <str>,
                          "audioModes": [<str>],
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "artist": {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>,
                              "picture": <str>
                            }
                          ],
                          "album": {
                            "id": <int>,
                            "title": <str>,
                            "cover": <str>,
                            "vibrantColor": <str>,
                            "videoCover": <str>
                          },
                          "mixes": {
                            "TRACK_MIX": <str>
                          }
                        }
                      ]
                    },
                    "videos": {
                      "limit": <int>,
                      "offset": <int>,
                      "totalNumberOfItems": <int>,
                      "items": [
                        {
                          "id": <int>,
                          "title": <str>,
                          "volumeNumber": <int>,
                          "trackNumber": <int>,
                          "releaseDate": <str>,
                          "imagePath": <str>,
                          "imageId": <str>,
                          "vibrantColor": <str>,
                          "duration": <int>,
                          "quality": <str>,
                          "streamReady": <bool>,
                          "adSupportedStreamReady": <bool>,
                          "djReady": <bool>,
                          "stemReady": <bool>,
                          "streamStartDate": <str>,
                          "allowStreaming": <bool>,
                          "explicit": <bool>,
                          "popularity": <int>,
                          "type": <str>,
                          "adsUrl": <str>,
                          "adsPrePaywallOnly": <bool>,
                          "artist": {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>,
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>,
                              "picture": <str>,
                            }
                          ],
                          "album": <dict>
                        }
                      ]
                    },
                    "topHit": {
                      "value": <dict>,
                      "type": <str>
                    }
                  }
        """

        self._check_scope(
            "search", "r_usr", flows={"device_code"}, require_authentication=False
        )

        url = f"{self.API_URL}/v1/search"
        if type:
            if type not in (
                TYPES := {
                    "artist",
                    "album",
                    "playlist",
                    "track",
                    "userProfile",
                    "video",
                }
            ):
                emsg = (
                    "Invalid target search type. Valid values: " f"{', '.join(TYPES)}."
                )
                raise ValueError(emsg)
            url += f"/{type}s"

        return self._get_json(
            url,
            params={
                "query": query,
                "type": type,
                "limit": limit,
                "offset": offset,
                "countryCode": self._get_country_code(country_code),
            },
        )

    ### STREAMS ###############################################################

    def get_collection_streams(
        self,
        collection_id: Union[int, str],
        type: str,
        *,
        audio_quality: str = "HI_RES",
        video_quality: str = "HIGH",
        max_resolution: int = 2160,
        playback_mode: str = "STREAM",
        asset_presentation: str = "FULL",
        streaming_session_id: str = None,
    ) -> list[tuple[bytes, str]]:
        """
        Get audio and video stream data for items (tracks and videos) in
        an album, mix, or playlist.

        .. admonition:: User authentication, authorization scope, and
                        subscription
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

           Full track and video playback information and lossless audio
           is only available with user authentication and an active
           TIDAL subscription.

           High-resolution and immersive audio is only available with
           the HiFi Plus plan and when the current client credentials
           are from a supported device.

           .. seealso::

              For more information on audio quality availability, see
              the `Download TIDAL <https://offer.tidal.com/download>`_,
              `TIDAL Pricing <https://tidal.com/pricing>`_, and
              `Dolby Atmos <https://support.tidal.com/hc/en-us/articles
              /360004255778-Dolby-Atmos>`_ web pages.

        .. note::

           This method is provided for convenience and is not a private
           TIDAL API endpoint.

        Parameters
        ----------
        collection_id : `int` or `str`
            TIDAL collection ID or UUID.

        type : `str`
            Collection type.

            **Valid values**: :code:`"album"`, :code:`"mix"`, and
            :code:`"playlist"`.

        audio_quality : `str`, keyword-only, default: :code:`"HI-RES"`
            Audio quality.

            .. container::

               **Valid values**:

               * :code:`"LOW"` for 64 kbps (22.05 kHz) MP3 without user
                 authentication or 96 kbps AAC with user authentication.
               * :code:`"HIGH"` for 320 kbps AAC.
               * :code:`"LOSSLESS"` for 1411 kbps (16-bit, 44.1 kHz) ALAC
                 or FLAC.
               * :code:`"HI_RES"` for up to 9216 kbps (24-bit, 96 kHz)
                 MQA-encoded FLAC.

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

               * :code:`"FULL"`: Full track or video.
               * :code:`"PREVIEW"`: 30-second preview of the track or
                 video.

        streaming_session_id : `str`, keyword-only, optional
            Streaming session ID.

        Returns
        -------
        streams : `list`
            Audio and video stream data and their MIME types.
        """

        if type not in (COLLECTION_TYPES := {"album", "mix", "playlist"}):
            emsg = (
                "Invalid collection type. Valid values: "
                f"{', '.join(COLLECTION_TYPES)}."
            )
            raise ValueError(emsg)

        if type == "album":
            items = self.get_album_items(collection_id)["items"]
        elif type == "mix":
            items = self.get_mix_items(collection_id)["items"]
        elif type == "playlist":
            items = self.get_playlist_items(collection_id)["items"]

        streams = []
        for item in items:
            if item["type"] == "track":
                stream = self.get_track_stream(
                    item["item"]["id"],
                    audio_quality=audio_quality,
                    playback_mode=playback_mode,
                    asset_presentation=asset_presentation,
                    streaming_session_id=streaming_session_id,
                )
            elif item["type"] == "video":
                stream = self.get_video_stream(
                    item["item"]["id"],
                    video_quality=video_quality,
                    max_resolution=max_resolution,
                    playback_mode=playback_mode,
                    asset_presentation=asset_presentation,
                    streaming_session_id=streaming_session_id,
                )
            streams.append(stream)
        return streams

    def get_track_stream(
        self,
        track_id: Union[int, str],
        *,
        audio_quality: str = "HI_RES",
        playback_mode: str = "STREAM",
        asset_presentation: str = "FULL",
        streaming_session_id: str = None,
    ) -> Union[bytes, str]:
        """
        Get the audio stream data for a track.

        .. admonition:: User authentication, authorization scope, and
                        subscription
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

           Full track playback information and lossless audio is only
           available with user authentication and an active TIDAL
           subscription.

           High-resolution and immersive audio is only available with
           the HiFi Plus plan and when the current client credentials
           are from a supported device.

           .. seealso::

              For more information on audio quality availability, see
              the `Download TIDAL <https://offer.tidal.com/download>`_,
              `TIDAL Pricing <https://tidal.com/pricing>`_, and
              `Dolby Atmos <https://support.tidal.com/hc/en-us/articles
              /360004255778-Dolby-Atmos>`_ web pages.

        .. note::

           This method is provided for convenience and is not a private
           TIDAL API endpoint.

        Parameters
        ----------
        track_id : `int` or `str`
            TIDAL track ID.

            **Example**: :code:`251380837`.

        audio_quality : `str`, keyword-only, default: :code:`"HI-RES"`
            Audio quality.

            .. container::

               **Valid values**:

               * :code:`"LOW"` for 64 kbps (22.05 kHz) MP3 without user
                 authentication or 96 kbps AAC with user authentication.
               * :code:`"HIGH"` for 320 kbps AAC.
               * :code:`"LOSSLESS"` for 1411 kbps (16-bit, 44.1 kHz) ALAC
                 or FLAC.
               * :code:`"HI_RES"` for up to 9216 kbps (24-bit, 96 kHz)
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
        stream : `bytes`
            Audio stream data.

        codec : `str`
            Audio codec.
        """

        manifest = base64.b64decode(
            self.get_track_playback_info(
                track_id,
                audio_quality=audio_quality,
                playback_mode=playback_mode,
                asset_presentation=asset_presentation,
                streaming_session_id=streaming_session_id,
            )["manifest"]
        )

        if b"urn:mpeg:dash" in manifest:
            manifest = minidom.parseString(manifest)
            codec = manifest.getElementsByTagName("Representation")[0].getAttribute(
                "codecs"
            )
            segment = manifest.getElementsByTagName("SegmentTemplate")[0]
            stream = bytearray()
            with self.session.get(segment.getAttribute("initialization")) as r:
                stream.extend(r.content)
            for i in range(
                1,
                sum(
                    int(tl.getAttribute("r") or 1)
                    for tl in segment.getElementsByTagName("S")
                )
                + 2,
            ):
                with self.session.get(
                    segment.getAttribute("media").replace("$Number$", str(i))
                ) as r:
                    stream.extend(r.content)
        else:
            manifest = json.loads(manifest)
            codec = manifest["codecs"]
            with self.session.get(manifest["urls"][0]) as r:
                stream = r.content
            if manifest["encryptionType"] == "OLD_AES":
                key_id = base64.b64decode(manifest["keyId"])
                key_nonce = (
                    Cipher(
                        algorithms.AES(
                            b"P\x89SLC&\x98\xb7\xc6\xa3\n?P.\xb4\xc7"
                            b"a\xf8\xe5n\x8cth\x13E\xfa?\xbah8\xef\x9e"
                        ),
                        modes.CBC(key_id[:16]),
                    )
                    .decryptor()
                    .update(key_id[16:])
                )
                stream = (
                    Cipher(algorithms.AES(key_nonce[:16]), modes.CTR(key_nonce[16:32]))
                    .decryptor()
                    .update(stream)
                )
            elif manifest["encryptionType"] != "NONE":
                raise NotImplementedError("Unsupported encryption type.")
        return stream, codec

    def get_video_stream(
        self,
        video_id: Union[int, str],
        *,
        video_quality: str = "HIGH",
        max_resolution: int = 2160,
        playback_mode: str = "STREAM",
        asset_presentation: str = "FULL",
        streaming_session_id: str = None,
    ) -> tuple[bytes, str]:
        """
        Get the video stream data for a music video.

        .. admonition:: User authentication, authorization scope, and
                        subscription
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

           Full video playback information is only available with user
           authentication and an active TIDAL subscription.

        .. note::

           This method is provided for convenience and is not a private
           TIDAL API endpoint.

        Parameters
        ----------
        video_id : `int` or `str`
            TIDAL video ID.

            **Example**: :code:`59727844`.

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

        Returns
        -------
        stream : `bytes`
            Video stream data.

        codec : `str`
            Video codec.
        """

        manifest = base64.b64decode(
            self.get_video_playback_info(
                video_id,
                video_quality=video_quality,
                playback_mode=playback_mode,
                asset_presentation=asset_presentation,
                streaming_session_id=streaming_session_id,
            )["manifest"]
        )

        codec, playlist = next(
            (c, pl)
            for c, res, pl in re.findall(
                r'(?<=CODECS=")(.*)",(?:RESOLUTION=)\d+x(\d+)\n(http.*)',
                self.session.get(json.loads(manifest)["urls"][0]).content.decode(
                    "utf-8"
                ),
            )[::-1]
            if int(res) < max_resolution
        )

        stream = bytearray()
        for ts in re.findall(
            "(?<=\n).*(http.*)", self.session.get(playlist).content.decode("utf-8")
        ):
            with self.session.get(ts) as r:
                stream.extend(r.content)
        return stream, codec

    ### TRACKS ################################################################

    def get_track(
        self, track_id: Union[int, str], country_code: str = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a track.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        track_id : `int` or `str`
            TIDAL track ID.

            **Example**: :code:`251380837`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        track : `dict`
            TIDAL catalog information for a track.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "title": <str>,
                    "duration": <int>,
                    "replayGain": <float>,
                    "peak": <float>,
                    "allowStreaming": <bool>,
                    "streamReady": <bool>,
                    "adSupportedStreamReady": <bool>,
                    "djReady": <bool>,
                    "stemReady": <bool>,
                    "streamStartDate": <str>,
                    "premiumStreamingOnly": <bool>,
                    "trackNumber": <int>,
                    "volumeNumber": <int>,
                    "version": <str>,
                    "popularity": <int>,
                    "copyright": <str>,
                    "url": <str>,
                    "isrc": <str>,
                    "editable": <bool>,
                    "explicit": <bool>,
                    "audioQuality": <str>,
                    "audioModes": [<str>],
                    "mediaMetadata": {
                      "tags": [<str>]
                    },
                    "artist": {
                      "id": <int>,
                      "name": <str>,
                      "type": <str>,
                      "picture": <str>
                    },
                    "artists": [
                      {
                        "id": <int>,
                        "name": <str>,
                        "type": <str>,
                        "picture": <str>
                      }
                    ],
                    "album": {
                      "id": <int>,
                      "title": <str>,
                      "cover": <str>,
                      "vibrantColor": <str>,
                      "videoCover": <str>
                    },
                    "mixes": {
                      "TRACK_MIX": <str>
                    }
                  }
        """

        self._check_scope(
            "get_track", "r_usr", flows={"device_code"}, require_authentication=False
        )

        return self._get_json(
            f"{self.API_URL}/v1/tracks/{track_id}",
            params={"countryCode": self._get_country_code(country_code)},
        )

    def get_track_contributors(
        self,
        track_id: Union[int, str],
        country_code: str = None,
        *,
        limit: int = None,
        offset: int = None,
    ) -> dict[str, Any]:
        """
        Get the contributors to a track and their roles.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        track_id : `int` or `str`
            TIDAL track ID.

            **Example**: :code:`251380837`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`100`
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        contributors : `dict`
            A dictionary containing a track's contributors and their
            roles, and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "name": <str>,
                        "role": <str>
                      }
                    ]
                  }
        """

        self._check_scope(
            "get_track_contributors",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/tracks/{track_id}/contributors",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
            },
        )

    def get_track_credits(
        self, track_id: Union[int, str], country_code: str = None
    ) -> list[dict[str, Any]]:
        """
        Get credits for a track.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        track_id : `int` or `str`
            TIDAL track ID.

        country : `str`, keyword-only, optional
            An ISO 3166-1 alpha-2 country code. If not specified, the
            country associated with the user account will be used.

            **Example**: :code:`"US"`.

        Returns
        -------
        credits : `list`
            A list of roles and their associated contributors.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "type": <str>,
                      "contributors": [
                        {
                          "name": <str>,
                          "id": <int>
                        }
                      ]
                    }
                  ]
        """

        self._check_scope(
            "get_track_credits",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/tracks/{track_id}/credits",
            params={"countryCode": self._get_country_code(country_code)},
        )

    def get_track_composers(self, track_id: Union[int, str]) -> list[str]:
        """
        Get the composers, lyricists, and/or songwriters of a track.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        .. note::

           This method is provided for convenience and is not a private
           TIDAL API endpoint.

        Parameters
        ----------
        track_id : `int` or `str`
            TIDAL track ID.

            **Example**: :code:`251380837`.

        Returns
        -------
        composers : `list`
            Composers, lyricists, and/or songwriters of the track.

            **Example**: :code:`['Tommy Wright III', 'Beyoncé',
            'Kelman Duran', 'Terius "The-Dream" G...de-Diamant',
            'Mike Dean']`
        """

        return sorted(
            {
                c["name"]
                for c in self.get_track_contributors(track_id)["items"]
                if c["role"] in {"Composer", "Lyricist", "Writer"}
            }
        )

    def get_track_lyrics(
        self, id: Union[int, str], country_code: str = None
    ) -> dict[str, Any]:
        """
        Get lyrics for a track.

        .. admonition:: User authentication and subscription
           :class: warning

           Requires user authentication via an OAuth 2.0 authorization
           flow and an active TIDAL subscription.

        Parameters
        ----------
        id : `int` or `str`
            TIDAL track ID.

            **Example**: :code:`251380837`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        lyrics : `dict`
            A dictionary containing formatted and time-synced lyrics (if
            available) in the `"lyrics"` and `"subtitles"` keys,
            respectively.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "trackId": <int>,
                    "lyricsProvider": <str>,
                    "providerCommontrackId": <str>,
                    "providerLyricsId": <str>,
                    "lyrics": <str>,
                    "subtitles": <str>,
                    "isRightToLeft": <bool>
                  }
        """

        self._check_scope("get_track_lyrics")

        try:
            return self._get_json(
                f"{self.WEB_URL}/v1/tracks/{id}/lyrics",
                params={"countryCode": self._get_country_code(country_code)},
            )
        except RuntimeError:
            logging.warning(
                "Either lyrics are not available for this track "
                "or the current account does not have an active "
                "TIDAL subscription."
            )

    def get_track_mix_id(
        self, tidal_id: Union[int, str], country_code: str = None
    ) -> str:
        """
        Get the curated mix of tracks based on a track.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        tidal_id : `int` or `str`
            TIDAL track ID.

            **Example**: :code:`251380837`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        mix_id : `str`
            TIDAL mix ID.

            **Example**: :code:`"0017159e6a1f34ae3d981792d72ecf"`.
        """

        self._check_scope(
            "get_track_mix_id",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        return self._get_json(
            f"{self.API_URL}/v1/tracks/{tidal_id}/mix",
            params={"countryCode": self._get_country_code(country_code)},
        )["id"]

    def get_track_playback_info(
        self,
        track_id: Union[int, str],
        *,
        audio_quality: str = "HI_RES",
        playback_mode: str = "STREAM",
        asset_presentation: str = "FULL",
        streaming_session_id: str = None,
    ) -> dict[str, Any]:
        """
        Get playback information for a track.

        .. admonition:: User authentication, authorization scope, and
                        subscription
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

           Full track playback information and lossless audio is only
           available with user authentication and an active TIDAL
           subscription.

           High-resolution and immersive audio is only available with
           the HiFi Plus plan and when the current client credentials
           are from a supported device.

           .. seealso::

              For more information on audio quality availability, see
              the `Download TIDAL <https://offer.tidal.com/download>`_,
              `TIDAL Pricing <https://tidal.com/pricing>`_, and
              `Dolby Atmos <https://support.tidal.com/hc/en-us/articles
              /360004255778-Dolby-Atmos>` web pages.

        Parameters
        ----------
        track_id : `int` or `str`
            TIDAL track ID.

            **Example**: :code:`251380837`.

        audio_quality : `str`, keyword-only, default: :code:`"HI-RES"`
            Audio quality.

            .. container::

               **Valid values**:

               * :code:`"LOW"` for 64 kbps (22.05 kHz) MP3 without user
                 authentication or 96 kbps AAC with user authentication.
               * :code:`"HIGH"` for 320 kbps AAC.
               * :code:`"LOSSLESS"` for 1411 kbps (16-bit, 44.1 kHz) ALAC
                 or FLAC.
               * :code:`"HI_RES"` for up to 9216 kbps (24-bit, 96 kHz)
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

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "trackId": <int>,
                    "assetPresentation": <str>,
                    "audioMode": <str>,
                    "audioQuality": <str>,
                    "manifestMimeType": <str>,
                    "manifestHash": <str>,
                    "manifest": <str>,
                    "albumReplayGain": <float>,
                    "albumPeakAmplitude": <float>,
                    "trackReplayGain": <float>,
                    "trackPeakAmplitude": <float>
                  }
        """

        self._check_scope(
            "get_track_playback_info",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        if audio_quality not in (
            AUDIO_QUALITIES := {"LOW", "HIGH", "LOSSLESS", "HI_RES"}
        ):
            emsg = (
                "Invalid audio quality. Valid values: "
                f"are{', '.join(AUDIO_QUALITIES)}."
            )
            raise ValueError(emsg)
        if playback_mode not in (PLAYBACK_MODES := {"STREAM", "OFFLINE"}):
            emsg = (
                "Invalid playback mode. Valid values: "
                f"modes are {', '.join(PLAYBACK_MODES)}."
            )
            raise ValueError(emsg)
        if asset_presentation not in (ASSET_PRESENTATIONS := {"FULL", "PREVIEW"}):
            emsg = (
                "Invalid asset presentation. Valid values: "
                "presentations are "
                f"{', '.join(ASSET_PRESENTATIONS)}."
            )
            raise ValueError(emsg)

        url = f"{self.API_URL}/v1/tracks/{track_id}/playbackinfo"
        # if self._flow:
        #     url += "postpaywall"
        url += "postpaywall" if self._flow else "prepaywall"
        return self._get_json(
            url,
            params={
                "audioquality": audio_quality,
                "assetpresentation": asset_presentation,
                "playbackmode": playback_mode,
                "streamingsessionid": streaming_session_id,
            },
        )

    def get_track_recommendations(
        self,
        track_id: Union[int, str],
        country_code: str = None,
        *,
        limit: int = None,
        offset=None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a track's recommended
        tracks and videos.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        track_id : `int` or `str`
            TIDAL track ID.

            **Example**: :code:`251380837`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, optional
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        recommendations : `dict`
            A dictionary containing TIDAL catalog information for the
            recommended tracks and metadata for the returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "id": <int>,
                        "title": <str>,
                        "duration": <int>,
                        "replayGain": <float>,
                        "peak": <float>,
                        "allowStreaming": <bool>,
                        "streamReady": <bool>,
                        "adSupportedStreamReady": <bool>,
                        "djReady": <bool>,
                        "stemReady": <bool>,
                        "streamStartDate": <str>,
                        "premiumStreamingOnly": <bool>,
                        "trackNumber": <int>,
                        "volumeNumber": <int>,
                        "version": <str>,
                        "popularity": <int>,
                        "copyright": <str>,
                        "url": <str>,
                        "isrc": <str>,
                        "editable": <bool>,
                        "explicit": <bool>,
                        "audioQuality": <str>,
                        "audioModes": [<str>],
                        "mediaMetadata": {
                          "tags": [<str>]
                        },
                        "artist": {
                          "id": <int>,
                          "name": <str>,
                          "type": <str>,
                          "picture": <str>
                        },
                        "artists": [
                          {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          }
                        ],
                        "album": {
                          "id": <int>,
                          "title": <str>,
                          "cover": <str>,
                          "vibrantColor": <str>,
                          "videoCover": <str>
                        },
                        "mixes": {
                          "TRACK_MIX": <str>
                        }
                      },
                      "sources": [
                        "SUGGESTED_TRACKS"
                      ]
                    ]
                  }
        """

        self._check_scope("get_track_recommendations", "r_usr", flows={"device_code"})

        return self._get_json(
            f"{self.API_URL}/v1/tracks/{track_id}/recommendations",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
            },
        )

    def get_favorite_tracks(
        self,
        country_code: str = None,
        *,
        limit: int = 50,
        offset: int = None,
        order: str = "DATE",
        order_direction: str = "DESC",
    ):
        """
        Get TIDAL catalog information for tracks in the current user's
        collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`50`
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        order : `str`, keyword-only, default: :code:`"DATE"`
            Sorting order.

            **Valid values**: :code:`"DATE"` and :code:`"NAME"`.

        order_direction : `str`, keyword-only, default: :code:`"DESC"`
            Sorting order direction.

            **Valid values**: :code:`"DESC"` and :code:`"ASC"`.

        Returns
        -------
        tracks : `dict`
            A dictionary containing TIDAL catalog information for tracks
            in the current user's collection and metadata for the
            returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "created": <str>,
                        "item": {
                          "id": <int>,
                          "title": <str>,
                          "duration": <int>,
                          "replayGain": <float>,
                          "peak": <float>,
                          "allowStreaming": <bool>,
                          "streamReady": <bool>,
                          "adSupportedStreamReady": <bool>,
                          "djReady": <bool>,
                          "stemReady": <bool>,
                          "streamStartDate": <str>,
                          "premiumStreamingOnly": <bool>,
                          "trackNumber": <int>,
                          "volumeNumber": <int>,
                          "version": <str>,
                          "popularity": <int>,
                          "copyright": <str>,
                          "url": <str>,
                          "isrc": <str>,
                          "editable": <bool>,
                          "explicit": <bool>,
                          "audioQuality": <str>,
                          "audioModes": [<str>],
                          "mediaMetadata": {
                            "tags": [<str>]
                          },
                          "artist": {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>,
                              "picture": <str>
                            }
                          ],
                          "album": {
                            "id": <int>,
                            "title": <str>,
                            "cover": <str>,
                            "vibrantColor": <str>,
                            "videoCover": <str>
                          },
                          "mixes": {
                            "TRACK_MIX": <str>
                          }
                        }
                      }
                    ]
                  }
        """

        self._check_scope("get_favorite_tracks", "r_usr", flows={"device_code"})

        return self._get_json(
            f"{self.API_URL}/v1/users/{self._user_id}/favorites/tracks",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
                "order": order,
                "orderDirection": order_direction,
            },
        )

    def favorite_tracks(
        self,
        track_ids: Union[int, str, list[Union[int, str]]],
        country_code: str = None,
        *,
        on_artifact_not_found: str = "FAIL",
    ) -> None:
        """
        Add tracks to the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        track_ids : `int`, `str`, or `list`
            TIDAL track ID(s).

            **Examples**: :code:`"251380837,251380838"` or
            :code:`[251380837, 251380838]`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        on_artifact_not_found : `str`, keyword-only, default: :code:`"FAIL"`
            Behavior when the item to be added does not exist.

            **Valid values**: :code:`"FAIL"` or :code:`"SKIP"`.
        """

        self._check_scope("favorite_tracks", "r_usr", flows={"device_code"})

        self._request(
            "post",
            f"{self.API_URL}/v1/users/{self._user_id}/favorites/tracks",
            params={"countryCode": self._get_country_code(country_code)},
            data={
                "trackIds": (
                    ",".join(map(str, track_ids))
                    if isinstance(track_ids, list)
                    else track_ids
                ),
                "onArtifactNotFound": on_artifact_not_found,
            },
        )

    def unfavorite_tracks(
        self, track_ids: Union[int, str, list[Union[int, str]]]
    ) -> None:
        """
        Remove tracks from the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        track_ids : `int`, `str`, or `list`
            TIDAL track ID(s).

            **Examples**: :code:`"251380837,251380838"` or
            :code:`[251380837, 251380838]`.
        """

        self._check_scope("unfavorite_tracks", "r_usr", flows={"device_code"})

        if isinstance(track_ids, list):
            track_ids = ",".join(map(str, track_ids))
        self._request(
            "delete",
            f"{self.API_URL}/v1/users/{self._user_id}" f"/favorites/tracks/{track_ids}",
        )

    ### USERS #################################################################

    def get_profile(self) -> dict[str, Any]:
        """
        Get the current user's profile information.

        .. admonition:: User authentication
           :class: warning

           Requires user authentication via an OAuth 2.0 authorization
           flow.

        Returns
        -------
        profile : `dict`
            A dictionary containing the current user's profile
            information.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "userId": <int>,
                    "email": <str>,
                    "countryCode": <str>,
                    "fullName": <str>,
                    "firstName": <str>,
                    "lastName": <str>,
                    "nickname": <str>,
                    "username": <str>,
                    "address": <str>,
                    "city": <str>,
                    "postalcode": <str>,
                    "usState": <str>,
                    "phoneNumber": <int>,
                    "birthday": <int>,
                    "channelId": <int>,
                    "parentId": <int>,
                    "acceptedEULA": <bool>,
                    "created": <int>,
                    "updated": <int>,
                    "facebookUid": <int>,
                    "appleUid": <int>,
                    "googleUid": <int>,
                    "accountLinkCreated": <bool>,
                    "emailVerified": <bool>,
                    "newUser": <bool>
                  }
        """

        self._check_scope("get_profile")

        return self._get_json(f"{self.LOGIN_URL}/oauth2/me")

    def get_session(self) -> dict[str, Any]:
        """
        Get information about the current private TIDAL API session.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Returns
        -------
        session : `dict`
            Information about the current private TIDAL API session.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "sessionId": <str>,
                    "userId": <int>,
                    "countryCode": <str>,
                    "channelId": <int>,
                    "partnerId": <int>,
                    "client": {
                      "id": <int>,
                      "name": <str>,
                      "authorizedForOffline": <bool>,
                      "authorizedForOfflineDate": <str>
                    }
                  }

        """

        self._check_scope("get_session", "r_usr", flows={"device_code"})

        return self._get_json(f"{self.API_URL}/v1/sessions")

    def get_favorite_ids(self) -> dict[str, list[str]]:
        """
        Get TIDAL IDs or UUIDs of the albums, artists, playlists,
        tracks, and videos in the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Returns
        -------
        ids : `dict`
            A dictionary containing the IDs or UUIDs of the items in the
            current user's collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "ARTIST": [<str>],
                    "ALBUM": [<str>],
                    "VIDEO": [<str>],
                    "PLAYLIST": [<str>],
                    "TRACK": [<str>]
                  }
        """

        self._check_scope("get_favorite_ids", "r_usr", flows={"device_code"})

        return self._get_json(f"{self.API_URL}/v1/users/{self._user_id}/favorites/ids")

    def get_user_profile(self, user_id: Union[int, str]) -> dict[str, Any]:
        """
        Get a TIDAL user's profile information.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        user_id : `int` or `str`
            TIDAL user ID.

            **Example**: :code:`172311284`.

        Returns
        -------
        profile : `dict`
            A dictionary containing the user's profile information.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "userId": <int>,
                    "name": <str>,
                    "color": [<str>],
                    "picture": <str>,
                    "numberOfFollowers": <int>,
                    "numberOfFollows": <int>,
                    "prompts": [
                      {
                        "id": <int>,
                        "title": <str>,
                        "description": <str>,
                        "colors": {
                          "primary": <str>,
                          "secondary": <str>,
                        },
                        "trn": <str>,
                        "data": <str>,
                        "updatedTime": <str>,
                        "supportedContentType": "TRACK"
                      }
                    ],
                    "profileType": <str>
                  }
        """

        self._check_scope("get_user_profile", "r_usr", flows={"device_code"})

        return self._get_json(f"{self.API_URL}/v2/profiles/{user_id}")

    def get_user_followers(
        self, user_id: Union[int, str] = None, *, limit: int = 500, cursor: str = None
    ) -> dict[str, Any]:
        """
        Get a TIDAL user's followers.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        user_id : `str`
            TIDAL user ID. If not specified, the ID associated with the
            user account in the current session is used.

            **Example**: :code:`172311284`.

        limit : `int`, keyword-only, default: :code:`500`
            Page size.

            **Example**: :code:`10`.

        cursor : `str`, keyword-only, optional
            Cursor position of the last item in previous search results.
            Use with `limit` to get the next page of search results.

        Returns
        -------
        followers : `dict`
            A dictionary containing the user's followers and the cursor
            position.
        """

        self._check_scope("get_user_followers", "r_usr", flows={"device_code"})

        if user_id is None:
            user_id = self._user_id
        return self._get_json(
            f"{self.API_URL}/v2/profiles/{user_id}/followers",
            params={"limit": limit, "cursor": cursor},
        )

    def get_user_following(
        self,
        user_id: Union[int, str] = None,
        *,
        include_only: str = None,
        limit: int = 500,
        cursor: str = None,
    ):
        """
        Get the people (artists, users, etc.) a TIDAL user follows.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        user_id : `str`
            TIDAL user ID. If not specified, the ID associated with the
            user account in the current session is used.

            **Example**: :code:`172311284`.

        include_only : `str`, keyword-only, optional
            Type of people to return.

            **Valid values**: :code:`"ARTIST"` and :code:`"USER"`.

        limit : `int`, keyword-only, default: :code:`500`
            Page size.

            **Example**: :code:`10`.

        cursor : `str`, keyword-only, optional
            Cursor position of the last item in previous search results.
            Use with `limit` to get the next page of search results.

        Returns
        -------
        following : `dict`
            A dictionary containing the people following the user and
            the cursor position.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "id": <int>,
                        "name": <str>,
                        "picture": <str>,
                        "imFollowing": <bool>,
                        "trn": <str>,
                        "followType": <str>
                      }
                    ],
                    "cursor": <str>
                  }
        """

        self._check_scope("get_user_following", "r_usr", flows={"device_code"})

        if include_only and include_only not in (
            ALLOWED_INCLUDES := {"ARTIST", "USER"}
        ):
            emsg = (
                "Invalid include type. Valid values: " f"{', '.join(ALLOWED_INCLUDES)}."
            )
            raise ValueError(emsg)

        if user_id is None:
            user_id = self._user_id
        return self._get_json(
            f"{self.API_URL}/v2/profiles/{user_id}/following",
            params={"includeOnly": include_only, "limit": limit, "cursor": cursor},
        )

    def follow_user(self, user_id: Union[int, str]) -> None:
        """
        Follow a user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        user_id : `int` or `str`
            TIDAL user ID.

            **Example**: :code:`172311284`.
        """

        self._check_scope("follow_user", "r_usr", flows={"device_code"})

        self._request(
            "put", f"{self.API_URL}/v2/follow", params={"trn": f"trn:user:{user_id}"}
        )

    def unfollow_user(self, user_id: Union[int, str]) -> None:
        """
        Unfollow a user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        user_id : `int` or `str`
            TIDAL user ID.

            **Example**: :code:`172311284`.
        """

        self._check_scope("unfollow_user", "r_usr", flows={"device_code"})

        self._request(
            "delete", f"{self.API_URL}/v2/follow", params={"trn": f"trn:user:{user_id}"}
        )

    def get_blocked_users(
        self, *, limit: int = None, offset: int = None
    ) -> dict[str, Any]:
        """
        Get users blocked by the current user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        Returns
        -------
        users : `dict`
            A dictionary containing the users blocked by the current
            user and the number of results.
        """

        self._check_scope("get_blocked_users", "r_usr", flows={"device_code"})

        return self._get_json(
            f"{self.API_URL}/v2/profiles/blocked-profiles",
            params={"limit": limit, "offset": offset},
        )

    def block_user(self, user_id: Union[int, str]) -> None:
        """
        Block a user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        user_id : `int` or `str`
            TIDAL user ID.

            **Example**: :code:`172311284`.
        """

        self._check_scope("block_user", "r_usr", flows={"device_code"})

        self._request("put", f"{self.API_URL}/v2/profiles/block/{user_id}")

    def unblock_user(self, user_id: Union[int, str]) -> None:
        """
        Unblock a user.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        user_id : `int` or `str`
            TIDAL user ID.

            **Example**: :code:`172311284`.
        """

        self._check_scope("unblock_user", "r_usr", flows={"device_code"})

        self._request("delete", f"{self.API_URL}/v2/profiles/block/{user_id}")

    ### VIDEOS ################################################################

    def get_video(
        self, video_id: Union[int, str], country_code: str = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a video.

        .. admonition:: Authorization scope
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

        Parameters
        ----------
        video_id : `int` or `str`
            TIDAL video ID.

            **Example**: :code:`59727844`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        Returns
        -------
        video : `dict`
            TIDAL catalog information for a video.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <int>,
                    "title": <str>,
                    "volumeNumber": <int>,
                    "trackNumber": <int>,
                    "releaseDate": <str>,
                    "imagePath": <str>,
                    "imageId": <str>,
                    "vibrantColor": <str>,
                    "duration": <int>,
                    "quality": <str>,
                    "streamReady": <bool>,
                    "adSupportedStreamReady": <bool>,
                    "djReady": <bool>,
                    "stemReady": <bool>,
                    "streamStartDate": <str>,
                    "allowStreaming": <bool>,
                    "explicit": <bool>,
                    "popularity": <int>,
                    "type": <str>,
                    "adsUrl": <str>,
                    "adsPrePaywallOnly": <bool>,
                    "artist": {
                      "id": <int>,
                      "name": <str>,
                      "type": <str>,
                      "picture": <str>,
                    },
                    "artists": [
                      {
                        "id": <int>,
                        "name": <str>,
                        "type": <str>,
                        "picture": <str>,
                      }
                    ],
                    "album": <dict>
                  }
        """

        self._check_scope(
            "get_video", "r_usr", flows={"device_code"}, require_authentication=False
        )

        return self._get_json(
            f"{self.API_URL}/v1/videos/{video_id}",
            params={"countryCode": self._get_country_code(country_code)},
        )

    def get_video_playback_info(
        self,
        video_id: Union[int, str],
        *,
        video_quality: str = "HIGH",
        playback_mode: str = "STREAM",
        asset_presentation: str = "FULL",
        streaming_session_id: str = None,
    ) -> dict[str, Any]:
        """
        Get playback information for a video.

        .. admonition:: User authentication, authorization scope, and
                        subscription
           :class: dropdown warning

           Requires the :code:`r_usr` authorization scope if the device
           code flow was used.

           Full video playback information is only available with user
           authentication and an active TIDAL subscription.

        Parameters
        ----------
        video_id : `int` or `str`
            TIDAL video ID.

            **Example**: :code:`59727844`.

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

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "videoId": <int>,
                    "streamType": <str>,
                    "assetPresentation": <str>,
                    "videoQuality": <str>,
                    "manifestMimeType": <str>,
                    "manifestHash": <str>,
                    "manifest": <str>
                  }
        """

        self._check_scope(
            "get_video_playback_info",
            "r_usr",
            flows={"device_code"},
            require_authentication=False,
        )

        if video_quality not in (
            VIDEO_QUALITIES := {"AUDIO_ONLY", "LOW", "MEDIUM", "HIGH"}
        ):
            emsg = (
                "Invalid video quality. Valid values: "
                f"are{', '.join(VIDEO_QUALITIES)}."
            )
            raise ValueError(emsg)
        if playback_mode not in (PLAYBACK_MODES := {"STREAM", "OFFLINE"}):
            emsg = (
                "Invalid playback mode. Valid values: "
                f"modes are {', '.join(PLAYBACK_MODES)}."
            )
            raise ValueError(emsg)
        if asset_presentation not in (ASSET_PRESENTATIONS := {"FULL", "PREVIEW"}):
            emsg = (
                "Invalid asset presentation. Valid values: "
                "presentations are "
                f"{', '.join(ASSET_PRESENTATIONS)}."
            )
            raise ValueError(emsg)

        url = f"{self.API_URL}/v1/videos/{video_id}/playbackinfo"
        url += "postpaywall" if self._flow else "prepaywall"
        return self._get_json(
            url,
            params={
                "videoquality": video_quality,
                "assetpresentation": asset_presentation,
                "playbackmode": playback_mode,
                "streamingsessionid": streaming_session_id,
            },
        )

    def get_favorite_videos(
        self,
        country_code: str = None,
        *,
        limit: int = 50,
        offset: int = None,
        order: str = "DATE",
        order_direction: str = "DESC",
    ):
        """
        Get TIDAL catalog information for videos in the current user's
        collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        limit : `int`, keyword-only, default: :code:`50`
            Page size.

            **Example**: :code:`10`.

        offset : `int`, keyword-only, optional
            Pagination offset (in number of items).

            **Example**: :code:`0`.

        order : `str`, keyword-only, default: :code:`"DATE"`
            Sorting order.

            **Valid values**: :code:`"DATE"` and :code:`"NAME"`.

        order_direction : `str`, keyword-only, default: :code:`"DESC"`
            Sorting order direction.

            **Valid values**: :code:`"DESC"` and :code:`"ASC"`.

        Returns
        -------
        videos : `dict`
            A dictionary containing TIDAL catalog information for videos
            in the current user's collection and metadata for the
            returned results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>,
                    "items": [
                      {
                        "created": <str>,
                        "item": {
                          "id": <int>,
                          "title": <str>,
                          "volumeNumber": <int>,
                          "trackNumber": <int>,
                          "releaseDate": <str>,
                          "imagePath": <str>,
                          "imageId": <str>,
                          "vibrantColor": <str>,
                          "duration": <int>,
                          "quality": <str>,
                          "streamReady": <bool>,
                          "adSupportedStreamReady": <bool>,
                          "djReady": <bool>,
                          "stemReady": <bool>,
                          "streamStartDate": <str>,
                          "allowStreaming": <bool>,
                          "explicit": <bool>,
                          "popularity": <int>,
                          "type": <str>,
                          "adsUrl": <str>,
                          "adsPrePaywallOnly": <bool>,
                          "artist": {
                            "id": <int>,
                            "name": <str>,
                            "type": <str>,
                            "picture": <str>
                          },
                          "artists": [
                            {
                              "id": <int>,
                              "name": "<str>,
                              "type": <str>,
                              "picture": <str>
                            }
                          ],
                          "album": <dict>
                        }
                      }
                    ]
                  }
        """

        self._check_scope("get_favorite_videos", "r_usr", flows={"device_code"})

        return self._get_json(
            f"{self.API_URL}/v1/users/{self._user_id}/favorites/videos",
            params={
                "countryCode": self._get_country_code(country_code),
                "limit": limit,
                "offset": offset,
                "order": order,
                "orderDirection": order_direction,
            },
        )

    def favorite_videos(
        self,
        video_ids: Union[int, str, list[Union[int, str]]],
        country_code: str = None,
        *,
        on_artifact_not_found: str = "FAIL",
    ) -> None:
        """
        Add videos to the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        video_ids : `int`, `str`, or `list`
            TIDAL video ID(s).

            **Examples**: :code:`"59727844,75623239"` or
            :code:`[59727844, 75623239]`.

        country_code : `str`, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country code associated with the user account in the current
            session or the current IP address will be used instead.

            **Example**: :code:`"US"`.

        on_artifact_not_found : `str`, keyword-only, default: :code:`"FAIL"`
            Behavior when the item to be added does not exist.

            **Valid values**: :code:`"FAIL"` or :code:`"SKIP"`.
        """

        self._check_scope("favorite_videos", "r_usr", flows={"device_code"})

        self._request(
            "post",
            f"{self.API_URL}/v1/users/{self._user_id}/favorites/videos",
            params={"countryCode": self._get_country_code(country_code)},
            data={
                "videoIds": (
                    ",".join(map(str, video_ids))
                    if isinstance(video_ids, list)
                    else video_ids
                ),
                "onArtifactNotFound": on_artifact_not_found,
            },
        )

    def unfavorite_videos(
        self, video_ids: Union[int, str, list[Union[int, str]]]
    ) -> None:
        """
        Remove videos from the current user's collection.

        .. admonition:: User authentication and authorization scope
           :class: warning

           Requires user authentication and the :code:`r_usr`
           authorization scope if the device code flow was used.

        Parameters
        ----------
        video_ids : `int`, `str`, or `list`
            TIDAL video ID(s).

            **Examples**: :code:`"59727844,75623239"` or
            :code:`[59727844, 75623239]`.
        """

        self._check_scope("unfavorite_videos", "r_usr", flows={"device_code"})

        if isinstance(video_ids, list):
            video_ids = ",".join(map(str, video_ids))
        self._request(
            "delete",
            f"{self.API_URL}/v1/users/{self._user_id}" f"/favorites/videos/{video_ids}",
        )
