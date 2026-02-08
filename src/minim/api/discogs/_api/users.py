from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import DiscogsResourceAPI


class UsersAPI(DiscogsResourceAPI):
    """
    Users API endpoints for the private Qobuz API.

    .. important::

       This class is managed by
       :class:`minim.api.discogs.DiscogsAPIClient` and should not be
       instantiated directly.
    """

    @TTLCache.cached_method(ttl="static")
    def get_my_identity(self) -> dict[str, Any]:
        """ """
        self._client._require_authentication("users.get_my_identity")
        return self._client._request(
            "GET", "https://api.discogs.com/oauth/identity"
        ).json()
