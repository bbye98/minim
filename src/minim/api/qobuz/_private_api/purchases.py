from __future__ import annotations
from typing import TYPE_CHECKING

from ..._shared import _copy_docstring
from ._shared import PrivateQobuzResourceAPI
from .users import PrivateUsersAPI

if TYPE_CHECKING:
    from typing import Any


class PrivatePurchasesAPI(PrivateQobuzResourceAPI):
    """
    Purchases API endpoints for the private Qobuz API.

    .. important::

       This class is managed by
       :class:`~minim.api.qobuz.PrivateQobuzAPIClient` and should not be
       instantiated directly.
    """

    @_copy_docstring(PrivateUsersAPI.get_my_purchases)
    def get_my_purchases(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        return self._client.users.get_my_purchases(limit=limit, offset=offset)

    @_copy_docstring(PrivateUsersAPI.get_my_purchased_item_ids)
    def get_my_purchased_item_ids(self) -> dict[str, Any]:
        return self._client.users.get_my_purchased_item_ids()
