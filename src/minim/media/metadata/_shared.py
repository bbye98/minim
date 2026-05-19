from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from numbers import Real
from typing import TYPE_CHECKING

from ..._utility import validate_number

if TYPE_CHECKING:
    from typing import Any

    from ..._types import Collection, OrderedCollection


@dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class AudioStreamInfo:
    """
    Audio stream information.

    Parameters
    ----------
    num_channels : int; keyword-only
        Number of channels.

    sample_rate : int; keyword-only
        Sample rate in hertz.

    bit_depth : int; keyword-only
        Bits per sample.

    num_samples : int; keyword-only
        Total number of samples.
    """

    _NUM_CHANNELS_RANGE = (1, 65_535)
    _SAMPLE_RATE_RANGE = (1, 4_294_967_295)
    _BIT_DEPTH_RANGE = (1, 32)

    #: Number of channels.
    num_channels: int
    #: Sample rate in hertz.
    sample_rate: int
    #: Bits per sample.
    bit_depth: int
    #: Total number of samples.
    num_samples: int

    def __post_init__(self) -> None:
        validate_number(
            "channels", self.num_channels, int, *self._NUM_CHANNELS_RANGE
        )
        validate_number(
            "sample_rate", self.sample_rate, int, *self._SAMPLE_RATE_RANGE
        )
        validate_number(
            "bit_depth", self.bit_depth, int, *self._BIT_DEPTH_RANGE
        )
        validate_number("num_samples", self.num_samples, int, 0)

    @property
    def bitrate(self) -> int:
        """
        Bitrate in bits per second.
        """
        return self.sample_rate * self.num_channels * self.bit_depth

    @property
    def duration(self) -> float:
        """
        Duration in seconds.
        """
        return self.num_samples / self.sample_rate


class AudioTags(ABC):
    """
    Abstract base class for audio metadata containers.
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
    def album(self) -> str | list[str] | None:
        """
        Title of the album or collection.
        """
        ...

    @album.setter
    @abstractmethod
    def album(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def album_artist(self) -> str | list[str] | None:
        """
        Main artists credited for the entire album or collection.
        """
        ...

    @album_artist.setter
    @abstractmethod
    def album_artist(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def artist(self) -> str | list[str] | None:
        """
        Main artists of the recording (e.g., the performing band or
        singers in popular music, the composers for classical music, or
        the authors of the original text in audiobooks).
        """
        ...

    @artist.setter
    @abstractmethod
    def artist(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def bpm(self) -> int | list[str] | None:
        """
        Tempo in beats per minute (BPM).
        """
        ...

    @bpm.setter
    @abstractmethod
    def bpm(
        self,
        value: int | float | str | OrderedCollection[int | float | str],
        /,
    ) -> None: ...

    @property
    @abstractmethod
    def comment(self) -> str | list[str] | None:
        """
        Free-form comments.
        """
        ...

    @comment.setter
    @abstractmethod
    def comment(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def compilation(self) -> bool | list[str] | None:
        """
        Whether the recording is part of a compilation.
        """
        ...

    @compilation.setter
    @abstractmethod
    def compilation(
        self, value: bool | int | str | OrderedCollection[bool | int | str], /
    ) -> None: ...

    @property
    @abstractmethod
    def composer(self) -> str | list[str] | None:
        """
        Composers or songwriters.
        """
        ...

    @composer.setter
    @abstractmethod
    def composer(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def contact(self) -> str | list[str] | None:
        """
        Contact information for the creators or distributors.
        """
        ...

    @contact.setter
    @abstractmethod
    def contact(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def copyright(self) -> str | list[str] | None:
        """
        Copyright attribution.
        """
        ...

    @copyright.setter
    @abstractmethod
    def copyright(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def date(self) -> str | list[str] | None:
        """
        Release date.
        """
        ...

    @date.setter
    @abstractmethod
    def date(
        self, value: str | datetime | OrderedCollection[str | datetime], /
    ) -> None: ...

    @property
    @abstractmethod
    def description(self) -> str | list[str] | None:
        """
        General description.
        """
        ...

    @description.setter
    @abstractmethod
    def description(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def disc_number(self) -> int | str | list[str] | None:
        """
        Disc number within a multi-disc set.
        """
        ...

    @disc_number.setter
    @abstractmethod
    def disc_number(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    @abstractmethod
    def disc_total(self) -> int | str | list[str] | None:
        """
        Total number of discs.
        """
        ...

    @disc_total.setter
    @abstractmethod
    def disc_total(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    @abstractmethod
    def encoder(self) -> str | list[str] | None:
        """
        Software or hardware used for encoding, or the person or
        organization that encoded the audio file.
        """
        ...

    @encoder.setter
    @abstractmethod
    def encoder(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def genre(self) -> str | list[str] | None:
        """
        Musical genres.
        """
        ...

    @genre.setter
    @abstractmethod
    def genre(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def grouping(self) -> str | list[str] | None:
        """
        Content group description.
        """
        ...

    @grouping.setter
    @abstractmethod
    def grouping(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def isrc(self) -> str | list[str] | None:
        """
        International Standard Recording Code (ISRC).
        """
        ...

    @isrc.setter
    @abstractmethod
    def isrc(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def label(self) -> str | list[str] | None:
        """
        Publisher or record label.
        """
        ...

    @label.setter
    @abstractmethod
    def label(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def license(self) -> str | list[str] | None:
        """
        License information.
        """
        ...

    @license.setter
    @abstractmethod
    def license(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def location(self) -> str | list[str] | None:
        """
        Recording locations.
        """
        ...

    @location.setter
    @abstractmethod
    def location(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def lyrics(self) -> str | list[str] | None:
        """
        Lyrics or transcription.
        """
        ...

    @lyrics.setter
    @abstractmethod
    def lyrics(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def performer(self) -> str | list[str] | None:
        """
        Performers (e.g., the conductor, orchestra, and/or soloists in
        classical music, or the narrator in audiobooks).
        """
        ...

    @performer.setter
    @abstractmethod
    def performer(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def title(self) -> str | list[str] | None:
        """
        Title of the recording.
        """
        ...

    @title.setter
    @abstractmethod
    def title(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def track_number(self) -> int | list[str] | None:
        """
        Track number within the album or collection.
        """
        ...

    @track_number.setter
    @abstractmethod
    def track_number(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    @abstractmethod
    def track_total(self) -> int | list[str] | None:
        """
        Total number of tracks.
        """
        ...

    @track_total.setter
    @abstractmethod
    def track_total(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    @abstractmethod
    def version(self) -> str | list[str] | None:
        """
        Version of the recording (e.g., remix information).
        """
        ...

    @version.setter
    @abstractmethod
    def version(self, value: str | OrderedCollection[str], /) -> None: ...

    @abstractmethod
    def get(
        self,
        fields: str | Collection[str],
        /,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> Any | dict[str, Any]:
        """
        Get track attributes.

        Parameters
        ----------
        fields : str or Collection[str]; positional-only
            Field names of the attributes.

        *args : tuple[Any, ...]
            Positional arguments to accept in implementations.

        **kwargs : dict[str, Any]
            Keyword arguments to accept in implementations.

        Returns
        -------
        attributes : Any or dict[str, Any]
            Track attributes. If `fields` is a collection of strings, a
            dictionary mapping field names to their corresponding values
            is returned.
        """
        ...

    @abstractmethod
    def serialize(
        self, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> bytes:
        """
        Serialize metadata to a bytestream.

        Parameters
        ----------
        *args : tuple[Any, ...]
            Positional arguments to accept in implementations.

        **kwargs : dict[str, Any]
            Keyword arguments to accept in implementations.

        Returns
        -------
        bytestream : bytes
            Bytestream containing the serialized metadata.
        """
        ...

    @abstractmethod
    def set(self, **kwargs: dict[str, Any]) -> None:
        """
        Set track attributes.

        Parameters
        ----------
        **kwargs : dict[str, Any]
            Key–value pairs of track attributes.
        """
        ...
