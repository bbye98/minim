from typing import Any

from ..._shared import TTLCache
from ._shared import DeezerResourceAPI


class SearchAPI(DeezerResourceAPI):
    """
    Search API endpoints for the Deezer API.

    .. note::

       This class is managed by :class:`minim.api.deezer.DeezerAPI` and
       should not be instantiated directly.
    """

    _SORT_FIELDS = {
        "RANKING",
        "TRACK",
        "ARTIST",
        "ALBUM",
        "RATING",
        "DURATION",
    }

    def _search_resource(
        self,
        resource_type: str | None,
        query: str,
        /,
        *,
        strict: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool = False,
    ) -> dict[str, Any]:
        """
        Get Deezer catalog information for albums, artists, playlists,
        podcasts, radios, tracks, and/or users that match a keyword
        string.

        Parameters
        ----------
        resource_type : str or None; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"playlists"`, :code:`"podcasts"`, :code:`"rasios"`,
            :code:`"tracks"`, :code:`"users"`.

        query : str; positional-only; optional
            Search query.

        strict : bool; keyword-only; optional
            Whether to disable fuzzy search and use strict matching.

            **API default**: :code:`False`.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Minimum value**: :code:`1`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the returned items by.

            **Valid values**: :code:`"RANKING"`, :code:`"TRACK"`,
            :code:`"ARTIST"`, :code:`"ALBUM"`, :code:`"RATING"`,
            :code:`"DURATION"`.

        descending : bool; keyword-only; default: :code:`False`
            Whether to sort in descending order. Only applicable when
            `sort_by` is not :code:`"RANKING"`.

        Returns
        -------
        results : dict[str, Any]
            Page of Deezer content metadata for the matching items.
        """
        endpoint = "search"
        if resource_type is not None:
            endpoint += f"/{resource_type}"
        self._validate_type("query", query, str)
        if not len(query) and resource_type != "history":
            raise ValueError("No search query provided.")
        params = {"q": query}
        if strict is not None:
            self._validate_type("strict", strict, bool)
            if strict:
                params["strict"] = "on"
        if limit is not None:
            self._validate_number("limit", limit, int, 1)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["index"] = offset
        if sort_by is not None:
            sort_by = sort_by.strip().upper()
            if sort_by == "RANKING":
                params["order"] = sort_by
            else:
                if sort_by not in self._SORT_FIELDS:
                    sort_fields_str = "', '".join(self._SORT_FIELDS)
                    raise ValueError(
                        f"Invalid sort field {sort_by!r}. "
                        f"Valid values: '{sort_fields_str}'."
                    )
                self._validate_type("descending", descending, bool)
                params["order"] = (
                    f"{sort_by}_{'DESC' if descending else 'ASC'}"
                )
        return self._client._request("GET", endpoint, params=params).json()

    @TTLCache.cached_method(ttl="search")
    def search_albums(
        self,
        query: str,
        /,
        *,
        strict: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool = False,
    ) -> dict[str, Any]:
        """
        `Search > Album <https://developers.deezer.com/api/search
        /album>`_: Get Deezer catalog information for albums that match
        a keyword string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        strict : bool; keyword-only; optional
            Whether to disable fuzzy search and use strict matching.

            **API default**: :code:`False`.

        limit : int; keyword-only; optional
            Maximum number of albums to return.

            **Minimum value**: :code:`1`.

        offset : int; keyword-only; optional
            Index of the first album to return. Use with `limit` to get
            the next batch of albums.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the returned albums by.

            **Valid values**: :code:`"RANKING"`, :code:`"TRACK"`,
            :code:`"ARTIST"`, :code:`"ALBUM"`, :code:`"RATING"`,
            :code:`"DURATION"`.

        descending : bool; keyword-only; default: :code:`False`
            Whether to sort in descending order. Only applicable when
            `sort_by` is not :code:`"RANKING"`.

        Returns
        -------
        albums : dict[str, Any]
            Page of Deezer content metadata for the matching albums.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
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
                        "cover": <str>,
                        "cover_big": <str>,
                        "cover_medium": <str>,
                        "cover_small": <str>,
                        "cover_xl": <str>,
                        "explicit_lyrics": <bool>,
                        "genre_id": <int>,
                        "id": <int>,
                        "link": <str>,
                        "md5_image": <str>,
                        "nb_tracks": <int>,
                        "record_type": <str>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": "album"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        return self._search_resource(
            "album",
            query,
            strict=strict,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @TTLCache.cached_method(ttl="search")
    def search_artists(
        self,
        query: str,
        /,
        *,
        strict: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool = False,
    ) -> dict[str, Any]:
        """
        `Search > Artist <https://developers.deezer.com/api/search
        /artist>`_: Get Deezer catalog information for artists that
        match a keyword string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        strict : bool; keyword-only; optional
            Whether to disable fuzzy search and use strict matching.

            **API default**: :code:`False`.

        limit : int; keyword-only; optional
            Maximum number of artists to return.

            **Minimum value**: :code:`1`.

        offset : int; keyword-only; optional
            Index of the first artist to return. Use with `limit` to get
            the next batch of artists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the returned artists by.

            **Valid values**: :code:`"RANKING"`, :code:`"TRACK"`,
            :code:`"ARTIST"`, :code:`"ALBUM"`, :code:`"RATING"`,
            :code:`"DURATION"`.

        descending : bool; keyword-only; default: :code:`False`
            Whether to sort in descending order. Only applicable when
            `sort_by` is not :code:`"RANKING"`.

        Returns
        -------
        artists : dict[str, Any]
            Page of Deezer content metadata for the matching artists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <int>,
                        "link": <str>,
                        "name": <str>,
                        "nb_album": <int>,
                        "nb_fan": <int>,
                        "picture": <str>,
                        "picture_big": <str>,
                        "picture_medium": <str>,
                        "picture_small": <str>,
                        "picture_xl": <str>,
                        "radio": <bool>,
                        "tracklist": <str>,
                        "type": "artist"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        return self._search_resource(
            "artist",
            query,
            strict=strict,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @TTLCache.cached_method(ttl="search")
    def search_playlists(
        self,
        query: str,
        /,
        *,
        strict: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool = False,
    ) -> dict[str, Any]:
        """
        `Search > Playlist <https://developers.deezer.com/api/search
        /playlist>`_: Get Deezer catalog information for playlists that
        match a keyword string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        strict : bool; keyword-only; optional
            Whether to disable fuzzy search and use strict matching.

            **API default**: :code:`False`.

        limit : int; keyword-only; optional
            Maximum number of playlists to return.

            **Minimum value**: :code:`1`.

        offset : int; keyword-only; optional
            Index of the first playlist to return. Use with `limit` to get
            the next batch of playlists.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the returned playlists by.

            **Valid values**: :code:`"RANKING"`, :code:`"TRACK"`,
            :code:`"ARTIST"`, :code:`"ALBUM"`, :code:`"RATING"`,
            :code:`"DURATION"`.

        descending : bool; keyword-only; default: :code:`False`
            Whether to sort in descending order. Only applicable when
            `sort_by` is not :code:`"RANKING"`.

        Returns
        -------
        playlists : dict[str, Any]
            Page of Deezer content metadata for the matching playlists.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "add_date": <str>,
                        "checksum": <str>,
                        "creation_date": <str>,
                        "id": <int>,
                        "link": <str>,
                        "md5_image": <str>,
                        "mod_date": <str>,
                        "nb_tracks": <int>,
                        "picture": <str>,
                        "picture_big": <str>,
                        "picture_medium": <str>,
                        "picture_small": <str>,
                        "picture_type": <str>,
                        "picture_xl": <str>,
                        "public": <bool>,
                        "title": <str>,
                        "tracklist": <str>,
                        "type": <str>,
                        "user": {
                          "id": <int>,
                          "name": <str>,
                          "tracklist": <str>,
                          "type": "user"
                        }
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        return self._search_resource(
            "playlist",
            query,
            strict=strict,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @TTLCache.cached_method(ttl="search")
    def search_podcasts(
        self,
        query: str,
        /,
        *,
        strict: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool = False,
    ) -> dict[str, Any]:
        """
        `Search > Podcast <https://developers.deezer.com/api/search
        /podcast>`_: Get Deezer catalog information for podcasts that
        match a keyword string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        strict : bool; keyword-only; optional
            Whether to disable fuzzy search and use strict matching.

            **API default**: :code:`False`.

        limit : int; keyword-only; optional
            Maximum number of podcasts to return.

            **Minimum value**: :code:`1`.

        offset : int; keyword-only; optional
            Index of the first podcast to return. Use with `limit` to get
            the next batch of podcasts.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the returned podcasts by.

            **Valid values**: :code:`"RANKING"`, :code:`"TRACK"`,
            :code:`"ARTIST"`, :code:`"ALBUM"`, :code:`"RATING"`,
            :code:`"DURATION"`.

        descending : bool; keyword-only; default: :code:`False`
            Whether to sort in descending order. Only applicable when
            `sort_by` is not :code:`"RANKING"`.

        Returns
        -------
        podcasts : dict[str, Any]
            Page of Deezer content metadata for the matching podcasts.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
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
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        return self._search_resource(
            "podcast",
            query,
            strict=strict,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @TTLCache.cached_method(ttl="search")
    def search_radios(
        self,
        query: str,
        /,
        *,
        strict: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool = False,
    ) -> dict[str, Any]:
        """
        `Search > Radio <https://developers.deezer.com/api/search
        /radio>`_: Get Deezer catalog information for radios that
        match a keyword string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        strict : bool; keyword-only; optional
            Whether to disable fuzzy search and use strict matching.

            **API default**: :code:`False`.

        limit : int; keyword-only; optional
            Maximum number of radios to return.

            **Minimum value**: :code:`1`.

        offset : int; keyword-only; optional
            Index of the first radio to return. Use with `limit` to get
            the next batch of radios.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the returned radios by.

            **Valid values**: :code:`"RANKING"`, :code:`"TRACK"`,
            :code:`"ARTIST"`, :code:`"ALBUM"`, :code:`"RATING"`,
            :code:`"DURATION"`.

        descending : bool; keyword-only; default: :code:`False`
            Whether to sort in descending order. Only applicable when
            `sort_by` is not :code:`"RANKING"`.

        Returns
        -------
        radios : dict[str, Any]
            Page of Deezer content metadata for the matching radios.

            .. admonition:: Sample response
               :class: dropdown

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
        return self._search_resource(
            "radio",
            query,
            strict=strict,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @TTLCache.cached_method(ttl="search")
    def search_tracks(
        self,
        query: str,
        /,
        *,
        strict: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool = False,
    ) -> dict[str, Any]:
        """
        `Search > Track <https://developers.deezer.com/api/search
        /track>`_: Get Deezer catalog information for tracks that match
        a keyword string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        strict : bool; keyword-only; optional
            Whether to disable fuzzy search and use strict matching.

            **API default**: :code:`False`.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to get
            the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the returned tracks by.

            **Valid values**: :code:`"RANKING"`, :code:`"TRACK"`,
            :code:`"ARTIST"`, :code:`"ALBUM"`, :code:`"RATING"`,
            :code:`"DURATION"`.

        descending : bool; keyword-only; default: :code:`False`
            Whether to sort in descending order. Only applicable when
            `sort_by` is not :code:`"RANKING"`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of Deezer content metadata for the matching tracks.

            .. admonition:: Sample response
               :class: dropdown

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
                        "explicit_lyrics": <bool>,
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
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        return self._search_resource(
            "track",
            query,
            strict=strict,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @TTLCache.cached_method(ttl="search")
    def search_users(
        self,
        query: str,
        /,
        *,
        strict: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool = False,
    ) -> dict[str, Any]:
        """
        `Search > User <https://developers.deezer.com/api/search
        /user>`_: Get Deezer catalog information for users that match
        a keyword string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        strict : bool; keyword-only; optional
            Whether to disable fuzzy search and use strict matching.

            **API default**: :code:`False`.

        limit : int; keyword-only; optional
            Maximum number of users to return.

            **Minimum value**: :code:`1`.

            **API default**: :code:`25`.

        offset : int; keyword-only; optional
            Index of the first user to return. Use with `limit` to get
            the next batch of users.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the returned users by.

            **Valid values**: :code:`"RANKING"`, :code:`"TRACK"`,
            :code:`"ARTIST"`, :code:`"ALBUM"`, :code:`"RATING"`,
            :code:`"DURATION"`.

        descending : bool; keyword-only; default: :code:`False`
            Whether to sort in descending order. Only applicable when
            `sort_by` is not :code:`"RANKING"`.

        Returns
        -------
        users : dict[str, Any]
            Page of Deezer content metadata for the matching users.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [
                      {
                        "id": <int>,
                        "name": <str>,
                        "picture": <str>,
                        "picture_big": <str>,
                        "picture_medium": <str>,
                        "picture_small": <str>,
                        "picture_xl": <str>,
                        "tracklist": <str>,
                        "type": "user"
                      }
                    ],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        return self._search_resource(
            "user",
            query,
            strict=strict,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )

    @TTLCache.cached_method(ttl="user")
    def get_search_history(
        self,
        query: str | None = None,
        /,
        *,
        strict: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_by: str | None = None,
        descending: bool = False,
    ) -> dict[str, Any]:
        """
        `Search > History <https://developers.deezer.com/api/search
        /history>`_: Get the current user's search history.

        .. admonition:: User authentication
           :class: authorization-scope

           .. tab:: Required

              User authentication
                 Access the :code:`GET /search/history` endpoint.

        Parameters
        ----------
        query : str; positional-only; optional
            Search query.

        strict : bool; keyword-only; optional
            Whether to disable fuzzy search and use strict matching.

            **API default**: :code:`False`.

        limit : int; keyword-only; optional
            Maximum number of searches to return.

            **Minimum value**: :code:`1`.

        offset : int; keyword-only; optional
            Index of the first search to return. Use with `limit` to get
            the next batch of searches.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        sort_by : str; keyword-only; optional
            Field to sort the returned searches by.

            **Valid values**: :code:`"RANKING"`, :code:`"TRACK"`,
            :code:`"ARTIST"`, :code:`"ALBUM"`, :code:`"RATING"`,
            :code:`"DURATION"`.

        descending : bool; keyword-only; default: :code:`False`
            Whether to sort in descending order. Only applicable when
            `sort_by` is not :code:`"RANKING"`.

        Returns
        -------
        searches : dict[str, Any]
            Current user's search history.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "count": <int>,
                    "data": [],
                    "next": <str>,
                    "prev": <str>,
                    "total": <int>
                  }
        """
        self._client._require_authentication("search.get_search_history")
        return self._search_resource(
            "history",
            query,
            strict=strict,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            descending=descending,
        )
