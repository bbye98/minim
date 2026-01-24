from typing import Any

from ..._shared import TTLCache
from ._shared import SpotifyResourceAPI


class ChaptersAPI(SpotifyResourceAPI):
    """
    Chapters API endpoints for the Spotify Web API.

    .. important::

       Audiobooks are only available in the US, UK, Canada, Ireland,
       New Zealand, and Australia markets.

    .. note::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPI`
       and should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="playback")
    def get_chapters(
        self, chapter_ids: str | list[str], /, *, country_code: str
    ) -> dict[str, Any]:
        """
        `Chapters > Get a Chapter <https://developer.spotify.com
        /documentation/web-api/reference/get-a-chapter>`_: Get Spotify
        catalog information for an audiobook chapter․
        `Chapters > Get Several Chapters <https://developer.spotify.com
        /documentation/web-api/reference/get-several-chapters>`_: Get
        Spotify catalog information for multiple audiobook chapters.

        .. admonition:: Third-party application mode
           :class: entitlement dropdown

           .. tab:: Optional

              :code:`user-read-playback-position` scope
                 Read your position in content you have played. `Learn
                 more. <https://developer.spotify.com/documentation
                 /web-api/concepts/scopes#user-read-playback-position>`__

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        chapter_ids : str or list[str]; positional-only
            Spotify IDs of the audiobook chapters. A maximum of 50 IDs
            can be sent in a request.

            **Examples**:

            .. container::

               * :code:`"0IsXVP0JmcB2adSE338GkK"`
               * :code:`"0IsXVP0JmcB2adSE338GkK,3ZXb8FKZGU0EHALYX6uCzU"`
               * :code:`["0IsXVP0JmcB2adSE338GkK",
                 "3ZXb8FKZGU0EHALYX6uCzU"]`

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If provided, only content
            available in that market is returned. When a user access
            token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither a country code is provided nor a country can
               be determined from the user account, the content is
               considered unavailable for the client.

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
                         "languages": <list[str]>,
                         "media_type": <str>,
                         "name": <str>,
                         "narrators": [
                           {
                             "name": <str>
                           }
                         ],
                         "publisher": <str>,
                         "total_chapters": <int>,
                         "type": "audiobook",
                         "uri": <str>
                       },
                       "available_markets": <list[str]>,
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
                       "type": "chapter",
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
                             "languages": <list[str]>,
                             "media_type": <str>,
                             "name": <str>,
                             "narrators": [
                               {
                                 "name": <str>
                               }
                             ],
                             "publisher": <str>,
                             "total_chapters": <int>,
                             "type": "audiobook",
                             "uri": <str>
                           },
                           "available_markets": <list[str]>,
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
                           "type": "chapter",
                           "uri": <str>
                         }
                       ]
                     }
        """
        return self._get_resources(
            "chapters", chapter_ids, country_code=country_code
        )
