from __future__ import annotations
from datetime import datetime
import re
import types
from typing import TYPE_CHECKING, Callable

from ._types import COLLECTION_TYPES

if TYPE_CHECKING:
    from typing import Any

    from ._types import Collection

ASCII_CHARS_REGEX = re.compile("[\x20-\x7e]*$")
TRANSLATION_TABLES = {"remove_separators": str.maketrans("", "", "‐‒–—―−")}

set_obj_attr = object.__setattr__


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
    value: int | float | str,
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

    value : int, float, or str; positional-only
        Variable value.

    data_type : type; positional-only
        Allowed numeric data type.

    lower_bound : int or float; optional
        Lower bound, inclusive.

    upper_bound : int or float; optional
        Upper bound, inclusive.
    """
    try:
        if isinstance(value, str):
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
