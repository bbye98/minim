from __future__ import annotations

import mmap
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from .._utility import as_buffer, validate_number, validate_type

if TYPE_CHECKING:
    from typing import Any, Self

    from .._types import BytesLike, PathLike
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

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(file_path={self._file_path!r}, "
            f"strict={self._strict})"
        )

    @abstractmethod
    def add_metadata(self, *args: Any, **kwargs: Any) -> None:
        """
        Add metadata structures and ancillary information.

        Parameters
        ----------
        *args : tuple[Any, ...]
            Positional arguments to accept in implementations.

        **kwargs : dict[str, Any]
            Keyword arguments to accept in implementations.
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
        Remove metadata structures and ancillary information.

        Parameters
        ----------
        *args : tuple[Any, ...]
            Positional arguments to accept in implementations.

        **kwargs : dict[str, Any]
            Keyword arguments to accept in implementations.
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
        :bdg-primary:`get` :bdg-secondary-line:`set`
        Format-specific metadata and ancillary information.
        """
        return self._metadata

    @property
    def stream_info(self) -> AudioStreamInfo | None:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set`
        Technical properties of the audio stream.
        """
        return self._stream_info

    @property
    def tags(self) -> AudioTags:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set`
        Metadata describing the audio track.
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


class NULPadding:
    """
    Padding consisting of NUL bytes (:code:`b"\x00"`).
    """

    __slots__ = ("_length",)

    def __init__(self, length: int) -> None:
        """
        This class implements the following special methods:

        * :code:`__add__` – Merge two NUL-bytes padding objects.

        * :code:`__iadd__` – Merge another NUL-bytes padding object into
          the current one in-place.

        * :code:`__len__` – Return the length of the NUL-bytes padding.

        Parameters
        ----------
        length : int
            Padding length, in bytes.
        """
        self.set_length(length)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(length={self._length})"

    def __add__(self, other: NULPadding) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand types for +: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )
        obj = type_.__new__(type_)
        obj._length = self._length + other._length
        return obj

    def __iadd__(self, other: NULPadding) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand types for +=: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )
        self._length += other._length
        return self

    def __len__(self) -> int:
        return self._length

    @classmethod
    def from_stream(
        cls, stream: BytesLike, /, *, strict: bool = True
    ) -> NULPadding:
        """
        Instantiate a NUL-bytes padding object from a bytes-like object.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing padding.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure the bytestream does not contain any
            non-zero bits.

        Returns
        -------
        padding : minim.media._shared.NULPadding
            NUL-bytes padding object.
        """
        stream = as_buffer(stream)
        if strict and any(stream):
            raise ValueError("Non-zero bits found in PADDING block.")

        obj = cls.__new__(cls)
        obj._length = len(stream)
        return obj

    def adjust_length(self, change: int, /) -> None:
        """
        Adjust the padding length.

        Parameters
        ----------
        change : int; positional-only
            Change to the padding length, in bytes.

        Raises
        ------
        TypeError
            If `change` is not an integer.
        """
        validate_type("change", change, int)
        self._length += change

    def set_length(self, length: int, /) -> None:
        """
        Set the padding length.

        Parameters
        ----------
        length : int; positional-only
            Padding length, in bytes.

        Raises
        ------
        TypeError
            If `length` is not an integer.

        ValueError
            If `length` is not zero or positive.
        """
        validate_number("length", length, int, 0)
        self._length = length

    def serialize(self, *args: Any, **kwargs: Any) -> bytes:
        """
        Serialize the padding to a bytestream.

        Parameters
        ----------
        *args : tuple[Any, ...]
            Additional (ignored) positional arguments.

        **kwargs : dict[str, Any]
            Additional (ignored) keyword arguments.

        Returns
        -------
        stream : bytes
            Bytestream containing the padding bytes.
        """
        return self._length * b"\x00"
