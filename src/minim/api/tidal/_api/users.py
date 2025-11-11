from collections.abc import Collection
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import TIDALAPI


class UsersAPI(ResourceAPI):
    """
    User Collections, User Entitlements, User Recommendations, and Users
    API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.TIDALAPI`
       and should not be instantiated directly.
    """

    _client: "TIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_my_profile(self) -> dict[str, Any]:
        """
        `Users > Get Current User's Profile
        <https://tidal-music.github.io/tidal-api-reference/#/users
        /get_users_me>`_: Get the current user's account information.

        .. admonition:: Authorization scope
           :class: authorization-scope

           .. tab:: Required

              :code:`user.read` scope
                 Read access to a user's account information, such as
                 country and email address.

        Returns
        -------
        profile : dict[str, Any]
            Current user's account information.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "data": {
                      "attributes": {
                        "country": <str>,
                        "email": <str>,
                        "emailVerified": <bool>,
                        "firstName": <str>,
                        "username": <str>
                      },
                      "id": <str>,
                      "type": "users",
                    },
                    "links": {
                      "self": "/users/me"
                    }
                  }
        """
        return self._client._request("GET", "users/me").json()
