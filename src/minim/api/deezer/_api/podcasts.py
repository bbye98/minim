from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import DeezerResourceAPI
from .users import UsersAPI


class PodcastsAPI(DeezerResourceAPI):
    """
    Podcasts API endpoints for the Deezer API.

    .. note::

       This class is managed by :class:`minim.api.deezer.DeezerAPI` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="popularity")
    def get_podcast(self, podcast_id: int | str, /) -> dict[str, Any]:
        """
        `Podcast <https://developers.deezer.com/api/podcast>`_: Get
        Deezer catalog information for a podcast.

        Parameters
        ----------
        podcast_id : int or str; positional-only
            Deezer ID of the podcast.

            **Examples**: :code:`436862`, :code:`"2740882"`.

        Returns
        -------
        podcast : dict[str, Any]
            Deezer content metadata for the podcast.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "available": <bool>,
                    "description": <str>,
                    "fans": <int>,
                    "id": <int>,
                    "link": <str>,
                    "picture": <str>,
                    "picture_big": <str>,
                    "picture_medium": <str>,
                    "picture_small": <str>,
                    "picture_xl": <str>,
                    "share": <str>,
                    "title": <str>,
                    "type": "podcast"
                  }
        """
        return self._request_resource_relationship(
            "GET", "podcast", podcast_id
        )

    @TTLCache.cached_method(ttl="daily")
    def get_podcast_episodes(
        self,
        podcast_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Podcast > Episodes <https://developers.deezer.com/api/podcast
        /episodes>`_: Get Deezer catalog information for a podcast's
        episodes.

        Parameters
        ----------
        podcast_id : int or str; positional-only
            Deezer ID of the podcast.

            **Examples**: :code:`436862`, :code:`"2740882"`.

        limit : int or None; keyword-only; optional
            Maximum number of episodes to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`25`.

        offset : int or None; keyword-only; optional
            Index of the first episode to return. Use with `limit` to
            get the next batch of episodes.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        episodes : dict[str, Any]
            Page of Deezer content metadata for the podcast's episodes.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "duration": <int>,
                        "id": <int>,
                        "picture": <str>,
                        "release_date": <str>,
                        "title": <str>,
                        "type": "episode"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        return self._request_resource_relationship(
            "GET",
            "podcast",
            podcast_id,
            "episodes",
            limit=limit,
            offset=offset,
        )

    @_copy_docstring(UsersAPI.follow_podcast)
    def follow_podcast(
        self, podcast_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        return self._client.users.follow_podcast(podcast_id, user_id=user_id)

    @_copy_docstring(UsersAPI.unfollow_podcast)
    def unfollow_podcast(
        self,
        podcast_id: int | str,
        /,
        *,
        user_id: int | str = "me",
    ) -> bool:
        return self._client.users.unfollow_podcast(podcast_id, user_id=user_id)
