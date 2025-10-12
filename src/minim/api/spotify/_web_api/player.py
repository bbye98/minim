from collections.abc import Collection
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class PlayerAPI:
    """
    Player API endpoints for the Spotify Web API.

    .. important::

       This class is managed by :class:`minim.api.spotify.WebAPI` and
       should not be instantiated directly.
    """

    _PLAYBACK_STATES = {"track", "context", "off"}

    def __init__(self, client: "WebAPI", /) -> None:
        """
        Parameters
        ----------
        client : minim.api.spotify.WebAPI
            Minim's Spotify Web API client.
        """
        self._client = client

    def get_playback_state(
        self, *, additional_types: str | None = None, market: str | None = None
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
        additional_types : str or Collection[str], keyword-only, optional
            Item types supported by the API client, provided as either a
            comma-separated string or a collection of strings.

            .. note::

               This parameter was introduced to allow existing clients
               to maintain their current behavior and might be
               deprecated in the future.

            **Default**: :code:`"track"`.

            **Valid values**: :code:`"track"`, :code:`"episode"`.

        market : str, keyword-only, optional
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
            "get_playback_state", "user-read-playback-state"
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

        .. warning::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints for the Spotify Web API.

        Parameters
        ----------
        device_id : str, positional-only
            Playback device ID.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.

        play : bool, keyword-only, optional
            Whether to start playback on the new device. If
            :code:`True`, playback begins immediately. If :code:`False`,
            the current playback state is preserved.
        """
        self._client._require_scopes(
            "transfer_playback", "user-modify-playback-state"
        )
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
        return self._client._request("GET", "me/player/devices").json()

    def get_currently_playing(
        self, *, additional_types: str | None = None, market: str | None = None
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
        additional_types : str or Collection[str], keyword-only, optional
            Item types supported by the API client, provided as either a
            comma-separated string or a collection of strings.

            .. note::

               This parameter was introduced to allow existing clients
               to maintain their current behavior and might be
               deprecated in the future.

            **Default**: :code:`"track"`.

            **Valid values**: :code:`"track"`, :code:`"episode"`.

        market : str, keyword-only, optional
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
            "get_currently_playing", "user-read-currently-playing"
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
        offset: dict[str, int | str] | None = None,
        uris: str | Collection[str] | None = None,
    ) -> None:
        """
        `Player > Start/Resume Playback <https://developer.spotify.com
        /documentation/web-api/reference/start-a-users-playback>`_:
        Start or resume playback.

        Parameters
        ----------
        device_id : str, keyword-only, optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.

        context_uri : str, keyword-only, optional


        offset : dict[str, int | str], keyword-only, optional


        uris : str or Collection[str], keyword-only, optional
        """

    def pause_playback(self, *, device_id: str | None = None) -> None:
        """
        `Player > Pause Playback <https://developer.spotify.com
        /documentation/web-api/reference/pause-a-users-playback>`_:
        Pause playback.

        .. admonition:: Authorization scope and subscription
           :class: authorization-scope

           .. tab:: Required

              Spotify Premium subscription
                 Access the :code:`/me/player` endpoint.
                 `Learn more. <https://www.spotify.com/us/premium/>`__

              :code:`user-modify-playback-state` scopel
                 Control playback on your Spotify clients and Spotify
                 Connect devices. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /reference/transfer-a-users-playback>`__

        .. warning::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints for the Spotify Web API.

        Parameters
        ----------
        device_id : str, keyword-only, optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes(
            "pause_playback", "user-modify-playback-state"
        )
        params = {}
        if device_id is not None:
            self._client._validate_spotify_id(device_id)
            params["device_id"] = device_id
        self._client._request("PUT", "me/player/pause", params=params)

    def skip_next(self, *, device_id: str | None = None) -> None:
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

        .. warning::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints for the Spotify Web API.

        Parameters
        ----------
        device_id : str, keyword-only, optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes("skip_next", "user-modify-playback-state")
        params = {}
        if device_id is not None:
            self._client._validate_spotify_id(device_id)
            params["device_id"] = device_id
        self._client._request("POST", "me/player/next", params=params)

    def skip_previous(self, *, device_id: str | None = None) -> None:
        """
        `Player > Skip To Next <https://developer.spotify.com
        /documentation/web-api/reference
        /skip-users-playback-to-next-track>`_: Skip to the previous item
        in the queue.

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

        .. warning::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints for the Spotify Web API.

        Parameters
        ----------
        device_id : str, keyword-only, optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes(
            "skip_previous", "user-modify-playback-state"
        )
        params = {}
        if device_id is not None:
            self._client._validate_spotify_id(device_id)
            params["device_id"] = device_id
        self._client._request("POST", "me/player/next", params=params)

    def seek(
        self, position_ms: int, /, *, device_id: str | None = None
    ) -> None:
        """
        `Player > Seek To Position <https://developer.spotify.com
        /documentation/web-api/reference
        /seek-to-position-in-currently-playing-track>`_: Seek to a
        specific position in the currently playing track.

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

        .. warning::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints for the Spotify Web API.

        Parameters
        ----------
        position_ms : int, positional-only
            Position (in milliseconds) to seek to. If a position greater
            than the length of the track is specified, the player will
            start playing the next song.

            **Minimum value**: :code:`0`.

            **Example**: :code:`25_000`.

        device_id : str, keyword-only, optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes("seek", "user-modify-playback-state")
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

        .. warning::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints for the Spotify Web API.

        Parameters
        ----------
        state : str, positional-only
            Playback repeat mode.

            **Valid values**:

            .. container::

               * :code:`"track"` – Repeat the current track.
               * :code:`"context"` – Repeat the current context (album,
                 artist, or playlist).
               * :code:`"off"` – Turn repeat off.

        device_id : str, keyword-only, optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes("set_repeat", "user-modify-playback-state")
        if state not in self._PLAYBACK_STATES:
            _states = "', '".join(self._PLAYBACK_STATES)
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

        .. warning::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints for the Spotify Web API.

        Parameters
        ----------
        volume_percent : int, positional-only
            Playback volume as a percentage.

            **Valid range**: :code:`0` to :code:`100`.

        device_id : str, keyword-only, optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes("set_volume", "user-modify-playback-state")
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

        .. warning::

           The order of execution is not guaranteed when this endpoint
           is used with other Player API endpoints for the Spotify Web API.

        Parameters
        ----------
        state : bool, positional-only
            Whether to shuffle playback.

        device_id : str, keyword-only, optional
            Playback device ID. If not specified, the currently active
            device is the target.

            **Example**:
            :code:`"0d1841b0976bae2a3a310dd74c0f3df354899bc8"`.
        """
        self._client._require_scopes(
            "set_shuffle", "user-modify-playback-state"
        )
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
        tracks recently played by the current user.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-read-recently-played` scope
                 Access your recently played items. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#user-read-recently-played>`__

        Parameters
        ----------
        after : int, keyword-only, optional


        before : int, keyword-only, optional


        limit : int, keyword-only, optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.
        """

    def get_queue(self) -> dict[str, Any]:
        pass

    def add_to_queue(
        self, uri: str, /, *, device_id: str | None = None
    ) -> None:
        pass
