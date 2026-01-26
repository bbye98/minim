from typing import TYPE_CHECKING, Any

from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from .. import SpotifyWebAPIClient


class SpotifyResourceAPI(ResourceAPI):
    """
    Base class for Spotify Web API resource endpoint groups.
    """

    _AUDIO_TYPES = {"episode", "track"}
    _client: "SpotifyWebAPIClient"

    @staticmethod
    def _prepare_spotify_ids(
        spotify_ids: str | list[str],
        /,
        *,
        limit: int,
        enforce_length: bool = True,
    ) -> tuple[str, int]:
        """
        Normalize, validate, and serialize Spotify IDs.

        Parameters
        ----------
        spotify_ids : str or list[str]; positional-only
            Comma-separated string or list of Spotify IDs.

        limit : int; keyword-only
            Maximum number of Spotify IDs that can be sent in the
            request.

        enforce_length : bool; keyword-only; default: :code:`True`
            Whether to enforce the canonical 22-character Spotify ID
            length.

        Returns
        -------
        spotify_ids : str
            Comma-separated string of Spotify IDs.

        num_ids : int
            Number of Spotify IDs.
        """
        if not spotify_ids:
            raise ValueError("At least one Spotify ID must be specified.")

        if isinstance(spotify_ids, str):
            return SpotifyResourceAPI._prepare_spotify_ids(
                spotify_ids.strip().split(","),
                limit=limit,
                enforce_length=enforce_length,
            )

        num_ids = len(spotify_ids)
        if num_ids > limit:
            raise ValueError(
                f"A maximum of {limit} Spotify IDs can be sent in a request."
            )
        spotify_ids_ = []
        for id_ in spotify_ids:
            id_ = id_.strip()
            SpotifyResourceAPI._validate_spotify_id(
                id_, enforce_length=enforce_length
            )
            spotify_ids_.append(id_)
        return ",".join(spotify_ids_), num_ids

    @staticmethod
    def _prepare_spotify_uris(
        spotify_uris: str | list[str],
        /,
        *,
        limit: int,
        resource_types: set[str],
    ) -> list[str]:
        """
        Normalize, validate, and prepare Spotify Uniform Resource
        Identifiers (URIs).

        Parameters
        ----------
        spotify_uris : str or list[str]; positional-only
            Comma-separated string or list of Spotify URIs.

        limit : int; keyword-only
            Maximum number of Spotify URIs that can be sent in the
            request.

        resource_types : set[str]
            Allowed Spotify resource types.

        Returns
        -------
        spotify_uris : list[str]
            List of Spotify URIs.
        """
        if not spotify_uris:
            raise ValueError("At least one Spotify URI must be specified.")

        if isinstance(spotify_uris, str):
            return SpotifyResourceAPI._prepare_spotify_uris(
                spotify_uris.strip().split(","),
                limit=limit,
                resource_types=resource_types,
            )

        if len(spotify_uris) > limit:
            raise ValueError(
                f"A maximum of {limit} Spotify URIs can be sent in a request."
            )
        spotify_uris_ = []
        for uri in spotify_uris:
            uri = uri.strip()
            SpotifyResourceAPI._validate_spotify_uri(
                uri, resource_types=resource_types
            )
            spotify_uris_.append(uri)
        return spotify_uris

    @staticmethod
    def _validate_spotify_id(
        spotify_id: str, /, *, enforce_length: bool = True
    ) -> None:
        """
        Validate a Spotify ID.

        Parameters
        ----------
        spotify_id : str; positional-only
            Spotify ID.

        enforce_length : bool; keyword-only; default: :code:`True`
            Whether to enforce the canonical 22-character Spotify ID
            length.
        """
        if (
            not isinstance(spotify_id, str)
            or enforce_length
            and len(spotify_id) != 22
            or not spotify_id.isalnum()
        ):
            raise ValueError(f"{spotify_id!r} is not a valid Spotify ID.")

    @staticmethod
    def _validate_spotify_uri(
        spotify_uri: str, /, *, resource_types: set[str]
    ) -> None:
        """
        Validate a Spotify Uniform Resource Identifier (URI).

        Parameters
        ----------
        spotify_uri : str; positional-only
            Spotify URI.

        resource_types : set[str]
            Allowed Spotify resource types.
        """
        if (
            not isinstance(spotify_uri, str)
            or len(uri_parts := spotify_uri.strip().split(":")) != 3
            or uri_parts[0] != "spotify"
            or uri_parts[1] not in resource_types
            or len(spotify_id := uri_parts[2]) != 22
            or not spotify_id.isalnum()
        ):
            raise ValueError(f"{spotify_uri!r} is not a valid Spotify URI.")

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
        resource_ids, num_ids = self._prepare_spotify_ids(
            resource_ids, limit=limit
        )
        params = {}
        if country_code is not None:
            self._client.markets._validate_market(country_code)
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
            Query parameters to include in the request. If not provided,
            an empty dictionary will be created.

            .. note::

               This `dict` is mutated in-place.

        Returns
        -------
        items : dict[str, Any]
            Page of Spotify content metadata for the items in the
            resource.
        """
        resource_id = resource_id.strip()
        self._validate_spotify_id(resource_id)
        if params is None:
            params = {}
        if country_code is not None:
            self._client.markets._validate_market(country_code)
            params["market"] = country_code
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 50)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET", f"{resource_type}/{resource_id}/{item_type}", params=params
        ).json()
