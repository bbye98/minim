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

    _client: "PrivateTIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_album_page(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
        locale: str | None = None,
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

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

            **API default**: :code:`"en_US"` – English (U.S.).

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
                                  "handle": None,
                                  "id": <int>,
                                  "name": <str>,
                                  "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                                  "type": <str>,
                                  "userId": <int>
                                }
                              ],
                              "audioModes": <list[str]>,
                              "audioQuality": <str>,
                              "copyright": <str>,
                              "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
                              "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                              "title": <str>,
                              "type": "ALBUM",
                              "upload": <bool>,
                              "url": <str>,
                              "version": <str>,
                              "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
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
                            "listFormat": <str>,
                            "pagedList": {
                              "dataApiPath": <str>,
                              "items": [
                                {
                                  "item": {
                                    "accessType": <str>,
                                    "adSupportedStreamReady": <bool>,
                                    "album": {
                                      "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                                      "id": <int>,
                                      "releaseDate": <str>,
                                      "title": <str>,
                                      "url": <str>,
                                      "vibrantColor": "#rrggbb",
                                      "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
                                    },
                                    "allowStreaming": <bool>,
                                    "artists": [
                                      {
                                        "handle": None,
                                        "id": <int>,
                                        "name": <str>,
                                        "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
                                    "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
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
                                      "handle": None,
                                      "id": <int>,
                                      "name": <str>,
                                      "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                                      "type": <str>,
                                      "userId": <int>
                                    }
                                  ],
                                  "audioModes": <list[str]>,
                                  "audioQuality": <str>,
                                  "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
                                  "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                                  "title": <str>,
                                  "upload": <bool>,
                                  "url": <str>,
                                  "vibrantColor": "#rrggbb",
                                  "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
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
                                  "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
        return self._get_entity_page(
            "album",
            album_id,
            country_code=country_code,
            device_type=device_type,
            locale=locale,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_page(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
        locale: str | None = None,
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

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

            **API default**: :code:`"en_US"` – English (U.S.).

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
                              "handle": None,
                              "id": <int>,
                              "mixes": {
                                "ARTIST_MIX": <str>
                              },
                              "name": <str>,
                              "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
                                    "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                                    "id": <int>,
                                    "releaseDate": <str>,
                                    "title": <str>,
                                    "url": <str>,
                                    "vibrantColor": "#rrggbb",
                                    "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
                                  },
                                  "allowStreaming": <bool>,
                                  "artists": [
                                    {
                                      "handle": None,
                                      "id": <int>,
                                      "name": <str>,
                                      "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
                                  "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
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
                                      "handle": None,
                                      "id": <int>,
                                      "name": <str>,
                                      "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                                      "type": <str>,
                                      "userId": <int>
                                    }
                                  ],
                                  "audioModes": <list[str]>,
                                  "audioQuality": <str>,
                                  "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
                                  "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                                  "title": <str>,
                                  "upload": <bool>,
                                  "url":<str>,
                                  "vibrantColor": "#rrggbb",
                                  "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
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
                                        "handle": None,
                                        "id": <int>,
                                        "name": <str>,
                                        "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
                                    "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                                    "id": <int>,
                                    "title": <str>,
                                    "vibrantColor": "#rrggbb",
                                    "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
                                  },
                                  "allowStreaming": <bool>,
                                  "artists": [
                                    {
                                      "handle": None,
                                      "id": <int>,
                                      "name": <str>,
                                      "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                                      "type": <str>,
                                      "userId": <int>
                                    }
                                  ],
                                  "djReady": <bool>,
                                  "doublePopularity": <float>,
                                  "duration": <int>,
                                  "explicit": <bool>,
                                  "id": <int>,
                                  "imageId": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                                  "popularity": <int>,
                                  "releaseDate": <str>,
                                  "stemReady": <bool>,
                                  "streamReady": <bool>,
                                  "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                                  "title": <str>,
                                  "trackNumber": <int>,
                                  "type": "Music Video",
                                  "url": <str>,
                                  "version": <str>,
                                  "vibrantColor": "#rrggbb",
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
                                  "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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

        return self._get_entity_page(
            "artist",
            artist_id,
            country_code=country_code,
            device_type=device_type,
            locale=locale,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_mix_page(
        self,
        mix_id: str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
        locale: str | None = None,
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

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

            **API default**: :code:`"en_US"` – English (U.S.).

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
                                    "vibrantColor": "#rrggbb"
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
                                    "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                                    "id": <int>,
                                    "releaseDate": <str>,
                                    "title": <str>,
                                    "url": <str>,
                                    "vibrantColor": "#rrggbb",
                                    "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
                                  },
                                  "allowStreaming": <bool>,
                                  "artists": [
                                    {
                                      "handle": None,
                                      "id": <int>,
                                      "name": <str>,
                                      "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
                                  "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
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
        return self._get_entity_page(
            "mix",
            mix_id,
            country_code=country_code,
            device_type=device_type,
            locale=locale,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_personalized_mixes_page(
        self,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
        locale: str | None = None,
    ) -> dict[str, Any]:
        """
        Get the TIDAL page layout for personalized mixes.

        Parameters
        ----------
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

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

            **API default**: :code:`"en_US"` – English (U.S.).

        Returns
        -------
        page : dict[str, Any]
            Page layout for the personalized mixes.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "id": <str>,
                    "rows": [
                      {
                        "modules": [
                          {
                            "collapse": <bool>,
                            "description": <str>,
                            "icon": <str>,
                            "id": <str>,
                            "preTitle": <str>,
                            "text":<str>,
                            "title": <str>,
                            "type": "TEXT_BLOCK",
                            "width": <int>
                          }
                        ]
                      }
                    ],
                    "selfLink": <str>,
                    "title": <str>
                  }
        """
        return self._get_entity_page(
            "my_collection_my_mixes",
            country_code=country_code,
            device_type=device_type,
            locale=locale,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_video_page(
        self,
        video_id: int | str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
        locale: str | None = None,
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

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

            **API default**: :code:`"en_US"` – English (U.S.).

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
                                "imageId": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                                "shortHeader": <str>,
                                "shortSubHeader": <str>,
                                "text": <str>,
                                "type": "VIDEO"
                              }
                            ],
                            "preTitle": <str>,
                            "title": <str>,
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
                                      "handle": None,
                                      "id": <int>,
                                      "name": <str>,
                                      "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
                                    "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                                    "id": <int>,
                                    "title": <str>,
                                    "vibrantColor": "#rrggbb",
                                    "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
                                  },
                                  "allowStreaming": <bool>,
                                  "artists": [
                                    {
                                      "handle": None,
                                      "id": <int>,
                                      "name": <str>,
                                      "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                                      "type": <str>,
                                      "userId": <int>
                                    }
                                  ],
                                  "djReady": <bool>,
                                  "doublePopularity": <float>,
                                  "duration": <int>,
                                  "explicit": <bool>,
                                  "id": <int>,
                                  "imageId": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                                  "popularity": <int>,
                                  "releaseDate": <str>,
                                  "stemReady": <bool>,
                                  "streamReady": <bool>,
                                  "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
                                  "title": <str>,
                                  "trackNumber": <int>,
                                  "type": "Music Video",
                                  "url": <str>,
                                  "version": <str>,
                                  "vibrantColor": "#rrggbb",
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
        return self._get_entity_page(
            "video",
            video_id,
            country_code=country_code,
            device_type=device_type,
            locale=locale,
        )

    def _get_entity_page(
        self,
        entity_type: str,
        entity_id: int | str | None = None,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
        locale: str | None = None,
    ) -> dict[str, Any]:
        """
        Get the TIDAL page layout for a specific entity.

        Parameters
        ----------
        entity_type : str; positional-only
            Entity type.

            **Valid values**: :code:`"album"`, :code:`"artist"`,
            :code:`"mix"`, :code:`"my_collection_my_mixes"`,
            :code:`"video"`.

        entity_id : int or str; positional-only; optional
            TIDAL ID of the entity. Optional only when
            :code:`entity_type="my_collection_my_mixes"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        device_type : str; keyword-only; default: :code:`"BROWSER"`
            Device type.

            .. container::

               * :code:`"BROWSER"` – Web browser.
               * :code:`"DESKTOP"` – Desktop TIDAL application.
               * :code:`"PHONE"` – Mobile TIDAL application.
               * :code:`"TV"` – Smart TV TIDAL application.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

            **API default**: :code:`"en_US"` – English (U.S.).

        Returns
        -------
        page : dict[str, Any]
            Page layout for the specified resource.
        """
        if device_type not in self._client._DEVICE_TYPES:
            device_types = "', '".join(self._client._DEVICE_TYPES)
            raise ValueError(
                f"Invalid device type {device_type!r}. "
                f"Valid values: '{device_types}'."
            )
        params = {"deviceType": device_type}
        self._client._resolve_country_code(country_code, params=params)
        if entity_id is not None:
            params[f"{entity_type}Id"] = str(entity_id)
        if locale is not None:
            self._client._validate_type("locale", locale, str)
            params["locale"] = locale
        if entity_type == "video":
            entity_type = "videos"
        return self._client._request(
            "GET", f"v1/pages/{entity_type}", params=params
        ).json()
