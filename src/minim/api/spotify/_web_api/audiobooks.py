from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import SpotifyResourceAPI
from .users import UsersAPI


class AudiobooksAPI(SpotifyResourceAPI):
    """
    Audiobooks API endpoints for the Spotify Web API.

    .. important::

       Audiobooks are only available in the US, UK, Canada, Ireland,
       New Zealand, and Australia markets.

    .. note::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPI`
       and should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="catalog")
    def get_audiobooks(
        self,
        audiobook_ids: str | list[str],
        /,
        *,
        country_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Audiobooks > Get an Audiobook <https://developer.spotify.com
        /documentation/web-api/reference/get-an-audiobook>`_: Get Spotify
        catalog information for a single audiobook․
        `Audiobook > Get Several Audiobooks <https://developer.spotify.com
        /documentation/web-api/reference/get-several-audiobooks>`_: Get
        Spotify catalog information for multiple audiobooks.

        .. admonition:: Third-party application mode
           :class: authorization-scope dropdown

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        audiobook_ids : str or list[str]; positional-only
            Spotify IDs of the audiobooks. A maximum of 50 IDs can be
            sent in a request.

            **Examples**:

            .. container::

               * :code:`"18yVqkdbdRvS24c0Ilj2ci"`
               * :code:`"18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ"`
               * :code:`["18yVqkdbdRvS24c0Ilj2ci",
                 "1HGw3J3NxZO1TP1BTtVhpZ"]`

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
        audiobooks : dict[str, Any]
            Spotify content metadata for the audiobooks.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single audiobook

                  .. code::

                     {
                       "authors": [
                         {
                           "name": <str>
                         }
                       ],
                       "available_markets": <list[str]>,
                       "chapters": {
                         "href": <str>,
                         "items": [
                           {
                             "audio_preview_url": <str>,
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
                         ],
                         "limit": <int>,
                         "next": <str>,
                         "offset": <int>,
                         "previous": <str>,
                         "total": <int>
                       },
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
                         <str>
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
                       "type": "audiobook",
                       "uri": <str>
                     }

               .. tab:: Multiple audiobooks

                  .. code::

                     {
                       "audiobooks": [
                         {
                           "authors": [
                             {
                               "name": <str>
                             }
                           ],
                           "available_markets": <list[str]>,
                           "chapters": {
                             "href": <str>,
                             "items": [
                               {
                                 "audio_preview_url": <str>,
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
                             ],
                             "limit": <int>,
                             "next": <str>,
                             "offset": <int>,
                             "previous": <str>,
                             "total": <int>
                           },
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
                         }
                       ]
                     }
        """
        return self._get_resources(
            "audiobooks", audiobook_ids, country_code=country_code
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_audiobook_chapters(
        self,
        audiobook_id: str,
        /,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Audiobooks > Get Audiobook Chapters
        <https://developer.spotify.com/documentation/web-api/reference
        /get-audiobook-chapters>`_: Get Spotify catalog information
        for chapters in an audiobook.

        .. admonition:: Third-party application mode
           :class: authorization-scope dropdown

           .. tab:: Optional

              Extended quota mode before November 27, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        audiobook_id : str; positional-only
            Spotify ID of the audiobook.

            **Examples**: :code:`"18yVqkdbdRvS24c0Ilj2ci"`.

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

        limit : int; keyword-only; optional
            Maximum number of audiobook chapters to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first audiobook chapter to return. Use with
            `limit` to get the next batch of audiobook chapters.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        chapters : dict[str, Any]
            Page of Spotify content metadata for the audiobook's
            chapters.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "audio_preview_url": <str>,
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
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        return self._get_resource_items(
            "audiobook",
            audiobook_id,
            "chapters",
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @_copy_docstring(UsersAPI.get_my_saved_audiobooks)
    def get_my_saved_audiobooks(
        self,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_my_saved_audiobooks(
            country_code=country_code, limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.save_audiobooks)
    def save_audiobooks(self, audiobook_ids: str | list[str], /) -> None:
        self._client.users.save_audiobooks(audiobook_ids)

    @_copy_docstring(UsersAPI.remove_saved_audiobooks)
    def remove_saved_audiobooks(
        self, audiobook_ids: str | list[str], /
    ) -> None:
        self._client.users.remove_saved_audiobooks(audiobook_ids)

    @_copy_docstring(UsersAPI.are_audiobooks_saved)
    def are_audiobooks_saved(
        self, audiobook_ids: str | list[str], /
    ) -> list[bool]:
        return self._client.users.are_audiobooks_saved(audiobook_ids)
