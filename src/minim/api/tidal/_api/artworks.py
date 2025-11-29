from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache
from ._shared import TIDALResourceAPI

if TYPE_CHECKING:
    from .. import TIDALAPI


class ArtworksAPI(TIDALResourceAPI):
    """
    Artworks API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _RESOURCES = {"owners"}
    _client: "TIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_artworks(
        self,
        artwork_ids: str | list[str],
        /,
        country_code: str | None = None,
        *,
        include: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """
        `Artworks > Get Single Artwork <https://tidal-music.github.io
        /tidal-api-reference/#/artworks/get_artworks__id_>`_: Get TIDAL
        catalog information for a single artwork․
        `Artworks > Get Multiple Artworks <https://tidal-music.github.io
        /tidal-api-reference/#/artworks/get_artworks>`_: Get TIDAL catalog
        information for multiple artworks.

        .. admonition:: User authentication
           :class: authorization-scope dropdown

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
            ISO 3166-1 alpha-2 country code. Only optional when the
            country code can be retrieved from the user's profile.

            **Example**: :code:`"US"`.

        include : str or list[str]; keyword-only; optional
            Related resources to include in the response.

            **Valid value**: :code:`"owners"`.

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
        params = {}
        self._client._resolve_country_code(country_code, params)
        if include is not None:
            params["include"] = self._prepare_include(include)
        if isinstance(artwork_ids, str):
            return self._client._request(
                "GET", f"artworks/{artwork_ids}", params=params
            ).json()
        for artwork_id in artwork_ids:
            if not isinstance(artwork_id, str):
                raise ValueError("Artwork IDs must be strings.")
        params["filter[id]"] = artwork_ids
        return self._client._request("GET", "artworks", params=params).json()

    @TTLCache.cached_method(ttl="catalog")
    def get_artwork_owners(
        self,
        artwork_id: str,
        /,
        *,
        include: bool = False,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        `Artworks > Get Artwork's Owners <https://tidal-music.github.io
        /tidal-api-reference/#/artworks
        /get_artworks__id__relationships_owners>`_: Get TIDAL catalog
        information for an artwork's owners.

        .. admonition:: User authentication
           :class: authorization-scope dropdown

           .. tab:: Optional

              User authentication
                 Access information on an item's owners.

        Parameters
        ----------
        artwork_id : str; positional-only
            TIDAL ID of the artwork.

            **Example**: :code:`"2xpmpI1s9DzeAPMlmNh9kM"`.

        include : bool; keyword-only; default: :code:`False`
            Whether to include TIDAL content metadata for
            the artwork's owners.

        cursor : str; keyword-only; optional
            Cursor for pagination.

            **Example**: :code:`"3nI1Esi"`.

        Returns
        -------
        owners : dict[str, Any]
            TIDAL catalog information for the artwork's owners.

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
        params = {}
        if include is not None:
            params["include"] = "owners"
        if cursor is not None:
            self._client._validate_type("cursor", cursor, str)
            params["page[cursor]"] = cursor
        return self._client._request(
            "GET", f"artworks/{artwork_id}/relationships/owners", params=params
        ).json()
