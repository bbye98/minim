from collections.abc import Collection
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class UsersAPI(ResourceAPI):
    """ """

    def get_my_profile(self) -> dict[str, Any]:
        """ """
        return self._client._request(
            "GET", "https://login.tidal.com/oauth2/me"
        ).json()
