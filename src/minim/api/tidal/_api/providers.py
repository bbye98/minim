from typing import Any

from ..._shared import TTLCache
from ._shared import TIDALResourceAPI


class ProvidersAPI(TIDALResourceAPI):
    """
    Providers API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="static")
    def get_providers(
        self, provider_ids: int | str | list[int | str], /
    ) -> dict[str, Any]:
        """
        `Providers > Get Single Provider <https://tidal-music.github.io
        /tidal-api-reference/#/providers/get_providers__id_>`_: Get
        TIDAL catalog information for a provider․
        `Providers > Get Multiple Providers
        <https://tidal-music.github.io/tidal-api-reference/#/providers
        /get_providers>`_: Get TIDAL catalog information for multiple
        providers.

        Parameters
        ----------
        provider_ids : int, str, or list[int | str]; positional-only
            TIDAL IDs of the providers.

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
        return self._get_resources(
            "providers", provider_ids, country_code=None
        )
