from __future__ import annotations
from datetime import datetime
import re
from typing import TYPE_CHECKING

from ... import __version__
from ..._types import COLLECTION_TYPES, ORDERED_COLLECTION_TYPES
from ..._utility import prepare_isrc, validate_numeric, validate_type
from .._shared import as_buffer
from ._shared import AudioTags

if TYPE_CHECKING:
    from typing import Any

    from ..._types import BytesLike, Collection, OrderedCollection


class VorbisComment(AudioTags):
    """
    Vorbis comment metadata container.

    .. seealso::

        `Ogg Vorbis I format specification:
        comment field and header specification
        <https://www.xiph.org/vorbis/doc/v-comment.html>`_.
    """

    _INVALID_KEY_CHARS_REGEX = re.compile("[^\x20-\x3c\x3e-\x7e]")

    _block_type = 4  # FLAC
    _validators = {
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

    __slots__ = "_fields", "_keep_empty_values", "_num_fields", "_vendor"

    def __init__(
        self,
        fields: dict[str, str | OrderedCollection[Any]] | None = None,
        vendor: str | None = None,
        *,
        keep_empty_values: bool = False,
    ) -> None:
        """
        Parameters
        ----------
        fields : dict[str, Any]; optional
            Key–value pairs of track attributes.

        vendor : str; optional
            Vendor name.

            **Example**: :code:`"Xiph.Org libVorbis I 20020717"`.

        keep_empty_values : bool; keyword-only; default: :code:`False`
            Whether to keep field–value pairs with empty values.
        """
        validate_type("keep_empty_values", keep_empty_values, bool)
        self._keep_empty_values = keep_empty_values

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
                        if keep_empty_values or fv:
                            field_values.append(fv)
                else:
                    field_value = stringify(field_value)
                    if not isinstance(field_value, str):
                        raise TypeError(
                            f"Value {field_value} in field {field_name} "
                            "could not be converted to a string."
                        )
                    if keep_empty_values or field_value:
                        self._fields[normalize_field_name(field_name)] = [
                            field_value
                        ]
        self._num_fields = len(self._fields)

        validate_type("vendor", vendor, str | None)
        self._vendor = vendor

    @classmethod
    def from_stream(
        cls,
        stream: BytesLike,
        /,
        *,
        keep_empty_values: bool = False,
    ) -> VorbisComment:
        """
        Instantiate a :class:`VorbisComment` object from a bytes-like
        object.

        Parameters
        ----------
        bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
        positional-only; optional
            Bytes-like object containing a Vorbis comment metadata
            block.

        keep_empty_values : bool; keyword-only; default: :code:`False`
            Whether to keep field–value pairs with empty values.

        Returns
        -------
        vorbis_comment : minim.media.metadata.VorbisComment
            Vorbis comment metadata container.
        """
        obj = cls.__new__(cls)
        validate_type("keep_empty_values", keep_empty_values, bool)
        obj._keep_empty_values = keep_empty_values

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
        obj._num_fields = int.from_bytes(
            stream[offset:end_offset], byteorder="little"
        )
        offset = end_offset

        # Read comment vectors
        normalize_field_name = cls._normalize_field_name
        fields = obj._fields = {}
        for _ in range(obj._num_fields):
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
            if keep_empty_values or field_value:
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
    def _block_length(self) -> int:
        """
        Length of encoded Vorbis comment without framing bit in bytes.
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
                4 + len(f"{key}={value}".encode("utf-8"))
                for key, values in self._fields.items()
                for value in values
            )
        )

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
        self.set(ISRC=prepare_isrc(value))

    @property
    def label(self) -> list[str] | None:
        """
        :code:`ORGANIZATION` – Publishers or record labels.
        """
        return self.get("ORGANIZATION")

    @label.setter
    def label(self, value: str | OrderedCollection[str], /) -> None:
        self.set(ORGANIZATION=value)

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
        **kwargs
            Key–value pairs of track attributes.
        """
        keep_empty_values = self._keep_empty_values
        for key, value in kwargs.items():
            key = self._normalize_field_name(key)
            new_key = key not in self._fields
            if new_key:
                self._fields[key] = values = []
            else:
                values = self._fields[key]
            validate = self._validators.get(key)
            has_validator = validate is not None

            if isinstance(value := self._stringify(value), str):
                if keep_empty_values or value:
                    if has_validator:
                        validate(value)
                    values.append(value)
            elif isinstance(value, ORDERED_COLLECTION_TYPES):
                for item in value:
                    if isinstance(item := self._stringify(item), str):
                        if keep_empty_values or item:
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
            return self._fields.get(self._normalize_field_name(fields))

        return {field: self.get(field) for field in fields}

    def remove(
        self,
        fields: str | Collection[str],
        /,
        *,
        indices: Collection[int] | None = None,
    ) -> None:
        """
        Remove track attributes.

        Parameters
        ----------
        fields : str or Collection[str]; positional-only
            Field names of the attributes.
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
            if indices is None:
                del self._fields[self._normalize_field_name(fields)]
            else:
                field_value = self._fields[self._normalize_field_name(fields)]
                for idx in sorted(indices, reverse=True):
                    field_value.pop(idx)
            return

        if indices is not None:
            raise ValueError(
                "`indices` cannot be specified when `fields` is a "
                "collection of strings."
            )

        for field in fields:
            self.remove(field)

    def set(self, **kwargs: Any) -> None:
        """
        Set track attributes.

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
        **kwargs
            Key–value pairs of track attributes.
        """
        keep_empty_values = self._keep_empty_values
        for key, value in kwargs.items():
            key = self._normalize_field_name(key)
            new_key = key not in self._fields
            validate = self._validators.get(key)
            has_validator = validate is not None
            if isinstance(value := self._stringify(value), str):
                if keep_empty_values or value:
                    if has_validator:
                        validate(value)
                    self._fields[key] = [value]
                    if new_key:
                        self._num_fields += 1
            elif isinstance(value, ORDERED_COLLECTION_TYPES):
                self._fields[key] = values = []
                for item in value:
                    if isinstance(item := self._stringify(item), str):
                        if keep_empty_values or item:
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
        Serialize the Vorbis comment to a bytestream.

        .. note::

           If a vendor name was not specified,
           :code:`f"Minim {minim.__version__}"` is used.

        Parameters
        ----------
        include_framing_bit : bool; keyword-only; default: :code:`False`
            Whether to include a framing bit (single byte of value
            :code:`1`) at the end of the bytestream. Required only by
            the Ogg container format.

        Returns
        -------
        bytestream : bytes
            Bytestream containing the serialized Vorbis comment block.
        """
        vectors = [
            len(
                vendor := (self._vendor or f"Minim {__version__}").encode(
                    encoding="utf-8"
                )
            ).to_bytes(4, byteorder="little"),
            vendor,
            self._num_fields.to_bytes(4, byteorder="little"),
        ]
        for key, values in self._fields.items():
            for value in values:
                vectors.extend(
                    (
                        len(
                            field := f"{key}={value}".encode(encoding="utf-8")
                        ).to_bytes(4, byteorder="little"),
                        field,
                    )
                )
        if include_framing_bit:
            vectors.append(b"\x01")
        return b"".join(vectors)
