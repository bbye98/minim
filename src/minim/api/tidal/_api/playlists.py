from collections.abc import Collection
from typing import TYPE_CHECKING, Any, Optional

from ..._shared import TTLCache
from ._shared import TIDALResourceAPI

if TYPE_CHECKING:
    from .. import TIDALAPI


class PlaylistsAPI(TIDALResourceAPI):
    """
    Playlists API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _ITEM_TYPES = {"tracks", "videos"}
    _RESOURCES = {"coverArt", "items", "owners"}
    _SORTS = {"createdAt", "lastModifiedAt", "name"}
    _client: "TIDALAPI"

    def get_playlists(
        self,
        playlist_uuids: str | Collection[str] | None = None,
        /,
        *,
        owner_ids: int | str | Collection[int | str] | None = None,
        country_code: str | None = None,
        include: str | Collection[str] | None = None,
        cursor: str | None = None,
        sort: str | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Single Playlist <https://tidal-music.github.io
        /tidal-api-reference/#/playlists/get_playlists__id_>`_: Get 
        TIDAL catalog information for a single playlist․
        `Playlists > Get Multiple Playlists 
        <https://tidal-music.github.io/tidal-api-reference/#/playlists
        /get_playlists>`_: Get TIDAL catalog information for multiple 
        playlists.

        .. admonition:: User authentication and authorization scope
           :class: authorization-scope

           .. tab:: Conditional

              :code:`playlists.read` scope
                 Read a user's playlists.

           .. tab:: Optional

              User authentication
                 Access information on an item's owners.

        Parameters
        ----------
        playlist_uuids : str or Collection[str], positional-only, \
        optional
            UUIDs of the TIDAL playlists, provided either as a string or
            a collection of strings.

            .. note::

               Exactly one of `playlist_uuids` or `owner_ids` must be 
               provided.

            **Examples**: 
            :code:`"550e8400-e29b-41d4-a716-446655440000"`,
            :code:`["550e8400-e29b-41d4-a716-446655440000"]`.

        owner_ids : int, str, or Collection[int | str], keyword-only, \
        optional
            TIDAL IDs of the playlists' owners, provided either as an 
            integer, a string, or a collection of integers and/or 
            strings.

            .. note::

               Exactly one of `playlist_uuids` or `owner_ids` must be 
               provided. When this parameter is specified, the request
               will always be sent to the endpoint for multiple
               playlists.

            **Examples**: :code:`123456`, :code:`"123456"`, 
            :code:`["123456"]`.

        country_code : str, keyword-only, optional
            ISO 3166-1 alpha-2 country code. Only optional when the 
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : str or Collection[str], keyword-only, optional
            Related resources to include in the response.

            **Valid values**: :code:`"coverArt"`, :code:`"items"`, 
            :code:`"owners"`.

        cursor : str, keyword-only, optional
            Cursor for pagination when requesting multiple playlists.

            **Example**: :code:`"3nI1Esi"`.

        sort : str, keyword-only, optional
            Field to sort the returned playlists by. Values are sorted
            in descending order with the :code:`-` prefix and in
            ascending order without.
        
            **Valid values**: :code:`"createdAt"`, :code:`"-createdAt`,
            :code:`"lastModifiedAt`, :code:`"-lastModifiedAt"`,
            :code:`"name"`, :code:`"-name"`.

        Returns
        -------
        playlists : dict[str, Any]
            TIDAL content metadata for the playlists.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single playlist

                  .. code::

                     {
                       "data": {
                         "attributes": {
                           "accessType": <str>,
                           "bounded": <bool>,
                           "createdAt": <str>,
                           "description": <str>,
                           "duration": <str>,
                           "externalLinks": [
                             {
                               "href": <str>,
                               "meta": {
                                 "type": <str>
                               }
                             }
                           ],
                           "lastModifiedAt": <str>,
                           "name": <str>,
                           "numberOfItems": <int>,
                           "playlistType": <str>
                         },
                         "id": <str>,
                         "relationships": {
                           "coverArt": {
                             "data": [
                               {
                                 "id": <str>,
                                 "type": "artworks"
                               }
                             ],
                             "links": {
                               "self": <str>
                             }
                           },
                           "items": {
                             "data": [
                               {
                                 "id": <str>,
                                 "meta": {
                                   "addedAt": <str>,
                                   "itemId": <str>
                                 },
                                 "type": "tracks"
                               },
                               {
                                 "id": <str>,
                                 "meta": {
                                   "addedAt": <str>,
                                   "itemId": <str>
                                 },
                                 "type": "videos"
                               }
                             ],
                             "links": {
                               "self": <str>
                             }
                           },
                           "owners": {
                             "data": [],
                             "links": {
                               "self": <str>
                             }
                           }
                         },
                         "type": "playlists"
                       },
                       "included": [
                         {
                           "attributes": {
                             "files": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "height": <int>,
                                   "width": <int>
                                 }
                               }
                             ],
                             "mediaType": "IMAGE"
                           },
                           "id": <str>,
                           "relationships": {
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "artworks"
                         },
                         {
                           "attributes": {
                             "accessType": "PUBLIC",
                             "availability": <list[str]>,
                             "copyright": {
                               "text": <str>
                             },
                             "duration": <str>,
                             "explicit": <bool>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "isrc": <str>,
                             "mediaTags": <list[str]>,
                             "popularity": <float>,
                             "spotlighted": <bool>,
                             "title": <str>,
                             "version": <str>
                           },
                           "id": <str>,
                           "relationships": {
                             "albums": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "artists": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "genres": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "lyrics": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "providers": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "radio": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "shares": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "similarTracks": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "sourceFile": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "trackStatistics": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "tracks"
                         },
                         {
                           "attributes": {
                             "availability": <list[str]>,
                             "copyright": {
                               "text": <str>
                             },
                             "duration": <str>,
                             "explicit": <bool>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "isrc": <str>,
                             "popularity": <float>,
                             "releaseDate": <str>,
                             "title": <str>
                           },
                           "id": <str>,
                           "relationships": {
                             "albums": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "artists": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "providers": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "thumbnailArt": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "videos"
                         }
                       ],
                       "links": {
                         "self": <str>
                       }
                     }

               .. tab:: Multiple playlists

                  .. code::

                     {
                       "data": [
                         {
                           "attributes": {
                             "accessType": <str>,
                             "bounded": <bool>,
                             "createdAt": <str>,
                             "description": <str>,
                             "duration": <str>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "lastModifiedAt": <str>,
                             "name": <str>,
                             "numberOfItems": <int>,
                             "playlistType": <str>
                           },
                           "id": <str>,
                           "relationships": {
                             "coverArt": {
                               "data": [
                                 {
                                   "id": <str>,
                                   "type": "artworks"
                                 }
                               ],
                               "links": {
                                 "self": <str>
                               }
                             },
                             "items": {
                               "data": [
                                 {
                                   "id": <str>,
                                   "meta": {
                                     "addedAt": <str>,
                                     "itemId": <str>
                                   },
                                   "type": "tracks"
                                 },
                                 {
                                   "id": <str>,
                                   "meta": {
                                     "addedAt": <str>,
                                     "itemId": <str>
                                   },
                                   "type": "videos"
                                 }
                               ],
                               "links": {
                                 "self": <str>
                               }
                             },
                             "owners": {
                               "data": [],
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "playlists"
                         }
                       ],
                       "included": [
                         {
                           "attributes": {
                             "files": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "height": <int>,
                                   "width": <int>
                                 }
                               }
                             ],
                             "mediaType": "IMAGE"
                           },
                           "id": <str>,
                           "relationships": {
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "artworks"
                         },
                         {
                           "attributes": {
                             "accessType": "PUBLIC",
                             "availability": <list[str]>,
                             "copyright": {
                               "text": <str>
                             },
                             "duration": <str>,
                             "explicit": <bool>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "isrc": <str>,
                             "mediaTags": <list[str]>,
                             "popularity": <float>,
                             "spotlighted": <bool>,
                             "title": <str>,
                             "version": <str>
                           },
                           "id": <str>,
                           "relationships": {
                             "albums": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "artists": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "genres": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "lyrics": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "owners": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "providers": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "radio": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "shares": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "similarTracks": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "sourceFile": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "trackStatistics": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "tracks"
                         },
                         {
                           "attributes": {
                             "availability": <list[str]>,
                             "copyright": {
                               "text": <str>
                             },
                             "duration": <str>,
                             "explicit": <bool>,
                             "externalLinks": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "type": <str>
                                 }
                               }
                             ],
                             "isrc": <str>,
                             "popularity": <float>,
                             "releaseDate": <str>,
                             "title": <str>
                           },
                           "id": <str>,
                           "relationships": {
                             "albums": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "artists": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "providers": {
                               "links": {
                                 "self": <str>
                               }
                             },
                             "thumbnailArt": {
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "videos"
                         }
                       ],
                       "links": {
                         "self": <str>
                       }
                     }
        """
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include is not None:
            params["include"] = params["include"] = self._prepare_include(
                include
            )
        if sum(arg is not None for arg in (playlist_uuids, owner_ids)) != 1:
            raise ValueError(
                "Exactly one of `playlist_uuids` or `owner_ids` must "
                "be provided."
            )
        if playlist_uuids is not None:
            if isinstance(playlist_uuids, str):
                self._client._validate_uuid(playlist_uuids)
                return self._client._request(
                    "GET", f"playlists/{playlist_uuids}", params=params
                ).json()
            for playlist_uuid in playlist_uuids:
                self._client._validate_uuid(playlist_uuid)
            params["filter[id]"] = playlist_uuids
        else:
            self._client._validate_tidal_ids(owner_ids)
            params["filter[owners.id]"] = owner_ids
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        if sort is not None:
            self._client._validate_type("sort", sort, str)
            if (sort[1:] if sort[0] == "-" else sort) not in self._SORTS:
                sorts = "', '".join(self._SORTS)
                raise ValueError(
                    f"Invalid sort field {sort!r}. Valid values: {sorts}."
                )
            params["sort"] = sort
        return self._client._request("GET", "playlists", params=params).json()

    def create_playlist(
        self,
        name: str,
        *,
        description: str | None = None,
        public: bool | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Create Playlist <https://tidal-music.github.io
        /tidal-api-reference/#/playlists/post_playlists>`_: Create a
        playlist.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`playlists.write` scope
                 Write to a user's playlists.

        Parameters
        ----------
        name : str
            Playlist name.

        description : str, keyword-only, optional
            Playlist description.

        public : bool, keyword-only, optional
            Whether the playlist is displayed on the user's profile.

            **Default**: :code:`False`.

        Returns
        -------
        playlist : dict[str, Any]
            TIDAL content metadata for the newly created playlist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": {
                      "attributes": {
                        "accessType": <str>,
                        "bounded": <bool>,
                        "createdAt": <str>,
                        "externalLinks": [
                          {
                            "href": <str>,
                            "meta": {
                              "type": "TIDAL_SHARING"
                            }
                          }
                        ],
                        "lastModifiedAt": <str>,
                        "name": <str>,
                        "playlistType": "USER"
                      },
                      "id": <str>,
                      "relationships": {
                        "coverArt": {
                          "links": {
                            "self": <str>
                          }
                        },
                        "items": {
                          "links": {
                            "self": <str>
                          }
                        },
                        "owners": {
                          "links": {
                            "self": <str>
                          }
                        }
                      },
                      "type": "playlists"
                    },
                    "links": {
                      "self": <str>
                    }
                  }
        """
        self._client._require_scopes("create_playlist", "playlists.write")
        self._client._validate_type("name", name, str)
        if not len(name):
            raise ValueError("The playlist name cannot be blank.")
        payload = {"data": {"attributes": {"name": name}, "type": "playlists"}}
        attrs = payload["data"]["attributes"]
        if description is not None:
            self._client._validate_type("description", description, str)
            attrs["description"] = description
        if public is not None:
            self._client._validate_type("public", public, bool)
            attrs["accessType"] = "PUBLIC" if public else "UNLISTED"
        return self._client._request("POST", "playlists", json=payload).json()

    def update_playlist_details(
        self,
        playlist_uuid: str,
        /,
        *,
        name: str | None = None,
        description: str | None = None,
        public: bool | None = None,
    ) -> None:
        """
        `Playlists > Update Playlist <https://tidal-music.github.io
        /tidal-api-reference/#/playlists/patch_playlists__id_>`_: Update
        the details of a playlist owned by the current user.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`playlists.write` scope
                 Write to a user's playlists.

        Parameters
        ----------
        playlist_uuid : str , positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"550e8400-e29b-41d4-a716-446655440000"`.

        name : str, keyword-only, optional
            Playlist name.

        description : str, keyword-only, optional
            Playlist description.

        public : bool, keyword-only, optional
            Whether the playlist is displayed on the user's profile.

            **Default**: :code:`False`.
        """
        self._client._require_scopes(
            "update_playlist_details", "playlists.write"
        )
        self._client._validate_uuid(playlist_uuid)
        payload = {
            "data": {
                "attributes": {},
                "id": playlist_uuid,
                "type": "playlists",
            }
        }
        attrs = payload["data"]["attributes"]
        if name is not None:
            self._client._validate_type("name", name, str)
            if not len(name):
                raise ValueError("The playlist name cannot be blank.")
            attrs["name"] = name
        if description is not None:
            self._client._validate_type("description", description, str)
            attrs["description"] = description
        if public is not None:
            self._client._validate_type("public", public, bool)
            attrs["accessType"] = "PUBLIC" if public else "UNLISTED"
        if not attrs:
            raise ValueError("At least one change must be specified.")
        self._client._request(
            "PATCH", f"playlists/{playlist_uuid}", json=payload
        )

    def delete_playlist(self, playlist_uuid: str, /) -> None:
        """
        `Playlists > Delete Playlist <https://tidal-music.github.io
        /tidal-api-reference/#/playlists/delete_playlists__id_>`_:
        Delete a playlist.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`playlists.write` scope
                 Write to a user's playlists.

        Parameters
        ----------
        playlist_uuid : str , positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"550e8400-e29b-41d4-a716-446655440000"`.
        """
        self._client._require_scopes("delete_playlist", "playlists.write")
        self._client._validate_uuid(playlist_uuid)
        self._client._request("DELETE", f"playlist/{playlist_uuid}")

    @TTLCache.cached_method(ttl="catalog")
    def get_playlist_cover_art(
        self,
        playlist_uuid: str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Playlist's Cover Art
        <https://tidal-music.github.io/tidal-api-reference/#/playlists
        /get_playlists__id__relationships_coverArt>`_: Get TIDAL
        catalog information for a playlist's cover art.

        Parameters
        ----------
        playlist_uuid : str , positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"550e8400-e29b-41d4-a716-446655440000"`.

        country_code : str, optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool, keyword-only, default: :code:`False`
            Specifies whether to include TIDAL content metadata for
            the playlist's cover art.

        cursor : str, keyword-only, optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        cover_art : dict[str, Any]
            TIDAL catalog information for the playlist's cover art.

            .. admonition:: Sample response
               :class: dropdown

               {
                 "data": [
                   {
                     "id": <str>,
                     "type": "artworks"
                   }
                 ],
                 "included": [
                   {
                     "attributes": {
                       "files": [
                         {
                           "href": <str>,
                           "meta": {
                             "height": <int>,
                             "width": <int>
                           }
                         }
                       ],
                       "mediaType": "IMAGE"
                     },
                     "id": <str>,
                     "relationships": {
                       "owners": {
                         "links": {
                           "self": <str>
                         }
                       }
                     },
                     "type": "artworks"
                   }
                 ],
                 "links": {
                   "meta": {
                     "nextCursor": <str>
                   },
                   "next": <str>,
                   "self": <str>
                 }
               }
        """
        self._client._validate_uuid(playlist_uuid)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = "coverArt"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET",
            f"playlists/{playlist_uuid}/relationships/coverArt",
            params=params,
        ).json()

    def get_playlist_items(
        self,
        playlist_uuid: str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Playlist Items
        <https://tidal-music.github.io/tidal-api-reference/#/playlists
        /get_playlists__id__relationships_coverArt>`_: Get TIDAL
        catalog information for items in a playlist.

        Parameters
        ----------
        playlist_uuid : str , positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"550e8400-e29b-41d4-a716-446655440000"`.

        country_code : str, optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool, keyword-only, default: :code:`False`
            Specifies whether to include TIDAL content metadata for
            the playlist items.

        cursor : str, keyword-only, optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        cover_art : dict[str, Any]
            TIDAL catalog information for the playlist items.

            .. admonition:: Sample response
               :class: dropdown

               {
                 "data": [
                   {
                     "id": <str>,
                     "meta": {
                       "addedAt": <int>,
                       "itemId": <int>
                     },
                     "type": "tracks"
                   },
                   {
                     "id": <str>,
                     "meta": {
                       "addedAt": <int>,
                       "itemId": <int>
                     },
                     "type": "videos"
                   }
                 ],
                 "included": [
                   {
                     "attributes": {
                       "accessType": "PUBLIC",
                       "availability": <list[str]>,
                       "copyright": {
                         "text": <str>
                       },
                       "duration": <str>,
                       "explicit": <bool>,
                       "externalLinks": [
                         {
                           "href": <str>,
                           "meta": {
                             "type": <str>
                           }
                         }
                       ],
                       "isrc": <str>,
                       "mediaTags": <list[str]>,
                       "popularity": <float>,
                       "spotlighted": <bool>,
                       "title": <str>,
                       "version": <str>
                     },
                     "id": <str>,
                     "relationships": {
                       "albums": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "artists": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "genres": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "lyrics": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "owners": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "providers": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "radio": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "shares": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "similarTracks": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "sourceFile": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "trackStatistics": {
                         "links": {
                           "self": <str>
                         }
                       }
                     },
                     "type": "tracks"
                   },
                   {
                     "attributes": {
                       "availability": <list[str]>,
                       "copyright": {
                         "text": <str>
                       },
                       "duration": <str>,
                       "explicit": <bool>,
                       "externalLinks": [
                         {
                           "href": <str>,
                           "meta": {
                             "type": <str>
                           }
                         }
                       ],
                       "isrc": <str>,
                       "popularity": <float>,
                       "releaseDate": <str>,
                       "title": <str>
                     },
                     "id": <str>,
                     "relationships": {
                       "albums": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "artists": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "providers": {
                         "links": {
                           "self": <str>
                         }
                       },
                       "thumbnailArt": {
                         "links": {
                           "self": <str>
                         }
                       }
                     },
                     "type": "videos"
                   }
                 ],
                 "links": {
                   "meta": {
                     "nextCursor": <str>
                   },
                   "next": <str>,
                   "self": <str>
                 }
               }
        """
        self._client._validate_uuid(playlist_uuid)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = "items"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET",
            f"playlists/{playlist_uuid}/relationships/items",
            params=params,
        ).json()

    def add_playlist_items(
        self,
        playlist_uuid: str,
        /,
        items: tuple[int | str, str] | Collection[tuple[int | str, str]],
        country_code: str | None = None,
        before: str | None = None,
    ) -> None:
        """
        `Playlists > Add Items to Playlist
        <https://tidal-music.github.io/tidal-api-reference/#/playlists
        /post_playlists__id__relationships_items>`_: Add items to a
        playlist owned by the current user.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`playlists.write` scope
                 Write to a user's playlists.

        Parameters
        ----------
        playlist_uuid : str , positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"550e8400-e29b-41d4-a716-446655440000"`.

        items : tuple[int | str, str] or \
        Collection[tuple[int | str, str]]
            TIDAL IDs of tracks and videos, provided as tuples of the ID
            and the item type, or as properly formatted dictionaries.

            **Examples**:

            .. container::

               * :code:`(458584456, "tracks")`
               * :code:`("29597422", "videos")`
               * :code:`{"id": "35633900", "types": "tracks"}`
               * :code:`[(458584456, "tracks"), ("29597422", "videos")]`

        country_code : str, optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        before : str, optional
            UUID of the item in the playlist before which to insert the
            items in `items`. If not specified, the items are appended 
            to the end of the playlist.

            **Example**: :code:`"3794bdb3-1529-48d7-8a99-ef2cb0cf22c3"`.
        """
        self._client._validate_uuid(playlist_uuid)
        params = {}
        if country_code is not None:
            self._client._resolve_country_code(country_code, params)
        payload = {"data": self._process_playlist_items(items, False)}
        if before is not None:
            payload["meta"] = {"positionBefore": before}
        self._client._request(
            "POST",
            f"playlists/{playlist_uuid}/relationships/items",
            params=params,
            json=payload,
        )

    def update_playlist_items(self) -> None: ...

    def remove_playlist_items(
        self,
        playlist_uuid: str,
        /,
        items: tuple[int | str, str, str]
        | Collection[tuple[int | str, str, str]],
    ) -> None: ...

    @TTLCache.cached_method(ttl="catalog")
    def get_playlist_owners(
        self,
        playlist_uuid: str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Playlists > Get Playlist's Owners
        <https://tidal-music.github.io/tidal-api-reference/#/playlists
        /get_playlists__id__relationships_owners>`_: Get TIDAL
        catalog information for an playlist's owners.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Optional

              User authentication
                 Access information on an item's owners.

        Parameters
        ----------
        playlist_uuid : str , positional-only
            UUID of the TIDAL playlist.

            **Example**: :code:`"550e8400-e29b-41d4-a716-446655440000"`.

        country_code : str, optional
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : bool, keyword-only, default: :code:`False`
            Specifies whether to include TIDAL content metadata for
            the playlist's owners.

        cursor : str, keyword-only, optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        owners : dict[str, Any]
            TIDAL catalog information for the playlist's owners.

            .. admonition:: Sample response
               :class: dropdown

               {
                 "data": [],
                 "included": [],
                 "links": {
                   "meta": {
                     "nextCursor": <str>
                   },
                   "next": <str>,
                   "self": <str>
                 }
               }
        """
        self._client._validate_uuid(playlist_uuid)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = "owners"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET",
            f"playlists/{playlist_uuid}/relationships/owners",
            params=params,
        ).json()

    @classmethod
    def _process_playlist_items(
        cls,
        items: tuple[int | str, str]
        | tuple[int | str, str, str]
        | dict[str, Any]
        | Collection[
            tuple[int | str, str] | tuple[int | str, str, str] | dict[str, Any]
        ],
        meta: bool = True,
        _recursive: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Process user-specified items to add to, update in, or remove
        from a playlist.

        Parameters
        ----------
        items : tuple[int | str, ...], dict[str, Any], or \
        Collection[tuple[int | str, ...] | dict[str, Any]]
            TIDAL IDs (and UUIDs) of tracks and videos, provided as
            tuples of the ID (and UUID) and the item type, or as
            properly formatted dictionaries.

        meta : bool, default: :code:`True`
            Specifies whether the items have UUID information.

        Returns
        -------
        items : list[dict[str, Any]]
            List of properly formatted dictionaries containing
            information for the tracks and videos.
        """
        if isinstance(items, dict):
            item_id = items.get("id")
            item_type = items.get("type")
            if meta:
                item_uuid = items.get("meta", {}).get("itemId")
        else:
            if isinstance(items[0], dict | list | tuple):
                if not 0 < len(items) <= 20:
                    raise ValueError(
                        "Between 1 and 20 items can be sent in a request."
                    )
                return [
                    cls._process_playlist_items(
                        item, meta=meta, _recursive=False
                    )
                    for item in items
                ]
            item_id, *item_uuid, item_type = items
            if meta:
                item_uuid = item_uuid[0]
        if item_type not in cls._ITEM_TYPES:
            item_types = "', '".join(cls._ITEM_TYPES)
            raise ValueError(
                f"Invalid item type {item_type!r}. Valid values: '{item_types}'."
            )
        item = {"id": str(item_id), "type": item_type}
        if meta:
            item["meta"] = {"itemId": item_uuid}
        if _recursive:
            return [item]
        return item
