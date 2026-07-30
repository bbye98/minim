from __future__ import annotations

import struct
from collections import defaultdict
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar

from ...._types import ORDERED_COLLECTION_TYPES
from ...._utility import (
    as_buffer,
    decode_32_bit_synchsafe_int,
    join_values,
    validate_iso_8859_1_string,
    validate_number,
    validate_numeric,
    validate_type,
)
from .._shared import AudioTags
from ._frames import (
    ID3v2Frame,
    ID3v2Padding,
    ID3v2TXXXFrame,
    UnknownID3v2Frame,
)
from ._shared import (
    TAG_VERSIONS,
    normalize_id3v1_tag_version,
    normalize_id3v2_tag_version,
)

if TYPE_CHECKING:
    from typing import Any

    from ...._types import BytesLike, Collection, OrderedCollection


class ID3v1:
    """
    ID3v1 metadata container.

    .. seealso::

       `What is ID3 (v1)? <https://id3.org/ID3v1>`_
    """

    _STRUCT_1_0: ClassVar[struct.Struct] = struct.Struct("3s30s30s30s4s30sB")
    _STRUCT_1_1: ClassVar[struct.Struct] = struct.Struct("3s30s30s30s4s28sBBB")

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
        title : str or None; keyword-only; optional
            Title of the recording.

        artist : str or None; keyword-only; optional
            Main artists of the recording (e.g., the performing band or
            singers in popular music, the composers for classical music,
            or the authors of the original text in audiobooks).

        album : str or None; keyword-only; optional
            Title of the album or collection.

        year : int, str, or None; keyword-only; optional
            Recording or release year.

        comment : str or None; keyword-only; optional
            Free-form comment.

        track_number : int or None; keyword-only; optional
            Track number within the album or collection.

        genre : int, str, or None; keyword-only; optional
            Musical genre.
        """
        self.title = title
        self.artist = artist
        self.album = album
        self.year = year
        self.genre = genre
        if track_number is None:
            if comment is not None:
                validate_type("comment", comment, str)
                if len(comment) > 30:
                    raise ValueError("`comment` cannot exceed 30 characters.")
                validate_iso_8859_1_string("comment", comment)
        else:
            validate_numeric("track_number", track_number, int, 1, 255)
            track_number = str(track_number)
            if comment is not None:
                validate_type("comment", comment, str)
                if len(comment) > 28:
                    raise ValueError(
                        "`comment` cannot exceed 28 characters when "
                        "`track_number` is set."
                    )
                validate_iso_8859_1_string("comment", comment)
        self._comment = comment
        self._track_number = track_number

    @classmethod
    def from_stream(cls, stream: BytesLike, /) -> ID3v1:
        """
        Instantiate an :class:`ID3v1` object from a bytestream.

        Parameters
        ----------
        stream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
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
    def genre(self) -> int | None:
        """
        Musical genre.
        """
        return self._genre

    @genre.setter
    def genre(self, value: int | str | None, /) -> None:
        if value is not None:
            validate_numeric("genre", value, int, 0, 255)
            value = int(value)
        self._genre = value

    @property
    def title(self) -> str | None:
        """
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
    def year(self) -> str | None:
        """
        Recording or release year.
        """
        return self._year

    @year.setter
    def year(self, value: int | str | None, /) -> None:
        if value is not None:
            validate_numeric("year", value, int, 0, 9_999)
            value = str(value)
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
        bytestream : bytes
            Bytestream containing the serialized ID3v1 tag.
        """
        match normalize_id3v1_tag_version(tag_version):
            case (1, 0):
                return self._STRUCT_1_1.pack(
                    b"TAG",
                    (self._title or "").encode(encoding="iso-8859-1"),
                    (self._artist or "").encode(encoding="iso-8859-1"),
                    (self._album or "").encode(encoding="iso-8859-1"),
                    (self._year or "").encode(encoding="iso-8859-1"),
                    (self._comment or "").encode(encoding="iso-8859-1"),
                    self._genre or 255,
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
                    (self._year or "").encode(encoding="iso-8859-1"),
                    (self._comment or "").encode(encoding="iso-8859-1"),
                    0,
                    self._track_number or 0,
                    self._genre or 255,
                )


class ID3v2Flags:
    """
    Flags and extended header for ID3v2 tags.
    """

    __slots__ = (
        "_has_crc",
        "_has_extended_header",
        "_has_footer",
        "_is_compressed",
        "_is_experimental",
        "_is_unsynchronized",
        "_is_update",
        "_tag_restrictions",
    )

    def __init__(
        self,
        is_unsynchronized: bool = False,
        has_extended_header: bool = False,
        is_experimental: bool = False,
        has_footer: bool = False,
        is_compressed: bool = False,
        is_update: bool = False,
        has_crc: bool = False,
        tag_restrictions: int | None = None,
    ) -> None:
        """
        Parameters
        ----------
        is_unsynchronized : bool; keyword-only; default: :code:`False`
            Whether the current tag has had unsynchronization applied to
            avoid false MPEG frame sync patterns in the metadata.

        has_extended_header : bool; keyword-only; default: :code:`False`
            Whether the current tag contains an extended header
            immediately after the main ID3v2 header.

        is_experimental : bool; keyword-only; default: :code:`False`
            Whether the current tag is marked as experimental by the
            encoder.

        has_footer : bool; keyword-only; default: :code:`False`
            Whether the current tag includes a 10-byte footer following
            the tag data.

        is_compressed : bool; keyword-only; default: :code:`False`
            Whether the current tag has compressed data.

        is_update : bool; keyword-only; default: :code:`False`
            Whether the current tag has an extended header and is
            identified as an updated version of an earlier tag.

        has_crc : bool; keyword-only; default: :code:`False`
            Whether the current tag has an extended header with CRC
            data.

        tag_restrictions : int; keyword-only; optional
            Tag restrictions byte in the extended header.
        """
        self.is_unsynchronized = is_unsynchronized
        self.has_extended_header = has_extended_header
        self.is_experimental = is_experimental
        self.has_footer = has_footer
        self.is_compressed = is_compressed
        self.is_update = is_update
        self.has_crc = has_crc
        self.tag_restrictions = tag_restrictions

    @classmethod
    def _from_byte_2_2(
        cls, byte_: int, /, *, strict: bool = True
    ) -> ID3v2Flags:
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
        flags : minim.media.metadata.ID3v2Flags
            Flags for ID3v2 tags.
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
    def _from_byte_2_3(
        cls, byte_: int, /, *, strict: bool = True
    ) -> ID3v2Flags:
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
        flags : minim.media.metadata.ID3v2Flags
            Flags for ID3v2 tags.
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
    def _from_byte_2_4(
        cls, byte_: int, /, *, strict: bool = True
    ) -> ID3v2Flags:
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
        flags : minim.media.metadata.ID3v2Flags
            Flags for ID3v2 tags.
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
    ) -> ID3v2Flags:
        """
        Instantiate an :class:`ID3v2Flags` object from a byte.

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
        flags : minim.media.metadata.ID3v2Flags
            Flags for ID3v2 tags.
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
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )

    @property
    def is_unsynchronized(self) -> bool:
        """
        Whether the current tag has had unsynchronization applied to
        avoid false MPEG frame sync patterns in the metadata.
        """
        return self._is_unsynchronized

    @is_unsynchronized.setter
    def is_unsynchronized(self, value: bool, /) -> None:
        validate_type("is_unsynchronized", value, bool)
        self._is_unsynchronized = value

    @property
    def has_extended_header(self) -> bool:
        """
        Whether the current tag contains an extended header immediately
        after the main ID3v2 header.
        """
        return self._has_extended_header

    @has_extended_header.setter
    def has_extended_header(self, value: bool, /) -> bool:
        validate_type("has_extended_header", value, bool)
        self._has_extended_header = value

    @property
    def is_experimental(self) -> None:
        """
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
        Whether the current tag has compressed data.
        """
        return self._is_compressed

    @is_compressed.setter
    def is_compressed(self, value: bool, /) -> None:
        validate_type("is_compressed", value, bool)
        self._is_compressed = value

    @property
    def is_update(self) -> bool:
        """
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
        Tag restrictions byte.
        """
        return self._tag_restrictions

    @tag_restrictions.setter
    def tag_restrictions(self, value: int | None, /) -> None:
        if value is not None:
            validate_number("tag_restrictions", value, int, 0, 255)
        self._tag_restrictions = value

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the ID3v2 flags to a bytestream.

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
            Bytestream containing the ID3v2 flags.
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
        "_key_index",
        "_unknown_index",
    )

    def __init__(
        self,
        frames: OrderedCollection[ID3v2Frame],
        /,
        *,
        flags: ID3v2Flags | None = None,
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
        """
        if not isinstance(frames, ORDERED_COLLECTION_TYPES):
            frames = [frames]

        self._frames = _frames = []
        self._class_index = class_index = defaultdict(list)
        self._key_index = key_index = defaultdict(dict)
        for frame_idx, frame in enumerate(frames):
            validate_type(f"frames[{frame_idx}]", frame, ID3v2Frame)
            _frames.append(frame)
            frame_cls = type(frame)
            class_index[frame_cls].append(frame)
            if frame._allow_multiple:
                key_index[frame_cls][frame._key] = frame

        if flags is None:
            self._flags = ID3v2Flags()
        else:
            validate_type("flags", flags, ID3v2Flags)
            self._flags = flags

    @classmethod
    def from_stream(
        cls, stream: BytesLike, /, *, strict: bool = True
    ) -> ID3v2:
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
        stream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
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

        offset = 10
        tag_end = offset + decode_32_bit_synchsafe_int(*tag_length)
        obj = cls.__new__(cls)
        obj._frames = frames = []
        obj._class_index = class_index = defaultdict(list)
        obj._key_index = key_index = defaultdict(dict)
        obj._unknown_index = unknown_index = defaultdict(list)
        match tag_version := (2, minor, patch):
            case (2, 4, _):
                obj._flags = flags = ID3v2Flags._from_byte_2_4(
                    flags, strict=strict
                )
                if flags.is_unsynchronized:
                    stream = (
                        stream[offset:tag_end]
                        .tobytes()
                        .replace(b"\xff\x00", b"\xff")
                    )
                    offset = 0
                    tag_end = len(stream)

                if flags.has_extended_header:
                    flag_byte = stream[offset + 5]
                    if strict and flag_byte & 0x8F:
                        raise ValueError(
                            "Non-zero bits found in reserved section "
                            "of ID3 extended header flags byte."
                        )
                    flags._is_update = is_update = bool((flag_byte >> 7) & 1)
                    flags._has_crc = has_crc = bool((flag_byte >> 6) & 1)
                    if bool((flag_byte >> 5) & 1):
                        flags._tag_restrictions = stream[
                            offset + 7 + is_update + 6 * has_crc
                        ]
                    offset += decode_32_bit_synchsafe_int(
                        *stream[offset : offset + 4]
                    )

                while offset < tag_end:
                    if not stream[offset]:
                        frames.append(
                            ID3v2Padding.from_stream(
                                stream[offset:], strict=strict
                            )
                        )
                        break

                    frame_id, *frame_length = (
                        cls._STRUCT_PARTIAL_FRAME_HEADER_2_4.unpack_from(
                            stream, offset
                        )
                    )
                    end_offset = (
                        offset
                        + 10
                        + decode_32_bit_synchsafe_int(*frame_length)
                    )
                    frame_cls = ID3v2Frame._get_class(frame_id)
                    frame = frame_cls._from_stream_2_4(
                        stream[offset:end_offset], strict=strict
                    )
                    if frame_cls is UnknownID3v2Frame:
                        frames.append(frame)
                        class_index[frame_cls].append(frame)
                        unknown_index[frame._frame_id].append(frame)
                    elif frame_cls._allow_multiple:
                        if (
                            strict
                            and (_frames := key_index.get(frame_cls))
                            and frame._key in _frames
                        ):
                            frame_id = frame_id.decode(encoding="ascii")
                            raise ValueError(
                                f"Duplicate {frame_id} frame found."
                            )
                        frames.append(frame)
                        class_index[frame_cls].append(frame)
                        if frame._key:
                            key_index[frame_cls][frame._key] = frame
                    else:
                        if existing_frame := class_index.get(frame_cls):
                            if strict:
                                frame_id = frame_id.decode(encoding="ascii")
                                raise ValueError(
                                    f"Duplicate {frame_id} frame found."
                                )
                            raise NotImplementedError  # TODO: Merge
                        else:
                            frames.append(frame)
                            class_index[frame_cls].append(frame)
                    offset = end_offset + 10 * flags.has_footer
            case (2, 3, _):
                obj._flags = flags = ID3v2Flags._from_byte_2_3(
                    flags, strict=strict
                )
                if flags.is_unsynchronized:
                    stream = (
                        stream[offset:tag_end]
                        .tobytes()
                        .replace(b"\xff\x00", b"\xff")
                    )
                    offset = 0
                    tag_end = len(stream)

                if flags.has_extended_header:
                    flag_byte = stream[offset + 4]
                    if strict and (flag_byte & 0x80 or stream[offset + 5]):
                        raise ValueError(
                            "Non-zero bits found in reserved section "
                            "of ID3 extended header flags byte."
                        )
                    flags._has_crc = bool(flag_byte >> 8)
                    offset += int.from_bytes(stream[offset : offset + 4]) + 4

                while offset < tag_end:
                    if not stream[offset]:
                        frames.append(
                            ID3v2Padding.from_stream(
                                stream[offset:], strict=strict
                            )
                        )
                        break

                    frame_id, frame_length = (
                        cls._STRUCT_PARTIAL_FRAME_HEADER_2_3.unpack_from(
                            stream, offset
                        )
                    )
                    end_offset = offset + 10 + frame_length
                    frame_cls = ID3v2Frame._get_class(frame_id)
                    frame = frame_cls._from_stream_2_3(
                        stream[offset:end_offset], strict=strict
                    )
                    if frame_cls is UnknownID3v2Frame:
                        frames.append(frame)
                        class_index[frame_cls].append(frame)
                        unknown_index[frame._frame_id].append(frame)
                    elif frame_cls._allow_multiple:
                        if (
                            strict
                            and (_frames := key_index.get(frame_cls))
                            and frame._key in _frames
                        ):
                            frame_id = frame_id.decode(encoding="ascii")
                            raise ValueError(
                                f"Duplicate {frame_id} frame found."
                            )
                        frames.append(frame)
                        class_index[frame_cls].append(frame)
                        if frame._key:
                            key_index[frame_cls][frame._key] = frame
                    else:
                        if existing_frame := class_index.get(frame_cls):
                            if strict:
                                frame_id = frame_id.decode(encoding="ascii")
                                raise ValueError(
                                    f"Duplicate {frame_id} frame found."
                                )
                            raise NotImplementedError  # TODO: Merge
                        else:
                            frames.append(frame)
                            class_index[frame_cls].append(frame)
                    offset = end_offset
            case (2, 2, _):
                obj._flags = flags = ID3v2Flags._from_byte_2_2(
                    flags, strict=strict
                )
                if flags.is_compressed:
                    return obj
                if flags.is_unsynchronized:
                    stream = (
                        stream[offset:tag_end]
                        .tobytes()
                        .replace(b"\xff\x00", b"\xff")
                    )
                    tag_end = offset + len(stream)

                raise NotImplementedError  # TODO
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )

        return obj

    @property
    def album(self) -> list[str] | None:
        """
        :code:`TAL`/:code:`TALB` – Title of the album or collection.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TALB")):
            return frames[-1]._text_info.copy()

    @album.setter
    def album(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def album_artist(self) -> list[str] | None:
        """
        :code:`TP2`/:code:`TPE2` – Main artists credited for the entire
        album or collection.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TPE2")):
            return frames[-1]._text_info.copy()

    @album_artist.setter
    def album_artist(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def artist(self) -> list[str] | None:
        """
        :code:`TP1`/:code:`TPE1` – Main artists of the recording (e.g.,
        the performing band or singers in popular music, the composers
        for classical music, or the authors of the original text in
        audiobooks).
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TPE1")):
            return frames[-1]._text_info.copy()

    @artist.setter
    def artist(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def bpm(self) -> list[str] | None:
        """
        :code:`TBP`/:code:`TBPM` – Tempo in beats per minute (BPM).
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TBPM")):
            return frames[-1]._text_info.copy()

    @bpm.setter
    def bpm(
        self,
        value: float | str | OrderedCollection[int | float | str],
        /,
    ) -> None: ...

    @property
    def comment(self) -> list[str] | None:
        """
        :code:`COM`/:code:`COMM` – Free-form comments.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"COMM")):
            return [frame._comment for frame in frames]

    @comment.setter
    def comment(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def compilation(self) -> list[str] | None:
        """
        :code:`TCP`/:code:`TCMP` – Whether the recording is part of a
        compilation.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TCMP")):
            return frames[-1]._text_info.copy()

    @compilation.setter
    def compilation(
        self, value: bool | int | str | OrderedCollection[bool | int | str], /
    ) -> None: ...

    @property
    def composer(self) -> list[str] | None:
        """
        :code:`TCM`/:code:`TCOM` – Composers or songwriters.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TCOM")):
            return frames[-1]._text_info.copy()

    @composer.setter
    def composer(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def contact(self) -> list[str] | None:
        """
        :code:`TXX:CONTACT`/:code:`TXXX:CONTACT` – Contact information
        for the creators or distributors.
        """
        if frame := next(
            (
                self._key_index.get(ID3v2TXXXFrame, {}).get(key)
                for key in ["CONTACT", "contact", "Contact"]
            ),
            None,
        ):
            return frame._text_info.copy()

    @contact.setter
    def contact(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def copyright(self) -> list[str] | None:
        """
        :code:`TCR`/:code:`TCOP` – Copyright attribution.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TCOP")):
            return frames[-1]._text_info.copy()

    @copyright.setter
    def copyright(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def date(self) -> list[str] | None:
        """
        :code:`TYE` + :code:`TDA` + :code:`TIM`/:code:`TYER` +
        :code:`TDAT` + :code:`TIME`/:code:`TDRC`/:code:`TDRL` –
        Recording or release date.
        """
        if frames := (
            self._class_index.get(ID3v2Frame._get_class(b"TDRC"))
            or self._class_index.get(ID3v2Frame._get_class(b"TDRL"))
        ):
            return frames[-1]._text_info.copy()

    @date.setter
    def date(
        self, value: str | datetime | OrderedCollection[str | datetime], /
    ) -> None: ...

    @property
    def description(self) -> list[str] | None:
        """
        :code:`TXX:DESCRIPTION`/:code:`TXXX:DESCRIPTION` – General
        description.
        """
        if frame := next(
            (
                self._key_index.get(ID3v2TXXXFrame, {}).get(key)
                for key in ["DESCRIPTION", "description", "Description"]
            ),
            None,
        ):
            return frame._text_info.copy()

    @description.setter
    def description(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def disc_number(self) -> list[str] | None:
        """
        :code:`TPA`/:code:`TPOS` – Disc number within a multi-disc set.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TPOS")):
            return [str(disc.number) for disc in frames[-1]._disc]

    @disc_number.setter
    def disc_number(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    def disc_total(self) -> list[str | None] | None:
        """
        :code:`TPA`/:code:`TPOS` – Total number of discs.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TPOS")):
            return [str(disc.total) for disc in frames[-1]._disc]

    @disc_total.setter
    def disc_total(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    def encoder(self) -> list[str] | None:
        """
        :code:`TSS`/:code:`TSSE` – Software or hardware used for
        encoding, or the person or organization that encoded the audio
        file.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TSSE")):
            return frames[-1]._text_info.copy()

    @encoder.setter
    def encoder(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def genre(self) -> list[str] | None:
        """
        :code:`TCO`/:code:`TCON` –  Musical genres.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TCON")):
            return frames[-1]._text_info.copy()

    @genre.setter
    def genre(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def grouping(self) -> list[str] | None:
        """
        :code:`TT1`/:code:`TIT1` – Content group description.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TIT1")):
            return frames[-1]._text_info.copy()

    @grouping.setter
    def grouping(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def isrc(self) -> list[str] | None:
        """
        :code:`TRC`/:code:`TSRC` – International Standard Recording Code
        (ISRC).
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TSRC")):
            return frames[-1]._text_info.copy()

    @isrc.setter
    def isrc(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def label(self) -> list[str] | None:
        """
        :code:`TPB`/:code:`TPUB` – Publishers or record labels.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TPUB")):
            return frames[-1]._text_info.copy()

    @label.setter
    def label(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def license(self) -> list[str] | None:
        """
        :code:`TXX:LICENSE`/:code:`TXXX:LICENSE` - License information.
        """
        if frame := next(
            (
                self._key_index.get(ID3v2TXXXFrame, {}).get(key)
                for key in ["LICENSE", "license", "License"]
            ),
            None,
        ):
            return frame._text_info.copy()

    @license.setter
    def license(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def location(self) -> list[str] | None:
        """
        :code:`TXX:LOCATION`/:code:`TXXX:LOCATION` – Recording
        locations.
        """
        if frame := next(
            (
                self._key_index.get(ID3v2TXXXFrame, {}).get(key)
                for key in ["LOCATION", "location", "Location"]
            ),
            None,
        ):
            return frame._text_info.copy()

    @location.setter
    def location(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def lyrics(self) -> list[str] | None:
        """
        :code:`SLT`/:code:`SYLT` (synchronized) or
        :code:`ULT`/:code:`USLT` (unsynchronized) – Lyrics or
        transcription.
        """
        lyrics = []
        if frames := self._class_index.get(ID3v2Frame._get_class(b"SYLT")):
            lyrics.extend(frame._lyrics for frame in frames)
        if frames := self._class_index.get(ID3v2Frame._get_class(b"USLT")):
            lyrics.extend(frame._lyrics for frame in frames)
        return lyrics

    @lyrics.setter
    def lyrics(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def performer(self) -> list[str] | None:
        """
        :code:`TP3`/:code:`TPE3` – Performers (e.g., the conductor,
        orchestra, and/or soloists in classical music, or the narrator
        in audiobooks).
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TPE3")):
            return frames[-1]._text_info.copy()

    @performer.setter
    def performer(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def title(self) -> list[str] | None:
        """
        :code:`TT2`/:code:`TIT2` – Title of the recording.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TIT2")):
            return frames[-1]._text_info.copy()

    @title.setter
    def title(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def track_number(self) -> list[str] | None:
        """
        :code:`TRK`/:code:`TRCK` – Track number within the album or
        collection.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TRCK")):
            return [str(track.number) for track in frames[-1]._track]

    @track_number.setter
    def track_number(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    def track_total(self) -> list[str | None] | None:
        """
        :code:`TRK`/:code:`TRCK` – Total number of tracks.
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TRCK")):
            return [str(track.total) for track in frames[-1]._track]

    @track_total.setter
    def track_total(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    def version(self) -> list[str] | None:
        """
        :code:`TT3`/:code:`TIT3` – Version of the recording (e.g., remix
        information).
        """
        if frames := self._class_index.get(ID3v2Frame._get_class(b"TIT3")):
            return frames[-1]._text_info.copy()

    @version.setter
    def version(self, value: str | OrderedCollection[str], /) -> None: ...

    def get(
        self,
        frame_types: bytes | ID3v2Frame | Collection[bytes | ID3v2Frame],
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

        Returns
        -------
        attributes : Any or dict[str, Any]
            Track attributes. If `fields` is a collection of strings, a
            dictionary mapping field names to their corresponding values
            is returned.
        """
        # TODO

    def set(self, **kwargs: dict[str, Any]) -> None:
        """
        Set track attributes.

        Parameters
        ----------
        **kwargs : dict[str, Any]
            Key–value pairs of track attributes.
        """
        # TODO

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the ID3v2 tag to a bytestream.

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
            Bytestream containing the serialized ID3v2 tag.
        """
        # TODO
