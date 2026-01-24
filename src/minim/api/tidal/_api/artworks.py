from typing import Any

from ..._shared import TTLCache
from ._shared import TIDALResourceAPI


class ArtworksAPI(TIDALResourceAPI):
    """
    Artworks API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPIClient`
       and should not be instantiated directly.
    """

    _RELATIONSHIPS = {"owners"}

    @TTLCache.cached_method(ttl="static")
    def get_artworks(
        self,
        artwork_ids: str | list[str],
        /,
        country_code: str | None = None,
        *,
        expand: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """
        `Artworks > Get Single Artwork <https://tidal-music.github.io
        /tidal-api-reference/#/artworks/get_artworks__id_>`_: Get TIDAL
        catalog information for an artwork․
        `Artworks > Get Multiple Artworks <https://tidal-music.github.io
        /tidal-api-reference/#/artworks/get_artworks>`_: Get TIDAL catalog
        information for multiple artworks.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab:: Optional

              User authentication
                 Access information on an item's owners.

        Parameters
        ----------
        artwork_ids : str or list[str]; positional-only
            TIDAL ID(s) of the artwork(s), provided as either a string
            or a list of strings.

            **Examples**: :code:`"2xpmpI1s9DzeAPMlmNh9kM"`,
            :code:`["2xpmpI1s9DzeAPMlmNh9kM", "iWOu0yW0IPH0H5O42lAP"]`.

        country_code : str; keyword-only; optional
            ISO 3166-1 alpha-2 country code.

            **Example**: :code:`"US"`.

        expand : str or list[str]; keyword-only; optional
            Related resources to include metadata for in the response.

            **Valid value**: :code:`"owners"`.

            **Examples**: :code:`"owners"`, :code:`["owners"]`.

        Returns
        -------
        artworks : dict[str, Any]
            TIDAL content metadata for the artworks.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Single artwork

                  .. code::

                     {
                       "data": {
                         "attributes": {
                           "files": [
                             {
                               "href": <str>,
                               "meta": {
                                 "height": <int>,
                                 "width": <int>
                               }
                             }
                           ],
                           "mediaType": "IMAGE"
                         },
                         "id": <str>,
                         "relationships": {
                           "owners": {
                             "data": [],
                             "links": {
                               "self": <str>
                             }
                           }
                         },
                         "type": "artworks"
                       },
                       "included": [],
                       "links": {
                         "self": <str>
                       }
                     }

               .. tab:: Multiple artworks

                  .. code::

                     {
                       "data": [
                         {
                           "attributes": {
                             "files": [
                               {
                                 "href": <str>,
                                 "meta": {
                                   "height": <int>,
                                   "width": <int>
                                 }
                               }
                             ],
                             "mediaType": "IMAGE"
                           },
                           "id": <str>,
                           "relationships": {
                             "owners": {
                               "data": [],
                               "links": {
                                 "self": <str>
                               }
                             }
                           },
                           "type": "artworks"
                         }
                       ],
                       "included": [],
                       "links": {
                         "self": <str>
                       }
                     }
        """
        return self._get_resources(
            "artworks", artwork_ids, country_code=country_code, expand=expand
        )

    @TTLCache.cached_method(ttl="static")
    def get_artwork_owners(
        self,
        artwork_id: str,
        /,
        *,
        include_metadata: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Artworks > Get Artwork's Owners <https://tidal-music.github.io
        /tidal-api-reference/#/artworks
        /get_artworks__id__relationships_owners>`_: Get TIDAL catalog
        information for an artwork's owners.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab:: Optional

              User authentication
                 Access information on an item's owners.

        Parameters
        ----------
        artwork_id : str; positional-only
            TIDAL ID of the artwork.

            **Example**: :code:`"2xpmpI1s9DzeAPMlmNh9kM"`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for the artwork's
            owners.

        cursor : str; keyword-only; optional
            Cursor for fetching the next page of results.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        owners : dict[str, Any]
            TIDAL content metadata for the artwork's owners.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": [],
                    "included": [],
                    "links": {
                      "self": <str>
                    }
                  }
        """
        return self._get_resource_relationship(
            "artworks",
            artwork_id,
            "owners",
            country_code=None,
            include_metadata=include_metadata,
            cursor=cursor,
        )
