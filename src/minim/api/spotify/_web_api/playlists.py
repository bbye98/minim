from collections.abc import Collection
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..._shared import _copy_docstring
from .users import WebAPIUserEndpoints

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPIPlaylistEndpoints:
    """
    Spotify Web API playlist endpoints.

    .. note::

       This class is managed by :class:`minim.api.spotify.WebAPI` and
       should not be instantiated directly.
    """

    _TYPES = {"track", "episode"}

    def __init__(self, client: "WebAPI", /) -> None:
        """
        Parameters
        ----------
        client : minim.api.spotify.WebAPI
            Minim's Spotify Web API client.
        """
        self._client = client

    def get_playlist(
        self,
        playlist_id: str,
        /,
        *,
        additional_types: str | Collection[str] | None = None,
        fields: str | Collection[str] | None = None,
        market: str | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Playlist <https://developer.spotify.com
        /documentation/web-api/reference/get-playlist>`_: Get Spotify
        catalog information for a playlist.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
        playlist_id : str, positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        additional_types : str or Collection[str], keyword-only, optional
            (Comma-separated) list of item types supported by the API
            client besides the default :code:`"track"` type.

            .. note::

               This parameter was introduced to allow existing clients
               to maintain their current behavior and might be
               deprecated in the future.

            **Valid values**: :code:`"track"`, :code:`"episode"`.

        fields : str or Collection[str], keyword-only, optional
            (Comma-separated) list of fields to return. Use a dot
            separator to specify non-recurring fields and parentheses to
            specify recurring fields within objects. Multiple levels of
            parentheses can be used to drill down into nested objects.
            Fields can be excluded by prefixing them with an exclamation
            mark. If omitted, all fields are returned.

            .. container::

               **Examples**:

               * :code:`"description,uri"` – Returns only the playlist
                 description and URI.
               * :code:`"tracks.items(added_at,added_by.id)"` – Returns
                 only the date added amd the Spotify user ID of the user
                 who added the track.
               * :code:`"tracks.items(track(name,href,album(name,href)))"`
                 – Drills down into the album details.
               * :code:`"tracks.items(track(name,href,album(!name,href)))"`
                 – Excludes the album name.

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
        playlist : dict[str, Any]
            Spotify content metadata for the playlist.

            .. admonition:: Sample responses
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
        self._client._validate_spotify_id(playlist_id)
        params = {}
        if additional_types is not None:
            params["additional_types"] = self._prepare_item_types(
                additional_types
            )
        if fields is not None:
            if isinstance(fields, str):
                if fields:
                    params["fields"] = fields
            else:
                params["fields"] = ",".join(fields)
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
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
        /change-playlist-details>`_: Change details of a playlist owned
        by the current user.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`playlist-modify-public`
                 Manage your public playlists.

              :code:`playlist-modify-private`
                 Manage your private playlists.

        Parameters
        ----------
        playlist_id : str, positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        name : str, keyword-only, optional
            Playlist name.

            **Example**: :code:`"My New Playlist Title"`.

        description : str, keyword-only, optional
            Playlist description.

        public : bool, keyword-only, optional
            Specifies whether the playlist is displayed on the user's
            profile.

        collaborative : bool, keyword-only, optional
            Specifies whether other users can modify the playlist.

            .. note::

               :code:`collaborative=True` can only be set on non-public
               playlists.
        """
        self._client._validate_spotify_id(playlist_id)
        self._client._require_scopes(
            "change_playlist_details",
            {"playlist-modify-public", "playlist-modify-private"},
        )
        payload = {}
        if name is not None:
            self._client._validate_type("name", name, str)
            payload["name"] = name
        if description is not None:
            self._client._validate_type("description", description, str)
            payload["description"] = description
        if public is not None:
            self._client._validate_type("public", public, bool)
            payload["public"] = public
        if collaborative is not None:
            self._client._validate_type("collaborative", collaborative, bool)
            payload["collaborative"] = collaborative
        if not payload:
            raise ValueError("At least one change must be specified.")
        self._client._request("PUT", f"playlists/{playlist_id}", json=payload)

    def get_playlist_items(
        self,
        playlist_id: str,
        /,
        *,
        additional_types: str | Collection[str] | None = None,
        fields: str | Collection[str] | None = None,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Playlist Items <https://developer.spotify.com
        /documentation/web-api/reference/get-playlists-tracks>`_: Get
        Spotify catalog information for items in a playlist.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Optional

              :code:`playlist-read-private`
                 Access your private playlists.

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
        playlist_id : str, positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        additional_types : str or Collection[str], keyword-only, optional
            (Comma-separated) list of item types supported by the API
            client besides the default :code:`"track"` type.

            .. note::

               This parameter was introduced to allow existing clients
               to maintain their current behavior and might be
               deprecated in the future.

            **Valid values**: :code:`"track"`, :code:`"episode"`.

        fields : str or Collection[str], keyword-only, optional
            (Comma-separated) list of fields to return. Use a dot
            separator to specify non-recurring fields and parentheses to
            specify recurring fields within objects. Multiple levels of
            parentheses can be used to drill down into nested objects.
            Fields can be excluded by prefixing them with an exclamation
            mark. If omitted, all fields are returned.

            .. container::

               **Examples**:

               * :code:`"description,uri"` – Returns only the playlist
                 description and URI.
               * :code:`"tracks.items(added_at,added_by.id)"` – Returns
                 only the date added amd the Spotify user ID of the user
                 who added the track.
               * :code:`"tracks.items(track(name,href,album(name,href)))"`
                 – Drills down into the album details.
               * :code:`"tracks.items(track(name,href,album(!name,href)))"`
                 – Excludes the album name.

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

        limit : int, keyword-only, optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first item to return. Use with `limit` to get
            the next set of items.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        items : dict[str, Any]
            Spotify content metadata for the playlist items.

            .. admonition:: Sample responses
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
        self._client._validate_spotify_id(playlist_id)
        params = {}
        if additional_types is not None:
            params["additional_types"] = self._prepare_item_types(
                additional_types
            )
        if fields is not None:
            if isinstance(fields, str):
                if fields:
                    params["fields"] = fields
            else:
                params["fields"] = ",".join(fields)
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"playlists/{playlist_id}/tracks", params=params
        ).json()

    def add_playlist_items(
        self,
        playlist_id: str,
        /,
        uris: str | Collection[str],
        *,
        position: int | None = None,
    ) -> dict[str, str]:
        """
        `Playlists > Add Items to Playlist
        <https://developer.spotify.com/documentation/web-api/reference
        /add-tracks-to-playlist>`_: Add items to a user's playlist.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`playlist-modify-public`
                 Manage your public playlists.

              :code:`playlist-modify-private`
                 Manage your private playlists.

        Parameters
        ----------
        playlist_id : str, positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        uris : str or Collection[str]
            (Comma-separated) list of Spotify URIs of tracks and/or show
            episodes. A maximum of 100 URIs can be sent in one request.

            .. container::

               **Examples**:

               * :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7RhQ"`,
               * :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M"`,
               * .. code::

                    [
                        "spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
                        "spotify:track:1301WleyT98MSxVHPZCA6M",
                        "spotify:episode:512ojhOuo1ktJprKbVcKyQ",
                    ]

        position : int, keyword-only, optional
            Zero-based index at which to insert the items. If not
            specified, the items are appended to the end of the
            playlist.

            .. container::

               **Examples**:

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
        self._client._require_scopes(
            "add_playlist_items",
            {"playlist-modify-public", "playlist-modify-private"},
        )
        self._client._validate_spotify_id(playlist_id)
        params = {}
        if position is not None:
            self._client._validate_number("position", position, int, 0)
            params["position"] = position
        return self._client._request(
            "POST",
            f"playlists/{playlist_id}/tracks",
            params=params,
            json={
                "uris": self._client._prepare_spotify_uris(
                    uris, limit=100, item_types=self._TYPES
                )
            },
        ).json()

    def reorder_playlist_items(
        self,
        playlist_id: str,
        /,
        *,
        insert_before: int,
        range_start: int,
        range_length: int | None = None,
        snapshot_id: str | None = None,
    ) -> dict[str, str]:
        """
        `Playlists > Update Playlist Items
        <https://developer.spotify.com/documentation/web-api/reference
        /reorder-or-replace-playlists-tracks>`_: Reorder items in a
        user's playlist.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`playlist-modify-public`
                 Manage your public playlists.

              :code:`playlist-modify-private`
                 Manage your private playlists.

        Parameters
        ----------
        playlist_id : str, positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        insert_before : int, keyword-only
            Zero-based index at which to insert the items.

            .. container::

               **Examples**:

               * :code:`0` – Move items selected by `range_start` and
                 `range_length` before the current item in the first
                 position.
               * :code:`10` – Move items selected by `range_start` and
                 `range_length` before the current item in the eleventh
                 position.

        range_start : int, keyword-only
            Zero-based index of the first item to be reordered.

        range_length : int, keyword-only, optional
            Number of items, starting from `range_start`, to be
            reordered.

            **Default**: :code:`1`.

        snapshot_id : str, keyword-only, optional
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
        self._client._require_scopes(
            "reorder_playlist_items",
            {"playlist-modify-public", "playlist-modify-private"},
        )
        self._client._validate_spotify_id(playlist_id)
        self._client._validate_number("insert_before", insert_before, int, 0)
        self._client._validate_number("range_start", range_start, int, 0)
        payload = {"insert_before": insert_before, "range_start": range_start}
        if range_length is not None:
            self._client._validate_number("range_length", range_length, int, 1)
            payload["range_length"] = range_length
        if snapshot_id is not None:
            self._client._validate_type("snapshot_id", snapshot_id, str)
            payload["snapshot_id"] = snapshot_id
        return self._client._request(
            "PUT", f"playlists/{playlist_id}/tracks", json=payload
        ).json()

    def replace_playlist_items(
        self,
        playlist_id: str,
        /,
        uris: str | Collection[str],
    ) -> dict[str, str]:
        """
        `Playlists > Update Playlist Items
        <https://developer.spotify.com/documentation/web-api/reference
        /reorder-or-replace-playlists-tracks>`_: Replace items in a
        user's playlist.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`playlist-modify-public`
                 Manage your public playlists.

              :code:`playlist-modify-private`
                 Manage your private playlists.

        Parameters
        ----------
        playlist_id : str, positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        uris : str or Collection[str]
            (Comma-separated) list of Spotify URIs of tracks and/or show
            episodes. A maximum of 100 URIs can be sent in one request.
            If None or an empty array is provided, the playlist is cleared.

            .. container::

               **Examples**:

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
        self._client._require_scopes(
            "replace_playlist_items",
            {"playlist-modify-public", "playlist-modify-private"},
        )
        self._client._validate_spotify_id(playlist_id)
        return self._client._request(
            "PUT",
            f"playlists/{playlist_id}/tracks",
            json={
                "uris": self._client._prepare_spotify_uris(
                    uris, limit=100, item_types=self._TYPES
                )
                if uris
                else []
            },
        ).json()

    def remove_playlist_items(
        self,
        playlist_id: str,
        /,
        uris: str | Collection[str],
        *,
        snapshot_id: str | None = None,
    ) -> dict[str, str]:
        """
        `Playlists > Remove Playlist Items
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-tracks-playlist>`_: Remove items from a user's playlist.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`playlist-modify-public`
                 Manage your public playlists.

              :code:`playlist-modify-private`
                 Manage your private playlists.

        Parameters
        ----------
        playlist_id : str, positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        uris : str or Collection[str]
            (Comma-separated) list of Spotify URIs of tracks and/or show
            episodes. A maximum of 100 URIs can be sent in one request.

            .. container::

               **Examples**:

               * :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7RhQ"`,
               * :code:`"spotify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:track:1301WleyT98MSxVHPZCA6M"`,
               * .. code::

                    [
                        "spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
                        "spotify:track:1301WleyT98MSxVHPZCA6M",
                        "spotify:episode:512ojhOuo1ktJprKbVcKyQ",
                    ]

        snapshot_id : str, keyword-only, optional
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
        self._client._require_scopes(
            "remove_playlist_items",
            {"playlist-modify-public", "playlist-modify-private"},
        )
        self._client._validate_spotify_id(playlist_id)
        payload = {
            "tracks": self._client._prepare_spotify_uris(
                uris, limit=100, item_types=self._TYPES
            )
        }
        if snapshot_id is not None:
            self._client._validate_type("snapshot_id", snapshot_id, str)
            payload["snapshot_id"] = snapshot_id
        return self._client._request(
            "DELETE", f"playlists/{playlist_id}/tracks", json=payload
        ).json()

    def get_user_playlists(
        self,
        user_id: str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Current User's Playlists
        <https://developer.spotify.com/documentation/web-api/reference
        /get-a-list-of-current-users-playlists>`_: Get playlists owned
        or followed by the current user․
        `Playlists > Get User's Playlists <https://developer.spotify.com
        /documentation/web-api/reference/get-list-users-playlists>`_:
        Get playlists owned or followed by a Spotify user.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`playlist-read-private`
                 Access your private playlists.

              :code:`playlist-read-collaborative`
                 Access your collaborative playlists.

        Parameters
        ----------
        user_id : str, positional-only, optional
            Spotify user ID. If not provided, the current user's
            playlists will be returned.

            **Example**: :code:`"smedjan"`.

        limit : int, keyword-only, optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first playlist to return. Use with `limit` to
            get the next set of playlists.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            Spotify content metadata for the playlists.

            .. admonition:: Sample responses
               :class: dropdown

               .. code::

                  {
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
        """
        self._client._require_scopes(
            "get_user_playlists", "playlist-read-private"
        )
        params = {}
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        if user_id:
            self._client._require_scopes(
                "get_user_playlists", "playlist-read-collaborative"
            )
            self._client._validate_spotify_id(user_id, strict_length=False)
            return self._client._request(
                "GET", f"users/{user_id}/playlists", params=params
            )

        return self._client._request("GET", "me/playlists", params=params)

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

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`playlist-modify-public`
                 Manage your public playlists.

              :code:`playlist-modify-private`
                 Manage your private playlists.

        Parameters
        ----------
        name : str
            Playlist name.

            **Example**: :code:`"My New Playlist Title"`.

        description : str, keyword-only, optional
            Playlist description.

        public : bool, keyword-only, optional
            Specifies whether the playlist is displayed on the user's
            profile.

            **Default**: :code:`True`.

        collaborative : bool, keyword-only, optional
            Specifies whether other users can modify the playlist.

            .. note::

               :code:`public=False` must accompany
               :code:`collaborative=True` to create a collaborative
               playlist.

            **Default**: :code:`False`.

        Returns
        -------
        playlist : dict[str, Any]
            Spotify content metadata for the newly created playlist.

            .. admonition:: Sample responses
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
        self._client._require_scopes(
            "create_playlist", "playlist-modify-public"
        )
        self._client._validate_type("name", name, str)
        payload = {"name": name}
        if description is not None:
            self._client._validate_type("description", description, str)
            payload["description"] = description
        if public is not None:
            self._client._validate_type("public", public, bool)
            if not public:
                self._client._require_scopes(
                    "create_playlist", "playlist-modify-private"
                )
            payload["public"] = public
        if collaborative is not None:
            self._client._validate_type("collaborative", collaborative, bool)
            payload["collaborative"] = collaborative
        return self._client._request(
            "POST",
            f"users/{self._client.user_profile['id']}/playlists",
            json=payload,
        ).json()

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
           :class: authorization-scope

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
        locale : str, keyword-only, optional
            Locale identifier consisting of an ISO 639-1 language
            code and an ISO 3166-1 alpha-2 country code joined by an
            underscore. When this parameter is provided, the category
            strings are returned in the specified language.

            .. note::

               If a locale identifier is not supplied or the specified
               language is not available, the category strings returned
               will be in the Spotify default language (American
               English).

            **Example**: :code:`"es_MX"` for Spanish (Mexico).

        limit : int, keyword-only, optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first playlist to return. Use with `limit` to
            get the next set of playlists.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        featured_playlists : dict[str, Any]
            Spotify content metadata for the featured playlists.

            .. admonition:: Sample responses
               :class: dropdown

               .. code::

                  TODO
        """
        params = {}
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        if locale:
            params["locale"] = locale
        return self._client._request(
            "GET", "browse/featured-playlists", params=params
        ).json()

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
           :class: authorization-scope

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
        category_id : str
            Spotify category ID.

            **Examples**: :code:`"dinner"`, :code:`"party"`.

        limit : int, keyword-only, optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first playlist to return. Use with `limit` to
            get the next set of playlists.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        categorized_playlists : dict[str, Any]
            Spotify content metadata for the category's playlists.

            .. admonition:: Sample responses
               :class: dropdown

               .. code::

                  TODO
        """
        params = {}
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"browse/categories/{category_id}/playlists", params=params
        ).json()

    def get_playlist_cover_image(
        self, playlist_id: str, /
    ) -> list[dict[str, int | str]]:
        """
        `Playlists > Get Playlist Cover Image
        <https://developer.spotify.com/documentation/web-api/reference
        /get-playlist-cover>`_: Get the cover image currently associated
        with a playlist.

        Parameters
        ----------
        playlist_id : str, positional-only
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
        self._client._validate_spotify_id(playlist_id)
        return self._client._request(
            "GET", f"playlists/{playlist_id}/images"
        ).json()

    def add_playlist_cover_image(
        self, playlist_id: str, /, image: bytes | str | Path
    ) -> None:
        """
        `Playlists > Add Custom Playlist Cover Image
        <https://developer.spotify.com/documentation/web-api/reference
        /upload-custom-playlist-cover>`_: Add a cover image to a
        playlist.

        Parameters
        ----------
        playlist_id : str, positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        image : bytes, str, or pathlib.Path
            Base64-encoded JPEG image data, provided as a bytes object
            or a file path.
        """
        self._client._require_scopes(
            "add_playlist_cover_image",
            {
                "ugc-image-upload",
                "playlist-modify-public",
                "playlist-modify-private",
            },
        )
        self._client._validate_spotify_id(playlist_id)
        if isinstance(image, str | Path):
            image = Path(image).resolve(True)
            with open(image, "rb") as f:
                image = f.read()
        if not isinstance(image, bytes) or not (
            image.startswith(b"\xff\xd8") and image.endswith(b"\xff\xd9")
        ):
            raise ValueError(
                "The value or file specified in the `image` argument "
                "does not contain binary data or a JPEG image."
            )
        if len(image) < 262_144:
            raise ValueError(
                "The JPEG image specified in the `image` argument "
                "exceeds 256 KB."
            )
        self._client._request(
            "PUT",
            f"playlists/{playlist_id}/images",
            data=image,
            headers={"Content-Type": "image/jpeg"},
        )

    @_copy_docstring(WebAPIUserEndpoints.follow_playlist)
    def follow_playlist(
        self, playlist_id: str, /, *, public: bool | None = None
    ) -> None:
        self._client.users.follow_playlist(playlist_id, public=public)

    @_copy_docstring(WebAPIUserEndpoints.unfollow_playlist)
    def unfollow_playlist(self, playlist_id: str, /) -> None:
        self._client.users.unfollow_playlist(playlist_id)

    @_copy_docstring(WebAPIUserEndpoints.is_following_playlist)
    def is_following_playlist(self, playlist_id: str, /) -> bool:
        return self._client.users.is_following_playlist(playlist_id)

    def _prepare_item_types(self, types: str | Collection[str], /) -> str:
        """
        Stringify a list of Spotify item types into a comma-delimited
        string.

        Parameters
        ----------
        types : str, positional-only
            Spotify item types.

        Returns
        -------
        types : str
            Comma-delimited string containing Spotify item types.
        """
        if isinstance(types, str):
            split_types = types.split(",")
            for type_ in split_types:
                self._validate_item_type(type_)
            return ",".join(sorted(split_types))

        types = set(types)
        for type_ in types:
            self._validate_item_type(type_)
        return ",".join(sorted(types))

    def _validate_item_type(self, type_: str, /) -> None:
        """
        Validate a Spotify item type.

        Parameters
        ----------
        type_ : str, positional-only
            Spotify item type.
        """
        if type_ not in self._TYPES:
            _types = ", ".join(self._TYPES)
            raise ValueError(
                f"Invalid Spotify item type {type_!r}. "
                f"Valid values: '{_types}'."
            )
