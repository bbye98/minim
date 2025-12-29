from typing import TYPE_CHECKING, Any

from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class PrivateTIDALResourceAPI(ResourceAPI):
    """
    Abstract base class for private TIDAL API resource endpoint groups.
    """

    _ASSET_PRESENTATIONS = {"FULL", "PREVIEW"}
    _PLAYBACK_MODES = {"STREAM", "OFFLINE"}
    _client: "PrivateTIDALAPI"

    def _get_resource(
        self,
        resource_type: str,
        resource_id: str,
        /,
        country_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Spotify catalog information for a resource.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"audio-features"`, :code:`"audiobooks"`,
            :code:`"chapters"`, :code:`"episodes"`, :code:`"shows"`,
            :code:`"tracks"`.

        resource_id : str; positional-only
            Spotify ID of the resource.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

            .. note::

               If neither a country code is provided nor a country can
               be determined from the user account, the content is
               considered unavailable for the client.

        Returns
        -------
        resource : dict[str, Any]
            TIDAL content metadata for the resource.
        """
        if country_code is None:
            country_code = self._client._my_country_code
        else:
            self._client._validate_country_code(country_code)
        return self._client._request(
            "GET",
            f"v1/{resource_type}/{resource_id}",
            params={"countryCode": country_code},
        ).json()

    def _get_resource_relationship(
        self,
        resource_type: str,
        resource_id: int | str,
        relationship: str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a resource related to a track.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"albums"`, :code:`"artists"`,
            :code:`"tracks"`, :code:`"videos"`.

        resource_id : str; positional-only
            TIDAL ID of the resource.

        relationship : str; positional-only
            Related resource type.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

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
        resource : dict[str, Any]
            TIDAL content metadata for the related resource.
        """
        if params is None:
            params = {}
        self._client._resolve_country_code(country_code, params)
        if limit is not None:
            self._client._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._client._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET",
            f"v1/{resource_type}/{resource_id}/{relationship}",
            params=params,
        ).json()
