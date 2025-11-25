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
            "GET", f"{self._client.LOGIN_URL}/oauth2/me"
        ).json()
