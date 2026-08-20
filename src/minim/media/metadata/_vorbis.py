from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar

from ... import __version__
from ..._types import COLLECTION_TYPES, ORDERED_COLLECTION_TYPES
from ..._utility import (
    as_buffer,
    prepare_isrc,
    validate_numeric,
    validate_type,
)
from ._shared import AudioTags

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, Self

    from ..._types import BytesLike, Collection, OrderedCollection


class VorbisComment(AudioTags):
    """
    Vorbis comment metadata container.

    .. seealso::

        `Ogg Vorbis I format specification:
        comment field and header specification
        <https://www.xiph.org/vorbis/doc/v-comment.html>`_.

    This class implements the following special methods:

    * :code:`__len__` – Return the number of fields.

    * :code:`__or__` – Merge two Vorbis comments, concatenating field
      values in container order and preferring the vendor name from the
      right-hand operand.

    * :code:`__ior__` – Merge another Vorbis comment into the current
      one in-place, concatenating field values in container order and
      preferring the vendor name from the right-hand operand.
    """

    _INVALID_KEY_CHARS_REGEX: ClassVar[re.Pattern[str]] = re.compile(
        "[^\x20-\x3c\x3e-\x7e]"
    )

    _block_type: ClassVar[int] = 4  # FLAC
    _validators: ClassVar[dict[str, Callable]] = {
        "BPM": lambda value: validate_numeric("BPM", value, int | float, 0),
        "COMPILATION": lambda value: validate_numeric(
            "COMPILATION", value, bool | int, 0, 1
        ),
        "DISCNUMBER": lambda value: validate_numeric(
            "DISCNUMBER", value, int, 1
        ),
        "DISCTOTAL": lambda value: validate_numeric(
            "DISCTOTAL", value, int, 1
        ),
        "TRACKNUMBER": lambda value: validate_numeric(
            "TRACKNUMBER", value, int, 1
        ),
        "TRACKTOTAL": lambda value: validate_numeric(
            "TRACKTOTAL", value, int, 1
        ),
    }

    __slots__ = ("_fields", "_vendor")

    def __init__(
        self,
        fields: dict[str, str | OrderedCollection[Any]] | None = None,
        vendor: str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        fields : dict[str, Any]; optional
            Key–value pairs of track metadata.

            **Example**: \
            :code:`{"ARTIST": "Galantis", "TITLE": "Runaway (U & I)"}`.

        vendor : str; optional
            Vendor name.

            **Example**: :code:`"Xiph.Org libVorbis I 20020717"`.

        Raises
        ------
        TypeError
            If `fields` is not a dictionary or contains keys or values
            that cannot be stringified, or if `vendor` is not a string.
        """
        normalize_field_name = self._normalize_field_name
        stringify = self._stringify
        self._fields = {}
        if fields is not None:
            validate_type("fields", fields, dict)
            for field_name, field_value in fields.items():
                validate_type("field_name", field_name, str)
                if isinstance(field_value, ORDERED_COLLECTION_TYPES):
                    field_values = self._fields[
                        normalize_field_name(field_name)
                    ] = []
                    for fv in field_value:
                        fv = stringify(fv)
                        if not isinstance(fv, str):
                            raise TypeError(
                                f"Value {fv} in field {field_name} "
                                "could not be converted to a string."
                            )
                        field_values.append(fv)
                else:
                    field_value = stringify(field_value)
                    if not isinstance(field_value, str):
                        raise TypeError(
                            f"Value {field_value} in field {field_name} "
                            "could not be converted to a string."
                        )
                    self._fields[normalize_field_name(field_name)] = [
                        field_value
                    ]

        if vendor is not None:
            validate_type("vendor", vendor, str)
        self._vendor = vendor

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(fields=<{len(self._fields)} fields>"
            + f", vendor={self._vendor!r})"
            if self._vendor
            else ")"
        )

    def __len__(self) -> int:
        return len(self._fields)

    def __or__(self, other: Self) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand types for |: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )

        obj = type_.__new__(type_)
        fields = {key: values.copy() for key, values in self._fields.items()}
        for key, values in other._fields.items():
            if key in fields:
                fields[key] += values
            else:
                fields[key] = values.copy()
        obj._fields = fields
        obj._vendor = other._vendor
        return obj

    def __ior__(self, other: Self) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand types for |: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )

        fields = self._fields
        for key, values in other._fields.items():
            if key in fields:
                fields[key] += values
            else:
                fields[key] = values.copy()
        self._vendor = other._vendor or self._vendor

    @classmethod
    def from_stream(cls, stream: BytesLike, /) -> VorbisComment:
        """
        Instantiate a :class:`VorbisComment` object from a bytes-like
        object.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing a Vorbis comment metadata
            block.

        Returns
        -------
        vorbis_comment : minim.media.metadata.VorbisComment
            Vorbis comment metadata container.

        Raises
        ------
        TypeError
            If `stream` is not a bytes-like object.
        """
        obj = cls.__new__(cls)
        stream = as_buffer(stream)

        # Read comment header
        length = int.from_bytes(stream[:4], byteorder="little")
        offset = 4
        end_offset = offset + length
        obj._vendor = (
            stream[offset:end_offset].tobytes().decode(encoding="utf-8")
        )
        offset = end_offset
        end_offset = offset + 4
        num_fields = int.from_bytes(
            stream[offset:end_offset], byteorder="little"
        )
        offset = end_offset

        # Read comment vectors
        normalize_field_name = cls._normalize_field_name
        fields = obj._fields = {}
        for _ in range(num_fields):
            end_offset = offset + 4
            length = int.from_bytes(
                stream[offset:end_offset], byteorder="little"
            )
            offset = end_offset
            end_offset = offset + length
            field_name, field_value = (
                stream[offset:end_offset]
                .tobytes()
                .decode(encoding="utf-8")
                .split("=", maxsplit=1)
            )
            offset = end_offset
            field_name = normalize_field_name(field_name)
            if field_name in fields:
                fields[field_name].append(field_value)
            else:
                fields[field_name] = [field_value]

        return obj

    @staticmethod
    def _normalize_field_name(key: str, /) -> str:
        """
        Normalize a field name to conform to the Vorbis comment
        specification.

        Parameters
        ----------
        field_name : str; positional-only
            Field name to normalize.

        Returns
        -------
        field_name : str
            Normalized field name.
        """
        return VorbisComment._INVALID_KEY_CHARS_REGEX.sub("_", key.upper())

    @property
    def _block_data_length(self) -> int:
        """
        Length of the encoded Vorbis comment without the framing bit, in
        bytes.
        """
        return (
            8
            + len(
                (
                    f"Minim {__version__}"
                    if self._vendor is None
                    else self._vendor
                ).encode(encoding="utf-8")
            )
            + sum(
                4 + len(f"{key}={value}".encode())
                for key, values in self._fields.items()
                for value in values
            )
        )

    @property
    def album(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`ALBUM` – Title of the album or collection.
        """
        return self.get("ALBUM")

    @album.setter
    def album(self, value: str | OrderedCollection[str], /) -> None:
        self.set(ALBUM=value)

    @property
    def album_artist(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`BPM` – Tempo in beats per minute (BPM).
        """
        return self.get("BPM")

    @bpm.setter
    def bpm(
        self,
        value: float | str | OrderedCollection[int | float | str],
        /,
    ) -> None:
        self.set(BPM=value)

    @property
    def comment(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`COMMENT` – Free-form comments.
        """
        return self.get("COMMENT")

    @comment.setter
    def comment(self, value: str | OrderedCollection[str], /) -> None:
        self.set(COMMENT=value)

    @property
    def compilation(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`COMPOSER` – Composers or songwriters.
        """
        return self.get("COMPOSER")

    @composer.setter
    def composer(self, value: str | OrderedCollection[str], /) -> None:
        self.set(COMPOSER=value)

    @property
    def contact(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`COPYRIGHT` – Copyright attribution.
        """
        return self.get("COPYRIGHT")

    @copyright.setter
    def copyright(self, value: str | OrderedCollection[str], /) -> None:
        self.set(COPYRIGHT=value)

    @property
    def date(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`DATE` or :code:`YEAR` (legacy) – Recording or release
        date.
        """
        return self.get("DATE") or self.get("YEAR")

    @date.setter
    def date(
        self, value: str | datetime | OrderedCollection[str | datetime], /
    ) -> None:
        self.set(DATE=value)

    @property
    def description(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`DESCRIPTION` – General description.
        """
        return self.get("DESCRIPTION")

    @description.setter
    def description(self, value: str | OrderedCollection[str], /) -> None:
        self.set(DESCRIPTION=value)

    @property
    def disc_number(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`DISCTOTAL` or :code:`TOTALDISCS` (legacy) – Total number
        of discs.
        """
        return self.get("DISCTOTAL") or self.get("TOTALDISCS")

    @disc_total.setter
    def disc_total(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None:
        self.set(DISCTOTAL=value)

    @property
    def encoder(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`GENRE` – Musical genres.
        """
        return self.get("GENRE")

    @genre.setter
    def genre(self, value: str | OrderedCollection[str], /) -> None:
        self.set(GENRE=value)

    @property
    def grouping(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`GROUPING` – Content group description.
        """
        return self.get("GROUPING")

    @grouping.setter
    def grouping(self, value: str | OrderedCollection[str], /) -> None:
        self.set(GROUPING=value)

    @property
    def isrc(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`ISRC` – International Standard Recording Code (ISRC).
        """
        return self.get("ISRC")

    @isrc.setter
    def isrc(self, value: str | OrderedCollection[str], /) -> None:
        self.set(ISRC=prepare_isrc(value))

    @property
    def label(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`ORGANIZATION` – Publishers or record labels.
        """
        return self.get("ORGANIZATION")

    @label.setter
    def label(self, value: str | OrderedCollection[str], /) -> None:
        self.set(ORGANIZATION=value)

    @property
    def license(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`LICENSE` – License information.
        """
        return self.get("LICENSE")

    @license.setter
    def license(self, value: str | OrderedCollection[str], /) -> None:
        self.set(LICENSE=value)

    @property
    def location(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`LOCATION` – Recording locations.
        """
        return self.get("LOCATION")

    @location.setter
    def location(self, value: str | OrderedCollection[str], /) -> None:
        self.set(LOCATION=value)

    @property
    def lyrics(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`LYRICS` – Lyrics or transcription.
        """
        return self.get("LYRICS")

    @lyrics.setter
    def lyrics(self, value: str | OrderedCollection[str], /) -> None:
        self.set(LYRICS=value)

    @property
    def performer(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TITLE` – Title of the recording.
        """
        return self.get("TITLE")

    @title.setter
    def title(self, value: str | OrderedCollection[str], /) -> None:
        self.set(TITLE=value)

    @property
    def track_number(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TRACKNUMBER` – Track number within the album or
        collection.
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
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`TRACKTOTAL` or :code:`TOTALTRACKS` (legacy) – Total
        number of tracks.
        """
        return self.get("TRACKTOTAL") or self.get("TOTALTRACKS")

    @track_total.setter
    def track_total(
        self, value: int | str | OrderedCollection[int | str], /
    ) -> None:
        self.set(TRACKTOTAL=value)

    @property
    def vendor(self) -> str | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Vendor name.
        """
        return self._vendor

    @vendor.setter
    def vendor(self, value: str, /) -> None:
        validate_type("vendor", value, str)
        self._vendor = value

    @property
    def version(self) -> list[str] | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        :code:`VERSION` – Version of the recording (e.g., remix
        information).
        """
        return self.get("VERSION")

    @version.setter
    def version(self, value: str | OrderedCollection[str], /) -> None:
        self.set(VERSION=value)

    def append(self, **kwargs: Any) -> None:
        """
        Append track metadata.

        .. note::

           The Vorbis comment specification allows for arbitrary
           case-insensitive field names consisting of only ASCII
           characters 0x20 (space) through 0x7D (:code:`}`),
           excluding 0x3D (:code:`=`). However, Python identifiers are
           case-sensitive, can contain Unicode characters, and have
           restrictions such as not containing whitespace or starting
           with a digit.

           To pass in fields with names that do not conform to Python
           identifier rules, unpack a dictionary containing key–value
           pairs.

           All field names will have illegal characters replaced with
           underscores and be converted to uppercase. It is possible
           that two fields with different invalid names are treated as
           the same field if their sanitized names are identical.

        Parameters
        ----------
        fields : dict[str, Any]; optional
            Key–value pairs of track metadata.

            **Example**: \
            :code:`{"ARTIST": "Galantis", "TITLE": "Runaway (U & I)"}`.

        **kwargs : dict[str, Any]
            Key–value pairs of track metadata.

        Raises
        ------
        TypeError
            If any key or value cannot be stringified.
        """
        for key, value in kwargs.items():
            key = self._normalize_field_name(key)
            if key in self._fields:
                values = self._fields[key]
            else:
                self._fields[key] = values = []
            validate = self._validators.get(key)
            has_validator = validate is not None

            if isinstance(value := self._stringify(value), str):
                if has_validator:
                    validate(value)
                values.append(value)
            elif isinstance(value, ORDERED_COLLECTION_TYPES):
                for item in value:
                    if isinstance(item := self._stringify(item), str):
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

    def get(
        self, field_names: str | Collection[str], /
    ) -> list[str] | dict[str, list[str] | None] | None:
        """
        Get track metadata.

        Parameters
        ----------
        field_names : str or Collection[str]; positional-only
            Field names of the track metadata to get.

        Returns
        -------
        metadata : list[str], dict[str, list[str] | None], or None
            Track metadata. If `field_names` is a collection of strings,
            a dictionary mapping field names to their corresponding
            values is returned.

        Raises
        ------
        TypeError
            If `field_names` is not a string or collection of strings.
        """
        if not (
            isinstance(field_names, str)
            or (
                isinstance(field_names, COLLECTION_TYPES)
                and all(
                    isinstance(field_name, str) for field_name in field_names
                )
            )
        ):
            raise TypeError(
                "`fields` must be a string or a collection of strings."
            )

        if isinstance(field_names, str):
            return self._fields.get(self._normalize_field_name(field_names))

        return {field_name: self.get(field_name) for field_name in field_names}

    def remove(
        self,
        field_names: str | Collection[str],
        /,
        *,
        indices: int | Collection[int] | None = None,
    ) -> None:
        """
        Remove track metadata.

        Parameters
        ----------
        field_names : str or Collection[str]; positional-only
            Field names of the track metadata to remove.

        indices : int or Collection[int]; keyword-only; optional
            Indices of values to remove from a specific field. Can be
            provided only when `field_names` is a string.

        Raises
        ------
        TypeError
            If `field_names` is not a string or a collection of strings,
            or if `indices` is not an integer or a collection of
            integers.

        ValueError
            If `indices` is specified when `field_names` is a collection
            of strings.
        """
        is_string = isinstance(field_names, str)
        if not (
            is_string
            or (
                isinstance(field_names, COLLECTION_TYPES)
                and all(
                    isinstance(field_name, str) for field_name in field_names
                )
            )
        ):
            raise TypeError(
                "`fields` must be a string or a collection of strings."
            )

        if is_string:
            if indices is None:
                del self._fields[self._normalize_field_name(field_names)]
            else:
                if isinstance(indices, int):
                    indices = [indices]
                elif not (
                    isinstance(indices, COLLECTION_TYPES)
                    and all(isinstance(index, int) for index in indices)
                ):
                    raise TypeError(
                        "`indices` must be an integer or a collection "
                        "of integers."
                    )
                field_value = self._fields[
                    self._normalize_field_name(field_names)
                ]
                for idx in sorted(indices, reverse=True):
                    field_value.pop(idx)
            return

        if indices is not None:
            raise ValueError(
                "`indices` cannot be specified when `fields` is a "
                "collection of strings."
            )

        for field_name in field_names:
            self.remove(field_name)

    def set(self, fields: dict[str, Any], **kwargs: Any) -> None:
        """
        Set track metadata.

        .. note::

           The Vorbis comment specification allows for arbitrary
           case-insensitive field names consisting of only ASCII
           characters 0x20 (space) through 0x7D (:code:`}`),
           excluding 0x3D (:code:`=`). However, Python identifiers are
           case-sensitive, can contain Unicode characters, and have
           restrictions such as not containing whitespace or starting
           with a digit.

           To pass in fields with names that do not conform to Python
           identifier rules, unpack a dictionary containing key–value
           pairs.

           All field names will have illegal characters replaced with
           underscores and be converted to uppercase. It is possible
           that two fields with different invalid names are treated as
           the same field if their sanitized names are identical.

        Parameters
        ----------
        fields : dict[str, Any]; optional
            Key–value pairs of track metadata.

            **Example**: \
            :code:`{"ARTIST": "Galantis", "TITLE": "Runaway (U & I)"}`.

        **kwargs : dict[str, Any]
            Additional key–value pairs of track metadata.

        Raises
        ------
        TypeError
            If any key or value cannot be stringified.

        ValueError
            If any value is outside the allowed range for its field.
        """
        if fields is None:
            fields = {}
        else:
            validate_type("fields", fields, dict)
        for key, value in (fields | kwargs).items():
            key = self._normalize_field_name(key)
            validate = self._validators.get(key)
            has_validator = validate is not None
            if isinstance(value := self._stringify(value), str):
                if has_validator:
                    validate(value)
                self._fields[key] = [value]
            elif isinstance(value, ORDERED_COLLECTION_TYPES):
                self._fields[key] = values = []
                for item in value:
                    if isinstance(item := self._stringify(item), str):
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

    def serialize(self, *, include_framing_bit: bool = False) -> bytes:
        """
        Serialize the Vorbis comment to a bytestream.

        .. note::

           If a vendor name was not specified,
           :code:`f"Minim {minim.__version__}"` is used.

        Parameters
        ----------
        include_framing_bit : bool; keyword-only; default: :code:`False`
            Whether to include a framing bit (:code:`b'\x01'`) at the
            end of the bytestream. Required only by the Ogg container
            format.

        Returns
        -------
        stream : bytes
            Bytestream containing the Vorbis comment.
        """
        vectors = [
            len(
                vendor := (self._vendor or f"Minim {__version__}").encode(
                    encoding="utf-8"
                )
            ).to_bytes(length=4, byteorder="little"),
            vendor,
            len(self._fields).to_bytes(length=4, byteorder="little"),
        ]
        for key, values in self._fields.items():
            for value in values:
                vectors.extend(
                    (
                        len(field := f"{key}={value}".encode()).to_bytes(
                            length=4, byteorder="little"
                        ),
                        field,
                    )
                )
        if include_framing_bit:
            vectors.append(b"\x01")
        return b"".join(vectors)
