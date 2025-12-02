from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class PrivatePagesAPI(ResourceAPI):
    """
    Pages API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _DEVICE_TYPES = {"BROWSER", "DESKTOP", "PHONE", "TV"}
    _client: "PrivateTIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_album_page(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
    ) -> dict[str, Any]:
        """
        Get the TIDAL page layout for an album.

        Parameters
        ----------
        album_id : int or str; positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321`, :code:`"251380836"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        device_type : str; keyword-only; default: :code:`"BROWSER"`
            Device type.

            **Valid values**:

            .. container::

               * :code:`"BROWSER"` – Web browser.
               * :code:`"DESKTOP"` – Desktop TIDAL application.
               * :code:`"PHONE"` – Mobile TIDAL application.
               * :code:`"TV"` – Smart TV TIDAL application.

        Returns
        -------
        page : dict[str, Any]
            Page layout for the album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <str>,
                    "rows": [
                      {
                        "modules": [
                          {
                            "album": {
                              "allowStreaming": <bool>,
                              "artists": [
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
                              "audioModes": <list[str]>,
                              "audioQuality": <str>,
                              "copyright": <str>,
                              "cover": <str>,
                              "duration": <int>,
                              "explicit": <bool>,
                              "id": <int>,
                              "mediaMetadata": {
                                "tags": <list[str]>
                              },
                              "numberOfTracks": <int>,
                              "numberOfVideos": <int>,
                              "numberOfVolumes": <int>,
                              "payToStream": <bool>,
                              "popularity": <int>,
                              "releaseDate": <str>,
                              "streamReady": <bool>,
                              "streamStartDate": <str>,
                              "title": <str>,
                              "type": "ALBUM",
                              "upload": <bool>,
                              "url": <str>,
                              "version": <str>,
                              "videoCover": <str>
                            },
                            "credits": {
                              "items": [
                                {
                                  "contributors": [
                                    {
                                      "id": <int>,
                                      "name": <str>
                                    }
                                  ],
                                  "type": <str>
                                }
                              ]
                            },
                            "description": <str>,
                            "id": <str>,
                            "playbackControls": [
                              {
                                "icon": <str>,
                                "playbackMode": <str>,
                                "shuffle": <bool>,
                                "targetModuleId": <str>,
                                "title": <str>
                              }
                            ],
                            "preTitle": <str>,
                            "review": {
                              "source": <str>,
                              "text": <str>
                            },
                            "title": <str>,
                            "type": "ALBUM_HEADER",
                            "width": <int>
                          }
                        ]
                      },
                      {
                        "modules": [
                          {
                            "copyright": <str>,
                            "description": <str>,
                            "id": <str>,
                            "listFormat": "NUMBERS",
                            "pagedList": {
                              "dataApiPath": <str>,
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
                                    "artists": [
                                      {
                                        "handle": <str>,
                                        "id": <int>,
                                        "name": <str>,
                                        "picture": <str>,
                                        "type": <str>,
                                        "userId": <int>
                                      }
                                    ],
                                    "audioModes": <list[str]>,
                                    "audioQuality": <str>,
                                    "djReady": <bool>,
                                    "doublePopularity": <float>,
                                    "duration": <int>,
                                    "editable": <bool>,
                                    "explicit": <bool>,
                                    "id": <int>,
                                    "mediaMetadata": {
                                      "tags": <list[str]>
                                    },
                                    "mixes": {
                                      "TRACK_MIX": <str>
                                    },
                                    "payToStream": <bool>,
                                    "popularity": <int>,
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
                            },
                            "playButton": <bool>,
                            "preTitle": <str>,
                            "quickPlay": <bool>,
                            "releaseDate": <str>,
                            "showMore": {
                              "apiPath": <str>,
                              "title": "View all"
                            },
                            "shuffleButton": <bool>,
                            "supportsPaging": <bool>,
                            "title": <str>,
                            "type": "ALBUM_ITEMS",
                            "width": <int>
                          }
                        ]
                      },
                      {
                        "modules": [
                          {
                            "description": <str>,
                            "header": <str>,
                            "id": <str>,
                            "layout": <str>,
                            "listFormat": <str>,
                            "pagedList": {
                              "dataApiPath": <str>,
                              "items": [
                                {
                                  "allowStreaming": <bool>,
                                  "artists": [
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
                                  "audioModes": <list[str]>,
                                  "audioQuality": <str>,
                                  "cover": <str>,
                                  "duration": <int>,
                                  "explicit": <bool>,
                                  "id": <int>,
                                  "mediaMetadata": {
                                    "tags": <list[str]>
                                  },
                                  "numberOfTracks": <int>,
                                  "numberOfVideos": <int>,
                                  "payToStream": <bool>,
                                  "releaseDate": <str>,
                                  "streamReady": <bool>,
                                  "streamStartDate": <str>,
                                  "title": <str>,
                                  "upload": <bool>,
                                  "url": <str>,
                                  "vibrantColor": <str>,
                                  "videoCover": <str>
                                }
                              ],
                              "limit": <int>,
                              "offset": <int>,
                              "totalNumberOfItems": <int>
                            },
                            "preTitle": <str>,
                            "quickPlay": <bool>,
                            "scroll": <str>,
                            "showMore": {
                              "apiPath": <str>,
                              "title": "View all"
                            },
                            "supportsPaging": <bool>,
                            "title": <str>,
                            "type": "ALBUM_LIST",
                            "width": <int>
                          }
                        ]
                      },
                      {
                        "modules": [
                          {
                            "description": <str>,
                            "header": <str>,
                            "id": <str>,
                            "layout": <str>,
                            "pagedList": {
                              "dataApiPath": <str>,
                              "items": [
                                {
                                  "artistRoles": [
                                    {
                                      "category": <str>,
                                      "categoryId": <int>
                                    }
                                  ],
                                  "artistTypes": <list[str]>,
                                  "id": <int>,
                                  "mixes": {
                                    "ARTIST_MIX": <str>
                                  },
                                  "name": <str>,
                                  "picture": <str>,
                                  "selectedAlbumCoverFallback": <str>
                                }
                              ],
                              "limit": <int>,
                              "offset": <int>,
                              "totalNumberOfItems": <int>
                            },
                            "preTitle": <str>,
                            "quickPlay": <bool>,
                            "scroll": <str>,
                            "showMore": {
                              "apiPath": <str>,
                              "title": "View all"
                            },
                            "supportsPaging": <bool>,
                            "title": <str>,
                            "type": "ARTIST_LIST",
                            "width": <int>
                          }
                        ]
                      }
                    ],
                    "selfLink": <str>,
                    "title": <str>
                  }
        """
        return self._get_resource_page(
            "album", album_id, country_code, device_type=device_type
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_page(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
    ) -> dict[str, Any]:
        """
        Get the TIDAL page layout for an artist.

        Parameters
        ----------
        artist_id : int or str; positional-only
            TIDAL ID of the artist.

            **Examples**: :code:`1566`, :code:`"4676988"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        device_type : str; keyword-only; default: :code:`"BROWSER"`
            Device type.

            .. container::

               * :code:`"BROWSER"` – Web browser.
               * :code:`"DESKTOP"` – Desktop TIDAL application.
               * :code:`"PHONE"` – Mobile TIDAL application.
               * :code:`"TV"` – Smart TV TIDAL application.

        Returns
        -------
        page : dict[str, Any]
            Page layout for the artist.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <str>,
                    "rows": [
                      {
                        "modules": [
                          {
                            "artist": {
                              "artistTypes": <list[str]>,
                              "handle": <str>,
                              "id": <int>,
                              "mixes": {
                                "ARTIST_MIX": <str>
                              },
                              "name": <str>,
                              "picture": <str>,
                              "selectedAlbumCoverFallback": <str>,
                              "url": <str>
                            },
                            "artistMix": {
                              "id": <str>
                            },
                            "bio": {
                              "source": <str>,
                              "text": <str>
                            },
                            "description": <str>,
                            "id": <str>,
                            "mixes": {
                              "ARTIST_MIX": <str>
                            },
                            "playbackControls": [
                              {
                                "icon": <str>,
                                "playbackMode": <str>,
                                "shuffle": <bool>,
                                "targetModuleId": <str>,
                                "title": <str>
                              }
                            ],
                            "preTitle": <str>,
                            "roleCategories": <Any>,
                            "store": <Any>,
                            "title": <str>,
                            "type": "ARTIST_HEADER",
                            "width": <int>
                          }
                        ]
                      },
                      {
                        "modules": [
                          {
                            "description": <str>,
                            "id": <str>,
                            "layout": <str>,
                            "listFormat": <str>,
                            "pagedList": {
                              "dataApiPath": <str>,
                              "items": [
                                {
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
                                  "artists": [
                                    {
                                      "handle": <str>,
                                      "id": <int>,
                                      "name": <str>,
                                      "picture": <str>,
                                      "type": <str>,
                                      "userId": <int>
                                    }
                                  ],
                                  "audioModes": <list[str]>,
                                  "audioQuality": <str>,
                                  "djReady": <bool>,
                                  "doublePopularity": <float>,
                                  "duration": <int>,
                                  "editable": <bool>,
                                  "explicit": <bool>,
                                  "id": <int>,
                                  "mediaMetadata": {
                                    "tags": <list[str]>
                                  },
                                  "mixes": {
                                    "TRACK_MIX": <str>
                                  },
                                  "payToStream": <bool>,
                                  "popularity": <int>,
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
                                }
                              ],
                              "limit": <int>,
                              "offset": <int>,
                              "totalNumberOfItems": <int>
                            },
                            "preTitle": <str>,
                            "quickPlay": <bool>,
                            "scroll": <bool>,
                            "showMore": {
                              "apiPath": <str>,
                              "title": "View all"
                            },
                            "showTableHeaders": <bool>,
                            "supportsPaging": <bool>,
                            "title": <str>,
                            "type": "TRACK_LIST",
                            "width": <int>
                          }
                        ]
                      },
                      {
                        "modules": [
                          {
                            "description": <str>,
                            "header": <str>,
                            "id": <str>,
                            "layout": <str>,
                            "listFormat": <str>,
                            "pagedList": {
                              "dataApiPath": <str>,
                              "items": [
                                {
                                  "allowStreaming": <bool>,
                                  "artists": [
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
                                  "audioModes": <list[str]>,
                                  "audioQuality": <str>,
                                  "cover": <str>,
                                  "duration": <int>,
                                  "explicit": <bool>,
                                  "id": <int>,
                                  "mediaMetadata": {
                                    "tags": <list[str]>
                                  },
                                  "numberOfTracks": <int>,
                                  "numberOfVideos": <int>,
                                  "payToStream": <bool>,
                                  "releaseDate": <str>,
                                  "streamReady": <bool>,
                                  "streamStartDate": <str>,
                                  "title": <str>,
                                  "upload": <bool>,
                                  "url":<str>,
                                  "vibrantColor": <str>,
                                  "videoCover": <str>
                                }
                              ],
                              "limit": <int>,
                              "offset": <int>,
                              "totalNumberOfItems": <int>
                            },
                            "preTitle": <str>,
                            "quickPlay": <bool>,
                            "scroll": <str>,
                            "showMore": {
                              "apiPath": <str>,
                              "title": "View all"
                            },
                            "supportsPaging": <bool>,
                            "title": <str>,
                            "type": "ALBUM_LIST",
                            "width": <int>
                          }
                        ]
                      },
                      {
                        "modules": [
                          {
                            "description": <str>,
                            "id": <str>,
                            "pagedList": {
                              "dataApiPath": <str>,
                              "items": [
                                {
                                  "item": {
                                    "creators": [],
                                    "description": <str>,
                                    "duration": <int>,
                                    "image": <str>,
                                    "lastItemAddedAt": <str>,
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
                                    "squareImage": <str>,
                                    "title": <str>,
                                    "type": "EDITORIAL",
                                    "url": <str>,
                                    "uuid": <str>
                                  },
                                  "type": "PLAYLIST"
                                }
                              ],
                              "limit": <int>,
                              "offset": <int>,
                              "totalNumberOfItems": <int>
                            },
                            "preTitle": <str>,
                            "quickPlay": <bool>,
                            "scroll": <str>,
                            "showMore": {
                              "apiPath": <str>,
                              "title": "View all"
                            },
                            "supportsPaging": <bool>,
                            "title": <str>,
                            "type": "MIXED_TYPES_LIST",
                            "width": <int>
                          }
                        ]
                      },
                      {
                        "modules": [
                          {
                            "description": <str>,
                            "id": <str>,
                            "layout": <str>,
                            "listFormat": <str>,
                            "pagedList": {
                              "dataApiPath": <str>,
                              "items": [
                                {
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
                                  "artists": [
                                    {
                                      "handle": <str>,
                                      "id": <int>,
                                      "name": <str>,
                                      "picture": <str>,
                                      "type": <str>,
                                      "userId": <int>
                                    }
                                  ],
                                  "djReady": <bool>,
                                  "doublePopularity": <float>,
                                  "duration": <int>,
                                  "explicit": <bool>,
                                  "id": <int>,
                                  "imageId": <str>,
                                  "popularity": <int>,
                                  "releaseDate": <str>,
                                  "stemReady": <bool>,
                                  "streamReady": <bool>,
                                  "streamStartDate": <str>,
                                  "title": <str>,
                                  "trackNumber": <int>,
                                  "type": "Music Video",
                                  "url": <str>,
                                  "version": <str>,
                                  "vibrantColor": <str>,
                                  "volumeNumber": <int>
                                }
                              ],
                              "limit": <int>,
                              "offset": <int>,
                              "totalNumberOfItems": <int>
                            },
                            "preTitle": <str>,
                            "quickPlay": <bool>,
                            "scroll": <str>,
                            "showMore": {
                              "apiPath": <str>,
                              "title": "View all"
                            },
                            "showTableHeaders": <bool>,
                            "supportsPaging": <bool>,
                            "title": <str>,
                            "type": "VIDEO_LIST",
                            "width": <int>
                          }
                        ]
                      },
                      {
                        "modules": [
                          {
                            "description": <str>,
                            "header": <str>,
                            "id": <str>,
                            "layout": <str>,
                            "pagedList": {
                              "dataApiPath": <str>,
                              "items": [
                                {
                                  "artistRoles": [
                                    {
                                      "category": <str>,
                                      "categoryId": <int>
                                    }
                                  ],
                                  "artistTypes": <list[str]>,
                                  "id": <int>,
                                  "mixes": {
                                    "ARTIST_MIX": <str>
                                  },
                                  "name": <str>,
                                  "picture": <str>,
                                  "selectedAlbumCoverFallback": <str>
                                }
                              ],
                              "limit": <int>,
                              "offset": <int>,
                              "totalNumberOfItems": <int>
                            },
                            "preTitle": <str>,
                            "quickPlay": <bool>,
                            "scroll": <str>,
                            "showMore": {
                              "apiPath": <str>,
                              "title": "View all"
                            },
                            "supportsPaging": <bool>,
                            "title": <str>,
                            "type": "ARTIST_LIST",
                            "width": <int>
                          }
                        ]
                      }
                    ],
                    "selfLink": <str>,
                    "title": <str>
                  }
        """

        return self._get_resource_page(
            "artist", artist_id, country_code, device_type=device_type
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_mix_page(
        self,
        mix_id: str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
    ) -> dict[str, Any]:
        """
        Get the TIDAL page layout for a mix.

        Parameters
        ----------
        mix_id : str; positional-only
            TIDAL ID of the mix.

            **Example**: :code:`"000ec0b01da1ddd752ec5dee553d48"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        device_type : str; keyword-only; default: :code:`"BROWSER"`
            Device type.

            .. container::

               * :code:`"BROWSER"` – Web browser.
               * :code:`"DESKTOP"` – Desktop TIDAL application.
               * :code:`"PHONE"` – Mobile TIDAL application.
               * :code:`"TV"` – Smart TV TIDAL application.

        Returns
        -------
        page : dict[str, Any]
            Page layout for the mix.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <str>,
                    "rows": [
                      {
                        "modules": [
                          {
                            "description": <str>,
                            "id": <str>,
                            "mix": {
                              "contentBehavior": <str>,
                              "description": <str>,
                              "descriptionColor": <str>,
                              "detailImages": {
                                "LARGE": {
                                  "height": <int>,
                                  "url": <str>,
                                  "width": <int>
                                },
                                "MEDIUM": {
                                  "height": <int>,
                                  "url": <str>,
                                  "width": <int>
                                },
                                "SMALL": {
                                  "height": <int>,
                                  "url": <str>,
                                  "width": <int>
                                }
                              },
                              "graphic": {
                                "images": [
                                  {
                                    "id": <str>,
                                    "type": "ARTIST",
                                    "vibrantColor": <str>
                                  }
                                ],
                                "text": <str>,
                                "type": "SQUARES_GRID"
                              },
                              "id": <str>,
                              "images": {
                                "LARGE": {
                                  "height": <int>,
                                  "url": <str>,
                                  "width": <int>
                                },
                                "MEDIUM": {
                                  "height": <int>,
                                  "url": <str>,
                                  "width": <int>
                                },
                                "SMALL": {
                                  "height": <int>,
                                  "url": <str>,
                                  "width": <int>
                                }
                              },
                              "master": <bool>,
                              "mixNumber": <int>,
                              "mixType": <str>,
                              "sharingImages": <Any>,
                              "shortSubtitle": <str>,
                              "subTitle": <str>,
                              "subTitleColor": <str>,
                              "title": <str>,
                              "titleColor": <str>
                            },
                            "playbackControls": [
                              {
                                "icon": <str>,
                                "playbackMode": <str>,
                                "shuffle": <bool>,
                                "targetModuleId": <str>,
                                "title": <str>
                              }
                            ],
                            "preTitle":<str>,
                            "title": <str>,
                            "type": "MIX_HEADER",
                            "width": <int>
                          }
                        ]
                      },
                      {
                        "modules": [
                          {
                            "description": <str>,
                            "id": <str>,
                            "layout": <str>,
                            "listFormat": <str>,
                            "pagedList": {
                              "dataApiPath": <str>,
                              "items": [
                                {
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
                                  "artists": [
                                    {
                                      "handle": <str>,
                                      "id": <int>,
                                      "name": <str>,
                                      "picture": <str>,
                                      "type": <str>,
                                      "userId": <int>
                                    }
                                  ],
                                  "audioModes": <list[str]>,
                                  "audioQuality": <str>,
                                  "djReady": <bool>,
                                  "doublePopularity": <float>,
                                  "duration": <int>,
                                  "editable": <bool>,
                                  "explicit": <bool>,
                                  "id": <int>,
                                  "mediaMetadata": {
                                    "tags": <list[str]>
                                  },
                                  "mixes": {
                                    "TRACK_MIX": <str>
                                  },
                                  "payToStream": <bool>,
                                  "popularity": <int>,
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
                                }
                              ],
                              "limit": <int>,
                              "offset": <int>,
                              "totalNumberOfItems": <int>
                            },
                            "preTitle": <str>,
                            "quickPlay": <bool>,
                            "scroll": <str>,
                            "showMore": {
                              "apiPath": <str>,
                              "title": "View all"
                            },
                            "showTableHeaders": <bool>,
                            "supportsPaging": <bool>,
                            "title": <str>,
                            "type": "TRACK_LIST",
                            "width": <int>
                          }
                        ]
                      }
                    ],
                    "selfLink": <str>,
                    "title": <str>
                  }
        """
        return self._get_resource_page(
            "mix", mix_id, country_code, device_type=device_type
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_video_page(
        self,
        video_id: int | str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
    ) -> dict[str, Any]:
        """
        Get the TIDAL page layout for a video.

        Parameters
        ----------
        video_id : int or str; positional-only
            TIDAL ID of the video.

            **Examples**: :code:`53315642`, :code:`"75623239"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        device_type : str; keyword-only; default: :code:`"BROWSER"`
            Device type.

            .. container::

               * :code:`"BROWSER"` – Web browser.
               * :code:`"DESKTOP"` – Desktop TIDAL application.
               * :code:`"PHONE"` – Mobile TIDAL application.
               * :code:`"TV"` – Smart TV TIDAL application.

        Returns
        -------
        page : dict[str, Any]
            Page layout for the video.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <str>,
                    "rows": [
                      {
                        "modules": [
                          {
                            "description": <str>,
                            "id": <str>,
                            "items": [
                              {
                                "artifactId": <str>,
                                "featured": <bool>,
                                "header": <str>,
                                "imageId": <str>,
                                "shortHeader": <str>,
                                "shortSubHeader": <str>,
                                "text": <str>,
                                "type": "VIDEO"
                              }
                            ],
                            "preTitle": <str>,
                            "title": "Featured",
                            "type": "MULTIPLE_TOP_PROMOTIONS",
                            "width": <int>
                          }
                        ]
                      },
                      {
                        "modules": [
                          {
                            "description": <str>,
                            "id": <str>,
                            "layout": <str>,
                            "pagedList": {
                              "dataApiPath": <str>,
                              "items": [
                                {
                                  "creators": <list[Any]>,
                                  "description": <str>,
                                  "duration": <int>,
                                  "image": <str>,
                                  "lastItemAddedAt": <str>,
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
                                  "squareImage": <str>,
                                  "title": <str>,
                                  "type": "EDITORIAL",
                                  "url": <str>,
                                  "uuid": <str>
                                }
                              ],
                              "limit": <int>,
                              "offset": <int>,
                              "totalNumberOfItems": <int>
                            },
                            "playlistStyle": <Any>,
                            "preTitle": <str>,
                            "quickPlay": <bool>,
                            "scroll": <str>,
                            "showMore": {
                              "apiPath": <str>,
                              "title": "View all"
                            },
                            "supportsPaging": <bool>,
                            "title": <str>,
                            "type": "PLAYLIST_LIST",
                            "width": <int>
                          }
                        ]
                      },
                      {
                        "modules": [
                          {
                            "description": <str>,
                            "id": <str>,
                            "layout": <str>,
                            "listFormat": <str>,
                            "pagedList": {
                              "dataApiPath": <str>,
                              "items": [
                                {
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
                                  "artists": [
                                    {
                                      "handle": <str>,
                                      "id": <int>,
                                      "name": <str>,
                                      "picture": <str>,
                                      "type": <str>,
                                      "userId": <int>
                                    }
                                  ],
                                  "djReady": <bool>,
                                  "doublePopularity": <float>,
                                  "duration": <int>,
                                  "explicit": <bool>,
                                  "id": <int>,
                                  "imageId": <str>,
                                  "popularity": <int>,
                                  "releaseDate": <str>,
                                  "stemReady": <bool>,
                                  "streamReady": <bool>,
                                  "streamStartDate": <str>,
                                  "title": <str>,
                                  "trackNumber": <int>,
                                  "type": "Music Video",
                                  "url": <str>,
                                  "version": <str>,
                                  "vibrantColor": <str>,
                                  "volumeNumber": <int>
                                }
                              ],
                              "limit": <int>,
                              "offset": <int>,
                              "totalNumberOfItems": <int>
                            },
                            "preTitle": <str>,
                            "quickPlay": <bool>,
                            "scroll": <str>,
                            "showMore": {
                              "apiPath": <str>,
                              "title": "View all"
                            },
                            "showTableHeaders": <bool>,
                            "supportsPaging": <bool>,
                            "title": <str>,
                            "type": "VIDEO_LIST",
                            "width": <int>
                          }
                        ]
                      }
                    ],
                    "selfLink": <str>,
                    "title": "Videos"
                  }
        """
        return self._get_resource_page(
            "video", video_id, country_code, device_type=device_type
        )

    def _get_resource_page(
        self,
        resource: str,
        resource_id: int | str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
    ) -> dict[str, Any]:
        """
        Get the TIDAL page layout for a specific resource type.

        Parameters
        ----------
        resource : str; positional-only
            Resource type.

            **Valid values**: :code:`"album"`, :code:`"artist"`,
            :code:`"mix"`, :code:`"video"`.

        resource_id : int or str; positional-only
            TIDAL ID of the resource.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        device_type : str; keyword-only; default: :code:`"BROWSER"`
            Device type.

            .. container::

               * :code:`"BROWSER"` – Web browser.
               * :code:`"DESKTOP"` – Desktop TIDAL application.
               * :code:`"PHONE"` – Mobile TIDAL application.
               * :code:`"TV"` – Smart TV TIDAL application.

        Returns
        -------
        page : dict[str, Any]
            Page layout for the specified resource.
        """
        if device_type not in self._DEVICE_TYPES:
            device_types = "', '".join(self._DEVICE_TYPES)
            raise ValueError(
                f"Invalid device type {device_type!r}. "
                f"Valid values: '{device_types}'."
            )
        params = {f"{resource}Id": str(resource_id), "deviceType": device_type}
        self._client._resolve_country_code(country_code, params)
        if resource == "video":
            resource = "videos"
        return self._client._request(
            "GET", f"v1/pages/{resource}", params=params
        ).json()
