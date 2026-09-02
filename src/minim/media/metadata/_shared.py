from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from numbers import Real
from typing import TYPE_CHECKING, ClassVar

from ..._utility import validate_number

if TYPE_CHECKING:
    from typing import Any

    from ..._types import OrderedCollection


@dataclass(frozen=True, kw_only=True, repr=True, slots=True)
class AudioStreamInfo:
    """
    Audio stream information.

    Parameters
    ----------
    num_channels : int; keyword-only
        Number of channels.

    sample_rate : int; keyword-only
        Sample rate, in hertz.

    bit_depth : int; keyword-only
        Bits per sample.

    num_samples : int; keyword-only
        Total number of samples.
    """

    _NUM_CHANNELS_RANGE: ClassVar[tuple[int, int]] = (1, 65_535)
    _SAMPLE_RATE_RANGE: ClassVar[tuple[int, int]] = (1, 4_294_967_295)
    _BIT_DEPTH_RANGE: ClassVar[tuple[int, int]] = (1, 32)

    #: :bdg-primary:`get` :bdg-secondary-line:`set` Number of channels.
    num_channels: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Sample rate, in
    #: hertz.
    sample_rate: int
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Bits per sample.
    bit_depth: int | None
    #: :bdg-primary:`get` :bdg-secondary-line:`set` Total number of
    #: samples.
    num_samples: int

    def __post_init__(self) -> None:
        validate_number(
            "channels", self.num_channels, int, *self._NUM_CHANNELS_RANGE
        )
        validate_number(
            "sample_rate", self.sample_rate, int, *self._SAMPLE_RATE_RANGE
        )
        if self.bit_depth is not None:
            validate_number(
                "bit_depth", self.bit_depth, int, *self._BIT_DEPTH_RANGE
            )
        validate_number("num_samples", self.num_samples, int, 0)

    @property
    @abstractmethod
    def bitrate(self) -> int:
        """
        Bitrate, in kilobits per second.
        """
        return self.sample_rate * self.num_channels * self.bit_depth / 1_000

    @property
    def duration(self) -> float:
        """
        Duration, in seconds.
        """
        return self.num_samples / self.sample_rate


class AudioTags(ABC):
    """
    Abstract base class for track metadata containers.
    """

    __slots__ = ()

    @staticmethod
    def _stringify(value: Any, /) -> Any:
        """
        Try to convert an arbitrary value to a string.

        Parameters
        ----------
        value : Any; positional-only
            Value to convert.

        Returns
        -------
        value : Any
            String representation of the value if it has a supported
            type, and the original value otherwise.
        """
        match value:
            case bool():
                return str(int(value))
            case bytes() | bytearray():
                return value.decode(encoding="utf-8")
            case datetime():
                return value.strftime("%Y-%m-%dT%H:%M:%SZ")
            case Real():
                return str(value)
            case _:
                return value

    @property
    @abstractmethod
    def album(self) -> list[str] | None:
        """
        Title of the album or collection.
        """
        ...

    @property
    @abstractmethod
    def album_artist(self) -> list[str] | None:
        """
        Main artists credited for the entire album or collection.
        """
        ...

    @property
    @abstractmethod
    def artist(self) -> list[str] | None:
        """
        Main artists of the recording (e.g., the performing band or
        singers in popular music, the composers for classical music, or
        the authors of the original text in audiobooks).
        """
        ...

    @property
    @abstractmethod
    def bpm(self) -> list[str] | None:
        """
        Tempo, in beats per minute (BPM).
        """
        ...

    @property
    @abstractmethod
    def comment(self) -> list[str] | None:
        """
        Free-form comments.
        """
        ...

    @property
    @abstractmethod
    def compilation(self) -> list[str] | None:
        """
        Whether the recording is part of a compilation.
        """
        ...

    @property
    @abstractmethod
    def composer(self) -> list[str] | None:
        """
        Composers or songwriters.
        """
        ...

    @property
    @abstractmethod
    def copyright(self) -> list[str] | None:
        """
        Copyright attribution.
        """
        ...

    @property
    @abstractmethod
    def date(self) -> list[str] | None:
        """
        Release date.
        """
        ...

    @property
    @abstractmethod
    def disc_number(self) -> str | list[str] | None:
        """
        Disc number within a multi-disc set.
        """
        ...

    @property
    @abstractmethod
    def disc_total(self) -> str | list[str] | None:
        """
        Total number of discs.
        """
        ...

    @property
    @abstractmethod
    def encoder(self) -> list[str] | None:
        """
        Software or hardware used for encoding, or the person or
        organization that encoded the audio file.
        """
        ...

    @property
    @abstractmethod
    def genre(self) -> list[str] | None:
        """
        Musical genres.
        """
        ...

    @property
    @abstractmethod
    def grouping(self) -> list[str] | None:
        """
        Content group description.
        """
        ...

    @property
    @abstractmethod
    def isrc(self) -> list[str] | None:
        """
        International Standard Recording Code (ISRC).
        """
        ...

    @property
    @abstractmethod
    def label(self) -> list[str] | None:
        """
        Publisher or record label.
        """
        ...

    @property
    @abstractmethod
    def lyrics(self) -> list[str] | None:
        """
        Lyrics or transcription.
        """
        ...

    @property
    @abstractmethod
    def performer(self) -> list[str] | None:
        """
        Performers (e.g., the conductor, orchestra, and/or soloists in
        classical music, or the narrator in audiobooks).
        """
        ...

    @property
    @abstractmethod
    def title(self) -> list[str] | None:
        """
        Title of the recording.
        """
        ...

    @property
    @abstractmethod
    def track_number(self) -> list[str] | None:
        """
        Track number within the album or collection.
        """
        ...

    @property
    @abstractmethod
    def track_total(self) -> list[str] | None:
        """
        Total number of tracks.
        """
        ...

    @property
    @abstractmethod
    def version(self) -> list[str] | None:
        """
        Version of the recording (e.g., remix information).
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """
        Clear all track metadata.
        """
        ...

    @abstractmethod
    def get(self, *args: Any, **kwargs: Any) -> Any:
        """
        Get track metadata.

        Parameters
        ----------
        *args : tuple[Any, ...]
            Positional arguments to accept in implementations.

        **kwargs : dict[str, Any]
            Keyword arguments to accept in implementations.

        Returns
        -------
        tags : Any
            Track metadata.
        """
        ...

    @abstractmethod
    def serialize(self, *args: Any, **kwargs: Any) -> bytes:
        """
        Serialize the track metadata container to a bytestream.

        Parameters
        ----------
        *args : tuple[Any, ...]
            Positional arguments to accept in implementations.

        **kwargs : dict[str, Any]
            Keyword arguments to accept in implementations.

        Returns
        -------
        stream : bytes
            Bytestream containing the serialized track metadata
            container.
        """
        ...

    @abstractmethod
    def set(self, *args: Any, **kwargs: Any) -> None:
        """
        Set track metadata.

        Parameters
        ----------
        *args : tuple[Any, ...]
            Positional arguments to accept in implementations.

        **kwargs : dict[str, Any]
            Keyword arguments to accept in implementations.
        """
        ...
