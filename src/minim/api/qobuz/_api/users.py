from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import APIClient


class UsersAPI(ResourceAPI):
    """
    Users API endpoints for the private Qobuz API.

    .. important::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    _client: "APIClient"

    def get_my_profile(self):
        """ """
        return self._client._request("GET", "user/get").json()
