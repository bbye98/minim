from typing import TYPE_CHECKING, Any

from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from .. import SpotifyWebAPI


class SpotifyResourceAPI(ResourceAPI):
    """
    Abstract base class for Spotify Web API resource endpoint groups.
    """

    _AUDIO_TYPES = {"episode", "track"}
    _client: "SpotifyWebAPI"

    @classmethod
    def _prepare_types(
        cls,
        types: str | list[str],
        /,
        *,
        allowed_types: set[str],
        type_prefix: str = "resource",
    ) -> str:
        """
        Normalize, validate, and serialize types.

        Parameters
        ----------
        types : str or list[str]; positional-only
            Types.

        allowed_types : set[str]; keyword-only
            Allowed types.

        type_prefix : str; keyword-only
            Prefix of the type.

        Returns
        -------
        types : str
            Comma-separated string of types.
        """
        if isinstance(types, str):
            return cls._prepare_types(
                types.strip().split(","),
                allowed_types=allowed_types,
                type_prefix=type_prefix,
            )

        types_ = set()
        for type_ in set(types):
            type_ = type_.strip().lower()
            if type_ not in allowed_types:
                allowed_types_str = "', '".join(sorted(allowed_types))
                raise ValueError(
                    f"Invalid {type_prefix} type {type_!r}. "
                    f"Valid values: '{allowed_types_str}'."
                )
            types_.add(type_)
        return ",".join(sorted(types_))

    def _get_resources(
        self,
        resource_type: str,
        resource_ids: str | list[str],
        /,
        *,
        country_code: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Get Spotify catalog information for one or more items of a
        resource type.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"audio-features"`, :code:`"audiobooks"`,
            :code:`"chapters"`, :code:`"episodes"`, :code:`"shows"`,
            :code:`"tracks"`.

        resource_ids : str or list[str]; positional-only
            Spotify IDs of the resources.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If provided, only content
            available in that market is returned. When a user access
            token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither a country code is provided nor a country can
               be determined from the user account, the content is
               considered unavailable for the client.

        limit : int; keyword-only; default: :code:`50`
            Maximum number of Spotify IDs that can be sent in the
            request.

        Returns
        -------
        resources : dict[str, Any]
            Spotify content metadata for the resources.
        """
        is_string = isinstance(resource_ids, str)
        resource_ids, num_ids = self._client._prepare_spotify_ids(
            resource_ids, limit=limit
        )
        params = {}
        if country_code is not None:
            self._client._validate_market(country_code)
            params["market"] = country_code
        if is_string and num_ids == 1:
            return self._client._request(
                "GET", f"{resource_type}/{resource_ids}", params=params
            ).json()
        params["ids"] = resource_ids
        return self._client._request(
            "GET", resource_type, params=params
        ).json()

    def _get_resource_items(
        self,
        resource_type: str,
        resource_id: str,
        item_type: str,
        /,
        *,
        country_code: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get Spotify catalog information for items belonging to a
        resource.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"audiobooks"`, :code:`"playlists"`, :code:`"shows"`.

        resource_id : str; positional-only
            Spotify ID of the resource.

        item_type : str; positional-only
            Item type belonging to the given resource type.

            **Valid values**:

            .. container::

               * :code:`"albums"` for artists.
               * :code:`"chapters"` for audiobooks.
               * :code:`"episodes"` for shows.
               * :code:`"tracks"` for albums and playlists.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code. If provided, only content
            available in that market is returned. When a user access
            token accompanies the request, the country associated
            with the user account takes priority over this parameter.

            .. note::

               If neither a country code is provided nor a country can
               be determined from the user account, the content is
               considered unavailable for the client.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`50`.

            **API default**: :code:`20`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        params : dict[str, Any]; keyword-only; optional
            Dictionary of additional query parameters to include in the
            request. If not provided, a new dictionary will be created.

            .. note::

               This `dict` is updated in-place.

        Returns
        -------
        items : dict[str, Any]
            Page of Spotify content metadata for the items in the
            resource.
        """
        self._client._validate_spotify_id(resource_id)
        if params is None:
            params = {}
        if country_code is not None:
            self._client._validate_market(country_code)
            params["market"] = country_code
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"{resource_type}/{resource_id}/{item_type}", params=params
        ).json()
