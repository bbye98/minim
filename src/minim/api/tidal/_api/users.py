from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache
from ._shared import TIDALResourceAPI

if TYPE_CHECKING:
    from .. import TIDALAPI


class UsersAPI(TIDALResourceAPI):
    """
    User Collections, User Entitlements, User Recommendations, and Users
    API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _COLLECTION_RELATIONSHIPS = {
        "albums",
        "artists",
        "owners",
        "playlists",
        "tracks",
        "videos",
    }
    _RECOMMENDATION_RELATIONSHIPS = {
        "discoveryMixes",
        "myMixes",
        "newArrivalMixes",
    }
    _client: "TIDALAPI"

    @classmethod
    def _prepare_resource_identifiers(
        cls,
        resource_type: str,
        resource_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        _recursive: bool = True,
    ) -> list[dict[str, str]]:
        """
        Normalize, validate, and prepare a list of resource identifiers.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"owners"`, :code:`"playlists"`, :code:`"tracks"`,
            :code:`"videos"`.

        resource_ids : str, dict[str, int | str], or \
        list[int | str | dict[str, int | str]]; positional-only
            TIDAL IDs or UUIDs of the items.

        Returns
        -------
        resource_identifiers : list[dict[str, str]]
            List of resource identifiers.
        """
        if isinstance(resource_ids, dict):
            resource_id = resource_ids.get("id")
            if resource_ids.get("type") != resource_type:
                raise ValueError(
                    f"The item with ID {resource_id!r} is not a "
                    f"{resource_type[:-1]}."
                )
        elif isinstance(resource_ids, int | str):
            resource_id = resource_ids
        else:
            num_resources = len(resource_ids)
            if not num_resources:
                raise ValueError(
                    f"At least one {resource_type[:-1]} must be specified."
                )
            if num_resources > 20:
                raise ValueError(
                    f"A maximum of 20 {resource_type} can be sent in a request."
                )
            return [
                cls._prepare_resource_identifiers(
                    resource_id, _recursive=False
                )
                for resource_id in resource_ids
            ]
        resource_identifier = {"id": str(resource_id), "type": resource_type}
        if _recursive:
            return [resource_identifier]
        return resource_identifier

    def get_collection(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        expand: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """
        `User Collections > Get User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections/get_userCollections__id_>`_: Get a TIDAL user's
        collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.read` scope
                 Read access to a user's collection.

        Parameters
        ----------
        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

        expand : str or list[str]; keyword-only; optional
            Related resources to include metadata for in the response.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"owners"`, :code:`"playlists"`, :code:`"tracks"`,
            :code:`"videos"`.

        Returns
        -------
        collection : dict[str, Any]
            TIDAL content metadata for the items in the current user's
            collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": {
                      "attributes": {},
                      "id": <str>,
                      "relationships": {
                        "albums": {
                          "data": [
                            {
                              "id": <str>,
                              "meta": {
                                "addedAt": <str>
                              },
                              "type": "albums"
                            }
                          ],
                          "links": {
                            "self": <str>
                          }
                        },
                        "artists": {
                          "data": [
                            {
                              "id": <str>,
                              "meta": {
                                "addedAt": <str>
                              },
                              "type": "artists"
                            }
                          ],
                          "links": {
                            "self": <str>
                          }
                        },
                        "owners": {
                          "data": [
                            {
                              "id": <str>,
                              "type": "users"
                            }
                          ],
                          "links": {
                            "self": <str>
                          }
                        },
                        "playlists": {
                          "data": [
                            {
                              "id": <str>,
                              "meta": {
                                "addedAt": <str>
                              },
                              "type": "playlists"
                            }
                          ],
                          "links": {
                            "self": <str>
                          }
                        },
                        "tracks": {
                          "data": [
                            {
                              "id": <str>,
                              "meta": {
                                "addedAt": <str>
                              },
                              "type": "tracks"
                            }
                          ],
                          "links": {
                            "self": <str>
                          }
                        },
                        "videos": {
                          "data": [
                            {
                              "id": <str>,
                              "meta": {
                                "addedAt": <str>
                              },
                              "type": "videos"
                            }
                          ],
                          "links": {
                            "self": <str>
                          }
                        }
                      },
                      "type": "userCollections"
                    },
                    "included": [
                      {
                        "attributes": {
                          "accessType": <str>,
                          "availability": <list[str]>,
                          "barcodeId": <str>,
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
                          "mediaTags": <list[str]>,
                          "numberOfItems": <int>,
                          "numberOfVolumes": <int>,
                          "popularity": <float>,
                          "releaseDate": <str>,
                          "title": <str>,
                          "type": "ALBUM"
                        },
                        "id": <str>,
                        "relationships": {
                          "artists": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "coverArt": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "genres": {
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
                          },
                          "providers": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "similarAlbums": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "suggestedCoverArts" : {
                            "links": {
                              "self": <str>
                            }
                          }
                        },
                        "type": "albums"
                      },
                      {
                        "attributes": {
                          "contributionsEnabled": <bool>,
                          "externalLinks": [
                            {
                              "href": <str>,
                              "meta": {
                                "type": <str>
                              }
                            }
                          ],
                          "name": <str>,
                          "popularity": <float>,
                          "spotlighted": <bool>
                        },
                        "id": <str>,
                        "relationships": {
                          "albums": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "biography": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "followers": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "following": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "owners": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "profileArt": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "radio": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "roles": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "similarArtists": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "trackProviders": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "tracks": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "videos": {
                            "links": {
                              "self": <str>
                            }
                          }
                        },
                        "type": "artists"
                      },
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
                      {
                        "attributes": {
                          "accessType": <str>,
                          "availability": <list[str]>,
                          "bpm": <float>,
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
                          "key": <str>,
                          "keyScale": <str>,
                          "mediaTags": <list[str]>,
                          "popularity": <float>,
                          "spotlighted": <bool>,
                          "title": <str>,
                          "toneTags": <list[str]>,
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
                          "country": <str>,
                          "email": <str>,
                          "emailVerified": <bool>,
                          "firstName": <str>,
                          "username": <str>
                        },
                        "id": <str>,
                        "type": "users"
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
                          "popularity": <float>
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
        self._client._require_scopes("users.get_collection", "collection.read")
        if user_id is None:
            user_id = self._client._my_profile["id"]
        else:
            self._client._validate_tidal_ids(user_id, _recursive=False)
        self._get_resources(
            "userCollections",
            user_id,
            country_code=country_code,
            locale=locale,
            expand=expand,
        )

    def get_favorite_albums(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        `User Collections > Get Albums in User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /get_userCollections__id__relationships_albums>`_: Get TIDAL
        catalog information for albums in a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.read` scope
                 Read access to a user's collection.

        Parameters
        ----------
        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the albums in
            the user's collection.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        sort_by : str; keyword-only; optional
            Field to sort the albums by.

            **Valid values**: :code:`"addedAt"`, :code:`"artists.name`,
            :code:`"releaseDate"`, :code:`"title"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        albums : dict[str, Any]
            TIDAL content metadata for the albums in the user's
            collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "meta": {
                          "addedAt": <str>
                        },
                        "type": "albums"
                      }
                    ],
                    "included": [
                      {
                        "attributes": {
                          "accessType": <str>,
                          "availability": <list[str]>,
                          "barcodeId": <str>,
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
                          "mediaTags": <list[str]>,
                          "numberOfItems": <int>,
                          "numberOfVolumes": <int>,
                          "popularity": <float>,
                          "releaseDate": <str>,
                          "title": <str>,
                          "type": "ALBUM"
                        },
                        "id": <str>,
                        "relationships": {
                          "artists": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "coverArt": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "genres": {
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
                          },
                          "providers": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "similarAlbums": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "suggestedCoverArts" : {
                            "links": {
                              "self": <str>
                            }
                          }
                        },
                        "type": "albums"
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
        self._client._require_scopes(
            "users.get_favorite_albums", "collection.read"
        )
        return self._get_collection_relationship(
            "albums",
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include=include_metadata,
            cursor=cursor,
            sort_by=sort_by,
            descending=descending,
            sort_fields={"addedAt", "artists.name", "releaseDate", "title"},
        )

    def favorite_albums(
        self,
        album_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        """
        `User Collections > Add Albums to User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /post_userCollections__id__relationships_albums>`_: Add albums
        to a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.write` scope
                 Write access to a user's collection.

        Parameters
        ----------
        album_ids : int, str, dict[str, int | str], or \
        list[int | str | dict[str, int | str]]; positional-only
            TIDAL IDs and/or resource identifiers of the albums.

            **Examples**:

            .. container::

               * :code:`46369321`
               * :code:`"251380836"`
               * :code:`{"id": "46369321", "types": "albums"}`
               * :code:`["251380836", {"id": "46369321", "types": "albums"}]`

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.
        """
        self._client._require_scopes(
            "users.favorite_albums", "collection.write"
        )
        self._modify_collection_resources(
            "POST",
            "albums",
            album_ids,
            user_id=user_id,
            country_code=country_code,
        )

    def unfavorite_albums(
        self,
        album_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
    ) -> None:
        """
        `User Collections > Remove Albums from User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /delete_userCollections__id__relationships_albums>`_: Remove
        albums from a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.write` scope
                 Write access to a user's collection.

        Parameters
        ----------
        album_ids : int, str, dict[str, int | str], or \
        list[int | str | dict[str, int | str]]; positional-only
            TIDAL IDs and/or resource identifiers of the albums.

            **Examples**:

            .. container::

               * :code:`46369321`
               * :code:`"251380836"`
               * :code:`{"id": "46369321", "types": "albums"}`
               * :code:`["251380836", {"id": "46369321", "types": "albums"}]`

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_scopes(
            "users.unfavorite_albums", "collection.write"
        )
        self._modify_collection_resources(
            "DELETE",
            "albums",
            album_ids,
            user_id=user_id,
            country_code=False,
        )

    def get_favorite_artists(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        `User Collections > Get Artists in User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /get_userCollections__id__relationships_artists>`_: Get TIDAL
        catalog information for artists in a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.read` scope
                 Read access to a user's collection.

        Parameters
        ----------
        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the artists in
            the user's collection.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        sort_by : str; keyword-only; optional
            Field to sort the artists by.

            **Valid values**: :code:`"addedAt"`, :code:`"name"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        artists : dict[str, Any]
            TIDAL content metadata for the artists in the user's
            collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "meta": {
                          "addedAt": <str>
                        },
                        "type": "artists"
                      }
                    ],
                    "included": [
                      {
                        "attributes": {
                          "contributionsEnabled": <bool>,
                          "externalLinks": [
                            {
                              "href": <str>,
                              "meta": {
                                "type": <str>
                              }
                            }
                          ],
                          "name": <str>,
                          "popularity": <float>,
                          "spotlighted": <bool>
                        },
                        "id": <str>,
                        "relationships": {
                          "albums": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "biography": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "followers": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "following": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "owners": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "profileArt": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "radio": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "roles": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "similarArtists": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "trackProviders": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "tracks": {
                            "links": {
                              "self": <str>
                            }
                          },
                          "videos": {
                            "links": {
                              "self": <str>
                            }
                          }
                        },
                        "type": "artists"
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
        self._client._require_scopes(
            "users.get_favorite_artists", "collection.read"
        )
        return self._get_collection_relationship(
            "artists",
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include_metadata=include_metadata,
            cursor=cursor,
            sort_by=sort_by,
            descending=descending,
            sort_fields={"addedAt", "name"},
        )

    def favorite_artists(
        self,
        artist_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        """
        `User Collections > Add Artists to User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /post_userCollections__id__relationships_artists>`_: Add artists
        to a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.write` scope
                 Write access to a user's collection.

        Parameters
        ----------
        artist_ids : int, str, dict[str, int | str], or \
        list[int | str | dict[str, int | str]]; positional-only
            TIDAL IDs and/or resource identifiers of the artists.

            **Examples**:

            .. container::

               * :code:`1566`
               * :code:`"4676988"`
               * :code:`{"id": "1566", "types": "artists"}`
               * :code:`["4676988", {"id": "46369321", "types": "artists"}]`

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.
        """
        self._client._require_scopes(
            "users.favorite_artists", "collection.write"
        )
        self._modify_collection_resources(
            "POST",
            "artists",
            artist_ids,
            user_id=user_id,
            country_code=country_code,
        )

    def unfavorite_artists(
        self,
        artist_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
    ) -> None:
        """
        `User Collections > Remove Artists from User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /delete_userCollections__id__relationships_artists>`_: Remove
        artists from a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.write` scope
                 Write access to a user's collection.

        Parameters
        ----------
        artist_ids : int, str, dict[str, int | str], or \
        list[int | str | dict[str, int | str]]; positional-only
            TIDAL IDs and/or resource identifiers of the artists.

            **Examples**:

            .. container::

               * :code:`1566`
               * :code:`"4676988"`
               * :code:`{"id": "1566", "types": "artists"}`
               * :code:`["4676988", {"id": "46369321", "types": "artists"}]`

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_scopes(
            "users.unfavorite_artists", "collection.write"
        )
        self._modify_collection_resources(
            "DELETE",
            "artists",
            artist_ids,
            user_id=user_id,
            country_code=False,
        )

    def get_favorite_owners(
        self,
        *,
        user_id: int | str | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `User Collections > Get Owners in User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /get_userCollections__id__relationships_owners>`_: Get TIDAL
        catalog information for owners in a user's collection.

        .. admonition:: Authorization scopes
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.read` scope
                 Read access to a user's collection.

           .. tab:: Optional

              :code:`user.read` scope
                 Read access to a user's account information, such as
                 country and email address.

        Parameters
        ----------
        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the owners of
            the user's collection.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        owners : dict[str, Any]
            TIDAL content metadata for the owners in the user's
            collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "type": "users"
                      }
                    ],
                    "included": [
                      {
                        "attributes": {
                          "country": <str>,
                          "email": <str>,
                          "emailVerified": <bool>,
                          "firstName": <str>,
                          "username": <str>
                        },
                        "id": <str>,
                        "type": "users"
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
        self._client._require_scopes(
            "users.get_collection_owners", "collection.read"
        )
        return self._get_collection_relationship(
            "owners",
            user_id=user_id,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    def get_favorite_playlists(
        self,
        *,
        user_id: int | str | None = None,
        include_folders: bool = False,
        include_metadata: bool = False,
        cursor: str | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        `User Collections > Get Playlists in User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /get_userCollections__id__relationships_playlists>`_: Get TIDAL
        catalog information for playlists in a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.read` scope
                 Read access to a user's collection.

        Parameters
        ----------
        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        include_folders : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            playlist folders in the user's collection.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the playlists
            in the user's collection.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        sort_by : str; keyword-only; optional
            Field to sort the playlists by.

            **Valid values**: :code:`"addedAt"`,
            :code:`"lastUpdatedAt"`, :code:`"name"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        playlists : dict[str, Any]
            TIDAL content metadata for the playlists (and playlist
            folders) in the user's collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "meta": {
                          "addedAt": <str>
                        },
                        "type": "playlists"
                      },
                      {
                        "id": <str>,
                        "meta": {
                          "addedAt": <str>
                        },
                        "type": "userCollectionFolders"
                      }
                    ],
                    "included": [
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
        self._client._require_scopes(
            "users.get_favorite_playlists", "collection.read"
        )
        params = {}
        if include_folders:
            params["collectionView"] = "FOLDERS"
        return self._get_collection_relationship(
            "playlists",
            user_id=user_id,
            country_code=False,
            include_metadata=include_metadata,
            cursor=cursor,
            sort_by=sort_by,
            descending=descending,
            sort_fields={"addedAt", "lastUpdatedAt", "name"},
            params=params,
        )

    def favorite_playlists(
        self,
        playlist_uuids: str | dict[str, str] | list[str | dict[str, str]],
        /,
        *,
        user_id: int | str | None = None,
    ) -> None:
        """
        `User Collections > Add Playlists to User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /post_userCollections__id__relationships_playlists>`_: Add
        playlists to a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.write` scope
                 Write access to a user's collection.

        Parameters
        ----------
        playlist_uuids : str, dict[str, str], or \
        list[str | dict[str, str]]; positional-only
            UUIDs and/or resource identifiers of the playlists.

            **Examples**:

            .. container::

               * :code:`"f0d6f5c4-081f-4348-9b65-ae677d92767b"`
               * .. code::

                    {
                        "id": "1e4c73df-b805-47cd-9e44-9a8721c5cb45",
                        "types": "playlists"
                    }
               * .. code::

                    [
                        "f0d6f5c4-081f-4348-9b65-ae677d92767b",
                        {
                            "id": "1e4c73df-b805-47cd-9e44-9a8721c5cb45",
                            "types": "playlists"
                        }
                    ]

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_scopes(
            "users.favorite_playlists", "collection.write"
        )
        self._modify_collection_resources(
            "POST", "playlists", playlist_uuids, user_id=user_id
        )

    def unfavorite_playlists(
        self,
        playlist_uuids: str | dict[str, str] | list[str | dict[str, str]],
        /,
        *,
        user_id: int | str | None = None,
    ) -> None:
        """
        `User Collections > Remove Playlists from User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /delete_userCollections__id__relationships_playlists>`_: Remove
        playlists from a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.write` scope
                 Write access to a user's collection.

        Parameters
        ----------
        playlist_uuids : str, dict[str, str], or \
        list[str | dict[str, str]]; positional-only
            UUIDs and/or resource identifiers of the playlists.

            **Examples**:

            .. container::

               * :code:`"f0d6f5c4-081f-4348-9b65-ae677d92767b"`
               * .. code::

                    {
                        "id": "1e4c73df-b805-47cd-9e44-9a8721c5cb45",
                        "types": "playlists"
                    }
               * .. code::

                    [
                        "f0d6f5c4-081f-4348-9b65-ae677d92767b",
                        {
                            "id": "1e4c73df-b805-47cd-9e44-9a8721c5cb45",
                            "types": "playlists"
                        }
                    ]

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_scopes(
            "users.unfavorite_playlists", "collection.write"
        )
        self._modify_collection_resources(
            "DELETE", "playlists", playlist_uuids, user_id=user_id
        )

    def get_favorite_tracks(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        `User Collections > Get Tracks in User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /get_userCollections__id__relationships_tracks>`_: Get TIDAL
        catalog information for tracks in a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.read` scope
                 Read access to a user's collection.

        Parameters
        ----------
        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the tracks in
            the user's collection.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        sort_by : str; keyword-only; optional
            Field to sort the tracks by.

            **Valid values**: :code:`"addedAt"`, :code:`"albums.title"`,
            :code:`"artists.name"`, :code:`"duration"`, :code:`"title"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        tracks : dict[str, Any]
            TIDAL content metadata for the tracks in the user's
            collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "meta": {
                          "addedAt": <str>
                        },
                        "type": "tracks"
                      }
                    ],
                    "included": [
                      {
                        "attributes": {
                          "accessType": <str>,
                          "availability": <list[str]>,
                          "bpm": <float>,
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
                          "key": <str>,
                          "keyScale": <str>,
                          "mediaTags": <list[str]>,
                          "popularity": <float>,
                          "spotlighted": <bool>,
                          "title": <str>,
                          "toneTags": <list[str]>,
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
        self._client._require_scopes(
            "users.get_favorite_tracks", "collection.read"
        )
        return self._get_collection_relationship(
            "tracks",
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include_metadata=include_metadata,
            cursor=cursor,
            sort_by=sort_by,
            descending=descending,
            sort_fields={
                "addedAt",
                "albums.title",
                "artists.name",
                "duration",
                "title",
            },
        )

    def favorite_tracks(
        self,
        track_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        """
        `User Collections > Add Tracks to User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /post_userCollections__id__relationships_tracks>`_: Add tracks
        to a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.write` scope
                 Write access to a user's collection.

        Parameters
        ----------
        track_ids : int, str, dict[str, int | str], or \
        list[int | str | dict[str, int | str]]; positional-only
            TIDAL IDs and/or resource identifiers of the tracks.

            **Examples**:

            .. container::

               * :code:`46369325`
               * :code:`"75413016"`
               * :code:`{"id": "46369325", "types": "tracks"}`
               * :code:`["75413016", {"id": "46369325", "types": "tracks"}]`

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.
        """
        self._client._require_scopes(
            "users.favorite_tracks", "collection.write"
        )
        self._modify_collection_resources(
            "POST",
            "tracks",
            track_ids,
            user_id=user_id,
            country_code=country_code,
        )

    def unfavorite_tracks(
        self,
        track_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
    ) -> None:
        """
        `User Collections > Remove Tracks from User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /delete_userCollections__id__relationships_tracks>`_: Remove
        tracks from a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.write` scope
                 Write access to a user's collection.

        Parameters
        ----------
        track_ids : int, str, dict[str, int | str], or \
        list[int | str | dict[str, int | str]]; positional-only
            TIDAL IDs and/or resource identifiers of the tracks.

            **Examples**:

            .. container::

               * :code:`46369325`
               * :code:`"75413016"`
               * :code:`{"id": "46369325", "types": "tracks"}`
               * :code:`["75413016", {"id": "46369325", "types": "tracks"}]`

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_scopes(
            "users.unfavorite_tracks", "collection.write"
        )
        self._modify_collection_resources(
            "DELETE",
            "tracks",
            track_ids,
            user_id=user_id,
            country_code=False,
        )

    def get_favorite_videos(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        `User Collections > Get Videos in User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /get_userCollections__id__relationships_videos>`_: Get TIDAL
        catalog information for videos in a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.read` scope
                 Read access to a user's collection.

        Parameters
        ----------
        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the videos in
            the user's collection.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        sort_by : str; keyword-only; optional
            Field to sort the videos by.

            **Valid values**: :code:`"addedAt"`, :code:`"artists.name"`,
            :code:`"duration"`, :code:`"title"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        Returns
        -------
        videos : dict[str, Any]
            TIDAL content metadata for the videos in the user's
            collection.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "meta": {
                          "addedAt": <str>
                        },
                        "type": "videos"
                      }
                    ],
                    "included": [
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
                          "popularity": <float>
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
        self._client._require_scopes(
            "users.get_favorite_videos", "collection.read"
        )
        return self._get_collection_relationship(
            "videos",
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include_metadata=include_metadata,
            cursor=cursor,
            sort_by=sort_by,
            descending=descending,
            sort_fields={"addedAt", "artists.name", "duration", "title"},
        )

    def favorite_videos(
        self,
        video_ids: str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        """
        `User Collections > Add Videos to User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /post_userCollections__id__relationships_videos>`_: Add videos
        to a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.write` scope
                 Write access to a user's collection.

        Parameters
        ----------
        video_ids : int, str, dict[str, int | str], or \
        list[int | str | dict[str, int | str]]; positional-only
            TIDAL IDs and/or resource identifiers of the videos.

            **Examples**:

            .. container::

               * :code:`53315642`
               * :code:`"75623239"`
               * :code:`{"id": "75623239", "types": "videos"}`
               * :code:`["53315642", {"id": "75623239", "types": "videos"}]`

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.
        """
        self._client._require_scopes(
            "users.favorite_videos", "collection.write"
        )
        self._modify_collection_resources(
            "POST",
            "videos",
            video_ids,
            user_id=user_id,
            country_code=country_code,
        )

    def unfavorite_videos(
        self,
        video_ids: str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
    ) -> None:
        """
        `User Collections > Remove Videos from User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /delete_userCollections__id__relationships_videos>`_: Remove
        videos from a user's collection.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`collection.write` scope
                 Write access to a user's collection.

        Parameters
        ----------
        video_ids : int, str, dict[str, int | str], or \
        list[int | str | dict[str, int | str]]; positional-only
            TIDAL IDs and/or resource identifiers of the videos.

            **Examples**:

            .. container::

               * :code:`53315642`
               * :code:`"75623239"`
               * :code:`{"id": "75623239", "types": "videos"}`
               * :code:`["53315642", {"id": "75623239", "types": "videos"}]`

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.
        """
        self._client._require_scopes(
            "users.unfavorite_videos", "collection.write"
        )
        self._modify_collection_resources(
            "DELETE",
            "videos",
            video_ids,
            user_id=user_id,
            country_code=False,
        )

    def get_entitlements(
        self,
        *,
        user_id: int | str | None = None,
        expand: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """
        `User Entitlements > Get User's Entitlements
        <https://tidal-music.github.io/tidal-api-reference/#
        /userEntitlements/get_userEntitlements__id_>`_: Get
        functionalities a user is entitled to access on TIDAL.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`entitlements.read` scope
                 Read functionalities a user is entitled to access on
                 TIDAL.

        Parameters
        ----------
        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        expand : str or list[str]; keyword-only; optional
            Related resources to include metadata for in the response.

            **Valid value**: :code:`"owners"`.

        Returns
        -------
        entitlements : dict[str, Any]
            Functionalities a user is entitled to access on TIDAL.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": {
                      "attributes": {
                        "entitlements": <list[str]>
                      },
                      "id": <str>,
                      "relationships": {
                        "owners": {
                          "data": [
                            {
                              "id": <str>,
                              "type": "users"
                            }
                          ],
                          "links": {
                            "self": <str>
                          }
                        }
                      },
                      "type": "userEntitlements"
                    },
                    "included": [
                      {
                        "attributes": {
                          "country": <str>,
                          "email": <str>,
                          "emailVerified": <bool>,
                          "username": <str>
                        },
                        "id": <str>,
                        "type": "users"
                      }
                    ],
                    "links": {
                      "self": <str>
                    }
                  }
        """
        self._client._require_scopes(
            "users.get_entitlements", "entitlements.read"
        )
        if user_id is None:
            user_id = self._client._my_profile["id"]
        else:
            self._client._validate_tidal_ids(user_id, _recursive=False)
        return self._get_resources(
            "userEntitlements",
            user_id,
            country_code=False,
            expand=expand,
            relationships={"owners"},
        )

    def get_entitlement_owners(
        self,
        *,
        user_id: int | str | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `User Entitlements > Get User Entitlements' Owners
        <https://tidal-music.github.io/tidal-api-reference/#
        /userEntitlements
        /get_userEntitlements__id__relationships_owners>`_: Get TIDAL
        catalog information for user entitlements' owners.

        Parameters
        ----------
        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the user
            entitlements' owners.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        owners : dict[str, Any]
            TIDAL content metadata for the user entitlements' owners.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "type": "users"
                      }
                    ],
                    "links": {
                      "self": <str>
                    }
                  }
        """
        self._client._require_scopes(
            "users.get_entitlements", "entitlements.read"
        )
        if user_id is None:
            user_id = self._client._my_profile["id"]
        else:
            self._client._validate_tidal_ids(user_id, _recursive=False)
        return self._get_resource_relationship(
            "userEntitlements",
            user_id,
            "owners",
            country_code=False,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="featured")
    def get_recommendations(
        self,
        *,
        user_id: str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        expand: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """
        `User Recommendations > Get Recommendations
        <https://tidal-music.github.io/tidal-api-reference/#
        /userRecommendations/get_userRecommendations__id_>`_: Get TIDAL
        catalog information for recommended media in personally curated
        mixes.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`recommendations.read` scope
                 Read access to a user's personal recommendations.

        Parameters
        ----------
        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not specified, it will
            be retrieved from the user's profile.

            **Example**: :code:`"US"`.


        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

        expand : str or list[str]; keyword-only; optional
            Related resources to include in the response.

            **Valid values**: :code:`"discoveryMixes"`,
            :code:`"myMixes"`, :code:`"newArrivalMixes"`.

        Returns
        -------
        recommendations : dict[str, Any]
            TIDAL content metadata for the items in the mixes.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": {
                      "attributes": {},
                      "id": <str>,
                      "relationships": {
                        "discoveryMixes": {
                          "data": [],
                          "links": {
                            "self": <str>
                          }
                        },
                        "myMixes": {
                          "data": [],
                          "links": {
                            "self": <str>
                          }
                        },
                        "newArrivalMixes": {
                          "data": [],
                          "links": {
                            "self": <str>
                          }
                        }
                      },
                      "type": "userRecommendations"
                    },
                    "included": [],
                    "links": {
                      "self": <str>
                    }
                  }
        """
        self._client._require_scopes(
            "users.get_recommendations", "recommendations.read"
        )
        if user_id is None:
            user_id = self._client._my_profile["id"]
        else:
            self._client._validate_tidal_ids(user_id, _recursive=False)
        return self._get_resources(
            "userRecommendations",
            user_id,
            country_code=country_code,
            locale=locale,
            expand=expand,
            relationships=self._RECOMMENDATION_RELATIONSHIPS,
        )

    @TTLCache.cached_method(ttl="featured")
    def get_discovery_mixes(
        self,
        *,
        user_id: str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include_metadata: bool = False,
        cursor: int | None = None,
    ) -> dict[str, Any]:
        """
        `User Recommendations > Get User's Discovery Mixes
        <https://tidal-music.github.io/tidal-api-reference/#
        /userRecommendations
        /get_userRecommendations__id__relationships_discoveryMixes>`_:
        Get TIDAL catalog information for the user's Discovery Mixes.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`recommendations.read` scope
                 Read access to a user's personal recommendations.

        Parameters
        ----------
          user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not specified, it will
            be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the user's
            Discovery Mixes.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        mixes : dict[str, Any]
            TIDAL catalog information for the user's Discovery Mixes.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

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
        self._client._require_scopes(
            "users.get_discovery_mixes", "recommendations.read"
        )
        self._get_resource_relationship(
            "userRecommendations",
            user_id,
            "discoveryMixes",
            country_code=country_code,
            locale=locale,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="featured")
    def get_mixes(
        self,
        *,
        user_id: str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include_metadata: bool = False,
        cursor: int | None = None,
    ) -> dict[str, Any]:
        """
        `User Recommendations > Get User's Mixes
        <https://tidal-music.github.io/tidal-api-reference/#
        /userRecommendations
        /get_userRecommendations__id__relationships_mixes>`_:
        Get TIDAL catalog information for the user's mixes.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`recommendations.read` scope
                 Read access to a user's personal recommendations.

        Parameters
        ----------
        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not specified, it will
            be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the user's
            mixes.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        mixes : dict[str, Any]
            TIDAL catalog information for the user's mixes.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

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
        self._client._require_scopes("users.get_mixes", "recommendations.read")
        self._get_resource_relationship(
            "userRecommendations",
            user_id,
            "myMixes",
            country_code=country_code,
            locale=locale,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="featured")
    def get_new_arrival_mixes(
        self,
        *,
        user_id: str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include_metadata: bool = False,
        cursor: int | None = None,
    ) -> dict[str, Any]:
        """
        `User Recommendations > Get User's New Arrival Mixes
        <https://tidal-music.github.io/tidal-api-reference/#
        /userRecommendations
        /get_userRecommendations__id__relationships_newArrivalMixes>`_:
        Get TIDAL catalog information for the user's New Arrival Mixes.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`recommendations.read` scope
                 Read access to a user's personal recommendations.

        Parameters
        ----------
          user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not specified, it will
            be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the user's New
            Arrival Mixes.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        mixes : dict[str, Any]
            TIDAL catalog information for the user's New Arrival Mixes.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

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
        self._client._require_scopes(
            "users.get_new_arrival_mixes", "recommendations.read"
        )
        self._get_resource_relationship(
            "userRecommendations",
            user_id,
            "newArrivalMixes",
            country_code=country_code,
            locale=locale,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_my_profile(self) -> dict[str, Any]:
        """
        `Users > Get Current User's Profile
        <https://tidal-music.github.io/tidal-api-reference/#/users
        /get_users_me>`_: Get profile information for the current user.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user.read` scope
                 Read access to a user's account information, such as
                 country and email address.

        Returns
        -------
        profile : dict[str, Any]
            Current user's profile information.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": {
                      "attributes": {
                        "country": <str>,
                        "email": <str>,
                        "emailVerified": <bool>,
                        "firstName": <str>,
                        "username": <str>
                      },
                      "id": <str>,
                      "type": "users",
                    },
                    "links": {
                      "self": "/users/me"
                    }
                  }
        """
        self._client._require_scopes("users.get_my_profile", "user.read")
        return self._client._request("GET", "users/me").json()

    def _get_collection_relationship(
        self,
        relationship: str,
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
        sort_fields: set[str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for items of a resource type in a
        user's collection.

        Parameters
        ----------
        relationship : str; positional-only
            Related resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"owners"`, :code:`"playlists"`, :code:`"tracks"`,
            :code:`"videos"`.

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. Only optional when it can
            be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the specified
            resource.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        sort_by : str; keyword-only; optional
            Field to sort the returned items by.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

            **API default**: :code:`False`.

        sort_fields : set[str]; keyword-only; optional
            Valid fields to sort by.

        params : dict[str, Any]; keyword-only; optional
            Dictionary of additional query parameters to include in the
            request. If not provided, a new dictionary will be created.

            .. note::

               This `dict` is mutated in-place.

        Returns
        -------
        resource : dict[str, Any]
            TIDAL content metadata for the specified resource.
        """
        if params is None:
            params = {}
        if user_id is None:
            user_id = self._client._my_profile["id"]
        else:
            self._client._validate_tidal_ids(user_id, _recursive=False)
        if sort_by is not None:
            self._process_sort(
                sort_by,
                descending=descending,
                prefix=f"{relationship}.",
                sort_fields=sort_fields,
                params=params,
            )
        return self._get_resource_relationship(
            "userCollections",
            user_id,
            relationship,
            country_code=country_code,
            locale=locale,
            include_metadata=include_metadata,
            cursor=cursor,
            sort_by=sort_by,
            descending=descending,
            sort_fields=sort_fields,
            params=params,
        )

    def _modify_collection_resources(
        self,
        method: str,
        resource_type: str,
        resource_ids: str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        """
        Add/remove items of a resource type to/from a user's collection.

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

            **Valid values**: :code:`"POST"`, :code:`"DELETE"`.

        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"owners"`, :code:`"playlists"`, :code:`"tracks"`,
            :code:`"videos"`.

        resource_ids : str, dict[str, int | str], or \
        list[int | str | dict[str, int | str]]; positional-only
            TIDAL IDs, UUIDs, or resource identifiers of the items.

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.
        """
        if user_id is None:
            user_id = self._client._my_profile["id"]
        else:
            self._client._validate_tidal_ids(user_id, _recursive=False)
        params = {}
        if country_code is not None:
            self._client._resolve_country_code(country_code, params)
        self._client._request(
            method,
            f"userCollections/{user_id}/relationships/{resource_type}",
            params=params,
            json={
                "data": self._prepare_resource_identifiers(
                    resource_type, resource_ids
                )
            },
        )
