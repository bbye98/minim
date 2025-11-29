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

    _COLLECTION_RESOURCES = {
        "albums",
        "artists",
        "owners",
        "playlists",
        "tracks",
        "videos",
    }
    _RECOMMENDATION_RESOURCES = {
        "discoveryMixes",
        "myMixes",
        "newArrivalMixes",
    }
    _client: "TIDALAPI"

    def get_collection(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include: str | list[str] | None = None,
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

            **Default**: :code:`"en_US"` – English (U.S.).

        include : str or list[str]; keyword-only; optional
            Related resources to include in the response.

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
                          "accessType": "PUBLIC",
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
                          "accessType": "PUBLIC",
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
        params = {}
        if country_code is not None:
            self._client._resolve_country_code(country_code, params)
        if locale is not None:
            self._client._validate_type("locale", locale, str)
            params["locale"] = locale
        if include is not None:
            params["include"] = self._prepare_include(
                include, resources=self._COLLECTION_RESOURCES
            )
        return self._client._request(
            "GET", f"userCollections/{user_id}", params=params
        ).json()

    def get_favorite_albums(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include: bool = False,
        cursor: str | None = None,
        sort: str | None = None,
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

            **Default**: :code:`"en_US"` – English (U.S.).

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the albums in the user's collection.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        sort : str; keyword-only; optional
            Field to sort the returned albums by. Values are sorted
            in descending order with the :code:`-` prefix and in
            ascending order without.

            **Valid values**: :code:`"addedAt"`, :code:`"-addedAt`,
            :code:`"artists.name`, :code:`"-artists.name"`,
            :code:`"releaseDate"`, :code:`"-releaseDate"`,
            :code:`"title"`, :code:`"-title"`.

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
                          "accessType": "PUBLIC",
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
        return self._get_collection_resource(
            "albums",
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include=include,
            cursor=cursor,
            sort=sort,
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
            TIDAL IDs of the albums, provided as integers, strings, or
            properly formatted dictionaries.

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
        self._modify_collection_resource(
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
        country_code: str | None = None,
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
            TIDAL IDs of the albums, provided as integers, strings, or
            properly formatted dictionaries.

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
        self._modify_collection_resource(
            "DELETE",
            "albums",
            album_ids,
            user_id=user_id,
            country_code=country_code,
        )

    def get_favorite_artists(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include: bool = False,
        cursor: str | None = None,
        sort: str | None = None,
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

            **Default**: :code:`"en_US"` – English (U.S.).

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the artists in the user's collection.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        sort : str; keyword-only; optional
            Field to sort the returned artists by. Values are sorted
            in descending order with the :code:`-` prefix and in
            ascending order without.

            **Valid values**: :code:`"addedAt"`, :code:`"-addedAt`,
            :code:`"name"`, :code:`"-name"`.

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
        return self._get_collection_resource(
            "artists",
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include=include,
            cursor=cursor,
            sort=sort,
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
            TIDAL IDs of the artists, provided as integers, strings, or
            properly formatted dictionaries.

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
        self._modify_collection_resource(
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
        country_code: str | None = None,
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
            TIDAL IDs of the artists, provided as integers, strings, or
            properly formatted dictionaries.

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
        self._modify_collection_resource(
            "DELETE",
            "artists",
            artist_ids,
            user_id=user_id,
            country_code=country_code,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_collection_owners(
        self,
        *,
        user_id: int | str | None = None,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `User Collections > Get Owners of User's Collection
        <https://tidal-music.github.io/tidal-api-reference/#
        /userCollections
        /get_userCollections__id__relationships_owners>`_: Get TIDAL
        catalog information for owners of a user's collection.

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

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the owners of the user's collection.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        owners : dict[str, Any]
            TIDAL content metadata for the owners of the user's
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
        return self._get_collection_resource(
            "owners", user_id=user_id, include=include, cursor=cursor
        )

    def get_favorite_playlists(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        folders: bool = False,
        include: bool = False,
        cursor: str | None = None,
        sort: str | None = None,
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

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

            **Default**: :code:`"en_US"` – English (U.S.).

        folders : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            playlist folders in the user's collection.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the playlists in the user's collection.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        sort : str; keyword-only; optional
            Field to sort the returned playlists by. Values are sorted
            in descending order with the :code:`-` prefix and in
            ascending order without.

            **Valid values**: :code:`"addedAt"`, :code:`"-addedAt`,
            :code:`"lastUpdatedAt"`, :code:`"-lastUpdatedAt"`,
            :code:`"name"`, :code:`"-name"`.

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
        params = {}
        if folders:
            params["collectionView"] = "FOLDERS"
        return self._get_collection_resource(
            "playlists",
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include=include,
            cursor=cursor,
            sort=sort,
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
            UUIDs of the playlists, provided as strings or properly
            formatted dictionaries.

            **Examples**:

            .. container::

               * :code:"f0d6f5c4-081f-4348-9b65-ae677d92767b"
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
        self._modify_collection_resource(
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
            UUIDs of the playlists, provided as strings or properly
            formatted dictionaries.

            **Examples**:

            .. container::

               * :code:"f0d6f5c4-081f-4348-9b65-ae677d92767b"
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
        self._modify_collection_resource(
            "DELETE", "playlists", playlist_uuids, user_id=user_id
        )

    def get_favorite_tracks(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include: bool = False,
        cursor: str | None = None,
        sort: str | None = None,
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

            **Default**: :code:`"en_US"` – English (U.S.).

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the tracks in the user's collection.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        sort : str; keyword-only; optional
            Field to sort the returned tracks by. Values are sorted
            in descending order with the :code:`-` prefix and in
            ascending order without.

            **Valid values**: :code:`"addedAt"`, :code:`"-addedAt`,
            :code:`"albums.title"`, :code:`"-albums.title"`,
            :code:`"artists.name"`, :code:`"-artists.name"`,
            :code:`"duration"`, :code:`"-duration"`, :code:`"title"`,
            :code:`"-title"`.

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
                          "accessType": "PUBLIC",
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
        return self._get_collection_resource(
            "tracks",
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include=include,
            cursor=cursor,
            sort=sort,
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
            TIDAL IDs of the tracks, provided as integers, strings, or
            properly formatted dictionaries.

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
        self._modify_collection_resource(
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
        country_code: str | None = None,
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
            TIDAL IDs of the tracks, provided as integers, strings, or
            properly formatted dictionaries.

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
        self._modify_collection_resource(
            "DELETE",
            "tracks",
            track_ids,
            user_id=user_id,
            country_code=country_code,
        )

    def get_favorite_videos(
        self,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include: bool = False,
        cursor: str | None = None,
        sort: str | None = None,
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

            **Default**: :code:`"en_US"` – English (U.S.).

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the videos in the user's collection.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        sort : str; keyword-only; optional
            Field to sort the returned videos by. Values are sorted
            in descending order with the :code:`-` prefix and in
            ascending order without.

            **Valid values**: :code:`"addedAt"`, :code:`"-addedAt`,
            :code:`"artists.name"`, :code:`"-artists.name"`,
            :code:`"duration"`, :code:`"-duration"`, :code:`"title"`,
            :code:`"-title"`.

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
        return self._get_collection_resource(
            "videos",
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include=include,
            cursor=cursor,
            sort=sort,
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
            TIDAL IDs of the videos, provided as integers, strings, or
            properly formatted dictionaries.

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
        self._modify_collection_resource(
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
        country_code: str | None = None,
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
            TIDAL IDs of the videos, provided as integers, strings, or
            properly formatted dictionaries.

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
        self._modify_collection_resource(
            "DELETE",
            "videos",
            video_ids,
            user_id=user_id,
            country_code=country_code,
        )

    def get_entitlements(
        self, *, user_id: int | str | None = None
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
                      "type": "userEntitlements"
                    },
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
        return self._client._request("GET", f"userEntitlements/{user_id}")

    @TTLCache.cached_method(ttl="featured")
    def get_recommendations(
        self,
        *,
        user_id: str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include: str | list[str] | None = None,
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

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

            **Default**: :code:`"en_US"` – English (U.S.).

        include : str or list[str]; keyword-only; optional
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
        params = {}
        if country_code is not None:
            self._client._resolve_country_code(country_code, params)
        if locale is not None:
            self._client._validate_type("locale", locale, str)
            params["locale"] = locale
        if include is not None:
            params["include"] = self._prepare_include(
                include, resources=self._RECOMMENDATION_RESOURCES
            )
        return self._client._request(
            "GET", f"userRecommendations/{user_id}", params=params
        )

    @TTLCache.cached_method(ttl="featured")
    def get_discovery_mixes(
        self,
        *,
        user_id: str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include: bool = False,
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

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

            **Default**: :code:`"en_US"` – English (U.S.).

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the user's Discovery Mixes.

        cursor : str; keyword-only; optional
            Cursor for pagination.

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
        return self._get_recommendation_mixes(
            "discoveryMixes",
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include=include,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="featured")
    def get_mixes(
        self,
        *,
        user_id: str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include: bool = False,
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

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

            **Default**: :code:`"en_US"` – English (U.S.).

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the user's mixes.

        cursor : str; keyword-only; optional
            Cursor for pagination.

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
        return self._get_recommendation_mixes(
            "myMixes",
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include=include,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="featured")
    def get_new_arrival_mixes(
        self,
        *,
        user_id: str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include: bool = False,
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

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

            **Default**: :code:`"en_US"` – English (U.S.).

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the user's New Arrival Mixes.

        cursor : str; keyword-only; optional
            Cursor for pagination.

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
        return self._get_recommendation_mixes(
            "newArrivalMixes",
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include=include,
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

    @classmethod
    def _process_collection_items(
        cls,
        resource: str,
        item_ids: int
        | str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
        /,
        *,
        _recursive: bool = True,
    ) -> list[dict[str, str]]:
        """
        Process user-specified items to add to or remove from a user's
        collection.

        Parameters
        ----------
        resource : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"owners"`, :code:`"playlists"`, :code:`"tracks"`,
            :code:`"videos"`.

        item_ids : str, dict[str, int | str], or \
        list[int | str | dict[str, int | str]]; positional-only
            TIDAL IDs or UUIDs of items, provided as strings or
            properly formatted dictionaries.

        Returns
        -------
        items : list[dict[str, str]]
            List of properly formatted dictionaries containing metadata
            for the items.
        """
        if isinstance(item_ids, dict):
            item_id = item_ids.get("id")
            if item_ids.get("type") != resource:
                raise ValueError(
                    f"Item with ID {item_id!r} is not a {resource[:-1]}."
                )
        elif isinstance(item_ids, int | str):
            item_id = item_ids
        else:
            num_items = len(item_ids)
            if not num_items:
                raise ValueError(
                    f"At least one {resource[:-1]} must be specified."
                )
            if num_items > 20:
                raise ValueError(
                    f"A maximum of 20 {resource} can be sent in a request."
                )
            return [
                cls._process_collection_items(item_id, _recursive=False)
                for item_id in item_ids
            ]
        item = {"id": str(item_id), "type": resource}
        if _recursive:
            return [item]
        return item

    def _get_collection_resource(
        self,
        resource: str,
        /,
        *,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include: bool = False,
        cursor: str | None = None,
        sort: str | None = None,
        sort_fields: set[str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for items of a resource type in a
        user's collection.

        Parameters
        ----------
        resource : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"owners"`, :code:`"playlists"`, :code:`"tracks"`,
            :code:`"videos"`.

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

            **Default**: :code:`"en_US"` – English (U.S.).

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the specified resource.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        sort : str; keyword-only; optional
            Field to sort the returned items by. Values are sorted
            in descending order with the :code:`-` prefix and in
            ascending order without.

        sort_fields : set[str]; keyword-only; optional
            Valid fields for `sort` to sort by.

        params : dict[str, Any]; keyword-only; optional
            Existing dictionary holding URL query parameters. If not
            provided, a new dictionary will be created.

        Returns
        -------
        resource : dict[str, Any]
            TIDAL catalog information for the specified resource.
        """
        self._client._require_scopes(
            f"users.get_collection_{resource}", "collection.read"
        )
        if user_id is None:
            user_id = self._client._my_profile["id"]
        else:
            self._client._validate_tidal_ids(user_id, _recursive=False)
        if params is None:
            params = {}
        if country_code is not None:
            self._client._resolve_country_code(country_code, params)
        if locale is not None:
            self._client._validate_type("locale", locale, str)
            params["locale"] = locale
        if include is not None:
            self._client._validate_type("include", include, bool)
            if include:
                params["include"] = resource
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["page[cursor]"] = cursor
        if sort is not None:
            self._client._validate_type("sort", sort, str)
            descending = sort[0] == "-"
            if (
                "." not in (_sort := sort[1:] if descending else sort)
                or (sort_values := _sort.split(".", maxsplit=1))[0] != resource
                or sort_values[1] not in sort_fields
            ):
                sorts = f"', '{resource}.".join(sort_fields)
                raise ValueError(
                    f"Invalid sort field {sort!r}. "
                    f"Valid values: '{resource}.{sorts}'."
                )
            params["sort"] = (
                f"{sort[:descending]}{resource}.{sort[descending:]}"
            )
        return self._client._request(
            "GET",
            f"userCollections/{user_id}/relationships/{resource}",
            params=params,
        ).json()

    def _modify_collection_resource(
        self,
        method: str,
        resource: str,
        /,
        item_ids: str
        | dict[str, int | str]
        | list[int | str | dict[str, int | str]],
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

        resource : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"owners"`, :code:`"playlists"`, :code:`"tracks"`,
            :code:`"videos"`.

        item_ids : str, dict[str, int | str], or \
        list[int | str | dict[str, int | str]]
            TIDAL IDs or UUIDs of items, provided as strings or
            properly formatted dictionaries.

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.
        """
        self._client._require_scopes(
            f"users.{'add' if method == 'POST' else 'remove'}_collection_{resource}",
            "collection.write",
        )
        if user_id is None:
            user_id = self._client._my_profile["id"]
        else:
            self._client._validate_tidal_ids(user_id, _recursive=False)
        params = {}
        if country_code is not None:
            self._client._resolve_country_code(country_code, params)
        self._client._request(
            method,
            f"userCollections/{user_id}/relationships/{resource}",
            json={"data": self._process_collection_items(resource, item_ids)},
        )

    def _get_recommendation_mixes(
        self,
        resource: str,
        /,
        *,
        user_id: str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include: bool = False,
        cursor: int | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for mixes recommended to a user.

        Parameters
        ----------
        resource : str; positional-only
            Resource type.

            **Valid values**: :code:`"discoveryMixes"`,
            :code:`"myMixes"`, :code:`"newArrivalMixes"`.

        user_id : int or str; keyword-only; optional
            TIDAL ID of the user. If not specified, the current user's
            TIDAL ID is used.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

            **Default**: :code:`"en_US"` – English (U.S.).

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the specified resource.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        resource : dict[str, Any]
            TIDAL catalog information for the specified resource.
        """
        self._client._require_scopes(
            f"users.get_{
                'user_mixes'
                if resource == 'myMixes'
                else ''.join(
                    char if char.islower() else f'_{char.lower()}'
                    for char in resource
                )
            }",
            "recommendations.read",
        )
        if user_id is None:
            user_id = self._client._my_profile["id"]
        else:
            self._client._validate_tidal_ids(user_id, _recursive=False)
        params = {}
        if country_code is not None:
            self._client._resolve_country_code(country_code, params)
        if locale is not None:
            self._client._validate_type("locale", locale, str)
            params["locale"] = locale
        if include is not None:
            self._client._validate_type("include", include, bool)
            if include:
                params["include"] = resource
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["page[cursor]"] = cursor
        return self._client._request(
            "GET",
            f"userRecommendations/{user_id}/relationships/{resource}",
            params=params,
        ).json()
