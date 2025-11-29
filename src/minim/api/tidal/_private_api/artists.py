from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI, _copy_docstring
from .users import UsersAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class ArtistsAPI(ResourceAPI):
    """
    Artists API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _client: "PrivateTIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_artist(
        self, artist_id: int | str, /, country_code: str | None = None
    ) -> dict[str, Any]:
        """ """

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_artists(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        filter: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """ """

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_biography(
        self, artist_id: int | str, /, country_code: str | None = None
    ) -> dict[str, Any]:
        """ """

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_links(
        self, artist_id: int | str, /, country_code: str | None = None
    ) -> dict[str, Any]:
        """ """

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_mix(
        self, artist_id: int | str, /, country_code: str | None = None
    ) -> dict[str, Any]:
        """ """

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_radio(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """ """

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_top_tracks(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """ """

    @TTLCache.cached_method(ttl="catalog")
    def get_artist_videos(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """ """

    @TTLCache.cached_method(ttl="catalog")
    def get_similar_artists(
        self,
        artist_id: int | str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """ """

    # @_copy_docstring(UsersAPI.get_blocked_artists)
    # def get_blocked_artists(
    #     self,
    #     user_id: int | str | None = None,
    #     /,
    #     *,
    #     limit: int | None = None,
    #     offset: int | None = None,
    # ) -> dict[str, Any]:
    #     return self._client.users.get_blocked_artists(
    #         user_id, limit=limit, offset=offset
    #     )

    # @_copy_docstring(UsersAPI.block_artists)
    # def block_artists(
    #     self, artist_id: int | str, /, user_id: int | str | None = None
    # ) -> None:
    #     self._client.users.block_artists(artist_id, user_id)

    # @_copy_docstring(UsersAPI.unblock_artists)
    # def unblock_artists(
    #     self, artist_id: int | str, /, user_id: int | str | None = None
    # ) -> None:
    #     self._client.users.unblock_artists(artist_id, user_id)

    # @_copy_docstring(UsersAPI.favorite_artists)
    # def get_favorite_artists(
    #     self,
    #     user_id: int | str | None = None,
    #     /,
    #     country_code: str | None = None,
    #     *,
    #     limit: int | None = None,
    #     offset: int | None = None,
    #     sort: str | None = None,
    #     reverse: bool | None = None,
    # ) -> dict[str, Any]:
    #     return self._client.users.get_favorite_artists(
    #         user_id,
    #         country_code,
    #         limit=limit,
    #         offset=offset,
    #         sort=sort,
    #         reverse=reverse,
    #     )

    # @_copy_docstring(UsersAPI.favorite_artists)
    # def favorite_artists(
    #     self,
    #     artist_ids: int | str | list[int | str],
    #     /,
    #     user_id: int | str | None = None,
    #     country_code: str | None = None,
    #     *,
    #     missing_ok: bool | None = None,
    # ) -> None:
    #     self._client.users.favorite_artists(
    #         artist_ids,
    #         user_id,
    #         country_code,
    #         missing_ok=missing_ok,
    #     )

    # @_copy_docstring(UsersAPI.unfavorite_artists)
    # def unfavorite_artists(
    #     self,
    #     artist_ids: int | str | list[int | str],
    #     /,
    #     user_id: int | str | None = None,
    # ) -> None:
    #     self._client.users.unfavorite_artists(artist_ids, user_id)
