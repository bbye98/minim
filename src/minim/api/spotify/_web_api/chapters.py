from collections.abc import Collection
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPIChapterEndpoints:
    """
    Spotify Web API audiobook chapter endpoints.

    .. important::

       Audiobooks are only available in the US, UK, Canada, Ireland,
       New Zealand, and Australia markets.

    .. note::

       This class is managed by :class:`minim.api.spotify.WebAPI` and
       should not be instantiated directly.
    """

    def __init__(self, client: "WebAPI", /) -> None:
        """
        Parameters
        ----------
        client : minim.api.spotify.WebAPI
            Minim's Spotify Web API client.
        """
        self._client = client

    def get_chapters(
        self, chapter_ids: str | Collection[str], /, *, market: str
    ) -> dict[str, Any]:
        """
        `Chapters > Get a Chapter <https://developer.spotify.com
        /documentation/web-api/reference/get-a-chapter>`_: Get Spotify
        catalog information for a single audiobook chapter․
        `Chapters > Get Several Chapters <https://developer.spotify.com
        /documentation/web-api/reference/get-several-chapters>`_: Get
        Spotify catalog information for multiple audiobook chapters.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
        chapter_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the audiobook
            chapters. A maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"0IsXVP0JmcB2adSE338GkK"`,
            :code:`"0IsXVP0JmcB2adSE338GkK,3ZXb8FKZGU0EHALYX6uCzU"`,
            :code:`["0IsXVP0JmcB2adSE338GkK", "3ZXb8FKZGU0EHALYX6uCzU"]`.

        market : str, keyword-only, optional
            ISO 3166-1 alpha-2 country code. If specified, only content
            available in that market is returned. When a valid user
            access token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither the market nor the user's country are
               provided, the content is considered unavailable for the
               client.

            **Example**: :code:`"ES"`.

        Returns
        -------
        chapters : dict[str, Any]
            Spotify content metadata for the audiobook chapters.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single audiobook chapter

                  .. code::

                     {
                       "audio_preview_url": <str>,
                       "audiobook": {
                         "authors": [
                           {
                             "name": <str>
                           }
                         ],
                         "available_markets": <list[str]>,
                         "copyrights": [
                           {
                             "text": <str>,
                             "type": <str>
                           }
                         ],
                         "description": <str>,
                         "edition": <str>,
                         "explicit": <bool>,
                         "external_urls": {
                           "spotify": <str>
                         },
                         "href": <str>,
                         "html_description": <str>,
                         "id": <str>,
                         "images": [
                           {
                             "height": <int>,
                             "url": <str>,
                             "width": <int>
                           }
                         ],
                         "languages": [
                           "string"
                         ],
                         "media_type": <str>,
                         "name": <str>,
                         "narrators": [
                           {
                             "name": <str>
                           }
                         ],
                         "publisher": <str>,
                         "total_chapters": <int>,
                         "type": <str>,
                         "uri": <str>
                       },
                       "available_markets": [
                         "string"
                       ],
                       "chapter_number": <int>,
                       "description": <str>,
                       "duration_ms": <int>,
                       "explicit": <bool>,
                       "external_urls": {
                         "spotify": <str>
                       },
                       "href": <str>,
                       "html_description": <str>,
                       "id": <str>,
                       "images": [
                         {
                           "height": <int>,
                           "url": <str>,
                           "width": <int>
                         }
                       ],
                       "is_playable": <bool>,
                       "languages": <list[str]>,
                       "name": <str>,
                       "release_date": <str>,
                       "release_date_precision": <str>,
                       "restrictions": {
                         "reason": <str>
                       },
                       "resume_point": {
                         "fully_played": <bool>,
                         "resume_position_ms": <int>
                       },
                       "type": <str>,
                       "uri": <str>
                     }

               .. tab:: Multiple audiobook chapters

                  .. code::

                     {
                       "chapters": [
                         {
                           "audio_preview_url": <str>,
                           "audiobook": {
                             "authors": [
                               {
                                 "name": <str>
                               }
                             ],
                             "available_markets": <list[str]>,
                             "copyrights": [
                               {
                                 "text": <str>,
                                 "type": <str>
                               }
                             ],
                             "description": <str>,
                             "edition": <str>,
                             "explicit": <bool>,
                             "external_urls": {
                               "spotify": <str>
                             },
                             "href": <str>,
                             "html_description": <str>,
                             "id": <str>,
                             "images": [
                               {
                                 "height": <int>,
                                 "url": <str>,
                                 "width": <int>
                               }
                             ],
                             "languages": [
                               "string"
                             ],
                             "media_type": <str>,
                             "name": <str>,
                             "narrators": [
                               {
                                 "name": <str>
                               }
                             ],
                             "publisher": <str>,
                             "total_chapters": <int>,
                             "type": <str>,
                             "uri": <str>
                           },
                           "available_markets": [
                             "string"
                           ],
                           "chapter_number": <int>,
                           "description": <str>,
                           "duration_ms": <int>,
                           "explicit": <bool>,
                           "external_urls": {
                             "spotify": <str>
                           },
                           "href": <str>,
                           "html_description": <str>,
                           "id": <str>,
                           "images": [
                             {
                               "height": <int>,
                               "url": <str>,
                               "width": <int>
                             }
                           ],
                           "is_playable": <bool>,
                           "languages": <list[str]>,
                           "name": <str>,
                           "release_date": <str>,
                           "release_date_precision": <str>,
                           "restrictions": {
                             "reason": <str>
                           },
                           "resume_point": {
                             "fully_played": <bool>,
                             "resume_position_ms": <int>
                           },
                           "type": <str>,
                           "uri": <str>
                         }
                       ]
                     }
        """
        string = isinstance(chapter_ids, str)
        chapter_ids, n_ids = self._client._prepare_spotify_ids(
            chapter_ids, limit=50
        )
        if string and n_ids == 1:
            return self._client._request(
                "GET", f"chapters/{chapter_ids}", params={"market": market}
            ).json()
        return self._client._request(
            "GET", "chapters", params={"ids": chapter_ids, "market": market}
        ).json()
