"""
MPEG-4 Part 14 (MP4) audio file handler and stream information reporter.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from .._types import BytesLike
from .._utility import as_buffer, validate_number, validate_type
from ._shared import Audio, MetadataView, NULPadding
from .metadata._shared import AudioStreamInfo, AudioTags


if TYPE_CHECKING:
    from typing import Any, Self

    from .._types import OrderedCollection

# @dataclass(frozen=True, kw_only=True, repr=False, slots=True)
# class MP4StreamInfo(AudioStreamInfo):
#     """
#     MP4 :code:`moov > trak > mdia > minf > stbl > stsd > alac/mp4a` or
#     audio stream information.
#     """


class MP4FREEBox(NULPadding):
    """
    MP4 :code:`free` box or a container for padding data.
    """

    __slots__ = ("_box_length", "_fourcc", "_has_extended_header")

    def __init__(self, length: int = 0, /) -> None:
        """ """
        super().__init__(length)
        self._fourcc = b"free"
        self._has_extended_header = length > 4_294_967_295
        self._box_length = 8 + 8 * self._has_extended_header + length

    @classmethod
    def _from_stream(cls, stream: BytesLike, /) -> Self:
        """ """
        obj = MP4Box._from_stream.__func__(cls, stream, fourcc=b"free")
        obj._length = obj._box_length - 8 * (1 + obj._has_extended_header)
        return obj

    @classmethod
    def from_stream(
        cls, stream: BytesLike, /, *args: Any, **kwargs: Any
    ) -> Self:
        """ """
        stream = as_buffer(stream)
        if stream[4:8] != b"free":
            raise ValueError("`stream` does not contain a MP4 `free` box.")

        return cls._from_stream(stream)

    # def serialize(self) -> bytes:  # TODO
    #     """ """


# @dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class MP4Box:
    """
    MP4 box container.
    """

    _CONTAINER_BOXES: ClassVar[dict[bytes, type[MP4Box] | None]] = {
        b"free": MP4FREEBox
    }

    __slots__ = ("_box_length", "_fourcc", "_has_extended_header", "_payload")

    def __init__(
        self,
        box_length: int,
        fourcc: bytes | bytearray,
        payload: bytes | bytearray | OrderedCollection[MP4Box],
    ) -> None:
        """ """
        validate_number("box_length", box_length, int, 0)
        self._box_length = box_length

        validate_type("fourcc", fourcc, bytes | bytearray)
        self._fourcc = fourcc

        validate_type(
            "payload", payload, bytes | bytearray | OrderedCollection
        )
        if isinstance(payload, OrderedCollection):
            for idx, box in enumerate(payload):
                validate_type(f"box[{idx}]", box, MP4Box)
        self._payload = payload

        self._has_extended_header = box_length > 4_294_967_295

    @classmethod
    def _from_stream(cls, stream: BytesLike, /, fourcc: str) -> Self:
        """ """
        obj = cls.__new__(cls)
        obj._fourcc = fourcc
        match box_length := int.from_bytes(stream[:4], byteorder="big"):
            case 1:
                obj._box_length = int.from_bytes(stream[8:16], byteorder="big")
                obj._has_extended_header = True
            case _:
                obj._box_length = box_length if box_length else len(stream)
                obj._has_extended_header = False
        return obj

    @classmethod
    def from_stream(
        cls, stream: BytesLike, /, *, file_offset: int | None = None
    ) -> Self:
        """ """
        stream = as_buffer(stream)
        fourcc = stream[4:8].tobytes()
        if fourcc in cls._CONTAINER_BOXES:
            return cls._CONTAINER_BOXES[fourcc].from_stream(stream)

        obj = cls._from_stream(stream, fourcc=fourcc)
        if file_offset is None:
            obj._payload = stream[
                8 * (1 + obj._has_extended_header) : obj._box_length
            ]
        else:
            obj._payload = file_offset + 8 * (1 + obj._has_extended_header)
        return obj


class MP4ILSTBox(AudioTags, MP4Box):
    """
    MP4 :code:`moov > udta > meta > ilst` box or metadata container.
    """


class MP4Audio(Audio):
    """
    MP4 audio file.

    .. note::

       Metadata structures and ancillary information are loaded from
       the audio file when the object is instantiated.

       .. seealso::

          :meth:`load_metadata` – Load metadata structures and ancillary
          information from the audio file.
    """

    @property
    def metadata(self):
        raise NotImplementedError()

    def _set_active_tags(self) -> None:
        raise NotImplementedError()

    def add_metadata(self) -> None:
        raise NotImplementedError()

    def load_metadata(self) -> None:
        """
        Load metadata blocks from the MP4 audio file.
        """
        self.open()
        file_path = self._file_path
        view = self._view
        view_length = len(view)
        strict = self._strict

        self._metadata = boxes = []
        self._type_index = type_index = defaultdict(list)
        # self._metadata_view = MP4MetadataView(metadata, type_index=type_index)
        self._tags = None

        offset = 0
        while offset < view_length:
            box = MP4Box.from_stream(view[offset:], file_offset=offset)
            boxes.append(box)
            offset += box._box_length

        raise NotImplementedError()

    def remove_metadata(self) -> None:
        raise NotImplementedError()

    def save(self) -> None:
        raise NotImplementedError()
