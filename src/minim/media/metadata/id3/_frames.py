from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import FrozenInstanceError, dataclass
import struct
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
    _REGISTER = True
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
        if not cls._REGISTER:
            return

        for tag_version in TAG_VERSIONS:
            if frame_id := cls.get_frame_id(tag_version):
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
        return cls._REGISTRY.get(frame_id)

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
    @abstractmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        ...

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


class ID3v2APICFrame(ID3v2Frame):
    """
    Attached picture frame.

    .. seealso::

       `ID3v2.3.0: 4.15. Attached picture
       <https://id3.org/id3v2.3.0#Attached_picture>`_.

       `ID3v2.4.0 Native Frames: 4.14. Attached picture
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _STRUCT_II = struct.Struct(">II")
    _STRUCT_IIIII = struct.Struct(">5I")

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
        """ """
        raise NotImplementedError  # TODO

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"PIC"
        return b"APIC"

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the :code:`APIC` frame to a bytestream.

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
            Bytestream containing :code:`APIC` frame data.
        """
        raise NotImplementedError  # TODO


class ID3v2COMMFrame(ID3v2Frame):
    """
    Comment frame.

    .. seealso::

       `ID3v2.3.0: 4.11. Comments
       <https://id3.org/id3v2.3.0#Comments>`_.

       `ID3v2.4.0 Native Frames: 4.10. Comments
       <https://id3.org/id3v2.4.0-frames>`_.
    """

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

    @classmethod
    @abstractmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"COM"
        return b"COMM"

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the comment frame to a bytestream.

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
            Bytestream containing the comment frame.
        """
        raise NotImplementedError  # TODO


# class ID3v2TPOSFrame(ID3v2Frame): ...  # TODO


# class ID3v2TRCKFrame(ID3v2Frame): ...  # TODO


# class ID3v2SYLTFrame(ID3v2Frame): ...  # TODO


# class ID3v2USLTFrame(ID3v2Frame): ...  # TODO


class ID3v2TextInfoFrame(ID3v2Frame):
    """
    Text information frame.

    .. seealso::

       `ID3v2.3.0: 4.2. Text information frames
       <https://id3.org/id3v2.3.0#Text_information_frames>`_.

       `ID3v2.4.0 Native Frames: 4.2. Text information frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

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
        Serialize the text information frame to a bytestream.

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


class ID3v2TALBFrame(ID3v2TextInfoFrame):
    """
    Album, movie, or show title frame.

    .. seealso::

       `ID3v2.3.0: 4.2.1. Text information frames - details
       <https://id3.org/id3v2.3.0#TALB>`_.

       `ID3v2.4.0 Native Frames: 4.2.1. Identification frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TAL"
        return b"TALB"


class ID3v2TBPMFrame(ID3v2TextInfoFrame):
    """
    Beats per minute (BPM) frame.

    .. seealso::

       `ID3v2.3.0: 4.2.1. Text information frames - details
       <https://id3.org/id3v2.3.0#TBPM>`_.

       `ID3v2.4.0 Native Frames: 4.2.3. Derived and subjective
       properties frames <https://id3.org/id3v2.4.0-frames>`_.
    """

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

        validate_numeric("bpm", bpm, int, 0)
        self._text_info = str(bpm)

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

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TBP"
        return b"TBPM"


class ID3v2TCMPFrame(ID3v2TextInfoFrame):
    """
    iTunes compilation flag frame.

    .. seealso::

       `TCMP - iTunes Compilation Flag (class 4)
       <https://id3.org/iTunes%20Compilation%20Flag>`_.
    """

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

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TCP"
        return b"TCMP"


class ID3v2TCOMFrame(ID3v2TextInfoFrame):
    """
    Composer frame.

    .. seealso::

       `ID3v2.3.0: 4.2.1. Text information frames - details
       <https://id3.org/id3v2.3.0#TCOM>`_.

       `ID3v2.4.0 Native Frames: 4.2.2. Involved persons frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TCM"
        return b"TCOM"


class ID3v2TCONFrame(ID3v2TextInfoFrame):
    """
    Content type frame.

    .. seealso::

       `ID3v2.3.0: 4.2.1. Text information frames - details
       <https://id3.org/id3v2.3.0#TCON>`_.

       `ID3v2.4.0 Native Frames: 4.2.3. Derived and subjective
       properties frames <https://id3.org/id3v2.4.0-frames>`_.
    """

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TCO"
        return b"TCON"


class ID3v2TCOPFrame(ID3v2TextInfoFrame):
    """
    Copyright message frame.

    .. seealso::

       `ID3v2.3.0: 4.2.1. Text information frames - details
       <https://id3.org/id3v2.3.0#TCOP>`_.

       `ID3v2.4.0 Native Frames: 4.2.4. Rights and license frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TCR"
        return b"TCOP"


class ID3v2TIT1Frame(ID3v2TextInfoFrame):
    """
    Content group description frame.

    .. seealso::

       `ID3v2.3.0: 4.2.1. Text information frames - details
       <https://id3.org/id3v2.3.0#TIT2>`_.

       `ID3v2.4.0 Native Frames: 4.2.1. Identification frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TT1"
        return b"TIT1"


class ID3v2TIT2Frame(ID3v2TextInfoFrame):
    """
    Title, song name, or content description frame.

    .. seealso::

       `ID3v2.3.0: 4.2.1. Text information frames - details
       <https://id3.org/id3v2.3.0#TIT2>`_.

       `ID3v2.4.0 Native Frames: 4.2.1. Identification frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TT2"
        return b"TIT2"


class ID3v2TIT3Frame(ID3v2TextInfoFrame):
    """
    Subtitle or description refinement frame.

    .. seealso::

       `ID3v2.3.0: 4.2.1. Text information frames - details
       <https://id3.org/id3v2.3.0#TIT3>`_.

       `ID3v2.4.0 Native Frames: 4.2.1. Identification frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TT3"
        return b"TIT3"


class ID3v2TPE1Frame(ID3v2TextInfoFrame):
    """
    Lead artist, performer, soloist, or performing group frame.

    .. seealso::

       `ID3v2.3.0: 4.2.1. Text information frames - details
       <https://id3.org/id3v2.3.0#TPE1>`_.

       `ID3v2.4.0 Native Frames: 4.2.2. Involved persons frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TP1"
        return b"TPE1"


class ID3v2TPE2Frame(ID3v2TextInfoFrame):
    """
    Band, orchestra, or accompaniment frame.

    .. seealso::

       `ID3v2.3.0: 4.2.1. Text information frames - details
       <https://id3.org/id3v2.3.0#TPE2>`_.

       `ID3v2.4.0 Native Frames: 4.2.2. Involved persons frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TP2"
        return b"TPE2"


class ID3v2TPUBFrame(ID3v2TextInfoFrame):
    """
    Publisher frame.

    .. seealso::

       `ID3v2.3.0: 4.2.1. Text information frames - details
       <https://id3.org/id3v2.3.0#TPE1>`_.

       `ID3v2.4.0 Native Frames: 4.2.2. Involved persons frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TPB"
        return b"TPUB"


class ID3v2TSRCFrame(ID3v2TextInfoFrame):
    """
    ISRC (International Standard Recording Code) frame.

    .. seealso::

       `ID3v2.3.0: 4.2.1. Text information frames - details
       <https://id3.org/id3v2.3.0#TSRC>`_.

       `ID3v2.4.0 Native Frames: 4.2.1. Identification frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

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

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TRC"
        return b"TSRC"


class ID3v2TSSEFrame(ID3v2TextInfoFrame):
    """
    Software, hardware, and settings used for encoding frame.

    .. seealso::

       `ID3v2.3.0: 4.2.1. Text information frames - details
       <https://id3.org/id3v2.3.0#TSSE>`_.

       `ID3v2.4.0 Native Frames: 4.2.2. Involved persons frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TSS"
        return b"TSSE"


class ID3v2TXXXFrame(ID3v2TextInfoFrame):
    """
    User-defined text information frame.

    .. seealso::

       `ID3v2.3.0: 4.2.2. User defined text information frame
       <https://id3.org/id3v2.3.0#User_defined_text_information_frame>`_.

       `ID3v2.4.0 Native Frames: 4.2.6. User defined text information
       frame <https://id3.org/id3v2.4.0-frames>`_.
    """

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

    @classmethod
    def get_frame_id(cls, tag_version: str | tuple[int, int, int]) -> bytes:
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
        if cls._normalize_tag_version(tag_version) == (2, 2, 0):
            return b"TXX"
        return b"TXXX"

    @property
    def description(self) -> str:
        """
        Description.
        """
        return self._description

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the :code:`TXXX` frame to a bytestream.

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
            Bytestream containing the :code:`TXXX` frame.
        """
        raise NotImplementedError  # TODO


class UnknownID3v2Frame(ID3v2Frame):
    """
    Unknown ID3v2 frame.
    """

    _REGISTER = False

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
