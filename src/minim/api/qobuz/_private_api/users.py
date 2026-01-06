from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .._core import PrivateQobuzAPI


class PrivateUsersAPI(ResourceAPI):
    """
    Users API endpoints for the private Qobuz API.

    .. important::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    _client: "PrivateQobuzAPI"

    @TTLCache.cached_method(ttl="user")
    def get_my_profile(self) -> dict[str, Any]:
        """
        Get detailed profile information for the current user.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access private profile information.

        Returns
        -------
        profile : dict[str, Any]
            Current user's profile information.

            .. admonition:: Sample responses
               :class: dropdown

               .. code::

                  {
                    "age": <int>,
                    "avatar": <str>,
                    "birthdate": <str>,
                    "country": <str>,
                    "country_code": <str>,
                    "creation_date": <str>,
                    "credential": {
                      "description": <str>,
                      "id": <int>,
                      "label": <str>,
                      "parameters": {
                        "color_scheme": {
                          "logo": <str>
                        },
                        "hfp_purchase": <bool>,
                        "hires_purchases_streaming": <bool>,
                        "hires_streaming": <bool>,
                        "included_format_group_ids": <list[int]>,
                        "label": <str>,
                        "lossless_streaming": <bool>,
                        "lossy_streaming": <bool>,
                        "mobile_streaming": <bool>,
                        "offline_streaming": <bool>,
                        "short_label": <str>,
                        "source": <str>
                      }
                    },
                    "display_name": <str>,
                    "email": <str>,
                    "firstname": <str>,
                    "genre": <str>,
                    "id": <int>,
                    "language_code": <str>,
                    "last_update": {
                      "favorite": <int>,
                      "favorite_album": <int>,
                      "favorite_artist": <int>,
                      "favorite_award": <int>,
                      "favorite_label": <int>,
                      "favorite_track": <int>,
                      "playlist": <int>,
                      "purchase": <int>
                    },
                    "lastname": <str>,
                    "login": <str>,
                    "publicId": <str>,
                    "store": <str>,
                    "store_features": {
                      "autoplay": <bool>,
                      "club": <bool>,
                      "download": <bool>,
                      "editorial": <bool>,
                      "inapp_purchase_subscripton": <bool>,
                      "music_import": <bool>,
                      "opt_in": <bool>,
                      "pre_register_opt_in": <bool>,
                      "pre_register_zipcode": <bool>,
                      "radio": <bool>,
                      "stream_purchase": <bool>,
                      "streaming": <bool>,
                      "wallet": <bool>,
                      "weeklyq": <bool>
                    },
                    "subscription": {
                      "end_date": <str>,
                      "household_size_max": <int>,
                      "is_canceled": <bool>,
                      "offer": <str>,
                      "periodicity": <str>,
                      "start_date": <str>
                    },
                    "zipcode": <str>,
                    "zone": <str>
                  }
        """
        self._client._require_authentication("users.get_my_profile")
        return self._client._request("GET", "user/get").json()

    @TTLCache.cached_method(ttl="user")
    def get_my_last_updates(self) -> dict[str, dict[str, int]]:
        """
        Get the current user's last update timestamps for favorites,
        playlists, and purchases.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access private profile information.

        Returns
        -------
        last_updates : dict[str, dict[str, int]]
            Current user's last update timestamps.

            .. admonition:: Sample responses
               :class: dropdown

               .. code::

                  {
                    "last_update":{
                      "favorite": <int>,
                      "favorite_album": <int>,
                      "favorite_artist": <int>,
                      "favorite_track": <int>,
                      "playlist": <int>,
                      "purchase": <int>
                    }
                  }

        """
        self._client._require_authentication("users.get_last_update")
        return self._client._request("GET", "user/lastUpdate").json()

    @TTLCache.cached_method(ttl="static")
    def login(
        self,
        username: str,
        password: str,
        /,
        *,
        device_uuid: str | None = None,
        device_model: str | None = None,
        device_os: str | None = None,
        device_platform: str | None = None,
    ) -> dict[str, Any]:
        """
        Perform a credential-based login.

        Parameters
        ----------
        username : str; positional-only
            Email or username.

        password : str; positional-only
            Password or its MD5 hash.

        device_uuid : str; keyword-only; optional
            UUID of the device running the client. If provided, the
            response will contain the Qobuz ID of the device to report
            streaming.

            **Example**: :code:`"16922031-0352-59D3-ADA2-B8E48236E8F0"`.

        device_model : str; keyword-only; optional
            Device model.

            **Example**: :code:`"Mac17,2"`.

        device_os : str; keyword-only; optional
            Device operating system.

            **Example**: :code:`"macOS 26.0"`.

        device_platform : str; keyword-only; optional
            Device platform.

            **Example**: :code:`"macOS-26.0-arm64"`.

        Returns
        -------
        token : dict[str, Any]
            User authentication token and profile information.

            .. admonition:: Sample responses
               :class: dropdown

               .. code::

                  {
                    "user": {
                      "age": <int>,
                      "avatar": <str>,
                      "birthdate": <str>,
                      "country": <str>,
                      "country_code": <str>,
                      "creation_date": <str>,
                      "credential": {
                        "description": <str>,
                        "id": <int>,
                        "label": <str>,
                        "parameters": {
                          "color_scheme": {
                            "logo": <str>
                          },
                          "hfp_purchase": <bool>,
                          "hires_purchases_streaming": <bool>,
                          "hires_streaming": <bool>,
                          "included_format_group_ids": <list[int]>,
                          "label": <str>,
                          "lossless_streaming": <bool>,
                          "lossy_streaming": <bool>,
                          "mobile_streaming": <bool>,
                          "offline_streaming": <bool>,
                          "short_label": <str>,
                          "source": <str>
                        }
                      },
                      "device": {
                        "device_manufacturer_id": <str>,
                        "device_model": <str>,
                        "device_os_version": <str>,
                        "device_platform": <str>,
                        "id": <int>
                      },
                      "display_name": <str>,
                      "email": <str>,
                      "firstname": <str>,
                      "genre": <str>,
                      "id": <int>,
                      "language_code": <str>,
                      "last_update": {
                        "favorite": <int>,
                        "favorite_album": <int>,
                        "favorite_artist": <int>,
                        "favorite_award": <int>,
                        "favorite_label": <int>,
                        "favorite_track": <int>,
                        "playlist": <int>,
                        "purchase": <int>
                      },
                      "lastname": <str>,
                      "login": <str>,
                      "publicId": <str>,
                      "store": <str>,
                      "store_features": {
                        "autoplay": <bool>,
                        "club": <bool>,
                        "download": <bool>,
                        "editorial": <bool>,
                        "inapp_purchase_subscripton": <bool>,
                        "music_import": <bool>,
                        "opt_in": <bool>,
                        "pre_register_opt_in": <bool>,
                        "pre_register_zipcode": <bool>,
                        "radio": <bool>,
                        "stream_purchase": <bool>,
                        "streaming": <bool>,
                        "wallet": <bool>,
                        "weeklyq": <bool>
                      },
                      "subscription": {
                        "end_date": <str>,
                        "household_size_max": <int>,
                        "is_canceled": <bool>,
                        "offer": <str>,
                        "periodicity": <str>,
                        "start_date": <str>
                      },
                      "zipcode": <str>,
                      "zone": <str>
                    },
                    "user_auth_token": <str>
                  }
        """
        self._client._validate_type("username", username, str)
        self._client._validate_type("password", password, str)
        params = {"username": username, "password": password}
        if device_uuid is not None:
            self._client._validate_uuid(device_uuid)
            params["device_manufacturer_id"] = device_uuid
        if device_model is not None:
            self._client._validate_type("device_model", device_model, str)
            params["device_model"] = device_model
        if device_os is not None:
            self._client._validate_type("device_os", device_os, str)
            params["device_os_version"] = device_os
        if device_platform is not None:
            self._client._validate_type(
                "device_platform", device_platform, str
            )
            params["device_platform"] = device_platform
        return self._client._request(
            "POST", "user/login", params=params
        ).json()

    @TTLCache.cached_method(ttl="daily")
    def get_personalized_playlists(self) -> list[dict[str, Any]]:
        """
        Get Qobuz catalog information for personally curated playlists.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Returns
        -------
        playlists : list[dict[str, Any]]
            Qobuz content metadata for the personally curated playlists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [
                    {
                      "baseline": <str>,
                      "description": <str>,
                      "graphics": {
                        "background": <str>,
                        "foreground": <str>
                      },
                      "images": {
                        "large": <str>,
                        "small": <str>
                      },
                      "step_pagination": <int>,
                      "title": <str>,
                      "type": <str>
                    }
                  ]
        """
        self._client._require_authentication("users.get_recommendations")
        return self._client._request("GET", "dynamic-tracks/list").json()

    @TTLCache.cached_method(ttl="daily")
    def get_personalized_playlist_tracks(
        self,
        playlist_type: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for tracks in a personally curated
        playlist.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        playlist_type : str; positional-only
            Type of the personally curated playlist.

            .. seealso::

               :meth:`get_personalized_playlists` – Get types of
               personally curated playlists.

            **Example**: :code:`"weekly"`.

        limit : int; keyword-only; optional
            Maximum number of items to return. Only applicable when
            `playlist_type` is not :code:`"weekly"`.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next batch of items. Only applicable when
            `playlist_type` is not :code:`"weekly"`.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of Qobuz content metadata for tracks in the personally
            curated playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "baseline": <str>,
                    "description": <str>,
                    "duration": <int>,
                    "expires_on": <int>,
                    "generated_at": <int>,
                    "graphics": {
                      "background": <str>,
                      "foreground": <str>
                    },
                    "images": {
                      "large": <str>,
                      "small": <str>
                    },
                    "step_pagination": <int>,
                    "title": <str>,
                    "track_count": <int>,
                    "tracks": {
                      "items": [
                        {
                          "album": {
                            "artist": {
                              "albums_count": <int>,
                              "id": <int>,
                              "image": None,
                              "name": <str>,
                              "picture": None,
                              "slug": <str>
                            },
                            "displayable": <bool>,
                            "downloadable": <bool>,
                            "genre": {
                              "id": <int>,
                              "name": <str>,
                              "path": <list[int]>,
                              "slug": <str>
                            },
                            "hires": <bool>,
                            "hires_streamable": <bool>,
                            "id": <str>,
                            "image": {
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
                            "previewable": <bool>,
                            "purchasable": <bool>,
                            "purchasable_at": <str>,
                            "qobuz_id": <int>,
                            "release_date_download": <str>,
                            "release_date_original": <str>,
                            "release_date_purchase": <str>,
                            "release_date_stream": <str>,
                            "released_at": <int>,
                            "sampleable": <bool>,
                            "streamable": <bool>,
                            "streamable_at": <int>,
                            "title": <str>,
                            "version": <str>
                          },
                          "audio_info": {
                            "replaygain_track_gain": <float>,
                            "replaygain_track_peak": <float>
                          },
                          "composer": {
                            "id": <int>,
                            "name": <str>
                          },
                          "copyright": <str>,
                          "displayable": <bool>,
                          "downloadable": <bool>,
                          "duration": <int>,
                          "hires": <bool>,
                          "hires_streamable": <bool>,
                          "id": <int>,
                          "isrc": <str>,
                          "maximum_bit_depth": <int>,
                          "maximum_channel_count": <int>,
                          "maximum_sampling_rate": <float>,
                          "parental_warning": <bool>,
                          "performer": {
                            "id": <int>,
                            "name": <str>,
                          },
                          "performers": <str>,
                          "position": <int>,
                          "previewable": <bool>,
                          "purchasable": <bool>,
                          "purchasable_at": <int>,
                          "release_date_download": <str>,
                          "release_date_original": <str>,
                          "release_date_purchase": <str>,
                          "release_date_stream": <str>,
                          "sampleable": <bool>,
                          "streamable": <bool>,
                          "streamable_at": <int>,
                          "title": <str>,
                          "version": <str>,
                          "work": None
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>
                    },
                    "type": <str>
                  }
        """
        self._client._require_authentication(
            "users.get_personalized_playlists"
        )
        self._client._validate_type("playlist_type", playlist_type, str)
        params = {"type": playlist_type.strip()}
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "dynamic-tracks/get", params=params
        ).json()

    @TTLCache.cached_method(ttl="popularity")
    def get_track_recommendations(self) -> dict[str, Any]:
        """ """
        pass
