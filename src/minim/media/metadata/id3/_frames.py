from __future__ import annotations

import re
import zlib
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import MAXYEAR, MINYEAR, datetime
from typing import TYPE_CHECKING, ClassVar, NamedTuple

from ...._types import ORDERED_COLLECTION_TYPES
from ...._utility import (
    ASCII_CHARS_REGEX,
    as_buffer,
    join_values,
    prepare_isrc,
    set_obj_attr,
    validate_number,
    validate_numeric,
    validate_range,
    validate_type,
)
from ._shared import (
    GENRES,
    TAG_VERSIONS,
    UNSYNCHRONIZATION_RE,
    decode_synchsafe_int,
    encode_synchsafe_int,
    normalize_id3v2_tag_version,
)

if TYPE_CHECKING:
    from typing import Any, Self

    from ...._types import BytesLike, OrderedCollection


class DateTime:
    """
    Datetime with optional components and free-form extras.
    """

    _DATETIME_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"^(\d{4})?(?:-(\d{2})(?:-(\d{2})(?:T(\d{2})(?::(\d{2})(?::(\d{2}))?)?)?)?)?(.*)$"
    )

    __slots__ = (
        "_day",
        "_extra",
        "_hour",
        "_minute",
        "_month",
        "_second",
        "_year",
    )

    def __init__(
        self,
        year: int | None = None,
        month: int | None = None,
        day: int | None = None,
        hour: int | None = None,
        minute: int | None = None,
        second: int | None = None,
        extra: str | None = None,
        *,
        strict: bool = True,
    ) -> None:
        """
        Parameters
        ----------
        year : int; optional
            Year.

        month : int; optional
            Month.

        day : int; optional
            Day.

        hour : int; optional
            Hour.

        minute : int; optional
            Minute.

        second : int; optional
            Second.

        extra : str; optional
            Extra information, such as timezone or fractional seconds.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the audio
            format specifications.
        """
        self._year = year
        self._month = month
        self._day = day
        self._hour = hour
        self._minute = minute
        self._second = second
        self._extra = extra
        if strict:
            if year is not None:
                validate_range("year", year, MINYEAR, MAXYEAR)
            if month is not None:
                validate_range("month", month, 1, 12)
            if day is not None:
                validate_range(
                    "day",
                    day,
                    1,
                    self._get_num_days_in_month(month, year=year)
                    if year and month
                    else 31,
                )
            if hour is not None:
                validate_range("hour", hour, 0, 23)
            if minute is not None:
                validate_range("minute", minute, 0, 59)
            if second is not None:
                validate_range("second", second, 0, 59)
            if extra is not None:
                validate_type("extra", extra, str)

    def __or__(self, other: Self) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand type(s) for |: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )
        return DateTime(
            year=other.year or self.year,
            month=other.month or self.month,
            day=other.day or self.day,
            hour=other.hour or self.hour,
            minute=other.minute or self.minute,
            second=other.second or self.second,
            extra=other.extra or self.extra,
            strict=False,
        )

    def __ior__(self, other: Self) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand type(s) for |=: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )
        if other.year is not None:
            self.year = other.year
        if other.month is not None:
            self.month = other.month
        if other.day is not None:
            self.day = other.day
        if other.hour is not None:
            self.hour = other.hour
        if other.minute is not None:
            self.minute = other.minute
        if other.second is not None:
            self.second = other.second
        if other.extra is not None:
            self.extra = other.extra
        return self

    @classmethod
    def from_string(cls, dt: str, /, *, strict: bool = True) -> DateTime:
        """
        Instantiate a :cls:`DateTime` object from a datetime string in
        ISO-8601 format.

        Parameters
        ----------
        dt : str; positional-only
            Datetime, in ISO-8601 format.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the audio
            format specifications.

        Returns
        -------
        dt : minim.metadata.id3.DateTime
            Datetime.
        """
        match = cls._DATETIME_RE.match(dt.upper())
        *datetime_components, extra = match.groups()
        return cls(
            *(
                None if dt_comp is None else int(dt_comp)
                for dt_comp in datetime_components
            ),
            extra.strip() or None,
            strict=strict,
        )

    @classmethod
    def from_tuple(
        cls, dt: tuple[int | str | None, ...], /, *, strict: bool = True
    ) -> DateTime:
        """
        Instantiate a :cls:`DateTime` object from a tuple of datetime
        components.

        Parameters
        ----------
        dt : tuple[int | str | None, ...]; positional-only
            Datetime components, in order of year, month, day, hour,
            minute, second, and extras. Optional components may be
            represented as :code:`None` or omitted only if there are no
            more components after them.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the audio
            format specifications.

        Returns
        -------
        dt : minim.metadata.id3.DateTime
            Datetime.
        """
        if not 1 <= len(dt) <= 7:
            raise ValueError(
                f"Datetime component tuple {dt!r} must have between "
                f"one and seven components."
            )

        return cls(
            *(None if dt_comp is None else int(dt_comp) for dt_comp in dt),
            strict=strict,
        )

    @staticmethod
    def _get_num_days_in_month(month: int, /, year: int) -> int:
        """
        Get the number of days in a month for a given year.

        Parameters
        ----------
        month : int; positional-only
            Month.

        year : int; positional-only
            Year.

        Returns
        -------
        num_days : int
            Number of days in the month for the given year.
        """
        if month == 2:
            return (
                29
                if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
                else 28
            )
        if month in {4, 6, 9, 11}:
            return 30
        return 31

    @property
    def year(self) -> int | None:
        """
        Year.
        """
        return self._year

    @year.setter
    def year(self, value: int | None) -> None:
        if value is not None:
            validate_range("year", value, MINYEAR, MAXYEAR)
            if self._month:
                validate_range(
                    "day",
                    self._day,
                    1,
                    self._get_num_days_in_month(self._month, year=value),
                )
        self._year = value

    @property
    def month(self) -> int | None:
        """
        Month.
        """
        return self._month

    @month.setter
    def month(self, value: int | None) -> None:
        if value is not None:
            validate_range("month", value, 1, 12)
            if self._year:
                validate_range(
                    "day",
                    self._day,
                    1,
                    self._get_num_days_in_month(value, year=self._year),
                )
        self._month = value

    @property
    def day(self) -> int | None:
        """
        Day.
        """
        return self._day

    @day.setter
    def day(self, value: int | None) -> None:
        if value is not None:
            validate_range(
                "day",
                value,
                1,
                self._get_num_days_in_month(self._month, year=self._year)
                if self._year and self._month
                else 31,
            )
        self._day = value

    @property
    def hour(self) -> int | None:
        """
        Hour.
        """
        return self._hour

    @hour.setter
    def hour(self, value: int | None) -> None:
        if value is not None:
            validate_range("hour", value, 0, 23)
        self._hour = value

    @property
    def minute(self) -> int | None:
        """
        Minute.
        """
        return self._minute

    @minute.setter
    def minute(self, value: int | None) -> None:
        if value is not None:
            validate_range("minute", value, 0, 59)
        self._minute = value

    @property
    def second(self) -> int | None:
        """
        Second.
        """
        return self._second

    @second.setter
    def second(self, value: int | None) -> None:
        if value is not None:
            validate_range("second", value, 0, 59)
        self._second = value

    @property
    def extra(self) -> str | None:
        """
        Extra information, such as timezone or fractional seconds.
        """
        return self._extra

    @extra.setter
    def extra(self, value: str | None) -> None:
        if value is not None:
            validate_type("extra", value, str)
        self._extra = value

    def to_string(self, *, use_placeholders: bool = False) -> str:
        """
        Convert the datetime to a string in ISO-8601 format.

        Parameters
        ----------
        use_placeholders: bool; keyword-only; default: :code:`False`
            Whether to use placeholders in place of missing datetime
            components.

        Returns
        -------
        dt : str
            Datetime, in ISO-8601 format.
        """
        if use_placeholders:
            dt = "YYYY" if self._year is None else f"{self._year:04}"
            dt += "-MM" if self._month is None else f"-{self._month:02}"
            dt += "-DD" if self._day is None else f"-{self._day:02}"
            dt += "Thh" if self._hour is None else f"T{self._hour:02}"
            dt += ":mm" if self._minute is None else f":{self._minute:02}"
            dt += ":ss" if self._second is None else f":{self._second:02}"
            if self._extra is not None:
                dt += str(self._extra)
        else:
            if self._year is None:
                return ""

            dt = f"{self._year:04}"
            if self._month is None:
                return dt

            dt += f"-{self._month:02}"
            if self._day is None:
                return dt

            dt += f"-{self._day:02}"
            if self._hour is None:
                return dt

            dt += f"T{self._hour:02}"
            if self._minute is None:
                return dt

            dt += f":{self._minute:02}"
            if self._second is None:
                return dt

            dt += f":{self._second:02}"
            if self._extra is not None:
                dt += str(self._extra)
        return dt


class Position(NamedTuple):
    """
    Position within a set.
    """

    number: int
    total: int | None = None

    @classmethod
    def from_string(
        cls, position: str, /, *, name: str = "position", strict: bool = True
    ) -> Position:
        """
        Instantiate a :cls:`Position` object from a string.

        Parameters
        ----------
        position : str; positional-only
            Position within a set.

        name : str; keyword-only; default: :code:`"position"`
            Type of position.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the audio
            format specifications.

        Returns
        -------
        position : minim.metadata.id3.Position
            Position within a set.
        """
        num_slashes = position.count("/")
        if num_slashes > 1:
            raise ValueError(f"Invalid {name} number {position!r}.")
        if num_slashes:
            position = position.split("/", maxsplit=1)
            if strict:
                validate_numeric(f"{name}[0]", position[0], int, 1)
            if position[1]:
                if strict:
                    validate_numeric(f"{name}[1]", position[1], int, 1)
                return cls(int(position[0]), int(position[1]))
            return cls(int(position[0]), None)
        else:
            if strict:
                validate_numeric(name, position, int, 1)
            return cls(int(position), None)

    @classmethod
    def from_tuple(
        cls,
        position: tuple[int, int | None],
        /,
        *,
        name: str = "position",
        strict: bool = True,
    ) -> Position:
        """
        Instantiate a :cls:`Position` object from a tuple.

        Parameters
        ----------
        position : tuple[int, int | None]; positional-only
            Position within a set.

        name : str; keyword-only; default: :code:`"position"`
            Type of position.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the audio
            format specifications.

        Returns
        -------
        position : minim.metadata.id3.Position
            Position within a set.
        """
        if strict:
            validate_numeric(f"{name}[0]", position[0], int, 1)
        if position[1]:
            if strict:
                validate_numeric(f"{name}[1]", position[1], int, 1)
            return cls(int(position[0]), int(position[1]))
        return cls(int(position[0]), None)

    def to_string(self) -> str:
        """
        Convert the position to a string.

        Returns
        -------
        position : str
            Position within a set as a string.
        """
        return (
            f"{self.number}/{self.total}"
            if self.total is not None
            else str(self.number)
        )


class ID3v2FrameFlags:
    """
    Flags for the ID3v2 frame.
    """

    __slots__ = (
        "_discard_on_file_alter",
        "_discard_on_tag_alter",
        "_has_data_length_indicator",
        "_has_group_id",
        "_is_compressed",
        "_is_encrypted",
        "_is_read_only",
        "_is_unsynchronized",
    )

    def __init__(
        self,
        *,
        discard_on_tag_alter: bool = False,
        discard_on_file_alter: bool = False,
        is_read_only: bool = False,
        has_group_id: bool = False,
        is_compressed: bool = False,
        is_encrypted: bool = False,
        is_unsynchronized: bool = False,
        has_data_length_indicator: bool = False,
    ) -> None:
        """
        Parameters
        ----------
        discard_on_tag_alter : bool; keyword-only; default: \
        :code:`False`
            Whether to discard the current frame if it is unknown and
            the ID3 tag it belongs to is edited.

        discard_on_file_alter : bool; keyword-only; default: \
        :code:`False`
            Whether to discard the current frame if it is unknown and
            the MPEG file it belongs to is edited.

        is_read_only : bool; keyword-only; default: :code:`False`
            Whether the current frame is read-only.

        has_group_id : bool; keyword-only; default: :code:`False`
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
        self.discard_on_tag_alter = discard_on_tag_alter
        self.discard_on_file_alter = discard_on_file_alter
        self.is_read_only = is_read_only
        self.has_group_id = has_group_id
        if is_compressed and not has_data_length_indicator:
            raise ValueError(
                "A data length indicator must be present when an ID3v2 "
                "frame is compressed."
            )
        self.is_compressed = is_compressed
        self.is_encrypted = is_encrypted
        self.is_unsynchronized = is_unsynchronized
        self.has_data_length_indicator = has_data_length_indicator

    @classmethod
    def _from_bytes_2_3(
        cls, status_flags: int, format_flags: int, /, *, strict: bool = True
    ) -> ID3v2FrameFlags:
        """
        Instantiate an :class:`ID3v2FrameFlags` object from ID3v2.3
        frame flags bytes.

        Parameters
        ----------
        status_flags : int; positional-only
            ID3v2.3 frame status flags byte.

        format_flags : int; positional-only
            ID3v2.3 frame format flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.ID3v2FrameFlags
            Flags for the ID3v2 frame.
        """
        if strict:
            if status_flags & 0x1F:
                raise ValueError(
                    "Reserved bits set in ID3v2 frame status flags byte."
                )
            if format_flags & 0x1F:
                raise ValueError(
                    "Reserved bits set in ID3v2 frame format flags byte."
                )

        obj = cls.__new__(cls)
        obj._discard_on_tag_alter = bool(status_flags & 0x80)
        obj._discard_on_file_alter = bool(status_flags & 0x40)
        obj._is_read_only = bool(status_flags & 0x20)
        obj._is_compressed = obj._has_data_length_indicator = bool(
            format_flags & 0x80
        )
        obj._is_encrypted = bool(format_flags & 0x40)
        obj._has_group_id = bool(format_flags & 0x20)
        obj._is_unsynchronized = False
        return obj

    @classmethod
    def _from_bytes_2_4(
        cls, status_flags: int, format_flags: int, /, *, strict: bool = True
    ) -> ID3v2FrameFlags:
        """
        Instantiate an :class:`ID3v2FrameFlags` object from ID3v2.4
        frame status flags byte.

        Parameters
        ----------
        status_flags : int; positional-only
            ID3v2.4 frame status flags byte.

        format_flags : int; positional-only
            ID3v2.4 frame format flags byte.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.ID3v2FrameFlags
            Flags for the ID3v2 frame.
        """
        if strict:
            if status_flags & 0x8F:
                raise ValueError(
                    "Reserved bits set in ID3v2 frame status flags byte."
                )
            if format_flags & 0x70:
                raise ValueError(
                    "Reserved bits set in ID3v2 frame format flags byte."
                )

        is_compressed = bool(format_flags & 0x08)
        has_data_length_indicator = bool(format_flags & 0x01)
        if is_compressed and not has_data_length_indicator:
            raise ValueError(
                "A data length indicator must be present when an "
                "ID3v2.4 frame is compressed."
            )

        obj = cls.__new__(cls)
        obj._discard_on_tag_alter = bool(status_flags & 0x40)
        obj._discard_on_file_alter = bool(status_flags & 0x20)
        obj._is_read_only = bool(status_flags & 0x10)
        obj._has_group_id = bool(format_flags & 0x40)
        obj._is_compressed = is_compressed
        obj._is_encrypted = bool(format_flags & 0x04)
        obj._is_unsynchronized = bool(format_flags & 0x02)
        obj._has_data_length_indicator = has_data_length_indicator
        return obj

    @classmethod
    def from_bytes(
        cls,
        status_flags: int,
        format_flags: int,
        /,
        tag_version: str | tuple[int, int, int],
        *,
        strict: bool = True,
    ) -> ID3v2FrameFlags:
        """
        Instantiate an :class:`ID3v2FrameFlags` object from ID3v2 frame
        status flags bytes.

        Parameters
        ----------
        status_flags : int; positional-only
            ID3v2 frame status flags byte.

        format_flags : int; positional-only
            ID3v2 frame format flags byte.

        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.ID3v2FrameFlags
            Flags for the ID3v2 frame.
        """
        validate_number("status_flags", status_flags, int, 0)
        validate_number("format_flags", format_flags, int, 0)
        match normalize_id3v2_tag_version(tag_version):
            case (2, 4, _):
                return cls._from_bytes_2_4(
                    status_flags, format_flags, strict=strict
                )
            case (2, 3, _):
                return cls._from_bytes_2_3(
                    status_flags, format_flags, strict=strict
                )
            case (2, 2, _):
                raise ValueError("ID3v2.2 frames do not have frame flags.")
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )

    @property
    def discard_on_tag_alter(self) -> bool:
        """
        Whether to discard the current frame if it is unknown and the
        ID3 tag it belongs to is edited.
        """
        return self._discard_on_tag_alter

    @discard_on_tag_alter.setter
    def discard_on_tag_alter(self, value: bool, /) -> None:
        validate_type("discard_on_tag_alter", value, bool)
        self._discard_on_tag_alter = value

    @property
    def discard_on_file_alter(self) -> bool:
        """
        Whether to discard the current frame if it is unknown and the
        MPEG file it belongs to is edited.
        """
        return self._discard_on_file_alter

    @discard_on_file_alter.setter
    def discard_on_file_alter(self, value: bool, /) -> None:
        validate_type("discard_on_file_alter", value, bool)
        self._discard_on_file_alter = value

    @property
    def is_read_only(self) -> bool:
        """
        Whether the current frame is read-only.
        """
        return self._is_read_only

    @is_read_only.setter
    def is_read_only(self, value: bool, /) -> None:
        validate_type("is_read_only", value, bool)
        self._is_read_only = value

    @property
    def has_group_id(self) -> bool:
        """
        Whether the current frame has a grouping identifier.
        """
        return self._has_group_id

    @has_group_id.setter
    def has_group_id(self, value: bool, /) -> None:
        validate_type("has_group_id", value, bool)
        self._has_group_id = value

    @property
    def is_compressed(self) -> bool:
        """
        Whether the current frame is compressed.
        """
        return self._is_compressed

    @is_compressed.setter
    def is_compressed(self, value: bool, /) -> None:
        validate_type("is_compressed", value, bool)
        self._is_compressed = value
        if value:
            self._has_data_length_indicator = True

    @property
    def is_encrypted(self) -> bool:
        """
        Whether the current frame is encrypted.
        """
        return self._is_encrypted

    @is_encrypted.setter
    def is_encrypted(self, value: bool, /) -> None:
        validate_type("is_encrypted", value, bool)
        self._is_encrypted = value

    @property
    def is_unsynchronized(self) -> bool:
        """
        Whether the current frame is unsynchronized.
        """
        return self._is_unsynchronized

    @is_unsynchronized.setter
    def is_unsynchronized(self, value: bool, /) -> None:
        validate_type("is_unsynchronized", value, bool)
        self._is_unsynchronized = value

    @property
    def has_data_length_indicator(self) -> bool:
        """
        Whether the current frame has an extra synchsafe integer
        preceding the payload.
        """
        return self._has_data_length_indicator

    @has_data_length_indicator.setter
    def has_data_length_indicator(self, value: bool, /) -> None:
        validate_type("has_data_length_indicator", value, bool)
        if not value and self._is_compressed:
            raise ValueError(
                "A data length indicator must be present when an "
                "ID3v2.4 frame is compressed."
            )
        self._has_data_length_indicator = value

    def serialize(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Serialize the ID3v2 frame flags to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        stream : bytes
            Bytestream containing the ID3v2 frame flags.
        """
        match tag_version := normalize_id3v2_tag_version(tag_version):
            case (2, 4, _):
                return bytes(
                    (
                        (
                            (0x40 if self._discard_on_tag_alter else 0)
                            | (0x20 if self._discard_on_file_alter else 0)
                            | (0x10 if self._is_read_only else 0)
                        ),
                        (
                            (0x40 if self._has_group_id else 0)
                            | (0x08 if self._is_compressed else 0)
                            | (0x04 if self._is_encrypted else 0)
                            | (0x02 if self._is_unsynchronized else 0)
                            | (0x01 if self._has_data_length_indicator else 0)
                        ),
                    )
                )
            case (2, 3, _):
                return bytes(
                    (
                        (
                            (0x80 if self._discard_on_tag_alter else 0)
                            | (0x40 if self._discard_on_file_alter else 0)
                            | (0x20 if self._is_read_only else 0)
                        ),
                        (
                            (0x80 if self._is_compressed else 0)
                            | (0x40 if self._is_encrypted else 0)
                            | (0x20 if self._has_group_id else 0)
                        ),
                    )
                )
            case (2, 2, _):
                raise ValueError("ID3v2.2 frames do not have frame flags.")
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )


class ID3v2Frame(ABC):
    """
    ID3v2 frame.
    """

    _TEXT_ENCODINGS: ClassVar[dict[int | str, int | str]] = {
        0: "iso-8859-1",
        1: "utf-16",
        2: "utf-16be",
        3: "utf-8",
    }
    _TEXT_ENCODINGS |= {v: k for k, v in _TEXT_ENCODINGS.items()}
    _REGISTRY: ClassVar[dict[bytes, type[ID3v2Frame]]] = {}

    _allow_multiple: bool

    __slots__ = ("_flags", "_group_id")

    def __init__(
        self,
        *,
        flags: ID3v2FrameFlags | None = None,
        group_id: int | None = None,
    ) -> None:
        """
        Parameters
        ----------
        flags : minim.media.metadata.ID3v2FrameFlags; keyword-only; \
        optional
            Flags for the ID3v2 frame.
        """
        if flags is None:
            self._flags = ID3v2FrameFlags()
            self._group_id = None
        else:
            validate_type("flags", flags, ID3v2FrameFlags)
            self._flags = flags
            if flags._has_group_id:
                validate_number("group_id", group_id, int, 0, 255)
            elif group_id is not None:
                raise ValueError(
                    "A grouping identifier was specified, but the "
                    "ID3v2 frame flags do not indicate grouping."
                )
            self._group_id = group_id

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
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2Frame:
        """
        Instantiate an :class:`ID3v2Frame` object from an ID3v2.2 frame
        bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing an ID3v2.2 frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        frame : minim.media.metadata.ID3v2Frame
            ID3v2 frame.
        """
        if strict and len(stream) < 7:
            raise ValueError(
                "ID3v2.2 frame must be at least 1 byte long, excluding "
                "the header."
            )

        obj = cls.__new__(cls)
        obj._flags = ID3v2FrameFlags()
        return obj

    @classmethod
    @abstractmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2Frame:
        """
        Instantiate an :class:`ID3v2Frame` object from an ID3v2.3 frame
        bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing an ID3v2.3 frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        frame : minim.media.metadata.ID3v2Frame
            ID3v2 frame.
        """
        if strict and len(stream) < 11:
            raise ValueError(
                "ID3v2.3 frame must be at least 1 byte long, excluding "
                "the header."
            )

        flags = ID3v2FrameFlags._from_bytes_2_3(
            stream[8], stream[9], strict=strict
        )
        if flags._is_encrypted:
            obj = UnknownID3v2Frame.__new__(UnknownID3v2Frame)
            obj._frame_id = stream[:4].tobytes()
            obj._frame_length = int.from_bytes(stream[4:8], byteorder="big")
            obj._frame_data = stream[10 : 10 + obj._frame_length].tobytes()
            return obj

        obj = cls.__new__(cls)
        obj._flags = flags
        return obj

    @classmethod
    @abstractmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2Frame:
        """
        Instantiate an :class:`ID3v2Frame` object from an ID3v2.4 frame
        bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing an ID3v2.4 frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        frame : minim.media.metadata.ID3v2Frame
            ID3v2 frame.
        """
        if strict and len(stream) < 11:
            raise ValueError(
                "ID3v2.4 frame must be at least 1 byte long, excluding "
                "the header."
            )

        flags = ID3v2FrameFlags._from_bytes_2_4(
            stream[8], stream[9], strict=strict
        )
        if flags._is_encrypted:
            obj = UnknownID3v2Frame.__new__(UnknownID3v2Frame)
            obj._frame_id = stream[:4].tobytes()
            obj._frame_length = int.from_bytes(stream[4:8], byteorder="big")
            obj._frame_data = stream[10 : 10 + obj._frame_length].tobytes()
            return obj

        obj = cls.__new__(cls)
        obj._flags = flags
        return obj

    @classmethod
    def from_stream(
        cls,
        stream: BytesLike,
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
        stream : BytesLike; positional-only; optional
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
        stream = as_buffer(stream)
        tag_version = normalize_id3v2_tag_version(tag_version)
        expected_frame_id = cls.get_frame_id(tag_version)
        if stream[: len(expected_frame_id)] != expected_frame_id:
            raise ValueError(
                f"`bytestream` does not contain a {expected_frame_id} frame."
            )

        match tag_version:
            case (2, 4, _):
                return cls._from_stream_2_4(stream, strict=strict)
            case (2, 3, _):
                return cls._from_stream_2_3(stream, strict=strict)
            case (2, 2, _):
                return cls._from_stream_2_2(stream, strict=strict)
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )

    @classmethod
    def get_frame_id(
        cls, tag_version: str | tuple[int, int, int]
    ) -> bytes | list[bytes] | None:
        """
        Get the ID3v2 frame IDs.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        frame_id : bytes, list[bytes], or None
            ID3v2 frame IDs. If no native frame is available for the
            specified ID3v2 tag version, :code:`None` is returned.
        """
        match normalize_id3v2_tag_version(tag_version):
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
    def _encode_2_2(frame_id: bytes, frame_data: bytes, /) -> bytes:
        """
        Encode an ID3v2.2 frame.

        Parameters
        ----------
        frame_id : bytes; positional-only
            Frame ID.

        frame_data : bytes; positional-only
            Frame data.

        Returns
        -------
        frame : bytes
            Encoded frame.
        """
        return (
            frame_id
            + len(frame_data).to_bytes(length=3, byteorder="big")
            + frame_data
        )

    @staticmethod
    def _split_bytestream(
        stream: memoryview, /, encoding: str, *, max_splits: int | None = None
    ) -> list[str]:
        """
        Split and decode a bytestream containing one or more encoded
        strings separated by null bytes.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing one or more encoded strings.

        encoding : str; positional-only
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        max_splits : int or None; keyword-only; default: :code:`None`
            Maximum number of splits to perform. If :code:`None`, all
            splits are performed.

        Returns
        -------
        strings : list[str]
            List of decoded strings.
        """
        match encoding:
            case "utf-16" | "utf-16be":
                strings = []
                offset = splits = 0
                length = len(stream)
                length_minus_one = length - 1

                while offset < length:
                    end_offset = None
                    for idx in range(offset, length_minus_one, 2):
                        if stream[idx] == 0 and stream[idx + 1] == 0:
                            end_offset = idx
                            break

                    if end_offset is None:
                        strings.append(
                            stream[offset:].tobytes().decode(encoding=encoding)
                        )
                        break

                    strings.append(
                        stream[offset:end_offset]
                        .tobytes()
                        .decode(encoding=encoding)
                    )
                    offset = end_offset + 2
                    splits += 1

                    if max_splits is not None and splits >= max_splits:
                        strings.append(
                            stream[offset:].tobytes().decode(encoding=encoding)
                        )
                        break

                return strings

            case "iso-8859-1" | "utf-8":
                return [
                    s.decode(encoding=encoding)
                    for s in stream.tobytes()
                    .rstrip(b"\x00")
                    .split(
                        b"\x00",
                        maxsplit=-1 if max_splits is None else max_splits,
                    )
                ]

            case _:
                raise ValueError(
                    f"Invalid or unsupported text encoding {encoding!r}."
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
    def _key(self) -> str:
        """
        Unique key.
        """
        if not self._allow_multiple:
            raise AttributeError(
                f"{type(self).__name__} cannot appear more than "
                "once in an ID3v2 tag, and thus does not have a unique "
                "key."
            )

    @property
    def flags(self) -> ID3v2FrameFlags:
        """
        Flags for the ID3v2 frame.
        """
        return self._flags

    @property
    def group_id(self) -> int | None:
        """
        Grouping identifier.
        """
        return self._group_id

    @group_id.setter
    def group_id(self, value: int | None) -> None:
        if value is None:
            self._flags._has_group_id = False
        else:
            validate_number("group_id", value, int, 0, 255)
        self._group_id = value

    @abstractmethod
    def serialize(
        self,
        tag_version: str | tuple[int, int, int],
        *,
        text_encoding: str | None = None,
    ) -> bytes:
        """
        Serialize the ID3v2 frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        text_encoding : str; keyword-only; optional
            Text encoding. If :code:`None`, the text encoding already
            associated with the frame is used.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        Returns
        -------
        stream : bytes
            Bytestream containing the ID3v2 frame.
        """
        ...

    def _decode_2_3(
        self, stream: memoryview, /, frame_length: int, *, strict: bool = True
    ) -> tuple[memoryview, int, int]:
        """
        Decode an ID3v2.3 frame.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing an ID3v2.3 frame.

        frame_length : int
            Length of encoded frame data, in bytes.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        stream : memoryview
            Decoded frame data.

        offset : int
            Byte offset marking the start of frame data.

        frame_length : int
            Length of decoded frame data, in bytes.
        """
        offset = 10
        flags = self._flags
        if flags._is_compressed:
            end_offset = offset + 4
            decompressed_length = int.from_bytes(
                stream[offset:end_offset], byteorder="big"
            )
            offset = end_offset
        if flags._has_group_id:
            self._group_id = stream[offset]
            offset += 1
        if flags._is_compressed:
            stream = zlib.decompress(stream[offset:frame_length])
            if strict and (data_length := len(stream)) != decompressed_length:
                raise ValueError(
                    f"Length of decoded frame data ({data_length}) "
                    "does not match expected decompressed size "
                    f"({decompressed_length})."
                )
            offset = 0
            frame_length = decompressed_length
        return as_buffer(stream), offset, frame_length

    def _decode_2_4(
        self, stream: memoryview, /, frame_length: int, *, strict: bool = True
    ) -> tuple[memoryview, int, int]:
        """
        Decode an ID3v2.4 frame.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing an ID3v2.4 frame.

        frame_length : int
            Length of encoded frame data, in bytes.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        stream : memoryview
            Decoded frame data.

        offset : int
            Byte offset marking the start of frame data.

        frame_length : int
            Length of decoded frame data, in bytes.
        """
        offset = 10
        flags = self._flags
        if flags._has_group_id:
            self._group_id = stream[offset]
            offset += 1
        if flags._has_data_length_indicator:
            end_offset = offset + 4
            data_length = decode_synchsafe_int(*stream[offset:end_offset])
            offset = end_offset
        if flags._is_unsynchronized:
            stream = (
                stream[offset:frame_length]
                .tobytes()
                .replace(b"\xff\x00", b"\xff")
            )
            offset = 0
            frame_length = len(stream)
        if flags._is_compressed:
            stream = zlib.decompress(stream[offset:frame_length])
            offset = 0
        if flags._has_data_length_indicator:
            if strict and (data_length_ := len(stream)) != data_length:
                raise ValueError(
                    f"Length of decoded frame data ({data_length_}) "
                    f"does not match data length indicator ({data_length})."
                )
            frame_length = data_length
        return as_buffer(stream), offset, frame_length

    def _encode_2_3(self, frame_id: bytes, frame_data: bytes, /) -> bytes:
        """
        Encode an ID3v2.3 frame.

        Parameters
        ----------
        frame_id : bytes; positional-only
            Frame ID.

        frame_data : bytes; positional-only
            Frame data.

        Returns
        -------
        frame : bytes
            Encoded frame.
        """
        flags = self._flags
        frame_length = len(frame_data)

        extra_info = bytearray()
        if flags._is_compressed:
            extra_info.extend(frame_length.to_bytes(4, byteorder="big"))
        if flags._has_group_id:
            extra_info.append(self._group_id)

        if flags._is_compressed:
            frame_data = zlib.compress(frame_data)
            frame_length = len(frame_data)

        return b"".join(
            (
                frame_id,
                (frame_length + len(extra_info)).to_bytes(
                    length=4, byteorder="big"
                ),
                self._flags.serialize((2, 3, 0)),
                extra_info,
                frame_data,
            )
        )

    def _encode_2_4(self, frame_id: bytes, frame_data: bytes, /) -> bytes:
        """
        Encode an ID3v2.4 frame.

        Parameters
        ----------
        frame_id : bytes; positional-only
            Frame ID.

        frame_data : bytes; positional-only
            Frame data.

        Returns
        -------
        frame : bytes
            Encoded frame.
        """
        flags = self._flags

        extra_info = bytearray()
        if flags._has_group_id:
            extra_info.append(self._group_id)
        if flags._has_data_length_indicator:
            extra_info.extend(encode_synchsafe_int(len(frame_data)))

        if flags._is_compressed:
            frame_data = zlib.compress(frame_data)
        if flags._is_unsynchronized:
            frame_data = UNSYNCHRONIZATION_RE.sub(b"\xff\x00", frame_data)

        return b"".join(
            (
                frame_id,
                bytes(encode_synchsafe_int(len(frame_data) + len(extra_info))),
                self._flags.serialize((2, 4, 0)),
                extra_info,
                frame_data,
            )
        )

    def _resolve_text_encoding(
        self, text_encoding: str | None, tag_version: tuple[int, int, int], /
    ) -> str:
        """
        Resolve the text encoding to use.

        Parameters
        ----------
        text_encoding : str or None; positional-only
            Text encoding. If :code:`None`, the default text encoding is
            used.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        tag_version : tuple[int, int, int]; positional-only
            ID3v2 tag version.

            **Valid values**: :code:`(2, 2, 0)`, :code:`(2, 3, 0)`,
            :code:`(2, 4, 0)`.

        Returns
        -------
        text_encoding : str
            Resolved text encoding.
        """
        TEXT_ENCODINGS = self._TEXT_ENCODINGS
        if text_encoding is None:
            text_encoding = (
                self._text_encoding
                if tag_version[:2] == (2, 4)
                else TEXT_ENCODINGS[
                    min(TEXT_ENCODINGS[self._text_encoding], 1)
                ]
            )
        else:
            text_encoding_byte = TEXT_ENCODINGS.get(text_encoding)
            if text_encoding_byte is None:
                valid_text_encodings = join_values(
                    (
                        te for te in TEXT_ENCODINGS if isinstance(te, str)
                    ).values()
                )
                raise ValueError(
                    f"Invalid text encoding {text_encoding!r}. Valid "
                    f"values: {valid_text_encodings}."
                )
            if tag_version[:2] != (2, 4):
                text_encoding = TEXT_ENCODINGS[min(text_encoding_byte, 1)]
        return text_encoding


class ID3v2TextInfoFrame(ID3v2Frame):
    """
    Text information frame.
    """

    _allow_multiple: ClassVar[bool] = False
    _frame_ids: ClassVar[dict[int, bytes]] = {}

    __slots__ = ("_text_encoding", "_text_info")

    def __init__(
        self,
        text_info: str | OrderedCollection[str],
        /,
        *,
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        text_info : str or OrderedCollection[str]; positional-only
            Text information.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        flags : minim.media.metadata.ID3v2FrameFlags; keyword-only; \
        optional
            Flags for the ID3v2 frame.
        """
        super().__init__(flags=flags)

        if isinstance(text_info, str):
            self._text_info = [text_info]
        elif isinstance(text_info, ORDERED_COLLECTION_TYPES):
            self._text_info = _text_info = []
            for ti_idx, ti in enumerate(text_info):
                validate_type(f"text_info[{ti_idx}]", ti, str)
                _text_info.append(ti)
        else:
            raise TypeError(
                "`text_info` must be a string or an ordered collection "
                "of strings."
            )

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        if text_encoding == "iso-8859-1":
            try:
                for ti in text_info:
                    ti.encode(encoding=text_encoding)
                is_utf = False
            except UnicodeEncodeError:
                is_utf = True
            if is_utf:
                raise ValueError(
                    "`text_info` cannot be encoded using ISO-8859-1."
                )
        self._text_encoding = text_encoding

    def __add__(self, other: ID3v2TextInfoFrame) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand type(s) for +: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )
        if self._allow_multiple:
            raise ValueError(
                f"{type_.__name__} can appear multiple times in a "
                "ID3v2 tag, so multiple values should be stored in "
                "separate instances."
            )
        TEXT_ENCODINGS = self._TEXT_ENCODINGS
        return type_(
            self._text_info + other._text_info,
            text_encoding=TEXT_ENCODINGS[
                max(
                    TEXT_ENCODINGS[self._text_encoding],
                    TEXT_ENCODINGS[other._text_encoding],
                )
            ],
            flags=self._flags,
        )

    def __iadd__(self, other: ID3v2TextInfoFrame) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand type(s) for +=: "
                f"'{type_.__name__}' and {type(other).__name__!r}."
            )
        if self._allow_multiple:
            raise ValueError(
                f"{type_.__name__} can appear multiple times in a "
                "ID3v2 tag, so multiple values should be stored in "
                "separate instances."
            )
        self._text_info.extend(other._text_info)
        TEXT_ENCODINGS = self._TEXT_ENCODINGS
        self._text_encoding = TEXT_ENCODINGS[
            max(
                TEXT_ENCODINGS[self._text_encoding],
                TEXT_ENCODINGS[other._text_encoding],
            )
        ]
        return self

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TextInfoFrame:
        """
        Instantiate an ID3v2 text information frame object from an
        ID3v2.2 frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the text information frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        text_info_frame : minim.media.metadata.ID3v2TextInfoFrame
            Text information frame.
        """
        obj = super()._from_stream_2_2(stream, strict=strict)
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        obj._text_info = cls._split_bytestream(
            stream[7 : 6 + int.from_bytes(stream[3:6], byteorder="big")],
            encoding=obj._text_encoding,
        )
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TextInfoFrame:
        """
        Instantiate an ID3v2 text information frame object from an
        ID3v2.3 frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the text information frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        text_info_frame : minim.media.metadata.ID3v2TextInfoFrame
            Text information frame.
        """
        obj = super()._from_stream_2_3(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_3(
            stream,
            frame_length=10 + int.from_bytes(stream[4:8], byteorder="big"),
            strict=strict,
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        obj._text_info = cls._split_bytestream(
            stream[offset + 1 : offset + frame_length],
            encoding=obj._text_encoding,
        )
        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TextInfoFrame:
        """
        Instantiate an ID3v2 text information frame object from an
        ID3v2.4 frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the text information frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        text_info_frame : minim.media.metadata.ID3v2TextInfoFrame
            Text information frame.
        """
        obj = super()._from_stream_2_4(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_4(
            stream,
            frame_length=10 + decode_synchsafe_int(*stream[4:8]),
            strict=strict,
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        obj._text_info = cls._split_bytestream(
            stream[offset + 1 : offset + frame_length],
            encoding=obj._text_encoding,
        )
        return obj

    @property
    def text_info(self) -> list[str]:
        """
        Text information.
        """
        return self._text_info.copy()

    @property
    def text_encoding(self) -> str:
        """
        Text encoding.
        """
        return self._text_encoding

    def serialize(
        self,
        tag_version: str | tuple[int, int, int],
        *,
        text_encoding: str | None = None,
    ) -> bytes:
        """
        Serialize the text information frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        text_encoding : str; keyword-only; optional
            Text encoding. If :code:`None`, the text encoding already
            associated with the frame is used.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        Returns
        -------
        stream : bytes
            Bytestream containing the text information frame.
        """
        tag_version = normalize_id3v2_tag_version(tag_version)
        frame_id = self._frame_ids.get(tag_version[1])
        if frame_id is None:
            raise RuntimeError(
                f"A(n) {type(self).__name__} cannot be "
                f"serialized to an ID3v2.{tag_version[1]} tag."
            )

        text_encoding = self._resolve_text_encoding(text_encoding, tag_version)
        null_char = (
            b"\x00\x00" if text_encoding.startswith("utf-16") else b"\x00"
        )
        frame_data = self._TEXT_ENCODINGS[text_encoding].to_bytes(
            byteorder="big"
        ) + null_char.join(
            ti.encode(encoding=text_encoding) for ti in self._text_info
        )
        match tag_version:
            case (2, 4, _):
                return self._encode_2_4(frame_id, frame_data)
            case (2, 3, _):
                return self._encode_2_3(frame_id, frame_data)
            case (2, 2, _):
                return self._encode_2_2(frame_id, frame_data)
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )


class ID3v2DateTimeFrame(ID3v2TextInfoFrame):
    """
    Datetime frame.
    """

    _frame_ids: ClassVar[dict[int, bytes]] = {}

    __slots__ = ("_datetimes",)

    def __init__(
        self,
        datetimes: str
        | datetime
        | tuple[int | str, ...]
        | list[str | datetime | tuple[int | str, ...]],
        /,
        *,
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        datetimes : str, datetime.datetime, tuple[int | str, ...], or \
        list[str | datetime | tuple[int | str, ...]]; positional-only
            Datetime, in ISO-8601 format.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        flags : minim.media.metadata.ID3v2FrameFlags; keyword-only; \
        optional
            Flags for the ID3v2 frame.
        """
        super(ID3v2TextInfoFrame, self).__init__(flags=flags)

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        self._text_encoding = text_encoding
        datetimes = self._parse_datetimes(datetimes)
        if not isinstance(datetimes, list):
            datetimes = [datetimes]
        self._datetimes = datetimes

    def __add__(self, other: ID3v2DateTimeFrame) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand type(s) for +: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )
        TEXT_ENCODINGS = self._TEXT_ENCODINGS
        return type_(
            self._datetimes + other._datetimes,
            text_encoding=TEXT_ENCODINGS[
                max(
                    TEXT_ENCODINGS[self._text_encoding],
                    TEXT_ENCODINGS[other._text_encoding],
                )
            ],
            flags=self._flags,
        )

    def __iadd__(self, other: ID3v2DateTimeFrame) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand type(s) for +=: "
                f"'{type_.__name__}' and {type(other).__name__!r}."
            )
        self._datetimes.extend(other._datetimes)
        TEXT_ENCODINGS = self._TEXT_ENCODINGS
        self._text_encoding = TEXT_ENCODINGS[
            max(
                TEXT_ENCODINGS[self._text_encoding],
                TEXT_ENCODINGS[other._text_encoding],
            )
        ]
        return self

    def __or__(self, other: ID3v2DateTimeFrame) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand type(s) for |: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )
        if len(self._datetimes) != len(other._datetimes):
            raise ValueError(
                "Cannot combine ID3v2DateTimeFrame objects with "
                "different numbers of datetimes."
            )
        TEXT_ENCODINGS = self._TEXT_ENCODINGS
        return type_(
            (
                self_dt | other_dt
                for self_dt, other_dt in zip(self._datetimes, other._datetimes)
            ),
            text_encoding=TEXT_ENCODINGS[
                max(
                    TEXT_ENCODINGS[self._text_encoding],
                    TEXT_ENCODINGS[other._text_encoding],
                )
            ],
            flags=other._flags,
        )

    def __ior__(self, other: ID3v2DateTimeFrame) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand type(s) for |=: "
                f"'{type_.__name__}' and {type(other).__name__!r}."
            )
        if len(self._datetimes) != len(other._datetimes):
            raise ValueError(
                "Cannot combine ID3v2DateTimeFrame objects with "
                "different numbers of datetimes."
            )
        for self_dt, other_dt in zip(self._datetimes, other._datetimes):
            self_dt |= other_dt
        TEXT_ENCODINGS = self._TEXT_ENCODINGS
        self._text_encoding = TEXT_ENCODINGS[
            max(
                TEXT_ENCODINGS[self._text_encoding],
                TEXT_ENCODINGS[other._text_encoding],
            )
        ]
        return self

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2DateTimeFrame:
        """
        Instantiate an ID3v2 datetime frame object from an ID3v2.4 frame
        bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the datetime frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        datetime_frame : minim.media.metadata.ID3v2DateTimeFrame
            Datetime frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_4(
            stream, strict=strict
        )
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_4(
            stream,
            frame_length=10 + decode_synchsafe_int(*stream[4:8]),
            strict=strict,
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        obj._datetimes = cls._parse_datetimes(
            cls._split_bytestream(
                stream[offset + 1 : offset + frame_length],
                encoding=obj._text_encoding,
            ),
            strict=strict,
        )
        return obj

    @staticmethod
    def _parse_datetimes(
        datetimes: str
        | datetime
        | tuple[int | str, ...]
        | Iterable[str | datetime | tuple[int | str, ...]],
        /,
        *,
        strict: bool = True,
    ) -> DateTime | list[DateTime]:
        """
        Parse datetimes.

        Parameters
        ----------
        datetimes : str, datetime.datetime, tuple[int | str, ...], or \
        Iterable[str | datetime | tuple[int | str, ...]]; \
        positional-only
            Datetimes, in ISO-8601 format.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        datetimes : minim.media.metadata.id3.DateTime or \
        list[minim.media.metadata.id3.DateTime]
            Parsed datetimes.
        """
        match datetimes:
            case str():
                return DateTime.from_string(datetimes, strict=strict)
            case datetime():
                return DateTime(
                    datetimes.year,
                    datetimes.month,
                    datetimes.day,
                    datetimes.hour,
                    datetimes.minute,
                    datetimes.second,
                    strict=False,
                )
            case tuple():
                return DateTime.from_tuple(datetimes, strict=strict)
            case _ if isinstance(datetimes, Iterable):
                return [
                    ID3v2DateTimeFrame._parse_datetimes(dt, strict=strict)
                    for dt in datetimes
                ]
            case _:
                raise TypeError(
                    "`datetimes` must be one or more strings, "
                    "datetime.datetime objects, or tuples of integers."
                )

    @property
    def _text_info(self) -> list[str]:
        """
        Text information.
        """
        return [dt.to_string() for dt in self._datetimes]

    def serialize(
        self,
        tag_version: str | tuple[int, int, int],
        *,
        text_encoding: str | None = None,
    ) -> bytes:
        """
        Serialize the datetime frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        text_encoding : str; keyword-only; optional
            Text encoding. If :code:`None`, the text encoding already
            associated with the frame is used.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        Returns
        -------
        stream : bytes
            Bytestream containing the datetime frame.
        """
        tag_version = normalize_id3v2_tag_version(tag_version)
        frame_id = self._frame_ids.get(4)
        if frame_id is None:
            raise RuntimeError(
                f"A(n) {type(self).__name__} cannot be "
                f"serialized to an ID3v2.{tag_version[1]} tag."
            )

        text_encoding = self._resolve_text_encoding(text_encoding, tag_version)
        match tag_version:
            case (2, 4, _):
                return self._encode_2_4(
                    frame_id,
                    self._TEXT_ENCODINGS[text_encoding].to_bytes(
                        byteorder="big"
                    )
                    + (
                        b"\x00\x00"
                        if text_encoding.startswith("utf-16")
                        else b"\x00"
                    ).join(
                        dt.to_string().encode(encoding=text_encoding)
                        for dt in self._datetimes
                    ),
                )
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )


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

    _MIME_TYPES: ClassVar[dict[str, str]] = {
        "image/jpeg": "JPG",
        "image/png": "PNG",
        "image/gif": "GIF",
        "image/bmp": "BMP",
        "image/tiff": "TIF",
    }
    _MIME_TYPES |= {v: k for k, v in _MIME_TYPES.items()}

    _allow_multiple: ClassVar[bool] = True
    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"PIC",
        3: b"APIC",
        4: b"APIC",
    }

    __slots__ = (
        "_description",
        "_mime_type",
        "_picture_data",
        "_picture_type",
        "_text_encoding",
    )

    def __init__(
        self,
        *,
        picture_type: int,
        mime_type: str,
        picture_data: bytes,
        description: str = "",
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
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

        flags : minim.media.metadata.ID3v2FrameFlags; keyword-only; \
        optional
            Flags for the ID3v2 frame.
        """
        super().__init__(flags=flags)

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
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2Frame:
        """
        Instantiate an :class:`ID3v2APICFrame` object from an ID3v2.2
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`PIC` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        picture_frame : minim.media.metadata.ID3v2APICFrame
            :code:`PIC` frame.
        """
        obj = super()._from_stream_2_2(stream, strict=strict)
        obj._text_encoding = text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        image_type = stream[7:10].tobytes().decode(encoding="ascii").upper()
        mime_type = cls._MIME_TYPES.get(image_type)
        if mime_type is None:
            if strict:
                raise ValueError(f"Invalid image type {image_type!r}.")
            mime_type = image_type
        obj._mime_type = mime_type
        obj._picture_type = stream[10]
        description, obj._picture_data = (
            stream[11:]
            .tobytes()
            .split(
                b"\x00\x00" if text_encoding.startswith("utf-16") else b"\x00",
                maxsplit=1,
            )
        )
        obj._description = description.decode(encoding=text_encoding)
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2Frame:
        """
        Instantiate an :class:`ID3v2APICFrame` object from an ID3v2.3
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`APIC` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        picture_frame : minim.media.metadata.ID3v2APICFrame
            :code:`APIC` frame.
        """
        obj = super()._from_stream_2_3(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_3(
            stream,
            frame_length=10 + int.from_bytes(stream[4:8], byteorder="big"),
        )
        obj._text_encoding = text_encoding = cls._TEXT_ENCODINGS[
            stream[offset]
        ]
        null_char = (
            b"\x00\x00" if text_encoding.startswith("utf-16") else b"\x00"
        )
        mime_type, stream = (
            stream[offset + 1 : offset + frame_length]
            .tobytes()
            .split(null_char, maxsplit=1)
        )
        mime_type = mime_type.decode(encoding="ascii")
        if not mime_type.startswith("image/") and not mime_type.isupper():
            mime_type = f"image/{mime_type}"
        obj._mime_type = mime_type
        obj._picture_type = stream[0]
        description, obj._picture_data = stream[1:].split(
            null_char, maxsplit=1
        )
        obj._description = description.decode(encoding=text_encoding)
        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2Frame:
        """
        Instantiate an :class:`ID3v2APICFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`APIC` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        picture_frame : minim.media.metadata.ID3v2APICFrame
            :code:`APIC` frame.
        """
        obj = super()._from_stream_2_4(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_4(
            stream,
            frame_length=10 + decode_synchsafe_int(*stream[4:8]),
            strict=strict,
        )
        obj._text_encoding = text_encoding = cls._TEXT_ENCODINGS[
            stream[offset]
        ]
        null_char = (
            b"\x00\x00" if text_encoding.startswith("utf-16") else b"\x00"
        )
        mime_type, stream = (
            stream[offset + 1 : offset + frame_length]
            .tobytes()
            .split(null_char, maxsplit=1)
        )
        mime_type = mime_type.decode(encoding="ascii")
        if not mime_type.startswith("image/") and not mime_type.isupper():
            mime_type = f"image/{mime_type}"
        obj._mime_type = mime_type
        obj._picture_type = stream[0]
        description, obj._picture_data = stream[1:].split(
            null_char, maxsplit=1
        )
        obj._description = description.decode(encoding=text_encoding)
        return obj

    @property
    def _key(self) -> str:
        """
        Unique key.
        """
        if self._picture_type in {1, 2}:
            return str(self._picture_type)
        return self._description

    def serialize(
        self,
        tag_version: str | tuple[int, int, int],
        *,
        text_encoding: str | None = None,
    ) -> bytes:
        """
        Serialize the :code:`PIC`/:code:`APIC` frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        text_encoding : str; keyword-only; optional
            Text encoding for the picture description. If :code:`None`,
            the text encoding already associated with the frame is used.

        Returns
        -------
        stream : bytes
            Bytestream containing the :code:`PIC`/:code:`APIC` frame.
        """
        tag_version = normalize_id3v2_tag_version(tag_version)
        text_encoding = self._resolve_text_encoding(text_encoding, tag_version)
        null_char = (
            b"\x00\x00" if text_encoding.startswith("utf-16") else b"\x00"
        )
        mime_type = self._mime_type
        match tag_version:
            case (2, 4, _):
                if (
                    not mime_type.startswith("image/")
                    and not mime_type.isupper()
                ):
                    mime_type = f"image/{mime_type}"
                return self._encode_2_4(
                    self._frame_ids[4],
                    b"".join(
                        (
                            self._TEXT_ENCODINGS[text_encoding].to_bytes(
                                byteorder="big"
                            ),
                            mime_type.encode(encoding="ascii"),
                            b"\x00",
                            self._picture_type.to_bytes(byteorder="big"),
                            self._description.encode(encoding=text_encoding),
                            null_char,
                            self._picture_data,
                        )
                    ),
                )
            case (2, 3, _):
                if (
                    not mime_type.startswith("image/")
                    and not mime_type.isupper()
                ):
                    mime_type = f"image/{mime_type}"
                return self._encode_2_3(
                    self._frame_ids[3],
                    b"".join(
                        (
                            self._TEXT_ENCODINGS[text_encoding].to_bytes(
                                byteorder="big"
                            ),
                            mime_type.encode(encoding="ascii"),
                            b"\x00",
                            self._picture_type.to_bytes(byteorder="big"),
                            self._description.encode(encoding=text_encoding),
                            null_char,
                            self._picture_data,
                        )
                    ),
                )
            case (2, 2, _):
                if len(mime_type) == 3:
                    mime_type = mime_type.upper()
                else:
                    mime_type_ = self._MIME_TYPES.get(mime_type)
                    if mime_type_ is None:
                        raise ValueError(
                            "Unknown three-character image format for "
                            f"MIME type {mime_type!r}."
                        )
                    mime_type = mime_type_
                return self._encode_2_2(
                    self._frame_ids[2],
                    b"".join(
                        (
                            self._TEXT_ENCODINGS[text_encoding].to_bytes(
                                byteorder="big"
                            ),
                            mime_type.encode(encoding="ascii"),
                            self._picture_type.to_bytes(byteorder="big"),
                            self._description.encode(encoding=text_encoding),
                            null_char,
                            self._picture_data,
                        )
                    ),
                )
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )


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

    _allow_multiple: ClassVar[bool] = True
    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"COM",
        3: b"COMM",
        4: b"COMM",
    }

    __slots__ = ("_comment", "_description", "_language", "_text_encoding")

    def __init__(
        self,
        description: str,
        comment: str,
        *,
        language: str = "eng",
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
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

        flags : minim.media.metadata.ID3v2FrameFlags; keyword-only; \
        optional
            Flags for the ID3v2 frame.
        """
        super().__init__(flags=flags)

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
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2COMMFrame:
        """
        Instantiate an :class:`ID3v2COMMFrame` object from an ID3v2.2
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`COM` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        comment_frame : minim.media.metadata.ID3v2COMMFrame
            :code:`COM` frame.
        """
        obj = super()._from_stream_2_2(stream, strict=strict)
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        obj._language = stream[7:10].tobytes().decode(encoding="ascii")
        obj._description, obj._comment = cls._split_bytestream(
            stream[10 : 6 + int.from_bytes(stream[3:6], byteorder="big")],
            encoding=obj._text_encoding,
            max_splits=1,
        )
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2COMMFrame:
        """
        Instantiate an :class:`ID3v2COMMFrame` object from an ID3v2.3
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`COMM` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        comment_frame : minim.media.metadata.ID3v2COMMFrame
            :code:`COMM` frame.
        """
        obj = super()._from_stream_2_3(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_3(
            stream,
            frame_length=10 + int.from_bytes(stream[4:8], byteorder="big"),
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        mid_offset = offset + 4
        obj._language = (
            stream[offset + 1 : mid_offset].tobytes().decode(encoding="ascii")
        )
        obj._description, obj._comment = cls._split_bytestream(
            stream[mid_offset : offset + frame_length],
            encoding=obj._text_encoding,
            max_splits=1,
        )
        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2COMMFrame:
        """
        Instantiate an :class:`ID3v2COMMFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`COMM` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        comment_frame : minim.media.metadata.ID3v2COMMFrame
            :code:`COMM` frame.
        """
        obj = super()._from_stream_2_4(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_4(
            stream,
            frame_length=10 + decode_synchsafe_int(*stream[4:8]),
            strict=strict,
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        mid_offset = offset + 4
        obj._language = (
            stream[offset + 1 : mid_offset].tobytes().decode(encoding="ascii")
        )
        obj._description, obj._comment = cls._split_bytestream(
            stream[mid_offset : offset + frame_length],
            encoding=obj._text_encoding,
            max_splits=1,
        )
        return obj

    @property
    def _key(self) -> str:
        """
        Unique key.
        """
        return f"{self._language}{self._description}"

    def serialize(
        self,
        tag_version: str | tuple[int, int, int],
        *,
        text_encoding: str | None = None,
    ) -> bytes:
        """
        Serialize the :code:`COM`/:code:`COMM` frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        text_encoding : str; keyword-only; optional
            Text encoding. If :code:`None`, the text encoding already
            associated with the frame is used.

        Returns
        -------
        stream : bytes
            Bytestream containing the :code:`COM`/:code:`COMM` frame.
        """
        tag_version = normalize_id3v2_tag_version(tag_version)
        text_encoding = self._resolve_text_encoding(text_encoding, tag_version)
        frame_data = b"".join(
            (
                self._TEXT_ENCODINGS[text_encoding].to_bytes(byteorder="big"),
                self._language.encode(encoding="ascii"),
                self._description.encode(encoding=text_encoding),
                b"\x00\x00" if text_encoding.startswith("utf-16") else b"\x00",
                self._comment.encode(encoding=text_encoding),
            )
        )
        match tag_version:
            case (2, 4, _):
                return self._encode_2_4(b"COMM", frame_data)
            case (2, 3, _):
                return self._encode_2_3(b"COMM", frame_data)
            case (2, 2, _):
                return self._encode_2_2(b"COM", frame_data)
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )


class ID3v2USLTFrame(ID3v2Frame):
    """
    "Unsynchronized lyric/text transcription" frame.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.9. Unsychronised lyrics/text
       transcription <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.9. Unsychronised lyric/text
       transcription <https://id3.org/id3v2.3.0
       #Unsychronised_lyrics.2Ftext_transcription>`_.

       `ID3v2.4.0 Native Frames: 4.8. Unsynchronised lyric/text
       transcription <https://id3.org/id3v2.4.0-frames>`_.
    """

    _allow_multiple: ClassVar[bool] = True
    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"ULT",
        3: b"USLT",
        4: b"USLT",
    }

    __slots__ = ("_description", "_language", "_lyrics", "_text_encoding")

    def __init__(
        self,
        lyrics: str,
        /,
        *,
        description: str = "",
        language: str = "eng",
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        lyrics : str; positional-only
            Lyrics.

        description : str; keyword-only; default: :code:`""`
            Short content description.

        language : str; keyword-only; default: :code:`"eng"`
            ISO 639-2 code for the language.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding for the lyrics and description.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        flags : minim.media.metadata.ID3v2FrameFlags; keyword-only; \
        optional
            Flags for the ID3v2 frame.
        """
        super().__init__(flags=flags)

        validate_type("description", description, str)
        self._description = description

        validate_type("lyrics", lyrics, str)
        self._lyrics = lyrics

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
                lyrics.encode(encoding=text_encoding)
                description.encode(encoding=text_encoding)
                is_utf = False
            except UnicodeEncodeError:
                is_utf = True
            if is_utf:
                raise ValueError(
                    "`description` or `lyrics` cannot be encoded "
                    "using ISO-8859-1."
                )

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2USLTFrame:
        """
        Instantiate an :class:`ID3v2USLTFrame` object from an ID3v2.2
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`ULT` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        lyrics_frame : minim.media.metadata.ID3v2USLTFrame
            :code:`ULT` frame.
        """
        obj = super()._from_stream_2_3(stream, strict=strict)
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        obj._language = stream[7:10].tobytes().decode(encoding="ascii")
        obj._description, obj._lyrics = cls._split_bytestream(
            stream[10 : 6 + int.from_bytes(stream[3:6], byteorder="big")],
            encoding=obj._text_encoding,
        )
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2USLTFrame:
        """
        Instantiate an :class:`ID3v2USLTFrame` object from an ID3v2.3
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`USLT` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        lyrics_frame : minim.media.metadata.ID3v2USLTFrame
            :code:`USLT` frame.
        """
        obj = super()._from_stream_2_3(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_3(
            stream,
            frame_length=10 + int.from_bytes(stream[4:8], byteorder="big"),
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        mid_offset = offset + 4
        obj._language = (
            stream[offset + 1 : mid_offset].tobytes().decode(encoding="ascii")
        )
        obj._description, obj._lyrics = cls._split_bytestream(
            stream[mid_offset : offset + frame_length],
            encoding=obj._text_encoding,
        )
        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2USLTFrame:
        """
        Instantiate an :class:`ID3v2USLTFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`USLT` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        lyrics_frame : minim.media.metadata.ID3v2USLTFrame
            :code:`USLT` frame.
        """
        obj = super()._from_stream_2_4(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_4(
            stream,
            frame_length=10 + decode_synchsafe_int(*stream[4:8]),
            strict=strict,
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        mid_offset = offset + 4
        obj._language = (
            stream[offset + 1 : mid_offset].tobytes().decode(encoding="ascii")
        )
        obj._description, obj._lyrics = cls._split_bytestream(
            stream[mid_offset : offset + frame_length],
            encoding=obj._text_encoding,
        )
        return obj

    @property
    def _key(self) -> str:
        """
        Unique key.
        """
        return f"{self._language}{self._description}"

    def serialize(
        self,
        tag_version: str | tuple[int, int, int],
        *,
        text_encoding: str | None = None,
    ) -> bytes:
        """
        Serialize the :code:`ULT`/:code:`USLT` frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        text_encoding : str; keyword-only; optional
            Text encoding. If :code:`None`, the text encoding already
            associated with the frame is used.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        Returns
        -------
        stream : bytes
            Bytestream containing the :code:`ULT`/:code:`USLT` frame.
        """
        tag_version = normalize_id3v2_tag_version(tag_version)
        text_encoding = self._resolve_text_encoding(text_encoding, tag_version)
        frame_data = b"".join(
            (
                self._TEXT_ENCODINGS[text_encoding].to_bytes(byteorder="big"),
                self._language.encode(encoding="ascii"),
                self._description.encode(encoding=text_encoding),
                (
                    b"\x00\x00"
                    if text_encoding.startswith("utf-16")
                    else b"\x00"
                ),
                self._lyrics.encode(encoding=text_encoding),
            )
        )
        match tag_version:
            case (2, 4, _):
                return self._encode_2_4(b"USLT", frame_data)
            case (2, 3, _):
                return self._encode_2_3(b"USLT", frame_data)
            case (2, 2, _):
                return self._encode_2_2(b"ULT", frame_data)
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )


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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TAL",
        3: b"TALB",
        4: b"TALB",
    }

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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TBP",
        3: b"TBPM",
        4: b"TBPM",
    }

    __slots__ = ()

    def __init__(
        self,
        bpm: float | str | OrderedCollection[int | float | str],
        /,
        *,
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        bpm : int, float, str, or \
        OrderedCollection[int | float | str]; positional-only
            Tempo, in beats per minute (BPM).

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        flags : minim.media.metadata.ID3v2FrameFlags; keyword-only; \
        optional
            Flags for the ID3v2 frame.
        """
        super(ID3v2TextInfoFrame, self).__init__(flags=flags)

        if isinstance(bpm, (int, float, str)):
            self._text_info = [str(round(float(bpm)))]
        elif isinstance(bpm, ORDERED_COLLECTION_TYPES):
            self._text_info = _text_info = []
            for idx, bpm_ in enumerate(bpm):
                validate_numeric(f"bpm[{idx}]", bpm, float, 0)
                _text_info.append(str(round(float(bpm_))))
        else:
            raise TypeError(
                "`bpm` must be a number, a string, or an ordered "
                "collection of numbers and/or strings."
            )

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        self._text_encoding = text_encoding

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict=True
    ) -> ID3v2TBPMFrame:
        """
        Instantiate an :class:`ID3v2TBPMFrame` object from an ID3v2.2
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TBP` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        bpm_frame : minim.media.metadata.ID3v2TBPMFrame
            :code:`TBP` frame.
        """
        obj = super()._from_stream_2_2(stream, strict=strict)
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        bpms = cls._split_bytestream(
            stream[7 : 6 + int.from_bytes(stream[3:6], byteorder="big")],
            encoding=obj._text_encoding,
        )
        if strict:
            for idx, bpm in enumerate(bpms):
                validate_numeric(f"bpms[{idx}]", bpm, int, 0)
        obj._text_info = bpms
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict=True
    ) -> ID3v2TBPMFrame:
        """
        Instantiate an :class:`ID3v2TBPMFrame` object from an ID3v2.3
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TBPM` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        bpm_frame : minim.media.metadata.ID3v2TBPMFrame
            :code:`TBPM` frame.
        """
        obj = super()._from_stream_2_3(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_3(
            stream,
            frame_length=10 + int.from_bytes(stream[4:8], byteorder="big"),
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        bpms = cls._split_bytestream(
            stream[offset + 1 : offset + frame_length],
            encoding=obj._text_encoding,
        )
        if strict:
            for idx, bpm in enumerate(bpms):
                validate_numeric(f"bpms[{idx}]", bpm, int, 0)
        obj._text_info = bpms
        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict=True
    ) -> ID3v2TBPMFrame:
        """
        Instantiate an :class:`ID3v2TBPMFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TBPM` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        bpm_frame : minim.media.metadata.ID3v2TBPMFrame
            :code:`TBPM` frame.
        """
        obj = super()._from_stream_2_4(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_4(
            stream,
            frame_length=10 + decode_synchsafe_int(*stream[4:8]),
            strict=strict,
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        bpms = cls._split_bytestream(
            stream[offset + 1 : offset + frame_length],
            encoding=obj._text_encoding,
        )
        if strict:
            for idx, bpm in enumerate(bpms):
                validate_numeric(f"bpms[{idx}]", bpm, int, 0)
        obj._text_info = bpms
        return obj


class ID3v2TCMPFrame(ID3v2TextInfoFrame):
    """
    "iTunes compilation flag" frame.

    .. seealso::

       `TCMP - iTunes Compilation Flag (class 4)
       <https://id3.org/iTunes%20Compilation%20Flag>`_.
    """

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TCP",
        3: b"TCMP",
        4: b"TCMP",
    }

    __slots__ = ()

    def __init__(
        self,
        compilation_flag: bool
        | int
        | str
        | OrderedCollection[bool | int | str],
        /,
        *,
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        compilation_flag : bool, int, str, or \
        OrderedCollection[bool | int | str]; positional-only
            Whether the recording is part of a compilation.

            **Examples**: :code:`True`, :code:`1`, :code:`"1"`.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        flags : minim.media.metadata.ID3v2FrameFlags; keyword-only; \
        optional
            Flags for the ID3v2 frame.
        """
        super(ID3v2TextInfoFrame, self).__init__(flags=flags)

        if isinstance(compilation_flag, bool | int | str):
            self._text_info = [str(int(compilation_flag))]
        elif isinstance(compilation_flag, ORDERED_COLLECTION_TYPES):
            self._text_info = _text_info = []
            for idx, flag in enumerate(compilation_flag):
                validate_numeric(f"compilation_flags[{idx}]", flag, int, 0, 1)
                _text_info.append(str(int(compilation_flag)))
        else:
            raise TypeError(
                "`compilation_flags` must be a boolean, a number, a "
                "string, or an ordered collection of booleans, "
                "numbers, and/or strings."
            )

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        self._text_encoding = text_encoding

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict=True
    ) -> ID3v2TCMPFrame:
        """
        Instantiate an :class:`ID3v2TCMPFrame` object from an ID3v2.2
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TCP` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        compilation_flag_frame : minim.media.metadata.ID3v2TCMPFrame
            :code:`TCP` frame.
        """
        obj = super()._from_stream_2_2(stream, strict=strict)
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        compilation_flags = cls._split_bytestream(
            stream[7 : 6 + int.from_bytes(stream[3:6], byteorder="big")],
            encoding=obj._text_encoding,
        )
        if strict:
            for idx, flag in enumerate(compilation_flags):
                validate_numeric(f"compilation_flags[{idx}]", flag, int, 0, 1)
        obj._text_info = compilation_flags
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict=True
    ) -> ID3v2TCMPFrame:
        """
        Instantiate an :class:`ID3v2TCMPFrame` object from an ID3v2.3
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TCMP` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        compilation_flag_frame : minim.media.metadata.ID3v2TCMPFrame
            :code:`TCMP` frame.
        """
        obj = super()._from_stream_2_3(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_3(
            stream,
            frame_length=10 + int.from_bytes(stream[4:8], byteorder="big"),
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        compilation_flags = cls._split_bytestream(
            stream[offset + 1 : offset + frame_length],
            encoding=obj._text_encoding,
        )
        if strict:
            for idx, flag in enumerate(compilation_flags):
                validate_numeric(f"compilation_flags[{idx}]", flag, int, 0, 1)

        obj._text_info = compilation_flags
        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict=True
    ) -> ID3v2TCMPFrame:
        """
        Instantiate an :class:`ID3v2TCMPFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TCMP` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        compilation_flag_frame : minim.media.metadata.ID3v2TCMPFrame
            :code:`TCMP` frame.
        """
        obj = super()._from_stream_2_4(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_4(
            stream,
            frame_length=10 + decode_synchsafe_int(*stream[4:8]),
            strict=strict,
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        compilation_flags = cls._split_bytestream(
            stream[offset + 1 : offset + frame_length],
            encoding=obj._text_encoding,
        )
        if strict:
            for idx, flag in enumerate(compilation_flags):
                validate_numeric(f"compilation_flags[{idx}]", flag, int, 0, 1)
        obj._text_info = compilation_flags
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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TCM",
        3: b"TCOM",
        4: b"TCOM",
    }

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

    _GENRE_RE: ClassVar[re.Pattern[str]] = re.compile(r"(?<!\()\((\d+)\)")

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TCO",
        3: b"TCON",
        4: b"TCON",
    }

    __slots__ = ("_refinements",)

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TCONFrame:
        """
        Instantiate an :class:`ID3v2TCONFrame` object from an ID3v2.2
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TCO` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        content_type_frame : minim.media.metadata.ID3v2TCONFrame
            :code:`TCO` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_2(
            stream, strict=strict
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        obj._text_info, obj._refinements = cls._deserialize_content_types(
            cls._split_bytestream(
                stream[7 : 6 + int.from_bytes(stream[3:6], byteorder="big")],
                encoding=obj._text_encoding,
            )
        )
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TCONFrame:
        """
        Instantiate an :class:`ID3v2TCONFrame` object from an ID3v2.3
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TCON` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        content_type_frame : minim.media.metadata.ID3v2TCONFrame
            :code:`TCON` frame.
        """
        obj = super()._from_stream_2_3(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_3(
            stream,
            frame_length=10 + int.from_bytes(stream[4:8], byteorder="big"),
            strict=strict,
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        obj._text_info, obj._refinements = cls._deserialize_content_types(
            cls._split_bytestream(
                stream[offset + 1 : offset + frame_length],
                encoding=obj._text_encoding,
            )
        )
        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TextInfoFrame:
        """
        Instantiate an :class:`ID3v2TCONFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TCON` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        content_type_frame : minim.media.metadata.ID3v2TCONFrame
            :code:`TCON` frame.
        """
        obj = super()._from_stream_2_4(stream, strict=strict)
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_4(
            stream,
            frame_length=10 + decode_synchsafe_int(*stream[4:8]),
            strict=strict,
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        obj._text_info = [
            GENRES.get(int(content_type), content_type)
            if content_type.isdecimal()
            else content_type
            for content_type in cls._split_bytestream(
                stream[offset + 1 : offset + frame_length],
                encoding=obj._text_encoding,
            )
        ]
        obj._refinements = len(obj._text_info) * [""]
        return obj

    @classmethod
    def _deserialize_content_types(
        cls, content_types: list[str], /
    ) -> tuple[list[str], list[str]]:
        """
        Deserialize content types by substituting in ID3v1 genres when
        applicable.

        Parameters
        ----------
        content_types : list[str]; positional-only
            Content types or genres.

        Returns
        -------
        content_types : list[str]
            Deserialized content types or genres.

        refinements : list[str]
            Refinements corresponding to the content types or genres.
        """
        text_info = []
        refinements = []
        pending_refinement = False

        for content_type in content_types:
            index = 0
            for genre in cls._GENRE_RE.finditer(content_type):
                if extra := content_type[index : genre.start()]:
                    extra = extra.removeprefix("(")
                    if pending_refinement:
                        refinements.append(extra)
                        pending_refinement = False
                    else:
                        text_info.append(extra)
                        refinements.append("")
                elif pending_refinement:
                    refinements.append("")
                    pending_refinement = False

                code = int(genre.group(1))
                text_info.append(GENRES.get(code, genre.group(0)))
                pending_refinement = True
                index = genre.end()

            if extra := content_type[index:]:
                extra = extra.removeprefix("(")
                if pending_refinement:
                    refinements.append(extra)
                    pending_refinement = False
                else:
                    text_info.append(extra)
                    refinements.append("")
            elif pending_refinement:
                refinements.append("")
                pending_refinement = False

        return text_info, refinements

    @classmethod
    def _serialize_content_types(
        cls, content_types: list[str], refinements: list[str], /
    ) -> list[str]:
        """
        Serialize content types by substituting in ID3v1 genre IDs when
        applicable.

        Parameters
        ----------
        content_types : list[str]; positional-only
            Content types or genres.

        refinements : list[str]; positional-only
            Refinements to the content types or genres.

        Returns
        -------
        content_types : list[str]
            Serialized content types or genres.
        """
        return [
            (
                (
                    f"({content_type}"
                    if content_type.startswith("(")
                    else content_type
                )
                if (code := GENRES.get(content_type.lower())) is None
                else f"({code})"
            )
            + refinement
            for content_type, refinement in zip(content_types, refinements)
        ]

    def serialize(
        self,
        tag_version: str | tuple[int, int, int],
        *,
        text_encoding: str | None = None,
    ) -> bytes:
        """
        Serialize the :code:`TCO`/:code:`TCON` frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        text_encoding : str; keyword-only; optional
            Text encoding. If :code:`None`, the text encoding already
            associated with the frame is used.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        Returns
        -------
        stream : bytes
            Bytestream containing the :code:`TCO`/:code:`TCON` frame.
        """
        tag_version = normalize_id3v2_tag_version(tag_version)
        text_encoding = self._resolve_text_encoding(text_encoding, tag_version)
        null_char = (
            b"\x00\x00" if text_encoding.startswith("utf-16") else b"\x00"
        )
        match tag_version:
            case (2, 4, _):
                return self._encode_2_4(
                    b"TCON",
                    self._TEXT_ENCODINGS[text_encoding].to_bytes(
                        byteorder="big"
                    )
                    + null_char.join(
                        ti.encode(encoding=text_encoding)
                        for ti in self._text_info
                    ),
                )
            case (2, 3, _):
                return self._encode_2_3(
                    b"TCON",
                    self._TEXT_ENCODINGS[text_encoding].to_bytes(
                        byteorder="big"
                    )
                    + null_char.join(
                        ti.encode(encoding=text_encoding)
                        for ti in self._serialize_content_types(
                            self._text_info, self._refinements
                        )
                    ),
                )
            case (2, 2, _):
                return self._encode_2_2(
                    b"TCO",
                    self._TEXT_ENCODINGS[text_encoding].to_bytes(
                        byteorder="big"
                    )
                    + null_char.join(
                        ti.encode(encoding=text_encoding)
                        for ti in self._serialize_content_types(
                            self._text_info, self._refinements
                        )
                    ),
                )
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )


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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TCR",
        3: b"TCOP",
        4: b"TCOP",
    }

    __slots__ = ()


class ID3v2TDRCFrame(ID3v2DateTimeFrame):
    """
    "Recording date" frame.

    .. note::

       For ID3v2.2/2.3 tags, information in this frame is stored in the
       :code:`TYE`/:code:`TYER`, :code:`TDA`/:code:`TDAT`, and
       :code:`TIM`/:code:`TIME` frames.

    .. seealso::

       `ID3v2.2.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2-00>`_.

       `ID3v2.3.0 Informal Standard: 4.2.1. Text information frames -
       details <https://id3.org/id3v2.3.0#TDAT>`_.

       `ID3v2.4.0 Native Frames: 4.2.5. Other text frames
       <https://id3.org/id3v2.4.0-frames>`_.
    """

    _frame_ids: ClassVar[dict[int, bytes | list[bytes]]] = {
        2: [b"TYE", b"TDA", b"TIM"],
        3: [b"TYER", b"TDAT", b"TIME"],
        4: b"TDRC",
    }

    __slots__ = ()

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2DateTimeFrame:
        """
        Instantiate an ID3v2 datetime frame object from an ID3v2.2 frame
        bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the datetime frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        datetime_frame : minim.media.metadata.ID3v2DateTimeFrame
            Datetime frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_2(
            stream, strict=strict
        )
        frame_length = int.from_bytes(stream[3:6], byteorder="big")
        obj._text_encoding = text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        match stream[:3]:
            case b"TYE":
                obj._datetimes = cls._parse_datetimes(
                    cls._split_bytestream(
                        stream[7 : 6 + frame_length], encoding=text_encoding
                    ),
                    strict=strict,
                )
            case b"TDA":
                obj._datetimes = datetimes = []
                for date in cls._split_bytestream(
                    stream[7 : 6 + frame_length], encoding=text_encoding
                ):
                    try:
                        if len(date) == 4:
                            datetimes.append(
                                DateTime(
                                    day=int(date[:2]),
                                    month=int(date[2:]),
                                    strict=strict,
                                )
                            )
                    except ValueError:
                        datetimes.append(
                            cls._parse_datetimes(date, strict=strict)
                        )
            case b"TIM":
                obj._datetimes = datetimes = []
                for time in cls._split_bytestream(
                    stream[7 : 6 + frame_length], encoding=text_encoding
                ):
                    try:
                        if len(time) == 4:
                            datetimes.append(
                                DateTime(
                                    hour=int(time[:2]),
                                    minute=int(time[2:]),
                                    strict=strict,
                                )
                            )
                    except ValueError:
                        datetimes.append(
                            cls._parse_datetimes(time, strict=strict)
                        )
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2DateTimeFrame:
        """
        Instantiate an ID3v2 datetime frame object from an ID3v2.3 frame
        bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the datetime frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        datetime_frame : minim.media.metadata.ID3v2DateTimeFrame
            Datetime frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_3(
            stream, strict=strict
        )
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_3(
            stream,
            frame_length=10 + int.from_bytes(stream[4:8], byteorder="big"),
        )
        obj._text_encoding = text_encoding = cls._TEXT_ENCODINGS[
            stream[offset]
        ]
        match stream[:4]:
            case b"TYER":
                obj._datetimes = cls._parse_datetimes(
                    cls._split_bytestream(
                        stream[offset + 1 : offset + frame_length],
                        encoding=text_encoding,
                    ),
                    strict=strict,
                )
            case b"TDAT":
                obj._datetimes = datetimes = []
                for date in cls._split_bytestream(
                    stream[offset + 1 : offset + frame_length],
                    encoding=text_encoding,
                ):
                    try:
                        if len(date) == 4:
                            datetimes.append(
                                DateTime(
                                    day=int(date[:2]),
                                    month=int(date[2:]),
                                    strict=strict,
                                )
                            )
                    except ValueError:
                        datetimes.append(
                            cls._parse_datetimes(date, strict=strict)
                        )
            case b"TIME":
                obj._datetimes = datetimes = []
                for time in cls._split_bytestream(
                    stream[offset + 1 : offset + frame_length],
                    encoding=text_encoding,
                ):
                    try:
                        if len(time) == 4:
                            datetimes.append(
                                DateTime(
                                    hour=int(time[:2]),
                                    minute=int(time[2:]),
                                    strict=strict,
                                )
                            )
                    except ValueError:
                        datetimes.append(
                            cls._parse_datetimes(time, strict=strict)
                        )
        return obj

    def serialize(
        self,
        tag_version: str | tuple[int, int, int],
        *,
        text_encoding: str | None = None,
    ) -> bytes:
        """
        Serialize the "recording date" frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        text_encoding : str; keyword-only; optional
            Text encoding. If :code:`None`, the text encoding already
            associated with the frame is used.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        Returns
        -------
        stream : bytes
            Bytestream containing the :code:`TDRC` or
            :code:`TYE`/:code:`TYER`, :code:`TDA`/:code:`TDAT`, and/or
            :code:`TIM`/`TIME` frames.
        """
        tag_version = normalize_id3v2_tag_version(tag_version)
        text_encoding = self._resolve_text_encoding(text_encoding, tag_version)
        null_char = (
            b"\x00\x00" if text_encoding.startswith("utf-16") else b"\x00"
        )
        match tag_version:
            case (2, 4, _):
                return super().serialize(
                    tag_version=tag_version, text_encoding=text_encoding
                )
            case (2, 3, _):
                years = []
                dates = []
                times = []
                for dt in self._datetimes:
                    years.append(
                        b""
                        if (year := dt._year) is None
                        else f"{year:04}".encode(encoding=text_encoding)
                    )
                    dates.append(
                        b""
                        if (month := dt._month) is None
                        or (day := dt._day) is None
                        else f"{month:02}{day:02}".encode(
                            encoding=text_encoding
                        )
                    )
                    times.append(
                        b""
                        if (hour := dt._hour) is None
                        or (minute := dt._minute) is None
                        else f"{hour:02}{minute:02}".encode(
                            encoding=text_encoding
                        )
                    )
                return b"".join(
                    self._encode_2_3(
                        frame_id,
                        self._TEXT_ENCODINGS[text_encoding].to_bytes(
                            byteorder="big"
                        )
                        + null_char.join(data),
                    )
                    if any(data)
                    else b""
                    for frame_id, data in (
                        (b"TYER", years),
                        (b"TDAT", dates),
                        (b"TIME", times),
                    )
                )
            case (2, 2, _):
                years = []
                dates = []
                times = []
                for dt in self._datetimes:
                    years.append(
                        b""
                        if (year := dt._year) is None
                        else f"{year:04}".encode(encoding=text_encoding)
                    )
                    dates.append(
                        b""
                        if (month := dt._month) is None
                        or (day := dt._day) is None
                        else f"{month:02}{day:02}".encode(
                            encoding=text_encoding
                        )
                    )
                    times.append(
                        b""
                        if (hour := dt._hour) is None
                        or (minute := dt._minute) is None
                        else f"{hour:02}{minute:02}".encode(
                            encoding=text_encoding
                        )
                    )
                return b"".join(
                    self._encode_2_2(
                        frame_id,
                        self._TEXT_ENCODINGS[text_encoding].to_bytes(
                            byteorder="big"
                        )
                        + null_char.join(data),
                    )
                    if any(data)
                    else b""
                    for frame_id, data in (
                        (b"TYE", years),
                        (b"TDA", dates),
                        (b"TIM", times),
                    )
                )
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )


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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TT1",
        3: b"TIT1",
        4: b"TIT1",
    }

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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TT2",
        3: b"TIT2",
        4: b"TIT2",
    }

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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TT3",
        3: b"TIT3",
        4: b"TIT3",
    }

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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TP1",
        3: b"TPE1",
        4: b"TPE1",
    }

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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TP2",
        3: b"TPE2",
        4: b"TPE2",
    }

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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TP3",
        3: b"TPE3",
        4: b"TPE3",
    }

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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TPA",
        3: b"TPOS",
        4: b"TPOS",
    }

    __slots__ = ("_disc",)

    def __init__(
        self,
        disc: int
        | str
        | tuple[int | str, int | str | None]
        | list[int | str | tuple[int | str, int | str | None]],
        /,
        *,
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        disc : int, str, tuple[int | str, int | str | None], or \
        list[int | str | tuple[int | str, int | str | None]]; \
        positional-only
            Disc number and optionally, the total number of discs.

            **Examples**: :code:`1`, :code:`"1"`, :code:`(1, None)`,
            :code:`(1, 1)`, :code:`"1/1"`.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        flags : minim.media.metadata.ID3v2FrameFlags; keyword-only; \
        optional
            Flags for the ID3v2 frame.
        """
        super(ID3v2TextInfoFrame, self).__init__(flags=flags)

        disc = self._parse_discs(disc)
        if not isinstance(disc, list):
            disc = [disc]
        self._disc = disc

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        self._text_encoding = text_encoding

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TPOSFrame:
        """
        Instantiate an :class:`ID3v2TPOSFrame` object from an ID3v2.2
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TPA` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        disc_frame : minim.media.metadata.ID3v2TPOSFrame
            :code:`TPA` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_2(
            stream, strict=strict
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        obj._disc = cls._parse_discs(
            cls._split_bytestream(
                stream[7 : 6 + int.from_bytes(stream[3:6], byteorder="big")],
                encoding=obj._text_encoding,
            ),
            strict=strict,
        )
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TPOSFrame:
        """
        Instantiate an :class:`ID3v2TPOSFrame` object from an ID3v2.3
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TPOS` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        disc_frame : minim.media.metadata.ID3v2TPOSFrame
            :code:`TPOS` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_3(
            stream, strict=strict
        )
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_3(
            stream,
            frame_length=10 + int.from_bytes(stream[4:8], byteorder="big"),
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        obj._disc = cls._parse_discs(
            cls._split_bytestream(
                stream[offset + 1 : offset + frame_length],
                encoding=obj._text_encoding,
            ),
            strict=strict,
        )
        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TPOSFrame:
        """
        Instantiate an :class:`ID3v2TPOSFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TPOS` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        disc_frame : minim.media.metadata.ID3v2TPOSFrame
            :code:`TPOS` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_4(
            stream, strict=strict
        )
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_4(
            stream,
            frame_length=10 + decode_synchsafe_int(*stream[4:8]),
            strict=strict,
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        obj._disc = cls._parse_discs(
            cls._split_bytestream(
                stream[offset + 1 : offset + frame_length],
                encoding=obj._text_encoding,
            ),
            strict=strict,
        )
        return obj

    @staticmethod
    def _parse_discs(
        discs: int
        | str
        | tuple[int | str, int | str | None]
        | list[int | str | tuple[int | str, int | str | None]],
        /,
        *,
        strict: bool = True,
    ) -> Position | list[Position]:
        """
        Parse disc numbers.

        Parameters
        ----------
        discs : int, str, tuple[int | str, int | str | None], or \
        list[int | str | tuple[int | str, int | str | None]]; \
        positional-only
            Disc numbers and, optionally, the total number of discs.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        discs : minim.media.metadata.id3.Position or \
        list[minim.media.metadata.id3.Position]
            Parsed disc numbers.
        """
        match discs:
            case int():
                return Position(discs)
            case str():
                return Position.from_string(discs, name="discs", strict=strict)
            case tuple() if len(discs) == 2:
                return Position.from_tuple(discs, name="discs", strict=strict)
            case list():
                return [
                    ID3v2TPOSFrame._parse_discs(disc, strict=strict)
                    for disc in discs
                ]
            case _:
                raise TypeError(
                    "`disc` must be an integer, a string, a tuple of "
                    "two integers and/or strings, or a list of "
                    "integers, strings, and/or tuples of two integers "
                    "and/or strings."
                )

    @property
    def _text_info(self) -> list[str]:
        """
        Text information.
        """
        return [disc.to_string() for disc in self._disc]


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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TPB",
        3: b"TPUB",
        4: b"TPUB",
    }

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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TRK",
        3: b"TRCK",
        4: b"TRCK",
    }

    __slots__ = ("_track",)

    def __init__(
        self,
        track: int
        | str
        | tuple[int | str, int | str | None]
        | list[int | str | tuple[int | str, int | str | None]],
        /,
        *,
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        track : int, str, tuple[int | str, int | str | None], or \
        list[int | str | tuple[int | str, int | str | None]]; \
        positional-only
            Track number and optionally, the total number of tracks.

            **Examples**: :code:`1`, :code:`"2"`, :code:`(3, None)`,
            :code:`(4, 5)`, :code:`"6/7"`.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        flags : minim.media.metadata.ID3v2FrameFlags; keyword-only; \
        optional
            Flags for the ID3v2 frame.
        """
        super(ID3v2TextInfoFrame, self).__init__(flags=flags)

        track = self._parse_tracks(track)
        if not isinstance(track, list):
            track = [track]
        self._track = track

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        self._text_encoding = text_encoding

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TRCKFrame:
        """
        Instantiate an :class:`ID3v2TRCKFrame` object from an ID3v2.2
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TRK` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        track_frame : minim.media.metadata.ID3v2TRCKFrame
            :code:`TRK` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_2(
            stream, strict=strict
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        obj._track = cls._parse_tracks(
            cls._split_bytestream(
                stream[7 : 6 + int.from_bytes(stream[3:6], byteorder="big")],
                encoding=obj._text_encoding,
            ),
            strict=strict,
        )
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TRCKFrame:
        """
        Instantiate an :class:`ID3v2TRCKFrame` object from an ID3v2.3
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TRCK` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        track_frame : minim.media.metadata.ID3v2TRCKFrame
            :code:`TRCK` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_3(
            stream, strict=strict
        )
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_3(
            stream,
            frame_length=10 + int.from_bytes(stream[4:8], byteorder="big"),
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        obj._track = cls._parse_tracks(
            cls._split_bytestream(
                stream[offset + 1 : offset + frame_length],
                encoding=obj._text_encoding,
            ),
            strict=strict,
        )
        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TRCKFrame:
        """
        Instantiate an :class:`ID3v2TRCKFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TRCK` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        track_frame : minim.media.metadata.ID3v2TRCKFrame
            :code:`TRCK` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_4(
            stream, strict=strict
        )
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_4(
            stream,
            frame_length=10 + decode_synchsafe_int(*stream[4:8]),
            strict=strict,
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        obj._track = cls._parse_tracks(
            cls._split_bytestream(
                stream[offset + 1 : offset + frame_length],
                encoding=obj._text_encoding,
            ),
            strict=strict,
        )
        return obj

    @staticmethod
    def _parse_tracks(
        tracks: int
        | str
        | tuple[int | str, int | str | None]
        | list[int | str | tuple[int | str, int | str | None]],
        /,
        *,
        strict: bool = True,
    ) -> tuple[int, int | None] | list[tuple[int, int | None]]:
        """
        Parse track numbers.

        Parameters
        ----------
        tracks : int, str, tuple[int | str, int | str | None], or \
        list[int | str | tuple[int | str, int | str | None]]; \
        positional-only
            Track numbers and, optionally, the total number of tracks.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        tracks : tuple[int, int or None] | list[tuple[int, int or None]]
            Parsed track numbers.
        """
        match tracks:
            case int():
                return Position(tracks)
            case str():
                return Position.from_string(
                    tracks, name="tracks", strict=strict
                )
            case tuple() if len(tracks) == 2:
                return Position.from_tuple(
                    tracks, name="tracks", strict=strict
                )
            case list():
                return [
                    ID3v2TRCKFrame._parse_tracks(track, strict=strict)
                    for track in tracks
                ]
            case _:
                raise TypeError(
                    "`tracks` must be an integer, a string, a tuple of "
                    "two integers and/or strings, or a list of "
                    "integers, strings, and/or tuples of two integers "
                    "and/or strings."
                )

    @property
    def _text_info(self) -> str:
        """
        Text information.
        """
        return [track.to_string() for track in self._track]


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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TRC",
        3: b"TSRC",
        4: b"TSRC",
    }

    __slots__ = ()

    def __init__(
        self,
        isrcs: str | OrderedCollection[str],
        /,
        *,
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
    ) -> None:
        """
        Parameters
        ----------
        isrcs : str or OrderedCollection[str]; positional-only
            ISRCs (International Standard Recording Codes).

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        flags : minim.media.metadata.ID3v2FrameFlags; keyword-only; \
        optional
            Flags for the ID3v2 frame.
        """
        super(ID3v2TextInfoFrame, self).__init__(flags=flags)

        if isinstance(isrcs, str):
            isrcs = [isrcs]
        self._text_info = [prepare_isrc(isrc) for isrc in isrcs]

        validate_type("text_encoding", text_encoding, str)
        text_encoding = text_encoding.lower()
        if text_encoding not in self._TEXT_ENCODINGS.values():
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. Valid "
                f"values: {join_values(self._TEXT_ENCODINGS.values())}."
            )
        self._text_encoding = text_encoding

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TSRCFrame:
        """
        Instantiate an :class:`ID3v2TSRCFrame` object from an ID3v2.2
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TRC` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        isrc_frame : minim.media.metadata.ID3v2TSRCFrame
            :code:`TRC` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_2(
            stream, strict=strict
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        obj._text_info = [
            prepare_isrc(isrc)
            for isrc in cls._split_bytestream(
                stream[7 : 6 + int.from_bytes(stream[3:6], byteorder="big")],
                encoding=obj._text_encoding,
            )
        ]
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TSRCFrame:
        """
        Instantiate an :class:`ID3v2TSRCFrame` object from an ID3v2.3
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TSRC` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        isrc_frame : minim.media.metadata.ID3v2TSRCFrame
            :code:`TSRC` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_3(
            stream, strict=strict
        )
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_3(
            stream,
            frame_length=10 + int.from_bytes(stream[4:8], byteorder="big"),
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        obj._text_info = [
            prepare_isrc(isrc)
            for isrc in cls._split_bytestream(
                stream[offset + 1 : offset + frame_length],
                encoding=obj._text_encoding,
            )
        ]
        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TSRCFrame:
        """
        Instantiate an :class:`ID3v2TSRCFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TSRC` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        isrc_frame : minim.media.metadata.ID3v2TSRCFrame
            :code:`TSRC` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_4(
            stream, strict=strict
        )
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_4(
            stream,
            frame_length=10 + decode_synchsafe_int(*stream[4:8]),
            strict=strict,
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        obj._text_info = [
            prepare_isrc(isrc)
            for isrc in cls._split_bytestream(
                stream[offset + 1 : offset + frame_length],
                encoding=obj._text_encoding,
            )
        ]
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

    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TSS",
        3: b"TSSE",
        4: b"TSSE",
    }

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

    _allow_multiple: ClassVar[bool] = True
    _frame_ids: ClassVar[dict[int, bytes]] = {
        2: b"TXX",
        3: b"TXXX",
        4: b"TXXX",
    }

    __slots__ = ("_description",)

    def __init__(
        self,
        description: str,
        value: str,
        /,
        *,
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
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

        flags : minim.media.metadata.ID3v2FrameFlags; keyword-only; \
        optional
            Flags for the ID3v2 frame.
        """
        super(ID3v2TextInfoFrame, self).__init__(flags=flags)

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
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TXXXFrame:
        """
        Instantiate an :class:`ID3v2TXXXFrame` object from an ID3v2.2
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TXX` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        text_info_frame : minim.media.metadata.ID3v2TXXXFrame
            :code:`TXX` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_2(
            stream, strict=strict
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        obj._description, *obj._text_info = cls._split_bytestream(
            stream[7 : 6 + int.from_bytes(stream[3:6], byteorder="big")],
            encoding=obj._text_encoding,
        )
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TXXXFrame:
        """
        Instantiate an :class:`ID3v2TXXXFrame` object from an ID3v2.3
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TXXX` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        text_info_frame : minim.media.metadata.ID3v2TXXXFrame
            :code:`TXXX` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_3(
            stream, strict=strict
        )
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_3(
            stream,
            frame_length=10 + int.from_bytes(stream[4:8], byteorder="big"),
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        obj._description, *obj._text_info = cls._split_bytestream(
            stream[offset + 1 : offset + frame_length],
            encoding=obj._text_encoding,
        )
        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> ID3v2TXXXFrame:
        """
        Instantiate an :class:`ID3v2TXXXFrame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the :code:`TXXX` frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        text_info_frame : minim.media.metadata.ID3v2TXXXFrame
            :code:`TXXX` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_4(
            stream, strict=strict
        )
        if isinstance(obj, UnknownID3v2Frame):
            return obj

        stream, offset, frame_length = obj._decode_2_4(
            stream,
            frame_length=10 + decode_synchsafe_int(*stream[4:8]),
            strict=strict,
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[offset]]
        obj._description, *obj._text_info = cls._split_bytestream(
            stream[offset + 1 : offset + frame_length],
            encoding=obj._text_encoding,
        )
        return obj

    @property
    def _key(self) -> str:
        """
        Unique key.
        """
        return self._description

    @property
    def description(self) -> str:
        """
        Description.
        """
        return self._description

    def serialize(
        self,
        tag_version: str | tuple[int, int, int],
        *,
        text_encoding: str | None = None,
    ) -> bytes:
        """
        Serialize the :code:`TXX`/:code:`TXXX` frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        text_encoding : str; keyword-only; optional
            Text encoding. If :code:`None`, the text encoding already
            associated with the frame is used.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        Returns
        -------
        stream : bytes
            Bytestream containing the :code:`TXX`/:code:`TXXX` frame.
        """
        tag_version = normalize_id3v2_tag_version(tag_version)
        text_encoding = self._resolve_text_encoding(text_encoding, tag_version)
        null_char = (
            b"\x00\x00" if text_encoding.startswith("utf-16") else b"\x00"
        )
        frame_data = b"".join(
            (
                self._TEXT_ENCODINGS[text_encoding].to_bytes(byteorder="big"),
                self._description.encode(encoding=text_encoding),
                null_char.join(
                    ti.encode(encoding=text_encoding) for ti in self._text_info
                ),
            )
        )
        match tag_version:
            case (2, 4, _):
                return self._encode_2_4(self._frame_ids[4], frame_data)
            case (2, 3, _):
                return self._encode_2_3(self._frame_ids[3], frame_data)
            case (2, 2, _):
                return self._encode_2_2(self._frame_ids[2], frame_data)
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )


class UnknownID3v2Frame(ID3v2Frame):
    """
    Unknown ID3v2 frame.
    """

    _allow_multiple: ClassVar[bool] = True
    _frame_ids: ClassVar[dict[int, bytes]] = {}

    __slots__ = ("_frame_data", "_frame_id", "_frame_length")

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

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> UnknownID3v2Frame:
        """
        Instantiate a :class:`UnknownID3v2Frame` object from an ID3v2.2
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the ID3v2 frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        frame : minim.media.flac.UnknownID3v2Frame
            ID3v2 frame.
        """
        obj = super()._from_stream_2_2(stream, strict=strict)
        obj._frame_id = stream[:3].tobytes()
        obj._frame_length = int.from_bytes(stream[3:6], byteorder="big")
        obj._flags = ID3v2FrameFlags()
        obj._frame_data = stream[6 : 6 + obj._frame_length].tobytes()
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> UnknownID3v2Frame:
        """
        Instantiate a :class:`UnknownID3v2Frame` object from an ID3v2.3
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the ID3v2 frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        frame : minim.media.flac.UnknownID3v2Frame
            ID3v2 frame.
        """
        obj = super()._from_stream_2_3(stream, strict=strict)
        if not hasattr(obj, "_frame_id"):
            obj._frame_id = stream[:4].tobytes()
            obj._frame_length = int.from_bytes(stream[4:8], byteorder="big")
            obj._frame_data = stream[10 : 10 + obj._frame_length].tobytes()
        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> UnknownID3v2Frame:
        """
        Instantiate a :class:`UnknownID3v2Frame` object from an ID3v2.4
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the ID3v2 frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        frame : minim.media.flac.UnknownID3v2Frame
            ID3v2 frame.
        """
        obj = super()._from_stream_2_4(stream, strict=strict)
        if not hasattr(obj, "_frame_id"):
            obj._frame_id = stream[:4].tobytes()
            obj._frame_length = decode_synchsafe_int(*stream[4:8])
            obj._frame_data = stream[10 : 10 + obj._frame_length].tobytes()
        return obj

    @property
    def _key(self) -> None:
        """
        Unique key.
        """
        return self._frame_id.decode(encoding="ascii")

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

    @property
    def frame_length(self) -> int:
        """
        Frame length, in bytes.
        """
        return len(self._frame_data)

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
        if normalize_id3v2_tag_version(tag_version) == (2, 2, 0):
            if len(frame_id) != 3:
                raise ValueError(
                    f"Frame ID {frame_id!r} is incompatible with "
                    f"ID3v2.{tag_version[1]} tags."
                )
            return frame_id

        if len(frame_id) != 4:
            raise ValueError(
                f"Frame ID {frame_id!r} is incompatible with "
                f"ID3v2.{tag_version[1]} tags."
            )
        return frame_id

    def serialize(
        self,
        tag_version: str | tuple[int, int, int],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> bytes:
        """
        Serialize the ID3v2 frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            ID3v2 tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        *args : tuple[Any, ...]
            Additional (ignored) positional arguments.

        **kwargs : dict[str, Any]
            Additional (ignored) keyword arguments.

        Returns
        -------
        stream : bytes
            Bytestream containing the ID3v2 frame.
        """
        match tag_version := normalize_id3v2_tag_version(tag_version):
            case (2, 4, _):
                if len(self._frame_id) != 4:
                    raise ValueError(
                        "Frame ID "
                        f"{self._frame_id.decode(encoding='ascii')!r} "
                        f"is incompatible with ID3v2.{tag_version[1]} "
                        "tags."
                    )
                return b"".join(
                    (
                        self._frame_id,
                        bytes(encode_synchsafe_int(self._frame_length)),
                        self._flags.to_bytes_2_4(),
                        self._frame_data,
                    )
                )
            case (2, 3, _):
                if len(self._frame_id) != 4:
                    raise ValueError(
                        "Frame ID "
                        f"{self._frame_id.decode(encoding='ascii')!r} "
                        f"is incompatible with ID3v2.{tag_version[1]} "
                        "tags."
                    )
                return b"".join(
                    (
                        self._frame_id,
                        self._frame_length.to_bytes(length=4, byteorder="big"),
                        self._flags.to_bytes_2_3(),
                        self._frame_data,
                    )
                )
            case (2, 2, _):
                if len(self._frame_id) != 3:
                    raise ValueError(
                        "Frame ID "
                        f"{self._frame_id.decode(encoding='ascii')!r} "
                        f"is incompatible with ID3v2.{tag_version[1]} "
                        "tags."
                    )
                return (
                    self._frame_id
                    + self._frame_length.to_bytes(length=3, byteorder="big")
                    + self._frame_data
                )
            case _:
                raise ValueError(
                    f"Invalid ID3v2 tag version {tag_version!r}. "
                    f"Valid values: {join_values(TAG_VERSIONS)}."
                )
