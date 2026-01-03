from typing import Any

from ._shared import PrivateQobuzResourceAPI


class PrivatePlaylistsAPI(PrivateQobuzResourceAPI):
    """
    Playlists API endpoints for the private Qobuz API.

    .. important::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    _RELATIONSHIPS = {"tracks", "getSimilarPlaylists", "focus", "focusAll"}

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
           :class: authorization-scope

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
        self._client._validate_qobuz_ids(playlist_id, _recursive=False)
        params = {
            "playlist_id": playlist_id,
            "track_ids": self._client._prepare_qobuz_ids(track_ids, str),
        }
        if allow_duplicates is not None:
            self._client._validate_type(
                "allow_duplicates", allow_duplicates, bool
            )
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
           :class: authorization-scope

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

        from_track_ids : int, str, or list[int | str]; keyword-only;
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
        self._client._validate_type("name", name, str)
        if not len(name):
            raise ValueError("The playlist name cannot be blank.")
        payload = {"name": name}
        if description is not None:
            self._client._validate_type("description", description, str)
            payload["description"] = description
        if public is not None:
            self._client._validate_type("public", public, bool)
            payload["public"] = public
        if collaborative is not None:
            self._client._validate_type("collaborative", collaborative, bool)
            payload["collaborative"] = collaborative
        if from_album_id is not None:
            self._client._validate_type("from_album_id", from_album_id, str)
            if not from_album_id.isalnum():
                raise ValueError(
                    f"Album ID {from_album_id!r} is not alphanumeric."
                )
            payload["album_id"] = from_album_id
        if from_track_ids is not None:
            self._client._validate_qobuz_ids(from_track_ids)
            payload["track_ids"] = self._client._prepare_qobuz_ids(
                from_track_ids, str
            )
        return self._client._request(
            "POST", "playlist/create", data=payload
        ).json()

    def delete_playlist(self, playlist_id: int | str, /) -> dict[str, Any]:
        """
        Delete a playlist.

        .. admonition:: User authentication
           :class: authorization-scope

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
            API response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        self._client._require_authentication("playlists.delete_playlist")
        self._client._validate_qobuz_ids(playlist_id, _recursive=False)
        return self._client._request(
            "POST", "playlist/delete", data={"playlist_id": playlist_id}
        )

    def remove_playlist_tracks(
        self,
        playlist_id: int | str,
        /,
        playlist_track_ids: int | str | list[int, str],
    ) -> dict[str, Any]:
        """
        Remove tracks from a playlist.

        .. admonition:: User authentication
           :class: authorization-scope

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
            :code:`[3775131234, "3775131243"]`.

            .. seealso::

               :meth:`get_playlist` – Get playlist track IDs by
               including :code:`"tracks"` in the `expand` parameter.

        Returns
        -------
        response : dict[str, str]
            API response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        self._client._require_authentication(
            "playlists.remove_playlist_tracks"
        )
        self._client._validate_qobuz_ids(playlist_id, _recursive=False)
        return self._client._request(
            "POST",
            "playlist/deleteTracks",
            data={
                "playlist_id": playlist_id,
                "playlist_track_ids": self._client._prepare_qobuz_ids(
                    playlist_track_ids, str
                ),
            },
        ).json()

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

            .. admonition:: Sample responses
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
        self._client._require_authentication("playlists.get_playlist")
        self._client._validate_qobuz_ids(playlist_id, _recursive=False)
        params = {"playlist_id": playlist_id}
        if expand is not None:
            params["extra"] = self._prepare_expand(expand)
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "playlist/get", params=params
        ).json()

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

                  TODO
        """
        self._client._validate_type("playlist_type", playlist_type, str)
        playlist_type = playlist_type.strip().lower()
        if playlist_type not in {"last-created", "editor-picks"}:
            raise ValueError(
                f"Invalid playlist type {playlist_type!r}. "
                "Valid values: 'last-created', 'editor-picks'."
            )
        params = {"type": playlist_type}
        if genre_ids is not None:
            self._client._validate_type(
                "genre_ids", genre_ids, int | str | tuple | list | set
            )
            if not isinstance(genre_ids, int):
                if isinstance(genre_ids, str):
                    genre_ids = genre_ids.split(",")
                for genre_id in genre_ids:
                    self._client._validate_genre_id(genre_id)
            params["genre_ids"] = self._client._prepare_qobuz_ids(
                genre_ids, str
            )
        if playlist_tag_slugs is not None:
            ...  # TODO
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "playlist/getFeatured", params=params
        ).json()

    def get_playlist_tags(self) -> dict[str, list[dict[str, Any]]]:
        """
        Get available playlist tags.

        Returns
        -------
        playlist_tags : dict[str, list[dict[str, Any]]]
            Qobuz content metadata for playlist tags.

            .. admonition:: Sample responses
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

    def get_user_playlists(self):
        pass

    def search_playlists(self):
        pass

    def follow_playlist(self):
        pass

    def unfollow_playlist(self):
        pass

    def update_playlist_details(self):
        pass

    def reorder_playlists(self):
        pass

    def reorder_playlist_items(self):
        pass
