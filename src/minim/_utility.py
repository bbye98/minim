from __future__ import annotations

import mmap
import re
import types
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

from ._types import COLLECTION_TYPES

if TYPE_CHECKING:
    from typing import Any

    from ._types import BytesLike, Collection

ASCII_CHARS_REGEX = re.compile("[\x20-\x7e]*$")
TRANSLATION_TABLES = {"remove_separators": str.maketrans("", "", "‐‒–—―−")}

set_obj_attr = object.__setattr__


def as_buffer(stream: BytesLike, /) -> memoryview:
    """
    Return a :cls:`memoryview` of a bytes-like object.

    Parameters
    ----------
    stream : BytesLike; positional-only
        Bytes-like object.

    Returns
    -------
    view : memoryview
        Buffer interface to the bytes-like object.

    Raises
    ------
    TypeError
        If `stream` is not a bytes-like object.
    """
    if isinstance(stream, memoryview):
        return stream

    if isinstance(stream, bytes | bytearray | mmap.mmap):
        return memoryview(stream)

    raise TypeError("`stream` must be a bytes-like object.")


def copy_docstring(
    source: Callable[..., Any],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Return a decorator that copies the docstring from one function to
    another.

    Parameters
    ----------
    source : Callable[..., Any]
        Function whose docstring is to be copied.

    Returns
    -------
    decorator : Callable[[Callable[..., Any]], Callable[..., Any]]
        Decorator that replaces the docstring of the decorated function
        with that of `source`.
    """

    def decorator(destination: Callable[..., Any]) -> Callable[..., Any]:
        destination.__doc__ = source.__doc__
        return destination

    return decorator


def join_values(
    values: Any,
    /,
    *,
    fmt: Callable = repr,
    whitespace: bool = True,
) -> str:
    """
    Sort and concatenate values into a formatted, comma-delimited
    string.

    Parameters
    ----------
    values : Any; positional-only
        Values to format and concatenate.

    fmt : Callable; keyword-only, default: :code:`repr`
        Formatting function to apply to each value.

    whitespace : bool; keyword-only; default: :code:`True`
        Whether to include whitespace after commas.

    Returns
    -------
    joined_values : str
        Comma-delimited string of the formatted values, sorted
        lexicographically.
    """
    if not isinstance(values, COLLECTION_TYPES):
        values = [values]
    return f",{' ' if whitespace else ''}".join(sorted(map(fmt, values)))


def prepare_barcode(barcode: int | str, /) -> str:
    """
    Validate and normalize a Universal Product Code (UPC) or European
    Article Number (EAN) barcode.

    Parameters
    ----------
    barcode : int or str; positional-only
        UPC or EAN barcode.

    Returns
    -------
    barcode : str
        Normalized UPC or EAN barcode without whitespace or separators.

    Raises
    ------
    TypeError
        If `barcode` is neither an integer nor a string.

    ValueError
        If `barcode` is an invalid UPC or EAN barcode.
    """
    barcode = (
        str(barcode)
        if isinstance(barcode, int)
        else prepare_string(barcode, remove_all_whitespace=True).translate(
            TRANSLATION_TABLES["remove_separators"]
        )
    )
    if not barcode.isdecimal() or len(barcode) not in {12, 13}:
        raise ValueError(f"{barcode!r} is not a valid UPC or EAN barcode.")
    return barcode


def prepare_datetime(dt: datetime | str, fmt: str, /) -> str:
    """
    Validate, normalize, and stringify a datetime.

    Parameters
    ----------
    dt : datetime.datetime or str; positional-only
        Datetime.

    fmt : str; positional-only
        Format string used to parse or format the datetime.

    Returns
    -------
    dt : str
        Normalized datetime string.

    Raises
    ------
    TypeError
        If `dt` is neither a string nor a :cls:`datetime.datetime`
        object.

    ValueError
        If `dt` is a string that does not match `fmt` or represents an
        invalid date or time.
    """
    if isinstance(dt, str):
        dt = dt.strip()
        datetime.strptime(dt, fmt)  # noqa: DTZ007
        return dt

    if isinstance(dt, datetime):
        return dt.strftime(fmt)

    raise TypeError("`dt` must be a string or a datetime.datetime object.")


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
        Normalized ISRC without whitespace or separators.

    Raises
    ------
    TypeError
        If `isrc` is not a string.

    ValueError
        If `isrc` is an invalid ISRC.
    """
    isrc = prepare_string("isrc", isrc, remove_all_whitespace=True).translate(
        TRANSLATION_TABLES["remove_separators"]
    )
    if len(isrc) != 12 or not (
        isrc[:2].isalpha() and isrc[2:5].isalnum() and isrc[5:].isdecimal()
    ):
        raise ValueError(f"{isrc!r} is not a valid ISRC.")
    return isrc


def prepare_iswc(iswc: str, /) -> str:
    """
    Validate and normalize an International Standard Musical Work Code
    (ISWC).

    Parameters
    ----------
    iswc : str; positional-only
        ISWC.

    Returns
    -------
    iswc : str
        Normalized ISWC without whitespace or separators.

    Raises
    ------
    TypeError
        If `iswc` is not a string.

    ValueError
        If `iswc` is an invalid ISWC.
    """
    iswc = prepare_string("iswc", iswc, remove_all_whitespace=True).translate(
        TRANSLATION_TABLES["remove_separators"]
    )
    if (
        len(iswc) != 11
        or (
            1
            + sum(
                (index + 1) * int(digit)
                for index, digit in enumerate(iswc[1:-1])
            )
        )
        % 10
    ) != int(iswc[-1]):
        raise ValueError(f"{iswc!r} is not a valid ISWC.")
    return iswc


def prepare_string(
    name: str,
    string: str,
    /,
    *,
    allow_blank: bool = False,
    remove_all_whitespace: bool = False,
) -> str:
    """
    Validate and normalize a string.

    Parameters
    ----------
    name : str; positional-only
        Parameter name for the string.

    string : str; positional-only
        String.

    allow_blank : bool; keyword-only; default: :code:`False`
        Whether to allow empty strings.

    remove_all_whitespace : bool; keyword-only; default: :code:`False`
        Whether to remove all whitespace throughout the string. If
        :code:`False`, only leading and trailing whitespace is removed.

    Returns
    -------
    string : str
        Normalized string with leading and trailing (or all with
        :code:`remove_all_whitespace=True`) whitespace removed.

    Raises
    ------
    TypeError
        If `string` is not a string.

    ValueError
        If `string` is an empty string and :code:`allow_blank=False`.
    """
    validate_type(name, string, str)
    string = (
        "".join(string.split()) if remove_all_whitespace else string.strip()
    )
    if not allow_blank and not len(string):
        raise ValueError(f"`{name}` cannot be blank.")
    return string


def validate_country_code(country_code: str, /) -> None:
    """
    Validate the format of an International Organization for
    Standardization (ISO) 3166-1 alpha-2 country code.

    Parameters
    ----------
    country_code : str; positional-only
        ISO 3166-1 alpha-2 country code.

    Raises
    ------
    ValueError
        If `country_code` is not a valid ISO 3166-1 alpha-2 country
        code.
    """
    if (
        not isinstance(country_code, str)
        or len(country_code) != 2
        or not country_code.isalpha()
    ):
        raise ValueError(
            f"{country_code!r} is not a valid ISO 3166-1 alpha-2 country code."
        )


def validate_iso_8859_1_string(name: str, value: bytes | str, /) -> None:
    """
    Validate that a string contains only ISO-8859-1 characters.

    Parameters
    ----------
    name : str; positional-only
        Parameter name for the string.

    value : bytes or str; positional-only
        String.

    Raises
    ------
    ValueError
        If `value` does not contain only ISO-8859-1 characters.
    """
    if value and any(ord(char) > 255 for char in value):
        raise ValueError(f"`{name}` can contain only ISO-8859-1 characters.")


def validate_language_code(language_code: str, /) -> None:
    """
    Validate the format of an International Organization for
    Standardization (ISO) 639-1 language code.

    Parameters
    ----------
    language_code : str; positional-only
        ISO 639-1 language code.

    Raises
    ------
    ValueError
        If `language_code` is not a valid ISO 639-1 language code.
    """
    if (
        not isinstance(language_code, str)
        or len(language_code) != 2
        or not language_code.isalpha()
    ):
        raise ValueError(
            f"{language_code!r} is not a valid ISO 639-1 language code."
        )


def validate_locale(locale: str, /) -> None:
    """
    Validate a locale identifier consisting of an ISO 639-1 language
    code and an ISO 3166-1 alpha-2 country code joined by an underscore.

    Parameters
    ----------
    locale : str; positional-only
        Locale identifier.

    Raises
    ------
    ValueError
        If `locale` is not a valid locale identifier.
    """
    if (
        not isinstance(locale, str)
        or len(locale) != 5
        or not locale[:2].isalpha()
        or locale[2] != "_"
        or not locale[3:].isalpha()
    ):
        raise ValueError(
            f"{locale!r} is not a valid locale identifier consisting "
            "of an ISO 639-1 language code and an ISO 3166-1 alpha-2 "
            "country code joined by an underscore."
        )


def validate_number(
    name: str,
    value: float,
    data_type: type | types.UnionType,
    /,
    lower_bound: float | None = None,
    upper_bound: float | None = None,
) -> None:
    """
    Validate a numeric value.

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

    Raises
    ------
    TypeError
        If `value` is not an instance of `data_type`.

    ValueError
        If `value` is outside the specified range.
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
    value: float | bytes | str,
    data_type: type,
    /,
    lower_bound: float | None = None,
    upper_bound: float | None = None,
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

    Raises
    ------
    TypeError
        If `value` is neither a numeric value nor the bytes or string
        representation of one.

    ValueError
        If `value` cannot be converted to `data_type` or is outside the
        specified range.
    """
    if isinstance(value, bytes | str):
        try:
            value = data_type(value)
        except (TypeError, ValueError):
            data_type_str = (
                data_type.__name__
                if isinstance(data_type, type)
                else str(data_type)
            )
            raise ValueError(
                f"`{name}` must be a(n) {data_type_str} or its numeric "
                f"string representation, not {value!r}."
            ) from None

    validate_number(name, value, data_type, lower_bound, upper_bound)


def validate_range(
    name: str,
    value: float,
    /,
    lower_bound: float | None = None,
    upper_bound: float | None = None,
) -> None:
    """
    Validate the value of a numeric variable.

    Parameters
    ----------
    name : str; positional-only
        Variable name.

    value : int or float; positional-only
        Variable value.

    lower_bound : int or float; optional
        Lower bound, inclusive.

    upper_bound : int or float; optional
        Upper bound, inclusive.

    Raises
    ------
    ValueError
        If `value` is outside the specified range.
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
                emsg = f"between {lower_bound} and {upper_bound}, inclusive"
            else:
                emsg = f"greater than or equal to {lower_bound}"
        else:
            emsg = f"less than or equal to {upper_bound}"
        raise ValueError(f"`{name}` must be {emsg}.")


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

    data_type : type or types.UnionType; positional-only
        Allowed data types.

    Raises
    ------
    TypeError
        If `value` is not an instance of `data_type`.
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


def validate_uuids(uuids: str | Collection[str], /) -> None:
    """
    Validate universally unique identifiers (UUIDs).

    Parameters
    ----------
    uuids : str or Collection[str]; positional-only
        UUIDs.

    Raises
    ------
    TypeError
        If `uuids` is neither a string nor a collection of strings.

    ValueError
        If `uuids` contains an invalid UUID.
    """
    if isinstance(uuids, str):
        try:
            uuid.UUID(uuids)
        except ValueError as e:
            raise ValueError(f"{uuids!r} is not a valid UUID.") from e

    elif isinstance(uuids, COLLECTION_TYPES):
        for uuid_ in uuids:
            validate_uuids(uuid_)
    else:
        raise TypeError(
            "UUIDs must be provided as a string or a collection of strings."
        )
