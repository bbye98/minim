from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from numbers import Real
import re
from typing import TYPE_CHECKING

from ..._types import COLLECTION_TYPES, ORDERED_COLLECTION_TYPES

if TYPE_CHECKING:
    from typing import Any

    from ..._types import Collection, OrderedCollection
    from ..._utility import validate_numeric, validate_type


class AudioMetadata(ABC):
    """
    Generic audio metadata container.
    """

    __slots__ = ()

    @property
    @abstractmethod
    def album(self) -> str | None:
        """
        Album or collection.
        """
        ...

    @album.setter
    @abstractmethod
    def album(self, value: str, /) -> None: ...

    @property
    @abstractmethod
    def album_artist(self) -> str | None:
        """
        Main artists credited for the entire album or collection.
        """
        ...

    @album_artist.setter
    @abstractmethod
    def album_artist(self, value: str | Collection[str], /) -> None: ...

    @property
    @abstractmethod
    def artist(self) -> str | None:
        """
        Artists (e.g., the performing band or singers in popular music,
        the composers for classical music, or the authors of the
        original text in audiobooks).
        """
        ...

    @artist.setter
    @abstractmethod
    def artist(self, value: str | Collection[str], /) -> None: ...

    @property
    @abstractmethod
    def bpm(self) -> int | float | None:
        """
        Tempo or beats per minute (BPM).
        """
        ...

    @bpm.setter
    @abstractmethod
    def bpm(self, value: int | float, /) -> None: ...

    @property
    @abstractmethod
    def comment(self) -> str | None:
        """
        Free-form comments.
        """
        ...

    @comment.setter
    @abstractmethod
    def comment(self, value: str | Collection[str], /) -> None: ...

    @property
    @abstractmethod
    def compilation(self) -> bool | None:
        """
        Whether the recording is part of a compilation.
        """
        ...

    @compilation.setter
    @abstractmethod
    def compilation(self, value: bool, /) -> None: ...

    @property
    @abstractmethod
    def composer(self) -> str | None:
        """
        Composers.
        """
        ...

    @composer.setter
    @abstractmethod
    def composer(self, value: str | Collection[str], /) -> None: ...

    @property
    @abstractmethod
    def contact(self) -> str | None:
        """
        Contact information for the creators or distributors.
        """
        ...

    @contact.setter
    @abstractmethod
    def contact(self, value: str | Collection[str], /) -> None: ...

    @property
    @abstractmethod
    def copyright(self) -> str | None:
        """
        Copyright attribution.
        """
        ...

    @copyright.setter
    @abstractmethod
    def copyright(self, value: str | Collection[str], /) -> None: ...

    @property
    @abstractmethod
    def date(self) -> datetime | None:
        """
        Release date.
        """
        ...

    @date.setter
    @abstractmethod
    def date(self, value: str | datetime, /) -> None: ...

    @property
    @abstractmethod
    def description(self) -> str | None:
        """
        General description.
        """
        ...

    @description.setter
    @abstractmethod
    def description(self, value: str, /) -> None: ...

    @property
    @abstractmethod
    def disc(self) -> tuple[int, int | None] | None:
        """
        Disc number and total number of discs.
        """
        ...

    @disc.setter
    @abstractmethod
    def disc(self, value: tuple[int | str, int | str | None], /) -> None: ...

    @property
    @abstractmethod
    def disc_number(self) -> int | None:
        """
        Disc number within a multi-disc set.
        """
        ...

    @disc_number.setter
    @abstractmethod
    def disc_number(self, value: int | str, /) -> None: ...

    @property
    @abstractmethod
    def disc_total(self) -> int | None:
        """
        Total number of discs.
        """
        ...

    @disc_total.setter
    @abstractmethod
    def disc_total(self, value: int | str, /) -> None: ...

    @property
    @abstractmethod
    def encoder(self) -> str | None:
        """
        Software or hardware used for encoding, or the person or
        organization that encoded the audio file.
        """
        ...

    @encoder.setter
    @abstractmethod
    def encoder(self, value: str, /) -> None: ...

    @property
    @abstractmethod
    def genre(self) -> str | None:
        """
        Genres.
        """
        ...

    @genre.setter
    @abstractmethod
    def genre(self, value: str | Collection[str], /) -> None: ...

    @property
    @abstractmethod
    def grouping(self) -> str | None:
        """
        Content group description.
        """
        ...

    @grouping.setter
    @abstractmethod
    def grouping(self, value: str | Collection[str], /) -> None: ...

    @property
    @abstractmethod
    def isrc(self) -> str | None:
        """
        International Standard Recording Code (ISRC).
        """
        ...

    @isrc.setter
    @abstractmethod
    def isrc(self, value: str, /) -> None: ...

    @property
    @abstractmethod
    def label(self) -> str | None:
        """
        Publisher or record label.
        """
        ...

    @label.setter
    @abstractmethod
    def label(self, value: str | Collection[str], /) -> None: ...

    @property
    @abstractmethod
    def license(self) -> str | None:
        """
        License information.
        """
        ...

    @license.setter
    @abstractmethod
    def license(self, value: str | Collection[str], /) -> None: ...

    @property
    @abstractmethod
    def location(self) -> str | None:
        """
        Recording locations.
        """
        ...

    @location.setter
    @abstractmethod
    def location(self, value: str | Collection[str], /) -> None: ...

    @property
    @abstractmethod
    def lyrics(self) -> str | None:
        """
        Lyrics.
        """
        ...

    @lyrics.setter
    @abstractmethod
    def lyrics(self, value: str, /) -> None: ...

    @property
    @abstractmethod
    def performer(self) -> str | None:
        """
        Performers (e.g., the conductor, orchestra, and/or soloists in
        classical music, or the narrator in audiobooks).
        """
        ...

    @performer.setter
    @abstractmethod
    def performer(self, value: str | Collection[str], /) -> None: ...

    @property
    @abstractmethod
    def title(self) -> str | None:
        """
        Title.
        """
        ...

    @title.setter
    @abstractmethod
    def title(self, value: str | Collection[str], /) -> None: ...

    @property
    @abstractmethod
    def track(self) -> tuple[int | None, int | None] | None:
        """
        Track number and total number of tracks.
        """
        ...

    @track.setter
    @abstractmethod
    def track(self, value: tuple[int, int | None], /) -> None: ...

    @property
    @abstractmethod
    def track_number(self) -> int | None:
        """
        Track number.
        """
        ...

    @track_number.setter
    @abstractmethod
    def track_number(self, value: int, /) -> None: ...

    @property
    @abstractmethod
    def track_total(self) -> int | None:
        """
        Total number of tracks.
        """
        ...

    @track_total.setter
    @abstractmethod
    def track_total(self, value: int, /) -> None: ...

    @property
    @abstractmethod
    def version(self) -> str | None:
        """
        Version (e.g., remix information).
        """
        ...

    @version.setter
    @abstractmethod
    def version(self, value: str, /) -> None: ...

    @abstractmethod
    def get(
        self,
        fields: str | Collection[str],
        /,
        *,
        delimiter: str | tuple[str, str] | None = (", ", " & "),
    ) -> str | list[str] | dict[str, str | list[str]]:
        """
        Get track attributes.

        Parameters
        ----------
        fields : str or Collection[str]; positional-only
            Field names of the attributes.

        delimiter : str or tuple[str, str]; keyword-only; \
        default: :code:`(", ", " & ")`
            Delimiters to use to concatenate multiple values into a 
            string. If :code:`None`, the raw values are returned. If a 
            string, all values are concatenated using the delimiter. If 
            a tuple, all but the last value is concatenated using the 
            first delimiter, and the final value using the second 
            delimiter.

        Returns
        -------
        attributes : str, list[str], or dict[str, str | list[str]]
            Track attributes. If `fields` is a string, a list of strings
            or a string is returned if `delimiter` is or is not 
            :code:`None`, respectively. If `fields` is a collection of 
            strings, a dictionary mapping field names to their 
            corresponding values is returned.
        """
        ...

    @abstractmethod
    def set(self, **kwargs: Any) -> None:
        """
        Set track attributes.

        Parameters
        ----------
        **kwargs
            Key–value pairs of track attributes.
        """
        ...


class VorbisComment(AudioMetadata):
    """
    Vorbis comment object.

    .. seealso::

        `Ogg Vorbis I format specification:
        comment field and header specification
        <https://www.xiph.org/vorbis/doc/v-comment.html>`_.
    """

    __slots__ = "_fields", "_ignore_duplicates", "_n_fields", "_vendor"

    def __init__(
        self,
        bytestream: bytes | None = None,
        /,
        *,
        ignore_duplicates: bool = False,
    ) -> None:
        """
        Parameters
        ----------
        bytestream : bytes; positional-only;, optional
            Bytestream containing a Vorbis comment metadata block.

        ignore_duplicates : bool; keyword-only; default: :code:`False`
            Whether to ignore duplicate values in existing fields.
        """
        if isinstance(bytestream, bytes):
            byte_offset = 4 + int.from_bytes(
                bytestream[:4], byteorder="little"
            )
            self._vendor = bytestream[4:byte_offset].decode()
            self._n_fields = int.from_bytes(
                bytestream[byte_offset : (byte_offset := byte_offset + 4)],
                byteorder="little",
            )
            self._fields = {}
            if ignore_duplicates:
                for _ in range(self._n_fields):
                    key, value = (
                        bytestream[
                            byte_offset : (
                                byte_offset := byte_offset
                                + int.from_bytes(
                                    bytestream[
                                        byte_offset : (
                                            byte_offset := byte_offset + 4
                                        )
                                    ],
                                    byteorder="little",
                                )
                            )
                        ]
                        .decode()
                        .split("=", maxsplit=1)
                    )
                    if value:
                        if (
                            key := self._normalize_key(key).upper()
                        ) in self._fields:
                            self._fields[key][value] = None
                        else:
                            self._fields[key] = {value}
                for key, values in self._fields.items():
                    self._fields[key] = list(values.keys())
            else:
                for _ in range(self._n_fields):
                    key, value = (
                        bytestream[
                            byte_offset : (
                                byte_offset := byte_offset
                                + int.from_bytes(
                                    bytestream[
                                        byte_offset : (
                                            byte_offset := byte_offset + 4
                                        )
                                    ],
                                    byteorder="little",
                                )
                            )
                        ]
                        .decode()
                        .split("=", maxsplit=1)
                    )
                    if value:
                        if (
                            key := self._normalize_key(key).upper()
                        ) in self._fields:
                            self._fields[key].append(value)
                        else:
                            self._fields[key] = [value]
        elif bytestream is None:
            self._vendor = None
            self._n_fields = 0
            self._fields = {}
        else:
            raise ValueError(
                "If provided, `bytestream` must be a bytes object."
            )

        self._ignore_duplicates = ignore_duplicates

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

    @staticmethod
    def _to_string(value: Any, /) -> Any:
        """
        Convert an arbitrary value to a string.

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
    def album(self) -> str | None:
        """
        :code:`ALBUM` – Album or collection.
        """
        value = self._get("ALBUM", delimiter=None)
        if value is not None:
            value = value[0]
        return value

    @album.setter
    def album(self, value: str, /) -> None:
        validate_type("album", value, str)
        self.set(ALBUM=value)

    @property
    def album_artist(self) -> str | None:
        """
        :code:`ALBUMARTIST` – Main artists credited for the entire album or collection.
        """
        return self._get("ALBUMARTIST")

    @album_artist.setter
    def album_artist(self, value: str | Collection[str], /) -> None:
        validate_type("album_artist", value, str | COLLECTION_TYPES)
        self.set(ALBUMARTIST=value)

    @property
    def artist(self) -> str | None:
        """
        :code:`ARTIST` – Artists (e.g., the performing band or singers
        in popular music, the composers for classical music, or the
        authors of the original text in audiobooks).
        """
        return self._get("ARTIST")

    @artist.setter
    def artist(self, value: str | Collection[str], /) -> None:
        validate_type("artist", value, str | COLLECTION_TYPES)
        self.set(ARTIST=value)

    @property
    def bpm(self) -> float | None:
        """
        :code:`BPM` – Tempo or beats per minute (BPM).
        """
        value = self._get("BPM", delimiter=None)
        if value is not None:
            value = float(value[0])
        return value

    @bpm.setter
    def bpm(self, value: int | float | str, /) -> None:
        validate_numeric("bpm", value, float, 0)
        self.set(BPM=value)

    @property
    def comment(self) -> str | None:
        """
        :code:`COMMENT` – Free-form comments.
        """
        return self._get("COMMENT", delimiter="\n", single_delimiter=True)

    @comment.setter
    def comment(self, value: str | Collection[str], /) -> None:
        validate_type("comment", value, str | COLLECTION_TYPES)
        self.set(COMMENT=value)

    @property
    def compilation(self) -> bool | None:
        """
        :code:`COMPILATION` – Whether the recording is part of a compilation.
        """
        value = self._get("COMPILATION", delimiter=None)
        if value is not None:
            value = bool(int(value[0]))
        return value

    @compilation.setter
    def compilation(self, value: bool | str, /) -> None:
        validate_type("compilation", value, bool | str)
        if isinstance(value, str) and value not in {"0", "1"}:
            raise ValueError(
                "`compilation` must be '0' or '1' when it is a string."
            )
        self.set(COMPILATION=value)

    @property
    def composer(self) -> str | None:
        """
        :code:`COMPOSER` – Composers.
        """
        return self._get("COMPOSER")

    @composer.setter
    def composer(self, value: str | Collection[str], /) -> None:
        validate_type("composer", value, str | COLLECTION_TYPES)
        self.set(COMPOSER=value)

    @property
    def contact(self) -> str | None:
        """
        :code:`CONTACT` – Contact information for the creators or distributors.
        """
        return self._get("CONTACT", delimiter=";", single_delimiter=True)

    @contact.setter
    def contact(self, value: str | Collection[str], /) -> None:
        validate_type("contact", value, str | COLLECTION_TYPES)
        self.set(CONTACT=value)

    @property
    def copyright(self) -> str | None:
        """
        :code:`COPYRIGHT` – Copyright attribution.
        """
        return self._get("COPYRIGHT", delimiter=";", single_delimiter=True)

    @copyright.setter
    def copyright(self, value: str | Collection[str], /) -> None:
        validate_type("copyright", value, str | COLLECTION_TYPES)
        self.set(COPYRIGHT=value)

    @property
    def date(self) -> str | None:
        """
        :code:`DATE` – Release date.
        """
        value = self._get("DATE", delimiter=None) or self._get(
            "YEAR", delimiter=None
        )
        if value is not None:
            value = value[0]
        return value

    @date.setter
    def date(self, value: str | datetime, /) -> None:
        validate_type("date", value, str | datetime)
        self.set(DATE=value)

    @property
    def description(self) -> str | None:
        """
        :code:`DESCRIPTION` – General description.
        """
        value = self._get("DESCRIPTION", delimiter=None)
        if value is not None:
            value = value[0]
        return value

    @description.setter
    def description(self, value: str, /) -> None:
        validate_type("description", value, str)
        self.set(DESCRIPTION=value)

    @property
    def disc(self) -> tuple[int, int | None] | None:
        """
        :code:`DISCNUMBER` and :code:`DISCTOTAL`
        (legacy: :code:`TOTALDISCS`) – Disc number and total number of
        discs.
        """
        values = self._get(("DISCNUMBER", "DISCTOTAL"), delimiter=None)
        disc_number = values["DISCNUMBER"]
        if disc_number is None:
            return
        disc_total = values["DISCTOTAL"] or self._get(
            "TOTALDISCS", delimiter=None
        )
        if disc_total is not None:
            disc_total = int(disc_total[0])
        return int(disc_number[0]), disc_total

    @disc.setter
    def disc(self, value: tuple[int | str, int | str | None], /) -> None:
        validate_type("disc", value, ORDERED_COLLECTION_TYPES)
        if len(value) != 2:
            raise ValueError(
                "`disc` must be an ordered collection of length 2."
            )
        disc_number, total_discs = value
        validate_numeric("disc[0]", disc_number, int, 1)
        self.set(DISCNUMBER=disc_number)
        if total_discs is not None:
            validate_numeric("disc[1]", total_discs, int, 1)
            self.set(TOTALDISCS=total_discs)

    @property
    def disc_number(self) -> int | None:
        """
        :code:`DISCNUMBER` – Disc number within a multi-disc set.
        """
        value = self._get("DISCNUMBER", delimiter=None)
        if value is not None:
            value = int(value[0])
        return value

    @disc_number.setter
    def disc_number(self, value: int | str, /) -> None:
        validate_numeric("disc_number", value, int, 1)
        self.set(DISCNUMBER=value)

    @property
    def disc_total(self) -> int | None:
        """
        :code:`DISCTOTAL` (legacy: :code:`TOTALDISCS`) – Total number of
        discs.
        """
        value = self._get("DISCTOTAL", delimiter=None) or self._get(
            "TOTALDISCS", delimiter=None
        )
        if value is not None:
            value = int(value[0])
        return value

    @disc_total.setter
    def disc_total(self, value: int, /) -> None:
        validate_numeric("disc_total", value, int, 1)
        self.set(DISCTOTAL=value)

    @property
    def encoder(self) -> str | None:
        """
        :code:`ENCODER` – Software or hardware used for encoding, or the
        person or organization that encoded the audio file.
        """
        value = self._get("ENCODER", delimiter=None)
        if value is not None:
            value = value[0]
        return value

    @encoder.setter
    def encoder(self, value: str, /) -> None:
        validate_type("encorder", value, str)
        self.set(ENCODER=value)

    @property
    def genre(self) -> str | None:
        """
        :code:`GENRE` – Genres.
        """
        return self._get("GENRE", delimiter=";", single_delimiter=True)

    @genre.setter
    def genre(self, value: str | Collection[str], /) -> None:
        validate_type("genre", value, str | COLLECTION_TYPES)
        self.set(GENRE=value)

    @property
    def grouping(self) -> str | None:
        """
        :code:`GROUPING` – Content group description.
        """
        value = self._get("GROUPING", delimiter=";", single_delimiter=True)
        return value

    @grouping.setter
    def grouping(self, value: str | Collection[str], /) -> None:
        validate_type("grouping", value, str | COLLECTION_TYPES)
        self.set(GROUPING=value)

    @property
    def isrc(self) -> str | None:
        """
        :code:`ISRC` – International Standard Recording Code (ISRC).
        """
        value = self._get("ISRC", delimiter=None)
        if value is not None:
            value = value[0]
        return value

    @isrc.setter
    def isrc(self, value: str, /) -> None: ...

    def _get(
        self,
        fields: str | Collection[str],
        /,
        *,
        delimiter: str | OrderedCollection[str] | None = (", ", " & "),
        single_delimiter: bool | None = None,
    ) -> str | list[str] | dict[str, str | list[str]] | None:
        """
        Get track attributes.

        Parameters
        ----------
        fields : str or Collection[str]; positional-only
            Field names of the attributes.

        delimiter : str or tuple[str, str]; keyword-only
            Delimiters to use to concatenate multiple values into a
            string. If :code:`None`, the raw values are returned. If a
            string, all values are concatenated using the delimiter. If
            a tuple, all but the last value is concatenated using the
            first delimiter, and the final value using the second
            delimiter.

        single_delimiter : bool; keyword-only; optional
            Whether there is only a single delimiter.

        Returns
        -------
        attributes : str, list[str], or dict[str, str | list[str]]
            Track attributes. If `fields` is a string, a list of strings
            or a string is returned if `delimiter` is or is not
            :code:`None`, respectively. If `fields` is a collection of
            strings, a dictionary mapping field names to their
            corresponding values is returned.
        """
        if isinstance(fields, str):
            values = self._fields.get(fields, None)
            if single_delimiter is None:
                single_delimiter = delimiter
            if values is not None and delimiter is not None:
                if len(values) == 1:
                    values = values[0]
                else:
                    values = (
                        delimiter.join(values)
                        if single_delimiter
                        else (
                            f"{delimiter[0].join(values[:-1])}"
                            f"{delimiter[1]}{values[-1]}"
                        )
                    )
            return values

        elif isinstance(fields, COLLECTION_TYPES):
            return {
                field: self._get(
                    field,
                    delimiter=delimiter,
                    single_delimiter=single_delimiter,
                )
                for field in fields
            }

    def get(
        self,
        fields: str | Collection[str],
        /,
        *,
        delimiter: str | OrderedCollection[str] | None = (", ", " & "),
    ) -> str | list[str] | dict[str, str | list[str]] | None:
        """
        Get track attributes.

        Parameters
        ----------
        fields : str or Collection[str]; positional-only
            Field names of the attributes.

        delimiter : str or tuple[str, str]; keyword-only; \
        default: :code:`(", ", " & ")`
            Delimiters to use to concatenate multiple values into a 
            string. If :code:`None`, the raw values are returned. If a 
            string, all values are concatenated using the delimiter. If 
            a tuple, all but the last value is concatenated using the 
            first delimiter, and the final value using the second 
            delimiter.

        Returns
        -------
        attributes : str, list[str], or dict[str, str | list[str]]
            Track attributes. If `fields` is a string, a list of strings
            or a string is returned if `delimiter` is or is not 
            :code:`None`, respectively. If `fields` is a collection of 
            strings, a dictionary mapping field names to their 
            corresponding values is returned.
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

        if delimiter is not None:
            if not (
                isinstance(delimiter, str)
                or (
                    isinstance(delimiter, ORDERED_COLLECTION_TYPES)
                    and len(delimiter) == 2
                )
            ):
                raise TypeError(
                    "`delimiter` must be a string or an ordered "
                    "collection of two strings."
                )

        return self._get(
            fields,
            delimiter=delimiter,
            single_delimiter=isinstance(delimiter, str),
        )

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
        if self._ignore_duplicates:
            new_keys = set()
            for key, value in kwargs.items():
                if not isinstance(key, str):
                    raise TypeError(f"Field name `{key}` is not a string.")
                key = self._normalize_key(key)
                new_keys.add(key)
                self._fields[key] = dict.fromkeys(self._fields.get(key, ()))
                if isinstance(value := self._to_string(value), str):
                    if value:
                        self._fields[key][value] = None
                elif isinstance(value, COLLECTION_TYPES):
                    for item in value:
                        if isinstance(item := self._to_string(item), str):
                            if item:
                                self._fields[key][item] = None
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
            for key in new_keys:
                self._fields[key] = list(self._fields[key].keys())
        else:
            for key, value in kwargs.items():
                if not isinstance(key, str):
                    raise TypeError(f"Field name `{key}` is not a string.")
                if (key := self._normalize_key(key)) not in self._fields:
                    self._fields[key] = []
                if isinstance(value := self._to_string(value), str):
                    if value:
                        self._fields[key].append(value)
                elif isinstance(value, COLLECTION_TYPES):
                    for item in value:
                        if isinstance(item := self._to_string(item), str):
                            if item:
                                self._fields[key].append(item)
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

        Examples
        --------
        >>> vc = VorbisComment()
        >>> vc.set(title="I Found U", artist=["Passion Pit", "Galantis"])
        >>> vc.set(
        ...     ALBUM="Church",
        ...     ALBUMARTIST="Galantis"
        ... )
        >>> vc.set(
        ...     compilation=False,
        ...     date=datetime(2019, 5, 15, 12, 0, 0),
        ...     tracknumber=9,
        ...     tracktotal=14
        ... )
        >>> vc.set(**{"日本語版": True})
        """
        for key, value in kwargs.items():
            if not isinstance(key, str):
                raise TypeError(f"Field name `{key}` is not a string.")
            key = self._normalize_key(key)
            if isinstance(value := self._to_string(value), str):
                if value:
                    self._fields[key] = [value]
            elif isinstance(value, COLLECTION_TYPES):
                self._fields[key] = []
                for item in value:
                    if isinstance(item := self._to_string(item), str):
                        if item:
                            self._fields[key].append(item)
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
