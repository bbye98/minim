"""
API clients for Discogs services, such as the Discogs API.
"""

from ._core import DiscogsAPIClient
from ._api.database import DatabaseAPI
from ._api.inventory import InventoryAPI
from ._api.marketplace import MarketplaceAPI
from ._api.search import SearchAPI
from ._api.users import UsersAPI

__all__ = [
    "DiscogsAPIClient",
    "DatabaseAPI",
    "InventoryAPI",
    "MarketplaceAPI",
    "SearchAPI",
    "UsersAPI",
]
