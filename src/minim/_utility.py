from __future__ import annotations
from datetime import MINYEAR, MAXYEAR, datetime
import re
import types
from typing import TYPE_CHECKING, Callable, NamedTuple

from ._types import COLLECTION_TYPES

if TYPE_CHECKING:
    from typing import Any

    from ._types import Collection

ASCII_CHARS_REGEX = re.compile("[\x20-\x7e]*$")
TRANSLATION_TABLES = {"remove_separators": str.maketrans("", "", "‐‒–—―−")}

set_obj_attr = object.__setattr__


class DateTime(NamedTuple):
    """
    Datetime with optional components.
    """

    year: int
    month: int | None = None
    day: int | None = None
    hour: int | None = None
    minute: int | None = None
    second: int | None = None

    _DATETIME_RE = re.compile(
        r"^(\d{4})(?:-(\d{2})(?:-(\d{2})(?:T(\d{2})(?::(\d{2})(?::(\d{2}))?)?)?)?)?$"
    )

    @classmethod
    def from_string(cls, dt: str, /) -> DateTime:
        """
        Instantiate a :cls:`DateTime` object from a datetime string in
        ISO-8601 format.

        Parameters
        ----------
        dt : str; positional-only
            Datetime, in ISO-8601 format.

        Returns
        -------
        dt : DateTime
            Datetime.
        """
        length = len(dt)
        if length > 19:
            dt = dt[:19]
            length = 19
        dt = dt.upper()

        if match := cls._DATETIME_RE.match(dt):
            groups = match.groups()
            try:
                end_idx = groups.index(None)
            except ValueError:
                end_idx = None
            dt = DateTime(*(int(dt_comp) for dt_comp in groups[:end_idx]))
            cls._validate_datetime(dt)
            return dt
        else:
            raise ValueError(f"Invalid datetime string {dt!r}.")

    @classmethod
    def from_tuple(cls, dt: tuple[int, ...], /) -> DateTime:
        """
        Instantiate a :cls:`DateTime` object from a tuple of datetime
        components.

        Parameters
        ----------
        dt : tuple[int, ...]; positional-only
            Datetime components, in order of year, month, day, hour,
            minute, second. Optional components may be omitted or be
            represented as :code:`None`.

        Returns
        -------
        dt : DateTime
            Datetime.
        """
        if not 1 <= len(dt) <= 6:
            raise ValueError(
                f"Datetime component tuple {dt!r} must have between 1 and "
                f"6 components."
            )
        dt = DateTime(
            *(None if dt_comp is None else int(dt_comp) for dt_comp in dt)
        )
        cls._validate_datetime(dt)
        return dt

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
        if month in {1, 3, 5, 7, 8, 10, 12}:
            return 31
        elif month in {4, 6, 9, 11}:
            return 30
        elif month == 2:
            if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
                return 29
            else:
                return 28

    @staticmethod
    def _validate_datetime(dt: DateTime, /) -> None:
        """
        Validate datetime components.

        Parameters
        ----------
        dt : DateTime; positional-only
            Datetime.
        """
        year = dt.year
        validate_range("year", year, MINYEAR, MAXYEAR)
        month = dt.month
        if month is not None:
            validate_range("month", month, 1, 12)
        if dt.day is not None:
            validate_range(
                "day",
                dt.day,
                1,
                DateTime._get_num_days_in_month(month, year=year),
            )
        if dt.hour is not None:
            validate_range("hour", dt.hour, 0, 23)
        if dt.minute is not None:
            validate_range("minute", dt.minute, 0, 59)
        if dt.second is not None:
            validate_range("second", dt.second, 0, 59)

    def to_string(self) -> str:
        """
        Convert the datetime to a string in ISO-8601 format.

        Returns
        -------
        dt : str
            Datetime, in ISO-8601 format.
        """
        dt = f"{self.year:04}"
        if self.month is not None:
            dt += f"-{self.month:02}"
            if self.day is not None:
                dt += f"-{self.day:02}"
                if self.hour is not None:
                    dt += f"T{self.hour:02}"
                    if self.minute is not None:
                        dt += f":{self.minute:02}"
                        if self.second is not None:
                            dt += f":{self.second:02}"
        return dt


def decode_32_bit_synchsafe_int(
    byte_1: int, byte_2: int, byte_3: int, byte_4: int, /
) -> int:
    """
    Decode a 32-bit synchsafe integer.

    Parameters
    ----------
    byte_1 : int; positional-only
        First byte in synchsafe integer.

    byte_2 : int; positional-only
        Second byte in synchsafe integer.

    byte_3 : int; positional-only
        Third byte in synchsafe integer.

    byte_4 : int; positional-only
        Fourth byte in synchsafe integer.

    Returns
    -------
    value : int
        Decoded synchsafe integer value.
    """
    return (byte_1 << 21) | (byte_2 << 14) | (byte_3 << 7) | byte_4


def join_values(
    values: Collection[Any],
    /,
    *,
    fmt: Callable = repr,
    whitespace: bool = True,
) -> str:
    """
    Concatenate values into a formatted string.

    Parameters
    ----------
    values : Collection[str]; positional-only
        Values.

    fmt : type; keyword-only, default: :code:`repr`
        Formatting function to apply to each value.

    whitespace : bool; keyword-only; default: :code:`True`
        Whether to include a whitespace after commas.

    Returns
    -------
    values : str
        Comma-delimited string of the values.
    """
    if not isinstance(values, COLLECTION_TYPES):
        values = [values]
    return f",{' ' if whitespace else ''}".join(sorted(map(fmt, values)))


def prepare_datetime(dt: datetime | str, fmt: str, /) -> str:
    """
    Validate, normalize, and stringify a datetime.

    Parameters
    ----------
    dt : datetime.datetime or str; positional-only
        Datetime.

    fmt : str; positional-only
        Datetime format.

    Returns
    -------
    dt : str
        Trimmed datetime string.
    """
    if isinstance(dt, str):
        dt = dt.strip()
        datetime.strptime(dt.strip(), fmt)
        return dt

    return dt.strftime(fmt)


def prepare_isrc(isrc: str, /) -> str:
    """
    Validate and normalize an International Standard Recording Code
    (ISRC).

    Parameters
    ----------
    isrc : str; positional-only
        ISRC.

    Returns
    -------
    isrc : str
        Trimmed ISRC string without hyphens or spaces.
    """
    isrc = prepare_string("isrc", isrc, remove_whitespace=True).translate(
        TRANSLATION_TABLES["remove_separators"]
    )
    if len(isrc) != 12 or not (
        isrc[:2].isalpha() and isrc[2:5].isalnum() and isrc[5:].isdecimal()
    ):
        raise ValueError(f"{isrc!r} is not a valid ISRC.")
    return isrc


def prepare_string(
    name: str,
    string: bytes | str,
    /,
    *,
    allow_blank: bool = False,
    remove_whitespace: bool = False,
) -> bytes | str:
    """
    Validate and strip a string.

    Parameters
    ----------
    name : str; positional-only.
        Parameter name for the string.

    string : bytes or str; positional-only
        String.

    allow_blank : bool; keyword-only; default: :code:`False`
        Whether to allow empty strings.

    remove_whitespace : bool; keyword-only; default: :code:`False`
        Whether to remove whitespace throughout the string.

    Returns
    -------
    string : bytes or str
        Stripped string.
    """
    validate_type(name, string, bytes | str)
    string = "".join(string.split()) if remove_whitespace else string.strip()
    if not allow_blank and not len(string):
        raise ValueError(f"`{name}` cannot be blank.")
    return string


def validate_number(
    name: str,
    value: int | float,
    data_type: type | types.UnionType,
    /,
    lower_bound: int | float | None = None,
    upper_bound: int | float | None = None,
) -> None:
    """
    Validate the value of a variable containing a number.

    Parameters
    ----------
    name : str; positional-only
        Variable name.

    value : int or float; positional-only
        Variable value.

    data_type : type or types.UnionType; positional-only
        Allowed numeric data types.

    lower_bound : int or float; optional
        Lower bound, inclusive.

    upper_bound : int or float; optional
        Upper bound, inclusive.
    """
    if not isinstance(value, data_type):
        data_type_str = (
            data_type.__name__
            if isinstance(data_type, type)
            else str(data_type)
        )
        raise TypeError(
            f"`{name}` must be a(n) {data_type_str}, not a(n) "
            f"{type(value).__name__}."
        )

    validate_range(
        name, value, lower_bound=lower_bound, upper_bound=upper_bound
    )


def validate_numeric(
    name: str,
    value: int | float | bytes | str,
    data_type: type,
    /,
    lower_bound: int | float | None = None,
    upper_bound: int | float | None = None,
) -> None:
    """
    Validate the value of a variable containing a numeric-like value.

    Parameters
    ----------
    name : str; positional-only
        Variable name.

    value : int, float, bytes, or str; positional-only
        Variable value.

    data_type : type; positional-only
        Allowed numeric data type.

    lower_bound : int or float; optional
        Lower bound, inclusive.

    upper_bound : int or float; optional
        Upper bound, inclusive.
    """
    try:
        if isinstance(value, bytes | str):
            value = data_type(value)
        validate_number(name, value, data_type, lower_bound, upper_bound)
    except TypeError:
        data_type_str = (
            data_type.__name__
            if isinstance(data_type, type)
            else str(data_type)
        )
        raise TypeError(
            f"`{name}` must be a(n) {data_type_str} or its numeric "
            f"string representation, not a(n) {type(value).__name__}."
        )


def validate_range(
    name: str,
    value: int | float,
    /,
    lower_bound: int | float | None = None,
    upper_bound: int | float | None = None,
) -> None:
    """
    Validate the value of a numeric variable.

    Parameters
    ----------
    name : str; positional-only
        Variable name.

    value : int, float, or str; positional-only
        Variable value.

    lower_bound : int or float; optional
        Lower bound, inclusive.

    upper_bound : int or float; optional
        Upper bound, inclusive.
    """
    has_lower_bound = lower_bound is not None
    has_upper_bound = upper_bound is not None
    if (
        has_lower_bound
        and value < lower_bound
        or has_upper_bound
        and value > upper_bound
    ):
        if has_lower_bound:
            if has_upper_bound:
                emsg = f"between {lower_bound} and {upper_bound}"
            else:
                emsg = f"greater than {lower_bound}"
        else:
            emsg = f"less than {upper_bound}"
        raise ValueError(f"`{name}` must be {emsg}, inclusive.")


def validate_type(
    name: str, value: Any, data_type: type | types.UnionType, /
) -> None:
    """
    Validate the data type of a variable.

    Parameters
    ----------
    name : str; positional-only
        Variable name.

    value : Any; positional-only
        Variable value.

    data_type : type or types.UnionTypes; positional-only
        Allowed data type.
    """
    if not isinstance(value, data_type):
        data_type_str = (
            data_type.__name__
            if isinstance(data_type, type)
            else str(data_type)
        )
        raise ValueError(
            f"`{name}` must be a(n) {data_type_str}, not a(n) "
            f"{type(value).__name__}."
        )
