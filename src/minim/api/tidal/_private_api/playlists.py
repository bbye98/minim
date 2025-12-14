from typing import TYPE_CHECKING, Any

from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class PrivatePlaylistsAPI(ResourceAPI):
    """
    Playlists API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _SORTS = {"DATE", "NAME"}
    _client: "PrivateTIDALAPI"

    @classmethod
    def _validate_filters(cls, filters: str | list[str], /) -> None:
        """
        Validate one or more playlist types to filter by.

        Parameters
        ----------
        filters : str or list[str]; positional-only; optional
            Playlist types to include in the results.
        """
        if not filters:
            raise ValueError("At least one playlist type must be specified.")

        if isinstance(filters, str):
            cls._validate_filters(filters.split(","))
        elif isinstance(filters, tuple | list):
            for filter in filters:
                if filter not in cls._FILTERS:
                    _filters = "', '".join(cls._FILTERS)
                    raise ValueError(
                        f"Invalid playlist type {filter!r}. "
                        f"Valid values: '{_filters}'."
                    )
        else:
            raise TypeError(
                "`filter_by` must be a comma-separated string or a "
                "list of strings."
            )

    def get_playlist(
        self,
        playlist_uuid: str,
        /,
        *,
        country_code: str | None = None,
        version: int = 2,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a playlist.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Conditional

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        playlist_uuid : str; positional-only
            Playlist UUID.

            **Example**: :code:`"0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used. Only
            applicable when :code:`version=1`.

            **Example**: :code:`"US"`.

        version : int; keyword-only; default: :code:`2`
            Selects which version of the private TIDAL API to use.

            **Valid values**:

            .. container::

               * :code:`1` – legacy
                 :code:`GET v1/playlists/{playlist_uuid}` endpoint.
               * :code:`2` – current
                 :code:`GET v2/user-playlists/{playlist_uuid}` endpoint.

        Returns
        -------
        playlist : dict[str, Any]
            TIDAL catalog information for the playlist.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Current (:code:`v2`) endpoint

                  .. code::

                     {
                       "followInfo": {
                         "followType": "PLAYLIST",
                         "followed": <bool>,
                         "nrOfFollowers": <int>,
                         "tidalResourceName": <str>
                       },
                       "playlist": {
                         "contentBehavior": <str>,
                         "created": <str>,
                         "creator": {
                           "id": <int>,
                           "name": <str>,
                           "picture": <str>,
                           "type": "USER"
                         },
                         "curators": [
                           {
                             "handle": <str>,
                             "id": <int>,
                             "name": <str>,
                             "picture": <str>
                           }
                         ],
                         "customImageUrl": <str>,
                         "description": <str>,
                         "duration": <int>,
                         "image": <str>,
                         "lastItemAddedAt": <str>,
                         "lastUpdated": <str>,
                         "numberOfTracks": <int>,
                         "numberOfVideos": <int>,
                         "promotedArtists": [
                           {
                             "contributionLinkUrl": <str>,
                             "handle": <str>,
                             "id": <int>,
                             "name": <str>,
                             "picture": <str>,
                             "type": <str>,
                             "userId": <int>
                           }
                         ],
                         "sharingLevel": "PUBLIC",
                         "source": <str>,
                         "squareImage": <str>,
                         "status": <str>,
                         "title": <str>,
                         "trn": <str>,
                         "type": "USER",
                         "url": <str>,
                         "uuid": <str>
                       },
                       "profile": {
                         "color": <list[str]>,
                         "name": <str>,
                         "userId": <int>
                       }
                     }

               .. tab:: Legacy (:code:`v1`) endpoint

                  .. code::

                     {
                       "created": <str>,
                       "creator": {
                         "id": <int>
                       },
                       "customImageUrl": <str>,
                       "description": <str>,
                       "duration": <int>,
                       "image": <str>,
                       "lastItemAddedAt": <str>,
                       "lastUpdated": <str>,
                       "numberOfTracks": <int>,
                       "numberOfVideos": <int>,
                       "popularity": <int>,
                       "promotedArtists": [
                         {
                           "handle": <str>,
                           "id": <int>,
                           "name": <str>,
                           "picture": <str>,
                           "type": <str>
                         }
                       ],
                       "publicPlaylist": <bool>,
                       "squareImage": <str>,
                       "title": <str>,
                       "type": <str>,
                       "url": <str>,
                       "uuid": <str>
                     }
        """
        self._client._validate_uuid(playlist_uuid)
        self._client._validate_number("version", version, int, 1, 2)
        if version == 1:
            if country_code is None:
                country_code = self._client._my_country_code
            else:
                self._client._validate_country_code(country_code)
            return self._client._request(
                "GET",
                f"v1/playlists/{playlist_uuid}",
                params={"countryCode": country_code},
            ).json()
        self._client._require_authentication("playlists.get_playlist")
        return self._client._request(
            "GET", f"v2/user-playlists/{playlist_uuid}"
        ).json()

    def get_playlist_items(
        self,
        playlist_uuid: str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for tracks and videos in a
        playlist.

        Parameters
        ----------
        playlist_uuid : str; positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"36ea71a8-445e-41a4-82ab-6628c581535d"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next set of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        items : dict[str, Any]
            Pages of TIDAL catalog information for the tracks and videos
            in the playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "cut": <Any>,
                        "item": {
                          "accessType": <str>,
                          "adSupportedStreamReady": <bool>,
                          "album": {
                            "cover": <str>,
                            "id": <int>,
                            "releaseDate": <str>,
                            "title": <str>,
                            "vibrantColor": <str>,
                            "videoCover": <str>
                          },
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": <str>,
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "artists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "audioModes": <list[str]>,
                          "audioQuality": <str>,
                          "bpm": <int>,
                          "copyright": <str>,
                          "dateAdded": <str>,
                          "description": <str>,
                          "djReady": <bool>,
                          "duration": <int>,
                          "editable": <bool>,
                          "explicit": <bool>,
                          "id": <int>,
                          "index": <int>,
                          "isrc": <str>,
                          "itemUuid": <str>,
                          "key": <str>,
                          "keyScale": <str>,
                          "mediaMetadata": {
                            "tags": <list[str]>
                          },
                          "mixes": {
                            "TRACK_MIX": <str>
                          },
                          "payToStream": <bool>,
                          "peak": <float>,
                          "popularity": <int>,
                          "premiumStreamingOnly": <bool>,
                          "replayGain": <float>,
                          "spotlighted": <bool>,
                          "stemReady": <bool>,
                          "streamReady": <bool>,
                          "streamStartDate": <str>,
                          "title": <str>,
                          "trackNumber": <int>,
                          "upload": <bool>,
                          "url": <str>,
                          "version": <str>,
                          "volumeNumber": <int>
                        },
                        "type": "track"
                      },
                      {
                        "cut": <Any>,
                        "item": {
                          "adSupportedStreamReady": <bool>,
                          "adsPrePaywallOnly": <bool>,
                          "adsUrl": <str>,
                          "album": {
                            "cover": <str>,
                            "id": <int>,
                            "title": <str>,
                            "vibrantColor": <str>,
                            "videoCover": <str>
                          },
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": <str>,
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "artists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "dateAdded": <str>,
                          "djReady": <bool>,
                          "duration": <int>,
                          "explicit": <bool>,
                          "id": <int>,
                          "imageId": <str>,
                          "imagePath": <str>,
                          "index": <int>,
                          "itemUuid": <str>,
                          "popularity": <int>,
                          "quality": <str>,
                          "releaseDate": <str>,
                          "stemReady": <bool>,
                          "streamReady": <bool>,
                          "streamStartDate": <str>,
                          "title": <str>,
                          "trackNumber": <int>,
                          "type": <str>,
                          "vibrantColor": <str>,
                          "volumeNumber": <int>
                        },
                        "type": "video"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._validate_uuid(playlist_uuid)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"v1/playlists/{playlist_uuid}/items", params=params
        ).json()

    def get_playlist_recommended_tracks(
        self,
        playlist_uuid: str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for tracks recommended based on a
        given playlist.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        playlist_uuid : str; positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"36ea71a8-445e-41a4-82ab-6628c581535d"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next set of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        tracks : dict[str, Any]
            Pages of TIDAL catalog information for the recommended
            tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "item": {
                          "accessType": <str>,
                          "adSupportedStreamReady": <bool>,
                          "album": {
                            "cover": <str>,
                            "id": <int>,
                            "releaseDate": <str>,
                            "title": <str>,
                            "url": <str>,
                            "vibrantColor": <str>,
                            "videoCover": <str>
                          },
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": <str>,
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "artists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "audioModes": <list[str]>,
                          "audioQuality": <str>,
                          "copyright": <str>,
                          "description": <str>,
                          "djReady": <bool>,
                          "doublePopularity": <float>,
                          "duration": <int>,
                          "editable": <bool>,
                          "explicit": <bool>,
                          "id": <int>,
                          "isrc": <str>,
                          "mediaMetadata": {
                            "tags": <list[str]>
                          },
                          "mixes": {
                            "TRACK_MIX": <str>
                          },
                          "payToStream": <bool>,
                          "peak": <float>,
                          "popularity": <int>,
                          "premiumStreamingOnly": <bool>,
                          "replayGain": <float>,
                          "spotlighted": <bool>,
                          "stemReady": <bool>,
                          "streamReady": <bool>,
                          "streamStartDate": <str>,
                          "title": <str>,
                          "trackNumber": <int>,
                          "upload": <bool>,
                          "url": <str>,
                          "version": <str>,
                          "volumeNumber": <int>
                        },
                        "type": "track"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication(
            "playlists.get_playlist_recommended_tracks"
        )
        self._client._validate_uuid(playlist_uuid)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET",
            f"v1/playlists/{playlist_uuid}/recommendations/items",
            params=params,
        ).json()

    def create_folder(
        self, name: str, *, folder_uuid: str | None = None
    ) -> dict[str, Any]:
        """
        Create a playlist folder.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        name : str
            Playlist folder name.

            **Example**: :code:`"My New Playlist Folder Title"`.

        folder_uuid : str; keyword-only; optional
            UUID of TIDAL playlist folder to add the new playlist folder
            to. Use :code:`"root"` or leave blank to target the
            top-level "Playlists" folder.

        Returns
        -------
        folder : dict[str, Any]
            TIDAL content metadata for the newly created playlist
            folder.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "addedAt": <str>,
                    "data": {
                      "createdAt": <str>,
                      "id": <str>,
                      "itemType": "FOLDER",
                      "lastModifiedAt": <str>,
                      "name": <str>,
                      "totalNumberOfItems": <int>,
                      "trn": <str>
                    },
                    "itemType": "FOLDER",
                    "lastModifiedAt": <str>,
                    "name": <str>,
                    "parent": {
                      "id": <str>,
                      "name": <str>
                    },
                    "trn": <str>
                  }
        """
        self._client._require_authentication("playlists.create_folder")
        self._client._validate_type("name", name, str)
        if not len(name):
            raise ValueError("The playlist folder name cannot be blank.")
        params = {"name": name}
        if folder_uuid is not None:
            if folder_uuid != "root":
                self._client._validate_uuid(folder_uuid)
            params["folderId"] = folder_uuid
        return self._client._request(
            "PUT",
            "v2/my-collection/playlists/folders/create-folder",
            params=params,
        ).json()

    def delete_folders(self, folder_uuids: str | list[str], /) -> None:
        """
        Delete playlist folders.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        folder_uuids : str; positional-only
            UUIDs or TIDAL resource names of the playlist folders,
            provided as either a comma-separated string or a list of
            strings.

            **Examples**:

            .. container::

               * :code:`"trn:folder:618ff600-dce1-4326-8724-9f0a51f63439"`
               * :code:`"trn:folder:618ff600-dce1-4326-8724-9f0a51f63439,550e8400-e29b-41d4-a716-446655440000"`
               * .. code::

                    [
                        "trn:folder:618ff600-dce1-4326-8724-9f0a51f63439",
                        "550e8400-e29b-41d4-a716-446655440000",
                    ]
        """
        return self._delete_resources("folder", folder_uuids)

    def create_playlist(
        self,
        name: str,
        *,
        description: str | None = None,
        public: bool | None = None,
        folder_uuid: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a playlist.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        name : str
            Playlist name.

            **Example**: :code:`"My New Playlist Title"`.

        description : str; keyword-only; optional
            Playlist description.

        public : bool; keyword-only; optional
            Whether the playlist is displayed on the user's profile.

            **API default**: :code:`False`.

        folder_uuid : str; keyword-only; optional
            UUID of TIDAL playlist folder to add the new playlist to.
            Use :code:`"root"` or leave blank to target the top-level
            "Playlists" folder.

        Returns
        -------
        playlist : dict[str, Any]
            TIDAL content metadata for the newly created playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "addedAt": <str>,
                    "data": {
                      "contentBehavior": <str>,
                      "created": <str>,
                      "creator": {
                        "id": <int>,
                        "name": <str>,
                        "picture": <str>,
                        "type": "USER"
                      },
                      "curators": [
                        {
                          "handle": <str>,
                          "id": <int>,
                          "name": <str>,
                          "picture": <str>
                        }
                      ],
                      "customImageUrl": <str>,
                      "description": <str>,
                      "duration": 0,
                      "image": <str>,
                      "itemType": "PLAYLIST",
                      "lastItemAddedAt": <str>,
                      "lastUpdated": <str>,
                      "numberOfTracks": 0,
                      "numberOfVideos": 0,
                      "promotedArtists": [
                        {
                          "handle": <str>,
                          "id": <int>,
                          "name": <str>,
                          "picture": <str>,
                          "type": <str>
                        }
                      ],
                      "sharingLevel": <str>,
                      "source": "DEFAULT",
                      "squareImage": <str>,
                      "status": "READY",
                      "title": <str>,
                      "trn": <str>,
                      "type": "USER",
                      "url": <str>,
                      "uuid": <str>
                    },
                    "itemType": "PLAYLIST",
                    "lastModifiedAt": <str>,
                    "name": <str>,
                    "parent": {
                      "id": <str>,
                      "name": <str>
                    },
                    "trn": <str>
                  }
        """
        self._client._require_authentication("playlists.create_playlist")
        self._client._validate_type("name", name, str)
        if not len(name):
            raise ValueError("The playlist name cannot be blank.")
        params = {"name": name}
        if description is not None:
            self._client._validate_type("description", description, str)
            params["description"] = description
        if public is not None:
            self._client._validate_type("public", public, bool)
            params["isPublic"] = public
        if folder_uuid is not None:
            if folder_uuid != "root":
                self._client._validate_uuid(folder_uuid)
            params["folderId"] = folder_uuid
        return self._client._request(
            "PUT",
            "v2/my-collection/playlists/folders/create-playlist",
            params=params,
        ).json()

    def move_playlists(
        self,
        playlist_uuids: str | list[str],
        /,
        folder_uuid: str | None = None,
    ) -> None:
        """
        Move playlists in the current user's collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        playlist_uuids : str or list[str]; positional-only; optional
            Playlist UUIDs, provided as either a comma-separated string
            or a list of strings. TIDAL resource names may be provided
            only when :code:`version=2`.

            **Examples**:

            .. container::

               * :code:`"trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`
               * :code:`"trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861,24c9cc46-2fcd-4afb-bcc6-d6c42315f32e"`
               * .. code::

                    [
                        "trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861",
                        "24c9cc46-2fcd-4afb-bcc6-d6c42315f32e",
                    ]

        folder_uuid : str; keyword-only; optional
            UUID of TIDAL playlist folder to add playlists to. Use
            :code:`"root"` or leave blank to target the top-level
            "Playlists" folder.
        """
        self._client._require_authentication("playlists.move_playlists")
        params = {
            "trns": self._client._prepare_uuids(
                "playlist", playlist_uuids, prefix=True
            ),
        }
        if folder_uuid is not None:
            if folder_uuid != "root":
                self._client._validate_uuid(folder_uuid)
            params["folderId"] = folder_uuid
        self._client._request(
            "PUT", "v2/my-collection/playlists/folders/move", params=params
        )

    def set_playlist_visibility(
        self, playlist_uuid: str, /, public: bool
    ) -> None:
        """
        Set the visibility of a playlist owned by the current user.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        playlist_uuid : str; positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"36ea71a8-445e-41a4-82ab-6628c581535d"`.

        public : bool
            Whether the playlist is displayed on the user's profile.
        """
        self._client._require_authentication("playlists.set_playlist_privacy")
        self._client._validate_uuid(playlist_uuid)
        self._client._request(
            "PUT",
            f"v2/playlists/{playlist_uuid}/set-"
            f"{'public' if public else 'private'}",
        )

    def update_playlist_details(
        self,
        playlist_uuid: str,
        /,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        """
        Update the details of a playlist owned by the current user.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        playlist_uuid : str; positional-only; optional
            Playlist UUID.

            **Example**: :code:`"0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`.
        """
        self._client._require_authentication(
            "playlists.update_playlist_details"
        )
        self._client._validate_uuid(playlist_uuid)
        payload = {}
        if name is not None:
            self._client._validate_type("name", name, str)
            if not len(name):
                raise ValueError("The playlist name cannot be blank.")
            payload["title"] = name
        if description is not None:
            self._client._validate_type("description", description, str)
            payload["description"] = description
        if not payload:
            raise ValueError("At least one change must be specified.")
        self._client._request(
            "POST", f"v1/playlists/{playlist_uuid}", data=payload
        )

    def delete_playlists(self, playlist_uuids: str | list[str], /) -> None:
        """
        Delete playlists.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        playlist_uuids : str; positional-only
            UUIDs or TIDAL resource names of the playlists, provided as
            either a comma-separated string or a list of
            strings.

            **Examples**:

            .. container::

               * :code:`"trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`
               * :code:`"trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861,24c9cc46-2fcd-4afb-bcc6-d6c42315f32e"`
               * .. code::

                    [
                        "trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861",
                        "24c9cc46-2fcd-4afb-bcc6-d6c42315f32e",
                    ]
        """
        return self._delete_resources("playlist", playlist_uuids)

    def add_playlist_items(
        self,
        playlist_uuid: str,
        /,
        country_code: str | None = None,
        *,
        track_ids: int | str | list[int | str] | None = None,
        from_album_id: int | str | None = None,
        from_playlist_uuid: str | None = None,
        on_duplicate: str | None = None,
    ) -> None:
        """ """
        self._client._require_authentication("playlists.add_playlist_items")
        data = {}
        if on_duplicate is not None:
            if on_duplicate not in {"ADD", "FAIL", "SKIP"}:
                raise ValueError(
                    "Invalid duplicate-handling behavior "
                    f"{on_duplicate!r}. Valid values: ..."
                )
            data["onDupes"] = on_duplicate
        self._client._request(
            "POST",
            f"v1/playlists/{playlist_uuid}/items",
            headers={
                "If-None-Match": self._get_playlist_etag(
                    playlist_uuid, country_code=country_code
                )
            },
        )

    def reorder_playlist_items(self) -> None:
        """ """
        ...

    def replace_playlist_items(self) -> None:
        """ """
        ...

    def remove_playlist_items(self) -> None:
        """ """
        ...

    def get_my_playlists(
        self,
        *,
        limit: int = 50,
        cursor: str | None = None,
        filter_by: str | list[str] | None = None,
        sort_by: str | None = None,
        reverse: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for playlists in the current
        user's collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        limit : int; keyword-only; default: :code:`50`
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        filter_by : str or list[str]; keyword-only; optional
            Playlist types to include in the results, provided as either
            a comma-separated string or a list of strings. If not
            specified, all playlists are returned.

            **Valid values**:

            .. container::

               * :code:`"FOLDER"` – Playlist folders.
               * :code:`"PLAYLIST"` – All playlists.
               * :code:`"FAVORITE_PLAYLIST"` – Favorited playlists.
               * :code:`"USER_PLAYLIST"` – User-created playlists.

            **Examples**: :code:`"USER_PLAYLIST"`,
            :code:`"FOLDER,USER_PLAYLIST"`,
            :code:`["FOLDER", "USER_PLAYLIST"]`.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**:

            .. container::

               * :code:`"DATE"` - Date added.
               * :code:`"NAME"` - Playlist name.

            **API default**: :code:`"DATE"`.

        reverse : bool; keyword-only; optional
            Whether to reverse the sort order from ascending to
            descending.

            **API default**: :code:`False`.

        Returns
        -------
        playlists : dict[str, Any]
            TIDAL content metadata for the playlists in the current
            user's collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "cursor": <str>,
                    "items": [
                      {
                        "addedAt": <str>,
                        "data": {
                          "createdAt": <str>,
                          "id": <str>,
                          "itemType": "FOLDER",
                          "lastModifiedAt": <str>,
                          "name": <str>,
                          "totalNumberOfItems": <int>,
                          "trn": <str>,
                        },
                        "itemType": "FOLDER",
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "parent": {
                          "id": <str>,
                          "name": <str>
                        },
                        "trn": <str>,
                      },
                      {
                        "addedAt": <str>,
                        "data": {
                          "contentBehavior": <str>,
                          "created": <str>,
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "curators": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>
                            }
                          ],
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "itemType": "PLAYLIST",
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": 1,
                          "numberOfVideos": 1,
                          "promotedArtists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>
                            }
                          ],
                          "sharingLevel": <str>,
                          "source": <str>,
                          "squareImage": <str>,
                          "status": <str>,
                          "title": <str>,
                          "trn": <str>,
                          "type": <str>,
                          "url": <str>,
                          "uuid": <str>
                        },
                        "itemType": "PLAYLIST",
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "parent": {
                          "id": <str>,
                          "name": <str>
                        },
                        "trn": <str>
                      }
                    ],
                    "lastModifiedAt": <str>
                  }
        """
        self._client._require_authentication("playlists.get_my_playlists")
        self._client._validate_number("limit", limit, int, 1, 50)
        params = {"limit": limit}
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        if filter_by is not None:
            self._validate_filters(filter_by)
            params["includeOnly"] = filter_by
        if sort_by is not None:
            if sort_by not in self._SORTS:
                sorts = "', '".join(sorted(self._SORTS))
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. Valid values: '{sorts}'."
                )
            params["order"] = sort_by
        if reverse is not None:
            self._client._validate_type("reverse", reverse, bool)
            params["orderDirection"] = "DESC" if reverse else "ASC"
        return self._client._request(
            "GET", "v2/my-collection/playlists", params=params
        ).json()

    def get_my_folder(
        self,
        folder_uuid: str | None = None,
        /,
        *,
        limit: int = 50,
        cursor: str | None = None,
        filter_by: str | list[str] | None = None,
        sort_by: str | None = None,
        reverse: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for playlists in a playlist folder
        in the current user's collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        folder_uuid : str; positional-only; optional
            UUID of TIDAL playlist folder to retrieve playlists from.
            Use :code:`"root"` or leave blank to target the top-level
            "Playlists" folder.

        limit : int; keyword-only; default: :code:`50`
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        filter_by : str or list[str]; keyword-only; optional
            Playlist types to include in the results, provided as either
            a comma-separated string or a list of strings. If not
            specified, all playlists are returned.

            **Valid values**:

            .. container::

               * :code:`"FOLDER"` – Playlist folders.
               * :code:`"PLAYLIST"` – All playlists.
               * :code:`"FAVORITE_PLAYLIST"` – Favorited playlists.
               * :code:`"USER_PLAYLIST"` – User-created playlists.

            **Examples**: :code:`"USER_PLAYLIST"`,
            :code:`"FOLDER,USER_PLAYLIST"`,
            :code:`["FOLDER", "USER_PLAYLIST"]`.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**:

            .. container::

               * :code:`"DATE"` - Date added.
               * :code:`"NAME"` - Playlist name.

            **API default**: :code:`"DATE"`.

        reverse : bool; keyword-only; optional
            Whether to reverse the sort order from ascending to
            descending.

            **API default**: :code:`False`.

        Returns
        -------
        playlists : dict[str, Any]
            TIDAL content metadata for the playlists in the playlist
            folder in the current user's collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "cursor": <str>,
                    "items": [
                      {
                        "addedAt": <str>,
                        "data": {
                          "createdAt": <str>,
                          "id": <str>,
                          "itemType": "FOLDER",
                          "lastModifiedAt": <str>,
                          "name": <str>,
                          "totalNumberOfItems": <int>,
                          "trn": <str>,
                        },
                        "itemType": "FOLDER",
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "parent": {
                          "id": <str>,
                          "name": <str>
                        },
                        "trn": <str>,
                      },
                      {
                        "addedAt": <str>,
                        "data": {
                          "contentBehavior": <str>,
                          "created": <str>,
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "curators": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>
                            }
                          ],
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "itemType": "PLAYLIST",
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": 1,
                          "numberOfVideos": 1,
                          "promotedArtists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>
                            }
                          ],
                          "sharingLevel": <str>,
                          "source": <str>,
                          "squareImage": <str>,
                          "status": <str>,
                          "title": <str>,
                          "trn": <str>,
                          "type": <str>,
                          "url": <str>,
                          "uuid": <str>
                        },
                        "itemType": "PLAYLIST",
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "parent": {
                          "id": <str>,
                          "name": <str>
                        },
                        "trn": <str>
                      }
                    ],
                    "lastModifiedAt": <str>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("playlists.get_my_folder")
        self._client._validate_number("limit", limit, int, 1, 50)
        params = {"limit": limit}
        if folder_uuid is not None:
            if folder_uuid != "root":
                self._client._validate_uuid(folder_uuid)
            params["folderId"] = folder_uuid
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        if filter_by is not None:
            self._validate_filters(filter_by)
            params["includeOnly"] = filter_by
        if sort_by is not None:
            if sort_by not in self._SORTS:
                sorts = "', '".join(sorted(self._SORTS))
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. Valid values: '{sorts}'."
                )
            params["order"] = sort_by
        if reverse is not None:
            self._client._validate_type("reverse", reverse, bool)
            params["orderDirection"] = "DESC" if reverse else "ASC"
        return self._client._request(
            "GET", "v2/my-collection/playlists/folders", params=params
        )

    def get_my_folders_and_playlists(
        self,
        *,
        limit: int = 50,
        cursor: str | None = None,
        filter_by: str | list[str] | None = None,
        sort_by: str | None = None,
        reverse: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for all playlist folders and
        playlists in the current user's collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        limit : int; keyword-only; default: :code:`50`
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`50`.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        filter_by : str or list[str]; keyword-only; optional
            Playlist types to include in the results, provided as either
            a comma-separated string or a list of strings. If not
            specified, all playlists are returned.

            **Valid values**:

            .. container::

               * :code:`"FOLDER"` – Playlist folders.
               * :code:`"PLAYLIST"` – All playlists.
               * :code:`"FAVORITE_PLAYLIST"` – Favorited playlists.
               * :code:`"USER_PLAYLIST"` – User-created playlists.

            **Examples**: :code:`"USER_PLAYLIST"`,
            :code:`"FOLDER,USER_PLAYLIST"`,
            :code:`["FOLDER", "USER_PLAYLIST"]`.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**:

            .. container::

               * :code:`"DATE"` - Date added.
               * :code:`"NAME"` - Playlist name.

            **API default**: :code:`"DATE"`.

        reverse : bool; keyword-only; optional
            Whether to reverse the sort order from ascending to
            descending.

            **API default**: :code:`False`.

        Returns
        -------
        playlists : dict[str, Any]
            TIDAL content metadata for the playlist folders and
            playlists in the current user's collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "cursor": <str>,
                    "items": [
                      {
                        "addedAt": <str>,
                        "data": {
                          "createdAt": <str>,
                          "id": <str>,
                          "itemType": "FOLDER",
                          "lastModifiedAt": <str>,
                          "name": <str>,
                          "totalNumberOfItems": <int>,
                          "trn": <str>,
                        },
                        "itemType": "FOLDER",
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "parent": {
                          "id": <str>,
                          "name": <str>
                        },
                        "trn": <str>,
                      },
                      {
                        "addedAt": <str>,
                        "data": {
                          "contentBehavior": <str>,
                          "created": <str>,
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "curators": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>
                            }
                          ],
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "itemType": "PLAYLIST",
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": 1,
                          "numberOfVideos": 1,
                          "promotedArtists": [
                            {
                              "id": <int>,
                              "name": <str>,
                              "type": <str>
                            }
                          ],
                          "sharingLevel": <str>,
                          "source": <str>,
                          "squareImage": <str>,
                          "status": <str>,
                          "title": <str>,
                          "trn": <str>,
                          "type": <str>,
                          "url": <str>,
                          "uuid": <str>
                        },
                        "itemType": "PLAYLIST",
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "parent": {
                          "id": <str>,
                          "name": <str>
                        },
                        "trn": <str>
                      }
                    ],
                    "lastModifiedAt": <str>,
                  }
        """
        self._client._require_authentication(
            "users.get_my_folders_and_playlists"
        )
        self._client._validate_number("limit", limit, int, 1, 50)
        params = {"limit": limit}
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        if filter_by is not None:
            self._validate_filters(filter_by)
            params["includeOnly"] = filter_by
        if sort_by is not None:
            if sort_by not in self._SORTS:
                sorts = "', '".join(sorted(self._SORTS))
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. Valid values: '{sorts}'."
                )
            params["order"] = sort_by
        if reverse is not None:
            self._client._validate_type("reverse", reverse, bool)
            params["orderDirection"] = "DESC" if reverse else "ASC"
        return self._client._request(
            "GET",
            "v2/my-collection/playlists/folders/flattened",
            params=params,
        )

    def get_user_playlists(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        reverse: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for editorial and user-created
        playlists in a user's collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next set of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**:

            .. container::

               * :code:`"DATE"` - Date added.
               * :code:`"NAME"` - Playlist name.

            **API default**: :code:`"DATE"`.

        reverse : bool; keyword-only; optional
            Whether to reverse the sort order from ascending to
            descending.

            **API default**: :code:`False`.

        Returns
        -------
        playlists : dict[str, Any]
            TIDAL catalog information for editorial and user-created
            playlists in the user's collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created": <str>,
                        "playlist": {
                          "created": <str>,
                          "creator": {
                            "id": <int>
                          },
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos":<int>,
                          "popularity": <int>,
                          "promotedArtists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "publicPlaylist": <bool>,
                          "squareImage": <str>,
                          "title": <str>,
                          "type": <str>,
                          "url": <str>,
                          "uuid": <str>
                        },
                        "type": "USER_CREATED"
                      },
                      {
                        "created": <str>,
                        "playlist": {
                          "created": <str>,
                          "creator": {
                            "id": <int>
                          },
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos":<int>,
                          "popularity": <int>,
                          "promotedArtists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "publicPlaylist": <bool>,
                          "squareImage": <str>,
                          "title": <str>,
                          "type": <str>,
                          "url": <str>,
                          "uuid": <str>
                        },
                        "type": "USER_FAVORITE"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication("playlists.get_user_playlists")
        if user_id is None:
            user_id = self._client._get_user_identifier()
        params = {}
        self._client._resolve_country_code(country_code, params)
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        if sort_by is not None:
            if sort_by not in self._SORTS:
                sorts = "', '".join(sorted(self._SORTS))
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. Valid values: '{sorts}'."
                )
            params["order"] = sort_by
        if reverse is not None:
            self._client._validate_type("reverse", reverse, bool)
            params["orderDirection"] = "DESC" if reverse else "ASC"
        return self._client._request(
            "GET",
            f"v1/users/{user_id}/playlistsAndFavoritePlaylists",
            params=params,
        ).json()

    def get_user_created_playlists(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for user-created playlists in a
        user's collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to
            get the next set of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        playlists : dict[str, Any]
            TIDAL catalog information for user-created playlists in the
            user's collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created": <str>,
                        "playlist": {
                          "created": <str>,
                          "creator": {
                            "id": <int>
                          },
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos":<int>,
                          "popularity": <int>,
                          "promotedArtists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "publicPlaylist": <bool>,
                          "squareImage": <str>,
                          "title": <str>,
                          "type": <str>,
                          "url": <str>,
                          "uuid": <str>
                        },
                        "type": "USER_CREATED"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        self._client._require_authentication(
            "users.get_user_created_playlists"
        )
        if user_id is None:
            user_id = self._client._get_user_identifier()
        params = {}
        self._client._resolve_country_code(country_code, params)
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 10_000)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"v1/users/{user_id}/playlists", params=params
        ).json()

    def get_user_public_playlists(
        self,
        user_id: int | str | None = None,
        /,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for public playlists in a user's
        collection.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access user recommendations, and view and modify user's
                 collection.

        Parameters
        ----------
        user_id : int or str; positional-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Valid range**: :code:`1` to :code:`10_000`.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

        Returns
        -------
        playlists : dict[str, Any]
            TIDAL content metadata for the public playlists in a user's
            collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "cursor": <str>,
                    "items": [
                      {
                        "followInfo": {
                          "followType": "PLAYLIST",
                          "followed": <bool>,
                          "nrOfFollowers": <int>,
                          "tidalResourceName": <str>
                        },
                        "playlist": {
                          "contentBehavior": <str>,
                          "created": <str>,
                          "creator": {
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": "USER"
                          },
                          "curators": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>
                            }
                          ],
                          "customImageUrl": <str>,
                          "description": <str>,
                          "duration": <int>,
                          "image": <str>,
                          "lastItemAddedAt": <str>,
                          "lastUpdated": <str>,
                          "numberOfTracks": <int>,
                          "numberOfVideos": <int>,
                          "promotedArtists": [
                            {
                              "contributionLinkUrl": <str>,
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>,
                              "userId": <int>
                            }
                          ],
                          "sharingLevel": "PUBLIC",
                          "source": <str>,
                          "squareImage": <str>,
                          "status": <str>,
                          "title": <str>,
                          "trn": <str>,
                          "type": "USER",
                          "url": <str>,
                          "uuid": <str>
                        },
                        "profile": {
                          "color": <list[str]>,
                          "name": <str>,
                          "userId": <int>
                        }
                      }
                    ]
                  }
        """
        self._client._require_authentication(
            "playlists.get_user_public_playlists"
        )
        if user_id is None:
            user_id = self._client._get_user_identifier()
        params = {}
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET", f"v2/user-playlists/{user_id}/public", params=params
        ).json()

    def _delete_resources(
        self, resource: str, uuids: str | list[str], /
    ) -> None:
        """
        Delete playlist folders or playlists.

        Parameters
        ----------
        resource : str; positional-only
            Resource type.

            **Valid values**: :code:`"folder"`, :code:`"playlist"`.

        uuids : str or list[str]; positional-only
            UUIDs of playlists or playlist folders.
        """
        self._client._require_authentication(f"users.delete_{resource}s")
        self._client._request(
            "PUT",
            "v2/my-collection/playlists/folders/remove",
            params={
                "trns": self._client._prepare_uuids(
                    resource, uuids, prefix=True
                )
            },
        )

    def _get_playlist_etag(
        self, playlist_uuid: str, /, country_code: str | None = None
    ) -> str:
        """ """
        self._client._validate_uuid(playlist_uuid)
        if country_code is None:
            country_code = self._client._my_country_code
        else:
            self._client._validate_country_code(country_code)
        return (
            self._client._request(
                "GET",
                f"v1/playlists/{playlist_uuid}",
                params={"countryCode": country_code},
            )
            .headers["ETag"]
            .replace('"', "")
        )
