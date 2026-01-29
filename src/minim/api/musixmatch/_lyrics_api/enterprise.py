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

    def submit_work(self) -> None:
        """ """

    def set_work_validity(self) -> None:
        """ """

    def screen_track_lyrics(self) -> None:
        """ """

    def get_track_catalog_record(self) -> None:
        """ """

    def get_catalog_feeds(self) -> None:
        """ """

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
