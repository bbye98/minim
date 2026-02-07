import copy
from datetime import datetime
from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import MusixmatchResourceAPI
from .tracks import TracksAPI


class EnterpriseAPI(MusixmatchResourceAPI):
    """
    Enterprise API endpoints for the Musixmatch Lyrics API.

    .. important::

       This class is managed by
       :class:`minim.api.musixmatch.MusixmatchLyricsAPIClient` and
       should not be instantiated directly.
    """

    _RIGHTSHOLDER_ROLES = {
        "A",
        "AD",
        "AM",
        "AR",
        "AQ",
        "C",
        "CA",
        "E",
        "ES",
        "PA",
        "PR",
        "SA",
        "SE",
        "SR",
        "TR",
    }

    @staticmethod
    def _process_work_rightsholders(
        rightsholders: list[dict[str, Any]], rightsholder_type: str, /
    ) -> None:
        """
        Process musical work rightsholders.

        Parameters
        ----------
        rightsholders : list[dict[str, Any]]; positional-only
            Musical work publishers or writers.

        rightsholder_type : str; positional-only
            Type of musical work rightsholder.

            **Valid values**: :code:`"publisher"`, :code:`"writer"`.
        """
        attr_prefix = f"work_data['owners'][{rightsholder_type!r}]"
        MusixmatchResourceAPI._validate_type(attr_prefix, rightsholders, list)
        for idx, rightsholder in enumerate(rightsholders):
            item_name = f"{attr_prefix}[{idx}]"
            MusixmatchResourceAPI._validate_type(item_name, rightsholder, dict)
            required_keys = {"name", "controlled"}
            for attr_key, attr_val in rightsholder.items():
                attr_name = f"{item_name}[{attr_key!r}]"
                match attr_key:
                    # data.owners.(publisher|writer).name
                    case "name":
                        rightsholder[attr_key] = (
                            MusixmatchResourceAPI._prepare_string(
                                attr_name, attr_val
                            )
                        )
                        required_keys.remove(attr_key)

                    # data.owners.(publisher|writer).controlled
                    case "controlled":
                        attr_val = MusixmatchResourceAPI._prepare_string(
                            attr_name, attr_val
                        ).upper()
                        if attr_val not in "NY":
                            raise ValueError(
                                f"`{attr_name}` must be either 'Y' or 'N'."
                            )
                        rightsholder[attr_key] = attr_val
                        required_keys.remove(attr_key)

                    # data.owners.(publisher|writer).identifier
                    case "identifier":
                        rightsholder[attr_key] = (
                            MusixmatchResourceAPI._prepare_string(
                                attr_name, attr_val
                            )
                        )

                    # data.owners.(publisher|writer).ipi
                    case "ipi":
                        attr_val = rightsholder[attr_key] = (
                            MusixmatchResourceAPI._prepare_string(
                                attr_name, attr_val
                            )
                            if isinstance(attr_val, str)
                            else str(attr_val)
                        )
                        MusixmatchResourceAPI._validate_numeric(
                            attr_name, attr_val, int
                        )

                    # data.owners.(publisher|writer).role
                    case "role":
                        attr_val = rightsholder[attr_key] = (
                            MusixmatchResourceAPI._prepare_string(
                                attr_name, attr_val
                            ).upper()
                        )
                        if attr_val not in EnterpriseAPI._RIGHTSHOLDER_ROLES:
                            raise ValueError(
                                f"Invalid role {attr_val!r} for "
                                f"`{item_name}`. Valid values: "
                                f"{MusixmatchResourceAPI._join_values(EnterpriseAPI._RIGHTSHOLDER_ROLES)}."
                            )

                    # data.owners.(publisher|writer).(mech|perf|sync)_ownership_share
                    case (
                        "mech_ownership_share"
                        | "perf_ownership_share"
                        | "sync_ownership_share"
                    ):
                        MusixmatchResourceAPI._validate_number(
                            attr_key, attr_val, int, 0, 10_000
                        )

                    case _:
                        raise ValueError(
                            f"Invalid key {attr_key!r} in the "
                            f"`{attr_name}` dictionary."
                        )

            if required_keys:
                raise ValueError(
                    f"`{attr_name}` is missing the following required key(s): "
                    f"{MusixmatchResourceAPI._join_values(required_keys)}."
                )

    @staticmethod
    def _process_work_owners(owners: dict[str, Any] | None, /) -> None:
        """
        Process musical work owners.

        Parameters
        ----------
        owners : dict[str, Any] or None; positional-only
            Musical work owners.
        """
        if owners is None:
            return

        MusixmatchResourceAPI._validate_type(
            "work_data['owners']", owners, dict
        )
        required_keys = {"publisher", "writer"}
        for attr_key, attr_val in owners.items():
            match attr_key:
                # data.owners.(publisher|writer)
                case "publisher" | "writer":
                    EnterpriseAPI._process_work_rightsholders(
                        attr_val, attr_key
                    )
                    required_keys.remove(attr_key)

                case _:
                    raise ValueError(
                        f"Invalid key {attr_key!r} in the "
                        "`work_data['owners']` dictionary."
                    )

        if required_keys:
            raise ValueError(
                "`work_data['owners']` is missing the following "
                "required key(s): "
                f"{MusixmatchResourceAPI._join_values(required_keys)}."
            )

    @staticmethod
    def _process_work_territories(
        territories: list[dict[str, Any]], /
    ) -> None:
        """
        Process musical work royalty collection territories.

        Parameters
        ----------
        territories : list[dict[str, Any]]; positional-only
            Musical work royalty collection territories.
        """
        attr_prefix = "work_data['owners']['territories']"
        MusixmatchResourceAPI._validate_type(attr_prefix, territories, list)
        for idx, territory in enumerate(territories):
            item_name = f"{attr_prefix}[{idx}]"
            MusixmatchResourceAPI._validate_type(item_name, territory, dict)
            required_keys = {"code"}
            optional_keys = {"mech_share", "perf_share", "sync_share"}
            for attr_key, attr_val in territory.items():
                attr_name = f"{item_name}[{attr_key!r}]"
                match attr_key:
                    case "code":
                        MusixmatchResourceAPI._validate_country_code(attr_val)
                        required_keys.remove(attr_key)

                    case "mech_share" | "perf_share" | "sync_share":
                        MusixmatchResourceAPI._validate_number(
                            attr_name, attr_val, int, 0, 10_000
                        )
                        optional_keys.discard(attr_key)

                    case _:
                        raise ValueError(
                            f"Invalid key {attr_key!r} in the "
                            f"`{attr_name}` dictionary."
                        )

            if required_keys:
                raise ValueError(
                    f"`{attr_name}` is missing the following required key(s): "
                    f"{MusixmatchResourceAPI._join_values(required_keys)}."
                )

            if len(optional_keys) == 3:
                raise ValueError(
                    f"`{attr_name}` requires at least one of the "
                    "following key(s): "
                    f"{MusixmatchResourceAPI._join_values(optional_keys)}."
                )

    @staticmethod
    def _process_work_collection(collection: dict[str, Any] | None, /) -> None:
        """
        Process musical work royalty collection.

        Parameters
        ----------
        collection : dict[str, Any] or None; positional-only
            Musical work royalty collection.
        """
        if collection is None:
            return

        MusixmatchResourceAPI._validate_type(
            "work_data['collection']", collection, dict
        )
        required_keys = {"territories"}
        for attr_key, attr_val in collection.items():
            match attr_key:
                # data.collection.territories
                case "territories":
                    EnterpriseAPI._process_work_territories(attr_val)
                    required_keys.remove(attr_key)

                # data.collection.validity_(begin|end)
                case "validity_begin" | "validity_end":
                    collection[attr_key] = (
                        MusixmatchResourceAPI._prepare_datetime(
                            attr_val, "%Y-%m-%d"
                        )
                    )

                case _:
                    raise ValueError(
                        f"Invalid key {attr_key!r} in the "
                        "`work_data['collection']` dictionary."
                    )

        if required_keys:
            raise ValueError(
                "`work_data['collection']` is missing the following "
                "required key(s): "
                f"{MusixmatchResourceAPI._join_values(required_keys)}."
            )

    @staticmethod
    def _prepare_work_data(work_data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate and normalize musical work data.

        Parameters
        ----------
        work_data : dict[str, Any]
            Musical work data.

        Returns
        -------
        work_data : dict[str, Any]
            Normalized musical work data.
        """
        MusixmatchResourceAPI._validate_type("work_data", work_data, dict)
        work_data = copy.deepcopy(work_data)
        required_keys = {"identifier", "title"}
        for attr_key, attr_val in work_data.items():
            attr_name = f"work_data[{attr_key!r}]"
            match attr_key:
                # data.identifier
                case "identifier":
                    attr_val = work_data[attr_key] = (
                        MusixmatchResourceAPI._prepare_string(
                            attr_name, attr_val
                        )
                    )
                    if len(attr_val) > 40:
                        raise ValueError(
                            f"`{attr_name}` must be between 1 and 40 "
                            "characters long."
                        )
                    required_keys.remove(attr_key)

                # data.title
                case "title":
                    work_data[attr_key] = (
                        MusixmatchResourceAPI._prepare_string(
                            attr_name, attr_val
                        )
                    )
                    required_keys.remove(attr_key)

                # data.alternate_titles
                case "alternative_titles":
                    MusixmatchResourceAPI._validate_type(
                        attr_name, attr_val, list
                    )
                    work_data[attr_key] = [
                        MusixmatchResourceAPI._prepare_string(
                            f"{attr_name}[{idx}]", title
                        )
                        for idx, title in enumerate(attr_val)
                    ]

                # data.iswc
                case "iswc":
                    work_data[attr_key] = MusixmatchResourceAPI._prepare_iswc(
                        attr_val
                    )

                # data.isrc
                case "isrc":
                    work_data[attr_key] = MusixmatchResourceAPI._prepare_isrc(
                        attr_val
                    )

                # data.performers
                case "performers":
                    MusixmatchResourceAPI._validate_type(
                        attr_name, attr_val, dict
                    )
                    required_subkeys = {"name"}
                    for subattr_key, subattr_val in attr_val.items():
                        subattr_name = f"{attr_name}[{subattr_key!r}]"
                        match subattr_key:
                            case "name":
                                attr_val[subattr_key] = (
                                    MusixmatchResourceAPI._prepare_string(
                                        subattr_name, subattr_val
                                    )
                                )
                                required_subkeys.remove(subattr_key)

                            case "identifier":
                                attr_val[subattr_key] = (
                                    MusixmatchResourceAPI._prepare_string(
                                        subattr_name, subattr_val
                                    )
                                )

                            case _:
                                raise ValueError(
                                    f"Invalid key {subattr_key!r} in the "
                                    f"`{attr_name}` dictionary."
                                )

                    if required_subkeys:
                        raise ValueError(
                            f"`{attr_name}` is missing the following "
                            "required key(s): "
                            f"{MusixmatchResourceAPI._join_values(required_subkeys)}."
                        )

                # data.owners
                case "owners":
                    EnterpriseAPI._process_work_owners(attr_val)

                # data.collection
                case "collection":
                    EnterpriseAPI._process_work_collection(attr_val)

                # data.lyrics
                case "lyrics":
                    MusixmatchResourceAPI._validate_type(
                        attr_name, attr_val, dict
                    )
                    required_subkeys = {"lyrics"}
                    for subattr_key, subattr_val in attr_val.items():
                        subattr_name = f"{attr_name}[{subattr_key!r}]"
                        match subattr_key:
                            # data.lyrics.(lyrics|lrc)
                            case "lyrics" | "lrc":
                                MusixmatchResourceAPI._validate_type(
                                    subattr_name, subattr_val, str
                                )

                            # data.lyrics.duration
                            case "duration":
                                MusixmatchResourceAPI._validate_number(
                                    subattr_name, subattr_val, int, 0
                                )

                            case _:
                                raise ValueError(
                                    f"Invalid key {subattr_key!r} in the "
                                    f"`{attr_name}` dictionary."
                                )

                    if required_subkeys:
                        raise ValueError(
                            f"`{attr_name}` is missing the following "
                            "required key(s): "
                            f"{MusixmatchResourceAPI._join_values(required_subkeys)}."
                        )

                case _:
                    raise ValueError(
                        f"Invalid key {attr_key!r} in the `work_data` "
                        "dictionary."
                    )

        if required_keys:
            raise ValueError(
                "`work_data` is missing the following required key(s): "
                f"{MusixmatchResourceAPI._join_values(required_keys)}."
            )

        return work_data

    def submit_work(self, work_data: dict[str, Any], /) -> dict[str, Any]:
        """
        `Enterprise > work.post <https://docs.musixmatch.com
        /enterprise-integration/api-reference/work-post>`_: Submit
        details for a musical work to Musixmatch.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        Parameters
        ----------
        work_data : dict[str, Any]; positional-only
            Details for a musical work.

            .. seealso::

               `Musixmatch Lyrics API documentation
               <https://docs.musixmatch.com/enterprise-integration
               /api-reference/work-post#body-data>`_ – Data schema.

        Returns
        -------
        work : dict[str, Any]
            Musixmatch catalog record for a musical work.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "alternate_titles": [
                          {
                            "title": <str>
                          }
                        ],
                        "collections": {
                          <str>: {
                            "territories": [
                              {
                                "code": <str>,
                                "countries": <list[str]>,
                                "mech_share": <int>,
                                "perf_share": <int>,
                                "publisher": None,
                                "sync_share": <int>
                              }
                            ],
                            "validity_begin": <str>,
                            "validity_end": None
                          }
                        },
                        "identifier": <str>,
                        "is_disabled": <int>,
                        "isrc": <list[str]>,
                        "iswc": <str>,
                        "last_trasmission": <str>,
                        "owners": {
                          "publisher": [
                            {
                              "controlled": <str>,
                              "id": <int>,
                              "identifier": <str>,
                              "ipi": <str>,
                              "mech_ownership_share": <int>,
                              "mech_society": None,
                              "name": <str>,
                              "perf_ownership_share": <int>,
                              "perf_society": None,
                              "role": None,
                              "sync_ownership_share": <int>,
                              "sync_society": None,
                              "type": "publisher",
                              "validity_begin": <str>
                            }
                          ],
                          "writer": [
                            {
                              "controlled": <str>,
                              "id": <int>,
                              "identifier": <str>,
                              "ipi": <str>,
                              "mech_ownership_share": <int>,
                              "mech_society": None,
                              "name": <str>,
                              "perf_ownership_share": <int>,
                              "perf_society": None,
                              "role": None,
                              "sync_ownership_share": <int>,
                              "sync_society": None,
                              "type": "writer",
                              "validity_begin": <str>
                            }
                          ]
                        },
                        "ownership": [],
                        "performers": [],
                        "publisher_short_name": <str>,
                        "source": {
                          "affiliation": None,
                          "control": <bool>,
                          "created": <str>,
                          "credits_priority": <str>,
                          "description": <str>,
                          "id": <int>,
                          "last_updated": <str>,
                          "report": <str>,
                          "sender_id": <str>,
                          "sender_name": <str>,
                          "short_name": <str>,
                          "type_of_right": <str>,
                          "validity_begin": <str>,
                          "validity_end": None
                        },
                        "submissions": [
                          {
                            "creation_date": <str>,
                            "disabled": <str>,
                            "filename": <str>,
                            "id": <int>,
                            "source": <int>,
                            "transmission_date": <str>
                          }
                        ],
                        "tablespace": <str>,
                        "title": <str>,
                        "type_of_right": <str>,
                        "validity_begin": None,
                        "validity_end": <str>,
                        "wgid": <str>,
                        "work_id": <int>
                      },
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._client._require_api_key("enterprise.submit_work")
        return self._client._request(
            "POST",
            "work.post",
            headers={"content-type": "application/json"},
            json=self._prepare_work_data(work_data),
        ).json()

    def set_work_validity(
        self, work_identifier: str, /, valid_until: str | datetime
    ) -> None:
        """
        `Enterprise > work.validity.post <https://docs.musixmatch.com
        /enterprise-integration/api-reference/work-validity-post>`_:
        Set the validity end date for a musical work on Musixmatch.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        Parameters
        ----------
        work_identifier : str; positional-only
            Unique identifier of the musical work.

            **Valid length**: :code:`1` to :code:`40`.

            **Example**: "00001100196005".

        valid_until : str or datetime.datetime
            Validity end date, in :code:`YYYY-MM-DD` format.

        Returns
        -------
        status : dict[str, Any]
            Whether the request completed successfully.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": <str>,
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._client._require_api_key("enterprise.set_work_validity")
        self._validate_type("work_identifier", work_identifier, str)
        work_identifier = self._prepare_string(
            "work_identifier", work_identifier
        )
        if not len(work_identifier) <= 40:
            raise ValueError(
                "`work_identifier` must be between 1 and 40 characters long."
            )
        return self._client._request(
            "POST",
            "work.validity.post",
            headers={"content-type": "application/json"},
            json={
                "data": {
                    "identifier": work_identifier,
                    "validity_end": self._prepare_datetime(
                        valid_until, "%Y-%m-%d"
                    ),
                }
            },
        ).json()

    @TTLCache.cached_method(ttl="daily")
    def screen_track_lyrics(
        self,
        text: str,
        /,
        *,
        max_candidates: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        `Enterprise > track.lyrics.fingerprint.post
        <https://docs.musixmatch.com/enterprise-integration
        /api-reference/track-lyrics-fingerprint-post>`_: Get Musixmatch
        catalog information for tracks whose lyrics match a text string,
        ranked by similarity.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        Parameters
        ----------
        text : str; positional-only
            Text to screen for potential lyrical content.

        max_candidates : int; keyword-only; optional
            Maximum number of track candidates.

            **Valid range**: :code:`1` to :code:`20`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to `max_candidates`.

        Returns
        -------
        tracks : dict[str, Any]
            Tracks whose lyrics match the text string.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "track_list": [
                          {
                            "similarity": <float>,
                            "track": {
                              "album_coverart_100x100": <str>,
                              "album_coverart_350x350": <str>,
                              "album_coverart_500x500": <str>,
                              "album_coverart_800x800": <str>,
                              "album_id": <int>,
                              "album_name": <str>,
                              "artist_id": <int>,
                              "artist_name": <str>,
                              "commontrack_id": <int>,
                              "commontrack_isrcs": <list[list[str]]>,
                              "explicit": <int>,
                              "has_lyrics": <int>,
                              "has_richsync": <int>,
                              "has_subtitles": <int>,
                              "instrumental": <int>,
                              "num_favourite": <int>,
                              "primary_genres": {
                                "music_genre_list": [
                                  {
                                    "music_genre": {
                                      "music_genre_id": <int>,
                                      "music_genre_name": <str>,
                                      "music_genre_name_extended": <str>,
                                      "music_genre_parent_id": <int>,
                                      "music_genre_vanity": <str>
                                    }
                                  }
                                ]
                              },
                              "restricted": <int>,
                              "track_edit_url": <str>,
                              "track_id": <int>,
                              "track_isrc": <str>,
                              "track_length": <int>,
                              "track_name": <str>,
                              "track_rating": <int>,
                              "track_share_url": <str>,
                              "track_spotify_id": <str>,
                              "updated_time": <str>
                            }
                          }
                        ]
                      },
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._client._require_api_key("enterprise.screen_track_lyrics")
        params = {}
        if max_candidates is not None:
            self._validate_number("max_candidates", max_candidates, int, 1, 20)
            params["size"] = max_candidates
        if limit is not None:
            self._validate_number(
                "limit", limit, int, 1, params.get("size", 20)
            )
            params["limit"] = limit
        return self._client._request(
            "POST",
            "track.lyrics.fingerprint.post",
            headers={"content-type": "application/json"},
            json={"data": {"text": text}},
            params=params,
        )

    @TTLCache.cached_method(ttl="static")
    def get_track_catalog_record(self, isrc: str) -> dict[str, Any]:
        """
        `Enterprise > track.dump.get <https://docs.musixmatch.com
        /enterprise-integration/api-reference/track-dump-get>`_: Get
        the Musixmatch catalog record for a track.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        Parameters
        ----------
        isrc : str
            ISRC of the track.

            **Example**: :code:`"USUM70905526"`.

        Returns
        -------
        track : dict[str, Any]
            Musixmatch catalog record for a track.

            .. admonition:: Sample reponse
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": [
                        {
                          "artist": <str>,
                          "commontrack_id": <int>,
                          "instrumental": <bool>,
                          "isrcs": <list[str]>,
                          "language_iso_code_1": <str>,
                          "last_updated": <str>,
                          "lyrics": <str>,
                          "lyrics_id": <int>,
                          "lyrics_tracking_url": <str>,
                          "restrictions": {
                            "allow": <list[str]>,
                            "blocked": <list[str]>
                          },
                          "snippet": <str>,
                          "subtitles": [
                            {
                              "body": <str>,
                              "id": <int>,
                              "length": <int>,
                              "tracking_url": <str>,
                            }
                          ],
                          "title": <str>,
                          "writers": [
                            {
                              "id": <int>,
                              "name": <str>
                            }
                          ]
                        }
                      ],
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._client._require_api_key("enterprise.get_track_catalog_record")
        return self._client._request(
            "GET",
            "track.dump.get",
            params={"track_isrc": self._prepare_isrc(isrc)},
        ).json()

    @TTLCache.cached_method(ttl="daily")
    def get_catalog_feeds(self) -> dict[str, Any]:
        """
        `Enterprise > tracks.dump.get <https://docs.musixmatch.com
        /enterprise-integration/api-reference/tracks-dump-get>`_: Get
        the latest Musixmatch catalog feeds.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        Returns
        -------
        catalog_feeds : dict[str, Any]
            Musixmatch catalog feeds.

            .. admonition:: Sample reponse
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": [
                        {
                          "created": <str>,
                          "download_url": <str>,
                          "full": <bool>,
                          "id": <int>
                        }
                      ],
                      "header": {
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._client._require_api_key("enterprise.get_catalog_feeds")
        return self._client._request("GET", "tracks.dump.get").json()

    @TTLCache.cached_method(ttl="static")
    def get_languages(
        self, *, include_romanization: bool | None = None
    ) -> dict[str, Any]:
        """
        `Enterprise > languages.get <https://docs.musixmatch.com
        /enterprise-integration/api-reference/languages-get>`_: Get
        languages supported by Musixmatch.

        .. admonition:: Subscription
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 Musixmatch Enterprise plan
                    Access extended music metadata, advanced search,
                    translations, song structure, and lyric analysis.
                    `Learn more. <https://about.musixmatch.com
                    /api-pricing>`__

        Parameters
        ----------
        include_romanization : bool; keyword-only; optional
            Whether to include romanization information for romanized
            languages.

            **API default**: :code:`False`.

        Returns
        -------
        languages : dict[str, Any]
            Languages supported by Musixmatch.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "message": {
                      "body": {
                        "language_list": [
                          {
                            "language": {
                              "has_romanization": <int>,
                              "iso_code_romanization": <str>,
                              "language_iso_code_1": <str>,
                              "language_iso_code_3": <str>,
                              "language_name": <str>
                            }
                          }
                        ]
                      },
                      "header": {
                        "available": <int>,
                        "execute_time": <float>,
                        "status_code": <int>
                      }
                    }
                  }
        """
        self._client._require_api_key("enterprise.get_languages")
        params = {}
        if include_romanization is not None:
            self._validate_type(include_romanization, bool)
            if include_romanization:
                params["has_romanization"] = "1"
        return self._client._request(
            "GET", "languages.get", params=params
        ).json()

    @_copy_docstring(TracksAPI.get_track_lyrics_analysis)
    def get_track_lyrics_analysis(
        self,
        *,
        track_id: int | str | None = None,
        common_track_id: int | str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        return self._client.tracks.get_track_lyrics_analysis(
            track_id=track_id, common_track_id=common_track_id, isrc=isrc
        )
