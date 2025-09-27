from collections.abc import Collection
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPIAudiobookEndpoints:
    """
    Spotify Web API audiobook endpoints.

    .. important::

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

    def get_audiobooks(
        self, audiobook_ids: str | Collection[str], /, *, market: str = None
    ) -> dict[str, Any]:
        """
        `Audiobooks > Get Audiobook <https://developer.spotify.com
        /documentation/web-api/reference/get-an-audiobook>`_: Get Spotify
        catalog information for a single audiobook․
        `Audiobook > Get Several Audiobooks <https://developer.spotify.com
        /documentation/web-api/reference/get-several-audiobooks>`_: Get
        Spotify catalog information for multiple audiobooks.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

        Parameters
        ----------
        audiobook_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the audiobooks. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"18yVqkdbdRvS24c0Ilj2ci"`,
            :code:`"18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ"`,
            :code:`["18yVqkdbdRvS24c0Ilj2ci", "1HGw3J3NxZO1TP1BTtVhpZ"]`.

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
                             "languages": [
                               "fr",
                               "en"
                             ],
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
                       "type": <str>,
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
                                 "type": <str>,
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
                         }
                       ]
                     }
        """
        audiobook_ids, n_ids = self._client._normalize_spotify_ids(
            audiobook_ids, limit=50
        )
        if n_ids > 1:
            return self._client._request(
                "GET",
                "audiobooks",
                params={"ids": audiobook_ids, "market": market},
            ).json()
        return self._client._request(
            "GET", f"audiobooks/{audiobook_ids}", params={"market": market}
        ).json()

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
        about an audiobook's chapters.

        .. important::

           Audiobooks are only available in the US, UK, Canada, Ireland,
           New Zealand and Australia markets.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

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
            Maximum number of chapters to return.

            **Valid values**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first chapter to return. Use with `limit` to
            get the next set of chapters.

            **Default**: :code:`0`.

        Returns
        -------
        chapters : dict[str, Any]
            Spotify content metadata for the audiobook's chapters.

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
                        "type": <str>,
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
        return self._client._request(
            "GET",
            f"audiobooks/{audiobook_id}/chapters",
            params={"market": market, "limit": limit, "offset": offset},
        ).json()

    def get_saved_audiobooks(
        self,
        *,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Audiobooks > Get User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference
        /get-users-saved-audiobooks>`_: Get the audiobooks saved in the
        current user's "Your Music" library.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read`
                 Access your saved content.

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs.

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

            **Valid values**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first audiobook to return. Use with `limit` to
            get the next set of audiobook

            **Default**: :code:`0`.

        Returns
        -------
        saved_audiobooks : dict[str, Any]
            Spotify content metadata for the user's saved audiobooks.

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
                        "type": <str>,
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
            "get_saved_audiobooks", "user-library-read"
        )
        return self._client._request(
            "GET",
            "me/audiobooks",
            params={"market": market, "limit": limit, "offset": offset},
        ).json()

    def save_audiobooks(self, audiobook_ids: str | Collection[str], /) -> None:
        """
        `Albums > Save Audiobooks for Current User
        <https://developer.spotify.com/documentation/web-api/reference
        /save-albums-user>`_: Save one or more audiobooks to the current
        user's "Your Music" library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify`
                  Manage your saved content.

        Parameters
        ----------
        audiobook_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the audiobooks. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"18yVqkdbdRvS24c0Ilj2ci"`,
            :code:`"18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ"`,
            :code:`["18yVqkdbdRvS24c0Ilj2ci", "1HGw3J3NxZO1TP1BTtVhpZ"]`.
        """
        self._client._require_scopes("save_audiobooks", "user-library-modify")
        self._client._request(
            "PUT",
            "me/audiobooks",
            params={
                "ids": self._client._normalize_spotify_ids(
                    audiobook_ids, limit=50
                )[0]
            },
        )

    def remove_saved_audiobooks(
        self, audiobook_ids: str | Collection[str], /
    ) -> None:
        """
        `Albums > Remove User's Saved Audiobooks
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-audiobooks-user>`_: Save one or more audiobooks to the
        current user's "Your Music" library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify`
                  Manage your saved content.

        Parameters
        ----------
        audiobook_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the audiobooks. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"18yVqkdbdRvS24c0Ilj2ci"`,
            :code:`"18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ"`,
            :code:`["18yVqkdbdRvS24c0Ilj2ci", "1HGw3J3NxZO1TP1BTtVhpZ"]`.
        """
        self._client._require_scopes(
            "remove_saved_audiobooks", "user-library-modify"
        )
        self._client._request(
            "DELETE",
            "me/audiobooks",
            params={
                "ids": self._client._normalize_spotify_ids(
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
        /check-users-saved-audiobooks>`_: Check if one or more
        audiobooks are already saved in the current user's "Your Music"
        library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read`
                  Access your saved content.

        Parameters
        ----------
        audiobook_ids : str or Collection[str], positional-only
            (Comma-separated) list of Spotify IDs of the audiobooks. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"18yVqkdbdRvS24c0Ilj2ci"`,
            :code:`"18yVqkdbdRvS24c0Ilj2ci,1HGw3J3NxZO1TP1BTtVhpZ"`,
            :code:`["18yVqkdbdRvS24c0Ilj2ci", "1HGw3J3NxZO1TP1BTtVhpZ"]`.

        Returns
        -------
        are_audiobooks_saved : list[bool]
            Whether the current user has each of the specified
            audiobooks saved in their "Your Music" library.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  [False, True]
        """
        self._client._require_scopes(
            "are_audiobooks_saved", "user-library-read"
        )
        return self._client._request(
            "GET",
            "me/audiobooks/contains",
            params={
                "ids": self._client._normalize_spotify_ids(
                    audiobook_ids, limit=20
                )[0]
            },
        ).json()
