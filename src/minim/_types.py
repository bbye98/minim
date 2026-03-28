from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar


T = TypeVar("T")

if TYPE_CHECKING:
    from typing import TypeAlias

    Collection: TypeAlias = list[T] | tuple[T, ...] | set[T]

COLLECTION_TYPES = list, tuple, set
