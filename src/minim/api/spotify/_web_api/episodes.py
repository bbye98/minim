from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import SpotifyResourceAPI
from .users import UsersAPI


class EpisodesAPI(SpotifyResourceAPI):
    """
    Episodes API endpoints for the Spotify Web API.

    .. important::

       This class is managed by :class:`minim.api.spotify.SpotifyWebAPIClient`
       and should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="playback")
    def get_episodes(
        self,
        episode_ids: str | list[str],
        /,
        *,
        country_code: str | None = None,
    ) -> dict[str, Any]:
        """
        `Episodes > Get Episode <https://developer.spotify.com
        /documentation/web-api/reference/get-an-episode>`_: Get Spotify
        catalog information for a show episode․
        `Episodes > Get Several Episodes <https://developer.spotify.com
        /documentation/web-api/reference/get-multiple-episodes>`_: Get
        Spotify catalog information for multiple show episodes.

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
        episode_ids : str or list[str]; positional-only
            Spotify IDs of the show episodes. A maximum of 50 IDs can be
            sent in a request.

            **Examples**:

            * :code:`"77o6BIVlYM3msb4MMIL1jH"`
            * :code:`"77o6BIVlYM3msb4MMIL1jH,0Q86acNRm6V9GYx55SXKwf"`
            * :code:`["77o6BIVlYM3msb4MMIL1jH",
              "0Q86acNRm6V9GYx55SXKwf"]`

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
        episodes : dict[str, Any]
            Spotify content metadata for the show episodes.

            .. admonition:: Sample responses
               :class: response dropdown

               .. tab-set::

                  .. tab-item:: Single show episode

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

                  .. tab-item:: Multiple show episodes

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
        self._client._require_scopes(
            "episodes.get_episodes", "user-read-playback-position"
        )
        return self._get_resources(
            "episodes", episode_ids, country_code=country_code
        )

    @_copy_docstring(UsersAPI.get_my_saved_episodes)
    def get_my_saved_episodes(
        self,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_my_saved_episodes(
            country_code=country_code, limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.save_episodes)
    def save_episodes(self, episode_ids: str | list[str], /) -> None:
        self._client.users.save_episodes(episode_ids)

    @_copy_docstring(UsersAPI.remove_saved_episodes)
    def remove_saved_episodes(self, episode_ids: str | list[str], /) -> None:
        self._client.users.remove_saved_episodes(episode_ids)

    @_copy_docstring(UsersAPI.are_episodes_saved)
    def are_episodes_saved(
        self, episode_ids: str | list[str], /
    ) -> list[bool]:
        return self._client.users.are_episodes_saved(episode_ids)
