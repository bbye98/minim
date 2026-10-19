"""
MPEG-4 Part 14 (MP4) audio file handler and stream information reporter.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from types import MemberDescriptorType
from typing import TYPE_CHECKING, ClassVar

from .._types import ORDERED_COLLECTION_TYPES, BytesLike
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


class MP4Box(ABC):
    """
    Abstract base class for MP4 boxes.
    """

    _REGISTRY: ClassVar[dict[bytes, type[MP4Box]]] = {}

    _fourcc: str
    _payload: bytes

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        fourcc = getattr(cls, "_fourcc", None)
        if fourcc is None:
            raise ValueError(f"Subclass {cls.__name__} must define '_fourcc'.")

        if not isinstance(fourcc, MemberDescriptorType):
            cls._REGISTRY[fourcc] = cls

    @classmethod
    @abstractmethod
    def _from_stream(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> tuple[Self, int, bool]:
        """
        Instantiate a :class:`MP4Box` object from a bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytestream containing the MP4 box data.

        strict : bool; keyword-only; default: :code:`True`
            Unused keyword argument included only for compatibility.

        Returns
        -------
        box : MP4Box
            MP4 box.

        box_length : int
            Length of the MP4 box, in bytes.

        has_extended_header : bool
            Whether the MP4 box has an extended header.
        """
        obj = cls.__new__(cls)
        match box_length := int.from_bytes(stream[:4], byteorder="big"):
            case 0:
                box_length = len(stream)
                has_extended_header = False
            case 1:
                box_length = int.from_bytes(stream[8:16], byteorder="big")
                has_extended_header = True
            case _:
                has_extended_header = False
        return obj, box_length, has_extended_header

    @classmethod
    def _get_class(cls, fourcc: bytes, /) -> Self:
        """
        Get the class corresponding to a four-character code.

        Parameters
        ----------
        fourcc : bytes; positional-only
            Four-character code.

        Returns
        -------
        cls : MP4Box
            MP4 box class.
        """
        return cls._REGISTRY.get(fourcc, UnknownMP4Box)

    @classmethod
    @abstractmethod
    def from_stream(cls, stream: BytesLike, /, *, strict: bool = True) -> Self:
        """
        Instantiate a :class:`MP4Box` object from a bytes-like object.

        Parameters
        ----------
        stream : bytes-like; positional-only
            Bytes-like object containing the MP4 box data.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the MP4
            specifications.

        Returns
        -------
        box : MP4Box
            MP4 box.
        """
        ...

    @property
    def _box_length(self) -> int:
        """
        Box length, in bytes.
        """
        return self._payload_length + 8 * (
            1 + (self._payload_length > 4_294_967_287)
        )

    @property
    @abstractmethod
    def _payload_length(self) -> int:
        """
        Box payload length, in bytes.
        """
        ...

    def serialize(self) -> bytes:
        """
        Serialize the MP4 box to a bytestream.

        Returns
        -------
        stream : bytes
            Bytestream containing the MP4 box.
        """
        payload = self._payload
        if isinstance(payload, list):
            payload = b"".join(pl.serialize() for pl in payload)

        payload_length = self._payload_length
        if payload_length > 4_294_967_287:
            return b"".join(
                (
                    b"\x00\x00\x00\x01",
                    self._fourcc,
                    (payload_length + 16).to_bytes(length=8, byteorder="big"),
                    payload,
                )
            )

        return b"".join(
            (
                (payload_length + 8).to_bytes(length=4, byteorder="big"),
                self._fourcc,
                payload,
            )
        )


class MP4freeBox(MP4Box, NULPadding):
    """
    MP4 free space (:code:`free`) box.

    .. seealso::

       `Free space atom ('free') <https://developer.apple.com
       /documentation/quicktime-file-format/free_space_atom>`_.

    This class implements the following special methods:

    * :code:`__add__` – Merge two :code:`free` box objects.

    * :code:`__iadd__` – Merge another :code:`free` box object into the
      current one in-place.

    * :code:`__len__` – Return the length of the :code:`free` box.
    """

    _fourcc: ClassVar[str] = b"free"

    __slots__ = ()

    @classmethod
    def _from_stream(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
        """
        Instantiate a :class:`MP4freeBox` object from a MP4 :code:`free`
        box bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the MP4 :code:`free` box data.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the MP4
            specifications.

        Returns
        -------
        free_box : MP4freeBox
            MP4 :code:`free` box.
        """
        obj, box_length, has_extended_header = super()._from_stream(
            stream, strict=strict
        )
        offset = 8 * (1 + has_extended_header)
        if strict and any(stream[offset:box_length]):
            raise ValueError("Non-zero bits found in MP4 free box.")

        obj._length = box_length - offset
        return obj

    @classmethod
    def from_stream(cls, stream: BytesLike, /, *, strict: bool = True) -> Self:
        """
        Instantiate a :class:`MP4freeBox` object from a MP4 :code:`free`
        box bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the MP4 :code:`free` box data.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the MP4
            specifications.

        Returns
        -------
        free_box : MP4freeBox
            MP4 :code:`free` box.
        """
        stream = as_buffer(stream)
        if stream[4:8] != b"free":
            raise ValueError("`stream` does not contain a MP4 free box.")

        return cls._from_stream(stream, strict=strict)

    @property
    def _payload(self) -> bytes:
        """
        Box payload.
        """
        return super().serialize()

    @property
    def _payload_length(self) -> int:
        """
        Box payload length, in bytes.
        """
        return self._length


class MP4ftypBox(MP4Box):
    """
    MP4 file type compatibility (:code:`ftyp`) box.

    .. seealso::

       `File type compatibility atom ('ftyp')
       <https://developer.apple.com/documentation/quicktime-file-format
       /file_type_compatibility_atom>`_.
    """

    _fourcc: ClassVar[str] = b"ftyp"

    __slots__ = ("_compatible_brands", "_major_brand", "_minor_version")

    def __init__(
        self,
        major_brand: bytes | bytearray,
        minor_version: int,
        compatible_brands: bytes
        | bytearray
        | OrderedCollection[bytes | bytearray],
    ) -> None:
        """
        Parameters
        ----------
        major_brand : bytes or bytearray
            Major brand identifier.

            **Examples**: :code:`b"M4A "`, :code:`b"qt  "`.

        minor_version : int
            Minor version number.

            **Valid range**: :code:`0` to :code:`4_294_967_295`.

        compatible_brands : bytes, bytearray, or \
        OrderedCollection[bytes | bytearray]
            Compatible brand identifiers.

            **Examples**: :code:`b"isom"`, :code:`b"iso2"`.
        """
        self.compatible_brands = compatible_brands
        super().__init__(box_length=16 + 4 * len(self.compatible_brands))
        self.major_brand = major_brand
        self.minor_version = minor_version

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(major_brand={self._major_brand!r}, "
            f"minor_version={self._minor_version}, "
            f"compatible_brands={self._compatible_brands!r})"
        )

    @classmethod
    def _from_stream(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
        """
        Instantiate a :class:`MP4ftypBox` object from a MP4 :code:`ftyp`
        box bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytestream containing the :code:`ftyp` box.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the MP4
            specifications.

        Returns
        -------
        ftyp_box : MP4ftypBox
            MP4 :code:`ftyp` box.
        """
        obj, box_length, has_extended_header = super()._from_stream(
            stream, strict=strict
        )
        if strict:
            if has_extended_header:
                raise ValueError(
                    "MP4 ftyp box cannot have an extended header."
                )

            if box_length < 16:
                raise ValueError(
                    "MP4 ftyp box must be at least 16 bytes long."
                )

        offset = 8 * (1 + has_extended_header)
        end_offset = offset + 4
        obj._major_brand = stream[offset:end_offset].tobytes()
        offset = end_offset
        end_offset = offset + 4
        obj._minor_version = int.from_bytes(
            stream[offset:end_offset], byteorder="big"
        )
        obj._compatible_brands = [
            stream[i : i + 4].tobytes()
            for i in range(end_offset, box_length, 4)
        ]
        return obj

    @classmethod
    def from_stream(cls, stream: BytesLike, /, *, strict: bool = True) -> Self:
        """
        Instantiate a :class:`MP4ftypBox` object from a MP4 :code:`ftyp`
        box bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytestream containing the :code:`ftyp` box.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the MP4
            specifications.

        Returns
        -------
        ftyp_box : MP4ftypBox
            MP4 :code:`ftyp` box.
        """
        stream = as_buffer(stream)
        if stream[4:8] != b"ftyp":
            raise ValueError("`stream` does not contain a MP4 ftyp box.")

        return cls._from_stream(stream, strict=strict)

    @property
    def _payload(self) -> bytes:
        """
        Box payload.
        """
        return b"".join(
            (
                self._major_brand,
                self._minor_version.to_bytes(length=4, byteorder="big"),
                *self._compatible_brands,
            )
        )

    @property
    def _payload_length(self) -> int:
        """
        Box payload length, in bytes.
        """
        return 8 + 4 * len(self._compatible_brands)

    @property
    def major_brand(self) -> bytes:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Major brand identifier.
        """
        return self._major_brand

    @major_brand.setter
    def major_brand(self, value: bytes | bytearray) -> None:
        validate_type("major_brand", value, bytes | bytearray)
        if len(value) != 4:
            raise ValueError("`major_brand` must be a 4-byte encoded string.")
        self._major_brand = bytes(value)

    @property
    def minor_version(self) -> int:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Minor version number.
        """
        return self._minor_version

    @minor_version.setter
    def minor_version(self, value: int) -> None:
        validate_number("minor_version", value, int, 0, 4_294_967_295)
        self._minor_version = value

    @property
    def compatible_brands(self) -> list[bytes]:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Compatible brand identifiers.
        """
        return self._compatible_brands.copy()

    @compatible_brands.setter
    def compatible_brands(
        self, value: bytes | bytearray | OrderedCollection[bytes | bytearray]
    ) -> None:
        compatible_brands = (
            list(value)
            if isinstance(value, ORDERED_COLLECTION_TYPES)
            else [value]
        )
        for idx, brand in enumerate(compatible_brands):
            validate_type(f"compatible_brands[{idx}]", brand, bytes)
            if len(brand) != 4:
                raise ValueError(
                    f"`compatible_brands[{idx}]` must be a 4-byte "
                    "encoded string."
                )
        self._compatible_brands = compatible_brands


class UnknownMP4Box(MP4Box):
    """ """

    __slots__ = ("_fourcc", "_payload")

    def __init__(
        self,
        fourcc: bytes,
        payload: bytes | bytearray | list[MP4Box],
    ) -> None:
        """ """
        super().__init__()

        validate_type("fourcc", fourcc, bytes)
        if len(fourcc) != 4:
            raise ValueError("`fourcc` must be a 4-byte encoded string.")
        self._fourcc = fourcc

        validate_type(
            "payload", payload, bytes | bytearray | OrderedCollection
        )
        if isinstance(payload, OrderedCollection):
            for idx, box in enumerate(payload):
                validate_type(f"box[{idx}]", box, MP4Box)
            payload = list(payload)
        else:
            payload = bytes(payload)
        self._payload = payload

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(fourcc={self._fourcc!r}, "
            f"payload=<{self._payload_length} byte(s)>)"
        )

    @classmethod
    def _from_stream(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
        """
        Instantiate a :class:`UnknownMP4Box` object from a MP4 box
        bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytestream containing the MP4 box data.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the MP4
            specifications.

        Returns
        -------
        box : UnknownMP4Box
            Unknown MP4 box.
        """
        obj, box_length, has_extended_header = super()._from_stream(
            stream, strict=strict
        )
        obj._fourcc = stream[4:8].tobytes()
        obj._payload = stream[
            8 * (1 + has_extended_header) : box_length
        ].tobytes()
        return obj

    @classmethod
    def from_stream(cls, stream: BytesLike, /, *, strict: bool = True) -> Self:
        """
        Instantiate a :class:`UnknownMP4Box` object from a bytes-like
        object.

        Parameters
        ----------
        stream : BytesLike; positional-only
            Bytes-like object containing the MP4 box data.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the MP4
            specifications.

        Returns
        -------
        box : UnknownMP4Box
            Unknown MP4 box.
        """
        return cls._from_stream(as_buffer(stream), strict=strict)

    @property
    def _payload_length(self) -> int:
        """
        Box payload length, in bytes.
        """
        payload = self._payload
        if isinstance(payload, bytes):
            return len(payload)

        return sum(pl._box_length for pl in payload)

    @property
    def fourcc(self) -> bytes:
        """
        Four-character code.
        """
        return self._fourcc

    @property
    def payload(self) -> bytes | list[MP4Box]:
        """
        Box payload.
        """
        payload = self._payload
        if isinstance(payload, bytes):
            return self._payload

        return self._payload.copy()


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
    def audio_data(self):
        raise NotImplementedError()

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
            box = MP4Box._get_class(
                view[offset + 4 : offset + 8]
            )._from_stream(view[offset:])
            boxes.append(box)
            type_index[box._fourcc].append(box)
            offset += box._box_length

        # TODO

    def remove_metadata(self) -> None:
        raise NotImplementedError()

    def save(self) -> None:
        raise NotImplementedError()
