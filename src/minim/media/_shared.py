from __future__ import annotations
from abc import ABC, abstractmethod
import mmap
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._types import BytesLike, PathLike
    from .metadata import AudioStreamInfo, AudioTags

    from typing import Any


def as_buffer(stream: BytesLike) -> memoryview:
    """
    Return a C-level buffer interface to a bytes-like object.

    Parameters
    ----------
    bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
    positional-only; optional
        Bytes-like object.

    Returns
    -------
    view : memoryview
        Buffer interface to the bytes-like object.
    """
    match stream:
        case bytes() | bytearray() | mmap.mmap():
            stream = memoryview(stream)
        case memoryview():
            pass
        case _:
            raise TypeError("`stream` must be a bytes-like object.")
    return stream


class Audio(ABC):
    """
    Abstract base class for audio files.
    """

    __slots__ = (
        "_file",
        "_file_path",
        "_format_metadata",
        "_mmap",
        "_stream_info",
        "_tags",
        "_view",
    )

    def __init__(self, file_path: PathLike, /) -> None:
        """ """
        self._file_path = Path(file_path).expanduser().resolve(strict=True)
        self.load_metadata()

    @abstractmethod
    def load_metadata(self) -> None:
        """ """
        ...

    @abstractmethod
    def save_metadata(
        self, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> None:
        """ """
        ...

    @property
    def stream_info(self) -> AudioStreamInfo:
        """
        Technical properties of the decoded audio stream.
        """
        return self._stream_info

    @property
    def format_metadata(self) -> Any:
        """
        Structural metadata instrinsic to the file format or container.
        """
        return self._format_metadata

    @property
    def tags(self) -> AudioTags:
        """
        Metadata fields associated with the audio.
        """
        return self._tags

    def open(self) -> None:
        """ """
        self.close()
        self._file = open(self._file_path, "rb")
        self._mmap = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)
        self._view = memoryview(self._mmap)

    def close(self) -> None:
        """ """
        if hasattr(self, "_view"):
            self._view.release()
            del self._view
        if hasattr(self, "_mmap") and not self._mmap.closed:
            self._mmap.close()
            del self._mmap
        if hasattr(self, "_file") and not self._file.closed:
            self._file.close()
            del self._file
