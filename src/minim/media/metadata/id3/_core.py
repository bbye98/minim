from __future__ import annotations

import struct
import zlib
from collections import defaultdict
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar

from ...._types import ORDERED_COLLECTION_TYPES
from ...._utility import (
    as_buffer,
    join_values,
    validate_iso_8859_1_string,
    validate_number,
    validate_numeric,
    validate_type,
)
from ..._shared import NULPadding
from .._shared import AudioTags
from ._frames import (
    EncryptedID3v2Frame,
    ID3v2DateTimeFrame,
    ID3v2Frame,
    UnknownID3v2Frame,
)
from ._shared import (
    ID3V1_GENRES,
    ID3V2_TAG_VERSIONS,
    UNSYNCHRONIZATION_RE,
    decode_synchsafe_int,
    encode_synchsafe_int,
    normalize_id3v1_tag_version,
    normalize_id3v2_tag_version,
)

if TYPE_CHECKING:
    from typing import Any, Self

    from ...._types import BytesLike, OrderedCollection
    from ._frames import *


class ID3v1:
    """
    ID3v1 metadata container.

    .. seealso::

       `What is ID3 (v1)? <https://id3.org/ID3v1>`_
    """

    _STRUCT_1_0: ClassVar[struct.Struct] = struct.Struct("3s30s30s30s4s30sB")
    _STRUCT_1_1: ClassVar[struct.Struct] = struct.Struct("3s30s30s30s4s28sBBB")

    __slots__ = (
        "_album",
        "_artist",
        "_comment",
        "_genre",
        "_title",
        "_track_number",
        "_year",
    )

    def __init__(
        self,
        *,
        title: str | None = None,
        artist: str | None = None,
        album: str | None = None,
        year: int | str | None = None,
        comment: str | None = None,
        track_number: int | None = None,
        genre: int | str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        title : str; keyword-only; optional
            Title of the recording.

        artist : str; keyword-only; optional
            Main artists of the recording (e.g., the performing band or
            singers in popular music, the composers for classical music,
            or the authors of the original text in audiobooks).

        album : str; keyword-only; optional
            Title of the album or collection.

        year : int or str; keyword-only; optional
            Recording or release year.

        comment : str; keyword-only; optional
            Free-form comment.

        track_number : int; keyword-only; optional
            Track number within the album or collection.

        genre : int or str; keyword-only; optional
            Musical genre.
        """
        self.title = title
        self.artist = artist
        self.album = album
        self.year = year
        self.genre = genre
        self.track_number = track_number
        self.comment = comment

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(title={self._title!r}, "
            f"artist={self._artist!r}, album={self._album!r}, "
            f"year={self._year}, comment={self._comment!r}, "
            f"track_number={self._track_number}, genre={self._genre!r})"
        )

    @classmethod
    def from_stream(cls, stream: BytesLike, /) -> Self:
        """
        Instantiate an :class:`ID3v1` object from a bytestream.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing an ID3v1 tag.

        Returns
        -------
        tag : minim.media.metadata.ID3v1
            ID3v1 tag.
        """
        (
            header,
            title,
            artist,
            album,
            year,
            comment,
            marker,
            track_number,
            genre,
        ) = cls._STRUCT_1_1.unpack_from(as_buffer(stream))
        if header != b"TAG":
            raise ValueError("`stream` does not contain an ID3v1 tag.")

        obj = cls.__new__(cls)
        obj._title = (
            title.rstrip(b"\x00").decode(encoding="iso-8859-1") or None
        )
        obj._artist = (
            artist.rstrip(b"\x00").decode(encoding="iso-8859-1") or None
        )
        obj._album = (
            album.rstrip(b"\x00").decode(encoding="iso-8859-1") or None
        )
        obj._year = year.rstrip(b"\x00").decode(encoding="iso-8859-1") or None
        if marker == 0 and track_number != 0:
            obj._track_number = track_number
            obj._comment = (
                comment.rstrip(b"\x00").decode(encoding="iso-8859-1") or None
            )
        else:
            obj._track_number = None
            obj._comment = (comment + marker + track_number).rstrip(
                b"\x00"
            ).decode(encoding="iso-8859-1") or None
        obj._genre = int(genre)
        return obj

    @property
    def album(self) -> str | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Title of the album or collection.
        """
        return self._album

    @album.setter
    def album(self, value: str | None, /) -> None:
        if value is not None:
            validate_type("album", value, str)
            if len(value) > 30:
                raise ValueError("`album` cannot exceed 30 characters.")
            validate_iso_8859_1_string("album", value)
        self._album = value

    @property
    def artist(self) -> str | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Main artists of the recording (e.g., the performing band or singers
        in popular music, the composers for classical music, or the
        authors of the original text in audiobooks).
        """
        return self._artist

    @artist.setter
    def artist(self, value: str | None, /) -> None:
        if value is not None:
            validate_type("artist", value, str)
            if len(value) > 30:
                raise ValueError("`artist` cannot exceed 30 characters.")
            validate_iso_8859_1_string("artist", value)
        self._artist = value

    @property
    def comment(self) -> str | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Free-form comment.
        """
        return self._comment

    @comment.setter
    def comment(self, value: str | None, /) -> None:
        if value is not None:
            validate_type("comment", value, str)
            if self._track_number is None:
                if len(value) > 30:
                    raise ValueError("`comment` cannot exceed 30 characters.")
            elif len(value) > 28:
                raise ValueError(
                    "`comment` cannot exceed 28 characters when "
                    "`track_number` is set."
                )
            validate_iso_8859_1_string("comment", value)
        self._comment = value

    @property
    def genre(self) -> int | str | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Musical genre.
        """
        return ID3V1_GENRES.get(self._genre, self._genre)

    @genre.setter
    def genre(self, value: int | str | None, /) -> None:
        if value is not None:
            if isinstance(value, str) and not value.isdecimal():
                value_ = ID3V1_GENRES.get(value.lower())
                if value_ is None:
                    raise ValueError(
                        f"Invalid or unknown ID3v1 genre {value!r}."
                    )
                value = value_
            else:
                validate_numeric("genre", value, int, 0, 255)
                value = int(value)
        self._genre = value

    @property
    def title(self) -> str | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Title of the recording.
        """
        return self._title

    @title.setter
    def title(self, value: str | None, /) -> None:
        if value is not None:
            validate_type("title", value, str)
            if len(value) > 30:
                raise ValueError("`title` cannot exceed 30 characters.")
            validate_iso_8859_1_string("title", value)
        self._title = value

    @property
    def track_number(self) -> int | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Track number within the album or collection.
        """
        return self._track_number

    @track_number.setter
    def track_number(self, value: int | None, /) -> None:
        if value is not None:
            if self._comment is not None and len(self._comment) > 28:
                raise ValueError(
                    "`track_number` cannot be set when `comment` "
                    "exceeds 28 characters."
                )
            validate_numeric("track_number", value, int, 1, 255)
            value = int(value)
        self._track_number = value

    @property
    def year(self) -> int | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Recording or release year.
        """
        return self._year

    @year.setter
    def year(self, value: int | str | None, /) -> None:
        if value is not None:
            validate_numeric("year", value, int, 0, 9_999)
            value = int(value)
        self._year = value

    def serialize(self, tag_version: str | tuple[int, int]) -> bytes:
        """
        Serialize the ID3v1 tag to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int]
            ID3v1 tag version.

            **Valid values**: :code:`"1.0"` or :code:`(1, 0)`,
            :code:`"1.1"` or :code:`(1, 1)`.

        Returns
        -------
        stream : bytes
            Bytestream containing the ID3v1 tag.
        """
        encoded_year = (
            f"{self._year:04d}".encode(encoding="iso-8859-1")
            if self._year
            else 4 * b"\x00"
        )
        match normalize_id3v1_tag_version(tag_version):
            case (1, 0):
                return self._STRUCT_1_0.pack(
                    b"TAG",
                    (self._title or "").encode(encoding="iso-8859-1"),
                    (self._artist or "").encode(encoding="iso-8859-1"),
                    (self._album or "").encode(encoding="iso-8859-1"),
                    encoded_year,
                    (self._comment or "").encode(encoding="iso-8859-1"),
                    255 if self._genre is None else self._genre,
                )
            case (1, 1):
                if self._comment is not None and len(self._comment) > 28:
                    raise RuntimeError(
                        "`comment` cannot exceed 28 characters when "
                        "serializing to an ID3v1.1 tag."
                    )
                return self._STRUCT_1_1.pack(
                    b"TAG",
                    (self._title or "").encode(encoding="iso-8859-1"),
                    (self._artist or "").encode(encoding="iso-8859-1"),
                    (self._album or "").encode(encoding="iso-8859-1"),
                    encoded_year,
                    (self._comment or "").encode(encoding="iso-8859-1"),
                    b"\x00",
                    self._track_number or 0,
                    255 if self._genre is None else self._genre,
                )


class ID3v2Flags:
    """
    Flags for an ID3v2 metadata container.
    """

    __slots__ = (
        "_has_extended_header",
        "_has_footer",
        "_is_compressed",
        "_is_experimental",
        "_is_unsynchronized",
    )

    def __init__(
        self,
        *,
        is_unsynchronized: bool = False,
        has_extended_header: bool = False,
        is_experimental: bool = False,
        has_footer: bool = False,
        is_compressed: bool = False,
    ) -> None:
        """
        Parameters
        ----------
        is_unsynchronized : bool; keyword-only; default: :code:`False`
            Whether the current tag has had unsynchronization applied to
            avoid false MPEG frame synchronization patterns in the
            metadata.

        has_extended_header : bool; keyword-only; default: :code:`False`
            Whether the current tag has an extended header after the
            main header.

        is_experimental : bool; keyword-only; default: :code:`False`
            Whether the current tag is marked as experimental by the
            encoder.

        has_footer : bool; keyword-only; default: :code:`False`
            Whether the current tag includes a 10-byte footer following
            the tag data.

        is_compressed : bool; keyword-only; default: :code:`False`
            Whether the current tag contains compressed data.
        """
        self.is_unsynchronized = is_unsynchronized
        self.has_extended_header = has_extended_header
        self.is_experimental = is_experimental
        self.has_footer = has_footer
        self.is_compressed = is_compressed

    def __repr__(self) -> str:
        flags = []
        if self._is_unsynchronized:
            flags.append("is_unsynchronized=True")
        if self._has_extended_header:
            flags.append("has_extended_header=True")
        if self._is_experimental:
            flags.append("is_experimental=True")
        if self._has_footer:
            flags.append("has_footer=True")
        if self._is_compressed:
            flags.append("is_compressed=True")
        return f"{type(self).__name__}({', '.join(flags)})"

    @classmethod
    def _from_byte_2_2(cls, byte_: int, /, *, strict: bool = True) -> Self:
        """
        Instantiate an :class:`ID3v2Flags` object from an ID3v2.2 tag
        flags byte.

        Parameters
        ----------
        byte_ : int; positional-only
            ID3v2.2 tag flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.id3.ID3v2Flags
            Flags for an ID3v2 tag.
        """
        if strict and byte_ & 0x3F:
            raise ValueError("Reserved bits set in ID3v2.2 flags byte.")

        obj = cls.__new__(cls)
        obj._is_unsynchronized = bool(byte_ & 0x80)
        obj._is_compressed = bool(byte_ & 0x40)
        obj._has_extended_header = obj._is_experimental = obj._has_footer = (
            False
        )
        return obj

    @classmethod
    def _from_byte_2_3(cls, byte_: int, /, *, strict: bool = True) -> Self:
        """
        Instantiate an :class:`ID3v2Flags` object from an ID3v2.3 tag
        flags byte.

        Parameters
        ----------
        byte_ : int; positional-only
            ID3v2.3 tag flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.id3.ID3v2Flags
            Flags for an ID3v2 tag.
        """
        if strict and byte_ & 0x1F:
            raise ValueError("Reserved bits set in ID3v2.3 flags byte.")

        obj = cls.__new__(cls)
        obj._is_unsynchronized = bool(byte_ & 0x80)
        obj._has_extended_header = bool(byte_ & 0x40)
        obj._is_experimental = bool(byte_ & 0x20)
        obj._has_footer = obj._is_compressed = False
        return obj

    @classmethod
    def _from_byte_2_4(cls, byte_: int, /, *, strict: bool = True) -> Self:
        """
        Instantiate an :class:`ID3v2Flags` object from an ID3v2.4 tag
        flags byte.

        Parameters
        ----------
        byte_ : int; positional-only
            ID3v2.4 tag flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.id3.ID3v2Flags
            Flags for an ID3v2 tag.
        """
        if strict and byte_ & 0xF:
            raise ValueError("Reserved bits set in ID3v2.4 flags byte.")

        obj = cls.__new__(cls)
        obj._is_unsynchronized = bool(byte_ & 0x80)
        obj._has_extended_header = bool(byte_ & 0x40)
        obj._is_experimental = bool(byte_ & 0x20)
        obj._has_footer = bool(byte_ & 0x10)
        obj._is_compressed = False
        return obj

    @classmethod
    def from_byte(
        cls,
        byte_: int,
        /,
        tag_version: str | tuple[int, int, int],
        *,
        strict: bool = True,
    ) -> Self:
        """
        Instantiate an :class:`ID3v2Flags` object from a ID3v2 tag flags
        byte.

        Parameters
        ----------
        byte_ : int; positional-only
            ID3v2 tag flags byte.

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
        flags : minim.media.metadata.id3.ID3v2Flags
            Flags for an ID3v2 tag.
        """
        validate_number("byte_", byte_, int, 0)
        match normalize_id3v2_tag_version(tag_version):
            case (2, 4, _):
                return cls._from_byte_2_4(byte_, strict=strict)
            case (2, 3, _):
                return cls._from_byte_2_3(byte_, strict=strict)
            case (2, 2, _):
                return cls._from_byte_2_2(byte_, strict=strict)
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
                )

    @property
    def is_unsynchronized(self) -> bool:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Whether the current tag has had unsynchronization applied to
        avoid false MPEG frame synchronization patterns in the metadata.
        """
        return self._is_unsynchronized

    @is_unsynchronized.setter
    def is_unsynchronized(self, value: bool, /) -> None:
        validate_type("is_unsynchronized", value, bool)
        self._is_unsynchronized = value

    @property
    def has_extended_header(self) -> bool:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Whether the current tag has an extended header after the main
        header.
        """
        return self._has_extended_header

    @has_extended_header.setter
    def has_extended_header(self, value: bool, /) -> bool:
        validate_type("has_extended_header", value, bool)
        self._has_extended_header = value

    @property
    def is_experimental(self) -> None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Whether the current tag is marked as experimental by the
        encoder.
        """
        return self._is_experimental

    @is_experimental.setter
    def is_experimental(self, value: bool, /) -> bool:
        validate_type("is_experimental", value, bool)
        self._is_experimental = value

    @property
    def has_footer(self) -> None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Whether the current tag includes a 10-byte footer following the
        tag data.
        """
        return self._has_footer

    @has_footer.setter
    def has_footer(self, value: bool, /) -> None:
        validate_type("has_footer", value, bool)
        self._has_footer = value

    @property
    def is_compressed(self) -> bool:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Whether the current tag contains compressed data.
        """
        return self._is_compressed

    @is_compressed.setter
    def is_compressed(self, value: bool, /) -> None:
        validate_type("is_compressed", value, bool)
        self._is_compressed = value

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the ID3v2 flags to bytes.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        bytes_ : bytes
            Bytes containing the ID3v2 flags.
        """
        match normalize_id3v2_tag_version(tag_version):
            case (2, 4, _):
                return bytes(
                    (
                        (self._is_unsynchronized << 7)
                        | (self._has_extended_header << 6)
                        | (self._is_experimental << 5)
                        | (self._has_footer << 4),
                    )
                )
            case (2, 3, _):
                return bytes(
                    (
                        (self._is_unsynchronized << 7)
                        | (self._has_extended_header << 6)
                        | (self._is_experimental << 5),
                    )
                )
            case (2, 2, _):
                return bytes(
                    (
                        (self._is_unsynchronized << 7)
                        | (self._is_compressed << 6),
                    )
                )


class ID3v2Padding(NULPadding):
    """
    ID3v2 padding.
    """

    __slots__ = ()

    @property
    def length(self) -> int:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Padding length, in bytes.
        """
        return self._length

    @length.setter
    def length(self, length: int, /) -> None:
        validate_number("length", length, int, 0)
        self._length = length


class ID3v2(AudioTags):
    """
    ID3v2 metadata container.

    .. seealso::

       `What is ID3v2? <https://id3.org/ID3v2Easy>`_
    """

    _STRUCT_ID3_HEADER: ClassVar[struct.Struct] = struct.Struct(">3s7B")
    _STRUCT_PARTIAL_FRAME_HEADER_2_3: ClassVar[struct.Struct] = struct.Struct(
        ">4sI"
    )
    _STRUCT_PARTIAL_FRAME_HEADER_2_4: ClassVar[struct.Struct] = struct.Struct(
        ">4s4B"
    )

    __slots__ = (
        "_class_index",
        "_flags",
        "_frames",
        "_has_crc",
        "_is_update",
        "_key_index",
        "_padding",
        "_tag_restrictions",
        "_unknown_index",
    )

    def __init__(
        self,
        frames: OrderedCollection[ID3v2Frame],
        /,
        *,
        flags: ID3v2Flags | None = None,
        is_update: bool = False,
        has_crc: bool = False,
        tag_restrictions: int = 0,
    ) -> None:
        """
        Parameters
        ----------
        frames : OrderedCollection[minim.media.metadata.id3.ID3v2Frame]; \
        positional-only
            ID3v2 frames.

        flags : minim.media.metadata.id3.ID3v2Flags; keyword-only; \
        optional
            Flags and extended header for ID3v2 tags.

        is_update : bool; keyword-only; default: :code:`False`
            Whether the current tag has an extended header and is
            identified as an updated version of an earlier tag.

        has_crc : bool; keyword-only; default: :code:`False`
            Whether the current tag has an extended header with CRC
            data.

        tag_restrictions : int; keyword-only; default: :code:`0`
            Tag restrictions byte in the extended header.

            .. note::

               Currently, tag restrictions are not enforced when
               serializing ID3v2 tags.
        """
        if not isinstance(frames, ORDERED_COLLECTION_TYPES):
            frames = [frames]

        self._frames = []
        self._class_index = defaultdict(list)
        self._key_index = defaultdict(dict)
        for frame_idx, frame in enumerate(frames):
            validate_type(f"frames[{frame_idx}]", frame, ID3v2Frame)
            self._add_frame(frame)

        if flags is None:
            self._flags = ID3v2Flags()
        else:
            validate_type("flags", flags, ID3v2Flags)
            self._flags = flags

        self.is_update = is_update
        self.has_crc = has_crc
        self.tag_restrictions = tag_restrictions

    def __repr__(self) -> str:
        optional_kwargs = [""]
        if self._is_update:
            optional_kwargs.append("is_update=True")
        if self._has_crc:
            optional_kwargs.append("has_crc=True")
        if self._tag_restrictions:
            optional_kwargs.append(
                f"tag_restrictions={self._tag_restrictions}"
            )
        return (
            f"{type(self).__name__}(<{len(self._frames)} frame(s)>, "
            f"flags={self._flags!r}{', '.join(optional_kwargs)})"
        )

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, flags: bytes, *, strict: bool = True
    ) -> Self:
        """
        Instantiate an :class:`ID3v2` object from an ID3v2.2 tag
        bytestream.

        .. note::

           If :code:`TYE`, :code:`TDA`, and/or :code:`TIM` are present
           and contain differing numbers of values, values are
           associated by ordinal position. Missing components are
           represented as :code:`None` when :code:`strict=False`;
           otherwise, an exception is raised.

        Parameters
        ----------
        stream : memoryview; positional-only; optional
            Bytes-like object containing an ID3v2.2 tag.

        flags : bytes
            ID3v2.2 tag flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        tag : minim.media.metadata.ID3v2
            ID3v2 tag.
        """
        obj = cls.__new__(cls)
        obj._frames = frames = []
        obj._padding = None
        obj._class_index = defaultdict(list)
        obj._key_index = defaultdict(dict)
        obj._unknown_index = defaultdict(list)
        obj._flags = flags = ID3v2Flags._from_byte_2_2(flags, strict=strict)
        obj._has_crc = obj._is_update = False
        obj._tag_restrictions = 0

        if flags._is_compressed:
            raise NotImplementedError(
                "Compressed ID3v2.2 tags are not supported."
            )  # TODO: Store raw data in immutable object

        if flags._is_unsynchronized:
            stream = memoryview(stream.tobytes().replace(b"\xff\x00", b"\xff"))
        offset = 0
        tag_end = len(stream)

        while offset < tag_end:
            if not stream[offset]:
                obj._padding = ID3v2Padding.from_stream(
                    stream[offset:], strict=strict
                )
                break

            end_offset = offset + 3
            frame_id = stream[offset:end_offset]
            end_offset += 3 + int.from_bytes(
                stream[end_offset : end_offset + 3], byteorder="big"
            )
            obj._add_frame(
                ID3v2Frame._get_class(frame_id)._from_stream_2_2(
                    stream[offset:end_offset], strict=strict
                ),
                strict=strict,
            )
            offset = end_offset

        if strict and not frames:
            raise ValueError("ID3v2 tag contains no frames.")

        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, flags: bytes, *, strict: bool = True
    ) -> Self:
        """
        Instantiate an :class:`ID3v2` object from an ID3v2.3 tag
        bytestream.

        .. note::

           If :code:`TYER`, :code:`TDAT`, and/or :code:`TIME` are
           present and contain differing numbers of values, values are
           associated by ordinal position. Missing components are
           represented as :code:`None` when :code:`strict=False`;
           otherwise, an exception is raised.

        Parameters
        ----------
        stream : memoryview; positional-only; optional
            Bytes-like object containing an ID3v2.3 tag.

        flags : bytes
            ID3v2.3 tag flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        tag : minim.media.metadata.ID3v2
            ID3v2 tag.
        """
        obj = cls.__new__(cls)
        obj._frames = frames = []
        obj._padding = None
        obj._class_index = defaultdict(list)
        obj._key_index = defaultdict(dict)
        obj._unknown_index = defaultdict(list)
        obj._flags = flags = ID3v2Flags._from_byte_2_3(flags, strict=strict)

        if flags._is_unsynchronized:
            stream = memoryview(stream.tobytes().replace(b"\xff\x00", b"\xff"))
        offset = 0
        tag_end = len(stream)

        if flags._has_extended_header:
            flag_byte = stream[offset + 4]
            if strict and (flag_byte & 0x80 or stream[offset + 5]):
                raise ValueError(
                    "Non-zero bits found in reserved section "
                    "of ID3 extended header flags byte."
                )
            obj._has_crc = bool(flag_byte >> 8)
            offset += int.from_bytes(stream[offset : offset + 4]) + 4
        else:
            obj._has_crc = False
        obj._is_update = False
        obj._tag_restrictions = 0

        while offset < tag_end:
            if not stream[offset]:
                obj._padding = ID3v2Padding.from_stream(
                    stream[offset:], strict=strict
                )
                break

            frame_id, frame_length = (
                cls._STRUCT_PARTIAL_FRAME_HEADER_2_3.unpack_from(
                    stream, offset
                )
            )
            end_offset = offset + 10 + frame_length
            obj._add_frame(
                ID3v2Frame._get_class(frame_id)._from_stream_2_3(
                    stream[offset:end_offset], strict=strict
                ),
                strict=strict,
            )
            offset = end_offset

        if strict and not frames:
            raise ValueError("ID3v2 tag contains no frames.")

        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, flags: bytes, *, strict: bool = True
    ) -> Self:
        """
        Instantiate an :class:`ID3v2` object from an ID3v2.4 tag
        bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only; optional
            Bytes-like object containing an ID3v2.4 tag.

        flags : bytes
            ID3v2.4 tag flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        tag : minim.media.metadata.ID3v2
            ID3v2 tag.
        """
        obj = cls.__new__(cls)
        obj._frames = frames = []
        obj._padding = None
        obj._class_index = defaultdict(list)
        obj._key_index = defaultdict(dict)
        obj._unknown_index = defaultdict(list)
        obj._flags = flags = ID3v2Flags._from_byte_2_4(flags, strict=strict)

        offset = 0
        if flags._has_extended_header:
            flag_byte = stream[offset + 5]
            if strict and flag_byte & 0x8F:
                raise ValueError(
                    "Non-zero bits found in reserved section "
                    "of ID3 extended header flags byte."
                )
            obj._is_update = bool((flag_byte >> 7) & 1)
            obj._has_crc = bool((flag_byte >> 6) & 1)
            if bool((flag_byte >> 5) & 1):
                obj._tag_restrictions = stream[
                    offset + 7 + obj._is_update + 6 * obj._has_crc
                ]
            offset += decode_synchsafe_int(*stream[offset : offset + 4])
        else:
            obj._is_update = obj._has_crc = False
            obj._tag_restrictions = 0

        is_unsynchronized = strict and flags._is_unsynchronized
        tag_end = len(stream)
        while offset < tag_end:
            if not stream[offset]:
                if strict and flags._has_footer:
                    raise ValueError(
                        "ID3v2.4 tag cannot simultaneously have a "
                        "footer and padding."
                    )
                obj._padding = ID3v2Padding.from_stream(
                    stream[offset:], strict=strict
                )
                break

            frame_id, *frame_length = (
                cls._STRUCT_PARTIAL_FRAME_HEADER_2_4.unpack_from(
                    stream, offset
                )
            )
            end_offset = offset + 10 + decode_synchsafe_int(*frame_length)
            frame = ID3v2Frame._get_class(frame_id)._from_stream_2_4(
                stream[offset:end_offset], strict=strict
            )
            if is_unsynchronized and not frame._flags._is_unsynchronized:
                raise ValueError(
                    "ID3v2.4 tag unsynchronization flag is set, but "
                    f"a(n) {frame_id.decode(encoding='ascii')} frame "
                    "is not marked as unsynchronized."
                )
            obj._add_frame(frame, strict=strict)
            offset = end_offset + 10 * flags._has_footer

        if strict and not frames:
            raise ValueError("ID3v2 tag contains no frames.")

        return obj

    @classmethod
    def from_stream(cls, stream: BytesLike, /, *, strict: bool = True) -> Self:
        """
        Instantiate an :class:`ID3v2` object from a bytestream.

        .. note::

           For ID3v2.2/2.3 tags with :code:`TYE`/:code:`TYER`,
           :code:`TDA`/:code:`TDAT`, and/or :code:`TIM`/:code:`TIME`
           frames containing differing numbers of values, values are
           associated by ordinal position. Missing components are
           represented as :code:`None` when :code:`strict=False`;
           otherwise, an exception is raised.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing an ID3v2 tag.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        tag : minim.media.metadata.ID3v2
            ID3v2 tag.
        """
        stream = as_buffer(stream)
        frame_id, minor, patch, flags, *tag_length = (
            cls._STRUCT_ID3_HEADER.unpack_from(stream)
        )
        if frame_id != b"ID3":
            raise ValueError("`stream` does not contain an ID3v2 tag.")

        stream = stream[10 : 10 + decode_synchsafe_int(*tag_length)]
        match tag_version := (2, minor, patch):
            case (2, 4, _):
                return cls._from_stream_2_4(stream, flags=flags, strict=strict)
            case (2, 3, _):
                return cls._from_stream_2_3(stream, flags=flags, strict=strict)
            case (2, 2, _):
                return cls._from_stream_2_2(stream, flags=flags, strict=strict)
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
                )

    @property
    def is_update(self) -> bool:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Whether the current tag is an updated version of an earlier
        tag.
        """
        return self._is_update

    @is_update.setter
    def is_update(self, value: bool, /) -> None:
        validate_type("is_update", value, bool)
        self._is_update = value

    @property
    def has_crc(self) -> bool:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Whether the current tag has an extended header with CRC
        data.
        """
        return self._has_crc

    @has_crc.setter
    def has_crc(self, value: bool, /) -> None:
        validate_type("has_crc", value, bool)
        self._has_crc = value

    @property
    def tag_restrictions(self) -> int:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Tag restrictions byte.

        .. note::

           Tag restrictions are not enforced when serializing ID3v2
           tags.
        """
        return self._tag_restrictions

    @tag_restrictions.setter
    def tag_restrictions(self, value: int, /) -> None:
        validate_number("tag_restrictions", value, int, 0, 255)
        self._tag_restrictions = value

    @property
    def album(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TAL`/:code:`TALB` – Title of the album or collection.
        """
        return self._get_text_info(b"TALB")

    @album.setter
    def album(
        self,
        value: str | ID3v2TALBFrame | OrderedCollection[str],
        /,
    ) -> None:
        self._set_text_info(b"TALB", value)

    @property
    def album_artist(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TP2`/:code:`TPE2` – Main artists credited for the entire
        album or collection.
        """
        return self._get_text_info(b"TPE2")

    @album_artist.setter
    def album_artist(
        self,
        value: str | ID3v2TPE2Frame | OrderedCollection[str],
        /,
    ) -> None:
        self._set_text_info(b"TPE2", value)

    @property
    def artist(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TP1`/:code:`TPE1` – Main artists of the recording (e.g.,
        the performing band or singers in popular music, the composers
        for classical music, or the authors of the original text in
        audiobooks).
        """
        return self._get_text_info(b"TPE1")

    @artist.setter
    def artist(
        self,
        value: str | ID3v2TPE1Frame | OrderedCollection[str],
        /,
    ) -> None:
        self._set_text_info(b"TPE1", value)

    @property
    def bpm(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TBP`/:code:`TBPM` – Tempo in beats per minute (BPM).
        """
        return self._get_text_info(b"TBPM")

    @bpm.setter
    def bpm(
        self,
        value: float
        | str
        | ID3v2TBPMFrame
        | OrderedCollection[int | float | str],
        /,
    ) -> None:
        self._set_text_info(b"TBPM", value)

    @property
    def comment(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`COM`/:code:`COMM` – Free-form comments.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"COMM")):
            return [frame._comment for frame in frames]

    @comment.setter
    def comment(
        self,
        value: str
        | tuple[str, str]
        | ID3v2COMMFrame
        | list[tuple[str, str] | ID3v2COMMFrame],
        /,
    ) -> None:
        frame_cls = ID3v2Frame._get_class(b"COMM")
        frame_name = frame_cls.__name__
        match value:
            case list():
                value_ = []
                for val in value:
                    if isinstance(val, frame_cls):
                        value_.append(val)
                    elif isinstance(val, tuple):
                        if len(val) != 2 or not all(
                            isinstance(v, str) for v in val
                        ):
                            raise ValueError(
                                "When `comment` is a tuple, it must "
                                "have length 2 and contain only "
                                "strings: (description, comment)."
                            )
                        value_.append(frame_cls(*val))
                    else:
                        raise TypeError(
                            "When `comment` is a list, it must contain "
                            "only tuples of two strings (description, "
                            f"comment) and {frame_name} objects."
                        )
                value = value_
            case str():
                value = [frame_cls(description="", comment=value)]
            case tuple():
                if len(value) != 2 or not all(
                    isinstance(val, str) for val in value
                ):
                    raise ValueError(
                        "When `comment` is a tuple, it must have length 2 "
                        "and contain only strings: (description, comment)."
                    )
                value = [frame_cls(*value)]
            case frame_cls():
                value = [value]
            case _:
                raise TypeError(
                    "`comment` must be a string (comment), a tuple of "
                    "two strings (description, comment), an "
                    f"{frame_name} object, or a list containing them."
                )
        self._set_known_frames(value)

    @property
    def compilation(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TCP`/:code:`TCMP` – Whether the recording is part of a
        compilation.
        """
        return self._get_text_info(b"TCMP")

    @compilation.setter
    def compilation(
        self,
        value: bool
        | int
        | str
        | ID3v2TCMPFrame
        | OrderedCollection[bool | int | str],
        /,
    ) -> None:
        self._set_text_info(b"TCMP", value)

    @property
    def composer(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TCM`/:code:`TCOM` – Composers or songwriters.
        """
        return self._get_text_info(b"TCOM")

    @composer.setter
    def composer(
        self,
        value: str | ID3v2TCOMFrame | OrderedCollection[str],
        /,
    ) -> None:
        self._set_text_info(b"TCOM", value)

    @property
    def copyright(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TCR`/:code:`TCOP` – Copyright attribution.
        """
        return self._get_text_info(b"TCOP")

    @copyright.setter
    def copyright(self, value: str | OrderedCollection[str], /) -> None:
        self._set_text_info(b"TCOP", value)

    @property
    def date(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TYE` + :code:`TDA` + :code:`TIM`/:code:`TYER` +
        :code:`TDAT` + :code:`TIME`/:code:`TDRC`/:code:`TDRL` –
        Recording or release date.
        """
        # if frames := (
        #     self._class_index.get(ID3v2Frame._get_class(b"TDRC"))
        #     or self._class_index.get(ID3v2Frame._get_class(b"TDRL"))
        # ):
        #     return frames[-1]._text_info.copy()
        raise NotImplementedError  # TODO

    @date.setter
    def date(
        self, value: str | datetime | OrderedCollection[str | datetime], /
    ) -> None:
        raise NotImplementedError  # TODO

    @property
    def disc_number(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TPA`/:code:`TPOS` – Disc number within a multi-disc set.
        """
        # if frames := self._class_index.get(ID3v2Frame._get_class(b"TPOS")):
        #     return [str(disc.number) for disc in frames[-1]._discs]
        raise NotImplementedError  # TODO

    @disc_number.setter
    def disc_number(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None:
        raise NotImplementedError  # TODO

    @property
    def disc_total(self) -> list[str | None] | None:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set`
        :code:`TPA`/:code:`TPOS` – Total number of discs.
        """
        # if frames := self._class_index.get(ID3v2Frame._get_class(b"TPOS")):
        #     return [str(disc.total) for disc in frames[-1]._discs]
        raise NotImplementedError  # TODO

    @property
    def encoder(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TSS`/:code:`TSSE` – Software or hardware used for
        encoding, or the person or organization that encoded the audio
        file.
        """
        return self._get_text_info(b"TSSE")

    @encoder.setter
    def encoder(
        self,
        value: str | ID3v2TSSEFrame | OrderedCollection[str],
        /,
    ) -> None:
        self._set_text_info(b"TSSE", value)

    @property
    def genre(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TCO`/:code:`TCON` –  Musical genres.
        """
        return self._get_text_info(b"TCON")

    @genre.setter
    def genre(
        self,
        value: str | ID3v2TCONFrame | OrderedCollection[str],
        /,
    ) -> None:
        self._set_text_info(b"TCON", value)

    @property
    def grouping(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TT1`/:code:`TIT1` – Content group description.
        """
        return self._get_text_info(b"TIT1")

    @grouping.setter
    def grouping(
        self,
        value: str | ID3v2TIT1Frame | OrderedCollection[str],
        /,
    ) -> None:
        self._set_text_info(b"TIT1", value)

    @property
    def isrc(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TRC`/:code:`TSRC` – International Standard Recording Code
        (ISRC).
        """
        return self._get_text_info(b"TSRC")

    @isrc.setter
    def isrc(
        self,
        value: str | ID3v2TSRCFrame | OrderedCollection[str],
        /,
    ) -> None:
        self._set_text_info(b"TSRC", value)

    @property
    def label(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TPB`/:code:`TPUB` – Publishers or record labels.
        """
        return self._get_text_info(b"TPUB")

    @label.setter
    def label(
        self,
        value: str | ID3v2TPUBFrame | OrderedCollection[str],
        /,
    ) -> None:
        self._set_text_info(b"TPUB", value)

    @property
    def lyrics(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`SLT`/:code:`SYLT` (synchronized) or
        :code:`ULT`/:code:`USLT` (unsynchronized) – Lyrics or
        transcription.
        """
        # lyrics = []
        # if frames := self._class_index.get(ID3v2Frame._get_class(b"SYLT")):
        #     lyrics.extend(frame._lyrics for frame in frames)
        # if frames := self._class_index.get(ID3v2Frame._get_class(b"USLT")):
        #     lyrics.extend(frame._lyrics for frame in frames)
        # return lyrics or None
        raise NotImplementedError  # TODO

    @lyrics.setter
    def lyrics(self, value: str | OrderedCollection[str], /) -> None:
        raise NotImplementedError  # TODO

    @property
    def performer(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TP3`/:code:`TPE3` – Performers (e.g., the conductor,
        orchestra, and/or soloists in classical music, or the narrator
        in audiobooks).
        """
        return self._get_text_info(b"TPE3")

    @performer.setter
    def performer(
        self,
        value: str | ID3v2TPE3Frame | OrderedCollection[str],
        /,
    ) -> None:
        self._set_text_info(b"TPE3", value)

    @property
    def title(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TT2`/:code:`TIT2` – Title of the recording.
        """
        return self._get_text_info(b"TIT2")

    @title.setter
    def title(
        self,
        value: str | ID3v2TIT2Frame | OrderedCollection[str],
        /,
    ) -> None:
        self._set_text_info(b"TIT2", value)

    @property
    def track_number(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TRK`/:code:`TRCK` – Track number within the album or
        collection.
        """
        # if frames := self._class_index.get(ID3v2Frame._get_class(b"TRCK")):
        #     return [str(track.number) for track in frames[-1]._tracks]
        raise NotImplementedError  # TODO

    @track_number.setter
    def track_number(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None:
        raise NotImplementedError  # TODO

    @property
    def track_total(self) -> list[str | None] | None:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set`
        :code:`TRK`/:code:`TRCK` – Total number of tracks.
        """
        # if frames := self._class_index.get(ID3v2Frame._get_class(b"TRCK")):
        #     return [str(track.total) for track in frames[-1]._tracks]
        raise NotImplementedError  # TODO

    @property
    def version(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TT3`/:code:`TIT3` – Version of the recording (e.g., remix
        information).
        """
        return self._set_text_info(b"TIT3")

    @version.setter
    def version(
        self,
        value: str | ID3v2TIT3Frame | OrderedCollection[str],
        /,
    ) -> None:
        self._set_text_info(b"TIT3", value)

    def _add_frame(
        self,
        frame: ID3v2Frame,
        /,
        *,
        strict: bool = True,
    ) -> None:
        """
        Add an ID3v2 frame to the data structures in a :class:`ID3v2`.

        Parameters
        ----------
        frame : minim.media.metadata.id3.ID3v2Frame; positional-only
            ID3v2 frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.
        """
        frame_cls = type(frame)
        if frame_cls is EncryptedID3v2Frame:
            actual_cls = frame._class or UnknownID3v2Frame
            if (
                strict
                and not self._allow_multiple
                and self._class_index.get(actual_cls)
            ):
                raise ValueError(
                    f"Multiple {frame._frame_id.decode(encoding='ascii')} "
                    "frames found."
                )
            self._frames.append(frame)
            self._class_index[frame_cls].append(frame)
            if actual_cls is UnknownID3v2Frame:
                self._unknown_index[frame._frame_id].append(frame)
        elif frame_cls is UnknownID3v2Frame:
            self._frames.append(frame)
            self._class_index[frame_cls].append(frame)
            self._unknown_index[frame._frame_id].append(frame)
        elif frame_cls._allow_multiple:
            if (
                strict
                and (existing_frame_keys := self._key_index.get(frame_cls))
                and frame._key in existing_frame_keys
            ):
                raise ValueError(
                    f"Duplicate {frame._frame_id.decode(encoding='ascii')} "
                    "frame found."
                )

            self._frames.append(frame)
            self._class_index[frame_cls].append(frame)
            if frame._key:
                self._key_index[frame_cls][frame._key] = frame
        else:
            existing_frames = self._class_index.get(frame_cls)
            if existing_frames:
                if strict:
                    raise ValueError(
                        f"Multiple {frame._frame_id.decode(encoding='ascii')} "
                        "frames found."
                    )

                existing_frame = existing_frames[-1]
                if issubclass(frame_cls, ID3v2DateTimeFrame):
                    existing_frame |= frame
                else:
                    existing_frame += frame
            else:
                if strict and self._unknown_index.get(frame_cls):
                    raise ValueError(
                        f"Multiple {frame._frame_id.decode(encoding='ascii')} "
                        "frames found."
                    )
                self._frames.append(frame)
                self._class_index[frame_cls].append(frame)

    def _get_text_info(self, frame_id: bytes) -> list[str] | None:
        """
        Get text information by frame ID.

        Parameters
        ----------
        frame_id : bytes
            Frame ID.

        Returns
        -------
        text_info : list[str] or None
            Text information. If no matching frames are found or the
            matching frames are encrypted, :code:`None` is returned.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(frame_id)):
            return frames[-1]._text_info.copy()

    def _set_text_info(
        self, frame_id: bytes, value: Any | OrderedCollection[Any]
    ) -> None:
        """
        Set text information by frame ID.

        Parameters
        ----------
        frame_id : bytes
            Frame ID.

        value : Any or Collection[Any]
            Text information.
        """
        frame_cls = ID3v2Frame._get_class(frame_id)
        self._set_known_frame(
            [frame_cls(val) for val in value]
            if isinstance(value, ORDERED_COLLECTION_TYPES)
            else [value if isinstance(value, frame_cls) else frame_cls(value)]
        )

    def _set_known_frames(self, value: list[ID3v2Frame], /) -> None:
        """
        Remove existing frames with the same frame ID and add the new
        frames.

        Parameters
        ----------
        value : list[minim.media.metadata.id3.ID3v2Frame]; \
        positional-only
            Frames.
        """
        frame_cls = type(value[0])
        self._frames = [
            frame
            for frame in self._frames
            if not (
                isinstance(frame, frame_cls)
                or isinstance(frame, EncryptedID3v2Frame)
                and frame._class is frame_cls
            )
        ]
        self._frames.extend(value)
        self._class_index[frame_cls] = value
        self._class_index[EncryptedID3v2Frame] = [
            frame
            for frame in self._class_index[EncryptedID3v2Frame]
            if frame._class is not frame_cls
        ]

    def get(self) -> None: ...

    def set(self) -> None: ...

    def serialize(
        self,
        tag_version: str | tuple[int, int, int],
        *,
        text_encoding: str | None = None,
        include_padding: bool = True,
    ) -> bytes:
        """
        Serialize the ID3v2 tag to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        text_encoding : str; keyword-only; optional
            Text encoding to use for all ID3v2 frames. If :code:`None`,
            the text encodings already associated with the frames are
            used.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        include_padding : bool; keyword-only; default: :code:`True`
            Whether to keep padding.

        Returns
        -------
        stream : bytes
            Bytestream containing the serialized ID3v2 tag.
        """
        tag_version = normalize_id3v2_tag_version(tag_version)
        if tag_version not in ID3V2_TAG_VERSIONS:
            raise ValueError(
                f"Invalid ID3v2 tag version {tag_version!r}. "
                f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
            )

        frames = b"".join(
            frame.serialize(tag_version, text_encoding=text_encoding)
            for frame in self._frames
        )
        padding = self._padding
        include_padding = include_padding and padding is not None
        if include_padding:
            padding_length = padding._length
            padding = self._padding.serialize()
        else:
            padding = b""
            padding_length = 0

        flags = self._flags
        match tag_version:
            case (2, 4, _):
                if flags._has_footer:
                    padding = b""
                    padding_length = 0

                if flags._has_extended_header:
                    tag_restrictions = self._tag_restrictions
                    extended_header = bytes(
                        (
                            1,
                            (
                                (self._is_update << 6)
                                | (self._has_crc << 5)
                                | ((tag_restrictions != 0) << 4)
                            ),
                        )
                    )

                    # TODO: Enforce tag restrictions? Not trivial to
                    # restrict only text information frames, and need
                    # external library to resolve image sizes.

                    if self._is_update:
                        extended_header += b"\x00"
                    if self._has_crc:
                        extended_header += bytes(
                            (
                                5,
                                *encode_synchsafe_int(
                                    zlib.crc32(frames + padding), num_bytes=5
                                ),
                            )
                        )
                    if tag_restrictions:
                        extended_header += bytes((1, tag_restrictions))
                    extended_header = (
                        bytes(encode_synchsafe_int(4 + len(extended_header)))
                        + extended_header
                    )
                else:
                    extended_header = b""

                if flags._has_footer:
                    footer = self._STRUCT_ID3_HEADER.pack(
                        b"3DI",
                        tag_version[1],
                        0,
                        int.from_bytes(
                            self._flags.serialize(tag_version), byteorder="big"
                        ),
                        *encode_synchsafe_int(
                            len(extended_header) + len(frames) + padding_length
                        ),
                    )
                else:
                    footer = b""

            case (2, 3, _):
                if flags._has_extended_header:
                    extended_header = (self._has_crc << 15).to_bytes(
                        2, byteorder="big"
                    ) + (padding_length if include_padding else 0).to_bytes(
                        4, byteorder="big"
                    )
                    if self._has_crc:
                        extended_header += zlib.crc32(frames).to_bytes(
                            4, byteorder="big"
                        )
                    extended_header = (
                        len(extended_header).to_bytes(4, byteorder="big")
                        + extended_header
                    )
                else:
                    extended_header = b""

                if flags._is_unsynchronized:
                    frames = UNSYNCHRONIZATION_RE.sub(
                        b"\xff\x00", extended_header + frames
                    )
                    extended_header = b""

                footer = b""

            case (2, 2, _):
                extended_header = footer = b""

                if flags._is_unsynchronized:
                    frames = UNSYNCHRONIZATION_RE.sub(b"\xff\x00", frames)

        return b"".join(
            (
                self._STRUCT_ID3_HEADER.pack(
                    b"ID3",
                    tag_version[1],
                    0,
                    int.from_bytes(
                        self._flags.serialize(tag_version), byteorder="big"
                    ),
                    *encode_synchsafe_int(
                        len(extended_header) + len(frames) + padding_length
                    ),
                ),
                extended_header,
                frames,
                padding,
                footer,
            )
        )
