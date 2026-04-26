from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import mmap
from pathlib import Path
from typing import TYPE_CHECKING

from ..._utility import validate_number

if TYPE_CHECKING:
    from ..metadata import AudioTags


@dataclass(frozen=True, slots=True)
class AudioStreamInfo:
    """
    Audio stream information.
    """

    _NUM_CHANNELS_RANGE = (1, 65_535)
    _SAMPLE_RATE_RANGE = (1, 4_294_967_295)
    _BITS_PER_SAMPLE_RANGE = (1, 32)

    #: Number of channels.
    num_channels: int
    #: Sample rate in Hz.
    sample_rate: int
    #: Bits per sample.
    bits_per_sample: int
    #: Total samples.
    total_samples: int

    def __post_init__(self) -> None:
        validate_number(
            "num_channels", self.num_channels, int, *self._NUM_CHANNELS_RANGE
        )
        validate_number(
            "sample_rate", self.sample_rate, int, *self._SAMPLE_RATE_RANGE
        )
        validate_number(
            "bits_per_sample",
            self.bits_per_sample,
            int,
            *self._BITS_PER_SAMPLE_RANGE,
        )
        validate_number("total_samples", self.total_samples, int, 0)

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
        return self.total_samples / self.sample_rate


class Audio(ABC):
    """
    Abstract base class for audio files.
    """

    _tags: AudioTags

    __slots__ = "_file", "_file_path", "_mmap", "_view"

    def __init__(self, file_path: str | Path, /) -> None:
        """ """
        self._file_path = Path(file_path).expanduser().resolve(strict=True)
        self.load_metadata()

    @abstractmethod
    def load_metadata(self) -> None:
        """ """
        ...

    @abstractmethod
    def save_metadata(self) -> None:
        """ """
        ...

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
        """
        Audio tag data.
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
