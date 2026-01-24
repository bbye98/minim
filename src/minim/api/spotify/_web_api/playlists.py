from pathlib import Path
from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import SpotifyResourceAPI
from .users import UsersAPI


class PlaylistsAPI(SpotifyResourceAPI):
    """
    Playlists API endpoints for the Spotify Web API.

    .. note::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPI`
       and should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="user")
    def get_playlist(
        self,
        playlist_id: str,
        /,
        *,
        supported_item_types: str | list[str] | None = None,
        fields: str | list[str] | None = None,
        country_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Playlist <https://developer.spotify.com
        /documentation/web-api/reference/get-playlist>`_: Get Spotify
        catalog information for a playlist.

        .. admonition:: Authorization scopes and third-party application mode
           :class: entitlement

           .. tab:: Conditional

              :code:`playlist-read-private` scope
                 Access your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-read-private>`__

              :code:`playlist-read-collaborative` scope
                 Access your collaborative playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-read-collaborative>`__

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        playlist_id : str; positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        supported_item_types : str or list[str]; keyword-only; optional
            Item types supported by the client.

            .. note::

               This parameter was introduced to allow existing clients
               to maintain their current behavior and may be deprecated
               in the future.

            **Valid values**: :code:`"track"`, :code:`"episode"`.

            **API default**: :code:`"track"`.

            **Examples**: :code:`"track"`, :code:`"track,episode"`,
            :code:`["track", "episode"]`.

        fields : str or list[str]; keyword-only; optional
            Fields to return. Use a dot separator to specify
            non-recurring fields and parentheses to specify recurring
            fields within objects. Multiple levels of parentheses can be
            used to drill down into nested objects. Fields can be
            excluded by prefixing them with an exclamation mark. If not
            specified, all fields are returned.

            **Examples**:

            .. container::

               * :code:`"description,uri"` – Returns only the playlist
                 description and URI.
               * :code:`"tracks.items(added_at,added_by.id)"` – Returns
                 only the date added and the Spotify user ID of the user
                 who added the track.
               * :code:`"tracks.items(track(name,href,album(name,href)))"`
                 – Drills down into the album details.
               * :code:`"tracks.items(track(name,href,album(!name,href)))"`
                 – Excludes the album name.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If provided, only content
            available in that market is returned. When a user access
            token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither a country code is provided nor a country can
               be determined from the user account, the content is
               considered unavailable for the client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        playlist : dict[str, Any]
            Spotify content metadata for the playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "collaborative": <bool>,
                    "description": <str>,
                    "external_urls": {
                      "spotify": <str>
                    },
                    "followers": {
                      "href": <str>,
                      "total": <int>
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
                    "owner": {
                      "display_name": <str>,
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "type": "user",
                      "uri": <str>
                    },
                    "primary_color": <int>,
                    "public": <bool>,
                    "snapshot_id": <str>,
                    "tracks": {
                      "href": <str>,
                      "items": [
                        {
                          "added_at": <str>,
                          "added_by": {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "type": "user",
                            "uri": <str>
                          },
                          "is_local": <bool>,
                          "primary_color": <str>,
                          "track": {
                            "audio_preview_url": <str>,
                            "description": <str>,
                            "duration_ms": <int>,
                            "episode": <bool>,
                            "explicit": <bool>,
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "html_description": <str>,
                            "id": <str>,
                            "images": [
                              {
                                "height": <int>,
                                "url": <str>,
                                "width": <int>
                              }
                            ],
                            "is_externally_hosted": <bool>,
                            "is_playable": <bool>,
                            "language": <str>,
                            "languages": <list[str]>,
                            "name": <str>,
                            "release_date": <str>,
                            "release_date_precision": <str>,
                            "show": {
                              "copyrights": <list[str]>,
                              "description": <str>,
                              "explicit": <bool>,
                              "external_urls": {
                                "spotify": <str>
                              },
                              "href": <str>,
                              "html_description": <str>,
                              "id": <str>,
                              "images": [
                                {
                                  "height": <int>,
                                  "url": <str>,
                                  "width": <int>
                                }
                              ],
                              "is_externally_hosted": <bool>,
                              "languages": <list[str]>,
                              "media_type": <str>,
                              "name": <str>,
                              "publisher": <str>,
                              "total_episodes": <int>,
                              "type": "show",
                              "uri": <str>
                            },
                            "track": <bool>,
                            "type": "track",
                            "uri": <str>
                          },
                          "video_thumbnail": {
                            "url": <str>
                          }
                        },
                        {
                          "added_at": <str>,
                          "added_by": {
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "type": "user",
                            "uri": <str>
                          },
                          "is_local": <bool>,
                          "primary_color": <str>,
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
                              "is_playable": <bool>,
                              "name": <str>,
                              "release_date": <str>,
                              "release_date_precision": <str>,
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
                            "disc_number": <int>,
                            "duration_ms": <int>,
                            "episode": <bool>,
                            "explicit": <bool>,
                            "external_ids": {
                              "isrc": <str>
                            },
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "is_local": <bool>,
                            "is_playable": <bool>,
                            "name": <str>,
                            "popularity": <int>,
                            "preview_url": <str>,
                            "track": <bool>,
                            "track_number": <int>,
                            "type": "track",
                            "uri": <str>
                          },
                          "video_thumbnail": {
                            "url": <str>
                          }
                        }
                      ],
                      "limit": <int>,
                      "next": <int>,
                      "offset": <int>,
                      "previous": <int>,
                      "total": <int>
                    },
                    "type": "playlist",
                    "uri": <str>
                  }
        """
        self._validate_spotify_id(playlist_id)
        params = {}
        if supported_item_types is not None:
            params["additional_types"] = self._prepare_types(
                supported_item_types,
                allowed_types=self._AUDIO_TYPES,
                type_prefix="audio",
            )
        if fields is not None:
            if isinstance(fields, str):
                if len(fields):
                    params["fields"] = fields
            else:
                params["fields"] = ",".join(fields)
        if country_code is not None:
            self._client.markets._validate_market(country_code)
            params["market"] = country_code
        return self._client._request(
            "GET", f"playlists/{playlist_id}", params=params
        ).json()

    def update_playlist_details(
        self,
        playlist_id: str,
        /,
        *,
        name: str | None = None,
        description: str | None = None,
        public: bool | None = None,
        collaborative: bool | None = None,
    ) -> None:
        """
        `Playlists > Change Playlist Details
        <https://developer.spotify.com/documentation/web-api/reference
        /change-playlist-details>`_: Update the details of a playlist.

        .. admonition:: Authorization scopes
           :class: entitlement

           .. tab:: Conditional

              :code:`playlist-modify-public` scope
                 Manage your public playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-public>`__

              :code:`playlist-modify-private` scope
                 Manage your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-private>`__

        Parameters
        ----------
        playlist_id : str; positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        name : str; keyword-only; optional
            New playlist name.

        description : str; keyword-only; optional
            New playlist description.

        public : bool; keyword-only; optional
            Whether the playlist is displayed on the current user's
            profile.

        collaborative : bool; keyword-only; optional
            Whether other users can modify the playlist.

            .. note::

               :code:`collaborative=True` can only be set on private
               playlists.
        """
        self._validate_spotify_id(playlist_id)
        payload = {}
        if name is not None:
            self._validate_type("name", name, str)
            if not len(name):
                raise ValueError("The playlist name cannot be blank.")
            payload["name"] = name
        if description is not None:
            self._validate_type("description", description, str)
            payload["description"] = description
        if public is not None:
            self._validate_type("public", public, bool)
            payload["public"] = public
        if collaborative is not None:
            self._validate_type("collaborative", collaborative, bool)
            if collaborative:
                if public is None:
                    payload["public"] = False
                elif public:
                    raise ValueError(
                        "`public` must be False when `collaborative` is True."
                    )
            payload["collaborative"] = collaborative
        if not payload:
            raise ValueError("At least one change must be specified.")
        self._client._request("PUT", f"playlists/{playlist_id}", json=payload)

    @TTLCache.cached_method(ttl="user")
    def get_playlist_items(
        self,
        playlist_id: str,
        /,
        *,
        supported_item_types: str | list[str] | None = None,
        fields: str | list[str] | None = None,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Playlist Items <https://developer.spotify.com
        /documentation/web-api/reference/get-playlists-tracks>`_: Get
        Spotify catalog information for items in a playlist.

        .. admonition:: Authorization scopes and third-party application mode
           :class: entitlement

           .. tab:: Conditional

              :code:`playlist-read-private` scope
                 Access your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-read-private>`__

              :code:`playlist-read-collaborative` scope
                 Access your collaborative playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-read-collaborative>`__

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        playlist_id : str; positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        supported_item_types : str or list[str]; keyword-only; optional
            Item types supported by the client.

            .. note::

               This parameter was introduced to allow existing clients
               to maintain their current behavior and may be deprecated
               in the future.

            **Valid values**: :code:`"track"`, :code:`"episode"`.

            **API default**: :code:`"track"`.

            **Examples**: :code:`"track"`, :code:`"track,episode"`,
            :code:`["track", "episode"]`.

        fields : str or list[str]; keyword-only; optional
            Fields to return. Use a dot separator to specify
            non-recurring fields and parentheses to specify recurring
            fields within objects. Multiple levels of parentheses can be
            used to drill down into nested objects. Fields can be
            excluded by prefixing them with an exclamation mark. If not
            specified, all fields are returned.

            **Examples**:

            .. container::

               * :code:`"description,uri"` – Returns only the playlist
                 description and URI.
               * :code:`"tracks.items(added_at,added_by.id)"` – Returns
                 only the date added and the Spotify user ID of the user
                 who added the track.
               * :code:`"tracks.items(track(name,href,album(name,href)))"`
                 – Drills down into the album details.
               * :code:`"tracks.items(track(name,href,album(!name,href)))"`
                 – Excludes the album name.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If provided, only content
            available in that market is returned. When a user access
            token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither a country code is provided nor a country can
               be determined from the user account, the content is
               considered unavailable for the client.

            **Example**: :code:`"ES"`.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        items : dict[str, Any]
            Page of Spotify content metadata for the playlist items.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "added_at": <str>,
                        "added_by": {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "type": "user",
                          "uri": <str>
                        },
                        "is_local": <bool>,
                        "primary_color": <str>,
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
                          "episode": <bool>,
                          "explicit": <bool>,
                          "external_ids": {
                            "spotify": <str>
                          },
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "is_local": <bool>,
                          "name": <str>,
                          "popularity": <int>,
                          "preview_url": <str>,
                          "track": <bool>,
                          "track_number": <int>,
                          "type": "track",
                          "uri": <str>
                        },
                        "video_thumbnail": {
                          "url": <str>
                        }
                      },
                      {
                        "added_at": <str>,
                        "added_by": {
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "type": "user",
                          "uri": <str>
                        },
                        "is_local": <bool>,
                        "primary_color": <str>,
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
                          "episode": <bool>,
                          "explicit": <bool>,
                          "external_ids": {
                            "isrc": <str>
                          },
                          "external_urls": {
                            "spotify": <str>
                          },
                          "href": <str>,
                          "id": <str>,
                          "is_local": <bool>,
                          "name": <str>,
                          "popularity": <int>,
                          "preview_url": <str>,
                          "track": <bool>,
                          "track_number": <int>,
                          "type": "track",
                          "uri": <str>
                        },
                        "video_thumbnail": {
                          "url": <str>
                        }
                      }
                    ],
                    "limit": <int>,
                    "next": <int>,
                    "offset": <int>,
                    "previous": <int>,
                    "total": <int>
                  }
        """
        self._validate_spotify_id(playlist_id)
        params = {}
        if supported_item_types is not None:
            params["additional_types"] = self._prepare_types(
                supported_item_types,
                allowed_types=self._AUDIO_TYPES,
                type_prefix="audio",
            )
        if fields is not None:
            if isinstance(fields, str):
                if len(fields):
                    params["fields"] = fields
            else:
                params["fields"] = ",".join(fields)
        if country_code is not None:
            self._client.markets._validate_market(country_code)
            params["market"] = country_code
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"playlists/{playlist_id}/tracks", params=params
        ).json()

    def add_playlist_items(
        self,
        playlist_id: str,
        /,
        uris: str | list[str],
        *,
        to_index: int | None = None,
    ) -> dict[str, str]:
        """
        `Playlists > Add Items to Playlist
        <https://developer.spotify.com/documentation/web-api/reference
        /add-tracks-to-playlist>`_: Add items to a playlist.

        .. admonition:: Authorization scopes and user authentication
           :class: entitlement

           .. tab:: Required

              User authentication
                 Access and manage your library.

           .. tab:: Conditional

              :code:`playlist-modify-public` scope
                 Manage your public playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-public>`__

              :code:`playlist-modify-private` scope
                 Manage your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-private>`__

        Parameters
        ----------
        playlist_id : str; positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        uris : str or list[str]
            Spotify URIs of tracks and/or show episodes. A maximum of
            100 URIs can be sent in a request.

            **Examples**:

            .. container::

               * :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7RhQ"`,
               * :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M"`,
               * .. code::

                    [
                        "spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
                        "spotify:track:1301WleyT98MSxVHPZCA6M",
                        "spotify:episode:512ojhOuo1ktJprKbVcKyQ",
                    ]

        to_index : int; keyword-only; optional
            Zero-based index at which to insert the tracks and/or shows.
            If not specified, the items are appended to the end of the
            playlist.

            **Examples**:

            .. container::

               * :code:`0` – Insert items in the first position.
               * :code:`2` – Insert items in the third position.

        Returns
        -------
        snapshot_id : dict[str, str]
            Version identifier for the playlist after the items have
            been added.

            **Sample response**:
            :code:`{"snapshot_id": "AAAAB8C+GjVHq8v4vzStbL6AUYzo1cDV"}`.
        """
        self._client._require_authentication("playlists.add_playlist_items")
        self._validate_spotify_id(playlist_id)
        params = {}
        if to_index is not None:
            self._validate_number("to_index", to_index, int, 0)
            params["position"] = to_index
        return self._client._request(
            "POST",
            f"playlists/{playlist_id}/tracks",
            params=params,
            json={
                "uris": self._prepare_spotify_uris(
                    uris, limit=100, resource_types=self._AUDIO_TYPES
                )
            },
        ).json()

    def reorder_playlist_items(
        self,
        playlist_id: str,
        /,
        *,
        from_index: int,
        to_index: int,
        from_count: int | None = None,
        snapshot_id: str | None = None,
    ) -> dict[str, str]:
        """
        `Playlists > Update Playlist Items
        <https://developer.spotify.com/documentation/web-api/reference
        /reorder-or-replace-playlists-tracks>`__: Reorder items in a
        playlist.

        .. admonition:: Authorization scopes and user authentication
           :class: entitlement

           .. tab:: Required

              User authentication
                 Access and manage your library.

           .. tab:: Conditional

              :code:`playlist-modify-public` scope
                 Manage your public playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-public>`__

              :code:`playlist-modify-private` scope
                 Manage your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-private>`__

        Parameters
        ----------
        playlist_id : str; positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        from_index : int; keyword-only
            Zero-based index of the first item to be reordered.

        to_index : int; keyword-only
            Zero-based index at which to insert the items.

            **Examples**:

            .. container::

               * :code:`0` – Move items selected by `range_start` and
                 `range_length` before the current item in the first
                 position.
               * :code:`10` – Move items selected by `range_start` and
                 `range_length` before the current item in the eleventh
                 position.

        from_count : int; keyword-only; optional
            Number of items, starting from `range_start`, to be
            reordered.

            **API default**: :code:`1`.

        snapshot_id : str; keyword-only; optional
            Version identifier for the playlist against which to make
            changes.

        Returns
        -------
        snapshot_id : dict[str, str]
            Version identifier for the playlist after the items have
            been reordered.

            **Sample response**:
            :code:`{"snapshot_id": "AAAAB8C+GjVHq8v4vzStbL6AUYzo1cDV"}`.
        """
        self._client._require_authentication(
            "playlists.reorder_playlist_items"
        )
        self._validate_spotify_id(playlist_id)
        self._validate_number("from_index", from_index, int, 0)
        self._validate_number("to_index", to_index, int, 0)
        payload = {"insert_before": to_index, "range_start": from_index}
        if from_count is not None:
            self._validate_number("from_count", from_count, int, 1)
            payload["range_length"] = from_count
        if snapshot_id is not None:
            self._validate_type("snapshot_id", snapshot_id, str)
            payload["snapshot_id"] = snapshot_id
        return self._client._request(
            "PUT", f"playlists/{playlist_id}/tracks", json=payload
        ).json()

    def replace_playlist_items(
        self, playlist_id: str, /, uris: str | list[str]
    ) -> dict[str, str]:
        """
        `Playlists > Update Playlist Items
        <https://developer.spotify.com/documentation/web-api/reference
        /reorder-or-replace-playlists-tracks>`__: Clear and replace
        items in a playlist.

        .. admonition:: Authorization scopes and user authentication
           :class: entitlement

           .. tab:: Required

              User authentication
                 Access and manage your library.

           .. tab:: Conditional

              :code:`playlist-modify-public` scope
                 Manage your public playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-public>`__

              :code:`playlist-modify-private` scope
                 Manage your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-private>`__

        Parameters
        ----------
        playlist_id : str; positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        uris : str or list[str]
            Spotify URIs of tracks and/or show episodes. A maximum of
            100 URIs can be sent in a request.

            **Examples**:

            .. container::

               * :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7RhQ"`,
               * :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M"`,
               * .. code::

                    [
                        "spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
                        "spotify:track:1301WleyT98MSxVHPZCA6M",
                        "spotify:episode:512ojhOuo1ktJprKbVcKyQ",
                    ]

        Returns
        -------
        snapshot_id : dict[str, str]
            Version identifier for the playlist after the items have
            been replaced.

            **Sample response**:
            :code:`{"snapshot_id": "AAAAB8C+GjVHq8v4vzStbL6AUYzo1cDV"}`.
        """
        self._client._require_authentication(
            "playlists.replace_playlist_items"
        )
        self._validate_spotify_id(playlist_id)
        return self._client._request(
            "PUT",
            f"playlists/{playlist_id}/tracks",
            json={
                "uris": self._prepare_spotify_uris(
                    uris, limit=100, resource_types=self._AUDIO_TYPES
                )
                if uris
                else []
            },
        ).json()

    def remove_playlist_items(
        self,
        playlist_id: str,
        /,
        uris: str | list[str],
        *,
        snapshot_id: str | None = None,
    ) -> dict[str, str]:
        """
        `Playlists > Remove Playlist Items
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-tracks-playlist>`_: Remove items from a playlist.

        .. admonition:: Authorization scopes and user authentication
           :class: entitlement

           .. tab:: Required

              User authentication
                 Access and manage your library.

           .. tab:: Conditional

              :code:`playlist-modify-public` scope
                 Manage your public playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-public>`__

              :code:`playlist-modify-private` scope
                 Manage your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-private>`__

        Parameters
        ----------
        playlist_id : str; positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        uris : str or list[str]
            Spotify URIs of tracks and/or show episodes. A maximum of
            100 URIs can be sent in a request.

            **Examples**:

            .. container::

               * :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7RhQ"`,
               * :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M"`,
               * .. code::

                    [
                        "spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
                        "spotify:track:1301WleyT98MSxVHPZCA6M",
                        "spotify:episode:512ojhOuo1ktJprKbVcKyQ",
                    ]

        snapshot_id : str; keyword-only; optional
            Version identifier for the playlist against which to make
            changes.

        Returns
        -------
        snapshot_id : dict[str, str]
            Version identifier for the playlist after the items have
            been removed.

            **Sample response**:
            :code:`{"snapshot_id": "AAAAB8C+GjVHq8v4vzStbL6AUYzo1cDV"}`.
        """
        self._client._require_authentication("playlists.remove_playlist_items")
        self._validate_spotify_id(playlist_id)
        payload = {
            "tracks": self._prepare_spotify_uris(
                uris, limit=100, resource_types=self._AUDIO_TYPES
            )
        }
        if snapshot_id is not None:
            self._validate_type("snapshot_id", snapshot_id, str)
            payload["snapshot_id"] = snapshot_id
        return self._client._request(
            "DELETE", f"playlists/{playlist_id}/tracks", json=payload
        ).json()

    @_copy_docstring(UsersAPI.get_my_playlists)
    def get_my_playlists(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        return self._client.users.get_my_playlists(limit=limit, offset=offset)

    @_copy_docstring(UsersAPI.get_user_playlists)
    def get_user_playlists(
        self,
        user_id: str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_user_playlists(
            user_id, limit=limit, offset=offset
        )

    def create_playlist(
        self,
        name: str,
        *,
        description: str | None = None,
        public: bool | None = None,
        collaborative: bool | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Create Playlist <https://developer.spotify.com
        /documentation/web-api/reference/create-playlist>`_: Create a
        playlist.

        .. admonition:: Authorization scopes and user authentication
           :class: entitlement

           .. tab:: Required

              User authentication
                 Access and manage your library.

           .. tab:: Conditional

              :code:`playlist-modify-public` scope
                 Manage your public playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-public>`__

              :code:`playlist-modify-private` scope
                 Manage your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-private>`__

        Parameters
        ----------
        name : str
            Playlist name.

            **Example**: :code:`"My New Playlist Title"`.

        description : str; keyword-only; optional
            Playlist description.

        public : bool; keyword-only; optional
            Whether the playlist is displayed on the current user's
            profile.

            **API default**: :code:`True`.

        collaborative : bool; keyword-only; optional
            Whether other users can modify the playlist.

            .. note::

               :code:`public=False` must accompany
               :code:`collaborative=True` to create a collaborative
               playlist.

            **API default**: :code:`False`.

        Returns
        -------
        playlist : dict[str, Any]
            Spotify content metadata for the newly created playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "collaborative": <bool>,
                    "description": <str>,
                    "external_urls": {
                      "spotify": <str>
                    },
                    "followers": {
                      "href": None,
                      "total": 0
                    },
                    "href": <str>,
                    "id": <str>,
                    "images": [],
                    "name": <str>,
                    "owner": {
                      "display_name": <str>,
                      "external_urls": {
                        "spotify": <str>
                      },
                      "href": <str>,
                      "id": <str>,
                      "type": "user",
                      "uri": <str>
                    },
                    "primary_color": None,
                    "public": <bool>,
                    "snapshot_id": <str>,
                    "tracks": {
                      "href": <str>,
                      "items": [],
                      "limit": 100,
                      "next": None,
                      "offset": 0,
                      "previous": None,
                      "total": 0
                    },
                    "type": "playlist",
                    "uri": <str>
                  }
        """
        self._client._require_authentication("playlists.create_playlist")
        self._validate_type("name", name, str)
        if not len(name):
            raise ValueError("The playlist name cannot be blank.")
        payload = {"name": name}
        if description is not None:
            self._validate_type("description", description, str)
            payload["description"] = description
        if public is not None:
            self._validate_type("public", public, bool)
            self._client._require_scopes(
                "playlists.create_playlist",
                f"playlist-modify-{'public' if public else 'private'}",
            )
            payload["public"] = public
        if collaborative is not None:
            self._validate_type("collaborative", collaborative, bool)
            if collaborative:
                if public is None:
                    payload["public"] = False
                elif public:
                    raise ValueError(
                        "`public` must be False when `collaborative` is True."
                    )
            payload["collaborative"] = collaborative
        return self._client._request(
            "POST",
            f"users/{self._client.my_profile['id']}/playlists",
            json=payload,
        ).json()

    @TTLCache.cached_method(ttl="daily")
    def get_featured_playlists(
        self,
        *,
        locale: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Featured Playlists
        <https://developer.spotify.com/documentation/web-api/reference
        /get-featured-playlists>`_: Get featured playlists.

        .. admonition:: Third-party application mode
           :class: entitlement dropdown

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        locale : str; keyword-only; optional
            IETF BCP 47 language tag consisting of an ISO 639-1 language
            code and an ISO 3166-1 alpha-2 country code joined by an
            underscore. If provided, categories are returned in the
            specified language.

            .. note::

               If a locale identifier is not supplied or the specified
               language is not available, categories will be returned in
               the Spotify default language (American English).

            **Example**: :code:`"es_MX"` – Spanish (Mexico).

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of Spotify content metadata for the featured playlists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "message": <str>,
                    "playlists": {
                      "href": <str>,
                      "items": [
                        {
                          "collaborative": <bool>,
                          "description": <str>,
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
                          "owner": {
                            "display_name": <str>,
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "type": <str>,
                            "uri": <str>
                          },
                          "public": <bool>,
                          "snapshot_id": <str>,
                          "tracks": {
                            "href": <str>,
                            "total": <int>
                          },
                          "type": <str>,
                          "uri": <str>
                        }
                      ],
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>
                    }
                  }
        """
        params = {}
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        if locale:
            self._validate_locale(locale)
            params["locale"] = locale
        return self._client._request(
            "GET", "browse/featured-playlists", params=params
        ).json()

    @TTLCache.cached_method(ttl="daily")
    def get_categorized_playlists(
        self,
        category_id: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Category's Playlist
        <https://developer.spotify.com/documentation/web-api/reference
        /get-a-categories-playlists>`_: Get playlists tagged with a
        particular category.

        .. admonition:: Third-party application mode
           :class: entitlement dropdown

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        category_id : str, positional-only
            Spotify category ID.

            .. seealso::

               :meth:`~minim.api.spotify.CategoriesAPI.get_categories`
               – Get information on available categories.

            **Examples**: :code:`"dinner"`, :code:`"party"`.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of Spotify content metadata for the playlists in the
            specified category.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "message": <str>,
                    "playlists": {
                      "href": <str>,
                      "items": [
                        {
                          "collaborative": <bool>,
                          "description": <str>,
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
                          "owner": {
                            "display_name": <str>,
                            "external_urls": {
                              "spotify": <str>
                            },
                            "href": <str>,
                            "id": <str>,
                            "type": <str>,
                            "uri": <str>
                          },
                          "public": <bool>,
                          "snapshot_id": <str>,
                          "tracks": {
                            "href": <str>,
                            "total": <int>
                          },
                          "type": <str>,
                          "uri": <str>
                        }
                      ],
                      "limit": <int>,
                      "next": <str>,
                      "offset": <int>,
                      "previous": <str>,
                      "total": <int>
                    }
                  }
        """
        params = {}
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"browse/categories/{category_id}/playlists", params=params
        ).json()

    @TTLCache.cached_method(ttl="user")
    def get_playlist_cover_image(
        self, playlist_id: str, /
    ) -> list[dict[str, int | str]]:
        """
        `Playlists > Get Playlist Cover Image
        <https://developer.spotify.com/documentation/web-api/reference
        /get-playlist-cover>`_: Get the cover image associated with a
        playlist.

        Parameters
        ----------
        playlist_id : str; positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        Returns
        -------
        playlist_cover_image : list[dict[str, int | str]]
            Playlist cover image.

            **Sample response**:

            .. code::

               [
                 {
                   "height": <int>,
                   "url": <str>,
                   "width": <int>
                 }
               ]
        """
        self._validate_spotify_id(playlist_id)
        return self._client._request(
            "GET", f"playlists/{playlist_id}/images"
        ).json()

    def add_playlist_cover_image(
        self, playlist_id: str, /, image: bytes | str | Path
    ) -> None:
        """
        `Playlists > Add Custom Playlist Cover Image
        <https://developer.spotify.com/documentation/web-api/reference
        /upload-custom-playlist-cover>`_: Add a custom cover image to a
        playlist.

        .. admonition:: Authorization scopes
           :class: entitlement

           .. tab:: Required

              :code:`ugc-image-upload` scope
                 Upload images to Spotify on your behalf. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#ugc-image-upload>`__

           .. tab:: Conditional

              :code:`playlist-modify-public` scope
                 Manage your public playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-public>`__

              :code:`playlist-modify-private` scope
                 Manage your private playlists. `Learn more.
                 <https://developer.spotify.com/documentation/web-api
                 /concepts/scopes#playlist-modify-private>`__

        Parameters
        ----------
        playlist_id : str; positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        image : bytes, str, or pathlib.Path
            Base64-encoded JPEG image data, provided as a bytes object
            or a file path.

            **Example**:
            :code:`"/9j/2wCEABoZGSccJz4lJT5CLy8vQkc9Ozs9R0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0cBHCcnMyYzPSYmPUc9Mj1HR0dEREdHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR//dAAQAAf/uAA5BZG9iZQBkwAAAAAH/wAARCAABAAEDACIAAREBAhEB/8QASwABAQAAAAAAAAAAAAAAAAAAAAYBAQAAAAAAAAAAAAAAAAAAAAAQAQAAAAAAAAAAAAAAAAAAAAARAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwAAARECEQA/AJgAH//Z"`.
        """
        self._client._require_scopes(
            "playlists.add_playlist_cover_image", "ugc-image-upload"
        )
        self._validate_spotify_id(playlist_id)
        if isinstance(image, str | Path):
            image = Path(image).resolve(True)
            with open(image, "rb") as f:
                image = f.read()
        if not isinstance(image, bytes) or not (
            image.startswith(b"\xff\xd8") and image.endswith(b"\xff\xd9")
        ):
            raise ValueError(
                "The value or file provided via `image` does not "
                "contain binary data or a JPEG image."
            )
        if len(image) < 262_144:
            raise ValueError(
                "The JPEG image provided via `image` exceeds 256 KB."
            )
        self._client._request(
            "PUT",
            f"playlists/{playlist_id}/images",
            data=image,
            headers={"Content-Type": "image/jpeg"},
        )

    @_copy_docstring(UsersAPI.follow_playlist)
    def follow_playlist(
        self, playlist_id: str, /, *, public: bool | None = None
    ) -> None:
        self._client.users.follow_playlist(playlist_id, public=public)

    @_copy_docstring(UsersAPI.unfollow_playlist)
    def unfollow_playlist(self, playlist_id: str, /) -> None:
        self._client.users.unfollow_playlist(playlist_id)

    @_copy_docstring(UsersAPI.is_following_playlist)
    def is_following_playlist(self, playlist_id: str, /) -> bool:
        return self._client.users.is_following_playlist(playlist_id)
