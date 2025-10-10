from collections.abc import Collection
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPIPlayerEndpoints:
    """
    Spotify Web API player endpoints.

    .. important::

       This class is managed by :class:`minim.api.spotify.WebAPI` and
       should not be instantiated directly.
    """

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

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-modify-playback-state` scope
                 Control playback on your Spotify clients and Spotify
                 Connect devices. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /reference/transfer-a-users-playback>`__

        .. important::

           This endpoint requires Spotify Premium.

        .. warning::

           The order of execution is not guaranteed when this endpoint
           is used with other Spotify Web API player endpoints.

        Parameters
        ----------
        device_id : str, positional-only
            Playback device ID.

        play : bool, keyword-only, optional
            Whether to start playback on the new device.

            .. container::

               * :code:`True` – Ensure playback starts.
               * :code:`False` – Maintain the current playback state.
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
        device_id: str,
        /,
        context_uri: str | None = None,
        track_uris: str | Collection[str] | None = None,
        offset: dict[str, int | str] | None = None,
    ) -> None:
        pass

    def pause_playback(self, device_id: str, /) -> None:
        pass

    def skip_next(self, device_id: str, /) -> None:
        pass

    def skip_previous(self, device_id: str, /) -> None:
        pass

    def seek(self, position_ms: int, *, device_id: str | None = None) -> None:
        pass

    def set_repeat(
        self, state: str, /, *, device_id: str | None = None
    ) -> None:
        pass

    def set_volume(
        self, volume_percent: int, /, *, device_id: str | None = None
    ) -> None:
        pass

    def set_shuffle(
        self, state: bool, /, *, device_id: str | None = None
    ) -> None:
        pass

    def get_recently_played(
        self,
        *,
        limit: int | None = None,
        after: int | None = None,
        before: int | None = None,
    ) -> dict[str, Any]:
        pass

    def get_queue(self) -> dict[str, Any]:
        pass

    def add_to_queue(
        self, uri: str, /, *, device_id: str | None = None
    ) -> None:
        pass
