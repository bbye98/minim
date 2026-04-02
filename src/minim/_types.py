from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar


T = TypeVar("T")

if TYPE_CHECKING:
    from typing import TypeAlias

    OrderedCollection: TypeAlias = list[T] | tuple[T, ...]
    Collection: TypeAlias = OrderedCollection | set[T]

ORDERED_COLLECTION_TYPES = list, tuple
COLLECTION_TYPES = list, tuple, set
