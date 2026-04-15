from __future__ import annotations
from datetime import datetime
import types
from typing import TYPE_CHECKING, Callable

from ._types import COLLECTION_TYPES

if TYPE_CHECKING:
    from typing import Any

    from ._types import Collection


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


@staticmethod
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
    has_lower_bound = lower_bound is not None
    has_upper_bound = upper_bound is not None
    if has_lower_bound:
        if has_upper_bound:
            emsg_suffix = (
                f" between {lower_bound} and {upper_bound}, inclusive"
            )
        else:
            emsg_suffix = f" greater than {lower_bound}, inclusive"
    else:
        if has_upper_bound:
            emsg_suffix = f" less than {upper_bound}, inclusive"
        else:
            emsg_suffix = ""
    if (
        not isinstance(value, data_type)
        or (has_lower_bound and value < lower_bound)
        or (has_upper_bound and value > upper_bound)
    ):
        data_type_str = (
            data_type.__name__
            if isinstance(data_type, type)
            else str(data_type)
        )
        raise ValueError(
            f"`{name}` must be a(n) {data_type_str}{emsg_suffix}."
        )


@staticmethod
def validate_numeric(
    name: str,
    value: int | float | str,
    data_type: type,
    /,
    lower_bound: int | float | None = None,
    upper_bound: int | float | None = None,
) -> None:
    """
    Validate the value of a variable containing a numeric value.

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
    except ValueError:
        raise ValueError(
            f"`{name}` must be a(n) {data_type.__name__} or its "
            "string representation."
        )


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
