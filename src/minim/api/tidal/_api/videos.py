from __future__ import annotations
from typing import TYPE_CHECKING

from ..._shared import TTLCache, _copy_docstring
from ._shared import TIDALResourceAPI
from .search import SearchAPI
from .users import UsersAPI

if TYPE_CHECKING:
    from typing import Any

    from ...._types import Collection


class VideosAPI(TIDALResourceAPI):
    """
    Videos API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`~minim.api.tidal.TIDALAPIClient`
       and should not be instantiated directly.
    """

    _RELATIONSHIPS = {
        "albums",
        "artists",
        "credits",
        "providers",
        "replacement",
        "similarVideos",
        "suggestedVideos",
        "thumbnailArt",
        "usageRules",
    }

    __slots__ = ()

    @TTLCache.cached_method(ttl="popularity")
    def get_videos(
        self,
        video_ids: int | str | Collection[int | str] | None = None,
        /,
        *,
        isrcs: str | Collection[str] | None = None,
        country_code: str | None = None,
        expand: str | Collection[str] | None = None,
    ) -> dict[str, Any]:
        """
        `Videos > Get Single Video <https://tidal-music.github.io
        /tidal-api-reference/#/videos/get_videos__id_>`_: Get TIDAL
        catalog information for a video․
        `Videos > Get Multiple Videos <https://tidal-music.github.io
        /tidal-api-reference/#/videos/get_videos__id_>`_: Get TIDAL
        catalog information for multiple videos.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 User authentication
                    Access information for a resource's owners.

        .. important::

           Exactly one of `video_ids` or `isrcs` must be provided. If
           `video_ids` is specified, the request will always be sent to
           the endpoint for multiple videos.

        Parameters
        ----------
        video_ids : int, str, or Collection[int | str]; \
        positional-only; optional
            TIDAL IDs of the videos.

            **Examples**: :code:`53315642`, :code:`"75623239"`,
            :code:`[53315642, "75623239"]`.

        isrcs : str or Collection[str]; keyword-only; optional
            International Standard Recording Codes (ISRCs) of the
            videos.

            **Examples**: :code:`"QMJMT1701237"`,
            :code:`[QMJMT1701237, "USAT21404265"]`.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        expand : str or Collection[str]; keyword-only; optional
            Related resources to include metadata for in the response.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"credits"`, :code:`"providers"`, 
            :code:`"replacement"`, :code:`"similarVideos"`, 
            :code:`"suggestedVideos"`, :code:`"thumbnailArt"`, 
            :code:`"usageRules"`.

            **Examples**: :code:`"thumbnailArt"`,
            :code:`["albums", "artists"]`.

        Returns
        -------
        videos : dict[str, Any]
            TIDAL metadata for the videos.

            .. admonition:: Sample responses
               :class: response dropdown

               .. tab-set::

                  .. tab-item:: Single video

                     .. code-block::

                        {
                          "data": {
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
                                "data": [
                                  {
                                    "id": <str>,
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
                                    "type": "artists"
                                  }
                                ],
                                "links": {
                                  "self": <str>
                                }
                              },
                              "providers": {
                                "data": [
                                  {
                                    "id": <str>,
                                    "type": "providers"
                                  }
                                ],
                                "links": {
                                  "self": <str>
                                }
                              },
                              "thumbnailArt": {
                                "data": [
                                  {
                                    "id": <str>,
                                    "type": "artworks"
                                  }
                                ],
                                "links": {
                                  "self": <str>
                                }
                              }
                            },
                            "type": "videos"
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
                                "name": <str>
                              },
                              "id": <str>,
                              "type": "providers"
                            }
                          ],
                          "links": {
                            "self": <str>
                          }
                        }

                  .. tab-item:: Multiple videos

                     .. code-block::

                        {
                          "data": [
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
                                  "data": [
                                    {
                                      "id": <str>,
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
                                      "type": "artists"
                                    }
                                  ],
                                  "links": {
                                    "self": <str>
                                  }
                                },
                                "providers": {
                                  "data": [
                                    {
                                      "id": <str>,
                                      "type": "providers"
                                    }
                                  ],
                                  "links": {
                                    "self": <str>
                                  }
                                },
                                "thumbnailArt": {
                                  "data": [
                                    {
                                      "id": <str>,
                                      "type": "artworks"
                                    }
                                  ],
                                  "links": {
                                    "self": <str>
                                  }
                                }
                              },
                              "type": "videos"
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
                                "name": <str>
                              },
                              "id": <str>,
                              "type": "providers"
                            }
                          ],
                          "links": {
                            "self": <str>
                          }
                        }
        """
        if sum(arg is not None for arg in [video_ids, isrcs]) != 1:
            raise ValueError(
                "Exactly one of `video_ids` or `isrcs` must be provided."
            )
        params = {}
        if isrcs is not None:
            if isinstance(isrcs, str):
                isrcs = self._prepare_isrc(isrcs)
            elif isinstance(isrcs, list | tuple):
                isrcs = [self._prepare_isrc(isrc) for isrc in isrcs]
            else:
                raise ValueError(
                    "`isrcs` must be a string or a list of strings."
                )
            params["filter[isrc]"] = isrcs
        return self._get_resources(
            "videos",
            video_ids,
            country_code=country_code,
            expand=expand,
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_video_albums(
        self,
        video_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Videos > Get Albums Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/videos
        /get_videos__id__relationships_albums>`_: Get TIDAL catalog
        information for albums containing a video.

        Parameters
        ----------
        video_id : int or str; positional-only
            TIDAL ID of the video.

            **Examples**: :code:`53315642`, :code:`"75623239"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the albums containing the
            video.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        albums : dict[str, Any]
            Page of TIDAL metadata for the albums containing the videos.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "data": [
                      {
                        "id": <str>,
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
        return self._get_resource_relationship(
            "videos",
            video_id,
            "albums",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_video_artists(
        self,
        video_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Videos > Get Artists Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/videos
        /get_videos__id__relationships_artists>`_: Get TIDAL catalog
        information for the artists of a video.

        Parameters
        ----------
        video_id : int or str; positional-only
            TIDAL ID of the video.

            **Examples**: :code:`53315642`, :code:`"75623239"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the video's artists.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        artists : dict[str, Any]
            Page of TIDAL metadata for the video's artists.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "data": [
                      {
                        "id": <str>,
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
        return self._get_resource_relationship(
            "videos",
            video_id,
            "artists",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="static")
    def get_video_providers(
        self,
        video_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Videos > Get Providers Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/videos
        /get_videos__id__relationships_providers>`_: Get TIDAL catalog
        information for the providers of a video.

        Parameters
        ----------
        video_id : int or str; positional-only
            TIDAL ID of the video.

            **Examples**: :code:`53315642`, :code:`"75623239"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the video's providers.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        providers : dict[str, Any]
            Page of TIDAL metadata for the video's providers.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "type": "providers"
                      }
                    ],
                    "included": [
                      {
                        "attributes": {
                          "name": <str>
                        },
                        "id": <str>,
                        "type": "providers"
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
        return self._get_resource_relationship(
            "videos",
            video_id,
            "providers",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="static")
    def get_video_thumbnail(
        self,
        video_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Videos > Get Thumbnail Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/videos
        /get_videos__id__relationships_thumbnailArt>`_: Get TIDAL
        catalog information for the thumbnail for a video.

        Parameters
        ----------
        video_id : int or str; positional-only
            TIDAL ID of the video.

            **Examples**: :code:`53315642`, :code:`"75623239"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the video's thumbnail.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        thumbnail : dict[str, Any]
            Page of TIDAL metadata for the video's thumbnail.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
        return self._get_resource_relationship(
            "videos",
            video_id,
            "thumbnailArt",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="static")
    def get_video_usage_rules(
        self,
        video_id: int | str,
        /,
        *,
        include_metadata: bool = False,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Videos > Get Usage Rules Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/videos
        /get_videos__id__relationships_usageRules>`_: Get TIDAL catalog
        information for the usage rules for a video.

        Parameters
        ----------
        video_id : int or str; positional-only
            TIDAL ID of the video.

            **Examples**: :code:`53315642`, :code:`"75623239"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the track's usage rules.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        usage_rules : dict[str, Any]
            TIDAL metadata for the video's usage rules.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "data": {
                      "id": <str>,
                      "type": "usageRules"
                    },
                    "included": [
                      {
                        "attributes": {
                          "countryCode": <str>,
                          "free": <list[str]>,
                          "paid": <list[str]>,,
                          "subscription": <list[str]>,
                        },
                        "id": <str>,
                        "type": "usageRules"
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
        return self._get_resource_relationship(
            "videos",
            video_id,
            "usageRules",
            include_metadata=include_metadata,
            share_code=share_code,
        )

    @_copy_docstring(SearchAPI.search_videos)
    def search_videos(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        include_explicit: bool | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return self._client.search.search_videos(
            query,
            country_code=country_code,
            include_explicit=include_explicit,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    @_copy_docstring(UsersAPI.get_user_saved_videos)
    def get_user_saved_videos(
        self,
        *,
        collection_id: str | None = None,
        user_id: int | str | None = None,
        country_code: str | None = None,
        locale: str | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_user_saved_videos(
            collection_id=collection_id,
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include_metadata=include_metadata,
            cursor=cursor,
            sort_by=sort_by,
            descending=descending,
        )

    @_copy_docstring(UsersAPI.save_videos)
    def save_videos(
        self,
        video_ids: str
        | dict[str, int | str]
        | Collection[int | str | dict[str, int | str]],
        /,
        *,
        collection_id: str | None = None,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        self._client.users.save_videos(
            video_ids,
            collection_id=collection_id,
            user_id=user_id,
            country_code=country_code,
        )

    @_copy_docstring(UsersAPI.remove_saved_videos)
    def remove_saved_videos(
        self,
        video_ids: str
        | dict[str, int | str]
        | Collection[int | str | dict[str, int | str]],
        /,
        *,
        collection_id: str | None = None,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        self._client.users.remove_saved_videos(
            video_ids,
            collection_id=collection_id,
            user_id=user_id,
            country_code=country_code,
        )
