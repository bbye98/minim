from collections.abc import Collection
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import SpotifyWebAPI


class AudiobooksAPI(ResourceAPI):
    """
    Audiobooks API endpoints for the Spotify Web API.

    .. important::

       Audiobooks are only available in the US, UK, Canada, Ireland,
       New Zealand, and Australia markets.

    .. note::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPI`
       and should not be instantiated directly.
    """

    _client: "SpotifyWebAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_audiobooks(
        self,
        audiobook_ids: str | Collection[str],
        /,
        *,
        market: str | None = None,
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
        audiobook_ids : str or Collection[str], positional-only
            Spotify IDs of the audiobooks, provided as either a
            comma-delimited string or as a collection of strings. A
            maximum of 50 IDs can be sent in a request.

            **Examples**:

            .. container::

               * :code:`"18yVqkdbdRvS24c0Ilj2ci"`
               * :code:`"18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ"`
               * :code:`["18yVqkdbdRvS24c0Ilj2ci", "1HGw3J3NxZO1TP1BTtVhpZ"]`

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
        is_string = isinstance(audiobook_ids, str)
        audiobook_ids, n_ids = self._client._prepare_spotify_ids(
            audiobook_ids, limit=50
        )
        params = {}
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if is_string and n_ids == 1:
            return self._client._request(
                "GET", f"audiobooks/{audiobook_ids}", params
            ).json()

        params["ids"] = audiobook_ids
        return self._client._request("GET", "audiobooks", params=params).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_audiobook_chapters(
        self,
        audiobook_id: str,
        /,
        *,
        market: str | None = None,
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
        audiobook_id : str
            Spotify ID of the audiobook.

            **Examples**: :code:`"18yVqkdbdRvS24c0Ilj2ci"`.

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

        limit : int, keyword-only, optional
            Maximum number of audiobook chapters to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first audiobook chapter to return. Use with
            `limit` to get the next set of audiobook chapters.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        chapters : dict[str, Any]
            Pages of Spotify content metadata for the audiobook's
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
        self._client._validate_spotify_id(audiobook_id)
        params = {}
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"audiobooks/{audiobook_id}/chapters", params=params
        ).json()

    def get_my_saved_audiobooks(
        self,
        *,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Audiobooks > Get User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference
        /get-users-saved-audiobooks>`_: Get Spotify catalog information
        for the audiobooks saved in the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

        Parameters
        ----------
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

        limit : int, keyword-only, optional
            Maximum number of audiobooks to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first audiobook to return. Use with `limit` to
            get the next set of audiobook

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        audiobooks : dict[str, Any]
            Pages of Spotify content metadata for the user's saved
            audiobooks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
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
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        self._client._require_scopes(
            "audiobooks.get_my_saved_audiobooks", "user-library-read"
        )
        params = {}
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", "me/audiobooks", params=params
        ).json()

    def save_audiobooks(self, audiobook_ids: str | Collection[str], /) -> None:
        """
        `Audiobooks > Save Audiobooks for Current User
        <https://developer.spotify.com/documentation/web-api/reference
        /save-albums-user>`_: Save one or more audiobooks to the current
        user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify` scope
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        audiobook_ids : str or Collection[str], positional-only
            Spotify IDs of the audiobooks, provided as either a
            comma-delimited string or as a collection of strings. A
            maximum of 50 IDs can be sent in a request.

            **Examples**:

            .. container::

               * :code:`"18yVqkdbdRvS24c0Ilj2ci"`
               * :code:`"18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ"`
               * :code:`["18yVqkdbdRvS24c0Ilj2ci", "1HGw3J3NxZO1TP1BTtVhpZ"]`
        """
        self._client._require_scopes(
            "audiobooks.save_audiobooks", "user-library-modify"
        )
        self._client._request(
            "PUT",
            "me/audiobooks",
            params={
                "ids": self._client._prepare_spotify_ids(
                    audiobook_ids, limit=50
                )[0]
            },
        )

    def remove_saved_audiobooks(
        self, audiobook_ids: str | Collection[str], /
    ) -> None:
        """
        `Audiobooks > Remove User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-audiobooks-user>`_: Remove one or more audiobooks from
        the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify` scope
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        audiobook_ids : str or Collection[str], positional-only
            Spotify IDs of the audiobooks, provided as either a
            comma-delimited string or as a collection of strings. A
            maximum of 50 IDs can be sent in a request.

            **Examples**:

            .. container::

               * :code:`"18yVqkdbdRvS24c0Ilj2ci"`
               * :code:`"18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ"`
               * :code:`["18yVqkdbdRvS24c0Ilj2ci", "1HGw3J3NxZO1TP1BTtVhpZ"]`
        """
        self._client._require_scopes(
            "audiobooks.remove_saved_audiobooks", "user-library-modify"
        )
        self._client._request(
            "DELETE",
            "me/audiobooks",
            params={
                "ids": self._client._prepare_spotify_ids(
                    audiobook_ids, limit=50
                )[0]
            },
        )

    def are_audiobooks_saved(
        self, audiobook_ids: str | Collection[str], /
    ) -> list[bool]:
        """
        `Audiobooks > Check User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference
        /check-users-saved-audiobooks>`_: Check whether one or more
        audiobooks are saved in the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

        Parameters
        ----------
        audiobook_ids : str or Collection[str], positional-only
            Spotify IDs of the audiobooks, provided as either a
            comma-delimited string or as a collection of strings. A
            maximum of 50 IDs can be sent in a request.

            **Examples**:

            .. container::

               * :code:`"18yVqkdbdRvS24c0Ilj2ci"`
               * :code:`"18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ"`
               * :code:`["18yVqkdbdRvS24c0Ilj2ci", "1HGw3J3NxZO1TP1BTtVhpZ"]`

        Returns
        -------
        saved : list[bool]
            Whether the current user has each of the specified
            audiobooks saved in their library.

            **Sample response**: :code:`[False, True]`.
        """
        self._client._require_scopes(
            "audiobooks.are_audiobooks_saved", "user-library-read"
        )
        return self._client._request(
            "GET",
            "me/audiobooks/contains",
            params={
                "ids": self._client._prepare_spotify_ids(
                    audiobook_ids, limit=20
                )[0]
            },
        ).json()
