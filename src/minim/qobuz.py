"""
Qobuz
=====
.. moduleauthor:: Benjamin Ye <GitHub: @bbye98>

This module contains a minim implementation of the private Qobuz API.
"""

import base64
import datetime
import hashlib
import os
import re
import subprocess
import time
from typing import Any, Union

import requests

from . import audio, utility, warnings

class PrivateAPI:

    """
    A Qobuz private API object.

    .. attention::

       This class is pending a major refactor.

    This class contains a minimal Python implementation of the Qobuz API,
    which allows songs, collections (albums, playlists), and performers to
    be queried, and information about them to be retrieved. As the Qobuz API
    is not public, there is no available official documentation for it. Its
    endpoints have been determined by watching HTTP network traffic.

    Without authentication, the Qobuz API can be used to query for and
    retrieve information about media and performers.

    By logging into Qobuz, the Qobuz API allows access to user information
    and media streaming (with an active Qobuz streaming plan). Valid user
    credentials (email address and password) or an user authorization token
    must either be provided explicitly to the :class:`PrivateAPI` constructor
    or be stored in the operating system's environment variables as 
    :code:`QOBUZ_EMAIL`, :code:`QOBUZ_PASSWORD`, and 
    :code:`QOBUZ_USER_AUTH_TOKEN`, respectively.

    Parameters
    ----------
    email : `str`, keyword-only, optional
        Account email address. If it is not stored as 
        :code:`QOBUZ_EMAIL` in the operating system's environment
        variables, it can be provided here.

    password : `str`, keyword-only, optional
        Account password. If it is not stored as :code:`QOBUZ_PASSWORD`
        in the operating system's environment variables, it can be 
        provided here.

    app_id : `str`, keyword-only, optional
        Qobuz app ID. If not provided, it will be retrieved 
        automatically.
    
    app_secret : `str`, keyword-only, optional
        Qobuz app secret. If not provided, it will be retrieved 
        automatically.

    auth_token : `str`, keyword-only, optional
        User authentication token. If it is not stored as 
        :code:`QOBUZ_USER_AUTH_TOKEN` in the operating system's 
        environment variables, it can be provided here.

    authenticate : `bool`, keyword-only, default: :code:`True`
        Determines whether user authentication is attempted.

    user_agent : `str`, keyword-only, optional
        User agent information to send in the header of HTTP requests.

    Attributes
    ----------
    API_URL : `str`
        URL for the Qobuz API.

    WEB_URL : `str`
        URL for the Qobuz web player.
    """

    API_URL = "https://www.qobuz.com/api.json/0.2"
    WEB_URL = "https://play.qobuz.com"

    def __init__(
            self, *, email: str = None, password: str = None, 
            app_id: str = None, app_secret: str = None, auth_token: str = None,
            authenticate: bool = True, user_agent: str = None):
        
        self.session = requests.Session()
        if user_agent:
            self.session.headers.update({"User-Agent": user_agent})

        if app_secret is None:
            self._get_app_id_and_secret()
        else:
            self.session.headers.update({"X-App-Id": app_id})
            self._app_secret = app_secret
        self.login(email, password, auth_token=auth_token,
                   authenticate=authenticate)

    def __repr__(self) -> None:

        """
        Set the unique string representation of the Qobuz API object.
        """

        return f"minim.qobuz.PrivateAPI() # {self.__str__()}"

    def __str__(self) -> None:

        """
        Set the readable string representation of the Qobuz API object.
        """

        if self._me:
            return (f"Qobuz API: {self._me['display_name']} "
                    f"[ID: {self._me['id']}, email: {self._me['email']}, "
                    f"subscription: {self._me['credential']['description']}]")
        return "Qobuz API: not logged in"
    
    def _get_app_id_and_secret(self) -> None:

        """
        Get the Qobuz app ID and secret.
        """

        js = re.search("/resources/.*/bundle.js", 
                       self.session.get(f"{self.WEB_URL}/login").text).group(0)
        bundle = self.session.get(f"{self.WEB_URL}{js}").text

        self.session.headers.update(
            {"X-App-Id": re.search(
                '(?:production:{api:{appId:")(.*?)(?:",appSecret)',
                bundle
            ).group(1)}
        )

        self._app_secret = [
            base64.b64decode("".join((s, *m.groups()))[:-44]).decode() 
            for s, m in (
                (s, re.search(f'(?:{c.capitalize()}",info:")(.*?)(?:",extras:")'
                              '(.*?)(?:"},{offset)', 
                              bundle))
                for s, c in re.findall('(?:[a-z].initialSeed\(")(.*?)'
                                       '(?:",window.utimezone.)(.*?)\)', 
                                       bundle)) if m
        ][1]

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
    
    def login(
            self, email: str = None, password: str = None, *,
            auth_token: str = None, authenticate: bool = True) -> None:
        
        """
        Log into Qobuz or switch accounts.

        Parameters
        ----------
        email : `str`, optional
            Account email address. If it is not stored as 
            :code:`QOBUZ_EMAIL` in the operating system's environment
            variables, it can be provided here.

        password : `str`, optional
            Account password. If it is not stored as 
            :code:`QOBUZ_PASSWORD` in the operating system's environment
            variables, it can be provided here.

        auth_token : `str`, keyword-only, optional
            User authentication token. If it is not stored as 
            :code:`QOBUZ_USER_AUTH_TOKEN` in the operating system's 
            environment variables, it can be provided here.

        authenticate : `bool`, keyword-only, default: :code:`True`
            Determines whether user authentication is attempted.
        """

        if authenticate and auth_token is None \
                and (email is None or password is None):
            auth_token = os.environ.get("QOBUZ_USER_AUTH_TOKEN")
            email = os.environ.get("QOBUZ_EMAIL")
            password = os.environ.get("QOBUZ_PASSWORD")
            if auth_token is None and (email is None or password is None):
                authenticate = False

        if not authenticate:
            self._me = None
        elif auth_token:
            self._me = self.get_me(auth_token)
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

    ### ALBUMS ################################################################

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
            Qobuz catalog information for the album.
        """

        return self._get_json(f"{self.API_URL}/album/get",
                              params={"album_id": album_id})
    
    def get_featured_albums(
            self, type: str = "new-releases", *, limit: int = None,
            offset: int = None) -> dict[str, Any]:

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
        """

        ALBUM_FEATURE_TYPES = {
            "best-sellers", "editor-picks", "ideal-discography", 
            "most-featured", "most-streamed", "new-releases", 
            "new-releases-full", "press-awards", "recent-releases",
            "qobuzissims", "harmonia-mundi", "universal-classic",
            "universal-jazz", "universal-jeunesse", "universal-chanson"
        }

        if type not in ALBUM_FEATURE_TYPES:
            raise ValueError("Invalid feature type. The supported "
                             f"types are {', '.join(ALBUM_FEATURE_TYPES)}.")

        return self._get_json(
            f"{self.API_URL}/album/getFeatured", 
            params={"type": type, "limit": limit, "offset": offset}
        )

    ### ARTISTS ###############################################################

    def get_artist(
            self, artist_id: Union[int, str], *, 
            extras: Union[str, list[str]] = None,
            limit: int = None, offset: int = None) -> dict[str, Any]:

        """
        Get Qobuz catalog information for an artist.

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
            Qobuz catalog information for the artist.
        """

        return self._get_json(
            f"{self.API_URL}/artist/get",
            params={"artist_id": artist_id,
                    "extra": extras if extras is None or isinstance(extras, str) 
                             else ",".join(extras),
                    "limit": limit, 
                    "offset": offset}
        )
    
    ### RECORD LABELS #########################################################

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
        """

        return self._get_json(
            f"{self.API_URL}/label/get",
            params={"label_id": label_id,
                    "extra": "albums" if albums else None,
                    "limit": limit, 
                    "offset": offset}
        )

    ### PLAYLISTS #############################################################

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
            Qobuz catalog information for the playlist.
        """

        return self._get_json(
            f"{self.API_URL}/playlist/get",
            params={"playlist_id": playlist_id,
                    "extra": "tracks" if tracks else None,
                    "limit": limit, 
                    "offset": offset}
        )
    
    def get_featured_playlists(
            self, type: str = "editor-picks", *, limit: int = None,
            offset: int = None) -> dict[str, Any]:
        
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
        """

        PLAYLIST_FEATURE_TYPES = {"editor-picks", "last-created"}

        if type not in PLAYLIST_FEATURE_TYPES:
            raise ValueError("Invalid feature type. The supported "
                             "types are "
                             f"{', '.join(PLAYLIST_FEATURE_TYPES)}.")

        return self._get_json(
            f"{self.API_URL}/playlist/getFeatured",
            params={"type": type, "limit": limit, "offset": offset}
        )["playlists"]

    ### USER PLAYLISTS ########################################################

    def create_playlist(
            self, name: str, *, description: str = None, public: bool = True,
            collaborative: bool = False) -> dict[str, Any]:
        
        """
        Create a user playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        name : `str`
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
            Qobuz catalog information for the newly created playlist.
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.create_playlist() "
                               "requires user authentication.")

        data = {"name": name, "is_public": str(public).lower(), 
                "is_collaborative": str(collaborative).lower()}
        if description:
            data["description"] = description

        return self._request(
            "post", f"{self.API_URL}/playlist/create", data=data
        ).json()
    
    def update_playlist(
            self, playlist_id: Union[int, str], *, name: str = None,
            description: str = None, public: bool = None, 
            collaborative: bool = None) -> dict[str, Any]:
        
        """
        Update the title, description, and/or privacy of a playlist 
        owned by the current user.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz playlist ID.

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
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.update_playlist() "
                               "requires user authentication.")

        data = {"playlist_id": playlist_id}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if public is not None:
            data["is_public"] = str(public).lower()
        if collaborative is not None:
            data["is_collaborative"] = str(collaborative).lower()

        return self._request("post", f"{self.API_URL}/playlist/update", 
                             data=data).json()

    def delete_playlist(self, playlist_id: Union[int, str]) -> None:

        """
        Delete a user playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz playlist ID.
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.delete_playlist() "
                               "requires user authentication.")
        
        self._request("post", f"{self.API_URL}/playlist/delete", 
                      data={"playlist_id": playlist_id})

    def update_playlist_position(
            self, from_playlist_id: Union[int, str], 
            to_playlist_id: Union[int, str]) -> None:
        
        """
        Organize a user's playlists.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        from_playlist_id : `int` or `str`
            Qobuz playlist ID of playlist to move.

        to_playlist_id : `int` or `str`
            Qobuz playlist ID of playlist to swap with that in 
            `from_playlist_id`.
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.update_playlist_position() "
                               "requires user authentication.")

        self._request("post", 
                      f"{self.API_URL}/playlist/updatePlaylistsPosition",
                      data={"playlist_ids": [from_playlist_id, to_playlist_id]})

    def add_playlist_tracks(
            self, playlist_id: Union[int, str], 
            track_ids: Union[int, str, list[Union[int, str]]], *,
            duplicate: bool = False) -> dict[str, Any]:
        
        """
        Add tracks to a user playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz playlist ID.

        track_ids : `int`, `str`, or `list`
            Qobuz track ID(s).

        duplicate : `bool`, keyword-only, default: :code:`False`
            Determines whether duplicate tracks should be added to the
            playlist.

        Returns
        -------
        playlist : `str`
            Qobuz catalog information for the updated playlist.
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.add_playlist_track() "
                               "requires user authentication.")
        
        if isinstance(track_ids, list):
            track_ids = ",".join(str(t) for t in track_ids)

        return self._request(
            "post", f"{self.API_URL}/playlist/addTracks",
            data={"playlist_id": playlist_id, "track_ids": track_ids,
                  "no_duplicate": str(not duplicate).lower()}
        ).json()
    
    def move_playlist_tracks(
            self, playlist_id: Union[int, str], 
            playlist_track_ids: Union[int, str, list[Union[int, str]]], 
            insert_before: int) -> dict[str, Any]:

        """
        Move tracks in a user playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz playlist ID.

        playlist_track_ids : `int`, `str`, or `list`
            Qobuz playlist track ID(s).

        insert_before : `int`
            Position to which to move the tracks specified in 
            `track_ids`.

        Returns
        -------
        playlist : `str`
            Qobuz catalog information for the updated playlist.
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.move_playlist_track() "
                               "requires user authentication.")

        if isinstance(playlist_track_ids, list):
            playlist_track_ids = ",".join(str(t) for t in playlist_track_ids)

        return self._request("post", 
                             f"{self.API_URL}/playlist/updateTracksPosition",
                             data={"playlist_id": playlist_id, 
                                   "playlist_track_ids": playlist_track_ids,
                                   "insert_before": insert_before}).json()

    def delete_playlist_tracks(
            self, playlist_id: Union[int, str], 
            playlist_track_ids: Union[int, str, list[Union[int, str]]]
        ) -> dict[str, Any]:

        """
        Delete tracks from a user playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz playlist ID.

        playlist_track_ids : `int`, `str`, or `list`
            Qobuz playlist track ID(s).

            .. note::
               Playlist track IDs are not the same as track IDs. To get
               playlist track IDs, use :meth:`get_playlist`.
        
        Returns
        -------
        playlist : `str`
            Qobuz catalog information for the updated playlist.
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.delete_playlist_track() "
                               "requires user authentication.")

        if isinstance(playlist_track_ids, list):
            playlist_track_ids = ",".join(str(t) for t in playlist_track_ids)

        return self._request(
            "post", f"{self.API_URL}/playlist/deleteTracks",
            data={"playlist_id": playlist_id, 
                  "playlist_track_ids": playlist_track_ids}
        ).json()
    
    def favorite_playlist(self, playlist_id: Union[int, str]) -> None:

        """
        Favorite (or subscribe to) a playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz playlist ID.
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.favorite_playlist() "
                               "requires user authentication.")
        
        self._request("post", f"{self.API_URL}/playlist/subscribe", 
                      data={"playlist_id": playlist_id})

    def unfavorite_playlist(self, playlist_id: Union[int, str]) -> None:

        """
        Unfavorite (or unsubscribe from) a playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist_id : `int` or `str`
            Qobuz playlist ID.
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.unfavorite_playlist() "
                               "requires user authentication.")
        
        self._request("post", f"{self.API_URL}/playlist/unsubscribe", 
                      data={"playlist_id": playlist_id})

    ### TRACKS ################################################################

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
            Qobuz catalog information for the track.
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

               * :code:`5` or :code:`"MP3"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` or :code:`"HI-RES"` for up to 24-bit,
                 192 kHz Hi-Res FLAC.
                 
        Returns
        -------
        url : `dict`
            A dictionary containing the URL and accompanying 
            information, such as the audio format, bit depth, etc.
        """
        
        AUDIO_QUALITIES = {"MP3": 5, "CD": 6, "HI-RES": 27}

        if isinstance(quality, int) or quality.isnumeric():
            if int(quality) not in {5, 6, 7, 27}:
                audio_qualities = ", ".join(f"{s} ({i})" for s, i 
                                            in AUDIO_QUALITIES.items())
                emsg = ("Invalid audio quality. The supported qualities "
                        f"are {audio_qualities}.")
                raise ValueError(emsg)
        else:
            if quality not in {"MP3", "CD", "HI-RES"}:
                audio_qualities = ", ".join(f"{s} ({i})" for s, i 
                                            in AUDIO_QUALITIES.items())
                emsg = ("Invalid audio quality. The supported qualities "
                        f"are {audio_qualities}.")
                raise ValueError(emsg)
            else:
                quality = AUDIO_QUALITIES[quality]

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
            from calling :meth:`get_track`.

        roles : `list`, keyword-only, optional
            Role filter. The special :code:`"Composers"` filter will 
            combine the :code:`"Composer"`, :code:`"ComposerLyricist"`,
            :code:`"Lyricist"`, and :code:`"Writer"` roles.

            .. note::
               `roles` is case-sensitive; all values must be in Pascal
               case.

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

        COMPOSER_ROLES = {"Composer", "ComposerLyricist", "Lyricist", "Writer"}

        if performers is None:
            if track_id is None:
                emsg = ("Either a Qobuz track ID or an unformatted "
                        "string containing the track credits must be "
                        "provided.")
                raise ValueError(emsg)
            performers = self.get_track(track_id)["performers"]

        if performers is None:
            return {}
        
        _performers = {}
        for p in performers.split(" - "):
            regex = re.search("(^.*[A-Za-z]\.|^.*&.*|[\d\s\w].*?)(?:, )(.*)",
                              p.rstrip())
            if regex:
                performer, performer_roles = regex.groups()
                _performers[performer] = performer_roles.split(", ")
        
        credits = {}
        if roles is None:
            roles = set(c for r in _performers.values() for c in r)
        if "Composers" in roles:
            roles.remove("Composers")
            lookup = set()
            credits["composers"] = [
                p for cr in COMPOSER_ROLES for p, r in _performers.items() 
                if cr in r and p not in lookup and lookup.add(p) is None
            ]
        for role in roles:
            credits[
                "_".join(
                    re.findall("(?:[A-Z][a-z]+)(?:-[A-Z][a-z]+)?", role)
                ).lower()
            ] = [p for p, r in _performers.items() if role in r]
        
        return credits
    
    def get_curated_tracks(
            self, *, limit: int = None, offset: int = None
        ) -> list[dict[str, Any]]:

        """
        Get weekly curated tracks for the user.

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
            Curated tracks.
        """

        return self._get_json(f"{self.API_URL}/dynamic-tracks/get",
                              params={"type": "weekly", "limit": limit,
                                      "offset": offset})

    ### SEARCH ################################################################

    def search(
            self, query: str, type: str = None, *, hi_res: bool = False, 
            new_release: bool = False, strict: bool = False, limit: int = 10, 
            offset: int = 0) -> dict[str, Any]:
        
        """
        Search Qobuz for media and performers.

        Parameters
        ----------
        query : `str`
            Search query.

        type : `str`, keyword-only, optional
            Category to search in. If specified, only matching releases 
            and tracks will be returned.

            .. note::
               `type` is case-sensitive; all values must be in Pascal
               case.

            **Valid values**: :code:`"MainArtist"`, :code:`"Composer"`, 
            :code:`"Performer"`, :code:`"ReleaseName"`, and 
            :code:`"Label"`.

        hi_res : `bool`, keyword-only, :code:`False`
            High-resolution audio only.

        new_release : `bool`, keyword-only, :code:`False`
            New releases only.

        strict : `bool`, keyword-only, :code:`False`
            Enable exact word or phrase matching.

        limit : `int`, keyword-only, default: :code:`10`
            Maximum number of results to return.

        offset : `int`, keyword-only, default: :code:`0`
            Index of the first result to return. Use with `limit` to get
            the next page of search results.

        Returns
        -------
        results : `dict`
            The search results.
        """

        if type and type not in {"MainArtist", "Composer", "Performer", 
                                 "ReleaseName", "Label"}:
            raise ValueError("Invalid search type.")

        if strict:
            query = f'"{query}"'
        if type:
            query += f" #By{type}"
        if hi_res:
            query += " #HiRes"
        if new_release:
            query += " #NewRelease"

        return self._get_json(f"{self.API_URL}/catalog/search",
                              params={"query": query, "limit": limit, 
                                      "offset": offset})

    ### STREAMS ###############################################################

    def get_track_stream(
            self, track_id: Union[int, str], *, quality: Union[int, str] = 27,
            save: bool = False, path: str = None, folder: bool = False, 
            metadata: bool = True) -> Union[bytes, str]:
        
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

               * :code:`5` or :code:`"MP3"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
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
        stream : `bytes` or `str`
            Audio stream data. If :code:`save=True`, the stream data is 
            saved to an audio file and its filename is returned instead.
        """

        AUDIO_FORMATS_EXTENSIONS = {"flac": "flac", "mpeg": "mp3"}

        json = self.get_track(track_id)
        credits = self.get_track_credits(
            performers=json["performers"], 
            roles=["MainArtist", "FeaturedArtist", "Composers"]
        )
        if json["performer"]["name"] in credits["main_artist"]:
            i = credits["main_artist"].index(json["performer"]["name"])
            if i != 0:
                credits["main_artist"].insert(0, credits["main_artist"].pop(i))
        else:
            credits["main_artist"] = [json["performer"]["name"]]

        artist = utility.multivalue_formatter(credits["main_artist"], False)
        title = json["title"].rstrip()

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
        with self.session.get(file["url"]) as r:
            stream = r.content

        if save:
            file = (f"{json['track_number']:02} {json['title']}").rstrip()
            if credits["featured_artist"] and "feat." not in file:
                file += (" [feat. {}]" if "(" in file 
                         else " (feat. {})").format(
                    utility.multivalue_formatter(credits['featured_artist'], 
                                                 False)
                )
            if json["version"]:
                file += (" [{}]" if "(" in file else " ({})").format(
                    json['version']
                )
            file = (file.translate({ord(c): '_' for c in '<>:"/\|?*'}) 
                    + f".{AUDIO_FORMATS_EXTENSIONS[format]}")
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
                    json, main_artist=credits["main_artist"],
                    feat_artist=credits["featured_artist"],
                    composer=credits["composers"],
                    artwork=json["album"]["image"]["large"],
                    comment=f"https://open.qobuz.com/track/{json['id']}"
                )
                Track.write_metadata()

            if folder:
                os.chdir("..")
            return f"{os.getcwd()}/{file}"
        
        else:
            return stream

    def get_collection_streams(
            self, id: Union[int, str], type: str, *, 
            quality: Union[int, str] = 27, save: bool = False, 
            path: str = None, folder: bool = False, metadata: bool = True
        ) -> list[Union[bytes, str]]:

        """
        Get audio stream data for all tracks in an album or a playlist.

        .. admonition:: User authentication

           Requires user authentication and an active Qobuz streaming 
           plan for full, high-quality audio streams.

        .. note::
           This method is provided for convenience and is not a Qobuz 
           API endpoint.

        Parameters
        ----------
        id : `int` or `str`
            Qobuz collection ID.

        type : `str`
            Qobuz collection type.

            **Valid values**: :code:`"album"` and :code:`"playlist"`.

        quality : `str`, keyword-only, default: :code:`27`
            Maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` or :code:`"MP3"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` or :code:`"HI-RES"` for up to 24-bit,
                 192 kHz Hi-Res FLAC.

        save : `bool`, keyword-only, default: :code:`False`
            Determines whether the streams are saved to audio files.

        path : `str`, keyword-only, optional
            If :code:`save=True`, path in which the audio files are 
            saved.

        folder : `bool`, keyword-only, default: :code:`False`
            Determines whether a folder in `path` (or in the current
            directory if `path` is not specified) is created to hold the
            audio files.

        metadata : `bool`, keyword-only, default: :code:`True`
            Determines whether the audio files' metadata is
            populated.

        Returns
        -------
        streams : `list`
            Audio stream data. If :code:`save=True`, the streams are
            saved to audio files and their filenames are returned 
            instead.
        """

        TYPES = {"album", "playlist"}
        if type not in TYPES:
            emsg = ("Invalid collection type. The supported types are " 
                    f"{'', ''.join(TYPES)}.")
            raise ValueError(emsg)

        if type == "album":
            json = self.get_album(id)
            artist = [a["name"] for a in json["artists"]]
            main_artist = json["artist"]["name"]
            if main_artist in artist:
                i = artist.index(main_artist)
                if i != 0:
                    artist.insert(0, artist.pop(i))
                artist = utility.multivalue_formatter(artist, False)
            else:
                artist = main_artist
            title = json["title"].rstrip()
        elif type == "playlist":
            json = self.get_playlist(id, limit=500)
            if json["featured_artists"]:
                artist = utility.multivalue_formatter(
                    [a["name"] for a in json["featured_artists"]], 
                    False
                )
            else:
                artist = json["owner"]["name"]
            title = json["name"]
        items = json["tracks"]["items"]

        streams = []
        if save:
            if path is not None:
                os.chdir(path)
            if folder:
                dirname = f"{artist} - {title}"
                if not os.path.isdir(dirname):
                    os.mkdir(dirname)
                os.chdir(dirname)

        for item in items:
            streams.append(
                self.get_track_stream(item["id"], quality=quality,
                                      save=save, metadata=metadata) \
                if item["streamable"] else None
            )
        
        if save and folder:
            os.chdir("..")
        return streams

    ### USER ##################################################################

    def get_me(self, auth_token: str = None) -> dict[str, Any]:

        """
        Get the user's information.

        Parameters
        ----------
        auth_token : `str`, optional
            User authentication token.

        Returns
        -------
        me : `dict`
            The user's information. Returns :code:`None` if not
            authenticated.
        """

        if auth_token is None:
            auth_token = self.session.headers.get("X-User-Auth-Token")

        if auth_token is None:
            return None

        return self._get_json(
            f"{self.API_URL}/user/get", 
            params={"user_auth_token": auth_token}
        )

    def get_user_favorites(self, type: str = None) -> dict[str, dict]:

        """
        Get the user's favorite albums, artists, and tracks.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        type : `str`
            Media type to return. If not specified, all of the user's
            favorite items are returned.

            .. container::
            
               **Valid values**: :code:`"albums"`, :code:`"artists"`, 
               and :code:`"tracks"`.
        
        Returns
        -------
        favorites : `dict`
            The user's favorite items.
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.get_user_favorites() "
                               "requires user authentication.")

        TYPES = {"albums", "artists", "tracks"}
        if type not in TYPES:
            emsg = ("Invalid feature type. The supported types are " 
                    f"{', '.join(TYPES)}.")
            raise ValueError(emsg)

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
    
    def get_user_playlists(
            self, *, limit: int = None, offset: int = None) -> dict[str, Any]:
        
        """
        Get the user's custom and favorite playlists.

        .. admonition:: User authentication

           Requires user authentication.

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
            The user's playlists.
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.get_user_playlists() "
                               "requires user authentication.")
        
        return self._get_json(
            f"{self.API_URL}/playlist/getUserPlaylists",
            params={"limit": limit, "offset": offset}
        )["playlists"]
    
    def get_user_purchases(
            self, type: str = "albums", *, limit: int = None, 
            offset: int = None) -> dict[str, Any]:

        """
        Get the user's purchases.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        type : `str`, default: :code:`"albums"`
            Item type.

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
            The user's purchases.
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.get_user_purchases() "
                               "requires user authentication.")
        
        TYPES = {"albums", "tracks"}
        if type not in TYPES:
            emsg = ("Invalid feature type. The supported types are " 
                    f"{', '.join(TYPES)}.")
            raise ValueError(emsg)

        return self._get_json(f"{self.API_URL}/purchase/getUserPurchases",
                              params={"type": type, "limit": limit, 
                                      "offset": offset})[type]
    
    def favorite_items(
            self, *, album_ids: Union[str, list[str]] = None, 
            artist_ids: Union[int, str, list[Union[int, str]]] = None,
            track_ids: Union[int, str, list[Union[int, str]]] = None) -> None:

        """
        Favorite albums, artists, and/or tracks.

        .. admonition:: User authentication

           Requires user authentication.

        .. note::
           For playlists, see :meth:`favorite_playlist`.

        Parameters
        ----------
        album_ids : `str` or `list`, keyword-only, optional
            Qobuz album ID(s).

        artist_ids : `int`, `str`, or `list`, keyword-only, optional
            Qobuz artist ID(s).

        track_ids : `int`, `str`, or `list`, keyword-only, optional
            Qobuz track ID(s).
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.favorite() "
                               "requires user authentication.")

        data = {}
        if album_ids:
            data["album_ids"] = ",".join(str(a) for a in album_ids) \
                                if isinstance(album_ids, list) \
                                else album_ids
        if artist_ids:
            data["artist_ids"] = ",".join(str(a) for a in artist_ids) \
                                 if isinstance(artist_ids, list) \
                                 else artist_ids
        if track_ids:
            data["track_ids"] = ",".join(str(a) for a in track_ids) \
                                if isinstance(track_ids, list) \
                                else track_ids

        self._request("post", f"{self.API_URL}/favorite/create", data=data)

    def unfavorite_items(
            self, *, album_ids: Union[str, list[str]] = None, 
            artist_ids: Union[int, str, list[Union[int, str]]] = None,
            track_ids: Union[int, str, list[Union[int, str]]] = None) -> None:

        """
        Unfavorite albums, artists, and/or tracks. 

        .. admonition:: User authentication

           Requires user authentication.

        .. note::
           For playlists, see :meth:`unfavorite_playlist`.

        Parameters
        ----------
        album_ids : `str` or `list`, keyword-only, optional
            Qobuz album ID(s).

        artist_ids : `int`, `str`, or `list`, keyword-only, optional
            Qobuz artist ID(s).

        track_ids : `int`, `str`, or `list`, keyword-only, optional
            Qobuz track ID(s).
        """

        if self._me is None:
            raise RuntimeError("qobuz.PrivateAPI.unfavorite() "
                               "requires user authentication.")

        data = {}
        if album_ids:
            data["album_ids"] = ",".join(str(a) for a in album_ids) \
                                if isinstance(album_ids, list) \
                                else album_ids
        if artist_ids:
            data["artist_ids"] = ",".join(str(a) for a in artist_ids) \
                                 if isinstance(artist_ids, list) \
                                 else artist_ids
        if track_ids:
            data["track_ids"] = ",".join(str(a) for a in track_ids) \
                                if isinstance(track_ids, list) \
                                else track_ids

        self._request("post", f"{self.API_URL}/favorite/delete", data=data)

class Album:

    """
    A Qobuz album.

    .. attention::

       This class is pending removal.

    Parameters
    ----------
    album_id : `str`
        Qobuz album ID.

    json : `dict`, keyword-only, optional
        Qobuz catalog information for the album 
        retrieved using :meth:`PrivateAPI.get_album`.

    session : `minim.qobuz.PrivateAPI`, keyword-only, optional
        Qobuz API session.

    **kwargs
        Keyword arguments to pass to the :class:`PrivateAPI` constructor
        if :code:`session=None`.

    Attributes
    ----------
    artists : `dict`
        Artist(s).

        **Format**: 
        
        .. code::

            {"main_artist": [<artist: minim.qobuz.Artist>, 
                             <artist: minim.qobuz.Artist>, ...],
             "featured_artist": [<artist: minim.qobuz.Artist>, 
                                 <artist: minim.qobuz.Artist>, ...]}

    primary_artist : `minim.qobuz.Artist`
        Primary artist.

    awards : `list`
        Accolades and awards.

        **Format**: 
        
        .. code::

           [{"award": <award: str>, "date": <date: datetime.datetime>, 
             "publication": <publication: str>}, 
            ...]

    copyright : `str`
        Copyright information.

    description : `str`
        Description or review.

    disc_count : `int`
        Total number of discs.

    duration : `datetime.timedelta`
        Total duration of all tracks.

    genre : `str`
        Primary genre.

    goodies : `list`
        Additional items included with the album, such as digital 
        booklets.
        
    hi_res : `bool`
        Whether high-resolution audio is available.

    id : `int` or `str`
        Qobuz album ID.

    images : `dict`
        URL(s) to front, back, and thumbnail-sized cover art.

        **Format**:

        .. code::

           {"front": {"small": <url: str>, "large": <url: str>},
            "back": <url: str>,
            "thumbnail": <url: str>}

    label : `minim.qobuz.Label`
        Record label.

    maximum_bit_depth : `int`
        Maximum number of bits per sample.

    maximum_channel_count : `int`
        Maximum number of audio channels.

    maximum_sample_rate : `int`
        Maximum sample rate in kHz.

    official : `bool`
        Whether the album is an official release.

    parental_warning : `bool`
        Whether the album contains explicit content.

    permissions : `dict`
        Access and availability.

        **Valid keys**: :code:`"displayable"`, :code:`"downloadable"`,
        :code:`"previewable"`, :code:`"purchasable"`, 
        :code:`"sampleable"`, and :code:`"streamable"`.

    qobuz_id : `int`
        Internal Qobuz album ID.

    release_date : `datetime.datetime`
        Release date.

    title : `str`
        Title.

    track_count : `int`
        Total number of tracks.

    tracks : `list`
        Tracks in the album.

        .. note::
           If :code:`None`, use :meth:`get_tracks` to get the tracks in
           the album.
        
    upc : `str`
        Universal Product Code (UPC).

    url : `str`
        Qobuz URL.
    """

    _PERMISSIONS = {"purchasable", "streamable", "previewable", 
                    "sampleable", "downloadable", "displayable"}

    def __init__(
            self, album_id: str, *, json: dict[str, Any] = None, 
            session: PrivateAPI = None, **kwargs):

        self._session = session if session else PrivateAPI(**kwargs)
        self.id = album_id
        self._json = self._session.get_album(self.id) if json is None else json
        self._set(self._json)

    def __repr__(self) -> None:

        """
        Set the unique string representation of the Qobuz album
        object.
        """

        return f"minim.qobuz.Album('{self.id}') # {self.__str__()}"

    def __str__(self) -> None:

        """
        Set the readable string representation of the Qobuz album 
        object.
        """

        return (f"Qobuz album: '{self.title}' "
                f"[artist: {self.primary_artist.name}]")
    
    def _set(self, json: dict[str, Any]) -> None:

        """
        Stores information from a JSON object into class variables.

        Parameters
        ----------
        json : `dict`, keyword-only, optional
            Qobuz catalog information for the album 
            retrieved using :meth:`PrivateAPI.get_album`.
        """

        if self._json is not json:
            self._json.update(json)

        self.primary_artist = Artist(json["artist"]["id"], 
                                     session=self._session)
        self.artists = {"main_artist": [], "featured_artist": []}
        if "artists" in json:
            for r in self.artists:
                _r = r.replace("_", "-")
                for a in json["artists"]:
                    if _r in a["roles"]:
                        self.artists[r].append(
                            Artist(a["id"], session=self._session)
                        )
        else:
            self.artists["main_artist"].append(self.primary_artist)
        self.awards = [
            {
                "name": a["name"],
                "date": datetime.datetime.utcfromtimestamp(a["awarded_at"]), 
                "publication": a["publication_name"]
            } 
            for a in json["awards"]
        ] if "awards" in json else None
        self.copyright = json.get("copyright")
        self.images = {"front": {"small": json["image"]["small"], 
                                 "large": json["image"]["large"]}, 
                       "back": json["image"]["back"] 
                               if "back" in json["image"] else None,
                       "thumbnail": json["image"]["thumbnail"]}
        self.description = json.get("description")
        self.disc_count = json.get("media_count")
        self.goodies = json.get("goodies")
        self.duration = datetime.timedelta(seconds=json["duration"]) \
                        if "duration" in json else None
        self.genre = json["genre"]["name"]
        self.hi_res = json["hires"]
        try:
            self.label = Label(json["label"]["id"], data=json["label"], 
                               session=self._session)
        except RuntimeError:
            self.label = None
        self.maximum_bit_depth = json["maximum_bit_depth"]
        self.maximum_channel_count = json["maximum_channel_count"]
        self.maximum_sample_rate = json["maximum_sampling_rate"]
        self.official = json.get("is_official")        
        self.parental_warning = json.get("parental_warning")
        self.permissions = {p: json[p] for p in self._PERMISSIONS}
        self.qobuz_id = json["qobuz_id"]
        self.release_date = min(
            json.get(k) if k in json and json.get(k) else "?" for k in {
                "release_date_original", 
                "release_date_download", 
                "release_date_stream"
            }
        )
        self.release_date = None if self.release_date == "?" else \
                            datetime.datetime.strptime(self.release_date, 
                                                       "%Y-%m-%d")
        self.title = json["title"].rstrip()
        if json["version"]:
            self.title += (" [{}]" if "(" in self.title 
                           else " ({})").format(json["version"])
        self.track_count = json.get("tracks_count")
        if "tracks" in json:
            self.tracks = [Track(t["id"], data=t, session=self._session) 
                           for t in json["tracks"]["items"]]
        elif not hasattr(self, "tracks"):
            self.tracks = None
        self.upc = json.get("upc")
        self.url = json.get("url")

    def refresh(self) -> None:

        """
        Refresh or update the album's information.
        """

        self._set(self._session.get_album(self.id))

    def get_tracks(self) -> None:

        """
        Get tracks in the album.
        """

        if self.tracks is not None:
            warnings.warn(f"Information for {len(self.tracks)} track(s) "
                          "already exists and will be overwritten.")

        self.tracks = [Track(t["id"], data=t, session=self._session) for t in 
                       self._session.get_album(self.id)["tracks"]["items"]]
        
    def get_file_urls(self, quality: Union[int, str] = 27) -> None:

        """
        Get the file URLs for all tracks.

        .. admonition:: User authentication

           Requires user authentication and an active Qobuz streaming 
           plan to access the URL for the full, high-quality audio track.

        Parameters
        ----------
        quality : `int` or `str`, default: :code:`27`
            Maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` or :code:`"MP3"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` or :code:`"HI-RES"` for up to 24-bit,
                 192 kHz Hi-Res FLAC.
        """

        if not hasattr(self, "tracks") or self.tracks is None:
            self.refresh()

        for t in self.tracks:
            t.get_file_url(quality=quality)

    def get_streams(
            self, *, quality: Union[int, str] = 27, save: bool = False,
            path: str = None, folder: bool = False, metadata: bool = True
        ) -> None:

        """
        Get audio stream data for all tracks.

        .. admonition:: User authentication

           Requires user authentication and an active Qobuz streaming 
           plan for full, high-quality audio streams.

        Parameters
        ----------
        quality : `str`, keyword-only, default: :code:`27`
            Maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` or :code:`"MP3"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` or :code:`"HI-RES"` for up to 24-bit,
                 192 kHz Hi-Res FLAC.

        save : `bool`, keyword-only, default: :code:`False`
            Determines whether the streams are saved to audio files.

        path : `str`, keyword-only, optional
            If :code:`save=True`, path in which the audio files are 
            saved.

        folder : `bool`, keyword-only, default: :code:`False`
            Determines whether a folder in `path` (or in the current
            directory if `path` is not specified) is created to hold the
            audio files.

        metadata : `bool`, keyword-only, default: :code:`True`
            Determines whether the audio files' metadata is
            populated.
        """

        if not hasattr(self, "tracks") or self.tracks is None:
            self.get_tracks()

        for t in self.tracks:
            t.get_stream(quality=quality, save=save, path=path, folder=folder,
                         metadata=metadata)
    
    def favorite(self) -> None:

        """
        Favorite the album.

        .. admonition:: User authentication

           Requires user authentication.
        """

        self._session.favorite_items(album_ids=self.id)

    def unfavorite(self) -> None:

        """
        Unfavorite the album.

        .. admonition:: User authentication

           Requires user authentication.
        """

        self._session.unfavorite_items(album_ids=self.id)

class Artist:

    """
    A Qobuz artist.

    .. attention::

       This class is pending removal.

    Parameters
    ----------
    artist_id : `str`
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

    json : `dict`, keyword-only, optional
        Qobuz catalog information for the artist 
        retrieved using :meth:`PrivateAPI.get_artist`.

    session : `minim.qobuz.PrivateAPI`, keyword-only, optional
        Qobuz API session.

    **kwargs
        Keyword arguments to pass to the :class:`PrivateAPI` constructor
        if :code:`session=None`.

    Attributes
    ----------
    albums : `list`
        Albums by the artist.

        .. note::
           If :code:`None`, use :meth:`get_albums` to get albums that
           the artist appears on.

    album_count : `int`
        Number of albums by the artist.

    biography : `str`
        Biography or introduction.

    id : `int` or `str`
        Qobuz artist ID.
        
    image : `dict`
        URLs to profile pictures of varying sizes.

        **Valid keys**: :code:`"small"`, :code:`"medium"`, and 
        :code:`"large"`.

    name : `str`
        Name.

    playlists : `list`
        Playlists inspired by the artist's music.

        .. note::
           If :code:`None`, use :meth:`get_playlists` to get playlists
           featuring the artist's music.

    similar_artist_ids : `list`
        Qobuz artist IDs of similar artists. 
        
        .. note::
           :class:`Artist` objects are not created to avoid infinite 
           recursion.

    tracks : `list`
        Tracks by the artist.

        .. note::
           If :code:`None`, use :meth:`get_tracks` to get tracks that
           the artist appears on.
    """

    def __init__(
            self, artist_id: str, *, extras: Union[str, list[str]] = None,
            limit: int = None, offset: int = None, json: dict[str, Any] = None,
            session: PrivateAPI = None, **kwargs):
        
        self._session = session if session else PrivateAPI(**kwargs)
        self.id = artist_id
        self._json = self._session.get_artist(self.id, extras=extras, 
                                              limit=limit, offset=offset) \
                     if json is None else json
        self._set(self._json) 

    def __repr__(self) -> None:

        """
        Set the unique string representation of the Qobuz artist
        object.
        """

        return f"minim.qobuz.Artist('{self.id}') # {self.__str__()}"

    def __str__(self) -> None:

        """
        Set the readable string representation of the Qobuz artist 
        object.
        """

        return f"Qobuz artist: {self.name}"
    
    def _set(self, json: dict[str, Any]) -> None:

        """
        Stores information from a JSON object into class variables.

        Parameters
        ----------
        json : `dict`, keyword-only, optional
            Qobuz catalog information for the artist 
            retrieved using :meth:`PrivateAPI.get_artist`.
        """

        if self._json is not json:
            self._json.update(json)

        if "albums" in json:
            self.albums = [Album(a["id"], json=a, session=self._session)
                           for a in json["albums"]["items"]]
        elif "album_last_release" in json:
            self.albums = [Album(json["album_last_release"]["id"],
                                 json=json["album_last_release"],
                                 session=self._session)]
            self.albums.append(
                [Album(a["id"], json=a, session=self._session) 
                 for a in json["albums_without_last_release"]["items"]]
            )
        elif not hasattr(self, "albums"):
            self.albums = None
        self.album_count = json["albums_count"]
        self.biography = json["biography"]["content"] \
                         if "biography" in json else None
        self.images = {s: json["image"][s] 
                       for s in {"small", "medium", "large"}} \
                      if json["image"] else None
        self.name = json["name"]
        if "playlists" in json:
            self.playlists = [Playlist(p["id"], json=p, session=self._session)
                              for p in json["playlists"]]
        elif not hasattr(self, "playlists"):
            self.playlists = None
        self.similar_artist_ids = json.get("similar_artist_ids", None)
        if "tracks" in json:
            self.tracks = [Track(t["id"], json=t, session=self._session)
                           for t in json["tracks"]["items"]]
        elif "tracks_appears_on" in json:
            self.tracks = [Track(t["id"], json=t, session=self._session)
                           for t in json["tracks_appears_on"]["items"]]
        elif not hasattr(self, "tracks"):
            self.tracks = None
    
    def refresh(self) -> None:

        """
        Refresh or update the artist's information.
        """

        self._set(self._session.get_artist(self.id))
    
    def get_albums(
            self, *, last_release: bool = False, limit: int = None, 
            offset: int = None) -> None:

        """
        Get albums by the artist.

        Parameters
        ----------
        last_release : `bool`, keyword-only, default: :code:`False`
            If :code:`True`, the first item in :code:`Artist.albums`
            will be guaranteed to be the latest release (even though
            generally this is the case anyway).
        
        limit : `int`, keyword-only, optional
            The maximum number of albums to return.

            **Default**: :code:`25`.

        offset : `int`, keyword-only, optional
            The index of the first album to return. Use with `limit` to 
            get the next page of albums.

            **Default**: :code:`0`.
        """

        if self.albums is not None:
            warnings.warn(f"Information for {len(self.albums)} album(s) "
                          "already exists and will be overwritten.")

        if last_release:
            self.albums = [
                Album(a["id"], json=a, session=self._session) 
                for a in self._session.get_artist(
                    self.id, extras="albums_with_last_release", limit=limit, 
                    offset=offset
                )["albums"]["items"]
            ]
        else:
            json = self._session.get_artist(self.id, extras="albums", 
                                            limit=limit, offset=offset)
            self.albums = [Album(json["album_last_release"]["id"],
                                 json=json["album_last_release"],
                                 session=self._session)]
            self.albums.append(
                [Album(a["id"], json=a, session=self._session) 
                 for a in json["albums_without_last_release"]["items"]]
            )
    
    def get_playlists(self, *, limit: int = None, offset: int = None) -> None:

        """
        Get playlists by the artist.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            The maximum number of playlists to return.

            **Default**: :code:`25`.

        offset : `int`, keyword-only, optional
            The index of the first playlist to return. Use with `limit` to 
            get the next page of playlists.

            **Default**: :code:`0`.
        """

        if self.playlists is not None:
            warnings.warn(f"Information for {len(self.playlists)} playlist(s) "
                          "already exists and will be overwritten.")

        self.playlists = [
            Playlist(a["id"], json=a, session=self._session) 
            for a in self._session.get_artist(
                self.id, extras="playlists", limit=limit, offset=offset
            )["playlists"]["items"]
        ]

    def get_tracks(
            self, *, appears_on: bool = False, limit: int = None, 
            offset: int = None) -> None:

        """
        Get tracks by the artist.

        Parameters
        ----------
        appears_on : `bool`, keyword-only, default: :code:`False`
            If :code:`True`, only tracks found in compilations or where
            another artist is featured are returned.

        limit : `int`, keyword-only, optional
            The maximum number of tracks to return.

            **Default**: :code:`25`.

        offset : `int`, keyword-only, optional
            The index of the first track to return. Use with `limit` to 
            get the next page of tracks.

            **Default**: :code:`0`.
        """

        if self.tracks is not None:
            warnings.warn(f"Information for {len(self.tracks)} track(s) "
                          "already exists and will be overwritten.")

        extras = "tracks"
        if appears_on:
            extras += "_appears_on"
        self.tracks = [
            Track(a["id"], json=a, session=self._session) 
            for a in self._session.get_artist(
                self.id, extras=extras, limit=limit, offset=offset
            )[extras]["items"]
        ]

    def favorite(self) -> None:

        """
        Favorite the artist.

        .. admonition:: User authentication

           Requires user authentication.
        """

        self._session.favorite_items(artist_ids=self.id)

    def unfavorite(self) -> None:

        """
        Unfavorite the artist.

        .. admonition:: User authentication

           Requires user authentication.
        """

        self._session.unfavorite_items(artist_ids=self.id)

class Label:

    """
    A Qobuz record label.

    .. attention::

       This class is pending removal.

    Parameters
    ----------
    label_id : `str`
        Qobuz record label ID.

    albums : `bool`, keyword-only, default: :code:`True`
        Specifies whether information on the albums released by the
        record label is returned.

    limit : `int`, keyword-only, optional
        The maximum number of albums to return. Has no effect if 
        :code:`albums=False`.

        **Default**: :code:`25`.

    offset : `int`, keyword-only, optional
        The index of the first album to return. Use with `limit` to
        get the next page of albums. Has no effect if 
        :code:`albums=False`.

        **Default**: :code:`0`.

    json : `dict`, keyword-only, optional
        Qobuz catalog information for the label 
        retrieved using :meth:`PrivateAPI.get_label`.

    session : `minim.qobuz.PrivateAPI`, keyword-only, optional
        Qobuz API session.

    **kwargs
        Keyword arguments to pass to the :class:`PrivateAPI` constructor
        if :code:`session=None`.

    Attributes
    ----------
    album_count : `int`
        Number of albums published by the record label.

    albums : `list`
        Albums published by the record label.

        .. note::
           If :code:`None`, use :meth:`get_albums` to get albums that
           published by the record label.

    name : `str`
        Name.
    """

    def __init__(
            self, label_id: str, *, albums: bool = False,
            limit: int = None, offset: int = None, json: dict[str, Any] = None,
            session: PrivateAPI = None, **kwargs):
        
        self._session = session if session else PrivateAPI(**kwargs)
        self.id = label_id
        self._json = self._session.get_label(self.id, albums=albums, 
                                             limit=limit, offset=offset) \
                     if json is None else json
        self._set(self._json)

    def __repr__(self) -> None:

        """
        Set the unique string representation of the Qobuz record label
        object.
        """

        return f"minim.qobuz.Label('{self.id}') # {self.__str__()}"

    def __str__(self) -> None:

        """
        Set the readable string representation of the Qobuz record label 
        object.
        """

        return f"Qobuz record label: {self.name}"

    def _set(self, json: dict[str, Any]) -> None:

        """
        Stores information from a JSON object into class variables.

        Parameters
        ----------
        json : `dict`, keyword-only, optional
            Qobuz catalog information for the label 
            retrieved using :meth:`PrivateAPI.get_label`.
        """

        if self._json is not json:
            self._json.update(json)

        self.album_count = json["albums_count"]
        if "albums" in json:
            self.albums = [Album(a["id"], json=a, session=self._session) 
                           for a in json["album"]["items"]]
        elif not hasattr(self, "albums"):
            self.albums = None
        self.name = json["name"]

    def refresh(self) -> None:

        """
        Refresh or update the record label's information.
        """

        self._set(self._session.get_label(self.id))

    def get_albums(self, *, limit: int = None, offset: int = None) -> None:

        """
        Get albums published by the record label.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            The maximum number of albums to return.

            **Default**: :code:`25`.

        offset : `int`, keyword-only, optional
            The index of the first album to return. Use with `limit` to
            get the next page of albums.

            **Default**: :code:`0`.
        """

        if self.albums is not None:
            warnings.warn(f"Information for {len(self.albums)} album(s) "
                          "already exists and will be overwritten.")

        self.albums = [
            Album(a["id"], json=a, session=self._session) 
            for a in self._session.get_label(
                self.id, albums=True, limit=limit, offset=offset
            )["albums"]["items"]
        ]

class Track:

    """
    A Qobuz track.

    .. attention::

       This class is pending removal.

    Parameters
    ----------
    track_id : `str`
        Qobuz track ID.

    json : `dict`, keyword-only, optional
        Qobuz catalog information for the track 
        retrieved using :meth:`PrivateAPI.get_track`.

    session : `minim.qobuz.PrivateAPI`, keyword-only, optional
        Qobuz API session.

    **kwargs
        Keyword arguments to pass to the :class:`PrivateAPI` constructor
        if :code:`session=None`.

    Attributes
    ----------
    album : `minim.qobuz.Album`
        Album.

    copyright : `str`
        Copyright information.

    credits : `dict`
        Credits.

        **Format**: :code:`{<role: str>: [<artist: str>, 
        <artist: str>, ...], ...}`.

    disc_number : `int`
        Disc number.

    duration : `int`
        Duration.

    file_url : `str`
        URL to the audio file. 
        
        .. note::
           Only available after running :meth:`get_file_url`.

    hi_res : `bool`
        Whether high-resolution audio is available.

    id : `int` or `str`
        Qobuz track ID.

    isrc : `str`
        International Standard Recording Code (ISRC).

    main_artist : `minim.qobuz.Artist`
        Primary artist.

    maximum_bit_depth : `int`
        Maximum number of bits per sample.

    maximum_channel_count : `int`
        Maximum number of audio channels.

    maximum_sample_rate : `int`
        Maximum sample rate in kHz.

    parental_warning : `bool`
        Whether the album contains explicit content.

    permissions : `dict`
        Access and availability.

        **Valid keys**: :code:`"displayable"`, :code:`"downloadable"`,
        :code:`"previewable"`, :code:`"purchasable"`, 
        :code:`"sampleable"`, and :code:`"streamable"`.

    playlist_track_id : `int`
        Playlist track ID.

    release_date : `datetime.datetime`
        Release date.

    replaygain : `dict`
        ReplayGain information.

        **Format**: :code:`{"gain": <replay_gain: float>, 
        "peak": <peak_loudness: float>}`.

    stream : `bytes`
        Audio stream data.

        .. note::
           Only available after running :meth:`get_stream`.

    title : `str`
        Title.

    track_number : `int`
        Track number.
    """

    _PERMISSIONS = {"purchasable", "streamable", "previewable", 
                    "sampleable", "downloadable", "displayable"}

    def __init__(
            self, track_id: str, *, json: dict[str, Any] = None, 
            session: PrivateAPI = None, **kwargs):
        
        self._session = session if session else PrivateAPI(**kwargs)
        self.id = track_id
        self._json = self._session.get_track(self.id) if json is None else json
        self._set(self._json)

    def __repr__(self) -> None:

        """
        Set the unique string representation of the Qobuz track
        object.
        """

        return f"minim.qobuz.Track('{self.id}') # {self.__str__()}"

    def __str__(self) -> None:

        """
        Set the readable string representation of the Qobuz track 
        object.
        """

        return (f"Qobuz track: '{self.title}' "
                f"[artist: {self.main_artist.name}, "
                f"album: {self.album.title}]")
    
    def _set(self, json: dict[str, Any]) -> None:

        """
        Stores information from a JSON object into class variables.

        Parameters
        ----------
        json : `dict`, keyword-only, optional
            Qobuz catalog information for the track 
            retrieved using :meth:`PrivateAPI.get_track`.
        """

        if self._json is not json:
            self._json.update(json)

        self.album = Album(json["album"]["id"], json=json["album"],
                           session=self._session)
        self.main_artist = Artist(
            json["performer"]["id"], 
            json=self._session.get_artist(json["performer"]["id"]), 
            session=self._session
        )
        self.copyright = json["copyright"]
        self.credits = self._session.get_track_credits(
            performers=json.get("performers")
        )
        self.disc_number = json.get("media_number")
        self.duration = datetime.timedelta(seconds=json["duration"])
        self.hi_res = json["hires"]
        self.isrc = json["isrc"]
        self.maximum_bit_depth = json["maximum_bit_depth"]
        self.maximum_channel_count = json["maximum_channel_count"]
        self.maximum_sample_rate = json["maximum_sampling_rate"]
        self.parental_warning = json["parental_warning"]
        self.permissions = {p: json[p] for p in self._PERMISSIONS}
        self.release_date = min(
            json.get(k) if k in json and json.get(k) else "?" for k in {
                "release_date_original", 
                "release_date_download", 
                "release_date_stream"
            }
        )
        self.release_date = None if self.release_date == "?" else \
                            datetime.datetime.strptime(self.release_date, 
                                                       "%Y-%m-%d")
        self.playlist_track_id = json.get("playlist_track_id")
        self.replaygain = {
            "gain": json["audio_info"]["replaygain_track_gain"],
            "peak": json["audio_info"]["replaygain_track_peak"]
        }
        self.title = json["title"].rstrip()
        if "featured_artist" in self.credits \
                and self.credits["featured_artist"] \
                and "feat." not in self.title:
            self.title += (" [feat. {}]" if "(" in self.title 
                           else " (feat. {})").format(
                utility.multivalue_formatter(self.credits["featured_artist"], 
                                             False)
            )
        if json["version"]:
            self.title += (" [{}]" if "(" in self.title 
                           else " ({})").format(json["version"])
        self.track_number = json.get("track_number")

    def refresh(self) -> None:

        """
        Refresh or update the track's information.
        """

        self._set(self._session.get_track(self.id))

    def get_file_url(self, quality: Union[int, str] = 27) -> None:

        """
        Get the file URL for a track.

        .. admonition:: User authentication

           Requires user authentication and an active Qobuz streaming 
           plan to access the URL for the full, high-quality audio track.

        Parameters
        ----------
        quality : `int` or `str`, default: :code:`27`
            Maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` or :code:`"MP3"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` or :code:`"HI-RES"` for up to 24-bit,
                 192 kHz Hi-Res FLAC.
        """

        self.file_url = self._session.get_track_file_url(
            self.id, quality
        )["url"]

    def get_stream(
            self, *, quality: Union[int, str] = 27,
            save: bool = False, path: str = None, folder: bool = False, 
            metadata: bool = True) -> None:
        
        """
        Get a track's audio stream data.

        .. admonition:: User authentication

           Requires user authentication and an active Qobuz streaming 
           plan for the full, high-quality audio stream.

        Parameters
        ----------
        quality : `str`, keyword-only, default: :code:`27`
            Maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` or :code:`"MP3"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` or :code:`"HI-RES"` for up to 24-bit,
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
        """

        self.stream = self._session.get_track_stream(self.id, quality=quality,
                                                     save=save, path=path, 
                                                     folder=folder, 
                                                     metadata=metadata)
    
    def favorite(self) -> None:

        """
        Favorite the track.

        .. admonition:: User authentication

           Requires user authentication.
        """

        self._session.favorite_items(track_ids=self.id)

    def unfavorite(self) -> None:

        """
        Unfavorite the track.

        .. admonition:: User authentication

           Requires user authentication.
        """

        self._session.unfavorite_items(track_ids=self.id)

class Playlist:

    """
    A Qobuz playlist.

    .. attention::

       This class is pending removal.

    Parameters
    ----------
    id_or_params : `int`, `str`, or `dict`
        Either a Qobuz playlist ID or parameters for a new playlist to
        pass to :meth:`PrivateAPI.create_playlist`.

    json : `dict`, keyword-only, optional
        Qobuz catalog information for the playlist 
        retrieved using :meth:`PrivateAPI.get_track`.

    session : `minim.qobuz.PrivateAPI`, keyword-only, optional
        Qobuz API session.

    **kwargs
        Keyword arguments to pass to the :class:`PrivateAPI` constructor
        if :code:`session=None`.

    Attributes
    ----------
    artists : `list`
        Featured artist(s).

    creation_date : `datetime.datetime`
        Creation date.

    description : `str`
        Description or review.

    duration : `datetime.timedelta`
        Total duration of all tracks.
    
    flags : `dict`
        Settings and visibility flags.

        **Valid keys**: :code:`"collaborative"`, :code:`"featured"`, and
        :code:`"public"`.

    genres : `list`
        Genre(s).

    images : `dict`
        URLs to images, such as a rectangular banner, and cover artwork
        to create a collage from.

        **Format**:

        .. code::

           {"banner": {"small": <url: str>, "large": <url: str>},
            "collage": {"small": <url: str>, "medium": <url: str>, 
                        "large": <url: str>}}

    name : `str`
        Name.

    owner : `dict`
        Owner.

        **Valid keys**: :code:`"id"` and :code:`"name"`.

    track_count : `int`
        Total number of tracks.

    tracks : `list`
        Tracks in the playlist.
    """

    def __init__(
            self, id_or_params: Union[int, str, dict[str, Any]], *, 
            json: dict[str, Any] = None, session: PrivateAPI = None, **kwargs):
        
        self._session = session if session else PrivateAPI(**kwargs)
        if isinstance(id_or_params, (int, str)):
            self.id = id_or_params
            self._json = self._session.get_playlist(self.id) \
                         if json is None else json
        elif isinstance(id_or_params, dict):
            self._json = self._session.create_playlist(**id_or_params)
            self.id = self._json["id"]
        else:
            emsg = ("Invalid first parameter, which must either be a "
                    "Qobuz playlist ID or a dictionary containing the "
                    "name, description, and visibility and "
                    "collaboration settings for a new playlist.")
            raise ValueError(emsg)
        self._set(self._json)

    def __repr__(self) -> None:

        """
        Set the unique string representation of the Qobuz playlist 
        object.
        """

        return f"minim.qobuz.Playlist('{self.id}') # {self.__str__()}"

    def __str__(self) -> None:

        """
        Set the readable string representation of the Qobuz playlist 
        object.
        """

        return (f"Qobuz playlist: '{self.name}' "
                f"[owner: {self.owner['name']}]")
        
    def _get_playlist_track_id(self, track: Track) -> int:

        """
        Get the playlist track ID of a track in the playlist.

        Parameters
        ----------
        track : `minim.qobuz.Track`
            Qobuz track object.

        Returns
        -------
        playlist_track_id : `int`
            Qobuz playlist track ID. Returns :code:`None` if the track 
            is not in the current playlist.
        """

        if track.playlist_track_id:
            return track.playlist_track_id
        
        for i, t in enumerate(self.tracks):
            if t.id == track.id:
                if t.playlist_track_id is None:
                    self.refresh()
                    return self.tracks[i].playlist_track_id
                else:
                    return t.playlist_track_id
            
        return None
    
    def _set(self, json: dict[str, Any]) -> None:

        """
        Stores information from a JSON object into class variables.

        Parameters
        ----------
        json : `dict`, keyword-only, optional
            Qobuz catalog information for the playlist 
            retrieved using :meth:`PrivateAPI.get_playlist`.
        """

        if self._json is not json:
            self._json.update(json)

        if "featured_artists" in json:
            self.artists = [Artist(a["id"], json=a, session=self._session) 
                            for a in json["featured_artists"]]
        elif not hasattr(self, "artists"):
            self.artists = None
        self.creation_date = datetime.datetime.utcfromtimestamp(
            json["created_at"]
        )
        self.description = json["description"]
        self.duration = datetime.timedelta(seconds=json["duration"])
        self.flags = {"collaborative": json["is_collaborative"],
                      "featured": json.get("is_featured", False),
                      "public": json["is_public"]}
        self.genres = [g["name"] for g in json["genres"]] \
                      if "genres" in json else None
        self.images = {"banner": {"small": None, "large": None},
                       "collage": {"small": None, "medium": None, 
                                   "large": None}}
        if "image_rectangle" in json and json["image_rectangle"]:
            self.images["banner"]["small"] = json["image_rectangle_mini"]
            self.images["banner"]["large"] = json["image_rectangle"]
        if "images" in json and json["images"]:
            self.images["collage"]["small"] = json["images"]
            self.images["collage"]["medium"] = json["images150"]
            self.images["collage"]["large"] = json["images300"]
        self.name = json["name"]
        self.owner = json["owner"]
        self.track_count = json["tracks_count"]
        if "tracks" in json:
            self.tracks = [Track(t["id"], json=t, session=self._session) 
                           for t in json["tracks"]["items"]]
        elif not hasattr(self, "tracks"):
            self.tracks = None

    def refresh(self) -> None:

        """
        Refresh or update the playlist's information.
        """

        self._set(self._session.get_playlist(self.id))

    def add_tracks(
            self, tracks: Union[int, str, Track, 
                                list[Union[int, str, Track]]], 
            *, duplicate: bool = False) -> None:
        
        """
        Add tracks to the playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        tracks : `int`, `str`, `qobuz.Track`, or `list`
            Qobuz track ID(s) or object(s).

        duplicate : `bool`, keyword-only, default: :code:`False`
            Determines whether duplicate tracks should be added to the
            playlist.
        """
        
        if isinstance(tracks, list):
            tracks = [t.id if isinstance(t, Track) else t for t in tracks]
        elif isinstance(tracks, Track):
            tracks = tracks.id
        self._session.add_playlist_tracks(self.id, tracks, duplicate=duplicate)
        self.refresh()

    def move_tracks(
            self, 
            playlist_tracks: Union[int, str, Track, 
                                   list[Union[int, str, Track]]],
            insert_before: int) -> None:
        
        """
        Move tracks in the playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist_tracks : `int`, `str`, `qobuz.Track`, or `list`
            Qobuz playlist track ID(s) or object(s).

            .. note::
               Playlist track IDs are not the same as track IDs.

            .. note::
               If `qobuz.Track` objects are passed in, they cannot have
               originated from another `qobuz.Playlist` object.

        insert_before : `int`
            Position to which to move the tracks specified in 
            `track_ids`.
        """

        if isinstance(playlist_tracks, Track):
            playlist_tracks = self._get_playlist_track_id(playlist_tracks)
            if playlist_tracks is None:
                emsg = (f"Track '{playlist_tracks.title}' not found in "
                        f"playlist '{self.name}'.")
                raise ValueError(emsg)
        elif isinstance(playlist_tracks, list):
            for i, t in enumerate(playlist_tracks):
                if isinstance(t, Track):
                    playlist_tracks[i] = self._get_playlist_track_id(t)
                    if playlist_tracks[i] is None:
                        emsg = (f"Track '{t.title}' not found in "
                                f"playlist '{self.name}'.")
                        raise ValueError(emsg)
        
        self._session.move_playlist_tracks(self.id, playlist_tracks, 
                                           insert_before)
        self.refresh()

    def delete_tracks(
            self, playlist_tracks: Union[int, str, Track, 
                                         list[Union[int, str, Track]]]
        ) -> None:

        """
        Delete tracks from the playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist_tracks : `int`, `str`, `qobuz.Track`, or `list`
            Qobuz playlist track ID(s) or object(s).

            .. note::
               Playlist track IDs are not the same as track IDs.

            .. note::
               If `qobuz.Track` objects are passed in, they cannot have
               originated from another `qobuz.Playlist` object.
        """

        if isinstance(playlist_tracks, Track):
            playlist_tracks = self._get_playlist_track_id(playlist_tracks)
            if playlist_tracks is None:
                emsg = f"Track '{playlist_tracks.title}' not found in playlist."
                raise ValueError(emsg)
        elif isinstance(playlist_tracks, list):
            for i, t in enumerate(playlist_tracks):
                if isinstance(t, Track):
                    playlist_tracks[i] = self._get_playlist_track_id(t)
                    if playlist_tracks[i] is None:
                        emsg = f"Track '{t.title}' not found in playlist."
                        raise ValueError(emsg)
        
        self._session.delete_playlist_tracks(self.id, playlist_tracks)
        self.refresh()

    def get_file_urls(self, quality: Union[int, str] = 27) -> None:

        """
        Get the file URLs for all tracks.

        .. admonition:: User authentication

           Requires user authentication and an active Qobuz streaming 
           plan to access the URL for the full, high-quality audio track.

        Parameters
        ----------
        quality : `int` or `str`, default: :code:`27`
            Maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` or :code:`"MP3"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` or :code:`"HI-RES"` for up to 24-bit,
                 192 kHz Hi-Res FLAC.
        """

        if not hasattr(self, "tracks") or self.tracks is None:
            self.refresh()

        for t in self.tracks:
            t.get_file_url(quality=quality)

    def get_streams(
            self, *, quality: Union[int, str] = 27, save: bool = False,
            path: str = None, folder: bool = False, metadata: bool = True
        ) -> None:

        """
        Get audio stream data for all tracks.

        .. admonition:: User authentication

           Requires user authentication and an active Qobuz streaming 
           plan for full, high-quality audio streams.

        Parameters
        ----------
        quality : `str`, keyword-only, default: :code:`27`
            Maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` or :code:`"MP3"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` or :code:`"HI-RES"` for up to 24-bit,
                 192 kHz Hi-Res FLAC.

        save : `bool`, keyword-only, default: :code:`False`
            Determines whether the streams are saved to audio files.

        path : `str`, keyword-only, optional
            If :code:`save=True`, path in which the audio files are 
            saved.

        folder : `bool`, keyword-only, default: :code:`False`
            Determines whether a folder in `path` (or in the current
            directory if `path` is not specified) is created to hold the
            audio files.

        metadata : `bool`, keyword-only, default: :code:`True`
            Determines whether the audio files' metadata is
            populated.
        """

        if not hasattr(self, "tracks") or self.tracks is None:
            self.refresh()

        for t in self.tracks:
            t.get_stream(quality=quality, save=save, path=path, folder=folder,
                         metadata=metadata)

    def favorite(self) -> None:

        """
        Favorite (or subscribe to) the playlist.

        .. admonition:: User authentication

           Requires user authentication.
        """

        self._session.favorite_playlist(self.id)

    def unfavorite(self) -> None:

        """
        Unfavorite (or unsubscribe from) the playlist.

        .. admonition:: User authentication

           Requires user authentication.
        """

        self._session.unfavorite_playlist(self.id)

    def update(
            self, *, name: str = None, description: str = None, 
            public: bool = None, collaborative: bool = None) -> None:

        """
        Update the title, description, and/or privacy of the playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        name : `str`, keyword-only, optional
            Qobuz playlist name.

        description : `str`, keyword-only, optional
            Brief playlist description.

        public : `bool`, keyword-only, optional
            Determines whether the playlist is public (:code:`True`) or
            private (:code:`False`).

        collaborative : `bool`, keyword-only, optional
            Determines whether the playlist is collaborative.
        """

        self._session.update_playlist(self.id, name=name, 
                                      description=description, 
                                      public=public, 
                                      collaborative=collaborative)
        self.refresh()

    def delete(self) -> None:

        """
        Delete the current playlist.

        .. admonition:: User authentication

           Requires user authentication.
        """

        self._session.delete_playlist(self.id)
        self.__dict__.clear()
        self.id = None
        self.name = "<deleted>"
        self.owner = {"name": None}

class User:

    """
    A Qobuz user.

    .. attention::

       This class is pending removal.

    Parameters
    ----------
    session : `minim.qobuz.PrivateAPI`, keyword-only, optional
        Qobuz API session.

    **kwargs
        Keyword arguments to pass to the :class:`PrivateAPI` constructor
        if :code:`session=None`.

    Attributes
    ----------
    age : `int`
        Age.

    avatar : `str`
        URL to the user's profile picture.

    country : `str`
        Country code.

    creation_date : `datetime.datetime`
        Creation date.

    display_name : `str`
        Display name.

    email : `str`
        Email address.

    favorites : `dict`
        Favorite albums, artists, and tracks.

        .. note::
           Only available after calling :meth:`get_user_favorites`.

        **Format**:

        .. code::

           {"albums": [<album: minim.qobuz.Album>, ...],
            "artists": [<artist: minim.qobuz.Artist>, ...],
            "tracks": [<track: minim.qobuz.Track>, ...]}

    gender : `str`
        Gender.
        
    id : `int` or `str`
        Qobuz user ID.

    language : `str`
        Language code.

    name : `str`
        First and last names.

    playlists : `list`
        Favorite or custom playlists.

        .. note::
           Only available after calling :meth:`get_user_playlists`.
        
    public_id : `str`
        Public Qobuz ID.

    purchases : `dict`
        Purchased albums and tracks.

        .. note::
           Only available after calling :meth:`get_user_purchases`.

        .. code::

           {"albums": [<album: minim.qobuz.Album>, ...],
            "tracks": [<track: minim.qobuz.Track>, ...]}

    store : `str`
        Country and language codes used for the Qobuz store.

    store_features : `dict`
        Qobuz store features.

        **Valid keys**: :code:`"download"`, :code:`"streaming"`, 
        :code:`"editorial"`, :code:`"club"`, :code:`"wallet"`,
        :code:`"weeklyq"`, :code:`"autoplay"`, 
        :code:`"inapp_purchase_subscripton"` (misspelling intentional),
        :code:`"opt_in"`, and :code:`"music_import"`.

    subscription : `dict`
        Qobuz subscription or streaming plan.

        **Format**:

        .. code::

           {'id': <int>, 
            'description': <str>, 
            'end_date': <datetime.datetime>, 
            'periodicity': <str>, 
            'permissions': {'lossy_streaming': <bool>,
                            'lossless_streaming': <bool>,
                            'hires_streaming': <bool>,
                            'hires_purchases_streaming': <bool>,
                            'mobile_streaming': <bool>,
                            'offline_streaming': <bool>,
                            'hfp_purchase': <bool>}, 
            'start_date': <datetime.datetime>}
        
    zone : `str`
        Geographical zone.
    """

    def __init__(self, session: PrivateAPI = None, **kwargs):
        
        self._session = session if session else PrivateAPI(**kwargs)
        self._json = self._session._me if self._session._me else {}
        self._set(self._json)

    def __repr__(self) -> None:

        """
        Set the unique string representation of the Qobuz user
        object.
        """

        return f"minim.qobuz.User() # {self.__str__()}"

    def __str__(self) -> None:

        """
        Set the readable string representation of the Qobuz user
        object.
        """

        if self._session._me:
            return (f"Qobuz user: {self.display_name} [ID: {self.id}, "
                    f"email: {self.email}, "
                    f"subscription: {self.subscription['description']}]")
        return "Qobuz user: not logged in"
    
    def _set(self, json: dict[str, Any]) -> None:

        """
        Stores information from a JSON object into class variables.

        Parameters
        ----------
        json : `dict`, keyword-only, optional
            Qobuz catalog information for the user
            retrieved using :meth:`PrivateAPI.get_me`.
        """

        if json:
            if self._json != json:
                self._json.update(json)

            self.age = json["age"]
            self.avatar = json["avatar"]
            self.country = json["country_code"]
            self.creation_date = datetime.datetime.strptime(
                json["creation_date"], "%Y-%m-%d"
            )
            self.display_name = json["display_name"]
            self.email = json["email"]
            self.gender = json["genre"]
            self.id = json["id"]
            self.language = json["language_code"]
            self.name = f"{json['firstname']} {json['lastname']}"
            self.public_id = json["publicId"]
            self.store = json["store"]
            self.store_features = json["store_features"]
            self.subscription = {
                "id": json["credential"]["id"],
                "description": json["credential"]["description"]
            }
            if self.subscription["id"]:
                self.subscription.update({
                    "end_date": datetime.datetime.strptime(
                        json["subscription"]["end_date"], "%Y-%m-%d"
                    ),
                    "periodicity": json["subscription"]["periodicity"],
                    "permissions": {
                        k: v for k, v in 
                        json["credential"]["parameters"].items() 
                        if isinstance(v, bool)
                    },
                    "start_date": datetime.datetime.strptime(
                        json["subscription"]["start_date"], "%Y-%m-%d"
                    ),
                })
            self.zone = json["zone"]

    def refresh(self) -> None:

        """
        Refresh or update the user's information.
        """

        self._set(self._session.get_me())

    ### ALBUMS ################################################################

    def get_album(self, album_id: str) -> Album:

        """
        Get Qobuz catalog information for an album.

        Parameters
        ----------
        album_id : `str`
            Qobuz album ID.

        Returns
        -------
        album : `minim.qobuz.album`
            Qobuz album object.
        """

        return Album(album_id, json=self._session.get_album(album_id), 
                     session=self._session)
    
    def get_featured_albums(
            self, type: str = "new-releases", *, limit: int = None,
            offset: int = None) -> list[Album]:

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

        limit : `int`, keyword-only, optional
            The maximum number of albums to return.

            **Default**: :code:`50`.

        offset : `int`, keyword-only, optional
            The index of the first album to return. Use with `limit` to
            get the next page of albums.

            **Default**: :code:`0`.

        Returns
        -------
        album : `list`
            Qobuz album objects.
        """

        return [Album(a["id"], json=a, session=self._session) 
                for a in self._session.get_featured_albums(
                    type, limit=limit, offset=offset
                )["albums"]["items"]]

    ### ARTISTS ###############################################################

    def get_artist(
            self, artist_id: Union[int, str], *, 
            extras: Union[str, list[str]] = None,
            limit: int = None, offset: int = None) -> Artist:

        """
        Get Qobuz catalog information for an artist.

        Parameters
        ----------
        artist_id : `int` or `str`
            Qobuz artist ID.

        extras : `str`, keyword-only, optional
            Specifies extra information about the artist to return.

            **Valid values**: :code:`"albums"`, :code:`"tracks"`,
            :code:`"playlists"`, :code:`"tracks_appears_on"`, and
            :code:`"albums_with_last_release"`.

        limit : `int`, keyword-only, optional
            The maximum number of albums or tracks to return. Has no 
            effect if :code:`extras=None`.

            **Default**: :code:`25`.

        offset : `int`, keyword-only, optional
            The index of the first album or track to return. Use with 
            `limit` to get the next page of albums or tracks. Has no 
            effect if :code:`extras=None`.

            **Default**: :code:`0`.

        Returns
        -------
        artist : `dict`
            Qobuz catalog information for the artist.
        """

        return Artist(
            artist_id, 
            json=self._session.get_artist(artist_id, extras=extras, 
                                          limit=limit, offset=offset), 
            session=self._session
        )
    
    ### RECORD LABELS #########################################################

    def get_label(
            self, label_id: Union[int, str], *, albums: bool = False,
            limit: int = None, offset: int = None) -> Label:

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

            **Default**: :code:`25`.

        offset : `int`, keyword-only, optional
            The index of the first album to return. Use with `limit` to
            get the next page of albums. Has no effect if 
            :code:`albums=False`.

            **Default**: :code:`0`.

        Returns
        -------
        label : `minim.qobuz.Label`
            Qobuz record label object.
        """

        return Label(
            label_id, 
            json=self._session.get_label(label_id, albums=albums, limit=limit, 
                                         offset=offset),
            session=self._session
        )

    ### PLAYLISTS #############################################################

    def get_playlist(
            self, playlist_id: Union[int, str], *, tracks: bool = True,
            limit: int = None, offset: int = None) -> Playlist:
        
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
        playlist : `minim.qobuz.Playlist`
            Qobuz playlist object.
        """

        return Playlist(
            playlist_id,
            json=self._session.get_playlist(playlist_id, tracks=tracks,
                                            limit=limit, offset=offset),
            session=self._session
        )
    
    def get_featured_playlists(
            self, type: str = "editor-picks", *, limit: int = None,
            offset: int = None) -> list[Playlist]:
        
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
        """

        return [Playlist(p["id"], json=p, session=self._session) 
                for p in self._session.get_featured_playlists(
                    type, limit=limit, offset=offset
                )["items"]]

    ### USER PLAYLISTS ########################################################

    def create_playlist(
            self, name: str, *, description: str = None, public: bool = True,
            collaborative: bool = False) -> Playlist:
        
        """
        Create a user playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        name : `str`
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
            Qobuz catalog information for the newly created playlist.
        """

        return Playlist({"name": name, "description": description,
                         "public": public, "collaborative": collaborative})
    
    def update_playlist(
            self, playlist: Union[int, str, Playlist], *, name: str = None,
            description: str = None, public: bool = None, 
            collaborative: bool = None) -> None:
        
        """
        Update the title, description, and/or privacy of a playlist 
        owned by the current user.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist : `int`, `str`, or `minim.qobuz.Playlist`
            Qobuz playlist ID or object.

        name : `str`, keyword-only, optional
            Qobuz playlist name.

        description : `str`, keyword-only, optional
            Brief playlist description.

        public : `bool`, keyword-only, optional
            Determines whether the playlist is public (:code:`True`) or
            private (:code:`False`).

        collaborative : `bool`, keyword-only, optional
            Determines whether the playlist is collaborative.
        """

        if isinstance(playlist, Playlist):
            playlist.update(name=name, description=description, public=public, 
                            collaborative=collaborative)
        else:
            self._session.update_playlist(playlist, name=name, 
                                          description=description, 
                                          public=public,
                                          collaborative=collaborative)

    def delete_playlist(self, playlist: Union[int, str, Playlist]) -> None:

        """
        Delete a user playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist : `int`, `str`, or `minim.qobuz.Playlist`
            Qobuz playlist ID or object.
        """

        if isinstance(playlist, Playlist):
            playlist.delete()
        else:
            self._session.delete_playlist(playlist)

    def update_playlist_position(
            self, from_playlist: Union[int, str, Playlist], 
            to_playlist: Union[int, str, Playlist]) -> None:
        
        """
        Organize a user's playlists.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        from_playlist : `int` or `str`
            Qobuz playlist ID or object to move.

        to_playlist : `int` or `str`
            Qobuz playlist ID or object to swap with that in 
            `from_playlist`.
        """

        if isinstance(from_playlist, Playlist):
            from_playlist = from_playlist.id
        if isinstance(to_playlist, Playlist):
            to_playlist = to_playlist.id

        self._session.update_playlist_position(from_playlist, to_playlist)

    def add_playlist_tracks(
            self, playlist: Union[int, str, Playlist], 
            tracks: Union[int, str, Track, list[Union[int, str, Playlist]]], 
            *, duplicate: bool = False) -> None:
        
        """
        Add tracks to a user playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist : `int`, `str`, or `minim.qobuz.Playlist`
            Qobuz playlist ID or object.

        tracks : `int`, `str`, `minim.qobuz.Track`, or `list`
            Qobuz track ID(s) or object(s).

        duplicate : `bool`, keyword-only, default: :code:`False`
            Determines whether duplicate tracks should be added to the
            playlist.
        """

        if isinstance(playlist, Playlist):
            playlist.add_tracks(tracks, duplicate=duplicate)
        else:
            if isinstance(tracks, Track):
                tracks = tracks.id
            elif isinstance(tracks, list):
                tracks = [t.id if isinstance(t, Track) else t for t in tracks]
            self._session.add_playlist_tracks(playlist, tracks, 
                                              duplicate=duplicate)
    
    def move_playlist_tracks(
            self, playlist: Union[int, str, Playlist], 
            playlist_tracks: Union[int, str, Track, list[Union[int, str, Track]]], 
            insert_before: int):

        """
        Move tracks in a user playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist : `int`, `str`, or `minim.qobuz.Playlist`
            Qobuz playlist ID or object.

        playlist_tracks : `int`, `str`, or `list`
            Qobuz playlist track ID(s).

            .. note::
               Playlist track IDs are not the same as track IDs.

        insert_before : `int`
            Position to which to move the tracks specified in 
            `track_ids`.
        """

        if isinstance(playlist, Playlist):
            playlist.move_tracks(playlist_tracks, insert_before)
        else:
            playlist = Playlist(playlist, session=self._session)
            if isinstance(playlist_tracks, Track):
                playlist_tracks = playlist._get_playlist_track_id(playlist_tracks)
                if playlist_tracks is None:
                    emsg = (f"Track '{playlist_tracks.title}' not found in "
                            f"playlist '{playlist.name}'.")
                    raise ValueError(emsg)
            elif isinstance(playlist_tracks, list):
                for i, t in enumerate(playlist_tracks):
                    if isinstance(t, Track):
                        playlist_tracks[i] = playlist._get_playlist_track_id(t)
                        if playlist_tracks[i] is None:
                            emsg = (f"Track '{t.title}' not found in "
                                    f"playlist '{playlist.name}'.")
                            raise ValueError(emsg)
            self._session.move_playlist_tracks(playlist, playlist_tracks, 
                                               insert_before)

    def delete_playlist_tracks(
            self, playlist: Union[int, str, Playlist], 
            playlist_tracks: Union[int, str, Track, list[Union[int, str, Track]]]
        ) -> None:

        """
        Delete tracks from a user playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist : `int`, `str`, or `minim.qobuz.Playlist`
            Qobuz playlist ID or object.

        playlist_tracks : `int`, `str`, or `list`
            Qobuz playlist track ID(s).

            .. note::
               Playlist track IDs are not the same as track IDs.
        """

        if isinstance(playlist, Playlist):
            playlist.delete_tracks(playlist_tracks)
        else:
            playlist = Playlist(playlist, session=self._session)
            if isinstance(playlist_tracks, Track):
                playlist_tracks = playlist._get_playlist_track_id(playlist_tracks)
                if playlist_tracks is None:
                    emsg = (f"Track '{playlist_tracks.title}' not found in "
                            f"playlist '{playlist.name}'.")
                    raise ValueError(emsg)
            elif isinstance(playlist_tracks, list):
                for i, t in enumerate(playlist_tracks):
                    if isinstance(t, Track):
                        playlist_tracks[i] = playlist._get_playlist_track_id(t)
                        if playlist_tracks[i] is None:
                            emsg = (f"Track '{t.title}' not found in "
                                    f"playlist '{playlist.name}'.")
                            raise ValueError(emsg)
            self._session.delete_playlist_tracks(playlist, playlist_tracks)
    
    def favorite_playlist(self, playlist: Union[int, str, Playlist]) -> None:

        """
        Favorite (or subscribe to) a playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist : `int`, `str`, or `minim.qobuz.Playlist`
            Qobuz playlist ID or object.
        """

        if isinstance(playlist, Playlist):
            playlist.favorite()
        else:
            self._session.favorite_playlist(playlist)

        self.get_user_playlists()

    def unfavorite_playlist(self, playlist: Union[int, str, Playlist]) -> None:

        """
        Unfavorite (or unsubscribe from) a playlist.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        playlist : `int`, `str`, or `minim.qobuz.Playlist`
            Qobuz playlist ID or object.
        """

        if isinstance(playlist, Playlist):
            playlist.unfavorite()
        else:
            self._session.unfavorite_playlist(playlist)
        
        self.get_user_playlists()

    ### TRACKS ################################################################

    def get_track(self, track_id: Union[int, str]) -> Track:

        """
        Get Qobuz catalog information for a track.

        Parameters
        ----------
        track_id : `int` or `str`
            Qobuz track ID.

        Returns
        -------
        track : `minim.qobuz.Track`
            Qobuz track object.
        """

        return Track(track_id, json=self._session.get_track(track_id), 
                     session=self._session)
        
    def get_track_file_url(
            self, track: Union[int, str, Track], quality: Union[int, str] = 27
        ) -> Union[None, str]:
        
        """
        Get the file URL for a track.

        .. admonition:: User authentication

           Requires user authentication and an active Qobuz streaming 
           plan to access the URL for the full, high-quality audio track.

        Parameters
        ----------
        track : `int`, `str`, `minim.qobuz.Track`
            Qobuz track ID or object.

        quality : `int` or `str`, default: :code:`27`
            Maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` or :code:`"MP3"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` or :code:`"HI-RES"` for up to 24-bit,
                 192 kHz Hi-Res FLAC.
                 
        Returns
        -------
        url : `str`
            URL to the audio file. If `track` is a :class:`Track` 
            object, the URL is stored in its `file_url` instance 
            variable instead.
        """

        if isinstance(track, Track):
            track.get_file_url(quality)
        else:
            return self._session.get_track_file_url(track, quality)["url"]

    def get_track_credits(
            self, track: Union[int, str, Track] = None, *, performers: str = None,
            roles: list = None) -> Union[None, dict[str, list]]:

        """
        Get credits for a track.
        
        .. note::
           This method is provided for convenience and is not a Qobuz 
           API endpoint.

        Parameters
        ----------
        track : `int`, `str`, or `minim.qobuz.Track`
            Qobuz track ID or object.

        performers : `str`, keyword-only, optional
            An unformatted string containing the track credits obtained
            from calling :meth:`PrivateAPI.get_track`.

        roles : `list`, keyword-only, optional
            Role filter. The special :code:`"Composers"` filter will 
            combine the :code:`"Composer"`, :code:`"ComposerLyricist"`,
            :code:`"Lyricist"`, and :code:`"Writer"` roles.

            .. note::
               `roles` is case-sensitive; all values must be in Pascal
               case.

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
            roles (in snake case) being the keys. If `track` is a 
            :class:`Track` object, the information is stored in its 
            `credits` instance variable instead.
        """
        
        if isinstance(track, Track):
            track.refresh()
        else:
            return self._session.get_track_credits(track, 
                                                   performers=performers,
                                                   roles=roles)

    def get_curated_tracks(
            self, *, limit: int = None, offset: int = None
        ) -> list[dict[str, Any]]:

        """
        Get weekly curated tracks for the user.

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
            Curated track objects.
        """

        return [Track(t["id"], json=t, session=self._session) 
                for t in self._session.get_curated_tracks(
                    limit=limit, offset=offset
                )["tracks"]["items"]]
    
    ### SEARCH ################################################################

    def search(
            self, query: str, type: str = None, *, hi_res: bool = False, 
            new_release: bool = False, strict: bool = False, limit: int = 10, 
            offset: int = 0) -> dict[str, Any]:
        
        """
        Search Qobuz for media and performers.

        Parameters
        ----------
        query : `str`
            Search query.

        type : `str`, keyword-only, optional
            Category to search in. If specified, only matching releases 
            and tracks will be returned.

            .. note::
               `type` is case-sensitive; all values must be in Pascal
               case.

            **Valid values**: :code:`"MainArtist"`, :code:`"Composer"`, 
            :code:`"Performer"`, :code:`"ReleaseName"`, and 
            :code:`"Label"`.

        hi_res : `bool`, keyword-only, :code:`False`
            High-resolution audio only.

        new_release : `bool`, keyword-only, :code:`False`
            New releases only.

        strict : `bool`, keyword-only, :code:`False`
            Enable exact word or phrase matching.

        limit : `int`, keyword-only, default: :code:`10`
            Maximum number of results to return.

        offset : `int`, keyword-only, default: :code:`0`
            Index of the first result to return. Use with `limit` to get
            the next page of search results.

        Returns
        -------
        results : `dict`
            The search results.

            **Format**:

            .. code::

               {"albums": [<album: qobuz.Album>, ...],
                "artists": [<artist: qobuz.Artist>], ...],
                "tracks": [<track: qobuz.Track>, ...],
                "most_popular": [...]}
        """

        TYPES_OBJECTS = {"albums": Album, "artists": Artist, 
                         "playlists": Playlist, "tracks": Track}

        _results = self._session.search(query, type, hi_res=hi_res, 
                                        new_release=new_release, strict=strict,
                                        limit=limit, offset=offset)
        results = {"query": _results["query"]}
        
        for type, obj in TYPES_OBJECTS.items():
            results[type] = [obj(i["id"], json=i, session=self._session) 
                             for i in _results[type]["items"]]
        
        if "most_popular" in _results:
            results["most_popular"] = [
                TYPES_OBJECTS[i["type"]](i["content"]["id"], json=i["content"],
                                        session=self._session) 
                for i in _results["most_popular"]["items"]
            ]
        
        return results

    ### STREAMS ###############################################################

    def get_track_stream(
            self, track: Union[int, str, Track], *, 
            quality: Union[int, str] = 27, save: bool = False, 
            path: str = None, folder: bool = False, metadata: bool = True
        ) -> Union[None, bytes]:
        
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
        track : `int`, `str`, or `minim.qobuz.Track`
            Qobuz track ID or object.

        quality : `str`, keyword-only, default: :code:`27`
            Maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` or :code:`"MP3"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` or :code:`"HI-RES"` for up to 24-bit,
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
        stream : `bytes` or `str`
            Audio stream data. If :code:`save=True`, the stream data is 
            saved to an audio file and its filename is returned instead.
            If `track` is a :class:`Track` object, the stream data is 
            stored in its `stream` instance variable instead.
        """

        if isinstance(track, Track):
            track.get_stream(quality=quality, save=save, path=path, 
                             folder=folder, metadata=metadata)
        return self._session.get_track_stream(track, quality=quality, 
                                              save=save, path=path, 
                                              folder=folder, metadata=metadata)

    def get_collection_streams(
            self, collection: Union[int, str, Album, Playlist], 
            type: str = None, *, quality: Union[int, str] = 27, 
            save: bool = False, path: str = None, folder: bool = False, 
            metadata: bool = True) -> Union[None, list[bytes]]:

        """
        Get audio stream data for all tracks in an album or a playlist.

        .. admonition:: User authentication

           Requires user authentication and an active Qobuz streaming 
           plan for full, high-quality audio streams.

        .. note::
           This method is provided for convenience and is not a Qobuz 
           API endpoint.

        Parameters
        ----------
        collection : `int`, `str`, `minim.qobuz.Album`, or \
        `minim.qobuz.Playlist`
            Qobuz collection ID or object.

        type : `str`, optional
            Qobuz collection type. Required if `collection` is not a 
            Qobuz album or playlist object.

            **Valid values**: :code:`"album"` and :code:`"playlist"`.

        quality : `str`, keyword-only, default: :code:`27`
            Maximum audio quality.

            .. container::

               **Valid values**:

               * :code:`5` or :code:`"MP3"` for constant bitrate 
                 (320 kbps) MP3.
               * :code:`6` or :code:`"CD"` for CD-quality 
                 (16-bit, 44.1 kHz) FLAC.
               * :code:`7` for up to 24-bit, 96 kHz Hi-Res FLAC.
               * :code:`27` or :code:`"HI-RES"` for up to 24-bit,
                 192 kHz Hi-Res FLAC.

        save : `bool`, keyword-only, default: :code:`False`
            Determines whether the streams are saved to audio files.

        path : `str`, keyword-only, optional
            If :code:`save=True`, path in which the audio files are 
            saved.

        folder : `bool`, keyword-only, default: :code:`False`
            Determines whether a folder in `path` (or in the current
            directory if `path` is not specified) is created to hold the
            audio files.

        metadata : `bool`, keyword-only, default: :code:`True`
            Determines whether the audio files' metadata is
            populated.

        Returns
        -------
        streams : `list`
            Audio stream data. If :code:`save=True`, the streams are
            saved to audio files and their filenames are returned 
            instead. If `collection` is an :class:`Album` or 
            :class:`Playlist` object, the stream data is 
            stored in its underlying :class:`Track` objects' `stream` 
            instance variables instead.
        """

        if isinstance(collection, (Album, Playlist)):
            collection.get_streams(quality=quality, save=save,
                                   path=path, folder=folder, 
                                   metadata=metadata)
        elif type is None:
            raise ValueError("Collection type not specified.")
        return self._session.get_collection_streams(collection, type, 
                                                    quality=quality, save=save,
                                                    path=path, folder=folder,
                                                    metadata=metadata)

    ### USER ##################################################################

    def login(
            self, email: str = None, password: str = None, *,
            auth_token: str = None) -> None:
        
        """
        Log into Qobuz or switch accounts.

        Parameters
        ----------
        email : `str`, optional
            Account email address. If it is not stored as 
            :code:`QOBUZ_EMAIL` in the operating system's environment
            variables, it can be provided here.

        password : `str`, optional
            Account password. If it is not stored as 
            :code:`QOBUZ_PASSWORD` in the operating system's environment
            variables, it can be provided here.

        auth_token : `str`, keyword-only, optional
            User authentication token. If it is not stored as 
            :code:`QOBUZ_USER_AUTH_TOKEN` in the operating system's 
            environment variables, it can be provided here.
        """

        self._session.login(email, password, auth_token=auth_token)
        self.refresh()

    def get_user_favorites(self, type: str = None) -> None:

        """
        Get the user's favorite albums, artists, and tracks.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        type : `str`
            Media type to return. If not specified, all of the user's
            favorite items are returned.

            .. container::
            
               **Valid values**: :code:`"albums"`, :code:`"artists"`, 
               and :code:`"tracks"`.
        """

        TYPES_OBJECTS = {"albums": Album, "artists": Artist, "tracks": Track}
        types = [type] if type else TYPES_OBJECTS.keys()

        if not hasattr(self, "favorites"):
            self.favorites = dict()

        for t in types:
            self.favorites[t] = [
                TYPES_OBJECTS[t](i["id"], json=i, session=self._session) 
                for i in self._session.get_user_favorites(t)[t]["items"]
            ]
    
    def get_user_playlists(
            self, *, limit: int = None, offset: int = None) -> None:
        
        """
        Get the user's custom and favorite playlists.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        limit : `int`, keyword-only, optional
            The maximum number of playlists to return.

            **Default**: :code:`500`.

        offset : `int`, keyword-only, optional
            The index of the first playlist to return. Use with `limit`
            to get the next page of playlists.

            **Default**: :code:`0`.
        """

        self.playlists = [
            Playlist(p["id"], json=p, session=self._session) for p in 
            self._session.get_user_playlists(limit=limit, offset=offset)["items"]
        ]
    
    def get_user_purchases(
            self, type: str = None, *, limit: int = None, 
            offset: int = None) -> list[Union[Album, Track]]:

        """
        Get the user's purchases.

        .. admonition:: User authentication

           Requires user authentication.

        Parameters
        ----------
        type : `str`, default: :code:`"albums"`
            Item type.

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
        purchases : `list`
            The user's purchases.
        """

        TYPES_OBJECTS = {"albums": Album, "tracks": Track}
        types = [type] if type else TYPES_OBJECTS.keys()

        if not hasattr(self, "purchases"):
            self.purchases = dict()

        for t in types:
            self.purchases[t] = [
                TYPES_OBJECTS[t](i["id"], json=i, session=self._session)
                for i in self._session.get_user_purchases(
                    t, limit=limit, offset=offset
                )[t]["items"]
            ]
    
    def favorite_items(
            self, *, 
            albums: Union[str, Album, list[Union[str, Album]]] = None,
            artists: Union[int, str, Artist, list[Union[int, str, Artist]]] = None,
            tracks: Union[int, str, Track, list[Union[int, str, Track]]] = None
        ) -> None:

        """
        Favorite albums, artists, and/or tracks.

        .. admonition:: User authentication

           Requires user authentication.

        .. note::
           For playlists, see :meth:`favorite_playlist`.

        Parameters
        ----------
        albums : `str`, `minim.qobuz.Album`, or `list`, \
        keyword-only, optional
            Qobuz album ID(s) or object(s).

        artists : `int`, `str`, `minim.qobuz.Artist`, or `list`, \
        keyword-only, optional
            Qobuz artist ID(s) or object(s).

        tracks : `int`, `str`, `minim.qobuz.Track`, or `list`, \
        keyword-only, optional
            Qobuz track ID(s) or object(s).
        """

        for obj, param, items in zip((Album, Artist, Track), 
                                     ("album_ids", "artist_ids", "track_ids"), 
                                     (albums, artists, tracks)):
            if items:
                if not isinstance(items, list):
                    items = [items]
                for i in reversed(items):
                    if isinstance(i, obj):
                        i.favorite()
                        items.remove(i)
                self._session.favorite_items(**{param: items})
        self.get_user_favorites()

    def unfavorite_items(
            self, *, 
            albums: Union[str, Album, list[Union[str, Album]]] = None,
            artists: Union[int, str, Artist, list[Union[int, str, Artist]]] = None,
            tracks: Union[int, str, Track, list[Union[int, str, Track]]] = None
        ) -> None:

        """
        Unfavorite albums, artists, and/or tracks. 

        .. admonition:: User authentication

           Requires user authentication.

        .. note::
           For playlists, see :meth:`unfavorite_playlist`.

        Parameters
        ----------
        albums : `str`, `minim.qobuz.Album`, or `list`, \
        keyword-only, optional
            Qobuz album ID(s) or object(s).

        artists : `int`, `str`, `minim.qobuz.Artist`, or `list`, \
        keyword-only, optional
            Qobuz artist ID(s) or object(s).

        tracks : `int`, `str`, `minim.qobuz.Track`, or `list`, \
        keyword-only, optional
            Qobuz track ID(s) or object(s).
        """

        for obj, param, items in zip((Album, Artist, Track), 
                                     ("album_ids", "artist_ids", "track_ids"), 
                                     (albums, artists, tracks)):
            if items:
                if not isinstance(items, list):
                    items = [items]
                for i in reversed(items):
                    if isinstance(i, obj):
                        i.unfavorite()
                        items.remove(i)
                self._session.unfavorite_items(**{param: items})
        self.get_user_favorites()