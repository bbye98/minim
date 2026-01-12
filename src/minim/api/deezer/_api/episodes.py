from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import DeezerResourceAPI
from .users import UsersAPI


class EpisodesAPI(DeezerResourceAPI):
    """
    Episodes API endpoints for the Deezer API.

    .. note::

       This class is managed by :class:`minim.api.deezer.DeezerAPI` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="static")
    def get_episode(self, episode_id: int | str, /) -> dict[str, Any]:
        """
        `Episode <https://developers.deezer.com/api/episode>`_: Get
        Deezer catalog information for a podcast episode.

        Parameters
        ----------
        episode_id : int or str; positional-only
            Deezer ID of the episode.

            **Example**: :code:`796445891`, :code:`"822265072"`.

        Returns
        -------
        episode : dict[str, Any]
            Deezer content metadata for the podcast episode.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "available": <bool>,
                    "description": <str>,
                    "duration": <int>,
                    "id": <int>,
                    "link": <str>,
                    "picture": <str>,
                    "picture_big": <str>,
                    "picture_medium": <str>,
                    "picture_small": <str>,
                    "picture_xl": <str>,
                    "podcast": {
                      "id": <int>,
                      "link": <str>,
                      "picture": <str>,
                      "picture_big": <str>,
                      "picture_medium": <str>,
                      "picture_small": <str>,
                      "picture_xl": <str>,
                      "title": <str>,
                      "type": "podcast"
                    },
                    "release_date": <str>,
                    "share": <str>,
                    "title": <str>,
                    "track_token": <str>,
                    "type": "episode"
                  }
        """
        return self._request_resource_relationship(
            "GET", "episode", episode_id
        )

    @_copy_docstring(UsersAPI.set_episode_resume_point)
    def set_episode_resume_point(
        self, episode_id: int | str, /, position: int
    ) -> dict[str, Any]:
        return self._client.users.set_episode_resume_point(
            episode_id, position=position
        )

    @_copy_docstring(UsersAPI.remove_episode_resume_point)
    def remove_episode_resume_point(
        self, episode_id: int | str, /
    ) -> dict[str, Any]:
        return self._client.users.remove_episode_resume_point(episode_id)
