from __future__ import annotations

import mmap
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from .._utility import validate_type

if TYPE_CHECKING:
    from typing import Any

    from .._types import PathLike
    from .metadata._shared import AudioStreamInfo, AudioTags


class Audio(ABC):
    """
    Abstract base class for audio files.
    """

    __slots__ = (
        "_file",
        "_file_path",
        "_metadata",
        "_mmap",
        "_stream_info",
        "_strict",
        "_tags",
        "_view",
    )

    def __init__(self, file_path: PathLike, /, *, strict: bool = True) -> None:
        """
        .. note::

           Metadata structures and ancillary information are loaded from
           the audio file when the object is instantiated.

           .. seealso::

              :meth:`load_metadata` – Load metadata structures and
              ancillary information from the audio file.

        Parameters
        ----------
        file_path : PathLike; positional-only
            Path to or name of the audio file.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the audio
            format specifications.

        Raises
        ------
        FileNotFoundError
            If `file_path` is an invalid file path or the file does not
            exist.

        TypeError
            If `file_path` is not a path-like object or `strict` is not
            a Boolean.
        """
        self._file_path = Path(file_path).expanduser().resolve(strict=True)
        validate_type("strict", strict, bool)
        self._strict = strict
        self._file = self._mmap = self._view = None
        self.load_metadata()

    @abstractmethod
    def add_metadata(self, *args: Any, **kwargs: Any) -> None:
        """
        Add metadata structures and ancillary information.
        """
        ...

    @abstractmethod
    def load_metadata(self) -> None:
        """
        Load metadata structures and ancillary information from the
        audio file.
        """
        ...

    @abstractmethod
    def remove_metadata(self, *args: Any, **kwargs: Any) -> None:
        """
        Remove metadata structures and/or ancillary information.
        """
        ...

    @abstractmethod
    def save(self, *args: Any, **kwargs: Any) -> None:
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
    def metadata(self) -> Any:
        """
        :bdg-primary:`read` :bdg-secondary-line:`write`
        Metadata structures and/or ancillary information stored in the
        audio file.
        """
        return self._metadata

    @property
    def stream_info(self) -> AudioStreamInfo | None:
        """
        :bdg-primary:`read` :bdg-secondary-line:`write`
        Technical properties of the decoded audio stream.
        """
        return self._stream_info

    @property
    def tags(self) -> AudioTags:
        """
        :bdg-primary:`read` :bdg-secondary-line:`write`
        Metadata fields associated with the audio.
        """
        return self._tags

    def open(self) -> None:
        """
        Initialize a memory-mapped view of the audio file.
        """
        self.close()
        self._file = open(self._file_path, "rb")  # noqa: SIM115
        self._mmap = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)
        self._view = memoryview(self._mmap)

    def close(self) -> None:
        """
        Release and unmap the audio file from memory.
        """
        if self._view is not None:
            self._view.release()
            self._view = None
        if (mmap := self._mmap) is not None and not mmap.closed:
            mmap.close()
            self._mmap = None
        if (file := self._file) is not None and not file.closed:
            file.close()
            self._file = None
