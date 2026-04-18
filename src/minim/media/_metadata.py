from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from numbers import Real
import re
import struct
from typing import TYPE_CHECKING

from .. import __version__
from .._types import COLLECTION_TYPES, ORDERED_COLLECTION_TYPES
from .._utility import validate_numeric, validate_type

if TYPE_CHECKING:
    import mmap
    from typing import Any

    from .._types import Collection, OrderedCollection


class AudioMetadata(ABC):
    """
    Generic audio metadata container.
    """

    __slots__ = ()

    @staticmethod
    def _stringify(value: Any, /) -> Any:
        """
        Try to convert an arbitrary value to a string.

        Parameters
        ----------
        value : Any; positional-only
            Value to convert.

        Returns
        -------
        value : Any
            String representation of the value if it has a supported
            type, and the original value otherwise.
        """
        match value:
            case bool():
                return str(int(value))
            case datetime():
                return value.strftime("%Y-%m-%dT%H:%M:%SZ")
            case Real():
                return str(value)
            case _:
                return value

    @property
    @abstractmethod
    def album(self) -> str | list[str] | None:
        """
        Title of the album or collection.
        """
        ...

    @album.setter
    @abstractmethod
    def album(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def album_artist(self) -> str | list[str] | None:
        """
        Main artists credited for the entire album or collection.
        """
        ...

    @album_artist.setter
    @abstractmethod
    def album_artist(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def artist(self) -> str | list[str] | None:
        """
        Main artists of the recording (e.g., the performing band or
        singers in popular music, the composers for classical music, or
        the authors of the original text in audiobooks).
        """
        ...

    @artist.setter
    @abstractmethod
    def artist(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def bpm(self) -> int | list[str] | None:
        """
        Tempo in beats per minute (BPM).
        """
        ...

    @bpm.setter
    @abstractmethod
    def bpm(
        self,
        value: int | float | str | OrderedCollection[int | float | str],
        /,
    ) -> None: ...

    @property
    @abstractmethod
    def comment(self) -> str | list[str] | None:
        """
        Free-form comments.
        """
        ...

    @comment.setter
    @abstractmethod
    def comment(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def compilation(self) -> bool | list[str] | None:
        """
        Whether the recording is part of a compilation.
        """
        ...

    @compilation.setter
    @abstractmethod
    def compilation(
        self, value: bool | int | str | OrderedCollection[bool | int | str], /
    ) -> None: ...

    @property
    @abstractmethod
    def composer(self) -> str | list[str] | None:
        """
        Composers or songwriters.
        """
        ...

    @composer.setter
    @abstractmethod
    def composer(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def contact(self) -> str | list[str] | None:
        """
        Contact information for the creators or distributors.
        """
        ...

    @contact.setter
    @abstractmethod
    def contact(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def copyright(self) -> str | list[str] | None:
        """
        Copyright attribution.
        """
        ...

    @copyright.setter
    @abstractmethod
    def copyright(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def date(self) -> str | list[str] | None:
        """
        Release date.
        """
        ...

    @date.setter
    @abstractmethod
    def date(
        self, value: str | datetime | OrderedCollection[str | datetime], /
    ) -> None: ...

    @property
    @abstractmethod
    def description(self) -> str | list[str] | None:
        """
        General description.
        """
        ...

    @description.setter
    @abstractmethod
    def description(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def disc_number(self) -> int | str | list[str] | None:
        """
        Disc number within a multi-disc set.
        """
        ...

    @disc_number.setter
    @abstractmethod
    def disc_number(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    @abstractmethod
    def disc_total(self) -> int | str | list[str] | None:
        """
        Total number of discs.
        """
        ...

    @disc_total.setter
    @abstractmethod
    def disc_total(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    @abstractmethod
    def encoder(self) -> str | list[str] | None:
        """
        Software or hardware used for encoding, or the person or
        organization that encoded the audio file.
        """
        ...

    @encoder.setter
    @abstractmethod
    def encoder(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def genre(self) -> str | list[str] | None:
        """
        Musical genres.
        """
        ...

    @genre.setter
    @abstractmethod
    def genre(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def grouping(self) -> str | list[str] | None:
        """
        Content group description.
        """
        ...

    @grouping.setter
    @abstractmethod
    def grouping(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def isrc(self) -> str | list[str] | None:
        """
        International Standard Recording Code (ISRC).
        """
        ...

    @isrc.setter
    @abstractmethod
    def isrc(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def label(self) -> str | list[str] | None:
        """
        Publisher or record label.
        """
        ...

    @label.setter
    @abstractmethod
    def label(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def license(self) -> str | list[str] | None:
        """
        License information.
        """
        ...

    @license.setter
    @abstractmethod
    def license(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def location(self) -> str | list[str] | None:
        """
        Recording locations.
        """
        ...

    @location.setter
    @abstractmethod
    def location(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def lyrics(self) -> str | list[str] | None:
        """
        Lyrics or transcription.
        """
        ...

    @lyrics.setter
    @abstractmethod
    def lyrics(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def performer(self) -> str | list[str] | None:
        """
        Performers (e.g., the conductor, orchestra, and/or soloists in
        classical music, or the narrator in audiobooks).
        """
        ...

    @performer.setter
    @abstractmethod
    def performer(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def title(self) -> str | list[str] | None:
        """
        Title of the recording.
        """
        ...

    @title.setter
    @abstractmethod
    def title(self, value: str | OrderedCollection[str], /) -> None: ...

    @property
    @abstractmethod
    def track_number(self) -> int | list[str] | None:
        """
        Track number within the album or collection.
        """
        ...

    @track_number.setter
    @abstractmethod
    def track_number(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    @abstractmethod
    def track_total(self) -> int | list[str] | None:
        """
        Total number of tracks.
        """
        ...

    @track_total.setter
    @abstractmethod
    def track_total(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None: ...

    @property
    @abstractmethod
    def version(self) -> str | list[str] | None:
        """
        Version of the recording (e.g., remix information).
        """
        ...

    @version.setter
    @abstractmethod
    def version(self, value: str | OrderedCollection[str], /) -> None: ...

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def set(self, **kwargs: dict[str, Any]) -> None:
        """
        Set track attributes.

        Parameters
        ----------
        **kwargs : dict[str, Any]
            Key–value pairs of track attributes.
        """
        ...


class ID3(AudioMetadata):
    """
    ID3 metadata container.
    """

    __slots__ = ("_frames",)


class ItemListBox(AudioMetadata):
    """
    MP4 item list box (:code:`moov.udta.meta.ilst`) metadata container.
    """

    __slots__ = ("_boxes",)


class VorbisComment(AudioMetadata):
    """
    Vorbis comment metadata container.

    .. seealso::

        `Ogg Vorbis I format specification:
        comment field and header specification
        <https://www.xiph.org/vorbis/doc/v-comment.html>`_.
    """

    _UINT32_LE = struct.Struct("<I")

    _validators = {
        "BPM": lambda value: validate_numeric("BPM", value, int | float, 0),
        "COMPILATION": lambda value: validate_numeric(
            "COMPILATION", value, bool | int, 0, 1
        ),
    }

    __slots__ = "_fields", "_keep_empty", "_num_fields", "_vendor"

    def __init__(
        self,
        bytestream: bytes | bytearray | memoryview | "mmap.mmap" | None = None,
        /,
        *,
        keep_empty: bool = False,
    ) -> None:
        """
        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing a Vorbis comment metadata
            block.

        keep_empty : bool; keyword-only; default: :code:`False`
            Whether to keep field–value pairs with empty values.
        """
        validate_type("keep_empty", keep_empty, bool)
        self._keep_empty = keep_empty
        self._fields = {}

        if bytestream is None:
            self._num_fields = 0
            self._vendor = None
            return

        if not isinstance(bytestream, memoryview):
            try:
                bytestream = memoryview(bytestream)
            except TypeError:
                raise TypeError("`bytestream` must be a bytes-like object.")

        unpack = self._UINT32_LE.unpack_from
        size = self._UINT32_LE.size
        offset = 0

        # Read comment header
        (length,) = unpack(bytestream, offset)
        offset += size
        end_offset = offset + length
        self._vendor = bytestream[offset:end_offset]
        offset = end_offset
        (self._num_fields,) = unpack(bytestream, offset)
        offset += size

        # Read comment vectors
        normalize_key = self._normalize_key
        fields = self._fields
        for _ in range(self._num_fields):
            (length,) = unpack(bytestream, offset)
            offset += size
            end_offset = offset + length
            key, value = (
                bytestream[offset:end_offset].decode().split("=", maxsplit=1)
            )
            offset = end_offset
            if keep_empty or value:
                key = normalize_key(key)
                if key in fields:
                    fields[key].append(value)
                else:
                    fields[key] = [value]

    @staticmethod
    def _normalize_key(key: str, /) -> str:
        """
        Normalize a field name to conform to the Vorbis comment
        specification.

        Parameters
        ----------
        key : str; positional-only
            Field name to normalize.

        Returns
        -------
        key : str
            Normalized field name.
        """
        return re.sub("[^\x20-\x3c\x3e-\x7e]", "_", key.upper())

    @property
    def album(self) -> list[str] | None:
        """
        :code:`ALBUM` – Title of the album or collection.
        """
        return self.get("ALBUM")

    @album.setter
    def album(self, value: str | OrderedCollection[str], /) -> None:
        self.set(ALBUM=value)

    @property
    def album_artist(self) -> list[str] | None:
        """
        :code:`ALBUMARTIST` – Main artists credited for the entire album
        or collection.
        """
        return self.get("ALBUMARTIST")

    @album_artist.setter
    def album_artist(self, value: str | OrderedCollection[str], /) -> None:
        self.set(ALBUMARTIST=value)

    @property
    def artist(self) -> list[str] | None:
        """
        :code:`ARTIST` – Main artists of the recording (e.g., the
        performing band or singers in popular music, the composers for
        classical music, or the authors of the original text in
        audiobooks).
        """
        return self.get("ARTIST")

    @artist.setter
    def artist(self, value: str | OrderedCollection[str], /) -> None:
        self.set(ARTIST=value)

    @property
    def bpm(self) -> list[str] | None:
        """
        :code:`BPM` – Tempo in beats per minute (BPM).
        """
        return self.get("BPM")

    @bpm.setter
    def bpm(
        self,
        value: int | float | str | OrderedCollection[int | float | str],
        /,
    ) -> None:
        self.set(BPM=value)

    @property
    def comment(self) -> list[str] | None:
        """
        :code:`COMMENT` – Free-form comments.
        """
        return self.get("COMMENT")

    @comment.setter
    def comment(self, value: str | OrderedCollection[str], /) -> None:
        self.set(COMMENT=value)

    @property
    def compilation(self) -> list[str] | None:
        """
        :code:`COMPILATION` – Whether the recording is part of a
        compilation.
        """
        return self.get("COMPILATION")

    @compilation.setter
    def compilation(
        self, value: bool | int | str | OrderedCollection[bool | int | str], /
    ) -> None:
        self.set(COMPILATION=value)

    @property
    def composer(self) -> list[str] | None:
        """
        :code:`COMPOSER` – Composers or songwriters.
        """
        return self.get("COMPOSER")

    @composer.setter
    def composer(self, value: str | OrderedCollection[str], /) -> None:
        self.set(COMPOSER=value)

    @property
    def contact(self) -> list[str] | None:
        """
        :code:`CONTACT` – Contact information for the creators or
        distributors.
        """
        return self.get("CONTACT")

    @contact.setter
    def contact(self, value: str | OrderedCollection[str], /) -> None:
        self.set(CONTACT=value)

    @property
    def copyright(self) -> list[str] | None:
        """
        :code:`COPYRIGHT` – Copyright attribution.
        """
        return self.get("COPYRIGHT")

    @copyright.setter
    def copyright(self, value: str | OrderedCollection[str], /) -> None:
        self.set(COPYRIGHT=value)

    @property
    def date(self) -> list[str] | None:
        """
        :code:`DATE` – Release date.
        """
        return self.get("DATE")

    @date.setter
    def date(
        self, value: str | datetime | OrderedCollection[str | datetime], /
    ) -> None:
        self.set(DATE=value)

    @property
    def description(self) -> list[str] | None:
        """
        :code:`DESCRIPTION` – General description.
        """
        return self.get("DESCRIPTION")

    @description.setter
    def description(self, value: str | OrderedCollection[str], /) -> None:
        self.set(DESCRIPTION=value)

    @property
    def disc_number(self) -> list[str] | None:
        """
        :code:`DISCNUMBER` – Disc number within a multi-disc set.
        """
        return self.get("DISCNUMBER")

    @disc_number.setter
    def disc_number(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None:
        self.set(DISCNUMBER=value)

    @property
    def disc_total(self) -> list[str] | None:
        """
        :code:`DISCTOTAL` – Total number of discs.
        """
        return self.get("DISCTOTAL")

    @disc_total.setter
    def disc_total(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None:
        self.set(DISCTOTAL=value)

    @property
    def encoder(self) -> list[str] | None:
        """
        :code:`ENCODER` – Software or hardware used for encoding, or the
        person or organization that encoded the audio file.
        """
        return self.get("ENCODER")

    @encoder.setter
    def encoder(self, value: str | OrderedCollection[str], /) -> None:
        self.set(ENCODER=value)

    @property
    def genre(self) -> list[str] | None:
        """
        :code:`GENRE` – Musical genres.
        """
        return self.get("GENRE")

    @genre.setter
    def genre(self, value: str | OrderedCollection[str], /) -> None:
        self.set(GENRE=value)

    @property
    def grouping(self) -> list[str] | None:
        """
        :code:`GROUPING` – Content group description.
        """
        return self.get("GROUPING")

    @grouping.setter
    def grouping(self, value: str | OrderedCollection[str], /) -> None:
        self.set(GROUPING=value)

    @property
    def isrc(self) -> list[str] | None:
        """
        :code:`ISRC` – International Standard Recording Code (ISRC).
        """
        return self.get("ISRC")

    @isrc.setter
    def isrc(self, value: str | OrderedCollection[str], /) -> None:
        self.set(ISRC=value)

    @property
    def label(self) -> list[str] | None:
        """
        :code:`LABEL` – Publisher or record label.
        """
        return self.get("LABEL")

    @label.setter
    def label(self, value: str | OrderedCollection[str], /) -> None:
        self.set(LABEL=value)

    @property
    def license(self) -> list[str] | None:
        """
        :code:`LICENSE` – License information.
        """
        return self.get("LICENSE")

    @license.setter
    def license(self, value: str | OrderedCollection[str], /) -> None:
        self.set(LICENSE=value)

    @property
    def location(self) -> list[str] | None:
        """
        :code:`LOCATION` – Recording locations.
        """
        return self.get("LOCATION")

    @location.setter
    def location(self, value: str | OrderedCollection[str], /) -> None:
        self.set(LOCATION=value)

    @property
    def lyrics(self) -> list[str] | None:
        """
        :code:`LYRICS` – Lyrics or transcription.
        """
        return self.get("LYRICS")

    @lyrics.setter
    def lyrics(self, value: str | OrderedCollection[str], /) -> None:
        self.set(LYRICS=value)

    @property
    def performer(self) -> list[str] | None:
        """
        :code:`PERFORMER` – Performers (e.g., the conductor, orchestra,
        and/or soloists in classical music, or the narrator in
        audiobooks).
        """
        return self.get("PERFORMER")

    @performer.setter
    def performer(self, value: str | OrderedCollection[str], /) -> None:
        self.set(PERFORMER=value)

    @property
    def title(self) -> list[str] | None:
        """
        :code:`TITLE` – Title of the recording.
        """
        return self.get("TITLE")

    @title.setter
    def title(self, value: str | OrderedCollection[str], /) -> None:
        self.set(TITLE=value)

    @property
    def track_number(self) -> list[str] | None:
        """
        :code:`TRACKNUMBER` – Track number within the album or collection.
        """
        return self.get("TRACKNUMBER")

    @track_number.setter
    def track_number(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None:
        self.set(TRACKNUMBER=value)

    @property
    def track_total(self) -> list[str] | None:
        """
        :code:`TRACKTOTAL` – Total number of tracks.
        """
        return self.get("TRACKTOTAL")

    @track_total.setter
    def track_total(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None:
        self.set(TRACKTOTAL=value)

    @property
    def vendor(self) -> bytes | None:
        """
        Vendor name.
        """
        return self._vendor

    @vendor.setter
    def vendor(self, value: bytes | str, /) -> None:
        validate_type("vendor", value, bytes | str)
        if isinstance(value, str):
            value = value.encode("utf-8")
        self._vendor = value

    @property
    def version(self) -> list[str] | None:
        """
        :code:`VERSION` – Version of the recording (e.g., remix
        information).
        """
        return self.get("VERSION")

    @version.setter
    def version(self, value: str | OrderedCollection[str], /) -> None:
        self.set(VERSION=value)

    def append(self, **kwargs: Any) -> None:
        """
        Append track attributes.

        .. note::

           The Vorbis comment specification allows for arbitrary
           case-insensitive field names consisting of only ASCII
           characters 0x20 through 0x7D, excluding 0x3D (:code:`=`).
           However, Python identifiers are case-sensitive, can contain
           Unicode characters, and have restrictions such as not
           containing whitespace or starting with a digit.

           To pass in fields with names that do not conform to Python
           identifier rules, unpack a dictionary containing key–value
           pairs.

           All field names will have illegal characters replaced with
           underscores and be converted to uppercase. It is possible
           that two fields with different invalid names are treated as
           the same field if their sanitized names are identical.

        Parameters
        ----------
        **kwargs
            Key–value pairs of track attributes.
        """
        keep_empty = self._keep_empty
        for key, value in kwargs.items():
            key = self._normalize_key(key)
            new_key = key not in self._fields
            if new_key:
                self._fields[key] = values = []
            else:
                values = self._fields[key]
            validate = self._validators.get(key)
            has_validator = validate is not None

            if isinstance(value := self._stringify(value), str):
                if keep_empty or value:
                    if has_validator:
                        validate(value)
                    values.append(value)
            elif isinstance(value, ORDERED_COLLECTION_TYPES):
                for item in value:
                    if isinstance(item := self._stringify(item), str):
                        if keep_empty or item:
                            if has_validator:
                                validate(item)
                            values.append(item)
                    else:
                        raise TypeError(
                            f"The value {item!r} in field '{key}' has "
                            f"unsupported type {type(item).__name__}."
                        )
            else:
                raise TypeError(
                    f"The value {value!r} for field '{key}' has "
                    f"unsupported type {type(value).__name__}."
                )

            if new_key:
                if values:
                    self._num_fields += 1
                else:
                    del self._fields[key]

    def get(self, fields: str | Collection[str], /) -> list[str] | None:
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
        if not (
            isinstance(fields, str)
            or (
                isinstance(fields, COLLECTION_TYPES)
                and all(isinstance(field, str) for field in fields)
            )
        ):
            raise TypeError(
                "`fields` must be a string or a collection of strings."
            )

        if isinstance(fields, str):
            return self._fields.get(fields)

        return {field: self._fields.get(field) for field in fields}

    def set(self, **kwargs: Any) -> None:
        """
        Set track attributes.

        .. note::

           The Vorbis comment specification allows for arbitrary
           case-insensitive field names consisting of only ASCII
           characters 0x20 through 0x7D, excluding 0x3D (:code:`=`).
           However, Python identifiers are case-sensitive, can contain
           Unicode characters, and have restrictions such as not
           containing whitespace or starting with a digit.

           To pass in fields with names that do not conform to Python
           identifier rules, unpack a dictionary containing key–value
           pairs.

           All field names will have illegal characters replaced with
           underscores and be converted to uppercase. It is possible
           that two fields with different invalid names are treated as
           the same field if their sanitized names are identical.

        Parameters
        ----------
        **kwargs
            Key–value pairs of track attributes.
        """
        keep_empty = self._keep_empty
        for key, value in kwargs.items():
            key = self._normalize_key(key)
            new_key = key not in self._fields
            validate = self._validators.get(key)
            has_validator = validate is not None
            if isinstance(value := self._stringify(value), str):
                if keep_empty or value:
                    if has_validator:
                        validate(value)
                    self._fields[key] = [value]
                    if new_key:
                        self._num_fields += 1
            elif isinstance(value, ORDERED_COLLECTION_TYPES):
                self._fields[key] = values = []
                for item in value:
                    if isinstance(item := self._stringify(item), str):
                        if keep_empty or item:
                            if has_validator:
                                validate(item)
                            values.append(item)
                    else:
                        raise TypeError(
                            f"The value {item!r} in field '{key}' has "
                            f"unsupported type {type(item).__name__}."
                        )
                if values:
                    if new_key:
                        self._num_fields += 1
                else:
                    del self._fields[key]
                    if not new_key:
                        self._num_fields -= 1
            else:
                raise TypeError(
                    f"The value {value!r} for field '{key}' has "
                    f"unsupported type {type(value).__name__}."
                )

    def serialize(self, *, include_framing_bit: bool = False) -> bytes:
        """
        Serialize metadata to a bytestream.

        Parameters
        ----------
        include_framing_bit : bool; keyword-only; default: :code:`False`
            Whether to include a framing bit (single byte of value 1) at
            the end of the bytestream. Required only by the Ogg
            container format.

        Returns
        -------
        bytestream : bytes
            Bytestream containing the serialized Vorbis comment block.
        """
        pack = self._UINT32_LE.pack
        vectors = [
            pack(
                len(vendor := self._vendor or f"Minim {__version__}".encode())
            ),
            vendor,
            pack(self._num_fields),
        ]
        for key, values in self._fields.items():
            for value in values:
                vectors.extend(
                    (
                        pack(len(field_bytes := f"{key}={value}".encode())),
                        field_bytes,
                    )
                )
        if include_framing_bit:
            vectors.append(b"\x01")
        return b"".join(vectors)
