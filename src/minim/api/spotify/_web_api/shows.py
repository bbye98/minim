from collections.abc import Collection
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPIShowEndpoints:
    """
    Spotify Web API show endpoints.

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

    def get_shows(
        self, show_ids: str | Collection[str], /, *, market: str | None = None
    ) -> dict[str, Any]:
        """
        `Shows > Get Show <https://developer.spotify.com/documentation
        /web-api/reference/get-a-show>`_: Get Spotify catalog
        information for a single show․
        `Shows > Get Several Shows <https://developer.spotify.com
        /documentation/web-api/reference/get-multiple-shows>`_: Get
        Spotify catalog information for multiple shows.

        .. admonition:: Third-party application mode
           :class: authorization-scope dropdown

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        show_ids : str or Collection[str], positional-only
            Spotify IDs of the shows, provided as either a
            comma-separated string or a collection of strings. A
            maximum of 50 IDs can be sent in one request.

            .. container::

               **Examples**:
               * :code:`"5CfCWKI5pZ28U0uOzXkDHe"`
               * :code:`"5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ"`
               * :code:`[5CfCWKI5pZ28U0uOzXkDHe", "5as3aKmN2k11yfDDDSrvaZ"]`

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
        shows : dict[str, Any]
            Spotify content metadata for the shows.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single show

                  .. code::

                     {
                       "available_markets": <list[str]>,
                       "copyrights": [
                         {
                           "text": <str>,
                           "type": <str>
                         }
                       ],
                       "description": <str>,
                       "episodes": {
                         "href": <str>,
                         "items": [
                           {
                             "audio_preview_url": <str>,
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
                             "is_externally_hosted": <bool>,
                             "is_playable": <bool>,
                             "language": <str>,
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
                             "type": "episode",
                             "uri": <str>
                           }
                         ],
                         "limit": <int>,
                         "next": <str>,
                         "offset": <int>,
                         "previous": <str>,
                         "total": <int>
                       },
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
                       "is_externally_hosted": <bool>,
                       "languages": <list[str]>,
                       "media_type": <str>,
                       "name": <str>,
                       "publisher": <str>,
                       "total_episodes": <int>,
                       "type": "show",
                       "uri": <str>
                     }

               .. tab:: Multiple shows

                  .. code::

                     {
                       "shows": [
                         {
                           "available_markets": <list[str]>,
                           "copyrights": [
                             {
                               "text": <str>,
                               "type": <str>
                             }
                           ],
                           "description": <str>,
                           "episodes": {
                             "href": <str>,
                             "items": [
                               {
                                 "audio_preview_url": <str>,
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
                                 "is_externally_hosted": <bool>,
                                 "is_playable": <bool>,
                                 "language": <str>,
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
                                 "type": "episode",
                                 "uri": <str>
                               }
                             ],
                             "limit": <int>,
                             "next": <str>,
                             "offset": <int>,
                             "previous": <str>,
                             "total": <int>
                           },
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
                           "is_externally_hosted": <bool>,
                           "languages": <list[str]>,
                           "media_type": <str>,
                           "name": <str>,
                           "publisher": <str>,
                           "total_episodes": <int>,
                           "type": "show",
                           "uri": <str>
                         }
                       ]
                     }
        """
        string = isinstance(show_ids, str)
        show_ids, n_ids = self._client._prepare_spotify_ids(show_ids, limit=50)
        params = {}
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if string and n_ids == 1:
            return self._client._request(
                "GET", f"shows/{show_ids}", params=params
            ).json()

        params["ids"] = show_ids
        return self._client._request("GET", "show", params=params).json()

    def get_show_episodes(
        self,
        show_id: str,
        /,
        *,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Shows > Get Show Episodes <https://developer.spotify.com
        /documentation/web-api/reference/get-a-shows-episodes>`_: Get
        Spotify catalog information for episodes in a show.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-read-playback-position` scope
                 Read your position in content you have played. `Learn
                 more. <https://developer.spotify.com/documentation
                 /web-api/concepts/scopes#user-read-playback-position>`__

           .. tab:: Optional

              Extended quota mode before November 11, 2024
                  Access 30-second preview URLs. `Learn more.
                  <https://developer.spotify.com/blog
                  /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        show_id : str
            Spotify ID of the show.

            **Examples**: :code:`"38bS44xjbVVZ3No3ByF1dJ"`.

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
            Maximum number of show episodes to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first show episode to return. Use with `limit`
            to get the next set of show episodes.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        episodes : dict[str, Any]
            Pages of Spotify content metadata for the show's episodes.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "audio_preview_url": <str>,
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
                        "is_externally_hosted": <bool>,
                        "is_playable": <bool>,
                        "language": <str>,
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
                        "type": "episodes",
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
            "get_show_episodes", "user-read-playback-position"
        )
        self._client._validate_spotify_id(show_id)
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
            "GET", f"shows/{show_id}/episodes", params=params
        ).json()

    def get_my_saved_shows(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        `Shows > Get User's Saved Shows <https://developer.spotify.com
        /documentation/web-api/reference/get-users-saved-shows>`_: Get
        the shows saved in the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

        Parameters
        ----------
        limit : int, keyword-only, optional
            Maximum number of shows to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first show to return. Use with `limit` to get
            the next set of shows.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.

        Returns
        -------
        shows : dict[str, Any]
            Pages of Spotify content metadata for the user's saved shows.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "added_at": <str>,
                        "show": {
                          "available_markets": <list[str]>,
                          "copyrights": [
                            {
                              "text": <str>,
                              "type": <str>
                            }
                          ],
                          "description": <str>,
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
                          "is_externally_hosted": <bool>,
                          "languages": <list[str]>,
                          "media_type": <str>,
                          "name": <str>,
                          "publisher": <str>,
                          "total_episodes": <int>,
                          "type": "show",
                          "uri": <str>
                        }
                      }
                    ],
                    "limit": <int>,
                    "next": <str>,
                    "offset": <int>,
                    "previous": <str>,
                    "total": <int>
                  }
        """
        self._client._require_scopes("get_my_saved_shows", "user-library-read")
        params = {}
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request("GET", "me/shows", params=params).json()

    def save_shows(self, show_ids: str | Collection[str], /) -> None:
        """
        `Shows > Save Shows for Current User
        <https://developer.spotify.com/documentation/web-api/reference
        /save-shows-user>`_: Save one or more shows to the current
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
        show_ids : str or Collection[str], positional-only
            Spotify IDs of the shows, provided as either a
            comma-separated string or a collection of strings. A
            maximum of 50 IDs can be sent in one request.

            .. container::

               **Examples**:
               * :code:`"5CfCWKI5pZ28U0uOzXkDHe"`
               * :code:`"5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ"`
               * :code:`[5CfCWKI5pZ28U0uOzXkDHe", "5as3aKmN2k11yfDDDSrvaZ"]`
        """
        self._client._require_scopes("save_shows", "user-library-modify")
        self._client._request(
            "PUT",
            "me/shows",
            params={
                "ids": self._client._prepare_spotify_ids(show_ids, limit=50)[0]
            },
        )

    def remove_saved_shows(self, show_ids: str | Collection[str], /) -> None:
        """
        `Shows > Remove User's Saved Shows
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-shows-user>`_: Save one or more shows to the current
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
        show_ids : str or Collection[str], positional-only
            Spotify IDs of the shows, provided as either a
            comma-separated string or a collection of strings. A
            maximum of 50 IDs can be sent in one request.

            .. container::

               **Examples**:
               * :code:`"5CfCWKI5pZ28U0uOzXkDHe"`
               * :code:`"5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ"`
               * :code:`[5CfCWKI5pZ28U0uOzXkDHe", "5as3aKmN2k11yfDDDSrvaZ"]`
        """
        self._client._require_scopes(
            "remove_saved_shows", "user-library-modify"
        )
        self._client._request(
            "DELETE",
            "me/shows",
            params={
                "ids": self._client._prepare_spotify_ids(show_ids, limit=50)[0]
            },
        )

    def are_shows_saved(self, show_ids: str | Collection[str], /) -> list[bool]:
        """
        `Shows > Check User's Saved Shows
        <https://developer.spotify.com/documentation/web-api/reference
        /check-users-saved-shows>`_: Check whether one or more shows are
        saved in the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read` scope
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

        Parameters
        ----------
        show_ids : str or Collection[str], positional-only
            Spotify IDs of the shows, provided as either a
            comma-separated string or a collection of strings. A
            maximum of 50 IDs can be sent in one request.

            .. container::

               **Examples**:
               * :code:`"5CfCWKI5pZ28U0uOzXkDHe"`
               * :code:`"5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ"`
               * :code:`[5CfCWKI5pZ28U0uOzXkDHe", "5as3aKmN2k11yfDDDSrvaZ"]`

        Returns
        -------
        saved : list[bool]
            Whether the current user has each of the specified shows
            saved in their library.

            **Sample response**: :code:`[False, True]`.
        """
        self._client._require_scopes("are_shows_saved", "user-library-read")
        return self._client._request(
            "GET",
            "me/shows/contains",
            params={
                "ids": self._client._prepare_spotify_ids(show_ids, limit=20)[0]
            },
        ).json()
