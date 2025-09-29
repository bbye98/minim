from collections.abc import Collection
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class WebAPISearchEndpoints:
    """
    Spotify Web API search endpoints.

    .. note::

       This class is managed by :class:`minim.api.spotify.WebAPI` and
       should not be instantiated directly.
    """

    _TYPES = {
        "album",
        "artist",
        "playlist",
        "track",
        "show",
        "episode",
        "audiobook",
    }

    def __init__(self, client: "WebAPI", /) -> None:
        """
        Parameters
        ----------
        client : minim.api.spotify.WebAPI
            Minim's Spotify Web API client.
        """
        self._client = client

    def search(
        self,
        query: str,
        /,
        types: str | Collection[str],
        *,
        include_external: str | None = None,
        market: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        `Search > Search for Item <https://developer.spotify.com
        /documentation/web-api/reference/search>`_: Get Spotify catalog
        information about albums, artists, playlists, tracks, shows,
        episodes, or audiobooks that match a keyword string.

        .. important::

           Audiobooks are only available in the US, UK, Canada, Ireland,
           New Zealand, and Australia markets.

        Parameters
        ----------
        query : str, positional-only
            Search query.

            .. tip::

               Searches can be narrowed using field filters. The
               available filters are :code:`album`, :code:`artist`,
               :code:`track`, :code:`year`, :code:`upc`,
               :code:`tag:hipster`, :code:`tag:new`, :code:`isrc`, and
               :code:`genre`. Each filter applies only to certain result
               types:

               * :code:`artist` and :code:`year` can be used when
                 searching albums, artists and tracks. The :code:`year`
                 filter accepts a single year or a range (e.g.,
                 1955-1960).

               * :code:`album` can be used when searching albums and
                 tracks.

               * :code:`genre` can be used when searching artists and
                 tracks.

               * :code:`isrc` and :code:`track` can be used when
                 searching tracks.

               * :code:`upc`, :code:`tag:new`, and :code:`tag:hipster`
                 can only be used while searching albums. The
                 :code:`tag:new` filter returns albums released in the
                 past two weeks, and the :code:`tag:hipster` filter
                 returns albums in the lowest 10% popularity.

            **Example**:
            :code:`"remaster track:Doxy artist:Miles Davis"`.

        types : str or Collection[str]
            (Comma-separated) list of item types to search across.

            **Valid values**: :code:`"album"`, :code:`"artist"`,
            :code:`"playlist"`, :code:`"track"`, :code:`"show"`,
            :code:`"episode"`, :code:`"audiobook"`.

        include_external : str, optional
            Externally hosted content that the API client can play.

            **Valid value**: :code:`"audio"`.

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
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`50`.

            **Default**: :code:`20`.

        offset : int, keyword-only, optional
            Index of the first item to return. Use with `limit` to get
            the next set of items.

            **Valid range**: :code:`0` to :code:`1_000`.

            **Minimum value**: :code:`0`.

            **Default**: :code:`0`.
        """
        if not query:
            raise ValueError("No search query provided.")

        params = {"q": query, "type": self._prepare_types(types)}
        if include_external:
            if include_external != "audio":
                raise ValueError("")
            params["include_external"] = include_external
        if market is not None:
            self._client._validate_market(market)
            params["market"] = market
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0, 1_000)
            params["offset"] = offset
        return self._client._request("GET", "search", params=params).json()

    def _prepare_types(self, types: str | Collection[str], /) -> str:
        """
        Stringify a list of Spotify item types into a comma-delimited
        string.

        Parameters
        ----------
        types : str, positional-only
            Spotify item types.

        Returns
        -------
        types : str
            Comma-delimited string containing Spotify item types.
        """
        if isinstance(types, str):
            split_types = types.split(",")
            for type_ in split_types:
                self._validate_type(type_)
            return ",".join(sorted(split_types))

        types = set(types)
        for type_ in types:
            self._validate_type(type_)
        return ",".join(sorted(types))

    def _validate_type(self, type_: str, /) -> None:
        """
        Validate Spotify item type.

        Parameters
        ----------
        type_ : str, positional-only
            Spotify item type.
        """
        if type_ not in self._TYPES:
            raise ValueError(
                f"{type_!r} is not a valid Spotify item type. "
                "Valid values: '" + ", ".join(self._TYPES) + "'."
            )
