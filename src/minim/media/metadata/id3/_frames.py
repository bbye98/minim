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
    validate_number,
    validate_numeric,
    validate_range,
    validate_type,
)
from ._shared import (
    ID3V1_GENRES,
    ID3V2_TAG_VERSIONS,
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

    This class implements the following special methods:

    * :code:`__or__` – Merge two datetimes, preferring components from
      the right-hand operator.

    * :code:`__ior__` – Merge another datetime into the current one
      in-place, preferring components from the right-hand operator.
    """

    _DATETIME_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"^(\d{4})?(?:-(\d{2})(?:-(\d{2})(?:"
        r"T(\d{2})(?::(\d{2})(?::(\d{2}))?)?)?)?)?(.*)$"
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

            **Valid values**: :code:`0` to :code:`9_999`.

        month : int; optional
            Month.

            **Valid values**: :code:`1` to :code:`12`.

        day : int; optional
            Day.

            **Valid values**: :code:`1` to :code:`31`.

        hour : int; optional
            Hour.

            **Valid values**: :code:`0` to :code:`23`.

        minute : int; optional
            Minute.

            **Valid values**: :code:`0` to :code:`59`.

        second : int; optional
            Second.

            **Valid values**: :code:`0` to :code:`59`.

        extra : str; optional
            Extra information, such as timezone or fractional seconds.

            **Examples**: :code:`"Z"`, :code:`"-5:00"`.

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

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(year={self._year}, month={self._month}, "
            f"day={self._day}, hour={self._hour}, minute={self._minute}, "
            f"second={self._second}, extra={self._extra!r})"
        )

    def __or__(self, other: Self) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand types for |: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )

        obj = type_.__new__(type_)
        obj._year = other._year or self._year
        obj._month = other._month or self._month
        obj.day = other._day or self._day
        obj._hour = self._hour if other._hour is None else other._hour
        obj._minute = self._minute if other._minute is None else other._hour
        obj._second = self._second if other._second is None else other.second
        obj._extra = other.extra or self.extra
        return obj

    def __ior__(self, other: Self) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand types for |=: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )
        if other._year is not None:
            self._year = other._year
        if other._month is not None:
            self._month = other._month
        if other._day is not None:
            self.day = other._day
        if other._hour is not None:
            self._hour = other._hour
        if other._minute is not None:
            self._minute = other._minute
        if other._second is not None:
            self._second = other._second
        if other._extra is not None:
            self._extra = other._extra
        return self

    @classmethod
    def from_string(cls, dt: str, /, *, strict: bool = True) -> Self:
        """
        Instantiate a :class:`DateTime` object from a datetime string in
        ISO-8601 format.

        Parameters
        ----------
        dt : str; positional-only
            Datetime, in ISO-8601 format.

            **Examples**: :code:`2024-02-29T12:34:56Z`,
            :code:`2024-02-29`.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the audio
            format specifications.

        Returns
        -------
        dt : minim.metadata.id3._frames.DateTime
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
    ) -> Self:
        """
        Instantiate a :class:`DateTime` object from a tuple of datetime
        components.

        Parameters
        ----------
        dt : tuple[int | str | None, ...]; positional-only
            Datetime components, in order of year, month, day, hour,
            minute, second, and extras. Optional components may be
            represented as :code:`None` or omitted only if there are no
            more components after them.

            **Examples**: :code:`(2024, 2, 29, 12, 34, 56, "Z")`,
            :code:`(2024, 2, 29)`.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the audio
            format specifications.

        Returns
        -------
        dt : minim.metadata.id3._frame.DateTime
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

            **Valid values**: :code:`1` to :code:`12`.

        year : int
            Year.

            **Valid values**: :code:`0` to :code:`9_999`.

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
        :bdg-primary:`get` :bdg-secondary:`set` Year.
        """
        return self._year

    @year.setter
    def year(self, value: int | None, /) -> None:
        if value is not None:
            validate_range("year", value, MINYEAR, MAXYEAR)
            if self._month is not None and self._day is not None:
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
        :bdg-primary:`get` :bdg-secondary:`set` Month.
        """
        return self._month

    @month.setter
    def month(self, value: int | None, /) -> None:
        if value is not None:
            validate_range("month", value, 1, 12)
            if self._year is not None and self._day is not None:
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
        :bdg-primary:`get` :bdg-secondary:`set` Day.
        """
        return self._day

    @day.setter
    def day(self, value: int | None, /) -> None:
        if value is not None:
            validate_range(
                "day",
                value,
                1,
                self._get_num_days_in_month(self._month, year=self._year)
                if self._year is not None and self._month is not None
                else 31,
            )
        self._day = value

    @property
    def hour(self) -> int | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Hour.
        """
        return self._hour

    @hour.setter
    def hour(self, value: int | None, /) -> None:
        if value is not None:
            validate_range("hour", value, 0, 23)
        self._hour = value

    @property
    def minute(self) -> int | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Minute.
        """
        return self._minute

    @minute.setter
    def minute(self, value: int | None, /) -> None:
        if value is not None:
            validate_range("minute", value, 0, 59)
        self._minute = value

    @property
    def second(self) -> int | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Second.
        """
        return self._second

    @second.setter
    def second(self, value: int | None, /) -> None:
        if value is not None:
            validate_range("second", value, 0, 59)
        self._second = value

    @property
    def extra(self) -> str | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Extra information, such as timezone or fractional seconds.
        """
        return self._extra

    @extra.setter
    def extra(self, value: str | None, /) -> None:
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
        validate_type("use_placeholders", use_placeholders, bool)
        if use_placeholders:
            dt = ["YYYY" if self._year is None else f"{self._year:04}"]
            dt.append("-MM" if self._month is None else f"-{self._month:02}")
            dt.append("-DD" if self._day is None else f"-{self._day:02}")
            dt.append("Thh" if self._hour is None else f"T{self._hour:02}")
            dt.append(":mm" if self._minute is None else f":{self._minute:02}")
            dt.append(":ss" if self._second is None else f":{self._second:02}")
            if self._extra is not None:
                dt.append(self._extra)
            return "".join(dt)

        if self._year is None:
            return ""

        dt = f"{self._year:04}"
        if self._month is None:
            return dt

        dt = [dt, f"-{self._month:02}"]
        if self._day is None:
            return "".join(dt)

        dt.append(f"-{self._day:02}")
        if self._hour is None:
            return "".join(dt)

        dt.append(f"T{self._hour:02}")
        if self._minute is None:
            return "".join(dt)

        dt.append(f":{self._minute:02}")
        if self._second is None:
            return "".join(dt)

        dt.append(f":{self._second:02}")
        if self._extra is not None:
            dt.append(self._extra)
        return "".join(dt)


class Position(NamedTuple):
    """
    Position within a set.
    """

    number: int | str
    total: int | str | None = None

    @classmethod
    def from_string(cls, position: str, /, *, strict: bool = True) -> Self:
        """
        Instantiate a :class:`Position` object from a string.

        Parameters
        ----------
        position : str; positional-only
            String containing the position within a set.

            **Examples**: :code:`"1"`, :code:`"1/2".

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the audio
            format specifications.

        Returns
        -------
        position : minim.metadata.id3._frames.Position
            Position within a set.
        """
        num_slashes = position.count("/")
        if num_slashes > 1:
            raise ValueError(f"Invalid position number {position!r}.")

        lower_bound = 1 if strict else None
        if num_slashes:
            position = position.split("/", maxsplit=1)
            validate_numeric("position[0]", position[0], int, lower_bound)
            if position[1]:
                validate_numeric("position[1]", position[1], int, lower_bound)
                return cls(int(position[0]), int(position[1]))
            return cls(int(position[0]), None)
        else:
            validate_numeric(position, position, int, lower_bound)
            return cls(int(position), None)

    @classmethod
    def from_tuple(
        cls,
        position: tuple[int | str, int | str | None],
        /,
        *,
        strict: bool = True,
    ) -> Self:
        """
        Instantiate a :class:`Position` object from a tuple.

        Parameters
        ----------
        position : tuple[int | str, int | str | None]; positional-only
            Tuple containing the position within a set.

            **Examples**: :code:`(1, 2)`, :code:`("1", "2")`,
            :code:`(1, None)`.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the audio
            format specifications.

        Returns
        -------
        position : minim.metadata.id3._frames.Position
            Position within a set.
        """
        lower_bound = 1 if strict else None
        validate_numeric("position[0]", position[0], int, lower_bound)
        if position[1]:
            validate_numeric("position[1]", position[1], int, lower_bound)
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
    Flags for an ID3v2 frame.
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
            preceding the payload denoting its raw length.
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

    def __repr__(self) -> str:
        flags = []
        if self._discard_on_tag_alter:
            flags.append("discard_on_tag_alter=True")
        if self._discard_on_file_alter:
            flags.append("discard_on_file_alter=True")
        if self._is_read_only:
            flags.append("is_read_only=True")
        if self._has_group_id:
            flags.append("has_group_id=True")
        if self._is_compressed:
            flags.append("is_compressed=True")
        if self._is_encrypted:
            flags.append("is_encrypted=True")
        if self._is_unsynchronized:
            flags.append("is_unsynchronized=True")
        if self._has_data_length_indicator:
            flags.append("has_data_length_indicator=True")
        return f"{type(self).__name__}({', '.join(flags)})"

    @classmethod
    def _from_bytes_2_3(
        cls, status_flags: int, format_flags: int, /, *, strict: bool = True
    ) -> Self:
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
        flags : minim.media.metadata.id3.ID3v2FrameFlags
            Flags for the ID3v2.3 frame.
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
    ) -> Self:
        """
        Instantiate an :class:`ID3v2FrameFlags` object from ID3v2.4
        frame flags bytes.

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
        flags : minim.media.metadata.id3.ID3v2FrameFlags
            Flags for the ID3v2.4 frame.
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
    ) -> Self:
        """
        Instantiate an :class:`ID3v2FrameFlags` object from ID3v2 frame
        flags bytes.

        Parameters
        ----------
        status_flags : int; positional-only
            ID3v2 frame status flags byte.

        format_flags : int; positional-only
            ID3v2 frame format flags byte.

        tag_version : str or tuple[int, int, int]
            Tag version.

            **Valid values**: :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        flags : minim.media.metadata.id3.ID3v2FrameFlags
            Flags.
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
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
                )

    @property
    def discard_on_tag_alter(self) -> bool:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
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
        :bdg-primary:`get` :bdg-secondary:`set`
        Whether the current frame has an extra synchsafe integer
        preceding the payload denoting its raw length.
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
        Serialize the ID3v2 frame flags to bytes.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            Tag version.

            **Valid values**: :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        bytes_ : bytes
            Bytes containing the ID3v2 frame flags.
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
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
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
        flags : minim.media.metadata.id3.ID3v2FrameFlags; \
        keyword-only; optional
            Flags.

        group_id : int; keyword-only; optional
            Group identifier.

            **Valid range**: :code:`0` to :code:`255`.
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

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        for frame_ids in cls._frame_ids.values():
            if isinstance(frame_ids, bytes):
                cls._REGISTRY[frame_ids] = cls
            else:
                for frame_id in frame_ids:
                    cls._REGISTRY[frame_id] = cls

    @abstractmethod
    def __repr__(self) -> str:
        return super().__repr__()

    @classmethod
    def _get_class(cls, frame_id: bytes, /) -> Self:
        """
        Get the class corresponding to an Frame ID.

        Parameters
        ----------
        frame_id : bytes; positional-only
            Frame ID.

        Returns
        -------
        cls : minim.media.metadata.id3._frames.ID3v2Frame
            ID3v2 frame class.
        """
        return cls._REGISTRY.get(frame_id, UnknownID3v2Frame)

    @classmethod
    @abstractmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
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
        frame : minim.media.metadata.id3._frames.ID3v2Frame
            ID3v2 frame.
        """
        if strict and len(stream) < 7:
            raise ValueError(
                "ID3v2.2 frame must be at least 1 byte long, excluding "
                "the header."
            )

        obj = cls.__new__(cls)
        obj._flags = ID3v2FrameFlags()
        obj._group_id = None
        return obj

    @classmethod
    @abstractmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
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
        frame : minim.media.metadata.id3._frames.ID3v2Frame
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
            obj = EncryptedID3v2Frame.__new__(EncryptedID3v2Frame)
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
    ) -> Self:
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
        frame : minim.media.metadata.id3._frames.ID3v2Frame
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
            obj = EncryptedID3v2Frame.__new__(EncryptedID3v2Frame)
            obj._frame_id = stream[:4].tobytes()
            obj._frame_length = int.from_bytes(stream[4:8], byteorder="big")
            obj._frame_data = stream[10 : 10 + obj._frame_length].tobytes()
            return obj

        obj = cls.__new__(cls)
        obj._flags = flags
        return obj

    @classmethod
    def _prepare_text_encoding(cls, text_encoding: int | str, /) -> None:
        """
        Validate and normalize a text encoding.

        Parameters
        ----------
        text_encoding : int or str; positional-only
            Text encoding.

        Returns
        -------
        text_encoding : str
            Normalized text encoding.
        """
        validate_type("text_encoding", text_encoding, int | str)
        text_encodings = cls._TEXT_ENCODINGS
        if isinstance(text_encoding, str):
            text_encoding = text_encoding.lower()
        if text_encoding not in text_encodings:
            text_encodings = tuple(text_encodings)
            num_encodings = len(text_encodings) // 2
            text_encodings = ", ".join(
                f"{s!r} (or {n})"
                for n, s in zip(
                    text_encodings[:num_encodings],
                    text_encodings[num_encodings:],
                )
            )
            raise ValueError(
                f"Invalid text encoding {text_encoding!r}. "
                f"Valid values: {text_encodings}."
            )
        if isinstance(text_encoding, int):
            text_encoding = text_encodings[text_encoding]
        return text_encoding

    @classmethod
    def from_stream(
        cls,
        stream: BytesLike,
        /,
        tag_version: str | tuple[int, int, int],
        *,
        strict: bool = True,
    ) -> Self:
        """
        Instantiate an :class:`ID3v2Frame` object from a bytes-like
        object.

        Parameters
        ----------
        stream : BytesLike; positional-only; optional
            Bytes-like object containing an ID3v2 frame.

        tag_version : str or tuple[int, int, int]
            Tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        frame : minim.media.metadata.id3._frames.ID3v2Frame
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
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
                )

    @classmethod
    def get_frame_id(
        cls, tag_version: str | tuple[int, int, int]
    ) -> bytes | list[bytes] | None:
        """
        Get the frame ID for a given tag version.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            Tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        frame_id : bytes, list[bytes], or None
            Frame ID. If no native frame is available for the
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
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
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

    @staticmethod
    def _ensure_iso88591_encode(name: str, values: str | list[str], /) -> None:
        """
        Ensure that all values can be encoded using ISO-8859-1.

        Parameters
        ----------
        name : str; positional-only
            Parameter name.

        values : str or list[str]; positional-only
            Values to encode.
        """
        try:
            if isinstance(values, str):
                values.encode(encoding="iso-8859-1")
            else:
                for value in values:
                    value.encode(encoding="iso-8859-1")
            is_utf = False
        except UnicodeEncodeError:
            is_utf = True
        if is_utf:
            raise ValueError(f"`{name}` cannot be encoded using ISO-8859-1.")

    @property
    @abstractmethod
    def _frame_ids(self) -> dict[int, bytes]:
        """
        ID3v2 frame IDs, with the keys being the ID3v2 tag minor
        versions.
        """
        ...

    @property
    def _key(self) -> Any:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set` Unique key.
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
        :bdg-primary:`get` :bdg-secondary-line:`set` Flags.
        """
        return self._flags

    @property
    def group_id(self) -> int | None:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Group identifier.
        """
        return self._group_id

    @group_id.setter
    def group_id(self, value: int | None, /) -> None:
        if value is None:
            self._flags._has_group_id = False
        else:
            validate_number("group_id", value, int, 0, 255)
        self._group_id = value

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
        else:
            self._group_id = None
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
        else:
            self._group_id = None
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
        if flags._is_encrypted:
            raise RuntimeError(
                "Cannot serialize an encrypted "
                f"{frame_id.decode(encoding='iso-8859-1')} frame."
            )
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
        if flags._is_encrypted:
            raise RuntimeError(
                "Cannot serialize an encrypted "
                f"{frame_id.decode(encoding='iso-8859-1')} frame."
            )

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
            Tag version.

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
            text_encoding_byte = TEXT_ENCODINGS[
                self._prepare_text_encoding(text_encoding)
            ]
            if tag_version[:2] != (2, 4):
                text_encoding = TEXT_ENCODINGS[min(text_encoding_byte, 1)]
        return text_encoding

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
            Tag version.

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


class ID3v2TextInfoFrame(ID3v2Frame):
    """
    Text information frame.
    """

    _allow_multiple: ClassVar[bool] = False
    _frame_ids: ClassVar[dict[int, bytes]] = {}

    __slots__ = ("_text_encoding", "_text_info")

    def __init__(
        self,
        text_info: Any | OrderedCollection[Any],
        /,
        *,
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
        group_id: int | None = None,
    ) -> None:
        """
        This class implements the following special methods:

        * :code:`__add__` – Concatenate two text information frames,
          appending values from the right-hand operand.

        * :code:`__iadd__` – Concatenate another text information frame
          with the current one in-place, appending values from the
          right-hand operand.

        Parameters
        ----------
        text_info : Any or OrderedCollection[Any]; positional-only
            Text information.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        flags : minim.media.metadata.id3.ID3v2FrameFlags; \
        keyword-only; optional
            Flags.

        group_id : int; keyword-only; optional
            Group identifier.

            **Valid range**: :code:`0` to :code:`255`.
        """
        super().__init__(flags=flags, group_id=group_id)
        self.text_info = text_info
        self.text_encoding = text_encoding

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"<{len(self._text_info)} value(s)>, "
            f"text_encoding={self._text_encoding!r}, "
            f"flags={self._flags!r}, group_id={self._group_id})"
        )

    def __add__(self, other: ID3v2TextInfoFrame) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand types for +: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )
        if self._allow_multiple:
            raise ValueError(
                f"{type_.__name__} can appear multiple times in a "
                "ID3v2 tag, so multiple values should be stored in "
                "separate instances."
            )
        TEXT_ENCODINGS = self._TEXT_ENCODINGS
        obj = type_.__new__(type_)
        obj._text_info = self._text_info + other._text_info
        obj._text_encoding = TEXT_ENCODINGS[
            max(
                TEXT_ENCODINGS[self._text_encoding],
                TEXT_ENCODINGS[other._text_encoding],
            )
        ]
        obj._flags = self._flags
        obj._group_id = self._group_id
        return obj

    def __iadd__(self, other: ID3v2TextInfoFrame) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand types for +=: "
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
    ) -> Self:
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
        text_info_frame : minim.media.metadata.id3._frames.ID3v2TextInfoFrame
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
    ) -> Self:
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
        text_info_frame : minim.media.metadata.id3._frames.ID3v2TextInfoFrame
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
    ) -> Self:
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
        text_info_frame : minim.media.metadata.id3._frames.ID3v2TextInfoFrame
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
        :bdg-primary:`get` :bdg-secondary:`set` Text information.
        """
        return self._text_info.copy()

    @text_info.setter
    def text_info(self, value: str | list[str], /) -> None:
        is_iso88591 = getattr(self, "_text_encoding", None) == "iso-8859-1"
        if isinstance(value, str):
            if is_iso88591:
                self._ensure_iso88591_encode("text_info", value)
            self._text_info = [value]
        elif isinstance(value, ORDERED_COLLECTION_TYPES):
            self._text_info = _text_info = []
            if is_iso88591:
                for ti_idx, ti in enumerate(value):
                    param_name = f"text_info[{ti_idx}]"
                    validate_type(param_name, ti, str)
                    self._ensure_iso88591_encode(param_name, ti)
                    _text_info.append(ti)
            else:
                for ti_idx, ti in enumerate(value):
                    validate_type(f"text_info[{ti_idx}]", ti, str)
                    _text_info.append(ti)
        else:
            raise TypeError(
                "`text_info` must be a string or an ordered collection "
                "of strings."
            )

    @property
    def text_encoding(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Text encoding.
        """
        return self._text_encoding

    @text_encoding.setter
    def text_encoding(self, value: int | str, /) -> None:
        value = self._prepare_text_encoding(value)
        if value == "iso-8859-1":
            self._ensure_iso88591_encode("text_info", self._text_info)
        self._text_encoding = value

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
            Tag version.

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
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
                )


class ID3v2DateTimeFrame(ID3v2TextInfoFrame):
    """
    Datetime frame.

    This class implements the following special methods:

    * :code:`__add__` – Concatenate two datetime frames, appending
      datetimes from the right-hand operand.

    * :code:`__iadd__` – Concatenate another datetime frame with the
      current one in-place, appending datetimes from the right-hand
      operand.

    * :code:`__or__` – Merge two datetime frames, combining
      corresponding datetimes.

    * :code:`__ior__` – Merge another datetime frame with the current
      one in-place, combining corresponding datetimes.
    """

    _frame_ids: ClassVar[dict[int, bytes]] = {}

    __slots__ = ("_datetimes",)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(<{len(self._datetimes)} value(s)>, "
            f"text_encoding={self._text_encoding!r}, "
            f"flags={self._flags!r}, group_id={self._group_id})"
        )

    def __add__(self, other: ID3v2DateTimeFrame) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand types for +: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )

        TEXT_ENCODINGS = self._TEXT_ENCODINGS
        obj = type_.__new__(type_)
        obj._datetimes = self._datetimes + other._datetimes
        obj._flags = self._flags
        obj._group_id = self._group_id
        obj._text_encoding = TEXT_ENCODINGS[
            max(
                TEXT_ENCODINGS[self._text_encoding],
                TEXT_ENCODINGS[other._text_encoding],
            )
        ]
        return obj

    def __iadd__(self, other: ID3v2DateTimeFrame) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand types for +=: "
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
                "Unsupported operand types for |: "
                f"{type_.__name__!r} and {type(other).__name__!r}."
            )
        if len(self._datetimes) != len(other._datetimes):
            raise ValueError(
                f"Cannot combine {type_.__name__} objects with "
                "different numbers of datetimes."
            )

        TEXT_ENCODINGS = self._TEXT_ENCODINGS
        obj = type_.__new__(type_)
        obj._datetimes = [
            self_dt | other_dt
            for self_dt, other_dt in zip(self._datetimes, other._datetimes)
        ]
        obj._flags = other._flags
        obj._group_id = (
            other._group_id if self._group_id is None else self._group_id
        )
        obj._text_encoding = TEXT_ENCODINGS[
            max(
                TEXT_ENCODINGS[self._text_encoding],
                TEXT_ENCODINGS[other._text_encoding],
            )
        ]
        return obj

    def __ior__(self, other: ID3v2DateTimeFrame) -> Self:
        type_ = type(self)
        if not isinstance(other, type_):
            raise TypeError(
                "Unsupported operand types for |=: "
                f"'{type_.__name__}' and {type(other).__name__!r}."
            )
        if len(self._datetimes) != len(other._datetimes):
            raise ValueError(
                f"Cannot combine {type_.__name__} objects with "
                "different numbers of datetimes."
            )

        for self_dt, other_dt in zip(self._datetimes, other._datetimes):
            self_dt |= other_dt
        if other._group_id is not None:
            self._group_id = other._group_id
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
    ) -> Self:
        """
        Instantiate an :class:`ID3v2DateTimeFrame` object from an
        ID3v2.4 frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the datetime frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        datetime_frame : minim.media.metadata.id3._frames.ID3v2DateTimeFrame
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
        | DateTime
        | Iterable[str | datetime | tuple[int | str, ...] | DateTime],
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
        datetimes : minim.media.metadata.id3._frames.DateTime or \
        list[minim.media.metadata.id3._frames.DateTime]
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
            case DateTime():
                return datetimes
            case _ if isinstance(datetimes, Iterable):
                return [
                    ID3v2DateTimeFrame._parse_datetimes(dt, strict=strict)
                    for dt in datetimes
                ]
            case _:
                raise TypeError(
                    "`datetimes` must be one or more strings, "
                    "datetime.datetime objects, tuples of integers, or "
                    "DateTime objects."
                )

    @property
    def _text_info(self) -> list[str]:
        """
        Text information.
        """
        return [dt.to_string() for dt in self._datetimes]

    @property
    def text_info(self) -> list[str]:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Text information (datetimes).
        """
        return self._text_info

    @text_info.setter
    def text_info(
        self,
        value: str
        | datetime
        | tuple[int | str, ...]
        | DateTime
        | list[str | datetime | tuple[int | str, ...] | DateTime],
        /,
    ) -> None:
        value = self._parse_datetimes(value)
        if not isinstance(value, list):
            value = [value]
        if getattr(self, "_text_encoding", None) == "iso-8859-1":
            for dt_idx, dt in enumerate(value):
                self._ensure_iso88591_encode(f"text_info[{dt_idx}]", dt._extra)
        self._datetimes = value

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
            Tag version.

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
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
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
        group_id: int | None = None,
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

        flags : minim.media.metadata.id3.ID3v2FrameFlags; \
        keyword-only; optional
            Flags.

        group_id : int; keyword-only; optional
            Group identifier.

            **Valid range**: :code:`0` to :code:`255`.
        """
        super().__init__(flags=flags, group_id=group_id)

        self.picture_type = picture_type

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

        self.description = description
        self.text_encoding = text_encoding

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(picture_type={self._picture_type!r}, "
            f"mime_type={self._mime_type!r}, "
            f"picture_data=<{len(self._picture_data)} byte(s)>, "
            f"description={self._description!r}, "
            f"text_encoding={self._text_encoding!r}, "
            f"flags={self._flags!r}, group_id={self._group_id})"
        )

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
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
        picture_frame : minim.media.metadata.id3.ID3v2APICFrame
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
    ) -> Self:
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
        picture_frame : minim.media.metadata.id3.ID3v2APICFrame
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
    ) -> Self:
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
        picture_frame : minim.media.metadata.id3.ID3v2APICFrame
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
    def _key(self) -> int | str:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set` Unique key.
        """
        if self._picture_type in {1, 2}:
            return self._picture_type
        return self._description

    @property
    def picture_type(self) -> int:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Picture type.
        """
        return self._picture_type

    @picture_type.setter
    def picture_type(self, value: int, /) -> None:
        validate_number("picture_type", value, int, 0, 20)
        self._picture_type = value

    @property
    def mime_type(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set` MIME type.
        """
        return self._mime_type

    @property
    def picture_data(self) -> bytes:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set` Picture data.
        """
        return self._picture_data

    @property
    def description(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Picture description.
        """
        return self._description

    @description.setter
    def description(self, value: str, /) -> None:
        validate_type("description", value, str)
        if getattr(self, "_text_encoding", None) == "iso-8859-1":
            self._ensure_iso88591_encode("description", value)
        self._description = value

    @property
    def text_encoding(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Text encoding.
        """
        return self._text_encoding

    @text_encoding.setter
    def text_encoding(self, value: int | str, /) -> None:
        value = self._prepare_text_encoding(value)
        if value == "iso-8859-1":
            self._ensure_iso88591_encode("description", self._description)
            self._ensure_iso88591_encode("text_info", self._text_info)
        self._text_encoding = value

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
            Tag version.

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
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
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
        comment: str,
        /,
        *,
        description: str = "",
        language: str = "eng",
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
        group_id: int | None = None,
    ) -> None:
        """
        Parameters
        ----------
        comment : str; positional-only
            Comment.

        description : str; keyword-only; default: :code:`""`
            Short content description.

        language : str; keyword-only; default: :code:`"eng"`
            ISO 639-2 code for the language.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding for the picture description.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        flags : minim.media.metadata.id3.ID3v2FrameFlags; \
        keyword-only; optional
            Flags.

        group_id : int; keyword-only; optional
            Group identifier.

            **Valid range**: :code:`0` to :code:`255`.
        """
        super().__init__(flags=flags, group_id=group_id)
        self.description = description
        self.comment = comment
        self.language = language
        self.text_encoding = text_encoding

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(description={self._description!r}, "
            f"comment={self._comment!r}, langauge={self._language!r}, "
            f"text_encoding={self._text_encoding!r}, "
            f"flags={self._flags!r}, group_id={self._group_id})"
        )

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
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
        comment_frame : minim.media.metadata.id3.ID3v2COMMFrame
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
    ) -> Self:
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
        comment_frame : minim.media.metadata.id3.ID3v2COMMFrame
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
    ) -> Self:
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
        comment_frame : minim.media.metadata.id3.ID3v2COMMFrame
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
    def _key(self) -> tuple[str, str]:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set` Unique key.
        """
        return self._language, self._description

    @property
    def description(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Short content description.
        """
        return self._description

    @description.setter
    def description(self, value: str, /) -> None:
        validate_type("description", value, str)
        if getattr(self, "_text_encoding", None) == "iso-8859-1":
            self._ensure_iso88591_encode("description", value)
        self._description = value

    @property
    def comment(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Comment.
        """
        return self._comment

    @comment.setter
    def comment(self, value: str, /) -> None:
        validate_type("comment", value, str)
        if getattr(self, "_text_encoding", None) == "iso-8859-1":
            self._ensure_iso88591_encode("comment", value)
        self._comment = value

    @property
    def language(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        ISO 639-2 code for the language.
        """
        return self._language

    @language.setter
    def language(self, value: str, /) -> None:
        validate_type("language", value, str)
        if len(value) != 3:
            raise ValueError(f"Invalid ISO 639-2 code {value!r}.")
        self._language = value

    @property
    def text_encoding(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Text encoding.
        """
        return self._text_encoding

    @text_encoding.setter
    def text_encoding(self, value: int | str, /) -> None:
        value = self._prepare_text_encoding(value)
        if value == "iso-8859-1":
            self._ensure_iso88591_encode("description", self._description)
            self._ensure_iso88591_encode("comment", self._comment)
        self._text_encoding = value

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
            Tag version.

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
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
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

    @classmethod
    def _from_stream_2_2(cls, stream: memoryview, /, *, strict=True) -> Self:
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
        bpm_frame : minim.media.metadata.id3.ID3v2TBPMFrame
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
    def _from_stream_2_3(cls, stream: memoryview, /, *, strict=True) -> Self:
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
        bpm_frame : minim.media.metadata.id3.ID3v2TBPMFrame
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
    def _from_stream_2_4(cls, stream: memoryview, /, *, strict=True) -> Self:
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
        bpm_frame : minim.media.metadata.id3.ID3v2TBPMFrame
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

    @ID3v2TextInfoFrame.text_info.setter
    def text_info(
        self, value: float | str | OrderedCollection[int | float | str], /
    ) -> None:
        if isinstance(value, (int, float, str)):
            self._text_info = [str(round(float(value)))]
        elif isinstance(value, ORDERED_COLLECTION_TYPES):
            self._text_info = _text_info = []
            for idx, bpm in enumerate(value):
                validate_numeric(f"text_info[{idx}]", bpm, int | float, 0)
                _text_info.append(str(round(float(bpm))))
        else:
            raise TypeError(
                "`text_info` must be a number, a string, or an ordered "
                "collection of numbers and/or strings."
            )


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

    @classmethod
    def _from_stream_2_2(cls, stream: memoryview, /, *, strict=True) -> Self:
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
        compilation_flag_frame : minim.media.metadata.id3.ID3v2TCMPFrame
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
    def _from_stream_2_3(cls, stream: memoryview, /, *, strict=True) -> Self:
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
        compilation_flag_frame : minim.media.metadata.id3.ID3v2TCMPFrame
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
    def _from_stream_2_4(cls, stream: memoryview, /, *, strict=True) -> Self:
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
        compilation_flag_frame : minim.media.metadata.id3.ID3v2TCMPFrame
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

    @ID3v2TextInfoFrame.text_info.setter
    def text_info(
        self, value: bool | int | str | OrderedCollection[bool | int | str], /
    ) -> None:
        if isinstance(value, bool | int | str):
            self._text_info = [str(int(value))]
        elif isinstance(value, ORDERED_COLLECTION_TYPES):
            self._text_info = _text_info = []
            for idx, flag in enumerate(value):
                validate_numeric(f"text_info[{idx}]", flag, int, 0, 1)
                _text_info.append(str(int(flag)))
        else:
            raise TypeError(
                "`text_info` must be a boolean, a number, a string, or "
                "an ordered collection of booleans, numbers, and/or "
                "strings."
            )


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
    ) -> Self:
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
        content_type_frame : minim.media.metadata.id3.ID3v2TCONFrame
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
    ) -> Self:
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
        content_type_frame : minim.media.metadata.id3.ID3v2TCONFrame
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
    ) -> Self:
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
        content_type_frame : minim.media.metadata.id3.ID3v2TCONFrame
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
            ID3V1_GENRES.get(int(content_type), content_type)
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
                text_info.append(ID3V1_GENRES.get(code, genre.group(0)))
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
                if (code := ID3V1_GENRES.get(content_type.lower())) is None
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
            Tag version.

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
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
                )

    @ID3v2TextInfoFrame.text_info.setter
    def text_info(self, value: str | OrderedCollection[str], /) -> None:
        if isinstance(value, str):
            self._text_info, self._refinements = (
                self._deserialize_content_types([value])
            )
        elif isinstance(value, ORDERED_COLLECTION_TYPES):
            self._text_info, self._refinements = (
                self._deserialize_content_types(value)
            )
        else:
            raise TypeError(
                "`text_info` must be a string or an ordered collection "
                "of strings."
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
    ) -> Self:
        """
        Instantiate an :class:`ID3v2TDRCFrame` object from an ID3v2.2
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the datetime frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        datetime_frame : minim.media.metadata.id3.ID3v2TDRCFrame
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
    ) -> Self:
        """
        Instantiate an :class:`ID3v2TDRCFrame` object from an ID3v2.3
        frame bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the datetime frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        datetime_frame : minim.media.metadata.id3.ID3v2TDRCFrame
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
            Tag version.

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
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
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

    __slots__ = ("_discs",)

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
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
        disc_frame : minim.media.metadata.id3.ID3v2TPOSFrame
            :code:`TPA` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_2(
            stream, strict=strict
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        obj._discs = cls._parse_discs(
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
    ) -> Self:
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
        disc_frame : minim.media.metadata.id3.ID3v2TPOSFrame
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
        obj._discs = cls._parse_discs(
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
    ) -> Self:
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
        disc_frame : minim.media.metadata.id3.ID3v2TPOSFrame
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
        obj._discs = cls._parse_discs(
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
        | Position
        | list[int | str | tuple[int | str, int | str | None] | Position],
        /,
        *,
        strict: bool = True,
    ) -> Position | list[Position]:
        """
        Parse disc numbers.

        Parameters
        ----------
        discs : int, str, tuple[int | str, int | str | None], \
        minim.media.metadata.id3.Position, or list[int | str \
        | tuple[int | str, int | str | None] \
        | minim.media.metadata.id3.Position]; positional-only
            Disc numbers and, optionally, the total number of discs.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        discs : minim.media.metadata.id3._frames.Position or \
        list[minim.media.metadata.id3._frames.Position]
            Parsed disc numbers.
        """
        match discs:
            case int():
                return Position(discs)
            case str():
                return Position.from_string(discs, strict=strict)
            case tuple() if len(discs) == 2:
                return Position.from_tuple(discs, strict=strict)
            case list():
                return [
                    ID3v2TPOSFrame._parse_discs(disc, strict=strict)
                    for disc in discs
                ]
            case Position():
                return discs
            case _:
                raise TypeError(
                    "`disc` must be one or more integers, strings, "
                    "tuples of two integers and/or strings, or "
                    "Position objects."
                )

    @property
    def _text_info(self) -> list[str]:
        """
        Text information.
        """
        return [disc.to_string() for disc in self._discs]

    @property
    def text_info(self) -> list[str]:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Text information (disc numbers and positions in set).
        """
        return self._text_info

    @text_info.setter
    def text_info(
        self,
        value: int
        | str
        | tuple[int | str, int | str | None]
        | list[int | str | tuple[int | str, int | str | None]],
        /,
    ) -> None:
        value = self._parse_discs(value)
        if not isinstance(value, list):
            value = [value]
        self._discs = value


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

    __slots__ = ("_tracks",)

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
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
        track_frame : minim.media.metadata.id3.ID3v2TRCKFrame
            :code:`TRK` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_2(
            stream, strict=strict
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        obj._tracks = cls._parse_tracks(
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
    ) -> Self:
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
        track_frame : minim.media.metadata.id3.ID3v2TRCKFrame
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
        obj._tracks = cls._parse_tracks(
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
    ) -> Self:
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
        track_frame : minim.media.metadata.id3.ID3v2TRCKFrame
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
        obj._tracks = cls._parse_tracks(
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
        | Position
        | list[int | str | tuple[int | str, int | str | None] | Position],
        /,
        *,
        strict: bool = True,
    ) -> Position | list[Position]:
        """
        Parse track numbers.

        Parameters
        ----------
        tracks : int, str, tuple[int | str, int | str | None], \
        minim.media.metadata.id3.Position, or list[int | str \
        | tuple[int | str, int | str | None] \
        | minim.media.metadata.id3.Position]; positional-only
            Track numbers and, optionally, the total number of tracks.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        tracks : minim.media.metadata.id3._frames.Position or \
        list[minim.media.metadata.id3._frames.Position]
            Parsed track numbers.
        """
        match tracks:
            case int():
                return Position(tracks)
            case str():
                return Position.from_string(tracks, strict=strict)
            case tuple() if len(tracks) == 2:
                return Position.from_tuple(tracks, strict=strict)
            case list():
                return [
                    ID3v2TRCKFrame._parse_tracks(track, strict=strict)
                    for track in tracks
                ]
            case Position():
                return tracks
            case _:
                raise TypeError(
                    "`tracks` must be one or more integers, strings, "
                    "tuples of two integers and/or strings, or "
                    "Position objects."
                )

    @property
    def _text_info(self) -> list[str]:
        """
        Text information.
        """
        return [track.to_string() for track in self._tracks]

    @property
    def text_info(self) -> list[str]:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Text information (track numbers and positions in set).
        """
        return self._text_info

    @text_info.setter
    def text_info(
        self,
        value: int
        | str
        | tuple[int | str, int | str | None]
        | list[int | str | tuple[int | str, int | str | None]],
        /,
    ) -> None:
        value = self._parse_tracks(value)
        if not isinstance(value, list):
            value = [value]
        self._tracks = value


class ID3v2TSRCFrame(ID3v2TextInfoFrame):
    """
    "International Standard Recording Code (ISRC)" frame.

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

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
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
        isrc_frame : minim.media.metadata.id3.ID3v2TSRCFrame
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
    ) -> Self:
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
        isrc_frame : minim.media.metadata.id3.ID3v2TSRCFrame
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
    ) -> Self:
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
        isrc_frame : minim.media.metadata.id3.ID3v2TSRCFrame
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

    @ID3v2TextInfoFrame.text_info.setter
    def text_info(self, value: str | OrderedCollection[str], /) -> None:
        if isinstance(value, str):
            value = [value]
        self._text_info = [prepare_isrc(isrc) for isrc in value]


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
        text_info: str,
        *,
        text_encoding: str = "utf-16",
        flags: ID3v2FrameFlags | None = None,
        group_id: int | None = None,
    ) -> None:
        """
        Parameters
        ----------
        description : str
            Text information description.

        text_info : str
            Text information.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        flags : minim.media.metadata.id3.ID3v2FrameFlags; \
        keyword-only; optional
            Flags.

        group_id : int; keyword-only; optional
            Group identifier.

            **Valid range**: :code:`0` to :code:`255`.
        """
        self.description = description
        super().__init__(
            text_info,
            text_encoding=text_encoding,
            flags=flags,
            group_id=group_id,
        )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(description={self._description!r}, "
            f"text_info={self._text_info!r}, "
            f"text_encoding={self._text_encoding!r}, "
            f"flags={self._flags!r}, group_id={self._group_id})"
        )

    def __add__(self, other: Self) -> Self:
        raise TypeError(
            "Unsupported operand type(s) for +: "
            f"{type(self).__name__!r} and {type(other).__name__!r}."
        )

    def __iadd__(self, other: Self) -> Self:
        raise TypeError(
            "Unsupported operand type(s) for +=: "
            f"{type(self).__name__!r} and {type(other).__name__!r}."
        )

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
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
        text_info_frame : minim.media.metadata.id3.ID3v2TXXXFrame
            :code:`TXX` frame.
        """
        obj = super(ID3v2TextInfoFrame, cls)._from_stream_2_2(
            stream, strict=strict
        )
        obj._text_encoding = cls._TEXT_ENCODINGS[stream[6]]
        obj._description, obj._text_info = cls._split_bytestream(
            stream[7 : 6 + int.from_bytes(stream[3:6], byteorder="big")],
            encoding=obj._text_encoding,
            max_splits=1,
        )
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
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
        text_info_frame : minim.media.metadata.id3.ID3v2TXXXFrame
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
        obj._description, obj._text_info = cls._split_bytestream(
            stream[offset + 1 : offset + frame_length],
            encoding=obj._text_encoding,
            max_splits=1,
        )
        return obj

    @classmethod
    def _from_stream_2_4(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
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
        text_info_frame : minim.media.metadata.id3.ID3v2TXXXFrame
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
        obj._description, obj._text_info = cls._split_bytestream(
            stream[offset + 1 : offset + frame_length],
            encoding=obj._text_encoding,
            max_splits=1,
        )
        return obj

    @property
    def _key(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set` Unique key.
        """
        return self._description

    @property
    def description(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Text information description.
        """
        return self._description

    @description.setter
    def description(self, value: str, /) -> None:
        validate_type("description", value, str)
        if getattr(self, "_text_encoding", None) == "iso-8859-1":
            self._ensure_iso88591_encode("description", value)
        self._description = value

    @property
    def text_info(self) -> str:
        return self._text_info

    @text_info.setter
    def text_info(self, value: str, /) -> None:
        validate_type("text_info", value, str)
        if getattr(self, "_text_encoding", None) == "iso-8859-1":
            self._ensure_iso88591_encode("text_info", value)
        self._text_info = value

    @ID3v2TextInfoFrame.text_encoding.setter
    def text_encoding(self, value: int | str, /) -> None:
        value = self._prepare_text_encoding(value)
        if value == "iso-8859-1":
            self._ensure_iso88591_encode("description", self._description)
            self._ensure_iso88591_encode("text_info", self._text_info)
        self._text_encoding = value

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
            Tag version.

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
        frame_data = b"".join(
            (
                self._TEXT_ENCODINGS[text_encoding].to_bytes(byteorder="big"),
                self._description.encode(encoding=text_encoding),
                self._text_info.encode(encoding=text_encoding),
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
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
                )


class ID3v2USLTFrame(ID3v2Frame):
    """
    "Unsynchronized lyrics/text transcription" frame.

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
        group_id: int | None = None,
    ) -> None:
        """
        Parameters
        ----------
        lyrics : str; positional-only
            Unsynchronized lyrics.

        description : str; keyword-only; default: :code:`""`
            Short content description.

        language : str; keyword-only; default: :code:`"eng"`
            ISO 639-2 code for the language.

        text_encoding : str; keyword-only; default: :code:`"utf-16"`
            Text encoding for the lyrics and description.

            **Valid values**: :code:`"iso-8859-1"`, :code:`"utf-16"`,
            :code:`"utf-16be"`, :code:`"utf-8"`.

        flags : minim.media.metadata.id3.ID3v2FrameFlags; \
        keyword-only; optional
            Flags.

        group_id : int; keyword-only; optional
            Group identifier.

            **Valid range**: :code:`0` to :code:`255`.
        """
        super().__init__(flags=flags, group_id=group_id)
        self.lyrics = lyrics
        self.description = description
        self.language = language
        self.text_encoding = text_encoding

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"<lyrics with {len(self._lyrics)} character(s)>, "
            f"description={self._description!r}, "
            f"language={self._language!r}, "
            f"text_encoding={self._text_encoding!r}, "
            f"flags={self._flags!r}, group_id={self._group_id})"
        )

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
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
        lyrics_frame : minim.media.metadata.id3.ID3v2USLTFrame
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
    ) -> Self:
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
        lyrics_frame : minim.media.metadata.id3.ID3v2USLTFrame
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
    ) -> Self:
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
        lyrics_frame : minim.media.metadata.id3.ID3v2USLTFrame
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
    def _key(self) -> tuple[str, str]:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set` Unique key.
        """
        return self._language, self._description

    @property
    def description(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        Short content description.
        """
        return self._description

    @description.setter
    def description(self, value: str, /) -> None:
        validate_type("description", value, str)
        if getattr(self, "_text_encoding", None) == "iso-8859-1":
            self._ensure_iso88591_encode("description", value)
        self._description = value

    @property
    def language(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary:`set`
        ISO 639-2 code for the language.
        """
        return self._language

    @language.setter
    def language(self, value: str, /) -> None:
        validate_type("language", value, str)
        if len(value) != 3:
            raise ValueError(f"Invalid ISO 639-2 code {value!r}.")
        self._language = value

    @property
    def lyrics(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Unsynchronized lyrics.
        """
        return self._lyrics

    @lyrics.setter
    def lyrics(self, value: str, /) -> None:
        validate_type("lyrics", value, str)
        self._lyrics = value

    @property
    def text_encoding(self) -> str:
        """
        :bdg-primary:`get` :bdg-secondary:`set` Text encoding.
        """
        return self._text_encoding

    @text_encoding.setter
    def text_encoding(self, value: int | str, /) -> None:
        value = self._prepare_text_encoding(value)
        if value == "iso-8859-1":
            self._ensure_iso88591_encode("description", self._description)
            self._ensure_iso88591_encode("lyrics", self._lyrics)
        self._text_encoding = value

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
            Tag version.

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
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
                )


class UnknownID3v2Frame(ID3v2Frame):
    """
    Unknown ID3v2 frame.
    """

    _allow_multiple: ClassVar[bool] = True
    _frame_ids: ClassVar[dict[int, bytes]] = {}

    __slots__ = ("_frame_data", "_frame_id", "_frame_length")

    def __init__(
        self,
        frame_id: bytes | bytearray,
        frame_data: bytes | bytearray,
        *,
        flags: ID3v2FrameFlags | None = None,
        group_id: int | None = None,
    ) -> None:
        """
        Parameters
        ----------
        frame_id : bytes or bytearray
            Frame ID.

        frame_data : bytes or bytearray
            Frame data.

        flags : minim.media.metadata.id3.ID3v2FrameFlags; \
        keyword-only; optional
            Flags.

        group_id : int; keyword-only; optional
            Group identifier.

            **Valid range**: :code:`0` to :code:`255`.
        """
        super().__init__(flags=flags, group_id=group_id)
        validate_type("frame_id", frame_id, bytes | bytearray)
        if not 3 <= len(frame_id) <= 4:
            raise ValueError(
                "`frame_id` must be three- or four-characters long."
            )
        self._frame_id = bytes(frame_id)
        validate_type("frame_data", frame_data, bytes | bytearray)
        self._frame_data = bytes(frame_data)
        self._frame_length = len(self._frame_data)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(frame_id={self._frame_id!r}, "
            f"frame_data=<{len(self._frame_data)} byte(s)>, "
            f"flags={self._flags!r}, group_id={self._group_id})"
        )

    @classmethod
    def _from_stream_2_2(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
        """
        Instantiate an unknown ID3v2 frame object from an ID3v2.2 frame
        bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the ID3v2 frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        frame : minim.media.metadata.id3.UnknownID3v2Frame
            ID3v2 frame.
        """
        obj = super()._from_stream_2_2(stream, strict=strict)
        obj._frame_id = stream[:3].tobytes()
        obj._frame_length = int.from_bytes(stream[3:6], byteorder="big")
        obj._frame_data = stream[6 : 6 + obj._frame_length].tobytes()
        return obj

    @classmethod
    def _from_stream_2_3(
        cls, stream: memoryview, /, *, strict: bool = True
    ) -> Self:
        """
        Instantiate an unknown ID3v2 frame object from an ID3v2.3 frame
        bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the ID3v2 frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        frame : minim.media.metadata.id3.UnknownID3v2Frame
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
    ) -> Self:
        """
        Instantiate an unknown ID3v2 frame object from an ID3v2.4 frame
        bytestream.

        Parameters
        ----------
        stream : memoryview; positional-only
            Bytes-like object containing the ID3v2 frame.

        strict : bool; keyword-only; default: :code:`True`
            Whether to ensure metadata strictly adheres to the ID3 tag
            specifications.

        Returns
        -------
        frame : minim.media.metadata.id3.UnknownID3v2Frame
            ID3v2 frame.
        """
        obj = super()._from_stream_2_4(stream, strict=strict)
        if not hasattr(obj, "_frame_id"):
            obj._frame_id = stream[:4].tobytes()
            obj._frame_length = decode_synchsafe_int(*stream[4:8])
            obj._frame_data = stream[10 : 10 + obj._frame_length].tobytes()
        return obj

    @property
    def frame_id(self) -> bytes:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set` Frame ID.
        """
        return self._frame_id

    @property
    def frame_data(self) -> bytes:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set` Raw frame data.
        """
        return self._frame_data

    @property
    def frame_length(self) -> int:
        """
        :bdg-primary:`get` :bdg-secondary-line:`set`
        Frame length, in bytes.
        """
        return len(self._frame_data)

    def get_frame_id(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Get the frame ID for a given tag version.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            Tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        frame_id : bytes
            Frame ID.
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
        *args: Any,
        **kwargs: Any,
    ) -> bytes:
        """
        Serialize the ID3v2 frame to a bytestream.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            Tag version.

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
                    f"Valid values: {join_values(ID3V2_TAG_VERSIONS)}."
                )


class EncryptedID3v2Frame(UnknownID3v2Frame):
    """
    Encrypted ID3v2 frame.
    """

    __slots__ = ("_class",)

    def __init__(
        self,
        frame_id: bytes | bytearray,
        frame_data: bytes | bytearray,
        *,
        flags: ID3v2FrameFlags | None = None,
        group_id: int | None = None,
    ) -> None:
        """
        Parameters
        ----------
        frame_id : bytes or bytearray
            Frame ID.

        frame_data : bytes or bytearray
            Frame data.

        flags : minim.media.metadata.id3.ID3v2FrameFlags; \
        keyword-only; optional
            Flags.

        group_id : int; keyword-only; optional
            Group identifier.

            **Valid range**: :code:`0` to :code:`255`.
        """
        super().__init__(
            frame_id=frame_id,
            frame_data=frame_data,
            flags=flags,
            group_id=group_id,
        )
        if (cls := self._get_class(frame_id)) is UnknownID3v2Frame:
            self._class = None
        else:
            self._class = cls
            self._allow_multiple = cls._allow_multiple
            self._frame_ids = cls._frame_ids

    def get_frame_id(self, tag_version: str | tuple[int, int, int]) -> bytes:
        """
        Get the frame ID for a given tag version.

        Parameters
        ----------
        tag_version : str or tuple[int, int, int]
            Tag version.

            **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
            :code:`"2.3.0"` or :code:`(2, 3, 0)`,
            :code:`"2.4.0"` or :code:`(2, 4, 0)`.

        Returns
        -------
        frame_id : bytes
            Frame ID.
        """
        if self._frame_ids:
            return ID3v2Frame.get_frame_id(self, tag_version=tag_version)
        return super().get_frame_id(tag_version=tag_version)
