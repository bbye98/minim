from collections.abc import Collection
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPIEpisodeEndpoints:
    """
    Spotify Web API show episode endpoints.

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

    def get_episodes(
        self,
        episode_ids: str | Collection[str],
        /,
        *,
        market: str | None = None,
    ) -> dict[str, Any]:
        """
        `Episodes > Get Episode <https://developer.spotify.com
        /documentation/web-api/reference/get-an-episode>`_: Get Spotify
        catalog information for a single show episode․
        `Episodes > Get Several Episodes <https://developer.spotify.com
        /documentation/web-api/reference/get-multiple-episodes>`_: Get
        Spotify catalog information for multiple show episodes.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-read-playback-position`
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
        episode_ids : str or Collection[str], positional-only
            Spotify IDs of the show episodes, provided as either a
            comma-separated string or a collection of strings. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"77o6BIVlYM3msb4MMIL1jH"`,
            :code:`"77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf"`,
            :code:`["77o6BIVlYM3msb4MMIL1jH", "0Q86acNRm6V9GYx55SXKwf"]`.

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
        episodes : dict[str, Any]
            Spotify content metadata for the show episodes.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single show episode

                  .. code::

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
                       },
                       "type": "episode",
                       "uri": <str>
                     }

               .. tab:: Multiple show episodes

                  .. code::

                     {
                       "episodes": [
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
                           },
                           "type": "episode",
                           "uri": <str>
                         }
                       ]
                     }
        """
        is_string = isinstance(episode_ids, str)
        episode_ids, n_ids = self._client._prepare_spotify_ids(
            episode_ids, limit=50
        )
        params = {}
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if is_string and n_ids == 1:
            return self._client._request(
                "GET", f"episodes/{episode_ids}", params=params
            ).json()

        params["ids"] = episode_ids
        return self._client._request("GET", "episodes", params=params).json()

    def get_my_saved_episodes(
        self,
        *,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Episodes > Get User's Saved Episodes
        <https://developer.spotify.com/documentation/web-api/reference
        /get-multiple-episodes>`_: Get Spotify catalog information for
        the show episodes saved in the current user's library.

        .. admonition:: Authorization scope and third-party application mode
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read`
                  Access your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-read>`__

              :code:`user-read-playback-position`
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
            Pages of Spotify content metadata for the user's saved show
            episodes.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "href": <str>,
                    "items": [
                      {
                        "added_at": <str>,
                        "episode": {
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
                          },
                          "type": "episode",
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
        self._client._require_scopes(
            "get_my_saved_episodes",
            ["user-library-read", "user-read-playback-position"],
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
        return self._client._request("GET", "me/episodes", params=params).json()

    def save_episodes(self, episode_ids: str | Collection[str], /) -> None:
        """
        `Episodes > Save Episodes for Current User
        <https://developer.spotify.com/documentation/web-api/reference
        /save-episodes-user>`_: Save one or more show episodes to the
        current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify`
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        episode_ids : str or Collection[str], positional-only
            Spotify IDs of the show episodes, provided as either a
            comma-separated string or a collection of strings. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"77o6BIVlYM3msb4MMIL1jH"`,
            :code:`"77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf"`,
            :code:`["77o6BIVlYM3msb4MMIL1jH", "0Q86acNRm6V9GYx55SXKwf"]`.
        """
        self._client._require_scopes("save_episodes", "user-library-modify")
        self._client._request(
            "PUT",
            "me/episodes",
            params={
                "ids": self._client._prepare_spotify_ids(episode_ids, limit=50)[
                    0
                ]
            },
        )

    def remove_saved_episodes(
        self, episode_ids: str | Collection[str], /
    ) -> None:
        """
        `Episodes > Remove User's Saved Episodes
        <https://developer.spotify.com/documentation/web-api/reference
        /remove-episodes-user>`_: Remove one or more show episodes from
        the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-modify`
                  Manage your saved content. `Learn more.
                  <https://developer.spotify.com/documentation/web-api
                  /concepts/scopes#user-library-modify>`__

        Parameters
        ----------
        episode_ids : str or Collection[str], positional-only
            Spotify IDs of the show episodes, provided as either a
            comma-separated string or a collection of strings. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"77o6BIVlYM3msb4MMIL1jH"`,
            :code:`"77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf"`,
            :code:`["77o6BIVlYM3msb4MMIL1jH", "0Q86acNRm6V9GYx55SXKwf"]`.
        """
        self._client._require_scopes(
            "remove_saved_episodes", "user-library-modify"
        )
        self._client._request(
            "DELETE",
            "me/episodes",
            params={
                "ids": self._client._prepare_spotify_ids(episode_ids, limit=50)[
                    0
                ]
            },
        )

    def are_episodes_saved(
        self, episode_ids: str | Collection[str], /
    ) -> list[bool]:
        """
        `Episodes > Check User's Saved Episodes
        <https://developer.spotify.com/documentation/web-api/reference
        /check-users-saved-episodes>`_: Check whether one or more show
        episodes are saved in the current user's library.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user-library-read`
                  Access your saved content.

        Parameters
        ----------
        episode_ids : str or Collection[str], positional-only
            Spotify IDs of the show episodes, provided as either a
            comma-separated string or a collection of strings. A
            maximum of 50 IDs can be sent in one request.

            **Examples**: :code:`"77o6BIVlYM3msb4MMIL1jH"`,
            :code:`"77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf"`,
            :code:`["77o6BIVlYM3msb4MMIL1jH", "0Q86acNRm6V9GYx55SXKwf"]`.

        Returns
        -------
        saved_flags : list[bool]
            Whether the current user has each of the specified show
            episodes saved in their library.

            **Sample response**: :code:`[False, True]`.
        """
        self._client._require_scopes("are_episodes_saved", "user-library-read")
        return self._client._request(
            "GET",
            "me/episodes/contains",
            params={
                "ids": self._client._prepare_spotify_ids(episode_ids, limit=50)[
                    0
                ]
            },
        ).json()
