from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import PrivateQobuzResourceAPI
from .search import PrivateSearchEndpoints


class PrivateArtistsAPI(PrivateQobuzResourceAPI):
    """
    Artists API endpoints for the private Qobuz API.

    .. important::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    _CONTENT_FILTERS = {"hires", "explicit"}
    _RELEASE_TYPES = {
        "all",
        "album",
        "live",
        "compilation",
        "epSingle",
        "other",
        "download",
        "composer",
    }
    _RELATIONSHIPS = {
        "albums",
        "albums_with_last_release",
        "playlists",
        "tracks_appears_on",
    }

    @TTLCache.cached_method(ttl="popularity")
    def get_artist(
        self,
        artist_id: int | str,
        /,
        *,
        expand: str | list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
        subresource: str = "page",
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for an artist.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Qobuz ID of the artist.

            **Examples**: :code:`865362`, :code:`"21473137"`.

        expand : str or list[str]; keyword-only; optional
            Related resources to include metadata for in the response.
            Only applicable when `subresource` is :code:`"get"`.

            **Valid values**: :code:`"albums"`,
            :code:`"albums_with_last_release"`, :code:`"playlists"`,
            :code:`"tracks_appears_on"`.

            **Examples**: :code:`"playlists"`,
            :code:`"albums,albums_with_last_release"`,
            :code:`["albums", "albums_with_last_release"]`.

        limit : int; keyword-only; optional
            Maximum number of albums to return when :code:`"albums"` or
            :code:`"albums_with_last_release"` is included in the
            `expand` parameter. Only applicable when `subresource` is
            :code:`"get"`.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first album to return when :code:`"albums"` or
            :code:`"albums_with_last_release"` is included in the
            `expand` parameter. Use with `limit` to get the next batch
            of albums. Only applicable when `subresource` is
            :code:`"get"`.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the artist's releases by. Only applicable when
            `subresource` is :code:`"page"`.

            **Valid values**: :code:`"relevant"`, :code:`"release_date"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order. Only applicable when
            `subresource` is :code:`"page"`.

        subresource : str; keyword-only; default: :code:`"page"`
            API subresource to use.

            **Valid values**:

            .. container::

               * :code:`"get"` – Legacy :code:`artist/get` endpoint.
               * :code:`"page"` – Current :code:`artist/page` endpoint.

        Returns
        -------
        artist : dict[str, Any]
            Qobuz content metadata for the artist.

            .. admonition:: Sample responses
               :class: dropdown

               .. code::

                  .. tab:: Current (:code:`subresource="page"`) endpoint

                     {
                       "artist_category": <str>,
                       "biography": {
                         "content": <str>,
                         "language": <str>,
                         "source": None
                       },
                       "id": <int>,
                       "images": {
                         "portrait": {
                           "format": <str>,
                           "hash": <str>
                         }
                       },
                       "last_release": {
                         "artist": {
                           "id": <int>,
                           "name": {
                             "display": <str>
                           }
                         },
                         "artists": [
                           {
                             "id": <int>,
                             "name": <str>,
                             "roles": <list[str]>
                           }
                         ],
                         "audio_info": {
                           "maximum_bit_depth": <int>,
                           "maximum_channel_count": <int>,
                           "maximum_sampling_rate": <float>
                         },
                         "awards": [],
                         "dates": {
                           "download": <str>,
                           "original": <str>,
                           "stream": <str>
                         },
                         "description": <str>,
                         "duration": <int>,
                         "genre": {
                           "id": <int>,
                           "name": <str>,
                           "path": <list[str]>
                         },
                         "id": <str>,
                         "image": {
                           "large": <str>,
                           "small": <str>,
                           "thumbnail": <str>
                         },
                         "label": {
                           "id": <int>,
                           "name": <str>
                         },
                         "parental_warning": <bool>,
                         "release_tags": [],
                         "release_type": <str>,
                         "rights": {
                           "downloadable": <bool>,
                           "hires_purchasable": <bool>,
                           "hires_streamable": <bool>,
                           "purchasable": <bool>,
                           "streamable": <bool>
                         },
                         "title": <str>,
                         "tracks_count": <int>,
                         "version": None
                       },
                       "name": {
                         "display": <str>
                       },
                       "playlists": {
                         "has_more": <bool>,
                         "items": []
                       },
                       "releases": [
                         {
                           "has_more": <bool>,
                           "items": [
                             {
                               "artist": {
                                 "id": <int>,
                                 "name": {
                                   "display": <str>
                                 }
                               },
                               "artists": [
                                 {
                                   "id": <int>,
                                   "name": <str>,
                                   "roles": <list[str]>
                                 }
                               ],
                               "audio_info": {
                                 "maximum_bit_depth": <int>,
                                 "maximum_channel_count": <int>,
                                 "maximum_sampling_rate": <float>
                               },
                               "awards": [],
                               "dates": {
                                 "download": <str>,
                                 "original": <str>,
                                 "stream": <str>
                               },
                               "duration": <int>,
                               "genre": {
                                 "id": <int>,
                                 "name": <str>,
                                 "path": <list[str]>
                               },
                               "id": <str>,
                               "image": {
                                 "large": <str>,
                                 "small": <str>,
                                 "thumbnail": <str>
                               },
                               "label": {
                                 "id": <int>,
                                 "name": <str>
                               },
                               "parental_warning": <bool>,
                               "release_tags": [],
                               "release_type": <str>,
                               "rights": {
                                 "downloadable": <bool>,
                                 "hires_purchasable": <bool>,
                                 "hires_streamable": <bool>,
                                 "purchasable": <bool>,
                                 "streamable": <bool>
                               },
                               "title": <str>,
                               "tracks_count": <int>,
                               "version": <str>,
                             }
                           ],
                           "type": "album"
                         },
                         {
                           "has_more": <bool>,
                           "items": [],
                           "type": "live"
                         },
                         {
                           "has_more": <bool>,
                           "items": [],
                           "type": "compilation"
                         },
                         {
                           "has_more": <bool>,
                           "items": [
                             {
                               "artist": {
                                 "id": <int>,
                                 "name": {
                                   "display": <str>
                                 }
                               },
                               "artists": [
                                 {
                                   "id": <int>,
                                   "name": <str>,
                                   "roles": <list[str]>
                                 }
                               ],
                               "audio_info": {
                                 "maximum_bit_depth": <int>,
                                 "maximum_channel_count": <int>,
                                 "maximum_sampling_rate": <float>
                               },
                               "awards": [],
                               "dates": {
                                 "download": <str>,
                                 "original": <str>,
                                 "stream": <str>,
                               },
                               "duration": <int>,
                               "genre": {
                                 "id": <int>,
                                 "name": <str>,
                                 "path": <list[int]>
                               },
                               "id": <str>,
                               "image": {
                                 "large": <str>,
                                 "small": <str>,
                                 "thumbnail": <str>
                               },
                               "label": {
                                 "id": <int>,
                                 "name": <str>
                               },
                               "parental_warning": <bool>,
                               "release_tags": [],
                               "release_type": <str>,
                               "rights": {
                                 "downloadable": <bool>,
                                 "hires_purchasable": <bool>,
                                 "hires_streamable": <bool>,
                                 "purchasable": <bool>,
                                 "streamable": <bool>
                               },
                               "title": <str>,
                               "tracks_count": <int>,
                               "version": <str>
                             }
                           ],
                           "type": "epSingle"
                         },
                         {
                           "has_more": <bool>,
                           "items": [],
                           "type": "download"
                         },
                         {
                           "has_more": <bool>,
                           "items": [
                             {
                               "artist": {
                                 "id": <int>,
                                 "name": {
                                   "display": <str>
                                 }
                               },
                               "artists": [
                                 {
                                   "id": <int>,
                                   "name": <str>,
                                   "roles": <list[str]>
                                 }
                               ],
                               "audio_info": {
                                 "maximum_bit_depth": <int>,
                                 "maximum_channel_count": <int>,
                                 "maximum_sampling_rate": <float>
                               },
                               "awards": [],
                               "dates": {
                                 "download": <str>,
                                 "original": <str>,
                                 "stream": <str>
                               },
                               "duration": <int>,
                               "genre": {
                                 "id": <int>,
                                 "name": <str>,
                                 "path": <list[int]>
                               },
                               "id": <str>,
                               "image": {
                                 "large": <str>,
                                 "small": <str>,
                                 "thumbnail": <str>
                               },
                               "label": {
                                 "id": <int>,
                                 "name": <str>
                               },
                               "parental_warning": <bool>,
                               "release_tags": [],
                               "release_type": <str>,
                               "rights": {
                                 "downloadable": <bool>,
                                 "hires_purchasable": <bool>,
                                 "hires_streamable": <bool>,
                                 "purchasable": <bool>,
                                 "streamable": <bool>
                               },
                               "title": <str>,
                               "tracks_count": <int>,
                               "version": <str>
                             }
                           ],
                           "type": "other"
                         },
                         {
                           "has_more": <bool>,
                           "items": [],
                           "type": "awardedRelease"
                         }
                       ],
                       "similar_artists": {
                         "has_more": <bool>,
                         "items": [
                           {
                             "id": <int>,
                             "images": {
                               "portrait": {
                                 "format": <str>,
                                 "hash": <str>
                               }
                             },
                             "name": {
                               "display": <str>
                             }
                           }
                         ]
                       },
                       "top_tracks": [
                         {
                           "album": {
                             "genre": {
                               "id": <int>,
                               "name": <str>,
                               "path": <list[int]>
                             },
                             "id": <str>,
                             "image": {
                               "large": <str>,
                               "small": <str>,
                               "thumbnail": <str>
                             },
                             "label": {
                               "id": <int>,
                               "name": <str>
                             },
                             "title": <str>,
                             "version": <str>
                           },
                           "artist": {
                             "id": <int>,
                             "name": {
                               "display": <str>
                             }
                           },
                           "artists": [],
                           "audio_info": {
                             "maximum_bit_depth": <int>,
                             "maximum_channel_count": <int>,
                             "maximum_sampling_rate": <float>
                           },
                           "composer": {
                             "id": <int>,
                             "name": <str>,
                           },
                           "duration": <int>,
                           "id": <int>,
                           "isrc": <str>,
                           "parental_warning": <bool>,
                           "physical_support": {
                             "media_number": <int>,
                             "track_number": <int>
                           },
                           "rights": {
                             "downloadable": <bool>,
                             "hires_purchasable": <bool>,
                             "hires_streamable": <bool>,
                             "previewable": <bool>,
                             "purchasable": <bool>,
                             "sampleable": <bool>,
                             "streamable": <bool>
                           },
                           "title": <str>,
                           "version": <str>,
                           "work": None
                         }
                       ]
                     }

                  .. tab:: Legacy (:code:`subresource="get"`) endpoint

                     {
                       "albums": {
                         "items": [
                           {
                             "articles": [],
                             "artist": {
                               "albums_count": <int>,
                               "id": <int>,
                               "image": None,
                               "name": <str>,
                               "picture": None,
                               "slug": <str>
                             },
                             "artists": [
                               {
                                 "id": <int>,
                                 "name": <str>,
                                 "roles": <list[str]>
                               }
                             ],
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
                               "back": None,
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
                             "media_count": <int>,
                             "parental_warning": <bool>,
                             "popularity": <int>,
                             "previewable": <bool>,
                             "purchasable": <bool>,
                             "purchasable_at": <int>,
                             "qobuz_id": <int>,
                             "release_date_download": <str>,
                             "release_date_original": <str>,
                             "release_date_stream": <str>,
                             "released_at": <int>,
                             "sampleable": <bool>,
                             "slug": <str>,
                             "streamable": <bool>,
                             "streamable_at": <int>,
                             "title": <str>,
                             "tracks_count": <int>,
                             "upc": <str>,
                             "url": <str>,
                             "version": <str>
                           }
                         ],
                         "limit": <int>,
                         "offset": <int>,
                         "total": <int>
                       },
                       "albums_as_primary_artist_count": <int>,
                       "albums_as_primary_composer_count": <int>,
                       "albums_count": <int>,
                       "albums_without_last_release": {
                         "items": [
                           {
                             "articles": [],
                             "artist": {
                               "albums_count": <int>,
                               "id": <int>,
                               "image": None,
                               "name": <str>,
                               "picture": None,
                               "slug": <str>
                             },
                             "artists": [
                               {
                                 "id": <int>,
                                 "name": <str>,
                                 "roles": <list[str]>
                               }
                             ],
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
                               "back": None,
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
                             "media_count": <int>,
                             "parental_warning": <bool>,
                             "popularity": <int>,
                             "previewable": <bool>,
                             "purchasable": <bool>,
                             "purchasable_at": <int>,
                             "qobuz_id": <int>,
                             "release_date_download": <str>,
                             "release_date_original": <str>,
                             "release_date_stream": <str>,
                             "released_at": <int>,
                             "sampleable": <bool>,
                             "slug": <str>,
                             "streamable": <bool>,
                             "streamable_at": <int>,
                             "title": <str>,
                             "tracks_count": <int>,
                             "upc": <str>,
                             "url": <str>,
                             "version": <str>
                           }
                         ],
                         "limit": <int>,
                         "offset": <int>,
                         "total": <int>
                       },
                       "biography": {
                         "content": <str>,
                         "language": <str>,
                         "source": <str>,
                         "summary": <str>,
                       },
                       "id": <int>,
                       "image": {
                         "extralarge": <str>,
                         "large": <str>,
                         "medium": <str>,
                         "mega": <str>,
                         "small": <str>,
                       },
                       "information": None,
                       "name": <str>,
                       "picture": None,
                       "playlists": [
                         {
                           "created_at": <int>,
                           "description": <str>,
                           "duration": <int>,
                           "featured_artists": [
                             {
                               "albums_count": <int>,
                               "id": <int>,
                               "image": None,
                               "name": <str>,
                               "picture": None,
                               "slug": <str>
                             }
                           ],
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
                           "published_from": <int>,
                           "published_to": <int>,
                           "slug": <str>,
                           "stores": <list[str]>,
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
                                 "article_ids": <dict[str, int]>,
                                 "articles": [
                                   {
                                     "currency": <str>,
                                     "description": <str>,
                                     "id": <int>,
                                     "label": <str>,
                                     "price": <float>,
                                     "type": <str>,
                                     "url": <str>,
                                   }
                                 ],
                                 "audio_info": {
                                   "replaygain_track_gain": <float>,
                                   "replaygain_track_peak": <float>
                                 },
                                 "composer": {
                                   "id": <int>,
                                   "name": <str>,
                                 },
                                 "copyright": <str>,
                                 "description": [],
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
                       ],
                       "similar_artist_ids": <list[int]>,
                       "slug": <str>,
                       "tracks_appears_on": {
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
                             "articles": [],
                             "audio_info": {
                               "replaygain_track_gain": <float>,
                               "replaygain_track_peak": <float>
                             },
                             "composer": {
                               "id": <int>,
                               "name": <str>
                             },
                             "copyright": <str>,
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
                       }
                     }
        """
        self._validate_qobuz_ids(artist_id, _recursive=False)
        params = {"artist_id": artist_id}
        if subresource == "page":
            if sort_by is not None:
                if sort_by not in (
                    sort_fields := {"relevant", "release_date"}
                ):
                    sort_fields_str = "', '".join(sorted(sort_fields))
                    raise ValueError(
                        f"Invalid sort field {sort_by!r}. "
                        f"Valid values: '{sort_fields_str}'."
                    )
                params["order"] = sort_by
            if descending is not None:
                self._validate_type("descending", descending, bool)
                params["orderDirection"] = "desc"
            return self._client._request(
                "GET", "artist/page", params=params
            ).json()
        if expand is not None:
            params["extra"] = self._prepare_expand(expand)
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request("GET", "artist/get", params=params).json()

    @TTLCache.cached_method(ttl="daily")
    def get_artist_releases(
        self,
        artist_id: int | str,
        /,
        *,
        release_types: str | list[str] | None = None,
        content_filters: str | list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
        include_tracks: bool = False,
        track_limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for an artist's releases.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access the :code:`GET /artist/getReleasesGrid` and
                 :code:`GET /artist/getReleasesList` endpoint.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Qobuz ID of the artist.

            **Examples**: :code:`865362`, :code:`"21473137"`.

        release_types : str or list[str]; keyword-only; optional
            Release types to include in the response.

            **Valid values**: :code:`"all"`, :code:`"album"`,
            :code:`"live"`, :code:`"compilation"`, :code:`"epSingle"`,
            :code:`"other"`, :code:`"download"`, :code:`"composer"`.

        content_filters : str or list[str]; keyword-only; optional
            Content filters to apply to the releases.

            **Valid values**: :code:`"hires"`, :code:`"explicit"`.

        limit : int; keyword-only; optional
            Maximum number of releases to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first release to return. Use with `limit` to
            get the next batch of releases.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the releases by.

            **Valid values**: :code:`"relevant"`,
            :code:`"release_date"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

        include_tracks : bool; keyword-only; default: :code:`False`
            Whether to include tracks in the response.

        track_limit : int; keyword-only; optional
            Maximum number of tracks to include per release when
            `include_tracks` is :code:`True`.

            **Valid range**: :code:`1` to :code:`30`.

            **API default**: :code:`10`.

        Returns
        -------
        releases : dict[str, Any]
            Page of Qobuz content metadata for the artist's releases.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "has_more": <bool>,
                    "items": [
                      {
                        "artist": {
                          "id": <int>,
                          "name": {
                            "display": <str>
                          }
                        },
                        "artists": [
                          {
                            "id": <int>,
                            "name": <str>,
                            "roles": <list[str]>
                          }
                        ],
                        "audio_info": {
                          "maximum_bit_depth": <int>,
                          "maximum_channel_count": <int>,
                          "maximum_sampling_rate": <float>
                        },
                        "awards": [],
                        "dates": {
                          "download": <str>,
                          "original": <str>,
                          "stream": <str>,
                        },
                        "duration": <int>,
                        "genre": {
                          "id": <int>,
                          "name": <str>,
                          "path": <list[int]>,
                        },
                        "id": <str>,
                        "image": {
                          "large": <str>,
                          "small": <str>,
                          "thumbnail": <str>
                        },
                        "label": {
                          "id": <int>,
                          "name": <str>
                        },
                        "parental_warning": <bool>,
                        "release_tags": [],
                        "release_type": <str>,
                        "rights": {
                          "downloadable": <bool>,
                          "hires_purchasable": <bool>,
                          "hires_streamable": <bool>,
                          "purchasable": <bool>,
                          "streamable": <bool>
                        },
                        "title": <str>,
                        "tracks": {
                          "has_more": <bool>,
                          "items": [
                            {
                              "artist": {
                                "id": <int>,
                                "name": {
                                  "display": <str>
                                }
                              },
                              "artists": [],
                              "audio_info": {
                                "maximum_bit_depth": <int>,
                                "maximum_channel_count": <int>,
                                "maximum_sampling_rate": <float>
                              },
                              "composer": {
                                "id": <int>,
                                "name": <str>,
                              },
                              "duration": <int>,
                              "id": <int>,
                              "isrc": <str>,
                              "parental_warning": <bool>,
                              "physical_support": {
                                "media_number": <int>,
                                "track_number": <int>
                              },
                              "rights": {
                                "downloadable": <bool>,
                                "hires_purchasable": <bool>,
                                "hires_streamable": <bool>,
                                "previewable": <bool>,
                                "purchasable": <bool>,
                                "sampleable": <bool>,
                                "streamable": <bool>
                              },
                              "title": <str>,
                              "version": <str>,
                              "work": None
                            }
                          ]
                        },
                        "tracks_count": <int>,
                        "version": <str>,
                      }
                    ]
                  }
        """
        self._client._require_authentication("artists.get_artist_releases")
        self._validate_qobuz_ids(artist_id, _recursive=False)
        params = {"artist_id": artist_id}
        if release_types is not None:
            params["release_type"] = self._prepare_comma_separated_values(
                "release type", release_types, self._RELEASE_TYPES
            )
        if content_filters is not None:
            params["filter"] = self._prepare_comma_separated_values(
                "content filter", content_filters, self._CONTENT_FILTERS
            )
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        if sort_by is not None:
            if sort_by not in (sort_fields := {"relevant", "release_date"}):
                sort_fields_str = "', '".join(sorted(sort_fields))
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. "
                    f"Valid values: '{sort_fields_str}'."
                )
            params["order"] = sort_by
        if descending is not None:
            self._validate_type("descending", descending, bool)
            params["orderDirection"] = "desc" if descending else "asc"
        if include_tracks:
            if track_limit is not None:
                self._validate_number("track_size", track_limit, int, 1, 30)
                params["track_size"] = track_limit
            return self._client._request(
                "GET", "artist/getReleasesList", params=params
            ).json()
        return self._client._request(
            "GET", "artist/getReleasesGrid", params=params
        ).json()

    @TTLCache.cached_method(ttl="popularity")
    def get_similar_artists(
        self,
        artist_id: int | str,
        /,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for other artists that are similar
        to an artist.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Qobuz ID of the artist.

            **Examples**: :code:`865362`, :code:`"21473137"`.

        limit : int; keyword-only; optional
            Maximum number of artists to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first artist to return. Use with `limit` to get
            the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        artists : dict[str, Any]
            Page of Qobuz content metadata for similar artists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "artists": {
                      "items": [
                        {
                          "albums_count": <int>,
                          "id": <int>,
                          "image": {
                            "extralarge": <str>,
                            "large": <str>,
                            "medium": <str>,
                            "mega": <str>,
                            "small": <str>
                          },
                          "name": <str>,
                          "picture": <str>,
                          "slug": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    }
                  }
        """
        self._validate_qobuz_ids(artist_id, _recursive=False)
        params = {"artist_id": artist_id}
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "artist/getSimilarArtists", params=params
        ).json()

    def get_featured_artists(
        self,
        genre_ids: int | str | list[int | str] | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for featured albums.

        Parameters
        ----------
        genre_ids : int, str, or list[int | str]; optional
            Qobuz IDs of the genres used to filter the featured artists
            toreturn.

            **Examples**: :code:`10`, :code:`"64"`, :code:`"10,64"`,
            :code:`[10, "64"]`.

        limit : int; keyword-only; optional
            Maximum number of artists to return per item type.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first artist to return per item type. Use with
            `limit` to get the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        artists : dict[str, Any]
            Page of Qobuz content metadata for the featured artists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "artists": {
                      "items": [
                        {
                          "albums_count": <int>,
                          "id": <int>,
                          "image": {
                            "extralarge": <str>,
                            "large": <str>,
                            "medium": <str>,
                            "mega": <str>,
                            "small": <str>
                          },
                          "name": <str>,
                          "picture": <str>,
                          "slug": <str>
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    }
                  }
        """
        return self._client.catalog.get_featured(
            "artists", genre_ids=genre_ids, limit=limit, offset=offset
        )

    def follow_artists(self, artist_ids: list[int | str], /) -> None:
        """
        Follow one or more artists.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        artist_ids : int, str, or list[int | str]; positional-only
            Qobuz IDs of the artists.

            **Examples**: :code:`865362`, :code:`"21473137"`,
            :code:`"865362,21473137"`, :code:`[865362, "21473137"]`.

        Returns
        -------
        response : dict[str, str]
            API JSON response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        return self._client.favorites.save(artist_ids=artist_ids)

    def unfollow_artists(self, artist_ids: list[int | str], /) -> None:
        """
        Unfollow one or more artists.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        artist_ids : int, str, or list[int | str]; positional-only
            Qobuz IDs of the artists.

            **Examples**: :code:`865362`, :code:`"21473137"`,
            :code:`"865362,21473137"`, :code:`[865362, "21473137"]`.

        Returns
        -------
        response : dict[str, str]
            API JSON response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        return self._client.favorites.remove_saved(artist_ids=artist_ids)

    def get_my_followed_artists(
        self,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get the current user's followed artists.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access and manage your library.

        Parameters
        ----------
        limit : int; keyword-only; optional
            Maximum number of artists to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first artist to return. Use with `limit` to get
            the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        artists : dict[str, Any]
            Page of Qobuz content metadata for artists in the user's
            favorites.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "artists": {
                      "items": [
                        {
                          "albums_count": <int>,
                          "favorited_at": <int>,
                          "id": <int>,
                          "image": {
                            "extralarge": <str>,
                            "large": <str>,
                            "medium": <str>,
                            "mega": <str>,
                            "small": <str>,
                          },
                          "name": <str>,
                          "slug": <str>
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
        return self._client.favorites.get_my_saved(
            "artists", limit=limit, offset=offset
        )

    def is_following_artist(self, artist_id: int | str, /) -> dict[str, bool]:
        """
        Check whether the current user is following a specific artist.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Qobuz ID of the artist.

            **Examples**: :code:`865362`, :code:`"21473137"`.

        Returns
        -------
        is_following : dict[str, bool]
            Whether the current user follows the artist.

            **Sample response**: :code:`{"status": <bool>}`.
        """
        return self._client.favorites.is_saved("artist", artist_id)

    def toggle_artist_followed(
        self, artist_id: int | str, /
    ) -> dict[str, str]:
        """
        Toggle the follow status of an artist.

        Parameters
        ----------
        artist_id : int or str; positional-only
            Qobuz ID of the artist.

            **Examples**: :code:`865362`, :code:`"21473137"`.

        Returns
        -------
        response : dict[str, str]
            API JSON response.

            **Sample response**: :code:`{"status": "success"}`.
        """
        return self._client.favorites.toggle_saved("artist", artist_id)

    @_copy_docstring(PrivateSearchEndpoints.search_artists)
    def search_artists(
        self,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.search.search_artists(
            query, limit=limit, offset=offset
        )
