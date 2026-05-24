from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import struct
from typing import TYPE_CHECKING

from ...._utility import (
    decode_32_bit_synchsafe_int,
    join_values,
    set_obj_attr,
    validate_number,
    validate_type,
)
from ..._shared import as_buffer
from .._shared import AudioTags
from ._frames import ID3v2Frame, UnknownID3v2Frame, ID3v2Padding
from . import TAG_VERSIONS

if TYPE_CHECKING:
    from typing import Any

    from ...._types import BytesLike, Collection, OrderedCollection


@dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class ID3v2Flags:
    """
    Flags for ID3v2 tags.

    Parameters
    ----------
    is_unsynchronized : bool; keyword-only; default: :code:`False`
        Whether the current tag has had unsynchronization applied to
        avoid false MPEG frame sync patterns in the metadata.

    has_extended_header : bool; keyword-only; default: :code:`False`
        Whether the current tag contains an extended header immediately
        after the main ID3v2 header.

    is_experimental : bool; keyword-only; default: :code:`False`
        Whether the current tag is marked as experimental by the
        encoder.

    has_footer : bool; keyword-only; default: :code:`False`
        Whether the current tag includes a 10-byte footer following the
        tag data.

    is_compressed : bool; keyword-only; default: :code:`False`
        Whether the current tag has compressed data.
    """

    #: Whether the current tag has had unsynchronization applied to
    #: avoid false MPEG frame sync patterns in the metadata.
    is_unsynchronized: bool = False
    #: Whether the current tag contains an extended header immediately
    #: after the main ID3v2 header.
    has_extended_header: bool = False
    #: Whether the current tag is marked as experimental by the encoder.
    is_experimental: bool = False
    #: Whether the current tag includes a 10-byte footer following the
    #: tag data.
    has_footer: bool = False
    #: Whether the current tag has compressed data.
    is_compressed: bool = False

    def __post_init__(self) -> None:
        validate_type("is_unsynchronized", self.is_unsynchronized, bool)
        validate_type("has_extended_header", self.has_extended_header, bool)
        validate_type("is_experimental", self.is_experimental, bool)
        validate_type("has_footer", self.has_footer, bool)
        validate_type("is_compressed", self.is_compressed, bool)

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
        set_obj_attr(obj, "is_unsynchronized", bool(byte_ & 0x80))
        set_obj_attr(obj, "has_extended_header", False)
        set_obj_attr(obj, "is_experimental", False)
        set_obj_attr(obj, "has_footer", False)
        set_obj_attr(obj, "is_compressed", bool(byte_ & 0x40))
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
        set_obj_attr(obj, "is_unsynchronized", bool(byte_ & 0x80))
        set_obj_attr(obj, "has_extended_header", bool(byte_ & 0x40))
        set_obj_attr(obj, "is_experimental", bool(byte_ & 0x20))
        set_obj_attr(obj, "has_footer", False)
        set_obj_attr(obj, "is_compressed", False)
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
        set_obj_attr(obj, "is_unsynchronized", bool(byte_ & 0x80))
        set_obj_attr(obj, "has_extended_header", bool(byte_ & 0x40))
        set_obj_attr(obj, "is_experimental", bool(byte_ & 0x20))
        set_obj_attr(obj, "has_footer", bool(byte_ & 0x10))
        set_obj_attr(obj, "is_compressed", False)
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


class ID3v2(AudioTags):
    """
    ID3v2 metadata container.
    """

    _STRUCT_ID3_HEADER = struct.Struct(">3s7B")
    _STRUCT_PARTIAL_FRAME_HEADER_2_3 = struct.Struct(">4sI")
    _STRUCT_PARTIAL_FRAME_HEADER_2_4 = struct.Struct(">4s4B")

    __slots__ = ("_flags", "_frames", "_tag_version")

    # def __init__(
    #     self,
    #     frames: OrderedCollection[ID3v2Frame],
    #     /,
    #     tag_version: str | tuple[int, int, int],
    #     *,
    #     flags: int | dict[str, bool] | ID3v2Flags = 0,
    # ) -> None:
    #     """ """

    @classmethod
    def from_stream(
        cls, stream: BytesLike, /, *, strict: bool = True
    ) -> ID3v2:
        """ """
        stream = as_buffer(stream)
        frame_id, minor, patch, flags, *tag_length = (
            cls._STRUCT_ID3_HEADER.unpack_from(stream)
        )
        if frame_id != b"ID3":
            raise ValueError("`stream` does not contain an ID3v2 tag.")

        offset = 10
        tag_end = offset + decode_32_bit_synchsafe_int(*tag_length)
        obj = cls.__new__(cls)
        obj._tag_version = tag_version = 2, minor, patch
        obj._frames = frames = []
        match tag_version:
            case (2, 4, _):
                obj._flags = flags = ID3v2Flags._from_byte_2_4(
                    flags, strict=strict
                )
                while offset < tag_end:
                    if not stream[offset]:
                        frames.append(
                            ID3v2Padding.from_stream(stream[offset:])
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

                    # TODO: Temporary skip.
                    if frame_id in {b"TRCK", b"TPOS", b"TDRC", b"APIC"}:
                        offset = end_offset
                        continue

                    frames.append(
                        (
                            ID3v2Frame._get_class(frame_id)
                            or UnknownID3v2Frame
                        ).from_stream(
                            stream[offset:end_offset],
                            tag_version=tag_version,
                            strict=strict,
                        )
                    )
                    offset = end_offset
            case (2, 3, _):
                raise NotImplementedError  # TODO
            case (2, 2, _):
                raise NotImplementedError  # TODO
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )

        return obj

    @property
    def album(self) -> str | list[str] | None:
        """
        :code:`TAL`/:code:`TALB` – Title of the album or collection.
        """
        ...

    @album.setter
    def album(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def album_artist(self) -> str | list[str] | None:
        """
        :code:`TP2`/:code:`TPE2` – Main artists credited for the entire
        album or collection.
        """
        ...

    @album_artist.setter
    def album_artist(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def artist(self) -> str | list[str] | None:
        """
        :code:`TP1`/:code:`TPE1` – Main artists of the recording (e.g.,
        the performing band or singers in popular music, the composers
        for classical music, or the authors of the original text in
        audiobooks).
        """
        ...

    @artist.setter
    def artist(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def bpm(self) -> int | list[str] | None:
        """
        :code:`TBP`/:code:`TBPM` – Tempo in beats per minute (BPM).
        """
        ...

    @bpm.setter
    def bpm(
        self,
        value: int | float | str | OrderedCollection[int | float | str],
        /,
    ) -> None: ...

    @property
    def comment(self) -> str | list[str] | None:
        """
        :code:`COM`/:code:`COMM` – Free-form comments.
        """
        ...

    @comment.setter
    def comment(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def compilation(self) -> bool | list[str] | None:
        """
        :code:`TCP`/:code:`TCMP` – Whether the recording is part of a
        compilation.
        """
        ...

    @compilation.setter
    def compilation(
        self, value: bool | int | str | OrderedCollection[bool | int | str], /
    ) -> None: ...

    @property
    def composer(self) -> str | list[str] | None:
        """
        :code:`TCM`/:code:`TCOM` – Composers or songwriters.
        """
        ...

    @composer.setter
    def composer(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def contact(self) -> str | list[str] | None:
        """
        Contact information for the creators or distributors.
        """
        ...

    @contact.setter
    def contact(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def copyright(self) -> str | list[str] | None:
        """
        :code:`TCR`/:code:`TCOP` – Copyright attribution.
        """
        ...

    @copyright.setter
    def copyright(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def date(self) -> str | list[str] | None:
        """
        Release date.
        """
        ...

    @date.setter
    def date(
        self, value: str | datetime | OrderedCollection[str | datetime], /
    ) -> None: ...

    @property
    def description(self) -> str | list[str] | None:
        """
        :code:`TT3`/:code:`TIT3` – General description.
        """
        ...

    @description.setter
    def description(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def disc_number(self) -> int | str | list[str] | None:
        """
        :code:`TPA`/:code:`TPOS` – Disc number within a multi-disc set.
        """
        ...

    @disc_number.setter
    def disc_number(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    def disc_total(self) -> int | str | list[str] | None:
        """
        :code:`TPA`/:code:`TPOS` – Total number of discs.
        """
        ...

    @disc_total.setter
    def disc_total(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    def encoder(self) -> str | list[str] | None:
        """
        :code:`TSS`/:code:`TSSE` – Software or hardware used for
        encoding, or the person or organization that encoded the audio
        file.
        """
        ...

    @encoder.setter
    def encoder(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def genre(self) -> str | list[str] | None:
        """
        :code:`TCO`/:code:`TCON` –  Musical genres.
        """
        ...

    @genre.setter
    def genre(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def grouping(self) -> str | list[str] | None:
        """
        :code:`TT1`/:code:`TIT1` – Content group description.
        """
        ...

    @grouping.setter
    def grouping(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def isrc(self) -> str | list[str] | None:
        """
        :code:`TRC`/:code:`TSRC` – International Standard Recording Code
        (ISRC).
        """
        ...

    @isrc.setter
    def isrc(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def label(self) -> str | list[str] | None:
        """
        :code:`TPB`/:code:`TPUB` – Publisher or record label.
        """
        ...

    @label.setter
    def label(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def license(self) -> str | list[str] | None:
        """
        License information.
        """
        ...

    @license.setter
    def license(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def location(self) -> str | list[str] | None:
        """
        Recording locations.
        """
        ...

    @location.setter
    def location(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def lyrics(self) -> str | list[str] | None:
        """
        :code:`SLT`/:code:`SYLT` (synchronized) or
        :code:`ULT`/:code:`USLT` (unsynchronized) – Lyrics or
        transcription.
        """
        ...

    @lyrics.setter
    def lyrics(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def performer(self) -> str | list[str] | None:
        """
        Performers (e.g., the conductor, orchestra, and/or soloists in
        classical music, or the narrator in audiobooks).
        """
        ...

    @performer.setter
    def performer(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def title(self) -> str | list[str] | None:
        """
        :code:`TT2`/:code:`TIT2` – Title of the recording.
        """
        ...

    @title.setter
    def title(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    def track_number(self) -> int | list[str] | None:
        """
        :code:`TRK`/:code:`TRCK` – Track number within the album or
        collection.
        """
        ...

    @track_number.setter
    def track_number(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    def track_total(self) -> int | list[str] | None:
        """
        :code:`TRK`/:code:`TRCK` – Total number of tracks.
        """
        ...

    @track_total.setter
    def track_total(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    def version(self) -> str | list[str] | None:
        """
        Version of the recording (e.g., remix information).
        """
        ...

    @version.setter
    def version(self, value: str | OrderedCollection[str], /) -> None: ...

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

    def set(self, **kwargs: dict[str, Any]) -> None:
        """
        Set track attributes.

        Parameters
        ----------
        **kwargs : dict[str, Any]
            Key–value pairs of track attributes.
        """
        ...
