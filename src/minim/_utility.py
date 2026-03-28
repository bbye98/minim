from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from ._types import COLLECTION_TYPES

if TYPE_CHECKING:
    from typing import Any

    from ._types import Collection


def join_values(values: Collection[Any], /, *, whitespace: bool = True) -> str:
    """
    Concatenate values into a formatted string.

    Parameters
    ----------
    values : Collection[str]; positional-only
        Values.

    whitespace : bool; keyword-only; default: :code:`True`
        Whether to include a whitespace after commas.

    Returns
    -------
    values : str
        Comma-delimited string of the values.
    """
    if not isinstance(values, COLLECTION_TYPES):
        values = [values]
    return f",{' ' if whitespace else ''}".join(sorted(map(repr, values)))


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
