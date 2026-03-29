from __future__ import annotations
from typing import TYPE_CHECKING

from ..._shared import _copy_docstring
from ._shared import DiscogsResourceAPI
from .database import DatabaseAPI

if TYPE_CHECKING:
    from typing import Any


class SearchAPI(DiscogsResourceAPI):
    """
    Search-related endpoints for the Discogs API.

    .. note::

       This class groups search-related endpoints for convenience.
       Discogs does not provide a dedicated Search API.

    .. important::

       This class is managed by
       :class:`~minim.api.discogs.DiscogsAPIClient` and should not be
       instantiated directly.
    """

    __slots__ = ()

    @_copy_docstring(DatabaseAPI.search)
    def search(
        self,
        query: str | None = None,
        /,
        *,
        resource_type: str | None = None,
        title: str | None = None,
        release: str | None = None,
        artist: str | None = None,
        artist_variation: str | None = None,
        track: str | None = None,
        credit: str | None = None,
        label: str | None = None,
        genre: str | None = None,
        style: str | None = None,
        release_country: str | None = None,
        release_format: str | None = None,
        release_year: int | str | None = None,
        catalog_number: str | None = None,
        barcode: str | None = None,
        submitter: str | None = None,
        contributor: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        return self._client.database.search(
            query=query,
            resource_type=resource_type,
            title=title,
            release=release,
            artist=artist,
            artist_variation=artist_variation,
            track=track,
            credit=credit,
            label=label,
            genre=genre,
            style=style,
            release_country=release_country,
            release_format=release_format,
            release_year=release_year,
            catalog_number=catalog_number,
            barcode=barcode,
            submitter=submitter,
            contributor=contributor,
            limit=limit,
            page=page,
        )
