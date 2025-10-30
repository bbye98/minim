from collections.abc import Collection, Sequence
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

    _RESOURCES = {
        "artists",
        "coverArt",
        "genres",
        "items",
        "owners",
        "providers",
        "similarAlbums",
        "genres",
    }
    _client: "TIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_albums(
        self,
        *,
        album_ids: int | str | Collection[int | str] | None = None,
        barcodes: int | str | Collection[int | str] | None = None,
        # owner_ids: int | str | Collection[int | str] | None = None,
        country_code: str | None = None,
        include: str | Sequence[str] | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """ """
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

    # def get_album_owners(
    #     self,
    #     album_id: int | str,
    #     /,
    #     *,
    #     include: bool = False,
    #     cursor: str | None = None,
    # ) -> dict[str, Any]:
    #    ...

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
