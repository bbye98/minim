from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import mmap
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from .._metadata import AudioTags


@dataclass(frozen=True, slots=True)
class AudioStreamInfo:
    """
    Audio stream information.
    """

    num_channels: int
    sample_rate: int
    bits_per_sample: int
    total_samples: int

    @property
    def bitrate(self) -> int:
        """
        Bitrate in bits per second.
        """
        return self.sample_rate * self.num_channels * self.bits_per_sample

    @property
    def duration(self) -> float:
        """
        Duration in seconds.
        """
        if self.sample_rate == 0:
            return 0.0
        return self.total_samples / self.sample_rate


class Audio(ABC):
    """
    Abstract base class for audio files.
    """

    _tags: AudioTags

    # __slots__ = ()

    def __init__(self, file_path: str | Path, /) -> None:
        """ """
        self._file_path = Path(file_path).expanduser().resolve(strict=True)
        self.open()

    @abstractmethod
    def open(self) -> None:
        """ """
        self.close()
        self._file = open(self._file_path, "rb")
        self._mmap = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)
        self._memoryview = memoryview(self._mmap)

    # @property
    # @abstractmethod
    # def info(self) -> dict[str, Any]:
    #     """ """
    #     return self._info

    # @property
    # @abstractmethod
    # def metadata(self) -> dict[str, Any]:
    #     """ """
    #     return self._metadata

    @property
    def tags(self) -> AudioTags:
        """ """
        return self._tags

    def close(self) -> None:
        """ """
        if hasattr(self, "_memoryview"):
            self._memoryview.release()
            del self._memoryview
        if hasattr(self, "_mmap") and not self._mmap.closed:
            self._mmap.close()
            del self._mmap
        if hasattr(self, "_file") and not self._file.closed:
            self._file.close()
            del self._file
