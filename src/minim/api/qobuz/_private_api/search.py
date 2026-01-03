from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .._core import PrivateQobuzAPI


class PrivateSearchEndpoints(ResourceAPI):
    """
    Search-related endpoints for the private Qobuz API.

    .. note::

       This class groups search-related endpoints for convenience.
       Qobuz does not provide a dedicated Search API.

    .. important::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    _client: "PrivateQobuzAPI"

    @TTLCache.cached_method(ttl="search")
    def search_tracks(
        self,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for tracks that match a keyword
        string.

        Parameters
        ----------
        query : str; positional-only
            Search query.

        limit : int; keyword-only; optional
            Maximum number of tracks to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first track to return. Use with `limit` to
            get the next batch of tracks.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        tracks : dict[str, Any]
            Page of Qobuz catalog information for the matching tracks.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "query": <str>,
                    "tracks": {
                      "items": [
                        {
                          "album": {
                            "artist": {
                              "albums_count": <int>,
                              "id": <int>,
                              "image": None,
                              "name": <str>,
                              "picture": None,
                              "slug": <str>
                            },
                            "displayable": <bool>,
                            "downloadable": <bool>,
                            "duration": <int>,
                            "genre": {
                              "color": <int>,
                              "id": <int>,
                              "name": <int>,
                              "path": <list[int]>,
                              "slug": <str>
                            },
                            "hires": <bool>,
                            "hires_streamable": <bool>,
                            "id": <str>,
                            "image": {
                              "large": <str>,
                              "small": <str>,
                              "thumbnail": <str>
                            },
                            "label": {
                              "albums_count": <int>,
                              "id": <int>,
                              "name": <str>,
                              "slug": <str>,
                              "supplier_id": <int>
                            },
                            "maximum_bit_depth": <int>,
                            "maximum_channel_count": <int>,
                            "maximum_sampling_rate": <int>,
                            "maximum_technical_specifications": <str>,
                            "media_count": <int>,
                            "parental_warning": <bool>,
                            "previewable": <bool>,
                            "purchasable": <bool>,
                            "purchasable_at": <int>,
                            "qobuz_id": <int>,
                            "release_date_download": <str>,
                            "release_date_original": <str>,
                            "release_date_purchase": <str>,
                            "release_date_stream": <str>,
                            "released_at": <int>,
                            "sampleable": <bool>,
                            "streamable": <bool>,
                            "streamable_at": <int>,
                            "title": <str>,
                            "tracks_count": <int>,
                            "upc": <str>,
                            "version": <str>
                          },
                          "audio_info": {
                            "replaygain_track_gain": <float>,
                            "replaygain_track_peak": <float>
                          },
                          "copyright": <str>,
                          "displayable": <bool>,
                          "downloadable": <bool>,
                          "duration": <int>,
                          "hires": <bool>,
                          "hires_streamable": <bool>,
                          "id": <int>,
                          "isrc": <str>,
                          "maximum_bit_depth": <int>,
                          "maximum_channel_count": <int>,
                          "maximum_sampling_rate": <float>,
                          "maximum_technical_specifications": <str>,
                          "media_number": <int>,
                          "parental_warning": <bool>,
                          "performer": {
                            "id": <int>,
                            "name": <str>
                          },
                          "performers": <str>,
                          "previewable": <bool>,
                          "purchasable": <bool>,
                          "purchasable_at": <int>,
                          "release_date_download": <str>,
                          "release_date_original": <str>,
                          "release_date_purchase": <str>,
                          "release_date_stream": <str>,
                          "sampleable": <bool>,
                          "streamable": <bool>,
                          "streamable_at": <int>,
                          "title": <str>,
                          "track_number": <int>,
                          "version": <str>,
                          "work": None
                        }
                      ],
                      "limit": <int>,
                      "offset": <int>,
                      "total": <int>
                    }
                  }
        """
        return self._search_resources(
            "track", query, limit=limit, offset=offset
        )

    def _search_resources(
        self,
        resource_type: str,
        query: str,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Qobuz catalog information for albums, artists, playlists,
        or tracks that match a keyword string.

        Parameters
        ----------
        resource_type : str or None; positional-only
            Resource type.

            **Valid values**: :code:`"album"`, :code:`"artist"`,
            :code:`"playlist"`, :code:`"track"`.

        query : str; positional-only
            Search query.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`500`.

            **API default**: :code:`50`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to
            get the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        Returns
        -------
        results : dict[str, Any]
            Search results.
        """
        self._client._validate_type("query", query, str)
        params = {"query": query}
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 500)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"{resource_type}/search", params=params
        ).json()
