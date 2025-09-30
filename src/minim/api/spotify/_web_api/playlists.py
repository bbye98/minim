from collections.abc import Collection
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPIPlaylistEndpoints:
    """
    Spotify Web API playlist endpoints.

    .. note::

       This class is managed by :class:`minim.api.spotify.WebAPI` and
       should not be instantiated directly.
    """

    _ADDITIONAL_TYPES = {"track", "episode"}

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

               * :code:`"description,uri"` — Returns only the playlist
                 description and URI.
               * :code:`"tracks.items(added_at,added_by.id)"` — Returns
                 only the date added amd the Spotify user ID of the user
                 who added the track.
               * :code:`"tracks.items(track(name,href,album(name,href)))"`
                 — Drills down into the album details.
               * :code:`"tracks.items(track(name,href,album(!name,href)))"`
                 — Excludes the album name.

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
                      "type": <str>,
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
                            "type": <str>,
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
                              "type": <str>,
                              "uri": <str>
                            },
                            "track": <bool>,
                            "type": <str>,
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
                            "type": <str>,
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
                                  "type": <str>,
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
                              "type": <str>,
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
                                "type": <str>,
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
                            "type": <str>,
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
                    "type": <str>,
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
        return self._client._request(f"playlists/{playlist_id}", params=params)

    def change_playlist_details(
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
        <https://developer.spotify.com/documentation/web-api/reference/
        change-playlist-details>`_: Change details of a playlist owned
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

               * :code:`"description,uri"` — Returns only the playlist
                 description and URI.
               * :code:`"tracks.items(added_at,added_by.id)"` — Returns
                 only the date added amd the Spotify user ID of the user
                 who added the track.
               * :code:`"tracks.items(track(name,href,album(name,href)))"`
                 — Drills down into the album details.
               * :code:`"tracks.items(track(name,href,album(!name,href)))"`
                 — Excludes the album name.

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
                          "type": <str>,
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
                                "type": <str>,
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
                            "type": <str>,
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
                              "type": <str>,
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
                          "type": <str>,
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
                          "type": <str>,
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
                                "type": <str>,
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
                            "type": <str>,
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
                              "type": <str>,
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
                          "type": <str>,
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
            f"playlists/{playlist_id}/tracks", params=params
        )

    def add_playlist_items(self):
        pass

    def update_playlist_items(self):
        pass

    def remove_playlist_items(self):
        pass

    def get_my_playlists(self):
        pass

    def get_user_playlists(self):
        pass

    def create_playlist(self):
        pass

    def get_featured_playlists(self):
        pass

    def get_categorized_playlists(self):
        pass

    def get_playlist_cover_image(self):
        pass

    def add_playlist_cover_image(self):
        pass

    def follow_playlist(
        self, playlist_id: str, /, *, public: bool | None = None
    ) -> None:
        """
        `Users > Follow Playlist <https://developer.spotify.com
        /documentation/web-api/reference/follow-playlist>`_: Add the
        current user as a follower of a playlist.

        .. admonition:: Authorization scopes
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

        public : bool, keyword-only, optional
            Specifies whether the playlist will be included in the
            current user's public playlists.

            **Default**: :code:`True`.
        """
        self._client.users.follow_playlist(playlist_id, public=public)

    def unfollow_playlist(self, playlist_id: str, /) -> None:
        """
        `Users > Unfollow Playlist <https://developer.spotify.com
        /documentation/web-api/reference/unfollow-playlist>`_: Remove
        the current user as a follower of a playlist.

        .. admonition:: Authorization scopes
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
        """
        self._client.users.unfollow_playlist(playlist_id)

    def is_following_playlist(self, playlist_id: str, /) -> bool:
        """
        `Users > Check if Current User Follows Playlist
        <https://developer.spotify.com/documentation/web-api/reference
        /check-if-user-follows-playlist>`_: Check whether the current
        user is following a playlist.

        Parameters
        ----------
        playlist_id : str, positional-only
            Spotify ID of the playlist.

            **Example**: :code:`"3cEYpjA9oz9GiPac4AsH4n"`.

        Returns
        -------
        is_following_playlist : bool
            Whether the current user follows the specified playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  True
        """
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
        Validate Spotify item type.

        Parameters
        ----------
        type_ : str, positional-only
            Spotify item type.
        """
        if type_ not in self._ADDITIONAL_TYPES:
            raise ValueError(
                f"{type_!r} is not a valid Spotify item type. Valid "
                "values: '" + ", ".join(self._ADDITIONAL_TYPES) + "'."
            )
