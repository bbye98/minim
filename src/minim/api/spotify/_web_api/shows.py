from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import SpotifyResourceAPI
from .users import UsersAPI


class ShowsAPI(SpotifyResourceAPI):
    """
    Shows API endpoints for the Spotify Web API.

    .. note::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPIClient`
       and should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="playback")
    def get_shows(
        self, show_ids: str | list[str], /, *, country_code: str | None = None
    ) -> dict[str, Any]:
        """
        `Shows > Get Show <https://developer.spotify.com/documentation
        /web-api/reference/get-a-show>`_: Get Spotify catalog
        information for a show․
        `Shows > Get Several Shows <https://developer.spotify.com
        /documentation/web-api/reference/get-multiple-shows>`_: Get
        Spotify catalog information for multiple shows.

        .. admonition:: Third-party application mode
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 :code:`user-read-playback-position` scope
                    Read your position in content you have played.
                    `Learn more. <https://developer.spotify.com
                    /documentation/web-api/concepts
                    /scopes#user-read-playback-position>`__

                 Extended quota mode before November 27, 2024
                    Access 30-second preview URLs. `Learn more.
                    <https://developer.spotify.com/blog
                    /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        show_ids : str or list[str]; positional-only
            Spotify IDs of the shows. A maximum of 50 IDs can be sent in
            a request.

            **Examples**:

            * :code:`"5CfCWKI5pZ28U0uOzXkDHe"`
            * :code:`"5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ"`
            * :code:`[5CfCWKI5pZ28U0uOzXkDHe",
              "5as3aKmN2k11yfDDDSrvaZ"]`

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
        shows : dict[str, Any]
            Spotify content metadata for the shows.

            .. admonition:: Sample responses
               :class: response dropdown

               .. tab-set::

                  .. tab-item:: Single show

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

                  .. tab-item:: Multiple shows

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
        return self._get_resources(
            "shows", show_ids, country_code=country_code
        )

    @TTLCache.cached_method(ttl="playback")
    def get_show_episodes(
        self,
        show_id: str,
        /,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Shows > Get Show Episodes <https://developer.spotify.com
        /documentation/web-api/reference/get-a-shows-episodes>`_: Get
        Spotify catalog information for episodes in a show.

        .. admonition:: Authorization scope and third-party application mode
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 :code:`user-read-playback-position` scope
                    Read your position in content you have played.
                    `Learn more. <https://developer.spotify.com
                    /documentation/web-api/concepts
                    /scopes#user-read-playback-position>`__

              .. tab-item:: Optional

                 Extended quota mode before November 27, 2024
                    Access 30-second preview URLs. `Learn more.
                    <https://developer.spotify.com/blog
                    /2024-11-27-changes-to-the-web-api>`__

        Parameters
        ----------
        show_id : str; positional-only
            Spotify ID of the show.

            **Examples**: :code:`"38bS44xjbVVZ3No3ByF1dJ"`.

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
            Maximum number of show episodes to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first show episode to return. Use with `limit`
            to get the next batch of show episodes.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        episodes : dict[str, Any]
            Page of Spotify content metadata for the show's episodes.

            .. admonition:: Sample response
               :class: response dropdown

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
            "shows.get_show_episodes", "user-read-playback-position"
        )
        return self._get_resource_items(
            "shows",
            show_id,
            "episodes",
            country_code=country_code,
            limit=limit,
            offset=offset,
        )

    @_copy_docstring(UsersAPI.get_my_saved_shows)
    def get_my_saved_shows(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        return self._client.users.get_my_saved_shows(
            limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.save_shows)
    def save_shows(self, show_ids: str | list[str], /) -> None:
        self._client.users.save_shows(show_ids)

    @_copy_docstring(UsersAPI.remove_saved_shows)
    def remove_saved_shows(self, show_ids: str | list[str], /) -> None:
        self._client.users.remove_saved_shows(show_ids)

    @_copy_docstring(UsersAPI.are_shows_saved)
    def are_shows_saved(self, show_ids: str | list[str], /) -> list[bool]:
        return self._client.users.are_shows_saved(show_ids)
