from collections.abc import Collection
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache
from ._shared import TIDALResourceAPI

if TYPE_CHECKING:
    from .. import TIDALAPI

if TYPE_CHECKING:
    from .. import TIDALAPI


class TracksAPI(TIDALResourceAPI):
    """
    Tracks API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _RESOURCES = {
        "albums",
        "artists",
        "genres",
        "lyrics",
        "owners",
        "providers",
        "radio",
        "shares",
        "similarTracks",
        "sourceFile",
        "trackStatistics",
    }
    _client: "TIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_tracks(
        self,
        track_ids: int | str | Collection[int | str] | None = None,
        /,
        *,
        isrcs: str | Collection[str] | None = None,
        owner_ids: int | str | Collection[int | str] | None = None,
        country_code: str | None = None,
        include: str | Collection[str] | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Tracks > Get Single Track <https://tidal-music.github.io
        /tidal-api-reference/#/tracks/get_tracks__id_>`_: Get TIDAL
        catalog information for a single track․
        `Tracks > Get Multiple Tracks <https://tidal-music.github.io
        /tidal-api-reference/#/tracks/get_tracks>`_: Get TIDAL catalog
        information for multiple tracks.

        .. admonition:: User authentication
           :class: authorization-scope dropdown

           .. tab:: Optional

              User authentication
                 Access information on an item's owners.

        Parameters
        ----------
        track_ids : int, str, or Collection[int | str], \
        positional-only, optional
            TIDAL IDs of the tracks, provided as either an integer, a
            string, or a collection of integers and/or strings.

            .. note::

               Exactly one of `track_ids`, `isrcs`, or `owner_ids` must
               be provided.

            **Examples**: 
            
            .. container::

               * :code:`46369325`
               * :code:`"75413016"`
               * :code:`[46369325, "75413016"]`

        isrcs : str, or Collection[str], keyword-only, optional
            International Standard Recording Codes (ISRCs) of the 
            tracks, provided as either a string or a collection of 
            strings.

            .. note::

               Exactly one of `track_ids`, `isrcs`, or `owner_ids` must
               be provided. When this parameter is specified, the 
               request will always be sent to the endpoint for multiple
               tracks.
               
            **Examples**: :code:`"QMJMT1701237"`,
            :code:`[QMJMT1701237, "USAT21404265"]`.

        owner_ids : int, str, or Collection[int | str], keyword-only, \
        optional
            TIDAL IDs of the tracks' owners, provided either as an 
            integer, a string, or a collection of integers and/or 
            strings.

            .. note::

               Exactly one of `track_ids`, `isrcs`, or `owner_ids` must
               be provided. When this parameter is specified, the 
               request will always be sent to the endpoint for multiple
               albums.

            **Examples**: :code:`123456`, :code:`"123456"`, 
            :code:`["123456"]`.

        country_code : str, keyword-only, optional
            ISO 3166-1 alpha-2 country code. Only optional when the 
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : str or Collection[str], keyword-only, optional
            Related resources to include in the response.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"genres"`, :code:`"lyrics"`, :code:`"owners"`, 
            :code:`"providers"`, :code:`"radio"`, :code:`"shares"`,
            :code:`"similarTracks"`, :code:`"sourceFile"`,
            :code:`"trackStatistics"`.

        cursor : str, keyword-only, optional
            Cursor for pagination when requesting multiple tracks.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        tracks : dict[str, Any]
            TIDAL content metadata for the tracks.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single track

                  .. code::

                     TODO

               .. tab:: Multiple tracks

                  .. code::

                     TODO
        """
        params = {}
        if country_code is not None:
            self._client._validate_country_code(country_code)
        if include is not None:
            params["include"] = self._prepare_include(include)
        if sum(arg is not None for arg in (track_ids, isrcs, owner_ids)) != 1:
            raise ValueError(
                "Exactly one of `track_ids`, `isrcs`, or "
                "`owner_ids` must be provided."
            )
        if track_ids is not None:
            self._client._validate_tidal_ids(track_ids)
            if isinstance(track_ids, int | str):
                return self._client._request(
                    "GET", f"tracks/{track_ids}", params=params
                ).json()
            params["filter[id]"] = track_ids
        elif isrcs is not None:
            if isinstance(isrcs, str):
                self._client._validate_isrc(isrcs)
            else:
                for isrc in isrcs:
                    self._client._validate_isrc(isrc)
            params["filter[isrc]"] = isrcs
        else:
            self._client._validate_tidal_ids(owner_ids)
            params["filter[owners.id]"] = owner_ids
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["page[cursor]"] = cursor
        return self._client._request("GET", "tracks", params=params).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_track_albums(
        self,
        track_id: str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """ """
        return self._get_track_resource(
            "albums", track_id, country_code, include=include, cursor=cursor
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_track_artists(
        self,
        track_id: str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """ """
        return self._get_track_resource(
            "artists", track_id, country_code, include=include, cursor=cursor
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_track_owners(
        self,
        track_id: str,
        /,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """ """
        return self._get_track_resource(
            "artists", track_id, False, include=include, cursor=cursor
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_track_providers(
        self,
        track_id: str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """ """
        return self._get_track_resource(
            "providers", track_id, country_code, include=include, cursor=cursor
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_track_radio(
        self,
        track_id: str,
        /,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """ """
        return self._get_track_resource(
            "artists", track_id, False, include=include, cursor=cursor
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_similar_tracks(
        self,
        track_id: str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """ """
        return self._get_track_resource(
            "similarTracks",
            track_id,
            country_code,
            include=include,
            cursor=cursor,
        )

    @TTLCache.cached_method(ttl="catalog")
    def get_track_source_file(
        self,
        track_id: str,
        /,
        *,
        include: bool = False,
    ) -> dict[str, Any]:
        """ """
        return self._get_track_resource(
            "sourceFile", track_id, False, include=include
        )

    def _get_track_resource(
        self,
        resource: str,
        track_id: int | str,
        /,
        country_code: bool | str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a resource related to an
        track.

        Parameters
        ----------
        resource : str, positional-only
            Related resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"genres"`, :code:`"lyrics"`, :code:`"owners"`,
            :code:`"providers"`, :code:`"radio"`, :code:`"shares"`,
            :code:`"similarTracks"`, :code:`"sourceFile"`,
            :code:`"trackStatistics"`.

        track_id : int or str, positional-only
            TIDAL ID of the track.

            **Examples**: :code:`46369325`, :code:`"75413016"`.

        country_code : bool or str, optional
            ISO 3166-1 alpha-2 country code. If :code:`False`, the
            country code is not included in the request.

            **Example**: :code:`"US"`.

        include : bool, keyword-only, default: :code:`False`
            Specifies whether to include TIDAL content metadata for
            the related resource.

        cursor : str, keyword-only, optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        resource : dict[str, Any]
            TIDAL catalog information for the related resource.
        """
        self._client._validate_tidal_ids(track_id, _recursive=False)
        params = {}
        if country_code is not False:
            self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = resource
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["page[cursor]"] = cursor
        return self._client._request(
            "GET",
            f"tracks/{track_id}/relationships/{resource}",
            params=params,
        ).json()
