"""
:mod:`minim.qobuz` -- Qobuz API
===============================
.. moduleauthor:: Benjamin Ye <GitHub: @bbye98>

This module contains a minimal Python implementation of the Qobuz API,
which allows songs, collections (albums, playlists), and performers to
be queried, and information about them to be retrieved. As the Qobuz API
is not public, there is no available official documentation for it. Its
endpoints have been determined by watching HTTP network traffic.

Without authentication, the Qobuz API can be used to query for and
retrieve information about media and performers.

By logging into Qobuz, the Qobuz API allows access to user information
and media streaming (with an active Qobuz streaming plan). Valid user
credentials (email address and password) or an user authorization token
must either be provided explicitly to the :class:`Session` constructor
or be stored in the operating system's environment variables as 
:code:`QOBUZ_EMAIL`, :code:`QOBUZ_PASSWORD`, and 
:code:`QOBUZ_USER_AUTH_TOKEN`, respectively.
"""

import base64
import hashlib
import os
import re
import subprocess
import time
from typing import Any, Union
import urllib
import warnings

import requests

from . import audio, utility

class Session:

    """
    A Qobuz API session.

    Parameters
    ----------
    email : `str`, keyword-only, optional
        Account email address.

    password : `str`, keyword-only, optional
        Account password.

    auth_token : `str`, keyword-only, optional
        User authentication token.

    user_agent : `str`, keyword-only, optional
        User agent information to send in the header of HTTP requests.

    Attributes
    ----------
    API_URL : `str`
        URL for the Qobuz API.

    WEB_URL : `str`
        URL for the Qobuz web player.
    """

    _AUDIO_FORMATS_EXTENSIONS = {
        "flac": "flac",
        "mpeg": "mp3"
    }
    _AUDIO_QUALITIES = {"MP3": 5, "CD": 6, "HI-RES-96": 7, "HI-RES-192": 27}
    _ILLEGAL_CHARACTERS = {ord(c): '_' for c in '<>:"/\|?*'}

    API_URL = "https://www.qobuz.com/api.json/0.2"
    WEB_URL = "https://play.qobuz.com"

    def __init__(
            self, *, email: str = None, password: str = None, 
            auth_token: str = None, user_agent: str = None):
        
        self.session = requests.Session()
        if user_agent:
            self.session.headers.update({"User-Agent": user_agent})

        self._get_app_id_and_secret()

        if auth_token is None and (email is None or password is None):
            auth_token = os.environ.get("QOBUZ_USER_AUTH_TOKEN")
            email = os.environ.get("QOBUZ_EMAIL")
            password = os.environ.get("QOBUZ_PASSWORD")
        if auth_token:
            resp = self._get_json(
                f"{self.API_URL}/user/get", 
                params={"user_auth_token": auth_token}
            )
            self._me = resp
            self.session.headers.update({"X-User-Auth-Token": auth_token})
        elif email and password:
            resp = self._request(
                "post",
                f"{self.API_URL}/user/login", 
                params={"email": email, "password": password}
            ).json()
            self._me = resp["user"]
            self.session.headers.update(
                {"X-User-Auth-Token": resp["user_auth_token"]}
            )
        else:
            self._me = self._auth_token = None

    def _get_app_id_and_secret(self) -> None:

        """
        Get the Qobuz app ID and secret.
        """

        js = re.search('/resources/.*/bundle.js', 
                       self.session.get(f"{self.WEB_URL}/login").text).group(0)
        bundle = self.session.get(f"{self.WEB_URL}{js}").text

        self.session.headers.update(
            {"X-App-Id": re.search(
                '(?:production:{api:{appId:")(.*?)(?:",appSecret)',
                bundle
            ).group(1)}
        )

        self._app_secret = base64.b64decode(
            (re.search('(?::[a-z].initialSeed\(")(.*?)'
                       '(?:",window.utimezone.berlin)',
                       bundle).group(1) 
             + "".join(re.search('(?:Berlin",info:")(.*?)'
                                 '(?:",extras:")(.*?)(?:"},{offset)', 
                                 bundle).groups()))[:-44]
        ).decode()

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

        resp = self.session.request(method, url, **kwargs)
        if resp.status_code not in range(200, 299):
            error = resp.json()
            raise RuntimeError(f'{error["code"]} {error["message"]}')
        return resp

    def get_album(self, album_id: str) -> dict[str, Any]:

        """
        Get Qobuz catalog information for an album.

        Parameters
        ----------
        album_id : `str`
            Qobuz album ID.

        Returns
        -------
        album : `dict`
            Qobuz catalog information for the album in JSON format.
        """

        return self._get_json(f"{self.API_URL}/album/get",
                              params={"album_id": album_id})
    
    def get_artist(
            self, artist_id: Union[int, str], *, albums: bool = True,
            limit: int = None, offset: int = None) -> dict[str, Any]:

        """
        Get Qobuz catalog information for an album.

        Parameters
        ----------
        artist_id : `int` or `str`
            Qobuz artist ID.

        albums : `bool`, keyword-only, default: :code:`True`
            Specifies whether information on the artist's albums is
            returned.

        limit : `int`, keyword-only, optional
            The maximum number of albums to return. Has no effect if 
            :code:`albums=False`.

            **Default**: :code:`50`.

        offset : `int`, keyword-only, optional
            The index of the first album to return. Use with `limit` to
            get the next page of albums. Has no effect if 
            :code:`albums=False`.

            **Default**: :code:`0`.

        Returns
        -------
        artist : `dict`
            Qobuz catalog information for the artist in JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/artist/get",
            params={"artist_id": artist_id,
                    "extra": "albums" if albums else None,
                    "limit": limit, 
                    "offset": offset}
        )
    
    def get_label(
            self, label_id: Union[int, str], *, albums: bool = False,
            limit: int = None, offset: int = None) -> dict[str, Any]:

        """
        Get Qobuz catalog information for a record label.

        Parameters
        ----------
        label_id : `int` or `str`
            Qobuz record label ID.

        albums : `bool`, keyword-only, default: :code:`True`
            Specifies whether information on the albums released by the
            record label is returned.

        limit : `int`, keyword-only, optional
            The maximum number of albums to return. Has no effect if 
            :code:`albums=False`.

            **Default**: :code:`50`.

        offset : `int`, keyword-only, optional
            The index of the first album to return. Use with `limit` to
            get the next page of albums. Has no effect if 
            :code:`albums=False`.

            **Default**: :code:`0`.

        Returns
        -------
        label : `dict`
            Qobuz catalog information for the record label in JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/label/get",
            params={"label_id": label_id,
                    "extra": "albums" if albums else None,
                    "limit": limit, 
                    "offset": offset}
        )

    def get_playlist(
            self, playlist_id: Union[int, str], *, tracks: bool = True,
            limit: int = None, offset: int = None) -> dict[str, Any]:
        
        """
        Get Qobuz catalog information for a playlist.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz playlist ID.

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
            Qobuz catalog information for the playlist in JSON format.
        """

        return self._get_json(
            f"{self.API_URL}/playlist/get",
            params={"playlist_id": playlist_id,
                    "extra": "tracks" if tracks else None,
                    "limit": limit, 
                    "offset": offset}
        )

    def get_track(self, track_id: Union[int, str]) -> dict[str, Any]:

        """
        Get Qobuz catalog information for a track.

        Parameters
        ----------
        track_id : `int` or `str`
            Qobuz track ID.

        Returns
        -------
        track : `dict`
            Qobuz catalog information for the track in JSON format.
        """

        return self._get_json(f"{self.API_URL}/track/get",
                              params={"track_id": track_id})
        
    def get_track_file_url(
            self, track_id: Union[int, str], quality: Union[int, str] = 27
        ) -> dict[str, Any]:
        
        """
        Get the file URL for a track.

        .. admonition:: User authentication

           Requires user authentication and an active Qobuz streaming 
           plan to access the URL for the full, high-quality audio track.

        Parameters
        ----------
        track_id : `int` or `str`
            Qobuz track ID.

        quality : `int` or `str`, default: :code:`27`
            Maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` or :code:`"LOSSY"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` or :code:`"HI-RES-96"` for up to 24-bit,
                 96 kHz Hi-Res FLAC.
               * :code:`27` or :code:`"HI-RES-192"` for up to 24-bit,
                 192 kHz Hi-Res FLAC.
                 
        Returns
        -------
        url : `dict`
            A dictionary containing the URL and accompanying 
            information, such as the audio format, bit depth, etc.
        """
        
        if isinstance(quality, int) or quality.isnumeric():
            if int(quality) not in {5, 6, 7, 27}:
                raise ValueError("Invalid audio quality.")
        else:
            if quality not in {"LOSSY", "CD", "HI-RES-96", "HI-RES-192"}:
                raise ValueError("Invalid audio quality.")
            else:
                quality = self._AUDIO_QUALITIES[quality]

        if self._me is None \
                or self._me["credential"]["description"] == "Qobuz Member":
            wmsg = ("No user authentication or Qobuz streaming plan "
                    "detected. The URL will lead to a 30-second preview "
                    "of the track.")
            warnings.warn(wmsg)

        timestamp = time.time()
        return self._get_json(
            f"{self.API_URL}/track/getFileUrl",
            params={
                "request_ts": timestamp,
                "request_sig": hashlib.md5(
                    (f"trackgetFileUrlformat_id{quality}"
                     f"intentstreamtrack_id{track_id}"
                     f"{timestamp}{self._app_secret}").encode()
                ).hexdigest(),
                "track_id": track_id,
                "format_id": quality,
                "intent": "stream"
            }
        )
    
    def get_track_stream(
            self, track_id: Union[int, str], *, quality: Union[int, str] = 27,
            save: bool = False, path: str = None, folder: bool = False, 
            metadata: bool = True) -> Union[None, bytes]:
        
        """
        Get a track's audio stream data.

        .. admonition:: User authentication

           Requires user authentication and an active Qobuz streaming 
           plan for the full, high-quality audio stream.

        .. note::
           This method is provided for convenience and is not a Qobuz 
           API endpoint.

        Parameters
        ----------
        track_id : `int` or `str`
            Qobuz track ID.

        quality : `str`, keyword-only, default: :code:`27`
            Maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` or :code:`"LOSSY"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` or :code:`"HI-RES-96"` for up to 24-bit,
                 96 kHz Hi-Res FLAC.
               * :code:`27` or :code:`"HI-RES-192"` for up to 24-bit,
                 192 kHz Hi-Res FLAC.

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

        data = self.get_track(track_id)
        credits = self.get_track_credits(
            performers=data["performers"], roles=["mainartist", "writer"]
        )
        i = credits["mainartist"].index(data["performer"]["name"])
        if i != 0:
            credits["mainartist"].insert(0, credits["mainartist"].pop(i))

        artist = utility.multivalue_formatter(credits["mainartist"], False)
        title = data["title"]

        if save:
            if path is not None:
                os.chdir(path)
            if folder:
                dirname = f"{artist} - {title}"
                if not os.path.isdir(dirname):
                    os.mkdir(dirname)
                os.chdir(dirname)

        file = self.get_track_file_url(track_id, quality=quality)
        format = file["mime_type"][6:]
        with urllib.request.urlopen(file["url"]) as r:
            stream = r.read()

        if save:
            file = (f"{data['track_number']:02} "
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

                Track.from_qobuz(
                    data,
                    artists=credits["mainartist"],
                    composers=credits["writer"],
                    artwork=data["album"]["image"]["large"],
                    comment=f"https://open.qobuz.com/track/{data['id']}"
                )
                Track.write_metadata()

            if folder:
                os.chdir("..")

    def get_track_credits(
            self, track_id: Union[int, str] = None, *, performers: str = None,
            roles: list = None) -> dict[str, list]:

        """
        Get credits for a track.
        
        .. note::
           This method is provided for convenience and is not a Qobuz 
           API endpoint.

        Parameters
        ----------
        track_id : `int` or `str`
            Qobuz track ID.

        performers : `str`, keyword-only, optional
            An unformatted string containing the track credits obtained
            from calling :meth:`Session.get_track`.

        roles : `list`, keyword-only, optional
            Role filter.

            **Valid values**: :code:`"mainartist"`, :code:`"producer"`, 
            :code:`"writer"`, etc.

        Returns
        -------
        credits : `dict`
            A dictionary containing the track contributors.
        """
        
        if performers is None:
            if track_id is None:
                emsg = ("Either a Qobuz track ID or an unformatted "
                        "string containing the track credits must be "
                        "provided.")
                raise ValueError(emsg)
            performers = self.get_track(track_id)["performers"]

        performers = {p[0]: [r.lower() for r in p[1:]] for p in 
                      (p.split(", ") for p in performers.split(" - "))}
        
        credits = {}
        if roles is None:
            roles = set(c for r in performers.values() for c in r)
        for role in roles:
            credits[role] = [p for p, r in performers.items() if role in r]
        
        return credits
    
    def get_user_favorites(self, type: str = None) -> dict[str, dict]:

        """
        Get the user's favorite albums, artists, articles, and tracks.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        type : `str`
            Media type to return. If not specified, all of the user's
            favorite items are returned.

            .. container::
            
               **Valid values**: :code:`"albums"`, :code:`"articles"`,
               :code:`"artists"`, and :code:`"tracks"`.
        
        Returns
        -------
        favorites : `dict`
            The user's favorite items.
        """

        if self._me is None:
            raise RuntimeError("You are not logged in.")

        if type not in {"albums", "articles", "artists", "tracks"}:
            raise ValueError("Invalid media type.")

        timestamp = time.time()
        return self._get_json(
            f"{self.API_URL}/favorite/getUserFavorites",
            params={
                "request_ts": timestamp,
                "request_sig": hashlib.md5(
                    (f"favoritegetUserFavorites{timestamp}"
                     f"{self._app_secret}").encode()
                ).hexdigest(),
                "type": type
            }
        )