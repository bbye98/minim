from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import DeezerResourceAPI
from .charts import ChartsAPI
from .users import UsersAPI


class RadiosAPI(DeezerResourceAPI):
    """
    Radios API endpoints for the Deezer API.

    .. important::

       This class is managed by :class:`minim.api.deezer.DeezerAPIClient` and
       should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="static")
    def get_radio(self, radio_id: int | str, /) -> dict[str, Any]:
        """
        `Radio <https://developers.deezer.com/api/radio>`_: Get Deezer
        catalog information for a radio.

        Parameters
        ----------
        radio_id : int or str; positional-only
            Deezer ID of the radio.

            **Examples**: :code:`31061`, :code:`"37151"`.

        Returns
        -------
        radio : dict[str, Any]
            Deezer content metadata for the radio.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "description": <str>,
                    "id": <int>,
                    "md5_image": <str>,
                    "picture": <str>,
                    "picture_big": <str>,
                    "picture_medium": <str>,
                    "picture_small": <str>,
                    "picture_xl": <str>,
                    "share": <str>,
                    "title": <str>,
                    "tracklist": <str>,
                    "type": "radio"
                  }
        """
        return self._request_resource_relationship("GET", "radio", radio_id)

    @TTLCache.cached_method(ttl="static")
    def get_per_genre_radios(self) -> dict[str, Any]:
        """
        `Radio > Genres <https://developers.deezer.com/api/radio
        /genres>`_: Get Deezer catalog information for radios,
        grouped by their genre IDs.

        Returns
        -------
        radios : dict[str, Any]
            Deezer content metadata for the radios.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <int>,
                        "radios": [
                          {
                            "id": <int>,
                            "md5_image": <str>,
                            "picture": <str>,
                            "picture_big": <str>,
                            "picture_medium": <str>,
                            "picture_small": <str>,
                            "picture_xl": <str>,
                            "title": <str>,
                            "tracklist": <str>,
                            "type": "radio"
                          }
                        ],
                        "title": <str>
                      }
                    ]
                  }
        """
        return self._client._request("GET", "radio/genres").json()

    def get_radio_tracks(
        self,
        radio_id: int | str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Radio > Tracks <https://developers.deezer.com/api/radio
        /tracks>`_: Get Deezer catalog information for the tracks in a
        radio.

        Parameters
        ----------
        radio_id : int or str; positional-only
            Deezer ID of the radio.

            **Examples**: :code:`31061`, :code:`"37151"`.

        limit : int or None; keyword-only; optional
            Maximum number of tracks to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`40`.

        offset : int or None; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of Deezer content metadata for the tracks in the radio.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "data": [
                      {
                        "album": {
                          "cover": <str>,
                          "cover_big": <str>,
                          "cover_medium": <str>,
                          "cover_small": <str>,
                          "cover_xl": <str>,
                          "id": <int>,
                          "md5_image": <str>,
                          "title": <str>,
                          "tracklist": <str>,
                          "type": "album"
                        },
                        "artist": {
                          "id": <int>,
                          "link": <str>,
                          "name": <str>,
                          "picture": <str>,
                          "picture_big": <str>,
                          "picture_medium": <str>,
                          "picture_small": <str>,
                          "picture_xl": <str>,
                          "tracklist": <str>,
                          "type": "artist"
                        },
                        "duration": <int>,
                        "explicit_content_cover": <int>,
                        "explicit_content_lyrics": <int>,
                        "explicit_lyrics": false,
                        "id": <int>,
                        "link": <str>,
                        "md5_image": <str>,
                        "preview": <str>,
                        "rank": <int>,
                        "readable": <bool>,
                        "title": <str>,
                        "title_short": <str>,
                        "title_version": <str>,
                        "type": "track"
                      }
                    ]
                  }
        """
        return self._request_resource_relationship(
            "GET", "radio", radio_id, "tracks", limit=limit, offset=offset
        )

    @TTLCache.cached_method(ttl="static")
    def get_genre_radios(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """
        `Radio > Lists <https://developers.deezer.com/api/radio
        /lists>`_: Get Deezer catalog information for all genres'
        radios.

        Parameters
        ----------
        limit : int or None; keyword-only; optional
            Maximum number of radios to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`25`.

        offset : int or None; keyword-only; optional
            Index of the first radio to return. Use with `limit` to get
            the next batch of radios.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        radios : dict[str, Any]
            Page of Deezer content metadata for all genres' radios.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <int>,
                        "md5_image": <str>,
                        "picture": <str>,
                        "picture_big": <str>,
                        "picture_medium": <str>,
                        "picture_small": <str>,
                        "picture_xl": <str>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "radio"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        params = {}
        if limit is not None:
            self._validate_number("limit", limit, int, 1)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["index"] = offset
        return self._client._request(
            "GET", "radio/lists", params=params
        ).json()

    @_copy_docstring(ChartsAPI.get_top_radios)
    def get_top_radios(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        return self._client.charts.get_top_radios(limit=limit, offset=offset)

    @_copy_docstring(UsersAPI.get_followed_radios)
    def get_followed_radios(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_followed_radios(
            user_id, limit=limit, offset=offset
        )

    @_copy_docstring(UsersAPI.save_radio)
    def save_radio(
        self, radio_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        return self._client.users.save_radio(radio_id, user_id=user_id)

    @_copy_docstring(UsersAPI.remove_saved_radio)
    def remove_saved_radio(
        self, radio_id: int | str, /, *, user_id: int | str = "me"
    ) -> bool:
        return self._client.users.remove_saved_radio(radio_id, user_id=user_id)

    @_copy_docstring(UsersAPI.get_radio_recommendations)
    def get_radio_recommendations(
        self,
        user_id: int | str = "me",
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._client.users.get_radio_recommendations(
            user_id, limit=limit, offset=offset
        )
