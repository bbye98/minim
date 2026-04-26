from __future__ import annotations
import mmap
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar


T = TypeVar("T")

if TYPE_CHECKING:
    from typing import TypeAlias

    OrderedCollection: TypeAlias = list[T] | tuple[T, ...]
    Collection: TypeAlias = OrderedCollection | set[T]

BytesLike = bytes | bytearray | memoryview | mmap.mmap
PathLike = str | Path
ORDERED_COLLECTION_TYPES = list | tuple
COLLECTION_TYPES = ORDERED_COLLECTION_TYPES | set
