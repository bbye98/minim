from collections.abc import Collection
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache
from ._shared import TIDALResourceAPI

if TYPE_CHECKING:
    from .. import TIDALAPI


class ProvidersAPI(TIDALResourceAPI):
    """
    Providers API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _client: "TIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_providers(
        self, provider_ids: int | str | Collection[int | str], /
    ) -> dict[str, Any]:
        """
        `Providers > Get Single Provider <https://tidal-music.github.io
        /tidal-api-reference/#/providers/get_providers__id_>`_: Get
        TIDAL catalog information for a single provider․
        `Providers > Get Multiple Providers
        <https://tidal-music.github.io/tidal-api-reference/#/providers
        /get_providers>`_: Get TIDAL catalog information for multiple
        providers.

        Parameters
        ----------
        provider_ids : int, str, or Collection[int | str], \
        positional-only
            TIDAL IDs of the providers, provided as either an integer, a
            string, or a collection of integers and/or strings.

            **Examples**: :code:`771`, :code:`"772"`, 
            :code:`[771, "772"]`.

        Returns
        -------
        providers : dict[str, Any]
            TIDAL content metadata for the providers.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single provider

                  .. code::

                     {
                       "data": {
                         "attributes": {
                           "name": <str>
                         },
                         "id": <str>,
                         "type": "providers"
                       },
                       "links": {
                         "self": <str>
                       }
                     }

               .. tab:: Multiple providers

                  .. code::

                     {
                       "data": [
                         {
                           "attributes": {
                             "name": <str>
                           },
                           "id": <str>,
                           "type": "providers"
                         }
                       ],
                       "links": {
                         "self": <str>
                       }
                     }
        """
        self._client._validate_tidal_ids(provider_ids)
        if isinstance(provider_ids, int | str):
            return self._client._request(
                "GET", f"providers/{provider_ids}"
            ).json()
        return self._client._request(
            "GET", "providers", params={"filter[id]": provider_ids}
        ).json()
