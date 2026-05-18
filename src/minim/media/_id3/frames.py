from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import struct
from typing import TYPE_CHECKING

from ..._utility import (
    ASCII_CHARS_REGEX,
    decode_32_bit_synchsafe_int,
    join_values,
    set_obj_attr,
    validate_number,
    validate_numeric,
    validate_type,
)
from .._shared import as_buffer

if TYPE_CHECKING:
    from typing import Any

    from ..._types import BytesLike


@dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class ID3v2FrameStatusFlags:
    """
    Status flags for an ID3v2 frame.
    """

    discard_on_tag_alter: bool = False
    discard_on_file_alter: bool = False
    is_read_only: bool = False

    def __post_init__(self) -> None:
        validate_type("discard_on_tag_alter", self.discard_on_tag_alter, bool)
        validate_type(
            "discard_on_file_alter", self.discard_on_file_alter, bool
        )
        validate_type("is_read_only", self.is_read_only, bool)

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
        Instantiate a :class:`ID3v2FrameStatusFlags` object from a byte.

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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))

        obj = cls.__new__(cls)
        match tag_version:
            case (2, 2, 0):
                if strict and byte_:
                    raise ValueError(
                        "Reserved bits set in ID3v2 frame status flags byte."
                    )
                set_obj_attr(obj, "discard_on_tag_alter", False)
                set_obj_attr(obj, "discard_on_file_alter", False)
                set_obj_attr(obj, "is_read_only", False)
            case (2, 3, 0):
                if strict and byte_ & 0x1F:
                    raise ValueError(
                        "Reserved bits set in ID3v2 frame status flags byte."
                    )
                set_obj_attr(obj, "discard_on_tag_alter", bool(byte_ & 0x80))
                set_obj_attr(obj, "discard_on_file_alter", bool(byte_ & 0x40))
                set_obj_attr(obj, "is_read_only", bool(byte_ & 0x20))
            case (2, 4, 0):
                if strict and byte_ & 0x8F:
                    raise ValueError(
                        "Reserved bits set in ID3v2 frame status flags byte."
                    )
                set_obj_attr(obj, "discard_on_tag_alter", bool(byte_ & 0x40))
                set_obj_attr(obj, "discard_on_file_alter", bool(byte_ & 0x20))
                set_obj_attr(obj, "is_read_only", bool(byte_ & 0x10))
            case _:
                raise ValueError(f"Invalid ID3v2 tag version {tag_version!r}.")

        return obj


@dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class ID3v2FrameFormatFlags:
    """
    Format flags for an ID3v2 frame.
    """

    has_grouping: bool = False
    is_compressed: bool = False
    is_encrypted: bool = False
    is_unsynchronized: bool = False
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
    def from_byte(
        cls,
        byte_: int,
        /,
        tag_version: str | tuple[int, int, int],
        *,
        strict: bool = True,
    ) -> ID3v2FrameFormatFlags:
        """
        Instantiate a :class:`ID3v2FrameFormatFlags` object from a byte.

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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))

        obj = cls.__new__(cls)
        match tag_version:
            case (2, 2, 0):
                if strict and byte_:
                    raise ValueError(
                        "Reserved bits set in ID3v2 frame status flags byte."
                    )
                set_obj_attr(obj, "has_grouping", False)
                set_obj_attr(obj, "is_compressed", False)
                set_obj_attr(obj, "is_encrypted", False)
                set_obj_attr(obj, "is_unsynchronized", False)
                set_obj_attr(obj, "has_data_length_indicator", False)
            case (2, 3, 0):
                if strict and byte_ & 0x1F:
                    raise ValueError(
                        "Reserved bits set in ID3v2 frame status flags byte."
                    )
                set_obj_attr(obj, "is_compressed", bool(byte_ & 0x80))
                set_obj_attr(obj, "is_encrypted", bool(byte_ & 0x40))
                set_obj_attr(obj, "has_grouping", bool(byte_ & 0x20))
                set_obj_attr(obj, "is_unsynchronized", False)
                set_obj_attr(obj, "has_data_length_indicator", False)
            case (2, 4, 0):
                if strict and byte_ & 0x70:
                    raise ValueError(
                        "Reserved bits set in ID3v2 frame status flags byte."
                    )
                set_obj_attr(obj, "has_grouping", bool(byte_ & 0x40))
                set_obj_attr(obj, "is_compressed", bool(byte_ & 0x08))
                set_obj_attr(obj, "is_encrypted", bool(byte_ & 0x04))
                set_obj_attr(obj, "is_unsynchronized", bool(byte_ & 0x02))
                set_obj_attr(
                    obj, "has_data_length_indicator", bool(byte_ & 0x01)
                )
            case _:
                raise ValueError(f"Invalid ID3v2 tag version {tag_version!r}.")

        return obj


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

        for tag_version in ((2, 2, 0), (2, 3, 0), (2, 4, 0)):
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
    def from_stream(
        cls,
        stream: BytesLike,
        /,
        tag_version: str | tuple[int, int, int],
        *,
        strict: bool = True,
    ) -> ID3v2Frame:
        """ 
        Instantiate a :class:`ID3v2Frame` object from a bytes-like 
        object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
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
        match tag_version:
            case (2, 2, 0):
                raise NotImplementedError  # TODO
            case (2, 3, 0):
                raise NotImplementedError  # TODO
            case (2, 4, 0):
                expected_frame_id = cls.get_frame_id(tag_version)
                if stream[:4] != expected_frame_id:
                    raise ValueError(
                        "`bytestream` does not contain a "
                        f"{expected_frame_id} frame."
                    )

                format_flags = ID3v2FrameFormatFlags.from_byte(
                    stream[8], tag_version=tag_version, strict=strict
                )
                status_flags = ID3v2FrameStatusFlags.from_byte(
                    stream[9], tag_version=tag_version, strict=strict
                )
            case _:
                raise ValueError(f"Invalid ID3v2 tag version {tag_version!r}.")

        obj = cls.__new__(cls)
        obj._format_flags = format_flags
        obj._status_flags = status_flags
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
        bytestream : bytes
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
    def from_stream(
        cls,
        stream: BytesLike,
        /,
        tag_version: str | tuple[int, int, int],
        *,
        strict: bool = True,
    ) -> ID3v2APICFrame:
        """ 
        Instantiate an :class:`ID3v2APICFrame` object from a bytes-like 
        object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing the :code:`APIC` frame.

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
        attached_picture : minim.media.metadata.APICFrame
            :code:`APIC` frame.
        """
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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))
        if tag_version == (2, 2, 0):
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
        bytestream : bytes
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

    __slots__ = ("_description", "_comment", "_text_encoding")

    def __init__(
        self,
        description: str,
        comment: str,
        *,
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
    def from_stream(
        cls,
        stream: BytesLike,
        /,
        tag_version: str | tuple[int, int, int],
        *,
        strict: bool = True,
    ) -> ID3v2COMMFrame:
        """ """
        stream = as_buffer(stream)
        obj = super().from_stream(
            stream, tag_version=tag_version, strict=strict
        )

        ...  # TODO

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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))
        if tag_version == (2, 2, 0):
            return b"COM"
        return b"COMM"


# class ID3v2TPOSFrame(ID3v2Frame): ...  # TODO


# class ID3v2TRCKFrame(ID3v2Frame): ...  # TODO


class ID3v2TextInfoFrame(ID3v2Frame):
    """
    Text information frame.

    .. seealso::

       `ID3v2.3.0: 4.2. Text information frames
       <https://id3.org/id3v2.3.0#Text_information_frames>`_.

       `ID3v2.4.0 Native Frames: 4.2. Text information frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    __slots__ = ("_text_info", "_text_encoding")

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
    def from_stream(
        cls,
        stream: BytesLike,
        /,
        tag_version: str | tuple[int, int, int],
        *,
        strict: bool = True,
    ) -> ID3v2TextInfoFrame:
        """ 
        Instantiate an ID3v2 text information frame object from a 
        bytes-like object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing the text information frame.

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
        text_info : minim.media.metadata.ID3v2TextInfoFrame
            Text information frame.
        """
        stream = as_buffer(stream)
        obj = super().from_stream(
            stream, tag_version=tag_version, strict=strict
        )

        match tag_version:
            case (2, 2, 0):
                raise NotImplementedError  # TODO
            case (2, 3, 0):
                raise NotImplementedError  # TODO
            case (2, 4, 0):
                frame_length = decode_32_bit_synchsafe_int(*stream[4:8])
                text_encoding = cls._TEXT_ENCODINGS[stream[10]]
                text_info, *end = (
                    stream[11 : 10 + frame_length].tobytes().split(b"\x00")
                )
                if len(end) != 1 or end[0]:
                    raise ValueError("Invalid text information frame data.")
            case _:
                raise ValueError(f"Invalid ID3v2 tag version {tag_version!r}.")

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
        bytestream : bytes
            Bytestream containing text information frame.
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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))
        if tag_version == (2, 2, 0):
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
    def from_stream(
        cls,
        stream: BytesLike,
        /,
        tag_version: str | tuple[int, int, int],
        *,
        strict: bool = True,
    ) -> ID3v2TBPMFrame:
        """ 
        Instantiate a :class:`ID3v2TBPMFrame` frame object from a 
        bytes-like object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing the text information frame.

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
        bpm : minim.media.metadata.ID3v2TBPMFrame
            BPM frame.
        """
        stream = as_buffer(stream)
        obj = super().from_stream(
            stream, tag_version=tag_version, strict=strict
        )

        match tag_version:
            case (2, 2, 0):
                raise NotImplementedError  # TODO
            case (2, 3, 0):
                raise NotImplementedError  # TODO
            case (2, 4, 0):
                frame_length = decode_32_bit_synchsafe_int(*stream[4:8])
                text_encoding = cls._TEXT_ENCODINGS[stream[10]]
                bpm, *end = (
                    stream[11 : 10 + frame_length].tobytes().split(b"\x00")
                )
                if len(end) != 1 or end[0]:
                    raise ValueError("Invalid text information frame data.")
            case _:
                raise ValueError(f"Invalid ID3v2 tag version {tag_version!r}.")

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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))
        if tag_version == (2, 2, 0):
            return b"TBP"
        return b"TBPM"


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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))
        if tag_version == (2, 2, 0):
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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))
        if tag_version == (2, 2, 0):
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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))
        if tag_version == (2, 2, 0):
            return b"TCR"
        return b"TCOP"


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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))
        if tag_version == (2, 2, 0):
            return b"TT2"
        return b"TIT2"


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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))
        if tag_version == (2, 2, 0):
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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))
        if tag_version == (2, 2, 0):
            return b"TP2"
        return b"TPE2"


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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))
        if tag_version == (2, 2, 0):
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
    def from_stream(
        cls,
        stream: BytesLike,
        /,
        tag_version: str | tuple[int, int, int],
        *,
        strict: bool = True,
    ) -> ID3v2TXXXFrame:
        """ 
        Instantiate an :class:`ID3v2TXXXFrame` object from a bytes-like 
        object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing the :code:`TXXX` frame.

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
        text_info : minim.media.metadata.ID3v2TXXXFrame
            :code:`TXXX` frame.
        """
        stream = as_buffer(stream)
        obj = super(ID3v2TextInfoFrame, cls).from_stream(
            stream, tag_version=tag_version, strict=strict
        )

        match tag_version:
            case (2, 2, 0):
                raise NotImplementedError  # TODO
            case (2, 3, 0):
                raise NotImplementedError  # TODO
            case (2, 4, 0):
                frame_length = decode_32_bit_synchsafe_int(*stream[4:8])
                text_encoding = cls._TEXT_ENCODINGS[stream[10]]
                description, value, *end = (
                    stream[11 : 10 + frame_length].tobytes().split(b"\x00")
                )
                if len(end) != 1 or end[0]:
                    raise ValueError("Invalid TXXX frame data.")
            case _:
                raise ValueError(f"Invalid ID3v2 tag version {tag_version!r}.")

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
        if isinstance(tag_version, str):
            tag_version = tuple(int(v) for v in tag_version.split("."))
        if tag_version == (2, 2, 0):
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
        bytestream : bytes
            Bytestream containing the :code:`TXXX` frame.
        """
        raise NotImplementedError  # TODO
