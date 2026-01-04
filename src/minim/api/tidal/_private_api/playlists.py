from typing import TYPE_CHECKING, Any

from ..._shared import ResourceAPI, _copy_docstring
from .users import PrivateUsersAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class PrivatePlaylistsAPI(ResourceAPI):
    """
    Playlists API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _PLAYLIST_TYPES = {
        "FOLDER",
        "PLAYLIST",
        "FAVORITE_PLAYLIST",
        "USER_PLAYLIST",
    }
    _SORT_FIELDS = {"DATE", "NAME"}
    _client: "PrivateTIDALAPI"

    @classmethod
    def _validate_types(cls, playlist_types: str | list[str], /) -> None:
        """
        Validate one or more playlist types to filter by.

        Parameters
        ----------
        playlist_types : str or list[str]; positional-only; optional
            Playlist types to return.
        """
        if not playlist_types:
            raise ValueError("At least one playlist type must be specified.")

        if isinstance(playlist_types, str):
            cls._validate_types(playlist_types.split(","))
        elif isinstance(playlist_types, tuple | list):
            for playlist_type in playlist_types:
                if playlist_type not in cls._PLAYLIST_TYPES:
                    playlist_types_str = "', '".join(cls._PLAYLIST_TYPES)
                    raise ValueError(
                        f"Invalid playlist type {playlist_type!r}. "
                        f"Valid values: '{playlist_types_str}'."
                    )
        else:
            raise TypeError(
                "`playlist_types` must be a comma-separated string or "
                "a list of strings."
            )

    def get_playlist(
        self,
        playlist_uuid: str,
        /,
        *,
        country_code: str | None = None,
        api_version: int = 2,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a playlist.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Conditional

              User authentication
                 Access and manage the user's collection.

        Parameters
        ----------
        playlist_uuid : str; positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used. Only applicable when :code:`version=1`.

            **Example**: :code:`"US"`.

        api_version : int; keyword-only; default: :code:`2`
            Private TIDAL API version.

            **Valid values**:

            .. container::

               * :code:`1` – legacy
                 :code:`GET v1/playlists/{playlist_uuid}` endpoint.
               * :code:`2` – current
                 :code:`GET v2/user-playlists/{playlist_uuid}` endpoint.

        Returns
        -------
        playlist : dict[str, Any]
            TIDAL content metadata for the playlist.

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
        self._client._validate_number("version", api_version, int, 1, 2)
        if api_version == 1:
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
            country associated with the current user account or IP
            address is used.

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
            Page of TIDAL content metadata for the tracks and videos in
            the playlist.

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
                 Access and manage the user's collection.

        Parameters
        ----------
        playlist_uuid : str; positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"36ea71a8-445e-41a4-82ab-6628c581535d"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

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
            Page of TIDAL content metadata for the recommended tracks.

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
                 Access and manage the user's collection.

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
                 Access and manage the user's collection.

        Parameters
        ----------
        folder_uuids : str; positional-only
            UUIDs or TIDAL resource names of the playlist folders.

            **Examples**:

            .. container::

               * :code:`"trn:folder:618ff600-dce1-4326-8724-9f0a51f63439"`
               * :code:`"trn:folder:618ff600-dce1-4326-8724-9f0a51f63439,550e8400-e29b-41d4-a716-446655440000"`
               * :code:`["trn:folder:618ff600-dce1-4326-8724-9f0a51f63439",
                 "550e8400-e29b-41d4-a716-446655440000"]`
        """
        self._client._require_authentication("users.delete_folders")
        self._client._request(
            "PUT",
            "v2/my-collection/playlists/folders/remove",
            params={
                "trns": self._client._prepare_uuids(
                    "folder", folder_uuids, has_prefix=True
                )
            },
        )

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
                 Access and manage the user's collection.

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
                 Access and manage the user's collection.

        Parameters
        ----------
        playlist_uuids : str or list[str]; positional-only
            UUIDs or TIDAL resource names of the playlists.

            **Examples**:

            .. container::

               * :code:`"trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`
               * :code:`"trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861,24c9cc46-2fcd-4afb-bcc6-d6c42315f32e"`
               * :code:`["trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861",
                 "24c9cc46-2fcd-4afb-bcc6-d6c42315f32e"]`

        folder_uuid : str
            UUID of TIDAL playlist folder to move playlists to. Use
            :code:`"root"` or leave blank to target the top-level
            "Playlists" folder.
        """
        self._client._require_authentication("playlists.move_playlists")
        params = {
            "trns": self._client._prepare_uuids(
                "playlist", playlist_uuids, has_prefix=True
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
        Set the visibility of a playlist.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage the user's collection.

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
        Update the details of a playlist.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage the user's collection.

        Parameters
        ----------
        playlist_uuid : str; positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`.

        name : str; keyword-only; optional
            New playlist name.

        description : str; keyword-only; optional
            New playlist description.
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
                 Access and manage the user's collection.

        Parameters
        ----------
        playlist_uuids : str; positional-only
            UUIDs or TIDAL resource names of the playlists.

            **Examples**:

            .. container::

               * :code:`"trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`
               * :code:`"trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861,24c9cc46-2fcd-4afb-bcc6-d6c42315f32e"`
               * :code:`["trn:playlist:0ae80812-f8d6-4fc4-90ea-b2df4ecc3861",
                 "24c9cc46-2fcd-4afb-bcc6-d6c42315f32e"]`
        """
        self._client._require_authentication("users.delete_playlists")
        self._client._request(
            "PUT",
            "v2/my-collection/playlists/folders/remove",
            params={
                "trns": self._client._prepare_uuids(
                    "playlist", playlist_uuids, has_prefix=True
                )
            },
        )

    def add_playlist_items(
        self,
        playlist_uuid: str,
        /,
        country_code: str | None = None,
        *,
        item_ids: int | str | list[int | str] | None = None,
        from_album_id: int | str | None = None,
        from_playlist_uuid: str | None = None,
        on_duplicate: str | None = None,
    ) -> None:
        """
        Add items to a playlist.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage the user's collection.

        .. note::

           Exactly one of `item_ids`, `from_album_id`, or
           `from_playlist_uuid` must be provided.

        Parameters
        ----------
        playlist_uuid : str; positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        item_ids : int, str, or list[int | str]; keyword-only; optional
            TIDAL IDs of the tracks and videos.

            **Examples**: :code:`46369325`, :code:`"75413016"`,
            :code:`"46369325,75413016"`, :code:`[46369325, "75413016"]`.

        from_album_id : int or str; keyword-only; optional
            TIDAL ID of the album to add tracks and videos from.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        from_playlist_uuid : str; keyword-only; optional
            UUID of the TIDAL playlist to add tracks and videos
            from.

            **Example**: :code:`"0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`.

        on_duplicate : str; keyword-only; optional
            Behavior when the items to be added are already in the
            playlist.

            **Valid values**: :code:`"ADD"`, :code:`"FAIL"`,
            :code:`"SKIP"`.
        """
        self._client._require_authentication("playlists.add_playlist_items")
        data = {}
        if (
            sum(
                arg is not None
                for arg in (item_ids, from_album_id, from_playlist_uuid)
            )
            != 1
        ):
            raise ValueError(
                "Exactly one of `item_ids`, `from_album_id`, or "
                "`from_playlist_uuid` must be specified."
            )
        if item_ids is not None:
            if isinstance(item_ids, str) and "," in item_ids:
                item_ids = item_ids.split(",")
            self._client._validate_tidal_ids(item_ids)
            if isinstance(item_ids, tuple | list):
                item_ids = ",".join(str(item_id) for item_id in item_ids)
            data["itemIds"] = str(item_ids)
        elif from_album_id is not None:
            self._client._validate_tidal_ids(from_album_id, _recursive=False)
            data["fromAlbumId"] = from_album_id
        else:
            self._client._validate_uuid(from_playlist_uuid)
            data["fromPlaylistUuid"] = from_playlist_uuid
        if on_duplicate is not None:
            if on_duplicate not in (options := {"ADD", "FAIL", "SKIP"}):
                _options = "', '".join(options)
                raise ValueError(
                    "Invalid duplicate-handling behavior "
                    f"{on_duplicate!r}. Valid values: '{_options}'."
                )
            data["onDupes"] = on_duplicate
        self._client._request(
            "POST",
            f"v1/playlists/{playlist_uuid}/items",
            data=data,
            headers={
                "If-None-Match": self._get_playlist_etag(
                    playlist_uuid, country_code=country_code
                )
            },
        )

    def reorder_playlist_items(
        self,
        playlist_uuid: str,
        /,
        from_item_indices: int | str | list[int | str],
        to_index: int | str,
        country_code: str | None = None,
    ) -> None:
        """
        Reorder items in a playlist.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage the user's collection.

        Parameters
        ----------
        playlist_uuid : str; positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`.

        from_item_indices : int, str, or list[int | str]
            Zero-based indices of items to move.

            **Examples**: :code:`1`, :code:`"2"`, :code:`"3,4"`,
            :code:`[5, "6"]`.

        to_index : int or str
            Zero-based index to move the items to.

            **Examples**: :code:`0`, :code:`"0"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.
        """
        self._client._require_authentication(
            "playlists.reorder_playlist_items"
        )
        if isinstance(from_item_indices, str) and "," in from_item_indices:
            from_item_indices = from_item_indices.split(",")
        self._client._validate_tidal_ids(from_item_indices)
        if isinstance(from_item_indices, tuple | list):
            from_item_indices = ",".join(
                str(item_idx) for item_idx in from_item_indices
            )
        self._client._validate_number("to_index", to_index, int, 0)
        self._client._request(
            "POST",
            f"v1/playlists/{playlist_uuid}/items/{from_item_indices}",
            params={"toIndex": to_index},
            headers={
                "If-None-Match": self._get_playlist_etag(
                    playlist_uuid, country_code=country_code
                )
            },
        )

    def replace_playlist_item(
        self,
        playlist_uuid: str,
        /,
        item_index: int | str,
        item_id: int | str,
        country_code: str | None = None,
    ) -> None:
        """
        Replace an item in a playlist with another item.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage the user's collection.

        Parameters
        ----------
        playlist_uuid : str; positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`.

        item_index : int or str
            Zero-based index of the item to be replaced.

             **Examples**: :code:`1`, :code:`"2"`.

        item_id : int or str
            TIDAL ID of the track or video to replace the item at the
            specified index.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.
        """
        self._client._require_authentication(
            "playlists.replace_playlist_items"
        )
        self._client._validate_number("item_index", item_index, int, 0)
        self._client._validate_tidal_ids(item_id)
        self._client._request(
            "POST",
            f"v1/playlists/{playlist_uuid}/items/{item_index}/replace",
            data={"itemId": item_id},
            headers={
                "If-None-Match": self._get_playlist_etag(
                    playlist_uuid, country_code=country_code
                )
            },
        )

    def remove_playlist_items(
        self,
        playlist_uuid: str,
        /,
        item_indices: int | str | list[int | str],
        country_code: str | None = None,
    ) -> None:
        """
        Remove items from a playlist.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage the user's collection.

        Parameters
        ----------
        playlist_uuid : str; positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"0ae80812-f8d6-4fc4-90ea-b2df4ecc3861"`.

        item_indices : int, str, or list[int | str]
            Zero-based indices of items to remove.

            **Examples**: :code:`1`, :code:`"2"`, :code:`"3,4"`,
            :code:`[5, "6"]`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.
        """
        self._client._require_authentication("playlists.remove_playlist_items")
        if isinstance(item_indices, str) and "," in item_indices:
            item_indices = item_indices.split(",")
        self._client._validate_tidal_ids(item_indices)
        if isinstance(item_indices, tuple | list):
            item_indices = ",".join(str(item_idx) for item_idx in item_indices)
        self._client._request(
            "DELETE",
            f"v1/playlists/{playlist_uuid}/items/{item_indices}",
            headers={
                "If-None-Match": self._get_playlist_etag(
                    playlist_uuid, country_code=country_code
                )
            },
        )

    @_copy_docstring(PrivateUsersAPI.get_favorite_playlists)
    def get_favorite_playlists(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_favorite_playlists(
            user_id,
            country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @_copy_docstring(PrivateUsersAPI.favorite_playlists)
    def favorite_playlists(
        self,
        playlist_uuids: str | list[str],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        folder_uuid: str | None = None,
        api_version: int = 2,
    ) -> None:
        self._client.users.favorite_playlists(
            playlist_uuids,
            user_id=user_id,
            country_code=country_code,
            folder_uuid=folder_uuid,
            api_version=api_version,
        )

    @_copy_docstring(PrivateUsersAPI.unfavorite_playlists)
    def unfavorite_playlists(
        self,
        playlist_uuids: str | list[str],
        /,
        *,
        user_id: int | str | None = None,
        api_version: int = 2,
    ) -> None:
        self._client.users.unfavorite_playlists(
            playlist_uuids, user_id=user_id, api_version=api_version
        )

    @_copy_docstring(PrivateUsersAPI.get_my_playlists)
    def get_my_playlists(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        playlist_types: str | list[str] | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_my_playlists(
            cursor=cursor,
            limit=limit,
            playlist_types=playlist_types,
            sort_by=sort_by,
            descending=descending,
        )

    @_copy_docstring(PrivateUsersAPI.get_my_folder)
    def get_my_folder(
        self,
        folder_uuid: str | None = None,
        /,
        *,
        cursor: str | None = None,
        limit: int = 50,
        playlist_types: str | list[str] | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_my_folder(
            folder_uuid,
            cursor=cursor,
            limit=limit,
            playlist_types=playlist_types,
            sort_by=sort_by,
            descending=descending,
        )

    @_copy_docstring(PrivateUsersAPI.get_my_folders_and_playlists)
    def get_my_folders_and_playlists(
        self,
        *,
        cursor: str | None = None,
        limit: int = 50,
        playlist_types: str | list[str] | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_my_folders_and_playlists(
            cursor=cursor,
            limit=limit,
            playlist_types=playlist_types,
            sort_by=sort_by,
            descending=descending,
        )

    @_copy_docstring(PrivateUsersAPI.get_user_playlists)
    def get_user_playlists(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_user_playlists(
            user_id,
            country_code=country_code,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @_copy_docstring(PrivateUsersAPI.get_user_created_playlists)
    def get_user_created_playlists(
        self,
        user_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_user_created_playlists(
            user_id, country_code=country_code, limit=limit, offset=offset
        )

    @_copy_docstring(PrivateUsersAPI.get_user_public_playlists)
    def get_user_public_playlists(
        self,
        user_id: int | str | None = None,
        /,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_user_public_playlists(
            user_id, cursor=cursor, limit=limit
        )

    def _get_playlist_etag(
        self, playlist_uuid: str, /, country_code: str | None = None
    ) -> str:
        """
        Get the entity tag (ETag) for a TIDAL playlist.

        Parameters
        ----------
        playlist_uuid : str; positional-only
            UUID of the TIDAL playlist.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

        Returns
        -------
        etag : str
            ETag for the playlist.

            **Example**: :code:`"1765846447570"`.
        """
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
