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
    if isinstance(stream, memoryview):
        return stream

    if isinstance(stream, bytes | bytearray | mmap.mmap):
        return memoryview(stream)

    raise TypeError("`stream` must be a bytes-like object.")


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
        """
        Parameters
        ----------
        file_path : str or pathlib.Path; positional-only
            Path to or name of the audio file.
        """
        self._file_path = Path(file_path).expanduser().resolve(strict=True)
        self.load_metadata()

    @abstractmethod
    def add_metadata(
        self, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> None:
        """
        Add metadata.
        """
        ...

    @abstractmethod
    def load_metadata(self) -> None:
        """
        Load audio metadata.
        """
        ...

    @abstractmethod
    def remove_metadata(
        self, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> None:
        """
        Remove metadata.
        """
        ...

    @abstractmethod
    def save(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        """
        Write changes to disk.

        Parameters
        ----------
        *args : tuple[Any, ...]
            Positional arguments to accept in implementations.

        **kwargs : dict[str, Any]
            Keyword arguments to accept in implementations.
        """
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
        Structural metadata intrinsic to the file format or container.
        """
        return self._format_metadata

    @property
    def tags(self) -> AudioTags:
        """
        Metadata fields associated with the audio.
        """
        return self._tags

    def open(self) -> None:
        """
        Initialize a memory-mapped view of the audio file.
        """
        self.close()
        self._file = open(self._file_path, "rb")
        self._mmap = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)
        self._view = memoryview(self._mmap)

    def close(self) -> None:
        """
        Release and unmap the audio file from memory.
        """
        if hasattr(self, "_view"):
            self._view.release()
            del self._view
        if hasattr(self, "_mmap") and not self._mmap.closed:
            self._mmap.close()
            del self._mmap
        if hasattr(self, "_file") and not self._file.closed:
            self._file.close()
            del self._file
