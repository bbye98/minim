from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import FrozenInstanceError, dataclass
from datetime import datetime
import re
from typing import TYPE_CHECKING

from ...._utility import (
    ASCII_CHARS_REGEX,
    decode_32_bit_synchsafe_int,
    join_values,
    prepare_isrc,
    set_obj_attr,
    validate_number,
    validate_numeric,
    validate_type,
)
from ..._shared import as_buffer
from . import TAG_VERSIONS

if TYPE_CHECKING:
    from typing import Any

    from ...._types import BytesLike


@dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class ID3v2FrameStatusFlags:
    """
    Status flags for an ID3v2 frame.

    Parameters
    ----------
    discard_on_tag_alter : bool; keyword-only; default: :code:`False`
        Whether to discard the current frame when the ID3 tag is edited.

    discard_on_file_alter : bool; keyword-only; default: :code:`False`
        Whether to discard the current frame when the audio data changes.

    is_read_only : bool; keyword-only; default: :code:`False`
        Whether the current frame is read-only.
    """

    #: Whether to discard the current frame when the ID3 tag is edited.
    discard_on_tag_alter: bool = False
    #: Whether to discard the current frame when the audio data changes.
    discard_on_file_alter: bool = False
    #: Whether the current frame is read-only.
    is_read_only: bool = False

    def __post_init__(self) -> None:
        validate_type("discard_on_tag_alter", self.discard_on_tag_alter, bool)
        validate_type(
            "discard_on_file_alter", self.discard_on_file_alter, bool
        )
        validate_type("is_read_only", self.is_read_only, bool)

    @classmethod
    def _from_byte_2_4(
        cls, byte_: int, /, *, strict: bool = True
    ) -> ID3v2FrameStatusFlags:
        """
        Instantiate an :class:`ID3v2FrameStatusFlags` object from an
        ID3v2.4 frame status flags byte.

        Parameters
        ----------
        byte_ : int; positional-only
            ID3v2.4 frame status flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.ID3v2FrameStatusFlags
            Status flags for an ID3v2 frame.
        """
        if strict and byte_ & 0x8F:
            raise ValueError(
                "Reserved bits set in ID3v2 frame status flags byte."
            )

        obj = cls.__new__(cls)
        set_obj_attr(obj, "discard_on_tag_alter", bool(byte_ & 0x40))
        set_obj_attr(obj, "discard_on_file_alter", bool(byte_ & 0x20))
        set_obj_attr(obj, "is_read_only", bool(byte_ & 0x10))
        return obj

    @classmethod
    def _from_byte_2_3(
        cls, byte_: int, /, *, strict: bool = True
    ) -> ID3v2FrameStatusFlags:
        """
        Instantiate an :class:`ID3v2FrameStatusFlags` object from an
        ID3v2.3 frame status flags byte.

        Parameters
        ----------
        byte_ : int; positional-only
            Flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.ID3v2FrameStatusFlags
            Status flags for an ID3v2 frame.
        """
        if strict and byte_ & 0x1F:
            raise ValueError(
                "Reserved bits set in ID3v2 frame status flags byte."
            )

        obj = cls.__new__(cls)
        set_obj_attr(obj, "discard_on_tag_alter", bool(byte_ & 0x80))
        set_obj_attr(obj, "discard_on_file_alter", bool(byte_ & 0x40))
        set_obj_attr(obj, "is_read_only", bool(byte_ & 0x20))
        return obj

    @classmethod
    def _from_byte_2_2(
        cls, byte_: int, /, *, strict: bool = True
    ) -> ID3v2FrameStatusFlags:
        """
        Instantiate an :class:`ID3v2FrameStatusFlags` object from an
        ID3v2.2 frame status flags byte.

        Parameters
        ----------
        byte_ : int; positional-only
            Flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.ID3v2FrameStatusFlags
            Status flags for an ID3v2 frame.
        """
        if strict and byte_:
            raise ValueError(
                "Reserved bits set in ID3v2 frame status flags byte."
            )

        obj = cls.__new__(cls)
        set_obj_attr(obj, "discard_on_tag_alter", False)
        set_obj_attr(obj, "discard_on_file_alter", False)
        set_obj_attr(obj, "is_read_only", False)
        return obj

    @classmethod
    def from_byte(
        cls,
        byte_: int,
        /,
        tag_version: str | tuple[int, int, int],
        *,
        strict: bool = True,
    ) -> ID3v2FrameStatusFlags:
        """
        Instantiate an :class:`ID3v2FrameStatusFlags` object from a byte.

        Parameters
        ----------
        byte_ : int; positional-only
            Flags byte.

        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.ID3v2FrameStatusFlags
            Status flags for an ID3v2 frame.
        """
        validate_number("byte_", byte_, int, 0)
        match ID3v2Frame._normalize_tag_version(tag_version):
            case (2, 4, _):
                return cls._from_byte_2_4(byte_, strict=strict)
            case (2, 3, _):
                return cls._from_byte_2_3(byte_, strict=strict)
            case (2, 2, _):
                return cls._from_byte_2_2(byte_, strict=strict)
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )


@dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class ID3v2FrameFormatFlags:
    """
    Format flags for an ID3v2 frame.

    Parameters
    ----------
    has_grouping : bool; keyword-only; default: :code:`False`
        Whether the current frame has a grouping identifier.

    is_compressed : bool; keyword-only; default: :code:`False`
        Whether the current frame is compressed.

    is_encrypted : bool; keyword-only; default: :code:`False`
        Whether the current frame is encrypted.

    is_unsynchronized : bool; keyword-only; default: :code:`False`
        Whether the current frame has frame-level unsynchronization.

    has_data_length_indicator : bool; keyword-only; \
    default: :code:`False`
        Whether the current frame has an extra synchsafe integer
        preceding the payload.
    """

    #: Whether the current frame has a grouping identifier.
    has_grouping: bool = False
    #: Whether the current frame is compressed.
    is_compressed: bool = False
    #: Whether the current frame is encrypted.
    is_encrypted: bool = False
    #: Whether the current frame has frame-level unsynchronization.
    is_unsynchronized: bool = False
    #: Whether the current frame has an extra synchsafe integer
    #: preceding the payload.
    has_data_length_indicator: bool = False

    def __post_init__(self) -> None:
        validate_type("has_grouping", self.has_grouping, bool)
        validate_type("is_compressed", self.is_compressed, bool)
        validate_type("is_encrypted", self.is_encrypted, bool)
        validate_type("is_unsynchronized", self.is_unsynchronized, bool)
        validate_type(
            "has_data_length_indicator", self.has_data_length_indicator, bool
        )

    @classmethod
    def _from_byte_2_4(
        cls, byte_: int, /, *, strict: bool = True
    ) -> ID3v2FrameFormatFlags:
        """
        Instantiate an :class:`ID3v2FrameFormatFlags` object from an
        ID3v2.4 frame format flags byte.

        Parameters
        ----------
        byte_ : int; positional-only
            Flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.ID3v2FrameFormatFlags
            Format flags for an ID3v2 frame.
        """
        if strict and byte_ & 0x70:
            raise ValueError(
                "Reserved bits set in ID3v2 frame format flags byte."
            )

        obj = cls.__new__(cls)
        set_obj_attr(obj, "has_grouping", bool(byte_ & 0x40))
        set_obj_attr(obj, "is_compressed", bool(byte_ & 0x08))
        set_obj_attr(obj, "is_encrypted", bool(byte_ & 0x04))
        set_obj_attr(obj, "is_unsynchronized", bool(byte_ & 0x02))
        set_obj_attr(obj, "has_data_length_indicator", bool(byte_ & 0x01))
        return obj

    @classmethod
    def _from_byte_2_3(
        cls, byte_: int, /, *, strict: bool = True
    ) -> ID3v2FrameFormatFlags:
        """
        Instantiate an :class:`ID3v2FrameFormatFlags` object from an
        ID3v2.3 frame format flags byte.

        Parameters
        ----------
        byte_ : int; positional-only
            Flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.ID3v2FrameFormatFlags
            Format flags for an ID3v2 frame.
        """
        if strict and byte_ & 0x1F:
            raise ValueError(
                "Reserved bits set in ID3v2 frame format flags byte."
            )

        obj = cls.__new__(cls)
        set_obj_attr(obj, "is_compressed", bool(byte_ & 0x80))
        set_obj_attr(obj, "is_encrypted", bool(byte_ & 0x40))
        set_obj_attr(obj, "has_grouping", bool(byte_ & 0x20))
        set_obj_attr(obj, "is_unsynchronized", False)
        set_obj_attr(obj, "has_data_length_indicator", False)
        return obj

    @classmethod
    def _from_byte_2_2(
        cls, byte_: int, /, *, strict: bool = True
    ) -> ID3v2FrameFormatFlags:
        """
        Instantiate an :class:`ID3v2FrameFormatFlags` object from an
        ID3v2.2 frame format flags byte.

        Parameters
        ----------
        byte_ : int; positional-only
            Flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.ID3v2FrameFormatFlags
            Format flags for an ID3v2 frame.
        """
        if strict and byte_:
            raise ValueError(
                "Reserved bits set in ID3v2 frame format flags byte."
            )

        obj = cls.__new__(cls)
        set_obj_attr(obj, "has_grouping", False)
        set_obj_attr(obj, "is_compressed", False)
        set_obj_attr(obj, "is_encrypted", False)
        set_obj_attr(obj, "is_unsynchronized", False)
        set_obj_attr(obj, "has_data_length_indicator", False)
        return obj

    @classmethod
    def from_byte(
        cls,
        byte_: int,
        /,
        tag_version: str | tuple[int, int, int],
        *,
        strict: bool = True,
    ) -> ID3v2FrameFormatFlags:
        """
        Instantiate an :class:`ID3v2FrameFormatFlags` object from a byte.

        Parameters
        ----------
        byte_ : int; positional-only
            Flags byte.

        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.ID3v2FrameFormatFlags
            Format flags for an ID3v2 frame.
        """
        validate_number("byte_", byte_, int, 0)
        match ID3v2Frame._normalize_tag_version(tag_version):
            case (2, 4, _):
                return cls._from_byte_2_4(byte_, strict=strict)
            case (2, 3, _):
                return cls._from_byte_2_3(byte_, strict=strict)
            case (2, 2, _):
                return cls._from_byte_2_2(byte_, strict=strict)
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )


class ID3v2Frame(ABC):
    """
    ID3v2 frame.
    """

    _TEXT_ENCODINGS = {0: "iso-8859-1", 1: "utf-16", 2: "utf-16be", 3: "utf-8"}
    _REGISTRY = {}

    __slots__ = "_format_flags", "_status_flags"

    def __init__(
        self,
        *,
        format_flags: ID3v2FrameFormatFlags | None = None,
        status_flags: ID3v2FrameStatusFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        format_flags : minim.media.metadata.ID3v2FrameFormatFlags; \
        keyword-only; optional
            Format flags for an ID3v2 frame.

        status_flags : minim.media.metadata.ID3v2FrameStatusFlags; \
        keyword-only; optional
            Status flags for an ID3v2 frame.
        """
        if format_flags is None:
            self._format_flags = ID3v2FrameFormatFlags()
        else:
            validate_type("format_flags", format_flags, ID3v2FrameFormatFlags)
            self._format_flags = format_flags

        if status_flags is None:
            self._status_flags = ID3v2FrameFormatFlags()
        else:
            validate_type("status_flags", status_flags, ID3v2FrameStatusFlags)
            self._status_flags = status_flags

    def __init_subclass__(cls, **kwargs: dict[str, Any]) -> None:
        super().__init_subclass__(**kwargs)
        for frame_ids in cls._frame_ids.values():
            if isinstance(frame_ids, bytes):
                cls._REGISTRY[frame_ids] = cls
            else:
                for frame_id in frame_ids:
                    cls._REGISTRY[frame_id] = cls

    @classmethod
    def _get_class(cls, frame_id: bytes, /) -> ID3v2Frame:
        """
        Get the class corresponding to an ID3v2 frame ID.

        Parameters
        ----------
        frame_id : bytes; positional-only
            ID3v2 frame ID.

        Returns
        -------
        cls : ID3v2Frame
            ID3v2 frame class.
        """
        return cls._REGISTRY.get(frame_id, UnknownID3v2Frame)

    @classmethod
    @abstractmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2Frame:
        """
        Instantiate an :class:`ID3v2Frame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only; optional
            Bytes-like object containing an ID3v2 frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        frame : minim.media.metadata.ID3v2Frame
            ID3v2 frame.
        """
        obj = cls.__new__(cls)
        obj._format_flags = ID3v2FrameFormatFlags._from_byte_2_4(
            stream[8], strict=strict
        )
        obj._status_flags = ID3v2FrameStatusFlags._from_byte_2_4(
            stream[9], strict=strict
        )
        return obj

    @classmethod
    def from_stream(
        cls,
        stream: memoryview,
        /,
        tag_version: str | tuple[int, int, int],
        *,
        strict: bool = True,
    ) -> ID3v2Frame:
        """
        Instantiate an :class:`ID3v2Frame` object from a bytes-like
        object.

        Parameters
        ----------
        stream : memoryview; positional-only; optional
            Bytes-like object containing an ID3v2 frame.

        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        frame : minim.media.metadata.ID3v2Frame
            ID3v2 frame.
        """
        tag_version = cls._normalize_tag_version(tag_version)
        expected_frame_id = cls.get_frame_id(tag_version)
        if stream[: len(expected_frame_id)] != expected_frame_id:
            raise ValueError(
                f"`bytestream` does not contain a {expected_frame_id} frame."
            )

        match tag_version:
            case (2, 4, _):
                return cls._from_stream_2_4(stream, strict=strict)
            case (2, 3, _):
                raise NotImplementedError  # TODO
            case (2, 2, _):
                raise NotImplementedError  # TODO
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )

    @classmethod
    def get_frame_id(
        cls, tag_version: str | tuple[int, int, int]
    ) -> bytes | None:
        """
        Get the ID3v2 frame ID.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        frame_id : bytes or None
            ID3v2 frame ID. If no native frame is available for the
            specified ID3v2 tag version, :code:`None` is returned.
        """
        match cls._normalize_tag_version(tag_version):
            case (2, 4, _):
                return cls._frame_ids.get(4)
            case (2, 3, _):
                return cls._frame_ids.get(3)
            case (2, 2, _):
                return cls._frame_ids.get(2)
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )

    @staticmethod
    def _normalize_tag_version(
        tag_version: str | tuple[int, int, int], /
    ) -> tuple[int, int, int]:
        """
        Normalize ID3v2 tag version.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        tag_version : tuple[int, int, int]
            ID3v2 tag version.
        """
        match tag_version:
            case tuple() | list():
                return tag_version
            case str():
                return tuple(int(v) for v in tag_version.split("."))
            case _:
                raise TypeError(
                    "`tag_version` must be a string or a tuple of "
                    "three integers."
                )

    @property
    @abstractmethod
    def _frame_ids(self) -> dict[int, bytes]:
        """
        ID3v2 frame IDs, with the keys being the ID3v2 tag minor
        versions.
        """
        ...

    @property
    def format_flags(self) -> ID3v2FrameFormatFlags:
        """
        Format flags for an ID3v2 frame.
        """
        return self._format_flags

    @property
    def status_flags(self) -> ID3v2FrameStatusFlags:
        """
        Status flags for an ID3v2 frame.
        """
        return self._status_flags

    @abstractmethod
    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the ID3v2 frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        stream : bytes
            Bytestream containing the ID3v2 frame.
        """
        ...


class ID3v2TextInfoFrame(ID3v2Frame):
    """
    Text information frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2. Text information frames
       <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2. Text information frames
       <https://id3.org/id3v2.3.0#Text_information_frames>`_.

       `ID3v2.4.0 Native Frames: 4.2. Text information frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {}

    __slots__ = "_text_info", "_text_encoding"

    def __init__(
        self,
        text_info: str,
        /,
        *,
        text_encoding: str = "utf-16",
        format_flags: ID3v2FrameFormatFlags | None = None,
        status_flags: ID3v2FrameStatusFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        text_info : str; positional-only
            Text information.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        format_flags : minim.media.metadata.ID3v2FrameFormatFlags; \
        keyword-only; optional
            Format flags.

        status_flags : minim.media.metadata.ID3v2FrameStatusFlags; \
        keyword-only; optional
            Status flags.
        """
        super().__init__(format_flags=format_flags, status_flags=status_flags)

        validate_type("text_info", text_info, str)
        self._text_info = text_info

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        if text_encoding == "iso-8859-1":
            try:
                text_info.encode(encoding=text_encoding)
                is_utf = False
            except UnicodeEncodeError:
                is_utf = True
            if is_utf:
                raise ValueError(
                    "`text_info` cannot be encoded using ISO-8859-1."
                )
        self._text_encoding = text_encoding

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TextInfoFrame:
        """
        Instantiate an ID3v2 text information frame object from an
        ID3v2.4 frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only; optional
            Bytes-like object containing the text information frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        text_info : minim.media.metadata.ID3v2TextInfoFrame
            Text information frame.
        """
        frame_length = decode_32_bit_synchsafe_int(*stream[4:8])
        text_encoding = cls._TEXT_ENCODINGS[stream[10]]
        text_info, *end = (
            stream[11 : 10 + frame_length].tobytes().split(b"\x00")
        )
        if len(end) != 1 or end[0]:
            raise ValueError("Invalid text information frame data.")

        obj = super()._from_stream_2_4(stream, strict=strict)
        obj._text_info = text_info.decode(encoding=text_encoding)
        obj._text_encoding = text_encoding
        return obj

    @property
    def text_info(self) -> str:
        """
        Text information.
        """
        return self._text_info

    @property
    def text_encoding(self) -> str:
        """
        Text encoding.
        """
        return self._text_encoding

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the ID3v2 frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        stream : bytes
            Bytestream containing the text information frame.
        """
        raise NotImplementedError  # TODO


class ID3v2DateTimeFrame(ID3v2TextInfoFrame):
    """
    Datetime frame.
    """

    _DATETIME_COMPONENTS = "year", "month", "day", "hour", "minute", "second"
    _DATETIME_RE = re.compile(
        r"^(\d{4})(?:-(\d{2})(?:-(\d{2})(?:T(\d{2})(?::(\d{2})(?::(\d{2}))?)?)?)?)?$"
    )
    _STRFTIME_FORMATS = (
        "{:04d}",
        "{:04d}-{:02d}",
        "{:04d}-{:02d}-{:02d}",
        "{:04d}-{:02d}-{:02d}T{:02d}",
        "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}",
        "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}",
    )

    _frame_ids = {}

    __slots__ = tuple(f"_{dt_comp}" for dt_comp in _DATETIME_COMPONENTS)

    def __init__(
        self,
        dt: str | datetime | None = None,
        /,
        *,
        year: int | str | None = None,
        month: int | str | None = None,
        day: int | str | None = None,
        hour: int | str | None = None,
        minute: int | str | None = None,
        second: int | str | None = None,
        text_encoding: str = "utf-16",
        format_flags: ID3v2FrameFormatFlags | None = None,
        status_flags: ID3v2FrameStatusFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        dt : str or datetime.datetime; positional-only; optional
            Release datetime, in ISO-8601 format.

        year : int or str; keyword-only; optional
            Release year.

        month : int or str; keyword-only; optional
            Release month.

        day : int or str; keyword-only; optional
            Release day.

        hour : int or str; keyword-only; optional
            Release hour.

        minute : int or str; keyword-only; optional
            Release minute.

        second : int or str; keyword-only; optional
            Release second.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        format_flags : minim.media.metadata.ID3v2FrameFormatFlags; \
        keyword-only; optional
            Format flags for an ID3v2 frame.

        status_flags : minim.media.metadata.ID3v2FrameStatusFlags; \
        keyword-only; optional
            Status flags for an ID3v2 frame.
        """
        super().__init__(format_flags=format_flags, status_flags=status_flags)

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        self._text_encoding = text_encoding

        if dt is None:
            pass
        else:
            if any(
                v is not None for v in (year, month, day, hour, minute, second)
            ):
                raise ValueError(
                    "Cannot specify both `dt` and individual datetime "
                    "components."
                )

            if isinstance(dt, str):
                self._parse_datetime_string(dt)
            elif isinstance(dt, datetime):
                self._year = dt.year
                self._month = dt.month
                self._day = dt.day
                self._hour = dt.hour
                self._minute = dt.minute
                self._second = dt.second
            else:
                raise TypeError(
                    "When provided, `dt` must be a string in ISO-8601 "
                    "format or a datetime.datetime object."
                )

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2DateTimeFrame:
        """ """
        frame_length = decode_32_bit_synchsafe_int(*stream[4:8])
        text_encoding = cls._TEXT_ENCODINGS[stream[10]]
        dt, *end = stream[11 : 10 + frame_length].tobytes().split(b"\x00")
        if len(end) != 1 or end[0]:
            raise ValueError("Invalid text information frame data.")

        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_4(
            stream, strict=strict
        )
        obj._parse_datetime_string(dt.decode(encoding=text_encoding))
        obj._text_encoding = text_encoding
        return obj

    @staticmethod
    def _get_num_days_in_month(month: int, /, year: int) -> int:
        """ """
        if month in {1, 3, 5, 7, 8, 10, 12}:
            return 31
        elif month in {4, 6, 9, 11}:
            return 30
        elif month == 2:
            if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
                return 29
            else:
                return 28

    def _parse_datetime_string(self, dt: str) -> None:
        """ """
        length = len(dt)
        if length > 19:
            dt = dt[:19]
            length = 19
        dt = dt.upper()

        if match := self._DATETIME_RE.match(dt):
            last_idx = 0
            for dt_comp, value in zip(
                self._DATETIME_COMPONENTS, match.groups()
            ):
                if value is None:
                    break
                setattr(self, f"_{dt_comp}", int(value))
                last_idx += 1

            for dt_comp in self._DATETIME_COMPONENTS[last_idx:]:
                setattr(self, f"_{dt_comp}", None)

            year = self._year
            validate_number("year", year, int, 0)
            month = self._month
            if month is not None:
                validate_number("month", month, int, 1, 12)
            if self._day is not None:
                validate_number(
                    "day",
                    self._day,
                    int,
                    1,
                    self._get_num_days_in_month(month, year=year),
                )
            if self._hour is not None:
                validate_number("hour", self._hour, int, 0, 23)
            if self._minute is not None:
                validate_number("minute", self._minute, int, 0, 59)
            if self._second is not None:
                validate_number("second", self._second, int, 0, 59)
        else:
            raise ValueError(f"Invalid datetime string {dt!r}.")

    @property
    def _text_info(self) -> str:
        """ """
        values = [self._year]
        for attr in self._DATETIME_COMPONENTS[1:]:
            val = getattr(self, f"_{attr}")
            if val is None:
                break
            values.append(val)
        return self._STRFTIME_FORMATS[len(values) - 1].format(*values)


class ID3v2TDRCFrame(ID3v2DateTimeFrame):
    """ """

    _frame_ids = {
        2: [b"TYE", b"TDA", b"TIM"],
        3: [b"TYER", b"TDAT", b"TIME"],
        4: b"TDRC",
    }

    __slots__ = ()


class ID3v2TDRLFrame(ID3v2DateTimeFrame):
    """ """

    _frame_ids = {4: b"TDRL"}

    __slots__ = ()


class ID3v2APICFrame(ID3v2Frame):
    """
    "Attached picture" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.15. Attached picture
       <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.15. Attached picture
       <https://id3.org/id3v2.3.0#Attached_picture>`_.

       `ID3v2.4.0 Native Frames: 4.14. Attached picture
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"PIC", 3: b"APIC", 4: b"APIC"}

    __slots__ = (
        "_picture_type",
        "_mime_type",
        "_picture_data",
        "_text_encoding",
        "_description",
    )

    def __init__(
        self,
        *,
        picture_type: int,
        mime_type: str,
        picture_data: bytes,
        description: str = "",
        text_encoding: str = "utf-16",
        format_flags: ID3v2FrameFormatFlags | None = None,
        status_flags: ID3v2FrameStatusFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        picture_type : int; keyword-only
            Picture type.

        mime_type : str; keyword-only
            MIME type.

            **Examples**: :code:`"image/jpeg"`, :code:`"image/png"`,
            :code:`"-->"`.

        picture_data : bytes; keyword-only
            Picture data.

        description : str; keyword-only; default: :code:`""`
            Picture description.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding for the picture description.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        format_flags : minim.media.metadata.ID3v2FrameFormatFlags; \
        keyword-only; optional
            Format flags.

        status_flags : minim.media.metadata.ID3v2FrameStatusFlags; \
        keyword-only; optional
            Status flags.
        """
        super().__init__(format_flags=format_flags, status_flags=status_flags)

        validate_number("picture_type", picture_type, int, 0, 20)
        self._picture_type = picture_type

        validate_type("mime_type", mime_type, str)
        mime_type = mime_type.lower()
        if not ASCII_CHARS_REGEX.match(mime_type):
            raise ValueError(
                "`mime_type` must contain only ASCII characters 0x20 "
                "(' ') through 0x7D ('}')."
            )
        self._mime_type = mime_type

        validate_type("picture_data", picture_data, bytes)
        self._picture_data = picture_data

        validate_type("description", description, str)
        self._description = description

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        if text_encoding == "iso-8859-1":
            try:
                description.encode(encoding=text_encoding)
                is_utf = False
            except UnicodeEncodeError:
                is_utf = True
            if is_utf:
                raise ValueError(
                    "`picture_description` cannot be encoded using ISO-8859-1."
                )
        self._text_encoding = text_encoding

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2Frame:
        """
        Instantiate an :class:`ID3v2APICFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing the :code:`APIC` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        picture : minim.media.metadata.ID3v2APICFrame
            :code:`APIC` frame.
        """
        obj = super()._from_stream_2_4(stream, strict=strict)
        obj._text_encoding = text_encoding = cls._TEXT_ENCODINGS[stream[10]]
        mime_type, stream = (
            stream[11 : 10 + decode_32_bit_synchsafe_int(*stream[4:8])]
            .tobytes()
            .split(b"\x00", maxsplit=1)
        )
        obj._mime_type = mime_type.decode(encoding=text_encoding)
        obj._picture_type = stream[0]
        description, obj._picture_data = stream[1:].split(b"\x00", maxsplit=1)
        obj._description = description.decode(encoding=text_encoding)
        return obj

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the ID3v2 frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        stream : bytes
            Bytestream containing the "attached picture" frame.
        """
        raise NotImplementedError  # TODO


class ID3v2COMMFrame(ID3v2Frame):
    """
    "Comments" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.11. Comments
       <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.11. Comments
       <https://id3.org/id3v2.3.0#Comments>`_.

       `ID3v2.4.0 Native Frames: 4.10. Comments
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"COM", 3: b"COMM", 4: b"COMM"}

    __slots__ = "_description", "_comment", "_language", "_text_encoding"

    def __init__(
        self,
        description: str,
        comment: str,
        *,
        language: str = "eng",
        text_encoding: str = "utf-16",
        format_flags: ID3v2FrameFormatFlags | None = None,
        status_flags: ID3v2FrameStatusFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        description : str
            Short content description.

        comment : str
            Comment.

        language : str; keyword-only; default: :code:`"eng"`
            ISO 639-2 code for the language.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding for the picture description.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        format_flags : minim.media.metadata.ID3v2FrameFormatFlags; \
        keyword-only; optional
            Format flags.

        status_flags : minim.media.metadata.ID3v2FrameStatusFlags; \
        keyword-only; optional
            Status flags.
        """
        super().__init__(format_flags=format_flags, status_flags=status_flags)

        validate_type("description", description, str)
        self._description = description

        validate_type("comment", comment, str)
        self._comment = comment

        validate_type("language", language, str)
        if len(language) != 3:
            raise ValueError(f"Invalid ISO 639-2 code {language!r}.")
        self._language = language

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        if text_encoding == "iso-8859-1":
            try:
                description.encode(encoding=text_encoding)
                comment.encode(encoding=text_encoding)
                is_utf = False
            except UnicodeEncodeError:
                is_utf = True
            if is_utf:
                raise ValueError(
                    "`description` or `comment` cannot be encoded "
                    "using ISO-8859-1."
                )
        self._text_encoding = text_encoding

    @classmethod
    def _from_stream_2_4(cls, stream: memoryview, /, *, strict: bool = True):
        """
        Instantiate an :class:`ID3v2COMMFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing the :code:`COMM` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        comment : minim.media.metadata.ID3v2COMMFrame
            :code:`COMM` frame.
        """
        frame_length = decode_32_bit_synchsafe_int(*stream[4:8])
        text_encoding = cls._TEXT_ENCODINGS[stream[10]]
        language = stream[11:14].tobytes()
        description, comment, *end = (
            stream[14 : 10 + frame_length].tobytes().split(b"\x00")
        )
        if len(end) != 1 or end[0]:
            raise ValueError("Invalid COMM frame data.")

        obj = super()._from_stream_2_4(stream, strict=strict)
        obj._language = language
        obj._description = description
        obj._comment = comment
        obj._text_encoding = text_encoding
        return obj

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the ID3v2 frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        stream : bytes
            Bytestream containing the "comments" frame.
        """
        raise NotImplementedError  # TODO


# class ID3v2SYLTFrame(ID3v2Frame): ...  # TODO


# class ID3v2USLTFrame(ID3v2Frame): ...  # TODO


class ID3v2TALBFrame(ID3v2TextInfoFrame):
    """
    "Album, movie, or show title" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TALB>`_.

       `ID3v2.4.0 Native Frames: 4.2.1. Identification frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TAL", 3: b"TALB", 4: b"TALB"}

    __slots__ = ()


class ID3v2TBPMFrame(ID3v2TextInfoFrame):
    """
    "Beats per minute (BPM)" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TBPM>`_.

       `ID3v2.4.0 Native Frames: 4.2.3. Derived and subjective
       properties frames <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TBP", 3: b"TBPM", 4: b"TBPM"}

    __slots__ = ()

    def __init__(
        self,
        bpm: int | str,
        /,
        *,
        text_encoding: str = "utf-16",
        format_flags: ID3v2FrameFormatFlags | None = None,
        status_flags: ID3v2FrameStatusFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        bpm : int or str; positional-only
            BPM.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        format_flags : minim.media.metadata.ID3v2FrameFormatFlags; \
        keyword-only; optional
            Format flags.

        status_flags : minim.media.metadata.ID3v2FrameStatusFlags; \
        keyword-only; optional
            Status flags.
        """
        super(ID3v2TextInfoFrame, self).__init__(
            format_flags=format_flags, status_flags=status_flags
        )

        validate_numeric("bpm", bpm, float, 0)
        self._text_info = str(round(float(bpm)))

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        self._text_encoding = text_encoding

    @classmethod
    def _from_stream_2_4(cls, stream: memoryview, /, *, strict=True):
        """
        Instantiate an :class:`ID3v2TBPMFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing the :code:`TBPM` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        bpm : minim.media.metadata.ID3v2TBPMFrame
            :code:`TBPM` frame.
        """
        frame_length = decode_32_bit_synchsafe_int(*stream[4:8])
        text_encoding = cls._TEXT_ENCODINGS[stream[10]]
        bpm, *end = stream[11 : 10 + frame_length].tobytes().split(b"\x00")
        if len(end) != 1 or end[0]:
            raise ValueError("Invalid text information frame data.")

        obj = super()._from_stream_2_4(stream, strict=strict)
        obj._text_info = bpm = bpm.decode(encoding=text_encoding)
        if strict:
            validate_numeric("bpm", bpm, int, 0)
        obj._text_encoding = text_encoding
        return obj


class ID3v2TCMPFrame(ID3v2TextInfoFrame):
    """
    "iTunes compilation flag" frame.

    .. seealso::

       `TCMP - iTunes Compilation Flag (class 4)
       <https://id3.org/iTunes%20Compilation%20Flag>`_.
    """

    _frame_ids = {2: b"TCP", 3: b"TCMP", 4: b"TCMP"}

    __slots__ = ()

    def __init__(
        self,
        is_compilation: bool | int | str,
        /,
        *,
        text_encoding: str = "utf-16",
        format_flags: ID3v2FrameFormatFlags | None = None,
        status_flags: ID3v2FrameStatusFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        is_compilation : bool, int, or str; positional-only
            Whether the recording is part of a compilation.

            **Examples**: :code:`True`, :code:`1`, :code:`"1"`

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        format_flags : minim.media.metadata.ID3v2FrameFormatFlags; \
        keyword-only; optional
            Format flags.

        status_flags : minim.media.metadata.ID3v2FrameStatusFlags; \
        keyword-only; optional
            Status flags.
        """
        super(ID3v2TextInfoFrame, self).__init__(
            format_flags=format_flags, status_flags=status_flags
        )

        if isinstance(is_compilation, bool):
            self._text_info = str(int(is_compilation))
        else:
            validate_numeric("is_compilation", is_compilation, int, 0, 1)
            self._text_info = str(is_compilation)

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        self._text_encoding = text_encoding

    @classmethod
    def _from_stream_2_4(cls, stream: memoryview, /, *, strict=True):
        """
        Instantiate an :class:`ID3v2TCMPFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing the :code:`TCMP` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        is_compilation : minim.media.metadata.ID3v2TCMPFrame
            :code:`TCMP` frame.
        """
        frame_length = decode_32_bit_synchsafe_int(*stream[4:8])
        text_encoding = cls._TEXT_ENCODINGS[stream[10]]
        is_compilation, *end = (
            stream[11 : 10 + frame_length].tobytes().split(b"\x00")
        )
        if len(end) != 1 or end[0]:
            raise ValueError("Invalid text information frame data.")

        obj = super()._from_stream_2_4(stream, strict=strict)
        obj._text_info = is_compilation = is_compilation.decode(
            encoding=text_encoding
        )
        if strict:
            validate_numeric("is_compilation", is_compilation, int, 0, 1)
        obj._text_encoding = text_encoding
        return obj


class ID3v2TCOMFrame(ID3v2TextInfoFrame):
    """
    "Composer" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TCOM>`_.

       `ID3v2.4.0 Native Frames: 4.2.2. Involved persons frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TCM", 3: b"TCOM", 4: b"TCOM"}

    __slots__ = ()


class ID3v2TCONFrame(ID3v2TextInfoFrame):
    """
    "Content type" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TCON>`_.

       `ID3v2.4.0 Native Frames: 4.2.3. Derived and subjective
       properties frames <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TCO", 3: b"TCON", 4: b"TCON"}

    __slots__ = ()


class ID3v2TCOPFrame(ID3v2TextInfoFrame):
    """
    "Copyright message" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TCOP>`_.

       `ID3v2.4.0 Native Frames: 4.2.4. Rights and license frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TCR", 3: b"TCOP", 4: b"TCOP"}

    __slots__ = ()


class ID3v2TIT1Frame(ID3v2TextInfoFrame):
    """
    "Content group description" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TIT2>`_.

       `ID3v2.4.0 Native Frames: 4.2.1. Identification frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TT1", 3: b"TIT1", 4: b"TIT1"}

    __slots__ = ()


class ID3v2TIT2Frame(ID3v2TextInfoFrame):
    """
    "Title, song name, or content description" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TIT2>`_.

       `ID3v2.4.0 Native Frames: 4.2.1. Identification frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TT2", 3: b"TIT2", 4: b"TIT2"}

    __slots__ = ()


class ID3v2TIT3Frame(ID3v2TextInfoFrame):
    """
    "Subtitle or description refinement" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TIT3>`_.

       `ID3v2.4.0 Native Frames: 4.2.1. Identification frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TT3", 3: b"TIT3", 4: b"TIT3"}

    __slots__ = ()


class ID3v2TPE1Frame(ID3v2TextInfoFrame):
    """
    "Lead artist, performer, soloist, or performing group" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TPE1>`_.

       `ID3v2.4.0 Native Frames: 4.2.2. Involved persons frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TP1", 3: b"TPE1", 4: b"TPE1"}

    __slots__ = ()


class ID3v2TPE2Frame(ID3v2TextInfoFrame):
    """
    "Band, orchestra, or accompaniment" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TPE2>`_.

       `ID3v2.4.0 Native Frames: 4.2.2. Involved persons frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TP2", 3: b"TPE2", 4: b"TPE2"}

    __slots__ = ()


class ID3v2TPE3Frame(ID3v2TextInfoFrame):
    """
    "Conductor or performer refinement" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TPE3>`_.

       `ID3v2.4.0 Native Frames: 4.2.2. Involved persons frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TP3", 3: b"TPE3", 4: b"TPE3"}

    __slots__ = ()


class ID3v2TPOSFrame(ID3v2TextInfoFrame):
    """
    "Part of a set" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TPOS>`_.

       `ID3v2.4.0 Native Frames: 4.2.1. Identification frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TPA", 3: b"TPOS", 4: b"TPOS"}

    __slots__ = "_disc_number", "_disc_total"

    def __init__(
        self,
        disc_number: int | str,
        /,
        *,
        disc_total: int | str | None = None,
        text_encoding: str = "utf-16",
        format_flags: ID3v2FrameFormatFlags | None = None,
        status_flags: ID3v2FrameStatusFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        disc_number : int or str; positional-only
            Disc number.

        disc_total : int or str; keyword-only; optional
            Total number of discs.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        format_flags : minim.media.metadata.ID3v2FrameFormatFlags; \
        keyword-only; optional
            Format flags.

        status_flags : minim.media.metadata.ID3v2FrameStatusFlags; \
        keyword-only; optional
            Status flags.
        """
        super(ID3v2TextInfoFrame, self).__init__(
            format_flags=format_flags, status_flags=status_flags
        )

        validate_numeric("disc_number", disc_number, int, 1)
        self.disc_number = str(disc_number)

        if disc_total is not None:
            validate_numeric("disc_total", disc_total, int, 1)
            disc_total = int(disc_total)
        self._disc_total = disc_total

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        self._text_encoding = text_encoding

    @property
    def _text_info(self) -> str:
        """
        Text information.
        """
        if self._disc_total is None:
            return str(self._disc_number)
        return f"{self._disc_number}/{self._disc_total}"

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TPOSFrame:
        """
        Instantiate an :class:`ID3v2TPOSFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only; optional
            Bytes-like object containing the :code:`TPOS` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        disc_number : minim.media.metadata.ID3v2TPOSFrame
            :code:`TPOS` frame.
        """
        frame_length = decode_32_bit_synchsafe_int(*stream[4:8])
        text_encoding = cls._TEXT_ENCODINGS[stream[10]]
        text_info, *end = (
            stream[11 : 10 + frame_length].tobytes().split(b"\x00")
        )
        if len(end) != 1 or end[0]:
            raise ValueError("Invalid text information frame data.")

        disc_number, *disc_total = text_info.split(b"/", maxsplit=1)
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_4(
            stream, strict=strict
        )
        obj._disc_number = int(disc_number)
        obj._disc_total = int(disc_total[0]) if disc_total else None
        obj._text_encoding = text_encoding
        return obj

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the ID3v2 frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        stream : bytes
            Bytestream containing the ID3v2 frame.
        """
        raise NotImplementedError  # TODO


class ID3v2TPUBFrame(ID3v2TextInfoFrame):
    """
    "Publisher" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TPE1>`_.

       `ID3v2.4.0 Native Frames: 4.2.2. Involved persons frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TPB", 3: b"TPUB", 4: b"TPUB"}

    __slots__ = ()


class ID3v2TRCKFrame(ID3v2TextInfoFrame):
    """
    "Track number and position in set" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TRCK>`_.

       `ID3v2.4.0 Native Frames: 4.2.1. Identification frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TRK", 3: b"TRCK", 4: b"TRCK"}

    __slots__ = "_track_number", "_track_total"

    def __init__(
        self,
        track_number: int | str,
        /,
        *,
        track_total: int | str | None = None,
        text_encoding: str = "utf-16",
        format_flags: ID3v2FrameFormatFlags | None = None,
        status_flags: ID3v2FrameStatusFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        track_number : int or str; positional-only
            Track number.

        track_total : int or str; keyword-only; optional
            Total number of tracks.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        format_flags : minim.media.metadata.ID3v2FrameFormatFlags; \
        keyword-only; optional
            Format flags.

        status_flags : minim.media.metadata.ID3v2FrameStatusFlags; \
        keyword-only; optional
            Status flags.
        """
        super(ID3v2TextInfoFrame, self).__init__(
            format_flags=format_flags, status_flags=status_flags
        )

        validate_numeric("track_number", track_number, int, 1)
        self._track_number = str(track_number)

        if track_total is not None:
            validate_numeric("track_total", track_total, int, 1)
            track_total = int(track_total)
        self._track_total = track_total

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        self._text_encoding = text_encoding

    @property
    def _text_info(self) -> str:
        """
        Text information.
        """
        if self._track_total is None:
            return str(self._track_number)
        return f"{self._track_number}/{self._track_total}"

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TRCKFrame:
        """
        Instantiate an :class:`ID3v2TRCKFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only; optional
            Bytes-like object containing the :code:`TRCK` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        track_number : minim.media.metadata.ID3v2TRCKFrame
            :code:`TRCK` frame.
        """
        frame_length = decode_32_bit_synchsafe_int(*stream[4:8])
        text_encoding = cls._TEXT_ENCODINGS[stream[10]]
        text_info, *end = (
            stream[11 : 10 + frame_length].tobytes().split(b"\x00")
        )
        if len(end) != 1 or end[0]:
            raise ValueError("Invalid text information frame data.")

        track_number, *track_total = text_info.split(b"/", maxsplit=1)
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_4(
            stream, strict=strict
        )
        obj._track_number = int(track_number)
        obj._track_total = int(track_total[0]) if track_total else None
        obj._text_encoding = text_encoding
        return obj

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the ID3v2 frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        stream : bytes
            Bytestream containing the ID3v2 frame.
        """
        raise NotImplementedError  # TODO


class ID3v2TSRCFrame(ID3v2TextInfoFrame):
    """
    "ISRC (International Standard Recording Code)" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TSRC>`_.

       `ID3v2.4.0 Native Frames: 4.2.1. Identification frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TRC", 3: b"TSRC", 4: b"TSRC"}

    __slots__ = ()

    @classmethod
    def _from_stream_2_4(cls, stream: memoryview, /, *, strict: bool = True):
        """
        Instantiate an :code:`ID3v2TSRCFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing the :code:`TSRC` frame.

        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        isrc : minim.media.metadata.ID3v2TSRCFrame
            :code:`TSRC` frame.
        """
        frame_length = decode_32_bit_synchsafe_int(*stream[4:8])
        text_encoding = cls._TEXT_ENCODINGS[stream[10]]
        text_info, *end = (
            stream[11 : 10 + frame_length].tobytes().split(b"\x00")
        )
        if len(end) != 1 or end[0]:
            raise ValueError("Invalid ISRC frame data.")

        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_4(
            stream, strict=strict
        )
        obj._text_info = prepare_isrc(text_info.decode(encoding=text_encoding))
        obj._text_encoding = text_encoding
        return obj


class ID3v2TSSEFrame(ID3v2TextInfoFrame):
    """
    "Software, hardware, and settings used for encoding" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TSSE>`_.

       `ID3v2.4.0 Native Frames: 4.2.2. Involved persons frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TSS", 3: b"TSSE", 4: b"TSSE"}

    __slots__ = ()


class ID3v2TXXXFrame(ID3v2TextInfoFrame):
    """
    "User-defined text information" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.2. User defined text
       information frame <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.2. User defined text
       information frame <https://id3.org/id3v2.3.0
       #User_defined_text_information_frame>`_.

       `ID3v2.4.0 Native Frames: 4.2.6. User defined text information
       frame <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids = {2: b"TXX", 3: b"TXXX", 4: b"TXXX"}

    __slots__ = ("_description",)

    def __init__(
        self,
        description: str,
        value: str,
        /,
        *,
        text_encoding: str = "utf-16",
        format_flags: ID3v2FrameFormatFlags | None = None,
        status_flags: ID3v2FrameStatusFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        description : str; positional-only
            Description.

        value : str; positional-only
            Value.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        format_flags : minim.media.metadata.ID3v2FrameFormatFlags; \
        keyword-only; optional
            Format flags.

        status_flags : minim.media.metadata.ID3v2FrameStatusFlags; \
        keyword-only; optional
            Status flags.
        """
        super(ID3v2TextInfoFrame, self).__init__(
            format_flags=format_flags, status_flags=status_flags
        )

        validate_type("description", description, str)
        self._description = description

        validate_type("value", value, str)
        self._text_info = value

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        if text_encoding == "iso-8859-1":
            try:
                description.encode(encoding=text_encoding)
                value.encode(encoding=text_encoding)
                is_utf = False
            except UnicodeEncodeError:
                is_utf = True
            if is_utf:
                raise ValueError(
                    "`description` or `value` cannot be encoded using "
                    "ISO-8859-1."
                )
        self._text_encoding = text_encoding

    @classmethod
    def _from_stream_2_4(
        cls, stream: BytesLike, /, *, strict: bool = True
    ) -> ID3v2TXXXFrame:
        """
        Instantiate an :class:`ID3v2TXXXFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing the :code:`TXXX` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        text_info : minim.media.metadata.ID3v2TXXXFrame
            :code:`TXXX` frame.
        """
        frame_length = decode_32_bit_synchsafe_int(*stream[4:8])
        text_encoding = cls._TEXT_ENCODINGS[stream[10]]
        description, value, *end = (
            stream[11 : 10 + frame_length].tobytes().split(b"\x00")
        )
        if len(end) != 1 or end[0]:
            raise ValueError("Invalid TXXX frame data.")

        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_4(
            stream, strict=strict
        )
        obj._description = description.decode(encoding=text_encoding)
        obj._text_info = value.decode(encoding=text_encoding)
        obj._text_encoding = text_encoding
        return obj

    @property
    def description(self) -> str:
        """
        Description.
        """
        return self._description

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the ID3v2 frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        stream : bytes
            Bytestream containing the "user-defined text information"
            frame.
        """
        raise NotImplementedError  # TODO


class UnknownID3v2Frame(ID3v2Frame):
    """
    Unknown ID3v2 frame.
    """

    _frame_ids = {}

    __slots__ = "_frame_id", "_frame_data"

    def __init__(
        self, frame_id: bytes | bytearray, frame_data: bytes | bytearray
    ) -> None:
        """
        Parameters
        ----------
        frame_id : bytes or bytearray
            ID3v2 frame ID.

        frame_data : bytes or bytearray
            ID3v2 frame data.
        """
        validate_type("frame_id", frame_id, bytes | bytearray)
        if not 3 <= len(frame_id) <= 4:
            raise ValueError(
                "`frame_id` must be three- or four-characters long."
            )
        set_obj_attr(self, "_frame_id", bytes(frame_id))
        validate_type("frame_data", frame_data, bytes | bytearray)
        set_obj_attr(self, "_frame_data", bytes(frame_data))

    def __setattr__(self, name: str, value: Any) -> None:
        raise FrozenInstanceError(f"cannot assign to field {name!r}")

    def __delattr__(self, name: str) -> None:
        raise FrozenInstanceError(f"cannot delete field {name!r}")

    @classmethod
    def _from_stream_2_4(
        cls, stream: BytesLike, /, *, strict: bool = True
    ) -> UnknownID3v2Frame:
        """
        Instantiate a :class:`UnknownID3v2Frame` object from a
        bytes-like object.

        Parameters
        ----------
        stream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing the ID3v2 frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        frame : minim.media.flac.UnknownID3v2Frame
            ID3v2 frame.
        """
        frame_id = stream[:4].tobytes()
        frame_length = decode_32_bit_synchsafe_int(*stream[4:8])
        frame_data = stream[10 : 10 + frame_length].tobytes()
        if frame_data[-1]:
            raise ValueError(
                "ID3v2.4 frame does not end with a null character."
            )

        obj = super()._from_stream_2_4(stream, strict=strict)
        obj._frame_id = frame_id
        obj._frame_data = frame_data
        return obj

    @property
    def frame_id(self) -> bytes:
        """
        Frame ID.
        """
        return self._frame_id

    @property
    def frame_data(self) -> bytes:
        """
        Raw frame data.
        """
        return self._frame_data

    def get_frame_id(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Get the ID3v2 frame ID.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        frame_id : bytes
            ID3v2 frame ID.
        """
        frame_id = self._frame_id
        if self._normalize_tag_version(tag_version) == (2, 2, 0):
            if len(frame_id) != 3:
                raise ValueError(
                    f"Frame ID {frame_id!r} is incompatible with "
                    f"ID3v2 tag version {tag_version!r}."
                )
            return frame_id

        if len(frame_id) != 4:
            raise ValueError(
                f"Frame ID {frame_id!r} is incompatible with "
                f"ID3v2 tag version {tag_version!r}."
            )
        return frame_id

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the ID3v2 frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        stream : bytes
            Bytestream containing the ID3v2 frame.
        """
        raise NotImplementedError  # TODO


class ID3v2Padding:
    """
    ID3v2 padding.
    """

    __slots__ = ("_length",)

    def __init__(self, length: int, /) -> None:
        """
        Parameters
        ----------
        length : int; positional-only
            Padding length in bytes.
        """
        self.length = length

    @property
    def length(self) -> int:
        """
        Padding length in bytes.
        """
        return self._length

    @length.setter
    def length(self, length: int, /) -> None:
        validate_number("length", length, int, 0)
        self._length = length

    def adjust_length(self, change: int, /) -> None:
        """
        Adjust the padding length.

        Parameters
        ----------
        change : int; positional-only
            Change to the padding length in bytes.
        """
        self.length += change

    def set_length(self, block_length: int, /) -> None:
        """
        Resize padding.

        Parameters
        ----------
        length : int; positional-only
            New padding length in bytes.
        """
        self.length = block_length

    @classmethod
    def from_stream(
        cls, stream: BytesLike, /, *, strict: bool = True
    ) -> ID3v2Padding:
        """
        Instantiate an :class:`ID3v2Padding` object from a bytes-like
        object.

        Parameters
        ----------
        stream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing padding.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        padding : minim.media.metadata.ID3v2Padding
            Padding.
        """
        stream = as_buffer(stream)
        if strict and any(stream):
            raise ValueError("Non-zero bits found in ID3v2 padding bytes.")

        obj = cls.__new__(cls)
        obj._length = len(stream)
        return obj

    def serialize(self) -> bytes:
        """
        Serialize the padding to a bytestream.

        Returns
        -------
        stream : bytes
            Bytestream containing the padding bytes.
        """
        return self._length * b"\x00"
