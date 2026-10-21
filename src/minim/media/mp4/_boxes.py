from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

from ..._types import ORDERED_COLLECTION_TYPES, BytesLike
from ..._utility import as_buffer, validate_number, validate_type
from .._shared import NULPadding

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Self

    from ..._types import OrderedCollection


class MP4Box(ABC):
    """
    Abstract base class for MP4 boxes.
    """

    _REGISTRY: ClassVar[dict[bytes, type[MP4Box]]] = {}

    _fourcc: bytes
    _payload: bytes | list[MP4Box]

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

            cls._REGISTRY[cls._fourcc] = cls

    @classmethod
    @abstractmethod
    def _from_stream(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> tuple[Self, int, bool]:
        """
        Instantiate an MP4 box object from a bytestream.

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
    def from_stream(cls, stream: BytesLike, /, *, strict: bool = True) -> Self:
        """
        Instantiate an MP4 box object from a bytes-like object.

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
        stream = as_buffer(stream)
        if stream[4:8] != cls._fourcc:
            raise ValueError(
                f"`stream` does not contain a MP4 {cls._fourcc} box."
            )

        return cls._from_stream(stream, strict=strict)

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


class MP4ContainerBox(MP4Box, register=False):
    """
    Abstract base class for MP4 container boxes.
    """

    __slots__ = ("_payload",)

    def __init__(self, payload: MP4Box | OrderedCollection[MP4Box], /) -> None:
        """
        Parameters
        ----------
        payload : MP4Box or OrderedCollection[MP4Box]; positional-only
            Child MP4 boxes.
        """
        self.payload = payload

    def __repr__(self) -> str:
        return f"{type(self).__name__}(<{len(self._payload)} box(es)>)"

    @classmethod
    def _from_stream(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
        """
        Instantiate an MP4 container box object from a bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytestream containing the MP4 container box data.

        strict : bool; keyword-only; default: :code:`True`
            Unused keyword argument included only for compatibility.

        Returns
        -------
        box : MP4ContainerBox
            MP4 container box.
        """
        obj, box_length, has_extended_header = super()._from_stream(
            stream, strict=strict
        )
        obj._payload = payload = []

        offset = 8 * (1 + has_extended_header)
        while offset < box_length:
            box = MP4Box._get_class(
                stream[offset + 4 : offset + 8]
            )._from_stream(stream[offset:], strict=strict)
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

    _fourcc: ClassVar[bytes] = b"ftyp"

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


class MP4mdatBox(MP4Box):
    """
    MP4 media data (:code:`mdat`) box.

    .. seealso::

       `Movie data atom ('mdat') <https://developer.apple.com
       /documentation/quicktime-file-format/movie_data_atom>`_.
    """

    _fourcc: ClassVar[bytes] = b"mdat"

    __slots__ = ("_file_path", "_media_data")

    def __init__(self, media_data: bytes | bytearray, /) -> None:
        """
        Parameters
        ----------
        media_data : bytes or bytearray; positional-only
            Media data.
        """
        self.media_data = media_data
        self._file_path = None

    def __repr__(self) -> str:
        return f"{type(self).__name__}(<{self._payload_length} byte(s)>)"

    @classmethod
    def _from_stream(
        cls,
        stream: memoryview,
        /,
        *,
        file_path: Path | None = None,
        offset: int | None = None,
        strict: bool = True,
    ) -> Self:
        """
        Instantiate a :class:`MP4mdatBox` object from a MP4 :code:`mdat`
        box bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytestream containing the :code:`mdat` box.

        file_path : Path; keyword-only; optional
            Path to the MP4 file.

        offset : int; keyword-only; optional
            Byte offset of the start of the bytestream.

        strict : bool; keyword-only; default: :code:`True`
            Unused keyword argument included only for compatibility.

        Returns
        -------
        mdat_box : MP4mdatBox
            MP4 :code:`mdat` box.
        """
        obj, box_length, has_extended_header = super()._from_stream(
            stream, strict=strict
        )
        if file_path is not None and offset is not None:
            obj._media_data = (
                offset + 8 * (1 + has_extended_header),
                offset + box_length,
            )
            obj._file_path = file_path
        else:
            obj._media_data = stream[8 * (1 + has_extended_header) :].tobytes()
            obj._file_path = None
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

    __slots__ = ()


class UnknownMP4Box(MP4Box, register=False):
    """
    Unknown MP4 box.
    """

    __slots__ = ("_fourcc", "_payload")

    def __init__(
        self,
        fourcc: bytes,
        payload: bytes | bytearray | MP4Box | OrderedCollection[MP4Box],
    ) -> None:
        """
        Parameters
        ----------
        fourcc : bytes
            Four-character code.

        payload : bytes, bytearray, or OrderedCollection[MP4Box]
            Box payload.
        """
        super().__init__()

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
