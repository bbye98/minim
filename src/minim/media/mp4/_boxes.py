from __future__ import annotations

import struct
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import TYPE_CHECKING, ClassVar

from ..._types import ORDERED_COLLECTION_TYPES, BytesLike
from ..._utility import as_buffer, join_values, validate_number, validate_type
from .._shared import NULPadding

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Self

    from ..._types import OrderedCollection


class MP4Box(ABC):
    """
    Abstract base class for MP4 boxes, without slots.
    """

    _REGISTRY: ClassVar[dict[bytes, type[MP4Box]]] = {}

    _fourcc: bytes | set[bytes]
    _payload: bytes | list[MP4Box]
    _is_top_level: bool

    __slots__ = ()

    def __init_subclass__(
        cls, *, register: bool = True, **kwargs: Any
    ) -> None:
        super().__init_subclass__(**kwargs)

        if register:
            for req_attr in ("_fourcc", "_payload"):
                if not hasattr(cls, req_attr):
                    raise ValueError(
                        f"Subclass {cls.__name__} must define {req_attr!r}."
                    )

            if isinstance(cls._fourcc, bytes):
                cls._REGISTRY[cls._fourcc] = cls
            else:
                for fourcc in cls._fourcc:
                    cls._REGISTRY[fourcc] = cls

    @classmethod
    @abstractmethod
    def _from_stream(
        cls, stream: memoryview, /, *, strict: bool
    ) -> tuple[Self, int, bool]:
        """
        Instantiate an MP4 box object from a bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytestream containing the MP4 box data.

        strict : bool; keyword-only
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
        match box_length := int.from_bytes(stream[:4]):
            case 0:
                box_length = len(stream)
                has_extended_header = False
            case 1:
                box_length = int.from_bytes(stream[8:16])
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
    def from_stream(
        cls,
        stream: BytesLike,
        /,
        *,
        parent: MP4Box | None = None,
        strict: bool = True,
    ) -> Self:
        """
        Instantiate an MP4 box object from a bytes-like object.

        Parameters
        ----------
        stream : bytes-like; positional-only
            Bytes-like object containing the MP4 box data.

        parent : MP4Box or None; keyword-only; optional
            Parent box.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the MP4
            specifications.

        Returns
        -------
        box : MP4Box
            MP4 box.
        """
        stream = as_buffer(stream)
        if stream[4:8] != cls._fourcc:
            raise ValueError(
                f"`stream` does not contain a MP4 {cls._fourcc} box."
            )

        return cls._from_stream(stream, parent=parent, strict=strict)

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
                    (payload_length + 16).to_bytes(length=8),
                    payload,
                )
            )

        return b"".join(
            ((payload_length + 8).to_bytes(length=4), self._fourcc, payload)
        )


class SlottedMP4Box(MP4Box, register=False):
    """
    Abstract base class for MP4 boxes, with slots.
    """

    __slots__ = ("_parent",)

    @property
    def parent(self) -> MP4Box | None:
        """
        Parent MP4 box.
        """
        return self._parent

    @parent.setter
    def parent(self, value: MP4Box | None) -> None:
        if self._is_top_level:
            if value is not None:
                raise ValueError("Cannot set parent for a top-level box.")
        else:
            validate_type("parent", value, MP4Box | None)
        self._parent = value


class MP4ContainerBox(SlottedMP4Box, register=False):
    """
    Base class for MP4 container boxes.
    """

    __slots__ = ("_payload",)

    def __init__(
        self,
        payload: MP4Box | OrderedCollection[MP4Box],
        /,
        *,
        parent: MP4Box | None = None,
    ) -> None:
        """
        Parameters
        ----------
        payload : MP4Box or OrderedCollection[MP4Box]; positional-only
            Child MP4 boxes.

        parent : MP4Box or None; keyword-only; optional
            Parent MP4 box.
        """
        self.payload = payload
        self.parent = parent

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(<{len(self._payload)} box(es)>, "
            f"parent=<{type(self._parent).__name__}>)"
        )

    @classmethod
    def _from_stream(
        cls, stream: memoryview, /, *, parent: MP4Box | None, strict: bool
    ) -> Self:
        """
        Instantiate an MP4 container box object from a bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytestream containing the MP4 container box data.

        parent : MP4Box or None; keyword-only
            Parent MP4 box.

        strict : bool; keyword-only
            Unused keyword argument included only for compatibility.

        Returns
        -------
        box : MP4ContainerBox
            MP4 container box.
        """
        obj, box_length, has_extended_header = super()._from_stream(
            stream, strict=strict
        )
        if strict and parent is not None and cls._is_top_level:
            raise ValueError(
                f"MP4 {cls._fourcc.decode()} box must be a top-level box."
            )

        obj._parent = parent
        obj._payload = payload = []

        offset = 8 * (1 + has_extended_header)
        while offset < box_length:
            box = MP4Box._get_class(
                stream[offset + 4 : offset + 8]
            )._from_stream(stream[offset:], parent=obj, strict=strict)
            payload.append(box)
            offset += box._box_length

        return obj

    @property
    def _payload_length(self) -> int:
        """
        Box payload length, in bytes.
        """
        return sum(pl._box_length for pl in self._payload)

    @property
    def payload(self) -> list[MP4Box]:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Box payload.
        """
        return self._payload.copy()

    @payload.setter
    def payload(self, value: MP4Box | OrderedCollection[MP4Box]) -> None:
        match value:
            case MP4Box():
                self._payload = [value]
            case ORDERED_COLLECTION_TYPES():
                for idx, pl in enumerate(value):
                    validate_type(f"payload[{idx}]", pl, MP4Box)
                self._payload = list(value)
            case _:
                raise TypeError(
                    "`payload` must be an MP4Box object or an ordered "
                    "collection of MP4Box objects."
                )


class MP4freeBox(MP4Box, NULPadding):
    """
    MP4 free space (:code:`free`) box.

    .. seealso::

       `Free space atom ('free') <https://developer.apple.com
       /documentation/quicktime-file-format/free_space_atom>`_.
    """

    _fourcc: ClassVar[bytes] = b"free"
    _is_top_level: ClassVar[bool] = False

    __slots__ = ("_parent",)

    def __init__(
        self, length: int = 0, /, *, parent: MP4Box | None = None
    ) -> None:
        """
        This class implements the following special methods:

        * :code:`__add__` – Merge two MP4 free box objects.

        * :code:`__iadd__` – Merge another MP4 free box object into the
          current one in-place.

        * :code:`__len__` – Return the length of the padding in the MP4
          free box.

        Parameters
        ----------
        length : int; positional-only; default: :code:`0`
            Padding length, in bytes.

        parent : MP4Box or None; keyword-only; optional
            Parent MP4 box.
        """
        super().__init__(length)
        self.parent = parent

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self._length}, "
            f"parent=<{type(self._parent).__name__}>)"
        )

    @classmethod
    def _from_stream(
        cls, stream: memoryview, /, *, parent: MP4Box | None, strict: bool
    ) -> Self:
        """
        Instantiate a :class:`MP4freeBox` object from a MP4 :code:`free`
        box bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the MP4 :code:`free` box data.

        parent : MP4Box or None; keyword-only
            Parent MP4 box.

        strict : bool; keyword-only
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
        obj._parent = parent
        return obj

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

    @property
    def parent(self) -> MP4Box | None:
        """
        Parent MP4 box.
        """
        return self._parent

    @parent.setter
    def parent(self, value: MP4Box | None) -> None:
        validate_type("parent", value, MP4Box | None)
        self._parent = value


class MP4ftypBox(SlottedMP4Box):
    """
    MP4 file type compatibility (:code:`ftyp`) box.

    .. seealso::

       `File type compatibility atom ('ftyp')
       <https://developer.apple.com/documentation/quicktime-file-format
       /file_type_compatibility_atom>`_.
    """

    _fourcc: ClassVar[bytes] = b"ftyp"
    _is_top_level: ClassVar[bool] = True

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

            **Valid range**: :code:`0` to :code:`0xFFFFFFFF`.

        compatible_brands : bytes, bytearray, or \
        OrderedCollection[bytes | bytearray]
            Compatible brand identifiers.

            **Examples**: :code:`b"isom"`, :code:`b"iso2"`.
        """
        self.compatible_brands = compatible_brands
        self.major_brand = major_brand
        self.minor_version = minor_version
        self._parent = None

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(major_brand={self._major_brand!r}, "
            f"minor_version={self._minor_version}, "
            f"compatible_brands={self._compatible_brands!r})"
        )

    @classmethod
    def _from_stream(
        cls, stream: memoryview, /, *, parent: MP4Box | None, strict: bool
    ) -> Self:
        """
        Instantiate a :class:`MP4ftypBox` object from a MP4 :code:`ftyp`
        box bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytestream containing the :code:`ftyp` box.

        parent : MP4Box or None; keyword-only
            Parent MP4 box.

        strict : bool; keyword-only
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
            if parent is not None:
                raise ValueError("MP4 ftyp box must be a top-level box.")

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
        obj._minor_version = int.from_bytes(stream[offset:end_offset])
        obj._compatible_brands = [
            stream[i : i + 4].tobytes()
            for i in range(end_offset, box_length, 4)
        ]
        obj._parent = parent
        return obj

    @property
    def _payload(self) -> bytes:
        """
        Box payload.
        """
        return b"".join(
            (
                self._major_brand,
                self._minor_version.to_bytes(length=4),
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
        validate_number("minor_version", value, int, 0, 0xFFFFFFFF)
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


class MP4mdatBox(SlottedMP4Box):
    """
    MP4 media data (:code:`mdat`) box.

    .. seealso::

       `Movie data atom ('mdat') <https://developer.apple.com
       /documentation/quicktime-file-format/movie_data_atom>`_.
    """

    _fourcc: ClassVar[bytes] = b"mdat"
    _is_top_level: ClassVar[bool] = True

    __slots__ = ("_file_path", "_media_data")

    def __init__(self, media_data: bytes | bytearray, /) -> None:
        """
        Parameters
        ----------
        media_data : bytes or bytearray; positional-only
            Media data.

        """
        self.media_data = media_data
        self._file_path = self._parent = None

    def __repr__(self) -> str:
        return f"{type(self).__name__}(<{self._payload_length} byte(s)>)"

    @classmethod
    def _from_stream(
        cls,
        stream: memoryview,
        /,
        *,
        parent: MP4Box | None,
        file_path: Path | None,
        offset: int | None,
        strict: bool,
    ) -> Self:
        """
        Instantiate a :class:`MP4mdatBox` object from a MP4 :code:`mdat`
        box bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytestream containing the :code:`mdat` box.

        parent : MP4Box or None
            Parent MP4 box.

        file_path : Path; keyword-only
            Path to the MP4 file.

        offset : int; keyword-only
            Byte offset of the start of the bytestream.

        strict : bool; keyword-only
            Unused keyword argument included only for compatibility.

        Returns
        -------
        mdat_box : MP4mdatBox
            MP4 :code:`mdat` box.
        """
        obj, box_length, has_extended_header = super()._from_stream(
            stream, strict=strict
        )
        if strict and parent is not None:
            raise ValueError("MP4 mdat box must be a top-level box.")

        if file_path is not None and offset is not None:
            obj._media_data = (
                offset + 8 * (1 + has_extended_header),
                offset + box_length,
            )
            obj._file_path = file_path
        else:
            obj._media_data = stream[8 * (1 + has_extended_header) :].tobytes()
            obj._file_path = None
        obj._parent = parent
        return obj

    @property
    def _payload(self) -> bytes:
        """
        Box payload.
        """
        return self.media_data

    @property
    def _payload_length(self) -> int:
        """
        Box payload length, in bytes.
        """
        media_data = self._media_data
        if isinstance(media_data, bytes):
            return len(media_data)

        return media_data[1] - media_data[0]

    @property
    def media_data(self) -> bytes:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Media data.
        """
        media_data = self._media_data
        if not isinstance(media_data, bytes):
            with open(self._file_path, "rb") as f:
                f.seek(media_data[0])
                self._media_data = media_data = f.read(
                    media_data[1] - media_data[0]
                )
        return media_data

    @media_data.setter
    def media_data(self, value: bytes | bytearray) -> None:
        validate_type("media_data", value, bytes | bytearray)
        self._media_data = bytes(value)


class MP4moovBox(MP4ContainerBox):
    """
    MP4 movie (:code:`moov`) box.

    .. seealso::

       `Movie atom ('moov') <https://developer.apple.com/documentation
       /quicktime-file-format/movie_atom>`_.
    """

    _fourcc: ClassVar[bytes] = b"moov"
    _is_top_level: ClassVar[bool] = True

    __slots__ = ()

    @classmethod
    def _from_stream(
        cls, stream: memoryview, /, *, parent: MP4Box | None, strict: bool
    ) -> Self:
        """
        Instantiate a :class:`MP4moovBox` object from a MP4 :code:`moov`
        box bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytestream containing the :code:`moov` box.

        parent : MP4Box or None; keyword-only
            Parent MP4 box.

        strict : bool; keyword-only
            Whether to ensure metadata strictly adheres to the MP4
            specifications.

        Returns
        -------
        moov_box : MP4moovBox
            MP4 :code:`moov` box.
        """
        if strict and parent is not None:
            raise ValueError("MP4 moov box must be a top-level box.")

        obj = super()._from_stream(stream, parent=parent, strict=strict)

        if strict and not any(
            isinstance(child, MP4mvhdBox) for child in obj._payload
        ):
            raise ValueError(
                "MP4 moov box bytestream does not contain a mvhd box."
            )

        return obj


class MP4mvhdBox(SlottedMP4Box):
    """
    MP4 movie header (:code:`mvhd`) box.

    .. seealso::

       `Movie header atom ('mvhd') <https://developer.apple.com
       /documentation/quicktime-file-format/movie_header_atom>`_.
    """

    _EPOCH: ClassVar[datetime] = datetime(1904, 1, 1, tzinfo=UTC)
    _EPOCH_OFFSET: ClassVar[int] = -2_082_844_800
    _STRUCT_HEADER: ClassVar[struct.Struct] = struct.Struct(">B3s")
    _STRUCTS: ClassVar[dict[int, struct.Struct]] = {
        0: struct.Struct(">5IH10s9i7I"),
        1: struct.Struct(">QQIQIH10s9i7I"),
    }
    _TRANSFORMATION_MATRIX_COLUMNS_SCALE_MIN_MAX = (
        (0x10000, -32_768, 32_767.999_984_741_21),
        (0x10000, -32_768, 32_767.999_984_741_21),
        (0x40000000, -2, 1.999_999_999_068_677_4),
    )

    _fourcc: ClassVar[bytes] = b"mvhd"
    _is_top_level: ClassVar[bool] = False

    __slots__ = (
        "_creation_time",
        "_current_time",
        "_duration",
        "_flags",
        "_modification_time",
        "_next_track_id",
        "_poster_time",
        "_preferred_rate",
        "_preferred_volume",
        "_preview_duration",
        "_preview_time",
        "_selection_duration",
        "_selection_time",
        "_timescale",
        "_transformation_matrix",
        "_version",
    )

    def __init__(
        self,
        *,
        version: int = 0,
        flags: int = 0,
        creation_time: datetime = _EPOCH,
        modification_time: datetime = _EPOCH,
        timescale: int = 1_000,
        duration: int | None = None,
        preferred_rate: float = 1.0,
        preferred_volume: float = 1.0,
        transformation_matrix: OrderedCollection[OrderedCollection[float]] = (
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
        ),
        preview_time: int = 0,
        preview_duration: int = 0,
        poster_time: int = 0,
        selection_time: int = 0,
        selection_duration: int = 0,
        current_time: int = 0,
        next_track_id: int = 1,
        parent: MP4Box | None = None,
    ) -> None:
        """
        Parameters
        ----------
        version : int; keyword-only; default: :code:`0`
            Version.

        flags : int; keyword-only; default: :code:`0`
            Flags.

        creation_time : datetime; keyword-only; \
        default: :code:`datetime(1904, 1, 1)`
            Datetime of the creation of the :code:`moov` box.

        modification_time : datetime; keyword-only; \
        default: :code:`datetime(1904, 1, 1)`
            Datetime of the last change to the :code:`moov` box.

        timescale : int; keyword-only; default: :code:`1_000`
            Timescale, or the number of time units that pass per second 
            in its time coordinate system.

        duration : int; keyword-only; optional
            Duration, in seconds.

        preferred_rate : float; keyword-only; default: :code:`1.0`
            Preferred rate, or the fraction of the media's normal rate, 
            for playback.

        preferred_volume : float; keyword-only; default: :code:`1.0`
            Preferred volume, as a fraction of the media's normal 
            volume.

        transformation_matrix : OrderedCollection[OrderedCollection[float]]; \
        keyword-only; \
        default: :code:`((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))`
            Transformation matrix.

        preview_time : int; keyword-only; default: :code:`0`
            Time in the media at which the preview begins, in seconds.

        preview_duration : int; keyword-only; default: :code:`0`
            Duration of the preview, in seconds.

        poster_time : int; keyword-only; default: :code:`0`
            Time in the media at which the poster begins, in seconds.

        selection_time : int; keyword-only; default: :code:`0`
            Time in the media at which the selection begins, in seconds.

        selection_duration : int; keyword-only; default: :code:`0`
            Duration of the selection, in seconds.

        current_time : int; keyword-only; default: :code:`0`
            Current time in the media, in seconds.

        next_track_id : int; keyword-only; default: :code:`1`
            Track ID of the next track in the media.

        parent : MP4Box | None; keyword-only; default: :code:`None`
            Parent box.
        """
        self.parent = parent
        self.version = version
        self.flags = flags
        self.creation_time = creation_time
        self.modification_time = modification_time
        self.timescale = timescale
        if duration is None:
            duration = 0xFFFFFFFFFFFFFFFF if version else 0xFFFFFFFF
        self.duration = duration
        self.preferred_rate = preferred_rate
        self.preferred_volume = preferred_volume
        self.transformation_matrix = transformation_matrix
        self.preview_time = preview_time
        self.preview_duration = preview_duration
        self.poster_time = poster_time
        self.selection_time = selection_time
        self.selection_duration = selection_duration
        self.current_time = current_time
        self.next_track_id = next_track_id

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(version={self.version}, "
            f"flags={self.flags}, "
            f"creation_time={self.creation_time!r}, "
            f"modification_time={self.modification_time!r}, "
            f"timescale={self.timescale}, duration={self.duration}, "
            f"preferred_rate={self.preferred_rate}, "
            f"preferred_volume={self.preferred_volume}, "
            f"transformation_matrix={self.transformation_matrix!r}, "
            f"preview_time={self.preview_time}, "
            f"preview_duration={self.preview_duration}, "
            f"poster_time={self.poster_time}, "
            f"selection_time={self.selection_time}, "
            f"selection_duration={self.selection_duration}, "
            f"current_time={self.current_time}, "
            f"next_track_id={self.next_track_id}, "
            f"parent=<{type(self._parent).__name__}>)"
        )

    @classmethod
    def _from_stream(
        cls, stream: memoryview, /, *, parent: MP4Box | None, strict: bool
    ) -> Self:
        """
        Instantiate a :class:`MP4mvhdBox` object from a MP4 box
        bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            MP4 box bytestream.

        parent : MP4Box or None; keyword-only
            Parent box.

        strict : bool; keyword-only
            Whether to raise an exception if the box is malformed.

        Returns
        -------
        mvhd_box : MP4mvhdBox
           :class:`MP4mvhdBox` box.
        """
        obj, _, has_extended_header = super()._from_stream(
            stream, strict=strict
        )
        offset = 8 * (1 + has_extended_header)
        version, flags = cls._STRUCT_HEADER.unpack_from(stream, offset)
        if version not in cls._STRUCTS:
            raise ValueError(
                "Invalid MP4 mvhd box version. "
                f"Valid values: {join_values(cls._STRUCTS)}."
            )

        if strict:
            if has_extended_header:
                raise ValueError(
                    "MP4 mvhd box cannot have an extended header."
                )

            if flags != b"\x00\x00\x00":
                raise ValueError("Non-zero bits found in MP4 mvhd box flags.")

        obj._version = version
        obj._flags = int.from_bytes(flags)

        (
            obj._creation_time,
            obj._modification_time,
            obj._timescale,
            obj._duration,
            obj._preferred_rate,
            obj._preferred_volume,
            reserved,
            a,
            b,
            u,
            c,
            d,
            v,
            x,
            y,
            w,
            obj._preview_time,
            obj._preview_duration,
            obj._poster_time,
            obj._selection_time,
            obj._selection_duration,
            obj._current_time,
            obj._next_track_id,
        ) = cls._STRUCTS[version].unpack_from(stream, offset + 4)

        if strict:
            if reserved != 10 * b"\x00":
                raise ValueError(
                    "Non-zero bits found in MP4 mvhd box reserved field."
                )

            if not obj._next_track_id:
                raise ValueError("MP4 mvhd box next track ID cannot be zero.")

        obj._transformation_matrix = ((a, b, u), (c, d, v), (x, y, w))
        obj._parent = parent
        return obj

    @property
    def _payload(self) -> bytes:
        """
        Box payload.
        """
        return self._STRUCT_HEADER.pack(
            self._version, self._flags.to_bytes(length=3)
        ) + self._STRUCTS[self._version].pack(
            self._creation_time,
            self._modification_time,
            self._timescale,
            self._duration,
            self._preferred_rate,
            self._preferred_volume,
            10 * b"\x00",
            *self._transformation_matrix[0],
            *self._transformation_matrix[1],
            *self._transformation_matrix[2],
            self._preview_time,
            self._preview_duration,
            self._poster_time,
            self._selection_time,
            self._selection_duration,
            self._current_time,
            self._next_track_id,
        )

    @property
    def _payload_length(self) -> int:
        """
        Box payload length, in bytes.
        """
        return 112 if self._version else 100

    @property
    def version(self) -> int:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Version.
        """
        return self._version

    @version.setter
    def version(self, value: int) -> None:
        if value not in self._STRUCTS:
            raise ValueError(
                "Invalid MP4 mvhd box version. "
                f"Valid values: {join_values(self._STRUCTS)}."
            )

        self._version = value

    @property
    def flags(self) -> int:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Flags.
        """
        return self._flags

    @flags.setter
    def flags(self, value: int) -> None:
        validate_number("flags", value, int, 0, 0xFFFFFF)
        self._flags = value

    @property
    def creation_time(self) -> datetime:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Datetime of the creation of the :code:`moov` box.
        """
        return datetime.fromtimestamp(
            self._creation_time + self._EPOCH_OFFSET, tz=UTC
        )

    @creation_time.setter
    def creation_time(self, value: datetime) -> None:
        validate_type("creation_time", value, datetime)
        value = round(value.timestamp()) - self._EPOCH_OFFSET
        validate_number(
            "creation_time",
            value,
            int,
            0,
            0xFFFFFFFFFFFFFFFF if self._version else 0xFFFFFFFF,
        )
        self._creation_time = value

    @property
    def modification_time(self) -> datetime:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Datetime of the last change to the :code:`moov` box.
        """
        return datetime.fromtimestamp(
            self._modification_time + self._EPOCH_OFFSET, tz=UTC
        )

    @modification_time.setter
    def modification_time(self, value: datetime) -> None:
        validate_type("modification_time", value, datetime)
        value = round(value.timestamp()) - self._EPOCH_OFFSET
        validate_number(
            "modification_time",
            value,
            int,
            0,
            0xFFFFFFFFFFFFFFFF if self._version else 0xFFFFFFFF,
        )
        self._modification_time = value

    @property
    def timescale(self) -> int:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Timescale, or the number of time units that pass per second in
        its time coordinate system.
        """
        return self._timescale

    @timescale.setter
    def timescale(self, value: int) -> None:
        validate_number("timescale", value, int, 1, 0xFFFFFFFF)
        self._timescale = value

    @property
    def duration(self) -> float:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Duration, in seconds.
        """
        return self._duration / self._timescale

    @duration.setter
    def duration(self, value: float) -> None:
        validate_number(
            "duration",
            value,
            float,
            0,
            (0xFFFFFFFFFFFFFFFF if self._version else 0xFFFFFFFF)
            / self._timescale,
        )
        self._duration = round(value * self._timescale)

    @property
    def preferred_rate(self) -> float:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Preferred rate, or the fraction of the media's normal rate, for
        playback.
        """
        return self._preferred_rate / 0x10000

    @preferred_rate.setter
    def preferred_rate(self, value: float) -> None:
        validate_number(
            "preferred_rate", value, float, 0.0, 65_535.999_984_741_21
        )
        self._preferred_rate = round(value * 0x10000)

    @property
    def preferred_volume(self) -> float:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Preferred volume, as a fraction of the media's normal volume.
        """
        return self._preferred_volume / 256

    @preferred_volume.setter
    def preferred_volume(self, value: float) -> None:
        validate_number("preferred_volume", value, float, 0.0, 255.996_093_75)
        self._preferred_volume = round(value * 256)

    @property
    def transformation_matrix(
        self,
    ) -> tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Transformation matrix.
        """
        return tuple(
            (row[0] / 0x10000, row[1] / 0x10000, row[2] / 0x40000000)
            for row in self._transformation_matrix
        )

    @transformation_matrix.setter
    def transformation_matrix(
        self, value: OrderedCollection[OrderedCollection[float]]
    ) -> None:
        if (
            not isinstance(value, ORDERED_COLLECTION_TYPES)
            or len(value) != 3
            or not all(
                isinstance(row, ORDERED_COLLECTION_TYPES) and len(row) == 3
                for row in value
            )
        ):
            raise ValueError(
                "`transformation_matrix` must be a 3-by-3 matrix of numbers."
            )

        matrix = []
        for row_idx, row in enumerate(value):
            encoded_row = []
            for col_idx, (col, (scale, minimum, maximum)) in enumerate(
                zip(row, self._TRANSFORMATION_MATRIX_COLUMNS_SCALE_MIN_MAX)
            ):
                validate_number(
                    f"transformation_matrix[{row_idx}][{col_idx}]",
                    col,
                    int | float,
                    minimum,
                    maximum,
                )
                encoded_row.append(round(col * scale))
            matrix.append(encoded_row)
        self._transformation_matrix = matrix

    @property
    def preview_time(self) -> float:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Time in the media at which the preview begins, in seconds.
        """
        return self._preview_time / self._timescale

    @preview_time.setter
    def preview_time(self, value: float) -> None:
        validate_number(
            "preview_time", value, float, 0, 0xFFFFFFFF / self._timescale
        )
        self._preview_time = round(value * self._timescale)

    @property
    def preview_duration(self) -> float:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Duration of the preview, in seconds.
        """
        return self._preview_duration / self._timescale

    @preview_duration.setter
    def preview_duration(self, value: float) -> None:
        validate_number(
            "preview_duration", value, float, 0, 0xFFFFFFFF / self._timescale
        )
        self._preview_duration = round(value * self._timescale)

    @property
    def poster_time(self) -> float:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Time in the media at which the poster begins, in seconds.
        """
        return self._poster_time / self._timescale

    @poster_time.setter
    def poster_time(self, value: float) -> None:
        validate_number(
            "poster_time", value, float, 0, 0xFFFFFFFF / self._timescale
        )
        self._poster_time = round(value * self._timescale)

    @property
    def selection_time(self) -> float:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Time in the media at which the current selection begins, in
        seconds.
        """
        return self._selection_time / self._timescale

    @selection_time.setter
    def selection_time(self, value: float) -> None:
        validate_number(
            "selection_time", value, float, 0, 0xFFFFFFFF / self._timescale
        )
        self._selection_time = round(value * self._timescale)

    @property
    def selection_duration(self) -> float:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Duration of the current selection, in seconds.
        """
        return self._selection_duration / self._timescale

    @selection_duration.setter
    def selection_duration(self, value: float) -> None:
        validate_number(
            "selection_duration", value, float, 0, 0xFFFFFFFF / self._timescale
        )
        self._selection_duration = round(value * self._timescale)

    @property
    def current_time(self) -> float:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Current time position within the media, in seconds.
        """
        return self._current_time / self._timescale

    @current_time.setter
    def current_time(self, value: float) -> None:
        validate_number(
            "current_time", value, float, 0, 0xFFFFFFFF / self._timescale
        )
        self._current_time = round(value * self._timescale)

    @property
    def next_track_id(self) -> int:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Track ID of the next track in the media.
        """
        return self._next_track_id

    @next_track_id.setter
    def next_track_id(self, value: int) -> None:
        validate_number("next_track_id", value, int, 1, 0xFFFFFFFF)
        self._next_track_id = value


class MP4ilstBox(MP4ContainerBox):
    """
    MP4 metadata item list (:code:`ilst`) box.

    .. seealso::

       `Metadata item list atom ('ilst') <https://developer.apple.com
       /documentation/quicktime-file-format/metadata_item_list_atom>`_.
    """

    _fourcc: ClassVar[bytes] = b"ilst"
    _is_top_level: ClassVar[bool] = False

    __slots__ = ()


# class MP4mdiaBox(MP4ContainerBox):
#     pass


# class MP4metaBox(MP4ContainerBox):
#     pass


# class MP4trakBox(MP4ContainerBox):
#     pass


class MP4udtaBox(MP4ContainerBox):
    """
    MP4 user data (:code:`udta`) box.

    .. seealso::

       `User data atom ('udta') <https://developer.apple.com
       /documentation/quicktime-file-format/user_data_atom>`_.
    """

    _fourcc: ClassVar[bytes] = b"udta"
    _is_top_level: ClassVar[bool] = False

    __slots__ = ()


class UnknownMP4Box(SlottedMP4Box, register=False):
    """
    Unknown MP4 box.
    """

    _is_top_level: ClassVar[bool] = False

    __slots__ = ("_fourcc", "_payload")

    def __init__(
        self,
        fourcc: bytes,
        payload: bytes | bytearray | MP4Box | OrderedCollection[MP4Box],
        *,
        parent: MP4Box | None = None,
    ) -> None:
        """
        Parameters
        ----------
        fourcc : bytes
            Four-character code.

        payload : bytes, bytearray, or OrderedCollection[MP4Box]
            Box payload.

        parent : MP4Box or None; keyword-only; optional
            Parent box.

        """
        super().__init__()
        self.parent = parent

        validate_type("fourcc", fourcc, bytes)
        if len(fourcc) != 4:
            raise ValueError("`fourcc` must be a 4-byte encoded string.")
        self._fourcc = fourcc

        match payload:
            case ORDERED_COLLECTION_TYPES():
                for idx, box in enumerate(payload):
                    validate_type(f"box[{idx}]", box, MP4Box)
                self._payload = list(payload)
            case MP4Box():
                self._payload = [payload]
            case bytes() | bytearray():
                self._payload = bytes(payload)
            case _:
                raise TypeError(
                    "`payload` must be a bytes object, a bytearray, or "
                    "one or more MP4Box objects."
                )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(fourcc={self._fourcc!r}, "
            f"payload=<{self._payload_length} byte(s)>, "
            f"parent=<{type(self._parent).__name__}>)"
        )

    @classmethod
    def _from_stream(
        cls, stream: memoryview, /, *, parent: MP4Box | None, strict: bool
    ) -> Self:
        """
        Instantiate a :class:`UnknownMP4Box` object from a MP4 box
        bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytestream containing the MP4 box data.

        parent : MP4Box or None; keyword-only
            Parent box.

        strict : bool; keyword-only
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
        obj._parent = parent
        return obj

    @classmethod
    def from_stream(
        cls,
        stream: BytesLike,
        /,
        *,
        parent: MP4Box | None = None,
        strict: bool = True,
    ) -> Self:
        """
        Instantiate a :class:`UnknownMP4Box` object from a bytes-like
        object.

        Parameters
        ----------
        stream : BytesLike; positional-only
            Bytes-like object containing the MP4 box data.

        parent : MP4Box or None; keyword-only; optional
            Parent box.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the MP4
            specifications.

        Returns
        -------
        box : UnknownMP4Box
            Unknown MP4 box.
        """
        return cls._from_stream(
            as_buffer(stream), parent=parent, strict=strict
        )

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
        :bdg-primary:`get` :bdg-secondary-line:`set` Four-character code.
        """
        return self._fourcc

    @property
    def payload(self) -> bytes | list[MP4Box]:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set` Box payload.
        """
        payload = self._payload
        if isinstance(payload, bytes):
            return self._payload

        return self._payload.copy()
