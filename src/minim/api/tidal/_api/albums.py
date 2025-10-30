from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import TIDALAPI


class AlbumsAPI(ResourceAPI):
    """
    Albums API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _RESOURCES = {"artists", "coverArt", "items", "providers", "similarAlbums"}
    _client: "TIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_albums(
        self,
        *,
        album_ids: int | str | Sequence[int | str] | None = None,
        barcodes: int | str | Sequence[int | str] | None = None,
        country_code: str | None = None,
        include: str | Sequence[str] | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Albums > Get Single Album <https://tidal-music.github.io
        /tidal-api-reference/#/albums/get_albums__id_>`_: Get TIDAL
        catalog information for a single album by its TIDAL ID․
        `Albums > Get Multiple Albums <https://tidal-music.github.io
        /tidal-api-reference/#/albums/get_albums>`_: Get TIDAL catalog
        information for multiple albums by their TIDAL IDs or barcodes.

        Parameters
        ----------
        album_ids : int, str, or Sequence[int | str], keyword-only, \
        optional
            TIDAL ID(s) of the album(s), provided as either an integer,
            a string, or a sequence of integers and/or strings.

            .. note::

               Exactly one of `album_ids` or `barcodes` must be provided.

            **Examples**: 
            
            .. container::

               * :code:`46369321`
               * :code:`"46369321"`
               * :code:`[46369321, 251380836]`
               * :code:`[46369321, "251380836"]`
               * :code:`["46369321", "251380836"]`

        barcodes : int, str, or Sequence[int | str], keyword-only, \
        optional
            Barcode ID(s) of the album(s), provided as either an integer,
            a string, or a sequence of integers and/or strings.

            .. note::

               Exactly one of `album_ids` or `barcodes` must be provided.

            **Examples**: 
            
            .. container::
            
               * :code:`075678671173`
               * :code:`"075678671173"`
               * :code:`[075678671173, 602448438034]`
               * :code:`[075678671173, "602448438034"]`
               * :code:`["075678671173", "602448438034"]`

        country_code : str, keyword-only, optional
            ISO 3166-1 alpha-2 country code. Only optional when the 
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : str or Sequence[str], keyword-only, optional
            Related resources to include in the response.

            **Valid values**: :code:`"artists"`, :code:`"coverArt"`,
            :code:`"items"`, :code:`"providers"`, 
            :code:`"similarAlbums"`.

        cursor : str, keyword-only, optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        albums : dict[str, Any]
            TIDAL content metadata for the albums. 

            .. admonition:: Sample response
               :class: dropdown

               .. tab:: Single album

                  .. code::

                     TODO

               .. tab:: Multiple albums

                  .. code::

                     TODO
        """
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include is not None:
            if isinstance(include, str):
                include = [include]
            for resource in include:
                if resource not in self._RESOURCES:
                    _resources = "', '".join(sorted(self._RESOURCES))
                    raise ValueError(
                        f"Invalid related resource {resource!r}. "
                        f"Valid values: '{_resources}'."
                    )
            params["include"] = include
        if album_ids is not None:
            if barcodes is not None:
                raise ValueError(
                    "Only one of `album_ids` or `barcodes` can be provided."
                )
            self._client._validate_tidal_ids(album_ids)
            if isinstance(album_ids, int | str):
                return self._client._request(
                    "GET", f"albums/{album_ids}", params=params
                ).json()
            params["filter[id]"] = album_ids
        elif barcodes is not None:
            if isinstance(barcodes, int | str):
                barcodes = [barcodes]
            for barcode in barcodes:
                self._client._validate_barcode(barcode)
            params["filter[barcodeId]"] = barcodes
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request("GET", "albums", params=params).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_album_artists(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """ """
        self._client._validate_tidal_ids(album_id)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = "artists"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET", f"albums/{album_id}/relationships/artists", params=params
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_album_cover_art(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """ """
        self._client._validate_tidal_ids(album_id)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = "coverArt"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET", f"albums/{album_id}/relationships/coverArt", params=params
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_album_items(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """ """
        self._client._validate_tidal_ids(album_id)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = "items"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET", f"albums/{album_id}/relationships/items", params=params
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_album_providers(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """ """
        self._client._validate_tidal_ids(album_id)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = "providers"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET", f"albums/{album_id}/relationships/providers", params=params
        ).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_similar_albums(
        self,
        album_id: int | str,
        /,
        country_code: str | None = None,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """ """
        self._client._validate_tidal_ids(album_id)
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include:
            params["include"] = "similarAlbums"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["cursor"] = cursor
        return self._client._request(
            "GET",
            f"albums/{album_id}/relationships/similarAlbums",
            params=params,
        ).json()
