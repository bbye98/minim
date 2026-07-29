from __future__ import annotations

import mmap
import re
import types
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Callable

from ._types import COLLECTION_TYPES

if TYPE_CHECKING:
    from typing import Any

    from ._types import BytesLike, Collection

ASCII_CHARS_REGEX = re.compile("[\x20-\x7e]*$")
TRANSLATION_TABLES = {"remove_separators": str.maketrans("", "", "‐‒–—―−")}

set_obj_attr = object.__setattr__


def as_buffer(stream: BytesLike) -> memoryview:
    """
    Return a C-level buffer interface to a bytes-like object.

    Parameters
    ----------
    bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
    positional-only; optional
        Bytes-like object.

    Returns
    -------
    view : memoryview
        Buffer interface to the bytes-like object.
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
        Function whose docstring should be copied.

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
        Trimmed UPC or EAN barcode without hyphens or spaces.
    """
    barcode = (
        str(barcode)
        if isinstance(barcode, int)
        else prepare_string(barcode, remove_whitespace=True).translate(
            TRANSLATION_TABLES["remove_separators"]
        )
    )
    if not barcode.isdecimal() or len(barcode) not in {12, 13}:
        raise ValueError(f"{barcode!r} is not a valid UPC or EAN.")
    return barcode


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
        Trimmed ISWC string without hyphens or spaces.
    """
    iswc = prepare_string("iswc", iswc, remove_whitespace=True).translate(
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
    remove_whitespace: bool = False,
) -> str:
    """
    Validate and strip a string.

    Parameters
    ----------
    name : str; positional-only.
        Parameter name for the string.

    string : str; positional-only
        String.

    allow_blank : bool; keyword-only; default: :code:`False`
        Whether to allow empty strings.

    remove_whitespace : bool; keyword-only; default: :code:`False`
        Whether to remove whitespace throughout the string.

    Returns
    -------
    string : str
        Stripped string.
    """
    validate_type(name, string, str)
    string = "".join(string.split()) if remove_whitespace else string.strip()
    if not allow_blank and not len(string):
        raise ValueError(f"`{name}` cannot be blank.")
    return string


def validate_country_code(country_code: str, /) -> None:
    """
    Validate an International Organization for Standardization (ISO)
    3166-1 alpha-2 country code.

    Parameters
    ----------
    country_code : str; positional-only
        ISO 3166-1 alpha-2 country code.
    """
    if (
        not isinstance(country_code, str)
        or len(country_code) != 2
        or not country_code.isalpha()
    ):
        raise ValueError(
            f"{country_code!r} is not a valid ISO 3166-1 alpha-2 country code."
        )


def validate_iso_8859_1_string(name: str, string: bytes | str, /) -> None:
    """
    Validate that a string only contains ISO-8859-1 characters.

    Parameters
    ----------
    name : str; positional-only
        Parameter name for the string.

    string : bytes or str; positional-only
        String.
    """
    if string and ord(max(string)) > 255:
        raise ValueError(f"`{name}` can only contain ISO-8859-1 characters.")


def validate_language_code(language_code: str, /) -> None:
    """
    Validate an International Organization for Standardization (ISO)
    639-1 language code.

    Parameters
    ----------
    language_code : str; positional-only
        ISO 639-1 language code.
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
    Validate an Internet Engineering Task Force (IETF) Best Current
    Practice (BCP) 47 language tag, as defined in Request for Comments
    (RFC) 1766.

    Parameters
    ----------
    locale : str; positional-only
        IETF BCP 47 language tag.
    """
    if (
        not isinstance(locale, str)
        or len(locale) != 5
        or not locale[:2].isalpha()
        or locale[2] != "_"
        or not locale[3:].isalpha()
    ):
        raise ValueError(
            f"{locale!r} is not a valid IETF BCP 47 language tag "
            "consisting of an ISO 639-1 language code and an ISO "
            "3166-1 alpha-2 country code joined by an underscore."
        )


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


def validate_uuids(
    uuids: str | Collection[str], /, *, recursive: bool = True
) -> None:
    """
    Validate universally unique identifiers (UUIDs).

    Parameters
    ----------
    uuids : str or Collection[str]; positional-only
        UUIDs.
    """
    if isinstance(uuids, str):
        try:
            uuid.UUID(uuids)
        except (TypeError, ValueError) as e:
            raise ValueError(f"{uuids!r} is not a valid UUID.") from e

    elif recursive and isinstance(uuids, COLLECTION_TYPES):
        for uuid_ in uuids:
            validate_uuids(uuid_, recursive=False)
    else:
        raise ValueError(
            "UUIDs must be provided as a string or a collection of strings."
        )
