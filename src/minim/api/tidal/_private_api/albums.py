from collections.abc import Collection
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class AlbumsAPI(ResourceAPI):
    """
    Albums API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _client: "PrivateTIDALAPI"

    def get_album(
        self, album_id: int | str, country_code: str | None = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a single album.

        Parameters
        ----------
        album_id : int or str, positional-only
            TIDAL ID of the album.

            **Examples**: :code:`46369321` or :code:`"46369321"`.

        country_code : str, keyword-only, optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        album : dict[str, Any]
            TIDAL content metadata for the album.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  TODO
        """
        if country_code is None:
            country_code = self._client._my_country_code
        return self._client._request(
            "GET",
            f"v1/albums/{album_id}",
            params={"countryCode": country_code},
        ).json()
