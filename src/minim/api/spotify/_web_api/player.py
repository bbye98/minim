from typing import TYPE_CHECKING, Any

from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from .. import SpotifyWebAPI


class PlayerAPI(ResourceAPI):
    """
    Player API endpoints for the Spotify Web API.

    .. important::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPI`
       and should not be instantiated directly.
    """

    _CONTEXT_TYPES = {"album", "artist", "playlist"}
    _PLAYBACK_STATES = {"track", "context", "off"}
    _client: "SpotifyWebAPI"

    def get_playback_state(
        self,
        *,
        additional_types: str | list[str] | None = None,
        market: str | None = None,
    ) -> dict[str, Any]:
        """
        `Player > Get Playback State <https://developer.spotify.com
        /documentation/web-api/reference
        /get-information-about-the-users-current-playback>`_: Get the
        current playback state.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-read-playback-state` scope
                 Read your currently playing content and Spotify Connect
                 devices. `Learn more. <https://developer.spotify.com
                 /documentation/web-api/reference
                 /get-information-about-the-users-current-playback>`__

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        additional_types : str or list[str]; keyword-only; optional
            Item types supported by the API client, provided as either a
            comma-separated string or a list of strings.

            .. note::

               This parameter was introduced to allow existing clients
               to maintain their current behavior and might be
               deprecated in the future.

            **Default**: :code:`"track"`.

            **Valid values**: :code:`"track"`, :code:`"episode"`.

        market : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If specified, only content
            available in that market is returned. When a valid user
            access token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither the market nor the user's country are
               provided, the content is considered unavailable for the
               client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        state : dict[str, Any]
            Playback state and Spotify content metadata for the
            currently playing item.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "actions": {
                      "interrupting_playback": <bool>,
                      "pausing": <bool>,
                      "resuming": <bool>,
                      "seeking": <bool>,
                      "skipping_next": <bool>,
                      "skipping_prev": <bool>,
                      "toggling_repeat_context": <bool>,
                      "toggling_repeat_track": <bool>,
                      "toggling_shuffle": <bool>,
                      "transferring_playback": <bool>
                    },
                    "context": {
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "type": <str>,
                      "uri": <str>
                    },
                    "currently_playing_type": <str>,
                    "device": {
                      "id": <str>,
                      "is_active": <bool>,
                      "is_private_session": <bool>,
                      "is_restricted": <bool>,
                      "name": <str>,
                      "supports_volume": <bool>,
                      "type": <str>,
                      "volume_percent": <int>
                    },
                    "is_playing": <bool>,
                    "item": {
                      "album": {
                        "album_type": <str>,
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
                        "available_markets": <list[str]>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "height": <int>,
                            "url": <str>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "release_date": <str>,
                        "release_date_precision": <str>,
                        "restrictions": {
                          "reason": <str>
                        },
                        "total_tracks": <int>,
                        "type": "album",
                        "uri": <str>
                      },
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
                      "available_markets": <list[str]>,
                      "disc_number": <int>,
                      "duration_ms": <int>,
                      "explicit": <bool>,
                      "external_ids": {
                        "ean": <str>,
                        "isrc": <str>,
                        "upc": <str>
                      },
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "is_local": <bool>,
                      "is_playable": <bool>,
                      "linked_from": {
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "type": "track",
                        "uri": <str>
                      },
                      "name": <str>,
                      "popularity": <int>,
                      "preview_url": <str>,
                      "restrictions": {
                        "reason": <str>
                      },
                      "track_number": <int>,
                      "type": "track",
                      "uri": <str>
                    },
                    "progress_ms": <int>,
                    "repeat_state": <str>,
                    "shuffle_state": <bool>,
                    "timestamp": <int>
                  }
        """
        self._client._require_scopes(
            "player.get_playback_state", "user-read-playback-state"
        )
        params = {}
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if additional_types is not None:
            params["additional_types"] = self._client._prepare_audio_types(
                additional_types
            )
        return self._client._request("GET", "me/player", params=params).json()

    def transfer_playback(
        self, device_id: str, /, *, play: bool | None = None
    ) -> None:
        """
        `Player > Transfer Playback <https://developer.spotify.com
        /documentation/web-api/reference/transfer-a-users-playback>`_:
        Transfer playback to a new device.

        .. admonition:: Authorization scope and subscription
           :class: authorization-scope

           .. tab:: Required

              Spotify Premium subscription
                 Access the :code:`/me/player` endpoint.
                 `Learn more. <https://www.spotify.com/us/premium/>`__

              :code:`user-modify-playback-state` scope
                 Control playback on your Spotify clients and Spotify
                 Connect devices. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /reference/transfer-a-users-playback>`__

        .. caution::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints in the Spotify Web API.

        Parameters
        ----------
        device_id : str; positional-only
            Playback device ID.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.

        play : bool; keyword-only; optional
            Whether to start playback on the new device. If
            :code:`True`, playback begins immediately. If :code:`False`,
            the current playback state is preserved.
        """
        self._client._require_scopes(
            "player.transfer_playback", "user-modify-playback-state"
        )
        self._client._require_spotify_premium("player.transfer_playback")
        self._client._validate_spotify_id(device_id)
        payload = {"device_id": device_id}
        if play is not None:
            self._client._validate_type("play", play, bool)
            payload["play"] = play
        self._client._request("PUT", "me/player", json=payload)

    def get_devices(
        self,
    ) -> dict[str, list[dict[str, bool | int | str]]]:
        """
        `Player > Get Available Devices <https://developer.spotify.com
        /documentation/web-api/reference
        /get-a-users-available-devices>`_: Get available Spotify Connect
        devices.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-read-playback-state` scope
                 Read your currently playing content and Spotify Connect
                 devices. `Learn more. <https://developer.spotify.com
                 /documentation/web-api/reference
                 /get-information-about-the-users-current-playback>`__

        Returns
        -------
        devices : dict[str, list[dict[str, bool | int | str]]]
            Metadata of the available Spotify Connect devices.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "devices": [
                      {
                        "id": <str>,
                        "is_active": <bool>,
                        "is_private_session": <bool>,
                        "is_restricted": <bool>,
                        "name": <str>,
                        "type": <str>,
                        "supports_volume": <bool>,
                        "volume_percent": <int>
                      }
                    ]
                  }
        """
        self._client._require_scopes(
            "player.get_devices", "user-read-playback-state"
        )
        return self._client._request("GET", "me/player/devices").json()

    def get_currently_playing(
        self,
        *,
        additional_types: str | list[str] | None = None,
        market: str | None = None,
    ) -> dict[str, Any]:
        """
        `Player > Get Currently Playing Track
        <https://developer.spotify.com/documentation/web-api/reference
        /get-the-users-currently-playing-track>`_: Get playback state
        and Spotify catalog information for the currently playing item.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-read-currently-playing` scope
                  Read your currently playing content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /reference/get-the-users-currently-playing-track>`__

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        additional_types : str or list[str]; keyword-only; optional
            Item types supported by the API client, provided as either a
            comma-separated string or a list of strings.

            .. note::

               This parameter was introduced to allow existing clients
               to maintain their current behavior and might be
               deprecated in the future.

            **Default**: :code:`"track"`.

            **Valid values**: :code:`"track"`, :code:`"episode"`.

        market : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If specified, only content
            available in that market is returned. When a valid user
            access token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither the market nor the user's country are
               provided, the content is considered unavailable for the
               client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        item : dict[str, Any]
            Playback state and Spotify content metadata for the
            currently playing item.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "actions": {
                      "interrupting_playback": <bool>,
                      "pausing": <bool>,
                      "resuming": <bool>,
                      "seeking": <bool>,
                      "skipping_next": <bool>,
                      "skipping_prev": <bool>,
                      "toggling_repeat_context": <bool>,
                      "toggling_repeat_track": <bool>,
                      "toggling_shuffle": <bool>,
                      "transferring_playback": <bool>
                    },
                    "context": {
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "type": <str>,
                      "uri": <str>
                    },
                    "currently_playing_type": <str>,
                    "device": {
                      "id": <str>,
                      "is_active": <bool>,
                      "is_private_session": <bool>,
                      "is_restricted": <bool>,
                      "name": <str>,
                      "supports_volume": <bool>,
                      "type": <str>,
                      "volume_percent": <int>
                    },
                    "is_playing": <bool>,
                    "item": {
                      "album": {
                        "album_type": <str>,
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
                        "available_markets": <list[str]>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "height": <int>,
                            "url": <str>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "release_date": <str>,
                        "release_date_precision": <str>,
                        "restrictions": {
                          "reason": <str>
                        },
                        "total_tracks": <int>,
                        "type": "album",
                        "uri": <str>
                      },
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
                      "available_markets": <list[str]>,
                      "disc_number": <int>,
                      "duration_ms": <int>,
                      "explicit": <bool>,
                      "external_ids": {
                        "ean": <str>,
                        "isrc": <str>,
                        "upc": <str>
                      },
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "is_local": <bool>,
                      "is_playable": <bool>,
                      "linked_from": {
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "type": "track",
                        "uri": <str>
                      },
                      "name": <str>,
                      "popularity": <int>,
                      "preview_url": <str>,
                      "restrictions": {
                        "reason": <str>
                      },
                      "track_number": <int>,
                      "type": "track",
                      "uri": <str>
                    },
                    "progress_ms": <int>,
                    "repeat_state": <str>,
                    "shuffle_state": <bool>,
                    "timestamp": <int>
                  }
        """
        self._client._require_scopes(
            "player.get_currently_playing", "user-read-currently-playing"
        )
        params = {}
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if additional_types is not None:
            params["additional_types"] = self._client._prepare_audio_types(
                additional_types
            )
        return self._client._request(
            "GET", "me/player/currently-playing", params=params
        ).json()

    def start_playback(
        self,
        *,
        device_id: str | None = None,
        context_uri: str | None = None,
        offset: int | str | None = None,
        uris: str | list[str] | None = None,
        position_ms: int | None = None,
    ) -> None:
        """
        `Player > Start/Resume Playback <https://developer.spotify.com
        /documentation/web-api/reference/start-a-users-playback>`_:
        Start or resume playback.

        .. admonition:: Authorization scope and subscription
           :class: authorization-scope

           .. tab:: Required

              Spotify Premium subscription
                 Access the :code:`/me/player/play` endpoint.
                 `Learn more. <https://www.spotify.com/us/premium/>`__

              :code:`user-modify-playback-state` scope
                 Control playback on your Spotify clients and Spotify
                 Connect devices. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /reference/transfer-a-users-playback>`__

        Parameters
        ----------
        device_id : str; keyword-only; optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.

        context_uri : str; keyword-only; optional
            Spotify URI of the album, artist, or playlist to play.

            .. note::

               Only one of `context_uri` or `uris` can be specified.

            **Example**: :code:`"spotify:album:1Je1IMUlBXcx1Fz0WE7oPT"`.

        offset : int or str; keyword-only; optional
            Zero-based index or Spotify URI of the item within the
            context specified by `context_uri` at which to start
            playback. Used only when `context_uri` is specified.

            **Examples**:

            .. container::

               * :code:`5` – Sixth item in the context.
               * :code:`spotify:track:1301WleyT98MSxVHPZCA6M` – Specific
                 item in the context.

        uris : str or list[str]; keyword-only; optional
            Spotify URIs of items to play, provided as either a
            comma-separated string or a list of strings.

            .. note::

               Only one of `context_uri` or `uris` can be specified.

            **Examples**:

            .. container::

               * :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7Rh"`
               * :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M"`
               * :code:`["spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
                 "spotify:track:1301WleyT98MSxVHPZCA6M"]`

        position_ms : int; keyword-only; optional
            Position in milliseconds within the first item at which to
            start playback. If a position greater than the length of
            that item is specified, the player will start playing the
            next item.

            **Minimum value**: :code:`0`.

            **Example**: :code:`25_000`.
        """
        self._client._require_scopes(
            "player.start_playback", "user-modify-playback-state"
        )
        self._client._require_spotify_premium("player.start_playback")
        params = {}
        if device_id is not None:
            self._client._validate_spotify_id(device_id)
            params["device_id"] = device_id
        payload = {}
        if context_uri is not None:
            if uris is not None:
                raise ValueError(
                    "Only one of `context_uri` or `uris` can be provided."
                )
            self._client._validate_spotify_uri(
                context_uri, item_types=self._CONTEXT_TYPES
            )
            payload["context_uri"] = context_uri
            if offset is not None:
                if isinstance(offset, int):
                    self._client._validate_number("offset", offset, int, 0)
                    payload["offset"] = {"position": offset}
                elif isinstance(offset, str):
                    self._client._validate_spotify_uri(
                        offset, item_types={"track"}
                    )
                    payload["offset"] = {"uri": offset}
                else:
                    raise ValueError(
                        "`offset` must be either a zero-based index "
                        "(int) or a Spotify track URI (str)."
                    )
        elif uris is not None:
            _item_types = {"track"}
            for uri in uris:
                self._client._validate_spotify_uri(uri, item_types=_item_types)
            payload["uris"] = list(uris)
        if position_ms is not None:
            self._client._validate_number("position_ms", position_ms, int, 0)
            payload["position_ms"] = position_ms
        self._client._request(
            "PUT", "me/player/play", params=params, json=payload
        )

    def pause_playback(self, *, device_id: str | None = None) -> None:
        """
        `Player > Pause Playback <https://developer.spotify.com
        /documentation/web-api/reference/pause-a-users-playback>`_:
        Pause playback.

        .. admonition:: Authorization scope and subscription
           :class: authorization-scope

           .. tab:: Required

              Spotify Premium subscription
                 Access the :code:`/me/player/pause` endpoint.
                 `Learn more. <https://www.spotify.com/us/premium/>`__

              :code:`user-modify-playback-state` scope
                 Control playback on your Spotify clients and Spotify
                 Connect devices. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /reference/transfer-a-users-playback>`__

        .. caution::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints in the Spotify Web API.

        Parameters
        ----------
        device_id : str; keyword-only; optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes(
            "player.pause_playback", "user-modify-playback-state"
        )
        self._client._require_spotify_premium("player.pause_playback")
        params = {}
        if device_id is not None:
            self._client._validate_spotify_id(device_id)
            params["device_id"] = device_id
        self._client._request("PUT", "me/player/pause", params=params)

    def skip_to_next(self, *, device_id: str | None = None) -> None:
        """
        `Player > Skip To Next <https://developer.spotify.com
        /documentation/web-api/reference
        /skip-users-playback-to-next-track>`_: Skip to the next item in
        the queue.

        .. admonition:: Authorization scope and subscription
           :class: authorization-scope

           .. tab:: Required

              Spotify Premium subscription
                 Access the :code:`/me/player/next` endpoint.
                 `Learn more. <https://www.spotify.com/us/premium/>`__

              :code:`user-modify-playback-state` scope
                 Control playback on your Spotify clients and Spotify
                 Connect devices. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /reference/transfer-a-users-playback>`__

        .. caution::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints in the Spotify Web API.

        Parameters
        ----------
        device_id : str; keyword-only; optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes(
            "player.skip_to_next", "user-modify-playback-state"
        )
        self._client._require_spotify_premium("player.skip_to_next")
        params = {}
        if device_id is not None:
            self._client._validate_spotify_id(device_id)
            params["device_id"] = device_id
        self._client._request("POST", "me/player/next", params=params)

    def skip_to_previous(self, *, device_id: str | None = None) -> None:
        """
        `Player > Skip To Previous <https://developer.spotify.com
        /documentation/web-api/reference
        /skip-users-playback-to-previous-track>`_: Skip to the previous
        item in the queue.

        .. admonition:: Authorization scope and subscription
           :class: authorization-scope

           .. tab:: Required

              Spotify Premium subscription
                 Access the :code:`/me/player/previous` endpoint.
                 `Learn more. <https://www.spotify.com/us/premium/>`__

              :code:`user-modify-playback-state` scope
                 Control playback on your Spotify clients and Spotify
                 Connect devices. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /reference/transfer-a-users-playback>`__

        .. caution::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints in the Spotify Web API.

        Parameters
        ----------
        device_id : str; keyword-only; optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes(
            "player.skip_to_previous", "user-modify-playback-state"
        )
        self._client._require_spotify_premium("player.skip_to_previous")
        params = {}
        if device_id is not None:
            self._client._validate_spotify_id(device_id)
            params["device_id"] = device_id
        self._client._request("POST", "me/player/next", params=params)

    def seek_to_position(
        self, position_ms: int, /, *, device_id: str | None = None
    ) -> None:
        """
        `Player > Seek To Position <https://developer.spotify.com
        /documentation/web-api/reference
        /seek-to-position-in-currently-playing-track>`_: Seek to a
        specific position in the currently playing item.

        .. admonition:: Authorization scope and subscription
           :class: authorization-scope

           .. tab:: Required

              Spotify Premium subscription
                 Access the :code:`/me/player/seek` endpoint.
                 `Learn more. <https://www.spotify.com/us/premium/>`__

              :code:`user-modify-playback-state` scope
                 Control playback on your Spotify clients and Spotify
                 Connect devices. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /reference/transfer-a-users-playback>`__

        .. caution::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints in the Spotify Web API.

        Parameters
        ----------
        position_ms : int; positional-only
            Position in milliseconds to seek to. If a position greater
            than the length of the item is specified, the player will
            start playing the next item.

            **Minimum value**: :code:`0`.

            **Example**: :code:`25_000`.

        device_id : str; keyword-only; optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes(
            "player.seek_to_position", "user-modify-playback-state"
        )
        self._client._require_spotify_premium("player.seek_to_position")
        self._client._validate_number("position_ms", position_ms, int, 0)
        params = {"position_ms": position_ms}
        if device_id is not None:
            self._client._validate_spotify_id(device_id)
            params["device_id"] = device_id
        self._client._request("PUT", "me/player/seek", params=params)

    def set_repeat(
        self, state: str, /, *, device_id: str | None = None
    ) -> None:
        """
        `Player > Set Repeat Mode <https://developer.spotify.com
        /documentation/web-api/reference
        /set-repeat-mode-on-users-playback>`_: Set playback repeat mode.

        .. admonition:: Authorization scope and subscription
           :class: authorization-scope

           .. tab:: Required

              Spotify Premium subscription
                 Access the :code:`/me/player/repeat` endpoint.
                 `Learn more. <https://www.spotify.com/us/premium/>`__

              :code:`user-modify-playback-state` scope
                 Control playback on your Spotify clients and Spotify
                 Connect devices. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /reference/transfer-a-users-playback>`__

        .. caution::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints in the Spotify Web API.

        Parameters
        ----------
        state : str; positional-only
            Playback repeat mode.

            **Valid values**:

            .. container::

               * :code:`"track"` – Repeat the current track.
               * :code:`"context"` – Repeat the current album, artist,
                 or playlist.
               * :code:`"off"` – Turn repeat off.

        device_id : str; keyword-only; optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes(
            "player.set_repeat", "user-modify-playback-state"
        )
        self._client._require_spotify_premium("player.set_repeat")
        if state not in self._PLAYBACK_STATES:
            _states = "', '".join(sorted(self._PLAYBACK_STATES))
            raise ValueError(
                f"Invalid playback state {state!r}. Valid values: '{_states}'."
            )
        params = {"state": state}
        if device_id is not None:
            self._client._validate_spotify_id(device_id)
            params["device_id"] = device_id
        self._client._request("PUT", "me/player/repeat", params=params)

    def set_volume(
        self, volume_percent: int, /, *, device_id: str | None = None
    ) -> None:
        """
        `Player > Set Playback Volume <https://developer.spotify.com
        /documentation/web-api/reference
        /set-volume-for-users-playback>`_: Set playback volume.

        .. admonition:: Authorization scope and subscription
           :class: authorization-scope

           .. tab:: Required

              Spotify Premium subscription
                 Access the :code:`/me/player/volume` endpoint.
                 `Learn more. <https://www.spotify.com/us/premium/>`__

              :code:`user-modify-playback-state` scope
                 Control playback on your Spotify clients and Spotify
                 Connect devices. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /reference/transfer-a-users-playback>`__

        .. caution::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints in the Spotify Web API.

        Parameters
        ----------
        volume_percent : int; positional-only
            Playback volume as a percentage.

            **Valid range**: :code:`0` to :code:`100`.

        device_id : str; keyword-only; optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes(
            "player.set_volume", "user-modify-playback-state"
        )
        self._client._require_spotify_premium("player.set_volume")
        self._client._validate_number(
            "volume_percent", volume_percent, int, 0, 100
        )
        params = {"volume_percent": volume_percent}
        if device_id is not None:
            self._client._validate_spotify_id(device_id)
            params["device_id"] = device_id
        self._client._request("PUT", "me/player/volume", params=params)

    def set_shuffle(
        self, state: bool, /, *, device_id: str | None = None
    ) -> None:
        """
        `Player > Toggle Playback Shuffle <https://developer.spotify.com
        /documentation/web-api/reference
        /toggle-shuffle-for-users-playback>`_: Set playback shuffle state.

        .. admonition:: Authorization scope and subscription
           :class: authorization-scope

           .. tab:: Required

              Spotify Premium subscription
                 Access the :code:`/me/player/shuffle` endpoint.
                 `Learn more. <https://www.spotify.com/us/premium/>`__

              :code:`user-modify-playback-state` scope
                 Control playback on your Spotify clients and Spotify
                 Connect devices. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /reference/transfer-a-users-playback>`__

        .. caution::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints in the Spotify Web API.

        Parameters
        ----------
        state : bool; positional-only
            Whether to shuffle playback.

        device_id : str; keyword-only; optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes(
            "player.set_shuffle", "user-modify-playback-state"
        )
        self._client._require_spotify_premium("player.set_shuffle")
        self._client._validate_type("state", state, bool)
        params = {"state": state}
        if device_id is not None:
            self._client._validate_spotify_id(device_id)
            params["device_id"] = device_id
        self._client._request("PUT", "me/player/shuffle", params=params)

    def get_recently_played(
        self,
        *,
        after: int | None = None,
        before: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        `Player > Get Recently Played Tracks
        <https://developer.spotify.com/documentation/web-api/reference
        /get-recently-played>`_: Get Spotify catalog information for
        items recently played by the current user.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-read-recently-played` scope
                 Access your recently played items. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-read-recently-played>`__

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        after : int; keyword-only; optional
            Only return items played after the time indicated by this
            Unix timestamp in milliseconds.

            .. note::

               Only one of `after` or `before` can be specified.

            **Minimum value**: :code:`0`.

        before : int; keyword-only; optional
            Only return items played before the time indicated by this
            Unix timestamp in milliseconds.

            .. note::

               Only one of `after` or `before` can be specified.

            **Minimum value**: :code:`0`.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        Returns
        -------
        items : dict[str, Any]
            Pages of Spotify content metadata for the recently played items.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "cursors": {
                      "after": <str>,
                      "before": <str>
                    },
                    "href": <str>,
                    "items": [
                      {
                        "context": {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "type": <str>,
                          "uri": <str>
                        },
                        "played_at": <str>,
                        "track": {
                          "album": {
                            "album_type": <str>,
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
                            "available_markets": <list[str]>,
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "images": [
                              {
                                "height": <int>,
                                "url": <str>,
                                "width": <int>
                              }
                            ],
                            "name": <str>,
                            "release_date": <str>,
                            "release_date_precision": <str>,
                            "restrictions": {
                              "reason": <str>
                            },
                            "total_tracks": <int>,
                            "type": "album",
                            "uri": <str>
                          },
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
                          "available_markets": <list[str]>,
                          "disc_number": <int>,
                          "duration_ms": <int>,
                          "explicit": <bool>,
                          "external_ids": {
                            "ean": <str>,
                            "isrc": <str>,
                            "upc": <str>
                          },
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "is_local": <bool>,
                          "is_playable": <bool>,
                          "linked_from": {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "type": "track",
                            "uri": <str>
                          },
                          "name": <str>,
                          "popularity": <int>,
                          "preview_url": <str>,
                          "restrictions": {
                            "reason": <str>
                          },
                          "track_number": <int>,
                          "type": "track",
                          "uri": <str>
                        }
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "total": <int>
                  }
        """
        self._client._require_scopes(
            "player.get_recently_played", "user-read-recently-played"
        )
        self._client._request("GET", "me/player/recently-played")
        params = {}
        if after is not None:
            if before is not None:
                raise ValueError(
                    "Only one of `after` or `before` can be provided."
                )
            self._client._validate_number("after", after, int, 0)
            params["after"] = after
        elif before is not None:
            self._client._validate_number("before", before, int, 0)
            params["before"] = before
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        return self._client._request(
            "GET", "me/player/recently-played", params=params
        ).json()

    def get_queue(self) -> dict[str, Any]:
        """
        `Player > Get the User's Queue <https://developer.spotify.com
        /documentation/web-api/reference/get-queue>`_: Get the currently
        playing item and queued items.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-read-currently-playing` scope
                  Read your currently playing content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /reference/get-the-users-currently-playing-track>`__

              :code:`user-read-playback-state` scope
                 Read your currently playing content and Spotify Connect
                 devices. `Learn more. <https://developer.spotify.com
                 /documentation/web-api/reference
                 /get-information-about-the-users-current-playback>`__

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Returns
        -------
        queue : dict[str, Any]
            Spotify content metadata for the currently playing item and
            queued items.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "currently_playing": {
                      "album": {
                        "album_type": <str>,
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
                        "available_markets": <list[str]>,
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "images": [
                          {
                            "height": <int>,
                            "url": <str>,
                            "width": <int>
                          }
                        ],
                        "name": <str>,
                        "release_date": <str>,
                        "release_date_precision": <str>,
                        "restrictions": {
                          "reason": <str>
                        },
                        "total_tracks": <int>,
                        "type": "album",
                        "uri": <str>
                      },
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
                      "available_markets": <list[str]>,
                      "disc_number": <int>,
                      "duration_ms": <int>,
                      "explicit": <bool>,
                      "external_ids": {
                        "ean": <str>,
                        "isrc": <str>,
                        "upc": <str>
                      },
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "is_local": <bool>,
                      "is_playable": <bool>,
                      "linked_from": {
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "type": "track",
                        "uri": <str>
                      },
                      "name": <str>,
                      "popularity": <int>,
                      "preview_url": <str>,
                      "restrictions": {
                        "reason": <str>
                      },
                      "track_number": <int>,
                      "type": "track",
                      "uri": <str>
                    },
                    "queue": [
                      {
                        "album": {
                          "album_type": <str>,
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
                          "available_markets": <list[str]>,
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "images": [
                            {
                              "height": <int>,
                              "url": <str>,
                              "width": <int>
                            }
                          ],
                          "name": <str>,
                          "release_date": <str>,
                          "release_date_precision": <str>,
                          "restrictions": {
                            "reason": <str>
                          },
                          "total_tracks": <int>,
                          "type": "album",
                          "uri": <str>
                        },
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
                        "available_markets": <list[str]>,
                        "disc_number": <int>,
                        "duration_ms": <int>,
                        "explicit": <bool>,
                        "external_ids": {
                          "ean": <str>,
                          "isrc": <str>,
                          "upc": <str>
                        },
                        "external_urls": {
                          "spotify": <str>
                        },
                        "href": <str>,
                        "id": <str>,
                        "is_local": <bool>,
                        "is_playable": <bool>,
                        "linked_from": {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "type": "track",
                          "uri": <str>
                        },
                        "name": <str>,
                        "popularity": <int>,
                        "preview_url": <str>,
                        "restrictions": {
                          "reason": <str>
                        },
                        "track_number": <int>,
                        "type": "track",
                        "uri": <str>
                      }
                    ]
                  }
        """
        self._client._require_scopes(
            "player.get_queue",
            {"user-read-currently-playing", "user-read-playback-state"},
        )
        return self._client._request("GET", "me/player/queue").json()

    def add_to_queue(
        self, uri: str, /, *, device_id: str | None = None
    ) -> None:
        """
        `Player > Add Item to Playback Queue
        <https://developer.spotify.com/documentation/web-api/reference
        /add-to-queue>`_: Add items to the playback queue.

        .. admonition:: Authorization scope and subscription
           :class: authorization-scope

           .. tab:: Required

              Spotify Premium subscription
                 Access the :code:`/me/player/queue` endpoint.
                 `Learn more. <https://www.spotify.com/us/premium/>`__

              :code:`user-modify-playback-state` scope
                 Control playback on your Spotify clients and Spotify
                 Connect devices. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /reference/transfer-a-users-playback>`__

        Parameters
        ----------
        uri : str; positional-only
            Spotify URI of the track or episode to add to the queue.

            **Example**: :code:`spotif:track:4iV5W9uYEdYUVa79Axb7Rh`.

        device_id : str; keyword-only; optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes(
            "player.add_to_queue", "user-modify-playback-state"
        )
        self._client._require_spotify_premium("player.add_to_queue")
        self._client._validate_spotify_uri(
            uri, item_types=self._client._AUDIO_TYPES
        )
        params = {"uri": uri}
        if device_id is not None:
            self._client._validate_spotify_id(device_id)
            params["device_id"] = device_id
        self._client._request("POST", "me/player/queue", params=params)
