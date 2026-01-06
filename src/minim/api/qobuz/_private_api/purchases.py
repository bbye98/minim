from typing import TYPE_CHECKING, Any

from ..._shared import ResourceAPI, _copy_docstring
from .users import PrivateUsersAPI

if TYPE_CHECKING:
    from .._core import PrivateQobuzAPI


class PrivatePurchasesAPI(ResourceAPI):
    """
    Purchases API endpoints for the private Qobuz API.

    .. important::

       This class is managed by :class:`minim.api.qobuz.PrivateQobuzAPI`
       and should not be instantiated directly.
    """

    _client: "PrivateQobuzAPI"

    @_copy_docstring(PrivateUsersAPI.get_my_purchases)
    def get_my_purchases(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        return self._client.users.get_my_purchases(limit=limit, offset=offset)

    @_copy_docstring(PrivateUsersAPI.get_my_purchased_item_ids)
    def get_my_purchased_item_ids(self) -> dict[str, Any]:
        return self._client.users.get_my_purchased_item_ids()
