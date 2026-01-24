from functools import cached_property
from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import PrivateQobuzResourceAPI
from .search import PrivateSearchAPI
from .users import PrivateUsersAPI


class PrivatePlaylistsAPI(PrivateQobuzResourceAPI):
    """
    Playlists API endpoints for the private Qobuz API.

    .. important::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPIClient`
       and should not be instantiated directly.
    """

    _PLAYLIST_TYPES = {"owner", "subscriber"}
    _RELATIONSHIPS = {"tracks", "getSimilarPlaylists", "focus", "focusAll"}

    @cached_property
    def available_playlist_tags(self) -> dict[str, dict[str, Any]]:
        """
        Available playlist tags.

        .. note::

           Accessing this property may call :meth:`get_playlist_tags`
           and make a request to the Qobuz API.
        """
        return {
            tag.pop("slug"): tag for tag in self.get_playlist_tags()["tags"]
        }

    def _validate_playlist_tag_slug(self, playlist_tag_slug: str, /) -> None:
        """
        Validate playlist tag slug.

        Parameters
        ----------
        playlist_tag_slug : str; positional-only
            Playlist tag slug.
        """
        if not isinstance(playlist_tag_slug, str):
            raise ValueError("Qobuz playlist tag slugs must be strings.")
        if "available_playlist_tags" in self.__dict__:
            if playlist_tag_slug not in self.available_playlist_tags:
                playlist_tag_slugs_str = "', '".join(
                    self.available_playlist_tags
                )
                raise ValueError(
                    f"Invalid playlist tag slug {playlist_tag_slug!r}. "
                    f"Valid values: {playlist_tag_slugs_str}."
                )

    def add_playlist_tracks(
        self,
        playlist_id: int | str,
        /,
        track_ids: int | str | list[int | str],
        *,
        allow_duplicates: bool | None = None,
    ) -> dict[str, Any]:
        """
        Add tracks to a playlist.

        .. admonition:: User authentication
           :class: entitlement

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        playlist_id : int or str; positional-only
            Qobuz ID of the playlist.

            **Examples**: :code:`2776610`, :code:`"6754150"`.

        track_ids : int, str, or list[int | str]
            Qobuz IDs of the tracks.

            **Examples**: :code:`23929516`, :code:`"344521217"`,
            :code:`"23929516,344521217"`,
            :code:`[23929516, "344521217"]`.

        allow_duplicates : bool; keyword-only; optional
            Whether to allow duplicate tracks in the playlist.

            **API default**: :code:`True`.

        Returns
        -------
        playlist : dict[str, Any]
            Qobuz content metadata for the updated playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "created_at": <int>,
                    "description": <str>,
                    "duration": <int>,
                    "id": <int>,
                    "is_collaborative": <bool>,
                    "is_public": <bool>,
                    "name": <str>,
                    "owner": {
                      "id": <int>,
                      "name": <str>
                    },
                    "public_at": <int>,
                    "tracks_count": <int>,
                    "updated_at": <int>,
                    "users_count": <int>
                  }
        """
        self._client._require_authentication("playlists.add_playlist_tracks")
        self._validate_qobuz_ids(playlist_id, _recursive=False)
        params = {
            "playlist_id": playlist_id,
            "track_ids": self._prepare_qobuz_ids(track_ids, data_type=str),
        }
        if allow_duplicates is not None:
            self._validate_type("allow_duplicates", allow_duplicates, bool)
            params["no_duplicate"] = not allow_duplicates
        return self._client._request(
            "POST", "playlist/addTracks", params=params
        ).json()

    def create_playlist(
        self,
        name: str,
        *,
        description: str | None = None,
        public: bool | None = None,
        collaborative: bool | None = None,
        from_album_id: str | None = None,
        from_track_ids: int | str | list[int | str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a playlist.

        .. admonition:: User authentication
           :class: entitlement

           .. tab:: Required

              User authentication
                 Access and manage your library.

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

            **API default**: :code:`False`.

        from_album_id : str; keyword-only; optional
            Qobuz ID of the album to add tracks from.

            **Examples**: :code:`"0075679933652"`,
            :code:`"aaxy9wirwgn2a"`.

        from_track_ids : int, str, or list[int | str]; keyword-only; \
        optional
            Qobuz IDs of the tracks to add.

            **Examples**: :code:`23929516`, :code:`"344521217"`,
            :code:`"23929516,344521217"`,
            :code:`[23929516, "344521217"]`.

        Returns
        -------
        playlist : dict[str, Any]
            Qobuz content metadata for the newly created playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "created_at": <int>,
                    "description": <str>,
                    "duration": <int>,
                    "id": <int>,
                    "is_collaborative": <bool>,
                    "is_public": <bool>,
                    "name": <str>,
                    "owner": {
                      "id": <int>,
                      "name": <str>
                    },
                    "public_at": <int>,
                    "tracks_count": <int>,
                    "updated_at": <int>,
                    "users_count": <int>
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
            payload["public"] = public
        if collaborative is not None:
            self._validate_type("collaborative", collaborative, bool)
            payload["collaborative"] = collaborative
        if from_album_id is not None:
            self._validate_album_id(from_album_id)
            payload["album_id"] = from_album_id
        if from_track_ids is not None:
            self._validate_qobuz_ids(from_track_ids)
            payload["track_ids"] = self._prepare_qobuz_ids(
                from_track_ids, data_type=str
            )
        return self._client._request(
            "POST", "playlist/create", data=payload
        ).json()

    def delete_playlist(self, playlist_id: int | str, /) -> dict[str, Any]:
        """
        Delete a playlist.

        .. admonition:: User authentication
           :class: entitlement

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        playlist_id : int or str; positional-only
            Qobuz ID of the playlist.

            **Examples**: :code:`2776610`, :code:`"6754150"`.

        Returns
        -------
        response : dict[str, str]
            API JSON response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        self._client._require_authentication("playlists.delete_playlist")
        self._validate_qobuz_ids(playlist_id, _recursive=False)
        return self._client._request(
            "POST", "playlist/delete", data={"playlist_id": playlist_id}
        ).json()

    def remove_playlist_tracks(
        self,
        playlist_id: int | str,
        /,
        playlist_track_ids: int | str | list[int, str],
    ) -> dict[str, Any]:
        """
        Remove tracks from a playlist.

        .. admonition:: User authentication
           :class: entitlement

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        playlist_id : int or str; positional-only
            Qobuz ID of the playlist.

            **Examples**: :code:`2776610`, :code:`"6754150"`.

        playlist_track_ids : int, str, or list[int | str]
            Playlist track IDs of the tracks to remove.

            **Examples**: :code:`3775131234`, :code:`"3775131243"`,
            :code:`"3775131234,3775131243"`,
            :code:`[3775131234, "3775131243"]`.

            .. seealso::

               :meth:`get_playlist` – Get playlist track IDs by
               including :code:`"tracks"` in the `expand` parameter.

        Returns
        -------
        playlist : dict[str, Any]
            Qobuz content metadata for the updated playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "created_at": <int>,
                    "description": <str>,
                    "duration": <int>,
                    "id": <int>,
                    "is_collaborative": <bool>,
                    "is_public": <bool>,
                    "name": <str>,
                    "owner": {
                      "id": <int>,
                      "name": <str>
                    },
                    "public_at": <int>,
                    "status": "success",
                    "tracks_count": <int>,
                    "updated_at": <int>,
                    "users_count": <int>
                  }
        """
        self._client._require_authentication(
            "playlists.remove_playlist_tracks"
        )
        self._validate_qobuz_ids(playlist_id, _recursive=False)
        return self._client._request(
            "POST",
            "playlist/deleteTracks",
            data={
                "playlist_id": playlist_id,
                "playlist_track_ids": self._prepare_qobuz_ids(
                    playlist_track_ids, data_type=str
                ),
            },
        ).json()

    @TTLCache.cached_method(ttl="user")
    def get_playlist(
        self,
        playlist_id: int | str,
        /,
        *,
        expand: str | list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for a playlist.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab:: Conditional

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        playlist_id : int or str; positional-only
            Qobuz ID of the playlist.

            **Examples**: :code:`2776610`, :code:`"6754150"`.

        expand : str or list[str]; keyword-only; optional
            Related resources to include metadata for in the response.

            **Valid values**: :code:`"tracks"`,
            :code:`"getSimilarPlaylists"`, :code:`"focus"`,
            :code:`"focusAll"`.

            **Examples**: :code:`"getSimilarPlaylists"`,
            :code:`"focus,focusAll"`, :code:`["focus", "focusAll"]`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return when :code:`"tracks"` is
            included in the `expand` parameter.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first track to return when :code:`"tracks"` is
            included in the `expand` parameter. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlist : dict[str, Any]
            Qobuz content metadata for the playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "created_at": <int>,
                    "description": <str>,
                    "duration": <int>,
                    "featured_artists": [],
                    "genres": [
                      {
                        "color": <str>,
                        "id": <int>,
                        "name": <str>,
                        "path": <list[int]>,
                        "percent": <int>,
                        "slug": <str>
                      }
                    ],
                    "id": <int>,
                    "image_rectangle": <list[str]>,
                    "image_rectangle_mini": <list[str]>,
                    "images": <list[str]>,
                    "images150": <list[str]>,
                    "images300": <list[str]>,
                    "is_collaborative": <bool>,
                    "is_featured": <bool>,
                    "is_public": <bool>,
                    "items_focus": None,
                    "name": <str>,
                    "owner": {
                      "id": <int>,
                      "name": <str>
                    },
                    "public_at": <int>,
                    "similarPlaylist": {
                      "items": [
                        {
                          "created_at": <int>,
                          "description": <str>,
                          "duration": <int>,
                          "featured_artists": [],
                          "genres": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "path": <list[int]>,
                              "slug": <str>
                            }
                          ],
                          "id": <int>,
                          "image_rectangle": <list[str]>,
                          "image_rectangle_mini": <list[str]>,
                          "images": <list[str]>,
                          "images150": <list[str]>,
                          "images300": <list[str]>,
                          "indexed_at": <int>,
                          "is_collaborative": <bool>,
                          "is_featured": <bool>,
                          "is_public": <bool>,
                          "name": <str>,
                          "owner": {
                            "id": <int>,
                            "name": <str>
                          },
                          "public_at": <int>,
                          "slug": <str>,
                          "stores": <list[str]>,
                          "tags": [
                            {
                              "featured_tag_id": <str>,
                              "genre_tag": {
                                "genre_id": <str>,
                                "name": <str>
                              },
                              "is_discover": <bool>,
                              "name_json": <str>,
                              "slug": <str>
                            }
                          ],
                          "tracks_count": <int>,
                          "updated_at": <int>,
                          "users_count": <int>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "slug": <str>,
                    "stores": <list[str]>,
                    "tags": [
                      {
                        "color": <str>,
                        "featured_tag_id": <str>,
                        "genre_tag": {
                          "genre_id": <str>,
                          "name": <str>
                        },
                        "is_discover": <bool>,
                        "name_json": <str>,
                        "slug": <str>
                      }
                    ],
                    "timestamp_position": <int>,
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
                            "duration": <int>,
                            "genre": {
                              "color": <str>,
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
                            "maximum_technical_specifications": <str>,
                            "media_count": <int>,
                            "parental_warning": <bool>,
                            "popularity": <int>,
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
                            "tracks_count": <int>,
                            "upc": <str>,
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
                          "created_at": <int>,
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
                          "maximum_technical_specifications": <str>,
                          "media_number": <int>,
                          "parental_warning": <bool>,
                          "performer": {
                            "id": <int>,
                            "name": <str>
                          },
                          "performers": <str>,
                          "playlist_track_id": <int>,
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
                          "track_number": <int>,
                          "version": <str>,
                          "work": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "tracks_count": <int>,
                    "updated_at": <int>,
                    "users_count": <int>
                  }
        """
        self._validate_qobuz_ids(playlist_id, _recursive=False)
        params = {"playlist_id": playlist_id}
        if expand is not None:
            params["extra"] = self._prepare_expand(expand)
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "playlist/get", params=params
        ).json()

    @TTLCache.cached_method(ttl="daily")
    def get_featured_playlists(
        self,
        playlist_type: str,
        *,
        genre_ids: int | str | list[int | str] | None = None,
        playlist_tag_slugs: str | list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get featured playlists.

        Parameters
        ----------
        playlist_type : str; optional
            Type of playlists to return.

            **Valid values**:

            .. container::

               * :code:`"last-created"` – Most recently created
                 playlists.
               * :code:`"editor-picks"` – Most recently created
                 playlists by Qobuz.

        genre_ids : int, str, or list[int | str]; keyword-only; optional
            Qobuz IDs of the genres used to filter the playlists to
            return.

            **Examples**: :code:`10`, :code:`"64"`, :code:`"10,64"`,
            :code:`[10, "64"]`.

        playlist_tag_slugs : str or list[str]; keyword-only; optional
            Playlist tag slugs used to filter the playlists to return.

            **Examples**: :code:`"hi-res"`, :code:`"artist,label"`,
            :code:`["focus", "mood"]`.

            .. seealso::

               :meth:`get_playlist_tags` – Get available playlist tag
               slugs.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of Qobuz content metadata for the featured playlists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "playlists": {
                      "items": [
                        {
                          "created_at": <int>,
                          "description": <str>,
                          "duration": <int>,
                          "featured_artists": [],
                          "genres": [
                            {
                              "color": <str>,
                              "id": <int>,
                              "name": <str>,
                              "path": <list[int]>,
                              "percent": <int>,
                              "slug": <str>
                            }
                          ],
                          "id": <int>,
                          "image_rectangle": <list[str]>,
                          "image_rectangle_mini": <list[str]>,
                          "images": <list[str]>,
                          "images150": <list[str]>,
                          "images300": <list[str]>,
                          "is_collaborative": <bool>,
                          "is_featured": <bool>,
                          "is_public": <bool>,
                          "name": <str>,
                          "owner": {
                            "id": <int>,
                            "name": <str>
                          },
                          "public_at": <int>,
                          "slug": <str>,
                          "stores": <list[str]>,
                          "tags": [
                            {
                              "color": <str>,
                              "featured_tag_id": <str>,
                              "genre_tag": {
                                "genre_id": <str>,
                                "name": <str>
                              },
                              "is_discover": <bool>,
                              "name_json": <str>,
                              "slug": <str>
                            }
                          ],
                          "tracks_count": <int>,
                          "updated_at": <int>,
                          "users_count": <int>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    }
                  }
        """
        self._validate_type("playlist_type", playlist_type, str)
        playlist_type = playlist_type.strip().lower()
        if playlist_type not in {"last-created", "editor-picks"}:
            raise ValueError(
                f"Invalid playlist type {playlist_type!r}. "
                "Valid values: 'last-created', 'editor-picks'."
            )
        params = {"type": playlist_type}
        if genre_ids is not None:
            self._validate_type(
                "genre_ids", genre_ids, int | str | tuple | list | set
            )
            if not isinstance(genre_ids, int):
                if isinstance(genre_ids, str):
                    genre_ids = genre_ids.strip().split(",")
                for genre_id in genre_ids:
                    self._client.genres._validate_genre_id(genre_id)
            params["genre_ids"] = self._prepare_qobuz_ids(
                genre_ids, data_type=str
            )
        if playlist_tag_slugs is not None:
            if isinstance(playlist_tag_slugs, str):
                playlist_tag_slugs = playlist_tag_slugs.split(",")
            for playlist_tag_slug in playlist_tag_slugs:
                self._validate_playlist_tag_slug(playlist_tag_slug)
            params["tags"] = ",".join(str(slug) for slug in playlist_tag_slugs)
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "playlist/getFeatured", params=params
        ).json()

    @TTLCache.cached_method(ttl="static")
    def get_playlist_tags(self) -> dict[str, list[dict[str, Any]]]:
        """
        Get available playlist tags.

        Returns
        -------
        playlist_tags : dict[str, list[dict[str, Any]]]
            Qobuz content metadata for playlist tags.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "tags": [
                      {
                        "color": <str>,
                        "featured_tag_id": <str>,
                        "genre_tag": None,
                        "is_discover": <str>,
                        "name_json": <str>,
                        "position": <str>,
                        "slug": <str>
                      }
                    ]
                  }
        """
        return self._client._request("GET", "playlist/getTags").json()

    @TTLCache.cached_method(ttl="user")
    def get_my_playlists(
        self,
        *,
        playlist_types: str | list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for playlists created and/or
        followed by the current user.

        .. admonition:: User authentication
           :class: entitlement

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        playlist_types : str or list[str]; keyword-only; optional
            Playlist types to return.

            **Valid values**:

            .. container::

               * :code:`"owner"` – Playlists created by the user.
               * :code:`"subscriber"` – Playlists followed by the user.

            **Examples**: :code:`"owner"`, :code:`"owner,subscriber"`,
            :code:`["owner", "subscriber"]`.

            **API default**: :code:`"owner,subscriber"`.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`500`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str, keyword-only, optional
            Field to sort the playlists by.

            **Valid values**: :code:`"updated_at"`, :code:`"position"`.

            **API default**: :code:`"position"`.

        descending : bool, keyword-only, optional
            Whether to sort in descending order.

            **API default**: :code:`True`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of Qobuz content metadata for the playlists in the
            current user's collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "playlists": {
                      "items": [
                        {
                          "created_at": <int>,
                          "description": <str>,
                          "duration": <int>,
                          "featured_artists": [],
                          "genres": [
                            {
                              "color": <str>,
                              "id": <int>,
                              "name": <str>,
                              "path": <list[int]>,
                              "percent": <int>,
                              "slug": <str>
                            }
                          ],
                          "id": <int>,
                          "image_rectangle": <list[str]>,
                          "image_rectangle_mini": <list[str]>,
                          "images": <list[str]>,
                          "images150": <list[str]>,
                          "images300": <list[str]>,
                          "indexed_at": <int>,
                          "is_collaborative": <bool>,
                          "is_featured": <bool>,
                          "is_public": <bool>,
                          "is_published": <bool>,
                          "name": <str>,
                          "owner": {
                            "id": <int>,
                            "name": <str>
                          },
                          "position": <int>,
                          "public_at": <int>,
                          "published_from": <int>,
                          "published_to": <int>,
                          "slug": <str>,
                          "stores": <list[str]>,
                          "subscribed_at": <int>,
                          "timestamp_position": <int>,
                          "tracks_count": <int>,
                          "updated_at": <int>,
                          "users_count": <int>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    },
                    "user": {
                      "id": <int>,
                      "login": <str>
                    }
                  }
        """
        self._client._require_authentication("playlists.get_my_playlists")
        params = {}
        if playlist_types is not None:
            params["filter"] = self._prepare_comma_separated_values(
                "playlist type", playlist_types, self._PLAYLIST_TYPES
            )
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        if sort_by is not None:
            if sort_by not in (sort_fields := {"updated_at", "position"}):
                sort_fields_str = "', '".join(sorted(sort_fields))
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. "
                    f"Valid values: '{sort_fields_str}'."
                )
            params["order"] = sort_by
        if descending is not None:
            self._validate_type("descending", descending, bool)
            params["orderDirection"] = "desc" if descending else "asc"
        return self._client._request(
            "GET", "playlist/getUserPlaylists", params=params
        ).json()

    @_copy_docstring(PrivateSearchAPI.search_playlists)
    def search_playlists(
        self,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.search.search_playlists(
            query, limit=limit, offset=offset
        )

    @_copy_docstring(PrivateUsersAPI.follow_playlist)
    def follow_playlist(self, playlist_id: int | str, /) -> dict[str, str]:
        return self._client.users.follow_playlist(playlist_id)

    @_copy_docstring(PrivateUsersAPI.unfollow_playlist)
    def unfollow_playlist(self, playlist_id: int | str, /) -> dict[str, str]:
        return self._client.users.unfollow_playlist(playlist_id)

    def update_playlist_details(
        self,
        playlist_id: str,
        /,
        *,
        name: str | None = None,
        description: str | None = None,
        public: bool | None = None,
        collaborative: bool | None = None,
        track_ids: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Update the details of a playlist.

        .. admonition:: User authentication
           :class: entitlement

           .. tab:: Required

              User authentication
                 Access and manage your library.

        .. important::

           At least one of :code:`name`, :code:`description`,
           :code:`public`, :code:`collaborative`, or :code:`track_ids`
           must be specified.

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

        collaborative : bool; keyword-only; optional
            Whether other users can modify the playlist.

        track_ids : int, str, or list[int | str]; keyword-only; \
        optional
            Qobuz IDs of the tracks to replace those currently in the
            playlist.

            **Examples**: :code:`23929516`, :code:`"344521217"`,
            :code:`"23929516,344521217"`,
            :code:`[23929516, "344521217"]`.

        Returns
        -------
        playlist : dict[str, Any]
            Qobuz content metadata for the updated playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "created_at": <int>,
                    "description": <str>,
                    "duration": <int>,
                    "id": <int>,
                    "is_collaborative": <bool>,
                    "is_public": <bool>,
                    "name": <str>,
                    "owner": {
                      "id": <int>,
                      "name": <str>
                    },
                    "public_at": <int>,
                    "tracks_count": <int>,
                    "updated_at": <int>,
                    "users_count": <int>
                  }
        """
        self._client._require_authentication(
            "playlists.update_playlist_details"
        )
        self._validate_qobuz_ids(playlist_id, _recursive=False)
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
            payload["is_public"] = public
        if collaborative is not None:
            self._validate_type("collaborative", collaborative, bool)
            payload["is_collaborative"] = collaborative
        if track_ids is not None:
            self._validate_qobuz_ids(track_ids)
            payload["track_ids"] = self._prepare_qobuz_ids(
                track_ids, data_type=str
            )
        if not payload:
            raise ValueError("At least one change must be specified.")
        payload["playlist_id"] = playlist_id
        return self._client._request(
            "POST", "playlist/update", data=payload
        ).json()

    def reorder_playlists(
        self, playlist_ids: int | str | list[int | str], /
    ) -> dict[str, str]:
        """
        Reorder playlists.

        .. admonition:: User authentication
           :class: entitlement

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        playlist_ids : int, str, or list[int | str]; positional-only
            Qobuz IDs of the playlists.

            **Examples**: :code:`2776610`, :code:`"6754150"`,
            :code:`"2776610,6754150"`, :code:`[2776610, "6754150"]`.

        Returns
        -------
        response : dict[str, str]
            API JSON response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        self._client._require_authentication("playlists.reorder_playlists")
        return self._client._request(
            "POST",
            "playlist/updatePlaylistsPosition",
            data={
                "playlist_ids": self._prepare_qobuz_ids(
                    playlist_ids, data_type=str
                )
            },
        ).json()

    def reorder_playlist_items(
        self,
        playlist_id: int | str,
        /,
        playlist_track_ids: int | str | list[int | str],
        to_index: int,
    ) -> dict[str, Any]:
        """
        Reorder items in a playlist.

        .. admonition:: User authentication
           :class: entitlement

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        playlist_id : int or str; positional-only
            Qobuz ID of the playlist.

            **Examples**: :code:`2776610`, :code:`"6754150"`.

        playlist_track_ids : int, str, or list[int | str]
            Playlist track IDs of the tracks to be reordered.

            **Examples**: :code:`3775131234`, :code:`"3775131243"`,
            :code:`"3775131234,3775131243"`,
            :code:`[3775131234, "3775131243"]`.

            .. seealso::

               :meth:`get_playlist` – Get playlist track IDs by
               including :code:`"tracks"` in the `expand` parameter.

        to_index : int
            Zero-based index at which to insert the items.

        Returns
        -------
        playlist : dict[str, Any]
            Qobuz content metadata for the updated playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "created_at": <int>,
                    "description": <str>,
                    "duration": <int>,
                    "id": <int>,
                    "is_collaborative": <bool>,
                    "is_public": <bool>,
                    "name": <str>,
                    "owner": {
                      "id": <int>,
                      "name": <str>
                    },
                    "public_at": <int>,
                    "tracks_count": <int>,
                    "updated_at": <int>,
                    "users_count": <int>
                  }
        """
        self._client._require_authentication(
            "playlists.reorder_playlist_items"
        )
        self._validate_qobuz_ids(playlist_id, _recursive=False)
        self._validate_number("to_index", to_index, int, 0)
        return self._client._request(
            "POST",
            "playlist/updateTracksPosition",
            data={
                "playlist_id": playlist_id,
                "playlist_track_ids": self._prepare_qobuz_ids(
                    playlist_track_ids, str
                ),
                "insert_before": to_index,
            },
        ).json()
