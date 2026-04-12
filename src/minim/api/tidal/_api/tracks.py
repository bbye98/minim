from __future__ import annotations
from typing import TYPE_CHECKING

from ...._types import COLLECTION_TYPES, ORDERED_COLLECTION_TYPES
from ..._shared import TTLCache, _copy_docstring
from ._shared import TIDALResourceAPI
from .search import SearchAPI
from .users import UsersAPI

if TYPE_CHECKING:
    from typing import Any

    from ...._types import Collection


class TracksAPI(TIDALResourceAPI):
    """
    Tracks and Track Manifests API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`~minim.api.tidal.TIDALAPIClient`
       and should not be instantiated directly.
    """

    _FORMATS = {"HEAACV1", "AACLC", "FLAC", "FLAC_HIRES", "EAC3_JOC"}
    _MANIFEST_TYPES = {"HLS", "MPEG_DASH"}
    _RELATIONSHIPS = {
        "albums",
        "artists",
        "credits",
        "download",
        "genres",
        "lyrics",
        "metadataStatus",
        "owners",
        "priceConfig",
        "providers",
        "radio",
        "shares",
        "similarTracks",
        "sourceFile",
        "suggestedTracks",
        "trackStatistics",
        "usageRules",
    }
    _SORT_FIELDS = {"createdAt", "title"}
    _URI_SCHEMES = {"DATA", "HTTPS"}
    _USAGES = {"DOWNLOAD", "PLAYBACK"}

    __slots__ = ()

    @classmethod
    def _prepare_formats(cls, formats: str | Collection[str], /) -> list[str]:
        """
        Validate, normalize and serialize audio formats.

        Parameters
        ----------
        formats : str or Collection[str]; positional-only
            Audio formats.

            **Valid values**: :code:`"HEAACV1"`, :code:`"AACLC"`,
            :code:`"FLAC"`, :code:`"FLAC_HIRES"`, :code:`"EAC3_JOC"`.

        Returns
        -------
        formats : list[str]
            List of audio formats.
        """
        if isinstance(formats, str):
            formats = cls._prepare_string("formats", formats)
            if formats not in cls._FORMATS:
                raise ValueError(
                    f"Invalid audio format {formats!r}. Valid values: "
                    f"{cls._join_values(cls._FORMATS)}."
                )
            return formats

        if isinstance(formats, COLLECTION_TYPES):
            return [cls._prepare_formats(format_) for format_ in formats]

        raise TypeError(
            "`formats` must be `None`, a string, or a collection of strings."
        )

    @TTLCache.cached_method(ttl="hourly")
    def get_track_media_info(
        self,
        track_id: int | str,
        /,
        *,
        manifest_type: str = "MPEG_DASH",
        formats: str | Collection[str] | None = None,
        uri_scheme: str = "HTTPS",
        intent: str = "PLAYBACK",
        adaptive: bool = True,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Track Manifests > Get Single Track Manifest
        <https://tidal-music.github.io/tidal-api-reference/#
        /trackManifests/get_trackManifests__id_>`_: Get TIDAL media
        information for a track.

        .. admonition:: Subscription
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 TIDAL streaming plan
                    Stream full-length and high-resolution audio.
                    `Learn more. <https://tidal.com/pricing>`__

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"251380837"`.

        manifest_type : str; keyword-only; default: :code:`"MPEG_DASH"`
            Streaming protocol to use for the manifest.

            **Valid values**:

            * :code:`"HLS"` – HTTP Live Streaming.
            * :code:`"MPEG_DASH"` – Dynamic Adaptive Streaming over
              HTTP.

        formats : str or Collection[str]; keyword-only; \
        default: :code:`None`
            Requested audio formats. If a collection, the highest 
            quality format available will be returned. If not specified,
            all audio formats are requested.

            **Valid values**: :code:`"HEAACV1"`, :code:`"AACLC"`,
            :code:`"FLAC"`, :code:`"FLAC_HIRES"`, :code:`"EAC3_JOC"`.

        uri_scheme : str; keyword-only; default: :code:`"HTTPS"`
            Whether to return a remote URL or a Base64 manifest.

            **Valid values**:

            * :code:`"HTTPS"` – Remote URL for the manifest.
            * :code:`"DATA"` – Base64 manifest.

        intent : str; keyword-only; default: :code:`"PLAYBACK"`
            Playback mode or intended use of the track.

            **Valid values**:

            * :code:`"DOWNLOAD"` – Offline download.
            * :code:`"PLAYBACK"` – Streaming playback.

        adaptive : bool; keyword-only; default: :code:`True`
            Whether the manifest should support adaptive bitrate
            switching based on network conditions.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        media_info : dict[str, Any]
            TIDAL media information for the track.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "data": {
                      "attributes": {
                        "albumAudioNormalizationData": {
                          "peakAmplitude": <float>,
                          "replayGain": <float>
                        },
                        "formats": <list[str]>,
                        "hash": <str>,
                        "previewReason": <str>,
                        "trackAudioNormalizationData": {
                          "peakAmplitude": <float>,
                          "replayGain": <float>
                        },
                        "trackPresentation": <str>,
                        "uri": <str>
                      },
                      "id": <str>,
                      "type": "trackManifests"
                    },
                    "links": {
                      "self": <str>
                    }
                  }
        """
        params = {}
        manifest_type = self._prepare_string(
            "manifest_type", manifest_type
        ).upper()
        if manifest_type not in self._MANIFEST_TYPES:
            raise ValueError(
                f"Invalid manifest type {manifest_type!r}. Valid "
                f"values: {self._join_values(self._MANIFEST_TYPES)}."
            )
        params["manifestType"] = manifest_type
        params["formats"] = (
            sorted(self._FORMATS)
            if formats is None
            else self._prepare_formats(formats)
        )
        uri_scheme = self._prepare_string("uri_scheme", uri_scheme).upper()
        if uri_scheme not in self._URI_SCHEMES:
            raise ValueError(
                f"Invalid URI scheme {uri_scheme!r}. Valid values: "
                f"{self._join_values(self._URI_SCHEMES)}."
            )
        params["uriScheme"] = uri_scheme
        intent = self._prepare_string("intent", intent).upper()
        if intent not in self._USAGES:
            raise ValueError(
                f"Invalid intent {intent!r}. Valid values: "
                f"{self._join_values(self._USAGES)}."
            )
        params["usage"] = intent
        self._validate_type("adaptive", adaptive, bool)
        params["adaptive"] = adaptive
        return self._get_resources(
            "trackManifests", track_id, share_code=share_code, params=params
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_tracks(
        self,
        track_ids: int | str | Collection[int | str] | None = None,
        /,
        *,
        isrcs: str | Collection[str] | None = None,
        owner_ids: int | str | Collection[int | str] | None = None,
        country_code: str | None = None,
        expand: str | Collection[str] | None = None,
        cursor: str | None = None,
        sort_by: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Single Track <https://tidal-music.github.io
        /tidal-api-reference/#/tracks/get_tracks__id_>`_: Get TIDAL
        catalog information for a track․
        `Tracks > Get Multiple Tracks <https://tidal-music.github.io
        /tidal-api-reference/#/tracks/get_tracks>`_: Get TIDAL catalog
        information for multiple tracks.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 User authentication
                    Access information for a resource's owners.

        .. important::

           Exactly one of `track_ids`, `isrcs`, or `owner_ids` must
           be provided. When `isrcs` or `owner_ids` is specified, the
           request will always be sent to the endpoint for multiple
           tracks.

        Parameters
        ----------
        track_ids : int, str, or Collection[int | str]; \
        positional-only; optional
            TIDAL IDs of the tracks.

            **Examples**: :code:`46369325`, :code:`"75413016"`,
            :code:`[46369325, "75413016"]`.

        isrcs : str or Collection[str]; keyword-only; optional
            International Standard Recording Codes (ISRCs) of the
            tracks.

            **Examples**: :code:`"QMJMT1701237"`,
            :code:`["QMJMT1701237", "USAT21404265"]`.

        owner_ids : int, str, or Collection[int | str]; keyword-only; \
        optional
            TIDAL IDs of the track resources' owners.

            **Examples**: :code:`123456`, :code:`"123456"`,
            :code:`[123456, "654321"]`.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        expand : str or Collection[str]; keyword-only; optional
            Related resources to include metadata for in the response.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"credits"`, :code:`"download"`, :code:`"genres"`, 
            :code:`"lyrics"`, :code:`"metadataStatus"`, 
            :code:`"owners"`, :code:`"priceConfig"`, 
            :code:`"providers"`, :code:`"radio"`, :code:`"replacement"`,
            :code:`"shares"`, :code:`"similarTracks"`, 
            :code:`"sourceFile"`, :code:`"suggestedTracks"`,
            :code:`"trackStatistics"`, :code:`"usageRules"`.

            **Examples**: :code:`"lyrics"`,
            :code:`["albums", "artists"]`.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results when requesting
            multiple tracks.

            **Example**: :code:`"3nI1Esi"`.

        sort_by : str; keyword-only; optional
            Field to sort the tracks by.

            **Valid values**: :code:`"createdAt"`, :code:`"title"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        tracks : dict[str, Any]
            Page of TIDAL metadata for the tracks.

            .. admonition:: Sample responses
               :class: response dropdown

               .. tab-set::

                  .. tab-item:: Single track

                     .. code-block::

                        {
                          "data": {
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
                              "genres": {
                                "data": [],
                                "links": {
                                  "self": <str>
                                }
                              },
                              "lyrics": {
                                "data": [],
                                "links": {
                                  "self": <str>
                                }
                              },
                              "owners": {
                                "data": [],
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
                              "radio": {
                                "data": [
                                  {
                                    "id": <str>,
                                    "type": "playlists"
                                  }
                                ],
                                "links": {
                                  "self": <str>
                                }
                              },
                              "shares": {
                                "data": [],
                                "links": {
                                  "self": <str>
                                }
                              },
                              "similarTracks": {
                                "data": [
                                  {
                                    "id": <str>,
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
                                "playlistType": "MIX"
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
                                "name": <str>
                              },
                              "id": <str>,
                              "type": "providers"
                            },
                            {
                              "attributes": {
                                "accessType": <str>,
                                "availability": <list[str]>,
                                "bpm": <float>,
                                "copyright": {
                                  "text": <str>
                                },
                                "createdAt": <str>,
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

                  .. tab-item:: Multiple tracks

                     .. code-block::

                        {
                          "data": [
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
                                "genres": {
                                  "data": [],
                                  "links": {
                                    "self": <str>
                                  }
                                },
                                "lyrics": {
                                  "data": [],
                                  "links": {
                                    "self": <str>
                                  }
                                },
                                "owners": {
                                  "data": [],
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
                                "radio": {
                                  "data": [
                                    {
                                      "id": <str>,
                                      "type": "playlists"
                                    }
                                  ],
                                  "links": {
                                    "self": <str>
                                  }
                                },
                                "shares": {
                                  "data": [],
                                  "links": {
                                    "self": <str>
                                  }
                                },
                                "similarTracks": {
                                  "data": [
                                    {
                                      "id": <str>,
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
                                "playlistType": "MIX"
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
                                "name": <str>
                              },
                              "id": <str>,
                              "type": "providers"
                            },
                            {
                              "attributes": {
                                "accessType": <str>,
                                "availability": <list[str]>,
                                "bpm": <float>,
                                "copyright": {
                                  "text": <str>
                                },
                                "createdAt": <str>,
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
        if sum(arg is not None for arg in (track_ids, isrcs, owner_ids)) != 1:
            raise ValueError(
                "Exactly one of `track_ids`, `isrcs`, or "
                "`owner_ids` must be provided."
            )
        params = {}
        if isrcs is not None:
            if isinstance(isrcs, str):
                isrcs = self._prepare_isrc(isrcs)
            elif isinstance(isrcs, COLLECTION_TYPES):
                isrcs = [self._prepare_isrc(isrc) for isrc in isrcs]
            else:
                raise ValueError(
                    "`isrcs` must be a string or a collection of strings."
                )
            params["filter[isrc]"] = isrcs
        elif owner_ids is not None:
            self._validate_tidal_ids(owner_ids)
            params["filter[owners.id]"] = (
                owner_ids
                if isinstance(owner_ids, ORDERED_COLLECTION_TYPES)
                else sorted(owner_ids)
            )
        if sort_by is not None:
            self._process_sort(
                sort_by,
                prefix="",
                sort_fields=self._SORT_FIELDS,
                params=params,
            )
        return self._get_resources(
            "tracks",
            track_ids,
            country_code=country_code,
            expand=expand,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_track_albums(
        self,
        track_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Albums Relationship <https://tidal-music.github.io
        /tidal-api-reference/#/tracks
        /get_tracks__id__relationships_albums>`_: Get TIDAL catalog
        information for albums containing a track.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the albums containing the
            track.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        albums : dict[str, Any]
            Page of TIDAL metadata for the albums containing the track.

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
            "tracks",
            track_id,
            "albums",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_track_artists(
        self,
        track_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Artists Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/tracks
        /get_tracks__id__relationships_artists>`_: Get TIDAL catalog
        information for the artists of a track.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the track's artists.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        artists : dict[str, Any]
            Page of TIDAL metadata for the track's artists.

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
            "tracks",
            track_id,
            "artists",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_owners(
        self,
        track_id: int | str,
        /,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Owners Relationship <https://tidal-music.github.io
        /tidal-api-reference/#/tracks
        /get_tracks__id__relationships_owners>`_: Get TIDAL profile
        information for the owners of a track resource.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the owners.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        owners : dict[str, Any]
            Page of TIDAL profile information for the track resource's
            owners.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

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
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "owners",
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_providers(
        self,
        track_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Providers Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/tracks
        /get_tracks__id__relationships_providers>`_: Get TIDAL catalog
        information for the providers of a track.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the track's providers.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        providers : dict[str, Any]
            Page of TIDAL metadata for the track's providers.

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
            "tracks",
            track_id,
            "providers",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="daily")
    def get_track_mix(
        self,
        track_id: int | str,
        /,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Radio Relationship <https://tidal-music.github.io
        /tidal-api-reference/#/tracks
        /get_tracks__id__relationships_radio>`_: Get TIDAL catalog
        information for a track's mix.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the track's mix.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        mix : dict[str, Any]
            Page of TIDAL metadata for the track's mix.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "data": [
                      {
                        "id": <str>,
                        "type": "playlists"
                      }
                    ],
                    "included": [
                      {
                        "attributes": {
                          "accessType": <str>,
                          "bounded": <bool>,
                          "createdAt": <str>,
                          "description": <str>,
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
                          "playlistType": "MIX"
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
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "radio",
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="popularity")
    def get_similar_tracks(
        self,
        track_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Similar Tracks Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/tracks
        /get_tracks__id__relationships_similarTracks>`_: Get TIDAL
        catalog information for similar tracks.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the similar tracks.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        tracks : dict[str, Any]
            Page of TIDAL metadata for the similar tracks.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "data": [
                      {
                        "id": <str>,
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
                          "createdAt": <str>,
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
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "similarTracks",
            country_code=country_code,
            include_metadata=include_metadata,
            cursor=cursor,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_source_file(
        self,
        track_id: int | str,
        /,
        *,
        include_metadata: bool = False,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Source File Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/tracks
        /get_tracks__id__relationships_sourceFile>`_: Get TIDAL
        catalog information for the source file for a track.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the track's source file.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        source_file : dict[str, Any]
            Page of TIDAL metadata for the track's source file.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "data": {
                      "id": <str>,
                      "type": "sourceFile"
                    },
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
        return self._get_resource_relationship(
            "tracks",
            track_id,
            "sourceFile",
            include_metadata=include_metadata,
            share_code=share_code,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_usage_rules(
        self,
        track_id: int | str,
        /,
        *,
        include_metadata: bool = False,
        share_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Usage Rules Relationship
        <https://tidal-music.github.io/tidal-api-reference/#/tracks
        /get_tracks__id__relationships_usageRules>`_: Get TIDAL catalog
        information for the usage rules for a track.

        Parameters
        ----------
        track_id : int or str; positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the track's usage rules.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        Returns
        -------
        usage_rules : dict[str, Any]
            TIDAL metadata for the track's usage rules.

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
            "tracks",
            track_id,
            "usageRules",
            include_metadata=include_metadata,
            share_code=share_code,
        )

    @_copy_docstring(SearchAPI.search_tracks)
    def search_tracks(
        self,
        query: str,
        /,
        country_code: str | None = None,
        *,
        include_explicit: bool | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return self._client.search.search_tracks(
            query,
            country_code=country_code,
            include_explicit=include_explicit,
            include_metadata=include_metadata,
            cursor=cursor,
        )

    @_copy_docstring(UsersAPI.get_user_saved_tracks)
    def get_user_saved_tracks(
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
        return self._client.users.get_user_saved_tracks(
            collection_id=collection_id,
            user_id=user_id,
            country_code=country_code,
            locale=locale,
            include_metadata=include_metadata,
            cursor=cursor,
            sort_by=sort_by,
            descending=descending,
        )

    @_copy_docstring(UsersAPI.save_tracks)
    def save_tracks(
        self,
        track_ids: int
        | str
        | dict[str, int | str]
        | Collection[int | str | dict[str, int | str]],
        /,
        *,
        collection_id: str | None = None,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        self._client.users.save_tracks(
            track_ids,
            collection_id=collection_id,
            user_id=user_id,
            country_code=country_code,
        )

    @_copy_docstring(UsersAPI.remove_saved_tracks)
    def remove_saved_tracks(
        self,
        track_ids: int
        | str
        | dict[str, int | str]
        | Collection[int | str | dict[str, int | str]],
        /,
        *,
        collection_id: str | None = None,
        user_id: int | str | None = None,
        country_code: str | None = None,
    ) -> None:
        self._client.users.remove_saved_tracks(
            track_ids,
            collection_id=collection_id,
            user_id=user_id,
            country_code=country_code,
        )
