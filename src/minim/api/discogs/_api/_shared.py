from typing import TYPE_CHECKING

from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from .. import DiscogsAPIClient


class DiscogsResourceAPI(ResourceAPI):
    """
    Base class for Discogs API resource endpoint groups.
    """

    _RELATIONSHIPS: set[str]
    _client: "DiscogsAPIClient"
