from collections.abc import Collection
from typing import Any


def join_values(values: Collection[Any], /) -> str:
    """
    Concatenate values into a formatted string.

    Parameters
    ----------
    values : Collection[str]; positional-only
        Values.

    Returns
    -------
    values : str
        Comma-delimited string of the values.
    """
    return ", ".join(r for r in sorted(repr(value) for value in values))
